"""
All prompt templates used by Prompt Coach, as module-level constants.
Never put logic here – only string templates.
"""

# ---------------------------------------------------------------------------
# System / instruction prompt for the prompt-improvement call
# ---------------------------------------------------------------------------
IMPROVE_SYSTEM_PROMPT = """You are an expert prompt engineer. Your job is to rewrite a weak user prompt
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
}"""

# ---------------------------------------------------------------------------
# System / instruction prompt for the scoring (judge) call
# ---------------------------------------------------------------------------
SCORE_SYSTEM_PROMPT = """You are an impartial prompt-quality judge.
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
}"""

# ---------------------------------------------------------------------------
# User-message template for the improvement call
# ---------------------------------------------------------------------------
def build_improve_user_message(weak_prompt: str, goal: str, audience: str) -> str:
    import json
    payload = {"weak_prompt": weak_prompt}
    if goal.strip():
        payload["goal"] = goal.strip()
    if audience.strip():
        payload["audience"] = audience.strip()
    return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# User-message template for the scoring call
# ---------------------------------------------------------------------------
def build_score_user_message(original: str, improved: str) -> str:
    import json
    return json.dumps({"original": original, "improved": improved}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Example weak prompts shown on the input screen
# ---------------------------------------------------------------------------
EXAMPLE_PROMPTS = [
    "write about climate change",
    "explain machine learning",
    "help me with my email",
    "write a cover letter",
    "give me a workout plan",
]
