import logging
import sys

import click

from GameserverLister.commands.options import common, http
from GameserverLister.common.logger import logger
from GameserverLister.common.types import GametoolsGame
from GameserverLister.listers import GametoolsServerLister


@click.command
@click.option(
    '-g',
    '--game',
    type=click.Choice(GametoolsGame),
    required=True,
    help='Game to list servers for'
)
@click.option(
    '--include-official',
    default=False,
    is_flag=True,
    help='Include DICE official servers in list (not recommended due to auto scaling official servers)'
)
@http.page_limit
@http.sleep
@http.max_attempts
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        game: GametoolsGame,
        page_limit: int,
        sleep: float,
        max_attempts: int,
        include_official: bool,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info(f'Listing servers for {game} via gametools')

    lister = GametoolsServerLister(
        game,
        page_limit,
        expired_ttl,
        recover,
        add_links,
        list_dir,
        sleep,
        max_attempts,
        include_official
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
