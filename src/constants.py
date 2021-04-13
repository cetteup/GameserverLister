import os

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
GSLIST_CONFIGS = {
    'bf1942': {
        'gameName': 'bfield1942',
        'gameKey': 'HpWx9z',
        'encType': '2',
        'superQueryType': '0',
        'servers': {
            'bf1942.sk': {
                'hostname': 'master.bf1942.sk',
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
    }
}
BATTLELOG_GAME_BASE_URIS = {
    'bf3': 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    'bf4': 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/',
    'bfh': 'https://battlelog.battlefield.com/bfh/servers/getServers/pc/',
    'mohwf': 'https://battlelog.battlefield.com/mohw/servers/getAutoBrowseServers/'
}
