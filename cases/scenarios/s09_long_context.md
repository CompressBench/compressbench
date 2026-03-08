---
id: s09_long_context
name: Long Context (>2K tokens)
category_map: []
case_ids: []
priority: P0
current_score: null
---

# Long Context (>2K tokens)

## What Is This Scenario

Real-world prompts are often 5K-50K+ tokens: full codebase files, lengthy documentation, multi-turn conversation histories, or RAG with many retrieved chunks. Current benchmark cases average ~450 tokens — way too short to represent production workloads. Compression behavior changes dramatically at scale: more redundancy to exploit, but also more risk of critical information being buried and deleted.

## Example Prompt

```
[5,000+ token system prompt with company policies]
[3,000+ tokens of retrieved documentation from 5 RAG chunks]
[2,000+ tokens of conversation history across 8 turns]

User: Based on everything above, what's the refund deadline for my digital purchase?
```

## Compression Red Lines

- [ ] **Answer-bearing content** — the specific paragraph/sentence that answers the user's question
- [ ] **Early-prompt rules** — system prompt instructions that appear far from the question
- [ ] **Cross-reference integrity** — "as mentioned in section 3" still makes sense after compression
- [ ] **Turn boundaries** — in long chat histories, who said what must be preserved
- [ ] **RAG chunk attribution** — which source said what (for citation)

## Compression Opportunities

- Massive redundancy in long texts (same concept rephrased multiple times)
- Boilerplate headers/footers repeated across RAG chunks
- Earlier conversation turns that were fully resolved
- Verbose policy language that can be condensed
- Irrelevant RAG chunks (retrieved but not relevant to the question)

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| task_accuracy | 35% | >= 0.85 | Downstream task still correct |
| critical_unit_recall | 25% | >= 0.90 | Key facts, numbers, entities preserved |
| positional_robustness | 20% | >= 0.80 | Info at beginning/middle/end equally preserved |
| token_savings | 20% | >= 30% | Long contexts should yield higher savings |

## Current Status

- **Cases**: 0 — all current cases are 200-750 tokens
- **Target**: 15 cases at varying lengths:
  - 5 cases @ 2K-5K tokens
  - 5 cases @ 5K-15K tokens
  - 5 cases @ 15K-50K tokens
- **Current Score**: N/A
- **Known Issues**: LLMLingua-2 may have memory/latency issues at 50K tokens; compression quality may degrade at scale
- **Recommended Strategy**: Chunked compression with importance scoring per chunk; protect first and last chunks more

## Notes

This is where compression delivers the most value — a 30K token prompt compressed to 15K saves real money and latency. But it's also where quality failures are hardest to catch (buried in a wall of text). Need to test positional bias: does the compressor disproportionately cut content from the middle?
