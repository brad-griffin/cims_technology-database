"""Turn the IEA guide dump into the structured raw-data extraction.

Run from the repo root:   python data/raw-data/iea/iea-guide-extract.py

The guide contributes ONE parameter and it is not a number this database has
carried before: a technology readiness level, assessed annually from 2020 to
2024. No costs, no efficiencies, no energy or emissions. What it is good for is
saying where a technology has got to and whether it is moving -- 133 industrial
rows with a five-point trajectory each.

TWO THINGS TO KNOW BEFORE USING THE TRLs:

  * The scale is the IEA ETP readiness scale, which runs to 11. It is NOT the
    1-9 NASA scale IPCC AR6 Table 11.3 uses, and the two are already in this
    database side by side. A 9 does not mean the same thing in both. The scale
    is recorded on every row.
  * The series is an assessment history, not a forecast. A technology that sits
    at 5 from 2020 to 2024 has not moved in five years, which is a finding; it
    is not a projection that it stays at 5.

Names are classified from the technology NAME ONLY. Feeding the description in
as well -- which is what the first attempt did -- reads the incumbent out of the
prose and names the wrong carrier: "Ammonia (high temperature heating)" became
natural-gas, because its description explains what it replaces. Rows the rules
cannot name are written to _unmapped.csv rather than forced.
"""
from __future__ import annotations

import collections
import csv
import importlib.util as _ilu
import re
import sys
from pathlib import Path

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
RECORDS = REPO_ROOT / "data" / "technology_database"
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = _DOCS, _HERE
ROOT = REPO_ROOT
STEM = "iea_2024_clean-tech-guide"
SOURCE_ID = "iea_2024_001"
YEARS = [2020, 2021, 2022, 2023, 2024]

_spec = _ilu.spec_from_file_location(
    "cims_map", ROOT / "cims" / "comparison" / "build_cims_map.py")
cims_map = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(cims_map)

# The guide's `category` under Industry -> our sector.
SECTOR = {
    "Iron and steel": "iron-and-steel", "Cement and concrete": "cement",
    "Chemicals and plastics": "chemicals", "Aluminium": "non-ferrous-metals",
    "Metallic products": "non-ferrous-metals", "Pulp and paper": "pulp-and-paper",
    "Industrial heating": "all-industry",
}
# Cross-cutting branches worth taking: these produce or capture for industry and
# the roster already carries the devices. Everything else in the guide is
# buildings, transport, power or fuels supply, and out of scope.
CROSS = {
    ("Hydrogen", "Production"): "all-industry",
    ("Carbon Capture and Storage", "CO2 capture"): "all-industry",
}
# Industrial heating rows name a temperature band in the sub-category.
HEAT_END_USE = {"High temperature": "process-heat-high-temp",
                "Low to medium temperature": "process-heat-low-temp"}
# Under Industrial heating the guide names the fuel and the band but no device:
# "Ammonia (high temperature heating)". The band supplies the device. Applied
# ONLY here, where the row is by construction a heat supply technology -- it
# would be an invention anywhere else in the guide, where a row with no device
# noun is usually a process route rather than a piece of equipment.
HEAT_EQUIPMENT = {"process-heat-high-temp": "direct-heater",
                  "process-heat-low-temp": "boiler"}
# Everything else takes its end use from what the row is doing.
END_USE = [
    (r"recycling|scrap|waste product", "material-preparation"),
    (r"carbon capture|ccus|\bccs\b|co2 capture", "other-services"),
    (r"heating|heat\b", "process-heat-high-temp"),
]
DEFAULT_END_USE = "material-conversion"


