---
doc: prd
status: approved
---

# PlainSpeak — Product Requirements

One line: PlainSpeak turns confusing text into plain language for people like Priya, a freelancer drowning in fine print — and proves she understood it with a quiz.
Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`.

## The Core Journey
1. Priya opens PlainSpeak and sees a single calm page: a text box, three audience cards, one Simplify button.
2. She pastes a dense paragraph (or taps a sample: medical, legal, academic).
3. She picks who the explanation is for: "Age 12", "Plain adult", or "Professional, but clear".
4. She hits Simplify. A short progress state shows the AI working.
5. She gets: the plain-language rewrite, 3 key takeaways, a readability scorecard (before → after), and a 3-question quiz.
6. She takes the quiz, sees her score instantly, and optionally re-reads. Success = she can explain the text back in her own words.

## Screens and Layout
Single page, single column, max-width ~720px, top to bottom:
1. Header: name + one-line promise + mode badge (Live AI / Demo mode).
2. Input card: textarea (with char counter), sample chips, audience selector (3 radio cards), Simplify button.
3. Results (appear below, smooth scroll): simplified text card → takeaways card → readability scorecard (two bars: grade level before/after) → quiz card (one question at a time, instant feedback, final score) → "Try another" reset.
No navigation, no second screen. The static `demo/index.html` mirrors this layout with a pre-run example.

## Look and Feel
Warm paper background (#faf7f0-ish), ink text, one accent color (deep teal). Serif display for headings, clean sans for body. Generous spacing; cards with soft borders, no heavy shadows. Copy is plain-spoken throughout — the product eats its own dogfood. Mobile-usable but desktop-first (the demo video is recorded on desktop).

## Features and Behavior

### Simplify flow
- Paste 50–5000 characters. Under 50: friendly inline error. Over 5000: truncate warning + refuse.
- Audience levels change the system prompt: AGE12 (simple words, short sentences, one analogy allowed), PLAIN (everyday adult language), PRO (precise but jargon-free).
- Live mode (LLM key present): one chat-completions call, JSON response `{simplified, takeaways[3], quiz[{question, options[4], answer}]}`.
- Demo mode (no key): rule-based simplification (sentence splitting, jargon dictionary), takeaways from source sentences, keyword quiz. Every demo-mode output is labelled "Demo mode".

### Readability scorecard
- Flesch Reading Ease and Flesch-Kincaid Grade Level computed locally for input and simplified text.
- Shown as: "Grade 16.2 → Grade 7.1" with a simple bar. If the score doesn't improve, we say so honestly.

### Quiz
- 3 multiple-choice questions, 4 options each, one at a time.
- Instant right/wrong feedback; final score "2/3 — nicely done" with a retry button.
- Live mode: comprehension questions from the LLM. Demo mode: keyword-recognition questions, labelled as such.

### Samples
Three built-in samples (medical discharge note, freelance contract clause, academic abstract), each ~120–180 words, clearly marked as samples.

## States and Boundaries
- **Empty state** — textarea placeholder + sample chips invite the first paste.
- **Loading** — button spinner + "Simplifying…" (max ~20s timeout, then error).
- **Demo mode banner** — persistent slim banner: "Demo mode: add an LLM key for live AI. Outputs are illustrative."
- **Error states** — inline, plain language: empty input, too long, LLM failure ("The AI didn't respond — try again or check your key"), never a stack trace.
- **Persistence** — none. Refresh clears everything. (PRD ref: scope cut accounts.)

## Product Decisions
- Flask + vanilla JS over Next.js — smallest thing that demos cleanly; no build step for the video. (Tradeoff accepted: less framework polish.)
- OpenAI-compatible API (not one provider) — works with OpenAI, or any compatible endpoint via env vars.
- Demo mode is rule-based, not fake-AI — it must never be mistaken for a live model call.

## What We're Building
Everything above: the one-page app, live + demo modes, scorecard, quiz, samples, static showcase, tests, README, planning docs.

## Deferred From the POC
- Accounts/history ("my simplifications") — no backend identity in a POC.
- File upload (PDF/DOCX) — paste-only per scope cut.
- Sharing links — the demo video covers it.

## Possible Later Enhancements
More audience levels; Hindi/Kannada output; adaptive quiz difficulty; a browser extension for "simplify this page".

## Non-Goals
- Medical/legal advice — a footer disclaimer says PlainSpeak is an explainer, not professional advice.
- Perfect simplification — the quiz exists precisely because AI can be wrong; we surface uncertainty instead of hiding it.

## Open Questions
- None blocking. Model default (`gpt-4o-mini`) is a suggestion; any OpenAI-compatible model works.
