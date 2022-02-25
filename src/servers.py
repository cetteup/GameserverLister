import json
from datetime import datetime
from typing import Union, Optional, Any, List

from src.constants import UNIX_EPOCH_START


class ObjectJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.dump()


class Server:
    uid: str
    # Only optional because lists may still contain entries without this attribute
    first_seen_at: Optional[datetime]
    last_seen_at: datetime

    def __init__(
            self,
            guid: str,
            first_seen_at: Optional[datetime] = datetime.now().astimezone(),
            last_seen_at: datetime = datetime.now().astimezone()
    ):
        self.uid = guid
        self.first_seen_at = first_seen_at
        self.last_seen_at = last_seen_at

    def update(self, updated: 'Server') -> None:
        self.last_seen_at = updated.last_seen_at

    @staticmethod
    def load(parsed: dict) -> Union['Server', dict]:
        pass

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        pass

    # Should be called "__dict__" but that confused the PyCharm debugger and
    # makes it impossible to inspect any instance variables
    # https://youtrack.jetbrains.com/issue/PY-43955
    def dump(self) -> dict:
        pass

    def __iter__(self):
        yield from self.dump().items()

    def __str__(self):
        return json.dumps(dict(self), cls=ObjectJSONEncoder)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and \
               other.uid == self.uid and \
               other.first_seen_at == self.first_seen_at and \
               other.last_seen_at == self.last_seen_at


class QueryableServer(Server):
    ip: str
    query_port: int

    def __init__(
            self,
            guid: str,
            ip: str,
            query_port: int,
            first_seen_at: Optional[datetime] = datetime.now().astimezone(),
            last_seen_at: datetime = datetime.now().astimezone()
    ):
        super().__init__(guid, first_seen_at, last_seen_at)
        self.ip = ip
        self.query_port = query_port

    def update(self, updated: 'QueryableServer') -> None:
        Server.update(self, updated)
        self.ip = updated.ip
        self.query_port = updated.query_port

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        return 'guid' in parsed and 'ip' in parsed and 'queryPort' in parsed

    def __eq__(self, other: Any) -> bool:
        return Server.__eq__(self, other) and other.ip == self.ip and other.query_port == self.query_port


class ViaStatus:
    principal: str
    first_seen_at: datetime
    last_seen_at: datetime

    def __init__(self, principal: str, first_seen_at: datetime = datetime.now().astimezone(),
                 last_seen_at: datetime = datetime.now().astimezone()):
        self.principal = principal
        self.first_seen_at = first_seen_at
        self.last_seen_at = last_seen_at

    def update(self, updated: 'ViaStatus') -> None:
        self.last_seen_at = updated.last_seen_at

    @staticmethod
    def load(parsed: dict) -> 'ViaStatus':
        first_seen_at = datetime.fromisoformat(parsed['firstSeenAt'])
        last_seen_at = datetime.fromisoformat(parsed['lastSeenAt'])

        return ViaStatus(
            parsed['principal'],
            first_seen_at,
            last_seen_at
        )

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        return 'principal' in parsed and 'firstSeenAt' in parsed and 'lastSeenAt' in parsed

    def dump(self) -> dict:
        return {
            'principal': self.principal,
            'firstSeenAt': self.first_seen_at.isoformat(),
            'lastSeenAt': self.last_seen_at.isoformat()
        }

    def __eq__(self, other):
        return isinstance(other, ViaStatus) and \
               other.principal == self.principal and \
               other.first_seen_at == self.first_seen_at and \
               other.last_seen_at == self.last_seen_at

    def __iter__(self):
        yield from self.dump().items()

    def __str__(self):
        return json.dumps(dict(self))

    def __repr__(self):
        return self.__str__()


