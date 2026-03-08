"""Baseline adapter: truncation (keep first N tokens)."""

from __future__ import annotations

import time

from .base import CompressorAdapter
from ..schemas import CompressResult


class TruncationAdapter(CompressorAdapter):
    """Truncates text to keep only the first N tokens.

    This is a weak baseline — real compressors should preserve
    information across the full text, not just the beginning.
    """

    name = "truncation"

    def compress(self, text: str, rate: float) -> CompressResult:
        t0 = time.perf_counter()
        words = text.split()
        n_keep = max(1, int(len(words) * rate))
        compressed = " ".join(words[:n_keep])
        ms = (time.perf_counter() - t0) * 1000

        return CompressResult(
            original_text=text,
            compressed_text=compressed,
            original_tokens=len(words),
            compressed_tokens=n_keep,
            rate_requested=rate,
            rate_applied=n_keep / max(1, len(words)),
            compression_ms=ms,
            method=self.name,
        )
