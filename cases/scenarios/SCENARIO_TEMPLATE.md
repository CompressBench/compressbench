---
id: s00_name
name: Scenario Display Name
category_map: [code_context]       # which CompressBench categories this covers
case_ids: [cb_001, cb_002]         # specific case IDs from openclaw_v1.jsonl
priority: P0                       # P0 = pilot customer critical, P1 = important, P2 = nice to have
current_score: null                # fill after benchmark run
---

# Scenario Template

## What Is This Scenario

{1-2 sentence description of the real-world use case. Who uses it, when, why.}

## Example Prompt

{A short representative example showing what prompts in this scenario look like.}

## Compression Red Lines

What MUST be preserved after compression — if any of these break, compression is a failure for this scenario.

- [ ] Red line 1
- [ ] Red line 2
- [ ] Red line 3

## Compression Opportunities

What CAN be safely removed or shortened.

- Opportunity 1
- Opportunity 2

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| metric_name | 30% | >= 0.90 | What it measures |

## Current Status

- **Cases**: N cases in openclaw_v1.jsonl
- **Current Score**: Not yet benchmarked
- **Known Issues**: None yet
- **Recommended Strategy**: default / custom

## Notes

{Any additional context, edge cases, customer feedback.}
