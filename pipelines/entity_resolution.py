"""
Enterprise Data Platform: PySpark Entity Resolution & MDM Engine
Executes deterministic matching on PII hashes and applies Survivorship Rules
to produce the authoritative Customer Golden Record dataset.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, coalesce, when, lit, current_timestamp, sha2, concat_ws
)

def run_entity_resolution():
    # 1. Initialize PySpark Session
    spark = SparkSession.builder \
        .appName("EnterpriseMDMEntityResolution") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    print("🔄 Starting Master Data Management (MDM) Entity Resolution...")

    base_dir = os.path.dirname(__file__)
    validated_dir = os.path.join(base_dir, "validated_data")

    billing_path = os.path.join(validated_dir, "stg_billing_validated.parquet")
    shipping_path = os.path.join(validated_dir, "stg_shipping_validated.parquet")

    if not (os.path.exists(billing_path) and os.path.exists(shipping_path)):
        print("❌ Validated datasets missing. Run data_quality.py first.")
        spark.stop()
        return

    # 2. Read Validated Staging Parquet Files
    df_billing = spark.read.parquet(billing_path).alias("bil")
    df_shipping = spark.read.parquet(shipping_path).alias("shp")

    # 3. Deterministic Matching via FULL OUTER JOIN on email_hash
    df_matched = df_billing.join(
        df_shipping,
        col("bil.email_hash") == col("shp.email_hash"),
        "full_outer"
    )

    # 4. Apply Survivorship Rules & Construct Golden Record
    # Identity Anchor: Select whichever email_hash is present
    anchor_email_hash = coalesce(col("bil.email_hash"), col("shp.email_hash"))

    # Survivorship Strategy:
    # - Name: Trust Billing DB first, fallback to Shipping
    # - Address: Trust Shipping DB first (more recent delivery address), fallback to Billing
    # - Phone: Take Shipping phone number
    df_golden = df_matched.select(
        # Unique Golden Key generated deterministically from Anchor Hash
        sha2(concat_ws("_", lit("GOLDEN"), anchor_email_hash), 256).alias("golden_customer_id"),
        
        # Attribute Survivorship
        coalesce(col("bil.full_name"), col("shp.recipient_name")).alias("primary_name"),
        anchor_email_hash.alias("primary_email_hash"),
        col("shp.phone_number").alias("primary_phone"),
        coalesce(col("shp.street_address"), col("bil.billing_address")).alias("primary_address"),
        
        # Linkage Auditing & Lineage
        col("bil.billing_id").alias("billing_linkage_id"),
        col("shp.shipping_id").alias("shipping_linkage_id"),
        
        # Total Source Linkages Calculation
        when(col("bil.billing_id").isNotNull() & col("shp.shipping_id").isNotNull(), 2)
        .otherwise(1).alias("total_source_linkages"),
        
        current_timestamp().alias("created_at"),
        current_timestamp().alias("updated_at"),
        lit("v1.0.0").alias("pipeline_version")
    )

    # 5. Persist Golden Record to Parquet
    golden_out = os.path.join(validated_dir, "dim_customer_golden.parquet")
    df_golden.write.mode("overwrite").parquet(golden_out)

    total_golden = df_golden.count()
    multi_source_matches = df_golden.filter(col("total_source_linkages") == 2).count()

    print(f"✨ Entity Resolution Complete!")
    print(f"📊 Total Golden Records: {total_golden}")
    print(f"🔗 Successfully Merged Multi-Source Entities: {multi_source_matches}")

    spark.stop()

if __name__ == "__main__":
    run_entity_resolution()
