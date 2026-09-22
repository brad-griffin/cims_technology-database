"""The rules the build holds the records and the facts to.

Everything here reads what is in memory after a build; nothing edits. A failure
stops the build with a non-zero exit, so `python data/harmonized/build.py` can
gate a commit.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .common import currency_year, split_list

RECORD_ID = re.compile(r"^t[pfc]-[a-z0-9_-]+-\d{4}$")


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
                fail[f"record-id not <prefix>-<source-id>-NNNN in {name}"].append(i)
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
    fail = {k: v for k, v in fail.items() if v}
    fail["_backlog"] = backlog
    return fail
