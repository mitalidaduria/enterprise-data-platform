"""
Enterprise Data Platform: Parquet to Relational DB Loader
Loads validated Parquet Golden Records into SQLite database for API serving.
"""

import os
import sqlite3
import pandas as pd

def load_parquet_to_sqlite():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    parquet_path = os.path.join(base_dir, "pipelines", "validated_data", "dim_customer_golden.parquet")
    db_path = os.path.join(base_dir, "infrastructure", "enterprise_data.db")

    if not os.path.exists(parquet_path):
        print(f"❌ Parquet file not found at {parquet_path}. Run entity_resolution.py first.")
        return

    # Read Parquet via Pandas
    df_golden = pd.read_parquet(parquet_path)

    # Establish SQLite Connection and Write Table
    conn = sqlite3.connect(db_path)
    df_golden.to_sql("dim_customer_golden", conn, if_exists="replace", index=False)
    conn.close()

    print(f"✅ Successfully loaded {len(df_golden)} Golden Records into '{db_path}' (Table: dim_customer_golden)")

if __name__ == "__main__":
    load_parquet_to_sqlite()
