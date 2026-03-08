"""Tests for CompressBench metrics."""

import json
from pathlib import Path

from compressbench.schemas import Case, CriticalUnit, StructureLabels, Task
from compressbench.metrics.trs import compute_trs
from compressbench.metrics.cir import compute_cir
from compressbench.metrics.sps import compute_sps
from compressbench.metrics.sfs import compute_sfs
from compressbench.metrics.ces import compute_ces
from compressbench.metrics.rs import compute_rs
from compressbench.scoring import compute_cbv2, aggregate_cbv2_across_rates
from compressbench.task_judge import judge_mcq, judge_extraction, judge_task


# -- TRS --

def test_trs_perfect():
    assert compute_trs(1.0, 1.0) == 1.0

def test_trs_half():
    assert compute_trs(1.0, 0.5) == 0.5

def test_trs_zero_original():
    assert compute_trs(0.0, 0.5) == 0.5

def test_trs_capped():
    # compressed score can't exceed original
    assert compute_trs(0.5, 1.0) == 1.0


# -- CIR --

def test_cir_all_recalled():
    units = [
        CriticalUnit("function", "parse_config"),
        CriticalUnit("number", "4096"),
    ]
    text = "The function parse_config reads a buffer of 4096 bytes."
    assert compute_cir(units, text) == 1.0

def test_cir_partial():
    units = [
        CriticalUnit("function", "parse_config"),
        CriticalUnit("number", "4096"),
    ]
    text = "The parse_config function handles configuration."
    assert compute_cir(units, text) == 0.5

def test_cir_empty():
    assert compute_cir([], "any text") == 1.0


# -- SPS --

def test_sps_identical():
    score = compute_sps("hello world foo bar", "hello world foo bar")
    assert score >= 0.99

def test_sps_different():
    score = compute_sps(
        "The quick brown fox jumps over the lazy dog",
        "completely unrelated text about quantum physics"
    )
    assert score < 0.5


# -- SFS --

def test_sfs_code_blocks():
    orig = "Text\n```python\nprint('hi')\n```\nMore text"
    comp = "Text\n```python\nprint('hi')\n```\nMore"
    assert compute_sfs(orig, comp) == 1.0

def test_sfs_lost_code_block():
    orig = "Text\n```python\nprint('hi')\n```\nMore text"
    comp = "Text print hi More text"
    labels = StructureLabels(has_code_block=True)
    score = compute_sfs(orig, comp, labels)
    assert score < 1.0

def test_sfs_no_structure():
    assert compute_sfs("plain text here", "plain text") == 1.0


# -- CES --

def test_ces_good_compression():
    score = compute_ces(1000, 300, 100)  # 70% savings, fast
    assert score > 0.5

def test_ces_no_compression():
    score = compute_ces(1000, 1000, 100)
    assert score < 0.5

def test_ces_zero_tokens():
    assert compute_ces(0, 0, 0) >= 0.0


# -- RS --

def test_rs_stable():
    assert compute_rs([80, 81, 79, 80]) > 0.9

def test_rs_unstable():
    assert compute_rs([90, 10, 50, 80]) < 0.5

def test_rs_single():
    assert compute_rs([50]) == 1.0


# -- CBv2 --

def test_cbv2_perfect():
    score, flags = compute_cbv2(1.0, 1.0, 1.0, 1.0, 1.0)
    assert score > 90
    assert "TRS_LOW" not in flags

def test_cbv2_trs_penalty():
    score, flags = compute_cbv2(0.80, 1.0, 1.0, 1.0, 1.0)
    assert "TRS_LOW" in flags

def test_cbv2_structure_invalid():
    score, flags = compute_cbv2(1.0, 1.0, 1.0, 0.0, 1.0,
                                 structure_required=True, structure_valid=False)
    assert score == 0.0

def test_cbv2_aggregate():
    by_rate = {0.25: 120, 0.50: 100, 0.70: 80}
    assert aggregate_cbv2_across_rates(by_rate) == 100.0


# -- Task Judge --

def test_judge_mcq_correct():
    task = Task("multiple_choice_qa", "Q?", "parse_config",
                ["parse_config", "load_settings", "read_yaml", "init_config"])
    score, correct = judge_mcq("parse_config", task)
    assert correct
    assert score == 1.0

def test_judge_mcq_wrong():
    task = Task("multiple_choice_qa", "Q?", "parse_config",
                ["parse_config", "load_settings"])
    score, correct = judge_mcq("load_settings", task)
    assert not correct

def test_judge_extraction_exact():
    task = Task("extraction", "Q?", "/api/health")
    score, correct = judge_extraction("/api/health", task)
    assert correct

def test_judge_extraction_contained():
    task = Task("extraction", "Q?", "/api/health")
    score, correct = judge_extraction("The endpoint is /api/health", task)
    assert correct


# -- Case loading --

def test_case_from_dict():
    d = {
        "id": "cb_test",
        "category": "code_context",
        "input_text": "test input",
        "original_tokens": 2,
        "task": {
            "type": "extraction",
            "question": "What?",
            "gold": "test",
        },
        "critical_units": [{"type": "entity", "value": "test"}],
        "structure_labels": {"has_code_block": True},
    }
    case = Case.from_dict(d)
    assert case.id == "cb_test"
    assert case.task.type == "extraction"
    assert len(case.critical_units) == 1
    assert case.structure_labels.has_code_block


def test_load_sample_cases():
    cases_path = Path(__file__).parent.parent / "cases" / "openclaw_v1.jsonl"
    if not cases_path.exists():
        return  # skip if no cases
    from compressbench.runner import load_cases
    cases = load_cases(cases_path)
    assert len(cases) >= 5
    for c in cases:
        assert c.id.startswith("cb_")
        assert c.task.question


if __name__ == "__main__":
    import sys
    # Simple test runner
    passed = failed = 0
    for name, obj in list(globals().items()):
        if name.startswith("test_") and callable(obj):
            try:
                obj()
                passed += 1
                print(f"  PASS  {name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL  {name}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
