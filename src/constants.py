import os
import socket

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
GAMESPY_PRINCIPALS = {
    '333networks.com-1': {
        'hostname': 'master.333networks.com',
        'port': 28900
    },
    '333networks.com-2': {
        'hostname': 'rhea.333networks.com',
        'port': 28900
    },
    'bf1942.sk': {
        'hostname': 'master.bf1942.sk',
        'port': 28900
    },
    'bf2hub': {
        'hostname': 'servers.bf2hub.com',
        'port': 28911
    },
    'crymp.net': {
        'hostname': 'master.crymp.net',
        'port': 28910
    },
    'errorist.eu': {
        'hostname': 'master.errorist.eu',
        'port': 28900
    },
    'jedi95.us': {
        'hostname': 'master.g.jedi95.us',
        'port': 28910
    },
    'newbiesplayground.net': {
        'hostname': 'master.newbiesplayground.net',
        'port': 28900
    },
    'oldunreal.com': {
        'hostname': 'master2.oldunreal.com',
        'port': 28900
    },
    'openspy': {
        'hostname': 'stella.ms5.openspy.net',
        'port': 28910
    },
    'phoenixnetwork': {
        'hostname': 'master.phoenixnetwork.net',
        'port': 28910
    },
    'play2142': {
        'hostname': 'stella.ms.play2142.ru',
        'port': 28910
    },
    'playbf2': {
        'hostname': 'battlefield2.ms.playbf2.ru',
        'port': 28910
    },
    'qtracker': {
        'hostname': 'master2.qtracker.com',
        'port': 28900
    },
    'vietcong.tk': {
        'hostname': 'brvps.tk',
        'port': 28900
    },
    'vietcong1.eu': {
        'hostname': 'vietcong1.eu',
        'port': 28900
    }
}
GSLIST_CONFIGS = {
    'crysis': {
        'gameName': 'crysis',
        'gameKey': 'ZvZDcL',
        'encType': '-1',
        'superQueryType': '8',
        'servers': ['crymp.net']
    },
    'crysiswars': {
        'gameName': 'crysiswars',
        'gameKey': 'zKbZiM',
        'encType': '-1',
        'superQueryType': '8',
        'servers': ['jedi95.us']
    },
    'bf1942': {
        'gameName': 'bfield1942',
        'gameKey': 'HpWx9z',
        'encType': '2',
        'superQueryType': '0',
        'servers': ['bf1942.sk', 'qtracker']
    },
    'bfvietnam': {
        'gameName': 'bfvietnam',
        'gameKey': 'h2P9dJ',
        'encType': '2',
        'superQueryType': '0',
        'servers': ['qtracker']
    },
    'bf2142': {
        'gameName': 'stella',
        'gameKey': 'M8o1Qw',
        'encType': '-1',
        'superQueryType': '8',
        'servers': ['openspy', 'play2142']
    },
    'bf2': {
        'gameName': 'battlefield2',
        'gameKey': 'hW6m9a',
        'encType': '-1',
        'superQueryType': '8',
        'servers': ['bf2hub', 'phoenixnetwork', 'playbf2']
    },
    'postal2': {
        'gameName': 'postal2',
        'gameKey': 'yw3R9c',
        'encType': '0',
        'superQueryType': '0',
        'servers': ['333networks.com-1']
    },
    'vietcong': {
        'gameName': 'vietcong',
        'gameKey': 'bq98mE',
        'encType': '2',
        'superQueryType': '0',
        'servers': ['vietcong.tk', 'vietcong1.eu', 'qtracker']
    }
}
BATTLELOG_GAME_BASE_URIS = {
    'bf3': 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    'bf4': 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/',
    'bfh': 'https://battlelog.battlefield.com/bfh/servers/getServers/pc/',
    'mohwf': 'https://battlelog.battlefield.com/mohw/servers/getAutoBrowseServers/'
}
QUAKE3_CONFIGS = {
    'cod': {
        'protocol': 6,
        'servers': {
            'activision': {
                'hostname': 'codmaster.activision.com',
                'port': 20510
            }
        }
    },
    'coduo': {
        'protocol': 22,
        'servers': {
            'activision': {
                'hostname': 'coduomaster.activision.com',
                'port': 20610
            }
        }
    },
    'cod2': {
        'protocol': 118,
        'servers': {
            'activision': {
                'hostname': 'cod2master.activision.com',
                'port': 20710
            }
        }
    },
    'cod4': {
        'protocol': 6,
        'servers': {
            'activision': {
                'hostname': 'cod4master.activision.com',
                'port': 20810
            }
        }
    },
    'cod4x': {
        'protocol': 6,
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
        'protocol': 3,
        'game_name': 'Nexuiz',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    'openarena': {
        'protocol': 71,
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    'q3rally': {
        'protocol': 71,
        'game_name': 'Q3Rally',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    'quake': {
        'protocol': 3,
        'game_name': 'DarkPlaces-Quake',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    'quake3arena': {
        'protocol': 68,
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
        'protocol': 57,
        'servers': {
            'idsoftware': {
                'hostname': 'wolfmaster.idsoftware.com',
                'port': 27950
            }
        }
    },
    'sof2-demo': {
        'protocol': 2001,
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    'sof2-full': {
        'protocol': 2002,
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    'sof2-gold': {
        'protocol': 2004,
        'servers': {
            'ravensoft': {
                'hostname': 'master.sof2.ravensoft.com',
                'port': 20110
            }
        }
    },
    'swjk': {
        'protocol': 26,
        'servers': {
            'ravensoft': {
                'hostname': 'masterjk3.ravensoft.com',
                'port': 29060
            }
        }
    },
    'tremulous': {
        'protocol': 69,
        'servers': {
            'tremulous.net': {
                'hostname': 'master.tremulous.net',
                'port': 30710
            }
        }
    },
    'urbanterror': {
        'protocol': 68,
        'servers': {
            'urbanterror.info': {
                'hostname': 'master.urbanterror.info',
                'port': 27900
            }
        }
    },
    'warfork': {
        'protocol': 23,
        'game_name': 'Warfork',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    'warsow': {
        'protocol': 22,
        'game_name': 'Warsow',
        'servers': {
            'deathmask.net': {
                'hostname': 'dpmaster.deathmask.net',
                'port': 27950
            }
        }
    },
    'wolfensteinet': {
        'protocol': 84,
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
        'protocol': 3,
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
