import json
import re
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Run gslist and capture output
commandOk = False
tries = 0
maxTries = 3
result = None
while not commandOk and tries < maxTries:
    try:
        logging.info('Running gslist command')
        result = subprocess.run(['gslist', '-n', 'battlefield2', '-x', 'servers.bf2hub.com:28911',
                                 '-Y', 'battlefield2', 'hW6m9a', '-o', '1'],
                                capture_output=True, timeout=10)
        commandOk = True
    except subprocess.TimeoutExpired as e:
        logging.error(f'gslist timed out, try {tries + 1}/{maxTries}')
        tries += 1

# Make sure any server were found
# (gslist sends all output to stderr so check there)
if result is None or 'servers found' not in str(result.stderr):
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
