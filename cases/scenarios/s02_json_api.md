---
id: s02_json_api
name: JSON & Structured Output
category_map: [structured_data]
case_ids: [cb_051, cb_052, cb_053, cb_054, cb_055, cb_056, cb_057, cb_058, cb_059, cb_060, cb_061, cb_062, cb_063, cb_064, cb_065, cb_066, cb_067, cb_068, cb_069, cb_070]
priority: P0
current_score: null
---

# JSON & Structured Output

## What Is This Scenario

Prompt contains API specs, JSON schemas, config files, or instructs the LLM to respond in structured format (JSON, YAML, XML). This is Sam's #1 complaint — "If your system requires specific formatting then compress does not work."

## Example Prompt

```
Parse this API response and extract all error codes:

{
  "status": 409,
  "error": {
    "code": "DUPLICATE_IDEMPOTENCY_KEY",
    "message": "Request with idempotency_key 'pay_8x2k' already processed",
    "details": {
      "original_status": 200,
      "cached_ttl_seconds": 86400
    }
  }
}

Return result as JSON: {"errors": [{"code": "...", "status": N}]}
```

## Compression Red Lines

- [ ] **JSON structure** — all `{}`, `[]`, `""`, `:`, `,` must be preserved exactly
- [ ] **Field names** — `"idempotency_key"`, `"cached_ttl_seconds"` (keys are semantically meaningful)
- [ ] **Numeric values** — `409`, `86400`, `200` (changing numbers = wrong data)
- [ ] **Output format instructions** — "Return result as JSON" must survive
- [ ] **Nesting depth** — flattening nested JSON changes meaning
- [ ] **URL/endpoint paths** — `/v2/orders/{id}/refund` must be exact

## Compression Opportunities

- Descriptive text around the JSON (explanations, context paragraphs)
- Repeated schema patterns (e.g., 10 similar endpoint descriptions)
- Human-readable field descriptions if the schema itself is present
- Markdown formatting around the structured data

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| json_validity | 35% | 100% | All JSON in output must parse without error |
| critical_unit_recall | 30% | >= 0.95 | Field names, numbers, URLs preserved |
| task_accuracy | 25% | >= 0.85 | Extraction/QA task still correct |
| token_savings | 10% | >= 10% | Even modest savings acceptable here |

## Current Status

- **Cases**: 20 cases (cb_051 — cb_070)
- **Avg tokens**: 351
- **Structure**: 55% have JSON, 30% have YAML, 60% have lists
- **Critical units**: mostly `entity`, `number`, `url`
- **Current Score**: Not yet benchmarked
- **Known Issues**: LLMLingua-2 aggressively removes JSON delimiters, breaks structure
- **Recommended Strategy**: Detect JSON blocks and skip compression entirely; only compress surrounding natural language

## Notes

This is the scenario Sam explicitly called out. For pilot customers with API-heavy workflows, getting this wrong = deal breaker. Consider a "JSON-aware" compression mode that parses and protects structured blocks.
