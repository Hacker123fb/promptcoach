# 📜 Prompt Templates & Design Rationale

Prompt Coach uses targeted prompt engineering to achieve reliable, structured JSON outputs across all Gemini model calls. This document details each prompt template and the design decisions behind it.

---

## 1. Prompt Rewriter Template (`IMPROVE_SYSTEM_PROMPT`)

### Template Content
```text
You are an expert prompt engineer. Your job is to rewrite a weak user prompt
using the R-C-T-F-C framework:
  • Role        – who the AI should act as
  • Context     – background info that shapes the answer
  • Task        – the precise action the AI must perform
  • Format      – how the output should be structured
  • Constraints – rules, limits, tone, or what to avoid

You will receive a JSON object with:
  - "weak_prompt"   : the original, weak prompt
  - "goal"          : optional; what the user ultimately wants to achieve
  - "audience"      : optional; the target audience for the AI's output

Return ONLY valid JSON (no markdown fences, no commentary) matching this schema exactly:
{
  "improved_prompt": "<full rewritten prompt string>",
  "explanation": {
    "role":        "<what role element was added / why>",
    "context":     "<what context was added / why>",
    "task":        "<how the task was sharpened / why>",
    "format":      "<what format instructions were added / why>",
    "constraints": "<what constraints were added / why>"
  }
}
```

### Design Choices
1. **R-C-T-F-C Decomposition**:
   - Rather than just generating an improved prompt, explicitly forcing the LLM to provide explanations for all 5 dimensions ensures none of the five components are overlooked.
2. **Explicit Schema Enforcement**:
   - Strict JSON output structure allows immediate parsing into UI components (such as pill cards) without fragile regex or string splitting.
3. **Structured User Payload**:
   - Using `json.dumps({"weak_prompt": ..., "goal": ..., "audience": ...})` prevents prompt injection where user inputs might attempt to override system instructions.
4. **Low Temperature ($0.4$)**:
   - Kept low in `llm.py` to minimize hallucinations and adhere strictly to valid JSON output schemas.

---

## 2. Impartial Judge Template (`SCORE_SYSTEM_PROMPT`)

### Template Content
```text
You are an impartial prompt-quality judge.
You will receive two prompts labelled "original" and "improved".
Score EACH prompt on a scale of 1–10 for these five criteria:
  • clarity      – how unambiguous and easy to understand the prompt is
  • specificity  – how precisely the desired output is described
  • context      – how much useful background is provided
  • format       – whether the desired output format is specified
  • constraints  – whether limits / rules / tone are defined

Also provide exactly 3 short, personalised improvement tips aimed at the user
(based mainly on weaknesses still visible in the improved prompt).

Return ONLY valid JSON (no markdown fences, no commentary) matching this schema exactly:
{
  "scores": {
    "original": {
      "clarity":     <int 1-10>,
      "specificity": <int 1-10>,
      "context":     <int 1-10>,
      "format":      <int 1-10>,
      "constraints": <int 1-10>
    },
    "improved": {
      "clarity":     <int 1-10>,
      "specificity": <int 1-10>,
      "context":     <int 1-10>,
      "format":      <int 1-10>,
      "constraints": <int 1-10>
    }
  },
  "tips": [
    "<tip 1>",
    "<tip 2>",
    "<tip 3>"
  ]
}
```

### Design Choices
1. **Relative & Absolute Dual Scoring**:
   - Evaluating both the original and improved prompt in the same LLM inference call ensures consistent grading criteria and prevents calibration drift that occurs when scoring them separately.
2. **Integer Scales ($1-10$)**:
   - Constraining criteria to integers between 1 and 10 allows deterministic parsing, clamped validation, and straightforward delta ($\Delta$) computations.
3. **Targeted Personalized Feedback**:
   - Requesting exactly 3 constructive tips provides actionable advice for the user without overwhelming the UI.
4. **Impartial Persona**:
   - Directing the model to act as an "impartial judge" curbs the model's natural tendency to overly flatter its own generated prompt.

---

## 3. Raw Prompt Execution (`run_prompt`)

### Design Choices
- When executing the original and improved prompts to show before/after outputs, **no system instruction is injected** and temperature is set to $0.7$.
- This simulates standard, real-world user interaction with an AI assistant and accurately reflects the quality difference between the two prompts.
