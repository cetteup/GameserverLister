import json
import logging
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from random import randint, choices
from typing import Callable, List, Tuple

import gevent
import requests
from gevent.pool import Pool
from nslookup import Nslookup
from pyq3serverlist import PrincipalServer, PyQ3SLError, PyQ3SLTimeoutError

from src.constants import BATTLELOG_GAME_BASE_URIS, GSLIST_CONFIGS, QUAKE3_CONFIGS, GAMESPY_PRINCIPALS, \
    GAMETOOLS_BASE_URI
from src.helpers import find_query_port, bfbc2_server_validator, parse_raw_server_info, battlelog_server_validator, \
    guid_from_ip_port, mohwf_server_validator, is_valid_port, is_valid_public_ip


class ServerLister:
    game: str
    server_list_dir_path: str
    server_list_file_path: str
    expired_ttl: int
    server_uid_key: str = 'guid'
    ensure_ascii: bool = True
    servers: list = []

    def __init__(self, game: str, expired_ttl: int, list_dir: str):
        self.game = game.lower()
        self.server_list_dir_path = os.path.realpath(list_dir)
        self.server_list_file_path = os.path.join(self.server_list_dir_path, f'{self.game}-servers.json')

        self.expired_ttl = expired_ttl

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
            with open(self.server_list_file_path, 'r') as serverListFile:
                logging.info('Reading servers from existing server list')
                self.servers = json.load(serverListFile)

    def update_server_list(self):
        pass

    def add_update_servers(self, found_servers: list):
        # Add/update found servers to/in known servers
        logging.info('Updating known server list with found servers')
        for found_server in found_servers:
            known_server_guids = [s[self.server_uid_key] for s in self.servers]
            # Update existing server entry or add new one
            if found_server[self.server_uid_key] in known_server_guids:
                logging.debug(f'Found server {found_server[self.server_uid_key]} already known, updating')
                index = known_server_guids.index(found_server[self.server_uid_key])
                self.servers[index] = {**self.servers[index], **found_server}
            else:
                logging.debug(f'Found server {found_server[self.server_uid_key]} is new, adding')
                # Add new server entry
                self.servers.append(self.build_server_list_dict(found_server))

    def build_server_list_dict(self, server: dict) -> dict:
        return {
            self.server_uid_key: server[self.server_uid_key],
            'ip': server['ip'],
            'queryPort': server['queryPort'],
            'firstSeenAt': server['lastSeenAt'],
            'lastSeenAt': server['lastSeenAt']
        }

    def remove_expired_servers(self) -> tuple:
        # Iterate over copy of server list and remove any expired servers from the (actual) server list
        logging.info(f'Checking server expiration ttl for {len(self.servers)} servers')
        expired_servers_removed = 0
        for index, server in enumerate(self.servers[:]):
            last_seen_at = (datetime.fromisoformat(server['lastSeenAt'])
                            if 'lastSeenAt' in server.keys() else datetime.min).astimezone()
            if datetime.now().astimezone() > last_seen_at + timedelta(hours=self.expired_ttl):
                logging.debug(f'Server {server[self.server_uid_key]} has not been seen in'
                              f' {self.expired_ttl} hours, removing it')
                self.servers.remove(server)
                expired_servers_removed += 1

        return expired_servers_removed,

    def write_to_file(self):
        logging.info(f'Writing {len(self.servers)} servers to output file')
        with open(self.server_list_file_path, 'w') as output_file:
            json.dump(self.servers, output_file, indent=2, ensure_ascii=self.ensure_ascii)


