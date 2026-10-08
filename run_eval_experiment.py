"""
run_eval_experiment.py — Collects empirical benchmark and example data for PROJECT_DETAILS.md
"""

import json
import time
from datetime import datetime
from evaluation import TEST_PROMPTS, run_single_eval
from llm import improve_prompt, run_prompt
from scoring import run_scoring
from utils import get_model_name

model = get_model_name()
print(f"Starting experiments with model: {model} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

data_store = {
    "model": model,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "run1": [],
    "run2": [],
    "cases": []
}

def save_checkpoint():
    with open("eval_data.json", "w", encoding="utf-8") as f:
        json.dump(data_store, f, indent=2, ensure_ascii=False)

# 1. Benchmark Run 1
print("\n--- BENCHMARK RUN 1 ---", flush=True)
for i, item in enumerate(TEST_PROMPTS, 1):
    print(f"Run 1 [{i}/10]: {item['domain']} - '{item['weak_prompt']}'", flush=True)
    res = run_single_eval(item['domain'], item['weak_prompt'], model=model)
    data_store["run1"].append({
        "domain": res.domain,
        "weak_prompt": res.weak_prompt,
        "improved_prompt": res.improved_prompt,
        "original_score": res.original_total,
        "improved_score": res.improved_total,
        "improvement": res.improvement,
        "error": res.error
    })
    save_checkpoint()
    time.sleep(1.5)

# 2. Benchmark Run 2
print("\n--- BENCHMARK RUN 2 (Consistency Check) ---", flush=True)
for i, item in enumerate(TEST_PROMPTS, 1):
    print(f"Run 2 [{i}/10]: {item['domain']} - '{item['weak_prompt']}'", flush=True)
    res = run_single_eval(item['domain'], item['weak_prompt'], model=model)
    data_store["run2"].append({
        "domain": res.domain,
        "weak_prompt": res.weak_prompt,
        "improved_prompt": res.improved_prompt,
        "original_score": res.original_total,
        "improved_score": res.improved_total,
        "improvement": res.improvement,
        "error": res.error
    })
    save_checkpoint()
    time.sleep(1.5)

# 3. 3 Detailed Case Study Runs
print("\n--- CASE STUDIES (3 Examples) ---", flush=True)
cases = [
    {
        "domain": "Environmental Science",
        "weak_prompt": "write about climate change",
        "goal": "High school science project overview",
        "audience": "10th grade biology students"
    },
    {
        "domain": "Software Engineering",
        "weak_prompt": "write python code",
        "goal": "Create a thread-safe in-memory LRU cache",
        "audience": "Senior Backend Engineers"
    },
    {
        "domain": "Career Development",
        "weak_prompt": "write a cover letter",
        "goal": "Apply for a Junior Machine Learning Engineer role",
        "audience": "AI Startup Hiring Team"
    }
]

for idx, c in enumerate(cases, 1):
    print(f"Case {idx}: {c['domain']} - '{c['weak_prompt']}'", flush=True)
    try:
        impr = improve_prompt(c['weak_prompt'], goal=c['goal'], audience=c['audience'], model=model)
        improved_text = impr['improved_prompt']
        orig_output = run_prompt(c['weak_prompt'], model=model)
        impr_output = run_prompt(improved_text, model=model)
        scores = run_scoring(c['weak_prompt'], improved_text, model=model)

        data_store["cases"].append({
            "domain": c['domain'],
            "weak_prompt": c['weak_prompt'],
            "goal": c['goal'],
            "audience": c['audience'],
            "improved_prompt": improved_text,
            "original_total": scores.original.total,
            "improved_total": scores.improved.total,
            "original_breakdown": scores.original.as_dict(),
            "improved_breakdown": scores.improved.as_dict(),
            "tips": scores.tips,
            "orig_output": orig_output,
            "impr_output": impr_output
        })
        save_checkpoint()
    except Exception as exc:
        print(f"Case {idx} error: {exc}", flush=True)
    time.sleep(1.5)

print("\nAll experiment data successfully written to eval_data.json!", flush=True)
