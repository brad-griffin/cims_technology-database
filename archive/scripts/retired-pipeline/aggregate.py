"""Aggregation rules that keep the harmonized roster general.

Run as part of populate.py; not a standalone step.

The extractions stay faithful to what each source printed - a _nodes.csv file
records the sector and end use the source itself implies. This module is where
those faithful-but-inconsistent assignments are harmonized into one roster, so
that re-extracting a source never has to re-litigate a grouping decision.

Seven rules, set by the user 2026-09-10 against a roster that had reached 506
technologies and 1,365 applications. R1-R4 are design doc D11, R5-R7 are D12:

  R1  The `all-industry` sector is renamed `cross-sector`.
  R2  Generic services that are the same equipment wherever they are installed
      - machine drive, facility services (lighting, space conditioning,
      ventilation), refrigeration and cooling, and steam and hot water
      including CHP - are held once on `cross-sector` instead of being repeated
      under every sector. The sectors a source reported them for are kept in
      `reported-sectors` on the application row, so the collapse is reversible.
  R3  `other-services` is retired. It was a residual bin holding real process
      equipment - blast furnaces, kilns, steam crackers - and every technology
      in it is reassigned to the end use that same equipment already has, in
      the same sector where possible.
  R4  Names generalize: the carrier is dropped from an efficiency-bucket
      variant, and a temperature-tier suffix is dropped because the end use
      already carries the tier. Merged technologies keep every source's fact
      rows, distinguished by source-id; the source ranking decides which is
      primary, and nothing is discarded.
  R5  Carriers collapse into fuel groups where they behave the same as a source
      of heat. Conservative on purpose - see FUEL_GROUP.
  R6  post-combustion, oxyfuel and oxyfuel-ccs collapse into one `ccs` variant.
      The process ROUTES ending in -ccs are not touched.
  R7  A roster entry a source named but never quantified gets
      `status = unquantified`, stays in the roster, and drops out of the wide
      views.

The scope rule behind R5, R6 and everything not merged: this database describes
the plant stock that EXISTS as well as the options that might replace it. A
merge that erases an existing-technology distinction is not worth a row.
"""
from __future__ import annotations

import collections

CROSS_SECTOR = "cross-sector"

# raw name -> the canonical name it aggregated into. Written to the
# `aggregated-from` column so every merge is visible in the roster itself and
# a reader can tell a general name from one that was always general.
AGGREGATED = collections.defaultdict(set)

# --- R1 -------------------------------------------------------------------
SECTOR_RENAME = {"all-industry": CROSS_SECTOR}

# --- R2 -------------------------------------------------------------------
# Held once on cross-sector. These are the services whose equipment does not
# change with the sector it is installed in: a 75 kW motor is the same motor in
# a mill and in a refinery, and a fire-tube boiler is the same boiler.
CROSS_SECTOR_END_USES = {
    "machine-drive",
    "facility-services",
    "refrigeration-and-cooling",
    "steam-and-hot-water",
}

# --- R3 -------------------------------------------------------------------
RETIRED_END_USES = {"other-services"}

# Where the equipment gives no usable evidence, or gives the wrong answer.
# Keyed on the full technology name first, then on the equipment.
OTHER_SERVICES_TECH = {
    # direct air capture is not a heat service and not a process step of the
    # sector it sits in; it is filed with the conversion it offsets
    "capture-unit_direct": "material-conversion",
}
OTHER_SERVICES_EQUIPMENT = {
    "converter": "material-conversion",        # the steel BOF converter vessel
    "flotation-cell": "material-preparation",  # mineral beneficiation
    "pasteurizer": "process-heat-low-temp",    # food, roughly 70-90 degC
    "management-system": "machine-drive",      # site energy management systems
    # bakery and food ovens run about 100-230 degC, so the band is medium,
    # not high: filing them high was the equipment-name guess D11 warns about
    "oven": "process-heat-medium-temp",
    "digester": "material-conversion",
    "cleaning-system": "drying-and-separation",
    "melting-furnace": "process-heat-high-temp",   # glass and secondary metal melting
}

# The state of the roster before this pass, for the review file. populate.py
# canonicalizes names as it reads, so by the time `rewrite` runs the roster is
# already collapsed and cannot count what it started from.
BASELINE = {"technologies": 506, "applications": 1365, "service-nodes": 402,
            "date": "2026-08-29"}

