import os
import duckdb

# --- Connect to DuckDB File ---
con = duckdb.connect(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "product_analytics_light.db"
    )
)

con.execute("""
CREATE OR REPLACE TABLE silver_deals AS
WITH fx AS (
    -- ECB euro reference rates, 6 Nov 2026 (units of currency per 1 EUR).
    -- The data is synthetic, so one fixed rate set is used for all dates.
    SELECT * FROM (VALUES
        ('EUR', 1.0),
        ('DKK', 7.4752),
        ('NOK', 10.5260),
        ('SEK', 11.0260),
        ('GBP', 0.83415)
    ) AS t(currency, units_per_eur)
)
SELECT
    deal_id,
    account_id,
    owner_user_id,
    pipeline_id,
    current_stage_id,
    LOWER(status) AS status,

    created_at,
    CAST(created_at AS DATE) AS created_date,

    closed_at,
    CAST(closed_at AS DATE) AS closed_date,

    last_stage_changed_at,
    CAST(last_stage_changed_at AS DATE) AS last_stage_changed_date,

    amount,
    UPPER(d.currency) AS currency,
    ROUND(amount / fx.units_per_eur, 2) AS amount_eur,
    UPPER(country_code) AS country_code,

    source_system,

    (closed_at IS NOT NULL) AS is_closed,

    CASE
        WHEN LOWER(status) IN ('won', 'closed_won') THEN TRUE
        ELSE FALSE
    END AS is_won,

    CASE
        WHEN closed_at IS NOT NULL
            THEN DATE_DIFF('day', CAST(created_at AS DATE), CAST(closed_at AS DATE))
        ELSE DATE_DIFF('day', CAST(created_at AS DATE), CURRENT_DATE)
    END AS deal_cycle_days,

    CASE
        WHEN CAST(created_at AS DATE) > CURRENT_DATE THEN 0
        ELSE DATE_DIFF('day', CAST(created_at AS DATE), CURRENT_DATE)
    END AS deal_age_days

FROM bronze_deals d
LEFT JOIN fx
    ON UPPER(d.currency) = fx.currency;
""")

print("Created silver_deals")
con.close()