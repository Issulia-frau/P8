import requests

BASE_URL = "http://localhost:8000"


def test_healthcheck():
    response = requests.get(f"{BASE_URL}/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict():
    payload = {
        "inputs": [
            {
                "feature1": 10,
                "feature2": 5,
                "feature3": 1
            }
        ]
    }

    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload
    )

    assert response.status_code == 200

    body = response.json()

    assert "predictions" in body
    assert "request_id" in body
    assert "latency" in body


def test_predict_opti():
    payload = {
        "inputs": [
            {
                "feature1": 10,
                "feature2": 5,
                "feature3": 1
            }
        ]
    }

    response = requests.post(
        f"{BASE_URL}/predictOpti",
        json=payload
    )

    assert response.status_code == 200

    body = response.json()

    assert "predictions" in body
    assert "request_id" in body
    assert "latency" in body