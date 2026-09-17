from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from .types import AdvisoryPacket, Language

NUMBER_RE = re.compile(r"(?<![A-Za-z_])[-+]?\d+(?:\.\d+)?(?:%|\b)")
PLACEHOLDER_RE = re.compile(r"\[\[NUM_(\d+)\]\]")


class Rephraser(Protocol):
    """Optional language model interface. It receives no literal numeric values."""

    def rephrase(self, text_with_placeholders: str, language: Language) -> str: ...


@dataclass
class IdentityRephraser:
    def rephrase(self, text_with_placeholders: str, language: Language) -> str:
        return text_with_placeholders


class NumberFirewallComposer:
    """Allows a language layer to rephrase text without seeing or inventing numbers.

    Numeric literals are replaced with opaque placeholders before the rephraser is called.
    The returned text is rejected if it introduces any literal number or drops/adds placeholders.
    Deterministic code then restores the trusted numeric values.
    """

    def __init__(self, rephraser: Rephraser | None = None):
        self.rephraser = rephraser or IdentityRephraser()

    def compose(self, packet: AdvisoryPacket) -> str:
        raw = f"{packet.title}\n\n{packet.body}".strip()
        protected, values = self._protect_numbers(raw)
        candidate = self.rephraser.rephrase(protected, packet.language)
        if not self._valid(candidate, len(values)):
            candidate = protected
        for idx, value in enumerate(values):
            candidate = candidate.replace(f"[[NUM_{idx}]]", value)
        return candidate

    @staticmethod
    def _protect_numbers(text: str) -> tuple[str, list[str]]:
        values: list[str] = []

        def repl(match: re.Match[str]) -> str:
            values.append(match.group(0))
            return f"[[NUM_{len(values) - 1}]]"

        return NUMBER_RE.sub(repl, text), values

    @staticmethod
    def _valid(candidate: str, expected_count: int) -> bool:
        if NUMBER_RE.search(candidate):
            return False
        indices = sorted(int(x) for x in PLACEHOLDER_RE.findall(candidate))
        return indices == list(range(expected_count))
