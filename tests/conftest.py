"""Shared fixtures for the PlainSpeak test suite."""
import pytest

import app as app_module


@pytest.fixture()
def client(monkeypatch):
    # Force demo mode in app tests unless a test overrides it.
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture()
def dense_text():
    return (
        "Notwithstanding anything to the contrary herein, the Contractor hereby "
        "assigns to the Client all right, title, and interest in and to any and "
        "all work product. In the event that any such assignment is deemed "
        "ineffective for any reason, the Contractor agrees to execute any and "
        "all documents necessary to facilitate said assignment, and compensation "
        "pursuant to this agreement shall be remitted subsequent to receipt of "
        "a valid invoice. The parties acknowledge that approximately forty-two "
        "individuals were utilized in the preparation of the deliverables."
    )
