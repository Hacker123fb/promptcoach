"""
Prompt Coach – Streamlit UI (app.py)
Interactive AI Prompt Engineering Studio using the R-C-T-F-C Framework.
"""

import io
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st

# ── Page config (MUST be the first Streamlit command) ────────────────────────
st.set_page_config(
    page_title="Prompt Coach — AI Prompt Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Deferred imports ────────────────────────────────────────────────────────
from prompts import EXAMPLE_PROMPTS
from llm import improve_prompt, run_prompt, get_client
from scoring import run_scoring, CRITERIA
from evaluation import TEST_PROMPTS, run_single_eval, results_to_df
from utils import detect_pii, get_model_name, get_api_key

# ── Custom CSS for Ultra-Modern UI & Interactivity ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Global Dark Ambient Background ── */
.stApp {
    background: radial-gradient(circle at 15% 15%, rgba(124, 58, 237, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(14, 165, 233, 0.12) 0%, transparent 45%),
                linear-gradient(135deg, #0b0914 0%, #131127 50%, #171530 100%);
    min-height: 100vh;
}

/* ── Sidebar Redesign ── */
[data-testid="stSidebar"] {
    background: rgba(13, 11, 28, 0.95) !important;
    border-right: 1px solid rgba(167, 139, 250, 0.18) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0;
}
[data-testid="stSidebarContent"] {
    padding: 1.5rem 1rem !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.22) 0%, rgba(99, 102, 241, 0.15) 50%, rgba(14, 165, 233, 0.12) 100%);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 24px;
    padding: 2.2rem 2rem 1.8rem;
    margin-bottom: 1.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(167, 139, 250, 0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-banner h1 {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #c4b5fd 0%, #93c5fd 50%, #6ee7b7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem 0;
}
.hero-banner .hero-sub {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 400;
    max-width: 680px;
    margin: 0 auto;
}
.hero-tags {
    margin-top: 1.1rem;
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    flex-wrap: wrap;
}
.htag {
    background: rgba(167, 139, 250, 0.12);
    border: 1px solid rgba(167, 139, 250, 0.35);
    border-radius: 999px;
    padding: 0.3rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: #ddd6fe;
    letter-spacing: 0.05em;
    transition: all 0.25s ease;
}
.htag:hover {
    background: rgba(167, 139, 250, 0.25);
    transform: translateY(-2px);
}

/* ── Modern Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    padding: 0.35rem;
    gap: 0.35rem;
    border: 1px solid rgba(255, 255, 255, 0.09);
    margin-bottom: 1.2rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 0.55rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: #94a3b8 !important;
    background: transparent !important;
    transition: all 0.25s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #e2e8f0 !important;
    background: rgba(255, 255, 255, 0.06) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.45) !important;
}

/* ── Glass Cards ── */
.glass-panel {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 18px;
    padding: 1.6rem;
    margin-bottom: 1.3rem;
    backdrop-filter: blur(14px);
    transition: border-color 0.3s ease;
}
.glass-panel:hover {
    border-color: rgba(167, 139, 250, 0.25);
}

.panel-title {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Interactive Buttons & Chips ── */
.stButton > button {
    border-radius: 999px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 1rem !important;
    border: 1px solid rgba(167, 139, 250, 0.35) !important;
    background: rgba(167, 139, 250, 0.09) !important;
    color: #c4b5fd !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: rgba(167, 139, 250, 0.26) !important;
    border-color: #a78bfa !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(124, 58, 237, 0.3) !important;
}

/* ── Primary Action Button ── */
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: #ffffff !important;
    font-size: 1.02rem !important;
    font-weight: 700 !important;
    padding: 0.7rem 2.4rem !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 24px rgba(124, 58, 237, 0.45) !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.65) !important;
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
}

/* ── Inputs ── */
textarea, .stTextInput input, .stSelectbox select {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    color: #f1f5f9 !important;
    border-radius: 12px !important;
    font-size: 0.94rem !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.35) !important;
}

/* ── Framework Breakdown Pills ── */
.framework-card {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(79, 70, 229, 0.15) 100%);
    border: 1px solid rgba(124, 58, 237, 0.35);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin: 0.4rem 0;
}
.framework-card .fc-header {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #c4b5fd;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.framework-card .fc-content {
    font-size: 0.9rem;
    color: #f1f5f9;
    margin-top: 0.3rem;
    line-height: 1.55;
}

