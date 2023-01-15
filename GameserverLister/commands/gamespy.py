import logging
import sys

import click

from GameserverLister.commands.options import common
from GameserverLister.common.logger import logger
from GameserverLister.common.types import GamespyGame, GamespyPrincipal
from GameserverLister.games.gamespy import GAMESPY_GAME_CONFIGS
from GameserverLister.listers import GameSpyServerLister


@click.command
@click.option(
    '-g',
    '--game',
    type=click.Choice(GamespyGame),
    required=True,
    help='Game to list servers for'
)
@click.option(
    '-p',
    '--principal',
    type=click.Choice(GamespyPrincipal),
    required=True,
    help='Principal server to query'
)
@click.option(
    '-b',
    '--gslist',
    'gslist_path',
    type=str,
    required=True,
    help='Path to gslist binary'
)
@click.option(
    '-f',
    '--filter',
    'gslist_filter',
    type=str,
    default='',
    help='Filter to apply to server list'
)
@click.option(
    '-s',
    '--super-query',
    'gslist_super_query',
    default=False,
    is_flag=True,
    help='Query each server in the list for it\'s status'
)
@click.option(
    '-t',
    '--timeout',
    'gslist_timeout',
    type=int,
    default=10,
    help='Timeout to use for gslist command'
)
@click.option(
    '-v',
    '--verify',
    default=False,
    is_flag=True,
    help='(Attempt to) verify game servers returned by principal are game servers for the current game'
)
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        game: GamespyGame,
        principal: GamespyPrincipal,
        gslist_path: str,
        gslist_filter: str,
        gslist_super_query: bool,
        gslist_timeout: int,
        verify: bool,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info(f'Listing servers for {game} via gamespy/{principal}')

    # Set principal
    available_principals = GAMESPY_GAME_CONFIGS[game].principals
    if principal not in GAMESPY_GAME_CONFIGS[game].principals:
        # Given principal is invalid => use default principal
        principal = available_principals[0]

    lister = GameSpyServerLister(
        game,
        principal,
        gslist_path,
        gslist_filter,
        gslist_super_query,
        gslist_timeout,
        verify,
        expired_ttl,
        recover,
        add_links,
        list_dir
    )

    before = len(lister.servers)
    lister.update_server_list()
    removed, recovered = lister.remove_expired_servers()
    lister.write_to_file()

    logger.info(f'Server list updated ('
                f'total: {len(lister.servers)}, '
                f'added: {len(lister.servers) + removed - before}, '
                f'removed: {removed}, '
                f'recovered: {recovered})')
