import os
import duckdb
import pandas as pd

# --- Connect to DuckDB File ---
con = duckdb.connect(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "product_analytics_light.db"
    )
)

# --- Path to Excel File ---
excel_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Module_2_raw__geography--.xlsx"
)

# --- Load Excel into DataFrame ---
df = pd.read_excel(excel_path, sheet_name=0)

# --- Register DataFrame as temp view ---
con.register("raw_geography_df", df)

# --- Create Bronze Table ---
con.execute("""
CREATE OR REPLACE TABLE bronze_geography AS
SELECT
    country_code,
    country_name,
    region,
    market,
    currency,
    sales_region
FROM raw_geography_df;
""")

print("Created bronze_geography table successfully.")
con.close()