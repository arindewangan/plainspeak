"""Tests for readability.py — Flesch scores must be sane and total."""
import pytest

from readability import analyze, count_syllables, grade_label


@pytest.mark.parametrize(
    "word,expected",
    [
        ("cat", 1),
        ("hello", 2),
        ("reading", 2),
        ("beautiful", 3),
        ("the", 1),
        ("a", 1),
        ("syllable", 3),
        ("", 0),
    ],
)
def test_count_syllables(word, expected):
    assert count_syllables(word) == expected


def test_simple_sentence_scores_easy():
    r = analyze("The cat sat on the mat. It was a happy cat.")
    assert r["words"] == 11
    assert r["sentences"] == 2
    assert r["flesch_ease"] > 80
    assert r["fk_grade"] < 4


def test_dense_sentence_scores_hard():
    r = analyze(
        "Notwithstanding the aforementioned contractual stipulations, the parties "
        "hereby acknowledge their respective obligations regarding the facilitation "
        "of subsequent remuneration procedures."
    )
    assert r["fk_grade"] > 12
    assert r["flesch_ease"] < 50


def test_empty_text_does_not_crash():
    r = analyze("")
    assert r["words"] == 0
    assert r["sentences"] == 0
    assert r["flesch_ease"] == 0.0
    assert r["fk_grade"] == 0.0
    r2 = analyze("   \n  ")
    assert r2["fk_grade"] == 0.0


def test_scores_bounded():
    r = analyze("Supercalifragilisticexpialidocious! " * 50)
    assert 0.0 <= r["flesch_ease"] <= 100.0
    assert r["fk_grade"] >= 0.0


@pytest.mark.parametrize(
    "grade,expected",
    [(2.0, "elementary school"), (7.0, "middle school"), (10.0, "high school"),
     (14.0, "college"), (18.0, "college graduate")],
)
def test_grade_label(grade, expected):
    assert grade_label(grade) == expected
