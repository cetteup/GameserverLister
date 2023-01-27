from typing import Dict

from GameserverLister.common.types import GamespyPrincipal, GamespyPrincipalConfig, GamespyGame, GamespyGameConfig

GAMESPY_PRINCIPAL_CONFIGS: Dict[GamespyPrincipal, GamespyPrincipalConfig] = {
    GamespyPrincipal.TripleThreeNetworks_com_1: GamespyPrincipalConfig(
        hostname='master.333networks.com'
    ),
    GamespyPrincipal.TripleThreeNetworks_com_2: GamespyPrincipalConfig(
        hostname='rhea.333networks.com'
    ),
    GamespyPrincipal.BF1942_org: GamespyPrincipalConfig(
        hostname='master.bf1942.org'
    ),
    GamespyPrincipal.BF2Hub_com: GamespyPrincipalConfig(
        hostname='servers.bf2hub.com',
        port_offset=1
    ),
    GamespyPrincipal.Crymp_net: GamespyPrincipalConfig(
        hostname='master.crymp.net'
    ),
    GamespyPrincipal.Errorist_eu: GamespyPrincipalConfig(
        hostname='master.errorist.eu'
    ),
    GamespyPrincipal.FH2_dev: GamespyPrincipalConfig(
        hostname='ms.fh2.dev'
    ),
    GamespyPrincipal.Jedi95_us: GamespyPrincipalConfig(
        hostname='master.g.jedi95.us'
    ),
    GamespyPrincipal.Newbiesplayground_net: GamespyPrincipalConfig(
        hostname='master.newbiesplayground.net'
    ),
    GamespyPrincipal.NightfirePC_com: GamespyPrincipalConfig(
        hostname='master.nightfirepc.com'  # This (currently) just points at openspy
    ),
    GamespyPrincipal.NovGames_ru: GamespyPrincipalConfig(
        hostname='2142.novgames.ru'
    ),
    GamespyPrincipal.OldUnreal_com_1: GamespyPrincipalConfig(
        hostname='master.oldunreal.com'
    ),
    GamespyPrincipal.OldUnreal_com_2: GamespyPrincipalConfig(
        hostname='master2.oldunreal.com'
    ),
    GamespyPrincipal.OpenSpy_net: GamespyPrincipalConfig(
        hostname='{0}.master.openspy.net'
    ),
    GamespyPrincipal.PhoenixNetwork_net: GamespyPrincipalConfig(
        hostname='master.phoenixnetwork.net'
    ),
    GamespyPrincipal.Play2142_ru: GamespyPrincipalConfig(
        hostname='{0}.ms.play2142.ru'
    ),
    GamespyPrincipal.PlayBF2_ru: GamespyPrincipalConfig(
        hostname='{0}.ms.playbf2.ru'
    ),
    GamespyPrincipal.Qtracker_com: GamespyPrincipalConfig(
        hostname='master2.qtracker.com'
    ),
    GamespyPrincipal.SWAT4Stats_com: GamespyPrincipalConfig(
        hostname='master.swat4stats.com'
    ),
    GamespyPrincipal.Vietcong_tk: GamespyPrincipalConfig(
        hostname='brvps.tk'
    ),
    GamespyPrincipal.Vietcong1_eu: GamespyPrincipalConfig(
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
            GamespyPrincipal.BF1942_org,
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.Qtracker_com
        ]
    ),
    GamespyGame.BFVietnam: GamespyGameConfig(
        game_name='bfvietnam',
        game_key='h2P9dJ',
        enc_type=2,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.Qtracker_com
        ]
    ),
    GamespyGame.BF2: GamespyGameConfig(
        game_name='battlefield2',
        game_key='hW6m9a',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.BF2Hub_com,
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.PhoenixNetwork_net,
            GamespyPrincipal.PlayBF2_ru
        ],
        link_template_refs={
            '_any': ['bf2.tv'],
            GamespyPrincipal.BF2Hub_com: ['bf2hub']
        }
    ),
    GamespyGame.FH2: GamespyGameConfig(
        game_name='battlefield2',
        game_key='hW6m9a',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.FH2_dev
        ],
        info_query='\\hostname'
    ),
    GamespyGame.BF2142: GamespyGameConfig(
        game_name='stella',
        game_key='M8o1Qw',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.NovGames_ru,
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.Play2142_ru
        ]
    ),
    GamespyGame.Crysis: GamespyGameConfig(
        game_name='crysis',
        game_key='ZvZDcL',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.Crymp_net
        ]
    ),
    GamespyGame.CrysisWars: GamespyGameConfig(
        game_name='crysiswars',
        game_key='zKbZiM',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.Jedi95_us
        ]
    ),
    GamespyGame.DeusEx: GamespyGameConfig(
        game_name='deusex',
        game_key='Av3M99',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.Newbiesplayground_net,
            GamespyPrincipal.OldUnreal_com_1
        ]
    ),
    GamespyGame.DukeNukemForever: GamespyGameConfig(
        game_name='dnf',
        game_key='      ',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1
        ]
    ),
    GamespyGame.JBNightfire: GamespyGameConfig(
        game_name='jbnightfire',
        game_key='S9j3L2',
        enc_type=-1,
        query_type=0,
        port=28910,
        principals=[
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.NightfirePC_com
        ]
    ),
    GamespyGame.Paraworld: GamespyGameConfig(
        game_name='paraworld',
        game_key='EUZpQF',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.OpenSpy_net
        ]
    ),
    GamespyGame.Postal2: GamespyGameConfig(
        game_name='postal2',
        game_key='yw3R9c',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1
        ]
    ),
    GamespyGame.Rune: GamespyGameConfig(
        game_name='rune',
        game_key='BnA4a3',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.Newbiesplayground_net,
            GamespyPrincipal.OldUnreal_com_1
        ]
    ),
    GamespyGame.SeriousSam: GamespyGameConfig(
        game_name='serioussam',
        game_key='AKbna4',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.Newbiesplayground_net,
            GamespyPrincipal.OldUnreal_com_1
        ]
    ),
    GamespyGame.SeriousSamSE: GamespyGameConfig(
        game_name='serioussamse',
        game_key='AKbna4',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.Newbiesplayground_net,
            GamespyPrincipal.OldUnreal_com_1
        ]
    ),
    GamespyGame.SWAT4: GamespyGameConfig(
        game_name='swat4',
        game_key='tG3j8c',
        enc_type=-1,
        query_type=0,
        port=28910,
        principals=[
            GamespyPrincipal.SWAT4Stats_com
        ],
        # The SWAT 4 principal is the only one which does not return servers if the list type byte is set to 1,
        # so we need to set it to 0 (only possible using a modified version glist: https://github.com/cetteup/gslist)
        list_type=0,
        info_query='\\hostname',
        link_template_refs={
            GamespyPrincipal.SWAT4Stats_com: ['swat4stats.com']
        }
    ),
    GamespyGame.Unreal: GamespyGameConfig(
        game_name='unreal',
        game_key='DAncRK',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.OldUnreal_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.Qtracker_com
        ]
    ),
    GamespyGame.UT: GamespyGameConfig(
        game_name='ut',
        game_key='Z5Nfb0',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.OldUnreal_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.OpenSpy_net,
            GamespyPrincipal.Qtracker_com
        ]
    ),
    GamespyGame.UT3: GamespyGameConfig(
        game_name='ut3pc',
        game_key='nT2Mtz',
        enc_type=-1,
        query_type=11,
        port=28910,
        principals=[
            GamespyPrincipal.OpenSpy_net
        ]
    ),
    GamespyGame.Vietcong: GamespyGameConfig(
        game_name='vietcong',
        game_key='bq98mE',
        enc_type=2,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.Vietcong_tk,
            GamespyPrincipal.Vietcong1_eu,
            GamespyPrincipal.Qtracker_com
        ]
    ),
    GamespyGame.Vietcong2: GamespyGameConfig(
        game_name='vietcong2',
        game_key='zX2pq6',
        enc_type=-1,
        query_type=8,
        port=28910,
        principals=[
            GamespyPrincipal.OpenSpy_net
        ]
    ),
    GamespyGame.WheelOfTime: GamespyGameConfig(
        game_name='wot',
        game_key='RSSSpA',
        enc_type=0,
        query_type=0,
        port=28900,
        principals=[
            GamespyPrincipal.TripleThreeNetworks_com_1,
            GamespyPrincipal.Errorist_eu,
            GamespyPrincipal.Newbiesplayground_net,
            GamespyPrincipal.OldUnreal_com_1
        ]
    ),
}
