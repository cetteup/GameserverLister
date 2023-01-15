import os
from datetime import datetime, timezone
from typing import Dict

from GameserverLister.common.types import Game, ValveGame, GamespyGame, TheaterGame, BattlelogGame, Quake3Game, \
    MedalOfHonorGame, Unreal2Game

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
UNIX_EPOCH_START = datetime(1970, 1, 1, tzinfo=timezone.utc)
GAMETRACKER_GAME_KEYS: Dict[Game, str] = {
    ValveGame.SEVEND2D: '7daystodie',
    GamespyGame.BF1942: 'bf1942',
    GamespyGame.BFVIETNAM: 'bfv',
    GamespyGame.BF2: 'bf2',
    GamespyGame.FH2: 'bf2',  # Forgotten Hope 2 is technically a BF2 mod, so servers are added as BF2 servers
    GamespyGame.BF2142: 'bf2',  # GameTracker does not support 2142, so some servers are added as BF2 servers
    TheaterGame.BFBC2: 'bc2',
    BattlelogGame.BF3: 'bf3',
    BattlelogGame.BF4: 'bf4',
    BattlelogGame.BFH: 'bfhl',
    Quake3Game.COD: 'cod',
    Quake3Game.CODUO: 'uo',
    Quake3Game.COD2: 'cod2',
    Quake3Game.COD4: 'cod4',
    GamespyGame.CRYSIS: 'crysis',
    GamespyGame.CRYSISWARS: 'warhead',
    ValveGame.DOD: 'dod',
    ValveGame.DODS: 'dods',
    MedalOfHonorGame.AA: 'mohaa',
    MedalOfHonorGame.BT: 'bt',
    MedalOfHonorGame.SH: 'sh',
    BattlelogGame.MOHWF: 'mohw',
    Quake3Game.OPENARENA: 'q3',  # GameTracker does not support OpenArena, so some servers are added as Quake 3 servers
    Quake3Game.QUAKE3ARENA: 'q3',  # Quake3Arena servers are listed as Quake 3 servers
    ValveGame.Rust: 'rust',
    Quake3Game.SOF2: 'sof2',
    GamespyGame.SWAT4: 'swat4',
    Quake3Game.SWJKJA: 'swjk',  # GameTracker seems to track all Jedi Knight servers in a single category
    Quake3Game.SWJKJO: 'swjk',
    ValveGame.TFC: 'tfc',
    ValveGame.TF2: 'tf2',
    GamespyGame.UT: 'ut',
    Unreal2Game.UT2003: 'ut2k4',  # GameTracker does not support UT2003, so some servers are added UT2004 servers
    Unreal2Game.UT2004: 'ut2k4',
    GamespyGame.UT3: 'ut3',
    Quake3Game.URBANTERROR: 'urbanterror',
    Quake3Game.WOLFENSTEINET: 'et',
}
