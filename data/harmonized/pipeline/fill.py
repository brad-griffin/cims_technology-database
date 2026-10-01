"""The fill step: values for empty archetype cells, graded by how they were reached
(design.md s6a, 2026-09-30).

The summaries (layer 3) hold what the examples say. This step runs after them and
only ever writes a cell that has NO sourced value, so a new source displaces a
fill on the next build without anyone touching the fill. Examples and extractions
are never changed.

Every archetype-parameter row carries a grade, best first:

  sourced    pooled from examples (reported, or derived within one source)
  identity   calculated from the archetype's own values by a definition or a
             physical relation (100 / efficiency; fuel x its emission factor)
  estimated  borrowed or scaled from other archetypes, or set by a class rule
  guess      a judgement with a stated range and rationale
             (records/fill/fill-judgement.csv)

A fill takes the worst grade among its inputs and its rule. Rules are records,
not code: records/fill/fill-rule.csv names each one, its grade, scope and
rationale, and switches it on or off. The methods below are what a rule's
`method` can name.

A filled row has n = 0 (no example stands behind it), `central-from` saying how
it was reached, `inputs` naming the cells it was computed from with their grades,
and `sources` the sources behind those inputs.
"""
from __future__ import annotations

from statistics import median

from .common import RECORDS, fnum, read, split_list
from . import convert

FILL = RECORDS / "fill"
GRADES = ["sourced", "identity", "estimated", "guess"]
STATUSES = ("active", "off")
FOSSIL = {"natural-gas", "coal", "oil", "diesel", "coke", "petroleum-coke", "lpg", "naphtha",
          "fuel-oil", "refinery-gas", "still-gas", "coke-oven-gas", "blast-furnace-gas"}


def worst(grades):
    gs = [g for g in grades if g in GRADES]
    return max(gs, key=GRADES.index) if gs else ""


def _g(x):
    return f"{x:.6g}"


def _scope(rule):
    """{key: value} from a scope cell: `product-unit=GJ; exclude-equipment=a|b`."""
    out = {}
    for part in split_list(rule.get("scope", "")):
        k, _, v = part.partition("=")
        out[k.strip()] = v.strip()
    return out


def _in_scope(rule, a, have):
    sc = _scope(rule)
    if "product-unit" in sc and a["product-unit"] != sc["product-unit"]:
        return False
    if a["equipment"] in sc.get("exclude-equipment", "").split("|"):
        return False
    if sc.get("exclude-chp") == "yes" and (
            "chp" in a["archetype"] or a["archetype"].startswith("combined-cycle")
            or any(k[0] == "efficiency-chp" for k in have)):
        return False
    for p in split_list(sc.get("require-absent", "").replace(",", ";")):
        if any(k[0] == p for k in have):
            return False
    return True


def _vals(row):
    return fnum(row.get("central")), fnum(row.get("low")), fnum(row.get("high"))


def _input(row, label):
    return f"{label} ({row.get('grade') or 'sourced'})"


# ---- methods: (rule, archetype record, {(param, target): row}, ctx) -> [fill dicts]

def m_inverse(rule, a, have, ctx):
    p, t = rule["parameter"], rule["target"]
    src = split_list(rule["inputs"])[0]
    s = have.get((src, ""))
    if not s or (p, t) in have:
        return []
    c, lo, hi = _vals(s)
    if not c:
        return []
    k = 100.0
    return [{"parameter": p, "target": t, "central": k / c,
             "low": k / hi if hi else None, "high": k / lo if lo else None,
             "inputs": [_input(s, src)], "grades": [s.get("grade", "sourced")],
             "sources": s.get("sources", ""), "external": []}]


