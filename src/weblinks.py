import json
from typing import Dict, Optional


class WebLink:
    site: str
    url: str
    official: bool

    def __init__(self, site: str, url: str, official: bool):
        self.site = site
        self.url = url
        self.official = official

    def update(self, updated: 'WebLink') -> None:
        self.url = updated.url
        self.official = updated.official

    @staticmethod
    def load(parsed: dict) -> 'WebLink':
        return WebLink(
            parsed['site'],
            parsed['url'],
            parsed['official']
        )

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        return 'site' in parsed and 'url' in parsed and 'official' in parsed

    def dump(self) -> dict:
        return {
            'site': self.site,
            'url': self.url,
            'official': self.official
        }

    def __eq__(self, other):
        return isinstance(other, WebLink) and \
               other.site == self.site and \
               other.url == self.url and \
               other.official == self.official

    def __iter__(self):
        yield from self.dump().items()

    def __str__(self):
        return json.dumps(dict(self))

    def __repr__(self):
        return self.__str__()


class WebLinkTemplate:
    site: str
    url_template: str
    official: bool

    def __init__(self, site: str, url_template: str, official: bool):
        self.site = site
        self.url_template = url_template
        self.official = official

    def render(self, game: str, uid: str, ip: Optional[str] = None, port: Optional[int] = None) -> WebLink:
        return WebLink(
            self.site,
            self.url_template.format(game, uid, ip, port),
            self.official
        )

"""
For URL templates:
0: game name/key
1: server uid
2: server ip
3: server port
"""
WEB_LINK_TEMPLATES: Dict[str, WebLinkTemplate] = {
    'battlefieldtracker': WebLinkTemplate(
        'battlefieldtracker.com',
        'https://battlefieldtracker.com/bf1/servers/pc/{1}',
        False
    ),
    'battlelog': WebLinkTemplate(
        'battlelog.com',
        'https://battlelog.battlefield.com/{0}/servers/show/pc/{1}',
        True
    ),
    'bf2.tv': WebLinkTemplate(
        'bf2.tv',
        'https://bf2.tv/servers/{2}:{3}',
        False
    ),
    'bf2hub': WebLinkTemplate(
        'bf2hub.com',
        'https://www.bf2hub.com/server/{2}:{3}/',
        True
    ),
    'cod.pm': WebLinkTemplate(
      'cod.pm',
      'https://cod.pm/server/{2}/{3}',
      False
    ),
    'gametools': WebLinkTemplate(
        'gametools.network',
        'https://gametools.network/servers/{0}/gameid/{1}/pc',
        False
    ),
    'gametracker': WebLinkTemplate(
        'gametracker.com',
        'https://www.gametracker.com/server_info/{2}:{3}/',
        False
    ),
}
