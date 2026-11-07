import os
import subprocess
import sys

# --- Run every layer in dependency order ---
HERE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    "bronze/bronze_accounts.py",
    "bronze/bronze_users.py",
    "bronze/bronze_deals.py",
    "bronze/bronze_product_events.py",
    "bronze/bronze_geography.py",

    "silver/silver_geography.py",
    "silver/silver_accounts.py",
    "silver/silver_users.py",
    "silver/silver_deals.py",
    "silver/silver_product_events.py",

    "gold/gold_dim_geography.py",
    "gold/gold_dim_accounts.py",
    "gold/gold_dim_users.py",
    "gold/gold_fact_deals.py",
    "gold/gold_fact_product_events.py",
    "gold/gold_fact_product_events_aggregated.py",
    "gold/gold_fact_advanced_activation.py",
]

for step in STEPS:
    print(f"--> {step}", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, step)], check=True)

print("Pipeline complete.")
