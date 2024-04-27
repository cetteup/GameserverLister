from typing import Dict

from GameserverLister.common.types import BattlelogGame

BATTLELOG_GAME_BASE_URIS: Dict[BattlelogGame, str] = {
    BattlelogGame.BF3: 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    BattlelogGame.BF4: 'https://battlelog.battlefield.com/bf4/servers/getServers',
    BattlelogGame.BFH: 'https://battlelog.battlefield.com/bfh/servers/getServers',
}
