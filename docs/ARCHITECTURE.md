# Architecture

## Governing principle

> The language layer may read a farmer's question and phrase an answer, but it does not decide which tool runs and it does not create numeric values.

The chat-only repository enforces this in code rather than through prompting alone.

## Request flow

```text
Farmer message
     |
     v
Language detector
     |
     v
Deterministic keyword router
     |
     v
Deterministic planner ----------- no LLM here
     |
     +--> area_converter
     +--> fertilizer_calculator
     +--> lexical_retriever (BM25 + source quota merge)
     |
     v
AdvisoryPacket (facts + provenance)
     |
     v
Number firewall
     |
 optional rephraser sees [[NUM_0]], [[NUM_1]], ... only
     |
 deterministic reinsertion of calculator values
     |
     v
Final answer
```

## Why this stripped-down repository has no vision code

The research system described in the presentation includes a two-stage crop-disease vision cascade. This repository intentionally excludes training data, model weights, training notebooks, inference pipelines, and image endpoints. It is a clean text-only reference implementation for the orchestration, deterministic tools, retrieval, and chat UX.

## Specialist agents

`AgentRegistry` exposes three specialist agents: `AreaConversionAgent`, `FertilizerAgent`, and `KnowledgeAgent`. The orchestrator may execute only the agent named by the deterministic plan; agents do not hand control to one another and no language model chooses an agent.

## Deterministic tool routing

`DeterministicRouter` uses explicit multilingual keywords and an audited priority rule. Fertilizer routing has priority over plain area conversion because fertilizer questions frequently contain land units. `DeterministicPlanner` is a literal intent-to-tool table.

## Retrieval

`LexicalRetriever` implements BM25 using the Python standard library. Candidates must first clear a relative relevance threshold; results are then merged with per-source-group quotas before a global score fill. This preserves source diversity without allowing a quota to force a clearly weak match into the response.

## Numerical firewall

`NumberFirewallComposer` replaces every numeric literal with an opaque placeholder before an optional rephraser is called. A candidate response is rejected if it introduces a literal number, adds a placeholder, or drops a placeholder. Trusted values are restored only after validation.

This is intentionally stronger than asking an LLM in a prompt to “not make up numbers.”
