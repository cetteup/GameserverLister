import argparse
import logging

from src.constants import QUAKE3_CONFIGS
from src.serverlisters import Quake3ServerLister

parser = argparse.ArgumentParser('Retrieve a list of game servers from a Quake 3 based principal server and write '
                                 'it to a JSON file')
parser.add_argument('-b', '--game', help='Game to query servers for', type=str,
                    choices=list(QUAKE3_CONFIGS.keys()), default=list(QUAKE3_CONFIGS.keys())[0])
parser.add_argument('-p', '--principal', help='Principal server to query', type=str,
                    choices=[p for g in QUAKE3_CONFIGS for p in QUAKE3_CONFIGS[g]['servers'].keys()])
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('-d', '--list-dir', help='Path to directory in which servers lists will be stored', type=str,
                    default='.')
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')

# Set principal
principal = None
availablePrincipals = list(QUAKE3_CONFIGS[args.game.lower()]['servers'].keys())
if len(availablePrincipals) > 1 and str(args.principal).lower() in availablePrincipals:
    # More than one principal available and given principal is valid => use given principal
    principal = args.principal.lower()
else:
    # Only one principal available or given principal is invalid => use default principal
    principal = availablePrincipals[0]

logging.info(f'Listing servers for {args.game.lower()} via {principal.lower()}')

# Init GameSpy server lister
lister = Quake3ServerLister(args.game, principal, args.expired_ttl, args.list_dir)
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
