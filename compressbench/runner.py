"""CompressBench runner — loads cases, compresses, judges, scores.

Pipeline:
    1. Load cases from JSONL
    2. For each case × rate:
       a. Compress input_text via adapter
       b. Run downstream task (send compressed prompt to LLM, get answer)
       c. Judge answer against gold
       d. Compute all metrics (TRS, CIR, SPS, SFS, CES)
       e. Compute CBv2 composite score
    3. Aggregate across cases and rates
    4. Save results
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional

from .adapters.base import CompressorAdapter
from .metrics.cir import compute_cir
from .metrics.ces import compute_ces
from .metrics.sfs import compute_sfs
from .metrics.sps import compute_sps
from .metrics.trs import compute_trs
from .scoring import aggregate_cbv2_across_rates, compute_cbv2
from .schemas import BenchmarkResult, Case, CaseResult, CompressResult
from .task_judge import judge_task


def load_cases(path: Path) -> list[Case]:
    """Load cases from a JSONL file."""
    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            cases.append(Case.from_dict(d))
    return cases


def _run_downstream_task(
    case: Case,
    prompt_text: str,
    llm_fn: Optional[callable] = None,
) -> str:
    """Send prompt + task question to downstream LLM and get answer.

    If no llm_fn is provided, uses a simple heuristic:
    - For MCQ: search prompt for choices, pick the one most present
    - For extraction: return empty (worst case)

    In real use, llm_fn should call an LLM API.
    """
    if llm_fn is not None:
        # Build the evaluation prompt
        task = case.task
        if task.type == "multiple_choice_qa":
            choices_str = "\n".join(
                f"  {chr(65 + i)}) {c}" for i, c in enumerate(task.choices)
            )
            eval_prompt = (
                f"Context:\n{prompt_text}\n\n"
                f"Question: {task.question}\n"
                f"Choices:\n{choices_str}\n\n"
                f"Answer with just the correct option text."
            )
        elif task.type == "extraction":
            eval_prompt = (
                f"Context:\n{prompt_text}\n\n"
                f"Question: {task.question}\n\n"
                f"Answer concisely with the extracted value only."
            )
        else:
            eval_prompt = (
                f"Context:\n{prompt_text}\n\n"
                f"Question: {task.question}\n\n"
                f"Answer concisely."
            )
        return llm_fn(eval_prompt)

    # No LLM — heuristic fallback for MCQ
    if case.task.type == "multiple_choice_qa" and case.task.choices:
        prompt_lower = prompt_text.lower()
        best_choice = ""
        best_count = -1
        for choice in case.task.choices:
            count = prompt_lower.count(choice.lower())
            if count > best_count:
                best_count = count
                best_choice = choice
        return best_choice

    return ""


def evaluate_case(
    case: Case,
    adapter: CompressorAdapter,
    rate: float,
    llm_fn: Optional[callable] = None,
    llm_judge_fn: Optional[callable] = None,
    original_score: Optional[float] = None,
) -> CaseResult:
    """Evaluate a single case at a single compression rate.

    Args:
        case: the benchmark case
        adapter: compression adapter to use
        rate: target compression rate
        llm_fn: optional LLM function for downstream task
        llm_judge_fn: optional LLM judge for free_form tasks
        original_score: pre-computed score for original (uncompressed) prompt.
                        If None, will be computed by running the task on original text.

    Returns:
        CaseResult with all metrics.
    """
    # 1. Compress
    compress_result = adapter.compress(case.input_text, rate)

    # 2. Get original score if not provided
    if original_score is None:
        orig_answer = _run_downstream_task(case, case.input_text, llm_fn)
        original_score, _ = judge_task(orig_answer, case.task, llm_judge_fn)

    # 3. Run downstream task on compressed text
    comp_answer = _run_downstream_task(
        case, compress_result.compressed_text, llm_fn
    )
    compressed_score, task_correct = judge_task(
        comp_answer, case.task, llm_judge_fn
    )

    # 4. Compute metrics
    trs = compute_trs(original_score, compressed_score)
    cir = compute_cir(case.critical_units, compress_result.compressed_text)
    sps = compute_sps(case.input_text, compress_result.compressed_text)
    sfs = compute_sfs(
        case.input_text,
        compress_result.compressed_text,
        case.structure_labels,
    )
    ces = compute_ces(
        compress_result.original_tokens,
        compress_result.compressed_tokens,
        compress_result.compression_ms,
    )

    # 5. Structure validity check
    structure_required = (
        case.structure_labels.has_json or case.structure_labels.has_yaml
    )
    structure_valid = sfs > 0.0 if structure_required else True

    # 6. CBv2
    cbv2, flags = compute_cbv2(
        trs, cir, sps, sfs, ces,
        structure_required=structure_required,
        structure_valid=structure_valid,
    )

    return CaseResult(
        case_id=case.id,
        category=case.category,
        rate=rate,
        method=adapter.name,
        compress=compress_result,
        trs=trs,
        cir=cir,
        sps=sps,
        sfs=sfs,
        ces=ces,
        cbv2=cbv2,
        task_answer=comp_answer,
        task_correct=task_correct,
    )


def run_benchmark(
    cases_path: Path,
    adapter: CompressorAdapter,
    rates: list[float] | None = None,
    llm_fn: Optional[callable] = None,
    llm_judge_fn: Optional[callable] = None,
    output_dir: Path | None = None,
    verbose: bool = True,
    provider: str = "",
) -> BenchmarkResult:
    """Run the full benchmark.

    Args:
        cases_path: path to JSONL cases file
        adapter: compression adapter
        rates: compression rates to test (default: [0.25, 0.50, 0.70])
        llm_fn: optional LLM function for downstream tasks
        llm_judge_fn: optional LLM judge for free_form
        output_dir: directory to save results
        verbose: print progress

    Returns:
        BenchmarkResult with all case results and aggregates.
    """
    if rates is None:
        rates = [0.25, 0.50, 0.70]

    cases = load_cases(cases_path)
    if not cases:
        print(f"No cases found in {cases_path}")
        return BenchmarkResult(method=adapter.name, provider=provider, rates=rates)

    if verbose:
        print(f"CompressBench v1.0 — Utility-Preserving Compression Benchmark")
        print(f"Cases: {len(cases)} | Rates: {', '.join(f'{r:.2f}' for r in rates)} | Method: {adapter.name}")
        print()

    result = BenchmarkResult(method=adapter.name, provider=provider, rates=rates)
    all_cases: list[CaseResult] = []

    # Pre-compute original scores for each case (once, not per rate)
    original_scores: dict[str, float] = {}
    if verbose:
        print("Computing original (uncompressed) baseline scores...")
    for case in cases:
        orig_answer = _run_downstream_task(case, case.input_text, llm_fn)
        score, _ = judge_task(orig_answer, case.task, llm_judge_fn)
        original_scores[case.id] = score

    for rate in rates:
        if verbose:
            print(f"\n{'='*60}")
            print(f"  Rate: {rate:.2f}")
            print(f"{'='*60}")

        for i, case in enumerate(cases):
            cr = evaluate_case(
                case, adapter, rate, llm_fn, llm_judge_fn,
                original_score=original_scores[case.id],
            )
            all_cases.append(cr)

            if verbose:
                sys.stdout.write(
                    f"  [{i+1:3d}/{len(cases)}] {case.category:<18s} "
                    f"@{rate:.2f}  "
                    f"TRS={cr.trs:.2f} CIR={cr.cir:.2f} SFS={cr.sfs:.2f} "
                    f"CES={cr.ces:.2f}  CBv2={cr.cbv2:.1f}\n"
                )

    result.cases = all_cases

    # Aggregate per rate
    for rate in rates:
        rate_cases = [c for c in all_cases if c.rate == rate]
        if not rate_cases:
            continue
        n = len(rate_cases)
        result.trs_by_rate[rate] = sum(c.trs for c in rate_cases) / n
        result.cir_by_rate[rate] = sum(c.cir for c in rate_cases) / n
        result.sps_by_rate[rate] = sum(c.sps for c in rate_cases) / n
        result.sfs_by_rate[rate] = sum(c.sfs for c in rate_cases) / n
        result.ces_by_rate[rate] = sum(c.ces for c in rate_cases) / n
        result.cbv2_by_rate[rate] = sum(c.cbv2 for c in rate_cases) / n

    result.cbv2_final = aggregate_cbv2_across_rates(result.cbv2_by_rate)

    # Print summary
    if verbose:
        print(f"\n{'='*60}")
        for rate in rates:
            print(f"\n=== RESULTS (rate={rate:.2f}) ===")
            print(f"  CBv2:  {result.cbv2_by_rate.get(rate, 0):.1f}")
            print(f"  TRS:   {result.trs_by_rate.get(rate, 0):.3f}")
            print(f"  CIR:   {result.cir_by_rate.get(rate, 0):.3f}")
            print(f"  SPS:   {result.sps_by_rate.get(rate, 0):.3f}")
            print(f"  SFS:   {result.sfs_by_rate.get(rate, 0):.3f}")
            print(f"  CES:   {result.ces_by_rate.get(rate, 0):.3f}")

        print(f"\n=== FINAL (mean across rates) ===")
        parts = " | ".join(
            f"CBv2@{r:.2f}: {result.cbv2_by_rate.get(r, 0):.1f}"
            for r in rates
        )
        print(f"  {parts}")
        print(f"  CBv2_final: {result.cbv2_final:.1f}")

    # Save results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = output_dir / f"result_{adapter.name}_{ts}.json"
        out_path.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if verbose:
            print(f"\nResults saved → {out_path}")

    return result
