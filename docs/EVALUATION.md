# Evaluation

## Reported research results

The project presentation reports the following results from the team's research system:

- Intent routing: **78.3%**
- Tool planning: **100% exact match**
- Tool-planning false positives: **0**
- Retrieval performance: reported separately in the presentation/experimental materials

These values are retained here as **reported project results supplied by the authors**. This stripped-down repository does not include the original full benchmark dataset, the vision subsystem, or all research experiments, so it does not claim to independently reproduce those figures.

## Reproducible mini benchmark in this repository

Run:

```bash
python scripts/evaluate.py
```

The bundled mini benchmark tests representative English, Devanagari Nepali, and romanized Nepali inputs for routing and exact tool planning. It is a smoke/regression benchmark, not a substitute for the original research evaluation.

## Unit tests

`pytest` covers:

- Nepal land-unit conversions
- fertilizer mass balance
- deterministic router behavior
- lexical retrieval
- number-firewall behavior
- end-to-end orchestration
