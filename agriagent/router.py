from __future__ import annotations

import re

from .language import normalize_text
from .types import Intent, RouteDecision


class DeterministicRouter:
    """Keyword-first router. No language model participates in routing."""

    AREA_KEYWORDS = {
        "convert", "conversion", "hectare", "hectares", "ha", "ropani", "रोपनी",
        "aana", "ana", "आना", "bigha", "बिघा", "kattha", "katha", "कट्ठा",
        "dhur", "धुर", "square meter", "m2", "sqm", "acre", "jagga", "जग्गा",
    }
    FERTILIZER_KEYWORDS = {
        "fertilizer", "fertiliser", "urea", "dap", "mop", "npk", "nitrogen", "phosphate",
        "potash", "खाद", "मल", "युरिया", "डीएपी", "khad", "mal", "dose", "dose rate",
    }
    GREETING_KEYWORDS = {
        "hi", "hello", "hey", "namaste", "नमस्ते", "नमस्कार", "hello agriagent",
    }
    HELP_KEYWORDS = {"help", "what can you do", "सहायता", "के गर्न सक्छ", "k garna sakchhau"}

    _NPK_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?\s*[-:/]\s*\d+(?:\.\d+)?\s*[-:/]\s*\d+(?:\.\d+)?\b"
    )

    def route(self, text: str) -> RouteDecision:
        normalized = normalize_text(text)

        if self._matches_phrase(normalized, self.GREETING_KEYWORDS) and len(normalized.split()) <= 5:
            return RouteDecision(Intent.GREETING, 1.0, reason="greeting keyword")
        if self._matches_phrase(normalized, self.HELP_KEYWORDS):
            return RouteDecision(Intent.HELP, 1.0, reason="help keyword")

        fertilizer_hits = self._hits(normalized, self.FERTILIZER_KEYWORDS)
        area_hits = self._hits(normalized, self.AREA_KEYWORDS)

        # Priority is deliberate: fertilizer questions often contain an area unit.
        if fertilizer_hits or self._NPK_PATTERN.search(normalized):
            confidence = min(1.0, 0.78 + 0.06 * len(fertilizer_hits))
            return RouteDecision(
                Intent.FERTILIZER_CALCULATION,
                confidence,
                tuple(sorted(fertilizer_hits)),
                "fertilizer terms take precedence over area terms",
            )
        if area_hits and re.search(r"\d", normalized):
            confidence = min(1.0, 0.78 + 0.05 * len(area_hits))
            return RouteDecision(
                Intent.AREA_CONVERSION,
                confidence,
                tuple(sorted(area_hits)),
                "area term plus numeric value",
            )

        # Anything crop/agronomy-like is handled by lexical retrieval.
        if len(normalized) >= 3:
            return RouteDecision(Intent.AGRONOMY_QUERY, 0.70, reason="fallback to lexical retrieval")
        return RouteDecision(Intent.UNKNOWN, 0.0, reason="empty or too short")

    @staticmethod
    def _matches_phrase(text: str, phrases: set[str]) -> bool:
        return any(phrase in text for phrase in phrases)

    @staticmethod
    def _hits(text: str, keywords: set[str]) -> set[str]:
        hits: set[str] = set()
        padded = f" {text} "
        for keyword in keywords:
            if " " in keyword:
                if keyword in text:
                    hits.add(keyword)
            elif re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", padded):
                hits.add(keyword)
        return hits
