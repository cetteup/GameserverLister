import logging
import sys
from random import randint
from typing import Tuple, Callable, List

import requests

from GameserverLister.common.helpers import guid_from_ip_port
from GameserverLister.common.servers import BadCompany2Server
from GameserverLister.common.types import TheaterGame, TheaterPlatform
from .common import FrostbiteServerLister


class BadCompany2ServerLister(FrostbiteServerLister):
    game: TheaterGame
    platform: TheaterPlatform

    def __init__(
            self,
            expire: bool,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            txt: bool,
            list_dir: str,
            timeout: float
    ):
        super().__init__(
            TheaterGame.BFBC2,
            TheaterPlatform.PC,
            BadCompany2Server,
            expire,
            expired_ttl,
            recover,
            add_links,
            txt,
            list_dir,
            timeout
        )

    def update_server_list(self):
        request_ok = False
        attempt = 0
        max_attempts = 3
        servers = None
        while not request_ok and attempt < max_attempts:
            try:
                logging.info('Fetching server list from Project Rome API')
                resp = self.session.get('https://fesl.cetteup.com/v1/bfbc2/servers/rome-pc', timeout=self.request_timeout)

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
                server['LID'],
                server['GID'],
                server['I'],
                server['P']
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
            response = self.session.get(f'https://fesl.cetteup.com/v1/bfbc2/servers/rome-pc/{server.lid}/{server.gid}',
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

    def build_port_to_try_list(self, game_port: int) -> List[int]:
        """
        Most Bad Company 2 server seem to be hosted directly by members of the community, resulting in pretty random
        query ports as well as strange/incorrect server configurations. So, try a bunch of ports and validate found
        query ports using the connect property OR the server name
        """
        return [
            48888,  # default query port
            game_port + 29321,  # game port + default port offset (mirror gamedig behavior)
            game_port,  # game port (some servers use same port for game + query)
            game_port + 100,  # game port + 100 (nitrado)
            game_port + 10,  # game port + 10
            game_port + 5,  # game port + 5 (several hosters)
            game_port + 1,  # game port + 1
            game_port + 29233,  # game port + 29233 (i3D.net)
            game_port + 29000,  # game port + 29000
            game_port + 29323,  # game port + 29323
            randint(48880, 48890),  # random port around default query port
            randint(48601, 48605),  # random port around 48600
            randint(19567, 48888),  # random port between default game port and default query port
            randint(game_port, game_port + 29321)  # random port between game port and game port + default offset
        ]

    def get_validator(self) -> Callable[[BadCompany2Server, dict], bool]:
        def validator(server: BadCompany2Server, parsed_result: dict) -> bool:
            # Consider server valid if game port matches
            if parsed_result.get('connect', '').endswith(f':{server.game_port}'):
                return True

            # Consider server valid if (unique) name matches
            names = [s.name for s in self.servers if s.name == server.name]
            if parsed_result.get('name') == server.name and len(names) == 1:
                return True

            return False

        return validator