def main() -> int:
    src = HERE / f"{STEM}_rows.csv"
    if not src.exists():
        print(f"missing {src.name}; run iea-guide-dump.py first", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))

    PCOLS = ["process", "technology", "parameter", "target", "unit", "value",
             "value-min", "value-max", "formula", "reference", "source-original", "note"]
    NCOLS = ["process", "technology", "sector", "end-use", "process-step", "service-unit"]
    params, nodes, unmapped = [], {}, []

    for r in rows:
        sector = SECTOR.get(r["category"]) if r["sector"] == "Industry" else \
                 CROSS.get((r["sector"], r["category"]))
        if not sector:
            continue                                   # out of scope
        name_txt = r["name"]
        equip, carrier, variant, _, conf, _, _ = cims_map.classify("", "", name_txt)
        assumed = ""
        if not equip and r["category"] == "Industrial heating" and carrier:
            band = HEAT_END_USE.get(r["sub-category"], "process-heat-high-temp")
            equip = HEAT_EQUIPMENT[band]
            assumed = (f"device not named in the guide; {equip} assumed from the "
                       f"{r['sub-category'].lower()} band")
        if not equip:
            unmapped.append({"row": r["row"], "sector-path": r["sector-path"],
                             "name": name_txt, "carrier-matched": carrier,
                             "variant-matched": variant,
                             "trl-latest": r["trl-latest"],
                             "description": r["description"][:300]})
            continue
        tech = "_".join(x for x in (equip, carrier, variant) if x)
        if r["category"] == "Industrial heating":
            end_use = HEAT_END_USE.get(r["sub-category"], "process-heat-high-temp")
        else:
            end_use = next((eu for pat, eu in END_USE
                            if re.search(pat, f"{name_txt} {r['sub-category']}", re.I)),
                           DEFAULT_END_USE)
        proc = r["sub-category"] or r["category"]
        nodes.setdefault((proc, tech), {
            "process": proc, "technology": tech, "sector": sector,
            "end-use": end_use, "process-step": "", "service-unit": "t"})

        series = [(y, r.get("trl-latest") if str(y) == r.get("trl-latest-year") else "")
                  for y in YEARS]
        hist = [(t["year"], t["trl"]) for t in []]      # filled below from the series file
        note = (f"{name_txt}. {r['description']}"
                f"{' NZE rationale: ' + r['nze-rationale'] if r['nze-rationale'] else ''} "
                f"IEA ETP readiness scale, which runs to 11 -- NOT the 1-9 NASA scale used "
                f"by IPCC AR6 Table 11.3, which is also in this database. "
                f"Guide path: {r['sector-path']}."
                + (f" REVIEW: {assumed}." if assumed else ""))
        if r["trl-latest"]:
            params.append({"process": proc, "technology": tech, "parameter": "trl",
                           "target": "", "unit": "", "value": r["trl-latest"],
                           "value-min": "", "value-max": "", "formula": "",
                           "reference": f"IEA ETP Clean Energy Technology Guide, "
                                        f"2024 edition, row {r['row']}",
                           "source-original": "", "note": note})

    # the annual series, kept long so a trajectory is queryable
    ser = list(csv.DictReader((HERE / f"{STEM}_trl-series.csv").open(encoding="utf-8-sig")))
    by_row = collections.defaultdict(list)
    for t in ser:
        by_row[t["row"]].append((t["year"], t["trl"]))
    kept = {r["row"] for r in rows}
    trl_rows = [{"row": k, "name": next(x["name"] for x in ser if x["row"] == k),
                 "year": y, "trl": v}
                for k in sorted(by_row, key=int) if k in kept for y, v in by_row[k]]

    for path, cols, out in (
            (HERE / f"{STEM}.csv", PCOLS, params),
            (HERE / f"{STEM}_nodes.csv", NCOLS, list(nodes.values())),
            (HERE / f"{STEM}_unmapped.csv",
             ["row", "sector-path", "name", "carrier-matched", "variant-matched",
              "trl-latest", "description"], unmapped)):
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader(); w.writerows(out)
        print(f"  {path.name:44} {len(out):>4} rows")

    inscope = len(nodes) + len(unmapped)
    print(f"\n  {inscope} in-scope rows -> {len(nodes)} technologies named, "
          f"{len(unmapped)} left unnamed for review")
    moved = sum(1 for k, v in by_row.items()
                if k in kept and len({t for _, t in v}) > 1)
    print(f"  {moved} of the in-scope technologies changed TRL between 2020 and 2024")
    return 0


if __name__ == "__main__":
    sys.exit(main())
