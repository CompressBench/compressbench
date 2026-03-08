"""Upload benchmark results to the CompressBench leaderboard."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

DEFAULT_SERVER_URL = "https://compressbench-leaderboard.vercel.app"
CONFIG_DIR = Path.home() / ".compressbench"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class UploadResult:
    status: str
    submission_id: str
    rank: int | None = None
    percentile: float | None = None
    leaderboard_url: str | None = None


class UploadError(RuntimeError):
    pass


def upload_results(
    results_path: Path,
    *,
    server_url: str | None = None,
    token: str | None = None,
    timeout_seconds: float = 30.0,
    dry_run: bool = False,
) -> UploadResult:
    """Upload benchmark results to the CompressBench leaderboard.

    Args:
        results_path: path to the JSON results file
        server_url: override server URL
        token: auth token (default: from env or config)
        timeout_seconds: HTTP request timeout
        dry_run: if True, validate but don't send

    Returns:
        UploadResult with status, rank, leaderboard URL

    Raises:
        UploadError: on failure
    """
    resolved_server = server_url or os.environ.get("COMPRESSBENCH_SERVER_URL") or DEFAULT_SERVER_URL
    resolved_token = _resolve_token(token)
    if not resolved_token:
        raise UploadError("COMPRESSBENCH_TOKEN is not configured. Run: compressbench register")

    payload = _build_payload(results_path)
    if dry_run:
        return UploadResult(status="dry_run", submission_id=payload["submission_id"])

    endpoint = resolved_server.rstrip("/") + "/api/results"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-CompressBench-Token": resolved_token,
        "User-Agent": f"CompressBench/{payload.get('version', '1.0.0')}",
    }
    req = request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8")) if resp.read() else {}
    except error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read().decode("utf-8")) if exc.read() else {}
        except Exception:
            err_body = {}
        raise UploadError(f"Upload failed ({exc.code}): {err_body or exc.reason}") from exc
    except error.URLError as exc:
        raise UploadError(f"Upload failed (network): {exc.reason}") from exc

    return UploadResult(
        status=str(data.get("status", "accepted")),
        submission_id=str(data.get("submission_id", payload["submission_id"])),
        rank=int(data["rank"]) if data.get("rank") else None,
        percentile=float(data["percentile"]) if data.get("percentile") else None,
        leaderboard_url=data.get("leaderboard_url"),
    )


def register_token(
    *,
    server_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> tuple[str, str | None]:
    """Register for a leaderboard token."""
    resolved_server = server_url or os.environ.get("COMPRESSBENCH_SERVER_URL") or DEFAULT_SERVER_URL
    endpoint = resolved_server.rstrip("/") + "/api/register"
    body = json.dumps({}).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "CompressBench/1.0.0"}
    req = request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8")) if resp.read() else {}
    except error.HTTPError as exc:
        raise UploadError(f"Registration failed ({exc.code})") from exc
    except error.URLError as exc:
        raise UploadError(f"Registration failed (network): {exc.reason}") from exc

    token = data.get("token") or data.get("api_key")
    if not token:
        raise UploadError("Registration failed: no token in response")
    return token, data.get("claim_url")


def save_token_config(token: str, claim_url: str | None = None) -> Path:
    """Save token to config file."""
    config = _read_config()
    config["token"] = token
    if claim_url:
        config["claim_url"] = claim_url
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return CONFIG_PATH


def _build_payload(results_path: Path) -> dict[str, Any]:
    raw = json.loads(results_path.read_text(encoding="utf-8"))

    # Build metrics_by_category from case-level data
    metrics_by_category: dict[str, dict[str, list[float]]] = {}
    for case in raw.get("cases", []):
        cat = case.get("category", "unknown")
        if cat not in metrics_by_category:
            metrics_by_category[cat] = {
                "cbv2": [], "trs": [], "cir": [], "sps": [], "sfs": [], "ces": [],
            }
        for m in ("cbv2", "trs", "cir", "sps", "sfs", "ces"):
            metrics_by_category[cat][m].append(case.get(m, 0))

    # Average the per-category metrics
    cat_averages: dict[str, dict[str, float]] = {}
    for cat, metrics in metrics_by_category.items():
        cat_averages[cat] = {
            m: sum(vals) / len(vals) if vals else 0
            for m, vals in metrics.items()
        }

    return {
        "submission_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version": raw.get("version", "1.0.0"),
        "method": raw.get("method", ""),
        "provider": raw.get("provider", ""),
        "cbv2_final": raw.get("cbv2_final", 0),
        "cbv2_by_rate": raw.get("cbv2_by_rate", {}),
        "metrics_by_rate": raw.get("metrics_by_rate", {}),
        "metrics_by_category": cat_averages,
        "cases": raw.get("cases", []),
        "metadata": {
            "system": _collect_system_metadata(),
        },
    }


def _read_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _resolve_token(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    env = os.environ.get("COMPRESSBENCH_TOKEN")
    if env:
        return env
    return _read_config().get("token")


def _collect_system_metadata() -> dict[str, Any]:
    return {
        "os": sys.platform,
        "os_version": platform.version(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }
