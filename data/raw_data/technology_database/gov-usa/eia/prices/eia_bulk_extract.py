"""Extract the price series from EIA bulk files into long-format CSVs.

    python data/raw-data/gov-usa/eia/prices/eia_bulk_extract.py

Reads the EIA bulk downloads saved beside this script (one JSON object per line):

  eia_2026_bulk-coal.zip  ->  eia_2026_bulk-coal_delivered-prices.csv
                              price of coal delivered to each end-use sector by
                              state and census division, annual and quarterly
                              (the history behind Annual Coal Report Table 34)
                          ->  eia_2026_bulk-coal_coke-trade-prices.csv
                              coke import and export prices, all terminals
                              (the bulk files hold no open-market coke price;
                              that stays in Quarterly Coal Report Table 25)
  eia_2026_bulk-seds.zip  ->  eia_2026_bulk-seds_prices.csv
                              every SEDS price series ($ per million Btu), by
                              state, sector and fuel, annual 1970 onward
  eia_2026_bulk-elec.zip  ->  eia_2026_bulk-elec_prices.csv
                              average cost of fossil fuels for electricity
                              generation, per physical unit and per million Btu,
                              by fuel, state and sector (petroleum coke among
                              them), and the retail electricity price by sector;
                              annual and quarterly (monthly series left out)

Values are copied as published (nominal US dollars of the period). Nothing is
deflated or converted here: the extraction layer keeps values as reported.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from pathlib import Path

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
RECORDS = REPO_ROOT / "data" / "technology_database"
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = _DOCS, _HERE


def series(zip_name):
    with zipfile.ZipFile(DOCS / zip_name) as z:
        name = z.namelist()[0]
        with z.open(name) as fh:
            for line in io.TextIOWrapper(fh, encoding="utf-8-sig"):
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if "series_id" in d:
                    yield d


def write(path, cols, rows):
    with open(HERE / path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        n = 0
        for r in rows:
            w.writerow(r)
            n += 1
    print(f"  {path}: {n} rows")


def parts(name):
    return [p.strip() for p in name.split(":")]


def coal():
    delivered, coke = [], []
    for d in series("eia_2026_bulk-coal.zip"):
        p = parts(d.get("name", ""))
        freq = {"A": "annual", "Q": "quarterly", "M": "monthly"}.get(d.get("f"), d.get("f"))
        if p[0] == "Price" and len(p) >= 4:
            for period, value in d.get("data", []):
                delivered.append([d["series_id"], p[1], p[2], freq, period, value, d.get("units", "")])
        elif p[0] in ("Export price", "Import price") and len(p) >= 5 and p[1] == "coke" \
                and p[3] == "all terminals":
            for period, value in d.get("data", []):
                coke.append([d["series_id"], p[0].split()[0].lower(), p[2], freq, period, value, d.get("units", "")])
    write("eia_2026_bulk-coal_delivered-prices.csv",
          ["series-id", "region", "sector", "frequency", "period", "value", "unit"], delivered)
    write("eia_2026_bulk-coal_coke-trade-prices.csv",
          ["series-id", "flow", "partner", "frequency", "period", "value", "unit"], coke)


def seds():
    rows = []
    for d in series("eia_2026_bulk-seds.zip"):
        if d.get("units") != "Dollars per million Btu":
            continue
        sid = d["series_id"]                       # SEDS.<MSN>.<STATE>.A
        _, msn, state, _ = (sid.split(".") + ["", "", "", ""])[:4]
        for period, value in d.get("data", []):
            rows.append([sid, msn, state, d.get("name", ""), period, value, d["units"]])
    write("eia_2026_bulk-seds_prices.csv",
          ["series-id", "msn", "state", "name", "year", "value", "unit"], rows)


ELEC_KEEP = {"ELEC.COST": "fuel cost per physical unit",
             "ELEC.COST_BTU": "fuel cost per million Btu",
             "ELEC.PRICE": "retail electricity price"}


def elec():
    """Fuel cost at power plants (per physical unit and per million Btu) and the
    retail electricity price by sector. Names read
    `<title> : <region> : <sector> : <fuel> : <frequency>` for fuel cost and
    `<title> : <region> : <sector> : <frequency>` for the retail price."""
    rows = []
    for d in series("eia_2026_bulk-elec.zip"):
        sid = d["series_id"]
        kind = ELEC_KEEP.get(sid.rsplit(".", 2)[0] if sid.count(".") >= 2 else "")
        if not kind:
            continue
        p = parts(d.get("name", ""))
        freq = {"A": "annual", "Q": "quarterly", "M": "monthly"}.get(d.get("f"), d.get("f"))
        if freq == "monthly":
            continue        # annual and quarterly only: monthly would push the file past 100 MB
        region = p[1] if len(p) > 1 else ""
        sector = p[2] if len(p) > 2 else ""
        fuel = p[3] if kind != "retail electricity price" and len(p) > 4 else ""
        for period, value in d.get("data", []):
            rows.append([sid, kind, region, sector, fuel, freq, period, value, d.get("units", "")])
    write("eia_2026_bulk-elec_prices.csv",
          ["series-id", "measure", "region", "sector", "fuel", "frequency", "period", "value", "unit"], rows)


if __name__ == "__main__":
    which = sys.argv[1:] or ["coal", "seds", "elec"]
    for w in which:
        print(w)
        {"coal": coal, "seds": seds, "elec": elec}[w]()
