#  Enterprise Data Platform: MDM, Governance & Real-Time ML Gateway

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-orange.svg)](https://spark.apache.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, end-to-end data architecture platform that ingests multi-source transactional datasets, applies SHA-256 PII masking, resolves customer identities into an authoritative **Master Data Management (MDM) Golden Record**, and serves real-time machine learning predictions via a FastAPI Gateway.

---

##  Executive Architecture Blueprint

```mermaid
flowchart TD
    subgraph Ingestion ["1. Distributed Ingestion Layer (/pipelines)"]
        A1[Billing DB CSV] --> B1[PySpark Engine]
        A2[Shipping DB CSV] --> B1
        B1 -->|SHA-256 PII Hashing| C1[Staging Parquet Files]
    end

    subgraph Governance ["2. Data Quality & MDM Engine"]
        C1 --> D1{Data Quality Gates}
        D1 -->|Valid| E1[Deterministic & Fuzzy Entity Resolution]
        D1 -->|Invalid| Q1[Quarantine Storage]
        E1 -->|Survivorship Matrix| F1[dim_customer_golden]
    end

    subgraph Serving ["3. Relational Serving & API Gateway (/gateway)"]
        F1 --> G1[(SQLite Database)]
        G1 --> H1[FastAPI Service]
        I1[Scikit-Learn ML Model] -->|In-Memory Loading| H1
    end

    subgraph Action ["4. Consumers & Autonomous Action"]
        H1 -->|REST Endpoint| J1[Real-Time Decision API]
        H1 -->|Automated Triggers| K1[Autonomous AI Agent]
    end
```
## Key Features & Architectural Highlights
Distributed PySpark Ingestion: Ingests and transforms multi-source operational records using distributed PySpark DataFrames.
Cryptographic PII Governance: Enforces SHA-256 cryptographic hashing (sha2) on sensitive identifiers (emails) prior to persistence, adhering to GOVERNANCE.md compliance policies.
Automated Quality Quarantine: Evaluates schema assertions (PK uniqueness, string length domain bounds) and routes corrupted data into isolated quarantine storage.
MDM & Entity Resolution: Executes deterministic matching on identity anchors (email_hash) and applies system-trust Survivorship Rules to create an authoritative Golden Record.
Low-Latency REST Gateway: Serves customer profiles and features via a FastAPI service with automated OpenAPI/Swagger interactive documentation.
Real-Time ML Decisioning: Features an in-memory Scikit-Learn Random Forest model that evaluates customer feature vectors and returns instant prediction probabilities.
Autonomous Action Agent: Consumes API routes to automate downstream business workflows (e.g., loyalty webhooks) based on model decision outputs.

##  Repository Structure
enterprise-data-platform/
├── docs/                   # System Architecture, Governance, & ERD Data Models
│   ├── ARCHITECTURE.md
│   ├── GOVERNANCE.md
│   └── DATA_MODEL.md
├── infrastructure/         # Relational Schema DDL & Database Loaders
│   ├── schema.sql
│   ├── load_db.py
│   └── enterprise_data.db
├── pipelines/              # PySpark ETL, Quality Gates, MDM, & Orchestration
│   ├── generate_data.py
│   ├── ingest_pyspark.py
│   ├── data_quality.py
│   ├── entity_resolution.py
│   └── orchestrator.py
├── gateway/                # REST API Service & Autonomous AI Agent
│   ├── app.py
│   └── agent_action.py
├── models/                 # Feature Engineering & ML Model Training
│   ├── train_model.py
│   └── customer_model.joblib
└── README.md               # Master Repository Documentation
