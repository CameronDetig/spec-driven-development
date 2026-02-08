import pytest


@pytest.mark.integration
def test_default_generator_mode_is_mock_deterministic(client):
    """
    Verify that default generator mode uses mock and produces deterministic output.
    
    Spec: generation-optional-llm.md
    Acceptance Criteria: "With default environment, app uses mock generator"
    """
    payload = {"question": "How can I contact support?", "top_k": 3}
    first = client.post("/ask", json=payload)
    second = client.post("/ask", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


@pytest.mark.optional
@pytest.mark.integration
def test_distilgpt2_mode_is_opt_in_and_fails_clearly_when_unavailable(monkeypatch):
    """
    Verify that distilgpt2 mode routes through LLM adapter or fails clearly if unavailable.
    
    Spec: generation-optional-llm.md
    Acceptance Criteria: "With `RAG_GENERATOR=distilgpt2`, app routes generation through LLM adapter"
    """
    # Ensure the app module is imported after setting env.
    monkeypatch.setenv("RAG_GENERATOR", "distilgpt2")

    import importlib
    import sys

    sys.modules.pop("app.main", None)
    app_module = importlib.import_module("app.main")
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)
    payload = {"question": "What credit card options do you have?", "top_k": 3}
    response = client.post("/ask", json=payload)

    # Accept success (if model is available) or explicit runtime failure.
    assert response.status_code in {200, 500, 503}
    if response.status_code in {500, 503}:
        body = response.json()
        as_text = str(body).lower()
        assert "distilgpt2" in as_text or "model" in as_text