# --- R5: fuel groups ------------------------------------------------------
# Carriers that behave the same as a source of heat collapse into one group.
# Deliberately conservative, because the database has to describe the plant
# stock that EXISTS as well as the options that might replace it (user,
# 2026-09-10), and most of the tempting merges destroy an existing-technology
# distinction rather than an accidental one:
#   coke stays out of coal          - in a blast furnace coke is the reductant,
#                                     not just a fuel
#   black-liquor stays out of biomass - the recovery boiler is the defining
#                                     unit of a kraft mill
#   ammonia and methanol stay put   - on a reformer or a reactor these name the
#                                     PRODUCT, and folding them into a fuel
#                                     group would rename the process
#   steam stays out of waste-heat   - purchased or site steam is not recovered
#                                     heat, and the cost basis differs
#   biogas, biomethane and municipal-waste stay out of biomass - different
#                                     carbon intensity and different policy
#                                     treatment under a clean fuel standard
FUEL_GROUP = {
    "lpg": "natural-gas",
    "liquid-biomass": "biomass",
    "landfill-gas": "biogas",
    "naphtha": "oil",
    "benzole-and-tars": "oil",
    "petroleum-coke": "coal",
    "blast-furnace-gas": "by-product-gas",
    "coke-oven-gas": "by-product-gas",
    "still-gas": "by-product-gas",
    "syngas": "by-product-gas",
}

# --- R6: one capture variant ----------------------------------------------
# How the CO2 is caught is a plant-engineering choice, not a technology the
# model picks between; what matters to it is that the unit captures. The
# process ROUTES that happen to end in -ccs (hisarna-ccs, corex-ccs,
# ulcored-ccs, top-gas-recycling-ccs) are NOT in this set: those are the
# alternative ironmaking routes the model exists to choose between.
CAPTURE_METHODS = {"ccs", "post-combustion", "oxyfuel", "oxyfuel-ccs"}

# --- R4 -------------------------------------------------------------------
EFF_BUCKETS = ("efficiency-base", "efficiency-moderate", "efficiency-strong")
TEMP_TIERS = ("low-temp", "medium-temp", "high-temp")

# Names that carry no equipment at all. Bataille's pulp-and-paper sheet has an
# "Other production steps (including improvement processes)" band whose rows
# name only the efficiency bucket, so they parsed as equipment=efficiency-base.
TECH_RENAME = {
    "efficiency-base": "process-improvement_efficiency-base",
    "efficiency-moderate": "process-improvement_efficiency-moderate",
    "efficiency-strong": "process-improvement_efficiency-strong",
    # the fuel is named by the carrier, never by a "fossil" catch-all
    "boiler_fossil": "boiler",
}


# --- splitting a name back into its three components ----------------------
_VOCAB: dict[str, set[str]] = {}
# set by populate.py so _apply_renames can split a name without being handed
# the path through five call frames
_VOCAB_PATH = [""]


def canon_tech(name: str) -> str:
    """The general name a source's technology name aggregates into.

    Pure and order-independent: it must give the same answer whether it is
    called while loading the first extraction or the last, because the fact
    rows and the roster row are canonicalized in different passes.
    """
    name = (name or "").strip()
    if not name:
        return name
    name = TECH_RENAME.get(name, name)
    equipment, carrier, variant = split_name(name, _VOCAB_PATH[0])
    # `oxyfuel-ccs` is in neither vocabulary, so split_name leaves it in the
    # carrier slot; it is a capture method and belongs in the variant
    if carrier in CAPTURE_METHODS and not variant:
        carrier, variant = "", carrier
    # R4: a temperature tier written as the variant duplicates the end use
    if variant in TEMP_TIERS:
        variant = ""
    # R4: an efficiency bucket is a bucket of measures, not a fuel-specific
    # device: dryer_coal_efficiency-base and dryer_natural-gas_efficiency-base
    # are the same "unimproved dryer" bucket, and their carriers are recorded
    # on the fact rows rather than in the name
    if variant in EFF_BUCKETS:
        carrier = ""
    # R5
    if carrier:
        carrier = FUEL_GROUP.get(carrier, carrier)
    # R6
    if variant in CAPTURE_METHODS:
        variant = "ccs"
    out = "_".join(x for x in (equipment, carrier, variant) if x)
    if out != name:
        AGGREGATED[out].add(name)
    return out


def canon_sector(sector: str) -> str:
    return SECTOR_RENAME.get(sector, sector)


