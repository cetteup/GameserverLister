import argparse
import logging

from src.serverlisters import GametoolsServerLister

parser = argparse.ArgumentParser(description='Retrieve a list of (BF1/BFV) game servers from the Gametools API '
                                             'and write it to a json file')
parser.add_argument('-g', '--game', help='Game to retrieve server list for (BF1/BFV)', type=str,
                    choices=['bf1', 'bfv'], required=True)
parser.add_argument('-p', '--page-limit', help='Number of pages to get after retrieving the last unique server',
                    type=int, default=10)
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('-d', '--list-dir', help='Path to directory in which servers lists will be stored', type=str,
                    default='.')
parser.add_argument('--sleep', help='Number of seconds to sleep between requests', type=float, default=0)
parser.add_argument('--max-attempts', help='Max number of attempts for fetching a page of servers', type=int, default=3)
parser.add_argument('--include-official', help='Add DICE official servers to the server list '
                                               '(not recommended due to auto scaling official servers)',
                    dest='include_official', action='store_true')
parser.add_argument('--debug', help='Enables logging of lots of debugging information', dest='debug',
                    action='store_true')
parser.set_defaults(include_official=False, debug=False)
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s')

logging.info(f'Listing servers for {args.game.lower()}')

# Init gametools server lister
lister = GametoolsServerLister(args.game, args.page_limit, args.expired_ttl, args.list_dir, args.sleep,
                               args.max_attempts, args.include_official)
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
stats['expiredServersRemoved'], stats['expiredServersRecovered'], *_ = lister.remove_expired_servers()

# Write updated list to file
lister.write_to_file()
# Update and log stats
stats['serverTotalAfter'] = len(lister.servers)
logging.info(f'Run stats: {stats}')
