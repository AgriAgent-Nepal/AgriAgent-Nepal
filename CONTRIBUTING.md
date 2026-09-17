# Contributing

Thank you for improving AgriAgent Nepal.

1. Create a feature branch.
2. Keep routing and tool planning deterministic and testable.
3. Do not place agronomic dose recommendations directly in code unless they come from a versioned, audited source and include provenance.
4. Any optional language model must sit behind the number firewall and must never decide tool execution.
5. Add or update tests for every routing, calculator, or retrieval change.
6. Run `pytest`, `ruff check agriagent tests scripts`, and `python scripts/evaluate.py` before opening a pull request.

For production knowledge records, store source title, URL/document identifier, effective date/version, crop/location scope, and review status.
