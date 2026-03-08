---
id: s07_function_calling
name: Function Calling & Tool Use
category_map: []
case_ids: []
priority: P0
current_score: null
---

# Function Calling & Tool Use

## What Is This Scenario

System prompts containing tool/function definitions in JSON Schema format. The LLM uses these schemas to decide which tool to call and how to format arguments. If compression corrupts the schema, tool calls fail silently or with wrong parameters.

## Example Prompt

```
You have access to the following tools:

{
  "type": "function",
  "function": {
    "name": "search_orders",
    "description": "Search customer orders by various filters",
    "parameters": {
      "type": "object",
      "properties": {
        "customer_id": {"type": "string", "description": "Customer UUID"},
        "status": {"type": "string", "enum": ["pending", "shipped", "delivered", "cancelled"]},
        "date_range": {
          "type": "object",
          "properties": {
            "start": {"type": "string", "format": "date"},
            "end": {"type": "string", "format": "date"}
          }
        },
        "min_total": {"type": "number", "minimum": 0}
      },
      "required": ["customer_id"]
    }
  }
}

User: Show me all pending orders for customer abc-123 from last month.
```

## Compression Red Lines

- [ ] **Function/tool names** — `search_orders` must be exact (LLM generates this in tool_call)
- [ ] **Parameter names** — `customer_id`, `date_range`, `min_total` (LLM builds JSON args with these)
- [ ] **Type annotations** — `"type": "string"`, `"type": "number"` (wrong type = API error)
- [ ] **Enum values** — `["pending", "shipped", "delivered", "cancelled"]` (must be complete list)
- [ ] **Required fields** — `"required": ["customer_id"]` (LLM needs to know what's mandatory)
- [ ] **JSON Schema structure** — nesting, `properties`, `$ref` links

## Compression Opportunities

- Verbose `description` fields (LLM often ignores them for well-named parameters)
- Repeated schema patterns across multiple tools
- Tool definitions for tools not relevant to the current query
- Natural language instructions around the tool definitions

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| schema_validity | 35% | 100% | Tool schema must parse as valid JSON Schema |
| tool_name_recall | 25% | 100% | All function names preserved exactly |
| param_recall | 25% | >= 0.95 | Parameter names, types, enums, required intact |
| token_savings | 15% | >= 15% | Modest savings acceptable |

## Current Status

- **Cases**: 0 — needs new cases
- **Target**: 15-20 cases covering single tool, multi-tool, nested params, enums
- **Current Score**: N/A
- **Recommended Strategy**: Detect JSON Schema blocks and protect entirely; compress surrounding natural language only

## Notes

Function calling is becoming standard across all major LLM providers. OpenAI, Anthropic, Google all support it. If compression breaks tool schemas, the entire agentic workflow fails. This is table stakes for enterprise adoption.
