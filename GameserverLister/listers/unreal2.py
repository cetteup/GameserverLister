import logging
from typing import List, Tuple, Optional, Union

import pyut2serverlist

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port, \
    is_server_listed_on_gametracker
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import Unreal2Game
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from GameserverLister.games.unreal2 import UNREAL2_CONFIGS
from .common import ServerLister


class Unreal2ServerLister(ServerLister):
    game: Unreal2Game
    principal: str
    cd_key: str

    principal_timeout: float

    def __init__(
            self,
            game: Unreal2Game,
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

    def build_server_links(
            self,
            uid: str,
            ip: Optional[str] = None,
            port: Optional[int] = None
    ) -> Union[List[WebLink], WebLink]:
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
