"""Dump the Bataille 2017 heavy-industry database faithfully, one row per row.

Run from the repo root:   python data/raw-data/other-reports/bataille-dump.py

Two sheets carry technology data and they are different in kind, so each gets
its own file:

  UKTM      390 technologies with UK TIMES investment costs. Quantitative but
            narrow -- 387 cost values, and state-of-development / GHG impact /
            energy impact filled on only 10 of 390 rows.
  Database  77 technologies from a literature survey. Qualitative: the impact
            and cost fields hold prose ("30% less than OPC"), and 72 rows carry
            a reference link, which is what makes this sheet worth having.

Both sheets are laid out as a report rather than a table: a bare sector name on
its own row opens a block, a row beginning "*" names the process step, and the
technology rows follow. Those band rows are forward-filled into columns here so
the output is rectangular, which is the only transformation this script makes.
Everything else is written exactly as the cell holds it.

Two traps in the layout, both of which produce plausible-looking wrong output:

  * The UKTM sheet has a SECOND, unrelated block in column Q -- a short list of
    generic efficiency options under three headings. It is not part of the
    table. Reading "the first non-empty cell" as the band label puts its heading
    "General Energy Efficiency" where the sector should be and silently relabels
    the whole Food & Drink block. Band detection therefore looks only at the
    table's own columns, and column Q is dumped separately.
  * On the Database sheet the technology name is sometimes blank and the type
    column carries the name instead. Treating "no name" as "band row" drops two
    real technologies. A band row is one where type, name AND description are
    all blank; the name falls back to the type, then to the description, and
    the fallback is recorded.
"""
from __future__ import annotations

import csv
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
XLSX = HERE / "bataille_2017_heavy-industry-database.xlsx"
STEM = "bataille_2017_heavy-industry-database"

# UKTM: headers on row 5, the unit qualifier on row 6, data from row 7.
UKTM_COLS = {
    1: "industry", 2: "technology-type", 3: "technology-name", 4: "description",
    5: "state-of-development", 6: "ghg-impact", 7: "energy-impact",
    8: "investment-cost", 9: "policy", 10: "canada-considerations",
    11: "reference-type", 12: "reference-links", 13: "uktm-code",
    14: "capacity-unit",
}
# Database: headers on row 3, a column-note row on row 4, data from row 5.
DB_COLS = {
    0: "industry", 1: "technology-type", 2: "technology-name", 3: "description",
    4: "state-of-development", 5: "ghg-impact", 6: "energy-impact", 7: "cost",
    8: "reference-type", 9: "reference-links",
}


def txt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).replace("\n", " ").strip()


def dump(ws, cols: dict[int, str], first_data_row: int, ident: tuple[int, ...]) -> list[dict]:
    """Walk a sheet, forward-filling the sector and process-step bands.

    `ident` is the columns that make a row a technology: type, name and
    description. A row with all three blank is a band row. Which kind it is
    comes from the leading "*": the sheet uses it for the process step and
    nothing else. A sector band resets the step, so a step never leaks across a
    sector boundary. Only the table's own columns are considered, so a
    neighbouring block cannot supply a band label.
    """
    last = max(cols)
    out, sector, step = [], "", ""
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i < first_data_row:
            continue
        row = tuple(row)[:last + 1]
        vals = [c for c in row if c not in (None, "")]
        if not vals:
            continue
        if not any(txt(row[c]) for c in ident if c < len(row)):
            band = txt(vals[0])
            if band.startswith("*"):
                step = band.lstrip("*").strip()
            else:
                sector, step = band, ""
            # A band row carrying numbers is a formatting accident in the
            # source -- row 25 repeats the values of row 24. Recorded, not used.
            extra = [txt(c) for c in vals[1:] if txt(c)]
            if extra:
                out.append({"row": i, "sector": sector, "process-step": step,
                            "band-row-stray-values": "; ".join(extra), "name-from": "",
                            **{v: "" for v in cols.values()}})
            continue
        d = {"row": i, "sector": sector, "process-step": step,
             "band-row-stray-values": "", "name-from": ""}
        for j, key in cols.items():
            d[key] = txt(row[j]) if j < len(row) else ""
        if not d["technology-name"]:
            for fallback in ("technology-type", "description"):
                if d[fallback]:
                    d["technology-name"] = d[fallback]
                    d["name-from"] = fallback
                    break
        out.append(d)
    return out


