"""
Prompt Coach – Streamlit UI (app.py)

Run with:  streamlit run app.py
"""

import re
import io
import os
from datetime import datetime

import streamlit as st
import pandas as pd

# ── Page config (MUST be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Prompt Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Global background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(10, 8, 30, 0.92) !important;
    border-right: 1px solid rgba(167,139,250,0.15) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebarContent"] { padding-top: 1.5rem; }

/* ── Banner ── */
.banner {
    background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(79,70,229,0.12));
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    backdrop-filter: blur(12px);
}
.banner h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.35rem 0;
    line-height: 1.1;
}
.banner .tagline {
    color: #94a3b8;
    font-size: 1.05rem;
    margin: 0;
}
.banner .framework-tags {
    margin-top: 0.9rem;
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.ftag {
    background: rgba(167,139,250,0.12);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #c4b5fd;
    letter-spacing: 0.06em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 0.3rem;
    gap: 0.25rem;
    border: 1px solid rgba(255,255,255,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 0.5rem 1.4rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    background: transparent !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.4) !important;
}

/* ── Glass cards ── */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(10px);
}

/* ── Section labels ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.6rem;
}

/* ── Chip / example buttons ── */
.stButton > button {
    border-radius: 999px !important;
    font-size: 0.82rem !important;
    padding: 0.3rem 0.9rem !important;
    border: 1px solid rgba(167,139,250,0.35) !important;
    background: rgba(167,139,250,0.07) !important;
    color: #c4b5fd !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: rgba(167,139,250,0.22) !important;
    border-color: #a78bfa !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(167,139,250,0.25) !important;
}

/* ── Primary button ── */
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
    color: white !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 2.2rem !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    box-shadow: 0 6px 28px rgba(124,58,237,0.6) !important;
    transform: translateY(-2px) !important;
}

/* ── Text areas & inputs ── */
textarea, .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.3) !important;
}

/* ── Framework pills ── */
.framework-pill {
    background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(79,70,229,0.18));
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin: 0.3rem 0;
    width: 100%;
}
.pill-title {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a78bfa;
}
.pill-body {
    font-size: 0.88rem;
    color: #e2e8f0;
    margin-top: 0.25rem;
    line-height: 1.5;
}

