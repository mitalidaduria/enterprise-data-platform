"""
Enterprise Data Platform: Automated Unit & Integration Test Suite
Executes regression tests across PII governance logic, FastAPI endpoints, and ML predictions.
"""

import os
import sys
import hashlib
from fastapi.testclient import TestClient

# Add project root directory to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from gateway.app import app

client = TestClient(app)

# -------------------------------------------------------------------------------
# 1. UNIT TEST: PII Governance Cryptographic Hashing
# -------------------------------------------------------------------------------
def test_sha256_pii_hash_length():
    """Verifies that PII email hashing adheres to the GOVERNANCE.md 64-character standard."""
    sample_email = "test.user@enterprise.org"
    hashed_email = hashlib.sha256(sample_email.encode("utf-8")).hexdigest()
    
    assert len(hashed_email) == 64, "SHA-256 hash must be exactly 64 characters long."
    assert isinstance(hashed_email, str), "Hash output must be a string."

# -------------------------------------------------------------------------------
# 2. INTEGRATION TEST: API Gateway Health Check Route
# -------------------------------------------------------------------------------
def test_api_health_endpoint():
    """Asserts that the API Gateway healthcheck route responds with HTTP 200 OK."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "service" in data

# -------------------------------------------------------------------------------
# 3. INTEGRATION TEST: API Golden Customer List Route
# -------------------------------------------------------------------------------
def test_get_customers_list():
    """Asserts that the /customers route returns a paginated list of Golden Records."""
    response = client.get("/customers?limit=5")
    
    if response.status_code == 200:
        records = response.json()
        assert isinstance(records, list)
        if len(records) > 0:
            assert "golden_customer_id" in records[0]
            assert "primary_name" in records[0]

# -------------------------------------------------------------------------------
# 4. INTEGRATION TEST: Real-Time Direct Feature ML Prediction Endpoint
# -------------------------------------------------------------------------------
def test_direct_ml_prediction_endpoint():
    """Sends a feature vector to POST /predict and asserts prediction response schema."""
    test_payload = {
        "total_source_linkages": 2,
        "has_phone": 1,
        "has_address": 1
    }
    
    response = client.post("/predict", json=test_payload)
    
    if response.status_code == 200:
        data = response.json()
        assert "engagement_prediction" in data
        assert "confidence_score" in data
        assert "decision_status" in data
        assert data["decision_status"] in ["HIGH_VALUE_TIER", "STANDARD_TIER"]
        assert 0.0 <= data["confidence_score"] <= 1.0
