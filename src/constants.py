import os
import socket
from datetime import datetime, timezone

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
GAMESPY_CONFIGS = {
    'crysis': {
        'gameName': 'crysis',
        'gameKey': 'ZvZDcL',
        'encType': '-1',
        'queryType': '8',
        'port': 28910,
        'servers': ['crymp.net'],
        'gamedigType': 'crysis'
    },
    'crysiswars': {
        'gameName': 'crysiswars',
        'gameKey': 'zKbZiM',
        'encType': '-1',
        'queryType': '8',
        'port': 28910,
        'servers': ['jedi95.us'],
        'gamedigType': 'crysiswars'
    },
    'bf1942': {
        'gameName': 'bfield1942',
        'gameKey': 'HpWx9z',
        'encType': '2',
        'queryType': '0',
        'port': 28900,
        'servers': ['bf1942.org', 'openspy', 'qtracker'],
        'gamedigType': 'bf1942'
    },
    'bfvietnam': {
        'gameName': 'bfvietnam',
        'gameKey': 'h2P9dJ',
        'encType': '2',
        'queryType': '0',
        'port': 28900,
        'servers': ['openspy', 'qtracker'],
        'gamedigType': 'bfv'
    },
    'bf2142': {
        'gameName': 'stella',
        'gameKey': 'M8o1Qw',
        'encType': '-1',
        'queryType': '8',
        'port': 28910,
        'servers': ['novgames', 'openspy', 'play2142'],
        'gamedigType': 'bf2142'
    },
    'bf2': {
        'gameName': 'battlefield2',
        'gameKey': 'hW6m9a',
        'encType': '-1',
        'queryType': '8',
        'port': 28910,
        'servers': ['bf2hub', 'openspy', 'phoenixnetwork', 'playbf2'],
        'gamedigType': 'bf2',
        'linkTemplateRefs': {
            '_any': ['bf2.tv'],
            'bf2hub': ['bf2hub']
        }
    },
    'jbnightfire': {
        'gameName': 'jbnightfire',
        'gameKey': 'S9j3L2',
        'encType': '-1',
        'queryType': '0',
        'port': 28910,
        'servers': ['openspy', 'nightfirepc.com'],
        'gamedigType': 'jamesbondnightfire'
    },
    'paraworld': {
        'gameName': 'paraworld',
        'gameKey': 'EUZpQF',
        'encType': '-1',
        'queryType': '8',
        'port': 28910,
        'servers': ['openspy'],
        'gamedigType': 'protocol-gamespy2'
    },
    'postal2': {
        'gameName': 'postal2',
        'gameKey': 'yw3R9c',
        'encType': '0',
        'queryType': '0',
        'port': 28900,
        'servers': ['333networks.com-1'],
        'gamedigType': 'postal2'
    },
    'vietcong': {
        'gameName': 'vietcong',
        'gameKey': 'bq98mE',
        'encType': '2',
        'queryType': '0',
        'port': 28900,
        'servers': ['vietcong.tk', 'vietcong1.eu', 'qtracker'],
        'gamedigType': 'vietcong'
    },
    'vietcong2': {
        'gameName': 'vietcong2',
        'gameKey': 'zX2pq6',
        'encType': '-1',
        'queryType': '8',
        'port': 28910,
        'servers': ['openspy'],
        'gamedigType': 'vietcong2'
    }
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
        'network_protocol': socket.SOCK_STREAM,
        'server_entry_prefix': b'\x00\x00\x00\x00\x04',
        'servers': {
            'cod4x.me': {
                'hostname': 'cod4master.cod4x.me',
                'port': 20810
            },
            'doszgep.cloud': {
                'hostname': 'cod4master.doszgep.cloud',
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
        }
    },
    'openarena': {
        'protocols': [
            71
        ],
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
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
    'sof2-demo': {
        'protocols': [
            2001
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    'sof2-full': {
        'protocols': [
            2002
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    'sof2-gold': {
        'protocols': [
            2004
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    'swjk': {
        'protocols': [
            26
        ],
        'servers': {
            'ravensoft': {
                'hostname': 'masterjk3.ravensoft.com',
                'port': 29060
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
        }
    }
}
GAMETRACKER_GAME_KEYS = {
    'bfvietnam': 'bfv',
    'bfbc2': 'bc2',
    'bfh': 'bfhl',
    'crysiswars': 'warhead',
    'mohbt': 'bt',
    'mohsh': 'sh',
    'mohwf': 'mohw'
}
