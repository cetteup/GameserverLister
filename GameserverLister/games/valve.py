from typing import Dict

from GameserverLister.common.types import ValvePrincipal, ValvePrincipalConfig, ValveGame, ValveGameConfig

VALVE_PRINCIPAL_CONFIGS: Dict[ValvePrincipal, ValvePrincipalConfig] = {
    ValvePrincipal.VALVE: ValvePrincipalConfig(
        hostname='hl2master.steampowered.com',
        port=27011
    )
}
VALVE_GAME_CONFIGS: Dict[ValveGame, ValveGameConfig] = {
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
        query_port_offset=-1
    ),
    ValveGame.Arma3: ValveGameConfig(
        app_id=107410,
        principals=[
            ValvePrincipal.VALVE
        ],
        query_port_offset=-1
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
        query_port_offset=-1
    ),
    ValveGame.DayZMod: ValveGameConfig(
        app_id=224580,
        principals=[
            ValvePrincipal.VALVE
        ],
        query_port_offset=-1
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
