import logging
import sys

import click

from GameserverLister.commands.options import common
from GameserverLister.common.logger import logger
from GameserverLister.common.types import Unreal2Game
from GameserverLister.games.unreal2 import UNREAL2_CONFIGS
from GameserverLister.listers import Unreal2ServerLister


@click.command
@click.option(
    '-g',
    '--game',
    type=click.Choice(Unreal2Game),
    required=True,
    help='Game to list servers for'
)
@click.option(
    '-p',
    '--principal',
    type=click.Choice([p for g in UNREAL2_CONFIGS for p in UNREAL2_CONFIGS[g]['servers'].keys()]),
    required=True,
    help='Principal server to query'
)
@click.option(
    '-c',
    '--cd-key',
    type=str,
    required=True,
    help='CD key for game'
)
@click.option(
    '-t',
    '--timeout',
    type=int,
    default=5,
    help='Timeout to use for principal query'
)
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        game: Unreal2Game,
        principal: str,
        cd_key: str,
        timeout: int,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info(f'Listing servers for {game} via unreal2/{principal}')

    # Set principal
    available_principals = list(UNREAL2_CONFIGS[game]['servers'].keys())
    if principal.lower() not in available_principals:
        # Given principal is invalid => use default principal
        principal = available_principals[0]

    lister = Unreal2ServerLister(
        game,
        principal,
        cd_key,
        timeout,
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
