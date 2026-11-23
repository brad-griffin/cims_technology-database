"""Faithful long-format dump of the UKERC Usable Energy Database technology tables.

Run from the repo root:
    python data/raw-data/other-reports/ukerc-dump.py

Writes ukerc_2013_usable-energy-database_rows.csv beside the workbook: one row
per (UKERC technology identifier, column), values exactly as the workbook holds
them.  This is the audit trail -- nothing is renamed, bucketed, converted or
dropped, so any later re-bucketing can be checked against it.  The template-
format extraction is built from this file, not from the workbook.

Each table has the same three header rows: row 2 group, row 3 column name,
row 4 unit.  Group cells are merged, so they are forward-filled across their
block.  Data starts at row 5.
"""
from __future__ import annotations

import csv
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import openpyxl  # noqa: E402

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = _DOCS, _HERE
SRC = DOCS / "ukerc_2013_usable-energy-database.xlsx"
DST = HERE / "ukerc_2013_usable-energy-database_rows.csv"
COLS = ["table", "ukerc-id", "technology-description", "baseline-applicable",
        "column-group", "column-name", "column-unit", "value"]
# identity columns repeated onto every emitted row rather than looked up later
ID_COLS = {0: "ukerc-id", 1: "technology-description", 2: "baseline-applicable"}


def clean(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return re.sub(r"\s+", " ", v).strip()
    return v


def main() -> int:
    if not SRC.exists():
        sys.exit(f"workbook not found: {SRC}")
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    tables = [s for s in wb.sheetnames if "Table" in s]
    out, per_table = [], {}

    for sheet in tables:
        ws = wb[sheet]
        rows = list(ws.iter_rows(min_row=1, max_row=4, values_only=True))
        groups = [clean(c) for c in rows[1]]
        names = [clean(c) for c in rows[2]]
        units = [clean(c) for c in rows[3]]
        width = max(len(groups), len(names), len(units))
        groups += [""] * (width - len(groups))
        names += [""] * (width - len(names))
        units += [""] * (width - len(units))
        # merged group cells only carry a value in their first column
        for j in range(1, width):
            if not groups[j]:
                groups[j] = groups[j - 1]

        n = 0
        for row in ws.iter_rows(min_row=5, values_only=True):
            if not row or not clean(row[0]):
                continue
            ident = {k: clean(row[i]) if i < len(row) else ""
                     for i, k in ID_COLS.items()}
            if not ident["ukerc-id"]:
                continue
            n += 1
            for j in range(width):
                v = clean(row[j]) if j < len(row) else ""
                if v == "" or j in ID_COLS:
                    continue
                out.append({"table": sheet, **ident, "column-group": groups[j],
                            "column-name": names[j], "column-unit": units[j],
                            "value": v})
        per_table[sheet] = n

    with DST.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader(); w.writerows(out)

    print(f"{DST.name}: {len(out)} value rows from {sum(per_table.values())} UKERC technologies")
    for k, v in per_table.items():
        print(f"  {v:4d}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
