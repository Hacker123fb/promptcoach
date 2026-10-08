"""
Scoring logic: wraps llm.score_prompts() and formats results for the UI.

Public functions:
  - run_scoring(original, improved) → ScoringResult
"""

from dataclasses import dataclass, field
from typing import Dict, List

CRITERIA = ["clarity", "specificity", "context", "format", "constraints"]


@dataclass
class PromptScores:
    clarity: int = 0
    specificity: int = 0
    context: int = 0
    format: int = 0
    constraints: int = 0

    @property
    def total(self) -> int:
        return self.clarity + self.specificity + self.context + self.format + self.constraints

    def as_dict(self) -> Dict[str, int]:
        return {
            "Clarity": self.clarity,
            "Specificity": self.specificity,
            "Context": self.context,
            "Format": self.format,
            "Constraints": self.constraints,
        }


@dataclass
class ScoringResult:
    original: PromptScores = field(default_factory=PromptScores)
    improved: PromptScores = field(default_factory=PromptScores)
    tips: List[str] = field(default_factory=list)


def _parse_scores(raw_scores: dict, label: str) -> PromptScores:
    """Extract and validate per-criterion scores from the raw Gemini JSON dict."""
    if label not in raw_scores:
        raise ValueError(f"Scoring response missing '{label}' key in scores.")
    data = raw_scores[label]
    scores = {}
    for criterion in CRITERIA:
        val = data.get(criterion, 0)
        try:
            val = int(val)
        except (TypeError, ValueError):
            val = 0
        scores[criterion] = max(1, min(10, val))  # clamp to [1, 10]
    return PromptScores(**scores)


def run_scoring(original: str, improved: str) -> ScoringResult:
    """
    Call the Gemini judge, parse the response, and return a ScoringResult.
    Raises RuntimeError / ValueError with clear messages on failure.
    """
    from llm import score_prompts  # avoid circular at module load

    raw = score_prompts(original, improved)

    original_scores = _parse_scores(raw["scores"], "original")
    improved_scores = _parse_scores(raw["scores"], "improved")

    tips = raw.get("tips", [])
    if not isinstance(tips, list):
        tips = [str(tips)]
    tips = [str(t) for t in tips[:3]]  # cap at 3

    return ScoringResult(
        original=original_scores,
        improved=improved_scores,
        tips=tips,
    )
