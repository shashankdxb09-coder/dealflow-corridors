# Documentation
This folder will hold notes, source references, and GPT usage guides.

# Deep Corridors ETL Bundle (1970–2025)
**Scope:** 10 corridors (both directions) · Layers: Commodity (UN Comtrade) + Human (Remittances: KNOMAD; Migration: UN DESA).  
**Output:** 3 CSVs in `data_summary/` matching your GPT schema.

## How to run (locally / Colab)
1) `pip install -r requirements.txt`
2) (Optional) Set `UNCOMTRADE_API_KEY` env var for higher limits.
3) Run **build_all.py**:
```
python etl/build_all.py --start 1970 --end 2025 --corridors config/corridors.json --commodities config/commodities.json
```
4) Upload the resulting CSVs to your Custom GPT Knowledge.

## Files
- `config/corridors.json` — the 10 back-and-forth corridors.
- `config/commodities.json` — commodity names → HS codes.
- `etl/uncomtrade_fetch.py` — bilateral commodity extractor.
- `etl/knomad_remit_fetch.py` — remittance fetch helper (totals + bilateral where available).
- `etl/undesa_migration_fetch.py` — migration stock (5-year) normalizer.
- `etl/build_all.py` — orchestrates end-to-end fetch and writes CSVs.

## CSV Schemas
- **commodities_corridors.csv**: `year, origin_iso3, dest_iso3, corridor, commodity, metric, value, unit, source_id, trust_tier`
  - `metric`: export_value_usd, import_value_usd, export_volume, import_volume
- **remittances_corridors.csv**: `year, origin_iso3, dest_iso3, corridor, metric, value_usd, source_id, trust_tier`
  - `metric`: remittance_inflow_usd, remittance_outflow_usd
- **migration_stock_corridors.csv**: `year, origin_iso3, dest_iso3, corridor, metric, value, unit, source_id, trust_tier`
  - `metric`: migrant_stock; `year` available at 1990, 1995, ..., 2020

## Trust policy
- Use `A_official` for UN/WorldBank/official stats.
- Keep any non-official or derived estimates in a separate file with `trust_tier=D_other` (excluded from aggregation).

## Notes
- UN Comtrade recommends limiting requests; the script batches by year/HS code to avoid throttling.
- For EU aggregate (EUU), where reporter not directly available, sum EU members and document the method in a sidecar notes file.
