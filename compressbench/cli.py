"""CompressBench CLI.

Usage:
    compressbench run --method random_drop --rates 0.25,0.5,0.7
    compressbench run --method truncation --rates 0.25,0.5,0.7
    compressbench run --method http --endpoint http://localhost:8080/compress
    compressbench run --method opencompress
    compressbench results latest
    compressbench results compare result1.json result2.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _find_cases_file() -> Path:
    """Find the cases JSONL file."""
    candidates = [
        Path(__file__).parent.parent / "cases" / "openclaw_v1.jsonl",
        Path("cases/openclaw_v1.jsonl"),
        Path.cwd() / "cases" / "openclaw_v1.jsonl",
    ]
    for p in candidates:
        if p.exists():
            return p
    # Default to package-relative
    return candidates[0]


def _get_adapter(args):
    """Create adapter from CLI args."""
    method = args.method

    if method == "random_drop":
        from .adapters.random_drop import RandomDropAdapter
        return RandomDropAdapter(seed=getattr(args, "seed", 42))

    if method == "truncation":
        from .adapters.truncation import TruncationAdapter
        return TruncationAdapter()

    if method == "http":
        from .adapters.http import HttpAdapter
        if not args.endpoint:
            print("Error: --endpoint required for http method", file=sys.stderr)
            sys.exit(1)
        return HttpAdapter(endpoint=args.endpoint)

    if method == "opencompress":
        from .adapters.opencompress import OpenCompressAdapter
        return OpenCompressAdapter(endpoint=args.endpoint)

    print(f"Error: unknown method '{method}'", file=sys.stderr)
    print("Available: random_drop, truncation, http, opencompress", file=sys.stderr)
    sys.exit(1)


def cmd_run(args):
    """Run the benchmark."""
    from .runner import run_benchmark

    adapter = _get_adapter(args)
    rates = [float(r.strip()) for r in args.rates.split(",")]
    cases_path = Path(args.cases) if args.cases else _find_cases_file()

    if not cases_path.exists():
        print(f"Error: cases file not found: {cases_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output) if args.output else Path("results")

    run_benchmark(
        cases_path=cases_path,
        adapter=adapter,
        rates=rates,
        output_dir=output_dir,
        verbose=not args.quiet,
        provider=getattr(args, "provider", ""),
    )


def cmd_results(args):
    """View or compare results."""
    if args.action == "latest":
        results_dir = Path(args.output) if args.output else Path("results")
        if not results_dir.exists():
            print("No results directory found.", file=sys.stderr)
            sys.exit(1)
        files = sorted(results_dir.glob("result_*.json"), reverse=True)
        if not files:
            print("No result files found.", file=sys.stderr)
            sys.exit(1)
        latest = files[0]
        data = json.loads(latest.read_text(encoding="utf-8"))
        _print_result(data, latest.name)

    elif args.action == "compare":
        if not args.files or len(args.files) < 2:
            print("Error: need at least 2 files to compare", file=sys.stderr)
            sys.exit(1)
        results = []
        for f in args.files:
            path = Path(f)
            if not path.exists():
                print(f"Error: file not found: {f}", file=sys.stderr)
                sys.exit(1)
            results.append((path.name, json.loads(path.read_text(encoding="utf-8"))))
        _print_comparison(results)


def _print_result(data: dict, name: str):
    """Print a single result summary."""
    print(f"\n{'='*60}")
    print(f"  Result: {name}")
    print(f"  Method: {data.get('method', '?')}")
    print(f"{'='*60}")
    print(f"\n  CBv2_final: {data.get('cbv2_final', 0):.1f}")

    by_rate = data.get("metrics_by_rate", {})
    for rate_str, metrics in sorted(by_rate.items()):
        print(f"\n  --- Rate {rate_str} ---")
        for k, v in metrics.items():
            print(f"    {k:<8s} {v:.4f}")


def _print_comparison(results: list[tuple[str, dict]]):
    """Print comparison table of multiple results."""
    print(f"\n{'='*70}")
    print(f"  CompressBench Results Comparison")
    print(f"{'='*70}")

    # Header
    header = f"{'Metric':<12s}"
    for name, _ in results:
        label = name[:20]
        header += f"  {label:>20s}"
    print(header)
    print("-" * len(header))

    # CBv2 final
    row = f"{'CBv2_final':<12s}"
    for _, data in results:
        row += f"  {data.get('cbv2_final', 0):>20.1f}"
    print(row)

    # Per-rate metrics
    all_rates = set()
    for _, data in results:
        all_rates.update(data.get("metrics_by_rate", {}).keys())

    for rate in sorted(all_rates):
        print(f"\n  Rate={rate}")
        metrics_keys = ["cbv2", "trs", "cir", "sps", "sfs", "ces"]
        for mk in metrics_keys:
            row = f"    {mk:<10s}"
            for _, data in results:
                val = data.get("metrics_by_rate", {}).get(rate, {}).get(mk, 0)
                row += f"  {val:>20.4f}"
            print(row)


def cmd_register(args):
    """Register for leaderboard."""
    from .upload import register_token, save_token_config
    token, claim_url = register_token()
    save_token_config(token, claim_url)
    print(f"Token saved. Claim URL: {claim_url or '(none)'}")


def cmd_submit(args):
    """Submit results to leaderboard."""
    from .upload import upload_results
    result = upload_results(Path(args.file))
    print(f"Submitted: {result.status}")
    if result.rank:
        print(f"Rank: #{result.rank}")
    if result.leaderboard_url:
        print(f"Leaderboard: {result.leaderboard_url}")


def main():
    parser = argparse.ArgumentParser(
        prog="compressbench",
        description="CompressBench — Utility-Preserving Compression Benchmark",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # run
    run_parser = subparsers.add_parser("run", help="Run the benchmark")
    run_parser.add_argument("--method", required=True,
                            choices=["random_drop", "truncation", "http", "opencompress"],
                            help="Compression method")
    run_parser.add_argument("--rates", default="0.25,0.50,0.70",
                            help="Comma-separated compression rates")
    run_parser.add_argument("--cases", help="Path to cases JSONL file")
    run_parser.add_argument("--endpoint", help="HTTP endpoint for http/opencompress methods")
    run_parser.add_argument("--output", help="Output directory for results")
    run_parser.add_argument("--seed", type=int, default=42,
                            help="Random seed for random_drop")
    run_parser.add_argument("--provider", default="",
                            help="Provider name (e.g. opencompress)")
    run_parser.add_argument("--quiet", "-q", action="store_true",
                            help="Suppress progress output")

    # results
    results_parser = subparsers.add_parser("results", help="View results")
    results_parser.add_argument("action", choices=["latest", "compare"],
                                help="Action: latest or compare")
    results_parser.add_argument("files", nargs="*", help="Files to compare")
    results_parser.add_argument("--output", help="Results directory")

    # register
    subparsers.add_parser("register", help="Register for leaderboard")

    # submit
    submit_parser = subparsers.add_parser("submit", help="Submit results")
    submit_parser.add_argument("file", help="Result JSON file to submit")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "results":
        cmd_results(args)
    elif args.command == "register":
        cmd_register(args)
    elif args.command == "submit":
        cmd_submit(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
