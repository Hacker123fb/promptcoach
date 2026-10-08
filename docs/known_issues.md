# ⚠️ Known Issues & Failure Modes

This document catalogues observed edge cases, LLM behavioral quirks, and production challenges identified during development, alongside how Prompt Coach mitigates each.

---

## 1. Malformed JSON & Markdown Code Fences

- **Observed Behavior**:
  LLMs instructed to output raw JSON occasionally enclose the output inside markdown code fences (e.g., ````json { ... } ````) or append conversational commentary (e.g., `Here is the JSON you requested: ...`).
- **Impact**:
  Causes standard `json.loads()` to raise `JSONDecodeError`, halting the application.
- **How It Was Handled**:
  - Implemented `_strip_fences()` in [`llm.py`](../llm.py) which strips leading ````json` and trailing ```` markers using regex.
  - Implemented a two-pass `_parse_json_robust()` function that attempts standard parsing first, falls back to fence-stripping on error, and raises an informative `ValueError` if parsing still fails.

---

## 2. Inconsistent or Out-of-Bounds Judge Scores

- **Observed Behavior**:
  The LLM judge can occasionally output floating point numbers (e.g., `7.5`), values exceeding the requested range (e.g., `11`), or exhibit subjective score drift between consecutive runs.
- **Impact**:
  Breaks integer-based score calculations, disrupts metric progress bars, and can mislead users.
- **How It Was Handled**:
  - Both original and improved prompts are scored in a **single inference call**, establishing a unified baseline for comparison.
  - Implemented strict boundary clamping in `_parse_scores()` inside [`scoring.py`](../scoring.py) using `max(1, min(10, int(val)))`.
  - Scaled color thresholds: Scores out of 10 are classified as Low ($\le 4$), Mid ($5-7$), or High ($> 7$). Total aggregate scores out of 50 are scaled to Low ($\le 20$), Mid ($21-35$), and High ($> 35$).

---

## 3. Rate Limits (HTTP 429) & Transient Model Overloads (HTTP 503)

- **Observed Behavior**:
  Free-tier Google AI Studio API keys are subject to requests-per-minute (RPM) and tokens-per-minute (TPM) quotas. During peak traffic or automated evaluation runs, the API may return 429 or 503 responses.
- **Impact**:
  Abrupt pipeline termination mid-step.
- **How It Was Handled**:
  - The `_chat()` function in [`llm.py`](../llm.py) catches rate-limit exceptions and transient network issues (matching `429`, `rate`, `500`, `503`, `timeout`).
  - Automatically performs a backoff sleep (3 seconds) and retries the call once before failing gracefully.
  - In the Evaluation batch suite ([`evaluation.py`](../evaluation.py)), individual prompt failures are captured inside `EvalResult.error` without crashing the remaining 9 items in the batch.

---

## 4. End-to-End Latency & Response Times

- **Observed Behavior**:
  Each prompt improvement cycle executes **three sequential or parallel API calls**:
  1. Rewriting prompt ($1$ call)
  2. Executing both original and improved prompts ($2$ calls)
  3. Judge scoring ($1$ call)
  Total pipeline latency can reach 6–10 seconds depending on network conditions.
- **Impact**:
  Can make the interface feel sluggish if feedback isn't provided.
- **How It Was Handled**:
  - Granular `st.spinner()` status banners communicate exactly which phase is currently processing:
    - *"🔮 Rewriting your prompt with the R-C-T-F-C framework…"*
    - *"⚡ Running both prompts through Gemini for comparison…"*
    - *"🏆 Scoring both prompts with the Gemini judge…"*
  - Default model is pinned to `gemini-2.5-flash`, providing fast responses without sacrificing reasoning quality.

---

## 5. Accidental Submission of PII / Sensitive Data

- **Observed Behavior**:
  Users may inadvertently enter email addresses, contact details, or credentials into prompt textareas.
- **Impact**:
  Exposure of personally identifiable information to external third-party model APIs.
- **How It Was Handled**:
  - Added an inline pre-submission regex scanner (`detect_pii`) in [`utils.py`](../utils.py).
  - Flags prospective email addresses or phone numbers with a visual amber alert box before the user clicks "Improve My Prompt".
  - Prominent Responsible Use expander and persistent footer disclaimers remind users not to enter confidential data.
