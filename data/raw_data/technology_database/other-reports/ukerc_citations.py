"""Turn UKERC's reference strings into source identifiers.

Run from the repo root:
    python data/raw-data/other-reports/ukerc-citations.py

Reads the faithful UKERC dump and writes ukerc-citations.csv: one row per
distinct original citation, with the source-id minted for it and the count of
UKERC rows that cite it.

Why this exists (design doc D7): UKERC is a compilation. Its numbers come from
IEA GHG, Worrell, the Carbon Trust and seventy other originals, and crediting
UKERC for them loses the provenance the database is supposed to keep. The
originals become `source-id` and UKERC becomes `via-source-id`.

The parsing is fiddly because the workbook is inconsistent:
  * ';' always separates citations, ',' usually does;
  * 'Worrell et al 1999, 2010' is two Worrell papers, not a second author;
  * 'Novacem 2011a, b' is two Novacem papers, the second written as a bare
    letter suffix;
  * the same source appears as 'IEA GHG 2008' and 'IEAGHG 2008', and with and
    without the full stop in 'et al.'.
None of that is fixed in the workbook -- it is normalised here, and the
original string is kept alongside so the mapping can be checked.
"""
from __future__ import annotations

import collections
import csv
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
SRC = HERE / "ukerc_2013_usable-energy-database_rows.csv"
DST = HERE / "ukerc_2013_usable-energy-database_citations.csv"
YEAR = re.compile(r"^\d{4}[a-z]?$")
SUFFIX = re.compile(r"^[a-z]$")


def parse(text: str) -> list[str]:
    out: list[str] = []
    stem = None                      # author of the last citation, for bare years
    full = None                      # author+year, for bare letter suffixes
    for chunk in text.split(";"):
        for frag in chunk.split(","):
            f = frag.strip().rstrip(".")
            if not f:
                continue
            if YEAR.match(f) and stem:
                if out and out[-1] == stem:
                    out.pop()        # the author was emitted alone; complete it
                out.append(f"{stem} {f}")
                full = out[-1]
                continue
            if SUFFIX.match(f) and full:
                out.append(re.sub(r"([a-z])?$", f, full, count=1)
                           if not full[-1].isalpha() or full[-1].isdigit()
                           else full[:-1] + f)
                continue
            out.append(f)
            m = re.match(r"(.*?)\s+\d{4}[a-z]?$", f)
            stem = m.group(1) if m else f
            full = f if m else None
    return out


# Short forms the data tables get wrong, resolved against the References tab and
# confirmed by the modeller 2026-08-28. Rewriting the citation here rather than
# aliasing later means the source-id and the short name are right everywhere.
CANONICAL = {
    "Novacem 2011a": "Novacem 2011",
    "NERA and EA 2009": "NERA and AEA 2009",
    "ECRA 2009b": "ECRA 2009",
    "IETD 2013": "IIP 2012",          # same database, two acronyms and two years
    "ITP 2012": "IIP 2012",           # Institute for Industrial Productivity
    "Fritzson et al 2006a": "Fritzson and Berntsson 2006a",
    "Fritzson et al 2006b": "Fritzson and Berntsson 2006b",
    "Normal 2013": "Norman 2013",     # UKERC's own author, his PhD thesis
    "NERA 2009": "NERA and AEA 2009", # confirmed by the modeller 2026-08-28
    # Four pairs the 2026-08-29 citation check confirmed are one document each,
    # merged on the modeller's instruction. The surviving short form is the one
    # the References tab itself uses, except IPPC 2012 -> EC 2012, where the tab
    # has both and "EC" names the issuer while "IPPC" names a directive.
    "Martin et al 2000b": "Martin et al 2000",   # both are LBNL-46990 / ACEEE IE003
    "ECRA 2009a": "ECRA 2009",                   # the tab has a single ECRA 2009 entry
    "Novacem 2011b": "Novacem 2011",             # both are the 31st CCSC paper
    "IPPC 2012": "EC 2012",                      # both are the iron and steel BREF
    # "Wheeler" is the affiliation Foster Wheeler mis-parsed as a second author.
    # Correcting the short form is what moves the id to collodi_2010_001; the
    # References tab still spells it the long way, which ALIAS handles.
    "Collodi and Wheeler 2010": "Collodi 2010",
    # One report, IEAGHG 2013/TR3 (user, 2026-11-04): the References tab lists it as
    # IEAGHG 2013a; the data tables also cite it unsuffixed and, misdated, as IEAGHG 2000.
    "IEAGHG 2000": "IEAGHG 2013a",
    "IEAGHG 2013": "IEAGHG 2013a",
}