class GameSpyServerLister(ServerLister):
    principal: str
    gslist_config: dict
    gslist_bin_path: str
    gslist_filter: str
    gslist_super_query: bool
    gslist_timeout: int

    def __init__(self, game: str, principal: str, gslist_bin_path: str, gslist_filter: str, gslist_super_query: bool,
                 gslist_timeout: int, expired_ttl: int, list_dir: str):
        super().__init__(game, expired_ttl, list_dir)
        self.principal = principal.lower()
        self.gslist_config = GSLIST_CONFIGS[self.game]
        self.gslist_bin_path = gslist_bin_path
        self.gslist_filter = gslist_filter
        self.gslist_super_query = gslist_super_query
        self.gslist_timeout = gslist_timeout

    def update_server_list(self):
        principal = GAMESPY_PRINCIPALS[self.principal]
        hostname = principal['hostname']
        # Combine game port and principal-specific port offset (defaulting to an offset of 0)
        port = self.gslist_config['port'] + principal.get('portOffset', 0)
        # Manually look up hostname to be able to spread retried across servers
        looker_upper = Nslookup()
        dns_result = looker_upper.dns_lookup(hostname)

        if len(dns_result.answer) == 0:
            logging.error(f'DNS lookup for {hostname} failed, exiting')
            sys.exit(1)

        # Run gslist and capture output
        command_ok = False
        tries = 0
        max_tries = 3
        gslist_result = None
        while not command_ok and tries < max_tries:
            # Alternate between first and last found A record
            server_ip = dns_result.answer[0] if tries % 2 == 0 else dns_result.answer[-1]
            try:
                logging.info(f'Running gslist command against {server_ip}')
                command = [self.gslist_bin_path, '-n', self.gslist_config['gameName'], '-x',
                           f'{server_ip}:{port}', '-Y', self.gslist_config['gameName'], self.gslist_config['gameKey'],
                           '-t', self.gslist_config['encType'], '-f', f'{self.gslist_filter}', '-o', '1']
                timeout = self.gslist_timeout
                # Add super query argument if requested
                if self.gslist_super_query:
                    command.extend(['-Q', self.gslist_config['superQueryType']])
                    # Extend timeout to account for server queries
                    timeout += 10
                gslist_result = subprocess.run(command, capture_output=True,
                                               cwd=self.server_list_dir_path, timeout=timeout)
                command_ok = True
            except subprocess.TimeoutExpired as e:
                logging.debug(e)
                logging.error(f'gslist timed out, try {tries + 1}/{max_tries}')
                tries += 1

        # Make sure any server were found
        # (gslist sends all output to stderr so check there)
        if gslist_result is None or 'servers found' not in str(gslist_result.stderr):
            logging.error('gslist could not retrieve any servers, exiting')
            sys.exit(1)

        # Read gslist output file
        logging.info('Reading gslist output file')
        with open(os.path.join(self.server_list_dir_path, f'{self.gslist_config["gameName"]}.gsl'), 'r') as gslist_file:
            raw_server_list = gslist_file.read()

        # Parse server list
        # List format: [ip-address]:[port]
        logging.info('Parsing server list')
        found_servers = []
        for line in raw_server_list.splitlines():
            ip, query_port = line.strip().split(':', 1)
            # Stop parsing once we reach the first line with query server data
            if len(query_port) > 5:
                break

            if not is_valid_public_ip(ip) or not is_valid_port(int(query_port)):
                logging.warning(f'Principal returned invalid server entry ({ip}:{query_port}), skipping it')
                continue

            found_servers.append({
                self.server_uid_key: guid_from_ip_port(ip, query_port),
                'ip': ip,
                'queryPort': int(query_port),
                'lastSeenAt': datetime.now().astimezone().isoformat()
            })

        self.add_update_servers(found_servers)


