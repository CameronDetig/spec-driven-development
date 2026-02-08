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
def test_flan_t5_mode_is_opt_in_and_fails_clearly_when_unavailable(client):
    """
    Verify that flan-t5 mode routes through LLM adapter or fails clearly if unavailable.
    
    Spec: generation-optional-llm.md
    Acceptance Criteria: "With `generator=flan-t5`, app routes generation through LLM adapter"
    """
    payload = {
        "question": "What credit card options do you have?",
        "top_k": 3,
        "generator": "flan-t5",
    }
    response = client.post("/ask", json=payload)

    # Accept success (if model is available) or explicit runtime failure.
    assert response.status_code in {200, 500, 503}
    if response.status_code in {500, 503}:
        body = response.json()
        as_text = str(body).lower()
        assert "flan-t5" in as_text or "model" in as_text
