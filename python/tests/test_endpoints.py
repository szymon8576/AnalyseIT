def test_sentence_claassification(client):

    for used_model in ["BERT", "LSTM"]:

        data = {"texts": ["This is test sentence.", "Another sentence."], "used_model": used_model}

        response = client.post('/classify-sentences', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert len(result) == len(data["texts"])
        assert "neutral" in result[0].keys()


def test_sentence_claassification_with_invalid_model(client):
    data = {
        "texts": ["This is test sentence.", "Another sentence."],
        "used_model": "DecisionTree"
    }

    response = client.post('/classify-sentences', json=data)
    assert response.status_code == 404
    assert b"Model DecisionTree not found" in response.data


def test_report_generation(client):
    data = {"texts": ["This is test sentence.", "Another sentence."]}

    response = client.post('/generate-report', json=data)
    assert response.status_code == 200

    result = response.get_json()
    assert "full_report" in result.keys()


def test_health_check(client):
    response = client.get('/health-check')
    assert response.status_code == 200
    assert response.data == b"OK"