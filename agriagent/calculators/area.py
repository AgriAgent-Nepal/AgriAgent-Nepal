from __future__ import annotations

from dataclasses import dataclass


# Values are based on Nepal government conversion tables. See docs/DATA_SOURCES.md.
SQM_PER_UNIT = {
    "sqm": 1.0,
    "hectare": 10_000.0,
    "acre": 4_046.8564224,
    "ropani": 508.74,
    "aana": 31.79625,  # 1/16 ropani, keeping internal consistency.
    "paisa": 7.9490625,
    "daam": 1.987265625,
    "bigha": 6_772.41,
    "kattha": 338.6205,  # 1/20 bigha.
    "dhur": 16.931025,   # 1/20 kattha.
}

ALIASES = {
    "m2": "sqm", "m²": "sqm", "sq m": "sqm", "square meter": "sqm", "square meters": "sqm",
    "ha": "hectare", "hectare": "hectare", "hectares": "hectare", "hector": "hectare",
    "ropani": "ropani", "रोपनी": "ropani",
    "aana": "aana", "ana": "aana", "आना": "aana",
    "paisa": "paisa", "पैसा": "paisa",
    "daam": "daam", "dam": "daam", "दाम": "daam",
    "bigha": "bigha", "बिघा": "bigha",
    "kattha": "kattha", "katha": "kattha", "कट्ठा": "kattha", "कठ्ठा": "kattha",
    "dhur": "dhur", "धुर": "dhur",
    "acre": "acre", "acres": "acre",
}


@dataclass(frozen=True)
class AreaConversion:
    input_value: float
    input_unit: str
    output_value: float
    output_unit: str
    square_metres: float
    hectares: float


def canonical_unit(unit: str) -> str:
    key = unit.strip().lower()
    if key not in ALIASES:
        raise ValueError(f"Unsupported area unit: {unit}")
    return ALIASES[key]


def convert_area(value: float, from_unit: str, to_unit: str = "hectare") -> AreaConversion:
    if value < 0:
        raise ValueError("Area cannot be negative.")
    source = canonical_unit(from_unit)
    target = canonical_unit(to_unit)
    sqm = value * SQM_PER_UNIT[source]
    out = sqm / SQM_PER_UNIT[target]
    return AreaConversion(
        input_value=value,
        input_unit=source,
        output_value=out,
        output_unit=target,
        square_metres=sqm,
        hectares=sqm / 10_000.0,
    )
