from agriagent.orchestrator import AgriAgent


def test_chat_area_debug_plan():
    result = AgriAgent().chat("Convert 5 ropani to hectare", debug=True)
    assert result["intent"] == "area_conversion"
    assert result["debug"]["planned_tools"] == ["area_converter"]
    assert "ha" in result["answer"]


def test_chat_fertilizer_plan_has_no_planner_llm():
    result = AgriAgent().chat("100-50-30 kg/ha fertilizer for 2 ropani", debug=True)
    assert result["debug"]["planned_tools"] == ["fertilizer_calculator"]
    assert "DAP" in result["answer"]
