import logging
import sys
from typing import Optional

import click

from GameserverLister.commands.options import common, http, queryport
from GameserverLister.common.logger import logger
from GameserverLister.common.types import BattlelogGame
from GameserverLister.listers import BattlelogServerLister


@click.command
@click.option(
    '-g',
    '--game',
    type=click.Choice(BattlelogGame),
    required=True,
    help='Game to list servers for'
)
@http.page_limit
@http.sleep
@http.max_attempts
@http.proxy
@queryport.find
@queryport.gamedig_bin
@queryport.gamedig_concurrency
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        game: BattlelogGame,
        page_limit: int,
        sleep: float,
        max_attempts: int,
        proxy: Optional[str],
        find_query_port: bool,
        gamedig_bin: str,
        gamedig_concurrency: int,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info(f'Listing servers for {game} via battlelog')

    lister = BattlelogServerLister(
        game,
        page_limit,
        expired_ttl,
        recover,
        add_links,
        list_dir,
        sleep,
        max_attempts,
        proxy
    )

    before = len(lister.servers)
    lister.update_server_list()

    if find_query_port:
        lister.find_query_ports(gamedig_bin, gamedig_concurrency, expired_ttl)

    removed, recovered = lister.remove_expired_servers()
    lister.write_to_file()

    logger.info(f'Server list updated ('
                f'total: {len(lister.servers)}, '
                f'added: {len(lister.servers) + removed - before}, '
                f'removed: {removed}, '
                f'recovered: {recovered})')
