import click

from GameserverLister.commands import gamespy, battlelog, unreal2, valve, quake3, gametools, bfbc2, medalofhonor


@click.group()
def cli():
    pass


cli.add_command(battlelog.run, 'battlelog')
cli.add_command(bfbc2.run, 'bfbc2')
cli.add_command(gamespy.run, 'gamespy')
cli.add_command(gametools.run, 'gametools')
cli.add_command(medalofhonor.run, 'medalofhonor')
cli.add_command(quake3.run, 'quake3')
cli.add_command(unreal2.run, 'unreal2')
cli.add_command(valve.run, 'valve')

if __name__ == '__main__':
    cli()
