# PlainSpeak — Paste the confusing. Get the clear.

Built for the **Build With AI: Basics** Devpost hackathon ($2,500 prize pool).
PlainSpeak turns dense text — medical notes, contract clauses, academic abstracts —
into plain language, then *proves you understood it* with a readability scorecard
and a 3-question quiz.

## How it works

1. Paste confusing text (or tap a built-in sample).
2. Pick the audience: **Age 12**, **Plain adult**, or **Professional**.
3. Hit **Simplify it** → get the plain rewrite, 3 key takeaways,
   before/after Flesch-Kincaid readability scores, and a quiz.

**Two modes, both honest:**
- **Live AI** — set `LLM_API_KEY` (any OpenAI-compatible key). One chat-completions
  call returns strict JSON: simplified text + takeaways + quiz.
- **Demo mode** — no key needed. A hand-written rule pipeline (sentence splitting,
  jargon dictionary) plus a keyword quiz. Every demo output is labelled as such;
  nothing pretends to be AI.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

Live AI mode (optional):

```bash
cp .env.example .env   # then put your key in .env
# LLM_BASE_URL and LLM_MODEL can point at any OpenAI-compatible endpoint
python app.py
```

## Run the tests

```bash
pytest tests/ -q   # 44 tests
```

## Project layout

```
app.py            Flask server: validation, live/demo routing, JSON API
llm.py            OpenAI-compatible caller (strict JSON contract, LLMError on failure)
fallback.py       Honestly-labelled rule-based demo mode
readability.py    Flesch Reading Ease + Flesch-Kincaid Grade (local, no AI)
templates/        index.html (single-page app)
static/           style.css, app.js (quiz + score rendering)
demo/            index.html — static clickable showcase (simulated, labelled)
tests/            pytest suite (44 tests)
devpost/          scope.md, prd.md, spec.md (skill-pack planning docs)
```

## API

- `GET /` — the app
- `GET /api/health` — `{"ok": true, "mode": "live"|"demo"}`
- `GET /api/samples/<medical|legal|academic>` — built-in sample texts
- `POST /api/simplify` — `{"text": "...", "level": "age12"|"plain"|"pro"}`
  → `{"mode", "simplified", "takeaways"[3], "quiz"[3], "readability_before", "readability_after"}`

## Built with the Devpost Learn Skill Pack

This project was planned and built with the `challengepost/learn-ai-basics` skill
pack (`npx skills add challengepost/learn-ai-basics --all -y`): the interview,
scope, PRD, and spec workflow in `.agents/skills/`, and the planning documents
in `devpost/scope.md`, `devpost/prd.md`, `devpost/spec.md`.

## License

MIT — see [LICENSE](LICENSE).
