import argparse
import logging
import os
import sys

from src.serverlisters import BC2ServerLister

parser = argparse.ArgumentParser(description='Retrieve a list of Bad Company 2 game servers and '
                                             'write it to a JSON file')
parser.add_argument('-b', '--ealist', help='Path to ealist binary', type=str, required=True)
parser.add_argument('-u', '--username', help='Username of EA user to use for ealist', type=str, required=True)
parser.add_argument('-p', '--password', help='Password of EA user to use for ealist', type=str, required=True)
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('-d', '--list-dir', help='Path to directory in which servers lists will be stored', type=str,
                    default='.')
parser.add_argument('--find-query-port', dest='find_query_port', action='store_true')
parser.add_argument('--gamedig-bin', help='Path to gamedig binary', type=str, default='/usr/bin/gamedig')
parser.add_argument('--gamedig-concurrency', help='Number of gamedig queries to run in parallel', type=int, default=12)
parser.add_argument('--use-wine', help='Run the ealist executable through wine', dest='use_wine', action='store_true')
parser.set_defaults(find_query_port=False, use_wine=False)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')

# Make sure ealist path is valid
if not os.path.isfile(args.ealist):
    sys.exit('Could not find ealist executable, please double check the provided path')

# Init BC2 lister
lister = BC2ServerLister(args.ealist, args.username, args.password, args.expired_ttl, args.list_dir, args.use_wine)
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

# Search query ports if requested
if args.find_query_port:
    lister.find_query_ports(args.gamedig_bin, args.gamedig_concurrency, args.expired_ttl)

# Write updated list to file
lister.write_to_file()
# Update and log stats
stats['serverTotalAfter'] = len(lister.servers)
logging.info(f'Run stats: {stats}')
