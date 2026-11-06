"""Turn the Bataille 2017 dump into the structured raw-data extraction.

Run from the repo root:   python data/raw-data/other-reports/bataille-extract.py
Reads the output of bataille-dump.py; writes the files the database build (data/harmonized/pipeline/extract.py) reads.

What the two sheets actually offer, which is narrower than their size suggests:

  UKTM      390 technologies and 387 investment costs. Everything else is
            almost empty -- state of development, GHG impact and energy impact
            are filled on 10 rows out of 390, and no row carries a reference.
            The costs are UK TIMES model inputs transcribed by Bataille, so the
            source is Bataille and the note says where the numbers came from.
  Database  79 technologies from a literature survey, with 74 reference links
            but prose in every value field ("30% less than OPC", "Up to 50%
            less"). Nothing there is a number this database can carry, so these
            become placeholder technologies -- which is what design decision D8
            asks for -- and their references go to a separate file for a later
            registration pass.

THE CAPACITY UNITS CANCEL EXACTLY, which looks like a missing conversion and is
not. Costs are GBP millions per capacity unit:
    £m / PJ_a  =  1e6 GBP / 1e6 GJ_a  =  1 GBP per GJ-per-yr
    £m / Mt_a  =  1e6 GBP / 1e6 t_a   =  1 GBP per t-per-yr
    £m / GW    =  1e6 GBP / 1e6 kW    =  1 GBP per kW
So the value is written unchanged under a unit string that matches the one the
UKERC extraction already uses, and this comment exists so nobody "fixes" it.
"""
from __future__ import annotations

import collections
import csv
import importlib.util as _ilu
import re
import sys
from pathlib import Path

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # extraction/
from paths import RECORDS, ROOT as REPO_ROOT, source_dirs  # noqa: E402
# documents in primary-sources/, extractions in data/raw_data/technology_database/ (2026-11-06)
DOCS, HERE = source_dirs(__file__)
ROOT = REPO_ROOT
STEM = "bataille_2017_heavy-industry-database"
SOURCE_ID = "bataille_2017_001"
SOURCE_FILE = f"{STEM}.xlsx"
CURRENCY = "2010_GBP"

_spec = _ilu.spec_from_file_location(
    "cims_map", ROOT / "cims" / "comparison" / "build_cims_map.py")
cims_map = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(cims_map)

SECTOR = {
    # UKTM sheet
    "Cement": "cement", "Pulp and Paper": "pulp-and-paper",
    "Iron and Steel": "iron-and-steel", "Chemicals": "chemicals",
    "Non-Ferrous Metals": "non-ferrous-metals", "Food & Drink": "food-and-beverage",
    "Non-Metallic Minerals": "non-metallic-minerals", "Others": "other-industry",
    # Database sheet adds these
    "Glass": "non-metallic-minerals", "Refineries": "petroleum-refining",
    "Mining": "mining", "Metal Processing": "non-ferrous-metals",
    "CCS": "all-industry", "All sectors": "all-industry",
    "Industrial heating": "all-industry", "BECCS": "all-industry",
}

# Process-step band text -> end use. Ordered: the first match wins, so the
# specific services are tested before the generic "Production processes:".
END_USE = [
    (r"chp plants", "steam-and-hot-water"),
    (r"boilers", "steam-and-hot-water"),
    (r"high temperature heat", "process-heat-high-temp"),
    (r"low temperature heat", "process-heat-low-temp"),
    (r"drying & separation", "drying-and-separation"),
    (r"motor drive", "machine-drive"),
    (r"refrigeration", "refrigeration-and-cooling"),
    (r"other services", "other-services"),
    (r"casting & rolling|finishing process", "forming-and-finishing"),
    (r"sinter production", "material-preparation"),
    (r"production process|alternative production route|high value chemicals|"
     r"ammonia", "material-conversion"),
]

# UKTM names most services as a pair, "New X technology" and "Advanced X
# technology", which classify() reduces to the same name. That pair is the
# efficiency split the database already models (design doc D8, and CIMS's own
# Std / Eff / High Eff), so it is carried as a variant rather than collapsed.
GRADE = [(r"^\s*advanced\b", "efficiency-strong"), (r"^\s*new\b", "efficiency-base")]

