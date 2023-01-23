from typing import Dict

from GameserverLister.common.types import GamespyPrincipal, GamespyPrincipalConfig, GamespyGame, GamespyGameConfig

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
    GamespyPrincipal.EPIC_GAMES_UNREAL: GamespyPrincipalConfig(
        hostname='unreal.epicgames.com'
    ),
    GamespyPrincipal.EPIC_GAMES_UT: GamespyPrincipalConfig(
        hostname='utmaster.epicgames.com'
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
        hostname='master.nightfirepc.com'  # This (currently) just points at openspy
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
