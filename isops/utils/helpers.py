import os
import re
from pathlib import Path
from typing import Dict, Generator, List, Optional, Pattern, Tuple

import pathspec
from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


def detect_encoding(path: Path) -> Optional[str]:
    """Detect the encoding of a file using BOM markers.

    Checks for UTF-16 BOM markers. Defaults to UTF-8 for files without BOM.
    Only reads a sample of the file for performance.

    Args:
        path (Path): The path of the file.

    Returns:
        Optional[str]: 'utf-16-le', 'utf-16-be', 'utf-8', or None on error.
    """
    try:
        with open(path, "rb") as f:
            # Read first 2 bytes for BOM check
            bom = f.read(2)
            if len(bom) < 2:
                return None

            # Check for UTF-16 BOM markers
            if bom == b"\xfe\xff":
                return "utf-16-be"
            elif bom == b"\xff\xfe":
                return "utf-16-le"

            # Default to UTF-8 for files without BOM
            return "utf-8"
    except OSError:
        return None


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
    except (YAMLError, UnicodeDecodeError):
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
    except (ParserError, ScannerError, UnicodeDecodeError):
        return []


def load_all_yaml_with_encoding(path: Path) -> Tuple[List[Dict], Optional[str]]:
    """Like load_all_yaml, but also returns the detected encoding.

    Args:
        path (Path): The path of the YAML file.

    Returns:
        Tuple[List[Dict], Optional[str]]: A tuple containing:
            - List of dictionaries corresponding to the different yaml blocks
            - The detected encoding (e.g., 'utf-8', 'utf-16') or None
            If parsing fails or file cannot be read, returns ([], None).
    """
    encoding = detect_encoding(path)

    # Handle UTF-16 files explicitly
    if encoding and encoding.startswith("utf-16"):
        try:
            yaml = YAML(typ="safe")
            with open(path, "r", encoding=encoding) as f:
                return list(yaml.load_all(f)), encoding
        except (ParserError, ScannerError, UnicodeDecodeError, OSError):
            return [], None

    # For UTF-8 or errors, use standard load_all_yaml
    data = load_all_yaml(path)
    return data, encoding if data else None


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
                # Only recurse if the element is a dict
                if isinstance(elem, dict):
                    yield from all_dict_values(elem)
        elif not isinstance(value, dict):
            yield key, str(value)


def _load_gitignore_spec(search_path: Path) -> Optional[pathspec.PathSpec]:
    """Load .gitignore patterns from the search path.

    Args:
        search_path (Path): The root path to search for .gitignore.

    Returns:
        Optional[pathspec.PathSpec]: A PathSpec object, or None if no .gitignore found
                                     or if parsing fails.
    """
    gitignore_path = search_path / ".gitignore"
    if not (gitignore_path.exists() and gitignore_path.is_file()):
        return None

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = f.read().splitlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    except (OSError, UnicodeDecodeError):
        # File access or encoding issues - return None
        return None


def find_all_files_by_regex(regex: Pattern[str], path: Path) -> Generator[Path, None, None]:
    """Find all the files that match a regular expression.

    Respects .gitignore patterns if a .gitignore file exists in the search path.
    Automatically excludes .git directory.

    Args:
        regex (Pattern[str]): Regex pattern (string or compiled).
        path (Path): Path of the root directory to search.

    Yields:
        Generator[Path, None, None]: Iterable of all the files
            in 'path' that match the 'regex'.
    """
    # Ensure pattern is compiled (handles both string and Pattern inputs)
    pattern = re.compile(regex) if isinstance(regex, str) else regex
    gitignore_spec = _load_gitignore_spec(path)

    for root, dirs, files in os.walk(path):
        root_path = Path(root)
        rel_root = root_path.relative_to(path)

        # Filter directories: exclude .git and gitignored dirs in one pass
        dirs[:] = [
            d
            for d in dirs
            if d != ".git"
            and (not gitignore_spec or not gitignore_spec.match_file(str(rel_root / d) + "/"))
        ]

        for file in files:
            file_path = root_path / file

            # Check if file matches the regex and is not ignored
            if pattern.search(str(file_path)):
                if not gitignore_spec or not gitignore_spec.match_file(
                    str(file_path.relative_to(path))
                ):
                    yield file_path
