import logging
import sys
from random import randint
from typing import Tuple, Optional, Union, List

import requests

from GameserverLister.common.helpers import bfbc2_server_validator, guid_from_ip_port, is_server_listed_on_gametracker
from GameserverLister.common.servers import BadCompany2Server
from GameserverLister.common.types import TheaterGame
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from .common import FrostbiteServerLister


class BadCompany2ServerLister(FrostbiteServerLister):
    game: TheaterGame

    def __init__(self, expired_ttl: float, recover: bool, add_links: bool, list_dir: str, timeout: float):
        super().__init__(TheaterGame.BFBC2, BadCompany2Server, expired_ttl, recover, add_links, list_dir, timeout)
        self.server_validator = bfbc2_server_validator

    def update_server_list(self):
        request_ok = False
        attempt = 0
        max_attempts = 3
        servers = None
        while not request_ok and attempt < max_attempts:
            try:
                logging.info('Fetching server list from FESL/Theater API')
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
            found_server = BadCompany2Server(
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

    def check_if_server_still_exists(self, server: BadCompany2Server, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
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
