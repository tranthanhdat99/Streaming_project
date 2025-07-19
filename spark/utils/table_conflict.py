"""
Define ON CONFLICT clauses (or full conflict SQL) for each target table.
If a table is not listed here, the DEFAULT_CONFLICT_CLAUSE will be used.
"""

# For tables whose primary‐key column is not named "id", specify the column here:
CONFLICT_CLAUSES = {
    "public.location":    "ON CONFLICT (location_id) DO NOTHING",
    "public.store":    "ON CONFLICT (store_id) DO NOTHING",
    "public.time":         "ON CONFLICT (time_id) DO NOTHING",
    "public.product":         "ON CONFLICT (product_id) DO NOTHING",
    "public.referrer":         "ON CONFLICT (referrer_id) DO NOTHING",
    "public.os":         "ON CONFLICT (os_id) DO NOTHING",
    "public.browser":         "ON CONFLICT (browser_id) DO NOTHING",
    "public.fact_event":         "ON CONFLICT (event_id) DO NOTHING",
    # Add more tables and their conflict clauses here:
    # "schema.some_other_table": "ON CONFLICT (some_other_id) DO NOTHING",
}

# Fallback if a table is not explicitly listed above:
DEFAULT_CONFLICT_CLAUSE = "ON CONFLICT (id) DO NOTHING"
