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
             "OWN_CAR_AGE0": 5,
             "EXT_SOURCE_10": 0.45,
             "EXT_SOURCE_30": 0.62,
             "APARTMENTS_AVG0": 0.12,
             "BASEMENTAREA_AVG0": 0.08,
             "YEARS_BEGINEXPLUATATION_AVG0": 0.98,
             "YEARS_BUILD_AVG0": 0.75,
             "COMMONAREA_AVG0": 0.02,
             "ELEVATORS_AVG0": 0.11,
             "ENTRANCES_AVG0": 0.14,
             "AMT_CREDIT_MAX_OVERDUE0": 1200,
             "CNT_CREDIT_PROLONG0": 0,
             "AMT_CREDIT_SUM0": 150000,
             "AMT_CREDIT_SUM_DEBT0": 40000,
             "AMT_CREDIT_SUM_LIMIT0": 200000
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
             "OWN_CAR_AGE0": 5,
             "EXT_SOURCE_10": 0.45,
             "EXT_SOURCE_30": 0.62,
             "APARTMENTS_AVG0": 0.12,
             "BASEMENTAREA_AVG0": 0.08,
             "YEARS_BEGINEXPLUATATION_AVG0": 0.98,
             "YEARS_BUILD_AVG0": 0.75,
             "COMMONAREA_AVG0": 0.02,
             "ELEVATORS_AVG0": 0.11,
             "ENTRANCES_AVG0": 0.14,
             "AMT_CREDIT_MAX_OVERDUE0": 1200,
             "CNT_CREDIT_PROLONG0": 0,
             "AMT_CREDIT_SUM0": 150000,
             "AMT_CREDIT_SUM_DEBT0": 40000,
             "AMT_CREDIT_SUM_LIMIT0": 200000
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