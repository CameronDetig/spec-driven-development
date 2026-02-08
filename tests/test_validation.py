def test_ask_missing_question_returns_400(client):
    response = client.post("/ask", json={})
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


def test_ask_question_too_short_returns_400(client):
    payload = {"question": "hey", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


def test_ask_question_too_long_returns_400(client):
    payload = {"question": "x" * 301, "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


def test_ask_top_k_zero_returns_400(client):
    payload = {"question": "What are your overdraft fees?", "top_k": 0}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


def test_ask_top_k_above_range_returns_400(client):
    payload = {"question": "What are your overdraft fees?", "top_k": 6}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


def test_ask_omitted_top_k_uses_default(client):
    payload = {"question": "What are your overdraft fees?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    assert response.json()["retrieval"]["top_k"] == 3


def test_ask_question_min_length_is_allowed(client):
    payload = {"question": "abcde", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200


def test_ask_question_max_length_is_allowed(client):
    payload = {"question": "x" * 300, "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200


def test_ask_top_k_negative_returns_400(client):
    payload = {"question": "What are your overdraft fees?", "top_k": -1}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


def test_ask_top_k_non_int_returns_400(client):
    payload = {"question": "What are your overdraft fees?", "top_k": "three"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()
