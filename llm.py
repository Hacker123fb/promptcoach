"""
All Gemini API interactions for Prompt Coach.

Public functions:
  - get_client()           → google.genai.Client (singleton, validated)
  - improve_prompt(...)    → dict  (improved_prompt + explanation)
  - run_prompt(prompt)     → str   (raw AI response)
  - score_prompts(...)     → dict  (scores + tips)
"""

import os
import json
import re
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

from utils import get_api_key, get_model_name

# ---------------------------------------------------------------------------
# Lazy, validated client singleton
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_client():
    """Return a validated google.genai.Client, raising clear errors on failure."""
    try:
        from google import genai  # noqa: F401  – import check first
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Run: pip install google-genai"
        ) from exc

    api_key = get_api_key()
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file or Streamlit Secrets."
        )

    from google import genai as genai_lib
    client = genai_lib.Client(api_key=api_key)
    return client


def _model_name() -> str:
    return get_model_name()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _strip_fences(text: str) -> str:
    """Remove markdown code fences that Gemini sometimes wraps JSON in."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_json_robust(raw: str) -> dict:
    """Try to parse JSON; strip fences on first failure and retry once."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = _strip_fences(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Gemini returned malformed JSON (even after stripping fences).\n"
                f"Raw response:\n{raw[:500]}"
            ) from exc


def _chat(system_prompt: str, user_message: str, *, retry: bool = True) -> str:
    """
    Send a single-turn system+user message to Gemini and return the text.
    Retries once on rate-limit / transient errors.
    """
    from google.genai import types

    client = get_client()
    model = _model_name()

    def _call():
        response = client.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
            ),
        )
        return response.text

    try:
        return _call()
    except Exception as first_exc:
        err_str = str(first_exc).lower()
        # Retry once on rate-limit or transient server errors
        if retry and any(k in err_str for k in ("429", "rate", "503", "500", "timeout")):
            import time
            time.sleep(3)
            try:
                return _call()
            except Exception as second_exc:
                raise RuntimeError(
                    f"Gemini call failed after retry: {second_exc}"
                ) from second_exc
        raise RuntimeError(f"Gemini call failed: {first_exc}") from first_exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def improve_prompt(weak_prompt: str, goal: str = "", audience: str = "") -> dict:
    """
    Rewrite *weak_prompt* using the R-C-T-F-C framework.

    Returns a dict with keys:
      - improved_prompt : str
      - explanation     : dict[str, str]  (role, context, task, format, constraints)
    """
    from prompts import IMPROVE_SYSTEM_PROMPT, build_improve_user_message

    user_msg = build_improve_user_message(weak_prompt, goal, audience)
    raw = _chat(IMPROVE_SYSTEM_PROMPT, user_msg)
    result = _parse_json_robust(raw)

    # Validate required keys
    if "improved_prompt" not in result:
        raise ValueError("Gemini response is missing 'improved_prompt' key.")
    if "explanation" not in result:
        raise ValueError("Gemini response is missing 'explanation' key.")

    return result


def run_prompt(prompt: str) -> str:
    """
    Run *prompt* through Gemini with no system instruction and return the text response.
    Used for the before/after comparison.
    """
    from google.genai import types

    client = get_client()
    model = _model_name()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Gemini call failed for prompt execution: {exc}") from exc


def score_prompts(original: str, improved: str) -> dict:
    """
    Ask Gemini to score *original* vs *improved* prompts and provide tips.

    Returns a dict with keys:
      - scores : dict  (original + improved sub-dicts with 5 criteria each)
      - tips   : list[str]
    """
    from prompts import SCORE_SYSTEM_PROMPT, build_score_user_message

    user_msg = build_score_user_message(original, improved)
    raw = _chat(SCORE_SYSTEM_PROMPT, user_msg)
    result = _parse_json_robust(raw)

    if "scores" not in result or "tips" not in result:
        raise ValueError("Scoring response is missing 'scores' or 'tips' keys.")

    return result
