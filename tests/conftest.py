import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is importable for app/ and ui/ modules.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def default_generator_env(monkeypatch: pytest.MonkeyPatch):
    """
    Force deterministic generator mode for all tests unless explicitly overridden.
    
    This fixture forces mock generator usage for deterministic tests.
    
    Spec: generation-mock.md, generation-optional-llm.md
    Requirement: "Default generator MUST be selected when no generator is specified or when `generator=mock`"
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

    client_instance = TestClient(app)

    # Ensure retrieval DB is built once tests start hitting /ask endpoints.
    status_resp = client_instance.get("/db/status")
    if status_resp.status_code == 200 and not status_resp.json().get("built", False):
        build_resp = client_instance.post("/db/build")
        if build_resp.status_code != 200:
            pytest.fail(f"Could not build retrieval DB for tests: {build_resp.text}")

    return client_instance
