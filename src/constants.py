import os
import socket
from datetime import datetime, timezone
from typing import Dict

from src.types import GamespyConfig

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
UNIX_EPOCH_START = datetime(1970, 1, 1, tzinfo=timezone.utc)
GAMESPY_PRINCIPALS = {
    '333networks.com-1': {
        'hostname': 'master.333networks.com'
    },
    '333networks.com-2': {
        'hostname': 'rhea.333networks.com'
    },
    'bf1942.org': {
        'hostname': 'master.bf1942.org'
    },
    'bf2hub': {
        'hostname': 'servers.bf2hub.com',
        'portOffset': 1
    },
    'crymp.net': {
        'hostname': 'master.crymp.net'
    },
    'errorist.eu': {
        'hostname': 'master.errorist.eu'
    },
    'jedi95.us': {
        'hostname': 'master.g.jedi95.us',
    },
    'newbiesplayground.net': {
        'hostname': 'master.newbiesplayground.net'
    },
    'nightfirepc.com': {
        # This (currently) just points at openspy
        'hostname': 'master.nightfirepc.com'
    },
    'novgames': {
        'hostname': '2142.novgames.ru'
    },
    'oldunreal.com': {
        'hostname': 'master2.oldunreal.com'
    },
    'openspy': {
        'hostname': '{0}.master.openspy.net'
    },
    'phoenixnetwork': {
        'hostname': 'master.phoenixnetwork.net'
    },
    'play2142': {
        'hostname': '{0}.ms.play2142.ru'
    },
    'playbf2': {
        'hostname': '{0}.ms.playbf2.ru'
    },
    'qtracker': {
        'hostname': 'master2.qtracker.com'
    },
    'vietcong.tk': {
        'hostname': 'brvps.tk'
    },
    'vietcong1.eu': {
        'hostname': 'vietcong1.eu'
    }
}
GAMESPY_CONFIGS: Dict[str, GamespyConfig] = {
    'crysis': GamespyConfig(
        game_name='crysis',
        game_key='ZvZDcL',
        enc_type=-1,
        query_type=8,
        port=28910,
        servers=['crymp.net'],
        gamedig_type='crysis'
    ),
    'crysiswars': GamespyConfig(
        game_name='crysiswars',
        game_key='zKbZiM',
        enc_type=-1,
        query_type=8,
        port=28910,
        servers=['jedi95.us'],
        gamedig_type='crysiswars'
    ),

    'bf1942': GamespyConfig(
        game_name='bfield1942',
        game_key='HpWx9z',
        enc_type=2,
        query_type=0,
        port=28900,
        servers=['bf1942.org', 'openspy', 'qtracker'],
        gamedig_type='bf1942'
    ),

    'bfvietnam': GamespyConfig(
        game_name='bfvietnam',
        game_key='h2P9dJ',
        enc_type=2,
        query_type=0,
        port=28900,
        servers=['openspy', 'qtracker'],
        gamedig_type='bfv'
    ),
    'bf2142': GamespyConfig(
        game_name='stella',
        game_key='M8o1Qw',
        enc_type=-1,
        query_type=8,
        port=28910,
        servers=['novgames', 'openspy', 'play2142'],
        gamedig_type='bf2142'
    ),
    'bf2': GamespyConfig(
        game_name='battlefield2',
        game_key='hW6m9a',
        enc_type=-1,
        query_type=8,
        port=28910,
        servers=['bf2hub', 'openspy', 'phoenixnetwork', 'playbf2'],
        gamedig_type='bf2',
        link_template_refs={
            '_any': ['bf2.tv'],
            'bf2hub': ['bf2hub']
        }
    ),
    'jbnightfire': GamespyConfig(
        game_name='jbnightfire',
        game_key='S9j3L2',
        enc_type=-1,
        query_type=0,
        port=28910,
        servers=['openspy', 'nightfirepc.com'],
        gamedig_type='jamesbondnightfire'
    ),
    'paraworld': GamespyConfig(
        game_name='paraworld',
        game_key='EUZpQF',
        enc_type=-1,
        query_type=8,
        port=28910,
        servers=['openspy'],
        gamedig_type='protocol-gamespy2'
    ),
    'postal2': GamespyConfig(
        game_name='postal2',
        game_key='yw3R9c',
        enc_type=0,
        query_type=0,
        port=28900,
        servers=['333networks.com-1'],
        gamedig_type='postal2'
    ),
    'vietcong': GamespyConfig(
        game_name='vietcong',
        game_key='bq98mE',
        enc_type=2,
        query_type=0,
        port=28900,
        servers=['vietcong.tk', 'vietcong1.eu', 'qtracker'],
        gamedig_type='vietcong'
    ),
    'vietcong2': GamespyConfig(
        game_name='vietcong2',
        game_key='zX2pq6',
        enc_type=-1,
        query_type=8,
        port=28910,
        servers=['openspy'],
        gamedig_type='vietcong2'
    )
}
BATTLELOG_GAME_BASE_URIS = {
    'bf3': 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    'bf4': 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/',
    'bfh': 'https://battlelog.battlefield.com/bfh/servers/getServers/pc/',
    'mohwf': 'https://battlelog.battlefield.com/mohw/servers/getAutoBrowseServers/'
}
GAMETOOLS_BASE_URI = 'https://api.gametools.network'
QUAKE3_CONFIGS = {
    'cod': {
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
    'coduo': {
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
    'cod2': {
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
    'cod4': {
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
    'cod4x': {
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
    'nexuiz': {
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
    'openarena': {
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
    'q3rally': {
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
    'quake': {
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
    'quake3arena': {
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
    'rtcw': {
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
    'sof2': {
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
    'swjkja': {
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
    'swjkjo': {
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
    'tremulous': {
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
    'urbanterror': {
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
    'warfork': {
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
    'warsow': {
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
    'wolfensteinet': {
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
    'xonotic': {
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
GAMETRACKER_GAME_KEYS = {
    'bf1942': 'bf1942',
    'bfvietnam': 'bfv',
    'bf2': 'bf2',
    'bf2142': 'bf2',  # GameTracker does not support 2142, so some servers are added as BF2 servers
    'bfbc2': 'bc2',
    'bf3': 'bf3',
    'bf4': 'bf4',
    'bfh': 'bfhl',
    'cod': 'cod',
    'coduo': 'uo',
    'cod2': 'cod2',
    'cod4': 'cod4',
    'crysis': 'crysis',
    'crysiswars': 'warhead',
    'mohaa': 'mohaa',
    'mohbt': 'bt',
    'mohsh': 'sh',
    'mohwf': 'mohw',
    'openarena': 'q3',  # GameTracker does not support OpenArena, so some servers are added as Quake 3 servers
    'quake3arena': 'q3',  # Quake3Arena servers are listed as Quake 3 servers
    'sof2': 'sof2',
    'swjkja': 'swjk',  # GameTracker seems to track all Jedi Knight servers in a single category
    'swjkjo': 'swjk',
    'urbanterror': 'urbanterror',
    'wolfensteinet': 'et',
}
