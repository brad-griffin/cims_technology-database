"""Whole-plant costs assembled from component costs the same source gives.

records/reference/whole-plant-assembly.csv lists each assembly: the whole-plant
archetype, the source, the parameter and unit of the sum, and its components.
A component is written `example-id | case | multiplier`:

  * example-id  an example of that source (normally mapped to a `component`
                archetype, such as anaerobic-digester or separator_biogas-upgrading);
  * case        the "[...]" label a row's note starts with, where one example
                holds several cases (size bands, feed mixes); blank if it holds one;
  * multiplier  a factor THE SAME SOURCE gives that puts the component on the
                sum's denominator (its locator goes in `factor-locator`); blank = 1.

    whole-plant cost = sum of (component value x multiplier)

written as a derived row (id tp-<source-id>-aNNN) on the whole-plant archetype,
with derived-from naming every component row. Components from another source,
a component that does not resolve to exactly one row, or a component in another
currency-year stop the build: the rule (docs/design.md section 2) is that parts
are added only within one source, never across sources.

`whole-example` attaches the row to an existing example of the whole-plant
archetype. Where that example already reports the total (`check-case` names its
row), the assembled row is a consistency check: it is marked a duplicate of the
reported row and not pooled, and the difference is reported. Otherwise a new
example `<source-id>:<archetype>@assembly-<assembly-id>` is created.
"""
from __future__ import annotations

import collections

from .common import REFERENCE, currency_year, fnum, read, split_list

FILE = REFERENCE / "whole-plant-assembly.csv"


def _pick(facts, eid, param, case):
    rows = [r for r in facts if r["example-id"] == eid and r["parameter"] == param
            and r.get("value-type") != "derived"
            and (not case or (r.get("note") or "").startswith(f"[{case}]"))]
    return rows


def derive(loader) -> dict:
    if not FILE.exists():
        return {}
    errors, stats, seq = [], collections.Counter(), collections.Counter()
    new = []
    for a in read(FILE):
        aid, arch, sid, param, unit = (a["assembly-id"], a["archetype"], a["source-id"],
                                        a["parameter"], a["unit"])
        parts = []
        for spec in split_list(a["components"]):
            eid, case, mult = ([x.strip() for x in spec.split("|")] + ["", ""])[:3]
            rows = _pick(loader.facts, eid, param, case)
            if len(rows) != 1:
                errors.append(f"{aid}: component {eid} [{case}] {param} matches {len(rows)} rows")
                continue
            r = rows[0]
            if r.get("source-id") != sid:
                errors.append(f"{aid}: component {r['record-id']} is from {r.get('source-id')}, not {sid}")
            m = fnum(mult) if mult else 1.0
            if currency_year(r.get("unit", "")) != currency_year(unit):
                errors.append(f"{aid}: {r['record-id']} is in {r.get('unit')}, the sum in {unit}")
            if m == 1.0 and r.get("unit") != unit:
                errors.append(f"{aid}: {r['record-id']} unit {r.get('unit')} differs from {unit} "
                              "and no same-source multiplier is given")
            parts.append((r, m))
        if errors and any(e.startswith(aid + ":") for e in errors):
            continue

        def total(field):
            vals = []
            for r, m in parts:
                v = fnum(r.get(field)) if fnum(r.get(field)) is not None else fnum(r.get("value"))
                if v is None:
                    return ""
                vals.append(v * m)
            return f"{sum(vals):.6g}"
        allv = all(fnum(r.get("value")) is not None for r, _ in parts)
        value = f"{sum(fnum(r['value']) * m for r, m in parts):.6g}" if allv else ""
        lo, hi = total("value-min"), total("value-max")
        if lo == value and hi == value:
            lo = hi = ""
        eid = a.get("whole-example") or ""
        ex = loader.examples.get(eid) if eid else None
        if eid and ex is None:
            errors.append(f"{aid}: whole-example {eid} is not an example")
            continue
        if ex is None:
            ex = loader.example(sid, arch, f"assembly {aid}", {}, parts[0][0].get("extraction-file", ""))
            ex.update({"archetype": arch, "mapping": "mapped", "detail": "assembled from components"})
            eid = ex["example-id"]
        elif ex.get("archetype") != arch:
            errors.append(f"{aid}: whole-example {eid} is mapped to {ex.get('archetype')!r}, not {arch}")
            continue
        seq[sid] += 1
        first = parts[0][0]
        formula = " + ".join(f"{r['record-id']}" + ("" if m == 1.0 else f" x {m:g}") for r, m in parts)
        row = dict(first, **{
            "record-id": f"tp-{sid}-a{seq[sid]:03d}", "example-id": eid, "archetype": arch,
            "source-technology": ex["source-technology"], "unit": unit, "currency": currency_year(unit),
            "value": value, "value-min": lo, "value-max": hi,
            "uncertainty-type": "reported-range" if (lo or hi) else "",
            "value-type": "derived", "formula": formula, "derived-kind": "assembly",
            "derived-from": "; ".join(r["record-id"] for r, _ in parts),
            "cost-basis": a.get("cost-basis") or first.get("cost-basis", ""),
            "source-locator": "; ".join(r.get("source-locator", "") for r, _ in parts),
            "whole-plant": "", "set-aside": "",
            "note": (f"ASSEMBLED ({aid}): the sum of this source's own component costs, "
                     f"{formula}. " + (f"Factor: {a['factor-locator']}. " if a.get("factor-locator") else "")
                     + (a.get("note") or ""))})
        if a.get("check-case"):
            rep = _pick(loader.facts, eid, param, a["check-case"])
            if len(rep) != 1:
                errors.append(f"{aid}: check-case matches {len(rep)} reported rows in {eid}")
                continue
            rep = rep[0]
            row["assembly-duplicate"] = rep["record-id"]
            diffs = []
            for fld in ("value", "value-min", "value-max"):
                x, y = fnum(row.get(fld)), fnum(rep.get(fld))
                if x is not None and y is not None and y:
                    diffs.append(abs(x - y) / abs(y))
            d = max(diffs) if diffs else None
            row["note"] = (f"CHECK: the source also prints this total ({rep['record-id']}); "
                           + ("they agree exactly. " if d == 0 else
                              f"they differ by up to {d:.1%}. " if d is not None else "")
                           + row["note"])
            stats["checks"] += 1
            stats["check mismatches"] += int(bool(d))
        else:
            stats["rows"] += 1
        new.append(row)
    if errors:
        raise SystemExit("whole-plant-assembly.csv:\n  " + "\n  ".join(errors))
    loader.facts.extend(new)
    return dict(stats)
