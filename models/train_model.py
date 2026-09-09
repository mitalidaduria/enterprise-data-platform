"""
Enterprise Data Platform: Machine Learning Training & Decision Engine
Extracts features from Golden Customer Records, trains a Scikit-Learn classifier,
evaluates performance metrics, and exports the serialized model artifact.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def train_decision_model():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "infrastructure", "enterprise_data.db")
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(db_path):
        print(f"❌ Database not found at '{db_path}'. Run load_db.py first.")
        return

    # 1. Fetch Golden Record Data
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM dim_customer_golden", conn)
    conn.close()

    if df.empty:
        print("❌ 'dim_customer_golden' table is empty.")
        return

    print(f"📊 Loaded {len(df)} Golden Records for Feature Engineering.")

    # 2. Feature Engineering Matrix Construct
    # Feature 1: Total Source Linkages (1 or 2)
    # Feature 2: Has Primary Phone (1 or 0)
    # Feature 3: Has Primary Address (1 or 0)
    df["has_phone"] = df["primary_phone"].apply(lambda x: 1 if pd.notnull(x) and x != "" else 0)
    df["has_address"] = df["primary_address"].apply(lambda x: 1 if pd.notnull(x) and x != "" else 0)

    X = df[["total_source_linkages", "has_phone", "has_address"]]

    # Synthetic Target Label for Decision Demonstration:
    # High-value engagement score probability derived from feature completeness
    np.random.seed(42)
    synthetic_prob = (
        0.4 * df["total_source_linkages"] + 
        0.3 * df["has_phone"] + 
        0.3 * df["has_address"]
    ) / 2.0
    y = (synthetic_prob + np.random.normal(0, 0.1, len(df)) > 0.5).astype(int)

    # 3. Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Train Model (Random Forest Classifier)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # 5. Evaluate Metrics
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print("\n🎯 --- Model Training & Evaluation Metrics ---")
    print(f"  * Accuracy : {accuracy:.4f}")
    print(f"  * Precision: {precision:.4f}")
    print(f"  * Recall   : {recall:.4f}")
    print(f"  * F1-Score : {f1:.4f}")

    # 6. Serialize and Save Model Artifact
    model_path = os.path.join(model_dir, "customer_model.joblib")
    joblib.dump(clf, model_path)
    print(f"\n💾 Serialized Model saved successfully to '{model_path}'")

if __name__ == "__main__":
    train_decision_model()
