import pytest


@pytest.mark.integration
def test_health_returns_ok(client):
    """
    Verify that GET /health returns 200 with {"status": "ok"} JSON response.
    
    Spec: health-endpoint.md
    Acceptance Criteria: "Calling `GET /health` returns status code `200`"
                         "Response JSON includes key `status` with value `ok`"
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "application/json" in response.headers.get("content-type", "")
