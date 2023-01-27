import logging
from typing import List, Tuple, Optional, Union

import pyvpsq

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port, \
    is_server_listed_on_gametracker
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import ValveGame, ValvePrincipal, ValveGameConfig
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from GameserverLister.games.valve import VALVE_PRINCIPAL_CONFIGS, VALVE_GAME_CONFIGS
from GameserverLister.listers.common import ServerLister


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
                            game_port += self.config.query_port_offset
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

    def build_server_links(
            self,
            uid: str,
            ip: Optional[str] = None,
            port: Optional[int] = None
    ) -> Union[List[WebLink], WebLink]:
        links = []
        if is_server_listed_on_gametracker(self.game, ip, port):
            links.append(WEB_LINK_TEMPLATES['gametracker'].render(self.game, uid, ip=ip, port=port))

        return links