# Where the sheet names a service but no device -- "Other processes based on
# coal", "New low temperature heat biomass technology" -- the end use supplies
# the device. Without this the name is a bare carrier, which the convention
# reserves for tech-flow rows, and every fuel in a block collapses onto one row.
DEFAULT_EQUIPMENT = {
    "steam-and-hot-water": "boiler", "process-heat-high-temp": "direct-heater",
    "process-heat-low-temp": "direct-heater", "drying-and-separation": "dryer",
    "machine-drive": "motor", "refrigeration-and-cooling": "chiller",
    # "Other services" is UKTM's own catch-all: 43 rows of "Other processes
    # based on <fuel>" with no device named anywhere. direct-heater is the
    # least-wrong device for a fuel-using process, and every row it names is
    # marked for review rather than presented as a confident classification.
    "other-services": "direct-heater",
}

# Database-sheet state of development -> the harmonized vocabulary.
MATURITY = {
    "current standard": "commercial", "commercial": "commercial",
    "small scale commercialization": "commercial",
    "pilot / early commercial": "pilot", "pilot": "pilot",
    "demonstration": "pilot", "conceptual": "r-and-d", "r&d": "r-and-d",
}

# £m per capacity unit -> (unit string, capacity basis, capacity unit). See the
# module docstring: the millions cancel the mega- in the capacity unit exactly.
CAPACITY = {
    "PJ_a": (f"{CURRENCY}/GJ-per-yr", "annual-output", "GJ"),
    "Mt_a": (f"{CURRENCY}/t-per-yr", "annual-output", "t"),
    "GW":   (f"{CURRENCY}/kW", "nameplate", "kW"),
}


def num(v):
    try:
        f = float(str(v).replace(",", ""))
        return f if f == f and abs(f) != float("inf") else None
    except (TypeError, ValueError):
        return None


def fmt(x):
    return "" if x is None else f"{x:.6g}"


def end_use_of(step: str, unmapped: list) -> str:
    s = step.lower()
    for pat, eu in END_USE:
        if re.search(pat, s):
            return eu
    if step:
        unmapped.append(step)
    return "other-services"


def read(suffix: str) -> list[dict]:
    path = HERE / f"{STEM}_{suffix}.csv"
    if not path.exists():
        print(f"missing {path.name}; run bataille-dump.py first", file=sys.stderr)
        sys.exit(1)
    return [r for r in csv.DictReader(path.open(encoding="utf-8-sig"))
            if r["technology-name"]]


def name_rows(rows: list[dict], sheet: str, unmapped: list, unnamed: list) -> list[dict]:
    """Give every row a sector, end use and a name on the repo convention."""
    out = []
    for r in rows:
        sector = SECTOR.get(r["sector"].strip())
        if not sector:
            unmapped.append(f"sector {r['sector']!r}")
            continue
        step = r["process-step"]
        equip, carrier, variant, _, conf, note, kind = cims_map.classify(
            sector, step, f"{r['technology-name']} {r['description']}")
        end_use = end_use_of(step, unmapped)
        assumed = ""
        if not equip:
            equip = DEFAULT_EQUIPMENT.get(end_use, "")
            if equip:
                assumed = (f"device not named in the source; {equip} assumed from the "
                           f"{end_use} end use")
                conf = "low"
        if not variant:
            for pat, grade in GRADE:
                if re.search(pat, r["technology-name"], re.I):
                    # Only where the block actually holds both halves of the pair:
                    # a lone "New X" is just X, and tagging it efficiency-base
                    # would imply a sibling that is not there.
                    variant = grade
                    break
        name = "_".join(x for x in (equip, carrier, variant) if x)
        if not name:
            unnamed.append((sheet, r["row"], r["technology-name"][:60]))
            continue
        out.append(dict(r, sector=sector, name=name, equip=equip, carrier=carrier,
                        variant=variant, end_use=end_use, assumed=assumed,
                        step=step, sheet=sheet, classify_note=note, confidence=conf))
    return out


def drop_lone_grades(rows: list[dict]) -> list[dict]:
    """Undo the New/Advanced variant where the block holds only one of the pair.

    "Advanced electric motor technology" is efficiency-strong because a "New
    electric motor technology" sits beside it. A block with only one of the two
    has no efficiency split to model, and tagging it would invent a sibling.
    """
    group = collections.defaultdict(set)
    for r in rows:
        group[(r["sector"], r["step"], r["equip"], r["carrier"])].add(r["variant"])
    for r in rows:
        g = group[(r["sector"], r["step"], r["equip"], r["carrier"])]
        if r["variant"].startswith("efficiency-") and len(
                {v for v in g if v.startswith("efficiency-")}) < 2:
            r["variant"] = ""
            r["name"] = "_".join(x for x in (r["equip"], r["carrier"]) if x)
    return rows


