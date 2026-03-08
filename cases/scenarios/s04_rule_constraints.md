---
id: s04_rule_constraints
name: System Prompts with Rules & Constraints
category_map: [documentation]
case_ids: [cb_071, cb_072, cb_073, cb_074, cb_075, cb_076, cb_077, cb_078, cb_079, cb_080, cb_081, cb_082, cb_083, cb_084, cb_085, cb_086, cb_087, cb_088, cb_089, cb_090]
priority: P0
current_score: null
---

# System Prompts with Rules & Constraints

## What Is This Scenario

Long system prompts containing setup instructions, configuration docs, behavioral rules, and constraints. At higher compression rates, context and rules get lost — if a rule like "never reveal pricing" gets compressed away, the model violates it.

## Example Prompt

```
# Customer Support Agent Configuration

## Rules
1. NEVER share internal pricing or cost breakdowns with customers
2. Always verify customer identity before accessing account data
3. Escalate to human agent if customer mentions "legal action" or "lawyer"
4. Response must be under 200 words
5. Use formal tone, no emojis

## Knowledge Base
- Refund policy: 30 days for physical items, 14 days for digital
- Premium support SLA: 4 hour response time
- Port 8443 is for internal API only, never share with customers

## Available Tools
- lookup_customer(email: str) -> CustomerRecord
- create_ticket(priority: str, description: str) -> TicketID
- check_order_status(order_id: str) -> OrderStatus
```

## Compression Red Lines

- [ ] **Behavioral rules** — "NEVER share internal pricing", "Escalate to human" — these are safety-critical
- [ ] **Exact thresholds** — "30 days", "14 days", "4 hour", "200 words"
- [ ] **Negations** — "NEVER", "do not", "must not" — removing negation reverses meaning
- [ ] **Tool signatures** — function names and parameter types
- [ ] **Conditional triggers** — "if customer mentions 'legal action'" — the trigger condition
- [ ] **Priority markers** — MUST, NEVER, ALWAYS, REQUIRED

## Compression Opportunities

- Verbose explanations of well-known concepts
- Repeated section headers and formatting
- Detailed examples when the rule itself is clear
- Background context that doesn't affect behavior
- Changelog / version history sections

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| constraint_retention | 40% | >= 0.95 | All rules/constraints preserved verbatim |
| critical_unit_recall | 25% | >= 0.95 | Numbers, thresholds, tool names intact |
| task_accuracy | 25% | >= 0.90 | Downstream task still correct |
| token_savings | 10% | >= 10% | Even modest savings OK — safety first |

## Current Status

- **Cases**: 20 cases (cb_071 — cb_090)
- **Avg tokens**: 491
- **Structure**: 100% have lists, 100% have headers, 95% have tables, 90% have code blocks
- **Critical units**: mostly `entity`, `number`, `command`, `url`
- **Current Score**: Not yet benchmarked
- **Known Issues**: LLMLingua-2 treats all tokens equally — rules and filler have same compression probability
- **Recommended Strategy**: Detect constraint/rule sentences (contains MUST/NEVER/ALWAYS, numbered rules) and whitelist them from compression

## Notes

This is the most dangerous scenario to get wrong. A compressed-away rule can cause the model to leak data, violate policies, or behave unsafely. For enterprise customers, this is a trust issue. Consider a "rule-aware" mode that parses imperative sentences and protects them. Bot777's hierarchical keep/drop rules work (`train/rules/hierarchical_rules_v1.yaml`) is directly relevant here.
