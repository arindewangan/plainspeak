"""Talk to any OpenAI-compatible chat-completions endpoint and get back
strictly-shaped JSON: simplified text, 3 takeaways, 3 quiz questions.

Never invents credentials: without LLM_API_KEY the caller must use demo mode.
"""
import json
import os

import requests

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
TIMEOUT_S = 25


class LLMError(Exception):
    """Anything that stops us getting a good answer from the model."""


LEVEL_PROMPTS = {
    "age12": (
        "Rewrite the text so a 12-year-old understands it completely. "
        "Use short sentences and everyday words. One friendly analogy is welcome, "
        "but never change the meaning or add facts that aren't there."
    ),
    "plain": (
        "Rewrite the text in clear, everyday adult language. Remove jargon, "
        "untangle long sentences, keep every important fact. Do not add new facts."
    ),
    "pro": (
        "Rewrite the text so a busy professional outside this field grasps it fast. "
        "Keep it precise and jargon-free, but don't dumb it down — respect the reader's intelligence."
    ),
}

SYSTEM_PROMPT = """You simplify dense text into plain language. Reply with ONLY a JSON object \
(no markdown, no commentary) shaped exactly like this:
{
  "simplified": "the full plain-language rewrite, same language as input",
  "takeaways": ["key point 1", "key point 2", "key point 3"],
  "quiz": [
    {"question": "...", "options": ["a", "b", "c", "d"], "answer": 0},
    {"question": "...", "options": ["a", "b", "c", "d"], "answer": 1},
    {"question": "...", "options": ["a", "b", "c", "d"], "answer": 2}
  ]
}
Rules: exactly 3 takeaways; exactly 3 quiz questions; each question has exactly 4 options \
with "answer" as the 0-based index of the correct one; quiz questions must be answerable \
from the simplified text alone; never invent facts beyond the input."""


def get_config() -> dict:
    return {
        "base_url": os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        "api_key": os.environ.get("LLM_API_KEY", "").strip(),
        "model": os.environ.get("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
    }


def has_key() -> bool:
    return bool(get_config()["api_key"])


def _validate_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise LLMError("model did not return a JSON object")
    simplified = data.get("simplified")
    takeaways = data.get("takeaways")
    quiz = data.get("quiz")
    if not isinstance(simplified, str) or not simplified.strip():
        raise LLMError("model response missing 'simplified' text")
    if not isinstance(takeaways, list) or len(takeaways) != 3 or not all(
        isinstance(t, str) and t.strip() for t in takeaways
    ):
        raise LLMError("model response must contain exactly 3 takeaways")
    if not isinstance(quiz, list) or len(quiz) != 3:
        raise LLMError("model response must contain exactly 3 quiz questions")
    for q in quiz:
        if not isinstance(q, dict):
            raise LLMError("malformed quiz question")
        opts = q.get("options")
        ans = q.get("answer")
        if (
            not isinstance(q.get("question"), str)
            or not q["question"].strip()
            or not isinstance(opts, list)
            or len(opts) != 4
            or not all(isinstance(o, str) for o in opts)
            or not isinstance(ans, int)
            or not 0 <= ans <= 3
        ):
            raise LLMError("malformed quiz question/options")
    return {
        "simplified": simplified.strip(),
        "takeaways": [t.strip() for t in takeaways],
        "quiz": [
            {
                "question": q["question"].strip(),
                "options": [o.strip() for o in q["options"]],
                "answer": q["answer"],
            }
            for q in quiz
        ],
    }


def simplify(text: str, level: str) -> dict:
    """Call the model. Raises LLMError on any failure. Caller handles fallback."""
    cfg = get_config()
    if not cfg["api_key"]:
        raise LLMError("no LLM_API_KEY configured")
    if level not in LEVEL_PROMPTS:
        raise LLMError(f"unknown level: {level}")

    url = f"{cfg['base_url']}/chat/completions"
    body = {
        "model": cfg["model"],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{LEVEL_PROMPTS[level]}\n\nText to simplify:\n{text}",
            },
        ],
    }
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {cfg['api_key']}"},
            json=body,
            timeout=TIMEOUT_S,
        )
    except requests.RequestException as exc:
        raise LLMError(f"could not reach the model: {exc}") from exc
    if resp.status_code != 200:
        raise LLMError(f"model API returned HTTP {resp.status_code}")
    try:
        content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise LLMError("model returned an unparseable response") from exc
    result = _validate_payload(data)
    result["mode"] = "live"
    return result
