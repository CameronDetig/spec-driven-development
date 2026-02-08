import pytest


@pytest.mark.integration
def test_db_status_endpoint_returns_expected_keys(client):
    response = client.get("/db/status")
    assert response.status_code == 200
    body = response.json()

    assert "built" in body
    assert "doc_count" in body
    assert "indexed_count" in body
    assert "collection" in body


@pytest.mark.integration
def test_db_build_endpoint_builds_or_confirms_build(client):
    response = client.post("/db/build")
    assert response.status_code == 200
    body = response.json()

    assert body["doc_count"] > 0
    assert body["indexed_count"] >= body["doc_count"]
    assert body["built"] is True
