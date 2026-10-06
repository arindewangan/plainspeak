"""Tests for app.py — routes, validation, demo/live routing."""
import json

import app as app_module
import llm


def test_health_demo_mode(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json() == {"ok": True, "mode": "demo"}


def test_index_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "PlainSpeak" in html
    assert "Simplify it" in html


def test_samples_endpoint(client):
    r = client.get("/api/samples/medical")
    assert r.status_code == 200
    d = r.get_json()
    assert len(d["text"]) > 100
    r2 = client.get("/api/samples/nope")
    assert r2.status_code == 404


def test_simplify_rejects_empty(client):
    r = client.post("/api/simplify", json={"text": "   ", "level": "plain"})
    assert r.status_code == 400


def test_simplify_rejects_too_short(client):
    r = client.post("/api/simplify", json={"text": "too short", "level": "plain"})
    assert r.status_code == 400
    assert "50" in r.get_json()["error"]


def test_simplify_rejects_too_long(client):
    r = client.post("/api/simplify", json={"text": "x" * 5001, "level": "plain"})
    assert r.status_code == 400


def test_simplify_rejects_bad_level(client):
    r = client.post("/api/simplify", json={"text": "x" * 60, "level": "elvish"})
    assert r.status_code == 400


def test_simplify_demo_end_to_end(client, dense_text):
    r = client.post("/api/simplify", json={"text": dense_text, "level": "plain"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["mode"] == "demo"
    assert d["simplified"].strip()
    assert 1 <= len(d["takeaways"]) <= 3
    assert len(d["quiz"]) == 3
    for key in ("readability_before", "readability_after"):
        assert key in d
        assert "fk_grade" in d[key] and "label" in d[key]
    # the simplification should actually read easier than the input
    assert d["readability_after"]["fk_grade"] < d["readability_before"]["fk_grade"]


def test_simplify_live_path_mocked(client, dense_text, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")

    def fake_simplify(text, level):
        return {
            "mode": "live",
            "simplified": "Live plain version.",
            "takeaways": ["a", "b", "c"],
            "quiz": [
                {"question": "q?", "options": ["1", "2", "3", "4"], "answer": 0},
                {"question": "q?", "options": ["1", "2", "3", "4"], "answer": 1},
                {"question": "q?", "options": ["1", "2", "3", "4"], "answer": 2},
            ],
        }

    monkeypatch.setattr(llm, "simplify", fake_simplify)
    r = client.post("/api/simplify", json={"text": dense_text, "level": "pro"})
    assert r.status_code == 200
    assert r.get_json()["mode"] == "live"


def test_simplify_llm_failure_is_502(client, dense_text, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")

    def boom(text, level):
        raise llm.LLMError("bad key")

    monkeypatch.setattr(llm, "simplify", boom)
    r = client.post("/api/simplify", json={"text": dense_text, "level": "plain"})
    assert r.status_code == 502
    assert "error" in r.get_json()
