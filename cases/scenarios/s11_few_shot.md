---
id: s11_few_shot
name: Few-shot Examples
category_map: []
case_ids: []
priority: P1
current_score: null
---

# Few-shot Examples

## What Is This Scenario

Prompts containing 2-10 input/output examples that teach the LLM a specific pattern or format. Few-shot prompting is one of the most common prompt engineering techniques. If compression removes examples or corrupts the pattern, the LLM reverts to zero-shot behavior and output quality drops significantly.

## Example Prompt

```
Classify the following customer feedback as positive, negative, or neutral.

Example 1:
Input: "The delivery was super fast and the product works great!"
Output: positive

Example 2:
Input: "Took 3 weeks to arrive and the box was damaged"
Output: negative

Example 3:
Input: "It's okay, does what it's supposed to do"
Output: neutral

Example 4:
Input: "Absolutely love it, already ordered two more for friends"
Output: positive

Now classify:
Input: "The return process was a nightmare, took 5 calls to resolve"
Output:
```

## Compression Red Lines

- [ ] **Example count** — if prompt has 5 examples, compressed version must keep all 5 (or at minimum 3)
- [ ] **Input/output pairing** — each example's input must stay paired with its correct output
- [ ] **Output format** — the exact format shown in examples (LLM mimics it)
- [ ] **Edge case examples** — examples showing unusual or boundary cases are highest value
- [ ] **The actual query** — the final input that needs classification

## Compression Opportunities

- Redundant examples that demonstrate the same pattern (e.g., 3 positive examples when 1 suffices)
- Verbose example inputs when the pattern is already clear
- Natural language instructions that restate what the examples already show
- Whitespace and formatting between examples

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| example_count | 30% | >= 60% | At least 60% of examples preserved |
| format_preservation | 25% | 100% | Input/output pairing and format intact |
| task_accuracy | 25% | >= 0.85 | LLM still produces correct output |
| token_savings | 20% | >= 20% | Few-shot prompts are repetitive |

## Current Status

- **Cases**: 0 — needs new cases
- **Target**: 10 cases:
  - 3 cases: classification tasks (sentiment, category, intent)
  - 3 cases: extraction tasks (entities, dates, amounts from text)
  - 2 cases: format transformation (CSV→JSON, text→SQL)
  - 2 cases: code generation with examples
- **Current Score**: N/A
- **Recommended Strategy**: Detect example patterns (numbered, labeled input/output pairs); compress within examples but never drop entire examples

## Notes

Few-shot is interesting because there's real compression opportunity — if you have 5 examples showing the same pattern, compressing the verbose ones while keeping the diverse ones is smart. But naive token-level compression doesn't understand "this is an example boundary" and may merge or corrupt examples. A structure-aware approach would treat each example as an atomic unit.
