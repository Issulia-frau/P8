from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthcheck():
    r = client.get("/")
    assert r.status_code == 200


def test_predict():
    r = client.post("/predict", json={
        "inputs": [{"feature1": 1, "feature2": 2, "feature3": 3}]
    })
    assert r.status_code == 200


def test_predict_opti():
    r = client.post("/predictOpti", json={
        "inputs": [{"feature1": 1, "feature2": 2, "feature3": 3}]
    })
    assert r.status_code == 200
