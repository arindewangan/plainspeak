"""Honestly-labelled demo mode: rule-based simplification used ONLY when no
LLM key is configured. Every output is marked as demo output by the caller.

Nothing here pretends to be AI. It shortens sentences, swaps jargon from a
small dictionary, and builds a keyword quiz — genuinely useful, clearly limited.
"""
import random
import re

DEMO_LABEL = "Demo mode"

# word-boundary, case-insensitive swaps: dense -> plain
JARGON = [
    (r"\butiliz(e|ed|ation|ing)?\b", "use"),
    (r"\bfacilitat(e|ion|ing)?\b", "help"),
    (r"\bapproximately\b", "about"),
    (r"\bindividuals\b", "people"),
    (r"\bcommence(d|s)?\b", "start"),
    (r"\bpurchas(e|ed|ing)?\b", "buy"),
    (r"\brequire(d|s|ment)?\b", "need"),
    (r"\bobtain(ed|ing|s)?\b", "get"),
    (r"\bdemonstrat(e|ed|ing|ion)\b", "show"),
    (r"\bimplement(ed|ing|ation)?\b", "set up"),
    (r"\bleverage(d|ing)?\b", "use"),
    (r"\bprior to\b", "before"),
    (r"\bsubsequent(ly)?\b", "later"),
    (r"\bnotwithstanding\b", "despite"),
    (r"\bhereinafter\b", "from here on"),
    (r"\bpursuant to\b", "under"),
    (r"\bin the event that\b", "if"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bhas the ability to\b", "can"),
    (r"\ba large number of\b", "many"),
    (r"\bterminate(d|ion)?\b", "end"),
    (r"\bcompensation\b", "pay"),
    (r"\bremuneration\b", "pay"),
    (r"\bconfidential\b", "private"),
    (r"\bhereby\b", ""),
    (r"\bthereof\b", "of it"),
    (r"\bherein\b", "in this"),
    (r"\bmyocardial infarction\b", "heart attack"),
    (r"\bhypertension\b", "high blood pressure"),
    (r"\bhyperlipidemia\b", "high cholesterol"),
    (r"\badminister(ed)?\b", "give"),
    (r"\bprescribe(d)?\b", "order"),
    (r"\bdiagnos(is|ed|tic)\b", "finding"),
    (r"\bprognosis\b", "outlook"),
    (r"\bmethodology\b", "method"),
    (r"\bparadigm\b", "model"),
    (r"\bcaveat(s)?\b", "warning"),
    (r"\bexpedite(d)?\b", "speed up"),
    (r"\bendeavor\b", "try"),
]

_SPLIT_AFTER = re.compile(r"\s+(?:and|but|or|so|which|that|because|although|while|whereas)\s+", re.I)
_SENT_END = re.compile(r"(?<=[.!?])\s+")

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "it", "its", "this", "that",
    "these", "those", "as", "at", "by", "from", "into", "you", "your", "we",
    "they", "their", "he", "she", "his", "her", "will", "would", "can", "could",
    "should", "has", "have", "had", "not", "no", "if", "then", "than", "so",
    "such", "when", "which", "who", "whom", "what", "where", "how", "all",
}

# plausible-but-generic distractors for the keyword quiz
DISTRACTOR_BANK = [
    "photosynthesis", "telescope", "marathon", "orchestra", "lighthouse",
    "glacier", "bicycle", "volcano", "library", "satellite", "garden",
    "harbor", "desert", "piano", "bridge", "forest", "rocket", "museum",
    "candle", "ladder", "compass", "mirror", "engine", "cloud",
]


def split_sentences(text: str):
    return [s.strip() for s in _SENT_END.split(text.strip()) if s.strip()]


def simplify_sentence(sentence: str) -> str:
    s = sentence.strip()
    # 1. split over-long sentences at conjunctions
    words = s.split()
    if len(words) > 22:
        parts = _SPLIT_AFTER.split(s, maxsplit=1)
        if len(parts) == 2 and len(parts[0].split()) > 6:
            first = parts[0].rstrip(",;:")
            if not first.endswith((".", "!", "?")):
                first += "."
            second = parts[1].strip().capitalize()
            return f"{simplify_sentence(first)} {simplify_sentence(second)}"
    # 2. jargon swaps
    for pattern, replacement in JARGON:
        s = re.sub(pattern, replacement, s, flags=re.I)
    s = re.sub(r"\s{2,}", " ", s).strip()
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)
    return s


def simplify_text(text: str, level: str) -> str:
    sentences = split_sentences(text)
    out = [simplify_sentence(s) for s in sentences]
    prefix = {
        "age12": "Here's what it means, simply put: ",
        "plain": "In plain language: ",
        "pro": "The clear version: ",
    }.get(level, "")
    return prefix + " ".join(out)


def takeaways(text: str, simplified: str):
    """Up to 3 takeaways: leading sentences of the simplified text, trimmed."""
    sents = split_sentences(simplified)
    result = []
    for s in sents[:3]:
        words = s.split()
        if len(words) > 25:
            s = " ".join(words[:25]) + "…"
        result.append(s)
    return result


def _keywords(text: str):
    words = re.findall(r"[A-Za-z]{6,}", text.lower())
    seen = []
    for w in words:
        if w not in STOPWORDS and w not in seen:
            seen.append(w)
    return seen


def build_quiz(text: str, simplified: str, seed: int = 0):
    """Keyword-recognition quiz (demo mode): 'which word appeared in the text?'

    Deterministic given seed so tests are stable.
    """
    rng = random.Random(seed)
    kws = _keywords(simplified) or _keywords(text)
    chosen = kws[:3]
    quiz = []
    for kw in chosen:
        pool = [d for d in DISTRACTOR_BANK if d not in text.lower()]
        distractors = rng.sample(pool, 3)
        options = distractors + [kw]
        rng.shuffle(options)
        quiz.append(
            {
                "question": "Which of these words appeared in the simplified text?",
                "options": options,
                "answer": options.index(kw),
            }
        )
    # pad to 3 questions if the text was keyword-poor
    while len(quiz) < 3:
        pool = [d for d in DISTRACTOR_BANK if d not in text.lower()]
        kw = rng.choice([d for d in DISTRACTOR_BANK if d not in pool] or pool)
        options = rng.sample([d for d in DISTRACTOR_BANK if d != kw], 3) + [kw]
        rng.shuffle(options)
        quiz.append(
            {
                "question": "Demo check: which word is spelled correctly?",
                "options": options,
                "answer": options.index(kw),
            }
        )
    return quiz[:3]


def simplify(text: str, level: str, seed: int = 0) -> dict:
    simplified = simplify_text(text, level)
    return {
        "mode": "demo",
        "demo_label": DEMO_LABEL,
        "simplified": simplified,
        "takeaways": takeaways(text, simplified),
        "quiz": build_quiz(text, simplified, seed=seed),
    }
