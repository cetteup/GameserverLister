import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

import gevent
import gevent.subprocess
import requests
from gevent.pool import Pool

BASE_URIS = {
    'bf3': 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    'bf4': 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/'
}


def find_query_port(ip: str, game_port: int, current_query_port: int = -1) -> int:
    query_port = -1
    """
    Order of ports to try:
    1. default query port
    2. game port + default port offset (mirror gamedig behavior)
    3. game port (some servers use same port for game + query)
    4. game port + 100 (nitrado)
    6. game port + 5 (several hosters)
    6. 48888 (gamed)
    """
    ports_to_try = [47200, game_port + 22000, game_port, game_port + 100, game_port + 5, 48888]
    # Add current query port add index 0 if valid
    if query_port != -1:
        ports_to_try.insert(current_query_port, 0)
    for port_to_try in ports_to_try:
        gamedig_result = gevent.subprocess.run(
            args=['/usr/bin/gamedig', '--type', args.game.lower(), f'{ip}:{port_to_try}', '--maxAttempts 2', '--socketTimeout 2000'],
            capture_output=True
        )
        # Stop searching if query was successful and response came from the correct server
        # (some servers run on the same IP, so make sure ip and game_port match)
        if '"error":"Failed all' not in str(gamedig_result.stdout) and \
                f'"connect":"{ip}:{game_port}' in str(gamedig_result.stdout):
            query_port = port_to_try
            break

    return query_port


parser = argparse.ArgumentParser(description='Retrieve a list of Battlelog (BF3/BF4) '
                                             'game servers and write it to a json file')
parser.add_argument('-g', '--game', help='Battlelog game to retrieve server list for (BF3/BF4)', type=str, required=True)
parser.add_argument('-p', '--page-limit', help='Number of pages to get after retrieving the last unique server', type=int, default=10)
parser.add_argument('--sleep', help='Number of seconds to sleep between requests', type=float, default=0)
parser.add_argument('--proxy', help='Proxy to use for requests '
                                    '(format: [protocol]://[username]:[password]@[hostname]:[port]', type=str)
parser.add_argument('--find-query-port', dest='find_query_port', action='store_true')
parser.set_defaults(find_query_port=False)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Make sure either bf3 of bf4 was provided as the 'game' parameter
if args.game.lower() not in ['bf3', 'bf4']:
    sys.exit('Game not supported, please select either BF3 or BF4')

# Set paths
rootDir = os.path.dirname(os.path.realpath(__file__))
serverListFilePath = os.path.join(rootDir, f'{args.game.lower()}-servers.json')

# Init session
session = requests.session()
# Set up headers
session.headers = {
    'X-Requested-With': 'XMLHttpRequest'
}
# Set up proxy if given
if args.proxy is not None:
    # All requests are sent via https, so just set up https proxy
    session.proxies = {
        'https': args.proxy
    }

offset = 0
perPage = 60
"""
The BF4 server browser returns tons of duplicate servers (pagination is completely broken).
You basically just a [perPage] random servers every time. Thus, there is no way of telling when to stop.
As a workaround, just stop after not retrieving a new/unique server for [args.page_limit] pages
"""
pagesSinceLastUniqueServer = 0
attempt = 0
maxAttempts = 3

# Init server list with servers from existing list or empty one
if os.path.isfile(serverListFilePath):
    with open(serverListFilePath, 'r') as serverListFile:
        servers = json.load(serverListFile)
else:
    servers = []
stats = {
    'serverTotalBefore': len(servers)
}
"""
Since pagination of the server list is completely broken, just get the first "page" over and over again until
no servers have been found in [args.page_limit] "pages".
"""
logging.info('Starting server list retrieval')
while pagesSinceLastUniqueServer < args.page_limit and attempt < maxAttempts:
    # Sleep when requesting anything but offset 0
    if offset > 0:
        time.sleep(args.sleep)

    try:
        response = session.get(f'{BASE_URIS[args.game.lower()]}?count={perPage}&offset=0', timeout=10)
    except Exception as e:
        logging.error(f'Request failed, retrying {attempt + 1}/{maxAttempts}')
        # Count try and start over
        attempt += 1
        continue

    if response.status_code == 200:
        # Reset tries
        attempt = 0
        # Parse response
        parsed = response.json()
        serverTotalBefore = len(servers)
        # Add all servers in response (if they are new)
        for server in parsed["data"]:
            logging.debug(f'{server["ip"]}:{server["port"]} - {server["name"]} # {server["guid"]}')

            foundServer = {
                'guid': server['guid'],
                'ip': server['ip'],
                'gamePort': server['port'],
                'queryPort': -1,
                'lastSeenAt': datetime.now().isoformat()
            }
            # Add non-private servers (servers with an IP) that are new
            serverGuids = [s['guid'] for s in servers]
            if len(foundServer['ip']) > 0 and foundServer['guid'] not in serverGuids:
                logging.debug('Got new server, adding it')
                servers.append(foundServer)
            elif len(foundServer['ip']) > 0:
                logging.debug('Got known server, updating last seen at')
                servers[serverGuids.index(foundServer['guid'])]['lastSeenAt'] = datetime.now().isoformat()
            else:
                logging.debug('Got duplicate server')
        if len(servers) == serverTotalBefore:
            pagesSinceLastUniqueServer += 1
            logging.info(f'Got nothing but duplicates (page: {int(offset / perPage)},'
                         f' pages since last unique: {pagesSinceLastUniqueServer})')
        else:
            logging.info(f'Got {len(servers) - serverTotalBefore} new servers')
            # Found new unique server, reset
            pagesSinceLastUniqueServer = 0
        offset += perPage
    else:
        logging.error(f'Server responded with {response.status_code}, retrying {attempt + 1}/{maxAttempts}')
        attempt += 1

# Add current server total to stats
stats['serverTotalAfter'] = len(servers)

if args.find_query_port:
    logging.info(f'Searching query port for {len(servers)} servers')
    searchStats = {
        'totalSearches': len(servers),
        'queryPortFound': 0
    }
    pool = Pool(12)
    jobs = []
    for server in servers:
        jobs.append(pool.spawn(find_query_port, server['ip'], server['gamePort'], server['queryPort']))
    # Wait for all jobs to complete
    gevent.joinall(jobs)
    for index, job in enumerate(jobs):
        if job.value != -1:
            servers[index]['queryPort'] = job.value
            searchStats['queryPortFound'] += 1
    logging.info(f'Query port search stats: {searchStats}')

# Write file (unless retrieval failed due to reaching the attempt max)
if attempt < maxAttempts:
    logging.info(f'Writing {len(servers)} servers to output file')

    with open(serverListFilePath, 'w') as outputFile:
        json.dump(servers, outputFile)

logging.info(f'Run stats: {stats}')
