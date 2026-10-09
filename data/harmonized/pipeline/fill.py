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
          "fuel-oil", "heavy-fuel-oil", "refinery-gas", "still-gas", "coke-oven-gas", "blast-furnace-gas"}


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
    if sc.get("exclude-ccs") == "yes" and ("_ccs-" in a["archetype"]
                                         or a.get("family") == "co2-capture"):
        return False
    if sc.get("exclude-chp") == "yes" and (
            "chp" in a["archetype"] or a["archetype"].startswith("combined-cycle")
            or any(k[0] == "efficiency-chp" for k in have)):
        return False
    if sc.get("only-ccs-host") == "yes" and not ("_ccs-" in a["archetype"]
                                                 and a.get("family") != "co2-capture"):
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
    if "fuel" in secs:
        # `fuel` is known by fuel only where named fuels are its split (pipeline/carriers.py,
        # 2026-10-05); then the carbon comes from that split alone
        split = {c: r for c, r in secs.items() if "of fuel, split from" in (r.get("central-from") or "")}
        if not split:
            return []                       # an unnamed fuel: the carbon cannot be known
        secs = split
    fos = {c: r for c, r in secs.items() if c in FOSSIL}
    if not fos or any((fnum(r.get("central")) or 0) < 0 for r in fos.values()):
        return []   # a negative carrier is fuel saved or recovered, not burned
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


def m_host_copy(rule, a, have, ctx):
    """The host plant's cost, unchanged: a host-with-capture archetype differs from
    its host only by a service request to the capture archetype, which carries the
    capture cost (modeller 2026-10-02)."""
    p = rule["parameter"]
    if (p, "") in have:
        return []
    hm = ctx["hosts"].get(a["archetype"])
    if not hm or hm.get("status") != "active" or not hm.get("host"):
        return []
    host = ctx["have"].get(hm["host"], {}).get((p, ""))
    if not host or fnum(host.get("central")) is None:
        return []
    hc, hl, hh = _vals(host)
    return [{"parameter": p, "target": "", "central": hc,
             "low": hc if hl is None else hl, "high": hc if hh is None else hh,
             "inputs": [_input(host, f"{hm['host']} {p}")],
             "grades": [host.get("grade", "sourced")],
             "sources": host.get("sources", ""), "external": []}]


# parameters whose value does not depend on the product unit: siblings need not
# share it (modeller 2026-10-09)
UNIT_FREE = {"lifetime", "construction-time", "capacity-factor"}


def _siblings(a, p, ctx):
    """(tier, [(archetype, row)]) -- the nearest archetypes with a SOURCED value of
    p: tier 1 same equipment and discriminator, tier 2 same equipment; the same
    product unit, except for the unit-free parameters (UNIT_FREE)."""
    A = ctx["arch"]
    for tier, same in ((1, ("equipment", "discriminator")), (2, ("equipment",))):
        rows = []
        for k, h in ctx["have"].items():
            if k == a["archetype"] or k not in A:
                continue
            b = A[k]
            if ((b["product-unit"] != a["product-unit"] and p not in UNIT_FREE)
                    or any(b[f] != a[f] for f in same)):
                continue
            r = h.get((p, ""))
            if _sourced(r):
                rows.append((k, r))
        if rows:
            return tier, rows
    return None, []


def _sourced(r):
    return bool(r) and r.get("grade") == "sourced" and fnum(r.get("central")) is not None


def _quantile(xs, q):
    xs = sorted(xs)
    if len(xs) == 1:
        return xs[0]
    i = q * (len(xs) - 1)
    lo = int(i)
    return xs[lo] + (xs[min(lo + 1, len(xs) - 1)] - xs[lo]) * (i - lo)


CAP100 = ("capacity-factor", "availability")


# ---- estimators: methods that borrow from OTHER archetypes. Each returns
# {central, low, high, inputs, sources} for archetype `a` from sourced values of
# other archetypes only, so the same function back-tests a cell that has a
# sourced value (that value is never in its own pool).

def e_sibling(rule, a, ctx):
    """The median of the nearest siblings' sourced values; the range spans theirs
    and at least +/- `widen` of the central."""
    p = rule["parameter"]
    tier, rows = _siblings(a, p, ctx)
    if not rows:
        return None
    widen = fnum(rule.get("widen")) or 0.0
    cs = [fnum(r["central"]) for _, r in rows]
    c = median(cs)
    lows = [fnum(r.get("low")) for _, r in rows if fnum(r.get("low")) is not None] + cs
    highs = [fnum(r.get("high")) for _, r in rows if fnum(r.get("high")) is not None] + cs
    lo, hi = min(lows + [c * (1 - widen)]), max(highs + [c * (1 + widen)])
    if p in CAP100:
        hi = min(hi, 100.0)
    return {"central": c, "low": lo, "high": hi,
            "inputs": [f"tier {tier}: " + ", ".join(k for k, _ in rows)],
            "sources": [x for _, r in rows for x in split_list(r.get("sources", ""))]}


