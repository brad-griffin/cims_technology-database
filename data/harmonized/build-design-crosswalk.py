"""Crosswalk the harmonized layer onto the design tables, and report it.

The design tables -- design/sector-end-use-table.csv (13 sectors plus
cross-sector, 91 end uses as of 2026-09-16) and design/end-use-technology-table.csv
(504 rows) -- become the controlled vocabulary of the
harmonized layer, in place of the roster the sources grew.  This script works
out where every existing service node, application and roster technology lands
in that vocabulary and writes it out.

IT WRITES NOTHING INTO THE HARMONIZED TABLES.  Output is
design-crosswalk-review.md plus two crosswalk CSVs, for review before any
adoption pass applies them (the user, 2026-09-14).

Run from the repo root:  python data/harmonized/build-design-crosswalk.py
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import design_names as dn
import design_names_hand as hand
import design_crosswalk as cw
import aggregate

ROOT = HERE.parent.parent


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def wr(path: Path, cols: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"  {path.name:34s} {len(rows):5d} rows")


# --- end-use resolution --------------------------------------------------
def step_rule(sector: str, step: str) -> str | None:
    if (sector, step) in cw.STEP_END_USE:
        return cw.STEP_END_USE[(sector, step)]
    for (s, pat), eu in cw.STEP_END_USE.items():
        if s == sector and pat.startswith("*") and step.endswith(pat[1:]):
            return eu
    return None


def resolve(sector: str, end_use: str, step: str, tech: str,
            equipment: str, variant: str) -> tuple[str, list[str], str]:
    """-> (design sector, design end uses, the rule that decided it)."""
    if tech in cw.TECH_END_USE:
        s, eu = cw.TECH_END_USE[tech]
        return s, [eu], "technology rule"
    # a separable steam system is cross-sector heat whatever sector raises it
    if end_use == "steam-and-hot-water":
        if variant == "chp":
            # CHP is a technology supplying the heat bands now, not an end use
            return "cross-sector", list(cw.BOTH_HEAT_BANDS), "chp supplies the bands"
        if equipment in cw.POWER_ONLY_EQUIPMENT:
            return "cross-sector", ["on-site-power-generation"], \
                "prime mover, no heat recovery"
        return "cross-sector", list(cw.BOTH_HEAT_BANDS), "steam serves both bands"
    # the step has its say before the generic services, so that mine
    # ventilation and mine air heating stay a mining end use
    if step:
        eu = step_rule(sector, step)
        if eu:
            return sector, [eu], "process step"
    # facility services, machine drive and refrigeration are cross-sector end
    # uses in the design table whatever sector the source reported them for --
    # the CIMS rows still carry their own sector, R2 having not run on them
    if end_use == "facility-services":
        return "cross-sector", [cw.FACILITY_SPLIT.get(equipment, "space-heating")], \
            "facility split by equipment"
    if end_use == "machine-drive":
        # the six MECS categories; the device decides which
        return "cross-sector", cw.MACHINE_DRIVE.get(equipment,
                                                    cw.MACHINE_DRIVE_DEFAULT), \
            "machine drive, MECS category"
    if end_use == "refrigeration-and-cooling":
        s, eu = cw.REFRIGERATION_END_USE
        return s, [eu], "refrigeration is a food and beverage end use"
    if end_use == "material-conversion" and equipment in cw.RNG_EQUIPMENT:
        s, eu = cw.RNG_END_USE
        return s, [eu], "biogas is a biofuels product"
    if sector == "petroleum-refining" and step in cw.REFINING_HEAT_GRADE:
        return "cross-sector", [cw.REFINING_HEAT_GRADE[step]], "refinery heat grade"
    # CIMS models a fuel blend and a hydrogen supply as services of their own
    if step == "methane-blend":
        s, eu = cw.RNG_END_USE
        return s, [eu], "fuel blend is renewable natural gas"
    if step == "hydrogen":
        s, eu = cw.HYDROGEN_BY_SECTOR.get(sector, cw.HYDROGEN_DEFAULT)
        return s, [eu], "hydrogen production, by host sector"
    if step == "cryogenics" and sector in cw.OXYGEN_BY_SECTOR:
        s, eu = cw.OXYGEN_BY_SECTOR[sector]
        return s, [eu], "oxygen supply, by sector"
    if step in cw.STEP_TO_CROSS_SECTOR:
        return "cross-sector", [cw.STEP_TO_CROSS_SECTOR[step]], "step moves cross-sector"
    if sector == "cross-sector" and end_use == "material-conversion":
        if equipment == "fuel-cell":
            return sector, ["on-site-power-generation"], "a fuel cell consumes hydrogen"
        if equipment in cw.CROSS_SECTOR_HYDROGEN:
            s, eu = cw.HYDROGEN_DEFAULT
            return s, [eu], "hydrogen production, no host sector"
    if sector == "chemicals" and end_use == "material-conversion":
        eu = cw.CHEMICALS_CONVERSION.get(equipment, "other-chemicals")
        return sector, [eu], "chemicals conversion by equipment"
    # After the sector rules: a reformer, electrolyzer or gasifier the sector
    # does not claim is hydrogen production -- on site where the host sector has
    # an end use for it, and the merchant hydrogen sector otherwise.
    if end_use == "material-conversion" and equipment in cw.HYDROGEN_SUPPLY_EQUIPMENT:
        s, eu = cw.HYDROGEN_BY_SECTOR.get(sector, cw.HYDROGEN_DEFAULT)
        return s, [eu], "hydrogen production, by host sector"
    key = (sector, end_use)
    if key in cw.EQUIPMENT_SPLIT:
        members, hit, miss = cw.EQUIPMENT_SPLIT[key]
        return sector, [hit if equipment in members else miss], "split by equipment"
    if key in cw.EU_END_USE:
        return sector, [cw.EU_END_USE[key]], "end use"
    return sector, [], "unmapped"


def main() -> int:
    aggregate._VOCAB_PATH[0] = HERE / "vocabulary.csv"
    seu = rd(dn.SEU)
    tt = rd(dn.TECHTABLE)
    vocab = dn.vocabularies()
    names = dn.build_names(tt, vocab, hand.EQUIPMENT_BY_LABEL,
                           hand.MERGE_LABEL, hand.HAND_NAME)

    tech = rd(HERE / "technology.csv")
    apps = rd(HERE / "technology-application.csv")
    cims = rd(HERE / "cims-map.csv")
    facts = {n: rd(HERE / f"tech-{n}.csv") for n in ("parameter", "flow", "constraint")}

    equip = {r["technology"]: r.get("equipment", "") for r in tech}
    variant = {r["technology"]: r.get("variant", "") for r in tech}
    carrier = {r["technology"]: r.get("energy-carrier", "") for r in tech}
    status = {r["technology"]: r.get("status", "") for r in tech}
    factcount = collections.Counter()
    for rows in facts.values():
        for r in rows:
            factcount[r.get("technology", "")] += 1


    # design tables, indexed
    design_eu = {(r["sector"], r["end-use"]): r for r in seu}
    label_rows = collections.defaultdict(list)
    for r in tt:
        label_rows[hand.MERGE_LABEL.get(r["technology"], r["technology"])].append(r)
    by_name = {d["name"]: lab for lab, d in names.items()}
    placements = collections.defaultdict(set)       # design name -> {(sector, end use)}
    for lab, d in names.items():
        for r in label_rows[lab]:
            placements[d["name"]].add((r["sector"], r["end-use"]))

    # ---- 1. applications onto design end uses --------------------------
    # Two inputs.  The application rows carry everything the extractions and
    # the design-doc roster placed.  The CIMS rows are read again from
    # cims-map.csv because R2 merged the generic end uses onto cross-sector
    # and dropped the process step, and the design table's oil-and-gas end
    # uses need that step back (LNG compression against pipeline compression).
    seen, app_rows, unmapped_apps = {}, [], []
    reach = collections.defaultdict(set)            # roster tech -> design (sector, eu)

    def place(t, s, eus, rule, origin, frm):
        if not eus:
            unmapped_apps.append({**frm, "technology": t})
            return
        for eu in eus:
            if (s, eu) not in design_eu:
                unmapped_apps.append({**frm, "technology": t})
                continue
            reach[t].add((s, eu))
            key = (t, s, eu)
            if key in seen:
                row = seen[key]
                if origin not in row["origin"]:
                    row["origin"] += "; " + origin
                if rule not in row["rule"]:
                    row["rule"] += "; " + rule
                continue
            row = {"technology": t, "design-sector": s, "design-end-use": eu,
                   "rule": rule, "origin": origin, **frm}
            seen[key] = row
            app_rows.append(row)

    for a in apps:
        t = a["technology"]
        s, eus, rule = resolve(a["sector"], a["end-use"], a["process-step"], t,
                               equip.get(t, ""), variant.get(t, ""))
        place(t, s, eus, rule, "application",
              {"from-sector": a["sector"], "from-end-use": a["end-use"],
               "from-process-step": a["process-step"]})

    for r in cims:
        if r["action"] not in {"retain", "merge", "merge-review"} or not r["sector"]:
            continue
        t = aggregate.canon_tech(r["technology"])
        step = r["process-step"]
        hit = cw.branch_rule(r["cims-branch"])
        if hit and step not in cw.CIMS_STEP_TO_HEAT_BANDS:
            s, eu = hit
            eus, rule = [eu], "CIMS branch"
        elif step in cw.CIMS_STEP_TO_HEAT_BANDS:
            s, eus, rule = resolve(r["sector"], "steam-and-hot-water", "", t,
                                   equip.get(t, ""), variant.get(t, ""))
            rule = "CIMS steam service; " + rule
        else:
            s, eus, rule = resolve(r["sector"], r["end-use"], step, t,
                                   equip.get(t, ""), variant.get(t, ""))
        place(t, s, eus, rule, "cims-map",
              {"from-sector": r["sector"], "from-end-use": r["end-use"],
               "from-process-step": step})

    # ---- 2. roster technologies onto design technologies ---------------
    # the design table's own roster-match column first
    claimed = collections.defaultdict(list)
    for lab, d in names.items():
        for r in label_rows[lab]:
            for m in r["roster-match"].replace(",", ";").split(";"):
                m = m.strip()
                if m:
                    claimed[m].append(d["name"])

    missing = [n for n, _ in cw.HAND_TECH.values() if n not in by_name]
    assert not missing, f"HAND_TECH names not in the design table: {missing}"
    tech_rows, orphans = [], []
    for r in tech:
        t = r["technology"]
        cands, how, note_hand = [], "", ""
        if t in claimed:
            cands, how = sorted(set(claimed[t])), "roster-match"
        if len(cands) > 1 and reach.get(t):
            narrowed = [c for c in cands
                        if placements[c] & reach[t]]
            if narrowed:
                cands, how = narrowed, "roster-match, narrowed by end use"
        # `ccs` is in BOTH the carrier and the variant vocabulary in section
        # 6.2, so split_name files it in whichever component it reads first:
        # 14 of the 36 `_ccs` names carry it as the carrier.  Read it back.
        v = variant.get(t, "") or (
            carrier.get(t, "") if carrier.get(t, "") in vocab.get("variant", ()) else "")

        def prefer(pool):
            """Within a pool, the row that matches the roster variant, else the
            conventional row, else the pool."""
            pref = []
            if v.startswith("efficiency-") and v != "efficiency-base":
                pref = [n for n in pool
                        if any(x["type"] == "efficient variant"
                               for x in label_rows[by_name[n]])]
                # a bucket row belongs to one device, so another device's bucket
                # is never the answer here: a pump's moderate bucket is the
                # premium motor and the variable-speed drive, not the gas-turbine
                # drive bucket that happens to sort first
                own = equip.get(t, "")
                pref = [n for n in pref
                        if "_efficiency-" not in n or n.rsplit("_", 1)[0] == own]
                same = [n for n in pref if n.split("_", 1)[0] == own]
                pref = same or pref
            elif v:
                pref = [n for n in pool if v in n]
            if not pref:
                pref = [n for n in pool
                        if any(x["type"] == "conventional"
                               for x in label_rows[by_name[n]])]
            return sorted(pref or pool)

        def strict(pool):
            """Only a row that matches the roster variant or is the conventional
            one; otherwise nothing, so the end use gets its say."""
            if v.startswith("efficiency-") and v != "efficiency-base":
                hit = [n for n in pool if any(x["type"] == "efficient variant"
                                              for x in label_rows[by_name[n]])]
            elif v and not v.startswith("efficiency-"):
                hit = [n for n in pool if v in n]
            else:
                hit = []
            return sorted(hit or [n for n in pool
                                  if any(x["type"] == "conventional"
                                         for x in label_rows[by_name[n]])])

        if not cands and v.startswith("efficiency-") and v != "efficiency-base":
            # the design table now carries `<equipment>_efficiency-moderate` and
            # `_efficiency-strong` rows; a roster bucket belongs on its own
            # bucket, and on the one for its own device where there is one
            same = [n for n in by_name if n.endswith("_" + v)
                    and n.rsplit("_", 1)[0] == equip.get(t, "")
                    and placements[n] & reach.get(t, set())]
            if same:
                cands, how = sorted(same), "efficiency bucket"
        if not cands and t in cw.HAND_TECH:
            n, note_hand = cw.HAND_TECH[t]
            cands, how = [n], "hand map"
        if not cands:
            eq = equip.get(t, "")
            pool = [n for n, lab in by_name.items()
                    if names[lab]["equipment"] == eq] if eq else []
            here = [n for n in pool if placements[n] & reach.get(t, set())]
            # Staying in the right end use beats matching the device: a wet
            # cement kiln belongs on the conventional clinker row, not on the
            # one other design row that happens to be spelled `kiln`.
            eu_pool = [n for n in by_name if placements[n] & reach.get(t, set())]
            if strict(here):
                cands, how = strict(here), "equipment, same end use"
            elif eu_pool:
                cands, how = prefer(eu_pool), "end use, conventional row"
            elif here:
                cands, how = sorted(here), "equipment, same end use"
            elif pool:
                cands, how = prefer(pool), "equipment, any end use"
        note = note_hand
        if not cands:
            orphans.append(r)
            continue
        chosen = cands[0]
        types = {x["type"] for x in label_rows[by_name[chosen]]}

        def add(base, extra):
            if not base:
                return extra
            return base + ("" if base.endswith((".", ";")) else ".") + " " + extra

        if v == "ccs" and not any(k in chosen for k in ("ccs", "oxy-fuel", "capture")):
            note = add(note,
                "carries ccs; the design table holds capture as its own end use "
                "(co2-capture-concentrated / -diffuse), so the fold keeps the "
                "device and the capture moves")
        # efficiency-base is the incumbent with no measures applied, so landing
        # it on the conventional row is right, not a loss
        if v.startswith("efficiency-") and v != "efficiency-base" \
                and "efficient variant" not in types:
            note = add(note,
                f"the {v} bucket folds onto a {'/'.join(sorted(types))} row; the "
                "design table has no efficient variant for this device")
        tech_rows.append({"roster-technology": t, "design-technology": chosen,
                          "note": note,
                          "design-label": by_name[chosen],
                          "equipment": equip.get(t, ""), "energy-carrier": carrier.get(t, ""),
                          "variant": variant.get(t, ""), "status": status.get(t, ""),
                          "fact-rows": factcount[t], "matched-by": how,
                          "other-candidates": "; ".join(cands[1:])})
    return write_review(seu, tt, names, label_rows, placements, app_rows,
                        unmapped_apps, tech_rows, orphans, tech, factcount,
                        vocab, apps, design_eu, cims)


def cims_branch_rows(cell: str, cims: list[dict]) -> tuple[list[dict], list[str]]:
    """The cims-map rows sitting on the branches a design row names.

    Since 2026-09-16 the design table writes CIMS services as paths in
    design/cims_hierarchy.csv (lower-case, hyphenated,
    `product`/`service` levels), with `{a, b}` alternatives and `(part)` /
    `(proposed)` tags; cims-map.csv still carries the model-input spelling.
    The two are matched loosely: on the last two path segments, slugged."""
    def slug(s: str) -> str:
        return re.sub(r"[^a-z0-9.]+", "-", s.lower()).strip("-")
    branches, hits = [], []
    for part in cell.split(";"):
        part = re.split(r"\s*->\s*", part.strip())[0]
        part = re.sub(r"\s*\(.*?\)", "", part)
        if not part or part.lower().startswith("none"):
            continue
        branches.append(part)
        m = re.match(r"^(.*?)\{(.*?)\}(.*)$", part)
        expanded = ([m.group(1) + x.strip() + m.group(3) for x in m.group(2).split(",")]
                    if m else [part])
        for p in expanded:
            segs = slug(p).split(".")
            tail = ".".join(segs[-2:])
            for r in cims:
                b = slug(r["cims-branch"])
                if b == tail or b.endswith("." + tail):
                    hits.append(r)
    return hits, branches


def write_review(seu, tt, names, label_rows, placements, app_rows, unmapped_apps,
                 tech_rows, orphans, tech, factcount, vocab, apps, design_eu,
                 cims) -> int:
    ccs_named = sum(1 for r in tech if r["technology"].endswith("_ccs"))
    ccs_as_carrier = sum(1 for r in tech if r["technology"].endswith("_ccs")
                         and r.get("energy-carrier") == "ccs")
    mapped = {r["roster-technology"] for r in tech_rows}
    landed = collections.Counter((r["design-sector"], r["design-end-use"])
                                 for r in app_rows if r["design-end-use"])
    filled = {r["design-technology"] for r in tech_rows}
    new_equipment = sorted({names[l]["equipment"] for l in names
                            if names[l]["equipment"] not in vocab.get("equipment", ())})
    new_disc = sorted({names[l]["discriminator"] for l in names
                       if names[l]["discriminator"]
                       and names[l]["discriminator"] not in vocab.get("variant", ())
                       and names[l]["discriminator"] not in vocab.get("energy-carrier", ())})

    wr(HERE / "design-crosswalk-technology.csv",
       ["roster-technology", "design-technology", "design-label", "equipment",
        "energy-carrier", "variant", "status", "fact-rows", "matched-by",
        "other-candidates", "note"], tech_rows)
    wr(HERE / "design-crosswalk-application.csv",
       ["technology", "from-sector", "from-end-use", "from-process-step",
        "design-sector", "design-end-use", "rule", "origin"], app_rows)

    out = []
    A = out.append
    A("# Adopting the design tables as the harmonized vocabulary")
    A("")
    A("Generated by `build-design-crosswalk.py`. **Nothing in `data/harmonized/` "
      "has been changed.** This is the crosswalk an adoption pass would apply, "
      "written out for review first (the user, 2026-09-14).")
    A("")
    A("## What changes")
    A("")
    A(f"| | now | design |")
    A("|---|---:|---:|")
    A(f"| Sectors | 11 | {len({r['sector'] for r in seu})} |")
    A(f"| End uses | 12 global | {len(seu)} sector-scoped |")
    A(f"| Technologies | {len(tech)} | {len(names)} |")
    A(f"| Applications | {len(apps)} | {len(app_rows)} |")
    A("")
    A("The sectors gained are `biofuels` and `oil-and-gas`; the end uses become "
      "sector-scoped, so the cross-sector heat bands supply the sector end uses "
      "rather than standing beside them, and CO2 capture splits three ways.")
    A("")
    A("## Coverage")
    A("")
    A(f"- **{len(mapped)} of {len(tech)}** roster technologies land on a design "
      f"technology; {len(orphans)} do not.")
    A(f"- **{len(filled)} of {len(names)}** design technologies receive at least one "
      f"roster technology. The other {len(names) - len(filled)} are the gap list: "
      "named in the design table, no data held.")
    A(f"- **{len(landed)} of {len(seu)}** design end uses receive at least one "
      f"application.")
    A(f"- {sum(factcount[o['technology']] for o in orphans)} fact rows sit on the "
      f"orphans, out of {sum(factcount.values())}.")
    A("")
    if orphans:
        A("### Orphans -- no design technology")
        A("")
        A("| roster technology | equipment | variant | status | fact rows |")
        A("|---|---|---|---|---:|")
        for o in sorted(orphans, key=lambda r: -factcount[r["technology"]]):
            A(f"| `{o['technology']}` | {o.get('equipment','')} | "
              f"{o.get('variant','')} | {o.get('status','')} | "
              f"{factcount[o['technology']]} |")
        A("")
    A("## Design end uses with nothing in them")
    A("")
    A("What CIMS holds on the branches each one names, and what the mapper did "
      "with those rows. A `review` or `fuel-node` row is not in the harmonized "
      "layer at all, so these end uses cannot be filled by re-labelling what is "
      "already there -- `build-cims-map.py` has to place them first.")
    A("")
    A("| design end use | CIMS branches named | rows | what the mapper did |")
    A("|---|---|---:|---|")
    for r in seu:
        if (r["sector"], r["end-use"]) in landed:
            continue
        hits, branches = cims_branch_rows(r["cims-services"], cims)
        acts = collections.Counter(x["action"] for x in hits)
        A(f"| `{r['sector']}` / `{r['end-use']}` | "
          f"{'; '.join(f'`{b}`' for b in branches) or 'none named'} | {len(hits)} | "
          f"{'; '.join(f'{a} {n}' for a, n in acts.most_common()) or '--'} |")
    A("")
    A("## Vocabulary the names need")
    A("")
    A(f"Naming follows section 5: `-` within a component, `_` between. With the "
      f"carrier now a list on the row rather than a name component, a design "
      f"technology is named `equipment_discriminator`.")
    A("")
    A(f"**{len(new_equipment)} equipment terms** are not in section 6.2 and would "
      "have to be added, or the labels renamed onto existing terms:")
    A("")
    A(", ".join(f"`{t}`" for t in new_equipment))
    A("")
    A(f"**{len(new_disc)} discriminators** are not existing variant or carrier "
      "terms. Section 6.2 treats a new term as a modelling decision, so the "
      "options are to add them, to widen the variant list into a free "
      "discriminator, or to shorten the names.")
    A("")
    A("## What adoption would change")
    A("")
    A("1. `build-template.py` -- `SECTORS` gains `biofuels` and `oil-and-gas`; "
      "`END_USES` is replaced by the 73 design rows and gains a `sector` column, "
      "so `end-use.csv` becomes sector-scoped. `service-unit` and "
      "`temperature-tier` come from the design table's `service-unit` and "
      "`heat-tier` columns.")
    A("2. Section 6.2 of the design document -- the equipment terms listed above, "
      "and a decision on the discriminators.")
    A("3. `populate.py` -- `END_USE_UNIT` is read from the design table rather "
      "than held as a dict; `node_for` keys on the design end use; the roster is "
      "seeded from the design technology table, so `add_tech` attaches a source's "
      "technology to an existing design row instead of creating one. "
      "`design_doc_roster()` (section 4 of the design doc) is superseded by the "
      "design technology table.")
    A("4. `aggregate.py` -- R2 and R4 are subsumed: the design table already says "
      "which end uses are cross-sector and already holds the carrier as a list, "
      "so the roster does not grow the names those rules exist to collapse. R3 "
      "(`other-services`) and R7 (`unquantified`) stay. R5 and R6 stay for the "
      "extraction rows, which still arrive spelled as their source spells them.")
    A("5. `build-cims-map.py` -- the `review` and `fuel-node` rows behind the "
      "empty end uses above have to be placed, and the mapper's end-use table "
      "now targets the design vocabulary.")
    A("6. The crosswalk tables in `design_crosswalk.py` and the names in "
      "`design_names*.py` become the adoption rules; the two CSVs beside this "
      "file are their output.")
    A("")
    A("## Folds that carry a note")
    A("")
    A("Where the fold costs something, or where the target is not the obvious one.")
    A("")
    A("| roster technology | design technology | what to know |")
    A("|---|---|---|")
    for r in sorted(tech_rows, key=lambda x: x["roster-technology"]):
        if r["note"]:
            A(f"| `{r['roster-technology']}` | `{r['design-technology']}` | "
              f"{r['note']} |")
    A("")
    A("## Every technology")
    A("")
    A("| design technology | label | type | sectors | roster technologies folded in | fact rows |")
    A("|---|---|---|---|---|---:|")
    folded = collections.defaultdict(list)
    for r in tech_rows:
        folded[r["design-technology"]].append(r["roster-technology"])
    for lab in sorted(names, key=lambda l: names[l]["name"]):
        d = names[lab]
        rows = label_rows[lab]
        types = "; ".join(sorted({r["type"] for r in rows}))
        secs = "; ".join(sorted({f"{r['sector']}/{r['end-use']}" for r in rows}))
        fold = folded.get(d["name"], [])
        n = sum(factcount[t] for t in fold)
        A(f"| `{d['name']}` | {lab} | {types} | {secs} | "
          f"{'; '.join(f'`{t}`' for t in sorted(fold)) or '--'} | {n} |")
    A("")
    A("## Every end use")
    A("")
    A("| design end use | applications | rules that placed them |")
    A("|---|---:|---|")
    rules = collections.defaultdict(collections.Counter)
    for r in app_rows:
        if r["design-end-use"]:
            rules[(r["design-sector"], r["design-end-use"])][r["rule"]] += 1
    for r in seu:
        k = (r["sector"], r["end-use"])
        A(f"| `{r['sector']}` / `{r['end-use']}` | {landed.get(k, 0)} | "
          f"{'; '.join(f'{a} ({b})' for a, b in rules[k].most_common()) or '--'} |")
    A("")
    if unmapped_apps:
        A("## Applications no rule placed")
        A("")
        A("| technology | sector | end use | process step |")
        A("|---|---|---|---|")
        for a in sorted({(x["technology"], x["from-sector"], x["from-end-use"],
                          x["from-process-step"]) for x in unmapped_apps}):
            A(f"| `{a[0]}` | {a[1]} | {a[2]} | {a[3]} |")
        A("")
    A("## Found while crosswalking")
    A("")
    A(f"- **`ccs` is in both the carrier and the variant vocabulary** in section "
      f"6.2, so `aggregate.split_name` files it in whichever component it reads "
      f"first: {ccs_as_carrier} of the {ccs_named} roster names ending `_ccs` "
      "carry it as the energy carrier and the rest as the variant. The design "
      "doc already notes this for `oxyfuel-ccs`; plain `ccs` has the same "
      "problem. Until it is fixed, anything keying on the variant column misses "
      "those rows -- this script reads the carrier back.")
    A("- **R2 has already merged away a distinction the new end uses need.** The "
      "generic end uses were collapsed onto `cross-sector` with no process step, "
      "so `Natural Gas.Production.Supply.Extraction.Compression`, "
      "`...Processing.Compression` and `...Transmission.Compression` are one "
      "application row with a joined `reported-steps` cell, while the design "
      "table puts them in three different end uses. CIMS placements here are "
      "therefore resolved from `cims-map.csv` by branch, not from the merged "
      "application row. An adoption pass has to do the same.")
    A("- **One efficiency bucket sits on a node it does not belong to.** "
      "`rolling-mill_efficiency-moderate` reaches `mining` / "
      "`separation-and-processing` through a mining forming-and-finishing node, "
      "which is why that end use is the only one taking a roster efficiency "
      "bucket with no efficient variant of its own. The design table is not "
      "missing an option here; the extraction filed a rolling mill in mining.")
    A("- **`Petroleum Crude.Steam` is claimed twice** -- by `oil-and-gas` / "
      "`in-situ-bitumen` in its `cims-services` cell, and by the cross-sector "
      "heat bands. The integral-vs-supplied rule and that row's own "
      "`heat-delivery` cell (\"draws heat-medium-temp\") both say the steam "
      "system is cross-sector, so that is where this crosswalk puts it, and "
      "`in-situ-bitumen` is left with only the CIMS In-Situ rows, which the "
      "mapper has not placed.")
    A("")
    A("## Naming flags")
    A("")
    A("| design technology | label | flag |")
    A("|---|---|---|")
    for lab in sorted(names, key=lambda l: names[l]["name"]):
        for f in names[lab]["flags"]:
            if f != "new discriminator":
                A(f"| `{names[lab]['name']}` | {lab} | {f} |")
    path = HERE / "design-crosswalk-review.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"  {path.name:34s} {len(out):5d} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
