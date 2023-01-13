import json
import logging
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from random import randint, choices
from typing import Callable, List, Tuple, Type, Optional, Union

import gevent
import pyq3serverlist
import pyut2serverlist
import pyvpsq
import requests
from gevent.pool import Pool
from nslookup import Nslookup

from src.constants import BATTLELOG_GAME_BASE_URIS, GAMESPY_GAME_CONFIGS, QUAKE3_CONFIGS, GAMESPY_PRINCIPAL_CONFIGS, \
    GAMETOOLS_BASE_URI, UNREAL2_CONFIGS, VALVE_GAME_CONFIGS, VALVE_PRINCIPAL_CONFIGS
from src.helpers import find_query_port, bfbc2_server_validator, battlelog_server_validator, \
    guid_from_ip_port, mohwf_server_validator, is_valid_port, is_valid_public_ip, is_server_for_gamespy_game, \
    is_server_listed_on_gametracker
from src.servers import Server, ClassicServer, FrostbiteServer, Bfbc2Server, GametoolsServer, ObjectJSONEncoder, \
    ViaStatus, WebLink
from src.types import GamespyGameConfig, GamespyGame, GamespyPrincipal, Game, Quake3Game, BattlelogGame, GametoolsGame, \
    MedalOfHonorGame, TheaterGame, Unreal2Game, ValveGame, ValvePrincipal, ValveGameConfig
from src.weblinks import WEB_LINK_TEMPLATES


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
                    logging.info('Reading servers from existing server list')
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
        logging.info(f'Updating known server list with {len(found_servers)} found servers')
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
        logging.info(f'Checking server expiration ttl for {len(self.servers)} servers')
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

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        pass

    def get_backoff_timeout(self, checks_since_last_ok: int) -> int:
        # Default to no backoff
        return 0

    def write_to_file(self):
        logging.info(f'Writing {len(self.servers)} servers to output file')
        with open(self.server_list_file_path, 'w') as output_file:
            json.dump(self.servers, output_file, indent=2, ensure_ascii=self.ensure_ascii, cls=ObjectJSONEncoder)