class FrostbiteServerLister(ServerLister):
    server_validator: Callable = lambda: True

    def __init__(self, game: str, expired_ttl: int, list_dir: str):
        super().__init__(game, expired_ttl, list_dir)

    def build_server_list_dict(self, server: dict) -> dict:
        return {
            self.server_uid_key: server[self.server_uid_key],
            'name': server['name'],
            'ip': server['ip'],
            'gamePort': server['gamePort'],
            'queryPort': -1,
            'firstSeenAt': server['lastSeenAt'],
            'lastSeenAt': server['lastSeenAt'],
            'lastQueriedAt': ''
        }

    def find_query_ports(self, gamedig_bin_path: str, gamedig_concurrency: int, expired_ttl: int):
        logging.info(f'Searching query port for {len(self.servers)} servers')

        search_stats = {
            'totalSearches': len(self.servers),
            'queryPortFound': 0,
            'queryPortReset': 0
        }
        pool = Pool(gamedig_concurrency)
        jobs = []
        for server in self.servers:
            ports_to_try = self.build_port_to_try_list(server['gamePort'])

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
            logging.debug(f'Checking query port search result for {server[self.server_uid_key]}')
            if job.value != -1:
                logging.debug(f'Query port found ({job.value}), updating server')
                server['queryPort'] = job.value
                server['lastQueriedAt'] = datetime.now().astimezone().isoformat()
                search_stats['queryPortFound'] += 1
            elif server['queryPort'] != -1 and \
                    (server.get('lastQueriedAt', '') == '' or
                     datetime.now().astimezone() > datetime.fromisoformat(server['lastQueriedAt']) + timedelta(hours=expired_ttl)):
                logging.debug(f'Query port expired, resetting to -1 (was {server["queryPort"]})')
                server['queryPort'] = -1
                search_stats['queryPortReset'] += 1
        logging.info(f'Query port search stats: {search_stats}')

    # Function has to be public to overrideable by derived classes
    def build_port_to_try_list(self, game_port: int) -> list:
        pass


class BC2ServerLister(FrostbiteServerLister):
    ealist_bin_path: str
    username: str
    password: str
    use_wine: bool

    def __init__(self, ealist_bin_path: str, username: str, password: str, expired_ttl: int,
                 list_dir: str, use_wine: bool):
        super().__init__('bfbc2', expired_ttl, list_dir)
        self.ealist_bin_path = ealist_bin_path
        self.username = username
        self.password = password
        self.use_wine = use_wine
        self.server_validator = bfbc2_server_validator

    def update_server_list(self):
        # Run ealist and capture output
        command_ok = False
        tries = 0
        max_tries = 3
        ealist_result = None
        while not command_ok and tries < max_tries:
            try:
                logging.info(f'Running ealist command')
                command = [self.ealist_bin_path, '-n', 'bfbc2-pc-server', '-a', self.username, self.password,
                           'mohair-pc', '-X', 'none', '-o', '1']
                # Prefix command with wine call if requested
                if self.use_wine:
                    command.insert(0, '/usr/bin/wine')

                ealist_result = subprocess.run(command, capture_output=True, cwd=self.server_list_dir_path, timeout=10)
                command_ok = True
            except subprocess.TimeoutExpired as e:
                logging.debug(e)
                logging.error(f'ealist timed out, try {tries + 1}/{max_tries}')
                tries += 1

        # Make sure any server were found
        # (ealist sends all output to stderr so check there)
        if ealist_result is None or 'servers found' not in str(ealist_result.stderr):
            logging.error('ealist could not retrieve any servers, exiting')
            sys.exit(1)

        # Read ealist output file
        logging.info('Reading ealist output file')
        gsl_file_path = os.path.join(self.server_list_dir_path, 'bfbc2-pc-server.gsl')
        with open(gsl_file_path, 'r') as ealist_file:
            raw_server_list = ealist_file.read()

        # Parse server list
        # List format: [ip-address]:[port]
        logging.info('Parsing server list')
        found_servers = []
        for line in raw_server_list.splitlines():
            raw_server_info = line.strip().split(' ', 1)[1]
            parsed = parse_raw_server_info(raw_server_info)
            found_servers.append({
                self.server_uid_key: guid_from_ip_port(parsed['hostaddr'], parsed['hostport']),
                'name': parsed['hostname'],
                'ip': parsed['hostaddr'],
                'gamePort': int(parsed['hostport']),
                'lastSeenAt': datetime.now().astimezone().isoformat()
            })

        self.add_update_servers(found_servers)

    def build_port_to_try_list(self, game_port: int) -> list:
        """
        Most Bad Company 2 server seem to be hosted directly by members of the community, resulting in pretty random
        query ports as well as strange/incorrect server configurations. So, try a bunch of ports and validate found
        query ports using the connect property OR the server name
        Order of ports to try:
        1. default query port
        2. game port + default port offset (mirror gamedig behavior)
        3. game port (some servers use same port for game + query)
        4. game port + 100 (nitrado)
        5. game port + 10
        6. game port + 5 (several hosters)
        7. game port + 1
        8. game port + 29233 (i3D.net)
        9. game port + 29000
        10. game port + 29323
        11. random port around default query port
        12. random port around 48600
        13. random port between default game port and default query port
        14. random port between game port and game port + default offset
        """
        ports_to_try = [48888, game_port + 29321, game_port, game_port + 100, game_port + 10, game_port + 5,
                        game_port + 1, game_port + 29233, game_port + 29000, game_port + 29323, randint(48880, 48890),
                        randint(48601, 48605), randint(19567, 48888), randint(game_port, game_port + 29321)]

        return ports_to_try


