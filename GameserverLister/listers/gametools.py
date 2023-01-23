import logging
from datetime import datetime
from typing import List, Tuple, Optional, Union

import requests

from GameserverLister.common.servers import GametoolsServer
from GameserverLister.common.types import GametoolsGame
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from GameserverLister.games.gametools import GAMETOOLS_BASE_URI
from .common import HttpServerLister


class GametoolsServerLister(HttpServerLister):
    game: GametoolsGame
    include_official: bool

    def __init__(
            self,
            game: GametoolsGame,
            page_limit: int,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            list_dir: str,
            sleep: float,
            max_attempts: int,
            include_official: bool
    ):
        super().__init__(game, GametoolsServer, page_limit, 100, expired_ttl, recover, add_links, list_dir, sleep,
                         max_attempts)
        # Allow non-ascii characters in server list (mostly used by server names for Asia servers)
        self.ensure_ascii = False
        self.include_official = include_official

    def get_server_list_url(self, per_page: int) -> str:
        return f'{GAMETOOLS_BASE_URI}/{self.game}/servers/?name=&limit={per_page}' \
               f'&nocache={datetime.now().timestamp()}'

    def add_page_found_servers(self, found_servers: List[GametoolsServer], page_response_data: dict) -> List[GametoolsServer]:
        for server in page_response_data['servers']:
            found_server = GametoolsServer(
                server['gameId'],
                server['prefix'],
            )

            if self.add_links:
                found_server.add_links(self.build_server_links(found_server.uid))

            # Add/update servers (ignoring official servers unless include_official is set)
            server_game_ids = [s.uid for s in found_servers]
            if found_server.uid not in server_game_ids and \
                    (not server['official'] or self.include_official):
                logging.debug(f'Got new server {found_server.uid}, adding it')
                found_servers.append(found_server)
            elif not server['official'] or self.include_official:
                logging.debug(f'Got duplicate server {found_server.uid}, updating last seen at')
                index = server_game_ids.index(found_server.uid)
                found_servers[index].last_seen_at = datetime.now().astimezone()
            else:
                logging.debug(f'Got official server {found_server.uid}, ignoring it')

        return found_servers

    def check_if_server_still_exists(self, server: GametoolsServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        check_ok = True
        found = False
        try:
            response = self.session.get(f'{GAMETOOLS_BASE_URI}/{self.game}/detailedserver/'
                                        f'?gameid={server.uid}', timeout=self.request_timeout)
            if response.status_code == 200:
                # Server was found on gametools => make sure it still not official (or include_official is set)
                parsed = response.json()
                found = not parsed['official'] or self.include_official
            elif response.status_code == 404:
                # gametools responded with, server was not found
                found = False
            else:
                # gametools responded with some other status code (504 gateway timeout for example)
                check_ok = False
            # Reset requests since last ok counter if server returned info/not found,
            # else increase counter and sleep
            if check_ok:
                checks_since_last_ok = 0
            else:
                checks_since_last_ok += 1
        except requests.exceptions.RequestException as e:
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
        links = [WEB_LINK_TEMPLATES['gametools'].render(self.game, uid)]
        # BF1 servers are also listed on battlefieldtracker.com
        if self.game is GametoolsGame.BF1:
            links.append(WEB_LINK_TEMPLATES['battlefieldtracker'].render(self.game, uid))

        return links
