---
id: s10_prompt_chain
name: Prompt Chains & Multi-step Instructions
category_map: []
case_ids: []
priority: P1
current_score: null
---

# Prompt Chains & Multi-step Instructions

## What Is This Scenario

Prompts containing sequential instructions where each step depends on the previous one. If compression removes or reorders a step, the entire chain breaks. Common in workflow automation, data pipelines, and complex agent tasks.

## Example Prompt

```
Process this customer refund request by following these steps exactly:

Step 1: Verify the order exists by calling lookup_order(order_id="ORD-9921")
Step 2: Check if the order is within the 30-day refund window
Step 3: If eligible, calculate refund amount:
   - Full refund if item is unopened
   - 80% refund if item is opened but undamaged
   - 50% refund if item is damaged
Step 4: Create a refund ticket with create_refund(order_id, amount, reason)
Step 5: Send confirmation email to customer with the refund timeline (3-5 business days)
Step 6: Log the interaction in the CRM

IMPORTANT: Do NOT skip any steps. Do NOT process refund if order is older than 30 days.
```

## Compression Red Lines

- [ ] **Step ordering** — Step 1 before Step 2 before Step 3 (causal dependency)
- [ ] **All steps present** — removing Step 4 means no refund gets created
- [ ] **Conditional branches** — "if unopened: 100%, if opened: 80%, if damaged: 50%"
- [ ] **Exact percentages and numbers** — `80%`, `50%`, `30-day`, `3-5 business days`
- [ ] **Negation constraints** — "Do NOT skip", "Do NOT process"
- [ ] **Function call references** — `lookup_order`, `create_refund`

## Compression Opportunities

- Verbose step descriptions when the action is self-evident
- Repeated phrasing across steps ("make sure to", "please ensure")
- Background context explaining why each step exists
- Examples that illustrate but don't define the steps

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| step_completeness | 35% | 100% | All steps present after compression |
| step_ordering | 25% | 100% | Order preserved |
| critical_unit_recall | 25% | >= 0.95 | Numbers, conditions, function names intact |
| token_savings | 15% | >= 15% | Moderate savings expected |

## Current Status

- **Cases**: 0 — needs new cases
- **Target**: 10 cases:
  - 5 cases with linear chains (3-8 steps)
  - 3 cases with branching logic (if/else paths)
  - 2 cases with loops/retries ("repeat until success")
- **Current Score**: N/A
- **Recommended Strategy**: Detect numbered/ordered lists and imperative sentences; protect step structure and ordering

## Notes

Prompt chains are the backbone of agentic workflows. Every AI agent platform (LangChain, CrewAI, OpenClaw) builds multi-step pipelines. If compression drops a step, the agent silently produces wrong results — no error, just wrong output. This makes failures hard to debug.