class GameSpyServerLister(ServerLister):
    game: GamespyGame
    servers: List[ClassicServer]
    principal: GamespyPrincipal
    config: GamespyGameConfig
    gslist_bin_path: str
    gslist_filter: str
    gslist_super_query: bool
    gslist_timeout: int
    verify: bool

    def __init__(
            self,
            game: GamespyGame,
            principal: GamespyPrincipal,
            gslist_bin_path: str,
            gslist_filter: str,
            gslist_super_query: bool,
            gslist_timeout: int,
            verify: bool,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str
    ):
        super().__init__(game, ClassicServer, expired_ttl, recover, add_links, list_dir)
        self.principal = principal.lower()
        self.config = GAMESPY_GAME_CONFIGS[self.game]
        self.gslist_bin_path = gslist_bin_path
        self.gslist_filter = gslist_filter
        self.gslist_super_query = gslist_super_query
        self.gslist_timeout = gslist_timeout
        self.verify = verify

    def update_server_list(self):
        principal = GAMESPY_PRINCIPAL_CONFIGS[self.principal]
        # Format hostname using game name (following old GameSpy format [game].master.gamespy.com)
        hostname = principal.hostname.format(self.config.game_name)
        # Combine game port and principal-specific port offset (defaults to an offset of 0)
        port = self.config.port + principal.get_port_offset()
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
                command = [self.gslist_bin_path, '-n', self.config.game_name, '-x',
                           f'{server_ip}:{port}', '-Y', self.config.game_name, self.config.game_key,
                           '-t', str(self.config.enc_type), '-f', f'{self.gslist_filter}', '-o', '1']
                timeout = self.gslist_timeout
                # Some principals do not respond with the default query list type byte (1),
                # so we need to explicitly set a different type byte
                if self.config.list_type is not None:
                    command.extend(['-T', str(self.config.list_type)])
                # Some principals do not respond unless an info query is sent (e.g. FH2 principal)
                if self.config.info_query is not None:
                    command.extend(['-X', self.config.info_query])
                # Add super query argument if requested
                if self.gslist_super_query:
                    command.extend(['-Q', str(self.config.query_type)])
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
        with open(os.path.join(self.server_list_dir_path, f'{self.config.game_name}.gsl'), 'r') as gslist_file:
            raw_server_list = gslist_file.read()

        # Parse server list
        # List format: [ip-address]:[port]
        logging.info(f'Parsing server list{" and verifying servers" if self.verify else ""}')
        found_servers = []
        for line in raw_server_list.splitlines():
            connect, *_ = line.split(' ', 1)
            ip, query_port = connect.strip().split(':', 1)

            if not is_valid_public_ip(ip) or not is_valid_port(int(query_port)):
                logging.warning(f'Principal returned invalid server entry ({ip}:{query_port}), skipping it')
                continue

            via = ViaStatus(self.principal)
            found_server = ClassicServer(
                guid_from_ip_port(ip, query_port),
                ip,
                int(query_port),
                via
            )

            if self.verify or self.add_links:
                # Attempt to query server in order to verify is a server for the current game
                # (some principals return servers for other games than what we queried)
                logging.debug(f'Querying server {found_server.uid}/{found_server.ip}:{found_server.query_port}')
                responded, query_response = self.query_server(found_server)
                logging.debug(f'Query {"was successful" if responded else "did not receive a response"}')

                if responded and self.verify and \
                        not is_server_for_gamespy_game(self.game, self.config.game_name, query_response):
                    logging.warning(f'Server does not seem to be a {self.game} server, ignoring it '
                                    f'({found_server.ip}:{found_server.query_port})')
                    continue

                if responded and 'hostport' in query_response and self.add_links:
                    found_server.add_links(self.build_server_links(
                        found_server.uid,
                        found_server.ip,
                        int(query_response['hostport'])
                    ))

            found_servers.append(found_server)

        self.add_update_servers(found_servers)

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        # Since we query the server directly, there is no way of handling HTTP server errors differently then
        # actually failed checks, so even if the query fails, we have to treat it as "check ok"
        check_ok = True
        responded, query_response = self.query_server(server)
        # Treat as server for game if verify is turned off
        server_for_game = not self.verify or is_server_for_gamespy_game(self.game, self.config.game_name, query_response)
        found = responded and server_for_game
        if responded and not server_for_game:
            logging.warning(f'Server {server.uid} does not seem to be a {self.game} server, treating as not found')

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        template_refs = self.config.link_template_refs if self.config.link_template_refs is not None else {}
        # Add principal-scoped links first, then add game-scoped links
        templates = [
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get(self.principal, [])],
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get('_any', [])]
        ]

        # Add GameTracker link if server is listed there
        if is_server_listed_on_gametracker(self.game, ip, port):
            templates.append(WEB_LINK_TEMPLATES['gametracker'])

        links = []
        for template in templates:
            links.append(template.render(self.game, uid, ip=ip, port=port))

        return links

    def query_server(self, server: ClassicServer) -> Tuple[bool, dict]:
        try:
            command = [self.gslist_bin_path, '-d', str(self.config.query_type), server.ip, str(server.query_port), '-0']
            # Timeout should never fire since gslist uses about a three-second timeout for the query
            gslist_result = subprocess.run(command, capture_output=True, timeout=self.gslist_timeout)

            # gslist will simply return an empty byte string (b'') if the server could not be queried
            if gslist_result.stdout != b'' and b'error' not in gslist_result.stderr.lower():
                parsed = {}
                for line in gslist_result.stdout.decode('latin1').strip('\n').split('\n'):
                    elements = line.lstrip().split(' ', 1)
                    if len(elements) != 2:
                        continue
                    key, value = elements
                    parsed[key.lower()] = value
                return True, parsed
        except subprocess.TimeoutExpired as e:
            logging.debug(e)
            logging.error(f'Failed to query server {server.uid} for expiration check')

        return False, {}


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


