import logging
import sys

import click

from GameserverLister.commands.options import common, gameport
from GameserverLister.commands.options.types import EnumChoice
from GameserverLister.common.logger import logger
from GameserverLister.common.types import ValveGame, ValvePrincipal
from GameserverLister.games.valve import VALVE_GAME_CONFIGS
from GameserverLister.listers import ValveServerLister
from GameserverLister.providers.valve import ValveGameServersServiceProvider


@click.command
@click.option(
    '-g',
    '--game',
    type=EnumChoice(ValveGame),
    required=True,
    help='Game to list servers for'
)
@click.option(
    '-p',
    '--principal',
    type=EnumChoice(ValvePrincipal),
    default=ValvePrincipal.VALVE,
    help='Principal server to query'
)
@click.option(
    '-f',
    '--filter',
    'filters',
    type=str,
    default='',
    help='Filter to apply to server list'
)
@click.option(
    '-t',
    '--timeout',
    type=int,
    default=5,
    help='Timeout to use for principal query'
)
@click.option(
    '-m',
    '--max-pages',
    type=int,
    default=10,
    help='Maximum number of pages to retrieve from the server list (per region)'
)
@click.option(
    '--web-api-key',
    type=str,
    required=True,
    envvar='STEAM_WEB_API_KEY',
    show_envvar=True,
    help='Steam Web API key to use for authentication'
)
@gameport.add
@common.expire
@common.expired_ttl
@common.list_dir
@common.recover
@common.add_links
@common.txt
@common.debug
def run(
        game: ValveGame,
        principal: str,
        filters: str,
        timeout: int,
        max_pages: int,
        web_api_key: str,
        add_game_port: bool,
        expire: bool,
        expired_ttl: int,
        recover: bool,
        add_links: bool,
        txt: bool,
        list_dir: str,
        debug: bool
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s')

    # Set principal
    available_principals = VALVE_GAME_CONFIGS[game].principals
    if principal not in VALVE_GAME_CONFIGS[game].principals:
        # Given principal is invalid => use default principal
        logging.warning(f'Principal {principal} is not available for {game}, '
                        f'defaulting to {available_principals[0]} instead')
        principal = available_principals[0]

    logger.info(f'Listing servers for {game} via valve/{principal}')

    provider = ValveGameServersServiceProvider(web_api_key)
    lister = ValveServerLister(
        game,
        principal,
        provider,
        timeout,
        filters,
        max_pages,
        add_game_port,
        expire,
        expired_ttl,
        recover,
        add_links,
        txt,
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
