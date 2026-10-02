"""Currency factors: YEAR_CUR -> 2025_CAD, for every currency-year the facts use.

Method (adopted 2026-09-09 from the CIMS repository so the two agree): deflate
in the source currency with that currency's GDP deflator, then exchange at the
target year's rate.

    factor(YYYY_XXX -> 2025_CAD) = deflator[XXX][2025] / deflator[XXX][YYYY]
                                   x exchange[CAD_per_XXX][2025]

The factor is not symmetric and must not be chained or reversed: convert once,
from the currency the estimate was published in. The two reference tables are
copied verbatim from the CIMS repository (data/processed_data/deflator_exchange/);
refresh them there, not by hand. Coverage is 2000-2025 for CAD, USD, GBP, EUR,
JPY, INR, CNY and DKK; anything else is reported and left unconverted. DKK has no
Bank of Canada series: its CAD rate is the Bank of Canada EUR rate divided by the
ECB's annual-average DKK per EUR (added 2026-10-02).

The series behind the two tables are registered in the reference manifest
(data/raw-data/source-details_reference.csv), with the conversion factors' sources:
the World Bank GDP deflator (the ECB's for EUR), and exchange rates from the Bank
of Canada to 2017 and Statistics Canada from 2017. Each row of
currency-conversion.csv names the ones it rests on.
"""
from __future__ import annotations

import re

from .common import OUTPUT, REFERENCE, read, write

TARGET_YEAR, TARGET_CUR = 2025, "CAD"
TARGET = f"{TARGET_YEAR}_{TARGET_CUR}"
DEFLATOR_SOURCE = {"EUR": "ecb_2026_001"}           # every other currency: the World Bank
DEFLATOR_DEFAULT = "world-bank_2026_001"
# currencies whose CAD rate is derived through the euro from the ECB reference rates
EXCHANGE_EXTRA = {"DKK": ["ecb_2026_002"]}


def exchange_source(year: int) -> str:
    return "can-statcan_2026_001" if year >= 2017 else "bank-of-canada_2026_001"
MONEY = re.compile(r"^(\d{4})_([A-Z]{3})")


def factors(fact_rows) -> tuple[dict[str, float], list[str]]:
    deflator = {(r["Context"], int(r["Year"])): float(r["Value"])
                for r in read(REFERENCE / "reference-currency-deflator.csv")}
    exchange = {(r["Context"], int(r["Year"])): float(r["Value"])
                for r in read(REFERENCE / "reference-currency-exchange.csv")}
    used = set()
    for r in fact_rows:
        for f in ("unit", "currency"):
            m = MONEY.match((r.get(f) or "").strip())
            if m:
                used.add((int(m.group(1)), m.group(2)))
    out, rows, skipped = {}, [], []
    for year, cur in sorted(used):
        pair = f"{TARGET_CUR}_per_{cur}"
        if (cur, year) not in deflator or (cur, TARGET_YEAR) not in deflator or (
                cur != TARGET_CUR and (pair, TARGET_YEAR) not in exchange):
            skipped.append(f"{year}_{cur}")
            continue
        inflate = deflator[(cur, TARGET_YEAR)] / deflator[(cur, year)]
        fx = exchange[(pair, TARGET_YEAR)] if cur != TARGET_CUR else 1.0
        out[f"{year}_{cur}"] = inflate * fx
        rows.append({"from-currency": f"{year}_{cur}", "to-currency": TARGET,
                     "factor": f"{inflate * fx:.6f}",
                     "method": f"deflator {cur} {deflator[(cur, TARGET_YEAR)]:.6g}/"
                               f"{deflator[(cur, year)]:.6g} = {inflate:.6g}, then x {fx:.6g} "
                               f"{pair} ({TARGET_YEAR})",
                     "source-id": "; ".join([DEFLATOR_SOURCE.get(cur, DEFLATOR_DEFAULT)]
                                            + ([exchange_source(TARGET_YEAR)] if cur != TARGET_CUR else [])
                                            + EXCHANGE_EXTRA.get(cur, []))})
    write(OUTPUT / "currency-conversion.csv",
          ["from-currency", "to-currency", "factor", "method", "source-id"], rows)
    return out, skipped
