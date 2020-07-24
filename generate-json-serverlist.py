import json
import re
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Run gslist and capture output
try:
    logging.info('Running gslist command')
    result = subprocess.run(['gslist', '-n', 'battlefield2', '-x', 'servers.bf2hub.com:28911',
                             '-Y', 'battlefield2', 'hW6m9a', '-o', 'bf2hub-servers.txt'],
                            capture_output=True, timeout=10)
except subprocess.TimeoutExpired as e:
    sys.exit('gslist timed out')

# Make sure any server were found
# (gslist sends all output to stderr so check there)
if 'servers found' not in str(result.stderr):
    sys.exit('gslist could not retrieve any servers')

# Read gslist output file
logging.info('Reading gslist output file')
with open('bf2hub-servers.txt', 'r') as gslistFile:
    rawServerList = gslistFile.read()

# Parse server list
# List format: [space-padding][ip-address][spaces][port]
logging.info('Parsing server list')
servers = []
regex = re.compile(r'\s+')
for line in rawServerList.splitlines():
    elements = regex.split(line.strip())
    servers.append({
        'ip': elements[0],
        'query_port': elements[1]
    })

logging.info(f'Writing {len(servers)} servers to output file')
with open('bf2hub-servers.json', 'w') as outputFile:
    json.dump(servers, outputFile)
