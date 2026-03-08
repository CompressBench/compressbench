"""Generic HTTP compression adapter.

Works with any endpoint that accepts POST JSON:
    {"text": "...", "rate": 0.5}
and returns:
    {"compressed_text": "...", "original_tokens": N, "compressed_tokens": M}
"""

from __future__ import annotations

import json
import time
from typing import Any
from urllib import error, request

from .base import CompressorAdapter
from ..schemas import CompressResult


class HttpAdapter(CompressorAdapter):
    """Generic HTTP adapter for any /compress endpoint."""

    name = "http"

    def __init__(
        self,
        endpoint: str,
        timeout: float = 120.0,
        headers: dict[str, str] | None = None,
    ):
        self.endpoint = endpoint
        self.timeout = timeout
        self.headers = headers or {}

    def compress(self, text: str, rate: float) -> CompressResult:
        payload = json.dumps({
            "text": text,
            "rate": rate,
        }).encode("utf-8")

        req_headers = {
            "Content-Type": "application/json",
            **self.headers,
        }
        req = request.Request(
            self.endpoint,
            data=payload,
            headers=req_headers,
            method="POST",
        )

        t0 = time.perf_counter()
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            ms = (time.perf_counter() - t0) * 1000

            compressed = body.get("compressed_text", text)
            orig_tokens = body.get("original_tokens", len(text.split()))
            comp_tokens = body.get("compressed_tokens", len(compressed.split()))

            return CompressResult(
                original_text=text,
                compressed_text=compressed,
                original_tokens=orig_tokens,
                compressed_tokens=comp_tokens,
                rate_requested=rate,
                rate_applied=body.get("rate_applied", rate),
                compression_ms=body.get("compression_ms", ms),
                method=self.name,
            )
        except Exception as e:
            ms = (time.perf_counter() - t0) * 1000
            return CompressResult(
                original_text=text,
                compressed_text=text,
                original_tokens=len(text.split()),
                compressed_tokens=len(text.split()),
                rate_requested=rate,
                rate_applied=1.0,
                compression_ms=ms,
                method=self.name,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            # Try a GET or small POST to see if endpoint is up
            req = request.Request(self.endpoint, method="GET")
            with request.urlopen(req, timeout=5):
                return True
        except Exception:
            return False
