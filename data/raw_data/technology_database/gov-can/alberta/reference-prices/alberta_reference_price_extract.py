"""Extract the Alberta ethane, methane and gas reference prices from the monthly
reference price calculation PDFs in this folder (Alberta Energy and Minerals; saved
by the modeller 2026-10-14). Writes alberta_2026_reference-prices.csv beside them.

Each PDF is one month. The ethane reference price is a royalty valuation in
CAD per GJ, nominal; the ethane ISC price is calculated like the gas reference
price (Alberta market gas price less the intra-Alberta transportation deduction,
times the pipeline fuel/loss factor).
Run: python alberta_reference_price_extract.py (needs pdftotext).
"""
import csv
import os
import re
import subprocess

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
RECORDS = REPO_ROOT / "data" / "technology_database"
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = str(_DOCS), str(_HERE)
NUM = r"\$?\s*([\d.]+)\s*\$?\s*(?:/\s*GJ|/Gigajoule)?"
PATTERNS = {
    # 2005 on: "Ethane Reference Price $2.71 /GJ" or "11.01 $/GJ"; 2000: "Ethane
    # Reference Price 8.28 Ethane Par Price 5.79" ($/GJ stated in the paragraph above)
    "ethane-reference-price": r"Ethane Reference Price\s+" + NUM,
    "ethane-par-price": r"Ethane Par Price\s+" + NUM,
    "methane-isc-reference-price": r"Methane ISC Reference Price\s+" + NUM,
    "gas-reference-price": r"(?:^|\n)\s*(?:Natural )?Gas Reference Price(?:[^\n]*?is)?\s+" + NUM,
}
# pages with no text layer, read from the page image (modeller 2026-10-14)
READ_BY_EYE = {
    "alberta_2020_monthly-reference-price-calculations-december.pdf": {
        "ethane-reference-price": "2.41", "ethane-par-price": "2.41",
        "methane-isc-reference-price": "2.41", "gas-reference-price": "2.41"},
}
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]
rows = []
for f in sorted(os.listdir(DOCS)):
    m = re.match(r"alberta_(\d{4})_monthly-reference-price-calculations-([a-z]+)\.pdf$", f)
    if not m or m.group(2) not in MONTHS:
        continue
    month = f"{MONTHS.index(m.group(2)) + 1:02d}"
    text = subprocess.run(["pdftotext", "-layout", os.path.join(DOCS, f), "-"],
                          capture_output=True, text=True).stdout
    text = re.sub(r"[ \t]+", " ", text)
    if len(text.strip()) < 400:
        for series, v in READ_BY_EYE.get(f, {}).items():
            rows.append({"year": m.group(1), "month": month, "series": series, "value": v,
                         "unit": f"{m.group(1)}_CAD/GJ", "file": f + " (read from the page image)"})
        continue
    for series, pat in PATTERNS.items():
        hit = re.search(pat, text, re.I)
        if hit:
            rows.append({"year": m.group(1), "month": month, "series": series,
                         "value": hit.group(1), "unit": f"{m.group(1)}_CAD/GJ", "file": f})
with open(os.path.join(HERE, "alberta_2026_reference-prices.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=["year", "month", "series", "value", "unit", "file"])
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["year"], r["month"], r["series"], r["value"])
