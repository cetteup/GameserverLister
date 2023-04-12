from typing import Dict

from GameserverLister.common.types import ValvePrincipal, ValvePrincipalConfig, ValveGame, ValveGameConfig

VALVE_PRINCIPAL_CONFIGS: Dict[ValvePrincipal, ValvePrincipalConfig] = {
    ValvePrincipal.VALVE: ValvePrincipalConfig(
        hostname='hl2master.steampowered.com',
        port=27011
    )
}
VALVE_GAME_CONFIGS: Dict[ValveGame, ValveGameConfig] = {
    ValveGame.AmericasArmyProvingGrounds: ValveGameConfig(
        app_id=203290,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
    ),
    ValveGame.ARKSurvivalEvolved: ValveGameConfig(
        app_id=346110,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.Arma2: ValveGameConfig(
        app_id=33930,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
    ),
    ValveGame.Arma3: ValveGameConfig(
        app_id=107410,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
    ),
    ValveGame.CounterStrike: ValveGameConfig(
        app_id=10,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.CounterStrikeConditionZero: ValveGameConfig(
        app_id=80,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.CounterStrikeSource: ValveGameConfig(
        app_id=240,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.CounterStrikeGlobalOffensive: ValveGameConfig(
        app_id=730,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.DayZ: ValveGameConfig(
        app_id=221100,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
    ),
    ValveGame.DayZMod: ValveGameConfig(
        app_id=224580,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
    ),
    ValveGame.DoD: ValveGameConfig(
        app_id=30,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.DoDS: ValveGameConfig(
        app_id=300,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.GarrysMod: ValveGameConfig(
        app_id=4000,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.Insurgency: ValveGameConfig(
        app_id=222880,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.InsurgencySandstorm: ValveGameConfig(
        app_id=581320,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
    ),
    ValveGame.Left4Dead: ValveGameConfig(
        app_id=500,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.Left4Dead2: ValveGameConfig(
        app_id=550,
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
    ValveGame.SevenD2D: ValveGameConfig(
        app_id=251570,
        principals=[
            ValvePrincipal.VALVE
        ]
    ),
    ValveGame.Squad: ValveGameConfig(
        app_id=393380,
        principals=[
            ValvePrincipal.VALVE
        ],
        distinct_query_port=True
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
