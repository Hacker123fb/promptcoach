"""
evaluation.py — Built-in test set and batch evaluation runner.

Public API:
  - TEST_PROMPTS      : list of dicts {domain, weak_prompt}
  - EvalResult        : dataclass for one evaluated prompt
  - run_single_eval() : evaluate one prompt (improve + score)
  - results_to_df()   : convert list[EvalResult] to pandas DataFrame
"""

from dataclasses import dataclass
from typing import List
import pandas as pd

# ---------------------------------------------------------------------------
# 10-prompt built-in test set — diverse domains
# ---------------------------------------------------------------------------
TEST_PROMPTS = [
    {"domain": "Education",  "weak_prompt": "explain photosynthesis"},
    {"domain": "Coding",     "weak_prompt": "write python code"},
    {"domain": "Marketing",  "weak_prompt": "write an ad"},
    {"domain": "Health",     "weak_prompt": "give me a diet plan"},
    {"domain": "Writing",    "weak_prompt": "write a story"},
    {"domain": "Business",   "weak_prompt": "write a business plan"},
    {"domain": "Science",    "weak_prompt": "explain quantum physics"},
    {"domain": "Travel",     "weak_prompt": "plan a trip"},
    {"domain": "Finance",    "weak_prompt": "explain investing"},
    {"domain": "Career",     "weak_prompt": "help me with my resume"},
]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------
@dataclass
class EvalResult:
    domain: str
    weak_prompt: str
    improved_prompt: str
    original_total: int
    improved_total: int
    improvement: int
    error: str = ""          # non-empty means this item failed


# ---------------------------------------------------------------------------
# Single-item evaluator (called per-prompt in the UI loop)
# ---------------------------------------------------------------------------
def run_single_eval(domain: str, weak_prompt: str) -> EvalResult:
    """
    Improve *weak_prompt* with Gemini, then score original vs improved.
    Returns an EvalResult; on failure fills the .error field and sets
    scores to 0 so the caller can continue safely.
    """
    from llm import improve_prompt        # deferred to avoid circular import
    from scoring import run_scoring

    try:
        improvement   = improve_prompt(weak_prompt)
        improved_text = improvement["improved_prompt"]
        sr            = run_scoring(weak_prompt, improved_text)
        return EvalResult(
            domain          = domain,
            weak_prompt     = weak_prompt,
            improved_prompt = improved_text,
            original_total  = sr.original.total,
            improved_total  = sr.improved.total,
            improvement     = sr.improved.total - sr.original.total,
        )
    except Exception as exc:
        return EvalResult(
            domain          = domain,
            weak_prompt     = weak_prompt,
            improved_prompt = "",
            original_total  = 0,
            improved_total  = 0,
            improvement     = 0,
            error           = str(exc),
        )


# ---------------------------------------------------------------------------
# DataFrame helper
# ---------------------------------------------------------------------------
def results_to_df(results: List[EvalResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({
            "Domain":           r.domain,
            "Weak Prompt":      r.weak_prompt,
            "Original Score":   r.original_total,
            "Improved Score":   r.improved_total,
            "Improvement (Δ)":  r.improvement,
            "Error":            r.error,
        })
    return pd.DataFrame(rows)
