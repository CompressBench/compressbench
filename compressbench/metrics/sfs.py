"""SFS — Structural Fidelity Score.

Checks whether structural elements are preserved after compression:
- Code block boundaries (```)
- List hierarchy (-, *, 1.)
- Section headers (#, ##, ...)
- JSON/YAML validity
- Table rows (|...|)
- Chat turn boundaries (role markers)

    SFS = weighted structural match score
"""

from __future__ import annotations

import json
import re
from typing import Any

from ..schemas import StructureLabels


def _count_code_blocks(text: str) -> int:
    """Count matched ``` pairs."""
    return text.count('```') // 2


def _count_headers(text: str) -> int:
    return sum(1 for line in text.split('\n')
               if line.strip().startswith('#'))


def _count_list_items(text: str) -> int:
    count = 0
    for line in text.split('\n'):
        s = line.strip()
        if re.match(r'^[-*+]\s', s) or re.match(r'^\d+\.\s', s):
            count += 1
    return count


def _count_table_rows(text: str) -> int:
    return sum(1 for line in text.split('\n')
               if '|' in line and line.strip().count('|') >= 2)


def _count_chat_turns(text: str) -> int:
    """Count role markers like 'user:', 'assistant:', 'system:', 'tool:'."""
    markers = re.findall(
        r'(?:^|\n)\s*(?:user|assistant|system|tool|human|ai)\s*:',
        text, re.IGNORECASE,
    )
    return len(markers)


def _json_valid(text: str) -> bool:
    """Check if text contains valid JSON blocks."""
    # Try the whole text
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        pass
    # Try code blocks
    for block in re.findall(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL):
        try:
            json.loads(block.strip())
            return True
        except (json.JSONDecodeError, ValueError):
            continue
    return False


def _structure_score(
    orig_count: int,
    comp_count: int,
) -> float:
    """Score how well a structural element count is preserved."""
    if orig_count == 0:
        return 1.0  # nothing to preserve
    if comp_count == 0:
        return 0.0  # all lost
    return min(comp_count / orig_count, 1.0)


def compute_sfs(
    original: str,
    compressed: str,
    labels: StructureLabels | None = None,
) -> float:
    """Compute Structural Fidelity Score.

    If labels are provided, only checks the relevant structures.
    Otherwise auto-detects structures from the original text.

    Args:
        original: original text
        compressed: compressed text
        labels: optional StructureLabels from the case

    Returns:
        SFS in [0, 1].
    """
    scores: list[tuple[float, float]] = []  # (weight, score)

    # Determine which structures to check
    check_code = labels.has_code_block if labels else _count_code_blocks(original) > 0
    check_list = labels.has_list if labels else _count_list_items(original) > 0
    check_headers = labels.has_headers if labels else _count_headers(original) > 0
    check_json = labels.has_json if labels else False
    check_table = labels.has_table if labels else _count_table_rows(original) > 0
    check_chat = labels.has_chat_turns if labels else _count_chat_turns(original) > 0

    if check_code:
        scores.append((2.0, _structure_score(
            _count_code_blocks(original), _count_code_blocks(compressed))))

    if check_headers:
        scores.append((1.5, _structure_score(
            _count_headers(original), _count_headers(compressed))))

    if check_list:
        scores.append((1.0, _structure_score(
            _count_list_items(original), _count_list_items(compressed))))

    if check_table:
        scores.append((1.5, _structure_score(
            _count_table_rows(original), _count_table_rows(compressed))))

    if check_chat:
        scores.append((2.0, _structure_score(
            _count_chat_turns(original), _count_chat_turns(compressed))))

    if check_json:
        orig_valid = _json_valid(original)
        comp_valid = _json_valid(compressed)
        if orig_valid:
            scores.append((2.0, 1.0 if comp_valid else 0.0))

    if not scores:
        return 1.0  # no structure to check

    total_weight = sum(w for w, _ in scores)
    weighted_sum = sum(w * s for w, s in scores)
    return weighted_sum / total_weight
