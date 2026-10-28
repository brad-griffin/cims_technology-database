"""The outputs people read: archetype tables, the hierarchy with its technologies and the wide views.

wide-archetype.csv has ONE ROW PER ARCHETYPE by construction: it is a pivot of
archetype-parameter.csv, whose key is the archetype. Each parameter gets a
central value, and `_low`, `_high` and `_n` beside it (low and high only where
the examples spread). Emission species are separate columns. Every cost and
intensity is per unit of the archetype's own product (`product-unit`), so a
column holds CAD per tonne on a kiln row and CAD per GJ on a boiler row: never
sort, average or chart a cost or intensity column across families.

Every archetype has a row, blank or not, including `component` archetypes
(intermediate parts priced to assemble whole-plant costs) and any archetype that
serves no hierarchy node: its `applies-to` reads NO_CONNECTION (2026-09-30).
`--quantified-only` restricts the wide view to archetypes with pooled numbers.
"""
from __future__ import annotations

import re
from collections import defaultdict

from .common import OUTPUT, read, split_list, write
from .hierarchy import Hierarchy
from .normalise import target_unit
from .placement import placement
from .bands import families
from . import capacityunit

IDENT = ["archetype", "label", "family", "families", "end-uses", "equipment", "discriminator", "modifiers",
         "type", "carriers", "heat-tier", "applies-to", "trl", "product-unit", "product",
         "secondary-products", "product-density", "product-density-unit", "product-energy-content",
         "product-energy-content-unit", "n-examples", "status", "sources"]


def unit_label(param: str, target: str) -> str:
    u = target_unit(param, "PU", "")
    if "PU" in u:
        return u.replace("PU-per-yr", "(product-unit per yr)").replace("PU", "product-unit") \
                .replace("kPU/yr", "kt/yr (or MW when product-unit is GJ)")
    return u



def product_properties():
    """{product: {product-density, -unit, product-energy-content, -unit}} from
    records/reference/product-property.csv, the values taken from the factors it
    names in conversion-factor.csv (density in t/m3; energy content, HHV, in GJ/t,
    or GJ/m3 for a product given per volume only) (modeller 2026-10-09)."""
    from . import convert
    from .common import REFERENCE
    rows = convert.Factors().rows
    out = {}
    for r in read(REFERENCE / "product-property.csv"):
        d = {}
        f = rows.get(r.get("density-factor", ""))
        if f and f.get("_f"):
            fu, tu = convert.atom(f["from-unit"]), convert.atom(f["to-unit"])
            k = f["_f"] * tu[1] / fu[1]
            if fu[0] == "volume" and tu[0] == "mass":
                d["product-density"] = f"{k:.4g}"
            elif fu[0] == "mass" and tu[0] == "volume":
                d["product-density"] = f"{1 / k:.4g}"
            if "product-density" in d:
                d["product-density-unit"] = "t/m3"
        f = rows.get(r.get("energy-content-factor", ""))
        if f and f.get("_f"):
            fu, tu = convert.atom(f["from-unit"]), convert.atom(f["to-unit"])
            if tu and fu and tu[0] == "energy" and fu[0] in ("mass", "volume"):
                d["product-energy-content"] = f"{f['_f'] * tu[1] / fu[1]:.4g}"
                d["product-energy-content-unit"] = "GJ/t" if fu[0] == "mass" else "GJ/m3"
        out[r["product"]] = d
    return out


NO_CONNECTION = "no connection"

WIDE_NOTES = {
    "source-corrections": (
        "Parameters whose pooled value includes a figure the source prints wrongly and the "
        "modeller corrected (a slipped decimal or zero, a wrong unit or carrier label), as "
        "examples so corrected / examples pooled. Each correction, the figure as printed and "
        "the evidence: records/reference/source-correction.csv; the rows carry the "
        "correction-id in example-parameter.csv (correction) and a note starting "
        "ASSUMED CORRECTION. These values are also counted in external-conversions and "
        "shaded purple in the workbook."),
    "filled": (
        "Parameters with no sourced value, filled by the fill step and graded: identity "
        "(calculated from this archetype's own values), estimated (from other archetypes or a "
        "class rule fitted on this database), proxy (a class constant from a named outside "
        "catalogue, records/fill/fill-assumption.csv) or guess (a judgement, "
        "records/fill/fill-judgement.csv); not-applicable marks a parameter that does "
        "not characterise the archetype. Shaded in the workbook; their _n is 0. Rule, "
        "inputs and rationale: archetype-parameter.csv (grade, method, rule-id, inputs, "
        "rationale); rules in records/fill/."),
    "external-conversions": (
        "Parameters whose pooled value rests on a conversion factor from outside the source "
        "(a heating value, a density, a process ratio, a pooled efficiency or an assumption), "
        "as examples so converted / examples pooled. Those values are shaded purple in the "
        "workbook. Which factors: archetype-parameter.csv (external-factors); how each example "
        "was converted: example-parameter.csv (conversion, conversion-class, "
        "conversion-factors)."),
}


