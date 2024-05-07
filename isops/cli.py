import re
from pathlib import Path
from typing import Dict, List, Pattern, Tuple

import click

from isops import __version__
from isops.utils import (
    all_dict_values,
    find_all_files_by_regex,
    find_by_key,
    load_all_yaml,
    verify_encryption_regex,
)

DEFAULT_PATH_REGEX = r".ya?ml$"
DEFAULT_ENCRYPTED_REGEX = r""


def _categorize_keys_based_on_their_values(
    secret: Dict, encrypted_regex: Pattern[str]
) -> Tuple[List[str], ...]:
    bad_keys: List[str] = []
    good_keys: List[str] = []
    for match in find_by_key(secret, encrypted_regex):
        for key, value in all_dict_values(match):
            if not verify_encryption_regex(str(value)):
                bad_keys.append(key)
            else:
                good_keys.append(key)
    return good_keys, bad_keys


def _validate_regex(ctx: click.Context, param: click.Parameter, value: str) -> str:
    try:
        re.compile(value)
        return value
    except re.error:
        raise click.BadParameter(param=param, message=f"{value} is not a valid regex.") from None


@click.option(
    "-r",
    "--config-regex",
    type=str,
    callback=_validate_regex,
    required=True,
    help="The regex that matches all the config files to use.",
)
@click.version_option(__version__, "-v", "--version", message=__version__)
@click.help_option("-h", "--help")
@click.option(
    "-s",
    "--summary",
    type=bool,
    required=False,
    is_flag=True,
    default=False,
    help="Print a summary at the end of the checks.",
)
@click.argument("path", nargs=1, type=click.Path())
@click.command(no_args_is_help=True)
@click.pass_context
def cli(ctx: click.Context, path: Path, config_regex: Pattern[str], summary: bool) -> None:
    """Ensure your SOPS secrets are encrypterd."""
    ctx.ensure_object(dict)

    received_path = Path(path)

    creation_rules = []
    for match_path in find_all_files_by_regex(config_regex, received_path):
        for config in load_all_yaml(Path(match_path)):
            try:
                creation_rules += config["creation_rules"]
                click.secho(message=f"Found config file: {match_path}", bold=True, fg="blue")
            except KeyError:
                click.secho(message=f"WARNING: skipping '{match_path}'", fg="yellow")
                continue

    if not creation_rules:
        click.secho(
            message="No valid config file found.",
            bold=True,
            fg="red",
        )
        ctx.exit(1)

    click.secho(message="---", bold=True, nl=True)

    good_keys: List[str] = []
    bad_keys: List[str] = []

    bad_keys_summary: List[str] = []
    bad_keys_number: int = 0
    good_keys_number: int = 0

    broken_yaml_found: str = ""

    for rule in creation_rules:
        if "path_regex" not in rule:
            rule["path_regex"] = DEFAULT_PATH_REGEX
        if "encrypted_regex" not in rule:
            rule["encrypted_regex"] = DEFAULT_ENCRYPTED_REGEX

        try:
            path_regex = rule["path_regex"]
            re.compile(path_regex)
        except re.error:
            click.secho(
                message=f"Invalid regex for 'path_regex': {path_regex}",
                bold=False,
                fg="red",
            )
            ctx.exit(1)

        try:
            encrypted_regex = rule["encrypted_regex"]
            re.compile(encrypted_regex)
        except re.error:
            click.secho(
                message=f"Invalid regex for 'encrypted_regex': {encrypted_regex}",
                bold=False,
                fg="red",
            )
            ctx.exit(1)

    for rule in creation_rules:
        path_regex = rule["path_regex"]
        encrypted_regex = rule["encrypted_regex"]

        if broken_yaml_found:
            break

        for file in find_all_files_by_regex(path_regex, received_path):
            if not load_all_yaml(file):
                click.secho(message=f"{file} is not a valid YAML!", bold=True, fg="red")
                broken_yaml_found = f"{file}"
                break

            for secret in load_all_yaml(file):
                if "sops" in secret:
                    secret.pop("sops", None)

                good_keys, bad_keys = _categorize_keys_based_on_their_values(
                    secret, encrypted_regex
                )
                all_keys: List[str] = good_keys + bad_keys

                for key in all_keys:
                    if key in good_keys:
                        click.secho(message=f"{file}::{key} ", bold=False, nl=False)
                        click.secho(message="[SAFE]", bold=False, fg="green")
                        good_keys_number += 1
                    else:
                        click.secho(message=f"{file}::{key} ", bold=False, nl=False)
                        click.secho(message="[UNSAFE]", bold=False, fg="red")
                        bad_keys_number += 1
                        if summary:
                            summary_line = f"UNSAFE secret '{key}' in '{file}'"
                            bad_keys_summary.append(summary_line)

    if summary:
        click.secho(message="---", bold=True, nl=True)
        click.secho(message="Summary:", bold=True, nl=True, fg="blue")
        if broken_yaml_found:
            click.secho(
                message=f"The yaml '{broken_yaml_found}' is broken, checks incomplete!",
                bold=True,
                nl=True,
                fg="red",
            )
        else:
            for entry in bad_keys_summary:
                click.secho(message=entry, bold=False, fg="red", nl=True)
            click.secho(message=f"{good_keys_number} safe ", bold=True, nl=False, fg="green")
            click.secho(message=f"{bad_keys_number} unsafe", bold=True, nl=True, fg="red")

    if bad_keys_number or broken_yaml_found:
        ctx.exit(1)

    ctx.exit(0)
