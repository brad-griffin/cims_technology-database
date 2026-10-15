"""One consistent energy split per archetype (rulings 2026-10-05).

Each carrier of specific-energy-consumption (natural-gas, electricity, steam, ...)
was pooled as its own population, so the carrier medians of an archetype could sum
to 1.5-3x its pooled total, or the total could fall below one carrier. Now the
split has two levels:

  total                       the row with no target: its pooled central, the
                              median of the examples that give one
    electricity, steam, ...   the carriers with no heating value
    fuel                      every combustible carrier together
      natural-gas, coal, ...  the named fuels: a split of `fuel`

  * Level 1. The carriers come from ONE example -- the split example -- as
    SHARES of that example's level-1 sum, each share times the pooled total, so
    they sum to the total. An example's `fuel` is its own `fuel` row, or the sum
    of the named fuels it gives. Low and high are the same shares of the
    total's low and high.
  * Level 2. The named fuels come from one example -- the fuel-split example --
    as shares of that example's named-fuel sum, each share times `fuel`, so they
    sum to `fuel`. A `fuel` row is written wherever the archetype has named
    fuels, even if no source gives one.
  * An archetype with carriers but no total gets a total: the split example's
    level-1 sum.
  * A carrier or fuel the chosen example does not name keeps its pooled value,
    flagged in `central-from` as pooled apart (it is not part of the split).
  * Where the split example's level-1 sum and the pooled total disagree by more
    than a factor of two, one of them is on another scope (a bucket or route
    total, say): the level-1 carriers are left as the split example states them,
    unscaled, and the total and the carriers say so. The fuel split is still
    applied to whatever `fuel` then is.
  * A row dropped only as a repeat of another example's figure (duplicate-of)
    still counts in its own example's split, so that example's balance is whole.
  * `n` is left as the number of examples that gave the carrier (modeller
    2026-10-05), even where the central comes from the split.

The split example is chosen among the examples that name at least one level-1
carrier: first one covering at least half the pooled total, then one that states
its own total and whose carriers add up to it within 25% (added 2026-10-13), then one naming two
or more level-1 carriers (an energy balance rather than one line), then the one
whose level-1 sum is closest to the pooled total, then the highest-ranked source
(source-priority.csv), then the example id. The fuel-split example is chosen
among the examples that name at least one fuel: first two or more named fuels,
then the one whose named-fuel sum is closest to `fuel`, then rank, then id.

Targets that are not carriers: component, total, not-stated.
"""
from __future__ import annotations

from collections import defaultdict
from math import log
from statistics import median

from .common import fnum

SEC = "specific-energy-consumption"
NOT_CARRIER = {"", "component", "total", "not-stated"}
FUEL_AGG = "fuel"
NO_HV_CARRIERS = {"electricity", "heat", "steam", "cooling", "hot-water", "waste-heat", "solar",
                  "geothermal", "nuclear", "hydrogen-as-feed"}


def _target(r):
    t = (r.get("target-norm") if r.get("target-norm") is not None else r.get("target")) or ""
    return t.strip().lower()


def _example_carriers(rows):
    """(own total, level-1 carriers, named fuels) for one example's pooled SEC
    rows: the median of its rows per target (as-reported rows preferred to
    derived, as in summarise). Level 1 has `fuel` = the example's own fuel row,
    else the sum of its named fuels."""
    by_t = defaultdict(list)
    for r in rows:
        by_t[_target(r)].append(r)
    out = {}
    for t, rs in by_t.items():
        rep = [r for r in rs if r.get("value-type") != "derived"] or rs
        vals = [fnum(r["value-norm"]) for r in rep if fnum(r.get("value-norm")) is not None]
        if vals:
            out[t] = median(vals)
    carriers = {t: v for t, v in out.items() if t not in NOT_CARRIER}
    named = {t: v for t, v in carriers.items() if t not in NO_HV_CARRIERS and t != FUEL_AGG}
    top = {t: v for t, v in carriers.items() if t in NO_HV_CARRIERS}
    if FUEL_AGG in carriers:
        top[FUEL_AGG] = carriers[FUEL_AGG]
    elif named:
        top[FUEL_AGG] = sum(named.values())
    return out.get(""), top, named


def _ok(d):
    return d and all(v is not None and v >= 0 for v in d.values()) and sum(d.values()) > 0


def _short(records, rs):
    return ", ".join(dict.fromkeys(records.short(r.get("source-id", "")) for r in rs))