class FrostbiteHttpServerLister(FrostbiteServerLister):
    page_limit: int
    per_page: int
    sleep: float
    max_attempts: int
    session: requests.Session

    def __init__(self, game: str, page_limit: int, per_page: int, expired_ttl: int, list_dir: str, sleep: float,
                 max_attempts: int):
        super().__init__(game, expired_ttl, list_dir)
        self.page_limit = page_limit
        self.per_page = per_page
        self.sleep = sleep
        self.max_attempts = max_attempts

        # Init session
        self.session = requests.session()

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
                    timeout=10
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

    def add_page_found_servers(self, found_servers: List[dict], page_response_data: dict) -> List[dict]:
        pass

    def remove_expired_servers(self) -> tuple:
        # Iterate over copy of server list and remove any expired servers from the (actual) server list
        logging.info(f'Checking server expiration ttl for {len(self.servers)} servers')
        requests_since_last_ok = 0
        expired_servers_removed = 0
        expired_servers_recovered = 0
        for index, server in enumerate(self.servers[:]):
            last_seen_at = (datetime.fromisoformat(server['lastSeenAt'])
                            if 'lastSeenAt' in server.keys() else datetime.min).astimezone()
            if datetime.now().astimezone() > last_seen_at + timedelta(hours=self.expired_ttl):
                time.sleep(1 + pow(self.sleep, requests_since_last_ok % self.max_attempts))
                # Check if server can be accessed directly
                request_ok, found, requests_since_last_ok = self.check_if_server_still_exists(
                    server, requests_since_last_ok
                )

                # Remove server if request was sent successfully but server was not found
                if request_ok and not found:
                    logging.debug(f'Server {server[self.server_uid_key]} has not been seen in '
                                  f'{self.expired_ttl} hours, removing it')
                    self.servers.remove(server)
                    expired_servers_removed += 1
                elif request_ok and found:
                    logging.debug(f'Server {server[self.server_uid_key]} did not appear in list but is still online, '
                                  f'updating last seen at')
                    self.servers[self.servers.index(server)]['lastSeenAt'] = datetime.now().astimezone().isoformat()
                    expired_servers_recovered += 1

        return expired_servers_removed, expired_servers_recovered

    def check_if_server_still_exists(self, server: dict, requests_since_last_ok: int) -> Tuple[bool, bool, int]:
        pass


