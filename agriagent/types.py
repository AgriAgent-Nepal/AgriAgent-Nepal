from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Language(str, Enum):
    ENGLISH = "en"
    NEPALI = "ne"
    ROMANIZED_NEPALI = "ne-roman"


class Intent(str, Enum):
    GREETING = "greeting"
    HELP = "help"
    AREA_CONVERSION = "area_conversion"
    FERTILIZER_CALCULATION = "fertilizer_calculation"
    AGRONOMY_QUERY = "agronomy_query"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RouteDecision:
    intent: Intent
    confidence: float
    matched_keywords: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    tool: str
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    citations: list[dict[str, str]] = field(default_factory=list)


@dataclass
class AdvisoryPacket:
    language: Language
    intent: Intent
    title: str
    body: str
    trusted_numbers: list[str] = field(default_factory=list)
    citations: list[dict[str, str]] = field(default_factory=list)
    debug: dict[str, Any] = field(default_factory=dict)
