import os
import re
from pathlib import Path
from typing import Dict, Generator, Optional, Pattern, Tuple

import yaml


def load_yaml(path: Path) -> Optional[Dict]:
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError:
            return None


def find_by_key(data: Dict, target: Pattern[str]) -> Generator[Dict, None, None]:
    pattern: Pattern[str] = re.compile(target)
    for key, value in data.items():
        if pattern.match(key):
            yield {key: value}
        elif isinstance(value, dict):
            yield from find_by_key(value, target)
        elif isinstance(value, list):
            for elem in value:
                yield from find_by_key(elem, target)


def get_all_values(data: Dict) -> Generator[Tuple[str, str], None, None]:
    for key, value in data.items():
        if isinstance(value, dict):
            yield from get_all_values(value)
        elif isinstance(value, list):
            for elem in value:
                yield from get_all_values(elem)
        elif not isinstance(value, dict):
            yield key, str(value)


def find_all_files_by_regex(
    regex: Pattern[str], path: Path
) -> Generator[Path, None, None]:
    pattern = re.compile(regex)
    for root, _, files in os.walk(path):
        for file in files:
            match = pattern.search(file)
            if match:
                yield Path(os.path.join(root, file))
