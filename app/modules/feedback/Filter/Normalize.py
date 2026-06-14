import unicodedata
import re
from .Util import less_repetition, remove_spaces, remove_point_between_letters

def strip_accents(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))

def to_lowercase(texto: str) -> str:
    return texto.lower()

def leetspeak(texto: str) -> str:
    mapa = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "@": "a",
        "$": "s",
        "5": "s",
        "7": "t",
    }
    if re.search(r"[a-z]", texto):
        for char, letra in mapa.items():
            texto = texto.replace(char, letra)
    return texto

def normalize(texto: str) -> str:
    texto = to_lowercase(texto)
    texto = strip_accents(texto)
    texto = leetspeak(texto)
    return texto

def normalize_full(texto: str) -> str:
    texto = to_lowercase(texto)
    texto = strip_accents(texto)
    texto = leetspeak(texto)
    texto = remove_point_between_letters(texto)
    texto = less_repetition(texto)
    texto = remove_spaces(texto)
    return texto