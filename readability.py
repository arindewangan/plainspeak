"""Local readability scoring: Flesch Reading Ease + Flesch-Kincaid Grade Level.

No AI involved — just counting words, sentences, and syllables.
"""
import re

_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_SENTENCE_END_RE = re.compile(r"[.!?]+")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")


def count_syllables(word: str) -> int:
    """Heuristic syllable count: vowel groups, minus silent trailing 'e'."""
    word = word.lower().strip()
    if not word:
        return 0
    # strip non-letters
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    # drop silent trailing 'e' (but not 'le' endings like "apple" -> keep)
    if word.endswith("e") and not word.endswith("le"):
        word = word[:-1]
    groups = _VOWEL_GROUP_RE.findall(word)
    return max(1, len(groups))


def split_sentences(text: str) -> list:
    parts = _SENTENCE_END_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def analyze(text: str) -> dict:
    """Return word/sentence/syllable counts and Flesch scores.

    Empty or whitespace-only text yields zeros (no crash).
    """
    sentences = split_sentences(text or "")
    words = _WORD_RE.findall(text or "")
    n_sent = len(sentences)
    n_words = len(words)
    n_syll = sum(count_syllables(w) for w in words)

    if n_sent == 0 or n_words == 0:
        return {
            "words": n_words,
            "sentences": n_sent,
            "syllables": n_syll,
            "flesch_ease": 0.0,
            "fk_grade": 0.0,
        }

    wps = n_words / n_sent          # words per sentence
    spw = n_syll / n_words          # syllables per word
    ease = 206.835 - 1.015 * wps - 84.6 * spw
    grade = 0.39 * wps + 11.8 * spw - 15.59
    return {
        "words": n_words,
        "sentences": n_sent,
        "syllables": n_syll,
        "flesch_ease": round(max(0.0, min(100.0, ease)), 1),
        "fk_grade": round(max(0.0, grade), 1),
    }


def grade_label(grade: float) -> str:
    """Human label for a Flesch-Kincaid grade level."""
    if grade < 6:
        return "elementary school"
    if grade < 9:
        return "middle school"
    if grade < 13:
        return "high school"
    if grade < 16:
        return "college"
    return "college graduate"
