import pytest


@pytest.mark.contract
@pytest.mark.integration
def test_ask_response_contract_contains_required_top_level_keys(client):
    """
    Verify that POST /ask response contains required top-level keys and types.
    
    Spec: ask-response-contract.md
    Acceptance Criteria: "Contract test validates required top-level keys exist on every 200 response"
    """
    payload = {"question": "What are your savings account options?", "top_k": 3}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert "answer" in body
    assert "sources" in body
    assert "retrieval" in body

    assert isinstance(body["answer"], str)
    assert isinstance(body["sources"], list)
    assert isinstance(body["retrieval"], dict)
    assert body["answer"].strip() != ""


@pytest.mark.contract
@pytest.mark.integration
@pytest.mark.requires_data
def test_ask_response_sources_have_required_fields_when_present(client):
    """
    Verify that source items in response contain all required fields with correct types.
    
    Spec: ask-response-contract.md
    Acceptance Criteria: "Contract test validates source item field presence and scalar types"
                         "Contract test validates `answer`, `id`, `title`, and `snippet` are non-empty strings"
    """
    payload = {"question": "Tell me about checking accounts", "top_k": 3}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    for source in body["sources"]:
        assert "id" in source
        assert "title" in source
        assert "snippet" in source
        assert "score" in source

        assert isinstance(source["id"], str)
        assert isinstance(source["title"], str)
        assert isinstance(source["snippet"], str)
        assert isinstance(source["score"], (int, float))
        assert source["id"].strip() != ""
        assert source["title"].strip() != ""
        assert source["snippet"].strip() != ""


@pytest.mark.contract
@pytest.mark.integration
def test_ask_response_retrieval_metadata_has_required_fields(client):
    """
    Verify that retrieval metadata contains required fields and matches payload.
    
    Spec: ask-response-contract.md
    Acceptance Criteria: "Retrieval metadata fields are always present and consistent with payload"
    """
    payload = {"question": "Do you offer auto loans?", "top_k": 2}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    retrieval = body["retrieval"]
    assert "top_k" in retrieval
    assert "matched" in retrieval
    assert isinstance(retrieval["top_k"], int)
    assert isinstance(retrieval["matched"], int)
    assert retrieval["top_k"] == 2
    assert retrieval["matched"] == len(body["sources"])


@pytest.mark.contract
@pytest.mark.integration
def test_ask_fallback_keeps_stable_schema(client):
    """
    Verify that fallback response (no matches) preserves full schema contract.
    
    Spec: ask-response-contract.md
    Acceptance Criteria: "Fallback path preserves full schema and uses empty `sources`"
    """
    payload = {
        "question": "zxqyqv synthetic non banking phrase no match please",
        "top_k": 3,
    }
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {"answer", "sources", "retrieval"}
    assert isinstance(body["answer"], str)
    assert body["answer"].strip() != ""
    assert body["sources"] == []
    assert isinstance(body["retrieval"], dict)
    assert body["retrieval"]["top_k"] == 3
    assert body["retrieval"]["matched"] == 0
