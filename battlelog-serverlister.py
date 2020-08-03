import argparse
import json
import logging
import sys
import time

import requests

BASE_URIS = {
    'bf3': 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    'bf4': 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/'
}

parser = argparse.ArgumentParser(description='Retrieve a list of Battlelog (BF3/BF4) '
                                             'game servers and write it to a json file')
parser.add_argument('-g', '--game', help='Battlelog game to retrieve server list for (BF3/BF4)', type=str, required=True)
parser.add_argument('-p', '--page-limit', help='Number of pages to get after retrieving the last unique server', type=int, default=10)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Make sure either bf3 of bf4 was provided as the 'game' parameter
if args.game.lower() not in ['bf3', 'bf4']:
    sys.exit('Game not supported, please select either BF3 or BF4')

# Init session
session = requests.session()
# Set up headers
session.headers = {
    'X-Requested-With': 'XMLHttpRequest'
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

servers = []
"""
Since pagination of the server list is completely broken, just get the first "page" over and over again until
no servers have been found in [args.page_limit] "pages".
"""
logging.info('Starting server list retrieval')
while pagesSinceLastUniqueServer < args.page_limit and attempt < maxAttempts:
    try:
        response = session.get(f'{BASE_URIS[args.game.lower()]}?count={perPage}&offset=0')
        # Reset tries
        attempt = 0
    except Exception as e:
        logging.error(f'Request failed, retrying {attempt}/{maxAttempts}')
        # Count try and start over
        attempt += 1
        continue

    if response.status_code == 200:
        # Parse response
        parsed = response.json()
        serverTotalBefore = len(servers)
        # Add all servers in response (if they are new)
        for server in parsed["data"]:
            logging.debug(f'{server["ip"]}:{server["port"]} - {server["name"]} # {server["guid"]}')

            serverToAdd = {
                'guid': server['guid'],
                'ip': server['ip'],
                'port': server['port']
            }
            # Add non-private servers (servers with an IP) that are new
            if len(serverToAdd['ip']) > 0 and serverToAdd not in servers:
                servers.append(serverToAdd)
            else:
                logging.debug('Got duplicate server')
        if len(servers) == serverTotalBefore:
            pagesSinceLastUniqueServer += 1
            logging.info(f'Got nothing but duplicates (page: {int(offset/perPage)},'
                         f' pages since last unique: {pagesSinceLastUniqueServer})')
        else:
            logging.info(f'Got {len(servers) - serverTotalBefore} new servers')
            # Found new unique server, reset
            pagesSinceLastUniqueServer = 0
        offset += perPage
    else:
        logging.error(f'Server responded with {response.status_code}, retrying {attempt}/{maxAttempts}')
        attempt += 1

logging.info(f'Writing {len(servers)} servers to output file')
with open(f'{args.game.lower()}-servers.json', 'w') as outputFile:
    json.dump(servers, outputFile)
