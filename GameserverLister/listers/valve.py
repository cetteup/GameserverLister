import logging
from typing import List, Tuple, Optional

import pyvpsq

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import ValveGame, ValvePrincipal, ValveGameConfig, ValvePlatform
from GameserverLister.games.valve import VALVE_PRINCIPAL_CONFIGS, VALVE_GAME_CONFIGS
from GameserverLister.listers.common import ServerLister


class ValveServerLister(ServerLister):
    game: ValveGame
    platform: ValvePlatform
    servers: List[ClassicServer]
    principal: ValvePrincipal
    config: ValveGameConfig

    principal_timeout: float
    filters: str
    max_pages: int

    add_game_port: bool

    def __init__(
            self,
            game: ValveGame,
            principal: ValvePrincipal,
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
        self.config = VALVE_GAME_CONFIGS[self.game]
        self.principal_timeout = principal_timeout
        self.filters = filters
        self.max_pages = max_pages
        self.add_game_port = add_game_port

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
                    if self.add_links or self.add_game_port:
                        game_port = self.get_server_game_port(found_server)
                        if game_port is not None:
                            if self.add_links:
                                found_server.add_links(self.build_server_links(
                                    found_server.uid,
                                    found_server.ip,
                                    game_port
                                ))
                            if self.add_game_port:
                                found_server.game_port = game_port
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
            logging.debug(e)
            logging.debug(f'Failed to query server {server.uid}')
            return False, None