class BattlelogServerLister(FrostbiteHttpServerLister):
    def __init__(self, game: str, page_limit: int, expired_ttl: int, list_dir: str,
                 sleep: float, max_attempts: int, proxy: str = None):
        super().__init__(game, page_limit, 60, expired_ttl, list_dir, sleep, max_attempts)
        self.page_limit = page_limit
        self.sleep = sleep
        self.max_attempts = max_attempts
        # Medal of Honor: Warfighter servers return the query port as part of the connect string, not the game port
        # => use different validator
        if self.game == 'mohwf':
            self.server_validator = mohwf_server_validator
        else:
            self.server_validator = battlelog_server_validator

        # Init session
        self.session = requests.session()
        # Set up headers
        self.session.headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }
        # Set up proxy if given
        if proxy is not None:
            # All requests are sent via https, so just set up https proxy
            self.session.proxies = {
                'https': proxy
            }

    def get_server_list_url(self, per_page: int) -> str:
        return f'{BATTLELOG_GAME_BASE_URIS[self.game]}?count={per_page}&offset=0'

    def add_page_found_servers(self, found_servers: List[dict], page_response_data: dict) -> List[dict]:
        for server in page_response_data['data']:
            found_server = {
                self.server_uid_key: server['guid'],
                'name': server['name'],
                'ip': server['ip'],
                'gamePort': server['port'],
                'lastSeenAt': datetime.now().astimezone().isoformat()
            }
            # Add non-private servers (servers with an IP) that are new
            server_guids = [s[self.server_uid_key] for s in found_servers]
            if len(found_server['ip']) > 0 and found_server[self.server_uid_key] not in server_guids:
                logging.debug(f'Got new server {server[self.server_uid_key]}, adding it')
                found_servers.append(found_server)
            elif len(found_server['ip']) > 0:
                logging.debug(f'Got duplicate server {server[self.server_uid_key]}, updating last seen at')
                index = server_guids.index(found_server[self.server_uid_key])
                found_servers[index]['lastSeenAt'] = datetime.now().astimezone().isoformat()
            else:
                logging.debug(f'Got private server {server[self.server_uid_key]}, ignoring it')

        return found_servers

    def check_if_server_still_exists(self, server: dict, requests_since_last_ok: int) -> Tuple[bool, bool, int]:
        request_ok = True
        found = False
        try:
            response = self.session.get(f'https://battlelog.battlefield.com/{self.game}/'
                                        f'servers/show/pc/{server[self.server_uid_key]}?json=1', timeout=10)
            if response.status_code == 200:
                # Server was found on Battlelog => make sure it is still public
                parsed = response.json()
                found = parsed['message']['SERVER_INFO']['ip'] != ''
            elif response.status_code == 422:
                # Battlelog responded with 422, explicitly indicating that the server was not found
                found = False
            else:
                # Battlelog responded with some other status code (rate limit 403 for example)
                # => treat server as found
                found = True
            # Reset requests since last ok counter if server returned info/not found,
            # else increase counter and sleep
            if response.status_code in [200, 422]:
                requests_since_last_ok = 0
            else:
                requests_since_last_ok += 1
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.error(f'Failed to fetch server {server[self.server_uid_key]} for expiration check')
            request_ok = False

        return request_ok, found, requests_since_last_ok

    def build_port_to_try_list(self, game_port: int) -> list:
        """
                Order of ports to try:
                1. default query port
                2. game port + default port offset (mirror gamedig behavior)
                3. game port (some servers use same port for game + query)
                4. game port + 100 (nitrado)
                5. game port + 5 (several hosters)
                6. 48888 (gamed)
                7. game port + 6 (i3D)
                8. game port + 8 (i3D)
                9. game port + 15 (i3D)
                10. game port - 5 (i3D)
                11. game port - 15 (i3D)
                12. game port - 23000 (G4G.pl)
                """
        ports_to_try = [47200, game_port + 22000, game_port, game_port + 100, game_port + 5, game_port + 1,
                        48888, game_port + 6, game_port + 8, game_port + 15, game_port - 5, game_port - 15,
                        game_port - 23000]

        return ports_to_try


