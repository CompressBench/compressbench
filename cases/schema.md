# CompressBench Case Schema

Each case is a single JSON object (one per line in JSONL format).

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique case ID, format: `cb_NNN` |
| `category` | string | yes | One of: `code_context`, `chat_history`, `structured_data`, `documentation`, `mixed` |
| `input_text` | string | yes | The full text to be compressed |
| `original_tokens` | int | yes | Word-split token count of input_text |
| `task` | object | yes | Downstream evaluation task |
| `critical_units` | array | yes | Critical information units to preserve |
| `structure_labels` | object | yes | Structural annotations |

## Task Object

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | `multiple_choice_qa`, `extraction`, or `free_form` |
| `question` | string | The evaluation question |
| `gold` | string | Correct answer |
| `choices` | array | MCQ choices (required for `multiple_choice_qa`) |

## Critical Unit Object

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | `function`, `class`, `number`, `flag`, `constraint`, `entity`, `url`, `path`, `variable` |
| `value` | string | The literal value to check for |

## Structure Labels Object

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `has_code_block` | bool | false | Contains ``` code blocks |
| `has_list` | bool | false | Contains bullet/numbered lists |
| `has_json` | bool | false | Contains JSON data |
| `has_yaml` | bool | false | Contains YAML data |
| `has_table` | bool | false | Contains markdown tables |
| `has_headers` | bool | false | Contains # headers |
| `has_chat_turns` | bool | false | Contains role: markers |

## Category Distribution (100 cases)

- `code_context`: 25 cases
- `chat_history`: 25 cases
- `structured_data`: 20 cases
- `documentation`: 20 cases
- `mixed`: 10 cases

## Split

- **dev**: 30 cases (public, with gold answers)
- **test**: 70 cases (gold answers hidden for leaderboard)

## Example

```json
{
  "id": "cb_001",
  "category": "code_context",
  "input_text": "def parse_config(path):\n    ...",
  "original_tokens": 250,
  "task": {
    "type": "multiple_choice_qa",
    "question": "Which function handles config parsing?",
    "choices": ["parse_config", "load_settings", "read_yaml", "init_config"],
    "gold": "parse_config"
  },
  "critical_units": [
    {"type": "function", "value": "parse_config"},
    {"type": "number", "value": "4096"},
    {"type": "flag", "value": "--strict"}
  ],
  "structure_labels": {
    "has_code_block": true,
    "has_list": false,
    "has_json": true,
    "has_yaml": false,
    "has_table": false,
    "has_headers": false,
    "has_chat_turns": false
  }
}
```
