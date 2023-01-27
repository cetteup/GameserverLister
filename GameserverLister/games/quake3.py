import socket
from typing import Dict

from GameserverLister.common.types import Quake3Game

QUAKE3_CONFIGS: Dict[Quake3Game, dict] = {
    Quake3Game.CoD: {
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
    Quake3Game.CoDUO: {
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
    Quake3Game.CoD2: {
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
    Quake3Game.CoD4: {
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
    Quake3Game.CoD4X: {
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
    Quake3Game.Nexuiz: {
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
    Quake3Game.OpenArena: {
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
    Quake3Game.Q3Rally: {
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
    Quake3Game.Quake: {
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
    Quake3Game.Quake3Arena: {
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
    Quake3Game.Tremulous: {
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
    Quake3Game.UrbanTerror: {
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
    Quake3Game.Warfork: {
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
    Quake3Game.Warsow: {
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
    Quake3Game.WolfensteinET: {
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
            },
            'etmaster.net': {
                'hostname': 'master0.etmaster.net',
                'port': 27950
            }
        }
    },
    Quake3Game.Xonotic: {
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
