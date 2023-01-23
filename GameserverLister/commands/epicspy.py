import logging
import sys

import click

from GameserverLister.commands.options import common
from GameserverLister.common.logger import logger
from GameserverLister.common.types import GamespyGame
from GameserverLister.listers import EpicSpyServerLister


@click.command
@click.option(
    '-g',
    '--game',
    type=click.Choice([GamespyGame.UNREAL, GamespyGame.UT]),
    required=True,
    help='Game to list servers for'
)
@click.option(
    '-t',
    '--timeout',
    type=int,
    default=5,
    help='Timeout to use for principal query'
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
    '-t',
    '--timeout',
    'gslist_timeout',
    type=int,
    default=10,
    help='Timeout to use for gslist command'
)
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        game: GamespyGame,
        timeout: int,
        gslist_path: str,
        gslist_timeout: int,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info(f'Listing servers for {game} via epicspy/epicgames.com')

    lister = EpicSpyServerLister(
        game,
        timeout,
        gslist_path,
        gslist_timeout,
        recover,
        add_links,
        list_dir,
        expired_ttl
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
