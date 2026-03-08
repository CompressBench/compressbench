"""CIR — Critical Information Recall.

Measures recall of pre-annotated critical information units in the
compressed output.

    CIR = recalled_units / total_units

Each case has critical_units like:
    {"type": "function", "value": "parse_config"}
    {"type": "number", "value": "4096"}
    {"type": "flag", "value": "--strict"}
    {"type": "constraint", "value": "timeout must be < 30s"}

Matching uses case-insensitive substring search for most types,
and fuzzy matching for constraints.
"""

from __future__ import annotations

import re
from typing import Sequence

from ..schemas import CriticalUnit


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return re.sub(r'\s+', ' ', text.lower().strip())


def _unit_recalled(unit: CriticalUnit, compressed: str) -> bool:
    """Check if a single critical unit is present in compressed text."""
    value = unit.value.strip()
    compressed_lower = compressed.lower()

    if unit.type in ("function", "class", "variable", "module"):
        # Exact identifier match (case-sensitive for code)
        return value in compressed

    if unit.type == "number":
        # Number can appear in various formats
        return value in compressed

    if unit.type in ("flag", "option", "command"):
        # Flags are case-sensitive
        return value in compressed

    if unit.type in ("url", "path", "file"):
        return value in compressed

    if unit.type == "constraint":
        # Fuzzy: check if key terms from the constraint appear
        terms = [t for t in re.split(r'\W+', value.lower()) if len(t) > 2]
        if not terms:
            return value.lower() in compressed_lower
        matched = sum(1 for t in terms if t in compressed_lower)
        return matched >= len(terms) * 0.7

    if unit.type == "entity":
        return value.lower() in compressed_lower

    # Default: case-insensitive substring
    return value.lower() in compressed_lower


def compute_cir(
    critical_units: Sequence[CriticalUnit],
    compressed_text: str,
) -> float:
    """Compute Critical Information Recall.

    Args:
        critical_units: list of CriticalUnit from the case
        compressed_text: the compressed text to check against

    Returns:
        CIR in [0, 1]. Returns 1.0 if there are no critical units.
    """
    if not critical_units:
        return 1.0

    recalled = sum(1 for u in critical_units
                   if _unit_recalled(u, compressed_text))
    return recalled / len(critical_units)
