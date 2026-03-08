"""Base compressor adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..schemas import CompressResult


class CompressorAdapter(ABC):
    """Abstract base class for compression methods."""

    name: str = "base"

    @abstractmethod
    def compress(self, text: str, rate: float) -> CompressResult:
        """Compress text to the target rate.

        Args:
            text: input text to compress
            rate: target compression rate (0.0–1.0, where 0.25 means
                  keep ~25% of tokens)

        Returns:
            CompressResult with original and compressed text + metadata.
        """
        ...

    def health_check(self) -> bool:
        """Check if the adapter is ready to use."""
        return True