class ClassicServer(QueryableServer):
    """
    Server for "classic" games whose principals which return a server list
    containing ips and query ports of game servers (GameSpy, Quake3)
    """
    via: List[ViaStatus]

    def __init__(
            self,
            guid: str,
            ip: str,
            query_port: int,
            via: Union[List[ViaStatus], ViaStatus],
            first_seen_at: Optional[datetime] = datetime.now().astimezone(),
            last_seen_at: datetime = datetime.now().astimezone()
    ):
        super().__init__(guid, ip, query_port, first_seen_at, last_seen_at)
        self.via = via if isinstance(via, list) else [via]

    def update(self, updated: 'ClassicServer') -> None:
        QueryableServer.update(self, updated)
        # Merge via statuses "manually"
        for via_status in updated.via:
            via_principals_self = [via_status.principal for via_status in self.via]
            if via_status.principal not in via_principals_self:
                self.via.append(via_status)
            else:
                index = via_principals_self.index(via_status.principal)
                self.via[index].update(via_status)

    @staticmethod
    def load(parsed: dict) -> Union['ClassicServer', dict]:
        # Return data as is if it's not a JSON representation
        if not ClassicServer.is_json_repr(parsed):
            return parsed

        first_seen_at = datetime.fromisoformat(parsed['firstSeenAt']) \
            if parsed.get('firstSeenAt') is not None else None
        last_seen_at = datetime.fromisoformat(parsed['lastSeenAt']) \
            if parsed.get('lastSeenAt') is not None else UNIX_EPOCH_START
        via = [ViaStatus.load(via_parsed) for via_parsed in parsed.get('via', []) if ViaStatus.is_json_repr(via_parsed)]

        return ClassicServer(
            parsed['guid'],
            parsed['ip'],
            parsed['queryPort'],
            via,
            first_seen_at,
            last_seen_at
        )

    def dump(self) -> dict:
        return {
            'guid': self.uid,
            'ip': self.ip,
            'queryPort': self.query_port,
            'firstSeenAt': self.first_seen_at.isoformat() if self.first_seen_at is not None else self.first_seen_at,
            'lastSeenAt': self.last_seen_at.isoformat(),
            'via': [via_status.dump() for via_status in self.via]
        }

    def __eq__(self, other):
        return QueryableServer.__eq__(self, other) and all(via_status in self.via for via_status in other.via)


class FrostbiteServer(QueryableServer):
    """
    Server for Frostbite-era games whose server lists are centralized (contain all relevant server info rather than
    just the query port)
    """
    name: str
    game_port: int
    last_queried_at: Optional[datetime]

    def __init__(
            self,
            guid: str,
            name: str,
            ip: str,
            game_port: int,
            query_port: int = -1,
            first_seen_at: Optional[datetime] = datetime.now().astimezone(),
            last_seen_at: datetime = datetime.now().astimezone(),
            last_queried_at: Optional[datetime] = None
    ):
        super().__init__(guid, ip, query_port, first_seen_at, last_seen_at)
        self.name = name
        self.game_port = game_port
        self.last_queried_at = last_queried_at

    def update(self, updated: 'FrostbiteServer') -> None:
        Server.update(self, updated)
        # Cannot use parent's update function here, since that would always overwrite the query port
        # (which may be -1 for updated if query failed or was not attempted/enabled)
        self.ip = updated.ip
        if updated.query_port != -1:
            self.query_port = updated.query_port
        self.name = updated.name
        self.game_port = updated.game_port
        # Only update timestamp if not none (don't reset)
        if updated.last_queried_at is not None:
            self.last_queried_at = updated.last_queried_at

    @staticmethod
    def load(parsed: dict) -> Union['FrostbiteServer', dict]:
        if not FrostbiteServer.is_json_repr(parsed):
            return parsed

        first_seen_at = datetime.fromisoformat(parsed['firstSeenAt']) \
            if parsed.get('firstSeenAt') is not None else None
        last_seen_at = datetime.fromisoformat(parsed['lastSeenAt']) \
            if parsed.get('lastSeenAt') is not None else UNIX_EPOCH_START
        last_queried_at = datetime.fromisoformat(parsed['lastQueriedAt']) \
            if parsed.get('lastQueriedAt') not in [None, ''] else None

        return FrostbiteServer(
            parsed['guid'],
            parsed['name'],
            parsed['ip'],
            parsed['gamePort'],
            parsed['queryPort'],
            first_seen_at,
            last_seen_at,
            last_queried_at
        )

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        return QueryableServer.is_json_repr(parsed) and 'name' in parsed and 'gamePort' in parsed

    def dump(self) -> dict:
        return {
            'guid': self.uid,
            'name': self.name,
            'ip': self.ip,
            'gamePort': self.game_port,
            'queryPort': self.query_port,
            'firstSeenAt': self.first_seen_at.isoformat() if self.first_seen_at is not None else self.first_seen_at,
            'lastSeenAt': self.last_seen_at.isoformat(),
            'lastQueriedAt': self.last_queried_at.isoformat() if self.last_queried_at is not None else self.last_queried_at,
        }


