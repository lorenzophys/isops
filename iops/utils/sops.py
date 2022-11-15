import os
import re
from pathlib import Path
from typing import Dict, List, Match, Optional, Pattern, Tuple

from iops.utils import load_yaml


def _match_config_files(path: Path) -> List[Path]:
    pattern: Pattern[str] = re.compile(r".sops.ya?ml")
    dotsops_dir: str = ".sops"
    root_matches: List[Path] = [
        Path(file) for file in os.listdir(path) if pattern.fullmatch(file)
    ]
    nested_matches: List[Path] = []

    if dotsops_dir in os.listdir(path):
        nested_matches = [
            Path(os.path.join(dotsops_dir, file))
            for file in os.listdir(path / dotsops_dir)
            if pattern.fullmatch(file)
        ]
    return root_matches + nested_matches


def ensure_dotsops(path: Path) -> Tuple[Path, Dict]:
    """Ensure that the sops config file is present.

    Args:
        path (Path): the root directory where the files to check
            are located.

    Returns:
        Tuple[Path, Dict]: Both the path of the config file and
            it's content are returned.
    """
    matches: List[Path] = _match_config_files(path)
    if not matches or len(matches) > 1:
        return Path("NonePath"), {}
    else:
        good_match = path / matches[0]
        return good_match, load_yaml(good_match)


def verify_encryption_regex(value: str) -> Optional[Match[str]]:
    """Verify that a value matches the encryption regex.

    Args:
        value (str): A string to validate.

    Returns:
        Optional[Match[str]]: Returns the full match object or None
            if the value doesn't match.
    """
    encryption_pattern: Pattern[str] = re.compile(
        r"^ENC\[AES256_GCM,data:(.+),iv:(.+),tag:(.+),type:(.+)\]"
    )
    return encryption_pattern.fullmatch(value)
