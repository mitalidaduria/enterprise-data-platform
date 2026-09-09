"""
Enterprise Data Platform: PySpark Distributed Ingestion Pipeline
Enforces PII SHA-256 Hashing, Lineage Tracking, and Parquet Storage.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, sha2, col

def run_ingestion_pipeline():
    # 1. Initialize PySpark Session
    spark = SparkSession.builder \
        .appName("EnterpriseDataIngestion") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    print("🚀 PySpark Session Initialized Successfully.")

    base_dir = os.path.dirname(__file__)
    raw_dir = os.path.join(base_dir, "raw_data")
    staging_dir = os.path.join(base_dir, "staging_data")

    # ---------------------------------------------------------------------------
    # 2. Ingest & Transform Billing Data
    # ---------------------------------------------------------------------------
    billing_raw_path = os.path.join(raw_dir, "raw_billing.csv")
    if os.path.exists(billing_raw_path):
        df_billing = spark.read.csv(billing_raw_path, header=True, inferSchema=True)
        
        # Enforce Governance & Lineage
        df_billing_transformed = df_billing \
            .withColumn("email_hash", sha2(col("email"), 256)) \
            .withColumn("src_system_id", lit("BILLING_DB")) \
            .withColumn("ingested_at", current_timestamp()) \
            .withColumn("pipeline_version", lit("v1.0.0"))
        
        # Write to Staging Parquet
        billing_out = os.path.join(staging_dir, "stg_billing.parquet")
        df_billing_transformed.write.mode("overwrite").parquet(billing_out)
        print(f"✅ Billing Data Ingested & Cleansed: {df_billing_transformed.count()} rows -> Parquet")

    # ---------------------------------------------------------------------------
    # 3. Ingest & Transform Shipping Data
    # ---------------------------------------------------------------------------
    shipping_raw_path = os.path.join(raw_dir, "raw_shipping.csv")
    if os.path.exists(shipping_raw_path):
        df_shipping = spark.read.csv(shipping_raw_path, header=True, inferSchema=True)
        
        # Enforce Governance & Lineage
        df_shipping_transformed = df_shipping \
            .withColumn("email_hash", sha2(col("email"), 256)) \
            .withColumn("src_system_id", lit("SHIPPING_DB")) \
            .withColumn("ingested_at", current_timestamp()) \
            .withColumn("pipeline_version", lit("v1.0.0"))
        
        # Write to Staging Parquet
        shipping_out = os.path.join(staging_dir, "stg_shipping.parquet")
        df_shipping_transformed.write.mode("overwrite").parquet(shipping_out)
        print(f"✅ Shipping Data Ingested & Cleansed: {df_shipping_transformed.count()} rows -> Parquet")

    spark.stop()

if __name__ == "__main__":
    run_ingestion_pipeline()
