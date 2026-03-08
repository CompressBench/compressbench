---
id: s08_multilingual
name: Multilingual (CJK & Non-Latin)
category_map: []
case_ids: []
priority: P1
current_score: null
---

# Multilingual (CJK & Non-Latin)

## What Is This Scenario

Prompts in Chinese, Japanese, Korean, or mixed-language content. CJK tokenization works fundamentally differently from English — each character is often a separate token, and subword boundaries don't align with word boundaries. Compression models trained primarily on English may produce garbage on CJK text.

## Example Prompt

```
你是一个客服助手。请根据以下规则回复用户：

## 规则
1. 退款政策：实物商品30天内可退，数字商品14天内可退
2. 不得透露内部定价或成本信息
3. 如果用户提到"投诉"或"律师"，立即转接人工
4. 回复不超过200字

## 用户消息
我上周买的耳机有质量问题，想退货。订单号是 ORD-2026-88431。
```

## Compression Red Lines

- [ ] **Semantic integrity** — CJK characters removed mid-word can change meaning entirely (e.g., 退款 vs 退)
- [ ] **Numbers and codes** — `ORD-2026-88431`, `30天`, `14天`, `200字`
- [ ] **Negations** — `不得` (must not), `不超过` (no more than) — removing one character reverses meaning
- [ ] **Named entities** — product names, person names, company names in CJK
- [ ] **Mixed-language content** — English terms embedded in CJK text (API names, brand names)
- [ ] **Punctuation** — CJK uses full-width punctuation; compression may corrupt encoding

## Compression Opportunities

- Honorifics and polite filler (您好, よろしくお願いします)
- Repeated contextual phrases
- Verbose explanations that can be condensed in CJK (CJK is already more information-dense per character)

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| task_accuracy | 35% | >= 0.85 | Downstream task still correct |
| critical_unit_recall | 30% | >= 0.90 | Numbers, entities, codes preserved |
| encoding_validity | 20% | 100% | No corrupted characters or broken UTF-8 |
| token_savings | 15% | >= 10% | CJK is already dense, lower savings expected |

## Current Status

- **Cases**: 0 in openclaw_v1.jsonl (5 chinese cases exist in legacy test_cases.jsonl)
- **Target**: 15 cases — 5 Chinese, 5 Japanese, 5 mixed (CJK + English)
- **Current Score**: N/A
- **Known Issues**: LLMLingua-2 (XLM-RoBERTa based) should handle multilingual, but untested on CJK at production compression rates
- **Recommended Strategy**: Test current model first; may need separate CJK-tuned compression model

## Notes

Chinese and Japanese markets are huge for LLM adoption. If we can't compress CJK prompts without corruption, we lose entire geographies. The XLM-RoBERTa backbone in LLMLingua-2 theoretically supports multilingual, but real-world performance at 50% compression is unknown.
