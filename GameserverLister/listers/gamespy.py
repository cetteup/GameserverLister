import logging
import subprocess
from typing import List, Tuple, Optional, Union

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, is_server_for_gamespy_game
from GameserverLister.common.servers import ClassicServer
from GameserverLister.common.types import GamespyGame, GamespyPrincipal, GamespyGameConfig, GamespyPlatform
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from GameserverLister.games.gamespy import GAMESPY_GAME_CONFIGS
from GameserverLister.listers.common import ServerLister
from GameserverLister.providers import GamespyProvider


class GamespyServerLister(ServerLister):
    game: GamespyGame
    platform: GamespyPlatform
    servers: List[ClassicServer]
    principal: GamespyPrincipal
    provider: GamespyProvider
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
            provider: GamespyProvider,
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
        self.principal = principal
        self.provider = provider
        self.config = GAMESPY_GAME_CONFIGS[self.game]
        self.gslist_bin_path = gslist_bin_path
        self.gslist_filter = gslist_filter
        self.gslist_super_query = gslist_super_query
        self.gslist_timeout = gslist_timeout
        self.verify = verify
        self.add_game_port = add_game_port

    def update_server_list(self):
        found_servers = []
        for server in self.get_servers():
            if not is_valid_public_ip(server.ip) or not is_valid_port(server.query_port):
                logging.warning(f'Ignoring invalid server entry ({server.ip}:{server.query_port})')
                continue

            if self.verify or self.add_links or self.add_game_port:
                # Attempt to query server in order to verify is a server for the current game
                # (some principals return servers for other games than what we queried)
                logging.debug(f'Querying server {server.uid}/{server.ip}:{server.query_port}')
                responded, query_response = self.query_server(server)
                logging.debug(f'Query {"was successful" if responded else "did not receive a response"}')

                if responded:
                    if self.verify and not is_server_for_gamespy_game(self.game, self.config.game_name, query_response):
                        logging.warning(f'Server does not seem to be a {self.game} server, ignoring it '
                                        f'({server.ip}:{server.query_port})')
                        continue

                    if self.add_links or self.add_game_port:
                        if query_response.get('hostport', '').isnumeric():
                            game_port = int(query_response['hostport'])
                            if self.add_links:
                                server.add_links(self.build_server_links(
                                    server.uid,
                                    server.ip,
                                    game_port
                                ))
                            if self.add_game_port:
                                server.game_port = game_port
                        elif 'hostport' in query_response:
                            logging.warning(f'Server returned an invalid hostport (\'{query_response["hostport"]}\', ' 
                                            f'not adding links/game port ({server.ip}:{server.query_port})')

            found_servers.append(server)

        self.add_update_servers(found_servers)

    def get_servers(self) -> List[ClassicServer]:
        return self.provider.list(
            self.principal,
            self.game,
            self.platform,
            filter=self.gslist_filter,
            super_query=self.gslist_super_query,
            cwd=self.server_list_dir_path,
            timeout=self.gslist_timeout
        )

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
