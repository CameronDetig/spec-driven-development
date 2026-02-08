import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def default_generator_env(monkeypatch: pytest.MonkeyPatch):
    """
    Force deterministic generator mode unless a test explicitly overrides it.
    """
    monkeypatch.setenv("RAG_GENERATOR", "mock")


@pytest.fixture()
def client() -> TestClient:
    """
    Import the FastAPI app lazily so tests clearly fail until app.main exists.
    """
    try:
        from app.main import app
    except Exception as exc:  # pragma: no cover - explicit failure path for missing app
        pytest.fail(f"Could not import `app.main.app`: {exc}")

    return TestClient(app)
