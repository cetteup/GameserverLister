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
    TripleThreeNetworks_com_1 = '333networks.com-1'
    TripleThreeNetworks_com_2 = '333networks.com-2'
    BF1942_org = 'bf1942.org'
    BF2Hub_com = 'bf2hub.com'
    Crymp_net = 'crymp.net'
    Errorist_eu = 'errorist.eu'
    FH2_dev = 'fh2.dev'
    Jedi95_us = 'jedi95.us'
    Newbiesplayground_net = 'newbiesplayground.net'
    NightfirePC_com = 'nightfirepc.com'
    NovGames_ru = 'novgames.ru'
    OldUnreal_com_1 = 'oldunreal.com-1'
    OldUnreal_com_2 = 'oldunreal.com-2'
    OpenSpy_net = 'openspy.net'
    PhoenixNetwork_net = 'phoenixnetwork.net'
    Play2142_ru = 'play2142.ru'
    PlayBF2_ru = 'playbf2.ru'
    Qtracker_com = 'qtracker.com'
    SWAT4Stats_com = 'swat4stats.com'
    Vietcong_tk = 'vietcong.tk'
    Vietcong1_eu = 'vietcong1.eu'


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
    BFVietnam = 'bfvietnam'
    BF2 = 'bf2'
    FH2 = 'fh2'
    BF2142 = 'bf2142'
    Crysis = 'crysis'
    CrysisWars = 'crysiswars'
    DeusEx = 'deusex'
    DukeNukemForever = 'dnf'
    JBNightfire = 'jbnightfire'
    Paraworld = 'paraworld'
    Postal2 = 'postal2'
    Rune = 'rune'
    SeriousSam = 'serioussam'
    SeriousSamSE = 'serioussamse'
    SWAT4 = 'swat4'
    Unreal = 'unreal'
    UT = 'ut'
    UT3 = 'ut3'
    Vietcong = 'vietcong'
    Vietcong2 = 'vietcong2'
    WheelOfTime = 'wot'


class Quake3Game(Game):
    CoD = 'cod'
    CoDUO = 'coduo'
    CoD2 = 'cod2'
    CoD4 = 'cod4'
    CoD4X = 'cod4x'
    Nexuiz = 'nexuiz'
    OpenArena = 'openarena'
    Q3Rally = 'q3rally'
    Quake = 'quake'
    Quake3Arena = 'quake3arena'
    RTCW = 'rtcw'
    SOF2 = 'sof2'
    SWJKJA = 'swjkja'
    SWJKJO = 'swjkjo'
    Tremulous = 'tremulous'
    UrbanTerror = 'urbanterror'
    Warfork = 'warfork'
    Warsow = 'warsow'
    WolfensteinET = 'wolfensteinet'
    Xonotic = 'xonotic'


class MedalOfHonorGame(Game):
    AA = 'mohaa'
    BT = 'mohbt'
    PA = 'mohpa'
    SH = 'mohsh'


class Unreal2Game(Game):
    UT2003 = 'ut2003'
    UT2004 = 'ut2004'


class ValveGame(Game):
    ARKSurvivalEvolved = 'arkse'
    Arma2 = 'arma2'
    Arma3 = 'arma3'
    CounterStrike  = 'cs'
    CounterStrikeConditionZero = 'cscz'
    CounterStrikeSource = 'css'
    CounterStrikeGlobalOffensive = 'csgo'
    DayZ = 'dayz'
    DayZMod = 'dayzmod'
    DoD = 'dod'
    DoDS = 'dods'
    RS2 = 'rs2'
    Rust = 'rust'
    SevenD2D = '7d2d'
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
    list_type: Optional[int] = None
    info_query: Optional[str] = None
    link_template_refs: Optional[Dict[Union[str, GamespyPrincipal], List[str]]] = None


@dataclass
class ValveGameConfig:
    app_id: int
    principals: List[ValvePrincipal]
    query_port_offset: Optional[int] = None
    link_template_refs: Optional[Dict[Union[str, ValvePrincipal], List[str]]] = None
