"""TRS — Task Retention Score.

Measures whether the downstream model can still complete the task
after compression.

    TRS = Score(compressed_prompt) / Score(original_prompt)

For MCQ and extraction tasks, Score is binary (0 or 1).
For free_form tasks, Score comes from an LLM judge (0.0–1.0).
"""

from __future__ import annotations

from ..schemas import Case, CaseResult


def compute_trs(
    original_score: float,
    compressed_score: float,
) -> float:
    """Compute Task Retention Score.

    Args:
        original_score: task score with original (uncompressed) prompt (0–1)
        compressed_score: task score with compressed prompt (0–1)

    Returns:
        TRS in [0, 1]. If original_score is 0, returns compressed_score
        directly (degenerate case).
    """
    if original_score <= 0:
        return compressed_score
    return min(compressed_score / original_score, 1.0)
