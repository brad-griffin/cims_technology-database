"""Extract open-market coke and breeze sales and prices from Quarterly Coal Reports.

    python data/raw-data/gov-usa/eia/prices/eia_qcr_extract.py

Reads every fourth-quarter Quarterly Coal Report saved beside this script
(eia_<published>_qcr-<year>q4.pdf) and writes

  eia_2026_qcr-coke-breeze-open-market.csv
      the "Open market sales and average price of coke and breeze" table
      (Table 25 from the 2009 report on; earlier reports have no such table),
      one row per report, commodity, measure and period column:
      the quarter, the previous quarter, the same quarter a year before, and
      the year-to-date totals for the report year and the year before (the
      fourth-quarter report's year to date is the full calendar year).
  eia_2026_qcr-coke-breeze-open-market-annual.csv
      one full-year value per year, commodity and measure, taken from the
      latest report that prints it: the next year's report restates the prior
      year, often revised (2023 coke: 256.02 first, 451.61 a year later).

Values are copied as published (nominal US dollars per short ton; sales in
thousand short tons). Withheld or blank cells are kept as printed. Needs
pdftotext (poppler).
"""
from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = _DOCS, _HERE
OUT = "eia_2026_qcr-coke-breeze-open-market.csv"
ANNUAL = "eia_2026_qcr-coke-breeze-open-market-annual.csv"
NUM = re.compile(r"^(?:-?[\d,]+(?:\.\d+)?|w|W|-|–|−|NM|\*)$")


def text(pdf):
    r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    return r.stdout.splitlines()


def table(lines):
    """Lines of the open-market table, from its heading to its note."""
    for i, line in enumerate(lines):
        low = line.lower()
        if "table" in low and "open market" in low and "coke and breeze" in low \
                and "...." not in line and ". . ." not in line:
            body = []
            for line2 in lines[i:i + 40]:
                if line2.strip().lower().startswith("note"):
                    break
                body.append(line2)
            return body
    return None


def tokens(line):
    return [t for t in line.replace("$", "").split() if NUM.match(t)]


def rows(year, body):
    """Yield (commodity, measure, values) with five period values each."""
    commodity = None
    i = 0
    while i < len(body):
        s = body[i].strip()
        # words of the row label; "verage price" is a 2009 layout break of "Average"
        words = re.sub(r"[^a-z ]", " ", s.lower()).split()
        w0 = words[0] if words else ""
        is_price = w0 in ("average", "verage") and len(words) > 1 and words[1] == "price"
        if w0 in ("coke", "breeze") and all(w == "w" for w in words[1:]):
            commodity = w0
        elif commodity and (w0 == "sales" or is_price):
            measure = "sales" if w0 == "sales" else "average-price"
            vals = tokens(re.sub(r"^(sales|a?verage price)[ .]*", "", s, flags=re.I))
            j = i
            while len(vals) < 5 and j + 1 < len(body) and j < i + 3:
                j += 1
                vals += tokens(body[j])
            yield commodity, measure, vals[:5]
            i = j
        i += 1


def periods(year):
    return [(f"{year}Q4", "quarter"), (f"{year}Q3", "quarter"), (f"{year - 1}Q4", "quarter"),
            (str(year), "year-to-date"), (str(year - 1), "year-to-date")]


def main():
    out = []
    for pdf in sorted(DOCS.glob("eia_*_qcr-*q4.pdf")):
        year = int(re.search(r"qcr-(\d{4})q4", pdf.name).group(1))
        body = table(text(pdf))
        if body is None:
            print(f"  {pdf.name}: no open-market coke table")
            continue
        n = 0
        for commodity, measure, vals in rows(year, body):
            if len(vals) < 5:
                print(f"  {pdf.name}: {commodity} {measure} gave {vals}")
            unit = "thousand short tons" if measure == "sales" else "USD per short ton"
            for (period, basis), v in zip(periods(year), vals):
                out.append([pdf.name, year, commodity, measure, period, basis, v.replace(",", ""), unit])
                n += 1
        print(f"  {pdf.name}: {n} values")
    with open(HERE / OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["report", "report-year", "commodity", "measure", "period", "basis", "value", "unit"])
        w.writerows(out)
    print(f"  {OUT}: {len(out)} rows")
    # Annual series: each year's full-year value from the latest report that
    # prints it (the next year's report carries the revised prior year).
    latest = {}
    for rep, ry, com, mea, per, basis, v, unit in out:
        if basis != "year-to-date" or not re.match(r"^-?[\d.]+$", v):
            continue
        k = (int(per), com, mea)
        if k not in latest or ry > latest[k][0]:
            latest[k] = (ry, rep, v, unit)
    with open(HERE / ANNUAL, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["year", "commodity", "measure", "value", "unit", "report"])
        for (y, com, mea), (ry, rep, v, unit) in sorted(latest.items()):
            w.writerow([y, com, mea, v, unit, rep])
    print(f"  {ANNUAL}: {len(latest)} rows")


if __name__ == "__main__":
    main()
