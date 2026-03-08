# CompressBench Scenarios

Human-readable scenario index for benchmark cases. Each scenario describes a real-world compression use case, what must be preserved, what can be compressed, and how to grade quality.

## Scenario Map

### Existing Cases (100 in openclaw_v1.jsonl)

| ID | Scenario | Priority | Cases | Category | Key Challenge |
|----|----------|----------|-------|----------|---------------|
| s01 | [Code Review & Debugging](s01_code_review.md) | **P0** | 25 | code_context | Preserve identifiers, indentation, structure |
| s02 | [JSON & Structured Output](s02_json_api.md) | **P0** | 20 | structured_data | Preserve JSON delimiters, field names, exact values |
| s03 | [Customer Service & Chat](s03_customer_service.md) | **P0** | 25 | chat_history | Preserve error codes and numbers, compress filler |
| s04 | [System Prompts with Rules](s04_rule_constraints.md) | **P0** | 20 | documentation | Preserve MUST/NEVER rules, safety-critical |
| s05 | [RAG & Documentation](s05_rag_docs.md) | P1 | 20* | documentation | Preserve answer-bearing content |
| s06 | [Agent Task Logs](s06_agent_workflow.md) | P1 | 10 | mixed | Mixed content, preserve tool calls and conclusions |

*s04 and s05 share the same 20 documentation cases — they represent different compression intents for the same content type.

### New Scenarios (cases TBD)

| ID | Scenario | Priority | Target Cases | Key Challenge |
|----|----------|----------|-------------|---------------|
| s07 | [Function Calling & Tool Use](s07_function_calling.md) | **P0** | 15-20 | Preserve JSON Schema, tool names, param types |
| s08 | [Multilingual (CJK)](s08_multilingual.md) | P1 | 15 | CJK tokenization, encoding integrity |
| s09 | [Long Context (>2K tokens)](s09_long_context.md) | **P0** | 15 | Positional bias, scaling behavior |
| s10 | [Prompt Chains & Multi-step](s10_prompt_chain.md) | P1 | 10 | Step completeness, ordering |
| s11 | [Few-shot Examples](s11_few_shot.md) | P1 | 10 | Example count, input/output pairing |

## How Categories Map

```
openclaw_v1.jsonl categories    →    Scenarios (existing)
─────────────────────────────        ──────────
code_context (25 cases)         →    s01 Code Review
structured_data (20 cases)      →    s02 JSON & Structured
chat_history (25 cases)         →    s03 Customer Service
documentation (20 cases)        →    s04 Rules + s05 RAG Docs
mixed (10 cases)                →    s06 Agent Workflow

New scenarios (no cases yet)    →    s07 Function Calling
                                     s08 Multilingual
                                     s09 Long Context
                                     s10 Prompt Chains
                                     s11 Few-shot Examples
```

## Priority Definitions

- **P0**: Pilot customer critical. Must score well before launch.
- **P1**: Important for product-market fit. Can iterate after initial launch.
- **P2**: Nice to have. Future expansion.

## Approach

```
Incoming prompt → Auto-classify scenario → Route to specialized compressor → Evaluate against scenario-specific red lines
```

Each scenario will eventually have its own compression strategy (or even distilled model). For now, running the generic LLMLingua-2 across all scenarios tells us where the gaps are.

## Case Creation Roadmap

| Phase | Scenarios | Total New Cases |
|-------|-----------|----------------|
| Phase 1 | s07 Function Calling, s09 Long Context | 30-35 |
| Phase 2 | s10 Prompt Chains, s11 Few-shot | 20 |
| Phase 3 | s08 Multilingual | 15 |

Target: **165 total cases** (100 existing + 65 new)

## Running Benchmarks

```bash
# Run all scenarios
python -m compressbench.cli run --method llmlingua2 --rates 0.25 0.50 0.70

# Check per-scenario scores
python -m compressbench.cli report --group-by category
```
