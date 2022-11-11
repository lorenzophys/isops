import click

from iops import __version__


@click.version_option(__version__, "-v", "--version", message=__version__)
@click.help_option("-h", "--help")
@click.argument("dir", nargs=-1, type=click.Path())
@click.command(no_args_is_help=True)
def cli(dir):
    """Top level command."""
    pass
