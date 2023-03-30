from typing import Dict

from GameserverLister.common.types import Unreal2Game

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
            'openspy.net': {
                'hostname': 'utmaster.openspy.net',
                'port': 28902
            },
            '333networks.com': {
                'hostname': 'ut2004master.333networks.com',
                'port': 28902
            },
            'errorist.eu': {
                'hostname': 'ut2004master.errorist.eu',
                'port': 28902
            }
        }
    }
}
