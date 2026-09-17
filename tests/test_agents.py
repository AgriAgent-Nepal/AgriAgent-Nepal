from agriagent.agents import AgentRegistry
from agriagent.types import Language


def test_registry_has_expected_specialists():
    registry = AgentRegistry()
    assert registry.names == ("area_converter", "fertilizer_calculator", "lexical_retriever")


def test_area_agent_executes_deterministically():
    result = AgentRegistry().run("area_converter", "2 ropani to hectare", Language.ENGLISH)
    assert result.ok
    assert result.data["conversion"]["hectares"] > 0