def _vocab(path):
    """carrier and variant term lists, read from vocabulary.csv.

    build-template.py harvests them out of design doc section 6.2, which is the
    single source of truth; hard-coding a copy here would be a second one."""
    if not _VOCAB:
        import csv
        _VOCAB["carrier"], _VOCAB["variant"] = set(), set()
        try:
            with open(path, encoding="utf-8-sig", newline="") as fh:
                for r in csv.DictReader(fh):
                    if r.get("list-name") in _VOCAB:
                        _VOCAB[r["list-name"]].add(r["term"])
        except OSError:
            pass
    return _VOCAB


def split_name(name: str, vocab_path) -> tuple[str, str, str]:
    """(equipment, energy-carrier, variant) for a technology name.

    The carrier is OPTIONAL (design doc section 5), so the second component of
    a two-component name is a carrier in `boiler_natural-gas` and a variant in
    `boiler_ccs`. Splitting on position alone put 129 variants -- ccs, oxyfuel,
    hisarna, every efficiency bucket -- into the energy-carrier column, which
    is why the vocabulary decides instead of the position.
    """
    v = _vocab(vocab_path)
    p = (name or "").split("_")
    equipment = p[0] if p else ""
    if len(p) >= 3:
        return equipment, p[1], "_".join(p[2:])
    if len(p) == 2:
        # a term that is a variant and not a carrier is a variant; anything
        # unrecognized stays a carrier, which is where an unlisted term has
        # always gone and is what validate-names.py reports on
        if p[1] in v["variant"] and p[1] not in v["carrier"]:
            return equipment, "", p[1]
        return equipment, p[1], ""
    return equipment, "", ""


# ---------------------------------------------------------------------------
# the post-pass
# ---------------------------------------------------------------------------
def _majority(counter):
    """The end use a counter points at, or "" where it is empty or tied."""
    if not counter:
        return ""
    top = counter.most_common(2)
    if len(top) > 1 and top[0][1] == top[1][1]:
        return ""
    return top[0][0]


