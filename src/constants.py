import os
import socket
from datetime import datetime, timezone
from typing import Dict

from src.types import GamespyGameConfig, GamespyGame, GamespyPrincipal, GamespyPrincipalConfig, Quake3Game, \
    BattlelogGame, Game, TheaterGame, MedalOfHonorGame, Unreal2Game, ValvePrincipal, ValvePrincipalConfig, \
    ValveGameConfig, ValveGame

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
UNIX_EPOCH_START = datetime(1970, 1, 1, tzinfo=timezone.utc)
GAMESPY_PRINCIPAL_CONFIGS: Dict[GamespyPrincipal, GamespyPrincipalConfig] = {
    GamespyPrincipal.THREE_THREE_THREE_NETWORKS_COM_1: GamespyPrincipalConfig(
        hostname='master.333networks.com'
    ),
    GamespyPrincipal.THREE_THREE_THREE_NETWORKS_COM_2: GamespyPrincipalConfig(
        hostname='rhea.333networks.com'
    ),
    GamespyPrincipal.BF1942_ORG: GamespyPrincipalConfig(
        hostname='master.bf1942.org'
    ),
    GamespyPrincipal.BF2HUB: GamespyPrincipalConfig(
        hostname='servers.bf2hub.com',
        port_offset=1
    ),
    GamespyPrincipal.CRYMP_NET: GamespyPrincipalConfig(
        hostname='master.crymp.net'
    ),
    GamespyPrincipal.EPIC_GAMES_UT3: GamespyPrincipalConfig(
        hostname='ut3master1.epicgames.com'
    ),
    GamespyPrincipal.ERRORIST_EU: GamespyPrincipalConfig(
        hostname='master.errorist.eu'
    ),
    GamespyPrincipal.FH2_DEV: GamespyPrincipalConfig(
        hostname='ms.fh2.dev'
    ),
    GamespyPrincipal.JEDI95_US: GamespyPrincipalConfig(
        hostname='master.g.jedi95.us'
    ),
    GamespyPrincipal.NEWBIESPLAYGROUND_NET: GamespyPrincipalConfig(
        hostname='master.newbiesplayground.net'
    ),
    GamespyPrincipal.NIGHTFIREPC_COM: GamespyPrincipalConfig(
        hostname='master.nightfirepc.com' # This (currently) just points at openspy
    ),
    GamespyPrincipal.NOVGAMES: GamespyPrincipalConfig(
        hostname='2142.novgames.ru'
    ),
    GamespyPrincipal.OLDUNREAL_COM_1: GamespyPrincipalConfig(
        hostname='master.oldunreal.com'
    ),
    GamespyPrincipal.OLDUNREAL_COM_2: GamespyPrincipalConfig(
        hostname='master2.oldunreal.com'
    ),
    GamespyPrincipal.OPENSPY: GamespyPrincipalConfig(
        hostname='{0}.master.openspy.net'
    ),
    GamespyPrincipal.PHOENIX_NETWORK: GamespyPrincipalConfig(
        hostname='master.phoenixnetwork.net'
    ),
    GamespyPrincipal.PLAY2142: GamespyPrincipalConfig(
        hostname='{0}.ms.play2142.ru'
    ),
    GamespyPrincipal.PLAYBF2: GamespyPrincipalConfig(
        hostname='{0}.ms.playbf2.ru'
    ),
    GamespyPrincipal.QTRACKER: GamespyPrincipalConfig(
        hostname='master2.qtracker.com'
    ),
    GamespyPrincipal.SWAT4STATS_COM: GamespyPrincipalConfig(
        hostname='master.swat4stats.com'
    ),
    GamespyPrincipal.VIETCONG_TK: GamespyPrincipalConfig(
        hostname='brvps.tk'
    ),
    GamespyPrincipal.VIETCONG1_EU: GamespyPrincipalConfig(
        hostname='vietcong1.eu'
    )
}
GAMESPY_GAME_CONFIGS: Dict[GamespyGame, GamespyGameConfig] = {
    GamespyGame.BF1942: GamespyGameConfig(
        game_name='bfield1942',
        game_key='HpWx9z',
        enc_type=2,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.BF1942_ORG,
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.QTRACKER
        ],
        gamedig_type='bf1942'
    ),
    GamespyGame.BFVIETNAM: GamespyGameConfig(
        game_name='bfvietnam',
        game_key='h2P9dJ',
        enc_type=2,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.QTRACKER
        ],
        gamedig_type='bfv'
    ),
    GamespyGame.BF2: GamespyGameConfig(
        game_name='battlefield2',
        game_key='hW6m9a',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.BF2HUB,
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.PHOENIX_NETWORK,
            GamespyPrincipal.PLAYBF2
        ],
        gamedig_type='bf2',
        link_template_refs={
            '_any': ['bf2.tv'],
            GamespyPrincipal.BF2HUB: ['bf2hub']
        }
    ),
    GamespyGame.FH2: GamespyGameConfig(
        game_name='battlefield2',
        game_key='hW6m9a',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.FH2_DEV
        ],
        gamedig_type='bf2',
        info_query='\\hostname'
    ),
    GamespyGame.BF2142: GamespyGameConfig(
        game_name='stella',
        game_key='M8o1Qw',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.NOVGAMES,
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.PLAY2142
        ],
        gamedig_type='bf2142'
    ),
    GamespyGame.CRYSIS: GamespyGameConfig(
        game_name='crysis',
        game_key='ZvZDcL',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.CRYMP_NET
        ],
        gamedig_type='crysis'
    ),
    GamespyGame.CRYSISWARS: GamespyGameConfig(
        game_name='crysiswars',
        game_key='zKbZiM',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.JEDI95_US
        ],
        gamedig_type='crysiswars'
    ),
    GamespyGame.JBNIGHTFIRE: GamespyGameConfig(
        game_name='jbnightfire',
        game_key='S9j3L2',
        enc_type=-1,
        query_type=0,
        port=28910,
        principals=[
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.NIGHTFIREPC_COM
        ],
        gamedig_type='jamesbondnightfire'
    ),
    GamespyGame.PARAWORLD: GamespyGameConfig(
        game_name='paraworld',
        game_key='EUZpQF',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.OPENSPY
        ],
        gamedig_type='protocol-gamespy2'
    ),
    GamespyGame.POSTAL2: GamespyGameConfig(
        game_name='postal2',
        game_key='yw3R9c',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.THREE_THREE_THREE_NETWORKS_COM_1
        ],
        gamedig_type='postal2'
    ),
    GamespyGame.SWAT4: GamespyGameConfig(
        game_name='swat4',
        game_key='tG3j8c',
        enc_type=-1,
        query_type=0,
        port=28910,
        principals=[
            GamespyPrincipal.SWAT4STATS_COM
        ],
        gamedig_type='swat4',
        # The SWAT 4 principal is the only one which does not return servers if the list type byte is set to 1,
        # so we need to set it to 0 (only possible using a modified version glist: https://github.com/cetteup/gslist)
        list_type=0,
        info_query='\\hostname',
        link_template_refs={
            GamespyPrincipal.SWAT4STATS_COM: ['swat4stats.com']
        }
    ),
    GamespyGame.UNREAL: GamespyGameConfig(
        game_name='unreal',
        game_key='DAncRK',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.THREE_THREE_THREE_NETWORKS_COM_1,
            GamespyPrincipal.OLDUNREAL_COM_1,
            GamespyPrincipal.ERRORIST_EU,
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.QTRACKER
        ],
        gamedig_type='unreal'
    ),
    GamespyGame.UT: GamespyGameConfig(
        game_name='ut',
        game_key='Z5Nfb0',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.THREE_THREE_THREE_NETWORKS_COM_1,
            GamespyPrincipal.OLDUNREAL_COM_1,
            GamespyPrincipal.ERRORIST_EU,
            GamespyPrincipal.OPENSPY,
            GamespyPrincipal.QTRACKER
        ],
        gamedig_type='ut'
    ),
    GamespyGame.UT3: GamespyGameConfig(
        game_name='ut3pc',
        game_key='nT2Mtz',
        enc_type=-1,
        query_type=11,
        port=28910,
        principals=[
            GamespyPrincipal.EPIC_GAMES_UT3
        ],
        gamedig_type='ut3'
    ),
    GamespyGame.VIETCONG: GamespyGameConfig(
        game_name='vietcong',
        game_key='bq98mE',
        enc_type=2,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.VIETCONG_TK,
            GamespyPrincipal.VIETCONG1_EU,
            GamespyPrincipal.QTRACKER
        ],
        gamedig_type='vietcong'
    ),
    GamespyGame.VIETCONG2: GamespyGameConfig(
        game_name='vietcong2',
        game_key='zX2pq6',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.OPENSPY
        ],
        gamedig_type='vietcong2'
    )
}
VALVE_PRINCIPAL_CONFIGS: Dict[ValvePrincipal, ValvePrincipalConfig] = {
    ValvePrincipal.VALVE: ValvePrincipalConfig(
        hostname='hl2master.steampowered.com',
        port=27011
    )
}
VALVE_GAME_CONFIGS: Dict[ValveGame, ValveGameConfig] = {
    ValveGame.DOD: ValveGameConfig(
        app_id=30,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.DODS: ValveGameConfig(
        app_id=300,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.RS2: ValveGameConfig(
        app_id=418460,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.Rust: ValveGameConfig(
        app_id=252490,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.SEVEND2D: ValveGameConfig(
        app_id=251570,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.TFC: ValveGameConfig(
        app_id=20,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.TF2: ValveGameConfig(
        app_id=440,
        principals=[
            ValvePrincipal.VALVE
        ]
    )
}
BATTLELOG_GAME_BASE_URIS: Dict[BattlelogGame, str] = {
    BattlelogGame.BF3: 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    BattlelogGame.BF4: 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/',
    BattlelogGame.BFH: 'https://battlelog.battlefield.com/bfh/servers/getServers/pc/',
    BattlelogGame.MOHWF: 'https://battlelog.battlefield.com/mohw/servers/getAutoBrowseServers/'
}
GAMETOOLS_BASE_URI = 'https://api.gametools.network'
QUAKE3_CONFIGS: Dict[Quake3Game, dict] = {
    Quake3Game.COD: {
        'protocols': [
            1,  # version 1.1
            2,  # version 1.2
            4,  # version 1.3
            5,  # version 1.4
            6,  # version 1.5
        ],
        'servers': {
            'activision': {
                'hostname': 'codmaster.activision.com',
                'port': 20510
            }
        },
        'linkTemplateRefs': {
            'activision': ['cod.pm']
        }
    },
    Quake3Game.CODUO: {
        'protocols': [
            21,  # version 1.41
            22,  # version 1.51
        ],
        'servers': {
            'activision': {
                'hostname': 'coduomaster.activision.com',
                'port': 20610
            }
        },
        'linkTemplateRefs': {
            'activision': ['cod.pm']
        }
    },
    Quake3Game.COD2: {
        'protocols': [
            115,  # version 1.0
            117,  # version 1.2
            118,  # version 1.3
        ],
        'servers': {
            'activision': {
                'hostname': 'cod2master.activision.com',
                'port': 20710
            }
        },
        'linkTemplateRefs': {
            'activision': ['cod.pm']
        }
    },
    Quake3Game.COD4: {
        'protocols': [
            1,  # version 1.0
            6,  # version 1.7
            7,  # version 1.8
        ],
        'servers': {
            'activision': {
                'hostname': 'cod4master.activision.com',
                'port': 20810
            }
        },
        'linkTemplateRefs': {
            'activision': ['cod.pm']
        }
    },
    Quake3Game.COD4X: {
        'protocols': [
            6  # cod4 does not support different protocols, you seem to get the same servers regardless
        ],
        'keywords': 'full empty \x00',
        'game_name': 'cod4x',
        'network_protocol': socket.SOCK_STREAM,
        'server_entry_prefix': b'\x00\x00\x00\x00\x04',
        'servers': {
            'cod4x.ovh': {
                'hostname': 'cod4master.cod4x.ovh',
                'port': 20810
            }
        }
    },
    Quake3Game.NEXUIZ: {
        'protocols': [
            3
        ],
        'game_name': 'Nexuiz',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official']
        }
    },
    Quake3Game.OPENARENA: {
        'protocols': [
            71
        ],
        'game_name': 'Quake3Arena',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official', 'arena.sh']
        }
    },
    Quake3Game.Q3RALLY: {
        'protocols': [
            71
        ],
        'game_name': 'Q3Rally',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official']
        }
    },
    Quake3Game.QUAKE: {
        'protocols': [
            3
        ],
        'game_name': 'DarkPlaces-Quake',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official']
        }
    },
    Quake3Game.QUAKE3ARENA: {
        'protocols': [
            68
        ],
        'servers': {
            'quake3arena.com': {
                'hostname': 'master.quake3arena.com',
                'port': 27950
            },
            'urbanterror.info-1': {
                'hostname': 'master.urbanterror.info',
                'port': 27900
            },
            'urbanterror.info-2': {
                'hostname': 'master2.urbanterror.info',
                'port': 27900
            },
            'excessiveplus.net': {
                'hostname': 'master0.excessiveplus.net',
                'port': 27950
            },
            'ioquake3.org': {
                'hostname': 'master.ioquake3.org',
                'port': 27950
            },
            'huxxer.de': {
                'hostname': 'master.huxxer.de',
                'port': 27950
            },
            'maverickservers.com': {
                'hostname': 'master.maverickservers.com',
                'port': 27950
            },
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    Quake3Game.RTCW: {
        'protocols': [
            57
        ],
        'servers': {
            'idsoftware': {
                'hostname': 'wolfmaster.idsoftware.com',
                'port': 27950
            }
        }
    },
    Quake3Game.SOF2: {
        'protocols': [
            2001,  # version sof2mp-1.02t (demo)
            2002,  # version sof2mp-1.00 (full)
            2004,  # version sof2mp-1.02 ("gold")
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    Quake3Game.SWJKJA: {
        'protocols': [
            25,  # version 1.00
            26,  # version 1.01
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'masterjk3.ravensoft.com',
                'port': 29060
            },
            'jkhub.org': {
                'hostname': 'master.jkhub.org',
                'port': 29060
            }
        }
    },
    Quake3Game.SWJKJO: {
        'protocols': [
            15,  # version 1.02
            16,  # version 1.04
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'masterjk2.ravensoft.com',
                'port': 28060
            },
            'jkhub.org': {
                'hostname': 'master.jkhub.org',
                'port': 28060
            }
        }
    },
    Quake3Game.TREMULOUS: {
        'protocols': [
            69
        ],
        'servers': {
            'tremulous.net': {
                'hostname': 'master.tremulous.net',
                'port': 30710
            }
        },
        'linkTemplateRefs': {
            'tremulous.net': ['deathmask.net-unofficial']
        }
    },
    Quake3Game.URBANTERROR: {
        'protocols': [
            68
        ],
        'servers': {
            'urbanterror.info': {
                'hostname': 'master.urbanterror.info',
                'port': 27900
            }
        },
        'linkTemplateRefs': {
            'urbanterror.info': ['deathmask.net-unofficial']
        }
    },
    Quake3Game.WARFORK: {
        'protocols': [
            23
        ],
        'game_name': 'Warfork',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official']
        }
    },
    Quake3Game.WARSOW: {
        'protocols': [
            22
        ],
        'game_name': 'Warsow',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official', 'arena.sh']
        }
    },
    Quake3Game.WOLFENSTEINET: {
        'protocols': [
            84
        ],
        'servers': {
            'idsoftware': {
                'hostname': 'etmaster.idsoftware.com',
                'port': 27950
            },
            'etlegacy.com': {
                'hostname': 'master.etlegacy.com',
                'port': 27950
            }
        }
    },
    Quake3Game.XONOTIC: {
        'protocols': [
            3
        ],
        'game_name': 'Xonotic',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            },
            'tchr.no': {
                'hostname': 'dpmaster.tchr.no',
                'port': 27950
            }
        },
        'linkTemplateRefs': {
            'deathmask.net': ['deathmask.net-official', 'arena.sh']
        }
    }
}
UNREAL2_CONFIGS: Dict[Unreal2Game, dict] = {
    Unreal2Game.UT2003: {
        'servers': {
            'openspy.net': {
                'hostname': 'utmaster.openspy.net',
                'port': 28902
            }
        }
    },
    Unreal2Game.UT2004: {
        'servers': {
            'epicgames.com': {
                'hostname': 'ut2004master1.epicgames.com',
                'port': 28902
            },
            'openspy.net': {
                'hostname': 'utmaster.openspy.net',
                'port': 28902
            }
        }
    }
}
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
