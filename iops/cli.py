import re
from pathlib import Path
from typing import Dict, List, Pattern, Tuple

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


def _extract_keys(secret: Dict, encrypted_regex: Pattern[str]) -> Tuple[List[str], ...]:
    bad_keys: List[str] = []
    good_keys: List[str] = []
    for match in find_by_key(secret, encrypted_regex):
        for key, value in get_all_values(match):
            if not verify_encryption_regex(str(value)):
                bad_keys.append(key)
            else:
                good_keys.append(key)
    return good_keys, bad_keys


@click.version_option(__version__, "--version", message=__version__)
@click.help_option("-h", "--help")
@click.argument("path", nargs=1, type=click.Path())
@click.command(no_args_is_help=True)
@click.pass_context
def cli(ctx: click.Context, path: Path) -> None:
    """Top level command."""
    ctx.ensure_object(dict)

    received_path = Path(path)

    dotsops_path, dotsops_content = ensure_dotsops(received_path)

    if dotsops_content == {}:
        click.secho(
            message="No valid .sops.yaml (or too many) found in the root or .sops directory.",
            bold=True,
            fg="red",
        )
        ctx.exit(1)

    click.secho(message=f"Found config file in {dotsops_path}", bold=True)

    if "creation_rules" not in dotsops_content.keys():
        click.secho(
            message=f"Error in {dotsops_path}: 'creation_rules' section not found.",
            bold=True,
            fg="red",
        )
        ctx.exit(1)

    creation_rules = dotsops_content["creation_rules"]

    for rule in creation_rules:
        if "path_regex" not in rule.keys():
            rule["path_regex"] = DEFAULT_PATH_REGEX
        if "encrypted_regex" not in rule.keys():
            rule["encrypted_regex"] = DEFAULT_ENCRYPTED_REGEX

        path_regex = rule["path_regex"]
        encrypted_regex = rule["encrypted_regex"]

        for file in find_all_files_by_regex(path_regex, received_path):
            dotsops_pattern: Pattern[str] = re.compile(r".sops.ya?ml")
            if dotsops_pattern.search(str(file)):
                continue

            secret = load_yaml(file)

            good_keys: List[str]
            bad_keys: List[str]

            if secret == {}:
                click.secho(message=f"{file} is not a valid YAML!", bold=True, fg="red")
                ctx.exit(1)
            else:
                good_keys, bad_keys = _extract_keys(secret, encrypted_regex)
                all_keys: List[str] = good_keys + bad_keys
                all_keys.sort()

            for key in all_keys:
                if key in good_keys:
                    click.secho(message=f"{file}::{key} ", bold=False, nl=False)
                    click.secho(message="[SAFE]", bold=False, fg="green")
                else:
                    click.secho(message=f"{file}::{key} ", bold=False, nl=False)
                    click.secho(message="[UNSAFE]", bold=False, fg="red")

    if bad_keys:
        ctx.exit(1)

    ctx.exit(0)
