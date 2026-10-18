import re
from typing import TypedDict

class DetectorResult(TypedDict):
    score: int
    reasons: list[str]

def special_character(message: str) -> bool:
    if not message:
        return False
    especiais = re.findall(r"[^a-z0-9\s,.]", message)
    return len(especiais) / len(message) > 0.3

def spam_detector(message: str) -> bool:
    return bool(re.search(r"(.)\1{3,}", message))

def space_detector(message: str) -> bool:
    regex = r"(?<![a-z])(?:[a-z]\s){3,}[a-z](?![a-z])"
    return bool(re.search(regex, message))

def detector(message: str) -> DetectorResult:
    score = 0
    reasons: list[str] = []

    if special_character(message):
        score += 1
        reasons.append("special_character")

    if space_detector(message):
        score += 1
        reasons.append("space_detector")

    if spam_detector(message):
        score += 2
        reasons.append("spam_detector")

    return DetectorResult(score=score, reasons=reasons)