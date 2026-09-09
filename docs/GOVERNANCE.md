# Enterprise Data Platform - Governance & Security Policy

## 1. Overview
This document defines the data governance, security standards, and PII handling procedures enforced across the Enterprise Data Platform pipelines.

## 2. Personally Identifiable Information (PII) Classification
The platform categorizes data into three sensitivity tiers:
- **Tier 1 (Restricted / PII):** Real names, email addresses, phone numbers, and payment details. Must be masked or tokenized at the ingestion layer.
- **Tier 2 (Internal / Operational):** Non-sensitive transaction metadata, timestamps, product IDs, and behavioral logs.
- **Tier 3 (Public):** General catalog information and public product descriptions.

## 3. PII Masking & Transformation Rules
- **Ingestion Masking:** PySpark transformation jobs must apply regex and hashing algorithms to strip raw email addresses and phone numbers before writing data to the Master Data Management (MDM) layer.
- **Access Control:** Downstream consumers (e.g., machine learning models and REST APIs) interact exclusively with tokenized surrogate keys or aggregated feature stores.

## 4. Data Lineage & Audit Logging
- Every transformation step from raw source to Golden Record is tracked to maintain a verifiable audit trail for compliance verification.

# Data Governance & Compliance Framework

## 1. Overview & Objectives
This framework defines the security boundaries, quality enforcement gates, and data lineage standards across the Enterprise Data Platform.

## 2. Personally Identifiable Information (PII) & Security Protocols
To protect individual privacy and maintain compliance, all incoming PII fields are categorized and treated prior to persistence:

| Field Name | Category | Direct Storage Rule | Downstream / Analytics Access |
| :--- | :--- | :--- | :--- |
| `first_name` / `last_name` | PII | Anonymized / Hashed | Masked (e.g., "R*** J***") |
| `email_address` | PII Identifier | SHA-256 Hashed | Used strictly for Entity Resolution |
| `credit_card` / `payment_id` | Sensitive Financial | Encrypted / Hashed | Excluded from feature stores |
| `customer_id` | System Identifier | Stored Plaintext | Full access for primary key indexing |

## 3. Data Quality Gate Criteria
All PySpark ingestion jobs must pass three automated quality checks prior to writing into the Master Data Management layer:
1. **Null Checks:** Primary keys (`customer_id`, `email_hash`) must never contain null values.
2. **Range / Domain Validation:** Numerical fields must fall within valid logical bounds (e.g., `age > 0`).
3. **Uniqueness:** Entity-resolved primary records must enforce strict uniqueness across Golden Record IDs.

## 4. Data Lineage & Metadata Standards
Every persisted record within the platform must append mandatory audit metadata fields:
* `src_system_id`: The originating transactional database (e.g., `billing_db`, `shipping_db`).
* `ingested_at`: UTC timestamp recording when the row was ingested.
* `pipeline_version`: Version marker of the transformation code that produced the record.
