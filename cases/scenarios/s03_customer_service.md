---
id: s03_customer_service
name: Customer Service & Chat
category_map: [chat_history]
case_ids: [cb_026, cb_027, cb_028, cb_029, cb_030, cb_031, cb_032, cb_033, cb_034, cb_035, cb_036, cb_037, cb_038, cb_039, cb_040, cb_041, cb_042, cb_043, cb_044, cb_045, cb_046, cb_047, cb_048, cb_049, cb_050]
priority: P0
current_score: null
---

# Customer Service & Chat

## What Is This Scenario

Multi-turn conversations where a user describes a problem and an assistant helps debug/resolve it. Includes support tickets, troubleshooting dialogues, and Q&A threads. Sam said "maybe for specific applications" like "customer service response" and "feedback from a customer" — this is the sweet spot.

## Example Prompt

```
user: Our production deployment on AWS ECS failed about 30 minutes ago. The service keeps restarting. Here is the error log:

ERROR: HealthCheck failed after 3 retries. Container exited with code 137 (OOMKilled).
Memory limit: 512MB, Peak usage: 498MB.

assistant: The container is being OOM-killed. Your peak memory (498MB) is very close to the 512MB limit. Two options:
1. Increase the memory limit to 1024MB in your task definition
2. Investigate why memory usage is so high — check for memory leaks

user: We increased to 1024MB but now the startup time is 45 seconds and the health check timeout is only 30 seconds.

What was the root cause and recommended fix?
```

## Compression Red Lines

- [ ] **Error messages & codes** — `code 137`, `OOMKilled`, exact log output
- [ ] **Numbers & thresholds** — `512MB`, `498MB`, `1024MB`, `45 seconds`, `30 seconds`
- [ ] **User's original problem statement** — can't lose what they asked
- [ ] **Sequence of events** — order of troubleshooting steps matters
- [ ] **Configuration values** — specific settings mentioned (memory limit, timeout)

## Compression Opportunities

- Conversational filler ("I see", "Let me check", "Thanks for the info")
- Repeated context across turns (user re-explains the same issue)
- Verbose error stack traces (keep key lines, trim repetitive frames)
- Polite language and greetings
- Assistant's intermediate reasoning that led to dead ends

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| task_accuracy | 35% | >= 0.85 | Root cause / answer still extractable |
| critical_unit_recall | 30% | >= 0.90 | Error codes, numbers, config values preserved |
| conversation_coherence | 20% | >= 0.80 | Turn sequence still makes sense |
| token_savings | 15% | >= 25% | Chat has lots of compressible filler |

## Current Status

- **Cases**: 25 cases (cb_026 — cb_050)
- **Avg tokens**: 423
- **Structure**: 100% have chat turns, 100% have code blocks, 72% have lists
- **Critical units**: mostly `number`, `entity`, `variable`, `function`
- **Current Score**: Not yet benchmarked
- **Known Issues**: Multi-turn context may lose turn boundaries; early turns get over-compressed
- **Recommended Strategy**: Aggressive on filler/greetings, conservative on error messages and numbers

## Notes

This is the highest-ROI scenario for compression — chat history is verbose by nature with lots of repeated context across turns. Sam explicitly suggested this use case. Pilot customers in support/helpdesk will benefit most.
