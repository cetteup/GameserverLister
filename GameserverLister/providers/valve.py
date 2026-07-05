from abc import abstractmethod
from typing import List

import requests

from GameserverLister.common.helpers import guid_from_ip_port
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import ValvePrincipal, ValveGame, ValvePlatform
from GameserverLister.games.valve import VALVE_PRINCIPAL_CONFIGS, VALVE_GAME_CONFIGS
from GameserverLister.providers import Provider


class ValveProvider(Provider):
    @abstractmethod
    def list(self, principal: ValvePrincipal, game: ValveGame, platform: ValvePlatform, **kwargs) -> List[
        ClassicServer]:
        pass


class ValveGameServersServiceProvider(ValveProvider):
    web_api_key: str

    session: requests.Session

    def __init__(self, web_api_key: str):
        self.web_api_key = web_api_key
        self.session = requests.Session()

    def list(
            self,
            principal: ValvePrincipal,
            game: ValveGame,
            platform: ValvePlatform,
            **kwargs
    ) -> List[ClassicServer]:
        principal_config = VALVE_PRINCIPAL_CONFIGS[principal]
        game_config = VALVE_GAME_CONFIGS[game]

        filters = {}
        # Add user-provided filters first to ensure we use internal values for app id and region
        if isinstance(kwargs.get('filters'), str):
            pairs = str(kwargs['filters']).strip('\\').split('\\')
            filters.update(zip(pairs[::2], pairs[1::2]))
        if isinstance(kwargs.get('region'), int):
            filters.update({'region': kwargs['region']})
        filters.update({'appid': str(game_config.app_id)})

        limit = kwargs.get('limit', 100)

        try:
            resp = self.session.get(
                f'https://{principal_config.hostname}:{principal_config.port}/IGameServersService/GetServerList/v1',
                params={
                    "key": self.web_api_key,
                    "format": "json",
                    "filter": '\\'.join(f'{k}\\{v}' for k, v in filters.items()),
                    "limit": limit,
                },
                timeout=kwargs.get('timeout', 10)
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to fetch server list: {e}') from None

        data = resp.json()
        if (
                not isinstance(data, dict)
                or not isinstance(data.get('response'), dict)
                or not isinstance(data['response'].get('servers', []), list)
        ):
            raise Exception(f'Principal returned an invalid/malformed response')

        servers: List[ClassicServer] = []
        for server in data['response'].get('servers', []):
            ip, _, query_port = server['addr'].partition(':')

            servers.append(
                ClassicServer(
                    guid_from_ip_port(ip, query_port),
                    ip,
                    int(query_port),
                    ViaStatus(principal),
                )
            )

        return servers
