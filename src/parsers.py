# Parser with arguments common to all serverlisters
import argparse

commonParser = argparse.ArgumentParser(add_help=False)
commonParser.add_argument('-e', '--expired-ttl',
                          help='How long to keep a server in list after it was last seen (in hours)',
                          type=float, default=12.0)
commonParser.add_argument('-d', '--list-dir',
                          help='Path to directory in which servers lists will be stored',
                          type=str, default='.')
commonParser.add_argument('--no-recover',
                          help='Remove servers that were not returned by the source after they expired, '
                               'do not attempt to contact/access server directly to check if they are still online',
                          dest='recover', action='store_false')
commonParser.add_argument('--add-links',
                          help='Enrich server list entries with links to websites '
                               'showing more details about the server',
                          dest='add_links', action='store_true')
commonParser.add_argument('--debug',
                          help='Enables logging of lots of debugging information',
                          dest='debug', action='store_true')
commonParser.set_defaults(recover=True, add_links=False, debug=False)

# Parser with arguments common to HTTP serverlisters
httpParser = argparse.ArgumentParser(add_help=False)
httpParser.add_argument('-p', '--page-limit',
                        help='Number of pages to get after retrieving the last unique server',
                        type=int, default=10)
httpParser.add_argument('--sleep',
                        help='Number of seconds to sleep between requests',
                        type=float, default=0)
httpParser.add_argument('--max-attempts',
                        help='Max number of attempts for fetching a page of servers',
                        type=int, default=3)
httpParser.add_argument('--proxy',
                        help='Proxy to use for requests (format: [protocol]://[username]:[password]@[hostname]:[port]',
                        type=str)

# Parser with arguments common to serverlisters that do not receive query port information
queryPortParser = argparse.ArgumentParser(add_help=False)
queryPortParser.add_argument('--find-query-port', dest='find_query_port', action='store_true')
queryPortParser.add_argument('--gamedig-bin', help='Path to gamedig binary', type=str, default='/usr/bin/gamedig')
queryPortParser.add_argument('--gamedig-concurrency', help='Number of gamedig queries to run in parallel', type=int,
                             default=12)
queryPortParser.set_defaults(find_query_port=False)
