import pandas as pd

# UN DESA publishes 5-year matrices (origin x destination). This loader melts to long schema.
def melt_undesa_matrix(df, year, origin_code_col="Origin", dest_code_cols=None):
    if dest_code_cols is None:
        dest_code_cols = [c for c in df.columns if c != origin_code_col]
    m = df.melt(id_vars=[origin_code_col], value_vars=dest_code_cols, var_name="dest_iso3", value_name="value")
    m["year"] = int(year)
    m["origin_iso3"] = m[origin_code_col]
    m["corridor"] = m["origin_iso3"].astype(str) + "->" + m["dest_iso3"].astype(str)
    m["metric"] = "migrant_stock"
    m["unit"] = "persons"
    m["source_id"] = "UN_DESA_MIG"
    m["trust_tier"] = "A_official"
    return m[["year","origin_iso3","dest_iso3","corridor","metric","value","unit","source_id","trust_tier"]]
