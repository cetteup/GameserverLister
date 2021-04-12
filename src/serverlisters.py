import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from random import randint
from typing import Callable

import gevent
import requests
from gevent.pool import Pool
from nslookup import Nslookup

from src.constants import ROOT_DIR, BATTLELOG_GAME_BASE_URIS, GSLIST_CONFIGS
from src.helpers import find_query_port, bfbc2_server_validator, parse_raw_server_info, battlelog_server_validator, \
    guid_from_ip_port


class ServerLister:
    game: str
    server_list_file_path: str
    expired_ttl: int

    def __init__(self, game: str, expired_ttl:  int):
        self.game = game.lower()
        self.server_list_file_path = os.path.join(ROOT_DIR, f'{self.game}-servers.json')

        self.expired_ttl = expired_ttl

        # Init server list with servers from existing list or empty one
        if os.path.isfile(self.server_list_file_path):
            with open(self.server_list_file_path, 'r') as serverListFile:
                logging.info('Reading servers from existing server list')
                self.servers = json.load(serverListFile)
        else:
            self.servers = []

    def update_server_list(self):
        pass

    def remove_expired_servers(self) -> tuple:
        # Iterate over copy of server list and remove any expired servers from the (actual) server list
        logging.info(f'Checking server expiration ttl for {len(self.servers)} servers')
        expired_servers_removed = 0
        for index, server in enumerate(self.servers[:]):
            last_seen_at = (datetime.fromisoformat(server['lastSeenAt'])
                            if 'lastSeenAt' in server.keys() else datetime.min).astimezone()
            if datetime.now().astimezone() > last_seen_at + timedelta(hours=self.expired_ttl):
                logging.debug(f'Server {server["guid"]} has not been seen in {self.expired_ttl} hours, removing it')
                self.servers.remove(server)
                expired_servers_removed += 1

        return expired_servers_removed,

    def write_to_file(self):
        logging.info(f'Writing {len(self.servers)} servers to output file')
        with open(self.server_list_file_path, 'w') as output_file:
            json.dump(self.servers, output_file, indent=2)


class GameSpyServerLister(ServerLister):
    project: str
    gslist_config: dict
    gslist_bin_path: str
    gslist_filter: str
    gslist_super_query: bool

    def __init__(self, game: str, project: str, gslist_bin_path: str, gslist_filter: str, gslist_super_query: bool,
                 expired_ttl: int):
        super().__init__(game, expired_ttl)
        self.project = project.lower()
        self.gslist_config = GSLIST_CONFIGS[self.game]
        self.gslist_bin_path = gslist_bin_path
        self.gslist_filter = gslist_filter
        self.gslist_super_query = gslist_super_query

    def update_server_list(self):
        logging.info(f'Fetching server list for {self.game} via {self.project}')

        # Manually look up hostname to be able to spread retried across servers
        looker_upper = Nslookup()
        dns_result = looker_upper.dns_lookup(self.gslist_config['servers'][self.project]['hostname'])

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
                           f'{server_ip}:{self.gslist_config["servers"][self.project]["port"]}',
                           '-Y', self.gslist_config['gameName'], self.gslist_config['gameKey'],
                           '-t', self.gslist_config['encType'], '-f', f'{self.gslist_filter}', '-o', '1']
                timeout = 10
                # Add super query argument if requested
                if self.gslist_super_query:
                    command.extend(['-Q', self.gslist_config['superQueryType']])
                    # Extend timeout to account for server queries
                    timeout = 20
                gslist_result = subprocess.run(command, capture_output=True, timeout=timeout)
                command_ok = True
            except subprocess.TimeoutExpired as e:
                logging.error(f'gslist timed out, try {tries + 1}/{max_tries}')
                tries += 1

        # Make sure any server were found
        # (gslist sends all output to stderr so check there)
        if gslist_result is None or 'servers found' not in str(gslist_result.stderr):
            sys.exit('gslist could not retrieve any servers')

        # Read gslist output file
        logging.info('Reading gslist output file')
        with open(f'{self.gslist_config["gameName"]}.gsl', 'r') as gslist_file:
            raw_server_list = gslist_file.read()

        # Parse server list
        # List format: [ip-address]:[port]
        logging.info('Parsing server list')
        for line in raw_server_list.splitlines():
            elements = line.strip().split(':')
            # Stop parsing once we reach the first line with query server data
            if len(elements[1]) > 5:
                break
            server = {
                'guid': guid_from_ip_port(elements[0], elements[1]),
                'ip': elements[0],
                'queryPort': elements[1],
                'lastSeenAt': datetime.now().astimezone().isoformat()
            }
            server_string = f'{server["ip"]}:{server["queryPort"]}'
            server_strings = [f'{s["ip"]}:{s["queryPort"]}' for s in self.servers]
            if server_string not in server_strings:
                logging.debug(f'Got new server {server["ip"]}:{server["queryPort"]}, adding it')
                self.servers.append(server)
            else:
                logging.debug(f'Got known server {server["ip"]}:{server["queryPort"]}, updating last seen at')
                index = server_strings.index(server_string)
                self.servers[index]['guid'] = server['guid']
                self.servers[index]['lastSeenAt'] = datetime.now().astimezone().isoformat()


