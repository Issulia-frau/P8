# API MLOps — Scoring Crédit

## Description

Ce projet expose un modèle de Machine Learning de scoring crédit via une API REST construite avec FastAPI.

L’API permet :
- de charger des modèles MLflow
- d’effectuer des prédictions
- de monitorer les performances du modèle
- de détecter le drift des données avec Evidently
- de centraliser les logs dans Elasticsearch
- d’utiliser une pipeline CI/CD avec GitHub Actions

---

# Fonctionnalités

## Endpoints API

### `GET /`
Healthcheck de l’API.

Réponse :

```json
{
  "status": "ok"
}
```

---

### `POST /predict`
Endpoint principal de prédiction.

---

### `POST /predictOpti`
Endpoint utilisant une version optimisée du modèle.

---

# Features utilisées par le modèle

| Feature |
|---|
| OWN_CAR_AGE0 |
| EXT_SOURCE_10 |
| EXT_SOURCE_30 |
| APARTMENTS_AVG0 |
| BASEMENTAREA_AVG0 |
| YEARS_BEGINEXPLUATATION_AVG0 |
| YEARS_BUILD_AVG0 |
| COMMONAREA_AVG0 |
| ELEVATORS_AVG0 |
| ENTRANCES_AVG0 |
| AMT_CREDIT_MAX_OVERDUE0 |
| CNT_CREDIT_PROLONG0 |
| AMT_CREDIT_SUM0 |
| AMT_CREDIT_SUM_DEBT0 |
| AMT_CREDIT_SUM_LIMIT0 |

---

# Exemple de requête

## Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{
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
}'
```

---

# Exemple de réponse

```json
{
  "request_id": "123456",
  "predictions": [0],
  "latency": 0.042
}
```

---

# Technologies utilisées

- Python 3.11
- FastAPI
- MLflow
- Pandas
- NumPy
- Evidently AI
- Elasticsearch
- Docker
- Pytest
- GitHub Actions

---

# Installation

## Cloner le projet

```bash
git clone <repo_url>
cd <repo>
```

---

## Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# Lancement de l’API

```bash
uvicorn main:app --reload
```

API disponible sur :

```text
http://localhost:8000
```

Documentation Swagger :

```text
http://localhost:8000/docs
```

---

# Tests

Lancer les tests :

```bash
pytest -v
```

---

# Docker

## Build image

```bash
docker build -t ml-api .
```

---

## Run container

```bash
docker run -p 8000:8000 ml-api
```

---

# CI/CD

Le projet utilise GitHub Actions pour :
- exécuter les tests automatisés
- vérifier le build Docker

Pipeline :

```text
Push / Pull Request
        |
        v
Pytest
        |
        v
Docker Build
```

---

# Monitoring

Le projet inclut :
- logging des requêtes
- mesure de latence
- profiling CPU
- détection de drift
- stockage Elasticsearch

---

# Variables d’environnement

| Variable | Description |
|---|---|
| `MODEL_URI` | URI MLflow du modèle principal |
| `MODEL_URI2` | URI MLflow du modèle optimisé |
| `ELASTIC_URL` | URL Elasticsearch |
| `TEST_MODE` | Active le mode test |

---

# Structure du projet

```text
project/
│
├── main.py
├── test_api.py
├── requirements.txt
├── Dockerfile
├── reference_sample.csv
│
└── .github/
    └── workflows/
        └── ci.yml
```
