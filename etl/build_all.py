import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json, argparse, pandas as pd, os
from etl.uncomtrade_fetch import fetch_bilateral_series, HS_LABELS
from etl.knomad_remit_fetch import normalize_knomad
from etl.undesa_migration_fetch import melt_undesa_matrix

def load_corridors(path):
    with open(path,"r") as f:
        return json.load(f)["corridors"]

def load_commodities(path):
    with open(path,"r") as f:
        o = json.load(f)
    return o["commodities"], o["hs_codes"]

def main(args):
    corridors = load_corridors(args.corridors)
    commodities, hs_map = load_commodities(args.commodities)
    start, end = args.start, args.end
    years = list(range(start, end+1))

    # Map HS code → friendly commodity label
    HS_LABELS.update({v.split(",")[0]: k for k, v in hs_map.items()})

    # ---------------- UN Comtrade (commodities) ----------------
    commod_rows = []
    # Reporter/partner are ISO3 or numeric codes; API also accepts text codes.
    for corridor in corridors:
        rep, par = corridor.split("->")
        for cname, hs_code in hs_map.items():
            # Use the first HS code if there are multiple (for steel basket)
            first_code = hs_code.split(",")[0]
            try:
                commod_rows += fetch_bilateral_series(rep, par, years, first_code)
            except Exception as e:
                print("Comtrade error", corridor, cname, e)

    df_commod = pd.DataFrame(commod_rows)
    if not df_commod.empty:
        df_commod.to_csv("data_summary/commodities_corridors.csv", index=False)

    # ---------------- KNOMAD (remittances) ----------------
    # NOTE: KNOMAD bilateral CSV paths vary; put your downloaded file path here and normalize.
    # Example usage:
    # df = pd.read_csv("inputs/knomad_bilateral_remittances.csv")
    # df_norm = normalize_knomad(df, origin_col="origin_iso3", dest_col="dest_iso3", year_col="year", value_col="value_usd")
    # df_norm.to_csv("data_summary/remittances_corridors.csv", index=False)

    # ---------------- UN DESA (migration stock) ----------------
    # Example usage:
    # df = pd.read_csv("inputs/undesa_migrant_stock_2020.csv")
    # out = melt_undesa_matrix(df, year=2020, origin_code_col="Origin")
    # out.to_csv("data_summary/migration_stock_corridors.csv", index=False)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, default=1970)
    p.add_argument("--end", type=int, default=2025)
    p.add_argument("--corridors", type=str, required=True)
    p.add_argument("--commodities", type=str, required=True)
    args = p.parse_args()
    main(args)