class FrostbiteServerLister(ServerLister):
    server_validator: Callable = lambda: True

    def __init__(self, game: str, expired_ttl: int,):
        super().__init__(game, expired_ttl)

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
            jobs.append(
                pool.spawn(find_query_port, gamedig_bin_path, self.game, server, ports_to_try, self.server_validator)
            )
        # Wait for all jobs to complete
        gevent.joinall(jobs)
        for index, job in enumerate(jobs):
            server = self.servers[index]
            logging.debug(f'Checking query port search result for {server["guid"]}')
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

    def __init__(self, ealist_bin_path: str, username: str, password: str, expired_ttl: int, use_wine: bool):
        super().__init__('bfbc2', expired_ttl)
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

                ealist_result = subprocess.run(command, capture_output=True, timeout=10)
                command_ok = True
            except subprocess.TimeoutExpired as e:
                logging.error(f'ealist timed out, try {tries + 1}/{max_tries}')
                tries += 1

        # Make sure any server were found
        # (ealist sends all output to stderr so check there)
        if ealist_result is None or 'servers found' not in str(ealist_result.stderr):
            sys.exit('ealist could not retrieve any servers')

        # Read ealist output file
        logging.info('Reading ealist output file')
        gsl_file_path = os.path.join(ROOT_DIR, 'bfbc2-pc-server.gsl')
        with open(gsl_file_path, 'r') as ealist_file:
            raw_server_list = ealist_file.read()

        # Parse server list
        # List format: [ip-address]:[port]
        logging.info('Parsing server list')
        for line in raw_server_list.splitlines():
            raw_server_info = line.strip().split(' ', 1)[1]
            parsed = parse_raw_server_info(raw_server_info)
            found_server = {
                'guid': abs(int(parsed['B-U-sguid'])),
                'name': parsed['hostname'],
                'ip': parsed['hostaddr'],
                'gamePort': int(parsed['hostport']),
                'lastSeenAt': datetime.now().astimezone().isoformat()
            }
            server_guids = [s['guid'] for s in self.servers]
            if found_server['guid'] not in server_guids:
                logging.debug(f'Got new server {found_server["guid"]}, adding it')
                self.servers.append({
                    'guid': found_server['guid'],
                    'name': found_server['name'],
                    'ip': found_server['ip'],
                    'gamePort': found_server['gamePort'],
                    'queryPort': -1,
                    'lastSeenAt': found_server['lastSeenAt'],
                    'lastQueriedAt': ''
                })
            else:
                logging.debug(f'Got known server {found_server["guid"]}, updating it')
                index = server_guids.index(found_server['guid'])
                self.servers[index] = {**self.servers[index], **found_server}

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
        10. random port between default game port and default query port
        11. random port between game port and game port + default offset
        """
        ports_to_try = [48888, game_port + 29321, game_port, game_port + 100, game_port + 10, game_port + 5,
                        game_port + 1, game_port + 29233, game_port + 29000,
                        randint(19567, 48888), randint(game_port, game_port + 29321)]

        return ports_to_try


class BattlelogServerLister(FrostbiteServerLister):
    page_limit: int
    sleep: float
    max_attempts: int
    session: requests.Session

    def __init__(self, game: str, page_limit: int, expired_ttl: int, sleep: float, max_attempts: int, proxy: str):
        super().__init__(game, expired_ttl)
        self.page_limit = page_limit
        self.sleep = sleep
        self.max_attempts = max_attempts
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

    def update_server_list(self):
        offset = 0
        per_page = 60
        """
        The BF4 server browser returns tons of duplicate servers (pagination is completely broken).
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
                    f'{BATTLELOG_GAME_BASE_URIS[self.game]}?count={per_page}&offset=0',
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
                for server in parsed['data']:
                    found_server = {
                        'guid': server['guid'],
                        'ip': server['ip'],
                        'gamePort': server['port'],
                        'lastSeenAt': datetime.now().astimezone().isoformat()
                    }
                    # Add non-private servers (servers with an IP) that are new
                    server_guids = [s['guid'] for s in found_servers]
                    if len(found_server['ip']) > 0 and found_server['guid'] not in server_guids:
                        logging.debug(f'Got new server {server["guid"]}, adding it')
                        found_servers.append(found_server)
                    elif len(found_server['ip']) > 0:
                        logging.debug(f'Got duplicate server {server["guid"]}, updating last seen at')
                        found_servers[server_guids.index(found_server['guid'])]['lastSeenAt'] = datetime.now().astimezone().isoformat()
                    else:
                        logging.debug(f'Got private server {server["guid"]}, ignoring it')
                if len(found_servers) == server_total_before:
                    pages_since_last_unique_server += 1
                    logging.info(f'Got nothing but duplicates (page: {int(offset / per_page)},'
                                 f' pages since last unique: {pages_since_last_unique_server})')
                else:
                    logging.info(f'Got {len(found_servers) - server_total_before} new servers')
                    # Found new unique server, reset
                    pages_since_last_unique_server = 0
                offset += per_page
            else:
                logging.error(
                    f'Server responded with {response.status_code}, retrying {attempt + 1}/{self.max_attempts}')
                attempt += 1

        # Add/update found servers to/in known servers
        logging.info('Updating known server list with found servers')
        for found_server in found_servers:
            known_server_guids = [s['guid'] for s in self.servers]
            # Update existing server entry or add new one
            if found_server['guid'] in known_server_guids:
                logging.debug(f'Found server {found_server["guid"]} already known, updating')
                index = known_server_guids.index(found_server['guid'])
                # guid is the same, found server does not contain queryPort so it is safe to update ip,
                # gamePort and lastSeenAt by merging knownServer and foundServer
                self.servers[index] = {**self.servers[index], **found_server}
            else:
                logging.debug(f'Found server {found_server["guid"]} is new, adding')
                # Add new server entry
                self.servers.append({
                    'guid': found_server['guid'],
                    'ip': found_server['ip'],
                    'gamePort': found_server['gamePort'],
                    'queryPort': -1,
                    'lastSeenAt': found_server['lastSeenAt'],
                    'lastQueriedAt': ''
                })

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
                request_ok = True
                found = False
                try:
                    response = self.session.get(f'https://battlelog.battlefield.com/{self.game}/'
                                                f'servers/show/pc/{server["guid"]}?json=1')
                    found = False if response.status_code == 422 else True
                    # Reset requests since last ok counter if server returned info/not found,
                    # else increase counter and sleep
                    if response.status_code in [200, 422]:
                        requests_since_last_ok = 0
                    else:
                        requests_since_last_ok += 1
                except requests.exceptions.RequestException as e:
                    logging.debug(e)
                    logging.error(f'Failed to fetch server {server["guid"]} for expiration check')
                    request_ok = False

                # Remove server if request was sent successfully but server was not found
                if request_ok and not found:
                    logging.debug(f'Server {server["guid"]} has not been seen in {self.expired_ttl} hours, removing it')
                    self.servers.remove(server)
                    expired_servers_removed += 1
                elif request_ok and found:
                    logging.debug(f'Server {server["guid"]} did not appear in list but is still online, '
                                  f'updating last seen at')
                    self.servers[self.servers.index(server)]['lastSeenAt'] = datetime.now().astimezone().isoformat()
                    expired_servers_recovered += 1

        return expired_servers_removed, expired_servers_recovered

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
                """
        ports_to_try = [47200, game_port + 22000, game_port, game_port + 100, game_port + 5, game_port + 1,
                        48888, game_port + 6, game_port + 8, game_port + 15, game_port - 5, game_port - 15]

        return ports_to_try