def m_fuel_emission_factor(rule, a, have, ctx):
    p, t = rule["parameter"], rule["target"]
    if (p, t) in have:
        return []
    secs = {k[1]: v for k, v in have.items() if k[0] == "specific-energy-consumption" and k[1]}
    fos = {c: r for c, r in secs.items() if c in FOSSIL}
    if not fos or "fuel" in secs:          # an unnamed fuel: the carbon cannot be known
        return []
    c = lo = hi = 0.0
    ins, grades, srcs, ext = [], [], [], []
    for carrier, r in sorted(fos.items()):
        f = ctx["factors"].rows.get(f"cf-ef-co2-{carrier}")
        if not f:
            return []                       # a fossil carrier with no factor: incomplete
        ef, efl, efh = fnum(f["factor"]), fnum(f.get("factor-low")), fnum(f.get("factor-high"))
        v, vl, vh = _vals(r)
        if v is None:
            return []
        c += v * ef
        lo += (vl if vl is not None else v) * (efl or ef)
        hi += (vh if vh is not None else v) * (efh or ef)
        ins.append(_input(r, f"specific-energy-consumption_{carrier}"))
        grades.append(r.get("grade", "sourced"))
        srcs += split_list(r.get("sources", ""))
        ext.append(f["factor-id"])
    return [{"parameter": p, "target": t, "central": c, "low": lo, "high": hi,
             "inputs": ins + ext, "grades": grades,
             "sources": "; ".join(dict.fromkeys(srcs)), "external": ext}]


def m_sum(rule, a, have, ctx):
    p = rule["parameter"]
    parts = split_list(rule["inputs"])
    species = {k[1] for k in have if k[0] in parts and k[1]}
    out = []
    for t in sorted(species):
        if rule["target"] not in ("*", t) or (p, t) in have:
            continue
        rows = [have.get((q, t)) for q in parts]
        if not all(rows) or any(fnum(r.get("central")) is None for r in rows):
            continue
        c = sum(fnum(r["central"]) for r in rows)
        lo = sum(fnum(r.get("low")) if fnum(r.get("low")) is not None else fnum(r["central"]) for r in rows)
        hi = sum(fnum(r.get("high")) if fnum(r.get("high")) is not None else fnum(r["central"]) for r in rows)
        out.append({"parameter": p, "target": t, "central": c, "low": lo, "high": hi,
                    "inputs": [_input(r, f"{q}_{t}") for q, r in zip(parts, rows)],
                    "grades": [r.get("grade", "sourced") for r in rows],
                    "sources": "; ".join(dict.fromkeys(s for r in rows for s in split_list(r.get("sources", "")))),
                    "external": []})
    return out


def m_host_increment(rule, a, have, ctx):
    """Host plant's pooled cost + the median increment the set-aside examples give."""
    p = rule["parameter"]
    if (p, "") in have:
        return []
    hm = ctx["hosts"].get(a["archetype"])
    if not hm or hm.get("status") != "active" or not hm.get("host"):
        return []
    host = ctx["have"].get(hm["host"], {}).get((p, ""))
    if not host or fnum(host.get("central")) is None:
        return []
    by_ex = {}
    for r in ctx["increments"].get((a["archetype"], p), []):
        if r.get("unit-norm") != host.get("unit"):
            continue
        by_ex.setdefault(r["example-id"], []).append(fnum(r["value-norm"]))
    if not by_ex:
        return []
    per = sorted(median(v) for v in by_ex.values())
    inc, ilo, ihi = median(per), per[0], per[-1]
    hc, hl, hh = _vals(host)
    hl = hc if hl is None else hl
    hh = hc if hh is None else hh
    srcs = split_list(host.get("sources", "")) + sorted(
        {r["source-id"] for rs in [ctx["increments"][(a["archetype"], p)]] for r in rs})
    return [{"parameter": p, "target": "", "central": hc + inc, "low": hl + ilo, "high": hh + ihi,
             "inputs": [_input(host, f"{hm['host']} {p}"),
                        f"increment median of {len(per)} example(s): "
                        + ", ".join(sorted(by_ex))],
             "grades": [host.get("grade", "sourced")],
             "sources": "; ".join(dict.fromkeys(srcs)), "external": []}]


def _siblings(a, p, ctx, exclude=None):
    """(tier, [sibling rows]) -- the nearest archetypes with a SOURCED value of p:
    tier 1 same equipment and discriminator, tier 2 same equipment; always the
    same product unit."""
    A = ctx["arch"]
    for tier, same in ((1, ("equipment", "discriminator")), (2, ("equipment",))):
        rows = []
        for k, h in ctx["have"].items():
            if k in (a["archetype"], exclude) or k not in A:
                continue
            b = A[k]
            if b["product-unit"] != a["product-unit"] or any(b[f] != a[f] for f in same):
                continue
            r = h.get((p, ""))
            if r and r.get("grade") == "sourced" and fnum(r.get("central")) is not None:
                rows.append((k, r))
        if rows:
            return tier, rows
    return None, []


