import click

add = click.option(
    '--add-name',
    default=False,
    is_flag=True,
    help='(Attempt to) add the (host-)name for each server'
)
