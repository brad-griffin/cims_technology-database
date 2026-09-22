"""Currency conversion factors for the harmonized layer.

Run from the repo root:   python data/harmonized/build-currency.py

Reads:
    reference-currency-deflator.csv   GDP deflator at market prices, per currency
    reference-currency-exchange.csv   annual average <TARGET>_per_<SOURCE> rates
Writes:
    currency-conversion.csv           YEAR_CUR -> 2025_CAD, one row per
                                      currency-year actually used in the database

METHOD, adopted 2026-09-09 from the CIMS repository so the two projects agree.
This REPLACES the earlier method (convert at the source year's FX rate, then
deflate with Canadian CPI). The two differ by about 3% on a 2000_USD value, so
factors built before this date are not comparable with factors built after it.

    factor(YYYY_XXX -> 2025_CAD)
        = deflator[XXX][2025] / deflator[XXX][YYYY]        deflate, in XXX
          x exchange[CAD_per_XXX][2025]                    then exchange, at 2025

Deflate first, within the SOURCE currency, then exchange at the TARGET year's
rate. Rebasing inside the source currency with that country's GDP deflator keeps
the estimate's real economic meaning against the price level of the output it was
measured in, and avoids mixing one country's inflation with another's. The
exchange step then moves a real value across currencies, so time effects and
space effects stay separate. The GDP deflator at market prices is the right index
for this, not CPI: these are producer capital and operating costs, not a consumer
basket.

Consequence, inherited from the method: **the factor is not symmetric and must
not be chained or reversed.** Converting 2010_USD to 2025_CAD and back does not
return the original number, because the two directions deflate in different
currencies and exchange in different years. Convert once, from the currency the
estimate was published in.

Deflator base years differ between currencies. That is deliberate and harmless:
the deflator only ever appears as a ratio of two years within one currency.

Sources
-------
Both reference tables are copied verbatim from the CIMS repository, at
``data/processed_data/deflator_exchange/``, where
``CIMS.data_processing.source.deflator_exchange`` builds them from:
  * World Bank WDI NY.GDP.DEFL.ZS, GDP deflator at market prices, for CAD, USD,
    GBP, JPY, INR and CNY.
  * ECB MNA.A.N.I10.W2.S1.S1.B.B1GQ._Z._Z._Z.IX.D.N, euro area GDP deflator, for
    EUR -- the World Bank series is per country and the euro has no one country.
  * Bank of Canada legacy monthly average noon rates (to 2017) and Statistics
    Canada / Bank of Canada monthly average rates (2017 on), averaged to annual
    over complete calendar years only.
Refresh them by rerunning that script and copying the two outputs here; do not
edit them by hand.

Coverage is 2000-2025 for CAD, USD, GBP, EUR, JPY, INR and CNY. A source year
before 2000, or a currency outside that set, cannot be converted -- the row is
reported and left out rather than approximated.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET_YEAR, TARGET_CUR = 2025, "CAD"
MONEY = re.compile(r"^(\d{4})_([A-Z]{3})")


def load(name: str) -> dict[tuple[str, int], float]:
    with (HERE / name).open(encoding="utf-8-sig", newline="") as fh:
        return {(r["Context"], int(r["Year"])): float(r["Value"])
                for r in csv.DictReader(fh)}


def used_currency_years() -> set[tuple[int, str]]:
    """Every YEAR_CUR that appears in a unit anywhere in the database.

    Discovered rather than hard-coded, so a new source's currency is converted
    without a code change -- the old build only ever emitted USD and GBP, which
    is why the ETSAP euro values had no factor.
    """
    out: set[tuple[int, str]] = set()
    for name in ("tech-parameter.csv", "tech-flow.csv"):
        path = HERE / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                for field in ("unit", "currency"):
                    m = MONEY.match((row.get(field) or "").strip())
                    if m:
                        out.add((int(m.group(1)), m.group(2)))
    return out


def main() -> None:
    deflator = load("reference-currency-deflator.csv")
    exchange = load("reference-currency-exchange.csv")

    rows, skipped = [], []
    for year, cur in sorted(used_currency_years()):
        pair = f"{TARGET_CUR}_per_{cur}"
        need = [(("deflator", cur, year), (cur, year) in deflator),
                (("deflator", cur, TARGET_YEAR), (cur, TARGET_YEAR) in deflator),
                (("exchange", pair, TARGET_YEAR), (pair, TARGET_YEAR) in exchange)]
        missing = [k for k, ok in need if not ok]
        if missing:
            skipped.append((f"{year}_{cur}", missing))
            continue
        inflate = deflator[(cur, TARGET_YEAR)] / deflator[(cur, year)]
        fx = exchange[(pair, TARGET_YEAR)] if cur != TARGET_CUR else 1.0
        factor = inflate * fx
        rows.append([
            f"{year}_{cur}", f"{TARGET_YEAR}_{TARGET_CUR}", f"{factor:.6f}",
            f"deflator {cur} {deflator[(cur, TARGET_YEAR)]:.6g}/{deflator[(cur, year)]:.6g} "
            f"= {inflate:.6g}, then x {fx:.6g} {pair} ({TARGET_YEAR})",
            "World Bank WDI / ECB GDP deflator at market prices; Bank of Canada and "
            "Statistics Canada annual average exchange rates; via the CIMS "
            "deflator_exchange tables",
            "derived"])

    with (HERE / "currency-conversion.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["from-currency", "to-currency", "factor", "method", "source", "status"])
        w.writerows(rows)

    print(f"  currency-conversion.csv      {len(rows)} factors -> "
          f"{TARGET_YEAR}_{TARGET_CUR}, method: deflate in source currency then "
          f"exchange at {TARGET_YEAR}")
    for r in rows:
        print(f"      {r[0]} -> {r[1]}  x {r[2]}")
    if skipped:
        print(f"\n  {len(skipped)} currency-year(s) have no factor and are left "
              f"unconverted rather than approximated:")
        for cy, missing in skipped:
            for kind, key, yr in missing:
                print(f"      {cy}: no {kind} for {key} in {yr}")


if __name__ == "__main__":
    main()