def _sources(rs):
    return "; ".join(dict.fromkeys(r.get("source-id", "") for r in rs))


def apply(summaries, facts, records) -> dict:
    pooled = defaultdict(lambda: defaultdict(list))
    for r in facts:
        # a row dropped only as a repeat of another example's figure still belongs to
        # this example's energy balance (it is pooled once, but split here in full)
        live = not r.get("excluded") or (r.get("duplicate-of") and r["excluded"].startswith("repeat:"))
        if r["parameter"] == SEC and r.get("value-norm") and live and r.get("archetype"):
            pooled[(r["archetype"], r["unit-norm"])][r["example-id"]].append(r)
    by_arch = defaultdict(list)
    for s in summaries:
        if s["parameter"] == SEC:
            by_arch[(s["archetype"], s["unit"])].append(s)
    stats = defaultdict(int)
    for key, rows in by_arch.items():
        total = next((s for s in rows if not (s.get("target") or "").strip()), None)
        tot = fnum(total["central"]) if total else None
        exs = []
        for eid, rs in pooled.get(key, {}).items():
            own, top, named = _example_carriers(rs)
            rank = min(records.rank(r.get("via-source-id") or r.get("source-id", "")) for r in rs)
            exs.append({"eid": eid, "rs": rs, "top": top, "named": named, "rank": rank, "own": own})
        # ---- level 1 -------------------------------------------------------
        cands = []
        for e in exs:
            if not _ok(e["top"]):
                continue
            csum = sum(e["top"].values())
            covers = (csum >= 0.5 * tot) if tot and tot > 0 else True
            closeness = abs(log(csum / tot)) if tot and tot > 0 else 0.0
            # an example that states its own total and whose carriers add up to it
            # is a whole energy balance, not one line of a table: preferred first
            # (sanity-check 2026-10-11, S117: a lone "other fuel" line had become
            # the smelting-reduction vessel's whole fuel)
            balanced = bool(e["own"] and e["own"] > 0 and 0.8 <= csum / e["own"] <= 1.25)
            cands.append(((not covers, not balanced, len(e["top"]) < 2, closeness, e["rank"], e["eid"]),
                          e, csum))
        if not cands:
            continue
        _, sp, csum = min(cands, key=lambda c: c[0])
        short = _short(records, sp["rs"])
        if tot is None and total is not None:
            # a total the sources give only as a range (sanity-check 2026-10-11,
            # S106): the carrier sum becomes its central where it falls inside the
            # band; otherwise the band stands (the fill takes its midpoint) and the
            # carriers are tested against that midpoint. Never a second total row.
            lo_, hi_ = fnum(total.get("low")), fnum(total.get("high"))
            if lo_ is not None and hi_ is not None and not (lo_ <= csum <= hi_):
                tot = (lo_ + hi_) / 2
                total["central-from"] = (total.get("central-from") or "range only") + (
                    f"; the carrier sum of {short} ({sp['eid']}), {csum:.3g}, falls outside "
                    "the band, so it does not set the central")
                stats["range-only totals kept as ranges"] += 1
            else:
                total["central"] = f"{csum:.6g}"
                total["central-from"] = (f"sum of the carriers of {short} ({sp['eid']}); "
                                         "band from the range-only examples")
                total["sources"] = "; ".join(dict.fromkeys(
                    [x for x in (total.get("sources") or "").split("; ") if x]
                    + _sources(sp["rs"]).split("; ")))
                if sp["eid"] not in (total.get("examples") or ""):
                    total["examples"] = "; ".join(sorted(
                        [x for x in (total.get("examples") or "").split("; ") if x] + [sp["eid"]]))
                    total["n"] = int(total.get("n") or 0) + 1
                tot = csum
                stats["range-only totals given the carrier sum"] += 1
        elif tot is None and (records.by_key.get(key[0]) or {}).get("family") == "lighting" \
                and len({t for e in exs for t in e["top"]}) == 1 and \
                (one := next(iter({t for e in exs for t in e["top"]}))) in \
                {(s.get("target") or "").strip().lower() for s in rows} and \
                fnum(next(s for s in rows if (s.get("target") or "").strip().lower() == one)
                     .get("central")) not in (None, 0):
            # a lighting archetype whose examples all name the same ONE carrier
            # (electricity): the total is that carrier's pooled median, not one
            # example's line (2026-10-14, lighting restructure; scoped to lighting
            # until the modeller rules on other single-carrier archetypes)
            src = next(s for s in rows if (s.get("target") or "").strip().lower() == one)
            total = dict(src, **{"target": "", "central-from":
                                 f"the pooled {one}, the only carrier any example names"})
            summaries.append(total)
            rows.append(total)
            tot = fnum(total["central"])
            stats["totals from a single pooled carrier"] += 1
        elif tot is None:
            total = dict(rows[0], **{"target": "", "central": f"{csum:.6g}", "low": "", "high": "",
                                     "n": 1, "n-external": 0, "external-factors": "",
                                     "central-from": f"sum of the carriers of {short} ({sp['eid']})",
                                     "sources": _sources(sp["rs"]), "examples": sp["eid"]})
            summaries.append(total)
            rows.append(total)
            tot = csum
            stats["totals derived from carriers"] += 1
        else:
            stats["totals kept (pooled)"] += 1
        tlo, thi = fnum(total.get("low")), fnum(total.get("high"))
        agree = tot > 0 and 0.5 <= csum / tot <= 2.0
        if not agree:
            total["central-from"] = (total.get("central-from") or "") + (
                f"; DISAGREES with the split example's carrier sum {csum:.3g} ({short}, {sp['eid']}): "
                "one of the two is on another scope; carriers left unscaled")
            stats["totals disagreeing with carriers"] += 1
        have = {(s.get("target") or "").strip().lower(): s for s in rows
                if (s.get("target") or "").strip()}

        def row_for(t, src_rs, eid):
            s = have.get(t)
            if s is None:
                s = dict(total, **{"target": t, "n": 1, "n-external": 0, "external-factors": "",
                                   "sources": _sources(src_rs), "examples": eid})
                summaries.append(s)
                have[t] = s
            return s

        for t, v in sp["top"].items():
            share = v / csum
            s = row_for(t, sp["rs"], sp["eid"])
            if agree:
                s["central"] = f"{share * tot:.6g}"
                s["low"] = f"{share * tlo:.6g}" if tlo is not None else ""
                s["high"] = f"{share * thi:.6g}" if thi is not None else ""
                s["central-from"] = f"share {share:.1%} of the total, split from {short} ({sp['eid']})"
                stats["carriers set as shares"] += 1
            else:
                s["central"] = f"{v:.6g}"
                s["low"], s["high"] = "", ""
                s["central-from"] = (f"as the split example states it ({short}, {sp['eid']}; share "
                                     f"{share:.1%} of its carrier sum {csum:.3g}, which disagrees "
                                     f"with the pooled total {tot:.3g})")
                stats["carriers left unscaled"] += 1
            if t == FUEL_AGG and FUEL_AGG not in {_target(r) for r in sp["rs"]}:
                s["central-from"] += "; fuel = the sum of the named fuels this example gives"
        # ---- level 2: named fuels as a split of `fuel` --------------------------
        fuel_row = have.get(FUEL_AGG)
        f_tot = fnum(fuel_row["central"]) if fuel_row and fuel_row.get("central") else None
        fcands = []
        for e in exs:
            if not _ok(e["named"]):
                continue
            nsum = sum(e["named"].values())
            closeness = abs(log(nsum / f_tot)) if f_tot and f_tot > 0 else 0.0
            fcands.append(((len(e["named"]) < 2, closeness, e["rank"], e["eid"]), e, nsum))
        named_split = set()
        if fcands and f_tot and f_tot > 0:
            _, fs, nsum = min(fcands, key=lambda c: c[0])
            fshort = _short(records, fs["rs"])
            flo, fhi = fnum(fuel_row.get("low")), fnum(fuel_row.get("high"))
            for t, v in fs["named"].items():
                share = v / nsum
                s = row_for(t, fs["rs"], fs["eid"])
                s["central"] = f"{share * f_tot:.6g}"
                s["low"] = f"{share * flo:.6g}" if flo is not None else ""
                s["high"] = f"{share * fhi:.6g}" if fhi is not None else ""
                s["central-from"] = f"share {share:.1%} of fuel, split from {fshort} ({fs['eid']})"
                named_split.add(t)
                stats["fuels set as shares of fuel"] += 1
        for t, s in have.items():
            if t in NOT_CARRIER or t in sp["top"] or t in named_split:
                continue
            level = "of fuel" if t not in NO_HV_CARRIERS and t != FUEL_AGG else "of the total"
            s["central-from"] = (s.get("central-from") or "") + \
                f"; pooled apart: not part of the split {level}, so it does not sum with the others"
            stats["pooled apart"] += 1
    return dict(stats)
