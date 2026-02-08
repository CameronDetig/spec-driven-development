import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def default_generator_env(monkeypatch: pytest.MonkeyPatch):
    """
    Force deterministic generator mode for all tests unless explicitly overridden.
    
    This fixture automatically sets RAG_GENERATOR=mock for every test to ensure
    deterministic behavior and avoid requiring LLM model downloads during testing.
    
    Spec: generation-mock.md, generation-optional-llm.md
    Requirement: "Default generator MUST be selected when `RAG_GENERATOR` is unset or set to `mock`"
    """
    monkeypatch.setenv("RAG_GENERATOR", "mock")


@pytest.fixture()
def client() -> TestClient:
    """
    Provide a FastAPI TestClient for making HTTP requests to the API in tests.
    
    The app is imported lazily to provide clear failure messages if app.main
    doesn't exist yet. This fixture is used by all API integration tests.
    
    Returns:
        TestClient: Configured test client for the FastAPI application
    
    Spec: health-endpoint.md, ask-endpoint-validation.md, ask-response-contract.md
    Note: Used by all endpoint tests to interact with the API
    """
    try:
        from app.main import app
    except Exception as exc:  # pragma: no cover - explicit failure path for missing app
        pytest.fail(f"Could not import `app.main.app`: {exc}")

    return TestClient(app)