def rewrite(steps, nodes, techs, apps, facts, flows, cons):
    """Apply R1-R4 to the loaded tables, in place. Returns review lines.

    Runs after every source is loaded, because R3 resolves an unclassified
    application against the end uses the same equipment has elsewhere in the
    database, and that evidence is only complete at the end.
    """
    review, counts = [], {}
    counts["before"] = (len(techs), len(apps), len(nodes))

    # -- R1: rename the sector --------------------------------------------
    for a in apps.values():
        a["sector"] = canon_sector(a["sector"])
    for key in [k for k in steps if k[0] in SECTOR_RENAME]:
        row = steps.pop(key)
        row["sector"] = canon_sector(row["sector"])
        steps.setdefault((row["sector"], row["process-step"]), row)

    # -- R3: retire other-services ----------------------------------------
    # evidence: what end use does this equipment have where it IS classified
    by_sector_equip = collections.defaultdict(collections.Counter)
    by_equip = collections.defaultdict(collections.Counter)
    by_tech = collections.defaultdict(collections.Counter)
    for a in apps.values():
        if a["end-use"] in RETIRED_END_USES:
            continue
        equip = a["technology"].split("_")[0]
        by_sector_equip[(a["sector"], equip)][a["end-use"]] += 1
        by_equip[equip][a["end-use"]] += 1
        by_tech[a["technology"]][a["end-use"]] += 1

    resolved, unresolved = [], []
    for a in apps.values():
        if a["end-use"] not in RETIRED_END_USES:
            continue
        tech, equip = a["technology"], a["technology"].split("_")[0]
        # the same technology already classified elsewhere is the best evidence
        # there is, and it makes the reassignment a merge rather than a move
        target, why = _majority(by_tech.get(tech)), "same technology elsewhere"
        if not target:
            target, why = OTHER_SERVICES_TECH.get(tech, ""), "hand map (technology)"
        if not target:
            target = _majority(by_sector_equip.get((a["sector"], equip)))
            why = "same equipment in this sector"
        if not target:
            target, why = OTHER_SERVICES_EQUIPMENT.get(equip, ""), "hand map (equipment)"
        if not target:
            target, why = _majority(by_equip.get(equip)), "same equipment, any sector"
        if not target:
            unresolved.append((tech, a["sector"]))
            continue
        resolved.append((tech, a["sector"], target, why))
        a["end-use"] = target
        # the step came from the residual bin and does not belong to the new
        # end use; the source's own wording is kept in the note
        if a.get("process-step"):
            a["note"] = (a["note"] + " " if a.get("note") else "") + \
                f"Reassigned from other-services; the source filed it under " \
                f"{a['process-step']!r}."
            a["process-step"] = ""

    # -- R2: generic services onto one cross-sector row --------------------
    for a in apps.values():
        if a["end-use"] not in CROSS_SECTOR_END_USES:
            continue
        a["reported-sectors"] = a["sector"]
        if a.get("process-step"):
            a["reported-steps"] = a["process-step"]
            a["process-step"] = ""
        a["sector"] = CROSS_SECTOR

    # -- R4b: an electricity-only device named both with and without --------
    # The design-document roster names a microwave heater `microwave-heater`
    # and an extraction names the same device `microwave-heater_electricity`.
    # Where the ONLY other form of a bare equipment name is its `_electricity`
    # form, there is no carrier to distinguish and the two are one technology.
    # The test is deliberately narrow: `converter` and `converter_coal` are not
    # merged, because a coal-fired converter is a real distinction from
    # whatever an unqualified converter turns out to run on.
    forms = collections.defaultdict(set)
    for name in techs:
        if "_" in name:
            forms[name.split("_")[0]].add(name)
    merges = {bare: f"{bare}_electricity" for bare in techs
              if "_" not in bare and forms.get(bare) == {f"{bare}_electricity"}}
    _apply_renames(merges, techs, apps, facts, flows, cons)

    # -- rebuild the applications and the node table -----------------------
    merged = {}
    for a in apps.values():
        key = "_".join(x for x in (a["sector"], a["end-use"], a["process-step"]) if x)
        a["service-node"] = key
        prev = merged.get((a["technology"], key))
        if prev is None:
            merged[(a["technology"], key)] = a
            continue
        # R2 collapses several sector rows onto one application, so these three
        # columns become "; "-joined LISTS on the merged row. `source-id` is a
        # single id everywhere else in the database; anything joining on it here
        # -- check-manifest.py did -- has to split first.
        for col in ("source-id", "reported-sectors", "reported-steps"):
            have = [x for x in prev.get(col, "").split("; ") if x]
            new = [x for x in a.get(col, "").split("; ") if x and x not in have]
            prev[col] = "; ".join(sorted(have + new))
        if a.get("note") and a["note"] not in prev.get("note", ""):
            prev["note"] = (prev.get("note", "") + " " + a["note"]).strip()
    apps.clear()
    apps.update(merged)

    live = {a["service-node"] for a in apps.values()}
    for key in [k for k in nodes if k not in live]:
        nodes.pop(key)
    for a in apps.values():
        key = a["service-node"]
        if key not in nodes:
            nodes[key] = {"service-node": key, "sector": a["sector"],
                          "end-use": a["end-use"], "process-step": a["process-step"],
                          "branch": "", "service-unit": "GJ",
                          "service-description": "", "note": ""}
        else:
            nodes[key].update({"sector": a["sector"], "end-use": a["end-use"],
                               "process-step": a["process-step"]})
    used_steps = {(a["sector"], a["process-step"]) for a in apps.values() if a["process-step"]}
    for key in [k for k in steps if k not in used_steps]:
        steps.pop(key)

    # -- R7: mark the technologies no source ever put a number on ---------
    # 169 roster entries were `draft` with no parameter, flow or constraint row
    # behind them: named by the CIMS roster or by a source's own list, never
    # quantified. They are not `placeholder`, which means "the design document
    # says this is in scope and we have not extracted it yet" -- these were
    # offered by a source that then said nothing measurable. They stay in the
    # roster because the CIMS names are the spine the CIMS map points at (D9)
    # and deleting them would break that mapping; the status is what lets the
    # wide views leave them out and lets the gap be counted.
    has_data = {r["technology"] for t in (facts, flows, cons) for r in t}
    unquantified = sorted(n for n, row in techs.items()
                          if n not in has_data and row.get("status") == "draft")
    for n in unquantified:
        techs[n]["status"] = "unquantified"
        techs[n]["note"] = (techs[n].get("note", "") + " " if techs[n].get("note") else "") + \
            "UNQUANTIFIED: a source names this technology but reports no value for it, " \
            "so it has no fact rows. Kept in the roster because the name is a mapping " \
            "target and the gap is worth counting; left out of the wide views."
    placeholders = sorted(n for n, row in techs.items()
                          if row.get("status") == "placeholder")

    counts["after"] = (len(techs), len(apps), len(nodes))
    review = ([
        "# Aggregation review",
        "",
        "Generated by `aggregate.py`, applied by `populate.py`. Rules R1-R7 are "
        "documented at the top of `aggregate.py`. Nothing here is hand-edited: "
        "re-running `populate.py` regenerates it.",
        "",
        "| | technologies | applications | service nodes |",
        "|---|---|---|---|",
        f"| as at {BASELINE['date']}, before this pass | {BASELINE['technologies']} | "
        f"{BASELINE['applications']} | {BASELINE['service-nodes']} |",
        f"| after R4, names generalized | {counts['before'][0]} | {counts['before'][1]} | "
        f"{counts['before'][2]} |",
        f"| after R1-R3, sectors and end uses | {counts['after'][0]} | {counts['after'][1]} | "
        f"{counts['after'][2]} |",
        "",
        "Every fact row survives: `tech-parameter`, `tech-flow` and `tech-constraint` are "
        "unchanged in length, re-pointed at the general name. A merged technology therefore "
        "carries each contributing source's rows side by side, told apart by `source-id`.",
        "",
        f"## R7 - technologies with no data: {len(unquantified)} unquantified, "
        f"{len(placeholders)} placeholder",
        "",
        f"{len(unquantified) + len(placeholders)} of {len(techs)} roster entries carry no "
        "parameter, flow or constraint row. They stay in `technology.csv` — the CIMS names "
        "among them are what `cims-map.csv` points at — but the wide views leave them out, "
        "so the view shows what the database knows and the roster shows what it has been "
        "asked to cover. `placeholder` is a gap the design document declared; "
        "`unquantified` is a name a source offered without a number.",
        "",
        "## R4 - names generalized",
        "",
        "| general name | aggregates |",
        "|---|---|",
    ] + [f"| `{k}` | {', '.join('`' + x + '`' for x in sorted(v))} |"
         for k, v in sorted(AGGREGATED.items()) if k in techs] + [
        "",
        "## R3 - other-services reassignments",
        "",
        "| technology | sector as reported | reassigned to | evidence |",
        "|---|---|---|---|",
    ] + [f"| `{t}` | {s} | {e} | {w} |" for t, s, e, w in sorted(set(resolved))] + [
        "",
    ] + ([f"**{len(unresolved)} applications could not be resolved and stayed in "
          "other-services:** " + ", ".join(f"`{t}` ({s})" for t, s in sorted(set(unresolved)))]
         if unresolved else ["Every other-services application was reassigned."]) + [
        "",
        "## R4b - bare placeholders merged into their carrier form",
        "",
    ] + ([f"- `{o}` -> `{n}`" for o, n in sorted(merges.items())] or ["None."]))
    return review, unresolved


