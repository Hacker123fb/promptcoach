"""
test_app.py — Unit tests for JSON parsing, score calculations, and PII detection.
Run with: pytest test_app.py
"""

import pytest
from llm import _strip_fences, _parse_json_robust
from scoring import PromptScores, ScoringResult, _parse_scores, CRITERIA
from utils import detect_pii


# ===========================================================================
# 1. JSON Parsing Tests
# ===========================================================================
class TestJsonParsing:
    def test_strip_fences_clean_json(self):
        raw = '{"key": "value"}'
        assert _strip_fences(raw) == '{"key": "value"}'

    def test_strip_fences_with_markdown_fences(self):
        fenced = '```json\n{"key": "value"}\n```'
        assert _strip_fences(fenced) == '{"key": "value"}'

    def test_strip_fences_with_generic_code_fence(self):
        fenced = '```\n{"improved_prompt": "hello world"}\n```'
        assert _strip_fences(fenced) == '{"improved_prompt": "hello world"}'

    def test_parse_json_robust_valid_json(self):
        raw = '{"improved_prompt": "Write a 500-word essay", "explanation": {}}'
        data = _parse_json_robust(raw)
        assert data["improved_prompt"] == "Write a 500-word essay"
        assert isinstance(data["explanation"], dict)

    def test_parse_json_robust_fenced_json(self):
        fenced = '```json\n{"improved_prompt": "Act as an expert", "explanation": {"role": "added"}}\n```'
        data = _parse_json_robust(fenced)
        assert data["improved_prompt"] == "Act as an expert"
        assert data["explanation"]["role"] == "added"

    def test_parse_json_robust_malformed_raises_value_error(self):
        broken = '{"improved_prompt": "Unclosed string'
        with pytest.raises(ValueError, match="Gemini returned malformed JSON"):
            _parse_json_robust(broken)


# ===========================================================================
# 2. Score Calculation Tests
# ===========================================================================
class TestScoreCalculation:
    def test_prompt_scores_total(self):
        scores = PromptScores(
            clarity=8,
            specificity=7,
            context=9,
            format=6,
            constraints=5,
        )
        assert scores.total == 35

    def test_prompt_scores_as_dict(self):
        scores = PromptScores(
            clarity=10,
            specificity=9,
            context=8,
            format=7,
            constraints=6,
        )
        score_dict = scores.as_dict()
        assert score_dict == {
            "Clarity": 10,
            "Specificity": 9,
            "Context": 8,
            "Format": 7,
            "Constraints": 6,
        }

    def test_parse_scores_normal(self):
        raw = {
            "original": {
                "clarity": 4,
                "specificity": 3,
                "context": 2,
                "format": 1,
                "constraints": 1,
            }
        }
        parsed = _parse_scores(raw, "original")
        assert parsed.clarity == 4
        assert parsed.specificity == 3
        assert parsed.total == 11

    def test_parse_scores_clamping(self):
        raw = {
            "improved": {
                "clarity": 15,    # Out of range > 10
                "specificity": -5,  # Out of range < 1
                "context": 8,
                "format": 10,
                "constraints": 0,   # Out of range < 1
            }
        }
        parsed = _parse_scores(raw, "improved")
        assert parsed.clarity == 10     # Clamped to 10
        assert parsed.specificity == 1   # Clamped to 1
        assert parsed.constraints == 1   # Clamped to 1
        assert parsed.context == 8
        assert parsed.format == 10

    def test_parse_scores_missing_label_raises_value_error(self):
        raw = {"original": {"clarity": 5}}
        with pytest.raises(ValueError, match="missing 'improved' key"):
            _parse_scores(raw, "improved")

    def test_scoring_result_delta_calculation(self):
        orig = PromptScores(clarity=2, specificity=2, context=2, format=2, constraints=2)
        impr = PromptScores(clarity=8, specificity=9, context=8, format=9, constraints=8)
        result = ScoringResult(original=orig, improved=impr, tips=["Add more context"])

        assert result.original.total == 10
        assert result.improved.total == 42
        delta = result.improved.total - result.original.total
        assert delta == 32


# ===========================================================================
# 3. Personal Data (PII) Detector Tests
# ===========================================================================
class TestPiiDetector:
    def test_clean_input_returns_no_findings(self):
        clean_text = "Write a comprehensive guide on training for a half-marathon."
        findings = detect_pii(clean_text)
        assert findings == []

    def test_empty_string_returns_no_findings(self):
        assert detect_pii("") == []
        assert detect_pii("   ") == []

    def test_detect_email_address(self):
        text = "Please send the summary report to john.doe@example.com by tomorrow."
        findings = detect_pii(text)
        assert "email address" in findings
        assert "phone number" not in findings

    def test_detect_phone_number_formats(self):
        phone_examples = [
            "Call me at +1 555-123-4567 if you have questions.",
            "Reach our customer support at (800) 555-0199.",
            "Contact number is 9876543210 for verification.",
        ]
        for example in phone_examples:
            findings = detect_pii(example)
            assert "phone number" in findings

    def test_detect_both_email_and_phone(self):
        text = "Reach Jane at jane@corp.org or call +1-202-555-0143."
        findings = detect_pii(text)
        assert "email address" in findings
        assert "phone number" in findings
        assert len(findings) == 2
