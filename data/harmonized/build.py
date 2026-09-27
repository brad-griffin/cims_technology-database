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

from pipeline import (assembly, checks, currency, examples, extract, factoruse, facts,  # noqa: E402
                      hierarchy, normalise, records, reports, sources, summarise, views,
                      wholeplant, workbook)
from pipeline.common import OUTPUT, write  # noqa: E402

FACT_COLS = ["record-id", "example-id", "archetype", "source-technology", "parameter", "target",
             "value", "value-min", "value-max", "unit", "value-norm", "value-min-norm",
             "value-max-norm", "unit-norm", "target-norm", "conversion", "heating-value",
             "conversion-class", "conversion-factors", "excluded", "set-aside", "duplicate-of", "whole-plant", "uncertainty-type",
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
SUM_COLS = ["central", "low", "high", "n", "n-external", "central-from", "external-factors",
            "sources", "examples"]


def main(argv) -> int:
    print("hierarchy")
    hier = hierarchy.Hierarchy()
    print(f"  {len(hier.nodes)} nodes, {len(hier.leaves)} leaves, sha256 {hier.digest}")
    print("records")
    rec = records.Records()
    print(f"  {len(rec.archetypes)} archetypes, {len(rec.service)} service links, "
          f"{len(rec.annotations)} annotations")
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
    pooled = [r for r in L.facts if r.get("value-norm") and not r.get("excluded")]
    cc = Counter(r.get("conversion-class") or "as reported" for r in pooled)
    print("  pooled parameter rows by conversion class: "
          + ", ".join(f"{k} {cc[k]}" for k in ["as reported"] + normalise.convert.CLASSES if cc[k]))
    print("summarise")
    psum = summarise.summarise(L.facts, rec, ("parameter", "target-norm"), L.examples)
    for r in psum:
        r["target"] = r.pop("target-norm")
    fsum = summarise.summarise(L.flows, rec, ("direction", "commodity"), L.examples)
    write(OUTPUT / "example.csv", EX_COLS, sorted(L.examples.values(), key=lambda e: e["example-id"]))
    write(OUTPUT / "example-parameter.csv", FACT_COLS, L.facts)
    write(OUTPUT / "set-aside-host-cost.csv",
          ["archetype", "example-id", "record-id", "parameter", "value", "unit", "source-id",
           "via-source-id", "source-locator", "note"],
          sorted((r for r in L.facts if r.get("set-aside") == "needs-host-cost"),
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
    write(OUTPUT / "archetype-parameter.csv",
          ["archetype", "parameter", "target", "unit"] + SUM_COLS, psum)
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
    wcols, wrows, wgroups, wunits = v["wide-archetype"]
    fcols, frows, fgroups, funits = v["wide-flow"]
    acols, arows = v["archetype"]
    fam_rank = {f: i for i, f in enumerate(rec.families)}
    src_band = []
    for f in list(rec.families) + [""]:
        for r in sorted(srcs, key=lambda x: str(x.get("short-name", "")).lower()):
            fs = [x.strip() for x in str(r.get("families", "")).split(";") if x.strip()]
            if (f in fs) or (not f and not fs):
                src_band.append(dict(r, _band=f))
    banner = ("VIEW - generated by data/harmonized/build.py. Anything typed here is lost on "
              "the next build; edit data/harmonized/records/ instead.")
    print("  " + workbook.write_book(
        {"wide-archetype": (wcols, wrows, wgroups, wunits, "family", "equipment",
                            banner + " One row per archetype; costs and intensities are per "
                            "product-unit, so never compare them across families. Energy is on "
                            "a higher heating value. Italic values rest on a conversion factor "
                            "from outside the source (see external-conversions)."),
         "wide-flow": (fcols, frows, fgroups, funits, "family", "equipment", banner),
         "archetype": (acols, arows, {}, {}, "family", "equipment", banner),
         "source-list": (sources.COLS, src_band, {}, {}, "_band", "", banner)},
        {"archetype-parameter": (["archetype", "parameter", "target", "unit"] + SUM_COLS, psum),
         "archetype-flow": (["archetype", "direction", "commodity", "unit"] + SUM_COLS, fsum),
         "example": (EX_COLS, sorted(L.examples.values(), key=lambda e: e["example-id"])),
         "example-parameter": (FACT_COLS, L.facts),
         "example-flow": (FLOW_COLS, L.flows),
         "example-constraint": (CONS_COLS, L.cons),
         "archetype-application": (["archetype", "family", "node", "annotation", "via", "note"],
                                   v["application"])},
        {**fam, "": "(not tied to one family)"},
        {"wide-archetype": v["wide-archetype-notes"]},
        {"wide-archetype": v["flagged"]}))
    q = Counter(a["status"] for a in arows)
    print(f"\ndone: {len(arows)} archetypes ({q['quantified']} quantified, {q['named']} named, "
          f"{q['not pooled']} with numbers none of which could be pooled, {q['gap']} gaps); wide view {len(wrows)} rows x {len(wcols)} columns")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
