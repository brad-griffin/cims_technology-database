"""Where the technology database's files are, for the extraction scripts.

The same layout in tech_data and in CIMS: the folder that holds
data/technology_database/ is the repo root (found by walking up from here).

    data/raw_data/technology_database/      the extractions and the manifest (FRDR)
    primary-sources/                        the source documents (local only; may be absent)
    data/technology_database/               the hand-edited records
    data/processed_data/technology_database/  what the build writes

An extraction script under extraction/sources/<publisher>/... reads its document from
the same folder under primary-sources/ and writes its CSVs to the same folder under
the raw data: ``PRIMARY_DIR, RAW_DIR = source_dirs(__file__)``.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent


def _repo_root() -> Path:
    for p in HERE.parents:
        if (p / "data" / "technology_database").is_dir():
            return p
    raise SystemExit("data/technology_database/ not found above " + str(HERE))


ROOT = _repo_root()
DATA = ROOT / "data"
RAW = DATA / "raw_data" / "technology_database"
PRIMARY = ROOT / "primary-sources"
RECORDS = DATA / "technology_database"
OUTPUT = DATA / "processed_data" / "technology_database"
SOURCES = HERE / "sources"


def source_dirs(script: str) -> tuple[Path, Path]:
    """(the document folder, the extraction folder) for a script under sources/."""
    sub = Path(script).resolve().parent.relative_to(SOURCES)
    return PRIMARY / sub, RAW / sub
