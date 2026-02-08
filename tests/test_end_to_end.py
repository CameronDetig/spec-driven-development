import pytest


@pytest.mark.integration
def test_known_question_returns_expected_doc_and_answer(client):
    """
    Verify that a known question returns the expected top document and a non-empty answer.

    Spec: retrieval-pipeline.md, generation-mock.md, ask-response-contract.md
    Acceptance: known query -> top doc + answer + retrieval metadata
    """
    payload = {"question": "What are your checking account monthly fees?", "top_k": 3}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["sources"], "Expected at least one source for known question"
    top_source = body["sources"][0]
    assert top_source["id"] == "checking_accounts"
    assert top_source["title"].lower().startswith("mockridge bank checking")
    assert isinstance(body["answer"], str) and body["answer"].strip() != ""
    assert body["retrieval"]["matched"] >= 1


@pytest.mark.integration
def test_pipeline_happy_path_returns_sorted_sources_and_metadata(client):
    """
    Verify end-to-end pipeline returns sorted sources, consistent metadata, and non-empty answer.

    Spec: retrieval-pipeline.md, ask-response-contract.md, generation-mock.md
    Acceptance: sorted scores, matched count, non-empty answer
    """
    payload = {"question": "Tell me about overdraft coverage and fees", "top_k": 2}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["retrieval"]["top_k"] == 2
    assert body["retrieval"]["matched"] == len(body["sources"])

    if len(body["sources"]) > 1:
        scores = [s["score"] for s in body["sources"]]
        assert scores == sorted(scores, reverse=True)

    for src in body["sources"]:
        assert isinstance(src["id"], str) and src["id"] != ""
        assert isinstance(src["title"], str) and src["title"] != ""
        assert isinstance(src["snippet"], str) and src["snippet"] != ""
        assert isinstance(src["score"], (int, float))

    assert isinstance(body["answer"], str) and body["answer"].strip() != ""
