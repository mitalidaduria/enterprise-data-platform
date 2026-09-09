"""
Enterprise Data Platform: REST API Gateway
Serves MDM Golden Customer Profiles and Feature Aggregations via FastAPI endpoints.
"""

import os
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

# Initialize FastAPI App
app = FastAPI(
    title="Enterprise Data Platform - MDM REST API",
    description="Serves authoritative Master Data Management (MDM) Golden Customer Records and features.",
    version="1.0.0"
)

# Database Connection Helper
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infrastructure", "enterprise_data.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not initialized. Run load_db.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Response Pydantic Schema Model
class GoldenCustomerResponse(BaseModel):
    golden_customer_id: str = Field(..., example="a1b2c3d4...")
    primary_name: str = Field(..., example="Robert Jones")
    primary_email_hash: str = Field(..., example="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    primary_phone: Optional[str] = Field(None, example="555-0199")
    primary_address: Optional[str] = Field(None, example="123 Main St")
    billing_linkage_id: Optional[str] = Field(None, example="BIL-9921")
    shipping_linkage_id: Optional[str] = Field(None, example="SHP-1042")
    total_source_linkages: int = Field(..., example=2)
    pipeline_version: str = Field(..., example="v1.0.0")

@app.get("/health", tags=["System"])
def health_check():
    """System Health Endpoint."""
    return {"status": "HEALTHY", "service": "MDM REST API Gateway", "version": "v1.0.0"}

@app.get("/customers/{customer_id}", response_model=GoldenCustomerResponse, tags=["Customers"])
def get_customer_by_id(
    customer_id: str = Path(..., description="The unique golden_customer_id hash")
):
    """Fetch an authoritative Golden Record profile by primary ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dim_customer_golden WHERE golden_customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Golden Customer record '{customer_id}' not found.")

    return dict(row)

@app.get("/customers", response_model=List[GoldenCustomerResponse], tags=["Customers"])
def list_customers(
    limit: int = Query(10, ge=1, le=100, description="Number of records to return")
):
    """Retrieve a paginated list of Golden Customer profiles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dim_customer_golden LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
