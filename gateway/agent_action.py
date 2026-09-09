"""
Enterprise Data Platform: Autonomous AI Agent Service
Consumes REST API endpoints to evaluate Golden Customer profiles against ML decisions
and executes automated downstream business triggers.
"""

import time
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def run_autonomous_agent():
    print("🤖 [AI Agent] Starting Autonomous Decision Agent Service...")

    # 1. Healthcheck Request
    try:
        health_resp = requests.get(f"{API_BASE_URL}/health")
        if health_resp.status_code != 200:
            print(f"❌ [AI Agent Error] API Gateway unhealthy: {health_resp.json()}")
            return
        print(f"✅ [AI Agent] Connected to API Gateway ({health_resp.json()['service']})")
    except Exception as e:
        print(f"❌ [AI Agent Error] Could not connect to API Gateway at {API_BASE_URL}. Ensure FastAPI server is running! Error: {e}")
        return

    # 2. Fetch Customer List via API
    print("\n🔍 [AI Agent] Fetching Golden Customer profiles for automated evaluation...")
    cust_resp = requests.get(f"{API_BASE_URL}/customers?limit=10")
    if cust_resp.status_code != 200:
        print(f"❌ [AI Agent Error] Failed to fetch customers: {cust_resp.text}")
        return

    customers = cust_resp.json()
    print(f"📋 [AI Agent] Retrived {len(customers)} records for evaluation.")

    # 3. Evaluate Predictions and Trigger Autonomous Actions
    for idx, customer in enumerate(customers, 1):
        customer_id = customer["golden_customer_id"]
        customer_name = customer["primary_name"]

        # Call Real-Time ML Decision Endpoint
        pred_resp = requests.get(f"{API_BASE_URL}/predict/{customer_id}")
        if pred_resp.status_code != 200:
            print(f"⚠️ [AI Agent] Prediction skipped for {customer_id}: {pred_resp.text}")
            continue

        decision_data = pred_resp.json()
        prediction = decision_data["engagement_prediction"]
        confidence = decision_data["confidence_score"]
        status = decision_data["decision_status"]

        print(f"\n------------------------------------------------------------")
        print(f"👤 Record #{idx}: {customer_name} (ID: {customer_id[:12]}...)")
        print(f"   * Model Prediction : Class {prediction} ({status})")
        print(f"   * Confidence Score : {confidence * 100:.1f}%")

        # 4. Action Trigger Logic
        if status == "HIGH_VALUE_TIER" and confidence >= 0.70:
            trigger_vip_action(customer_name, customer_id, confidence)
        else:
            trigger_standard_action(customer_name, customer_id)

        time.sleep(0.5)

    print("\n✨ [AI Agent] Batch evaluation and action triggers complete.")

def trigger_vip_action(name: str, customer_id: str, confidence: float):
    """Simulates automated downstream business trigger for High-Value entities."""
    print(f"   🚀 [ACTION TRIGGERED] High-Value Loyalty Perks Issued for '{name}'!")
    print(f"      -> Payload sent to Loyalty Webhook | Confidence: {confidence}")

def trigger_standard_action(name: str, customer_id: str):
    """Simulates standard notification workflow."""
    print(f"   ℹ️  [ACTION TRIGGERED] Enrolled '{name}' in Standard Engagement Workflow.")

if __name__ == "__main__":
    run_autonomous_agent()
