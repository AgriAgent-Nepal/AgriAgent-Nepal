from __future__ import annotations

import json
from importlib.resources import files

from agriagent.planner import DeterministicPlanner
from agriagent.router import DeterministicRouter
from agriagent.types import Intent


def main() -> None:
    path = files("agriagent.data").joinpath("eval_cases.json")
    cases = json.loads(path.read_text(encoding="utf-8"))
    router = DeterministicRouter()
    planner = DeterministicPlanner()

    correct = 0
    plan_correct = 0
    false_positive_tools = 0
    rows = []
    for case in cases:
        expected = Intent(case["intent"])
        predicted = router.route(case["text"]).intent
        expected_tools = planner.tool_names(expected)
        predicted_tools = planner.tool_names(predicted)
        correct += predicted == expected
        plan_correct += predicted_tools == expected_tools
        if not expected_tools and predicted_tools:
            false_positive_tools += 1
        rows.append((case["text"], expected.value, predicted.value, predicted == expected))

    total = len(cases)
    print("AgriAgent Nepal — bundled mini benchmark")
    print(f"Cases: {total}")
    print(f"Intent accuracy: {correct / total * 100:.1f}% ({correct}/{total})")
    print(f"Exact tool-plan match: {plan_correct / total * 100:.1f}% ({plan_correct}/{total})")
    print(f"False-positive tool plans: {false_positive_tools}")
    print("\nCases:")
    for text, exp, pred, ok in rows:
        print(f"[{'OK' if ok else 'XX'}] {exp:24s} -> {pred:24s} | {text}")


if __name__ == "__main__":
    main()
