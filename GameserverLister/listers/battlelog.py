import logging
from datetime import datetime
from random import randint
from typing import List, Tuple, Optional, Union, Callable

import requests

from GameserverLister.common.servers import FrostbiteServer
from GameserverLister.common.types import BattlelogGame, BattlelogPlatform
from GameserverLister.common.weblinks import WEB_LINK_TEMPLATES, WebLink
from GameserverLister.games.battlelog import BATTLELOG_GAME_BASE_URIS
from .common import HttpServerLister, FrostbiteServerLister


class BattlelogServerLister(HttpServerLister, FrostbiteServerLister):
    game: BattlelogGame

    def __init__(
            self,
            game: BattlelogGame,
            platform: BattlelogPlatform,
            page_limit: int,
            expire: bool,
            expired_ttl: float,
            recover: bool,
            add_links: bool,
            txt: bool,
            list_dir: str,
            sleep: float,
            max_attempts: int,
            proxy: str = None
    ):
        super().__init__(
            game,
            platform,
            FrostbiteServer,
            page_limit,
            60,
            expire,
            expired_ttl,
            recover,
            add_links,
            txt,
            list_dir,
            sleep,
            max_attempts
        )

        # Set up headers
        self.session.headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }
        # Set up proxy if given
        if proxy is not None:
            # All requests are sent via https, so just set up https proxy
            self.session.proxies = {
                'https': proxy
            }

    def get_server_list_url(self, per_page: int) -> str:
        return f'{BATTLELOG_GAME_BASE_URIS[self.game]}/{self.platform}/?count={per_page}&offset=0'

    def add_page_found_servers(self, found_servers: List[FrostbiteServer], page_response_data: dict) -> List[FrostbiteServer]:
        for server in page_response_data['data']:
            found_server = FrostbiteServer(
                server['guid'],
                server['name'],
                server['ip'],
                server['port'],
            )

            if self.add_links:
                found_server.add_links(self.build_server_links(found_server.uid))
                # Gametools uses the gameid for BF4 server URLs, so add that separately
                if self.game is BattlelogGame.BF4:
                    found_server.add_links(WEB_LINK_TEMPLATES['gametools'].render(self.game, self.platform, server['gameId']))

            # Add non-private servers (servers with an IP) that are new
            server_uids = [s.uid for s in found_servers]
            if len(found_server.ip) > 0 and found_server.uid not in server_uids:
                logging.debug(f'Got new server {found_server.uid}, adding it')
                found_servers.append(found_server)
            elif len(found_server.ip) > 0:
                logging.debug(f'Got duplicate server {found_server.uid}, updating last seen at')
                index = server_uids.index(found_server.uid)
                found_servers[index].last_seen_at = datetime.now().astimezone()
            else:
                logging.debug(f'Got private server {found_server.uid}, ignoring it')

        return found_servers

    def check_if_server_still_exists(self, server: FrostbiteServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        check_ok = True
        found = False
        try:
            response = self.session.get(f'https://battlelog.battlefield.com/{self.game}/'
                                        f'servers/show/{self.platform}/{server.uid}?json=1',
                                        timeout=self.request_timeout)
            if response.status_code == 200:
                # Server was found on Battlelog => make sure it is still public
                # TODO use server validator here
                parsed = response.json()
                found = parsed['message']['SERVER_INFO']['ip'] != ''
            elif response.status_code == 422:
                # Battlelog responded with 422, explicitly indicating that the server was not found
                found = False
            else:
                # Battlelog responded with some other status code (rate limit 403 for example)
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
        links = [WEB_LINK_TEMPLATES['battlelog'].render(self.game, self.platform, uid)]

        # Gametools uses the guid as the "gameid" for BF3 and BFH, so we can add links for those
        # (BF4 uses the real gameid, so we need to handle those links separately)
        if self.game in ['bf3', 'bfh']:
            links.append(WEB_LINK_TEMPLATES['gametools'].render(self.game, self.platform, uid))

        return links

    def build_port_to_try_list(self, game_port: int) -> List[int]:
        return [
            47200,  # default query port
            game_port + 22000,  # default port offset (mirror gamedig behavior)
            game_port,  # some servers use the same port for game + query
            game_port + 100,  # nitrado
            game_port + 5,  # several hosters
            game_port + 1,
            48888,  # gamed
            game_port + 6,  # i3D
            game_port + 8,  # i3D
            game_port + 10,  # Servers.com/4netplayers
            game_port + 15,  # i3D
            game_port + 50,
            game_port - 5,  # i3D
            game_port - 15,  # i3D
            game_port - 23000,  # G4G.pl
            randint(47190, 47210),  # random port around default query port
            25200 + randint(0, 22000),  # random port between default game port and default query port
            randint(game_port - 10, game_port + 10),  # random port around default game port
            game_port + randint(0, 22000),  # random port between game port and game port + default offset
        ]

    def get_validator(self) -> Callable[[FrostbiteServer, dict], bool]:
        def validator(server: FrostbiteServer, parsed_result: dict) -> bool:
            return parsed_result.get('connect') == f'{server.ip}:{server.game_port}'

        return validator
