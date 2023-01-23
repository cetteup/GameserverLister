import logging
import socket
from typing import List, Tuple

import pyq3serverlist
from pyq3serverlist.buffer import Buffer

from GameserverLister.common.types import GamespyGame, GamespyPrincipal
from GameserverLister.games.gamespy import GAMESPY_PRINCIPAL_CONFIGS
from GameserverLister.listers import GameSpyServerLister


class EpicSpyServerLister(GameSpyServerLister):
    """
    Epic Games' "GameSpy" principals use a simplified response structure, returning \\ip\\{ip}{port}\\... as string
    """
    principal_timeout: float

    def __init__(self,
            game: GamespyGame,
            principal_timeout: float,
            gslist_bin_path: str,
            gslist_timeout: int,
            recover: bool,
            add_links: bool,
            list_dir: str,
            expired_ttl: float
    ):
        super().__init__(
            game,
            GamespyPrincipal.EPIC_GAMES_UNREAL if game is GamespyGame.UNREAL else GamespyPrincipal.EPIC_GAMES_UT,
            gslist_bin_path,
            '',
            False,
            gslist_timeout,
            True,
            expired_ttl,
            recover,
            add_links,
            list_dir
        )
        self.principal_timeout = principal_timeout

    def get_servers(self) -> List[Tuple[str, int]]:
        config = GAMESPY_PRINCIPAL_CONFIGS[self.principal]
        connection = pyq3serverlist.Connection(
            config.hostname, 28900 + config.get_port_offset(), socket.SOCK_STREAM, self.principal_timeout
        )

        query_ok = False
        attempt = 0
        max_attempts = 3
        servers: List[Tuple[str, int]] = []
        while not query_ok and attempt < max_attempts:
            try:
                challenge = connection.read()
                if challenge.read(21) != b'\\basic\\\\secure\\wookie':
                    logging.error(f'Principal returned invalid challenge, attempt {attempt + 1}/{max_attempts}')
                    attempt += 1
                    continue
                challenge_response = Buffer()
                challenge_response.write_string(f'\\gamename\\{self.game}\\location\\0\\validate\\\\final\\')
                connection.write(challenge_response.get_buffer())
                list_request = Buffer()
                list_request.write_string(f'\\list\\\\gamename\\{self.game}\\final\\')
                connection.write(list_request.get_buffer())
                response = connection.read()
                while response.peek(3) == b'\\ip':
                    response.skip(4)
                    ip, _, query_port = response.read_string(b'\\').partition(':')
                    servers.append((ip, int(query_port)))
                query_ok = True
            except pyq3serverlist.PyQ3SLTimeoutError:
                logging.error(f'Principal server query timed out, attempt {attempt + 1}/{max_attempts}')
                attempt += 1
            except pyq3serverlist.PyQ3SLError as e:
                logging.debug(e)
                logging.error(f'Failed to query principal server, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        return servers
