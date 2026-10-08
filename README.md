# 🎯 Prompt Coach

**Prompt Coach** is an interactive AI-assisted web application built with Python, Streamlit, and the official Google Gemini SDK (`google-genai`). It transforms vague, weak prompts into structured, highly effective prompts using the **R-C-T-F-C framework** (Role, Context, Task, Format, Constraints), executes before/after prompt comparisons, and scores prompt quality with an impartial AI judge.

---

## 🌟 Key Features

- **Prompt Rewriting (R-C-T-F-C Framework)**:
  - Takes any weak prompt (plus optional Goal & Target Audience).
  - Automatically identifies and enriches all 5 elements:
    - 🎭 **Role**: Who the AI should act as.
    - 🌍 **Context**: Essential background and domain grounding.
    - 📋 **Task**: Clear, actionable directions.
    - 📐 **Format**: Expected response structure (markdown, tables, sections).
    - 🔒 **Constraints**: Boundaries, tone guidelines, and negative constraints.
  - Returns structured JSON with an element-by-element explanatory breakdown.
- **Side-by-Side Before & After Execution**:
  - Concurrently runs both the original weak prompt and the improved prompt against Gemini.
  - Displays responses side by side in red/green comparison containers.
- **AI Judge & Score Breakdown**:
  - Independent Gemini call evaluates both prompts on 5 dimensions (1–10 scale): *Clarity*, *Specificity*, *Context*, *Format*, *Constraints*.
  - Displays visual, color-coded score badges (🔴 Low $\le 4$, 🟡 Mid $5-7$, 🟢 High $8-10$).
  - Side-by-side animated progress bars for each criterion.
  - Overall score gain metric with percentage improvement and 3 actionable tips.
- **One-Click Copy**:
  - Formatted `st.code` block for instant copying of the improved prompt.
- **Session History & CSV Export**:
  - Retains all prompt runs across the session in `st.session_state`.
  - Chronological card view showing prompts, scores, and metadata.
  - One-click export to CSV (`prompt_coach_history.csv`).
- **Domain Evaluation Suite (10 Test Cases)**:
  - Built-in test suite covering 10 distinct domains: Education, Coding, Marketing, Health, Writing, Business, Science, Travel, Finance, Career.
  - Live batch execution with progress tracking.
  - Comparative metrics (Avg Original, Avg Improved, Avg $\Delta$, Best $\Delta$).
  - Before vs. After bar chart visualization and CSV download.
- **Responsible Use & PII Safeguard**:
  - Built-in regex scanner that warns users when sensitive PII (email addresses, phone numbers) is entered.
  - Responsible use guidance regarding AI inaccuracies and advisory scores.

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/) (>= 1.35.0)
- **AI Engine / LLM**: [Google Gemini API](https://ai.google.dev/) via the official [`google-genai`](https://pypi.org/project/google-genai/) SDK
- **Data Manipulation**: [pandas](https://pandas.pydata.org/)
- **Configuration & Secrets**: [`python-dotenv`](https://pypi.org/project/python-dotenv/) + Streamlit Cloud `st.secrets` fallback
- **Testing**: [pytest](https://pytest.org/)

---

## 🔑 How to Get a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** in the top navigation.
4. Click **"Create API key"** (in a new or existing Google Cloud project).
5. Copy the generated API key (starts with `AIza...`).

---

## 🚀 Setup & Local Installation

### 1. Clone the repository / Navigate to directory
```bash
git clone https://github.com/Hacker123fb/promptcoach.git
cd promptcoach
```

### 2. Create and activate a virtual environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy the sample environment file:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Edit `.env` and insert your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
# Optional (defaults to gemini-2.5-flash):
# MODEL_NAME=gemini-2.5-flash
```

---

## 💻 Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```
Then open your browser at **http://localhost:8501**.

To run unit tests:
```bash
pytest test_app.py -v
```

---

## 📁 Project Structure

```
├── .env.example            # Sample environment variables template
├── .gitignore              # Ignores .env and Python/pytest caches
├── .streamlit/             # Streamlit theme & headless server config
├── app.py                  # Main Streamlit UI (tabs, banners, inputs, charts)
├── evaluation.py           # 10-prompt benchmark suite and batch evaluator
├── llm.py                  # Gemini API interactions, retries, JSON sanitization
├── prompts.py              # System prompts & user prompt templates (R-C-T-F-C, Judge)
├── scoring.py              # Judge score parsing, data models, and clamping
├── test_app.py             # Pytest unit tests (JSON parsing, scoring, PII detector)
├── utils.py                # PII scanner, secrets resolution (st.secrets + env fallback)
├── requirements.txt        # Pinned project dependencies
└── docs/
    ├── architecture.md     # Flowchart and architectural breakdown
    ├── prompts.md          # Full prompt templates with design rationale
    └── known_issues.md     # Edge cases, failure modes, and mitigations
```
