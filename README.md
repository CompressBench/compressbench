# CompressBench

**Real-world benchmarks for prompt compression methods**

[![Leaderboard](https://img.shields.io/badge/leaderboard-compressbench.ai-blue)](https://compressbench-leaderboard.vercel.app)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

CompressBench evaluates prompt compression methods by measuring whether compressed prompts still enable LLMs to complete downstream tasks — not just text similarity.

Results are collected on a public leaderboard at **[compressbench-leaderboard.vercel.app](https://compressbench-leaderboard.vercel.app)**.

## Why CompressBench?

Most compression benchmarks measure text similarity (BLEU, ROUGE). CompressBench tests what actually matters:

- **Task completion** — Can the model still solve the original task after compression?
- **Information preservation** — Are critical facts, entities, and code preserved?
- **Structural fidelity** — Are code blocks, JSON, tables, and headers intact?
- **Real-world diversity** — 100 cases across 5 categories at 3 compression rates

## Quick Start

```bash
pip install compressbench

# Run baseline benchmarks
compressbench run --method truncation
compressbench run --method random_drop

# Test your own compressor (any HTTP endpoint)
compressbench run --method http --endpoint http://localhost:8080/compress

# View results
compressbench results latest

# Submit to leaderboard
compressbench register
compressbench submit results/result_truncation_*.json
```

**Requirements:** Python 3.10+

## What Gets Tested

100 benchmark cases across 5 categories, each evaluated at 3 compression rates (0.25, 0.50, 0.70) = **300 evaluations per method**.

| Category | Cases | What's tested |
|----------|-------|---------------|
| **Code Context** | 20 | Bug finding, function identification, config interpretation |
| **Chat History** | 20 | Commitment extraction, unresolved issue detection |
| **Structured Data** | 20 | Field lookup, constraint validation, JSON/YAML parsing |
| **Documentation** | 20 | Q&A, instruction following, specification recall |
| **Mixed** | 20 | Agent planning, multi-hop decisions |

## Metrics

| Metric | Weight | Description |
|--------|--------|-------------|
| **TRS** (Task Retention Score) | 50% | Can the model still complete the task after compression? |
| **CIR** (Critical Information Recall) | 20% | Are key facts/entities preserved? |
| **SPS** (Semantic Preservation Score) | 10% | Semantic similarity (embedding cosine) |
| **SFS** (Structural Fidelity Score) | 10% | Code blocks, lists, headers, JSON preserved? |
| **CES** (Compression Efficiency Score) | 10% | Did it actually compress to the target rate? |

## Scoring Formula

```
CBv2 = 100 × TRS^0.50 × CIR^0.20 × SPS^0.10 × SFS^0.10 × CES^0.10
Final score = mean(CBv2@0.25, CBv2@0.50, CBv2@0.70)
```

**Hard constraints:**
- TRS < 0.85 → 50% score penalty
- CIR < 0.80 → flagged as information-lossy
- Structure required but invalid → case score = 0

## Custom Compressor

Implement a compression endpoint that accepts:

```json
POST /compress
{"text": "...", "rate": 0.5}
```

And returns:

```json
{"compressed_text": "...", "original_tokens": 1000, "compressed_tokens": 500}
```

Then run:

```bash
compressbench run --method http --endpoint http://localhost:8080/compress
```

## Project Structure

```
compressbench/
├── cases/                 ← 100 benchmark cases (JSONL)
├── compressbench/
│   ├── cli.py             ← CLI commands
│   ├── runner.py           ← Benchmark pipeline
│   ├── schemas.py          ← Data types
│   ├── scoring.py          ← CBv2 computation
│   ├── upload.py           ← Leaderboard upload
│   ├── adapters/           ← Compression method adapters
│   └── metrics/            ← Individual metric calculations
├── tests/                 ← 28 tests
└── pyproject.toml
```

## License

Apache 2.0
