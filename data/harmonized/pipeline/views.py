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

from collections import defaultdict

from .common import OUTPUT, read, split_list, write
from .hierarchy import Hierarchy
from .normalise import target_unit

IDENT = ["archetype", "label", "family", "end-uses", "equipment", "discriminator", "modifiers",
         "type", "carriers", "heat-tier", "applies-to", "trl", "product-unit", "product",
         "n-examples", "status", "sources"]


def unit_label(param: str, target: str) -> str:
    u = target_unit(param, "PU", "")
    if "PU" in u:
        return u.replace("PU-per-yr", "(product-unit per yr)").replace("PU", "product-unit") \
                .replace("kPU/yr", "kt/yr (or MW when product-unit is GJ)")
    return u


NO_CONNECTION = "no connection"


def applies_to(key, service):
    """The nodes an archetype serves, or NO_CONNECTION when it serves none."""
    return "; ".join(Hierarchy.short(s["branch"]) for s in service.get(key, [])) or NO_CONNECTION


def build(records, hier, examples, summaries, flow_summaries, include_empty=True):
    """Also returns `flagged`: the (archetype, column) cells of the wide view whose
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
    with_data = ({s["archetype"] for s in summaries if s.get("grade", "sourced") == "sourced"}
                 | {s["archetype"] for s in flow_summaries})
    with_fill = {s["archetype"] for s in summaries if s.get("grade", "sourced") != "sourced"}
    with_facts = {e["archetype"] for e in examples.values() if e.get("n-facts")}
    arows = []
    for a in records.archetypes:
        k = a["archetype"]
        exs = ex_by_arch.get(k, [])
        src = sorted({e["source-id"] for e in exs}, key=lambda s: (records.rank(s), s))
        arows.append(dict(a, **{
            "applies-to": applies_to(k, service),
            "end-uses": "; ".join(dict.fromkeys(s["end-use"] for s in service.get(k, []))),
            "n-examples": len(exs),
            "sources": "; ".join(records.short(s) for s in src),
            "status": ("quantified" if k in with_data else
                       "estimated" if k in with_fill else
                       "not pooled" if k in with_facts else
                       "named" if exs else "gap")}))
    # families alphabetically by the label a reader sees (modeller, 2026-09-26)
    fam_label = {f: (r.get("label") or f).lower() for f, r in records.families.items()}
    arows.sort(key=lambda r: (fam_label.get(r["family"], r["family"]), r["equipment"], r["archetype"]))
    write(OUTPUT / "archetype.csv",
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
    write(OUTPUT / "archetype-application.csv",
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
    hrows = read(hier.path)
    hcols = [c for c in (list(hrows[0]) if hrows else ["branch"]) if c != "technology"]
    write(OUTPUT / "cims_hierarchy.csv", hcols, hrows)
    tech = []
    for h in hrows:
        b = (h.get("branch") or "").strip()
        if not b:
            continue
        for t in sorted(by_node.get(b, [])) or [""]:
            tech.append(dict(h, technology=t))
    write(OUTPUT / "cims_hierarchy_technology.csv", hcols[:1] + ["technology"] + hcols[1:], tech)

    # ---- wide-archetype.csv -----------------------------------------------------
    by_arch = defaultdict(dict)
    colkeys = set()
    for s in summaries:
        base = s["parameter"] + (f"_{s['target']}" if s.get("target") else "")
        by_arch[s["archetype"]][base] = s
        colkeys.add((s["parameter"], s.get("target", ""), base))
    colkeys = sorted(colkeys, key=lambda x: (param_order.get(x[0], 99), x[1]))
    spread = {b for (_, _, b) in colkeys
              if any(by_arch[a][b]["low"] for a in by_arch if b in by_arch[a])}
    cols, units, groups, notes = list(IDENT) + ["external-conversions", "filled"], {}, {c: "identity" for c in IDENT}, {}
    groups["external-conversions"] = groups["filled"] = "identity"
    notes["filled"] = (
        "Parameters with no sourced value, filled by the fill step and graded: identity "
        "(calculated from this archetype's own values), estimated (from other archetypes or a "
        "class rule) or guess (a judgement). Shaded in the workbook; their _n is 0. Rule, "
        "inputs and rationale: archetype-parameter.csv (grade, method, rule-id, inputs, "
        "rationale); rules in records/fill/.")
    notes["external-conversions"] = (
        "Parameters whose pooled value rests on a conversion factor from outside the source "
        "(a heating value, a density, a process ratio, a pooled efficiency or an assumption), "
        "as examples so converted / examples pooled. Those values are shaded purple in the "
        "workbook. Which factors: archetype-parameter.csv (external-factors); how each example "
        "was converted: example-parameter.csv (conversion, conversion-class, "
        "conversion-factors).")
    for p, t, b in colkeys:
        extra = [b] + ([f"{b}_low", f"{b}_high"] if b in spread else []) + [f"{b}_n"]
        cols += extra
        for c in extra:
            units[c] = "" if c.endswith("_n") else unit_label(p, t)
            groups[c] = records.parameters.get(p, {}).get("parameter-class", "")
        # the parameter's note goes on its central column only, not on _low/_high/_n
        pdef = records.parameters.get(p, {})
        notes[b] = " ".join(x for x in (
            pdef.get("definition", ""),
            f"Species: {t}." if t else "",
            "Central value: the median of three or more examples, otherwise the value from the "
            "highest-ranked source; low and high are the widest values any example gives.") if x)
    wide, flagged, graded = [], set(), {}
    for a in arows:
        if a["archetype"] not in with_data and not include_empty:
            continue
        row = {c: a.get(c, "") for c in IDENT}
        ext, filled = [], []
        for b, s in by_arch.get(a["archetype"], {}).items():
            g = s.get("grade", "sourced")
            if g != "sourced":
                filled.append((b, f"{b} {g}"))
                graded.update({(a["archetype"], c): g for c in (b, f"{b}_low", f"{b}_high")})
            row[b], row[f"{b}_n"] = s["central"], s["n"]
            if b in spread:
                row[f"{b}_low"], row[f"{b}_high"] = s["low"], s["high"]
            if s.get("n-external"):
                ext.append((b, f"{b} {s['n-external']}/{s['n']}"))
                flagged |= {(a["archetype"], c) for c in (b, f"{b}_low", f"{b}_high")}
        order = {c: i for i, c in enumerate(cols)}
        row["external-conversions"] = "; ".join(t for _, t in sorted(ext, key=lambda x: order.get(x[0], 0)))
        row["filled"] = "; ".join(t for _, t in sorted(filled, key=lambda x: order.get(x[0], 0)))
        wide.append(row)
    write(OUTPUT / "wide-archetype.csv", cols, wide)
    write(OUTPUT / "wide-archetype-columns.csv", ["column", "group", "unit", "note"],
          [{"column": c, "group": groups.get(c, ""), "unit": units.get(c, ""),
            "note": notes.get(c, "")} for c in cols],
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
    write(OUTPUT / "wide-flow.csv", flow_cols, frows)
    funits = {c: ("" if c in fident or c.endswith("_n") else "per product-unit") for c in flow_cols}
    fgroups = {c: ("identity" if c in fident else "inputs" if c.startswith("in_") else "outputs")
               for c in flow_cols}
    return {"archetype": (IDENT + ["status"], arows),
            "wide-archetype": (cols, wide, groups, units),
            "wide-archetype-notes": notes,
            "flagged": flagged,
            "graded": graded,
            "wide-flow": (flow_cols, frows, fgroups, funits),
            "application": app}
