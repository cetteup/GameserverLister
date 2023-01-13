from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Union


# https://stackoverflow.com/a/54919285/9395553
class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Principal(str, ExtendedEnum):
    pass


class GamespyPrincipal(Principal):
    THREE_THREE_THREE_NETWORKS_COM_1 = '333networks.com-1'
    THREE_THREE_THREE_NETWORKS_COM_2 = '333networks.com-2'
    BF1942_ORG = 'bf1942.org'
    BF2HUB = 'bf2hub'
    CRYMP_NET = 'crymp.net'
    EPIC_GAMES_UT3 = 'epicgames.com-ut3'
    ERRORIST_EU = 'errorist.eu'
    FH2_DEV = 'fh2.dev'
    JEDI95_US = 'jedi95.us'
    NEWBIESPLAYGROUND_NET = 'newbiesplayground.net'
    NIGHTFIREPC_COM = 'nightfirepc.com'
    NOVGAMES = 'novgames'
    OLDUNREAL_COM_1 = 'oldunreal.com-1'
    OLDUNREAL_COM_2 = 'oldunreal.com-2'
    OPENSPY = 'openspy'
    PHOENIX_NETWORK = 'phoenixnetwork'
    PLAY2142 = 'play2142'
    PLAYBF2 = 'playbf2'
    QTRACKER = 'qtracker'
    SWAT4STATS_COM = 'swat4stats.com'
    VIETCONG_TK = 'vietcong.tk'
    VIETCONG1_EU = 'vietcong1.eu'


class ValvePrincipal(Principal):
    VALVE = 'valve'


@dataclass
class GamespyPrincipalConfig:
    hostname: str
    port_offset: Optional[int] = None

    def get_port_offset(self) -> int:
        if self.port_offset is None:
            return 0
        return self.port_offset


@dataclass
class ValvePrincipalConfig:
    hostname: str
    port: int


class Game(str, ExtendedEnum):
    pass


class GamespyGame(Game):
    BF1942 = 'bf1942'
    BFVIETNAM = 'bfvietnam'
    BF2 = 'bf2'
    FH2 = 'fh2'
    BF2142 = 'bf2142'
    CRYSIS = 'crysis'
    CRYSISWARS = 'crysiswars'
    JBNIGHTFIRE = 'jbnightfire'
    PARAWORLD = 'paraworld'
    POSTAL2 = 'postal2'
    SWAT4 = 'swat4'
    UNREAL = 'unreal'
    UT = 'ut'
    UT3 = 'ut3'
    VIETCONG = 'vietcong'
    VIETCONG2 = 'vietcong2'


class Quake3Game(Game):
    COD = 'cod'
    CODUO = 'coduo'
    COD2 = 'cod2'
    COD4 = 'cod4'
    COD4X = 'cod4x'
    NEXUIZ = 'nexuiz'
    OPENARENA = 'openarena'
    Q3RALLY = 'q3rally'
    QUAKE = 'quake'
    QUAKE3ARENA = 'quake3arena'
    RTCW = 'rtcw'
    SOF2 = 'sof2'
    SWJKJA = 'swjkja'
    SWJKJO = 'swjkjo'
    TREMULOUS = 'tremulous'
    URBANTERROR = 'urbanterror'
    WARFORK = 'warfork'
    WARSOW = 'warsow'
    WOLFENSTEINET = 'wolfensteinet'
    XONOTIC = 'xonotic'


class MedalOfHonorGame(Game):
    AA = 'mohaa'
    BT = 'mohbt'
    PA = 'mohpa'
    SH = 'mohsh'


class Unreal2Game(Game):
    UT2003 = 'ut2003'
    UT2004 = 'ut2004'


class ValveGame(Game):
    DOD = 'dod'
    DODS = 'dods'
    RS2 = 'rs2'
    TFC = 'tfc'
    TF2 = 'tf2'


class TheaterGame(Game):
    BFBC2 = 'bfbc2'


class BattlelogGame(Game):
    BF3 = 'bf3'
    BF4 = 'bf4'
    BFH = 'bfh'
    MOHWF = 'mohwf'


class GametoolsGame(Game):
    BF1 = 'bf1'
    BFV = 'bfv'


@dataclass
class GamespyGameConfig:
    game_name: str
    game_key: str
    enc_type: int
    query_type: int
    port: int
    principals: List[GamespyPrincipal]
    gamedig_type: str
    list_type: Optional[int] = None
    info_query: Optional[str] = None
    link_template_refs: Optional[Dict[Union[str, GamespyPrincipal], List[str]]] = None


@dataclass
class ValveGameConfig:
    app_id: int
    principals: List[ValvePrincipal]
    query_port_offset: Optional[int] = None
    link_template_refs: Optional[Dict[Union[str, ValvePrincipal], List[str]]] = None
