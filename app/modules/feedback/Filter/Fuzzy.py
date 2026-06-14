from rapidfuzz import fuzz
from Normalize import normalize_full
from Util import BLACKLIST_NORMALIZED
from typing import TypedDict

class FuzzyResult(TypedDict):
    score: int
    matched: str | None

MIN_WORD_LEN = 5

SHORT_THRESHOLD = 92
LONG_THRESHOLD  = 85

def _threshold_for(blocked_word: str) -> int:
    return SHORT_THRESHOLD if len(blocked_word) <= 6 else LONG_THRESHOLD

def fuzzy_detection(text: str, blacklist: list[str], default_threshold: int) -> tuple[bool, str | None]:
    words = text.split()
    for word in words:
        if len(word) < MIN_WORD_LEN:
            continue
        for blocked in blacklist:
            if len(blocked) < MIN_WORD_LEN:
                continue
            threshold = _threshold_for(blocked) if default_threshold == 0 else default_threshold
            if fuzz.partial_ratio(word, blocked) >= threshold:
                return True, blocked
    return False, None

def fuzzy(text: str, blacklist: list[str] = BLACKLIST_NORMALIZED, threshold: int = 0) -> FuzzyResult:
    normalized = normalize_full(text)
    matched, word = fuzzy_detection(normalized, blacklist, threshold)
    return FuzzyResult(score=3 if matched else 0, matched=word)
