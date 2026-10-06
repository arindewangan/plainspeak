---
doc: spec
status: approved
---

# PlainSpeak — Technical Spec

## How This Works, In Plain Language
The app has four parts. The **page** (HTML/CSS/JS) is what Priya sees and touches. The **server** (Flask, `app.py`) takes her text, checks it's sane, and decides which brain to use. The **AI caller** (`llm.py`) talks to any OpenAI-compatible language model and asks for a strict JSON answer: simplified text, 3 takeaways, 3 quiz questions. The **demo brain** (`fallback.py`) is a set of honest, hand-written rules used only when no API key is configured — it shortens sentences and swaps jargon from a small dictionary, and says so on screen. A tiny **readability** module (`readability.py`) scores text with the Flesch formulas — no AI needed, just counting words, sentences, and syllables. Nothing is stored anywhere; when she refreshes, it's gone.

## The Core Journey Through the System
Priya pastes text and hits Simplify → `app.js` POSTs `{text, level}` to `/api/simplify` → `app.py` validates (50–5000 chars, known level) → if `LLM_API_KEY` is set, `llm.py` sends a chat-completions request with a level-specific system prompt and parses the JSON; otherwise `fallback.py` runs the rule pipeline → `readability.py` scores input and output → server returns one JSON blob → `app.js` renders the rewrite, takeaways, score bars, then the quiz one question at a time.
PRD ref: `prd.md > The Core Journey`.

## Stack
- Python 3.12, Flask 3.x — tiny server, no build step. (https://flask.palletsprojects.com/)
- `requests` — one POST to the LLM endpoint.
- Vanilla HTML/CSS/JS — single page, no framework, no bundler. Rationale: the demo video needs zero build friction.
- pytest — tests. (https://docs.pytest.org/)
- LLM: any OpenAI-compatible chat-completions endpoint via env (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, default `gpt-4o-mini`). No key is invented; without one the app runs in labelled demo mode.

## Where It Runs and How Someone Tries It
Local process. Requirements: Python 3.10+, `pip install -r requirements.txt`. Optional: `LLM_API_KEY` (and optionally `LLM_BASE_URL`, `LLM_MODEL`).
Start: `python app.py` → open http://127.0.0.1:5000. The demo video records this flow: paste sample → Simplify → results → quiz. Deployment optional; the static `demo/index.html` works from any static host.

## Look and Feel
Warm paper background, ink text, deep-teal accent; serif headings (Georgia), system sans body; single 720px column of soft-bordered cards; calm, editorial, plain-spoken microcopy. No gradients, no mascots. Build constraint honored: pure CSS, no framework.

## Components

### app.py (server)
Validates input, routes to `llm` or `fallback`, attaches readability scores, returns JSON. Serves `/`, `/api/simplify`, `/api/health`.
PRD ref: `prd.md > Simplify flow`.

### llm.py (AI caller)
Builds level-specific system prompts, calls `{LLM_BASE_URL}/chat/completions` with `response_format: json_object`, parses and validates the JSON shape. Raises `LLMError` on any failure (network, non-200, bad JSON, missing fields).
PRD ref: `prd.md > Simplify flow`, `prd.md > Quiz`.

### fallback.py (demo brain)
Rule pipeline: split sentences over ~22 words at conjunctions/semicolons; swap ~40 jargon terms via dictionary; takeaways = up to 3 leading sentences, trimmed; quiz = 3 keyword-recognition questions with distractors from a built-in bank. Returns `mode: "demo"` and every string the UI shows is prefixed/labelled as demo output.
PRD ref: `prd.md > Simplify flow`, `prd.md > Quiz`.

### readability.py (scores)
`analyze(text)` → words, sentences, syllables, Flesch Reading Ease, Flesch-Kincaid Grade. Heuristic syllable counter (vowel groups, silent-e rule). Empty/whitespace input → zeros, no crash.
PRD ref: `prd.md > Readability scorecard`.

### Frontend (templates/index.html, static/app.js, static/style.css)
Renders input card, results cards, score bars, and the step-through quiz. Fetches `/api/simplify`. Shows the demo-mode banner when `mode == "demo"`.
PRD ref: `prd.md > Screens and Layout`.

## Data Model
No persistence. In-memory per request only: `{text, level}` in → `{mode, simplified, takeaways[], quiz[], readability_before, readability_after}` out. Refresh clears state (client-side JS variables only).

## File Structure
```
plainspeak/
├── app.py                 # Flask server + validation + routing
├── llm.py                 # OpenAI-compatible caller, JSON contract
├── fallback.py            # labelled rule-based demo mode
├── readability.py         # Flesch scores
├── requirements.txt
├── .env.example           # key names, no secrets
├── .gitignore
├── LICENSE                # MIT
├── README.md
├── devpost/               # skill-pack planning docs (this file, scope, prd)
│   ├── learner-profile.md # gitignored (personal)
│   ├── scope.md
│   ├── prd.md
│   └── spec.md
├── templates/index.html
├── static/{style.css,app.js}
├── demo/index.html         # static showcase (simulated, labelled)
├── tests/
└── .agents/skills/…        # Devpost Learn Skill Pack (installed via npx)
```

## External Services and Dependencies
- OpenAI-compatible chat completions: `POST {LLM_BASE_URL}/chat/completions`, body `{model, messages, temperature: 0.3, response_format: {type: "json_object"}}`. Keys required only for live mode. No other external services.

## Important Failure Modes
- **No API key** → labelled demo mode, not an error. (The expected path for reviewers.)
- **LLM call fails** (bad key, timeout, bad JSON) → HTTP 502 with plain-language message; UI suggests retry or demo mode. Never a traceback.
- **Input too short/long** → HTTP 400 with plain-language message; inline in UI.

## What Was Simplified and Why
- **Rule-based demo brain** instead of a local LLM — a local model would need downloads/GPU; the rules are transparent and honestly labelled.
- **Keyword quiz in demo mode** instead of comprehension questions — real comprehension needs a model; keyword recognition is a genuine (small) check, labelled as such.
- **No database** — nothing needs to persist for the POC.

## Decisions and Open Issues
- Chose Flask over Next.js: zero build step, fastest path to a working demo video. Tradeoff: less SPA polish; accepted, the page is simple enough.
- Chose OpenAI-compatible API over one vendor: reviewer can use any key they have.
- Genuine learner uncertainty discussed: "how do I make the LLM return reliable JSON?" — resolved via `response_format: json_object` + server-side shape validation + `LLMError` fallback. Will verify with a mocked test (no real key in CI).
- Open: none blocking the build.
