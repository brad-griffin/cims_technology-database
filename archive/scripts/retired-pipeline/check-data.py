"""Check the harmonized database against the rules it is supposed to satisfy.

Run from the repo root:   python data/raw-data/check-data.py

check-manifest.py checks the source manifest against the disk; this checks the
tables populate.py writes against the conventions the design document sets, so
that a hand edit or a new loader path cannot quietly break one. It reads only
what is on disk -- it never runs the pipeline -- so it can gate a commit.

  * every parameter is one parameter.csv defines;
  * a quantified row carries the basis parameter.csv says that parameter needs
    (a capex with no cost-basis could be equipment or installed, and those
    differ by about a factor of two);
  * `currency` is a currency-year and only that -- `2013_USD`, never
    `2013_USD/kW`, which is what `unit` is for;
  * record-ids are unique and shaped `<prefix>-<source-id>-NNNN`;
  * every `derived-from` resolves to a record-id in the same table;
  * the roster is the design vocabulary (since the adoption, 2026-09-22): the
    end uses are the design table's, every technology carries a design-table
    label, every service node sits on a leaf of design/cims_hierarchy.csv, and
    every application and fact points at a technology and node that exist,
    with the source's own name kept in roster-technology.

The missing-basis rule has a known backlog: extractions that predate the
basis rules carry status=review and a BASIS NOT RECORDED note until the
backfill pass, and are reported per source rather than failed. A row missing
its required basis that is NOT marked for review is a regression, and fails --
that is the condition this gate exists for.

Exit status is non-zero if anything fails, so it can gate a commit.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
HARMONIZED = ROOT / "data" / "harmonized"
DESIGN = ROOT / "design"

MONEY = re.compile(r"^(\d{4}_[A-Z]{3})")
RECORD_ID = re.compile(r"^t[pfc]-[a-z0-9_-]+-\d{4}$")


def read(p: Path) -> list[dict]:
    return list(csv.DictReader(p.open(encoding="utf-8-sig"))) if p.exists() else []


def currency_year(unit: str) -> str:
    """The same rule populate.py writes the column with."""
    m = MONEY.match((unit or "").strip())
    return m.group(1) if m else ""


def main() -> int:
    params = read(HARMONIZED / "parameter.csv")
    facts = read(HARMONIZED / "tech-parameter.csv")
    if not params or not facts:
        print(f"parameter.csv or tech-parameter.csv not found under {HARMONIZED}",
              file=sys.stderr)
        return 1
    fail = collections.defaultdict(list)
    defined = {r["parameter"] for r in params}
    basis_req = {r["parameter"]: (r.get("basis-required") or "").strip()
                 for r in params if (r.get("basis-required") or "").strip()}

    # ---- parameters are the ones the dictionary defines -------------------
    for r in facts:
        if r["parameter"] not in defined:
            fail["parameter not in parameter.csv"].append(
                f"{r['record-id']}: {r['parameter']}")

    # ---- the basis each parameter requires --------------------------------
    backlog = collections.Counter()
    for r in facts:
        col = basis_req.get(r["parameter"], "")
        # a basis says what a number is per; an unquantified row has no number
        # for it to qualify, so it is not held against this rule
        if not col or not (r.get("value") or r.get("value-min") or r.get("value-max")):
            continue
        if (r.get(col) or "").strip():
            continue
        if (r.get("status") or "") == "review":
            backlog[r.get("source-id", "")] += 1      # known, awaiting backfill
        else:
            fail["missing a required basis and not marked for review"].append(
                f"{r['record-id']}: {r['parameter']} needs {col}, "
                f"status={r.get('status', '')!r}")

    # ---- currency is a currency-year and nothing else ----------------------
    for r in facts:
        want = currency_year(r.get("unit", ""))
        if (r.get("currency") or "") != want:
            fail["currency is not the currency-year of unit"].append(
                f"{r['record-id']}: unit {r.get('unit', '')!r}, "
                f"currency {r.get('currency', '')!r}, expected {want!r}")

    # ---- record ids and the one column that points at them -----------------
    for name in ("tech-parameter.csv", "tech-flow.csv", "tech-constraint.csv"):
        rows = read(HARMONIZED / name)
        ids = [r["record-id"] for r in rows if r.get("record-id")]
        if len(ids) != len(set(ids)):
            dup = [k for k, v in collections.Counter(ids).items() if v > 1]
            fail[f"duplicate record-id in {name}"] = dup
        for r in rows:
            rid = r.get("record-id", "")
            if rid and not RECORD_ID.match(rid):
                fail[f"record-id not <prefix>-<source-id>-NNNN in {name}"].append(rid)
        known = set(ids)
        for r in rows:
            # declared as a semicolon-separated list of record-ids
            for ref in (x.strip() for x in (r.get("derived-from") or "").split(";")):
                if ref and ref not in known:
                    fail[f"derived-from does not resolve in {name}"].append(
                        f"{r.get('record-id', '')} -> {ref}")

    # ---- the design vocabulary and the hierarchy ---------------------------
    seu = read(DESIGN / "sector-end-use-table.csv")
    labels = {r["technology"] for r in read(DESIGN / "end-use-technology-table.csv")}
    hier = {r["branch"] for r in read(DESIGN / "cims_hierarchy.csv")}
    eus = read(HARMONIZED / "end-use.csv")
    techs = read(HARMONIZED / "technology.csv")
    nodes = read(HARMONIZED / "service-node.csv")
    apps = read(HARMONIZED / "technology-application.csv")
    if {r["end-use"] for r in eus} != {r["end-use"] for r in seu}:
        fail["end-use.csv is not the design table's end uses"] = sorted(
            {r["end-use"] for r in eus} ^ {r["end-use"] for r in seu})
    tnames = [r["technology"] for r in techs]
    if len(tnames) != len(set(tnames)):
        fail["duplicate technology"] = [k for k, v in collections.Counter(tnames).items() if v > 1]
    for r in techs:
        if r.get("technology-label") not in labels:
            fail["technology with no design-table label"].append(
                f"{r['technology']}: {r.get('technology-label', '')!r}")
    known_eu = {r["end-use"] for r in eus}
    for r in nodes:
        if r["branch"] not in hier:
            fail["service node not on a hierarchy leaf"].append(f"{r['service-node']}: {r['branch']}")
        if r["end-use"] not in known_eu:
            fail["service node on an unknown end use"].append(r["service-node"])
    tset, nset = set(tnames), {r["service-node"] for r in nodes}
    for r in apps:
        if r["technology"] not in tset:
            fail["application for an unknown technology"].append(r["technology"])
        if r["service-node"] not in nset:
            fail["application on an unknown service node"].append(r["service-node"])
    for name in ("tech-parameter.csv", "tech-flow.csv", "tech-constraint.csv"):
        for r in read(HARMONIZED / name):
            if r["technology"] not in tset:
                fail[f"{name} row for an unknown technology"].append(
                    f"{r['record-id']}: {r['technology']}")
            if not (r.get("roster-technology") or "").strip():
                fail[f"{name} row with no roster-technology"].append(r["record-id"])

    print(f"  {len(techs)} technologies, {len(nodes)} service nodes on hierarchy leaves, "
          f"{len(apps)} applications")
    print(f"  {len(facts)} parameter rows, {len(defined)} parameters defined, "
          f"{len(basis_req)} of them requiring a basis")
    if backlog:
        print(f"  basis backfill outstanding: {sum(backlog.values())} rows marked for "
              f"review across {len(backlog)} sources")
        for sid, k in backlog.most_common():
            print(f"      {sid or '(unattributed)'}: {k}")
    if not fail:
        print("  all checks passed")
        return 0
    for k, v in fail.items():
        print(f"\n  {k.upper()} ({len(v)}):")
        for x in v[:12]:
            print(f"      {x}")
        if len(v) > 12:
            print(f"      ... and {len(v) - 12} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())
