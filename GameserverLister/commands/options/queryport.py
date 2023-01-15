import click

find = click.option(
    '--find-query-port',
    default=False,
    is_flag=True,
    help='(Attempt to) find the query port for each server'
)
gamedig_bin = click.option(
    '--gamedig-bin',
    type=str,
    default='/usr/bin/gamedig',
    help='Path to gamedig binary'
)
gamedig_concurrency = click.option(
    '--gamedig-concurrency',
    type=int,
    default=12,
    help='Number of gamedig queries to run in parallel'
)
