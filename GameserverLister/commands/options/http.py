import click

page_limit = click.option(
    '-p',
    '--page-limit',
    type=int,
    default=10,
    help='Number of pages to get after retrieving the last unique server'
)
sleep = click.option(
    '--sleep',
    type=float,
    default=0,
    help='Number of seconds to sleep between requests'
)
max_attempts = click.option(
    '--max-attempts',
    type=int,
    default=3,
    help='Max number of attempts for fetching a page of servers'
)
proxy = click.option(
    '--proxy',
    type=str,
    help='Proxy to use for requests (format: [protocol]://[username]:[password]@[hostname]:[port]'
)
