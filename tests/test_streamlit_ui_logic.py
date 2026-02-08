import importlib

import pytest


@pytest.mark.unit
def test_get_db_status_normalizes_payload(monkeypatch):
    """
    Verify DB status helper returns normalized minimal payload for the UI.

    Spec: streamlit-ui.md
    Acceptance Criteria: "DB status payload is normalized to `built` and `doc_count` for UI consumption"
    """
    pytest.importorskip("streamlit")
    module = importlib.import_module("ui.streamlit_app")

    class _FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"built": True, "doc_count": 11, "indexed_count": 11, "collection": "faq"}

    monkeypatch.setattr(module.requests, "get", lambda *args, **kwargs: _FakeResponse())

    built, payload, error = module._get_db_status()

    assert built is True
    assert payload == {"built": True, "doc_count": 11}
    assert error == ""


@pytest.mark.unit
def test_get_db_status_handles_non_200(monkeypatch):
    """
    Verify DB status helper reports HTTP failures as a non-empty error string.

    Spec: streamlit-ui.md
    Acceptance Criteria: "DB status helper surfaces HTTP failures without crashing the UI flow"
    """
    pytest.importorskip("streamlit")
    module = importlib.import_module("ui.streamlit_app")

    class _FakeResponse:
        status_code = 503

    monkeypatch.setattr(module.requests, "get", lambda *args, **kwargs: _FakeResponse())

    built, payload, error = module._get_db_status()

    assert built is False
    assert payload == {}
    assert "DB status request failed (503)." in error