class BC2ServerLister(FrostbiteServerLister):
    game: TheaterGame

    def __init__(self, expired_ttl: float, recover: bool, add_links: bool, list_dir: str, timeout: float):
        super().__init__(TheaterGame.BFBC2, Bfbc2Server, expired_ttl, recover, add_links, list_dir, timeout)
        self.server_validator = bfbc2_server_validator

    def update_server_list(self):
        request_ok = False
        attempt = 0
        max_attempts = 3
        servers = None
        while not request_ok and attempt < max_attempts:
            try:
                logging.info(f'Fetching server list from FESL/Theater API')
                resp = self.session.get('https://fesl.cetteup.com/servers/pc', timeout=self.request_timeout)

                if resp.ok:
                    servers = resp.json()
                    request_ok = True
                else:
                    attempt += 1
            except requests.exceptions.RequestException as e:
                logging.debug(e)
                logging.error(f'Failed to fetch servers from API, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        # Make sure any servers were found
        if servers is None:
            logging.error('Failed to retrieve server list, exiting')
            sys.exit(1)

        # Add servers from list
        found_servers = []
        for server in servers:
            found_server = Bfbc2Server(
                guid_from_ip_port(server['I'], server['P']),
                server['N'],
                int(server['LID']),
                int(server['GID']),
                server['I'],
                int(server['P'])
            )

            if self.add_links:
                found_server.add_links(self.build_server_links(
                    found_server.uid,
                    found_server.ip,
                    found_server.game_port
                ))

            found_servers.append(found_server)

        self.add_update_servers(found_servers)

    def check_if_server_still_exists(self, server: Bfbc2Server, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        check_ok = True
        found = False
        try:
            response = self.session.get(f'https://fesl.cetteup.com/servers/pc/{server.lid}/{server.gid}',
                                        timeout=self.request_timeout)

            if response.ok:
                found = True
            elif response.status_code == 404:
                found = False
            else:
                check_ok = False
            # Reset requests since last ok counter if server returned info/not found,
            # else increase counter and sleep
            if check_ok:
                checks_since_last_ok = 0
            else:
                checks_since_last_ok += 1
        except requests.RequestException as e:
            logging.debug(e)
            logging.error(f'Failed to fetch server {server.uid} for expiration check')
            check_ok = False

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        links = []
        if is_server_listed_on_gametracker(self.game, ip, port):
            links.append(WEB_LINK_TEMPLATES['gametracker'].render(self.game, uid, ip=ip, port=port))

        return links

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


class BattlelogServerLister(HttpServerLister, FrostbiteServerLister):
    game: BattlelogGame

    def __init__(
            self,
            game: BattlelogGame,
            page_limit: int,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str,
            sleep: float,
            max_attempts: int,
            proxy: str = None
    ):
        super().__init__(game, FrostbiteServer, page_limit, 60, expired_ttl, recover, add_links, list_dir, sleep, max_attempts)
        # Medal of Honor: Warfighter servers return the query port as part of the connect string, not the game port
        # => use different validator
        if self.game is BattlelogGame.MOHWF:
            self.server_validator = mohwf_server_validator
        else:
            self.server_validator = battlelog_server_validator

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

    def add_page_found_servers(self, found_servers: List[FrostbiteServer], page_response_data: dict) -> List[FrostbiteServer]:
        for server in page_response_data['data']:
            found_server = FrostbiteServer(
                server['guid'],
                server['name'],
                server['ip'],
                server['port'],
            )

            if self.add_links:
                found_server.add_links(self.build_server_links(found_server.uid))
                # Gametools uses the gameid for BF4 server URLs, so add that separately
                if self.game is BattlelogGame.BF4:
                    found_server.add_links(WEB_LINK_TEMPLATES['gametools'].render(self.game, server['gameId']))

            # Add non-private servers (servers with an IP) that are new
            server_uids = [s.uid for s in found_servers]
            if len(found_server.ip) > 0 and found_server.uid not in server_uids:
                logging.debug(f'Got new server {found_server.uid}, adding it')
                found_servers.append(found_server)
            elif len(found_server.ip) > 0:
                logging.debug(f'Got duplicate server {found_server.uid}, updating last seen at')
                index = server_uids.index(found_server.uid)
                found_servers[index].last_seen_at = datetime.now().astimezone()
            else:
                logging.debug(f'Got private server {found_server.uid}, ignoring it')

        return found_servers

    def check_if_server_still_exists(self, server: FrostbiteServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        check_ok = True
        found = False
        try:
            response = self.session.get(f'https://battlelog.battlefield.com/{self.game}/'
                                        f'servers/show/pc/{server.uid}?json=1',
                                        timeout=self.request_timeout)
            if response.status_code == 200:
                # Server was found on Battlelog => make sure it is still public
                # TODO use server validator here
                parsed = response.json()
                found = parsed['message']['SERVER_INFO']['ip'] != ''
            elif response.status_code == 422:
                # Battlelog responded with 422, explicitly indicating that the server was not found
                found = False
            else:
                # Battlelog responded with some other status code (rate limit 403 for example)
                check_ok = False
            # Reset requests since last ok counter if server returned info/not found,
            # else increase counter and sleep
            if check_ok:
                checks_since_last_ok = 0
            else:
                checks_since_last_ok += 1
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.error(f'Failed to fetch server {server.uid} for expiration check')
            check_ok = False

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        # Medal of Honor: Warfighter (mohwf) is just called "mohw" on Battlelog
        game = 'mohw' if self.game is BattlelogGame.MOHWF else self.game
        links = [WEB_LINK_TEMPLATES['battlelog'].render(game, uid)]

        # Gametools uses the guid as the "gameid" for BF3 and BFH, so we can add links for those
        # (BF4 uses the real gameid, so we need to handle those links separately)
        if self.game in ['bf3', 'bfh']:
            links.append(WEB_LINK_TEMPLATES['gametools'].render(self.game, uid))

        return links

    def build_port_to_try_list(self, game_port: int) -> list:
        """
                Order of ports to try:
                1. default query port
                2. game port + default port offset (mirror gamedig behavior)
                3. game port (some servers use same port for game + query)
                4. game port + 100 (nitrado)
                5. game port + 5 (several hosters)
                6. 48888 (gamed)
                7. game port + 50
                8. game port + 6 (i3D)
                9. game port + 8 (i3D)
                10. game port + 15 (i3D)
                11. game port - 5 (i3D)
                12. game port - 15 (i3D)
                13. game port - 23000 (G4G.pl)
                """
        ports_to_try = [47200, game_port + 22000, game_port, game_port + 100, game_port + 5, game_port + 1,
                        48888, game_port + 6, game_port + 8, game_port + 15, game_port - 5, game_port - 15,
                        game_port - 23000]

        return ports_to_try


class GametoolsServerLister(HttpServerLister):
    game: GametoolsGame
    include_official: bool

    def __init__(
            self,
            game: GametoolsGame,
            page_limit: int,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str,
            sleep: float,
            max_attempts: int,
            include_official: bool
    ):
        super().__init__(game, GametoolsServer, page_limit, 100, expired_ttl, recover, add_links, list_dir, sleep,
                         max_attempts)
        # Allow non-ascii characters in server list (mostly used by server names for Asia servers)
        self.ensure_ascii = False
        self.include_official = include_official

    def get_server_list_url(self, per_page: int) -> str:
        return f'{GAMETOOLS_BASE_URI}/{self.game}/servers/?name=&limit={per_page}' \
               f'&nocache={datetime.now().timestamp()}'

    def add_page_found_servers(self, found_servers: List[GametoolsServer], page_response_data: dict) -> List[GametoolsServer]:
        for server in page_response_data['servers']:
            found_server = GametoolsServer(
                server['gameId'],
                server['prefix'],
            )

            if self.add_links:
                found_server.add_links(self.build_server_links(found_server.uid))

            # Add/update servers (ignoring official servers unless include_official is set)
            server_game_ids = [s.uid for s in found_servers]
            if found_server.uid not in server_game_ids and \
                    (not server['official'] or self.include_official):
                logging.debug(f'Got new server {found_server.uid}, adding it')
                found_servers.append(found_server)
            elif not server['official'] or self.include_official:
                logging.debug(f'Got duplicate server {found_server.uid}, updating last seen at')
                index = server_game_ids.index(found_server.uid)
                found_servers[index].last_seen_at = datetime.now().astimezone()
            else:
                logging.debug(f'Got official server {found_server.uid}, ignoring it')

        return found_servers

    def check_if_server_still_exists(self, server: GametoolsServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        check_ok = True
        found = False
        try:
            response = self.session.get(f'{GAMETOOLS_BASE_URI}/{self.game}/detailedserver/'
                                        f'?gameid={server.uid}', timeout=self.request_timeout)
            if response.status_code == 200:
                # Server was found on gametools => make sure it still not official (or include_official is set)
                parsed = response.json()
                found = not parsed['official'] or self.include_official
            elif response.status_code == 404:
                # gametools responded with, server was not found
                found = False
            else:
                # gametools responded with some other status code (504 gateway timeout for example)
                check_ok = False
            # Reset requests since last ok counter if server returned info/not found,
            # else increase counter and sleep
            if check_ok:
                checks_since_last_ok = 0
            else:
                checks_since_last_ok += 1
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.error(f'Failed to fetch server {server.uid} for expiration check')
            check_ok = False

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        links = [WEB_LINK_TEMPLATES['gametools'].render(self.game, uid)]
        # BF1 servers are also listed on battlefieldtracker.com
        if self.game is GametoolsGame.BF1:
            links.append(WEB_LINK_TEMPLATES['battlefieldtracker'].render(self.game, uid))

        return links


class Quake3ServerLister(ServerLister):
    game: Quake3Game
    principal: str
    protocols: List[int]
    network_protocol: int
    game_name: str
    keywords: str
    server_entry_prefix: bytes

    def __init__(self, game: Quake3Game, principal: str, expired_ttl: float, recover: bool, add_links: bool, list_dir: str):
        super().__init__(game, ClassicServer, expired_ttl, recover, add_links, list_dir)
        # Merge default config with given principal config
        default_config = {
            'keywords': 'full empty',
            'game_name': '',
            'network_protocol': socket.SOCK_DGRAM,
            'server_entry_prefix': b''
        }
        principal_config = {key: value for (key, value) in QUAKE3_CONFIGS[self.game].items()
                            if key in default_config.keys()}
        self.principal = principal
        self.keywords, self.game_name, \
            self.network_protocol, self.server_entry_prefix = {**default_config, **principal_config}.values()
        self.protocols = QUAKE3_CONFIGS[self.game]['protocols']

    def update_server_list(self):
        # Use same connection to principal for all queries
        hostname, port = QUAKE3_CONFIGS[self.game]['servers'][self.principal].values()
        principal = pyq3serverlist.PrincipalServer(hostname, port, self.network_protocol)

        # Fetch servers for all protocols
        found_servers = []
        for protocol in self.protocols:
            raw_servers = self.get_servers(principal, protocol)
            for raw_server in raw_servers:
                if not is_valid_public_ip(raw_server.ip) or not is_valid_port(raw_server.port):
                    logging.warning(
                        f'Principal returned invalid server entry '
                        f'({raw_server.ip}:{raw_server.port}), skipping it'
                    )
                    continue

                via = ViaStatus(self.principal)
                found_server = ClassicServer(
                    guid_from_ip_port(raw_server.ip, str(raw_server.port)),
                    raw_server.ip,
                    raw_server.port,
                    via
                )

                if self.add_links:
                    found_server.add_links(self.build_server_links(
                        found_server.uid,
                        found_server.ip,
                        found_server.query_port
                    ))

                found_servers.append(found_server)

        self.add_update_servers(found_servers)

    def get_servers(self, principal: pyq3serverlist.PrincipalServer, protocol: int) -> List[pyq3serverlist.Server]:
        query_ok = False
        attempt = 0
        max_attempts = 3
        servers = []
        while not query_ok and attempt < max_attempts:
            try:
                servers = principal.get_servers(protocol, self.game_name, self.keywords, self.server_entry_prefix)
                query_ok = True
            except pyq3serverlist.PyQ3SLTimeoutError:
                logging.error(f'Principal server query timed out using protocol {protocol}, '
                              f'attempt {attempt + 1}/{max_attempts}')
                attempt += 1
            except pyq3serverlist.PyQ3SLError as e:
                logging.debug(e)
                logging.error(f'Failed to query principal server using protocol {protocol}, '
                              f'attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        return servers

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        # Since we query the server directly, there is no way of handling HTTP server errors differently then
        # actually failed checks, so even if the query fails, we have to treat it as "check ok"
        check_ok = True
        found = False
        try:
            pyq3serverlist.Server(server.ip, server.query_port).get_status()

            # get_status will raise an exception if the server cannot be contacted,
            # so this will only be reached if the query succeeds
            found = True
        except pyq3serverlist.PyQ3SLError as e:
            logging.debug(e)
            logging.debug(f'Failed to query server {server.uid} for expiration check')

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        template_refs = QUAKE3_CONFIGS[self.game].get('linkTemplateRefs', {})
        # Add principal-scoped links first, then add game-scoped links
        templates = [
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get(self.principal, [])],
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get('_any', [])]
        ]

        # Add GameTracker link if server is listed there
        if is_server_listed_on_gametracker(self.game, ip, port):
            templates.append(WEB_LINK_TEMPLATES['gametracker'])

        links = []
        for template in templates:
            links.append(template.render(self.game, uid, ip=ip, port=port))

        return links


class MedalOfHonorServerLister(ServerLister):
    """
    The defacto standard principal server for Medal of Honor games uses a query GameSpy protocol implementation that
    does not work with gslist. However, they also provide server lists as text files, which unfortunately only contain
    the game port. So, instead of extending the GameSpy server lister and trying to find the query port, we use the
    text files to find servers. Since the Medal of Honor games support Quake3-like queries on the game port, we can use
    that to query servers with the information we have.
    """
    game: MedalOfHonorGame

    def __init__(self, game: MedalOfHonorGame, expired_ttl: float, recover: bool, add_links: bool, list_dir: str):
        super().__init__(game, ClassicServer, expired_ttl, recover, add_links, list_dir)

    def update_server_list(self):
        request_ok = False
        attempt = 0
        max_attempts = 3
        raw_server_list = None
        while not request_ok and attempt < max_attempts:
            try:
                logging.info('Fetching server list from mohaaservers.tk')
                resp = self.session.get(self.get_server_list_url(), timeout=self.request_timeout)

                if resp.ok:
                    raw_server_list = resp.text
                    request_ok = True
                else:
                    attempt += 1
            except requests.exceptions.RequestException as e:
                logging.debug(e)
                logging.error(f'Failed to fetch servers from mohaaservers.tk, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        # Make sure any servers were found
        if raw_server_list is None:
            logging.error('Failed to retrieve server list, exiting')
            sys.exit(1)

        # Parse list
        found_servers = []
        for line in raw_server_list.strip(' \n').split('\n'):
            # Silently skip any completely empty lines
            if len(line) == 0:
                continue

            elems = line.strip().split(':')

            if len(elems) != 2:
                logging.warning(f'Principal returned malformed server list entry ({line}), skipping it')
                continue

            ip, query_port = elems
            if not is_valid_public_ip(ip) or not is_valid_port(int(query_port)):
                logging.warning(f'Principal returned invalid server entry ({ip}:{query_port}), skipping it')
                continue

            via = ViaStatus('mohaaservers.tk')
            found_server = ClassicServer(
                guid_from_ip_port(ip, query_port),
                ip,
                int(query_port),
                via
            )

            if self.add_links:
                # query port = game port for MOH games, so we can use that here to build links
                found_server.add_links(self.build_server_links(
                    found_server.uid,
                    found_server.ip,
                    found_server.query_port
                ))

            found_servers.append(found_server)

        self.add_update_servers(found_servers)

    def get_server_list_url(self) -> str:
        # mohaaservers uses a "key" without the "moh" prefix, e.g. "servers_aa" for "mohaa"
        return f'https://mohaaservers.tk/servlist/servers_{self.game[3:]}.txt'

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        # Since we query the server directly, there is no way of handling HTTP server errors differently then
        # actually failed checks, so even if the query fails, we have to treat it as "check ok"
        check_ok = True
        found = False
        try:
            pyq3serverlist.MedalOfHonorServer(server.ip, server.query_port).get_status()

            # get_status will raise an exception if the server cannot be contacted,
            # so this will only be reached if the query succeeds
            found = True
        except pyq3serverlist.PyQ3SLError as e:
            logging.debug(e)
            logging.debug(f'Failed to query server {server.uid} for expiration check')

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        links = []
        if is_server_listed_on_gametracker(self.game, ip, port):
            links.append(WEB_LINK_TEMPLATES['gametracker'].render(self.game, uid, ip=ip, port=port))

        return links


class Unreal2ServerLister(ServerLister):
    game: Unreal2Game
    principal: str
    cd_key: str

    principal_timeout: float

    def __init__(
            self,
            game: Quake3Game,
            principal: str,
            cd_key: str,
            principal_timeout: float,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str
    ):
        super().__init__(game, ClassicServer, expired_ttl, recover, add_links, list_dir)
        self.principal = principal
        self.cd_key = cd_key
        self.principal_timeout = principal_timeout

    def update_server_list(self):
        hostname, port = UNREAL2_CONFIGS[self.game]['servers'][self.principal].values()
        principal = pyut2serverlist.PrincipalServer(
            hostname,
            port,
            pyut2serverlist.Game(self.game),
            self.cd_key,
            timeout=self.principal_timeout
        )

        found_servers = []
        raw_servers = self.get_servers(principal)
        for raw_server in raw_servers:
            if not is_valid_public_ip(raw_server.ip) or not is_valid_port(raw_server.query_port):
                logging.warning(
                    f'Principal returned invalid server entry '
                    f'({raw_server.ip}:{raw_server.query_port}), skipping it'
                )
                continue

            via = ViaStatus(self.principal)
            found_server = ClassicServer(
                guid_from_ip_port(raw_server.ip, str(raw_server.query_port)),
                raw_server.ip,
                raw_server.query_port,
                via
            )

            if self.add_links:
                found_server.add_links(self.build_server_links(
                    found_server.uid,
                    found_server.ip,
                    raw_server.game_port
                ))

            found_servers.append(found_server)

        self.add_update_servers(found_servers)

    @staticmethod
    def get_servers(principal: pyut2serverlist.PrincipalServer) -> List[pyut2serverlist.Server]:
        query_ok = False
        attempt = 0
        max_attempts = 3
        servers = []
        while not query_ok and attempt < max_attempts:
            try:
                servers = principal.get_servers()
                query_ok = True
            except pyut2serverlist.TimeoutError:
                logging.error(f'Principal server query timed out, attempt {attempt + 1}/{max_attempts}')
                attempt += 1
            except pyut2serverlist.Error as e:
                logging.debug(e)
                logging.error(f'Failed to query principal server, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        return servers

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        # Since we query the server directly, there is no way of handling HTTP server errors differently then
        # actually failed checks, so even if the query fails, we have to treat it as "check ok"
        check_ok = True
        found = False
        try:
            pyut2serverlist.Server(server.ip, server.query_port).get_info()

            # get_info will raise an exception if the server cannot be contacted,
            # so this will only be reached if the query succeeds
            found = True
        except pyut2serverlist.Error as e:
            logging.debug(e)
            logging.debug(f'Failed to query server {server.uid} for expiration check')

        return check_ok, found, checks_since_last_ok

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        template_refs = UNREAL2_CONFIGS[self.game].get('linkTemplateRefs', {})
        # Add principal-scoped links first, then add game-scoped links
        templates = [
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get(self.principal, [])],
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get('_any', [])]
        ]

        # Add GameTracker link if server is listed there
        if is_server_listed_on_gametracker(self.game, ip, port):
            templates.append(WEB_LINK_TEMPLATES['gametracker'])

        links = []
        for template in templates:
            links.append(template.render(self.game, uid, ip=ip, port=port))

        return links


class ValveServerLister(ServerLister):
    game: ValveGame
    servers: List[ClassicServer]
    principal: ValvePrincipal
    config: ValveGameConfig

    principal_timeout: float
    filters: str
    max_pages: int

    def __init__(
            self,
            game: ValveGame,
            principal: ValvePrincipal,
            principal_timeout: float,
            filters: str,
            max_pages: int,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str
    ):
        super().__init__(game, ClassicServer, expired_ttl, recover, add_links, list_dir)
        self.principal = principal
        self.config = VALVE_GAME_CONFIGS[self.game]
        self.principal_timeout = principal_timeout
        self.filters = filters
        self.max_pages = max_pages

    def update_server_list(self):
        principal_config = VALVE_PRINCIPAL_CONFIGS[self.principal]
        principal = pyvpsq.PrincipalServer(
            principal_config.hostname,
            principal_config.port,
            timeout=self.principal_timeout
        )

        found_servers = []
        # Try to reduce the consecutive number of requests by iterating over regions
        for region in pyvpsq.Region:
            for raw_server in self.get_servers(principal, self.config.app_id, region, self.filters, self.max_pages):
                if not is_valid_public_ip(raw_server.ip) or not is_valid_port(raw_server.query_port):
                    logging.warning(
                        f'Principal returned invalid server entry '
                        f'({raw_server.ip}:{raw_server.query_port}), skipping it'
                    )
                    continue

                via = ViaStatus(self.principal)
                found_server = ClassicServer(
                    guid_from_ip_port(raw_server.ip, str(raw_server.query_port)),
                    raw_server.ip,
                    raw_server.query_port,
                    via
                )

                if found_server not in found_servers:
                    if self.add_links:
                        game_port = found_server.query_port
                        if self.config.query_port_offset is not None:
                            game_port -= self.config.query_port_offset
                        found_server.add_links(self.build_server_links(
                            found_server.uid,
                            found_server.ip,
                            game_port
                        ))
                    found_servers.append(found_server)

        self.add_update_servers(found_servers)

    @staticmethod
    def get_servers(
            principal: pyvpsq.PrincipalServer,
            app_id: int,
            region: pyvpsq.Region,
            filters: str,
            max_pages: int
    ) -> List[pyvpsq.Server]:
        servers = []
        try:
            for server in principal.get_servers(fr'\appid\{app_id}{filters}', region, max_pages):
                servers.append(server)
        except pyvpsq.TimeoutError:
            logging.error('Principal server query timed out')
        except pyvpsq.Error:
            logging.error('Failed to query principal server')

        return servers

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        found, _ = self.query_server(server)
        return True, found, checks_since_last_ok

    @staticmethod
    def query_server(server: ClassicServer) -> Tuple[bool, Optional[pyvpsq.ServerInfo]]:
        try:
            info = pyvpsq.Server(server.ip, server.query_port).get_info()
            return True, info
        except pyvpsq.Error as e:
            logging.debug(e)
            logging.debug(f'Failed to query server {server.uid}')
            return False, None

    def build_server_links(self, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> Union[List[WebLink], WebLink]:
        links = []
        if is_server_listed_on_gametracker(self.game, ip, port):
            links.append(WEB_LINK_TEMPLATES['gametracker'].render(self.game, uid, ip=ip, port=port))

        return links
