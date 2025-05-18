import logging
import os
import subprocess
from abc import abstractmethod
from typing import List

import requests

from GameserverLister.common.helpers import resolve_host, guid_from_ip_port
from GameserverLister.common.servers import ClassicServer, ViaStatus, Server
from GameserverLister.common.types import GamespyPrincipal, GamespyGame, GamespyPlatform, Principal, Game, Platform
from GameserverLister.games.gamespy import GAMESPY_PRINCIPAL_CONFIGS, GAMESPY_GAME_CONFIGS
from GameserverLister.providers.provider import Provider


class GamespyProvider(Provider):
    @abstractmethod
    def list(self, principal: GamespyPrincipal, game: GamespyGame, platform: GamespyPlatform, **kwargs) -> List[ClassicServer]:
        pass


class GamespyListProtocolProvider(GamespyProvider):
    gslist_bin_path: str

    def __init__(self, gslist_bin_path: str):
        self.gslist_bin_path = gslist_bin_path

    def list(
            self,
            principal: GamespyPrincipal,
            game: GamespyGame,
            platform: GamespyPlatform,
            **kwargs
    ) -> List[ClassicServer]:
        principal_config = GAMESPY_PRINCIPAL_CONFIGS[principal]
        game_config = GAMESPY_GAME_CONFIGS[game]
        # Format hostname using game name (following old GameSpy format [game].master.gamespy.com)
        hostname = principal_config.hostname.format(game_config.game_name)
        # Combine game port and principal-specific port offset (defaults to an offset of 0)
        port = game_config.port + principal_config.get_port_offset()

        # Manually look up hostname to be able to spread retries across servers
        ips = resolve_host(hostname)
        if len(ips) == 0:
            raise Exception(f'Failed to resolve principal hostname: {hostname}')

        cwd = kwargs.get('cwd', os.getcwd())
        timeout = kwargs.get('timeout', 10)

        # Run gslist and capture output
        command_ok = False
        attempt = 0
        max_attempts = 3
        gslist_result = None
        while not command_ok and attempt < max_attempts:
            # Alternate between first and last found A record
            ip = ips[0] if attempt % 2 == 0 else ips[-1]

            command = [
                self.gslist_bin_path,
                '-n', game_config.game_name,
                '-x', f'{ip}:{port}',
                '-Y', game_config.game_name, game_config.game_key,
                '-t', str(game_config.enc_type),
                '-o', '1',
            ]

            # Add filter if one was given
            if isinstance(kwargs.get('filter'), str):
                command.extend(['-f', kwargs['filter']])

            # Some principals do not respond with the default query list type byte (1),
            # so we need to explicitly set a different type byte
            if game_config.list_type is not None:
                command.extend(['-T', str(game_config.list_type)])

            # Some principals do not respond unless an info query is sent (e.g. FH2 principal)
            if game_config.info_query is not None:
                command.extend(['-X', game_config.info_query])

            # Add super query argument if requested
            if kwargs.get('super_query'):
                command.extend(['-Q', str(game_config.query_type)])
                # Extend timeout to account for server queries
                timeout += 10

            try:
                logging.debug(f'Running gslist command against {ip}')
                gslist_result = subprocess.run(
                    command,
                    capture_output=True,
                    cwd=cwd,
                    timeout=timeout,
                )
                command_ok = True
            except subprocess.TimeoutExpired:
                logging.error(f'gslist timed out, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        # Make sure any server were found (gslist sends all output to stderr so check there)
        if gslist_result is None or 'servers found' not in str(gslist_result.stderr):
            raise Exception('Failed to retrieve any servers via gslist')

        # Read gslist output file
        logging.debug('Reading gslist output file')
        with open(os.path.join(cwd, f'{game_config.game_name}.gsl'), 'r') as gslist_file:
            raw_server_list = gslist_file.read()

        # Parse server list
        # Format: [ip-address]:[port]
        logging.debug(f'Parsing server list')
        servers: List[ClassicServer] = []
        for line in raw_server_list.splitlines():
            connect, *_ = line.split(' ', 1)
            ip, query_port = connect.strip().split(':', 1)
            servers.append(ClassicServer(
                guid_from_ip_port(ip, str(query_port)),
                ip,
                int(query_port),
                ViaStatus(principal)
            ))

        return servers


class CrympAPIProvider(GamespyProvider):
    session: requests.Session

    def __init__(self):
        self.session = requests.Session()

    def list(
            self,
            principal: GamespyPrincipal,
            game: GamespyGame,
            platform: GamespyPlatform,
            **kwargs
    ) -> List[ClassicServer]:
        if principal is not GamespyPrincipal.Crymp_org:
            raise Exception(f'Unsupported principal for {self.__class__.__name__}: {principal}')
        if game is not GamespyGame.Crysis:
            raise Exception(f'Unsupported game for {self.__class__.__name__}: {game}')

        principal_config = GAMESPY_PRINCIPAL_CONFIGS[principal]
        game_config = GAMESPY_GAME_CONFIGS[game]

        # Format hostname using game name (following old GameSpy format [game].master.gamespy.com)
        hostname = principal_config.hostname.format(game_config.game_name)

        try:
            resp = self.session.get(
                f'https://{hostname}/api/servers',
                timeout=kwargs.get('timeout', 10)
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to fetch server list: {e}') from None

        servers: List[ClassicServer] = []
        for server in resp.json():
            servers.append(
                ClassicServer(
                    guid_from_ip_port(server['ip'], str(server['gamespy_port'])),
                    server['ip'],
                    server['gamespy_port'],
                    ViaStatus(principal)
                )
            )

        return servers
