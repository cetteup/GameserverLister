import argparse
import json
import logging
import os
import subprocess
import sys

from nslookup import Nslookup

parser = argparse.ArgumentParser(description='Retrieve a list of BF2Hub gameservers and write it to a JSON file')
parser.add_argument('-g', '--gslist', help='Path to gslist binary', type=str, required=True)
parser.add_argument('-f', '--filter', help='Filter to apply to server list', type=str, default='')
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Make sure gslist path is valid
if not os.path.isfile(args.gslist):
    sys.exit("Could not find gslist executable, please double check the provided path")

# Manually look up servers.bf2hub.com to be able to spread retried across servers
lookerUpper = Nslookup()
dnsResult = lookerUpper.dns_lookup('servers.bf2hub.com')

# Run gslist and capture output
commandOk = False
tries = 0
maxTries = 3
gslistResult = None
while not commandOk and tries < maxTries:
    # Alternate between first and last found A record
    serverIp = dnsResult.answer[0] if tries % 2 == 0 else dnsResult.answer[-1]
    try:
        logging.info(f'Running gslist command against {serverIp}')
        gslistResult = subprocess.run([args.gslist, '-n', 'battlefield2', '-x', f'{serverIp}:28911',
                                       '-Y', 'battlefield2', 'hW6m9a', '-f', f'{args.filter}', '-o', '1'],
                                      capture_output=True, timeout=10)
        commandOk = True
    except subprocess.TimeoutExpired as e:
        logging.error(f'gslist timed out, try {tries + 1}/{maxTries}')
        tries += 1

# Make sure any server were found
# (gslist sends all output to stderr so check there)
if gslistResult is None or 'servers found' not in str(gslistResult.stderr):
    sys.exit('gslist could not retrieve any servers')

# Read gslist output file
logging.info('Reading gslist output file')
with open('battlefield2.gsl', 'r') as gslistFile:
    rawServerList = gslistFile.read()

# Parse server list
# List format: [ip-address]:[port]
logging.info('Parsing server list')
servers = []
for line in rawServerList.splitlines():
    elements = line.strip().split(':')
    servers.append({
        'ip': elements[0],
        'query_port': elements[1]
    })

logging.info(f'Writing {len(servers)} servers to output file')
with open('bf2hub-servers.json', 'w') as outputFile:
    json.dump(servers, outputFile)
