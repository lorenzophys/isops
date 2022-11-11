import os
import re
from pathlib import Path
from typing import Dict, List, Match, Optional, Pattern

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


def ensure_dotsops(path: Path) -> Optional[Dict]:
    matches: List[Path] = _match_config_files(path)
    if not matches:
        return None
    elif len(matches) > 1:
        return None
    else:
        dot_sops_path: Path = path / matches[0]
        return load_yaml(dot_sops_path)


def verify_encryption_regex(value: str) -> Optional[Match[str]]:
    encryption_pattern: Pattern[str] = re.compile(
        r"^ENC\[AES256_GCM,data:(.+),iv:(.+),tag:(.+),type:(.+)\]"
    )
    return encryption_pattern.fullmatch(value)
