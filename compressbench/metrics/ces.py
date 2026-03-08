"""CES — Compression Efficiency Score.

Combines token savings, throughput, and latency into a single efficiency score.

    CES = 0.7 * token_saving + 0.2 * throughput_norm + 0.1 * (1 - latency_norm)

Normalization references:
- token_saving: (orig - comp) / orig, in [0, 1]
- throughput_norm: tokens/sec normalized against reference (10000 tok/s = 1.0)
- latency_norm: ms normalized against reference (5000 ms = 1.0, capped)
"""

from __future__ import annotations


# Reference values for normalization
_THROUGHPUT_REF = 10_000.0   # tokens/sec for score=1.0
_LATENCY_REF = 5_000.0       # ms for score=1.0 (worst acceptable)


def compute_ces(
    original_tokens: int,
    compressed_tokens: int,
    compression_ms: float,
) -> float:
    """Compute Compression Efficiency Score.

    Args:
        original_tokens: token count before compression
        compressed_tokens: token count after compression
        compression_ms: wall-clock compression time in milliseconds

    Returns:
        CES in [0, 1].
    """
    # Token saving ratio
    if original_tokens <= 0:
        token_saving = 0.0
    else:
        token_saving = max(0.0, (original_tokens - compressed_tokens) / original_tokens)

    # Throughput normalized
    if compression_ms <= 0:
        throughput_norm = 1.0  # instant = perfect
    else:
        tps = original_tokens / (compression_ms / 1000.0)
        throughput_norm = min(tps / _THROUGHPUT_REF, 1.0)

    # Latency normalized (lower is better)
    latency_norm = min(compression_ms / _LATENCY_REF, 1.0)

    ces = (0.7 * token_saving
           + 0.2 * throughput_norm
           + 0.1 * (1.0 - latency_norm))
    return max(0.0, min(1.0, ces))
