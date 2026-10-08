"""The rules the build holds the records and the facts to.

Everything here reads what is in memory after a build; nothing edits. A failure
stops the build with a non-zero exit, so `python data/harmonized/build.py` can
gate a commit.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .common import RAW, REFERENCE, currency_year, read, split_list
from . import convert, fill

RECORD_ID = re.compile(r"^t[pfc]-[a-z0-9_-]+-(\d{4}|[wadx]\d{3})$")


def draws_on_targets(cell: str) -> list[str]:
    """The targets of a draws-on cell: `target (duty); target (duty)`, split at
    parenthesis depth zero so a duty may itself contain a semicolon."""
    parts, depth, cur = [], 0, ""
    for ch in cell or "":
        depth += ch == "("
        depth -= ch == ")"
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.split("(")[0].strip() for p in parts if p.strip()]


def run(records, hier, loader, ex_result) -> dict[str, list[str]]:
    fail = defaultdict(list, records.check(hier))
    fill.check(records, fail)
    for x in ex_result["unknown"]:
        fail["source-example row names an unknown archetype"].append(x)
    ids = {r["annotation"] for r in records.annotations}
    for r in records.annotations:
        for t in draws_on_targets(r.get("draws-on", "")):
            if t not in ids and t not in ("integral", "none"):
                fail["draws-on names an unknown annotation"].append(f"{r['annotation']}: {t}")
    backlog = Counter()
    for r in loader.facts:
        if r["parameter"] not in records.parameters:
            fail["parameter not in vocabulary/parameter.csv"].append(
                f"{r['record-id']}: {r['parameter']}")
        if (r.get("currency") or "") != currency_year(r.get("unit", "")):
            fail["currency is not the currency-year of unit"].append(r["record-id"])
        col = (records.parameters.get(r["parameter"], {}).get("basis-required") or "").strip()
        if col and (r.get("value") or r.get("value-min") or r.get("value-max")) \
                and not (r.get(col) or "").strip():
            if r.get("status") == "review":
                backlog[r.get("source-id", "")] += 1
            else:
                fail["missing a required basis and not marked for review"].append(r["record-id"])
    for name, rows in (("example-parameter", loader.facts), ("example-flow", loader.flows),
                       ("example-constraint", loader.cons)):
        ids_ = [r["record-id"] for r in rows]
        for k, n in Counter(ids_).items():
            if n > 1:
                fail[f"duplicate record-id in {name}"].append(k)
        for i in ids_:
            if not RECORD_ID.match(i):
                fail[f"record-id not <prefix>-<source-id>-NNNN (or -wNNN, -aNNN, -dNNN, -xNNN) in {name}"].append(i)
        known = set(ids_)
        for r in rows:
            for ref in split_list(r.get("derived-from", "")):
                if ref not in known:
                    fail[f"derived-from does not resolve in {name}"].append(
                        f"{r['record-id']} -> {ref}")
    for r in loader.flows:
        if r["commodity"] not in records.commodities:
            fail["flow commodity not in vocabulary/commodity.csv"].append(
                f"{r['record-id']}: {r['commodity']}")
    conversion_references(fail, records, loader)
    fail = {k: v for k, v in fail.items() if v}
    fail["_backlog"] = backlog
    return fail


def conversion_references(fail, records, loader) -> None:
    """The conversion factors, the tables that apply them, and the separate
    manifest of the reference sources behind them (design.md s5)."""
    ref = read(RAW / "source-details_reference.csv")
    main = {r["source_id"] for r in read(RAW / "source-details_sources.csv")}
    rid = [r["source_id"] for r in ref]
    for k, n in Counter(rid).items():
        if n > 1:
            fail["duplicate source_id in source-details_reference.csv"].append(k)
    if rid != sorted(rid):
        fail["source-details_reference.csv not in alphabetical order"].append("sort by source_id")
    for k in set(rid) & main:
        fail["source registered in both the reference and the main manifest"].append(k)
    F = convert.Factors()
    backed = set()
    for fid, f in F.rows.items():
        if f.get("class") not in convert.CLASSES:
            fail["conversion factor with no valid class"].append(f"{fid}: {f.get('class')}")
        sids = split_list(f.get("source-id", ""))
        if not sids:
            fail["conversion factor with no source-id"].append(fid)
        for sid in sids:
            backed.add(sid)
            if sid not in rid and sid not in main:
                fail["conversion factor source-id not registered"].append(f"{fid}: {sid}")
        dims = {(convert.atom(u) or ("",))[0] for u in (f["from-unit"], f["to-unit"])}
        if "energy" in dims and "HHV" not in (f.get("basis") or ""):
            fail["energy factor not on a higher-heating-value basis"].append(fid)
        for a in split_list(f.get("applies-to", "")):
            if a not in records.by_key:
                fail["conversion factor applies to an unknown archetype"].append(f"{fid}: {a}")
    for r in ref:
        if r["source_id"] not in backed and "currency" not in (r.get("used_for") or ""):
            fail["reference source backs no conversion factor"].append(r["source_id"])
        if (r.get("file_on_disk") or "").strip() and not (RAW.parent.parent / r["file_on_disk"]).exists():
            fail["reference file recorded but missing"].append(r["file_on_disk"])
    for r in read(REFERENCE / "example-conversion.csv"):
        for x in split_list(r.get("factor-id", "")):
            if x not in F.rows and x not in ("none", "set-aside"):
                fail["example-conversion names an unknown factor"].append(f"{r['example-id']}: {x}")
        if r["example-id"] not in loader.examples:
            fail["example-conversion names an unknown example"].append(r["example-id"])
    hvs = read(REFERENCE / "heating-value-stream.csv")
    for k, n in Counter(r["archetype"] for r in hvs).items():
        if n > 1:
            # a second row silently replaces the first when the table is loaded
            fail["duplicate archetype in heating-value-stream.csv"].append(k)
    for k, n in Counter(r["factor-id"] for r in read(REFERENCE / "conversion-factor.csv")).items():
        if n > 1:
            fail["duplicate factor-id in conversion-factor.csv"].append(k)
    for r in hvs:
        if r["archetype"] not in records.by_key:
            fail["heating-value-stream names an unknown archetype"].append(r["archetype"])
        for x in (r.get("fuel-in", ""), r.get("product-out", "")):
            if x and (x not in F.rows or F.rows[x]["from-unit"] != "GJ-LHV"):
                fail["heating-value-stream names a factor that is not an HHV/LHV ratio"].append(
                    f"{r['archetype']}: {x}")
    for r in read(REFERENCE / "efficiency-bridge.csv"):
        if r["example-id"] not in loader.examples:
            fail["efficiency-bridge names an unknown example"].append(r["example-id"])
        if r.get("bridge") not in ("yes", "no"):
            fail["efficiency-bridge: bridge must be yes or no"].append(r["example-id"])
