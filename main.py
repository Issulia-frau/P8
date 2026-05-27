"""
import mlflow.pyfunc
from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()

MODEL_URI = os.getenv("MODEL_URI", "runs:/<BEST_RUN_ID>/model")

model = mlflow.pyfunc.load_model(MODEL_URI)

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: dict):
    df = pd.DataFrame(data["inputs"])
    preds = model.predict(df)
    return {"predictions": preds.tolist()}
"""



"""
train_mean = X1.mean()
prod_mean = df.mean()

drift = (prod_mean - train_mean).abs()

logging.info({"drift": drift.to_dict()})

"""


import mlflow.pyfunc
from fastapi import FastAPI, HTTPException
import pandas as pd
import os
import time
import logging
import uuid
import cProfile
import pstats
import io
import json
from evidently import Report
from evidently.presets import DataDriftPreset
import copy
import numpy as np

from elasticsearch import Elasticsearch
import threading
import os


app = FastAPI()
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

if TEST_MODE:
    model = None
    model2 = None
    REFERENCE_DF = None
else:
    REFERENCE_DF = pd.read_csv("reference_sample.csv")
    model = mlflow.pyfunc.load_model(MODEL_URI)
    model2 = mlflow.pyfunc.load_model(MODEL_URI2)
    
    MODEL_URI = os.getenv("MODEL_URI", "runs:/c6d38647e7e94d7795d9b13950b0c3cd/model")
    MODEL_URI2 = os.getenv("MODEL_URI", "runs:/2dfdd4935e3e4492b06b0db361e5d1f9/model")



logging.basicConfig(level=logging.INFO)


TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

if not TEST_MODE:
    model = mlflow.pyfunc.load_model(MODEL_URI)
    model2 = mlflow.pyfunc.load_model(MODEL_URI2)
    REFERENCE_DF = pd.read_csv("reference_sample.csv")
else:
    model = None
    model2 = None
    REFERENCE_DF = None
#--------------fix for warnings------------------------
def sanitize(df):
    df = df.copy()

    def clean_value(x):
        if hasattr(x, "item"):
            x = x.item()
        if isinstance(x, (list, dict)):
            return str(x)   # force scalar
        return x

    for col in df.columns:
        df[col] = df[col].apply(clean_value)

    return df




def make_es_safe(obj):
    return json.loads(
        json.dumps(obj, default=str, ensure_ascii=False)
    )

#-------------fix warning numpy--------------------------

def prepare_for_drift(df):
    df = df.copy()

    df = df.replace([float("inf"), float("-inf")], None)

    # ONLY drop completely empty columns
    df = df.dropna(axis=1, how="all")

    return df


def prepare_for_drift_noneval(df):
    df = df.copy()

    # Replace infinities
    df = df.replace([float("inf"), float("-inf")], np.nan)

    # Replace sentinel missing values
    df = df.replace(-1, np.nan)

    # Drop only completely empty columns
    df = df.dropna(axis=1, how="all")

    return df



#----------------------------------------

# Elasticsearch

es = Elasticsearch(os.getenv("ELASTIC_URL", "http://localhost:9200"))
INDEX_NAME = "ml-api-logs"
DRIFT_INDEX = "ml-drift-reports"

def log_to_es(doc):
    """Non-blocking ES logging"""
    try:
        es.index(index=INDEX_NAME, document=doc)
    except Exception as e:
        logging.error(f"Elasticsearch logging failed: {e}")




#----------------------------------------------------------------------
"""
        #drift_result = report.as_dict()
        #drift_result = report.dict()
        #drift_result = report.json()
        if hasattr(report, "as_dict"):
            drift_result = report.as_dict()
        elif hasattr(report, "dict"):
            drift_result = report.dict()
        elif hasattr(report, "json"):
            drift_result = report.json()
        else:
         drift_result = str(report)

        # fix warning json
        drift_result = json.loads(json.dumps(drift_result, default=str))
"""

"""
def run_drift_check(current_df):

    try:

        report = Report(
            metrics=[
                DataDriftPreset()
            ]
        )

        report.run(
            reference_data=REFERENCE_DF,
            current_data=current_df
        )

        if hasattr(report, "as_dict"):
            drift_result = report.as_dict()
        else:
            drift_result = str(report)


        #drift_result = make_es_safe(drift_result)



        es.index(
            index=DRIFT_INDEX,
            document=make_es_safe(drift_result)
            #document=drift_result
        )

        logging.info("Drift report stored")

    except Exception as e:
        logging.error(f"Drift detection failed: {e}")

"""

def safe_serialize(obj):
    return json.loads(
        json.dumps(obj, default=str, ensure_ascii=False)
    )


#-------------------------------------------------------------
def flatten_drift(test_json):
    metrics = test_json["metrics"]

    summary = {
        "timestamp": time.time(),
        "drift_share": None,
        "drifted_columns_count": None
    }

    features = []

    for m in metrics:

        name = m["metric_name"]

        # dataset-level drift
        if "DriftedColumnsCount" in name:
            summary["drifted_columns_count"] = m["value"]["count"]
            summary["drift_share"] = m["value"]["share"]

        # feature-level drift
        if "ValueDrift" in name:
            features.append({
                "feature": m["config"]["column"],
                "drift_score": m["value"]
            })

    return summary, features

#---------------------------------------------------------------------


