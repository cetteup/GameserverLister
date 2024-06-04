import logging
import os
import subprocess
import sys
from typing import List, Tuple, Optional, Union

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port, \
    is_server_for_gamespy_game, resolve_host
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import GamespyGame, GamespyPrincipal, GamespyGameConfig, GamespyPlatform
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from GameserverLister.games.gamespy import GAMESPY_PRINCIPAL_CONFIGS, GAMESPY_GAME_CONFIGS
from .common import ServerLister


class GameSpyServerLister(ServerLister):
    game: GamespyGame
    platform: GamespyPlatform
    servers: List[ClassicServer]
    principal: GamespyPrincipal
    config: GamespyGameConfig
    gslist_bin_path: str
    gslist_filter: str
    gslist_super_query: bool
    gslist_timeout: int
    verify: bool
    add_game_port: bool

    def __init__(
            self,
            game: GamespyGame,
            principal: GamespyPrincipal,
            gslist_bin_path: str,
            gslist_filter: str,
            gslist_super_query: bool,
            gslist_timeout: int,
            verify: bool,
            add_game_port: bool,
            expire: bool,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            txt: bool,
            list_dir: str
    ):
        super().__init__(
            game,
            GamespyPlatform.PC,
            ClassicServer,
            expire,
            expired_ttl,
            recover,
            add_links,
            txt,
            list_dir
        )
        self.principal = principal.lower()
        self.config = GAMESPY_GAME_CONFIGS[self.game]
        self.gslist_bin_path = gslist_bin_path
        self.gslist_filter = gslist_filter
        self.gslist_super_query = gslist_super_query
        self.gslist_timeout = gslist_timeout
        self.verify = verify
        self.add_game_port = add_game_port

    def update_server_list(self):
        raw_servers = self.get_servers()
        found_servers = []
        for ip, query_port in raw_servers:
            if not is_valid_public_ip(ip) or not is_valid_port(int(query_port)):
                logging.warning(f'Principal returned invalid server entry ({ip}:{query_port}), skipping it')
                continue

            via = ViaStatus(self.principal)
            found_server = ClassicServer(
                guid_from_ip_port(ip, str(query_port)),
                ip,
                query_port,
                via
            )

            if self.verify or self.add_links or self.add_game_port:
                # Attempt to query server in order to verify is a server for the current game
                # (some principals return servers for other games than what we queried)
                logging.debug(f'Querying server {found_server.uid}/{found_server.ip}:{found_server.query_port}')
                responded, query_response = self.query_server(found_server)
                logging.debug(f'Query {"was successful" if responded else "did not receive a response"}')

                if responded:
                    if self.verify and not is_server_for_gamespy_game(self.game, self.config.game_name, query_response):
                        logging.warning(f'Server does not seem to be a {self.game} server, ignoring it '
                                        f'({found_server.ip}:{found_server.query_port})')
                        continue

                    if self.add_links or self.add_game_port:
                        if query_response.get('hostport', '').isnumeric():
                            game_port = int(query_response['hostport'])
                            if self.add_links:
                                found_server.add_links(self.build_server_links(
                                    found_server.uid,
                                    found_server.ip,
                                    game_port
                                ))
                            if self.add_game_port:
                                found_server.game_port = game_port
                        elif 'hostport' in query_response:
                            logging.warning(f'Server returned an invalid hostport (\'{query_response["hostport"]}\', ' 
                                            f'not adding links/game port ({found_server.ip}:{found_server.query_port})')

            found_servers.append(found_server)

        self.add_update_servers(found_servers)

    def get_servers(self) -> List[Tuple[str, int]]:
        principal = GAMESPY_PRINCIPAL_CONFIGS[self.principal]
        # Format hostname using game name (following old GameSpy format [game].master.gamespy.com)
        hostname = principal.hostname.format(self.config.game_name)
        # Combine game port and principal-specific port offset (defaults to an offset of 0)
        port = self.config.port + principal.get_port_offset()

        # Manually look up hostname to be able to spread retried across servers
        ips = resolve_host(hostname)
        if len(ips) == 0:
            logging.error(f'DNS lookup for {hostname} failed, exiting')
            sys.exit(1)

        # Run gslist and capture output
        command_ok = False
        tries = 0
        max_tries = 3
        gslist_result = None
        while not command_ok and tries < max_tries:
            # Alternate between first and last found A record
            ip = ips[0] if tries % 2 == 0 else ips[-1]
            try:
                logging.info(f'Running gslist command against {ip}')
                command = [self.gslist_bin_path, '-n', self.config.game_name, '-x',
                           f'{ip}:{port}', '-Y', self.config.game_name, self.config.game_key,
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
                gslist_result = subprocess.run(
                    command, capture_output=True,
                    cwd=self.server_list_dir_path, timeout=timeout
                )
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
        servers: List[Tuple[str, int]] = []
        for line in raw_server_list.splitlines():
            connect, *_ = line.split(' ', 1)
            ip, query_port = connect.strip().split(':', 1)
            servers.append((ip, int(query_port)))

        return servers

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

    def build_server_links(
            self,
            uid: str,
            ip: Optional[str] = None,
            port: Optional[int] = None
    ) -> Union[List[WebLink], WebLink]:
        template_refs = self.config.link_template_refs if self.config.link_template_refs is not None else {}
        # Add principal-scoped links first, then add game-scoped links
        templates = [
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get(self.principal, [])],
            *[WEB_LINK_TEMPLATES.get(ref) for ref in template_refs.get('_any', [])]
        ]

        links = []
        for template in templates:
            links.append(template.render(self.game, self.platform, uid, ip=ip, port=port))

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
