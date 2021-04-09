import argparse
import json
import logging
import os
import time
from datetime import datetime

import gevent.subprocess
import requests
from gevent.pool import Pool

from helpers import find_query_port, battlelog_server_validator

BASE_URIS = {
    'bf3': 'https://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/',
    'bf4': 'https://battlelog.battlefield.com/bf4/servers/getServers/pc/',
    'bfh': 'https://battlelog.battlefield.com/bfh/servers/getServers/pc/'
}


def list_index_of_dict_with_value(needle: object, haystack: list) -> int:
    """
    Find a dict with a given value in a list of dictionaries and return index of (first) dictionary that contains value
    :param needle:
    :param haystack:
    :return:
    """
    for list_index, list_item in enumerate(haystack):
        if needle in list_item.values():
            return list_index


parser = argparse.ArgumentParser(description='Retrieve a list of Battlelog (BF3/BF4) '
                                             'game servers and write it to a json file')
parser.add_argument('-g', '--game', help='Battlelog game to retrieve server list for (BF3/BF4)', type=str,
                    choices=['bf3', 'bf4', 'bfh'], required=True)
parser.add_argument('-p', '--page-limit', help='Number of pages to get after retrieving the last unique server',
                    type=int, default=10)
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('--sleep', help='Number of seconds to sleep between requests', type=float, default=0)
parser.add_argument('--proxy', help='Proxy to use for requests '
                                    '(format: [protocol]://[username]:[password]@[hostname]:[port]', type=str)
parser.add_argument('--find-query-port', dest='find_query_port', action='store_true')
parser.set_defaults(find_query_port=False)
parser.add_argument('--gamedig-bin', help='Path to gamedig binary', type=str, default='/usr/bin/gamedig')
parser.add_argument('--gamedig-concurrency', help='Number of gamedig queries to run in parallel', type=int, default=12)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Set paths
rootDir = os.path.dirname(os.path.realpath(__file__))
serverListFilePath = os.path.join(rootDir, f'{args.game.lower()}-servers.json')

logging.info(f'Listing server for {args.game.lower()}')

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
        logging.info('Reading servers from existing server list')
        knownServers = json.load(serverListFile)
else:
    knownServers = []
stats = {
    'serverTotalBefore': len(knownServers)
}
"""
Since pagination of the server list is completely broken, just get the first "page" over and over again until
no servers have been found in [args.page_limit] "pages".
"""
foundServers = []
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
        serverTotalBefore = len(foundServers)
        # Add all servers in response (if they are new)
        for server in parsed["data"]:
            foundServer = {
                'guid': server['guid'],
                'ip': server['ip'],
                'gamePort': server['port'],
                'lastSeenAt': datetime.now().astimezone().isoformat()
            }
            # Add non-private servers (servers with an IP) that are new
            serverGuids = [s['guid'] for s in foundServers]
            if len(foundServer['ip']) > 0 and foundServer['guid'] not in serverGuids:
                logging.debug(f'Got new server {server["guid"]}, adding it')
                foundServers.append(foundServer)
            elif len(foundServer['ip']) > 0:
                logging.debug(f'Got duplicate server {server["guid"]}, updating last seen at')
                foundServers[serverGuids.index(foundServer['guid'])]['lastSeenAt'] = datetime.now().astimezone().isoformat()
            else:
                logging.debug(f'Got private server {server["guid"]}, ignoring it')
        if len(foundServers) == serverTotalBefore:
            pagesSinceLastUniqueServer += 1
            logging.info(f'Got nothing but duplicates (page: {int(offset / perPage)},'
                         f' pages since last unique: {pagesSinceLastUniqueServer})')
        else:
            logging.info(f'Got {len(foundServers) - serverTotalBefore} new servers')
            # Found new unique server, reset
            pagesSinceLastUniqueServer = 0
        offset += perPage
    else:
        logging.error(f'Server responded with {response.status_code}, retrying {attempt + 1}/{maxAttempts}')
        attempt += 1

