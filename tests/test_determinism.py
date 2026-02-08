def test_same_input_produces_same_output(client):
    payload = {"question": "Do you support fraud disputes in the mobile app?", "top_k": 3}

    first = client.post("/ask", json=payload)
    second = client.post("/ask", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