def _sibling_estimate(rows, widen, cap=None):
    cs = [fnum(r["central"]) for _, r in rows]
    c = median(cs)
    lows = [fnum(r.get("low")) for _, r in rows if fnum(r.get("low")) is not None] + cs
    highs = [fnum(r.get("high")) for _, r in rows if fnum(r.get("high")) is not None] + cs
    lo, hi = min(lows + [c * (1 - widen)]), max(highs + [c * (1 + widen)])
    if cap is not None:
        hi = min(hi, cap)
    return c, lo, hi


def m_sibling(rule, a, have, ctx):
    """The median of the nearest siblings' sourced values; the range spans theirs
    and at least +/- `widen` of the central (set from the back-test)."""
    p = rule["parameter"]
    if (p, "") in have:
        return []
    tier, rows = _siblings(a, p, ctx)
    if not rows:
        return []
    widen = fnum(rule.get("widen")) or 0.0
    c, lo, hi = _sibling_estimate(rows, widen, 100.0 if p in ("capacity-factor", "availability") else None)
    return [{"parameter": p, "target": "", "central": c, "low": lo, "high": hi,
             "inputs": [f"tier {tier}: " + ", ".join(k for k, _ in rows)],
             "grades": ["sourced"],
             "sources": "; ".join(dict.fromkeys(x for _, r in rows for x in split_list(r.get("sources", "")))),
             "external": []}]


def backtest(records, rules_, have, ctx):
    """Each sibling rule run on the cells that HAVE a sourced value, as if they had
    none: how often the sourced value falls inside the estimate's range, and how
    far the central is from it. Rows for output/fill-backtest.csv."""
    out = []
    for rule in rules_:
        if rule.get("method") != "sibling":
            continue
        p = rule["parameter"]
        widen = fnum(rule.get("widen")) or 0.0
        for a in records.archetypes:
            r = have.get(a["archetype"], {}).get((p, ""))
            if not r or r.get("grade") != "sourced" or fnum(r.get("central")) is None:
                continue
            tier, rows = _siblings(a, p, ctx)
            if not rows:
                continue
            c, lo, hi = _sibling_estimate(rows, widen, 100.0 if p in ("capacity-factor", "availability") else None)
            t = fnum(r["central"])
            out.append({"rule-id": rule["rule-id"], "archetype": a["archetype"], "parameter": p,
                        "sourced": _g(t), "estimate": _g(c), "low": _g(lo), "high": _g(hi),
                        "inside": "yes" if lo <= t <= hi else "no",
                        "ratio": _g(c / t) if t else "", "tier": tier,
                        "siblings": "; ".join(k for k, _ in rows)})
    return out


METHODS = {"sibling": m_sibling, "inverse": m_inverse, "fuel-emission-factor": m_fuel_emission_factor, "sum": m_sum,
           "host-increment": m_host_increment}


def rules():
    return read(FILL / "fill-rule.csv")


def judgements():
    return read(FILL / "fill-judgement.csv")


def check(records, fail) -> None:
    """The fill records against the vocabularies (part of the build's gate)."""
    seen = set()
    for r in rules():
        rid = r.get("rule-id", "")
        if rid in seen:
            fail["duplicate rule-id in fill-rule.csv"].append(rid)
        seen.add(rid)
        if r.get("status") not in STATUSES:
            fail["fill-rule status must be active or off"].append(rid)
        if r.get("grade") not in GRADES[1:]:
            fail["fill-rule grade must be identity, estimated or guess"].append(rid)
        if r.get("method") not in METHODS:
            fail["fill-rule names an unknown method"].append(f"{rid}: {r.get('method')}")
        if r.get("parameter") not in records.parameters:
            fail["fill-rule names an unknown parameter"].append(f"{rid}: {r.get('parameter')}")
        if not (r.get("rationale") or "").strip():
            fail["fill-rule with no rationale"].append(rid)
    for h in read(FILL / "host-archetype.csv"):
        if h.get("archetype") not in records.by_key:
            fail["host-archetype names an unknown archetype"].append(h.get("archetype", ""))
        if h.get("host") and h["host"] not in records.by_key:
            fail["host-archetype names an unknown host"].append(f"{h['archetype']}: {h['host']}")
        if h.get("status") not in ("active", "unmapped", "off"):
            fail["host-archetype status must be active, unmapped or off"].append(h.get("archetype", ""))
        if h.get("status") == "active" and not h.get("host"):
            fail["host-archetype active with no host"].append(h.get("archetype", ""))
    for j in judgements():
        k = f"{j.get('archetype')}: {j.get('parameter')}"
        if j.get("archetype") not in records.by_key:
            fail["fill-judgement names an unknown archetype"].append(k)
        if j.get("parameter") not in records.parameters:
            fail["fill-judgement names an unknown parameter"].append(k)
        if not (j.get("rationale") or "").strip() or not (j.get("author") or "").strip():
            fail["fill-judgement needs a rationale and an author"].append(k)
        c, lo, hi = fnum(j.get("central")), fnum(j.get("low")), fnum(j.get("high"))
        if c is None or lo is None or hi is None or not lo <= c <= hi:
            fail["fill-judgement needs central within a stated low-high range"].append(k)


