"""RS — Robustness Score.

Measures consistency of compression quality across perturbations
of the same input (rewording, reordering, noise injection, different rates).

    RS = 1 - normalized_variance

Phase 2 — stub implementation for now.
"""

from __future__ import annotations

from typing import Sequence


def compute_rs(scores: Sequence[float]) -> float:
    """Compute Robustness Score from a list of per-perturbation scores.

    Args:
        scores: CBv2 or TRS scores across perturbations of the same case.

    Returns:
        RS in [0, 1]. Higher means more robust (less variance).
        Returns 1.0 if fewer than 2 scores provided.
    """
    if len(scores) < 2:
        return 1.0

    mean = sum(scores) / len(scores)
    if mean <= 0:
        return 0.0

    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    # Normalize variance by mean^2 to get coefficient of variation squared
    cv_sq = variance / (mean ** 2)

    # RS = 1 - sqrt(cv_sq), clamped to [0, 1]
    import math
    rs = 1.0 - math.sqrt(cv_sq)
    return max(0.0, min(1.0, rs))
