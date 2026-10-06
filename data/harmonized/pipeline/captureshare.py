"""Share of a host's CO2 sent to capture (ruling 2026-10-05).

Sources print the CAPTURE PLANT's rate: 90% of the CO2 in the gas it treats.
That rate stays with the capture archetype. On a host with capture, the share
of the host's CO2 that is sent to the capture plant is

    share-to-capture = CO2 captured / (capture rate x the host's total CO2)

worked out two ways, in this order:

  1. Same example. Where an example on the host-with-capture archetype gives both
     the CO2 captured and the CO2 still emitted (same unit, both >= 0), the host's
     CO2 is their sum, so the share is captured / (rate x (captured + emitted)),
     with the example's own rate where it states one between 85% and 100%, else
     90%. The central is the median over such examples. Both numbers then sit on
     one scope, including the extra fuel the capture plant needs.
  2. Base archetype. Otherwise the host's CO2 is its base archetype's pooled
     total (records/fill/host-archetype.csv, emissions-total co2, same unit):
     captured / (rate x base total), the rate being the pooled share on the host
     if it lies between 85% and 100%, else 90%.

A share up to 110% is read as rounding of the rate and set to 100%. Above 110%
the two inputs are on different scopes (a host total net of exports, a
different product basis), so nothing is derived; the pooled value stays and
`central-from` says why. Example: blast furnace with end-of-pipe capture on the
hot-stove flue gas, 0.376 / (0.9 x 1.10) = 38% sent to capture; 34% of the
furnace's CO2 is captured.

The pooled share-to-capture is replaced by the derivation where one can be made
(the sources' 90% is a capture-plant rate, not a share), and the row says how it
was made in `central-from`. Hosts without the inputs keep the pooled value.
"""
from __future__ import annotations

from collections import defaultdict
from statistics import median

from .common import REFERENCE, fnum, read

DEFAULT_RATE = 0.90


MAX_OVER = 1.10


def _same_example(facts, a):
    """[(share, example-id, how)] from examples giving captured and emitted CO2."""
    by = defaultdict(lambda: defaultdict(list))
    for r in facts or ():
        if (r.get("archetype") == a and not r.get("excluded") and r.get("value-norm")
                and r["parameter"] in ("emissions-captured", "emissions-total", "share-to-capture")
                and (r.get("target-norm") or r.get("target") or "").strip() in ("co2", "")):
            by[r["example-id"]][r["parameter"]].append(r)
    out = []
    for eid, d in by.items():
        if "emissions-captured" not in d or "emissions-total" not in d:
            continue
        c, e = d["emissions-captured"][0], d["emissions-total"][0]
        if c["unit-norm"] != e["unit-norm"]:
            continue
        cv, ev = fnum(c["value-norm"]), fnum(e["value-norm"])
        if cv is None or ev is None or cv <= 0 or ev < 0:
            continue
        own = fnum(d["share-to-capture"][0]["value-norm"]) if "share-to-capture" in d else None
        rate = own / 100 if own and 85 <= own <= 100 else DEFAULT_RATE
        sh = cv / (rate * (cv + ev))
        if sh > MAX_OVER:
            continue
        out.append((min(1.0, sh), eid, f"{cv:.3g} / ({rate:.0%} x ({cv:.3g} + {ev:.3g}))"))
    return out


def apply(summaries, records, facts=None) -> dict:
    hosts = {r["archetype"]: r["host"] for r in read(REFERENCE.parent / "fill" / "host-archetype.csv")
             if (r.get("status") or "active") == "active"}
    idx = {(s["archetype"], s["parameter"], (s.get("target") or "").strip()): s for s in summaries}
    stats = defaultdict(int)
    for a in records.by_key:
        rec = records.by_key[a]
        if "_ccs-" not in a or rec.get("family") == "co2-capture":
            continue
        sh = idx.get((a, "share-to-capture", "co2"))
        pooled = fnum(sh["central"]) if sh and sh.get("central") else None
        base = hosts.get(a)
        same = _same_example(facts, a)
        if same:
            vals = sorted(x[0] for x in same)
            share = median(vals)
            how = (f"derived from {len(same)} example(s) giving CO2 captured and CO2 emitted: "
                   "captured / (capture rate x (captured + emitted)); "
                   + "; ".join(f"{x[2]} = {x[0]:.0%}" for x in sorted(same)[:4])
                   + (f"; median {share:.0%}" if len(same) > 1 else ""))
            lo, hi = (f"{vals[0] * 100:.4g}", f"{vals[-1] * 100:.4g}") if len(vals) > 1 else ("", "")
            ext = "assume:capture-rate"
            stats["shares from the same example"] += 1
        else:
            cap = idx.get((a, "emissions-captured", "co2"))
            tot = idx.get((base, "emissions-total", "co2")) if base else None
            if not cap or not tot or not cap.get("central") or not tot.get("central"):
                continue
            if cap["unit"] != tot["unit"]:
                stats["unit mismatch"] += 1
                continue
            c, t = fnum(cap["central"]), fnum(tot["central"])
            if not c or not t or t <= 0:
                continue
            rate = pooled / 100 if pooled and 85 <= pooled <= 100 else DEFAULT_RATE
            raw = c / (rate * t)
            if raw > MAX_OVER:
                if sh is not None:
                    sh["central-from"] = (sh.get("central-from") or "") + (
                        f"; not derived: CO2 captured {c:.3g} / (capture rate {rate:.0%} x {base} total "
                        f"CO2 {t:.3g}) = {raw:.0%}, so the two are on different scopes")
                stats["not derived (over 110%)"] += 1
                continue
            share = min(1.0, raw)
            how = (f"derived: CO2 captured {c:.3g} / (capture rate {rate:.0%} x {base} total CO2 "
                   f"{t:.3g}) = {raw:.0%}" + (", set to 100%" if raw > 1 else ""))
            lo, hi, ext = "", "", f"base:{base}; assume:capture-rate"
            stats["shares from the base archetype"] += 1
        if pooled is not None:
            how += f"; replaces the pooled {pooled:.0f}%, a capture-plant rate"
        if sh is None:
            src = idx.get((a, "emissions-captured", "co2")) or {}
            sh = dict(src, **{"archetype": a, "parameter": "share-to-capture", "target": "co2",
                              "unit": "%", "n": 0, "n-external": 0})
            summaries.append(sh)
            idx[(a, "share-to-capture", "co2")] = sh
            stats["shares added"] += 1
        sh.update({"central": f"{share * 100:.4g}", "low": lo, "high": hi, "central-from": how,
                   "external-factors": "; ".join(x for x in (sh.get("external-factors"), ext) if x)})
    return dict(stats)
