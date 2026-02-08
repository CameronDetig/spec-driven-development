import pytest


@pytest.mark.validation
@pytest.mark.integration
def test_ask_missing_question_returns_400(client):
    """
    Verify that POST /ask returns 400 when question field is missing.
    
    Spec: ask-endpoint-validation.md
    Acceptance Criteria: "Missing `question` returns `400`"
    """
    response = client.post("/ask", json={})
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_question_too_short_returns_400(client):
    """
    Verify that POST /ask returns 400 when question is shorter than 5 characters.
    
    Spec: ask-endpoint-validation.md
    Acceptance Criteria: "`question` shorter than 5 characters returns `400`"
    """
    payload = {"question": "hey", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_question_too_long_returns_400(client):
    """
    Verify that POST /ask returns 400 when question is longer than 300 characters.
    
    Spec: ask-endpoint-validation.md
    Acceptance Criteria: "`question` longer than 300 characters returns `400`"
    """
    payload = {"question": "x" * 301, "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_top_k_zero_returns_400(client):
    """
    Verify that POST /ask returns 400 when top_k is 0.
    
    Spec: ask-endpoint-validation.md
    Acceptance Criteria: "`top_k = 0` returns `400`"
    """
    payload = {"question": "What are your overdraft fees?", "top_k": 0}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_top_k_above_range_returns_400(client):
    """
    Verify that POST /ask returns 400 when top_k is above the valid range (>5).
    
    Spec: ask-endpoint-validation.md
    Acceptance Criteria: "`top_k > 5` returns `400`"
    """
    payload = {"question": "What are your overdraft fees?", "top_k": 6}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_omitted_top_k_uses_default(client):
    """
    Verify that POST /ask accepts omitted top_k and defaults to 3.
    
    Spec: ask-endpoint-validation.md
    Acceptance Criteria: "Omitted `top_k` is accepted and treated as `3`"
    """
    payload = {"question": "What are your overdraft fees?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    assert response.json()["retrieval"]["top_k"] == 3


@pytest.mark.validation
@pytest.mark.integration
def test_ask_question_min_length_is_allowed(client):
    """
    Verify that POST /ask accepts a question at minimum length (5 characters).
    
    Spec: ask-endpoint-validation.md
    Requirement: "`question` is required string with length `5..300`"
    """
    payload = {"question": "abcde", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200


@pytest.mark.validation
@pytest.mark.integration
def test_ask_question_max_length_is_allowed(client):
    """
    Verify that POST /ask accepts a question at maximum length (300 characters).
    
    Spec: ask-endpoint-validation.md
    Requirement: "`question` is required string with length `5..300`"
    """
    payload = {"question": "x" * 300, "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200


@pytest.mark.validation
@pytest.mark.integration
def test_ask_top_k_negative_returns_400(client):
    """
    Verify that POST /ask returns 400 when top_k is negative.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`top_k` is optional integer with default `3` and valid range `1..5`"
    """
    payload = {"question": "What are your overdraft fees?", "top_k": -1}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_top_k_non_int_returns_400(client):
    """
    Verify that POST /ask returns 400 when top_k is not an integer.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`top_k` is optional integer with default `3` and valid range `1..5`"
    """
    payload = {"question": "What are your overdraft fees?", "top_k": "three"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_empty_string_question_returns_400(client):
    """
    Verify that POST /ask returns 400 when question is an empty string.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`question` is required string with length `5..300`"
    Edge case: Empty string is different from missing field
    """
    payload = {"question": "", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_whitespace_only_question_returns_400(client):
    """
    Verify that POST /ask returns 400 when question contains only whitespace.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`question` is required string with length `5..300`"
    Edge case: Whitespace-only strings should not be accepted
    """
    payload = {"question": "     ", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_null_question_returns_400(client):
    """
    Verify that POST /ask returns 400 when question is null/None.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`question` is required string with length `5..300`"
    Edge case: Null values should be rejected
    """
    payload = {"question": None, "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_top_k_float_returns_400(client):
    """
    Verify that POST /ask returns 400 when top_k is a float.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`top_k` is optional integer with default `3` and valid range `1..5`"
    Edge case: Float values like 2.5 should be rejected
    """
    payload = {"question": "What are your overdraft fees?", "top_k": 2.5}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_top_k_null_returns_400(client):
    """
    Verify that POST /ask returns 400 when top_k is explicitly null/None.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`top_k` is optional integer with default `3` and valid range `1..5`"
    Edge case: Explicit null is different from omitted field and should be rejected
    """
    payload = {"question": "What are your overdraft fees?", "top_k": None}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.validation
@pytest.mark.integration
def test_ask_question_with_special_characters_is_allowed(client):
    """
    Verify that POST /ask accepts questions with special characters.
    
    Spec: ask-endpoint-validation.md
    Edge case: Special characters should be allowed as long as length is valid
    """
    payload = {"question": "What's the APR% for credit cards?", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200


@pytest.mark.validation
@pytest.mark.integration
def test_ask_question_with_unicode_is_allowed(client):
    """
    Verify that POST /ask accepts questions with unicode characters.
    
    Spec: ask-endpoint-validation.md
    Edge case: Unicode characters should be supported
    """
    payload = {"question": "¿Cuáles son las tarifas de sobregiro?", "top_k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200


@pytest.mark.validation
@pytest.mark.integration
def test_ask_generator_invalid_returns_400(client):
    """
    Verify that POST /ask returns 400 when generator is not an allowed value.
    
    Spec: ask-endpoint-validation.md
    Requirement: "`generator` is optional string with allowed values `mock` or `distilgpt2`"
    """
    payload = {"question": "What are your overdraft fees?", "top_k": 3, "generator": "gpt4"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("application/json")
    assert "detail" in response.json()
