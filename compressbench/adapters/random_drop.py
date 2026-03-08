"""Baseline adapter: random token drop."""

from __future__ import annotations

import random
import time

from .base import CompressorAdapter
from ..schemas import CompressResult


class RandomDropAdapter(CompressorAdapter):
    """Randomly drops tokens to achieve the target rate.

    This is a weak baseline — any real compressor should beat it.
    """

    name = "random_drop"

    def __init__(self, seed: int = 42):
        self.seed = seed

    def compress(self, text: str, rate: float) -> CompressResult:
        t0 = time.perf_counter()
        words = text.split()
        n_keep = max(1, int(len(words) * rate))

        rng = random.Random(self.seed)
        kept_indices = sorted(rng.sample(range(len(words)),
                                          min(n_keep, len(words))))
        compressed = " ".join(words[i] for i in kept_indices)
        ms = (time.perf_counter() - t0) * 1000

        return CompressResult(
            original_text=text,
            compressed_text=compressed,
            original_tokens=len(words),
            compressed_tokens=len(kept_indices),
            rate_requested=rate,
            rate_applied=len(kept_indices) / max(1, len(words)),
            compression_ms=ms,
            method=self.name,
        )