class Bfbc2Server(FrostbiteServer):
    lid: int
    gid: int

    def __init__(
            self,
            guid: str,
            name: str,
            lid: int,
            gid: int,
            ip: str,
            game_port: int,
            query_port: int = -1,
            first_seen_at: Optional[datetime] = datetime.now().astimezone(),
            last_seen_at: datetime = datetime.now().astimezone(),
            last_queried_at: Optional[datetime] = None
    ):
        super().__init__(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        self.lid = lid
        self.gid = gid

    @staticmethod
    def load(parsed: dict) -> Union['Bfbc2Server', dict]:
        # Will change to own validation in future
        if not FrostbiteServer.is_json_repr(parsed):
            return parsed

        first_seen_at = datetime.fromisoformat(parsed['firstSeenAt']) \
            if parsed.get('firstSeenAt') is not None else None
        last_seen_at = datetime.fromisoformat(parsed['lastSeenAt']) \
            if parsed.get('lastSeenAt') is not None else UNIX_EPOCH_START
        last_queried_at = datetime.fromisoformat(parsed['lastQueriedAt']) \
            if parsed.get('lastQueriedAt') not in [None, ''] else None

        return Bfbc2Server(
            parsed['guid'],
            parsed['name'],
            parsed.get('lid', -1),
            parsed.get('gid', -1),
            parsed['ip'],
            parsed['gamePort'],
            parsed['queryPort'],
            first_seen_at,
            last_seen_at,
            last_queried_at
        )

    def dump(self) -> dict:
        return {
            'guid': self.uid,
            'name': self.name,
            'ip': self.ip,
            'gamePort': self.game_port,
            'queryPort': self.query_port,
            'lid': self.lid,
            'gid': self.gid,
            'firstSeenAt': self.first_seen_at.isoformat() if self.first_seen_at is not None else self.first_seen_at,
            'lastSeenAt': self.last_seen_at.isoformat(),
            'lastQueriedAt': self.last_queried_at.isoformat() if self.last_queried_at is not None else self.last_queried_at
        }


class GametoolsServer(Server):
    name: str

    def __init__(
            self,
            game_id: str,
            name: str,
            first_seen_at: Optional[datetime] = datetime.now().astimezone(),
            last_seen_at: datetime = datetime.now().astimezone(),
    ):
        super().__init__(game_id, first_seen_at, last_seen_at)
        self.name = name

    def update(self, updated: 'GametoolsServer') -> None:
        Server.update(self, updated)
        self.name = updated.name

    @staticmethod
    def load(parsed: dict) -> Union['GametoolsServer', dict]:
        if not GametoolsServer.is_json_repr(parsed):
            return parsed

        first_seen_at = datetime.fromisoformat(parsed['firstSeenAt']) \
            if parsed.get('firstSeenAt') is not None else None
        last_seen_at = datetime.fromisoformat(parsed['lastSeenAt']) \
            if parsed.get('lastSeenAt') is not None else UNIX_EPOCH_START

        return GametoolsServer(
            parsed['gameId'],
            parsed['name'],
            first_seen_at,
            last_seen_at
        )

    @staticmethod
    def is_json_repr(parsed: dict) -> bool:
        return 'gameId' in parsed and 'name' in parsed

    def dump(self) -> dict:
        return {
            'gameId': self.uid,
            'name': self.name,
            'firstSeenAt': self.first_seen_at.isoformat() if self.first_seen_at is not None else self.first_seen_at,
            'lastSeenAt': self.last_seen_at.isoformat()
        }
