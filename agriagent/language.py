from __future__ import annotations

import re
import unicodedata

from .types import Language

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

ROMANIZED_HINTS = {
    "malai", "mero", "kati", "bali", "dhaan", "dhan", "gahu", "makai", "tarkari",
    "rog", "kira", "pani", "khad", "jagga", "chha", "cha", "lai", "sodhnus", "herne",
}

STRONG_ROMANIZED_HINTS = {"malai", "mero", "jagga", "chha", "cha", "lai", "kira", "khad"}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text


def detect_language(text: str) -> Language:
    normalized = normalize_text(text)
    if DEVANAGARI_RE.search(normalized):
        return Language.NEPALI

    words = set(re.findall(r"[a-z]+", normalized))
    matched = words & ROMANIZED_HINTS
    if len(matched) >= 2 or (matched & STRONG_ROMANIZED_HINTS and len(words) <= 6):
        return Language.ROMANIZED_NEPALI
    return Language.ENGLISH