class GametoolsServerLister(FrostbiteHttpServerLister):
    # Use gameId as server uid
    server_uid_key: str = 'gameId'
    # Allow non-ascii characters in server list (mostly used by server names for Asia servers)
    ensure_ascii: bool = False

    include_official: bool

    def __init__(self, game: str, page_limit: int, expired_ttl: int, list_dir: str, sleep: float, max_attempts: int,
                 include_official: bool):
        super().__init__(game, page_limit, 100, expired_ttl, list_dir, sleep, max_attempts)
        self.page_limit = page_limit
        self.sleep = sleep
        self.max_attempts = max_attempts
        self.include_official = include_official

        # Init session
        self.session = requests.session()

    def get_server_list_url(self, per_page: int) -> str:
        return f'{GAMETOOLS_BASE_URI}/{self.game}/servers/?name=&limit={per_page}' \
               f'&nocache={datetime.now().timestamp()}'

    def add_page_found_servers(self, found_servers: List[dict], page_response_data: dict) -> List[dict]:
        for server in page_response_data['servers']:
            found_server = {
                self.server_uid_key: server['gameId'],
                'name': server['prefix'],
                'lastSeenAt': datetime.now().astimezone().isoformat()
            }
            # Add/update servers (ignoring official servers unless include_official is set)
            server_game_ids = [s[self.server_uid_key] for s in found_servers]
            if found_server[self.server_uid_key] not in server_game_ids and \
                    (not server['official'] or self.include_official):
                logging.debug(f'Got new server {server[self.server_uid_key]}, adding it')
                found_servers.append(found_server)
            elif not server['official'] or self.include_official:
                logging.debug(f'Got duplicate server {server[self.server_uid_key]}, updating last seen at')
                index = server_game_ids.index(found_server[self.server_uid_key])
                found_servers[index]['lastSeenAt'] = datetime.now().astimezone().isoformat()
            else:
                logging.debug(f'Got official server {server[self.server_uid_key]}, ignoring it')

        return found_servers

    def check_if_server_still_exists(self, server: dict, requests_since_last_ok: int) -> Tuple[bool, bool, int]:
        request_ok = True
        found = False
        try:
            response = self.session.get(f'{GAMETOOLS_BASE_URI}/{self.game}/detailedserver/'
                                        f'?gameid={server[self.server_uid_key]}', timeout=10)
            if response.status_code == 200:
                # Server was found on gametools => make sure it still not official (or include_official is set)
                parsed = response.json()
                found = not parsed['official'] or self.include_official
            elif response.status_code == 404:
                # gametools responded with, server was not found
                found = False
            else:
                # gametools responded with some other status code (504 gateway timeout for example)
                # => treat server as found
                found = True
            # Reset requests since last ok counter if server returned info/not found,
            # else increase counter and sleep
            if response.status_code in [200, 404]:
                requests_since_last_ok = 0
            else:
                requests_since_last_ok += 1
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.error(f'Failed to fetch server {server[self.server_uid_key]} for expiration check')
            request_ok = False

        return request_ok, found, requests_since_last_ok

    def build_server_list_dict(self, server: dict) -> dict:
        return {
            self.server_uid_key: server[self.server_uid_key],
            'name': server['name'],
            'firstSeenAt': server['lastSeenAt'],
            'lastSeenAt': server['lastSeenAt']
        }


class Quake3ServerLister(ServerLister):
    principal: PrincipalServer
    protocol: int
    game_name: str
    keywords: str
    server_entry_prefix: bytes

    def __init__(self, game: str, principal_server: str, expired_ttl: int, list_dir: str):
        super().__init__(game, expired_ttl, list_dir)
        # Merge default config with given principal config
        default_config = {
            'keywords': 'full empty',
            'game_name': '',
            'network_protocol': socket.SOCK_DGRAM,
            'server_entry_prefix': b''
        }
        principal_config = {key: value for (key, value) in QUAKE3_CONFIGS[self.game].items()
                            if key in default_config.keys()}
        keywords, game_name, network_protocol, server_entry_prefix = {**default_config, **principal_config}.values()
        hostname, port = QUAKE3_CONFIGS[self.game]['servers'][principal_server].values()
        self.principal = PrincipalServer(hostname, port, network_protocol)
        self.protocol = QUAKE3_CONFIGS[self.game]['protocol']
        self.game_name = game_name
        self.keywords = keywords
        self.server_entry_prefix = server_entry_prefix

    def update_server_list(self):
        query_ok = False
        attempt = 0
        max_attempts = 3
        found_servers = []
        while not query_ok and attempt < max_attempts:
            try:
                # Get servers
                found_servers = self.principal.get_servers(self.protocol, self.game_name,
                                                           self.keywords, self.server_entry_prefix)
                query_ok = True
            except PyQ3SLTimeoutError:
                logging.error(f'Principal server query timed out, attempt {attempt + 1}/{max_attempts}')
                attempt += 1
            except PyQ3SLError as e:
                logging.debug(e)
                logging.error(f'Failed to query principal server, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        # Create servers dicts, adding required attributes
        found_server_dicts = []
        for found_server in found_servers:
            found_server_dicts.append({
                self.server_uid_key: guid_from_ip_port(found_server.ip, str(found_server.port)),
                'ip': found_server.ip,
                'queryPort': found_server.port,
                'lastSeenAt': datetime.now().astimezone().isoformat()
            })

        self.add_update_servers(found_server_dicts)
