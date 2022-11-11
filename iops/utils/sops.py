import os
import re
from pathlib import Path
from typing import Dict, List, Union

from iops.utils import load_yaml


def _match_config_files(path: Path) -> List[Path]:
    pattern = re.compile(r".sops.ya?ml")
    dotsops_dir = ".sops"
    root_matches = [file for file in os.listdir(path) if pattern.fullmatch(file)]
    nested_matches = []

    if dotsops_dir in os.listdir(path):
        nested_matches = [
            os.path.join(dotsops_dir, file)
            for file in os.listdir(path / dotsops_dir)
            if pattern.fullmatch(file)
        ]
    return root_matches + nested_matches


def ensure_dotsops(path: Path) -> Union[Dict, None]:
    matches = _match_config_files(path)
    if not matches:
        return None
    elif len(matches) > 1:
        return None
    else:
        dot_sops_path = os.path.join(path, matches[0])
        return load_yaml(dot_sops_path)


def verify_encryption_regex(value: str) -> Union[bool, None]:
    encryption_pattern = re.compile(
        r"^ENC\[AES256_GCM,data:(.+),iv:(.+),tag:(.+),type:(.+)\]"
    )
    return encryption_pattern.fullmatch(value)
