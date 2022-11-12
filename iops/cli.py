from pathlib import Path
from typing import Dict, List, Pattern

import click

from iops import __version__
from iops.utils import (
    ensure_dotsops,
    find_all_files_by_regex,
    find_by_key,
    get_all_values,
    load_yaml,
    verify_encryption_regex,
)

DEFAULT_PATH_REGEX = r"\.ya?ml"
DEFAULT_ENCRYPTED_REGEX = r""


def _extract_bad_keys(secret: Dict, encrypted_regex: Pattern[str]) -> List[str]:
    bad_keys: List[str] = []
    for match in find_by_key(secret, encrypted_regex):
        for key, value in get_all_values(match):
            if not verify_encryption_regex(str(value)):
                bad_keys.append(key)
    return bad_keys


@click.version_option(__version__, "--version", message=__version__)
@click.help_option("-h", "--help")
@click.argument("path", nargs=1, type=click.Path())
@click.command(no_args_is_help=True)
@click.pass_context
def cli(ctx: click.Context, path: Path) -> None:
    """Top level command."""
    ctx.ensure_object(dict)

    received_path = Path(path)

    click.echo("START")  # verbose

    dotsops_path, dotsops_content = ensure_dotsops(received_path)

    if dotsops_content is None:
        click.echo("No .sops.yaml")  # always
        ctx.exit(1)
    else:
        creation_rules = dotsops_content["creation_rules"]
        click.echo(f"Found config file in {dotsops_path}")  # verbose

    for rule in creation_rules:
        if "path_regex" not in rule.keys():
            rule["path_regex"] = DEFAULT_PATH_REGEX
        if "encrypted_regex" not in rule.keys():
            rule["encrypted_regex"] = DEFAULT_ENCRYPTED_REGEX

        click.echo(
            f"ENCRYPTION_REGEX: {rule['encrypted_regex']} PATH_REGEX: {rule['path_regex']}"
        )  # verbose

        path_regex = rule["path_regex"]

        for file in find_all_files_by_regex(path_regex, received_path):
            click.echo(file)  # verbose

            encrypted_regex = rule["encrypted_regex"]
            secret = load_yaml(file)
            if secret is None:
                click.echo("Invalid YAML!")  # Always
                ctx.exit(1)
            else:
                bad_keys = _extract_bad_keys(secret, encrypted_regex)

            if not bad_keys:
                click.echo("OK!")  # verbose
            else:
                for bad_key in bad_keys:
                    click.echo(f"{bad_key} should be encrypted!")  # Always

    if not bad_keys:
        ctx.exit(0)
    else:
        ctx.exit(1)
