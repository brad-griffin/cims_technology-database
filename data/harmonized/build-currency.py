"""Reference rates, and the currency factors derived from them.

Run from the repo root:   python data/harmonized/build-currency.py

Writes:
    reference-exchange-rate.csv   Bank of Canada annual average rates to CAD
    reference-cpi.csv             Statistics Canada CPI, monthly and annual average
    currency-conversion.csv       YEAR_CUR -> 2025_CAD, derived from the two above

Method, agreed 2026-08-27: convert at the SOURCE YEAR's annual average rate,
then deflate in Canadian dollars.

    factor(YYYY_XXX -> 2025_CAD) = fx(XXX->CAD, YYYY) x CPI(2025) / CPI(YYYY)

Converting first and deflating second keeps one price index in play instead of
two, which is why only Canadian CPI is needed. Doing it the other way -- deflate
in the source currency, then convert at today's rate -- needs a US and a UK
deflator as well, and embeds whatever real exchange-rate drift happened in
between.

Sources, retrieved 2026-08-28:
  * Exchange rates, Bank of Canada Valet.
    2000-2016: IEXA0101 (US dollar, noon) and IEXA1201 (UK pound sterling),
    the legacy annual averages, retired after 2017.
    2017-2025: FXAUSDCAD and FXAGBPCAD, the current annual averages.
    The two series join cleanly: 2016 USD 1.3248 -> 2017 USD 1.2986.
  * CPI, Bank of Canada Valet STATIC_INFLATIONCALC, which republishes the
    Statistics Canada all-items Consumer Price Index for Canada, 2002=100
    (StatCan table 18-10-0005-01). Monthly; annual averages computed here.

Both were transcribed through a fetch tool rather than downloaded, so two
checks were run before use: the 2002 monthly CPI values average to 99.99,
which the 2002=100 base requires, and an independent second fetch of 2021-2025
returned identical values. The exchange rates were pulled one series at a time
after a multi-series request returned the pound's column under the dollar's
heading.

2026 is deliberately excluded: its year is incomplete.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET_YEAR, TARGET_CUR = 2025, "CAD"

# Bank of Canada annual average, units of CAD per unit of foreign currency
FX = {
    "USD": {2000: 1.48520240, 2001: 1.54841633, 2002: 1.57035976, 2003: 1.40146175,
            2004: 1.30152024, 2005: 1.21163240, 2006: 1.13409360, 2007: 1.07478127,
            2008: 1.06601429, 2009: 1.14197729, 2010: 1.02993904, 2011: 0.98906920,
            2012: 0.99958008, 2013: 1.02991480, 2014: 1.10446640, 2015: 1.27871080,
            2016: 1.32480640, 2017: 1.2986, 2018: 1.2957, 2019: 1.3269, 2020: 1.3415,
            2021: 1.2535, 2022: 1.3013, 2023: 1.3497, 2024: 1.3698, 2025: 1.3978},
    "GBP": {2000: 2.24987680, 2001: 2.22975618, 2002: 2.35817530, 2003: 2.28829960,
            2004: 2.38418532, 2005: 2.20669880, 2006: 2.08858760, 2007: 2.14865378,
            2008: 1.96166905, 2009: 1.78035578, 2010: 1.59177012, 2011: 1.58607000,
            2012: 1.58399402, 2013: 1.61126560, 2014: 1.81903120, 2015: 1.95398400,
            2016: 1.79621160, 2017: 1.6720, 2018: 1.7299, 2019: 1.6945, 2020: 1.7199,
            2021: 1.7246, 2022: 1.6076, 2023: 1.6784, 2024: 1.7504, 2025: 1.8420},
    "CAD": {y: 1.0 for y in range(2000, 2026)},
}
FX_SERIES = {("USD", True): "IEXA0101", ("USD", False): "FXAUSDCAD",
             ("GBP", True): "IEXA1201", ("GBP", False): "FXAGBPCAD",
             ("CAD", True): "n/a", ("CAD", False): "n/a"}

# Statistics Canada all-items CPI, Canada, 2002=100, monthly (Jan..Dec)
CPI_MONTHLY = {
 2000: [93.5, 94.1, 94.8, 94.5, 94.9, 95.5, 95.8, 95.7, 96.1, 96.3, 96.6, 96.7],
 2001: [96.3, 96.8, 97.1, 97.8, 98.6, 98.7, 98.4, 98.4, 98.6, 98.1, 97.2, 97.4],
 2002: [97.6, 98.2, 98.9, 99.5, 99.7, 99.9, 100.5, 100.9, 100.9, 101.2, 101.5, 101.1],
 2003: [102.0, 102.8, 103.1, 102.4, 102.5, 102.5, 102.6, 102.9, 103.1, 102.8, 103.1, 103.2],
 2004: [103.3, 103.5, 103.9, 104.1, 105.0, 105.1, 105.0, 104.8, 105.0, 105.2, 105.6, 105.4],
 2005: [105.3, 105.7, 106.3, 106.6, 106.7, 106.9, 107.1, 107.5, 108.4, 107.9, 107.7, 107.6],
 2006: [108.2, 108.0, 108.6, 109.2, 109.7, 109.5, 109.6, 109.8, 109.2, 109.0, 109.2, 109.4],
 2007: [109.4, 110.2, 111.1, 111.6, 112.1, 111.9, 112.0, 111.7, 111.9, 111.6, 111.9, 112.0],
 2008: [111.8, 112.2, 112.6, 113.5, 114.6, 115.4, 115.8, 115.6, 115.7, 114.5, 114.1, 113.3],
 2009: [113.0, 113.8, 114.0, 113.9, 114.7, 115.1, 114.7, 114.7, 114.7, 114.6, 115.2, 114.8],
 2010: [115.1, 115.6, 115.6, 116.0, 116.3, 116.2, 116.8, 116.7, 116.9, 117.4, 117.5, 117.5],
 2011: [117.8, 118.1, 119.4, 119.8, 120.6, 119.8, 120.0, 120.3, 120.6, 120.8, 120.9, 120.2],
 2012: [120.7, 121.2, 121.7, 122.2, 122.1, 121.6, 121.5, 121.8, 122.0, 122.2, 121.9, 121.2],
 2013: [121.3, 122.7, 122.9, 122.7, 123.0, 123.0, 123.1, 123.1, 123.3, 123.0, 123.0, 122.7],
 2014: [123.1, 124.1, 124.8, 125.2, 125.8, 125.9, 125.7, 125.7, 125.8, 125.9, 125.4, 124.5],
 2015: [124.3, 125.4, 126.3, 126.2, 126.9, 127.2, 127.3, 127.3, 127.1, 127.2, 127.1, 126.5],
 2016: [126.8, 127.1, 127.9, 128.3, 128.8, 129.1, 128.9, 128.7, 128.8, 129.1, 128.6, 128.4],
 2017: [129.5, 129.7, 129.9, 130.4, 130.5, 130.4, 130.4, 130.5, 130.8, 130.9, 131.3, 130.8],
 2018: [131.7, 132.5, 132.9, 133.3, 133.4, 133.6, 134.3, 134.2, 133.7, 134.1, 133.5, 133.4],
 2019: [133.6, 134.5, 135.4, 136.0, 136.6, 136.3, 137.0, 136.8, 136.2, 136.6, 136.4, 136.4],
 2020: [136.8, 137.4, 136.6, 135.7, 136.1, 137.2, 137.2, 137.0, 136.9, 137.5, 137.7, 137.4],
 2021: [138.2, 138.9, 139.6, 140.3, 141.0, 141.4, 142.3, 142.6, 142.9, 143.9, 144.2, 144.0],
 2022: [145.3, 146.8, 148.9, 149.8, 151.9, 152.9, 153.1, 152.6, 152.7, 153.8, 154.0, 153.1],
 2023: [153.9, 154.5, 155.3, 156.4, 157.0, 157.2, 158.1, 158.7, 158.5, 158.6, 158.8, 158.3],
 2024: [158.3, 158.8, 159.8, 160.6, 161.5, 161.4, 162.1, 161.8, 161.1, 161.8, 161.8, 161.2],
 2025: [161.3, 163.0, 163.5, 163.4, 164.3, 164.4, 164.9, 164.8, 164.9, 165.3, 165.4, 165.0],
}


def main() -> int:
    cpi = {y: sum(v) / len(v) for y, v in CPI_MONTHLY.items()}
    base = cpi[2002]
    if abs(base - 100.0) > 0.05:
        sys.exit(f"CPI base check failed: 2002 averages to {base:.2f}, expected 100.00")
    print(f"CPI base check: 2002 annual average = {base:.2f} (2002=100) OK")

    with (HERE / "reference-exchange-rate.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "currency", "cad-per-unit", "series", "source"])
        for cur in ("USD", "GBP"):
            for y in sorted(FX[cur]):
                w.writerow([y, cur, f"{FX[cur][y]:.8g}", FX_SERIES[(cur, y <= 2016)],
                            "Bank of Canada Valet, annual average"])
    print(f"  reference-exchange-rate.csv  {2 * len(FX['USD'])} rows, 2000-2025, USD and GBP")

    with (HERE / "reference-cpi.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "month", "cpi", "basis", "source"])
        for y in sorted(CPI_MONTHLY):
            for m, v in enumerate(CPI_MONTHLY[y], start=1):
                w.writerow([y, m, v, "2002=100",
                            "Statistics Canada all-items CPI, Canada, via Bank of Canada Valet"])
            w.writerow([y, "annual", f"{cpi[y]:.4f}", "2002=100",
                        "annual average of the twelve monthly values above"])
    print(f"  reference-cpi.csv            {len(CPI_MONTHLY) * 13} rows, 2000-2025 monthly plus annual")

    rows = []
    for cur in ("USD", "GBP", "CAD"):
        for y in sorted(FX[cur]):
            if y not in cpi:
                continue
            factor = FX[cur][y] * cpi[TARGET_YEAR] / cpi[y]
            rows.append([f"{y}_{cur}", f"{TARGET_YEAR}_{TARGET_CUR}", f"{factor:.6f}",
                         f"{FX[cur][y]:.6g} CAD/{cur} ({y}) x CPI {cpi[TARGET_YEAR]:.2f}"
                         f"/{cpi[y]:.2f}",
                         "Bank of Canada annual average FX; Statistics Canada CPI",
                         "derived"])
    with (HERE / "currency-conversion.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["from-currency", "to-currency", "factor", "method", "source", "status"])
        w.writerows(rows)
    print(f"  currency-conversion.csv      {len(rows)} factors -> {TARGET_YEAR}_{TARGET_CUR}")
    for k in ("2007_USD", "2013_USD", "2014_USD", "2018_USD", "2013_GBP"):
        f = next(r[2] for r in rows if r[0] == k)
        print(f"      {k} -> 2025_CAD  x {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