def e_cost_ratio(rule, a, ctx):
    """p = base parameter x the median p/base ratio of archetypes with BOTH sourced,
    from the nearest pool of at least `min-pool` (same equipment, then family,
    then all). Range: the pool's `widen` and 1-`widen` quantiles."""
    p, base = rule["parameter"], split_list(rule["inputs"])[0]
    sc = _scope(rule)
    need = int(sc.get("min-pool", "3"))
    b = ctx["have"].get(a["archetype"], {}).get((base, ""))
    if not _sourced(b):
        return None
    bc = fnum(b["central"])
    A = ctx["arch"]
    ratios = {}
    for k, h in ctx["have"].items():
        if k == a["archetype"] or k not in A:
            continue
        x, y = h.get((base, "")), h.get((p, ""))
        if _sourced(x) and _sourced(y) and fnum(x["central"]) > 0 \
                and x["unit"].split("/")[-1] == y["unit"].split("/")[-1]:
            ratios[k] = fnum(y["central"]) / fnum(x["central"])
    for level in ("equipment", "family", None):
        pool = {k: v for k, v in ratios.items() if level is None or A[k][level] == a[level]}
        if len(pool) >= need or level is None:
            break
    if not pool:
        return None
    q = fnum(rule.get("widen")) or 0.0
    vs = list(pool.values())
    m = median(vs)
    return {"central": bc * m, "low": bc * _quantile(vs, q), "high": bc * _quantile(vs, 1 - q),
            "inputs": [_input(b, base),
                       f"{p}/{base} median {m:.4g} of {len(pool)} archetypes "
                       f"({'same ' + level if level else 'all'})"],
            "sources": split_list(b.get("sources", ""))}


def e_modifier_ratio(rule, a, ctx):
    """A variant (`base_<modifier>`) = its base archetype's sourced value x the
    median variant/base ratio that single sources give where they price BOTH a
    base and its variant with the same modifier. Needs `min-pool` such pairs.
    Range: the smallest and largest of those ratios, applied to the base's range."""
    p = rule["parameter"]
    parts = a["archetype"].split("_")
    if len(parts) < 2:
        return None
    mod, base = parts[-1], "_".join(parts[:-1])
    b = ctx["have"].get(base, {}).get((p, ""))
    if not _sourced(b):
        return None
    sc = _scope(rule)
    need = int(sc.get("min-pool", "2"))
    ratios = [(r, sid, v) for (r, sid, v) in ctx["mod_ratios"].get((mod, p), [])
              if v != a["archetype"]]
    if len(ratios) < need:
        return None
    rs = [r for r, _, _ in ratios]
    m = median(rs)
    bc, bl, bh = _vals(b)
    bl = bc if bl is None else bl
    bh = bc if bh is None else bh
    return {"central": bc * m, "low": bl * min(rs), "high": bh * max(rs),
            "inputs": [_input(b, f"{base} {p}"),
                       f"_{mod}/base median {m:.4g} from {len(rs)} same-source pairs: "
                       + ", ".join(f"{v} ({sid})" for _, sid, v in ratios)],
            "sources": split_list(b.get("sources", ""))}


ESTIMATORS = {"sibling": e_sibling, "cost-ratio": e_cost_ratio, "modifier-ratio": e_modifier_ratio}


def _estimated(fn):
    def m(rule, a, have, ctx):
        p = rule["parameter"]
        if (p, "") in have:
            return []
        e = fn(rule, a, ctx)
        if not e:
            return []
        return [{"parameter": p, "target": "", "central": e["central"], "low": e["low"],
                 "high": e["high"], "inputs": e["inputs"], "grades": ["sourced"],
                 "sources": "; ".join(dict.fromkeys(e["sources"])), "external": []}]
    return m


def backtest(records, rules_, have, ctx):
    """Each borrowing rule run on the cells that HAVE a sourced value, as if they
    had none: does the sourced value fall inside the estimate's range, and how far
    is the central from it. Rows for output/fill-backtest.csv."""
    out = []
    for rule in rules_:
        fn = ESTIMATORS.get(rule.get("method"))
        if not fn:
            continue
        p = rule["parameter"]
        for a in records.archetypes:
            r = have.get(a["archetype"], {}).get((p, ""))
            if not _sourced(r) or not _in_scope(rule, a, {}):
                continue
            e = fn(rule, a, ctx)
            if not e:
                continue
            t, c, lo, hi = fnum(r["central"]), e["central"], e["low"], e["high"]
            out.append({"rule-id": rule["rule-id"], "archetype": a["archetype"], "parameter": p,
                        "sourced": _g(t), "estimate": _g(c), "low": _g(lo), "high": _g(hi),
                        "inside": "yes" if min(lo, hi) <= t <= max(lo, hi) else "no",
                        "ratio": _g(c / t) if t else "", "inputs": "; ".join(e["inputs"])})
    return out


METHODS = {"inverse": m_inverse, "fuel-emission-factor": m_fuel_emission_factor, "sum": m_sum,
           "host-increment": m_host_increment, "host-copy": m_host_copy,
           **{k: _estimated(f) for k, f in ESTIMATORS.items()}}


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
    hosts = read(FILL / "host-archetype.csv")
    seen_h = set()
    for h in hosts:
        if h.get("archetype") in seen_h:
            fail["duplicate archetype in host-archetype.csv"].append(h["archetype"])
        seen_h.add(h.get("archetype"))
    for h in hosts:
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
    # same-source variant/base ratios: (modifier, parameter) -> [(ratio, source, variant)]
    per = {}
    for r in facts:
        v = fnum(r.get("value-norm"))
        if v is None or r.get("excluded") or r.get("target-norm") or not r.get("archetype"):
            continue
        per.setdefault((r["source-id"], r["archetype"], r["parameter"], r["unit-norm"]), []).append(v)
    mod_ratios = {}
    for (sid, k, p, u), vs in per.items():
        parts = k.split("_")
        if len(parts) < 2:
            continue
        bv = per.get((sid, "_".join(parts[:-1]), p, u))
        if bv and median(bv) > 0:
            mod_ratios.setdefault((parts[-1], p), []).append((median(vs) / median(bv), sid, k))
    ctx = {"factors": convert.Factors(), "have": have, "increments": increments,
           "arch": records.by_key, "mod_ratios": mod_ratios,
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
