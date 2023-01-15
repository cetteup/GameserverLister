import logging
import sys

import click

from GameserverLister.commands.options import common, queryport
from GameserverLister.common.logger import logger
from GameserverLister.listers import BadCompany2ServerLister


@click.command
@click.option(
    '-t',
    '--timeout',
    type=int,
    default=10,
    help='Timeout to use for server list retrieval request'
)
@queryport.find
@queryport.gamedig_bin
@queryport.gamedig_concurrency
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.debug
def run(
        timeout: int,
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
    logger.info('Listing servers for bfbc2')

    lister = BadCompany2ServerLister(
        expired_ttl,
        recover,
        add_links,
        list_dir,
        timeout
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
