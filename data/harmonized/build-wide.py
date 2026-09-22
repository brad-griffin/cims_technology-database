"""Build wide-format views of the harmonized database.

Run from the repo root (after populate.py):
    python data/harmonized/build-wide.py

Writes, and adds both as banded sheets to the workbook:
    wide-technology.csv   one row per technology, one column per parameter
    wide-flow.csv         one row per technology, one column per commodity

These are VIEWS, not tables. The long `tech-parameter`, `tech-flow` and
`tech-constraint` remain the record and keep every value in the unit its source
reported. The wide views are where units are harmonized so that sources can be
compared, which is a different job and a lossy one -- regenerate them after any
change to the long tables, and never edit them.

What the view does that the database does not:

  * **Harmonizes units.** Technical values convert to the parameter's target
    unit via `unit-conversion.csv` (exact physical constants). Monetary values
    convert to 2025_CAD via `currency-conversion.csv` -- whose factors are the
    modeller's to supply, since a deflator and an exchange rate are judgements
    with a citable source, not constants. Until they are filled, monetary values
    stay in their source currency and each currency gets its own column, which
    is deliberately awkward: it is a standing prompt to supply the rates.
  * **Folds every source for a parameter into one column.** Derived and
    as-reported values sit together. The central value comes from the
    highest-ranked source in `source-priority.csv` -- broadest first, then most
    recent -- and the min/max span every source's value and its own range.
  * **Names its sources.** A `sources` column lists the short names that
    contributed to the row, best-ranked first. There is no source-id column;
    the long tables carry the ids.

A column exists per (parameter, target, unit). Two rows for the same parameter
in units that cannot be converted into one another -- a capex per kW and a capex
per tonne of annual output -- get separate columns rather than being averaged
into a number that means nothing. The unit is stated in the header, not in a
column of its own.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workbook import apply_view

HERE = Path(__file__).resolve().parent
# trl is on the common 1-9 ladder (see trl-scale-map.csv), so it can sit in a
# comparison view; trl-as-reported and trl-scale stay in the roster table for
# anyone auditing the mapping rather than comparing across technologies.
# technology-label and status were dropped 2026-09-10. The label held only the
# first CIMS name that claimed a technology, chosen by load order, when up to 29
# stood behind it -- CIMS names live in cims-map.csv until CIMS is properly
# connected. status read `draft` on every row, because the view already filters
# out `placeholder` and `unquantified`.
ROSTER_COLS = ["equipment", "energy-carrier", "variant",
               "state-of-development", "trl", "year-available"]
MONEY = re.compile(r"^(\d{4})_([A-Z]{3})(?:/(.+))?$")
TARGET_CURRENCY = "2025_CAD"


def read(name):
    p = HERE / name
    if not p.exists():
        sys.exit(f"{name} not found -- run populate.py first")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write(name, cols, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"  {name:24s} {len(cols):4d} columns, {len(rows):5d} rows")


def fnum(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def slug(x):
    return re.sub(r"[^a-z0-9]+", "-", str(x).lower()).strip("-")


class Units:
    """Physical and currency conversion, driven entirely by the two CSVs so a
    factor is never buried in code."""

    def __init__(self):
        self.phys = {}
        for r in read("unit-conversion.csv"):
            f, o = fnum(r["factor"]), fnum(r["offset"])
            if f is not None:
                self.phys[(r["from-unit"], r["to-unit"])] = (f, o or 0.0)
        self.cur, self.missing = {}, set()
        for r in read("currency-conversion.csv"):
            f = fnum(r["factor"])
            if f is not None:
                self.cur[r["from-currency"]] = (r["to-currency"], f)

    def has_route(self, unit, target):
        return unit == target or (unit, target) in self.phys

    def convert(self, value, unit, target):
        """(value, unit) -> target unit, or None when no route exists.

        A None value with a valid route returns None, so callers must test the
        ROUTE with has_route rather than the returned value. Testing the value
        left every row that carries only a min and a max -- a range with no
        central estimate, which ETSAP prints often -- unconverted and stranded
        in its own column: capacity in kW and t/d, specific energy in MWh/t,
        and three of the four heat-pump COPs were all sitting out for this
        reason."""
        if value is None or unit == target:
            return value
        if (unit, target) in self.phys:
            f, o = self.phys[(unit, target)]
            return value * f + o
        return None

    def money_target(self, unit):
        """Rewrite a monetary unit into 2025_CAD, keeping its denominator.
        Returns (target-unit, factor) or (unit, None) when the rate is missing."""
        m = MONEY.match(unit)
        if not m:
            return unit, None
        denom = m.group(3)
        cur = f"{m.group(1)}_{m.group(2)}"
        if cur not in self.cur:
            self.missing.add(cur)
            return unit, None
        to, f = self.cur[cur]
        return (f"{to}/{denom}" if denom else to), f


GJ_PER_KW_YR = 8760 * 0.0036          # 1 kW running all year = 31.536 GJ
GJ_PER_KWH = 0.0036


def scales(facts):
    """Per technology, whatever lets a cost rate be put on a common basis:
    specific energy consumption (GJ per unit of product), annual output (GJ),
    and capacity factor."""
    s = collections.defaultdict(dict)
    for r in facts:
        v = fnum(r["value"])
        if v is None:
            continue
        p, u = r["parameter"], (r["unit"] or "").strip()
        if p == "specific-energy-consumption" and u.startswith("GJ"):
            s[r["technology"]].setdefault("sec", v)
        elif p == "annual-output" and u == "GJ":
            s[r["technology"]].setdefault("annual-output", v)
            s[r["technology"]].setdefault("annual-output@", r["source-id"])
        elif p == "capacity-factor":
            s[r["technology"]].setdefault("cf", v / 100 if v > 1.5 else v)
        elif p == "capacity" and u in ("kW", "MW"):
            s[r["technology"]].setdefault("kw", v * (1000 if u == "MW" else 1))
            s[r["technology"]].setdefault("kw@", r["source-id"])
    return s


def to_common_basis(value, lo, hi, unit, tech, sc):
    """Put a money rate on ONE UNIT OF THE TECHNOLOGY'S OWN OUTPUT.

    Set by the user 2026-09-10 (D13). The basis is per unit of output, in
    whatever unit that technology's output is measured in: a tonne for a
    process technology, a GJ for an energy service. It is deliberately NOT one
    common denominator across the database.

    What this replaced, and why: the old version manufactured a GJ denominator
    for every cost by dividing a per-tonne rate by `specific-energy-consumption`
    -- final energy INPUT per tonne of product. The absolute and per-kW routes
    divided by annual OUTPUT instead. One column therefore mixed cost per GJ of
    input with cost per GJ of output, quantities that differ by the efficiency
    (about 1.18x for an 85% boiler, 3.5x for a heat pump), and 84 of the 86
    populated cells were the input kind while the docstring claimed the output
    kind. Converting the input ones to output was impossible in any case: of the
    49 technologies on that route, exactly one carries an efficiency.

    Dropping the division fixes it. A per-tonne rate is ALREADY per unit of
    output, and is what 262 of the 784 cost rows say natively, so the harmonized
    figure is now the source's own number. Only genuinely convertible
    denominators are still converted: kWh to GJ, kW of rating to GJ delivered in
    a year, and an absolute sum to a rate where the same source states an annual
    output. Anything else keeps the unit it arrived in.
    """
    if not unit.startswith("2025_CAD"):
        return value, lo, hi, unit
    denom = unit.split("/", 1)[1] if "/" in unit else ""
    ao, cf = sc.get("annual-output"), sc.get("cf")
    scale, target = None, None

    if denom in ("GJ-per-yr", "GJ") or denom.endswith("-per-yr") or denom:
        # already per unit of this technology's output -- a tonne of product, a
        # GJ of service, a cubic metre of milk. Left exactly as reported.
        if denom == "kWh":
            scale, target = 1.0 / GJ_PER_KWH, "2025_CAD/GJ"
        elif denom == "kW":
            # a capacity RATING, not an output: kW -> GJ delivered in a year.
            # With no capacity factor the only defensible reading is nameplate.
            if cf:
                scale, target = 1.0 / (GJ_PER_KW_YR * cf), "2025_CAD/GJ-per-yr"
            else:
                scale, target = 1.0 / GJ_PER_KW_YR, "2025_CAD/GJ-per-yr"
        else:
            return value, lo, hi, unit
    elif not denom and ao:
        # an absolute sum, made a rate by the annual output the source states
        scale, target = 1.0 / ao, "2025_CAD/GJ-per-yr"
    if scale is None:
        return value, lo, hi, unit
    f = lambda x: None if x is None else x * scale
    return f(value), f(lo), f(hi), target


def normalize(facts, params, units, sc, product_unit, out_unit):
    """One record per (technology, parameter, target, unit-after-conversion).

    Folds derived and as-reported values together, converts what it can, and
    keeps every source's number so the range spans them all.
    """
    # The wide view shows quantities, so a row that records only that a source
    # rated an option without costing it ("Cost of H2") has nothing to show. It
    # stays in tech-parameter, where the finding lives; leaving it in here spawns
    # a second, permanently empty column for every parameter that has one.
    facts = [r for r in facts
             if (r["value"] or "").strip() or (r["value-min"] or "").strip()
             or (r["value-max"] or "").strip()]

    dominant = {}
    counts = collections.defaultdict(collections.Counter)
    for r in facts:
        counts[(r["parameter"], r["target"])][(r["unit"] or "").strip()] += 1
    for k, c in counts.items():
        dominant[k] = c.most_common(1)[0][0]
    seen_units = {k: set(c) for k, c in counts.items()}

    out = collections.defaultdict(list)
    for r in facts:
        v = fnum(r["value"])
        if v is None and r["formula"]:
            continue                       # a formula with no computed value
        unit = (r["unit"] or "").strip()
        lo, hi = fnum(r["value-min"]), fnum(r["value-max"])
        if MONEY.match(unit):
            tgt, f = units.money_target(unit)
            if f is not None:
                v = None if v is None else v * f
                lo = None if lo is None else lo * f
                hi = None if hi is None else hi * f
                unit = tgt
            if r["parameter"].startswith(("capex", "opex", "decommissioning")):
                d0 = unit.split("/", 1)[1] if "/" in unit else ""
                if d0.endswith("-per-yr") and d0 != "GJ-per-yr":
                    product_unit.setdefault(r["technology"], d0[:-len("-per-yr")])
                elif d0 and not d0.endswith("-per-yr") and d0 not in ("kW", "kWh"):
                    product_unit.setdefault(r["technology"], d0)
                # capex-total is gone (D13). It was a derived column only, never
                # a stored parameter, and it depended on reference-capacity.csv,
                # every cell of which was blank. An absolute sum that cannot be
                # made a rate now simply keeps its own unit instead of being
                # dropped as a duplicate of a total that no longer exists.
                v, lo, hi, unit = to_common_basis(
                    v, lo, hi, unit, r["technology"], sc.get(r["technology"], {}))
        else:
            # Aim at the dictionary's unit; if there is no route to it, aim at
            # the unit most of this parameter's rows already use. That folds
            # MJ/unit into GJ/unit without needing a rule per parameter, and
            # leaves genuinely different denominators in separate columns.
            cands = [params.get(r["parameter"], {}).get("unit-default", ""),
                     dominant.get((r["parameter"], r["target"]), "")]
            # A generic "/unit" denominator is the source's shorthand for the
            # technology's own product unit. Where that unit is a tonne, say so
            # -- it lets GJ/unit, GJ/t, kWh/t and MWh/t become one column
            # instead of four (D13, R-specific-energy). Where it is anything
            # else (a cubic metre of milk, a thousand pounds of output, a GJ of
            # service) the generic spelling is kept, because those genuinely
            # are different denominators and must not be summed as tonnes.
            if unit.endswith("/unit") and out_unit.get(r["technology"]) == "t":
                unit = unit[:-len("/unit")] + "/t"
            # ...and, failing those, any other unit this parameter already
            # uses that is reachable from here. That is what folds t/d into
            # kt/yr and kW into MW for `capacity`, where there is no single
            # default because a mass throughput and a power rating are
            # different dimensions and both are legitimate.
            cands += sorted(seen_units.get((r["parameter"], r["target"]), set()))
            for tgt in [c for c in cands if c and c != unit]:
                if not units.has_route(unit, tgt):
                    continue
                v = units.convert(v, unit, tgt)
                lo, hi = units.convert(lo, unit, tgt), units.convert(hi, unit, tgt)
                unit = tgt
                break
        key = (r["technology"], r["parameter"], r["target"], unit)
        out[key].append({"value": v, "min": lo, "max": hi, "source": r["source-id"],
                         "via": r.get("via-source-id", ""),
                         "derived": bool(r["formula"])})
    return out


def main() -> int:
    techs = read("technology.csv")
    facts = read("tech-parameter.csv")
    flows = read("tech-flow.csv")
    # The views show what the database KNOWS; the roster shows what it has been
    # asked to cover. 187 of 415 technologies carried no parameter, flow or
    # constraint row -- CIMS and source roster names that were never quantified
    # -- and as blank rows they made the view about twice as long as its
    # content. They keep their place in technology.csv, marked `placeholder` or
    # `unquantified`. The test is on the data itself rather than on the status
    # column, so the view cannot drift from what populate.py labelled.
    # (User's request, 2026-09-10.)
    with_data = ({r["technology"] for r in facts} | {r["technology"] for r in flows}
                 | {r["technology"] for r in read("tech-constraint.csv")})
    hidden = [t for t in techs if t["technology"] not in with_data]
    techs = [t for t in techs if t["technology"] in with_data]
    nodes = {r["service-node"]: r for r in read("service-node.csv")}
    params = {r["parameter"]: r for r in read("parameter.csv")}
    # A technology can serve several sectors, so the roster holds it once and
    # technology-application says where it applies. The wide view is a reading
    # of the roster by sector, so a technology appears under each sector it
    # serves -- the same idiom the source-list sheet already uses.
    apps = collections.defaultdict(list)
    for a in read("technology-application.csv"):
        apps[a["technology"]].append(a)

    # ONE ROW PER (technology, sector, end use), with the process steps joined
    # into a single cell (user's request, 2026-09-10). A technology serving six
    # steps of one end use was six rows that differed in nothing but that cell:
    # every fact column is keyed on the technology alone, so the other rows
    # repeated the same numbers and made the technology look six times as
    # common as it is. Collapsing them loses nothing.
    def placements(t):
        rows = apps.get(t["technology"])
        if not rows:
            return [{"sector": "", "end-use": "", "process-step": "", "nodes": []}]
        by_band = {}
        for a in rows:
            n = nodes.get(a["service-node"], {})
            band = (n.get("sector", ""), n.get("end-use", ""))
            v = by_band.setdefault(band, {"sector": band[0], "end-use": band[1],
                                          "steps": [], "nodes": []})
            v["nodes"].append(a["service-node"])
            step = n.get("process-step", "")
            if step and step not in v["steps"]:
                v["steps"].append(step)
        for v in by_band.values():
            v["process-step"] = "; ".join(sorted(v["steps"]))
        return list(by_band.values())

    placed = [(t, v) for t in techs for v in placements(t)]
    units = Units()

    prio = {r["source-id"]: r for r in read("source-priority.csv")}
    def rank(sid):
        return int(prio.get(sid, {}).get("rank") or 99)

    def rec_rank(rec):
        """Rank a record by the compilation it came through, where there is one:
        a value UKERC selected and harmonized carries UKERC's standing even
        though the number belongs to whoever UKERC cited."""
        return rank(rec.get("via") or rec["source"])
    def short(sid):
        return prio.get(sid, {}).get("short-name") or sid

    # display order comes from the dictionaries' own row order, so temperature
    # tiers run low, medium, high rather than alphabetically
    sector_order = {r["sector"]: i for i, r in enumerate(read("sector.csv"))}
    end_use_order = {r["end-use"]: i for i, r in enumerate(read("end-use.csv"))}

    sc = scales(facts)
    product_unit = {}

    # What one unit of each technology's output is measured in. A process
    # technology makes tonnes; an energy service delivers GJ. Read off the
    # service nodes the technology serves, so it is available even where no
    # cost row has stated a denominator. Costs and specific energy are both
    # expressed per unit of this (D13).
    out_unit = {}
    for t, v in placed:
        for nid in v["nodes"]:
            su = (nodes.get(nid, {}).get("service-unit") or "").strip()
            if su:
                out_unit.setdefault(t["technology"], su)
                break

    grouped = normalize(facts, params, units, sc, product_unit, out_unit)

    # one column per (parameter, target, unit); the commonest unit for a
    # parameter keeps the bare name, the rest are suffixed
    per_param = collections.defaultdict(collections.Counter)
    for (_, p, tg, u) in grouped:
        per_param[(p, tg)][u] += 1
    # ONE COLUMN PER COST PARAMETER (D13). Every per-output money unit shares
    # the column, so it holds CAD/t for a blast furnace and CAD/GJ for a boiler
    # and is read against `product-unit`. Within an end-use band the unit is
    # effectively constant, which is what makes that workable; ACROSS bands the
    # column must not be sorted, averaged or charted. An absolute sum is not a
    # rate and keeps its own column.
    def cost_col(u):
        return u.startswith("2025_CAD") and "/" in u
    colname, colunit = {}, {}
    for (p, tg), counter in per_param.items():
        base = f"{p}_{tg}" if tg else p
        money = p.startswith(("capex", "opex", "decommissioning"))
        main_unit = counter.most_common(1)[0][0]
        if money:
            rates = [u for u in counter if cost_col(u)]
            main_unit = max(rates, key=lambda u: counter[u]) if rates else main_unit
        for u in counter:
            key = (p, tg, u)
            if money and cost_col(u):
                colname[key] = base
                # the column holds whatever each technology's output is
                # measured in, so naming one unit in the header would be a lie
                colunit[colname[key]] = "2025_CAD per unit of output (see product-unit)"
            else:
                colname[key] = base if u == main_unit else f"{base}__{slug(u)}"
                colunit.setdefault(colname[key], u)
    # Two units must never share a column by accident. `opex-variable` was
    # doubled in the header for exactly that reason: 2025_CAD/GJ was mapped to
    # the bare name by a suffix table and 2025_CAD/t reached the same name by
    # being the commonest unit, so the header carried the name twice and both
    # copies read the same cell -- one unit's values silently overwrote the
    # other's. Deliberate sharing (the cost columns above) is fine; anything
    # else falls back to the unit suffix.
    seen = {}
    for key in sorted(colname):
        p, tg, u = key
        name = colname[key]
        if name in seen and seen[name] != ("cost" if p.startswith(
                ("capex", "opex", "decommissioning")) and cost_col(u) else key):
            if not (p.startswith(("capex", "opex", "decommissioning")) and cost_col(u)):
                colname[key] = f"{name}__{slug(u)}"
                colunit[colname[key]] = u
                continue
        seen[name] = ("cost" if p.startswith(("capex", "opex", "decommissioning"))
                      and cost_col(u) else key)

    # cost parameters deliberately share one column across units, so the same
    # name arrives several times; the view needs it once
    order = sorted(dict.fromkeys(colname.values()),
                   key=lambda c: (list(params).index(c.split("__")[0].split("_")[0])
                                  if c.split("__")[0].split("_")[0] in params else 99, c))
    cols = (["technology", "sector", "end-use", "process-step"] + ROSTER_COLS
            + ["product-unit", "sources", "via"] + order)

    rows = []
    for t, v in placed:
        row = {"technology": t["technology"], "sector": v["sector"],
               "end-use": v["end-use"], "process-step": v["process-step"]}
        row.update({c: t.get(c, "") for c in ROSTER_COLS})
        srcs, vias = set(), set()
        for (tech, p, tg, u), recs in grouped.items():
            if tech != t["technology"]:
                continue
            recs = sorted(recs, key=rec_rank)
            central = next((r for r in recs if r["value"] is not None), None)
            vals = [x for r in recs for x in (r["value"], r["min"], r["max"])
                    if x is not None]
            c = colname[(p, tg, u)]
            if central:
                row[c] = round(central["value"], 6)
            # A min/max pair is only information when the values behind the cell
            # actually spread. One source reporting one number was writing
            # min = max = that number, which happened on 58% of the filled pairs
            # and reads as a measured range when it is a single point. The test
            # is on the DISTINCT values, not on the number of records, so a
            # single source's own reported range still prints, and two sources
            # that agree exactly do not. (User's request, 2026-09-10.)
            spread = {round(v, 6) for v in vals}
            if len(spread) > 1:
                row[c + "_min"], row[c + "_max"] = min(spread), max(spread)
            srcs.update(r["source"] for r in recs)
            vias.update(r["via"] for r in recs if r.get("via"))
        row["product-unit"] = (product_unit.get(t["technology"])
                               or out_unit.get(t["technology"], ""))
        row["via"] = ", ".join(short(v) for v in sorted(vias, key=rank))
        row["sources"] = ", ".join(short(s) for s in sorted(srcs, key=rank))
        rows.append(row)

    # min/max columns are created above; fold them into the column order,
    # skipping any pair no row fills. Since a pair is only written where the
    # values spread, a parameter every source states as a single point now has
    # no range at all, and two empty columns per parameter is a real cost in a
    # sheet this wide.
    used = {c for r in rows for c, v in r.items() if v != "" and c.endswith(("_min", "_max"))}
    full = []
    for c in cols:
        full.append(c)
        if c in colunit and (f"{c}_min" in used or f"{c}_max" in used):
            full += [f"{c}_min", f"{c}_max"]
    cols = full
    for r in rows:
        for c in cols:
            r.setdefault(c, "")

    # Technology sorts BEFORE process-step: the sheet bands on sector and end
    # use only, so within an end-use band the reader sees one alphabetical run
    # of technology names. Sorting on the step first split that run into blocks
    # keyed on source wording ('Boilers', 'size-3') with no visible heading, so
    # a name could not be found by scanning. (User's request, 2026-09-10.)
    rows.sort(key=lambda r: (sector_order.get(r["sector"], 99),
                             end_use_order.get(r["end-use"], 99),
                             r["technology"], r["process-step"]))
    write("wide-technology.csv", cols, rows)
    if hidden:
        by = collections.Counter(t["status"] for t in hidden)
        print(f"  {len(hidden)} technologies with no data left out of the views "
              f"({', '.join(f'{v} {k}' for k, v in sorted(by.items()))})")

    # ---- wide technology x commodity ------------------------------------
    coms_in = sorted({r["commodity"] for r in flows if r["direction"] == "input"})
    coms_out = sorted({r["commodity"] for r in flows if r["direction"] == "output"})
    fcols = (["technology", "sector", "end-use", "process-step", "per-unit",
              "sources", "via"]
             + [f"in_{c}" for c in coms_in] + [f"out_{c}" for c in coms_out])
    fby, funit, fsrc, fvia = (collections.defaultdict(dict), {},
                              collections.defaultdict(set), collections.defaultdict(set))
    for r in flows:
        key = ("in_" if r["direction"] == "input" else "out_") + r["commodity"]
        u = (r["unit"] or "").strip()
        v = fnum(r["value"])
        cv = units.convert(v, u, "GJ/unit") if u.endswith("/unit") and u != "GJ/unit" else v
        fby[r["technology"]].setdefault(key, round(cv, 6) if cv is not None else r["value"])
        funit.setdefault(r["technology"], r["per-unit"])
        fsrc[r["technology"]].add(r["source-id"])
        if r.get("via-source-id"):
            fvia[r["technology"]].add(r["via-source-id"])
    frows = []
    for t, v in placed:
        if t["technology"] not in fby:
            continue
        row = {"technology": t["technology"], "sector": v["sector"],
               "end-use": v["end-use"], "process-step": v["process-step"],
               "per-unit": funit.get(t["technology"], ""),
               "sources": ", ".join(short(s) for s in
                                    sorted(fsrc[t["technology"]], key=rank)),
               "via": ", ".join(short(v) for v in
                                sorted(fvia[t["technology"]], key=rank))}
        row.update(fby[t["technology"]])
        frows.append(row)
    frows.sort(key=lambda r: (sector_order.get(r["sector"], 99),
                              end_use_order.get(r["end-use"], 99),
                              r["technology"], r["process-step"]))
    write("wide-flow.csv", fcols, frows)

    pclass = {r["parameter"]: r["parameter-class"] for r in params.values()}
    ident = {"technology", "sector", "end-use", "process-step", "sources", "per-unit",
             "product-unit", "via", *ROSTER_COLS}

    def group_of(c):
        if c in ident:
            return "identity"
        base = c.split("__")[0]
        for suf in ("_min", "_max"):
            if base.endswith(suf):
                base = base[: -len(suf)]
        return pclass.get(base, pclass.get(base.split("_")[0], ""))
    tgroups = {c: group_of(c) for c in cols}
    fgroups = {c: ("identity" if c in ident else
                   "inputs" if c.startswith("in_") else "outputs") for c in fcols}

    tunits = {}
    for c in cols:
        base = c[:-4] if c.endswith("_min") else c[:-4] if c.endswith("_max") else c
        tunits[c] = colunit.get(base, "")
    funits = {c: ("" if c in ident else "GJ/unit") for c in fcols}

    add_sheets({"wide-technology": (cols, rows), "wide-flow": (fcols, frows)},
               {"wide-technology": tgroups, "wide-flow": fgroups},
               {"wide-technology": tunits, "wide-flow": funits})
    if units.missing:
        print(f"\n  {len(units.missing)} currencies have no factor in "
              f"currency-conversion.csv, so those values stay in their source "
              f"currency and get their own columns:")
        for c in sorted(units.missing):
            print(f"      {c} -> {TARGET_CURRENCY}")
    return 0


# Number formats, by the magnitude of the value itself rather than by column:
# 11 of the numeric columns span more than 1000x within themselves (capex runs
# 0.000736 to 39,630), so one format per column would either round the small
# values to zero or bury the large ones in decimals. Bands set by the user
# 2026-09-10, holding roughly three significant figures throughout.
NUM_FORMAT = [(1000, "#,##0"), (100, "#,##0"), (10, "#,##0.0"),
              (1, "#,##0.00"), (0.1, "0.000"), (0.01, "0.0000")]
SMALL_FORMAT = "0.00E+00"
# A year is not a measurement and must never take a thousands separator -- 2035,
# not 2,035. A TRL is a rung on a 1-9 ladder.
PLAIN_INT_COLS = {"year-available", "trl"}


def _number_format(v, col):
    if col in PLAIN_INT_COLS:
        return "0"
    a = abs(v)
    if a == 0:
        return "0"
    for lo, fmt in NUM_FORMAT:
        if a >= lo:
            return fmt
    return SMALL_FORMAT


def _cell(v):
    """Numbers go in as numbers so Excel can sort and plot them."""
    if not isinstance(v, str) or v == "":
        return v
    try:
        return int(v) if v.lstrip("-").isdigit() else float(v)
    except ValueError:
        return v


def add_sheets(tables, groups, unitrow) -> None:
    """Write the wide views as banded sheets in the style of the UKTM sheet of
    the Bataille database: a teal header band, sector names as large bold rows,
    end uses as bold group rows prefixed with '*', and the data indented under
    them starting in column B.

    The layout is deliberately unlike the database sheets. These are views:
    banded rows cannot be filtered or sorted without breaking the grouping, and
    that is the point -- the long tables are where data is edited, and anything
    typed here is lost on the next run. Units live in a header row, not in
    columns of their own, because every value in a column now shares one unit.
    """
    import warnings
    warnings.filterwarnings("ignore")
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb_path = HERE / "technology-database-template.xlsx"
    if not wb_path.exists():
        print("  workbook not found; CSVs written only")
        return
    try:
        wb = openpyxl.load_workbook(wb_path)
    except PermissionError:
        print("  workbook is open in Excel; CSVs written, sheets not added")
        return

    TEAL = PatternFill("solid", fgColor="006666")
    TEAL_D = PatternFill("solid", fgColor="004D4D")
    BAND = PatternFill("solid", fgColor="E8F0EF")
    WARN = PatternFill("solid", fgColor="FFF3CD")
    head_font = Font(sz=12, bold=True, color="FFFFFF")
    grp_font = Font(sz=10, bold=True, color="FFFFFF", italic=True)
    unit_font = Font(sz=10, color="D6E6E6")
    sector_font = Font(sz=16, bold=True, color="1F3B57")
    end_use_font = Font(sz=11, bold=True, color="0E5A4E")
    body_font = Font(sz=11)
    warn_font = Font(sz=11, bold=True, color="7A5C00")
    rule = Border(bottom=Side(style="thin", color="006666"))

    GRP, HDR, UNIT = 3, 4, 5
    for name, (cols, rows) in tables.items():
        if name in wb.sheetnames:
            del wb[name]
        ws = wb.create_sheet(name)
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 2.5
        first = 2

        ws.cell(1, 2, "VIEW — generated by data/harmonized/build-wide.py from the long "
                      "tables. Units are harmonized here for comparison; the database "
                      "keeps every value in the unit its source reported. Anything typed "
                      "here is lost on the next run.")
        for j in range(2, min(len(cols) + 2, 16)):
            ws.cell(1, j).fill = WARN
        ws.cell(1, 2).font = warn_font
        ws.row_dimensions[1].height = 30

        for j, c in enumerate(cols, start=first):
            gc = ws.cell(GRP, j, groups.get(name, {}).get(c, ""))
            gc.fill, gc.font = TEAL_D, grp_font
            gc.alignment = Alignment(horizontal="left", vertical="bottom", wrap_text=True)
            hc = ws.cell(HDR, j, c)
            hc.fill, hc.font = TEAL, head_font
            hc.alignment = Alignment(horizontal="left", vertical="bottom", wrap_text=True)
            uc = ws.cell(UNIT, j, unitrow.get(name, {}).get(c, ""))
            uc.fill, uc.font = TEAL, unit_font
            uc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            # the process-step cell now holds every step the technology
            # serves in this end use, joined; 20 characters cut most of them off
            ws.column_dimensions[get_column_letter(j)].width = (
                42 if j == first else 38 if c == "process-step"
                else max(11, min(20, len(c) + 3)))
        ws.row_dimensions[HDR].height = 46
        ws.row_dimensions[UNIT].height = 26

        r = UNIT + 2
        last_sector = last_end_use = None
        for row in rows:
            sector, end_use = row.get("sector", ""), row.get("end-use", "")
            if sector != last_sector:
                r += 1
                c = ws.cell(r, first, sector or "(unassigned)")
                c.font = sector_font
                for j in range(first, len(cols) + first):
                    ws.cell(r, j).fill = BAND
                    ws.cell(r, j).border = rule
                ws.row_dimensions[r].height = 22
                r += 1
                last_sector, last_end_use = sector, None
            if end_use != last_end_use:
                c = ws.cell(r, first, f"*{end_use}" if end_use else "*(unassigned)")
                c.font = end_use_font
                r += 1
                last_end_use = end_use
            for j, col in enumerate(cols, start=first):
                val = _cell(row.get(col, ""))
                cell = ws.cell(r, j, val)
                cell.font = body_font
                if j == first:
                    cell.alignment = Alignment(indent=1)
                elif isinstance(val, (int, float)) and not isinstance(val, bool):
                    cell.number_format = _number_format(val, col)
                    cell.alignment = Alignment(horizontal="right")
            r += 1
        ws.freeze_panes = ws.cell(UNIT + 2, first + 1).coordinate
    apply_view(wb)
    try:
        wb.save(wb_path)
    except PermissionError:
        # the guard above catches an Excel lock on the READ; Excel allows the
        # read and refuses the write, so the save needs its own
        print("  workbook is open in Excel; CSVs written, wide sheets not rebuilt")
        return
    print(f"  workbook: {', '.join(tables)} rebuilt, units in the header row "
          f"({len(wb.sheetnames)} sheets)")


if __name__ == "__main__":
    sys.exit(main())