def main() -> int:
    unmapped, unnamed = [], []
    uktm = name_rows(read("uktm-rows"), "UKTM", unmapped, unnamed)
    db = name_rows(read("database-rows"), "Database", unmapped, unnamed)
    uktm = drop_lone_grades(uktm)

    PCOLS = ["process", "technology", "parameter", "target", "unit", "value",
             "value-min", "value-max", "formula", "reference", "source-original", "note"]
    NCOLS = ["process", "technology", "sector", "end-use", "process-step", "service-unit"]
    params, nodes, refs = [], {}, []
    odd = []
    # Several UKTM rows can legitimately reduce to one technology in one sector
    # and step -- MEA and KS-1 capture on the same kiln, scrap and shaft preheat
    # on the same arc furnace. Emitting one parameter row each would put two
    # values on one technology and let whichever loads last win. They are
    # gathered here and emitted once, with the spread as min/max and every
    # contributing UKTM row named, so the collapse is visible instead of lossy.
    costs = collections.defaultdict(list)

    for r in uktm:
        proc = r["step"] or r["sector"]
        base = (f"Bataille 2017 UKTM sheet row {r['row']}"
                + (f", UKTM code {r['uktm-code']}" if r["uktm-code"] else ""))
        desc = r["description"] or r["technology-name"]
        # Keyed on the sector too. "Production processes: Drying & separation"
        # appears under four sectors, and a (step, name) key silently collects
        # all four sectors' costs onto one technology -- the same trap that put
        # 116 referential failures in the UKERC pass.
        key = (r["sector"], proc, r["name"])
        nodes.setdefault(key, {
            "process": proc, "technology": r["name"], "sector": r["sector"],
            "end-use": r["end_use"], "process-step": r["step"],
            "service-unit": CAPACITY.get(r["capacity-unit"], ("", "", ""))[2]})

        cost, cap = num(r["investment-cost"]), CAPACITY.get(r["capacity-unit"])
        if cost is not None and cap:
            unit, cbasis, cunit = cap
            note = (f"{desc}. UK TIMES investment cost, transcribed by Bataille from "
                    f"the UKTM model: {r['investment-cost']} GBP million per "
                    f"{r['capacity-unit']} in 2010 prices. The millions cancel the "
                    f"mega- in the capacity unit exactly, so the value is unchanged.")
            if r["assumed"]:
                note += f" REVIEW: {r['assumed']}."
            if r["variant"] == "ccs" and cost < 100:
                # The cement CCS rows sit two orders below the kiln they retrofit
                # (26.9 against 309 GBP/t-per-yr) while their KS-1 and oxyfuel
                # siblings sit near it. That reads as an incremental add-on cost
                # mixed in among whole-plant costs. Flagged, not adjusted.
                note += (" REVIEW: low against the whole-plant costs in the same "
                         "block; may be an incremental capture cost rather than a "
                         "plant cost.")
                odd.append((r["row"], r["name"], cost))
            costs[(r["sector"], proc, r["name"], unit)].append(
                (cost, base, note, r["technology-name"]))
        elif cost is not None:
            odd.append((r["row"], r["name"], "cost with no capacity unit"))

        trl = num(r["state-of-development"])
        if trl is not None:
            params.append({"process": proc, "technology": r["name"], "parameter": "trl",
                           "target": "", "unit": "", "value": fmt(trl), "value-min": "",
                           "value-max": "", "formula": "", "reference": base,
                           "source-original": "",
                           "note": f"{desc}. UKTM column 'State of development'."})
        ghg, en = num(r["ghg-impact"]), num(r["energy-impact"])
        if ghg is not None and "ccs" in (r["variant"] or ""):
            params.append({"process": proc, "technology": r["name"],
                           "parameter": "capture-rate", "target": "co2", "unit": "fraction",
                           "value": fmt(ghg), "value-min": "", "value-max": "",
                           "formula": "", "reference": base, "source-original": "",
                           "note": f"{desc}. UKTM column 'GHG impact', read as the "
                                   "captured fraction because this row is a capture "
                                   "technology. The same column on non-capture rows "
                                   "is a reduction relative to current practice and "
                                   "is left in the note there."})
        elif ghg is not None or en is not None:
            # Relative to "current standard", with no stated baseline technology.
            # There is no parameter for that, and inventing one for eight rows
            # would be worse than recording the source's own words.
            nodes[key]["note-carry"] = (
                f"UKTM 'GHG impact' {r['ghg-impact']!r}, 'Energy impact' "
                f"{r['energy-impact']!r}, both relative to current practice with no "
                "baseline technology stated. Not carried as parameters.")

    for (sector, proc, name, unit), got in costs.items():
        vals = [c for c, _, _, _ in got]
        lo, hi = min(vals), max(vals)
        # The primary is the lowest cost, which for these blocks is the plain
        # technology rather than a variant of it; the spread carries the rest.
        cost, base, note, _ = min(got, key=lambda g: g[0])
        if len(got) > 1:
            note += (" Collapsed from " + str(len(got)) + " UKTM rows that reduce to "
                     "this name: " + "; ".join(f"{n} = {fmt(c)}" for c, _, _, n in got)
                     + ". The value is the lowest and the spread is min/max.")
        params.append({"process": proc, "technology": name, "parameter": "capex",
                       "target": "", "unit": unit, "value": fmt(cost),
                       "value-min": fmt(lo) if hi > lo else "",
                       "value-max": fmt(hi) if hi > lo else "",
                       "formula": "", "reference": base, "source-original": "",
                       "note": note})

    for r in db:
        proc = r["step"] or r["sector"]
        key = (r["sector"], proc, r["name"])
        nodes.setdefault(key, {
            "process": proc, "technology": r["name"], "sector": r["sector"],
            "end-use": r["end_use"], "process-step": r["step"], "service-unit": ""})
        sod = MATURITY.get(re.sub(r"\s*\(.*", "", r["state-of-development"]).strip().lower())
        ref = f"Bataille 2017 Database sheet row {r['row']}"
        if sod:
            params.append({"process": proc, "technology": r["name"],
                           "parameter": "state-of-development", "target": "", "unit": "",
                           "value": sod, "value-min": "", "value-max": "", "formula": "",
                           "reference": ref, "source-original": "",
                           "note": f"{r['description'] or r['technology-name']}. "
                                   f"Bataille records this as "
                                   f"{r['state-of-development']!r}."})
        qual = [f"{k} {r[k]!r}" for k in ("ghg-impact", "energy-impact", "cost") if r[k]]
        if qual:
            nodes[key]["note-carry"] = (
                "Bataille Database sheet gives this only in prose: "
                + "; ".join(qual) + ". Not carried as parameters.")
        if r["reference-links"]:
            refs.append({"row": r["row"], "sector": r["sector"],
                         "technology": r["name"],
                         "technology-name-as-given": r["technology-name"],
                         "reference-type": r["reference-type"],
                         "reference-links": r["reference-links"]})

    for path, cols, rows in (
            (HERE / f"{STEM}.csv", PCOLS, params),
            (HERE / f"{STEM}_nodes.csv", NCOLS,
             [{k: v for k, v in n.items() if k in NCOLS} for n in nodes.values()]),
            (HERE / f"{STEM}_database-references.csv",
             ["row", "sector", "technology", "technology-name-as-given",
              "reference-type", "reference-links"], refs)):
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader(); w.writerows(rows)
        print(f"  {path.name:56} {len(rows):>4} rows")

    print(f"\n  {len(nodes)} distinct technologies from {len(uktm)} UKTM and "
          f"{len(db)} Database rows")
    print("  parameters: " + ", ".join(
        f"{n} {k}" for k, n in collections.Counter(
            p["parameter"] for p in params).most_common()))
    if unnamed:
        print(f"  {len(unnamed)} row(s) the naming rules could not name:")
        for sheet, row, t in unnamed[:8]:
            print(f"      {sheet} row {row}: {t}")
        if len(unnamed) > 8:
            print(f"      ... and {len(unnamed) - 8} more")
    if odd:
        print(f"  {len(odd)} cost row(s) flagged for review")
    if unmapped:
        c = collections.Counter(unmapped)
        print(f"  {len(c)} unmapped process step(s)/sector(s): "
              + "; ".join(f"{k!r} x{v}" for k, v in c.most_common(6)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