def _apply_renames(renames, techs, apps, facts, flows, cons):
    """Rename a technology everywhere it is referenced, merging on collision."""
    if not renames:
        return
    for old, new in renames.items():
        AGGREGATED[new].add(old)
        AGGREGATED[new] |= AGGREGATED.pop(old, set())
    for old, new in renames.items():
        row = techs.pop(old, None)
        if row is None:
            continue
        keep = techs.get(new)
        if keep is None:
            row["technology"] = new
            row["equipment"], row["energy-carrier"], row["variant"] = split_name(
                new, _VOCAB_PATH[0])
            techs[new] = row
            continue
        _merge_tech_row(keep, row)
    for a in list(apps.values()):
        if a["technology"] in renames:
            a["technology"] = renames[a["technology"]]
    for table in (facts, flows, cons):
        for r in table:
            if r.get("technology") in renames:
                r["technology"] = renames[r["technology"]]


def _merge_tech_row(keep, drop):
    """Fold one roster row into another. A populated cell always wins over a
    blank one; where both are populated and differ, the survivor is kept and
    the loser's value is recorded in the note rather than thrown away."""
    KEEP_BLANK = {"technology", "equipment", "energy-carrier", "variant", "note", "status"}
    for col, val in drop.items():
        if col in KEEP_BLANK or not val:
            continue
        if not keep.get(col):
            keep[col] = val
        elif keep[col] != val and col not in ("trl-source",):
            keep["note"] = (keep.get("note", "") + " " if keep.get("note") else "") + \
                f"On merge, the folded-in row gave {col}={val!r}; kept {keep[col]!r}."
    if drop.get("note") and drop["note"] not in keep.get("note", ""):
        keep["note"] = (keep.get("note", "") + " " + drop["note"]).strip()
    # a draft beats a placeholder: something is quantified
    if keep.get("status") == "placeholder" and drop.get("status") == "draft":
        keep["status"] = "draft"
