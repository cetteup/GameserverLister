import os
import socket

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
GSLIST_CONFIGS = {
    'crysis': {
        'gameName': 'crysis',
        'gameKey': 'ZvZDcL',
        'encType': '-1',
        'superQueryType': '8',
        'servers': {
            'crymp.net': {
                'hostname': 'master.crymp.net',
                'port': 28910
            }
        }
    },
    'crysiswars': {
        'gameName': 'crysiswars',
        'gameKey': 'zKbZiM',
        'encType': '-1',
        'superQueryType': '8',
        'servers': {
            'jedi95.us': {
                'hostname': 'master.g.jedi95.us',
                'port': 28910
            }
        }
    },
    'bf1942': {
        'gameName': 'bfield1942',
        'gameKey': 'HpWx9z',
        'encType': '2',
        'superQueryType': '0',
        'servers': {
            'bf1942.sk': {
                'hostname': 'master.bf1942.sk',
                'port': 28900
            },
            'qtracker': {
                'hostname': 'master2.qtracker.com',
                'port': 28900
            }
        }
    },
    'bfvietnam': {
        'gameName': 'bfvietnam',
        'gameKey': 'h2P9dJ',
        'encType': '2',
        'superQueryType': '0',
        'servers': {
            'qtracker': {
                'hostname': 'master2.qtracker.com',
                'port': 28900
            }
        }
    },
    'bf2142': {
        'gameName': 'stella',
        'gameKey': 'M8o1Qw',
        'encType': '-1',
        'superQueryType': '8',
        'servers': {
            'openspy': {
                'hostname': 'stella.ms5.openspy.net',
                'port': 28910
            },
            'play2142': {
                'hostname': 'stella.ms.play2142.ru',
                'port': 28910
            }
        }
    },
    'bf2': {
        'gameName': 'battlefield2',
        'gameKey': 'hW6m9a',
        'encType': '-1',
        'superQueryType': '8',
        'servers': {
            'bf2hub': {
                'hostname': 'servers.bf2hub.com',
                'port': 28911
            },
            'playbf2': {
                'hostname': 'battlefield2.ms.playbf2.ru',
                'port': 28910
            }
        }
    },
    'vietcong': {
        'gameName': 'vietcong',
        'gameKey': 'bq98mE',
        'encType': '2',
        'superQueryType': '0',
        'servers': {
            'vietcong.tk': {
                'hostname': 'brvps.tk',
                'port': 28900
            },
            'vietcong1.eu': {
                'hostname': 'vietcong1.eu',
                'port': 28900
            },
            'qtracker': {
                'hostname': 'master2.qtracker.com',
                'port': 28900
            }
        }
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
    'openarena': {
        'protocol': 71,
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
    'swjk': {
        'protocol': 26,
        'servers': {
            'ravensoft': {
                'hostname': 'masterjk3.ravensoft.com',
                'port': 29060
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
    }
}
