"""Extract the technology roster from the CIMS model inputs.

Run from the repo root:   python database/harmonized/extract-cims-roster.py [CIMS_MODEL_DIR]

Default CIMS_MODEL_DIR is the sibling checkout:
    ../data_processing_calibration/cims/data/model_inputs/model

Writes database/harmonized/cims-roster.csv -- one row per distinct technology.

Two things this collapses on purpose:
  * the provincial copies. CIMS repeats every technology per region with the
    region in the branch string; the roster keeps one row and lists the regions.
  * the parameter-overlay folders (FIC, DIC, DCC, market_share_limits). Those
    are not sectors: they carry extra parameters for technologies that live in
    the sector folders, and are merged into the same row.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE.parent.parent.parent / "data_processing_calibration" / "cims" / "data" \
          / "model_inputs" / "model"
COLS = ["cims-sector", "cims-service", "cims-technology", "cims-branch", "regions",
        "parameters", "source-files", "cims-source", "units", "year-min", "year-max"]


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not base.is_dir():
        sys.exit(f"CIMS model input directory not found: {base}\n"
                 "Pass it as an argument, or connect the data_processing_calibration folder.")
    rec: dict[tuple, dict] = {}
    files = 0
    for p in sorted(base.glob("*/*.csv")):
        files += 1
        folder = p.parent.name
        with p.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                tech = (r.get("Technology") or "").strip()
                if not tech:
                    continue
                branch = re.sub(r"^CIMS\.CAN\.[A-Z]{2}\.", "", (r.get("Branch") or "").strip())
                key = ((r.get("Sector") or "").strip(), (r.get("Service") or "").strip(),
                       tech, branch)
                d = rec.setdefault(key, collections.defaultdict(set))
                d["folders"].add(folder)
                d["regions"].add((r.get("Region") or "").strip())
                d["params"].add((r.get("Parameter") or "").strip())
                if r.get("Source"):
                    d["sources"].add(r["Source"].strip())
                if r.get("Unit"):
                    d["units"].add(r["Unit"].strip())
                y = (r.get("Year") or "").strip()
                if y.isdigit():
                    d["years"].add(y)
    rows = []
    for (sector, service, tech, branch), d in sorted(rec.items()):
        yrs = sorted(d["years"])
        rows.append({"cims-sector": sector, "cims-service": service, "cims-technology": tech,
                     "cims-branch": branch, "regions": ";".join(sorted(d["regions"])),
                     "parameters": ";".join(sorted(x for x in d["params"] if x)),
                     "source-files": ";".join(sorted(d["folders"])),
                     "cims-source": ";".join(sorted(d["sources"]))[:300],
                     "units": ";".join(sorted(d["units"])),
                     "year-min": yrs[0] if yrs else "", "year-max": yrs[-1] if yrs else ""})
    dst = HERE / "cims-roster.csv"
    with dst.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader(); w.writerows(rows)
    print(f"{files} CIMS input files -> {len(rows)} distinct technologies -> {dst.name}")
    c = collections.Counter(r["cims-sector"] for r in rows)
    for k, v in sorted(c.items(), key=lambda x: -x[1])[:12]:
        print(f"  {v:5d}  {k or '(blank)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
