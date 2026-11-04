"""Write every Word document in the review packages.

    python review-packages/scripts/build_review_docs.py

Reads scripts/sector-facts.json (written by sector_facts.py) and writes, in each
review-package_<package>/ folder, the reviewer guide, the sector note (sector
packages only), and a copy of the shared methodology summary.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import docx_guides  # noqa: E402
import docx_methodology  # noqa: E402
import docx_sector_notes  # noqa: E402

OUT = HERE.parent
PACKAGES = ["breweries", "steel", "pulp-and-paper", "cement-and-lime", "chemicals", "conventional-oil", "oil-sands", "natural-gas", "biofuels", "hydrogen", "mining", "aluminum", "petroleum-refining", "whole-database"]


def main():
    facts = json.loads((HERE / "sector-facts.json").read_text(encoding="utf-8"))
    for p in PACKAGES:
        (OUT / f"review-package_{p}").mkdir(exist_ok=True)
    first = OUT / f"review-package_{PACKAGES[0]}" / "methodology-summary.docx"
    docx_methodology.build(first, facts)
    for p in PACKAGES[1:]:
        shutil.copyfile(first, OUT / f"review-package_{p}" / "methodology-summary.docx")
    docx_sector_notes.build(OUT, facts)
    docx_guides.build(OUT, facts)
    n = sum(1 for _ in OUT.glob("review-package_*/*.docx"))
    print(f"wrote {n} Word documents in {OUT}")


if __name__ == "__main__":
    main()
