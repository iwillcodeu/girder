from click_plugins import with_plugins
from pkg_resources import iter_entry_points
import click


@with_plugins(iter_entry_points('girder.cli_plugins'))
@click.group()
def cli():
    pass


def main():
    cli()
