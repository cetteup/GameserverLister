import json
from datetime import datetime, timedelta
from typing import Dict, Optional

from GameserverLister.common.constants import UNIX_EPOCH_START


class WebLink:
    site: str
    url: str
    official: bool
    as_of: datetime

    def __init__(self, site: str, url: str, official: bool, as_of: datetime = datetime.now().astimezone()):
        self.site = site
        self.url = url
        self.official = official
        self.as_of = as_of

    def is_expired(self, expired_ttl: float) -> bool:
        return datetime.now().astimezone() > self.as_of + timedelta(hours=expired_ttl)

    def update(self, updated: 'WebLink') -> None:
        self.url = updated.url
        self.official = updated.official
        self.as_of = updated.as_of

    @staticmethod
    def load(parsed: dict) -> 'WebLink':
        as_of = datetime.fromisoformat(parsed['asOf']) \
            if parsed.get('asOf') is not None else UNIX_EPOCH_START
        return WebLink(
            parsed['site'],
            parsed['url'],
            parsed['official'],
            as_of
        )

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        return 'site' in parsed and 'url' in parsed and 'official' in parsed

    def dump(self) -> dict:
        return {
            'site': self.site,
            'url': self.url,
            'official': self.official,
            'asOf': self.as_of.isoformat()
        }

    def __eq__(self, other):
        return isinstance(other, WebLink) and \
               other.site == self.site and \
               other.url == self.url and \
               other.official == self.official and \
               other.as_of == self.as_of

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
    'arena.sh': WebLinkTemplate(
        'arena.sh',
        'https://arena.sh/game/{2}:{3}/',
        False
    ),
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
    # deathmask.net shows servers from their own as well as other masters,
    # so they are not the official source for all servers
    'deathmask.net-official': WebLinkTemplate(
        'deathmask.net',
        'https://dpmaster.deathmask.net/?game={0}&server={2}:{3}',
        True
    ),
    'deathmask.net-unofficial': WebLinkTemplate(
        'deathmask.net',
        'https://dpmaster.deathmask.net/?game={0}&server={2}:{3}',
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
    'swat4stats.com': WebLinkTemplate(
        'swat4stats.com',
        'https://swat4stats.com/servers/{2}:{3}/',
        False
    )
}
