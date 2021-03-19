import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from random import randint

import gevent.subprocess
from gevent.pool import Pool

from helpers import find_query_port, parse_raw_server_info, bfbc2_server_validator

parser = argparse.ArgumentParser(description='Retrieve a list of BF2Hub game servers and write it to a JSON file')
parser.add_argument('-b', '--ealist', help='Path to ealist binary', type=str, required=True)
parser.add_argument('-u', '--username', help='Username of EA user to use for ealist', type=str, required=True)
parser.add_argument('-p', '--password', help='Password of EA user to use for ealist', type=str, required=True)
parser.add_argument('-e', '--expired-ttl', help='How long to keep a server in list after it was last seen (in hours)',
                    type=int, default=24)
parser.add_argument('--find-query-port', dest='find_query_port', action='store_true')
parser.add_argument('--gamedig-bin', help='Path to gamedig binary', type=str, default='/usr/bin/gamedig')
parser.add_argument('--gamedig-concurrency', help='Number of gamedig queries to run in parallel', type=int, default=12)
parser.add_argument('--use-wine', help='Run the ealist executable through wine', dest='use_wine', action='store_true')
parser.set_defaults(find_query_port=False, use_wine=False)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Make sure ealist path is valid
if not os.path.isfile(args.ealist):
    sys.exit('Could not find ealist executable, please double check the provided path')

# Set paths
rootDir = os.path.dirname(os.path.realpath(__file__))
serverListFilePath = os.path.join(rootDir, 'bfbc2-servers.json')

# Run ealist and capture output
commandOk = False
tries = 0
maxTries = 3
ealistResult = None
while not commandOk and tries < maxTries:
    try:
        logging.info(f'Running ealist command')
        ealistResult = subprocess.run(['/usr/bin/wine' if args.use_wine else args.ealist,
                                       args.ealist if args.use_wine else '', '-n', 'bfbc2-pc-server', '-a',
                                       args.username, args.password, 'mohair-pc','-X', 'none', '-o', '1'],
                                      capture_output=True, timeout=10)
        commandOk = True
    except subprocess.TimeoutExpired as e:
        logging.error(f'ealist timed out, try {tries + 1}/{maxTries}')
        tries += 1

# Make sure any server were found
# (ealist sends all output to stderr so check there)
if ealistResult is None or 'servers found' not in str(ealistResult.stderr):
    sys.exit('ealist could not retrieve any servers')

# Read ealist output file
logging.info('Reading ealist output file')
with open('bfbc2-pc-server.gsl', 'r') as ealistFile:
    rawServerList = ealistFile.read()

# Init server list with servers from existing list or empty one
if os.path.isfile(serverListFilePath):
    with open(serverListFilePath, 'r') as serverListFile:
        logging.info('Reading servers from existing server list')
        servers = json.load(serverListFile)
else:
    servers = []

stats = {
    'serverTotalBefore': len(servers)
}

# Parse server list
# List format: [ip-address]:[port]
logging.info('Parsing server list')
for line in rawServerList.splitlines():
    rawServerInfo = line.strip().split(' ', 1)[1]
    parsed = parse_raw_server_info(rawServerInfo)
    foundServer = {
        'guid': abs(int(parsed['B-U-sguid'])),
        'name': parsed['hostname'],
        'ip': parsed['hostaddr'],
        'gamePort': int(parsed['hostport']),
        'lastSeenAt': datetime.now().astimezone().isoformat()
    }
    serverGuids = [s['guid'] for s in servers]
    if foundServer['guid'] not in serverGuids:
        logging.debug(f'Got new server {foundServer["guid"]}, adding it')
        servers.append({
            'guid': foundServer['guid'],
            'name': foundServer['name'],
            'ip': foundServer['ip'],
            'gamePort': foundServer['gamePort'],
            'queryPort': -1,
            'lastSeenAt': foundServer['lastSeenAt']
        })
    else:
        logging.debug(f'Got known server {foundServer["guid"]}, updating it')
        index = serverGuids.index(foundServer['guid'])
        servers[index] = {**servers[index], **foundServer}

# Iterate over copy of server list and remove any expired servers from the (actual) server list
logging.info(f'Checking server expiration ttl for {len(servers)} servers')
stats['expiredServersRemoved'] = 0
for index, server in enumerate(servers[:]):
    lastSeenAt = (datetime.fromisoformat(server['lastSeenAt'])
                  if 'lastSeenAt' in server.keys() else datetime.min).astimezone()
    timePassed = datetime.now().astimezone() - lastSeenAt
    if timePassed.total_seconds() >= args.expired_ttl * 60 * 60:
        logging.debug(f'Server {server["guid"]} has not been seen in {args.expired_ttl} hours, removing it')
        servers.remove(server)
        stats['expiredServersRemoved'] += 1

# Add current server total to stats
stats['serverTotalAfter'] = len(servers)

if args.find_query_port:
    logging.info(f'Searching query port for {len(servers)} servers')

    searchStats = {
        'totalSearches': len(servers),
        'queryPortFound': 0
    }
    pool = Pool(args.gamedig_concurrency)
    jobs = []
    for server in servers:
        """
        Most Bad Company 2 server seem to be hosted directly by members of the community, resulting in pretty random
        query ports as well as strange/incorrect server configurations. So, try a bunch of ports and validate found
        query ports using the connect property OR the server name
        Order of ports to try:
        1. default query port
        2. game port + default port offset (mirror gamedig behavior)
        3. game port (some servers use same port for game + query)
        4. game port + 100 (nitrado)
        5. game port + 10
        6. game port + 5 (several hosters)
        7. game port + 1
        8. game port + 29233 (i3D.net)
        9. game port + 29000
        10. random port between default game port and default query port
        11. random port between game port and game port + default offset
        """
        portsToTry = [48888, server['gamePort'] + 29321, server['gamePort'], server['gamePort'] + 100,
                      server['gamePort'] + 10, server['gamePort'] + 5, server['gamePort'] + 1,
                      server['gamePort'] + 29233, server['gamePort'] + 29000,
                      randint(19567, 48888), randint(server['gamePort'], server['gamePort'] + 29321)]
        jobs.append(pool.spawn(find_query_port, args.gamedig_bin, 'bfbc2', server, portsToTry, bfbc2_server_validator))
    # Wait for all jobs to complete
    gevent.joinall(jobs)
    for index, job in enumerate(jobs):
        if job.value != -1:
            servers[index]['queryPort'] = job.value
            searchStats['queryPortFound'] += 1
    logging.info(f'Query port search stats: {searchStats}')

logging.info(f'Writing {len(servers)} servers to output file')
with open(serverListFilePath, 'w') as outputFile:
    json.dump(servers, outputFile)

logging.info(f'Run stats: {stats}')
