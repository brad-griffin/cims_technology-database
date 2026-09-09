"""Build wide-format views of the harmonized database.

Run from the repo root (after populate.py):
    python data/harmonized/build-wide.py

Writes, and adds both as banded sheets to the workbook:
    wide-technology.csv   one row per technology, one column per parameter
    wide-flow.csv         one row per technology, one column per commodity

These are VIEWS, not tables. The long `tech-parameter`, `tech-flow` and
`tech-constraint` remain the record and keep every value in the unit its source
reported. The wide views are where units are harmonised so that sources can be
compared, which is a different job and a lossy one -- regenerate them after any
change to the long tables, and never edit them.

What the view does that the database does not:

  * **Harmonises units.** Technical values convert to the parameter's target
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
ROSTER_COLS = ["technology-label", "equipment", "energy-carrier", "variant",
               "state-of-development", "trl", "year-available", "status"]
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

    def convert(self, value, unit, target):
        """(value, unit) -> target unit, or None when no route exists."""
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
    """Put a money rate on the common basis: 2025_CAD per GJ of annual output
    capacity. Returns (value, lo, hi, unit) unchanged when there is no route.

    Every source prices its technology against a different denominator -- per kW,
    per tonne of annual product, per GJ, or as an absolute sum -- and those are
    not interconvertible without knowing how much the thing makes. Dividing by
    specific energy consumption or annual output supplies exactly that, and is
    the only step here that is not arithmetic on the source's own numbers.
    """
    if not unit.startswith("2025_CAD"):
        return value, lo, hi, unit
    denom = unit.split("/", 1)[1] if "/" in unit else ""
    sec, ao, cf = sc.get("sec"), sc.get("annual-output"), sc.get("cf")
    scale = None
    target = "2025_CAD/GJ-per-yr"

    if denom == "GJ-per-yr":
        return value, lo, hi, unit
    if denom == "GJ":                                  # a per-output cost
        return value, lo, hi, unit
    if denom == "kWh":                                 # variable cost per kWh
        scale, target = GJ_PER_KWH, "2025_CAD/GJ"
    elif denom == "kW":
        # kW of capacity -> GJ delivered in a year. With no capacity factor the
        # only defensible reading is nameplate, and the unit has to say so.
        if cf:
            scale, target = 1.0 / (GJ_PER_KW_YR * cf), "2025_CAD/GJ-per-yr"
        else:
            scale, target = 1.0 / GJ_PER_KW_YR, "2025_CAD/GJ-per-yr-nameplate"
    elif denom.endswith("-per-yr"):
        # Only divide by an energy throughput that is positive and not near
        # zero. A technology whose net energy is negative (BOF gas recovery) or
        # a rounding away from nothing would otherwise come back with a
        # negative or explosive cost per GJ.
        if sec is not None and sec > 0.05:
            scale = 1.0 / sec
        else:
            return value, lo, hi, "2025_CAD/product-per-yr"
    elif denom == "" and ao:
        scale = 1.0 / ao                               # absolute cost -> per GJ/yr
    if scale is None:
        return value, lo, hi, unit
    f = lambda x: None if x is None else x * scale
    return f(value), f(lo), f(hi), target


def normalise(facts, params, units, sc, product_unit, refcap, refcap_used):
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
                if r["parameter"] == "capex" and v is not None:
                    # The capital cost of ONE unit at its own working size --
                    # a boiler, a kiln, a plant -- which is what a modeller
                    # asks for first. Either the source gave a whole-unit sum,
                    # or a rate is multiplied by that technology's own capacity.
                    tot, ref, refu = None, None, ""
                    scl = sc.get(r["technology"], {})
                    d1 = unit.split("/", 1)[1] if "/" in unit else ""
                    # A rate must meet a scale from the SAME source. Pairing
                    # UKERC's cost per GJ/yr with an EPA plant size produces a
                    # total that reads as one source's finding and is neither's.
                    same_kw = scl.get("kw@") == r["source-id"]
                    same_ao = scl.get("annual-output@") == r["source-id"]
                    if not d1:
                        tot = v
                        if same_kw:
                            ref, refu = scl.get("kw"), "kW"
                    elif d1 == "kW" and scl.get("kw") and same_kw:
                        tot, ref, refu = v * scl["kw"], scl["kw"], "kW"
                    elif d1 == "GJ-per-yr" and scl.get("annual-output") and same_ao:
                        tot = v * scl["annual-output"]
                        ref, refu = scl["annual-output"], "GJ/yr"
                    elif d1.endswith("-per-yr"):
                        rc = refcap.get(r["technology"])
                        if rc:
                            tot, ref, refu = v * rc[0], rc[0], rc[1]
                    if tot is not None:
                        out[(r["technology"], "capex-total", "", "2025_CAD")].append(
                            {"value": tot, "min": None, "max": None,
                             "source": r["source-id"], "derived": bool(r["formula"])})
                        if ref is not None:
                            refcap_used[r["technology"]] = (ref, refu)
                was_absolute = "/" not in unit
                v, lo, hi, unit = to_common_basis(
                    v, lo, hi, unit, r["technology"], sc.get(r["technology"], {}))
                if was_absolute and "/" not in unit:
                    # an absolute sum with no annual output to divide by: it is
                    # already recorded in capex-total, so do not keep a second
                    # copy in the rate column
                    continue
        else:
            # Aim at the dictionary's unit; if there is no route to it, aim at
            # the unit most of this parameter's rows already use. That folds
            # MJ/unit into GJ/unit without needing a rule per parameter, and
            # leaves genuinely different denominators in separate columns.
            cands = [params.get(r["parameter"], {}).get("unit-default", ""),
                     dominant.get((r["parameter"], r["target"]), "")]
            for tgt in [c for c in cands if c]:
                cv = units.convert(v, unit, tgt)
                if cv is not None and tgt != unit:
                    lo, hi = units.convert(lo, unit, tgt), units.convert(hi, unit, tgt)
                    v, unit = cv, tgt
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
    nodes = {r["service-node"]: r for r in read("service-node.csv")}
    params = {r["parameter"]: r for r in read("parameter.csv")}
    # A technology can serve several sectors, so the roster holds it once and
    # technology-application says where it applies. The wide view is a reading
    # of the roster by sector, so a technology appears under each sector it
    # serves -- the same idiom the source-list sheet already uses.
    apps = collections.defaultdict(list)
    for a in read("technology-application.csv"):
        apps[a["technology"]].append(a)
    placed = [(t, a) for t in techs for a in
              (apps.get(t["technology"]) or [{"service-node": ""}])]
    units = Units()

    prio = {r["source-id"]: r for r in read("source-priority.csv")}
    def rank(sid):
        return int(prio.get(sid, {}).get("rank") or 99)

    def rec_rank(rec):
        """Rank a record by the compilation it came through, where there is one:
        a value UKERC selected and harmonised carries UKERC's standing even
        though the number belongs to whoever UKERC cited."""
        return rank(rec.get("via") or rec["source"])
    def short(sid):
        return prio.get(sid, {}).get("short-name") or sid

    # display order comes from the dictionaries' own row order, so temperature
    # tiers run low, medium, high rather than alphabetically
    sector_order = {r["sector"]: i for i, r in enumerate(read("sector.csv"))}
    end_use_order = {r["end-use"]: i for i, r in enumerate(read("end-use.csv"))}

    sc = scales(facts)
    product_unit, refcap_used = {}, {}

    # A reference plant size per (sector, process step), for the sources that
    # price per unit of annual product and never state a plant. Blank rows are
    # the honest state: nothing here is guessed.
    refcap_by_step = {}
    rcp = HERE / "reference-capacity.csv"
    if rcp.exists():
        for r in read("reference-capacity.csv"):
            c = fnum(r.get("capacity"))
            if c:
                refcap_by_step[(r["sector"], r["process-step"])] = (c, r.get("unit", ""))
    refcap = {}
    for t, a in placed:
        n = nodes.get(a["service-node"], {})
        hit = refcap_by_step.get((n.get("sector", ""), n.get("process-step", "")))
        if hit:
            # First node wins. A reference plant size is a property of the step,
            # and a technology serving several steps has no single one; taking
            # the first is arbitrary but at least stable and stated.
            refcap.setdefault(t["technology"], hit)

    grouped = normalise(facts, params, units, sc, product_unit, refcap, refcap_used)

    # one column per (parameter, target, unit); the commonest unit for a
    # parameter keeps the bare name, the rest are suffixed
    per_param = collections.defaultdict(collections.Counter)
    for (_, p, tg, u) in grouped:
        per_param[(p, tg)][u] += 1
    # A money parameter ends up in at most four columns, each a different
    # quantity rather than a different spelling of one: the common per-GJ/yr
    # basis, a per-unit-of-product rate for rows with no energy throughput to
    # divide by, a nameplate rate where no capacity factor is known, and an
    # absolute sum where the source gave one.
    # The canonical unit differs by parameter: a capital cost is per unit of
    # annual CAPACITY, a variable operating cost is per unit of OUTPUT. Both
    # were previously mapped to the bare column name, which collided.
    def suffix_for(p, u):
        canonical = "2025_CAD/GJ" if p.startswith("opex-variable") else "2025_CAD/GJ-per-yr"
        other = "2025_CAD/GJ-per-yr" if p.startswith("opex-variable") else "2025_CAD/GJ"
        return {canonical: "", other: "-per-capacity" if p.startswith("opex-variable")
                                     else "-per-output",
                "2025_CAD/product-per-yr": "-per-product",
                "2025_CAD/GJ-per-yr-nameplate": "-nameplate",
                "2025_CAD": "-total"}.get(u)
    colname, colunit = {}, {}
    for (p, tg), counter in per_param.items():
        base = f"{p}_{tg}" if tg else p
        main_unit = counter.most_common(1)[0][0]
        for u in counter:
            key = (p, tg, u)
            suf = (suffix_for(p, u)
                   if p.startswith(("capex", "opex", "decommissioning"))
                   and not p.endswith("-total") else None)
            if suf is not None:
                colname[key] = base + suf
            else:
                colname[key] = base if u == main_unit else f"{base}__{slug(u)}"
            colunit[colname[key]] = u

    order = sorted(colname.values(),
                   key=lambda c: (list(params).index(c.split("__")[0].split("_")[0])
                                  if c.split("__")[0].split("_")[0] in params else 99, c))
    cols = (["technology", "sector", "end-use", "process-step"] + ROSTER_COLS
            + ["product-unit", "reference-capacity", "reference-capacity-unit",
               "sources", "via"] + order)

    rows = []
    for t, a in placed:
        node = nodes.get(a["service-node"], {})
        row = {"technology": t["technology"], "sector": node.get("sector", ""),
               "end-use": node.get("end-use", ""),
               "process-step": node.get("process-step", "")}
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
            if vals:
                lo, hi = min(vals), max(vals)
                if central is None or lo < central["value"]:
                    row[f"{c}"] = row.get(c, "")
                row[c + "_min"], row[c + "_max"] = round(lo, 6), round(hi, 6)
            srcs.update(r["source"] for r in recs)
            vias.update(r["via"] for r in recs if r.get("via"))
        row["product-unit"] = product_unit.get(t["technology"], "")
        row["via"] = ", ".join(short(v) for v in sorted(vias, key=rank))
        rc = refcap_used.get(t["technology"])
        if rc:
            row["reference-capacity"] = round(rc[0], 6)
            row["reference-capacity-unit"] = rc[1]
        row["sources"] = ", ".join(short(s) for s in sorted(srcs, key=rank))
        rows.append(row)

    # min/max columns are created above; fold them into the column order
    full = []
    for c in cols:
        full.append(c)
        if c in colunit:
            full += [f"{c}_min", f"{c}_max"]
    cols = full
    for r in rows:
        for c in cols:
            r.setdefault(c, "")

    rows.sort(key=lambda r: (sector_order.get(r["sector"], 99),
                             end_use_order.get(r["end-use"], 99),
                             r["process-step"], r["technology"]))
    write("wide-technology.csv", cols, rows)

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
    for t, a in placed:
        if t["technology"] not in fby:
            continue
        node = nodes.get(a["service-node"], {})
        row = {"technology": t["technology"], "sector": node.get("sector", ""),
               "end-use": node.get("end-use", ""),
               "process-step": node.get("process-step", ""),
               "per-unit": funit.get(t["technology"], ""),
               "sources": ", ".join(short(s) for s in
                                    sorted(fsrc[t["technology"]], key=rank)),
               "via": ", ".join(short(v) for v in
                                sorted(fvia[t["technology"]], key=rank))}
        row.update(fby[t["technology"]])
        frows.append(row)
    frows.sort(key=lambda r: (sector_order.get(r["sector"], 99),
                              end_use_order.get(r["end-use"], 99),
                              r["process-step"], r["technology"]))
    write("wide-flow.csv", fcols, frows)

    pclass = {r["parameter"]: r["parameter-class"] for r in params.values()}
    ident = {"technology", "sector", "end-use", "process-step", "sources", "per-unit",
             "product-unit", "reference-capacity", "reference-capacity-unit", "via",
             *ROSTER_COLS}
    pclass["capex-total"] = "cost"

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
                      "tables. Units are harmonised here for comparison; the database "
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
            ws.column_dimensions[get_column_letter(j)].width = (
                42 if j == first else max(11, min(20, len(c) + 3)))
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
                cell = ws.cell(r, j, _cell(row.get(col, "")))
                cell.font = body_font
                if j == first:
                    cell.alignment = Alignment(indent=1)
            r += 1
        ws.freeze_panes = ws.cell(UNIT + 2, first + 1).coordinate
    apply_view(wb)
    wb.save(wb_path)
    print(f"  workbook: {', '.join(tables)} rebuilt, units in the header row "
          f"({len(wb.sheetnames)} sheets)")


if __name__ == "__main__":
    sys.exit(main())
