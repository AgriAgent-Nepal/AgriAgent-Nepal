# AgriAgent Nepal 🌾

A **chat-based, multi-agent AI advisory reference system for Nepalese agriculture**, designed around one governing rule:

> **The language layer may read the question and phrase the answer, but it never decides what runs and it never creates a number.**

Tool routing is deterministic. Land-unit conversions and fertilizer quantities come from audited Python calculators. Agronomy knowledge is retrieved lexically from a local, provenance-aware corpus. This repository intentionally removes the crop-disease vision training/model subsystem and keeps only the text/chat architecture.

## Team

**Shova Gelal · Barosh Manandhar · Bishesh Marasini · Bhawana Ojha**  
Department of Artificial Intelligence, School of Engineering  
Kathmandu University (KU), Dhulikhel, Nepal

---

## Why AgriAgent Nepal?

AgriAgent Nepal was conceived to address the agronomy-advisory gap faced by Nepal's smallholder farmers. The project presentation frames that gap as extension services reaching only **15% of farming households** while agriculture employs **62% of the population**. The engineering question is therefore more important than “can an LLM answer farming questions?”:

**How do we make the parts that can cause real-world mistakes deterministic, inspectable, and testable?**

This repository is the chat-only implementation of that idea.

## What is included

- 🇳🇵 **Trilingual input handling** — English, Devanagari Nepali, and romanized Nepali
- 🧭 **Keyword-first deterministic intent router**
- 🧰 **Explicit intent → tool planner** with no model-based planning
- 📐 **Nepal land-unit calculator** — ropani, aana, paisa, daam, bigha, kattha, dhur, hectare, acre, square metre
- 🌱 **Deterministic fertilizer calculator** for scaling an *already-approved* N-P2O5-K2O rate to a farmer's field
- 🔎 **BM25 lexical retrieval written in Python**
- 🧩 **Source-quota merge** for retrieval diversity
- 🔢 **Number firewall** that hides all numeric literals from an optional language-model rephraser and restores only trusted calculator values afterward
- 💬 **Simple responsive browser chat UI**
- ⚡ **FastAPI JSON API**
- 🖥️ **Terminal chat client**
- ✅ **Tests, regression benchmark, CI, docs, and MIT license**

## Deliberately not included

This repository contains **no crop-disease vision model**: no image endpoint, training notebook, model weights, dataset, augmentation pipeline, or vision inference code. The full research architecture may use a two-stage vision cascade, but this repo is intentionally a clean text-only implementation.

## Architecture

```text
User question
    │
    ▼
Language detection
    │
    ▼
Deterministic keyword router
    │
    ▼
Deterministic planner ──────────────┐
    │                               │
    ├── area_converter              │  no LLM selects a tool
    ├── fertilizer_calculator       │
    └── lexical_retriever           │
            │                       │
            └── BM25 + quota merge ─┘
    │
    ▼
Audited facts / calculator outputs
    │
    ▼
Number firewall
    │   12.34 → [[NUM_0]] before any optional LLM
    ▼
Surface phrasing
    │
    ▼
Deterministic numeric reinsertion
    │
    ▼
Answer + source metadata
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for details.

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/YOUR-USERNAME/AgriAgent-Nepal.git
cd AgriAgent-Nepal

python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install:

```bash
pip install -e ".[dev]"
```

### 2. Start the web chat

```bash
agriagent serve
```

Open **http://127.0.0.1:8000**.

### 3. Or use the terminal

```bash
agriagent chat --debug
```

## Example questions

```text
Convert 5 ropani to hectare

100-50-30 kg/ha fertilizer for 2 ropani

टमाटरको पातमा कालो दाग छ, के हेर्नु पर्छ?

