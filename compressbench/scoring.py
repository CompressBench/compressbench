"""CBv2 scoring formula — multiplicative gating.

    CBv2 = 100 * TRS^0.50 * CIR^0.20 * SPS^0.10 * SFS^0.10 * CES^0.10

Hard constraints:
    - TRS < 0.85 → score * 0.5 penalty
    - CIR < 0.80 → flagged as information-lossy (no penalty, just flag)
    - Structure required but output invalid → case score = 0
"""

from __future__ import annotations


def compute_cbv2(
    trs: float,
    cir: float,
    sps: float,
    sfs: float,
    ces: float,
    structure_required: bool = False,
    structure_valid: bool = True,
) -> tuple[float, list[str]]:
    """Compute CBv2 composite score.

    Args:
        trs: Task Retention Score [0, 1]
        cir: Critical Information Recall [0, 1]
        sps: Semantic Preservation Score [0, 1]
        sfs: Structural Fidelity Score [0, 1]
        ces: Compression Efficiency Score [0, 1]
        structure_required: whether the case requires structural fidelity
        structure_valid: whether the compressed output has valid structure

    Returns:
        (cbv2_score, flags) where flags is a list of warning strings.
    """
    flags: list[str] = []

    # Hard constraint: structure required but invalid → 0
    if structure_required and not structure_valid:
        flags.append("STRUCTURE_INVALID")
        return 0.0, flags

    # Clamp inputs to [0, 1]
    trs = max(0.0, min(1.0, trs))
    cir = max(0.0, min(1.0, cir))
    sps = max(0.0, min(1.0, sps))
    sfs = max(0.0, min(1.0, sfs))
    ces = max(0.0, min(1.0, ces))

    # Avoid 0^exponent issues
    eps = 1e-9

    score = 100.0 * (
        (trs + eps) ** 0.50
        * (cir + eps) ** 0.20
        * (sps + eps) ** 0.10
        * (sfs + eps) ** 0.10
        * (ces + eps) ** 0.10
    )

    # Hard constraint: TRS < 0.85 → 50% penalty
    if trs < 0.85:
        score *= 0.5
        flags.append("TRS_LOW")

    # Flag: CIR < 0.80 → information-lossy
    if cir < 0.80:
        flags.append("CIR_LOSSY")

    return round(score, 4), flags


def aggregate_cbv2_across_rates(
    cbv2_by_rate: dict[float, float],
) -> float:
    """Compute final CBv2 as mean across rates.

    Args:
        cbv2_by_rate: mapping of rate → CBv2 score

    Returns:
        CBv2_final = mean(CBv2@rate1, CBv2@rate2, ...)
    """
    if not cbv2_by_rate:
        return 0.0
    return sum(cbv2_by_rate.values()) / len(cbv2_by_rate)
