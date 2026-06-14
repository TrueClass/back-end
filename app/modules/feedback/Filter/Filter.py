from Normalize import normalize
from Detectors import detector
from Fuzzy import fuzzy
from Blacklist import blacklist
from Util import BLACKLIST

THRESHOLD = 89

def filter_message(message: str) -> dict:
    normalized_message = normalize(message)

    if blacklist(normalized_message):
        return {"blocked": True, "reason": "blacklist"}

    score = fuzzy(normalized_message, BLACKLIST, THRESHOLD) + detector(message)

    if score >= 4:
        return {"blocked": True, "reason": "suspect message", "score": score}

    return {"blocked": False, "score": score}