# Add/update found servers to/in known servers
logging.info('Updating known server list with found servers')
for foundServer in foundServers:
    knownServerIndex = list_index_of_dict_with_value(foundServer['guid'], knownServers)
    # Update existing server entry or add new one
    if knownServerIndex is not None:
        logging.debug(f'Found server {foundServer["guid"]} already known, updating')
        # guid is the same, found server does not contain queryPort so it is safe to update ip,
        # gamePort and lastSeenAt by merging knownServer and foundServer
        knownServers[knownServerIndex] = {**knownServers[knownServerIndex], **foundServer}
    else:
        logging.debug(f'Found server {foundServer["guid"]} is new, adding')
        # Add new server entry
        knownServers.append({
            'guid': foundServer['guid'],
            'ip': foundServer['ip'],
            'gamePort': foundServer['gamePort'],
            'queryPort': -1,
            'lastSeenAt': foundServer['lastSeenAt']
        })
# Iterate over copy of server list and remove any expired servers from the (actual) server list
logging.info(f'Checking server expiration ttl for {len(knownServers)} servers')
stats['expiredServersRemoved'] = 0
stats['expiredServersRecovered'] = 0
for index, server in enumerate(knownServers[:]):
    lastSeenAt = (datetime.fromisoformat(server['lastSeenAt']) if
                  'lastSeenAt' in server.keys() else datetime.min).astimezone()
    timePassed = datetime.now().astimezone() - lastSeenAt
    if timePassed.total_seconds() >= args.expired_ttl * 60 * 60:
        # Check if server can be accessed directly
        requestOk = True
        found = False
        try:
            response = session.get(f'https://battlelog.battlefield.com/{args.game.lower()}/'
                                   f'servers/show/pc/{server["guid"]}?json=1')
            found = False if response.status_code == 422 else True
        except Exception as e:
            logging.error(f'Failed to fetch server {server["guid"]} for expiration check')
            requestOk = False

        # Remove server if request was sent successfully but server was not found
        if requestOk and not found:
            logging.debug(f'Server {server["guid"]} has not been seen in {args.expired_ttl} hours, removing it')
            knownServers.remove(server)
            stats['expiredServersRemoved'] += 1
        elif requestOk and found:
            logging.debug(f'Server {server["guid"]} did not appear in list but is still online, updating last seen at')
            knownServers[knownServers.index(server)]['lastSeenAt'] = datetime.now().astimezone().isoformat()
            stats['expiredServersRecovered'] += 1

# Add current server total to stats
stats['serverTotalAfter'] = len(knownServers)

if args.find_query_port:
    logging.info(f'Searching query port for {len(knownServers)} servers')

    searchStats = {
        'totalSearches': len(knownServers),
        'queryPortFound': 0
    }
    pool = Pool(args.gamedig_concurrency)
    jobs = []
    for server in knownServers:
        """
        Order of ports to try:
        1. default query port
        2. game port + default port offset (mirror gamedig behavior)
        3. game port (some servers use same port for game + query)
        4. game port + 100 (nitrado)
        6. game port + 5 (several hosters)
        6. 48888 (gamed)
        """
        portsToTry = [47200, server['gamePort'] + 22000, server['gamePort'], server['gamePort'] + 100,
                      server['gamePort'] + 5, server['gamePort'] + 1, 48888]
        jobs.append(pool.spawn(find_query_port, args.gamedig_bin, args.game, server,
                               portsToTry, battlelog_server_validator))
    # Wait for all jobs to complete
    gevent.joinall(jobs)
    for index, job in enumerate(jobs):
        if job.value != -1:
            knownServers[index]['queryPort'] = job.value
            # Update last seen at timestamp if server was queried successfully
            knownServers[index]['lastSeenAt'] = datetime.now().astimezone().isoformat()
            searchStats['queryPortFound'] += 1
    logging.info(f'Query port search stats: {searchStats}')

# Write file (unless retrieval failed due to reaching the attempt max)
if attempt < maxAttempts:
    logging.info(f'Writing {len(knownServers)} servers to output file')

    with open(serverListFilePath, 'w') as outputFile:
        json.dump(knownServers, outputFile)

logging.info(f'Run stats: {stats}')
