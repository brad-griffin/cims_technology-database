"""Dump the IEA ETP Clean Energy Technology Guide faithfully, one row per technology.

Run from the repo root:   python data/raw-data/iea/iea-guide-dump.py

The guide is already a CSV, so this does three things and nothing else:

  * Decodes it. THE FILE IS MIXED ENCODING: mostly UTF-8, with a handful of
    stray cp1252 bytes -- the degree sign in "below 5<deg>C" is a bare 0xB0
    where the curly quotes around "lengthwise graphitisation" are proper UTF-8
    E2 80 9C. Reading the whole file as cp1252 "works" without error and
    silently turns every curly quote into mojibake; reading it as UTF-8 dies on
    the degree signs. So it is decoded as UTF-8 with the invalid runs repaired
    as cp1252, and the repairs are counted and reported.
  * Splits the `sector` column. It is a single comma-joined path from a
    breadth class down to a sub-category -- "large-scale or industrial,Industry,
    Iron and steel,Direct reduced iron (DRI)" -- and because the path is
    comma-joined inside a CSV field it is easy to mistake for four columns.
    Split into scale / sector / category / sub-category / detail.
  * Reshapes the TRL columns. trl2020 ... trl2024 is a time series, not five
    unrelated fields; it is emitted long, one row per technology per year, so
    the trajectory is queryable.

The edition is dated by the last populated TRL column: trl2024 carries 594 of
640 rows, which makes this the 2024 edition whatever the file is named.
"""
from __future__ import annotations

import collections
import csv
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "iea_2024_clean-energy-technology-guide.csv"
STEM = "iea_2024_clean-tech-guide"
YEARS = [2020, 2021, 2022, 2023, 2024]
LEVELS = ["scale", "sector", "category", "sub-category", "detail"]


def decode(path: Path) -> tuple[str, list[tuple[int, str]]]:
    """UTF-8, with any byte run that is not valid UTF-8 repaired as cp1252."""
    raw = path.read_bytes()
    out, fixed, i = [], [], 0
    while i < len(raw):
        try:
            out.append(raw[i:].decode("utf-8"))
            break
        except UnicodeDecodeError as e:
            out.append(raw[i:i + e.start].decode("utf-8"))
            run = raw[i + e.start:i + e.end]
            out.append(run.decode("cp1252", errors="replace"))
            fixed.append((i + e.start, run.hex()))
            i += e.end
    return "".join(out), fixed


def main() -> int:
    if not SRC.exists():
        print(f"not found: {SRC}", file=sys.stderr)
        return 1
    text, bad = decode(SRC)
    rows = list(csv.DictReader(io.StringIO(text)))

    wide, trl = [], []
    for i, r in enumerate(rows, start=2):
        parts = [p.strip() for p in (r.get("sector") or "").split(",")]
        d = {"row": i, "name": (r.get("name") or "").strip()}
        d.update({lv: (parts[j] if j < len(parts) else "") for j, lv in enumerate(LEVELS)})
        # A path can run deeper than five levels; keep the tail rather than lose it.
        d["path-extra"] = ",".join(parts[len(LEVELS):])
        d["sector-path"] = (r.get("sector") or "").strip()
        for k in ("description", "NZErationale", "supplyChain"):
            d[k.lower() if k != "NZErationale" else "nze-rationale"] = (r.get(k) or "").strip()
        d["trl-latest"] = ""
        d["trl-latest-year"] = ""
        for y in YEARS:
            v = (r.get(f"trl{y}") or "").strip()
            if v:
                d["trl-latest"], d["trl-latest-year"] = v, str(y)
                trl.append({"row": i, "name": d["name"], "year": y, "trl": v})
        wide.append(d)

    cols = (["row", "name", "sector-path"] + LEVELS + ["path-extra", "trl-latest",
            "trl-latest-year", "description", "nze-rationale", "supplychain"])
    p = HERE / f"{STEM}_rows.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(wide)
    print(f"  {p.name:44} {len(wide):>4} rows")
    p = HERE / f"{STEM}_trl-series.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["row", "name", "year", "trl"])
        w.writeheader(); w.writerows(trl)
    print(f"  {p.name:44} {len(trl):>4} rows")

    with (HERE / f"{STEM}_meta.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["parameter", "value"])
        w.writerow(["source-id", "iea_2024_001"])
        w.writerow(["edition", "2024, dated by the last populated TRL column"])
        w.writerow(["file-encoding", "mixed: UTF-8 with stray cp1252 bytes; "
                                      "decode as UTF-8 and repair the invalid runs"])
        w.writerow(["trl-scale", "IEA ETP readiness scale, 1-11 (not the 1-9 NASA scale "
                                 "IPCC Table 11.3 uses)"])
        w.writerow(["licence", "CC BY 4.0"])

    ind = [d for d in wide if d["sector"] == "Industry"]
    print(f"\n  {len(wide)} technologies, {len(ind)} under Industry, "
          f"{len({d['sector'] for d in wide})} top-level sectors")
    print("  latest TRL year: " + ", ".join(
        f"{y}={n}" for y, n in sorted(collections.Counter(
            d["trl-latest-year"] for d in wide if d["trl-latest-year"]).items())))
    if bad:
        print(f"  {len(bad)} non-UTF-8 byte run(s) repaired as cp1252: "
              + ", ".join(f"0x{h} at {i}" for i, h in bad[:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
