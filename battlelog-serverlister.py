import argparse
import logging

from src.serverlisters import BattlelogServerLister

parser = argparse.ArgumentParser(description='Retrieve a list of Battlelog (BF3/BF4/BFH/MOHWF) '
                                             'game servers and write it to a json file')
parser.add_argument('-g', '--game', help='Battlelog game to retrieve server list for (BF3/BF4/BFH/MOHWF)', type=str,
                    choices=['bf3', 'bf4', 'bfh', 'mohwf'], required=True)
parser.add_argument('-p', '--page-limit', help='Number of pages to get after retrieving the last unique server',
                    type=int, default=10)
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('--sleep', help='Number of seconds to sleep between requests', type=float, default=0)
parser.add_argument('--max-attempts', help='Max number of attempts for fetching a page of servers', type=int, default=3)
parser.add_argument('--proxy', help='Proxy to use for requests '
                                    '(format: [protocol]://[username]:[password]@[hostname]:[port]', type=str)
parser.add_argument('--find-query-port', dest='find_query_port', action='store_true')
parser.set_defaults(find_query_port=False)
parser.add_argument('--gamedig-bin', help='Path to gamedig binary', type=str, default='/usr/bin/gamedig')
parser.add_argument('--gamedig-concurrency', help='Number of gamedig queries to run in parallel', type=int, default=12)
parser.add_argument('--debug', help='Enables logging of lots of debugging information', dest='debug',
                    action='store_true')
parser.set_defaults(debug=False)
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s')

logging.info(f'Listing servers for {args.game.lower()}')

# Init Battelog server lister
lister = BattlelogServerLister(args.game, args.page_limit, args.expired_ttl, args.sleep, args.max_attempts, args.proxy)
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
if args.find_query_port:
    lister.find_query_ports(args.gamedig_bin, args.gamedig_concurrency, args.expired_ttl)

# Write updated list to file
lister.write_to_file()
# Update and log stats
stats['serverTotalAfter'] = len(lister.servers)
logging.info(f'Run stats: {stats}')
