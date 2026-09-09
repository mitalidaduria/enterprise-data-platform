"""
Enterprise Data Platform: PySpark Data Quality Gates & Quarantine Pipeline
Validates staging datasets against strict domain rules and segregates invalid records.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, current_timestamp, lit

def run_quality_gates():
    # 1. Initialize PySpark Session
    spark = SparkSession.builder \
        .appName("EnterpriseDataQualityGates") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    print("🔍 Initializing Data Quality Validation Engine...")

    base_dir = os.path.dirname(__file__)
    staging_dir = os.path.join(base_dir, "staging_data")
    validated_dir = os.path.join(base_dir, "validated_data")
    quarantine_dir = os.path.join(base_dir, "quarantine_data")

    # Helper function to validate Billing data
    def validate_billing():
        path = os.path.join(staging_dir, "stg_billing.parquet")
        if not os.path.exists(path):
            print("⚠️ Staging Billing data not found.")
            return

        df = spark.read.parquet(path)
        total_count = df.count()

        # Define Data Quality Validation Rules
        rule_valid_pk = col("billing_id").isNotNull() & (col("billing_id") != "")
        rule_valid_hash = col("email_hash").isNotNull() & (length(col("email_hash")) == 64)

        valid_condition = rule_valid_pk & rule_valid_hash

        # Split into Valid and Quarantined DataFrames
        df_valid = df.filter(valid_condition)
        df_quarantine = df.filter(~valid_condition) \
            .withColumn("quarantine_reason", lit("Failed PK or SHA-256 Hash Length Check")) \
            .withColumn("quarantined_at", current_timestamp())

        # Write Validated Records
        valid_out = os.path.join(validated_dir, "stg_billing_validated.parquet")
        df_valid.write.mode("overwrite").parquet(valid_out)

        # Write Quarantined Records
        quarantine_out = os.path.join(quarantine_dir, "stg_billing_quarantine.parquet")
        df_quarantine.write.mode("overwrite").parquet(quarantine_out)

        print(f"✅ [Billing Quality Gate] Total: {total_count} | Valid: {df_valid.count()} | Quarantined: {df_quarantine.count()}")

    # Helper function to validate Shipping data
    def validate_shipping():
        path = os.path.join(staging_dir, "stg_shipping.parquet")
        if not os.path.exists(path):
            print("⚠️ Staging Shipping data not found.")
            return

        df = spark.read.parquet(path)
        total_count = df.count()

        # Define Validation Rules
        rule_valid_pk = col("shipping_id").isNotNull() & (col("shipping_id") != "")
        rule_valid_hash = col("email_hash").isNotNull() & (length(col("email_hash")) == 64)
        rule_valid_phone = col("phone_number").isNotNull()

        valid_condition = rule_valid_pk & rule_valid_hash & rule_valid_phone

        # Split into Valid and Quarantined DataFrames
        df_valid = df.filter(valid_condition)
        df_quarantine = df.filter(~valid_condition) \
            .withColumn("quarantine_reason", lit("Failed PK, SHA-256 Hash, or Phone Check")) \
            .withColumn("quarantined_at", current_timestamp())

        # Write Validated Records
        valid_out = os.path.join(validated_dir, "stg_shipping_validated.parquet")
        df_valid.write.mode("overwrite").parquet(valid_out)

        # Write Quarantined Records
        quarantine_out = os.path.join(quarantine_dir, "stg_shipping_quarantine.parquet")
        df_quarantine.write.mode("overwrite").parquet(quarantine_out)

        print(f"✅ [Shipping Quality Gate] Total: {total_count} | Valid: {df_valid.count()} | Quarantined: {df_quarantine.count()}")

    # Execute Gate Evaluations
    validate_billing()
    validate_shipping()

    spark.stop()

if __name__ == "__main__":
    run_quality_gates()
