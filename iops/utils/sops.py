import re
from typing import Match, Optional, Pattern


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
