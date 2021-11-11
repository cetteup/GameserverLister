import argparse
import logging
import os
import sys

from src.constants import GSLIST_CONFIGS, GAMESPY_PRINCIPALS
from src.serverlisters import GameSpyServerLister

parser = argparse.ArgumentParser(description='Retrieve a list of game servers for GameSpy-based games '
                                             'and write it to a JSON file')
parser.add_argument('-g', '--gslist', help='Path to gslist binary', type=str, required=True)
parser.add_argument('-b', '--game', help='Game to query servers for', type=str,
                    choices=list(GSLIST_CONFIGS.keys()), default=list(GSLIST_CONFIGS.keys())[0])
parser.add_argument('-p', '--principal', help='Principal server to query',
                    type=str, choices=list(GAMESPY_PRINCIPALS.keys()))
parser.add_argument('-f', '--filter', help='Filter to apply to server list', type=str, default=None)
parser.add_argument('-t', '--timeout', help='Timeout to use for gslist command', type=int, default=10)
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('-d', '--list-dir', help='Path to directory in which servers lists will be stored', type=str,
                    default='.')
parser.add_argument('-s', '--super-query', help='Query each server in the list for it\'s status', dest='super_query',
                    action='store_true')
parser.set_defaults(super_query=False)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')

# Make sure gslist path is valid
if not os.path.isfile(args.gslist):
    sys.exit('Could not find gslist executable, please double check the provided path')

# Set principal
principal = None
availablePrincipals = GSLIST_CONFIGS[args.game]['servers']
if len(availablePrincipals) > 1 and str(args.principal).lower() in GSLIST_CONFIGS[args.game]['servers']:
    # More than one principal available and given principal is valid => use given principal
    principal = args.principal.lower()
else:
    # Only one principal available or given principal is invalid => use default principal
    principal = availablePrincipals[0]

logging.info(f'Listing servers for {args.game.lower()} via {principal.lower()}')

# Init GameSpy server lister
lister = GameSpyServerLister(args.game, principal, args.gslist, args.filter, args.super_query,
                             args.timeout, args.expired_ttl, args.list_dir)
# Init stats dict
stats = {
    'serverTotalBefore': len(lister.servers),
    'serverTotalAfter': -1,
    'expiredServersRemoved': -1
}
# Run list update
lister.update_server_list()
# Check for any remove any expired servers
stats['expiredServersRemoved'], = lister.remove_expired_servers()

# Write updated list to file
lister.write_to_file()
# Update and log stats
stats['serverTotalAfter'] = len(lister.servers)
logging.info(f'Run stats: {stats}')
