import argparse
import logging
import os
import sys

from src.constants import GSLIST_CONFIGS
from src.serverlisters import GameSpyServerLister

parser = argparse.ArgumentParser(description='Retrieve a list of game servers for GameSpy-based Battlefield games '
                                             'and write it to a JSON file')
parser.add_argument('-g', '--gslist', help='Path to gslist binary', type=str, required=True)
parser.add_argument('-b', '--game', help='Battlefield game to query servers for', type=str,
                    choices=['bf1942', 'bfvietnam', 'bf2', 'bf2142'], default='bf2')
parser.add_argument('-p', '--project', help='Project who\'s master server should be queried (BF1942 and BF2 only)',
                    type=str, choices=['bf1942.sk', 'qtracker', 'bf2hub', 'playbf2'])
parser.add_argument('-f', '--filter', help='Filter to apply to server list', type=str, default='')
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('-s', '--super-query', help='Query each server in the list for it\'s status', dest='super_query',
                    action='store_true')
parser.set_defaults(super_query=False)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Make sure gslist path is valid
if not os.path.isfile(args.gslist):
    sys.exit('Could not find gslist executable, please double check the provided path')

# Set project
project = None
availableProjects = list(GSLIST_CONFIGS[args.game.lower()]['servers'].keys())
if len(availableProjects) > 1 and args.project.lower() in availableProjects:
    # More than one project available and given project is valid => use given project
    project = args.project.lower()
else:
    # Only one project available or given project is invalid => use default project
    project = availableProjects[0]

# Init GameSpy server lister
lister = GameSpyServerLister(args.game, project, args.gslist, args.filter, args.super_query, args.expired_ttl)
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
