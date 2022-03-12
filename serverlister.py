import argparse
import logging
import sys

from src.constants import GAMESPY_CONFIGS, GAMESPY_PRINCIPALS, QUAKE3_CONFIGS
from src.parsers import commonParser, httpParser, queryPortParser
from src.serverlisters import BattlelogServerLister, BC2ServerLister, GameSpyServerLister, GametoolsServerLister, \
    Quake3ServerLister, MedalOfHonorServerLister

parser = argparse.ArgumentParser(description='Retrieve a list of game servers from a given source and '
                                             'write it to a json file')
subparsers = parser.add_subparsers(title='Server list source', dest='source', required=True)

battlelogParser = subparsers.add_parser('battlelog', parents=[commonParser, httpParser, queryPortParser])
battlelogParser.add_argument('-g', '--game',
                             help='Battlelog game to retrieve server list for (BF3/BF4/BFH/MOHWF)',
                             type=str, choices=['bf3', 'bf4', 'bfh', 'mohwf'], required=True)

bfbc2Parser = subparsers.add_parser('bfbc2', parents=[commonParser, queryPortParser])
bfbc2Parser.add_argument('-t', '--timeout',
                         help='Timeout to use for server list retrieval request',
                         type=int, default=10)
bfbc2Parser.set_defaults(use_wine=False)

gamespyParser = subparsers.add_parser('gamespy', parents=[commonParser])
gamespyParser.add_argument('-g', '--gslist',
                           help='Path to gslist binary',
                           type=str, required=True)
gamespyParser.add_argument('-b', '--game',
                           help='Game to query servers for',
                           type=str, choices=list(GAMESPY_CONFIGS.keys()), default=list(GAMESPY_CONFIGS.keys())[0])
gamespyParser.add_argument('-p', '--principal',
                           help='Principal server to query',
                           type=str, choices=list(GAMESPY_PRINCIPALS.keys()))
gamespyParser.add_argument('-f', '--filter',
                           help='Filter to apply to server list',
                           type=str, default='')
gamespyParser.add_argument('-t', '--timeout',
                           help='Timeout to use for gslist command',
                           type=int, default=10)
gamespyParser.add_argument('-s', '--super-query',
                           help='Query each server in the list for it\'s status',
                           dest='super_query', action='store_true')
gamespyParser.add_argument('-v', '--verify',
                           help='(Attempt to) verify game servers returned by principal are game servers '
                                'for the current game',
                           dest='verify', action='store_true')
gamespyParser.set_defaults(super_query=False, verify=False)

gametoolsParser = subparsers.add_parser('gametools', parents=[commonParser, httpParser])
gametoolsParser.add_argument('-g', '--game', help='Game to retrieve server list for (BF1/BFV)', type=str,
                             choices=['bf1', 'bfv'], required=True)
gametoolsParser.add_argument('--include-official',
                             help='Add DICE official servers to the server list '
                                  '(not recommended due to auto scaling official servers)',
                             dest='include_official', action='store_true')
parser.set_defaults(include_official=False)

quake3Parser = subparsers.add_parser('quake3', parents=[commonParser])
quake3Parser.add_argument('-b', '--game',
                          help='Game to query servers for',
                          type=str, choices=list(QUAKE3_CONFIGS.keys()), default=list(QUAKE3_CONFIGS.keys())[0])
quake3Parser.add_argument('-p', '--principal',
                          help='Principal server to query',
                          type=str, choices=[p for g in QUAKE3_CONFIGS for p in QUAKE3_CONFIGS[g]['servers'].keys()])

medalOfHonorParser = subparsers.add_parser('medalofhonor', parents=[commonParser])
medalOfHonorParser.add_argument('-b', '--game',
                                help='Game to query servers for',
                                type=str, choices=['mohaa', 'mohbt', 'mohpa', 'mohsh'], default='mohaa')

args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, stream=sys.stdout,
                    format='%(asctime)s %(levelname)-8s %(message)s')

# Determine which lister to use and init that lister
serverListSource = args.source
if args.source == 'battlelog':
    # Init Battelog server lister
    game = args.game
    lister = BattlelogServerLister(game, args.page_limit, args.expired_ttl, args.recover, args.list_dir, args.sleep,
                                   args.max_attempts, args.proxy)
elif args.source == 'bfbc2':
    # Init BC2 lister
    game = 'bfbc2'
    lister = BC2ServerLister(args.expired_ttl, args.recover, args.list_dir, args.timeout)
elif args.source == 'gamespy':
    # Set principal
    principal = None
    availablePrincipals = GAMESPY_CONFIGS[args.game]['servers']
    if len(availablePrincipals) > 1 and str(args.principal).lower() in GAMESPY_CONFIGS[args.game]['servers']:
        # More than one principal available and given principal is valid => use given principal
        principal = args.principal.lower()
    else:
        # Only one principal available or given principal is invalid => use default principal
        principal = availablePrincipals[0]

    # Add principal name to server list source
    serverListSource += f'/{principal}'

    # Init GameSpy server lister
    game = args.game
    lister = GameSpyServerLister(game, principal, args.gslist, args.filter, args.super_query, args.timeout, args.verify,
                                 args.expired_ttl, args.recover, args.list_dir)
elif args.source == 'gametools':
    # Init gametools server lister
    game = args.game
    lister = GametoolsServerLister(game, args.page_limit, args.expired_ttl, args.recover, args.list_dir, args.sleep,
                                   args.max_attempts, args.include_official)
elif args.source == 'quake3':
    # Set principal
    principal = None
    availablePrincipals = list(QUAKE3_CONFIGS[args.game.lower()]['servers'].keys())
    if len(availablePrincipals) > 1 and str(args.principal).lower() in availablePrincipals:
        # More than one principal available and given principal is valid => use given principal
        principal = args.principal.lower()
    else:
        # Only one principal available or given principal is invalid => use default principal
        principal = availablePrincipals[0]

    # Add principal name to server list source
    serverListSource += f'/{principal}'

    # Init GameSpy server lister
    game = args.game
    lister = Quake3ServerLister(game, principal, args.expired_ttl, args.recover, args.list_dir)
else:
    serverListSource = 'mohaaservers.tk'
    game = args.game
    lister = MedalOfHonorServerLister(game, args.expired_ttl, args.recover, args.list_dir)

logging.info(f'Listing servers for {game} via {serverListSource}')

# Init stats dict
stats = {
    'serverTotalBefore': len(lister.servers),
    'serverTotalAfter': -1,
    'expiredServersRemoved': -1,
    'expiredServersRecovered': -1
}
# Run list update
lister.update_server_list()
# Check for any remove any expired servers
stats['expiredServersRemoved'], stats['expiredServersRecovered'] = lister.remove_expired_servers()

# Search query ports if requested
if 'find_query_port' in args and args.find_query_port:
    lister.find_query_ports(args.gamedig_bin, args.gamedig_concurrency, args.expired_ttl)

# Write updated list to file
lister.write_to_file()
# Update and log stats
stats['serverTotalAfter'] = len(lister.servers)
logging.info(f'Run stats: {stats}')
