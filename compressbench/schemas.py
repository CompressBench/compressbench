"""Data types for CompressBench cases, results, and metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CriticalUnit:
    """A single critical information unit that must be preserved."""
    type: str        # function, number, flag, constraint, entity, url, etc.
    value: str       # the literal value to check for


@dataclass
class Task:
    """Downstream task attached to a case."""
    type: str        # multiple_choice_qa, extraction, free_form
    question: str
    gold: str        # correct answer
    choices: list[str] = field(default_factory=list)  # for MCQ


@dataclass
class StructureLabels:
    """Structure annotations for a case."""
    has_code_block: bool = False
    has_list: bool = False
    has_json: bool = False
    has_yaml: bool = False
    has_table: bool = False
    has_headers: bool = False
    has_chat_turns: bool = False


@dataclass
class Case:
    """A single benchmark case."""
    id: str
    category: str           # code_context, chat_history, structured_data, documentation, mixed
    input_text: str
    original_tokens: int
    task: Task
    critical_units: list[CriticalUnit] = field(default_factory=list)
    structure_labels: StructureLabels = field(default_factory=StructureLabels)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Case:
        task_d = d["task"]
        task = Task(
            type=task_d["type"],
            question=task_d["question"],
            gold=task_d["gold"],
            choices=task_d.get("choices", []),
        )
        cus = [CriticalUnit(type=cu["type"], value=cu["value"])
               for cu in d.get("critical_units", [])]
        sl_d = d.get("structure_labels", {})
        sl = StructureLabels(**{k: v for k, v in sl_d.items()
                                if k in StructureLabels.__dataclass_fields__})
        return cls(
            id=d["id"],
            category=d["category"],
            input_text=d["input_text"],
            original_tokens=d.get("original_tokens", len(d["input_text"].split())),
            task=task,
            critical_units=cus,
            structure_labels=sl,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "input_text": self.input_text,
            "original_tokens": self.original_tokens,
            "task": {
                "type": self.task.type,
                "question": self.task.question,
                "gold": self.task.gold,
                "choices": self.task.choices,
            },
            "critical_units": [{"type": cu.type, "value": cu.value}
                               for cu in self.critical_units],
            "structure_labels": {
                "has_code_block": self.structure_labels.has_code_block,
                "has_list": self.structure_labels.has_list,
                "has_json": self.structure_labels.has_json,
                "has_yaml": self.structure_labels.has_yaml,
                "has_table": self.structure_labels.has_table,
                "has_headers": self.structure_labels.has_headers,
                "has_chat_turns": self.structure_labels.has_chat_turns,
            },
        }


@dataclass
class CompressResult:
    """Output from a compression adapter."""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    rate_requested: float
    rate_applied: float
    compression_ms: float
    method: str = "unknown"
    error: Optional[str] = None


@dataclass
class CaseResult:
    """Full evaluation result for one case at one rate."""
    case_id: str
    category: str
    rate: float
    method: str
    compress: CompressResult
    trs: float = 0.0
    cir: float = 0.0
    sps: float = 0.0
    sfs: float = 0.0
    ces: float = 0.0
    cbv2: float = 0.0
    task_answer: str = ""
    task_correct: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "category": self.category,
            "rate": self.rate,
            "method": self.method,
            "trs": round(self.trs, 4),
            "cir": round(self.cir, 4),
            "sps": round(self.sps, 4),
            "sfs": round(self.sfs, 4),
            "ces": round(self.ces, 4),
            "cbv2": round(self.cbv2, 4),
            "task_answer": self.task_answer,
            "task_correct": self.task_correct,
            "original_tokens": self.compress.original_tokens,
            "compressed_tokens": self.compress.compressed_tokens,
            "compression_ms": round(self.compress.compression_ms, 1),
        }


@dataclass
class BenchmarkResult:
    """Aggregated benchmark result across all cases and rates."""
    method: str
    provider: str = ""
    version: str = "1.0.0"
    cases: list[CaseResult] = field(default_factory=list)
    rates: list[float] = field(default_factory=list)

    # Per-rate aggregates
    cbv2_by_rate: dict[float, float] = field(default_factory=dict)
    trs_by_rate: dict[float, float] = field(default_factory=dict)
    cir_by_rate: dict[float, float] = field(default_factory=dict)
    sps_by_rate: dict[float, float] = field(default_factory=dict)
    sfs_by_rate: dict[float, float] = field(default_factory=dict)
    ces_by_rate: dict[float, float] = field(default_factory=dict)

    # Final
    cbv2_final: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "provider": self.provider,
            "version": self.version,
            "cbv2_final": round(self.cbv2_final, 4),
            "cbv2_by_rate": {str(k): round(v, 4) for k, v in self.cbv2_by_rate.items()},
            "metrics_by_rate": {
                str(r): {
                    "trs": round(self.trs_by_rate.get(r, 0), 4),
                    "cir": round(self.cir_by_rate.get(r, 0), 4),
                    "sps": round(self.sps_by_rate.get(r, 0), 4),
                    "sfs": round(self.sfs_by_rate.get(r, 0), 4),
                    "ces": round(self.ces_by_rate.get(r, 0), 4),
                    "cbv2": round(self.cbv2_by_rate.get(r, 0), 4),
                }
                for r in self.rates
            },
            "cases": [c.to_dict() for c in self.cases],
        }