Mero makai ma fauji kira jasto dekhinchha, k herne?
```

The fertilizer example is intentionally phrased as a **calculation from an existing nutrient rate**. AgriAgent does not choose that agronomic rate itself.

## API

### `POST /api/chat`

Request:

```json
{
  "message": "Convert 5 ropani to hectare",
  "debug": true
}
```

Response structure:

```json
{
  "answer": "...",
  "language": "en",
  "intent": "area_conversion",
  "citations": [],
  "debug": {
    "planned_tools": ["area_converter"]
  }
}
```

Interactive API documentation is available at `/docs` while the server is running.

## Why the number firewall matters

Prompting a language model to “only use provided numbers” is not a guarantee. This repository instead protects numeric values structurally:

1. deterministic code calculates the numeric answer;
2. every numeric literal is replaced with an opaque token such as `[[NUM_0]]`;
3. an optional rephraser receives placeholders, never the actual values;
4. output is rejected if it invents a literal number or changes the placeholder set;
5. trusted values are reinserted by deterministic code.

The default repository uses an identity rephraser, so **no external model or API key is required**. A local or hosted LLM adapter can be added later without giving it routing authority or raw numeric values.

## Retrieval: lexical + quota merge

The retriever implements BM25 without an embedding service. Search results are first selected by source-group quotas (`government`, `university`, `extension`), then remaining slots are filled by global BM25 score. This keeps the retrieval mechanism inspectable and prevents one source family from trivially occupying every result.

The included corpus is deliberately small demo content. Before real deployment, replace it with curated and versioned material from authoritative Nepal agriculture sources.

## Reported research results

The project presentation reports:

| Component | Reported result |
|---|---:|
| Intent routing | 78.3% |
| Tool planning | 100% exact match |
| Tool false positives | 0 |

These are **reported project results supplied by the research team**. The original full benchmark is not bundled in this stripped-down repository, so this repo does not claim to reproduce the 78.3% result automatically. See [`docs/EVALUATION.md`](docs/EVALUATION.md).

## Run the bundled benchmark

```bash
python scripts/evaluate.py
```

This runs a small regression set across English, नेपाली, and romanized Nepali routing plus exact tool-plan checks.

## Test everything

```bash
pytest
ruff check agriagent tests scripts
python scripts/evaluate.py
```

GitHub Actions runs the same checks on Python 3.10, 3.11, and 3.12.

## Project layout

```text
AgriAgent-Nepal/
├── agriagent/
│   ├── api.py                  # FastAPI app
│   ├── agents.py               # specialist deterministic agents + registry
│   ├── cli.py                  # terminal + server CLI
│   ├── orchestrator.py         # request execution pipeline
│   ├── router.py               # keyword-first deterministic router
│   ├── planner.py              # audited intent -> tool table
│   ├── parsing.py              # structured request parsing
│   ├── retrieval.py            # BM25 + source-quota merge
│   ├── composer.py             # numeric firewall
│   ├── calculators/
│   │   ├── area.py
│   │   └── fertilizer.py
│   ├── data/
│   │   ├── knowledge.json
│   │   └── eval_cases.json
│   └── static/index.html       # browser chat UI
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_SOURCES.md
│   ├── EVALUATION.md
│   └── SAFETY_AND_GOVERNANCE.md
├── scripts/evaluate.py
├── tests/
├── .github/workflows/tests.yml
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
└── README.md
```

## Data and unit provenance

Nepal land-unit constants are based on government conversion tables. Government publications commonly state relationships such as **1 ropani = 16 aana = 5476 sq ft**, **1 bigha = 20 kattha = 72900 sq ft**, and **1 kattha = 20 dhur = 3645 sq ft**. See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the implementation policy and provenance notes.

## Known limitation: romanized Nepali

Romanized Nepali is intentionally handled with lightweight normalization and keyword aliases rather than a learned transliteration model. This makes failures auditable but means spelling variation can reduce routing/retrieval quality. Improving romanized Nepali normalization while keeping routing deterministic is one of the clearest next steps.

## Future work

- Offline-capable mobile/PWA client
- Larger reviewed Nepal agronomy corpus
- Better romanized Nepali normalization and transliteration
- Location/crop-season metadata filters in retrieval
- Versioned government recommendation tables with validity dates
- Optional guarded local-language rephraser behind the number firewall
- Evaluation against the original research benchmark

## Research and deployment note

This is research/demo software, not a substitute for a qualified agronomist or official extension service. The bundled text corpus is illustrative. A production deployment should use reviewed, versioned, locally scoped agronomic sources and current registered-product guidance.

## License

MIT License. See [`LICENSE`](LICENSE).
