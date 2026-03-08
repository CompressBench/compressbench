"""Downstream task judge — evaluates model answers against gold.

Task types:
    - multiple_choice_qa: exact match against gold answer
    - extraction: fuzzy/exact match for extracted values
    - free_form: LLM judge scoring (falls back to token overlap)
"""

from __future__ import annotations

import os
import re
from typing import Optional

from .schemas import Task


def _normalize_answer(text: str) -> str:
    """Normalize answer for comparison."""
    text = text.strip().lower()
    # Remove common prefixes
    for prefix in ("answer:", "the answer is", "answer is"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    # Remove quotes
    text = text.strip("\"'`")
    return text


def judge_mcq(answer: str, task: Task) -> tuple[float, bool]:
    """Judge a multiple-choice answer.

    Returns:
        (score, correct) where score is 0 or 1.
    """
    norm_answer = _normalize_answer(answer)
    norm_gold = _normalize_answer(task.gold)

    # Direct match
    if norm_answer == norm_gold:
        return 1.0, True

    # Check if answer contains the gold choice
    if norm_gold in norm_answer:
        return 1.0, True

    # Check letter matching (A/B/C/D)
    if task.choices:
        for i, choice in enumerate(task.choices):
            letter = chr(ord('A') + i)
            if _normalize_answer(choice) == norm_gold:
                if norm_answer in (letter.lower(), f"({letter.lower()})"):
                    return 1.0, True

    return 0.0, False


def judge_extraction(answer: str, task: Task) -> tuple[float, bool]:
    """Judge an extraction answer.

    Uses exact match first, then fuzzy substring matching.

    Returns:
        (score, correct) where score is 0 or 1.
    """
    norm_answer = _normalize_answer(answer)
    norm_gold = _normalize_answer(task.gold)

    # Exact match
    if norm_answer == norm_gold:
        return 1.0, True

    # Gold contained in answer
    if norm_gold in norm_answer:
        return 1.0, True

    # Answer contained in gold (partial credit)
    if norm_answer and norm_answer in norm_gold:
        return 0.5, False

    return 0.0, False


def judge_free_form(
    answer: str,
    task: Task,
    llm_judge_fn: Optional[callable] = None,
) -> tuple[float, bool]:
    """Judge a free-form answer.

    Uses LLM judge if available, otherwise falls back to token overlap.

    Args:
        answer: model's answer
        task: Task with gold answer
        llm_judge_fn: optional callable(question, gold, answer) -> float

    Returns:
        (score, correct) where score is 0.0–1.0.
    """
    if llm_judge_fn is not None:
        try:
            score = llm_judge_fn(task.question, task.gold, answer)
            return score, score >= 0.5
        except Exception:
            pass

    # Fallback: token overlap F1 between answer and gold
    gold_tokens = set(re.findall(r'\w+', task.gold.lower()))
    answer_tokens = set(re.findall(r'\w+', answer.lower()))

    if not gold_tokens or not answer_tokens:
        return 0.0, False

    tp = len(gold_tokens & answer_tokens)
    precision = tp / len(answer_tokens) if answer_tokens else 0
    recall = tp / len(gold_tokens) if gold_tokens else 0

    if precision + recall == 0:
        return 0.0, False

    f1 = 2 * precision * recall / (precision + recall)
    return f1, f1 >= 0.5


def judge_task(
    answer: str,
    task: Task,
    llm_judge_fn: Optional[callable] = None,
) -> tuple[float, bool]:
    """Route to the appropriate judge based on task type.

    Args:
        answer: model's answer string
        task: Task with type, question, gold, choices
        llm_judge_fn: optional LLM judge for free_form tasks

    Returns:
        (score, correct)
    """
    if task.type == "multiple_choice_qa":
        return judge_mcq(answer, task)
    elif task.type == "extraction":
        return judge_extraction(answer, task)
    elif task.type == "free_form":
        return judge_free_form(answer, task, llm_judge_fn)
    else:
        # Unknown type — treat as extraction
        return judge_extraction(answer, task)