/* ── Before/after response boxes ── */
.response-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.2rem;
    min-height: 180px;
    color: #cbd5e1;
    font-size: 0.88rem;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-y: auto;
    max-height: 400px;
}
.response-label-bad  { color: #f87171; font-weight: 600; margin-bottom: 0.5rem; }
.response-label-good { color: #34d399; font-weight: 600; margin-bottom: 0.5rem; }

/* ── Score badges ── */
.score-badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
}
.score-low  { background: rgba(239,68,68,0.18);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.5); }
.score-mid  { background: rgba(251,191,36,0.18); color: #fde68a; border: 1px solid rgba(251,191,36,0.5); }
.score-high { background: rgba(52,211,153,0.18); color: #6ee7b7; border: 1px solid rgba(52,211,153,0.5); }

/* ── Custom progress bar ── */
.prog-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0.45rem 0;
}
.prog-label {
    width: 100px;
    font-size: 0.83rem;
    color: #94a3b8;
    flex-shrink: 0;
}
.prog-track {
    flex: 1;
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
    height: 7px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}
.prog-value {
    width: 36px;
    text-align: right;
    font-size: 0.82rem;
    font-weight: 600;
    flex-shrink: 0;
}

/* ── Tips ── */
.tip-box {
    background: rgba(52,211,153,0.07);
    border-left: 3px solid #34d399;
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    color: #a7f3d0;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── History card ── */
.hist-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.hist-meta {
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 0.4rem;
}
.hist-prompt {
    font-size: 0.9rem;
    color: #e2e8f0;
    font-style: italic;
}

/* ── PII warning ── */
.pii-warn {
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.4);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    color: #fde68a;
    font-size: 0.88rem;
    margin-bottom: 0.8rem;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 0.8rem;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ── DataFrames ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Expander ── */
details > summary {
    color: #a78bfa !important;
    font-weight: 600 !important;
}

/* ── Sidebar section headers ── */
.sb-header {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c3aed;
    margin: 1rem 0 0.4rem;
}
.sb-model-badge {
    display: inline-block;
    background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 8px;
    padding: 0.35rem 0.8rem;
    font-size: 0.8rem;
    color: #c4b5fd;
    font-weight: 600;
    font-family: 'Courier New', monospace;
    word-break: break-all;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Eval domain badge ── */
.domain-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.35);
    color: #93c5fd;
}
</style>
""", unsafe_allow_html=True)

# ── Deferred imports ────────────────────────────────────────────────────────
from prompts import EXAMPLE_PROMPTS
from llm import improve_prompt, run_prompt, get_client
from scoring import run_scoring, CRITERIA
from evaluation import TEST_PROMPTS, run_single_eval, results_to_df
from utils import detect_pii, get_model_name

# ── Helper: score badge HTML ────────────────────────────────────────────────
def score_badge(val: int, *, show_of_ten: bool = True) -> str:
    if show_of_ten:
        cls = "score-low" if val <= 4 else ("score-mid" if val <= 7 else "score-high")
        label = f"{val}/10"
    else:
        cls = "score-low" if val <= 20 else ("score-mid" if val <= 35 else "score-high")
        label = f"{val}/50"
    return f'<span class="score-badge {cls}">{label}</span>'

# ── Helper: coloured progress bar HTML ─────────────────────────────────────
def prog_bar(label: str, value: int, max_val: int = 10) -> str:
    pct = (value / max_val) * 100
    color = "#ef4444" if value <= 4 else ("#f59e0b" if value <= 7 else "#10b981")
    return f"""
<div class="prog-row">
  <span class="prog-label">{label}</span>
  <div class="prog-track">
    <div class="prog-fill" style="width:{pct}%;background:{color};"></div>
  </div>
  <span class="prog-value" style="color:{color};">{value}</span>
</div>"""

# ── API key validation ──────────────────────────────────────────────────────
try:
    get_client()
except EnvironmentError as e:
    st.error(f"⚠️ **Configuration Error:** {e}")
    st.info("Create a `.env` file in the project root:\n```\nGEMINI_API_KEY=your_key_here\n```")
    st.stop()
except ImportError as e:
    st.error(f"⚠️ **Missing dependency:** {e}")
    st.stop()

# ── Session state defaults ──────────────────────────────────────────────────
_defaults = {
    "weak_prompt":       "",
    "goal":              "",
    "audience":          "",
    "improvement":       None,
    "original_response": None,
    "improved_response": None,
    "scoring_result":    None,
    "history":           [],          # list of dicts for History tab
    "eval_results":      [],          # list of EvalResult for Evaluation tab
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎯 Prompt Coach")
    st.markdown("---")

    st.markdown('<p class="sb-header">📌 About</p>', unsafe_allow_html=True)
    st.markdown(
        "Prompt Coach helps you write better AI prompts by applying the "
        "**R-C-T-F-C framework** — structuring prompts with Role, Context, "
        "Task, Format, and Constraints."
    )

    st.markdown('<p class="sb-header">⚙️ How It Works</p>', unsafe_allow_html=True)
    st.markdown(
        "1. **Type** a weak prompt\n"
        "2. **Gemini** rewrites it with R-C-T-F-C\n"
        "3. Both prompts are **run** side-by-side\n"
        "4. An **AI judge** scores and tips you\n"
        "5. Each session is saved in **History**"
    )

    st.markdown('<p class="sb-header">🤖 Active Model</p>', unsafe_allow_html=True)
    model_name = get_model_name()
    st.markdown(f'<span class="sb-model-badge">{model_name}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="sb-header">📊 Session Stats</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Runs", len(st.session_state.history))
    with col_b:
        avg_imp = (
            sum(h["improvement"] for h in st.session_state.history) / len(st.session_state.history)
            if st.session_state.history else 0
        )
        st.metric("Avg Δ", f"+{avg_imp:.1f}" if avg_imp > 0 else "—")

    st.markdown("---")
    st.caption("Built with Streamlit + Google Gemini")

# ══════════════════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="banner">
  <h1>🎯 Prompt Coach</h1>
  <p class="tagline">Transform weak prompts into powerful ones — see the difference instantly</p>
  <div class="framework-tags">
    <span class="ftag">🎭 Role</span>
    <span class="ftag">🌍 Context</span>
    <span class="ftag">📋 Task</span>
    <span class="ftag">📐 Format</span>
    <span class="ftag">🔒 Constraints</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════
tab_coach, tab_history, tab_eval = st.tabs(
    ["🎯  Coach", "📜  History", "🧪  Evaluation"]
)

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — COACH
# ══════════════════════════════════════════════════════════════════════════
with tab_coach:

    # ── Responsible use expander ──────────────────────────────────────────
    with st.expander("⚠️ Responsible Use — please read before submitting"):
        st.markdown("""
**Important notices:**
- 🤖 AI outputs (including improved prompts and scores) can be **inaccurate or biased**. Always review results critically.
- 🔒 **Do not enter personal or sensitive information** — including names, passwords, financial data, or medical details.
- 📊 Scores come from an **AI judge** and are indicative, not absolute measures of quality.
- 🌐 Your inputs are sent to **Google Gemini** via the API and are subject to Google's data policies.
- 🧠 This tool is for **learning and experimentation** — treat improved prompts as starting points, not final outputs.
        """)

    # ── Input card ───────────────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">✍️ Your Weak Prompt</p>', unsafe_allow_html=True)

    # Example chips
    st.markdown("**Try an example:**")
    chip_cols = st.columns(len(EXAMPLE_PROMPTS))
    for col, ex in zip(chip_cols, EXAMPLE_PROMPTS):
        with col:
            if st.button(ex, key=f"chip_{ex}"):
                st.session_state.weak_prompt      = ex
                st.session_state.improvement      = None
                st.session_state.original_response = None
                st.session_state.improved_response = None
                st.session_state.scoring_result   = None
                st.rerun()

    weak_prompt = st.text_area(
        "Prompt",
        value=st.session_state.weak_prompt,
        height=110,
        placeholder="e.g. write about climate change",
        label_visibility="collapsed",
        key="prompt_textarea",
    )
    st.session_state.weak_prompt = weak_prompt

    # PII warning
    pii_hits = detect_pii(weak_prompt)
    if pii_hits:
        st.markdown(
            f'<div class="pii-warn">⚠️ <strong>Possible sensitive data detected</strong>: '
            f'your input may contain a <strong>{" and ".join(pii_hits)}</strong>. '
            f'Please remove personal information before submitting.</div>',
            unsafe_allow_html=True,
        )

    # Optional fields
    oc1, oc2 = st.columns(2)
    with oc1:
        goal = st.text_input(
            "🎯 Goal (optional)",
            value=st.session_state.goal,
            placeholder="e.g. understand basics for a school project",
            key="goal_input",
        )
        st.session_state.goal = goal
    with oc2:
        audience = st.text_input(
            "👥 Target Audience (optional)",
            value=st.session_state.audience,
            placeholder="e.g. high-school students",
            key="audience_input",
        )
        st.session_state.audience = audience

    improve_btn = st.button("🚀 Improve My Prompt", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Pipeline ─────────────────────────────────────────────────────────
    if improve_btn:
        if not weak_prompt.strip():
            st.warning("⚠️ Please enter a prompt before clicking **Improve My Prompt**.")
            st.stop()

        st.session_state.improvement       = None
        st.session_state.original_response = None
        st.session_state.improved_response = None
        st.session_state.scoring_result    = None

        # Stage 1 — Rewrite
        with st.spinner("🔮 Rewriting your prompt with the R-C-T-F-C framework…"):
            try:
                improvement = improve_prompt(
                    weak_prompt=weak_prompt, goal=goal, audience=audience
                )
                st.session_state.improvement = improvement
            except Exception as exc:
                st.error(f"❌ **Prompt improvement failed:** {exc}")
                st.stop()

        improved_text = st.session_state.improvement["improved_prompt"]

        # Stage 2 — Run both
        with st.spinner("⚡ Running both prompts through Gemini for comparison…"):
            errs = []
            try:
                st.session_state.original_response = run_prompt(weak_prompt)
            except Exception as exc:
                errs.append(f"Original prompt run failed: {exc}")
                st.session_state.original_response = f"[Error] {exc}"
            try:
                st.session_state.improved_response = run_prompt(improved_text)
            except Exception as exc:
                errs.append(f"Improved prompt run failed: {exc}")
                st.session_state.improved_response = f"[Error] {exc}"
            if errs:
                st.warning("\n\n".join(errs))

        # Stage 3 — Score
        with st.spinner("🏆 Scoring both prompts with the Gemini judge…"):
            try:
                scoring_result = run_scoring(weak_prompt, improved_text)
                st.session_state.scoring_result = scoring_result
            except Exception as exc:
                st.error(f"❌ **Scoring failed:** {exc}")

        # Save to history
        sr = st.session_state.scoring_result
        st.session_state.history.append({
            "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_prompt": weak_prompt,
            "improved_prompt": improved_text,
            "goal":            goal,
            "audience":        audience,
            "original_total":  sr.original.total if sr else 0,
            "improved_total":  sr.improved.total if sr else 0,
            "improvement":     (sr.improved.total - sr.original.total) if sr else 0,
        })

    # ── Results ──────────────────────────────────────────────────────────
    if st.session_state.improvement:
        improvement   = st.session_state.improvement
        improved_text = improvement["improved_prompt"]
        explanation   = improvement.get("explanation", {})

        st.markdown("---")

        # ── Improved prompt + Copy ────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">✨ Improved Prompt</p>', unsafe_allow_html=True)
        st.markdown(
            "👇 **Copy** the improved prompt with the button in the top-right corner of the code block:",
        )
        st.code(improved_text, language=None)

        # ── R-C-T-F-C breakdown ───────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">🧩 R-C-T-F-C Breakdown</p>', unsafe_allow_html=True)
        for key, (icon, label) in {
            "role":        ("🎭", "Role"),
            "context":     ("🌍", "Context"),
            "task":        ("📋", "Task"),
            "format":      ("📐", "Format"),
            "constraints": ("🔒", "Constraints"),
        }.items():
            text = explanation.get(key, "—")
            st.markdown(
                f'<div class="framework-pill">'
                f'<div class="pill-title">{icon} {label}</div>'
                f'<div class="pill-body">{text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Before / After ────────────────────────────────────────────────
        if (
            st.session_state.original_response is not None
            or st.session_state.improved_response is not None
        ):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(
                '<p class="section-label">🔬 Before / After AI Responses</p>',
                unsafe_allow_html=True,
            )
            col_orig, col_impr = st.columns(2)
            with col_orig:
                st.markdown(
                    '<p class="response-label-bad">❌ Weak Prompt Response</p>',
                    unsafe_allow_html=True,
                )
                orig_text = st.session_state.original_response or ""
                st.markdown(
                    f'<div class="response-box">{orig_text}</div>',
                    unsafe_allow_html=True,
                )
            with col_impr:
                st.markdown(
                    '<p class="response-label-good">✅ Improved Prompt Response</p>',
                    unsafe_allow_html=True,
                )
                impr_text = st.session_state.improved_response or ""
                st.markdown(
                    f'<div class="response-box">{impr_text}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Scores ───────────────────────────────────────────────────────
        if st.session_state.scoring_result:
            result = st.session_state.scoring_result

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(
                '<p class="section-label">📊 Prompt Quality Scores</p>',
                unsafe_allow_html=True,
            )

            # Total metrics
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("Original Score", f"{result.original.total} / 50")
            with mc2:
                delta = result.improved.total - result.original.total
                st.metric(
                    "Improved Score",
                    f"{result.improved.total} / 50",
                    delta=f"+{delta}" if delta >= 0 else str(delta),
                )
            with mc3:
                pct_gain = (delta / max(result.original.total, 1)) * 100
                st.metric("Score Gain", f"+{pct_gain:.0f}%")

            st.markdown("<br>", unsafe_allow_html=True)

            # Per-criterion progress bars side by side
            pb_col1, pb_col2 = st.columns(2)
            criteria_display = [c.capitalize() for c in CRITERIA]

            with pb_col1:
                st.markdown(
                    '<p style="color:#f87171;font-size:0.82rem;font-weight:600;margin-bottom:0.5rem;">'
                    '❌ Original — per criterion</p>',
                    unsafe_allow_html=True,
                )
                bars_html = ""
                for c, label in zip(CRITERIA, criteria_display):
                    bars_html += prog_bar(label, getattr(result.original, c))
                st.markdown(bars_html, unsafe_allow_html=True)

            with pb_col2:
                st.markdown(
                    '<p style="color:#34d399;font-size:0.82rem;font-weight:600;margin-bottom:0.5rem;">'
                    '✅ Improved — per criterion</p>',
                    unsafe_allow_html=True,
                )
                bars_html = ""
                for c, label in zip(CRITERIA, criteria_display):
                    bars_html += prog_bar(label, getattr(result.improved, c))
                st.markdown(bars_html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Detailed table
            orig_vals = [getattr(result.original, c) for c in CRITERIA]
            impr_vals = [getattr(result.improved, c) for c in CRITERIA]
            df = pd.DataFrame({
                "Criterion": criteria_display + ["Total"],
                "Original":  orig_vals + [result.original.total],
                "Improved":  impr_vals + [result.improved.total],
            })
            df["Δ"] = df["Improved"] - df["Original"]
            df["Δ"] = df["Δ"].apply(lambda x: f"+{x}" if x > 0 else str(x))

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Criterion": st.column_config.TextColumn("Criterion", width="medium"),
                    "Original":  st.column_config.NumberColumn("Original (/10)", format="%d"),
                    "Improved":  st.column_config.NumberColumn("Improved (/10)", format="%d"),
                    "Δ":         st.column_config.TextColumn("Δ", width="small"),
                },
            )

            # Tips
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<p class="section-label">💡 Personalised Improvement Tips</p>',
                unsafe_allow_html=True,
            )
            for i, tip in enumerate(result.tips, 1):
                st.markdown(
                    f'<div class="tip-box"><strong>Tip {i}:</strong> {tip}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — HISTORY
# ══════════════════════════════════════════════════════════════════════════
with tab_history:
    history = st.session_state.history

    if not history:
        st.info("No sessions yet. Run the Coach tab to start building your history.")
    else:
        st.markdown(f"### 📜 {len(history)} session(s) this session")

        # Download CSV
        hist_df = pd.DataFrame(history)
        csv_bytes = hist_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download History as CSV",
            data=csv_bytes,
            file_name="prompt_coach_history.csv",
            mime="text/csv",
            key="hist_download",
        )

        st.markdown("---")

        # Show each run newest-first
        for idx, run in enumerate(reversed(history)):
            run_num = len(history) - idx
            delta   = run["improvement"]
            delta_str = f"+{delta}" if delta >= 0 else str(delta)
            badge_html = score_badge(run["original_total"], show_of_ten=False)
            badge_html_imp = score_badge(run["improved_total"], show_of_ten=False)

            with st.expander(
                f"Run #{run_num} · {run['timestamp']} · "
                f"Original: {run['original_total']}/50 → Improved: {run['improved_total']}/50 (Δ {delta_str})",
                expanded=(idx == 0),
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original Prompt**")
                    st.markdown(
                        f'<div class="hist-prompt">"{run["original_prompt"]}"</div>',
                        unsafe_allow_html=True,
                    )
                    if run.get("goal"):
                        st.caption(f"Goal: {run['goal']}")
                    if run.get("audience"):
                        st.caption(f"Audience: {run['audience']}")
                    st.markdown(
                        f"Score: {badge_html}", unsafe_allow_html=True
                    )
                with c2:
                    st.markdown("**Improved Prompt**")
                    st.code(run["improved_prompt"], language=None)
                    st.markdown(
                        f"Score: {badge_html_imp}", unsafe_allow_html=True
                    )

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — EVALUATION
# ══════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("### 🧪 Built-in Evaluation Suite")
    st.markdown(
        "Run all **10 diverse weak prompts** through the full Coach pipeline. "
        "Each prompt is improved and scored so you can measure the framework's impact."
    )

    # Test set preview table
    preview_df = pd.DataFrame(TEST_PROMPTS).rename(
        columns={"domain": "Domain", "weak_prompt": "Weak Prompt"}
    )
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

    run_eval_btn = st.button("▶️ Run Evaluation on All 10 Prompts", type="primary", key="eval_btn")

    if run_eval_btn:
        st.session_state.eval_results = []
        prog = st.progress(0.0, text="Starting evaluation…")
        status_placeholder = st.empty()

        for i, item in enumerate(TEST_PROMPTS):
            status_placeholder.markdown(
                f"⚙️ Processing **{i+1}/10** — *{item['domain']}*: `{item['weak_prompt']}`"
            )
            result = run_single_eval(item["domain"], item["weak_prompt"])
            st.session_state.eval_results.append(result)
            prog.progress((i + 1) / len(TEST_PROMPTS), text=f"{i+1}/10 complete")

        prog.empty()
        status_placeholder.empty()
        st.success("✅ Evaluation complete!")

    if st.session_state.eval_results:
        results = st.session_state.eval_results
        df = results_to_df(results)

        st.markdown("---")
        st.markdown("#### 📊 Results")

        # Summary metrics
        valid = [r for r in results if not r.error]
        if valid:
            avg_orig = sum(r.original_total for r in valid) / len(valid)
            avg_impr = sum(r.improved_total for r in valid) / len(valid)
            avg_delta = sum(r.improvement for r in valid) / len(valid)
            max_delta = max(r.improvement for r in valid)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Avg Original", f"{avg_orig:.1f}/50")
            with m2:
                st.metric("Avg Improved", f"{avg_impr:.1f}/50")
            with m3:
                st.metric("Avg Δ", f"+{avg_delta:.1f}")
            with m4:
                st.metric("Best Δ", f"+{max_delta}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Results table
        display_df = df.drop(columns=["Error"])
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Domain":          st.column_config.TextColumn("Domain", width="small"),
                "Weak Prompt":     st.column_config.TextColumn("Weak Prompt", width="medium"),
                "Original Score":  st.column_config.NumberColumn("Original (/50)", format="%d"),
                "Improved Score":  st.column_config.NumberColumn("Improved (/50)", format="%d"),
                "Improvement (Δ)": st.column_config.NumberColumn("Δ", format="+%d"),
            },
        )

        # Errors (if any)
        err_rows = df[df["Error"] != ""]
        if not err_rows.empty:
            with st.expander(f"⚠️ {len(err_rows)} error(s) during evaluation"):
                st.dataframe(err_rows[["Domain", "Weak Prompt", "Error"]], use_container_width=True)

        # Bar chart — before vs after per domain
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📈 Before vs After — Score Comparison")

        if valid:
            chart_df = pd.DataFrame({
                "Domain":   [r.domain for r in valid],
                "Original": [r.original_total for r in valid],
                "Improved": [r.improved_total for r in valid],
            }).set_index("Domain")

            st.bar_chart(chart_df, color=["#f87171", "#34d399"])

        # CSV download
        csv_eval = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Evaluation Results as CSV",
            data=csv_eval,
            file_name="prompt_coach_evaluation.csv",
            mime="text/csv",
            key="eval_download",
        )

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#475569;font-size:0.78rem;'>"
    "⚠️ AI outputs can be inaccurate or biased — do not enter personal or sensitive information — "
    "scores are from an AI judge and are indicative, not absolute. &nbsp;|&nbsp; "
    "Prompt Coach · Powered by Google Gemini · R-C-T-F-C Framework"
    "</p>",
    unsafe_allow_html=True,
)
