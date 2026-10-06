---
doc: scope
status: approved
---

# PlainSpeak

One line: Paste any confusing text — a medical note, a legal clause, an academic abstract — and get it back in plain language, with proof you actually understood it.

## The Unique Kernel
PlainSpeak doesn't just simplify text — it proves comprehension. Every simplification comes with a before/after readability score and a short quiz generated from the simplified version. The "oh, that's cool" beat is watching a Flesch-Kincaid grade level drop from "college graduate" to "age 12" and then acing the quiz.

## Who It's For
Priya, a freelance designer in Bengaluru. She just received a dense client contract and a medical discharge summary for her father in the same week. Today she pastes them into a chatbot and gets back a wall of text she trusts blindly — or she gives up and signs things she hasn't understood.

## The Core Loop
She opens PlainSpeak, pastes the confusing text (or taps a sample), picks who it's for ("explain like I'm 12" / "plain professional"), and hits Simplify. She reads the plain version, glances at the readability score dropping, then takes the 3-question quiz. She comes back every time life hands her fine print.

## Inspiration & Identity
Calm, trustworthy, editorial — more "helpful explainer" than "AI gadget." Clean typography, generous whitespace, a warm paper-like background. The tone of the copy is plain-spoken itself: the product demonstrates its own value in every label. No gradients-for-show, no robot mascots.

## Why This Matters to the Learner
The builder (a working software engineer) keeps hitting the same wall: AI tools that paraphrase without proving anything. Building the quiz-and-score loop is the interesting part — it's where "AI basics" (prompting for structured output, honest fallbacks) becomes a real product decision.

## What "Working" Looks Like
A running Flask app: paste ~a paragraph of jargon, get a plain-language rewrite plus 3 takeaways plus a 3-question multiple-choice quiz plus readability scores before/after. Works with any OpenAI-compatible LLM key; without a key it runs a clearly-labelled offline demo mode (rule-based simplification + keyword quiz) so the loop is always demonstrable.

## The POC Boundary
In: one page, one flow (paste → simplify → takeaways → quiz → scores), 3 audience levels, 3 built-in samples, live LLM mode + labelled demo mode, readability metrics, static showcase page.
Out: accounts, history, PDF upload, sharing, mobile app.

## Later
PDF/DOCX upload, saved library of simplifications, more languages, difficulty-adaptive quizzes.

## Explicitly Cut
- **User accounts** — nothing persists; no login needed for a POC.
- **File upload** — paste-only keeps the demo tight and avoids parsing rabbit holes.
- **Auto-generated share links** — the demo video is the sharing mechanism for the hackathon.
