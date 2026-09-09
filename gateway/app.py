"""
Enterprise Data Platform: REST API Gateway & Real-Time ML Decision Engine
Serves MDM Golden Customer Profiles and executes live machine learning predictions.
"""

import os
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
import joblib
import pandas as pd

# Initialize FastAPI App
app = FastAPI(
    title="Enterprise Data Platform - MDM REST API & Decision Gateway",
    description="Serves Master Data Management (MDM) Golden Records and real-time ML model predictions.",
    version="1.1.0"
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "infrastructure", "enterprise_data.db")
MODEL_PATH = os.path.join(BASE_DIR, "models", "customer_model.joblib")

# In-Memory Global Model Storage
model_artifact = None

@app.on_event("startup")
def load_model_on_startup():
    """Loads serialized Scikit-Learn model into RAM at server startup for ultra-fast inference."""
    global model_artifact
    if os.path.exists(MODEL_PATH):
        model_artifact = joblib.load(MODEL_PATH)
        print(f"🚀 [Startup] Loaded Machine Learning Model Artifact from '{MODEL_PATH}'")
    else:
        print(f"⚠️ [Startup Warning] Model artifact not found at '{MODEL_PATH}'. Run train_model.py first.")

# Database Helper
def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not initialized. Run load_db.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Pydantic Schema Models ---
class GoldenCustomerResponse(BaseModel):
    golden_customer_id: str
    primary_name: str
    primary_email_hash: str
    primary_phone: Optional[str] = None
    primary_address: Optional[str] = None
    billing_linkage_id: Optional[str] = None
    shipping_linkage_id: Optional[str] = None
    total_source_linkages: int
    pipeline_version: str

class DirectPredictionRequest(BaseModel):
    total_source_linkages: int = Field(..., example=2, description="Number of linked source systems (1 or 2)")
    has_phone: int = Field(..., example=1, description="Phone presence flag (1 = Yes, 0 = No)")
    has_address: int = Field(..., example=1, description="Address presence flag (1 = Yes, 0 = No)")

class PredictionResponse(BaseModel):
    golden_customer_id: Optional[str] = None
    engagement_prediction: int = Field(..., example=1, description="Predicted class (1 = High Engagement, 0 = Standard)")
    confidence_score: float = Field(..., example=0.89, description="Model prediction probability score")
    decision_status: str = Field(..., example="HIGH_VALUE_TIER", description="Business decision output category")

# --- API Endpoints ---

@app.get("/health", tags=["System"])
def health_check():
    """System Health Check Endpoint."""
    model_status = "LOADED" if model_artifact is not None else "NOT_LOADED"
    return {
        "status": "HEALTHY",
        "service": "MDM REST API Gateway",
        "model_status": model_status,
        "version": "v1.1.0"
    }

@app.get("/customers/{customer_id}", response_model=GoldenCustomerResponse, tags=["Customers"])
def get_customer_by_id(customer_id: str = Path(..., description="The unique golden_customer_id hash")):
    """Fetch an authoritative Golden Customer profile by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dim_customer_golden WHERE golden_customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Golden Customer record '{customer_id}' not found.")

    return dict(row)

@app.get("/predict/{customer_id}", response_model=PredictionResponse, tags=["ML Decisioning"])
def predict_customer_decision(customer_id: str = Path(..., description="The unique golden_customer_id hash")):
    """Real-Time ML Inference: Looks up a customer's Golden Record and computes an automated decision score."""
    if model_artifact is None:
        raise HTTPException(status_code=500, detail="ML Model is not loaded. Train model first.")

    # 1. Fetch Golden Record
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dim_customer_golden WHERE golden_customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Golden Customer record '{customer_id}' not found.")

    record = dict(row)

    # 2. Extract Feature Vector on the Fly
    total_source_linkages = record.get("total_source_linkages", 1)
    has_phone = 1 if record.get("primary_phone") else 0
    has_address = 1 if record.get("primary_address") else 0

    feature_matrix = pd.DataFrame([{
        "total_source_linkages": total_source_linkages,
        "has_phone": has_phone,
        "has_address": has_address
    }])

    # 3. Model Inference
    prediction = int(model_artifact.predict(feature_matrix)[0])
    probabilities = model_artifact.predict_proba(feature_matrix)[0]
    confidence = round(float(probabilities[prediction]), 4)

    decision_status = "HIGH_VALUE_TIER" if prediction == 1 else "STANDARD_TIER"

    return PredictionResponse(
        golden_customer_id=customer_id,
        engagement_prediction=prediction,
        confidence_score=confidence,
        decision_status=decision_status
    )

@app.post("/predict", response_model=PredictionResponse, tags=["ML Decisioning"])
def predict_direct_features(payload: DirectPredictionRequest):
    """Direct Feature ML Inference: Accepts raw feature values and returns an instant decision score."""
    if model_artifact is None:
        raise HTTPException(status_code=500, detail="ML Model is not loaded.")

    feature_matrix = pd.DataFrame([{
        "total_source_linkages": payload.total_source_linkages,
        "has_phone": payload.has_phone,
        "has_address": payload.has_address
    }])

    prediction = int(model_artifact.predict(feature_matrix)[0])
    probabilities = model_artifact.predict_proba(feature_matrix)[0]
    confidence = round(float(probabilities[prediction]), 4)

    decision_status = "HIGH_VALUE_TIER" if prediction == 1 else "STANDARD_TIER"

    return PredictionResponse(
        golden_customer_id="AD_HOC_EVALUATION",
        engagement_prediction=prediction,
        confidence_score=confidence,
        decision_status=decision_status
    )
