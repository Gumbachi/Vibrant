import re


def is_valid_hex(hexcode: str):
    """Validate a hex code."""
    return bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexcode))
