from .Detectors import detector
from .Fuzzy import fuzzy
from .Blacklist import blacklist
from .Util import BLACKLIST

THRESHOLD = 89

def filter_message(message: str) -> dict:
    if blacklist(message):
        return {"blocked": True, "reason": "blacklist"}

    detector_result = detector(message)
    fuzzy_result = fuzzy(message, BLACKLIST, THRESHOLD)

    score = fuzzy_result["score"] + detector_result["score"]

    if score >= 4:
        return {
            "blocked": True,
            "reason": "suspect message",
            "score": score,
            "reasons": detector_result["reasons"]
        }

    return {
        "blocked": False,
        "score": score,
        "reasons": detector_result["reasons"]
    }