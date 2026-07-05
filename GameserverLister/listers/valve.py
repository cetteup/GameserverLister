import logging
from typing import List, Tuple, Optional

import pyvpsq

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port
from GameserverLister.common.servers import ClassicServer
from GameserverLister.common.types import ValveGame, ValvePrincipal, ValveGameConfig, ValvePlatform
from GameserverLister.games.valve import VALVE_GAME_CONFIGS
from GameserverLister.listers.common import ServerLister
from GameserverLister.providers.valve import ValveProvider


class ValveServerLister(ServerLister):
    game: ValveGame
    platform: ValvePlatform
    servers: List[ClassicServer]
    principal: ValvePrincipal
    provider: ValveProvider
    config: ValveGameConfig

    principal_timeout: float
    filters: str
    max_pages: int

    add_game_port: bool

    def __init__(
            self,
            game: ValveGame,
            principal: ValvePrincipal,
            provider: ValveProvider,
            principal_timeout: float,
            filters: str,
            max_pages: int,
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
            ValvePlatform.PC,
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
        self.config = VALVE_GAME_CONFIGS[self.game]
        self.principal_timeout = principal_timeout
        self.filters = filters
        self.max_pages = max_pages
        self.add_game_port = add_game_port

    def update_server_list(self):
        found_servers = []
        # Try to reduce the consecutive number of requests by iterating over regions
        for region in pyvpsq.Region:
            for server in self.get_servers(region):
                if not is_valid_public_ip(server.ip) or not is_valid_port(server.query_port):
                    logging.warning(f'Ignoring invalid server entry ({server.ip}:{server.query_port})')
                    continue

                if server not in found_servers:
                    if self.add_links or self.add_game_port:
                        game_port = self.get_server_game_port(server)
                        if game_port is not None:
                            if self.add_links:
                                server.add_links(self.build_server_links(
                                    server.uid,
                                    server.ip,
                                    game_port
                                ))
                            if self.add_game_port:
                                server.game_port = game_port
                    found_servers.append(server)

        self.add_update_servers(found_servers)

    def get_servers(self, region: int) -> List[ClassicServer]:
        return self.provider.list(
            self.principal,
            self.game,
            self.platform,
            filters=self.filters,
            region=region,
            timeout=self.principal_timeout,
        )


    def get_server_game_port(self, server: ClassicServer) -> Optional[int]:
        if not self.config.distinct_query_port:
            return server.query_port

        responded, info = self.query_server(server)
        if responded and info.game_port is not None:
            return info.game_port

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        found, _ = self.query_server(server)
        return True, found, checks_since_last_ok

    @staticmethod
    def query_server(server: ClassicServer) -> Tuple[bool, Optional[pyvpsq.ServerInfo]]:
        try:
            info = pyvpsq.Server(server.ip, server.query_port).get_info()
            return True, info
        except pyvpsq.Error as e:
            logging.debug(f'Failed to query server {server.uid}: {e}')
            return False, None