def run_drift_check(current_df):
    try:

        report = Report(metrics=[DataDriftPreset()])

        test = report.run(
            reference_data=REFERENCE_DF,
            current_data=current_df
        )

        # serialize actual evaluation result
        if hasattr(test, "json"):
            payload = test.json()

            if isinstance(payload, str):
                payload = json.loads(payload)

        elif hasattr(test, "dict"):
            payload = test.dict()

        elif hasattr(test, "model_dump"):
            payload = test.model_dump()

        else:
            payload = {"result": str(test)}


        summary, features = flatten_drift(payload)

        # 1. global drift metrics (for charts)
        es.index(
            index="ml-drift-metrics",
            document=summary
        )

        # 2. per-feature drift rows (for ranking charts)
        for f in features:
            es.index(
                index="ml-drift-metrics",
                document={
                    "timestamp": summary["timestamp"],
                    "feature": f["feature"],
                    "drift_score": f["drift_score"]
                }
            )
        # IMPORTANT:
        # store as string to avoid ES mapping conflicts
        es_doc = {
            "timestamp": time.time(),
            "report": json.dumps(payload)
        }

        es.index(
            index=DRIFT_INDEX,
            document=es_doc
        )

        logging.info("Drift report stored")

    except Exception:
        logging.exception("Drift detection failed")
#---------------------------------------------------------------------

def run_drift_check_api2(current_df):
    try:

        report = Report(metrics=[DataDriftPreset()])

        test = report.run(
            reference_data=REFERENCE_DF,
            current_data=current_df
        )

        # serialize actual evaluation result
        if hasattr(test, "json"):
            payload = test.json()

            if isinstance(payload, str):
                payload = json.loads(payload)

        elif hasattr(test, "dict"):
            payload = test.dict()

        elif hasattr(test, "model_dump"):
            payload = test.model_dump()

        else:
            payload = {"result": str(test)}


        summary, features = flatten_drift(payload)

        # 1. global drift metrics (for charts)
        es.index(
            index="ml-drift-metrics",
            document=summary
        )

        # 2. per-feature drift rows (for ranking charts)
        for f in features:
            es.index(
                index="ml-drift-api2",
                document={
                    "timestamp": summary["timestamp"],
                    "feature": f["feature"],
                    "drift_score": f["drift_score"]
                }
            )
        # IMPORTANT:
        # store as string to avoid ES mapping conflicts
        es_doc = {
            "timestamp": time.time(),
            "report": json.dumps(payload)
        }

        es.index(
            index=DRIFT_INDEX,
            document=es_doc
        )

        logging.info("Drift report stored")

    except Exception:
        logging.exception("Drift detection failed")

#---------------------------------------------------------------------


@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: dict):

    if model is None:
        return {
            "request_id": "test-mode",
            "predictions": [0] * len(df),
            "latency": 0
        }

    
    request_id = str(uuid.uuid4())
    start_time = time.time()


    pr = cProfile.Profile()
    pr.enable()


    try:
        df = pd.DataFrame(data["inputs"])

        preds = model.predict(df)

        latency = time.time() - start_time

        pr.disable()


        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumtime")
        ps.print_stats(10)  # top 10 slowest functions

        profile_output = s.getvalue()



        log_data = {
            "request_id": request_id,
            #"inputs": df.to_dict(),
            #"inputs": df.to_dict(orient="records"),
            "inputs" : sanitize(df).to_dict(orient="records"),
            "predictions": preds.tolist(),
            "latency": latency,
            "profile": profile_output
        }

        #logging.info(log_data)
        logging.info(json.dumps(log_data))

        # Elasticsearch log
        threading.Thread(
            target=log_to_es,
            args=(log_data,),
            daemon=True
        ).start()

        #drift log

        df_clean = prepare_for_drift(df)
        #df_clean.to_csv("mrclean.csv",index=False)
        threading.Thread(
            target=run_drift_check,
            #args=(df.copy(),),
            #args=(prepare_for_drift(df),),
            args=(df_clean,),
            daemon=True
        ).start()

        return {
            "request_id": request_id,
            "predictions": preds.tolist(),
            "latency": latency
        }

    except Exception as e:
        pr.disable()
        latency = time.time() - start_time

        logging.error({
            "request_id": request_id,
            "error": str(e),
            "latency": latency
        })

        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/predictOpti")
def predict2(data: dict):


    if model is None:
        return {
            "request_id": "test-mode",
            "predictions": [0] * len(df),
            "latency": 0
        }


    
    request_id = str(uuid.uuid4())
    start_time = time.time()

    
    pr = cProfile.Profile()
    pr.enable()


    try:
        df = pd.DataFrame(data["inputs"])

        preds = model2.predict(df)

        latency = time.time() - start_time

        pr.disable()


        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumtime")
        ps.print_stats(10)  # top 10 slowest functions

        profile_output = s.getvalue()



        log_data = {
            "request_id": request_id,
            #"inputs": df.to_dict(),
            #"inputs": df.to_dict(orient="records"),
            "inputs" : sanitize(df).to_dict(orient="records"),
            "predictions": preds.tolist(),
            "latency": latency,
            "profile": profile_output
        }

        #logging.info(log_data)
        logging.info(json.dumps(log_data))

        # Elasticsearch log
        threading.Thread(
            target=log_to_es,
            args=(log_data,),
            daemon=True
        ).start()

        #drift log

        df_clean = prepare_for_drift_noneval(df)
        #df_clean.to_csv("mrclean.csv",index=False)
        threading.Thread(
            target=run_drift_check_api2,
            #args=(df.copy(),),
            #args=(prepare_for_drift(df),),
            args=(df_clean,),
            daemon=True
        ).start()

        return {
            "request_id": request_id,
            "predictions": preds.tolist(),
            "latency": latency
        }

    except Exception as e:
        pr.disable()
        latency = time.time() - start_time

        logging.error({
            "request_id": request_id,
            "error": str(e),
            "latency": latency
        })

        raise HTTPException(status_code=500, detail=str(e))
    


    #analyse perf cprofile cpu gpu
    #onnx
    #
