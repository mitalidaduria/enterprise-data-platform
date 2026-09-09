# 🏛️ Enterprise Data Platform: MDM, Governance & Real-Time ML Gateway

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-orange.svg)](https://spark.apache.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, end-to-end data architecture platform that ingests multi-source transactional datasets, applies SHA-256 PII masking, resolves customer identities into an authoritative **Master Data Management (MDM) Golden Record**, and serves real-time machine learning predictions via a FastAPI Gateway.

---

## 📌 Executive Architecture Blueprint

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
