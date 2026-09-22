"""Check the source manifest against the disk and against the database.

Run from the repo root:   python data/raw-data/check-manifest.py

The manifest is two hand-maintained CSVs -- source-details_sources.csv (one row
per source) and source-details_files.csv (one row per file held for a source).
It was a workbook until 2026-08-29; the conversion is recorded in the README.
Nothing generates these files, so this checks the things that quietly rot:

  * a file row whose file does not exist where it says it does;
  * a file row pointing at a source that is not registered;
  * a source-id used in the harmonized database that is not registered;
  * rows out of alphabetical order.

Exit status is non-zero if anything fails, so it can gate a commit.
"""
from __future__ import annotations

import collections
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCES = HERE / "source-details_sources.csv"
FILES = HERE / "source-details_files.csv"
HARMONIZED = ROOT / "data" / "harmonized"


def read(p: Path) -> list[dict]:
    return list(csv.DictReader(p.open(encoding="utf-8-sig"))) if p.exists() else []


def main() -> int:
    srcs, files = read(SOURCES), read(FILES)
    if not srcs:
        print(f"manifest not found at {SOURCES}", file=sys.stderr)
        return 1
    fail = collections.defaultdict(list)

    ids = [d["source_id"] for d in srcs]
    if len(ids) != len(set(ids)):
        dup = [k for k, v in collections.Counter(ids).items() if v > 1]
        fail["duplicate source_id"] = dup
    if ids != sorted(ids):
        fail["sources not in alphabetical order"] = ["run the sort in the README"]
    fkeys = [(d["source_id"], d["file_name"]) for d in files]
    if fkeys != sorted(fkeys):
        fail["files not in alphabetical order"] = ["sort by source_id then file_name"]

    for d in files:
        if d["source_id"] not in set(ids):
            fail["file row for an unregistered source"].append(
                f"{d['source_id']} / {d['file_name']}")
        on_disk = (d.get("file_on_disk") or "").strip()
        if not on_disk:
            fail["file row with no file on disk"].append(
                f"{d['source_id']} / {d['file_name']}")
            continue
        path = ROOT / d["file_path"] / on_disk
        if not path.exists():
            fail["file recorded but missing"].append(str(path))

    used = collections.Counter()
    for path in (HARMONIZED / "output" / "example-parameter.csv",
                 HARMONIZED / "output" / "example-flow.csv",
                 HARMONIZED / "output" / "example-constraint.csv",
                 HARMONIZED / "records" / "source-example.csv"):
        for r in read(path):
            for col in ("source-id", "via-source-id"):
                sid = (r.get(col) or "").strip()
                if sid:
                    used[sid] += 1
    for sid in sorted(set(used) - set(ids)):
        fail["used in the database but not registered"].append(
            f"{sid} ({used[sid]} rows)")

    print(f"  {len(srcs)} sources, {len(files)} files, "
          f"{len(used)} source-ids used in the database")
    unused = sorted(set(ids) - set(used))
    print(f"  {len(set(ids) & set(used))} registered sources are used; "
          f"{len(unused)} are registered and not yet used")
    if not fail:
        print("  all checks passed")
        return 0
    for k, v in fail.items():
        print(f"\n  {k.upper()} ({len(v)}):")
        for x in v[:12]:
            print(f"      {x}")
        if len(v) > 12:
            print(f"      ... and {len(v) - 12} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())
