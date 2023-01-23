import logging
import socket
from typing import List, Tuple, Optional, Union

import pyq3serverlist

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port, \
    is_server_listed_on_gametracker
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import Quake3Game
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from GameserverLister.games.quake3 import QUAKE3_CONFIGS
from .common import ServerLister


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

    def build_server_links(
            self,
            uid: str,
            ip: Optional[str] = None,
            port: Optional[int] = None
    ) -> Union[List[WebLink], WebLink]:
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
