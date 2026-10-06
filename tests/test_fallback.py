"""Tests for fallback.py — the honestly-labelled demo mode."""
import re

import fallback


def test_jargon_swapped(dense_text):
    out = fallback.simplify_text(dense_text, "plain")
    lowered = out.lower()
    assert "notwithstanding" not in lowered
    assert "facilitate" not in lowered
    assert "pursuant to" not in lowered
    assert "utilized" not in lowered
    # meaning preserved: key facts still present
    assert "contractor" in lowered
    assert "invoice" in lowered


def test_long_sentences_get_split():
    long_one = (
        "The committee decided to approve the proposal and allocate the funds "
        "because the research demonstrated significant potential for improving "
        "outcomes across all participating institutions in the region."
    )
    out = fallback.simplify_text(long_one, "plain")
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", out) if s.strip()]
    assert len(sentences) >= 2
    assert all(len(s.split()) <= 24 for s in sentences)


def test_level_prefixes():
    for level, marker in [("age12", "simply put"), ("plain", "plain language"), ("pro", "clear version")]:
        out = fallback.simplify_text("This is a reasonably long sentence with several words in it for testing.", level)
        assert marker in out.lower()


def test_takeaways_capped_at_three(dense_text):
    simplified = fallback.simplify_text(dense_text, "plain")
    takes = fallback.takeaways(dense_text, simplified)
    assert 1 <= len(takes) <= 3
    assert all(t.strip() for t in takes)


def test_quiz_shape_and_determinism(dense_text):
    simplified = fallback.simplify_text(dense_text, "plain")
    q1 = fallback.build_quiz(dense_text, simplified, seed=42)
    q2 = fallback.build_quiz(dense_text, simplified, seed=42)
    assert q1 == q2  # deterministic
    assert len(q1) == 3
    for q in q1:
        assert isinstance(q["question"], str) and q["question"].strip()
        assert len(q["options"]) == 4
        assert 0 <= q["answer"] <= 3
        # the marked answer really is one of the options
        assert isinstance(q["options"][q["answer"]], str)


def test_simplify_returns_demo_payload(dense_text):
    result = fallback.simplify(dense_text, "plain", seed=7)
    assert result["mode"] == "demo"
    assert result["demo_label"] == fallback.DEMO_LABEL
    assert result["simplified"].strip()
    assert 1 <= len(result["takeaways"]) <= 3
    assert len(result["quiz"]) == 3


def test_demo_never_claims_to_be_ai(dense_text):
    result = fallback.simplify(dense_text, "plain")
    blob = (result["simplified"] + " ".join(result["takeaways"])).lower()
    assert "as an ai" not in blob
    assert "i am an ai language model" not in blob