def applies_to(key, service):
    """The nodes an archetype serves, or NO_CONNECTION when it serves none."""
    return "; ".join(Hierarchy.short(s["branch"]) for s in service.get(key, [])) or NO_CONNECTION


def build(records, hier, examples, summaries, flow_summaries, include_empty=True,
          outdir=OUTPUT, wide_only=False):
    """`outdir`: the folder written to; `wide_only`: write the wide views only (the
    unfilled set, output/unfilled/, 2026-10-09). Also returns `flagged`: the (archetype, column) cells of the wide view whose
    pooled value rests on at least one factor from outside its source; and
    `graded`: {(archetype, column): grade} for the cells the fill step wrote."""
    service = defaultdict(list)
    for s in records.service:
        service[s["archetype"]].append(s)
    ex_by_arch = defaultdict(list)
    for e in examples.values():
        if e.get("archetype"):
            ex_by_arch[e["archetype"]].append(e)
    fam_order = {f: i for i, f in enumerate(records.families)}
    param_order = {p: i for i, p in enumerate(records.parameters)}

    # ---- archetype.csv: every archetype, with what the database holds ------
    with_data = ({s["archetype"] for s in summaries
                  if s.get("grade", "sourced") == "sourced" or s.get("method") == "range-midpoint"}
                 | {s["archetype"] for s in flow_summaries})
    with_fill = {s["archetype"] for s in summaries
                 if s.get("grade", "sourced") not in ("sourced", "not-applicable")}
    with_facts = {e["archetype"] for e in examples.values() if e.get("n-facts")}
    arows = []
    props = product_properties()
    fams = families(records)   # home family first, then the end uses' families (2026-10-09)
    for a in records.archetypes:
        k = a["archetype"]
        exs = ex_by_arch.get(k, [])
        src = sorted({e["source-id"] for e in exs}, key=lambda s: (records.rank(s), s))
        arows.append(dict(a, **props.get(a.get("product", ""), {}), **{
            "families": fams.get(k, a["family"]),
            "applies-to": applies_to(k, service),
            "end-uses": "; ".join(dict.fromkeys(s["end-use"] for s in service.get(k, []))),
            "n-examples": len(exs),
            # alphabetical by short name (modeller 2026-10-09; was by source rank)
            "sources": "; ".join(sorted((records.short(s) for s in src), key=str.lower)),
            "status": ("quantified" if k in with_data else
                       "estimated" if k in with_fill else
                       "not pooled" if k in with_facts else
                       "named" if exs else "gap")}))
    # cross-cutting service families first, in records/vocabulary order (heat supply,
    # power, machine drive, ...), then the sector families alphabetically by the
    # label a reader sees (modeller 2026-09-26, 2026-10-08)
    fam_rank = {f: ((0, i, "") if r.get("kind") == "service" else (1, 0, (r.get("label") or f).lower()))
                for i, (f, r) in enumerate(records.families.items())}
    from .bands import type_rank
    arows.sort(key=lambda r: (fam_rank.get(r["family"], (2, 0, r["family"])), type_rank(r), r["archetype"]))
    if not wide_only:
        write(outdir / "archetype.csv",
              IDENT + ["trl-basis", "description", "examples-named", "note"], arows)

    # ---- archetype-application.csv: the long view, every node served ---------
    app = []
    for a in arows:
        for s in service.get(a["archetype"], []):
            for n in hier.expand(s["branch"]):
                app.append({"archetype": a["archetype"], "family": a["family"],
                            "node": n, "annotation": s.get("end-use", ""),
                            "via": s["branch"] if "*" in s["branch"] else "",
                            "note": s.get("note", "")})
    if not wide_only:
        write(outdir / "archetype-application.csv",
              ["archetype", "family", "node", "annotation", "via", "note"], app)

    # ---- cims_hierarchy.csv and cims_hierarchy_technology.csv -----------------
    # cims_hierarchy.csv is the snapshot as the build used it. The technology
    # version keeps its row order, with `technology` as the second column: a node
    # is repeated once per archetype serving it; a node nothing serves appears
    # once with `technology` blank.
    by_node = defaultdict(list)
    for r in app:
        if r["archetype"] not in by_node[r["node"]]:
            by_node[r["node"]].append(r["archetype"])
    hrows = read(hier.path) if not wide_only else []
    hcols = [c for c in (list(hrows[0]) if hrows else ["branch"]) if c != "technology"]
    if not wide_only:
        write(outdir / "cims_hierarchy.csv", hcols, hrows)
    tech = []
    for h in hrows:
        b = (h.get("branch") or "").strip()
        if not b:
            continue
        for t in sorted(by_node.get(b, [])) or [""]:
            tech.append(dict(h, technology=t))
    if not wide_only:
        write(outdir / "cims_hierarchy_technology.csv", hcols[:1] + ["technology"] + hcols[1:], tech)

    # ---- the wide views ---------------------------------------------------------
    # Three views (modeller 2026-10-08/09), placed by pipeline/placement.py:
    #   wide-archetype                   one column set per parameter, the main view
    #   wide-carriers-species            specific energy by carrier and emissions by
    #                                    species, alphabetical (CO2-eq stays main)
    #   wide-secondary-parameter         every other target (CSV only, not in the
    #                                    workbook): values by stream or part
    # The CHP efficiency, the temperature range and the single-stream efficiency
    # are already rolled into the summaries (pipeline/rollin.py).
    by_arch = defaultdict(dict)
    pt, sunit = {}, defaultdict(set)
    for s in summaries:
        base = s["parameter"] + (f"_{s['target']}" if s.get("target") else "")
        by_arch[s["archetype"]][base] = s
        pt[base] = (s["parameter"], s.get("target", ""))
        sunit[base].add(s.get("unit", ""))
    fill_note = {}
    SHEET = {"main": "wide-archetype", "carriers": "wide-carriers-species",
             "secondary": "wide-secondary-parameter"}
    sheets = {v: defaultdict(dict) for v in SHEET.values()}
    for k, cells in by_arch.items():
        for b, s in cells.items():
            where = SHEET.get(placement(*pt[b]))
            if where:
                sheets[where][k][b] = s
    colmeta = {}

    def unit_of(b):
        p, t = pt.get(b) or colmeta.get(b, (b, ""))
        if t and placement(p, t) == "secondary":
            u = "; ".join(sorted(x for x in sunit.get(b, ()) if x))
            if p in ("capacity", "annual-output") and u:
                return f"{u} {t}" + (" per yr" if p == "annual-output" else "")
            return u or unit_label(p, t)
        if p == "annual-output":
            return "product-unit per yr"
        return unit_label(p, t)

    def note_of(b):
        p, t = pt.get(b) or colmeta.get(b, (b, ""))
        pdef = records.parameters.get(p, {})
        extra = {
            "efficiency": "On CHP archetypes (label says CHP) this column is the total CHP "
                          "efficiency, electricity plus useful heat over fuel in (efficiency-chp); "
                          "the electric and heat efficiencies are beside it.",
            "efficiency_unspecified": "CHP archetypes only: an efficiency the source gives without "
                                      "saying electric, heat or total. The main view's efficiency "
                                      "on these rows is the total CHP efficiency.",
            "efficiency_heat": "Heat out over energy in. On a single-output heat archetype it repeats "
                               "the efficiency column.",
            "efficiency_electricity": "Electricity out over energy in. On a single-output power "
                                      "archetype it repeats the efficiency column.",
            "efficiency-chp": "Non-CHP archetypes: a total heat-plus-power efficiency some sources give "
                              "(a boiler or turbine run in CHP mode).",
            "temperature-output": "Low and high also span the minimum and maximum operating "
                                  "temperatures sources give (temperature-min, temperature-max).",
        }.get(b, "")
        return " ".join(x for x in (
            pdef.get("definition", ""), f"Species or stream: {t}." if t else "", extra,
            "Central value: the median of three or more examples, otherwise the value from the "
            "highest-ranked source; low and high are the widest values any example gives.") if x)

    cap_rules = capacityunit.load()

    def emit(name, cells, ident, order):
        keys = sorted({b for c in cells.values() for b in c}, key=order)
        spread = {b for b in keys if any(c[b].get("low") for c in cells.values() if b in c)}
        cols = list(ident)
        if name == "wide-archetype":
            cols += ["external-conversions", "source-corrections", "filled"]
        units, groups, notes = {}, {c: "identity" for c in cols}, dict(fill_note)
        for b in keys:
            if b == "temperature-output" and "heat-tier" in cols:
                cols.remove("heat-tier")
                cols.append("heat-tier")
            extra = [b] + ([f"{b}_low", f"{b}_high"] if b in spread else []) + [f"{b}_n"]
            if name == "wide-archetype" and b == "capacity":
                cols.append("capacity-unit")
                groups["capacity-unit"] = records.parameters.get("capacity", {}).get("parameter-class", "")
                units["capacity-unit"] = ""
                notes["capacity-unit"] = ("The unit the capacity columns are in, chosen per archetype as the "
                                          "unit its industry rates plants in (records/reference/capacity-unit.csv). "
                                          "Not the product-unit: annual output and the per-capacity costs stay "
                                          "per product-unit.")
            cols += extra
            p = (pt.get(b) or colmeta.get(b, (b, "")))[0]
            for c in extra:
                units[c] = ("" if c.endswith("_n") else
                            "see capacity-unit" if name == "wide-archetype" and b == "capacity" else unit_of(b))
                groups[c] = records.parameters.get(p, {}).get("parameter-class", "")
            notes[b] = note_of(b)
        index = {c: i for i, c in enumerate(cols)}
        rows, flagged, graded = [], set(), {}
        for a in arows:
            if a["archetype"] not in with_data and not include_empty:
                continue
            row = dict(a)                  # family and equipment stay in the row for banding
            ext, filled, cor = [], [], []
            for b, s in cells.get(a["archetype"], {}).items():
                g = s.get("grade", "sourced")
                if g != "sourced":
                    filled.append((b, f"{b} {g}"))
                    graded.update({(a["archetype"], c): g for c in (b, f"{b}_low", f"{b}_high")})
                row[b], row[f"{b}_n"] = ("not applicable" if g == "not-applicable" else s["central"]), s["n"]
                if b in spread:
                    row[f"{b}_low"], row[f"{b}_high"] = s["low"], s["high"]
                if s.get("n-corrected"):
                    cor.append((b, f"{b} {s['n-corrected']}/{s['n']}"))
                if s.get("n-external"):
                    ext.append((b, f"{b} {s['n-external']}/{s['n']}"))
                    flagged |= {(a["archetype"], c) for c in (b, f"{b}_low", f"{b}_high")}
            if name == "wide-archetype":
                capacityunit.apply(cap_rules, row)
                row["external-conversions"] = "; ".join(t for _, t in sorted(ext, key=lambda x: index.get(x[0], 0)))
                row["source-corrections"] = "; ".join(t for _, t in sorted(cor, key=lambda x: index.get(x[0], 0)))
                row["filled"] = "; ".join(t for _, t in sorted(filled, key=lambda x: index.get(x[0], 0)))
            rows.append(row)
        return cols, rows, groups, units, notes, flagged, graded

    def by_param(b):
        p, t = pt.get(b) or colmeta.get(b, (b, ""))
        return (param_order.get(p, 99), t)

    fill_note.update(WIDE_NOTES)
    ident_main = [c for c in IDENT if c not in ("family", "equipment")]
    ident_side = ["archetype", "label", "product-unit", "product"]
    out = {}
    for name, ident, order in (("wide-archetype", ident_main, by_param),
                               ("wide-carriers-species", ident_side, lambda b: b),
                               ("wide-secondary-parameter", ident_side, by_param)):
        out[name] = emit(name, sheets[name], ident, order)
    for name, csvname in (("wide-archetype", "wide-archetype.csv"),
                          ("wide-carriers-species", "wide-archetype-carriers-species.csv"),
                          ("wide-secondary-parameter", "wide-archetype-secondary-parameter.csv")):
        cols, rows = out[name][0], out[name][1]
        write(outdir / csvname, cols, rows)
    write(outdir / "wide-archetype-columns.csv", ["sheet", "column", "group", "unit", "note"],
          [{"sheet": name, "column": c, "group": o[2].get(c, ""), "unit": o[3].get(c, ""),
            "note": o[4].get(c, "")} for name, o in out.items() for c in o[0]],
          quiet=True)

    # ---- wide-flow.csv: central values per commodity --------------------------
    fby = defaultdict(dict)
    fcols = set()
    for s in flow_summaries:
        c = ("in_" if s["direction"] == "input" else "out_") + s["commodity"]
        fby[s["archetype"]][c] = s["central"] or ""
        fby[s["archetype"]][c + "_n"] = s["n"]
        fcols.add(c)
    fcols = sorted(fcols, key=lambda c: (not c.startswith("in_"), c))
    fident = ["archetype", "label", "family", "equipment", "product-unit", "sources"]
    flow_cols = fident + [x for c in fcols for x in (c, c + "_n")]
    frows = []
    for a in arows:
        if a["archetype"] in fby:
            row = {c: a.get(c, "") for c in fident}
            row.update(fby[a["archetype"]])
            frows.append(row)
    if not wide_only:
        write(outdir / "wide-flow.csv", flow_cols, frows)
    funits = {c: ("" if c in fident or c.endswith("_n") else "per product-unit") for c in flow_cols}
    fgroups = {c: ("identity" if c in fident else "inputs" if c.startswith("in_") else "outputs")
               for c in flow_cols}
    return {"archetype": (IDENT + ["status"], arows),
            "wide": out,
            "wide-flow": (flow_cols, frows, fgroups, funits),
            "application": app}
