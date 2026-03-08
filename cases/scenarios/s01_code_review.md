---
id: s01_code_review
name: Code Review & Debugging
category_map: [code_context]
case_ids: [cb_001, cb_002, cb_003, cb_004, cb_005, cb_006, cb_007, cb_008, cb_009, cb_010, cb_011, cb_012, cb_013, cb_014, cb_015, cb_016, cb_017, cb_018, cb_019, cb_020, cb_021, cb_022, cb_023, cb_024, cb_025]
priority: P0
current_score: null
---

# Code Review & Debugging

## What Is This Scenario

Developer pastes code into LLM for review, debugging, or refactoring. The prompt contains function definitions, class structures, variable names, error messages, and stack traces. This is the #1 use case for coding assistants like OpenClaw, Cursor, Copilot.

## Example Prompt

```
Review this authentication middleware for security issues:

class AuthMiddleware:
    def __init__(self, secret_key, algorithm="HS256"):
        self.secret = secret_key
        self.algo = algorithm
        self.max_attempts = 5
        self.lockout_duration = 900

    def validate_token(self, token: str) -> dict:
        payload = jwt.decode(token, self.secret, algorithms=[self.algo])
        if payload["exp"] < time.time():
            raise TokenExpired(f"Token expired at {payload['exp']}")
        return payload
```

## Compression Red Lines

- [ ] **Function/class names** — `validate_token`, `AuthMiddleware` must survive intact
- [ ] **Variable names** — `secret_key`, `max_attempts`, `lockout_duration` (LLM needs exact names to reference)
- [ ] **Numeric constants** — `5`, `900`, `"HS256"` (changing these changes the meaning)
- [ ] **Error messages** — `"Token expired at"` (LLM needs to see what user sees)
- [ ] **Code structure** — indentation, class hierarchy, function signatures
- [ ] **Import relationships** — what depends on what

## Compression Opportunities

- Docstrings and inline comments (LLM can infer intent from code)
- Blank lines between methods
- Type hint verbosity (e.g., `Optional[Dict[str, Any]]` → shorter)
- Redundant `self.` chains if context is obvious
- Long variable names that repeat (e.g., `authentication_manager` mentioned 20x)

## Grading Criteria

| Metric | Weight | Red Line | Description |
|--------|--------|----------|-------------|
| critical_unit_recall | 40% | >= 0.95 | All function/variable/class names preserved |
| task_accuracy | 30% | >= 0.85 | Downstream QA still answerable after compression |
| code_structure | 20% | >= 0.90 | Indentation, blocks, signatures intact |
| token_savings | 10% | >= 15% | Meaningful compression achieved |

## Current Status

- **Cases**: 25 cases (cb_001 — cb_025)
- **Avg tokens**: 460
- **Structure**: 96% have code blocks, 40% have lists, 36% have headers
- **Critical units**: mostly `function`, `variable`, `number`, `class`
- **Current Score**: Not yet benchmarked
- **Known Issues**: LLMLingua-2 may break indentation, shorten variable names
- **Recommended Strategy**: Conservative compression, protect all identifiers

## Notes

Sam's feedback: "Compression log flights was kinda harder to read too" — likely refers to code output losing structure. This scenario is critical to get right for developer-facing products.