def norm(c: str) -> str:
    c = re.sub(r"\s+", " ", c).strip()
    c = c.replace("et al.", "et al").replace("IEA GHG", "IEAGHG")
    return CANONICAL.get(c, c)


def source_id(cite: str) -> str:
    m = re.match(r"(.*?)\s+(\d{4})([a-z]?)$", cite)
    if not m:
        return "unattributed"
    author, year, suf = m.groups()
    slug = re.sub(r"[^a-z0-9]+", "-", author.lower()).strip("-")
    slug = slug.replace("-et-al", "").replace("-and-", "-")
    return f"{slug}_{year}_{'abcdefgh'.index(suf) + 2 if suf else 1:03d}"


def main() -> int:
    if not SRC.exists():
        sys.exit(f"{SRC.name} not found -- run ukerc-dump.py first")
    counts: collections.Counter = collections.Counter()
    raw_forms = collections.defaultdict(set)
    for r in csv.DictReader(SRC.open(encoding="utf-8-sig")):
        if r["column-name"] == "Reference" or "References related" in r["column-group"]:
            for c in parse(r["value"]):
                n = norm(c)
                counts[n] += 1
                raw_forms[n].add(r["value"].strip())
    rows = []
    for cite, n in counts.most_common():
        if cite.lower() in ("own calculation", "n/a", "-"):
            sid = ""
            note = "not an external citation; left with UKERC as the source"
        else:
            sid = source_id(cite)
            note = "" if sid != "unattributed" else "no year in the citation; needs a human"
        rows.append({"citation": cite, "source-id": sid, "rows-citing": n,
                     "raw-forms": " | ".join(sorted(raw_forms[cite])[:3]), "note": note})

    # Flag ids that probably name one document. 'NERA 2009', 'NERA and AEA 2009'
    # and 'NERA and EA 2009' are almost certainly the same report with a typo,
    # but merging them is a reading of the source, not a parsing rule.
    # An 'a'/'b' suffix is UKERC deliberately distinguishing two documents by the
    # same author in the same year -- not a duplicate. Only flag where the AUTHOR
    # text itself differs while the leading word and year agree.
    def author(c):
        return re.sub(r"\s+\d{4}[a-z]?$", "", c).strip().lower()

    stem = collections.defaultdict(set)
    for r in rows:
        if r["source-id"] and r["source-id"] != "unattributed":
            head = r["source-id"].split("_")[0].split("-")[0]
            stem[(head, r["source-id"].split("_")[1])].add(
                (r["source-id"], author(r["citation"])))
    for r in rows:
        if not r["source-id"] or r["source-id"] == "unattributed":
            continue
        key = (r["source-id"].split("_")[0].split("-")[0], r["source-id"].split("_")[1])
        me = author(r["citation"])
        others = sorted(sid for sid, a in stem[key] if a != me)
        if others:
            r["note"] = (r["note"] + "; " if r["note"] else "") + \
                        "possibly the same document as " + ", ".join(others) + \
                        " - merge only after checking UKERC's reference list"
    with DST.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["citation", "source-id", "rows-citing",
                                           "raw-forms", "note"])
        w.writeheader(); w.writerows(rows)
    ok = sum(1 for r in rows if r["source-id"] and r["source-id"] != "unattributed")
    print(f"{DST.name}: {len(rows)} distinct citations, {ok} with a minted source-id")
    for r in rows[:12]:
        print(f"   {r['rows-citing']:4d}  {r['citation'][:38]:38s} -> {r['source-id']}")
    odd = [r for r in rows if not r["source-id"] or r["source-id"] == "unattributed"]
    if odd:
        print(f"   {len(odd)} need attention: " +
              ", ".join(f"{r['citation']!r}" for r in odd))
    return 0


if __name__ == "__main__":
    sys.exit(main())
