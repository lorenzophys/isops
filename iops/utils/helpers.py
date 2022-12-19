import os
import re
from pathlib import Path
from typing import Dict, Generator, List, Pattern, Tuple

from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


def load_yaml(path: Path) -> Dict:
    """Load a YAML content into a python dictionary.

    Args:
        path (Path): The path of the YAML file.

    Returns:
        Dict: The YAML file in a python dictionary form.
    """
    try:
        yaml = YAML(typ="safe")
        return yaml.load(path)
    except YAMLError:
        return {}


def load_all_yaml(path: Path) -> List[Dict]:
    """Like load_yaml, but loads yaml blocks.

    Args:
        path (Path): The path of the YAML file.

    Returns:
        List: A list of dictionaries corresponding to
            the different yaml blocks.

    """
    try:
        yaml = YAML(typ="safe")
        return list(yaml.load_all(path))
    except (ParserError, ScannerError):
        return []


def find_by_key(data: Dict, target: Pattern[str]) -> Generator[Dict, None, None]:
    """Find the innermost key-value pair children of a target key in a dictionary.

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
                if not isinstance(elem, dict):
                    continue
                yield from find_by_key(elem, target)


def all_dict_values(data: Dict) -> Generator[Tuple[str, str], None, None]:
    """Get all the values in a dictionary.

    Args:
        data (Dict): Dictionary to parse.

    Yields:
        Generator[Tuple[str, str], None, None]: Iterable of all the values in
            the 'data' dictionary.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            yield from all_dict_values(value)
        elif isinstance(value, list):
            for elem in value:
                yield from all_dict_values(elem)
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
            match = pattern.search(os.path.join(root, file))
            if match:
                yield Path(os.path.join(root, file))
