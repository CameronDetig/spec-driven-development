import pytest


@pytest.mark.integration
@pytest.mark.requires_data
def test_known_query_returns_expected_top_document(client):
    """
    Verify that a known banking query retrieves the expected FAQ document.
    
    Spec: retrieval-pipeline.md
    Acceptance Criteria: "A known banking query retrieves an expected FAQ document as top result"
    """
    payload = {"question": "What are your checking account monthly fees?", "top_k": 3}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["retrieval"]["matched"] >= 1
    assert len(body["sources"]) >= 1

    top_source = body["sources"][0]
    combined = f"{top_source['title']} {top_source['snippet']}".lower()
    assert "checking" in combined or "checking_accounts" in top_source.get("id", "").lower()


@pytest.mark.integration
@pytest.mark.requires_data
def test_top_k_controls_maximum_number_of_sources(client):
    """
    Verify that changing top_k parameter controls the maximum returned source count.
    
    Spec: retrieval-pipeline.md
    Acceptance Criteria: "Changing `top_k` changes the maximum returned source count accordingly"
    """
    payload = {"question": "Tell me about bank account options", "top_k": 1}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert len(body["sources"]) <= 1
    assert body["retrieval"]["top_k"] == 1
    assert body["retrieval"]["matched"] == len(body["sources"])


@pytest.mark.integration
@pytest.mark.requires_data
def test_sources_are_sorted_by_descending_score(client):
    """
    Verify that source list is sorted by relevance score in descending order.
    
    Spec: retrieval-pipeline.md
    Acceptance Criteria: "Source list is sorted by score descending"
    """
    payload = {"question": "How do overdraft fees work?", "top_k": 5}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()
    if len(body["sources"]) < 2:
        assert body["retrieval"]["matched"] == len(body["sources"])
        return
    scores = [source["score"] for source in body["sources"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.integration
def test_unknown_query_returns_fallback_with_empty_sources(client):
    """
    Verify that out-of-domain query triggers unmatched retrieval (fallback) path.
    
    Spec: retrieval-pipeline.md
    Acceptance Criteria: "Unknown/out-of-domain query triggers unmatched retrieval path"
    """
    payload = {
        "question": "quartz nebula hedgehog protocol 91821 unrelated",
        "top_k": 3,
    }
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert isinstance(body["answer"], str)
    assert body["answer"].strip() != ""
    assert body["sources"] == []
    assert body["retrieval"]["top_k"] == 3
    assert body["retrieval"]["matched"] == 0
