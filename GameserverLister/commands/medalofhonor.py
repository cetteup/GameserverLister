import logging
import sys

import click

from GameserverLister.commands.options import common
from GameserverLister.common.logger import logger
from GameserverLister.common.types import MedalOfHonorGame
from GameserverLister.listers import MedalOfHonorServerLister


@click.command
@click.option(
    '-g',
    '--game',
    type=click.Choice(MedalOfHonorGame),
    required=True,
    help='Game to list servers for'
)
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        game: MedalOfHonorGame,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info(f'Listing servers for {game} via mohaaservers.tk')

    lister = MedalOfHonorServerLister(
        game,
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
