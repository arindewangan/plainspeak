"""Tests for llm.py — config, validation, and mocked HTTP behaviour.

No real network calls: every HTTP interaction is monkeypatched.
"""
import json

import pytest
import requests

import llm


def test_has_key_false_without_env(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    assert llm.has_key() is False


def test_has_key_true_with_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    assert llm.has_key() is True


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    cfg = llm.get_config()
    assert cfg["base_url"] == "https://api.openai.com/v1"
    assert cfg["model"] == "gpt-4o-mini"


def test_simplify_requires_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(llm.LLMError):
        llm.simplify("some text " * 20, "plain")


def test_simplify_rejects_unknown_level(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    with pytest.raises(llm.LLMError):
        llm.simplify("some text " * 20, "martian")


class _FakeResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def _good_payload():
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "simplified": "Plain version here.",
                            "takeaways": ["one", "two", "three"],
                            "quiz": [
                                {"question": "q1?", "options": ["a", "b", "c", "d"], "answer": 0},
                                {"question": "q2?", "options": ["a", "b", "c", "d"], "answer": 1},
                                {"question": "q3?", "options": ["a", "b", "c", "d"], "answer": 2},
                            ],
                        }
                    )
                }
            }
        ]
    }


def test_simplify_success_mocked(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: _FakeResp(200, _good_payload())
    )
    out = llm.simplify("some dense text " * 10, "plain")
    assert out["mode"] == "live"
    assert out["simplified"] == "Plain version here."
    assert len(out["takeaways"]) == 3
    assert len(out["quiz"]) == 3
    assert out["quiz"][0]["answer"] == 0


def test_simplify_sends_bearer_and_json_format(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-secret")
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResp(200, _good_payload())

    monkeypatch.setattr(requests, "post", fake_post)
    llm.simplify("some dense text " * 10, "age12")
    assert captured["headers"]["Authorization"] == "Bearer sk-secret"
    assert captured["json"]["response_format"] == {"type": "json_object"}
    assert "12-year-old" in captured["json"]["messages"][1]["content"]


def test_simplify_http_error(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResp(401, {}))
    with pytest.raises(llm.LLMError, match="HTTP 401"):
        llm.simplify("some dense text " * 10, "plain")


def test_simplify_network_failure(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")

    def boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(requests, "post", boom)
    with pytest.raises(llm.LLMError, match="could not reach"):
        llm.simplify("some dense text " * 10, "plain")


def test_simplify_bad_json_shape(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    bad = {"choices": [{"message": {"content": json.dumps({"simplified": "x"})}}]}
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResp(200, bad))
    with pytest.raises(llm.LLMError):
        llm.simplify("some dense text " * 10, "plain")
