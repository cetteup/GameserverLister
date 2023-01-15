import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from random import choices
from typing import Type, List, Tuple, Optional, Union, Callable

import gevent
import requests
from gevent.pool import Pool

from GameserverLister.common.helpers import is_valid_port, find_query_port
from GameserverLister.common.servers import Server, ObjectJSONEncoder, FrostbiteServer
from GameserverLister.common.types import Game
from GameserverLister.common.weblinks import WebLink


class ServerLister:
    game: Game
    server_list_dir_path: str
    server_list_file_path: str
    expired_ttl: float
    recover: bool
    add_links: bool
    ensure_ascii: bool
    server_class: Type[Server]
    servers: List[Server]

    session: requests.Session
    request_timeout: float

    def __init__(
            self,
            game: Game,
            server_class: Type[Server],
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str,
            request_timeout: float = 5.0
    ):
        self.game = game
        self.server_list_dir_path = os.path.realpath(list_dir)
        self.server_list_file_path = os.path.join(self.server_list_dir_path, f'{self.game}-servers.json')

        self.expired_ttl = expired_ttl
        self.recover = recover
        self.add_links = add_links

        self.ensure_ascii = True
        self.server_class = server_class
        self.servers = []

        # Init session
        self.session = requests.session()
        self.request_timeout = request_timeout

        # Create list dir if it does not exist
        if not os.path.isdir(self.server_list_dir_path):
            try:
                os.mkdir(self.server_list_dir_path)
            except IOError as e:
                logging.debug(e)
                logging.error(f'Failed to create missing server list directory at {self.server_list_dir_path}')
                sys.exit(1)

        # Init server list with servers from existing list or empty one
        if os.path.isfile(self.server_list_file_path):
            try:
                with open(self.server_list_file_path, 'r') as serverListFile:
                    logging.info('Loading existing server list')
                    self.servers = json.load(serverListFile, object_hook=self.server_class.load)
            except IOError as e:
                logging.debug(e)
                logging.error('Failed to read existing server list file')
                sys.exit(1)
            except json.decoder.JSONDecodeError as e:
                logging.debug(e)
                logging.error('Failed to parse existing server list file contents')
                sys.exit(1)

    def update_server_list(self):
        pass

    def add_update_servers(self, found_servers: List[Server]):
        # Add/update found servers to/in known servers
        logging.info(f'Updating server list with {len(found_servers)} found servers')
        for found_server in found_servers:
            known_server_uids = [s.uid for s in self.servers]
            # Update existing server entry or add new one
            if found_server.uid in known_server_uids:
                logging.debug(f'Found server {found_server.uid} already known, updating')
                index = known_server_uids.index(found_server.uid)
                self.servers[index].update(found_server)
                self.servers[index].trim(self.expired_ttl)
            else:
                logging.debug(f'Found server {found_server.uid} is new, adding')
                # Add new server entry
                self.servers.append(found_server)

    def remove_expired_servers(self) -> tuple:
        # Iterate over copy of server list and remove any expired servers from the (actual) server list
        logging.info(f'Checking expiration ttl for {len(self.servers)} servers')
        checks_since_last_ok = 0
        expired_servers_removed = 0
        expired_servers_recovered = 0
        for server in self.servers[:]:
            expired = datetime.now().astimezone() > server.last_seen_at + timedelta(hours=self.expired_ttl)
            if expired and self.recover:
                # Attempt to recover expired server by contacting/accessing it directly
                time.sleep(self.get_backoff_timeout(checks_since_last_ok))
                # Check if server can be accessed directly
                check_ok, found, checks_since_last_ok = self.check_if_server_still_exists(
                    server, checks_since_last_ok
                )

                # Remove server if request was sent successfully but server was not found
                if check_ok and not found:
                    logging.debug(f'Server {server.uid} has not been seen in '
                                  f'{self.expired_ttl} hours and could not be recovered, removing it')
                    self.servers.remove(server)
                    expired_servers_removed += 1
                elif check_ok and found:
                    logging.debug(f'Server {server.uid} did not appear in list but is still online, '
                                  f'updating last seen at')
                    index = self.servers.index(server)
                    self.servers[index].last_seen_at = datetime.now().astimezone()
                    self.servers[index].trim(self.expired_ttl)

                    expired_servers_recovered += 1
            elif expired:
                logging.debug(f'Server {server.uid} has not been seen in '
                              f'{self.expired_ttl} hours, removing it')
                self.servers.remove(server)
                expired_servers_removed += 1

        return expired_servers_removed, expired_servers_recovered

    def check_if_server_still_exists(self, server: Server, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        pass

    def build_server_links(
            self,
            uid: str,
            ip: Optional[str] = None,
            port: Optional[int] = None
    ) -> Union[List[WebLink], WebLink]:
        pass

    def get_backoff_timeout(self, checks_since_last_ok: int) -> int:
        # Default to no backoff
        return 0

    def write_to_file(self):
        logging.info(f'Writing {len(self.servers)} servers to output file')
        with open(self.server_list_file_path, 'w') as output_file:
            json.dump(self.servers, output_file, indent=2, ensure_ascii=self.ensure_ascii, cls=ObjectJSONEncoder)


class FrostbiteServerLister(ServerLister):
    servers: List[FrostbiteServer]
    server_validator: Callable

    def __init__(
            self,
            game: Game,
            server_class: Type[Server],
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str,
            request_timeout: float = 5.0
    ):
        super().__init__(game, server_class, expired_ttl, recover, add_links, list_dir, request_timeout)

    def find_query_ports(self, gamedig_bin_path: str, gamedig_concurrency: int, expired_ttl: float):
        logging.info(f'Searching query port for {len(self.servers)} servers')

        search_stats = {
            'totalSearches': len(self.servers),
            'queryPortFound': 0,
            'queryPortReset': 0
        }
        pool = Pool(gamedig_concurrency)
        jobs = []
        for server in self.servers:
            ports_to_try = self.build_port_to_try_list(server.game_port)

            # Remove any invalid ports
            ports_to_try = [p for p in ports_to_try if is_valid_port(p)]

            # Get default port (first in list) and 5 random ports from selection
            ports_to_try = [ports_to_try[0], *choices(ports_to_try[1:], k=5)]

            jobs.append(
                pool.spawn(find_query_port, gamedig_bin_path, self.game, server, ports_to_try, self.server_validator)
            )
        # Wait for all jobs to complete
        gevent.joinall(jobs)
        for index, job in enumerate(jobs):
            server = self.servers[index]
            logging.debug(f'Checking query port search result for {server.uid}')
            if job.value != -1:
                logging.debug(f'Query port found ({job.value}), updating server')
                server.query_port = job.value
                server.last_queried_at = datetime.now().astimezone()
                search_stats['queryPortFound'] += 1
            elif server.query_port != -1 and \
                    (server.last_queried_at is None or
                     datetime.now().astimezone() > server.last_queried_at + timedelta(hours=expired_ttl)):
                logging.debug(f'Query port expired, resetting to -1 (was {server.query_port})')
                server.query_port = -1
                # TODO Reset last queried at here?
                search_stats['queryPortReset'] += 1
        logging.info(f'Query port search stats: {search_stats}')

    # Function has to be public to overrideable by derived classes
    def build_port_to_try_list(self, game_port: int) -> list:
        pass


class HttpServerLister(ServerLister):
    page_limit: int
    per_page: int
    sleep: float
    max_attempts: int

    def __init__(
            self,
            game: Game,
            server_class: Type[Server],
            page_limit: int,
            per_page: int,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str,
            sleep: float,
            max_attempts: int
    ):
        super().__init__(game, server_class, expired_ttl, recover, add_links, list_dir, request_timeout=10)
        self.page_limit = page_limit
        self.per_page = per_page
        self.sleep = sleep
        self.max_attempts = max_attempts

    def update_server_list(self):
        offset = 0
        """
        The Frostbite server browsers returns tons of duplicate servers (pagination is completely broken/non-existent).
        You basically just a [per_page] random servers every time. Thus, there is no way of telling when to stop.
        As a workaround, just stop after not retrieving a new/unique server for [args.page_limit] pages
        """
        pages_since_last_unique_server = 0
        attempt = 0
        """
        Since pagination of the server list is completely broken, just get the first "page" over and over again until
        no servers have been found in [args.page_limit] "pages".
        """
        found_servers = []
        logging.info('Starting server list retrieval')
        while pages_since_last_unique_server < self.page_limit and attempt < self.max_attempts:
            # Sleep when requesting anything but offset 0 (use increased sleep when retrying)
            if offset > 0:
                time.sleep(pow(self.sleep, attempt + 1))

            try:
                response = self.session.get(
                    self.get_server_list_url(self.per_page),
                    timeout=self.request_timeout
                )
            except requests.exceptions.RequestException as e:
                logging.debug(e)
                logging.error(f'Request failed, retrying {attempt + 1}/{self.max_attempts}')
                # Count try and start over
                attempt += 1
                continue

            if response.status_code == 200:
                # Reset tries
                attempt = 0
                # Parse response
                parsed = response.json()
                server_total_before = len(found_servers)
                # Add all servers in response (if they are new)
                found_servers = self.add_page_found_servers(found_servers, parsed)
                if len(found_servers) == server_total_before:
                    pages_since_last_unique_server += 1
                    logging.info(f'Got nothing but duplicates (page: {int(offset / self.per_page)},'
                                 f' pages since last unique: {pages_since_last_unique_server})')
                else:
                    logging.info(f'Got {len(found_servers) - server_total_before} new servers')
                    # Found new unique server, reset
                    pages_since_last_unique_server = 0
                offset += self.per_page
            else:
                logging.error(f'Server responded with {response.status_code}, '
                              f'retrying {attempt + 1}/{self.max_attempts}')
                attempt += 1

        self.add_update_servers(found_servers)

    def get_server_list_url(self, per_page: int) -> str:
        pass

    def add_page_found_servers(self, found_servers: List[Server], page_response_data: dict) -> List[Server]:
        pass

    def get_backoff_timeout(self, checks_since_last_ok: int) -> int:
        return 1 + pow(self.sleep, checks_since_last_ok % self.max_attempts)
