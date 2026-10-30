"""Extract the Alberta ethane, methane and gas reference prices from the monthly
reference price calculation PDFs in this folder (Alberta Energy and Minerals; saved
by the modeller 2026-10-14). Writes alberta_reference-prices.csv beside them.

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

HERE = os.path.dirname(os.path.abspath(__file__))
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
    "alberta_2020-12_monthly-reference-price-calculations.pdf": {
        "ethane-reference-price": "2.41", "ethane-par-price": "2.41",
        "methane-isc-reference-price": "2.41", "gas-reference-price": "2.41"},
}
rows = []
for f in sorted(os.listdir(HERE)):
    m = re.match(r"alberta_(\d{4})-(\d{2})_monthly-reference-price-calculations\.pdf$", f)
    if not m:
        continue
    text = subprocess.run(["pdftotext", "-layout", os.path.join(HERE, f), "-"],
                          capture_output=True, text=True).stdout
    text = re.sub(r"[ \t]+", " ", text)
    if len(text.strip()) < 400:
        for series, v in READ_BY_EYE.get(f, {}).items():
            rows.append({"year": m.group(1), "month": m.group(2), "series": series, "value": v,
                         "unit": f"{m.group(1)}_CAD/GJ", "file": f + " (read from the page image)"})
        continue
    for series, pat in PATTERNS.items():
        hit = re.search(pat, text, re.I)
        if hit:
            rows.append({"year": m.group(1), "month": m.group(2), "series": series,
                         "value": hit.group(1), "unit": f"{m.group(1)}_CAD/GJ", "file": f})
with open(os.path.join(HERE, "alberta_reference-prices.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["year", "month", "series", "value", "unit", "file"])
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["year"], r["month"], r["series"], r["value"])
