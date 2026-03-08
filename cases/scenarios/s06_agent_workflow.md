---
id: s06_agent_workflow
name: Agent Task Logs & Multi-step Workflows
category_map: [mixed]
case_ids: [cb_091, cb_092, cb_093, cb_094, cb_095, cb_096, cb_097, cb_098, cb_099, cb_100]
priority: P1
current_score: null
---

# Agent Task Logs & Multi-step Workflows

## What Is This Scenario

AI agent execution logs containing tool calls, intermediate results, error traces, and multi-step reasoning. The context includes a mix of code, JSON, natural language, and structured data. This is what OpenClaw, Cursor, and similar coding agents generate internally.

## Example Prompt

```
## Agent Task Log: Database Migration Debugging
**Session ID**: agent-run-4482
**Started**: 2026-02-18T14:23:07Z

### Step 1: Analyze error
Tool: read_file("migrations/003_add_indexes.sql")
Result: CREATE INDEX idx_orders_user ON orders(user_id);

### Step 2: Run migration
Tool: execute_sql("migrations/003_add_indexes.sql")
Error: PSQLException: relation "orders" does not exist

### Step 3: Check table state
Tool: execute_sql("SELECT tablename FROM pg_tables WHERE schemaname='public'")
Result: ["users", "products", "order_items"]

Diagnosis: Table is named "order_items", not "orders". Migration references wrong table name.
```

## Compression Red Lines

- [ ] **Tool names and arguments** — `read_file("migrations/003_add_indexes.sql")`
- [ ] **Error messages** — exact error text for debugging
- [ ] **Step sequence** — order of operations matters for understanding causality
- [ ] **Final diagnosis/conclusion** — the key insight
- [ ] **SQL/code snippets** — exact queries and commands

## Compression Opportunities

- Verbose intermediate reasoning that didn't lead anywhere
- Repeated tool call patterns (same tool structure, different args)
- Agent's self-talk ("Let me think about this...", "I'll try another approach")
- Timestamp and metadata boilerplate
- Large tool results that were inspected but not relevant to the conclusion

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| task_accuracy | 35% | >= 0.85 | Diagnosis/conclusion still extractable |
| critical_unit_recall | 30% | >= 0.90 | Tool calls, errors, SQL preserved |
| sequence_preservation | 20% | >= 0.85 | Step ordering maintained |
| token_savings | 15% | >= 20% | Agent logs are verbose |

## Current Status

- **Cases**: 10 cases (cb_091 — cb_100)
- **Avg tokens**: 535 (largest category)
- **Structure**: 100% code blocks, 100% lists, 100% headers, 70% chat turns
- **Critical units**: `number`, `entity`, `variable`, `function`, `constraint`
- **Current Score**: Not yet benchmarked
- **Known Issues**: Mixed content makes uniform compression strategy suboptimal
- **Recommended Strategy**: Hybrid — protect tool calls and errors, aggressively compress agent reasoning

## Notes

This is the most complex scenario because it mixes all content types. Also the most relevant to OpenClaw's own product — if we can compress agent context well, our own product benefits directly. Consider this a P1 priority after the P0 customer-facing scenarios.
