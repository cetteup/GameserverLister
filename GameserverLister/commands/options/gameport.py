import click

add = click.option(
    '--add-game-port',
    default=False,
    is_flag=True,
    help='(Attempt to) add the game port for each server'
)
