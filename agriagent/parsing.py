from __future__ import annotations

import re
from dataclasses import dataclass

from .calculators.area import ALIASES
from .language import normalize_text

NUMBER = r"(?P<value>\d+(?:\.\d+)?)"


@dataclass(frozen=True)
class ParsedAreaRequest:
    value: float
    from_unit: str
    to_unit: str


@dataclass(frozen=True)
class ParsedFertilizerRequest:
    n: float
    p2o5: float
    k2o: float
    area_value: float
    area_unit: str


def _unit_pattern() -> str:
    aliases = sorted(ALIASES, key=len, reverse=True)
    return "|".join(re.escape(x) for x in aliases)


def parse_area_request(text: str) -> ParsedAreaRequest:
    normalized = normalize_text(text)
    units = _unit_pattern()
    pair = re.search(rf"{NUMBER}\s*(?P<from>{units})\b", normalized)
    if not pair:
        raise ValueError("Include an area value and unit, for example: '5 ropani to hectare'.")

    target_match = re.search(rf"(?:to|in|into|मा)\s*(?P<to>{units})\b", normalized)
    target = target_match.group("to") if target_match else "hectare"
    return ParsedAreaRequest(float(pair.group("value")), pair.group("from"), target)


def parse_fertilizer_request(text: str) -> ParsedFertilizerRequest:
    normalized = normalize_text(text)

    npk = re.search(
        r"(?P<n>\d+(?:\.\d+)?)\s*[-:/]\s*"
        r"(?P<p>\d+(?:\.\d+)?)\s*[-:/]\s*"
        r"(?P<k>\d+(?:\.\d+)?)",
        normalized,
    )
    if not npk:
        raise ValueError(
            "Include an approved N-P2O5-K2O rate, e.g. '100-50-30 kg/ha for 2 ropani'."
        )

    units = _unit_pattern()
    # Search the area after 'for'/'on' first so NPK values are never mistaken for land size.
    area = re.search(rf"(?:for|on|area|जग्गा|क्षेत्र|lai|ma)\s*{NUMBER}\s*(?P<unit>{units})\b", normalized)
    if not area:
        # Fall back to the last value+unit pair in the message.
        pairs = list(re.finditer(rf"{NUMBER}\s*(?P<unit>{units})\b", normalized))
        if not pairs:
            raise ValueError("Include the field area, e.g. 'for 2 ropani'.")
        area = pairs[-1]

    return ParsedFertilizerRequest(
        n=float(npk.group("n")),
        p2o5=float(npk.group("p")),
        k2o=float(npk.group("k")),
        area_value=float(area.group("value")),
        area_unit=area.group("unit"),
    )
