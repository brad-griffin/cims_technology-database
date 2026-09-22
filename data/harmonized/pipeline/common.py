"""Paths and CSV helpers shared by every stage."""
from __future__ import annotations

import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE.parent                          # data/harmonized
ROOT = DB.parent.parent                   # repo root
RAW = ROOT / "data" / "raw-data"
RECORDS = DB / "records"                  # hand-edited records
VOCAB = RECORDS / "vocabulary"            # controlled vocabularies
REFERENCE = RECORDS / "reference"         # conversion and ranking tables
OUTPUT = DB / "output"                    # everything the build writes
HIERARCHY = RECORDS / "cims_hierarchy.csv"

MONEY = re.compile(r"^(\d{4}_[A-Z]{3})")


def read(path: Path) -> list[dict]:
    """Rows of a CSV as dicts; an absent file is an empty table."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write(path: Path, cols: list[str], rows: list[dict], quiet: bool = False) -> None:
    """Write rows in the given column order; missing keys are blank."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c, "")) for c in cols})
    if not quiet:
        try:
            shown = path.relative_to(DB)
        except ValueError:
            shown = path
        print(f"  {str(shown):42s} {len(rows):6d} rows")


def split_list(cell: str) -> list[str]:
    """A ;-separated list cell as a list of stripped, non-empty items."""
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def fnum(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def currency_year(unit: str) -> str:
    """The currency-year a money unit is expressed in, or "" if it is not money.
    `currency` holds `2013_USD` and nothing else; what the money is per belongs
    to `unit`."""
    m = MONEY.match((unit or "").strip())
    return m.group(1) if m else ""
