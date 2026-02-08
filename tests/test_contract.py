def test_ask_response_contract_contains_required_top_level_keys(client):
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


def test_ask_response_sources_have_required_fields_when_present(client):
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


def test_ask_response_retrieval_metadata_has_required_fields(client):
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


def test_ask_fallback_keeps_stable_schema(client):
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
