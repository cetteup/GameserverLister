import click

expired_ttl = click.option(
    '-e',
    '--expired-ttl',
    type=float,
    default=12.0,
    help='How long to keep a server in list after it was last seen (in hours)'
)
recover = click.option(
    '--no-recover',
    'recover',
    default=True,
    is_flag=True,
    help='Remove servers that were not returned by the source after they expired, '
         'do not attempt to contact/access server directly to check if they are still online'
)
add_links = click.option(
    '--add-links',
    default=False,
    is_flag=True,
    help='Enrich server list entries with links to websites showing more details about the server'
)
list_dir = click.option(
    '-d',
    '--list-dir',
    type=str,
    default='lists',
    help='Path to directory in which servers lists will be stored'
)
debug = click.option(
    '--debug',
    default=False,
    is_flag=True,
    help='Log lots of debugging information',
)