def dump_options(ws, col: int, first_data_row: int) -> list[dict]:
    """Dump the UKTM sheet's separate column-Q list of generic efficiency options.

    Three headings ("General Energy Efficiency", "Energy Efficient Technologies",
    "IEEA Technologies") each open a list whose first entry is the literal word
    "Option". Kept because named example measures are exactly what the efficiency
    buckets need (design doc D8), and discarded from the table above because it
    is not part of it.
    """
    out, heading = [], ""
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i < first_data_row or col >= len(row):
            continue
        v = txt(row[col])
        if not v or v == "Option":
            continue
        if v.endswith(("Efficiency", "Technologies")) and " " in v:
            heading = v
            continue
        out.append({"row": i, "heading": heading, "option": v})
    return out


def write(rows: list[dict], cols: dict[int, str], suffix: str) -> None:
    field = ["row", "sector", "process-step"] + list(cols.values()) + \
            ["name-from", "band-row-stray-values"]
    path = HERE / f"{STEM}_{suffix}.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=field)
        w.writeheader()
        w.writerows(rows)
    data = [r for r in rows if r.get(cols[max(cols)]) or r.get(cols[min(cols)])]
    print(f"  {path.name:58} {len(rows):>4} rows")
    return data


def main() -> int:
    import openpyxl
    if not XLSX.exists():
        print(f"not found: {XLSX}", file=sys.stderr)
        return 1
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

    uktm = dump(wb["UKTM"], UKTM_COLS, first_data_row=7, ident=(2, 3, 4))
    db = dump(wb["Database"], DB_COLS, first_data_row=5, ident=(1, 2, 3))
    options = dump_options(wb["UKTM"], col=16, first_data_row=7)
    wb.close()

    write(uktm, UKTM_COLS, "uktm-rows")
    write(db, DB_COLS, "database-rows")
    path = HERE / f"{STEM}_uktm-efficiency-options.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["row", "heading", "option"])
        w.writeheader(); w.writerows(options)
    print(f"  {path.name:58} {len(options):>4} rows")

    with (HERE / f"{STEM}_meta.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parameter", "value"])
        w.writerow(["licence", "CC BY-NC-ND 4.0"])
        w.writerow(["source-id", "bataille_2017_001"])
        w.writerow(["currency", "2010_GBP"])
        w.writerow(["currency-note", "UKTM investment costs are labelled "
                    "'Investment cost - 2010 (2010 prices)' in GBP millions per "
                    "capacity unit"])
        w.writerow(["contact", "Chris Bataille, per the Read Me sheet"])

    nu = sum(1 for r in uktm if r["technology-name"])
    nd = sum(1 for r in db if r["technology-name"])
    cost = sum(1 for r in uktm if r["investment-cost"])
    ref = sum(1 for r in db if r["reference-links"])
    stray = sum(1 for r in uktm + db if r["band-row-stray-values"])
    print(f"\n  UKTM     {nu} technologies, {cost} with an investment cost, "
          f"{len({r['sector'] for r in uktm if r['sector']})} sectors")
    print(f"  Database {nd} technologies, {ref} with a reference link, "
          f"{len({r['sector'] for r in db if r['sector']})} industry labels")
    fb = sum(1 for r in uktm + db if r["name-from"])
    if fb:
        print(f"  {fb} technolog(ies) had a blank name column; name taken from "
              "the type or description column and recorded in name-from")
    if stray:
        print(f"  {stray} band row(s) carried stray values; kept in "
              "band-row-stray-values, not used as data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
