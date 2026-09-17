.PHONY: install test lint eval serve

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check agriagent tests scripts

eval:
	python scripts/evaluate.py

serve:
	agriagent serve
