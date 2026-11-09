import os
import sys
import duckdb

# --- Connect to DuckDB File ---
con = duckdb.connect(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "product_analytics_light.db"
    ),
    read_only=True
)

# Each check returns the number of rows that break the rule; 0 means pass.
CHECKS = {
    # Keys: present and unique
    "gold_dim_accounts: AccountId is unique and not null": """
        SELECT COUNT(*) - COUNT(DISTINCT AccountId) FROM gold_dim_accounts
    """,
    "gold_dim_users: UserId is unique and not null": """
        SELECT COUNT(*) - COUNT(DISTINCT UserId) FROM gold_dim_users
    """,
    "gold_dim_geography: CountryCode is unique and not null": """
        SELECT COUNT(*) - COUNT(DISTINCT CountryCode) FROM gold_dim_geography
    """,
    "gold_fact_deals: DealId is unique and not null": """
        SELECT COUNT(*) - COUNT(DISTINCT DealId) FROM gold_fact_deals
    """,
    "gold_fact_product_events: EventId is unique and not null": """
        SELECT COUNT(*) - COUNT(DISTINCT EventId) FROM gold_fact_product_events
    """,

    # Relationships: every fact row points to a known account
    "gold_fact_product_events: every event has a known account": """
        SELECT COUNT(*)
        FROM gold_fact_product_events e
        LEFT JOIN gold_dim_accounts a ON e.AccountId = a.AccountId
        WHERE a.AccountId IS NULL
    """,
    "gold_fact_deals: every deal has a known account": """
        SELECT COUNT(*)
        FROM gold_fact_deals d
        LEFT JOIN gold_dim_accounts a ON d.AccountId = a.AccountId
        WHERE a.AccountId IS NULL
    """,

    # Standardized values
    "gold_dim_accounts: AccountStatus uses the standard values": """
        SELECT COUNT(*) FROM gold_dim_accounts
        WHERE AccountStatus NOT IN ('active', 'churned', 'cancelled')
    """,
    "gold_fact_deals: every amount has a EUR conversion": """
        SELECT COUNT(*) FROM gold_fact_deals
        WHERE DealAmount IS NOT NULL AND DealAmountEUR IS NULL
    """,

    # Activation model
    "gold_fact_advanced_activation: one row per account": """
        SELECT (SELECT COUNT(*) FROM gold_fact_advanced_activation)
             - (SELECT COUNT(*) FROM gold_dim_accounts)
    """,
    "gold_fact_advanced_activation: time to value falls inside the 14-day window": """
        SELECT COUNT(*) FROM gold_fact_advanced_activation
        WHERE IsActivated AND TimeToValueDays NOT BETWEEN 0 AND 14
    """,
    "gold_fact_advanced_activation: activation flag matches activation date": """
        SELECT COUNT(*) FROM gold_fact_advanced_activation
        WHERE IsActivated <> (ActivationDate IS NOT NULL)
    """,
}

failures = 0
for name, sql in CHECKS.items():
    bad_rows = con.execute(sql).fetchone()[0]
    status = "PASS" if bad_rows == 0 else f"FAIL ({bad_rows} rows)"
    if bad_rows != 0:
        failures += 1
    print(f"{status:<16} {name}")

con.close()

print(f"\n{len(CHECKS) - failures} of {len(CHECKS)} checks passed.")
sys.exit(1 if failures else 0)
