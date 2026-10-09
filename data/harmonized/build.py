"""Build the harmonized technology database. The one entry point.

    python data/harmonized/build.py            everything
    python data/harmonized/build.py --check    stop after the checks (no outputs)
    python data/harmonized/build.py --quantified-only
                                               the wide view lists only archetypes with
                                               pooled numbers (default: every archetype)

Stages (docs/pipeline.md):
  1. hierarchy   stamp records/cims_hierarchy.csv, report what changed, and hold
                 every path in the records to it
  2. records     load the archetypes and vocabularies and hold them to the rules
  3. extract     read every extraction as reported (layer 1 -> facts)
  4. clean       evaluate arithmetic, one spelling per unit, per-source record ids
  5. examples    attach each example to its archetype (records/source-example.csv)
  6. checks      the gate: any failure stops the build here
  7. normalise   every fact on its archetype's basis (currency, units, product)
  8. summarise   one value set per archetype and parameter (layer 3)
     fill        graded values for empty cells: identity, estimated, guess
                 (records/fill/)
  9. views       archetype, application and the wide views
 10. reports     source list, citation review, mapping review, docs/vocabulary.md
 11. workbook    the Excel workbook, last, from the outputs

Reads data/raw-data/ and data/harmonized/records/. Writes data/harmonized/output/
and docs/vocabulary.md, and appends new examples to records/source-example.csv.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import (assembly, captureenergy, captureshare, carriers, checks, correction, ukercsaving, currency, examples, extract,  # noqa: E402
                      bands, factoruse, facts, fill, hierarchy, normalise, placement, records, reports, rollin, rollup, sources,
                      summarise, views, wholeplant, workbook)
from pipeline.common import OUTPUT, write  # noqa: E402

FACT_COLS = ["record-id", "example-id", "archetype", "source-technology", "parameter", "target",
             "value", "value-min", "value-max", "unit", "value-norm", "value-min-norm",
             "value-max-norm", "unit-norm", "target-norm", "conversion", "heating-value",
             "conversion-class", "conversion-factors", "excluded", "set-aside", "correction", "duplicate-of", "whole-plant", "uncertainty-type",
             "value-type", "formula", "derived-from", "cost-basis", "capacity-basis", "currency",
             "discount-rate", "region", "year", "source-id", "source-file", "source-locator",
             "extraction-file", "via-source-id", "via-locator", "confidence", "status", "note"]
FLOW_COLS = ["record-id", "example-id", "archetype", "source-technology", "direction",
             "commodity", "value", "value-min", "value-max", "unit", "per-unit", "value-norm",
             "value-min-norm", "value-max-norm", "unit-norm", "excluded", "co-product",
             "value-type", "formula", "region", "year", "source-id", "source-file",
             "source-locator", "via-source-id", "status", "note"]
CONS_COLS = ["record-id", "example-id", "archetype", "source-technology", "constraint", "region",
             "year", "value", "unit", "constraint-basis", "value-min", "value-max", "value-type",
             "source-id", "source-file", "source-locator", "via-source-id", "status", "note"]
EX_COLS = ["example-id", "archetype", "mapping", "source-id", "source-technology", "process",
           "detail", "sector-reported", "end-use-reported", "step-reported",
           "service-unit-reported", "description", "trl", "trl-as-reported", "trl-scale",
           "state-of-development", "year-available", "extraction-file", "note"]
SUM_COLS = ["central", "low", "high", "n", "n-external", "n-corrected", "central-from", "external-factors",
            "sources", "examples"]
FILL_COLS = ["grade", "method", "rule-id", "inputs", "rationale"]


def main(argv) -> int:
    print("hierarchy")
    hier = hierarchy.Hierarchy()
    print(f"  {len(hier.nodes)} nodes, {len(hier.leaves)} leaves, sha256 {hier.digest}")
    print("records")
    rec = records.Records()
    print(f"  {len(rec.archetypes)} archetypes, {len(rec.service)} service links, "
          f"{len(rec.annotations)} annotations")
    linked = {s["archetype"] for s in rec.service}
    loose = [a["archetype"] for a in rec.archetypes if a["archetype"] not in linked]
    if loose:
        print(f"  {len(loose)} with no connection to the hierarchy: {', '.join(loose)}")
    print("extract")
    L = extract.load()
    for m in L.missing:
        print(f"  warning: {m} not found, skipped")
    stats = facts.clean(L.facts, L.flows, L.cons)
    print(f"  {len(L.examples)} examples, {len(L.facts)} parameter rows, {len(L.flows)} flow "
          f"rows, {len(L.cons)} constraint rows; " + ", ".join(f"{v} {k}" for k, v in stats.items()))
    print("examples")
    ex = examples.apply(L, rec)
    m = Counter(e["mapping"] for e in L.examples.values())
    print(f"  {m['mapped']} mapped, {m['none']} (none), {m['unmapped']} not yet mapped"
          + (f"; {len(ex['new'])} new rows appended to records/source-example.csv" if ex["new"] else ""))
    if ex["stale"]:
        print(f"  {len(ex['stale'])} rows in source-example.csv match no extraction: "
              + ", ".join(ex["stale"][:5]))

    wp = wholeplant.derive(L)
    print(f"  UKERC measures: {wp.get('whole-plant rows', 0)} whole-plant rows derived, "
          f"{wp.get('set aside', 0)} measure costs set aside for a host-plant cost")
    asm = assembly.derive(L)
    if asm:
        print(f"  assembled whole-plant costs: {asm.get('rows', 0)} rows derived, "
              f"{asm.get('checks', 0)} consistency checks against printed totals"
              + (f" ({asm['check mismatches']} differ)" if asm.get("check mismatches") else ""))
    cor = correction.apply(L)
    if cor:
        print(f"  source corrections: {cor.get('added', 0)} values added, {cor.get('replaced', 0)} "
              f"replaced, {cor.get('marked', 0)} already-corrected rows marked, "
              f"{cor.get('rebased', 0)} restated on the archetype's product "
              "(records/reference/source-correction.csv)")
    print("checks")
    fail = checks.run(rec, hier, L, ex)
    backlog = fail.pop("_backlog")
    if backlog:
        print(f"  basis backfill outstanding: {sum(backlog.values())} rows marked for review "
              f"({', '.join(f'{s} {n}' for s, n in backlog.most_common())})")
    if fail:
        for k, v in fail.items():
            print(f"\n  {k.upper()} ({len(v)}):")
            for x in v[:12]:
                print(f"      {x}")
            if len(v) > 12:
                print(f"      ... and {len(v) - 12} more")
        return 1
    print("  all checks passed")
    if "--check" in argv:
        return 0

    print("normalise")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stamp = hierarchy.stamp(hier)
    factors, skipped = currency.factors(L.facts + L.flows)
    if skipped:
        print(f"  no currency factor for {', '.join(skipped)}; those rows are not pooled")
    units = normalise.Units(factors)
    normalise.normalise(L.facts, L.examples, rec, units)
    normalise.normalise_flows(L.flows, rec, units, L.examples)
    ce = captureenergy.apply(L.facts, L.examples, rec)
    print(f"  capture energy on host plants: {ce.get('set aside', 0)} rows set aside, "
          f"{ce.get('derived per t CO2', 0)} restated per t CO2 on capture archetypes")
    us = ukercsaving.derive(L.facts, rec, summarise.summarise)
    correction.propagate(L.facts)
    ru = rollup.apply(L.facts, rec)
    print("  targets rolled into their base parameter: "
          + (", ".join(f"{k} {v}" for k, v in ru.items()) or "none"))
    print("  UKERC buckets: " + ", ".join(f"{k} {v}" for k, v in us.items()))
    pooled = [r for r in L.facts if r.get("value-norm") and not r.get("excluded")]
    cc = Counter(r.get("conversion-class") or "as reported" for r in pooled)
    print("  pooled parameter rows by conversion class: "
          + ", ".join(f"{k} {cc[k]}" for k in ["as reported"] + normalise.convert.CLASSES if cc[k]))
    print("summarise")
    psum = summarise.summarise(L.facts, rec, ("parameter", "target-norm"), L.examples)
    for r in psum:
        r["target"] = r.pop("target-norm")
    cs = carriers.apply(psum, L.facts, rec)
    print("  energy carriers: " + ", ".join(f"{k} {v}" for k, v in cs.items()))
    sh = captureshare.apply(psum, rec, L.facts)
    print("  share-to-capture: " + (", ".join(f"{k} {v}" for k, v in sh.items()) or "none derived"))
    fsum = summarise.summarise(L.flows, rec, ("direction", "commodity"), L.examples)
    print("fill")
    fst = fill.apply(psum, rec, normalise.target_unit, L.facts)
    bt = fst.pop("_backtest")
    print("  " + (", ".join(f"{k} {v}" for k, v in fst.items()) or "nothing to fill"))
    ri = rollin.apply(psum, rec)
    print("  roll-ins: " + ", ".join(f"{k} {v}" for k, v in ri.items()))
    for rid in dict.fromkeys(b["rule-id"] for b in bt):
        rs = [b for b in bt if b["rule-id"] == rid]
        near = sum(1 for b in rs if b["ratio"] and 0.75 <= float(b["ratio"]) <= 1.25)
        print(f"  back-test {rid}: {sum(b['inside'] == 'yes' for b in rs)}/{len(rs)} sourced "
              f"values inside the estimate's range, {near}/{len(rs)} within 25%")
    write(OUTPUT / "fill-backtest.csv", ["rule-id", "archetype", "parameter", "sourced", "estimate",
                                         "low", "high", "inside", "ratio", "inputs"], bt)
    write(OUTPUT / "example.csv", EX_COLS, sorted(L.examples.values(), key=lambda e: e["example-id"]))
    write(OUTPUT / "example-parameter.csv", FACT_COLS, L.facts)
    write(OUTPUT / "set-aside-host-cost.csv",
          ["archetype", "example-id", "record-id", "parameter", "value", "unit", "source-id",
           "via-source-id", "source-locator", "note"],
          sorted((r for r in L.facts if r.get("set-aside") == "needs-host-cost"),
                 key=lambda r: (r["archetype"], r["example-id"], r["record-id"])))
    # costs sources give on host-with-capture archetypes: capture cost, to move to
    # a co2-capture archetype (docs/sanity-check-list.csv)
    write(OUTPUT / "ccs-addon-cost.csv",
          ["archetype", "example-id", "record-id", "parameter", "value", "unit", "cost-basis",
           "source-id", "via-source-id", "source-locator", "note"],
          sorted((r for r in L.facts if r.get("set-aside") == "ccs-add-on"),
                 key=lambda r: (r["archetype"], r["example-id"], r["record-id"])))
    # energy sources give on host plants with capture: the capture plant's, set
    # aside and (where ccs-host-energy.csv maps it) restated per t CO2 captured
    write(OUTPUT / "ccs-addon-energy.csv",
          ["archetype", "example-id", "record-id", "parameter", "target", "value", "unit",
           "value-norm", "unit-norm", "source-id", "via-source-id", "source-locator", "note"],
          sorted((r for r in L.facts if r.get("set-aside") == captureenergy.SET_ASIDE),
                 key=lambda r: (r["archetype"], r["example-id"], r["record-id"])))
    # the worklist for establishing efficiency factors later
    sec = {}
    for r in L.facts:
        if r["parameter"] == "specific-energy-consumption" and r.get("value"):
            sec.setdefault(r["example-id"], f"{r['value']} {r['unit']}")
    aside = [dict(r, **{"fuel-per-unit": sec.get(r["example-id"], "")})
             for r in L.facts if r.get("set-aside") in ("needs-efficiency", "not-bridged")]
    write(OUTPUT / "set-aside-efficiency.csv",
          ["archetype", "example-id", "record-id", "parameter", "value", "unit",
           "fuel-per-unit", "set-aside", "excluded", "duplicate-of", "formula", "source-id",
           "via-source-id", "source-locator", "note"],
          sorted(aside, key=lambda r: (r["archetype"], r["example-id"], r["record-id"])))
    write(OUTPUT / "example-flow.csv", FLOW_COLS, L.flows)
    factoruse.write_outputs(L.facts, units.factors)
    write(OUTPUT / "example-constraint.csv", CONS_COLS, L.cons)
    order = {a["archetype"]: i for i, a in enumerate(rec.archetypes)}
    psum.sort(key=lambda r: (order.get(r["archetype"], 9999), r["parameter"], r["target"]))
    fsum.sort(key=lambda r: (order.get(r["archetype"], 9999), r["direction"], r["commodity"]))
    # secondary parameters (values by stream or part) have their own file
    # (modeller 2026-10-09); views still see every summary
    sec = [r for r in psum if placement.placement(r["parameter"], r["target"]) == "secondary"]
    main = [r for r in psum if placement.placement(r["parameter"], r["target"]) != "secondary"]
    write(OUTPUT / "archetype-parameter.csv",
          ["archetype", "parameter", "target", "unit"] + SUM_COLS + FILL_COLS, main)
    write(OUTPUT / "archetype-secondary-parameter.csv",
          ["archetype", "parameter", "target", "unit"] + SUM_COLS + FILL_COLS, sec)
    write(OUTPUT / "archetype-flow.csv",
          ["archetype", "direction", "commodity", "unit"] + SUM_COLS, fsum)
    nf = Counter(r["example-id"] for r in L.facts + L.flows + L.cons
                 if r.get("value") or r.get("value-min") or r.get("value-max"))
    for e in L.examples.values():
        e["n-facts"] = nf.get(e["example-id"], 0)
    print("views")
    v = views.build(rec, hier, L.examples, psum, fsum, include_empty="--quantified-only" not in argv)
    print("reports")
    srcs = sources.source_list(rec, L.examples, (L.facts, L.flows, L.cons))
    sources.citation_review(srcs)
    reports.mapping_review(rec, hier, L, {"rows": len(hier.nodes), "sha": hier.digest, **stamp},
                           v, ex)
    reports.vocabulary_md(rec, hier, v)
    print("  mapping-review.md, citation-review.md, docs/vocabulary.md")
    print("workbook")
    fam = {f: r["label"] for f, r in rec.families.items()}
    W = v["wide"]
    wcols, wrows = W["wide-archetype"][0], W["wide-archetype"][1]
    fcols, frows, fgroups, funits = v["wide-flow"]
    acols, arows = v["archetype"]
    fam_rank = {f: i for i, f in enumerate(rec.families)}
    src_band = []
    # band the source list in the same family order as the wide view (the main table)
    wide_order = list(dict.fromkeys(r.get("family", "") for r in wrows if r.get("family")))
    fam_order = wide_order + [f for f in rec.families if f not in wide_order]
    for f in fam_order + [""]:
        n0 = len(src_band)
        for r in sorted(srcs, key=lambda x: str(x.get("short-name", "")).lower()):
            fs = [x.strip() for x in str(r.get("families", "")).split(";") if x.strip()]
            if (f in fs) or (not f and not fs):
                src_band.append(dict(r, _band=f))
        if f and len(src_band) == n0:
            # keep the family band visible even when no source informs it yet
            src_band.append({"_band": f, "note": "no source informs this family yet"})
    banner = ("VIEW - generated by data/harmonized/build.py. Anything typed here is lost on "
              "the next build; edit data/harmonized/records/ instead.")
    print("  " + workbook.write_book(
        {"wide-archetype": W["wide-archetype"][:1] + (bands.expand(W["wide-archetype"][1], rec),)
                           + W["wide-archetype"][2:4] + ("_family", "_sub",
                            banner + " One row per archetype; costs and intensities are per "
                            "product-unit, so never compare them across families. Energy is on "
                            "a higher heating value. Shading: purple = sourced, but converted with a "
                            "factor from outside the source (see external-conversions); blue = "
                            "identity (calculated from the archetype's own values); orange = "
                            "estimated; red = guess (see filled). Unshaded = sourced as reported. "
                            "_low, _high and _n columns are grouped: use the + above a column to "
                            "show them. Bands: family, then end use in process order; an archetype "
                            "serving several end uses is repeated under each, in the family that "
                            "owns that end use (see the families column)."),
         "wide-carriers-species": W["wide-carriers-species"][:1]
                           + (bands.expand(W["wide-carriers-species"][1], rec),)
                           + W["wide-carriers-species"][2:4] + ("_family", "_sub",
                            banner + " Specific energy consumption by carrier and emissions by "
                            "species, per product-unit, alphabetical. The all-carrier total and "
                            "CO2-eq emissions are in wide-archetype."),
         "wide-flow": (fcols, frows, fgroups, funits, "family", "equipment", banner),
         "archetype": (acols, arows, {}, {}, "family", "equipment", banner),
         "source-list": (sources.COLS, src_band, {}, {}, "_band", "", banner)},
        {"archetype-parameter": (["archetype", "parameter", "target", "unit"] + SUM_COLS + FILL_COLS, main),
         "archetype-flow": (["archetype", "direction", "commodity", "unit"] + SUM_COLS, fsum),
         "example": (EX_COLS, sorted(L.examples.values(), key=lambda e: e["example-id"])),
         "example-parameter": (FACT_COLS, L.facts),
         "example-flow": (FLOW_COLS, L.flows),
         "example-constraint": (CONS_COLS, L.cons),
         "archetype-application": (["archetype", "family", "node", "annotation", "via", "note"],
                                   v["application"])},
        {**fam, "": "(not tied to one family)"},
        {k: o[4] for k, o in W.items() if k != "wide-secondary-parameter"},
        {k: o[5] for k, o in W.items() if k != "wide-secondary-parameter"},
        {k: o[6] for k, o in W.items() if k != "wide-secondary-parameter"},
        grouped={k for k in W if k != "wide-secondary-parameter"},
        band_notes=bands.FAMILY_NOTE))
    q = Counter(a["status"] for a in arows)
    print(f"\ndone: {len(arows)} archetypes ({q['quantified']} quantified, {q['named']} named, "
          f"{q['estimated']} estimated only, {q['not pooled']} with numbers none of which could be pooled, {q['gap']} gaps); wide view {len(wrows)} rows x {len(wcols)} columns "
          f"(carriers-species {len(W['wide-carriers-species'][0])}, secondary {len(W['wide-secondary-parameter'][0])} columns)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
