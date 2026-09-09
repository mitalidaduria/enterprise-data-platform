"""
Enterprise Data Platform: Raw Synthetic Data Generator
Generates mock multi-source operational datasets (Billing & Shipping)
with realistic PII, typos, and overlapping entity attributes for MDM testing.
"""

import csv
import hashlib
import os
import random
import uuid

# Configuration & Output Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
os.makedirs(DATA_DIR, exist_ok=True)

NUM_RECORD_PAIRS = 1000  # Generates 1,000 overlapping customer entities

FIRST_NAMES = ["Robert", "Bob", "Rob", "William", "Bill", "Elizabeth", "Liz", "Michael", "Mike", "Sarah"]
LAST_NAMES = ["Jones", "Smith", "Taylor", "Brown", "Wilson", "Davies", "Evans", "Thomas", "Johnson"]
STREETS = ["123 Main St", "456 Oak Ave", "789 Pine Rd", "101 Maple Dr", "202 Birch Ln"]
DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "enterprise.org"]

def generate_datasets():
    billing_rows = []
    shipping_rows = []

    for i in range(NUM_RECORD_PAIRS):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        domain = random.choice(DOMAINS)
        
        # Identity Anchor: Shared Email across systems
        raw_email = f"{first_name.lower()}.{last_name.lower()}{i}@"{domain}
        
        # 1. Billing System Record
        billing_id = f"BIL-{uuid.uuid4().hex[:8].upper()}"
        credit_card_hash = hashlib.sha256(f"CARD-{i}".encode()).hexdigest()
        billing_address = random.choice(STREETS)
        
        billing_rows.append([
            billing_id,
            full_name,
            raw_email,
            credit_card_hash,
            billing_address
        ])

        # 2. Shipping System Record (Slightly altered name/phone to test Fuzzy Match/MDM)
        shipping_id = f"SHP-{uuid.uuid4().hex[:8].upper()}"
        recipient_name = f"{first_name[0]}. {last_name}"  # e.g., "R. Jones" vs "Robert Jones"
        phone_number = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        street_address = billing_address  # Same physical address

        shipping_rows.append([
            shipping_id,
            recipient_name,
            raw_email,
            street_address,
            phone_number
        ])

    # Write Raw Billing File
    billing_path = os.path.join(DATA_DIR, "raw_billing.csv")
    with open(billing_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["billing_id", "full_name", "email", "credit_card_hash", "billing_address"])
        writer.writerows(billing_rows)

    # Write Raw Shipping File
    shipping_path = os.path.join(DATA_DIR, "raw_shipping.csv")
    with open(shipping_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["shipping_id", "recipient_name", "email", "street_address", "phone_number"])
        writer.writerows(shipping_rows)

    print(f"✅ Generated {NUM_RECORD_PAIRS} synthetic raw records in '{DATA_DIR}'")

if __name__ == "__main__":
    generate_datasets()
