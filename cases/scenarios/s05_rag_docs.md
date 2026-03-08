---
id: s05_rag_docs
name: RAG & Documentation Context
category_map: [documentation]
case_ids: [cb_071, cb_072, cb_073, cb_074, cb_075, cb_076, cb_077, cb_078, cb_079, cb_080, cb_081, cb_082, cb_083, cb_084, cb_085, cb_086, cb_087, cb_088, cb_089, cb_090]
priority: P1
current_score: null
---

# RAG & Documentation Context

## What Is This Scenario

Long documentation passages retrieved by RAG and injected into context. SDK guides, install instructions, API references, runbooks. The LLM needs to answer a specific question from the docs. Most of the text is relevant background but only a few sentences contain the actual answer.

## Example Prompt

```
Based on the following documentation, answer the question.

# Installing the Vectrix Python SDK
## Prerequisites
- Python >= 3.9
- pip >= 22.0
- A valid API key from dashboard.vectrix.dev

## Installation
pip install vectrix-sdk

## Configuration
Set your API key:
export VECTRIX_API_KEY=vx_live_abc123

## Quick Start
from vectrix import Client
client = Client()
results = client.search("quarterly revenue", top_k=5)

Question: What is the minimum Python version required?
```

## Compression Red Lines

- [ ] **Answer-bearing sentences** — the specific text that answers the question
- [ ] **Version numbers** — `3.9`, `22.0`, `v2.3.1`
- [ ] **Code examples** — install commands, config snippets
- [ ] **URLs and paths** — `dashboard.vectrix.dev`, env var names

## Compression Opportunities

- Sections unrelated to the question (if question is known at compression time)
- Verbose introductions and overviews
- Repeated patterns in API reference (similar endpoint descriptions)
- Table of contents, navigation text
- License/changelog boilerplate

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| task_accuracy | 40% | >= 0.90 | Question still answerable correctly |
| critical_unit_recall | 30% | >= 0.90 | Version numbers, commands, URLs preserved |
| structural_preservation | 15% | >= 0.80 | Headers, code blocks, lists intact |
| token_savings | 15% | >= 20% | Docs are verbose, good compression potential |

## Current Status

- **Cases**: Shares 20 cases with s04 (cb_071 — cb_090), overlapping category
- **Avg tokens**: 491
- **Current Score**: Not yet benchmarked
- **Known Issues**: Without knowing the question at compression time, we can't target irrelevant sections
- **Recommended Strategy**: Question-aware compression (compress harder on sections far from the query topic)

## Notes

This overlaps with s04_rule_constraints — same `documentation` category but different intent. s04 focuses on preserving rules, s05 focuses on preserving answer-bearing content. Future case expansion should split these into separate case IDs. RAG is a huge market — every company doing "chat with your docs" benefits from this.