/* ── Comparison Response Boxes ── */
.comp-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 14px;
    padding: 1.3rem;
    min-height: 220px;
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-y: auto;
    max-height: 440px;
}
.comp-label-red {
    color: #f87171;
    font-weight: 700;
    font-size: 0.88rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.comp-label-green {
    color: #34d399;
    font-weight: 700;
    font-size: 0.88rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Score Badges & Meters ── */
.score-badge {
    display: inline-block;
    padding: 0.25rem 0.85rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
}
.score-low  { background: rgba(239, 68, 68, 0.18);  color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.45); }
.score-mid  { background: rgba(251, 191, 36, 0.18); color: #fde68a; border: 1px solid rgba(251, 191, 36, 0.45); }
.score-high { background: rgba(52, 211, 153, 0.18); color: #6ee7b7; border: 1px solid rgba(52, 211, 153, 0.45); }

/* ── Dynamic Progress Bars ── */
.bar-row {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 0.55rem 0;
}
.bar-lbl {
    width: 105px;
    font-size: 0.84rem;
    color: #94a3b8;
    flex-shrink: 0;
    font-weight: 500;
}
.bar-track {
    flex: 1;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}
.bar-val {
    width: 42px;
    text-align: right;
    font-size: 0.84rem;
    font-weight: 700;
    flex-shrink: 0;
}

/* ── Tip Cards ── */
.tip-card {
    background: rgba(52, 211, 153, 0.07);
    border-left: 3px solid #34d399;
    border-radius: 0 12px 12px 0;
    padding: 0.85rem 1.1rem;
    margin: 0.5rem 0;
    color: #a7f3d0;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── PII Warning Box ── */
.pii-box {
    background: rgba(251, 191, 36, 0.12);
    border: 1px solid rgba(251, 191, 36, 0.4);
    border-radius: 12px;
    padding: 0.85rem 1.1rem;
    color: #fde68a;
    font-size: 0.9rem;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Sidebar Cards ── */
.sb-card {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.sb-heading {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.5rem;
}
.sb-status {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: #34d399;
    background: rgba(52, 211, 153, 0.12);
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    border: 1px solid rgba(52, 211, 153, 0.3);
}

/* ── History Card ── */
.history-entry {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.9rem;
    transition: all 0.2s ease;
}
.history-entry:hover {
    border-color: rgba(167, 139, 250, 0.3);
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    padding: 0.9rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
""", unsafe_allow_html=True)

# ── Session State Management ────────────────────────────────────────────────
if "prompt_input" not in st.session_state:
    st.session_state["prompt_input"] = ""
if "goal_input" not in st.session_state:
    st.session_state["goal_input"] = ""
if "audience_input" not in st.session_state:
    st.session_state["audience_input"] = ""
if "improvement" not in st.session_state:
    st.session_state["improvement"] = None
if "original_response" not in st.session_state:
    st.session_state["original_response"] = None
if "improved_response" not in st.session_state:
    st.session_state["improved_response"] = None
if "scoring_result" not in st.session_state:
    st.session_state["scoring_result"] = None
if "history" not in st.session_state:
    st.session_state["history"] = []
if "eval_results" not in st.session_state:
    st.session_state["eval_results"] = []

# ── Callback Helpers for Rock-Solid Button Interactivity ─────────────────────
def handle_select_example(text: str):
    st.session_state["prompt_input"] = text
    st.session_state["improvement"] = None
    st.session_state["original_response"] = None
    st.session_state["improved_response"] = None
    st.session_state["scoring_result"] = None

def handle_clear_all():
    st.session_state["prompt_input"] = ""
    st.session_state["goal_input"] = ""
    st.session_state["audience_input"] = ""
    st.session_state["improvement"] = None
    st.session_state["original_response"] = None
    st.session_state["improved_response"] = None
    st.session_state["scoring_result"] = None

def handle_apply_scenario(prompt_text: str, goal_text: str, aud_text: str):
    st.session_state["prompt_input"] = prompt_text
    st.session_state["goal_input"] = goal_text
    st.session_state["audience_input"] = aud_text
    st.session_state["improvement"] = None
    st.session_state["original_response"] = None
    st.session_state["improved_response"] = None
    st.session_state["scoring_result"] = None

def handle_clear_history():
    st.session_state["history"] = []

def handle_clear_eval():
    st.session_state["eval_results"] = []

# ── Visual Helpers ──────────────────────────────────────────────────────────
def format_score_badge(val: int, is_out_of_ten: bool = True) -> str:
    if is_out_of_ten:
        cls = "score-low" if val <= 4 else ("score-mid" if val <= 7 else "score-high")
        label = f"{val}/10"
    else:
        cls = "score-low" if val <= 20 else ("score-mid" if val <= 35 else "score-high")
        label = f"{val}/50"
    return f'<span class="score-badge {cls}">{label}</span>'

def render_prog_bar(label: str, value: int, max_val: int = 10) -> str:
    pct = max(0, min(100, int((value / max_val) * 100)))
    color = "#ef4444" if value <= 4 else ("#f59e0b" if value <= 7 else "#10b981")
    return f"""
<div class="bar-row">
  <span class="bar-lbl">{label}</span>
  <div class="bar-track">
    <div class="bar-fill" style="width:{pct}%;background:{color};"></div>
  </div>
  <span class="bar-val" style="color:{color};">{value}</span>
</div>"""

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Comprehensive Interactive Control Panel
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.8rem;">
      <span style="font-size:1.8rem;">🎯</span>
      <div>
        <div style="font-weight:800;font-size:1.2rem;letter-spacing:-0.02em;color:#fff;">Prompt Coach</div>
        <div style="font-size:0.75rem;color:#94a3b8;">AI Engineering Studio</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Active Model & Configuration
    st.markdown('<div class="sb-card">', unsafe_allow_html=True)
    st.markdown('<div class="sb-heading">🤖 Model Engine</div>', unsafe_allow_html=True)
    
    current_default = get_model_name()
    available_models = [
        "gemini-3.5-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-2.5-pro",
    ]
    default_idx = available_models.index(current_default) if current_default in available_models else 0
    
    selected_model = st.selectbox(
        "Active LLM",
        options=available_models,
        index=default_idx,
        help="Select the Gemini model engine for rewriting and evaluation."
    )
    
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.05,
        help="Lower values are more deterministic and structured; higher values allow more creative formulations."
    )

    # API Status Indicator
    api_key_set = bool(get_api_key())
    if api_key_set:
        st.markdown('<div class="sb-status">● API Connected</div>', unsafe_allow_html=True)
    else:
        st.error("⚠️ No API Key found in .env or Secrets")

    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Quick Scenario Presets
    st.markdown('<div class="sb-card">', unsafe_allow_html=True)
    st.markdown('<div class="sb-heading">⚡ One-Click Scenarios</div>', unsafe_allow_html=True)
    st.caption("Auto-load realistic weak prompts & objectives:")

    scenarios = [
        ("🌍 Climate Essay", "write about climate change", "High school science project", "10th grade students"),
        ("💻 Python Code", "write python code for a cache", "Build an LRU cache with TTL expiration", "Senior Backend Engineer"),
        ("📢 Marketing Ad", "write an ad for coffee", "Promote new cold brew blend launch", "Busy young professionals"),
        ("💼 Job Resume", "help me with my resume", "Highlight transition into AI engineering", "Tech hiring managers"),
    ]

    for label, sc_prompt, sc_goal, sc_aud in scenarios:
        st.button(
            label,
            key=f"sc_{label}",
            on_click=handle_apply_scenario,
            args=(sc_prompt, sc_goal, sc_aud),
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Session Statistics
    st.markdown('<div class="sb-card">', unsafe_allow_html=True)
    st.markdown('<div class="sb-heading">📊 Session Dashboard</div>', unsafe_allow_html=True)
    
    history_count = len(st.session_state["history"])
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Total Runs", history_count)
    with col_s2:
        if history_count > 0:
            avg_gain = sum(h["improvement"] for h in st.session_state["history"]) / history_count
            st.metric("Avg Δ Gain", f"+{avg_gain:.1f}")
        else:
            st.metric("Avg Δ Gain", "—")
            
    if history_count > 0:
        st.button("🗑️ Clear History", on_click=handle_clear_history, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. R-C-T-F-C Framework Guide
    with st.expander("📚 R-C-T-F-C Cheat Sheet"):
        st.markdown("""
        - **🎭 Role**: Specify expert persona & perspective.
        - **🌍 Context**: Supply background domain realities.
        - **📋 Task**: Direct with unambiguous action verbs.
        - **📐 Format**: Define tables, sections, or length.
        - **🔒 Constraints**: Set boundaries, rules, and negative prompts.
        """)

    st.caption("Prompt Coach · Powered by Google Gemini")

# ══════════════════════════════════════════════════════════════════════════
# HERO HEADER BANNER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
  <h1>🎯 Prompt Coach</h1>
  <p class="hero-sub">Transform weak, vague instructions into high-precision prompts with instant side-by-side AI comparisons and judge evaluation.</p>
  <div class="hero-tags">
    <span class="htag">🎭 Role</span>
    <span class="htag">🌍 Context</span>
    <span class="htag">📋 Task</span>
    <span class="htag">📐 Format</span>
    <span class="htag">🔒 Constraints</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════
tab_coach, tab_history, tab_eval = st.tabs([
    "🎯 Prompt Coach",
    "📜 Session History",
    "🧪 10-Domain Benchmark",
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1: PROMPT COACH
# ══════════════════════════════════════════════════════════════════════════
with tab_coach:

    # Responsible Use Notice
    with st.expander("🛡️ Responsible Use & Advisory Notice"):
        st.markdown("""
        - 🤖 **Indicative AI Metrics**: Scores are determined by an automated Gemini judge. They represent estimated quality improvement and are not absolute mathematical guarantees.
        - 🔒 **Data Privacy**: Do not submit confidential passwords, proprietary business secrets, or personally identifiable information (PII).
        - 🌐 **Model Outputs**: Generative models may produce biased or inaccurate statements. Always review refined prompts and outputs prior to production use.
        """)

    # Input Box Panel
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title"><span>✍️</span> Input Weak Prompt</div>', unsafe_allow_html=True)

    # Quick Example Chips
    st.caption("Click any example to populate instantly:")
    chip_cols = st.columns(len(EXAMPLE_PROMPTS))
    for col, ex in zip(chip_cols, EXAMPLE_PROMPTS):
        with col:
            st.button(
                ex,
                key=f"ex_btn_{ex}",
                on_click=handle_select_example,
                args=(ex,),
                use_container_width=True
            )

    # Text Area
    weak_prompt_val = st.text_area(
        "Enter your prompt",
        key="prompt_input",
        height=110,
        placeholder="e.g. write about climate change, fix this code, help me with an email...",
        label_visibility="collapsed",
    )

    # PII Scanner Alert
    pii_alerts = detect_pii(weak_prompt_val)
    if pii_alerts:
        st.markdown(
            f'<div class="pii-box">⚠️ <strong>Privacy Warning</strong>: Input appears to contain an '
            f'<strong>{" and ".join(pii_alerts)}</strong>. Please remove sensitive details.</div>',
            unsafe_allow_html=True,
        )

    # Optional Meta Fields
    col_g, col_a = st.columns(2)
    with col_g:
        st.text_input(
            "🎯 Goal (optional)",
            key="goal_input",
            placeholder="e.g. create a concise summary for a team pitch",
        )
    with col_a:
        st.text_input(
            "👥 Target Audience (optional)",
            key="audience_input",
            placeholder="e.g. non-technical executives, beginners, students",
        )

    # Primary Action Buttons
    col_btn1, col_btn2, _ = st.columns([2, 1, 4])
    with col_btn1:
        submit_clicked = st.button("🚀 Improve My Prompt", type="primary", use_container_width=True)
    with col_btn2:
        st.button("🔄 Clear All", on_click=handle_clear_all, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Execution Pipeline
    if submit_clicked:
        if not weak_prompt_val.strip():
            st.warning("⚠️ Please provide a prompt before clicking **Improve My Prompt**.")
        else:
            st.session_state["improvement"] = None
            st.session_state["original_response"] = None
            st.session_state["improved_response"] = None
            st.session_state["scoring_result"] = None

            # 1. Rewrite Stage
            with st.spinner("🔮 Deconstructing and improving prompt via R-C-T-F-C framework…"):
                try:
                    res_improve = improve_prompt(
                        weak_prompt=weak_prompt_val,
                        goal=st.session_state["goal_input"],
                        audience=st.session_state["audience_input"],
                        model=selected_model,
                        temperature=temperature,
                    )
                    st.session_state["improvement"] = res_improve
                except Exception as exc:
                    st.error(f"❌ Prompt improvement failed: {exc}")
                    st.stop()

            improved_prompt_str = st.session_state["improvement"]["improved_prompt"]

            # 2. Side-by-Side Execution Stage
            with st.spinner("⚡ Running both prompts through Gemini to generate comparative outputs…"):
                err_msgs = []
                try:
                    st.session_state["original_response"] = run_prompt(
                        weak_prompt_val, model=selected_model, temperature=0.7
                    )
                except Exception as exc:
                    err_msgs.append(f"Original execution notice: {exc}")
                    st.session_state["original_response"] = f"[Notice] {exc}"

                try:
                    st.session_state["improved_response"] = run_prompt(
                        improved_prompt_str, model=selected_model, temperature=0.7
                    )
                except Exception as exc:
                    err_msgs.append(f"Improved execution notice: {exc}")
                    st.session_state["improved_response"] = f"[Notice] {exc}"

                if err_msgs:
                    st.info("\n".join(err_msgs))

            # 3. Judge Scoring Stage
            with st.spinner("🏆 Impartial AI Judge evaluating both prompts across 5 dimensions…"):
                try:
                    res_score = run_scoring(
                        weak_prompt_val, improved_prompt_str, model=selected_model
                    )
                    st.session_state["scoring_result"] = res_score
                except Exception as exc:
                    st.error(f"❌ Judge scoring error: {exc}")

            # Append to session history
            sr = st.session_state["scoring_result"]
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "original_prompt": weak_prompt_val,
                "improved_prompt": improved_prompt_str,
                "goal": st.session_state["goal_input"],
                "audience": st.session_state["audience_input"],
                "model": selected_model,
                "original_total": sr.original.total if sr else 0,
                "improved_total": sr.improved.total if sr else 0,
                "improvement": (sr.improved.total - sr.original.total) if sr else 0,
            })

    # Render Results If Available
    if st.session_state["improvement"]:
        impr_obj = st.session_state["improvement"]
        improved_txt = impr_obj["improved_prompt"]
        explanations = impr_obj.get("explanation", {})

        st.markdown("---")

        # Result Panel: Improved Prompt & One-Click Copy
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span>✨</span> Refined R-C-T-F-C Prompt</div>', unsafe_allow_html=True)
        st.caption("Use the copy button in the top-right corner of the code block:")
        st.code(improved_txt, language=None)

        # Download Prompt Option
        st.download_button(
            label="💾 Download Refined Prompt (.txt)",
            data=improved_txt,
            file_name="improved_prompt.txt",
            mime="text/plain",
            key="dl_improved_txt"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span>🧩</span> R-C-T-F-C Framework Breakdown</div>', unsafe_allow_html=True)

        fc_defs = {
            "role": ("🎭", "Role"),
            "context": ("🌍", "Context"),
            "task": ("📋", "Task"),
            "format": ("📐", "Format"),
            "constraints": ("🔒", "Constraints"),
        }
        for k, (icon, title) in fc_defs.items():
            desc = explanations.get(k, "—")
            st.markdown(
                f'<div class="framework-card">'
                f'<div class="fc-header">{icon} {title}</div>'
                f'<div class="fc-content">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Side-by-Side Outputs
        if st.session_state["original_response"] or st.session_state["improved_response"]:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title"><span>🔬</span> Comparative Output Verification</div>', unsafe_allow_html=True)
            
            c_orig, c_impr = st.columns(2)
            with c_orig:
                st.markdown('<div class="comp-label-red">❌ Original (Weak) Prompt Response</div>', unsafe_allow_html=True)
                txt_orig = st.session_state["original_response"] or ""
                st.markdown(f'<div class="comp-box">{txt_orig}</div>', unsafe_allow_html=True)

            with c_impr:
                st.markdown('<div class="comp-label-green">✅ Improved (R-C-T-F-C) Prompt Response</div>', unsafe_allow_html=True)
                txt_impr = st.session_state["improved_response"] or ""
                st.markdown(f'<div class="comp-box">{txt_impr}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Scoring & Judge Feedback
        if st.session_state["scoring_result"]:
            res = st.session_state["scoring_result"]

            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title"><span>📊</span> Prompt Quality Scorecard</div>', unsafe_allow_html=True)

            m_c1, m_c2, m_c3 = st.columns(3)
            with m_c1:
                st.metric("Original Prompt", f"{res.original.total} / 50")
            with m_c2:
                delta = res.improved.total - res.original.total
                st.metric("Improved Prompt", f"{res.improved.total} / 50", delta=f"+{delta}" if delta >= 0 else str(delta))
            with m_c3:
                gain_pct = (delta / max(res.original.total, 1)) * 100
                st.metric("Net Quality Gain", f"+{gain_pct:.0f}%")

            st.markdown("<br>", unsafe_allow_html=True)

            # Criteria Progress Meters
            col_pb1, col_pb2 = st.columns(2)
            crit_names = [c.capitalize() for c in CRITERIA]

            with col_pb1:
                st.markdown('<div style="color:#f87171;font-weight:700;font-size:0.85rem;margin-bottom:0.4rem;">Original Prompt Dimension Scores</div>', unsafe_allow_html=True)
                bars_html_orig = "".join([render_prog_bar(lbl, getattr(res.original, c)) for c, lbl in zip(CRITERIA, crit_names)])
                st.markdown(bars_html_orig, unsafe_allow_html=True)

            with col_pb2:
                st.markdown('<div style="color:#34d399;font-weight:700;font-size:0.85rem;margin-bottom:0.4rem;">Improved Prompt Dimension Scores</div>', unsafe_allow_html=True)
                bars_html_impr = "".join([render_prog_bar(lbl, getattr(res.improved, c)) for c, lbl in zip(CRITERIA, crit_names)])
                st.markdown(bars_html_impr, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Score Table
            df_scores = pd.DataFrame({
                "Criterion": crit_names + ["Total Score"],
                "Original (/10)": [getattr(res.original, c) for c in CRITERIA] + [res.original.total],
                "Improved (/10)": [getattr(res.improved, c) for c in CRITERIA] + [res.improved.total],
            })
            df_scores["Improvement (Δ)"] = df_scores["Improved (/10)"] - df_scores["Original (/10)"]
            df_scores["Improvement (Δ)"] = df_scores["Improvement (Δ)"].apply(lambda x: f"+{x}" if x > 0 else str(x))

            st.dataframe(df_scores, use_container_width=True, hide_index=True)

            # Personal Tips
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="panel-title"><span>💡</span> Personalised Improvement Tips</div>', unsafe_allow_html=True)
            for idx, tip in enumerate(res.tips, 1):
                st.markdown(f'<div class="tip-card"><strong>Tip {idx}:</strong> {tip}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2: SESSION HISTORY
# ══════════════════════════════════════════════════════════════════════════
with tab_history:
    hist = st.session_state["history"]

    if not hist:
        st.info("No runs recorded in this session yet. Return to the Coach tab and submit a prompt!")
    else:
        col_h_head, col_h_clear = st.columns([4, 1])
        with col_h_head:
            st.markdown(f"### 📜 Session History ({len(hist)} saved runs)")
        with col_h_clear:
            st.button("🗑️ Clear History", on_click=handle_clear_history, key="clear_hist_tab_btn", use_container_width=True)

        # CSV Download Button
        df_hist = pd.DataFrame(hist)
        csv_data = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export History as CSV",
            data=csv_data,
            file_name="prompt_coach_history.csv",
            mime="text/csv",
            key="btn_download_history"
        )

        st.markdown("---")

        # Chronological Cards (Newest First)
        for idx, item in enumerate(reversed(hist)):
            run_no = len(hist) - idx
            delta_val = item["improvement"]
            delta_str = f"+{delta_val}" if delta_val >= 0 else str(delta_val)
            badge_orig = format_score_badge(item["original_total"], is_out_of_ten=False)
            badge_impr = format_score_badge(item["improved_total"], is_out_of_ten=False)

            with st.expander(
                f"Run #{run_no} · {item['timestamp']} · Orig: {item['original_total']}/50 → Impr: {item['improved_total']}/50 (Δ {delta_str})",
                expanded=(idx == 0)
            ):
                h_c1, h_c2 = st.columns(2)
                with h_c1:
                    st.markdown("**Original Prompt:**")
                    st.info(f"\"{item['original_prompt']}\"")
                    if item.get("goal"):
                        st.caption(f"🎯 Goal: {item['goal']}")
                    if item.get("audience"):
                        st.caption(f"👥 Audience: {item['audience']}")
                    st.markdown(f"Score: {badge_orig}", unsafe_allow_html=True)

                    # Interactive Re-load Button
                    st.button(
                        "🔄 Re-load into Coach",
                        key=f"reload_hist_{idx}",
                        on_click=handle_apply_scenario,
                        args=(item["original_prompt"], item.get("goal", ""), item.get("audience", ""))
                    )

                with h_c2:
                    st.markdown("**Refined R-C-T-F-C Prompt:**")
                    st.code(item["improved_prompt"], language=None)
                    st.markdown(f"Score: {badge_impr}", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3: 10-DOMAIN EVALUATION BENCHMARK
# ══════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("### 🧪 10-Domain Prompt Quality Benchmark")
    st.markdown(
        "Evaluate the R-C-T-F-C framework across **10 standard benchmark domains** "
        "(Education, Coding, Marketing, Health, Writing, Business, Science, Travel, Finance, Career)."
    )

    # Preview Table
    df_preview = pd.DataFrame(TEST_PROMPTS).rename(columns={"domain": "Domain", "weak_prompt": "Weak Prompt"})
    st.dataframe(df_preview, use_container_width=True, hide_index=True)

    col_eb1, col_eb2, _ = st.columns([2, 1, 3])
    with col_eb1:
        start_eval_clicked = st.button("▶️ Run Evaluation on All 10 Prompts", type="primary", use_container_width=True)
    with col_eb2:
        if st.session_state["eval_results"]:
            st.button("🧹 Clear Results", on_click=handle_clear_eval, use_container_width=True)

    if start_eval_clicked:
        st.session_state["eval_results"] = []
        progress_bar = st.progress(0.0, text="Initializing benchmark suite…")
        status_box = st.empty()

        for idx, item in enumerate(TEST_PROMPTS):
            status_box.markdown(f"⚙️ Evaluating **{idx+1}/10** — *{item['domain']}*: `{item['weak_prompt']}`")
            item_res = run_single_eval(item["domain"], item["weak_prompt"], model=selected_model)
            st.session_state["eval_results"].append(item_res)
            progress_bar.progress((idx + 1) / len(TEST_PROMPTS), text=f"{idx+1}/10 prompts evaluated")

        progress_bar.empty()
        status_box.empty()
        st.success("✅ 10-Domain evaluation benchmark successfully finished!")

    if st.session_state["eval_results"]:
        e_results = st.session_state["eval_results"]
        df_eval = results_to_df(e_results)

        st.markdown("---")
        st.markdown("#### 📊 Evaluation Results Summary")

        valid_runs = [r for r in e_results if not r.error]
        if valid_runs:
            avg_o = sum(r.original_total for r in valid_runs) / len(valid_runs)
            avg_i = sum(r.improved_total for r in valid_runs) / len(valid_runs)
            avg_d = sum(r.improvement for r in valid_runs) / len(valid_runs)
            max_d = max(r.improvement for r in valid_runs)

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Avg Original Score", f"{avg_o:.1f} / 50")
            with col_m2:
                st.metric("Avg Improved Score", f"{avg_i:.1f} / 50")
            with col_m3:
                st.metric("Avg Quality Gain (Δ)", f"+{avg_d:.1f}")
            with col_m4:
                st.metric("Best Domain Gain (Δ)", f"+{max_d}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Full Table
        df_display = df_eval.drop(columns=["Error"])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Comparative Bar Chart
        st.markdown("#### 📈 Comparative Score Visualizer")
        if valid_runs:
            df_chart = pd.DataFrame({
                "Domain": [r.domain for r in valid_runs],
                "Original": [r.original_total for r in valid_runs],
                "Improved": [r.improved_total for r in valid_runs],
            }).set_index("Domain")

            st.bar_chart(df_chart, color=["#f87171", "#34d399"])

        # CSV Export
        eval_csv = df_eval.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Benchmark Results as CSV",
            data=eval_csv,
            file_name="prompt_coach_benchmark.csv",
            mime="text/csv",
            key="btn_download_eval_csv"
        )

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#64748b;font-size:0.8rem;'>"
    "⚠️ AI judge outputs are advisory and indicative. Do not enter sensitive or confidential data. &nbsp;|&nbsp; "
    "Prompt Coach · Built with Streamlit & Google Gemini"
    "</p>",
    unsafe_allow_html=True,
)
