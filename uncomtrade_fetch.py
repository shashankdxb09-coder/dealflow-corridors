import os, time, json, requests, pandas as pd
from urllib.parse import urlencode
from tqdm import tqdm

API = "https://comtradeapi.un.org/data/v1/get/"
API_KEY = os.environ.get("UNCOMTRADE_API_KEY","")

HS_LABELS = {}  # injected by build_all

def _req(params):
    headers = {"Accept":"application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    url = API + "commodities?" + urlencode(params)
    for attempt in range(5):
        r = requests.get(url, headers=headers, timeout=60)
        if r.status_code == 200:
            return r.json()
        time.sleep(2*(attempt+1))
    r.raise_for_status()

def fetch_bilateral_series(reporter, partner, years, hs_code):
    """Return list of dict rows for a single hs_code across years for both export/import values."""
    out = []
    for year in tqdm(years, desc=f"{reporter}->{partner} hs {hs_code}"):
        params = dict(
            typeCode="C",
            freqCode="A",
            clCode="HS",
            reporterCode=reporter,
            partnerCode=partner,
            period=year,
            cmdCode=hs_code,
            flowCode="M,X",  # imports and exports
            fmt="JSON"
        )
        data = _req(params)
        for d in data.get("dataset", []):
            flow = d.get("flowCode")
            metric = "import_value_usd" if flow == "M" else "export_value_usd"
            value = d.get("primaryValue")
            unit = "USD"
            out.append(dict(
                year=int(d.get("period")),
                origin_iso3=d.get("reporterISO"),
                dest_iso3=d.get("partnerISO"),
                corridor=f"{d.get('reporterISO')}->{d.get('partnerISO')}",
                commodity=HS_LABELS.get(hs_code, hs_code),
                metric=metric,
                value=value,
                unit=unit,
                source_id="UNCOMTRADE",
                trust_tier="A_official"
            ))
    return out
