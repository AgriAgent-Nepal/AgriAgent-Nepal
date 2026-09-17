from __future__ import annotations

from .types import Intent, ToolCall


class DeterministicPlanner:
    """Maps intents to tools using an explicit audited table."""

    PLAN = {
        Intent.AREA_CONVERSION: ("area_converter",),
        Intent.FERTILIZER_CALCULATION: ("fertilizer_calculator",),
        Intent.AGRONOMY_QUERY: ("lexical_retriever",),
        Intent.GREETING: (),
        Intent.HELP: (),
        Intent.UNKNOWN: (),
    }

    def tool_names(self, intent: Intent) -> tuple[str, ...]:
        return self.PLAN[intent]

    def plan(self, intent: Intent, arguments: dict) -> list[ToolCall]:
        return [ToolCall(name=name, arguments=arguments) for name in self.tool_names(intent)]
