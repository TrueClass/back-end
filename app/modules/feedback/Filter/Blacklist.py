import re
from .Util import BLACKLIST_NORMALIZED
from .Normalize import normalize_full

def create_regex_blacklist(blacklist: list) -> re.Pattern:
    parts = [r"".join(f"{re.escape(c)}+" for c in word) for word in blacklist]
    pattern = r"(?<![a-z])(" + "|".join(parts) + r")(?![a-z])"
    return re.compile(pattern)

BLACKLIST_REGEX = create_regex_blacklist(BLACKLIST_NORMALIZED)

def compare_blacklist(text: str) -> bool:
    return bool(BLACKLIST_REGEX.search(text))


def blacklist(text: str) -> bool:
    fully_normalized = normalize_full(text)
    return compare_blacklist(fully_normalized)
