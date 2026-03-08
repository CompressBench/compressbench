"""SPS — Semantic Preservation Score.

    SPS = cosine(emb(original), emb(compressed))

Uses sentence-transformers (BGE/GTE/e5) when available.
Falls back to token-overlap proxy when sentence-transformers is not installed.
"""

from __future__ import annotations

import re

_SENT_MODEL = None
_SENT_MODEL_LOADED = False


def _ensure_model():
    global _SENT_MODEL, _SENT_MODEL_LOADED
    if _SENT_MODEL_LOADED:
        return
    _SENT_MODEL_LOADED = True
    try:
        from sentence_transformers import SentenceTransformer
        _SENT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        pass
    except Exception:
        pass


def _token_overlap_proxy(original: str, compressed: str) -> float:
    """Fallback: token-overlap F1 as semantic proxy."""
    orig_toks = set(re.findall(r'\w+', original.lower()))
    comp_toks = set(re.findall(r'\w+', compressed.lower()))
    if not orig_toks or not comp_toks:
        return 0.0
    tp = len(orig_toks & comp_toks)
    prec = tp / len(comp_toks)
    rec = tp / len(orig_toks)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def compute_sps(original: str, compressed: str) -> float:
    """Compute Semantic Preservation Score.

    Args:
        original: original text
        compressed: compressed text

    Returns:
        SPS in [0, 1].
    """
    _ensure_model()

    if _SENT_MODEL is not None:
        try:
            import numpy as np
            embs = _SENT_MODEL.encode([original, compressed],
                                       convert_to_numpy=True)
            a, b = embs[0], embs[1]
            sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
            return max(0.0, min(1.0, sim))
        except Exception:
            pass

    return _token_overlap_proxy(original, compressed)
