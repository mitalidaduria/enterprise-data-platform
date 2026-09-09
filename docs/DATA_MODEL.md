# MDM Logical Data Model & Entity Resolution Specification

## 1. Executive Summary
This document defines the logical architecture for unifying disparate source systems (`billing`, `shipping`, `support`) into an authoritative **Customer Golden Record** table via Master Data Management (MDM) logic.

## 2. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    STG_BILLING {
        string billing_id PK
        string full_name
        string email
        string credit_card_hash
        timestamp updated_at
    }

    STG_SHIPPING {
        string shipping_id PK
        string recipient_name
        string street_address
        string phone_number
        timestamp updated_at
    }

    DIM_CUSTOMER_GOLDEN {
        string golden_customer_id PK
        string primary_name
        string primary_email_hash
        string primary_phone
        string primary_address
        int total_source_linkages
        timestamp created_at
        timestamp updated_at
    }

    STG_BILLING ||--o| DIM_CUSTOMER_GOLDEN : "resolves_to"
    STG_SHIPPING ||--o| DIM_CUSTOMER_GOLDEN : "resolves_to"
