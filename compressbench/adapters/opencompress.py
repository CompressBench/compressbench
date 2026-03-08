"""OpenCompress API adapter.

Calls the OpenCompress compression endpoint:
    POST /api/compress
    {"user_prompt": "...", "compression_rate": 0.5}
"""

from __future__ import annotations

import json
import os
import time
from urllib import error, request

from .base import CompressorAdapter
from ..schemas import CompressResult

DEFAULT_ENDPOINT = "https://mac.tailb28e57.ts.net:8443/api/compress"


class OpenCompressAdapter(CompressorAdapter):
    """Adapter for the OpenCompress compression API."""

    name = "opencompress"

    def __init__(
        self,
        endpoint: str | None = None,
        timeout: float = 120.0,
    ):
        self.endpoint = (
            endpoint
            or os.environ.get("OPENCOMPRESS_ENDPOINT")
            or DEFAULT_ENDPOINT
        )
        self.timeout = timeout

    def compress(self, text: str, rate: float) -> CompressResult:
        payload = json.dumps({
            "user_prompt": text,
            "compression_rate": rate,
        }).encode("utf-8")

        req = request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        t0 = time.perf_counter()
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            ms = (time.perf_counter() - t0) * 1000

            compressed = body.get("compressed_text", text)
            return CompressResult(
                original_text=text,
                compressed_text=compressed,
                original_tokens=body.get("original_tokens", len(text.split())),
                compressed_tokens=body.get("compressed_tokens", len(compressed.split())),
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
        health_url = self.endpoint.replace("/api/compress", "/api/health")
        try:
            req = request.Request(health_url, method="GET")
            with request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False
