import os
import re
from pathlib import Path
from typing import Dict, Generator, Pattern, Tuple

import yaml


def load_yaml(path: Path) -> Dict:
    """Load a YAML content into a python dictionary.

    Args:
        path (Path): The path of the YAML file.

    Returns:
        Dict: The YAML file in a python dictionary form.
    """
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError:
            return {}


def find_by_key(data: Dict, target: Pattern[str]) -> Generator[Dict, None, None]:
    """Find the innermost key, value pair children of a target key in a dictionary.

    Args:
        data (Dict): the dictionary to parse
        target (Pattern[str]): the target key to search for

    Yields:
        Generator[Dict, None, None]: Iterable of the innermost children
            of the 'target' key of the 'data' dictionary
    """
    pattern: Pattern[str] = re.compile(target)

    for key, value in data.items():
        if pattern.search(key):
            yield {key: value}
        elif isinstance(value, dict):
            yield from find_by_key(value, target)
        elif isinstance(value, list):
            for elem in value:
                yield from find_by_key(elem, target)


def get_all_values(data: Dict) -> Generator[Tuple[str, str], None, None]:
    """Get all the values in a dictionary.

    Args:
        data (Dict): Dictionary to parse.

    Yields:
        Generator[Tuple[str, str], None, None]: Iterable of all the values in
            the 'data' dictionary.
    """
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
    """Find all the files that match a regular expression.

    Args:
        regex (Pattern[str]): Regex pattern.
        path (Path): Path of the root directory to search.

    Yields:
        Generator[Path, None, None]: Iterable of all the files
            in 'path' that match the 'regex'.
    """
    pattern: Pattern[str] = re.compile(regex)

    for root, _, files in os.walk(path):
        for file in files:
            # print("FILE: ", os.path.join(root, file))
            match = pattern.search(os.path.join(root, file))
            # print("PATTERN: ", regex)
            # print("MATCH: ", match)
            if match:
                yield Path(os.path.join(root, file))
