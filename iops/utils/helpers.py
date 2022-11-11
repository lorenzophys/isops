from pathlib import Path
from typing import Dict, Generator, Optional, Union

import yaml


def load_yaml(path: Path) -> Optional[Dict]:
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError:
            return None


def find_by_key(data: Dict, target: str) -> Generator[Dict, None, None]:
    for key, value in data.items():
        if key == target:
            yield {key: value}
        elif isinstance(value, dict):
            yield from find_by_key(value, target)
        elif isinstance(value, list):
            for elem in value:
                yield from find_by_key(elem, target)


def get_all_values(data: Dict) -> Generator[Union[str, int], None, None]:
    for _, value in data.items():
        if isinstance(value, dict):
            yield from get_all_values(value)
        elif isinstance(value, list):
            for elem in value:
                yield from get_all_values(elem)
        elif not isinstance(value, dict):
            yield value
