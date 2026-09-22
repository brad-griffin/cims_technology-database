"""Write the `cims-services` column of sector-end-use-table.csv from the crosswalk.

Run from anywhere, after hierarchy_crosswalk.py:
    python design/build/cims_services.py

The column used to be hand-written in the CIMS model-input spelling. Since
2026-09-16 it names paths in design/cims_hierarchy.csv
(without the `<sector>.` prefix), generated from design/cims-hierarchy-crosswalk.csv
so the two cannot drift. Notation:

    {a, b}       alternatives at that position
    (part)       the CIMS service is split across several end uses
    (proposed)   a node the proposal adds; not in the hierarchy yet

End uses with no CIMS node keep a "none: ..." cell, written here.
"""
import collections
import csv
import io
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE.parent
TABLE = DESIGN / "sector-end-use-table.csv"
XWALK = DESIGN / "cims-hierarchy-crosswalk.csv"

NONE = {
    "biofuels/renewable-natural-gas":
        "none: commodity only (common-energy.renewable-natural-gas); the fuel-blend nodes blend it into supply",
    "biofuels/renewable-diesel-and-saf":
        "none: commodity only (common-energy.renewable-diesel, common-energy.saf)",
}


def compress(paths):
    """paths: list of (path, tags). Brace identical tails across sectors, then leaves."""
    by_tail = collections.OrderedDict()
    for p, tags in paths:
        head, _, tail = p.partition(".")
        by_tail.setdefault((tail, tags), []).append(head)
    step1 = []
    for (tail, tags), heads in by_tail.items():
        h = heads[0] if len(heads) == 1 else "{" + ", ".join(heads) + "}"
        step1.append((f"{h}.{tail}", tags))
    by_parent = collections.OrderedDict()
    for p, tags in step1:
        if p.startswith("{"):
            by_parent[(p, tags)] = None
            continue
        parent, _, leaf = p.rpartition(".")
        by_parent.setdefault((parent, tags), []).append(leaf)
    out = []
    for (parent, tags), leaves in by_parent.items():
        if leaves is None:
            s = parent
        elif len(leaves) == 1:
            s = f"{parent}.{leaves[0]}"
        else:
            s = f"{parent}.{{{', '.join(leaves)}}}"
        out.append(s + "".join(f" ({t})" for t in tags))
    return "; ".join(out)


def main():
    rows = list(csv.DictReader(open(XWALK, encoding="utf-8", newline="")))
    per = collections.defaultdict(list)
    for r in rows:
        if not r["end-use"]:
            continue
        path = r["branch"].split(".", 1)[1]
        tags = tuple(t for t, on in (("part", r["share"] == "part"),
                                     ("proposed", r["status"] == "proposed-new")) if on)
        for eu in r["end-use"].split("; "):
            per[eu].append((path, tags))
    table = list(csv.DictReader(open(TABLE, encoding="utf-8", newline="")))
    cols = list(table[0].keys())
    ids = {f"{t['sector']}/{t['end-use']}" for t in table}
    unknown = sorted(set(per) - ids)
    assert not unknown, f"crosswalk names end uses the table lacks: {unknown}"
    missing = []
    for t in table:
        key = f"{t['sector']}/{t['end-use']}"
        if key in per:
            t["cims-services"] = compress(per[key])
        elif key in NONE:
            t["cims-services"] = NONE[key]
        else:
            missing.append(key)
    assert not missing, f"end uses with no CIMS node and no 'none' text: {missing}"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(table)
    TABLE.write_text(buf.getvalue(), encoding="utf-8")
    print(f"cims-services written for {len(table)} end uses ({len(per)} from the crosswalk)")


if __name__ == "__main__":
    main()
