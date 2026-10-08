# 🏗️ Prompt Coach — System Architecture

This document describes the high-level system architecture, data flow, and module boundaries of the **Prompt Coach** application.

---

## 🔄 End-to-End Flowchart

```mermaid
flowchart TD
    User([👤 User]) -->|Types weak prompt, goal, audience| UI[🖥️ Streamlit UI - app.py]
    
    subgraph UI_Layer [Frontend & Session Layer]
        UI --> Scanner[🛡️ PII & Input Validator<br/>utils.py / app.py]
        Scanner -->|Valid Input| StateMgr[💾 Session State Manager<br/>st.session_state]
    end

    subgraph Prompt_Construction [Prompt Construction Layer]
        StateMgr --> Builder[📝 R-C-T-F-C Prompt Builder<br/>prompts.py]
        Builder --> SysPrompt[System Instructions + JSON Schema Specification]
    end

    subgraph LLM_Integration [Gemini API Integration Layer - llm.py]
        SysPrompt --> ClientInit[🔑 Client & Key Resolver<br/>st.secrets / os.getenv]
        ClientInit --> APICall1["🚀 Gemini API Call 1: Rewriter<br/>(model.generate_content)"]
        APICall1 --> JSONCleaner["🧹 JSON Parser & Code-Fence Stripper<br/>(_parse_json_robust)"]
    end

    subgraph Dual_Execution [Comparative Execution Layer]
        JSONCleaner -->|Extract Improved Prompt| DualRun{"⚡ Side-by-Side Runner<br/>(llm.run_prompt)"}
        StateMgr -.->|Original Prompt| DualRun
        DualRun --> OrigResp["❌ Original Output"]
        DualRun --> ImprResp["✅ Improved Output"]
    end

    subgraph Judge_Layer [Judge & Scoring Layer - scoring.py]
        OrigResp & ImprResp --> JudgePrompt["⚖️ Impartial Judge Prompt Builder<br/>(SCORE_SYSTEM_PROMPT)"]
        JudgePrompt --> APICall2["🤖 Gemini API Call 2: Judge<br/>(5 Criteria Scoring 1-10)"]
        APICall2 --> ScoreParser["📊 Clamping & Score Aggregation<br/>(PromptScores & ScoringResult)"]
    end

    subgraph Output_Presentation [Results Display & History]
        JSONCleaner --> Pills["🧩 R-C-T-F-C Explanatory Pills"]
        JSONCleaner --> CopyBlock["📋 Copyable Code Block"]
        OrigResp & ImprResp --> CompCards["🔬 Side-by-Side Output Cards"]
        ScoreParser --> VisualScores["📈 Color Badges & Progress Bars"]
        ScoreParser --> Tips["💡 Personalised Tips"]
        
        Pills & CopyBlock & CompCards & VisualScores & Tips --> ResultsScreen[🎯 Rendered Results on Coach Tab]
        ResultsScreen --> HistStore[📜 Append to Session History & CSV Exporter]
        ResultsScreen --> User
    end

    classDef primary fill:#7c3aed,stroke:#a78bfa,stroke-width:2px,color:#fff;
    classDef success fill:#059669,stroke:#34d399,stroke-width:2px,color:#fff;
    classDef warning fill:#d97706,stroke:#fbbf24,stroke-width:2px,color:#fff;
    classDef dark fill:#1e1b4b,stroke:#4338ca,stroke-width:1px,color:#c7d2fe;

    class UI,ResultsScreen primary;
    class APICall1,APICall2 success;
    class Scanner,JSONCleaner warning;
    class StateMgr,Builder,ScoreParser dark;
```

---

## 🧩 Architectural Layers & Module Responsibilities

### 1. Presentation & State Layer (`app.py`)
- **Page Layout & Styling**: Dark-theme glassmorphism CSS, custom banners, cards, and tab system (`Coach`, `History`, `Evaluation`).
- **Reactive Workflow**: Drives step-by-step UI feedback via `st.spinner`, alerts, and metrics.
- **State Persistence**: Maintains run history and evaluation batch state in `st.session_state`.
- **Exporting**: Implements CSV streaming for both individual runs and benchmark suites.

### 2. Guardrails & Utilities Layer (`utils.py`)
- **PII Detector**: Evaluates inputs against email and telephone regex patterns before LLM dispatch, raising amber advisory warnings.
- **Secrets Resolver**: Provides unified fallback resolution: checks `st.secrets` (for Streamlit Community Cloud) first, then `os.getenv` / `.env` (for local environments).

### 3. Prompt Engineering Layer (`prompts.py`)
- **R-C-T-F-C System Template**: Instructs Gemini to act as a Prompt Engineer and rewrite prompts along Role, Context, Task, Format, and Constraints dimensions.
- **Judge System Template**: Instructs Gemini to act as an impartial referee, evaluating clarity, specificity, context, format, and constraints on a 1–10 integer scale.
- **Message Builders**: Serializes inputs into clean, normalized JSON structures.

### 4. API & Resilience Layer (`llm.py`)
- **Singleton Client**: Cached initialization of the `google.genai.Client`.
- **Error Recovery & Retries**: Detects transient HTTP 429/500/503 rate-limiting errors and automatically retries with exponential backoff.
- **Fenced JSON Normalizer**: Handles LLMs wrapping structured JSON output in triple-backtick markdown blocks by stripping fences and retrying parsing before throwing errors.

### 5. Scoring & Parsing Engine (`scoring.py`)
- **Data Models**: `PromptScores` and `ScoringResult` dataclasses encapsulate criterion totals and delta calculations.
- **Range Clamping**: Enforces $[1, 10]$ boundaries on all judge criteria scores to guard against LLM hallucination of invalid numbers.

### 6. Benchmark & Evaluation Suite (`evaluation.py`)
- **Domain Coverage**: 10 curated test cases spanning diverse subjects (Education, Coding, Marketing, Health, Writing, Business, Science, Travel, Finance, Career).
- **Batch Pipeline**: Sequentially triggers rewrites and evaluations while streaming live progress metrics to the UI.
