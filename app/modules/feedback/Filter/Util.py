import re
import unicodedata

BLACKLIST = [
    # insultos
    "idiota", "imbecil", "burro", "jumento", "estupido",
    "desgracado", "inutil", "verme", "maldito",
    "babaca", "escroto", "arrombado", "otario",
    # xingamentos pesados
    "vagabundo", "vagabunda", "canalha", "corno",
    # palavrões gerais
    "porra", "caralho", "cacete", "caceta", "merda", "bosta",
    "krl", "crl", "poha",
    # sexuais / ofensivos
    "puta", "puto", "foder", "foda", "fodas", "fdp",
    "filhodaputa", "filhadaputa", "vaitomarnocus", "vtnc", "vtnm",
    "cu", "buceta", "pau", "pinto",
    # variações comuns (bypass)
    "pqp", "vsf", "tmnc",
    # variações sonoras para fuzzy
    "porro", "parra", "pirra", "perre", "fuder",
]

def _strip_accents(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))

BLACKLIST_NORMALIZED = [_strip_accents(w.lower()) for w in BLACKLIST]

def less_repetition(texto: str) -> str:
    return re.sub(r"(.)\1{2,}", r"\1", texto)


def remove_spaces(texto: str) -> str:
    pattern = re.compile(r'(?<![a-z])([a-z])\s(?=[a-z](?:\s[a-z]|[^a-z]|$))')
    prev = None
    while prev != texto:
        prev = texto
        texto = pattern.sub(r'\1', texto)
    return texto

def remove_point_between_letters(texto: str) -> str:
    return re.sub(r'(?<=[a-z])[^a-z0-9\s](?=[a-z])', '', texto)
