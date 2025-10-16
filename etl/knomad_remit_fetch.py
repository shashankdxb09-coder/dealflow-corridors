import pandas as pd, requests, io, zipfile

# KNOMAD maintains remittance datasets; bilateral availability varies.
# This function loads a "by destination" or "bilateral" CSV and maps to schema.
def normalize_knomad(df, origin_col, dest_col, year_col, value_col, origin_iso_map=None, dest_iso_map=None):
    origin = df[origin_col].map(origin_iso_map) if origin_iso_map else df[origin_col]
    dest = df[dest_col].map(dest_iso_map) if dest_iso_map else df[dest_col]
    out = pd.DataFrame({
        "year": df[year_col].astype(int),
        "origin_iso3": origin,
        "dest_iso3": dest,
        "corridor": origin.astype(str) + "->" + dest.astype(str),
        "metric": "remittance_outflow_usd",   # flip to inflow if you ingest from the destination perspective
        "value_usd": pd.to_numeric(df[value_col], errors="coerce"),
        "source_id": "WORLD_BANK_KNOMAD",
        "trust_tier": "A_official"
    })
    return out
