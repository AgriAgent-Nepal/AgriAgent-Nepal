from __future__ import annotations

from dataclasses import asdict

from .calculators.area import convert_area
from .calculators.fertilizer import calculate_npk_program
from .parsing import parse_area_request, parse_fertilizer_request
from .retrieval import LexicalRetriever
from .types import Language, ToolResult


class AreaConversionAgent:
    name = "area_converter"

    def run(self, message: str, language: Language) -> ToolResult:
        req = parse_area_request(message)
        result = convert_area(req.value, req.from_unit, req.to_unit)
        return ToolResult(
            tool=self.name,
            ok=True,
            data={"request": asdict(req), "conversion": asdict(result)},
            citations=[
                {
                    "title": "Nepal government land-area conversion tables",
                    "url": "https://www.dudbc.gov.np/",
                }
            ],
        )


class FertilizerAgent:
    name = "fertilizer_calculator"

    def run(self, message: str, language: Language) -> ToolResult:
        req = parse_fertilizer_request(message)
        area = convert_area(req.area_value, req.area_unit, "hectare")
        plan = calculate_npk_program(
            area_ha=area.hectares,
            target_n_kg_ha=req.n,
            target_p2o5_kg_ha=req.p2o5,
            target_k2o_kg_ha=req.k2o,
        )
        return ToolResult(
            tool=self.name,
            ok=True,
            data={"request": asdict(req), "area": asdict(area), "plan": asdict(plan)},
            citations=[
                {
                    "title": "Nepal land-area conversion source",
                    "url": "https://www.dudbc.gov.np/",
                }
            ],
        )


class KnowledgeAgent:
    name = "lexical_retriever"

    def __init__(self, retriever: LexicalRetriever | None = None):
        self.retriever = retriever or LexicalRetriever.from_package_data()

    def run(self, message: str, language: Language) -> ToolResult:
        hits = self.retriever.search(message, top_k=3)
        if not hits:
            return ToolResult(
                tool=self.name,
                ok=False,
                message="I could not find a sufficiently relevant record in the local demo knowledge base.",
            )
        return ToolResult(
            tool=self.name,
            ok=True,
            data={
                "passages": [h.record.localized_text(language) for h in hits],
                "hits": [{"id": h.record.id, "score": h.score} for h in hits],
            },
            citations=[
                {
                    "title": h.record.source_title,
                    "url": h.record.source_url,
                    "record_id": h.record.id,
                }
                for h in hits
            ],
        )


class AgentRegistry:
    """Explicit registry of specialist agents allowed to execute tool plans."""

    def __init__(self):
        agents = [AreaConversionAgent(), FertilizerAgent(), KnowledgeAgent()]
        self._agents = {agent.name: agent for agent in agents}

    def run(self, tool_name: str, message: str, language: Language) -> ToolResult:
        if tool_name not in self._agents:
            raise ValueError(f"Unknown tool/agent: {tool_name}")
        return self._agents[tool_name].run(message, language)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._agents)