def apply(psum, records, target_unit, facts=()) -> dict:
    """Grade the pooled rows, then add the fills. Returns counts by grade and rule."""
    for r in psum:
        r.update({"grade": "sourced", "method": "pooled", "rule-id": "", "inputs": "",
                  "rationale": ""})
    have = {}
    for r in psum:
        have.setdefault(r["archetype"], {})[(r["parameter"], r.get("target", ""))] = r
    increments = {}
    for r in facts:
        if (r.get("set-aside") == "needs-host-cost" and r.get("archetype")
                and fnum(r.get("value-norm")) is not None):
            increments.setdefault((r["archetype"], r["parameter"]), []).append(r)
    ctx = {"factors": convert.Factors(), "have": have, "increments": increments,
           "arch": records.by_key,
           "hosts": {h["archetype"]: h for h in read(FILL / "host-archetype.csv")}}
    stats = {"_backtest": backtest(records, [r for r in rules() if r.get("status") == "active"], have, ctx)}
    for rule in rules():
        if rule.get("status") != "active":
            continue
        fn = METHODS[rule["method"]]
        for a in records.archetypes:
            h = have.setdefault(a["archetype"], {})
            if not _in_scope(rule, a, h):
                continue
            for f in fn(rule, a, h, ctx):
                grade = worst([rule["grade"]] + f["grades"])
                p, t = f["parameter"], f["target"]
                pdef = records.parameters.get(p, {})
                c, lo, hi = f["central"], f.get("low"), f.get("high")
                spread = lo is not None and hi is not None and abs(hi - lo) > 1e-12 * max(1, abs(c))
                row = {"archetype": a["archetype"], "parameter": p, "target": t,
                       "unit": target_unit(p, a["product-unit"], pdef.get("unit-default", "")),
                       "central": _g(c), "low": _g(min(lo, hi)) if spread else "",
                       "high": _g(max(lo, hi)) if spread else "", "n": 0,
                       "n-external": "", "central-from": f"{grade}: {rule['formula']}",
                       "external-factors": "; ".join(f["external"]),
                       "sources": f["sources"], "examples": "",
                       "grade": grade, "method": rule["method"], "rule-id": rule["rule-id"],
                       "inputs": "; ".join(f["inputs"]), "rationale": rule["rationale"]}
                psum.append(row)
                h[(p, t)] = row
                stats[rule["rule-id"]] = stats.get(rule["rule-id"], 0) + 1
    for j in judgements():
        if (j.get("status") or "active") != "active":
            continue
        h = have.setdefault(j["archetype"], {})
        key = (j["parameter"], j.get("target", ""))
        if key in h:
            # a sourced or calculated value now exists: the guess is stale, not used
            stats["guess displaced"] = stats.get("guess displaced", 0) + 1
            continue
        row = {"archetype": j["archetype"], "parameter": j["parameter"], "target": j.get("target", ""),
               "unit": j["unit"], "central": j["central"], "low": j["low"], "high": j["high"],
               "n": 0, "n-external": "", "central-from": "guess: " + j["rationale"],
               "external-factors": "", "sources": "", "examples": "", "grade": "guess",
               "method": "judgement", "rule-id": "", "inputs": f"{j['author']} {j.get('date', '')}".strip(),
               "rationale": j["rationale"]}
        psum.append(row)
        h[key] = row
        stats["guess"] = stats.get("guess", 0) + 1
    return stats
