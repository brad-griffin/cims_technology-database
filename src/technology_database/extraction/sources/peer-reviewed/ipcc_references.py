"""Pull the primary literature behind Table 11.3 out of the chapter's own reference list.

Run from the repo root:   python data/raw-data/peer-reviewed/ipcc-references.py

Table 11.3's footnotes cite about two dozen works by author and year. Those are
the originals under design doc D7, and none of them is held locally -- but the
chapter carries a full reference list with DOIs, so the citations do not have to
be guessed at or searched for. This reads that list and matches the short forms
the footnotes use, writing what it finds and, just as importantly, what it does
not.

The reference list is set in two columns with a hanging indent. Reading it with
a plain text dump interleaves the columns and mangles every entry, so each page
is split at the middle and the columns are read in order; an entry starts where
a line begins at the column's left margin and continues while lines are indented.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # extraction/
from paths import RECORDS, ROOT as REPO_ROOT, source_dirs  # noqa: E402
# documents in primary-sources/, extractions in data/raw_data/technology_database/ (2026-11-06)
DOCS, HERE = source_dirs(__file__)
PDF = DOCS / "ipcc_2022_ar6-wgiii-chapter11.pdf"
STEM = "ipcc_2022_ar6-wgiii-chapter11"

# The short forms Table 11.3's footnotes use, with the surname(s) to match on.
# Suffixed years (2014b, 2017a) are the chapter's own disambiguation and are
# matched loosely, because the reference list prints the suffix but the footnote
# sometimes does not.
WANTED = [
    ("Abbas and Wan Daud 2010", "Abbas", "2010"), ("Amin et al 2011", "Amin", "2011"),
    ("Armijo and Philibert 2020", "Armijo", "2020"), ("Ashik et al 2015", "Ashik", "2015"),
    ("Axelson et al 2018", "Axelson", "2018"),
    ("Bazzanella and Ausfelder 2017", "Bazzanella", "2017"),
    ("Birat 2012", "Birat", "2012"), ("De Luna et al 2019", "De Luna", "2019"),
    ("Fasihi et al 2019", "Fasihi", "2019"),
    ("Fechner and Kray 2012", "Fechner", "2012"),
    ("Fischedick et al 2014b", "Fischedick", "2014b"),
    ("Habert et al 2020", "Habert", "2020"), ("IEA 2018a", "IEA", "2018a"),
    ("IEA 2019f", "IEA", "2019f"), ("Keith et al 2018", "Keith", "2018"),
    ("Lehne and Preston 2018", "Lehne", "2018"), ("Leeson et al 2017", "Leeson", "2017"),
    ("Li et al 2019", "Li", "2019"), ("Moore 2017", "Moore", "2017"),
    ("Philibert 2017a", "Philibert", "2017a"), ("Philibert 2017b", "Philibert", "2017b"),
    ("van der Meijden et al 2011", "van der Meijden", "2011"),
    ("Vogl et al 2018", "Vogl", "2018"), ("Wilson et al 2003", "Wilson", "2003"),
]


def entries(pdf) -> list[str]:
    """Every reference-list entry, as one string each."""
    start = None
    for i, page in enumerate(pdf.pages):
        t = page.extract_text() or ""
        if re.search(r"^\s*References\s*$", t, re.M):
            start = i
    if start is None:
        return []
    out, cur = [], []
    for i in range(start, len(pdf.pages)):
        page = pdf.pages[i]
        mid = page.width / 2
        for lo, hi in ((0, mid), (mid, page.width)):
            col = page.crop((lo, 0, hi, page.height))
            words = col.extract_words()
            if not words:
                continue
            lines = {}
            for w in words:
                lines.setdefault(round(w["top"]), []).append(w)
            # The list has a hanging indent, so lines start at one of two
            # positions: the entry margin and the continuation indent. Take the
            # two commonest and use the smaller. The minimum is not safe -- the
            # chapter number sits in the outer margin, left of the text block,
            # and using it makes every real line look indented so a whole page
            # merges into one entry. The mode is not safe either: continuations
            # outnumber first lines, so it lands on the indent and every line
            # then starts a new entry.
            starts = collections.Counter(
                round(min(w["x0"] for w in ws)) for ws in lines.values())
            common = [x for x, _ in starts.most_common(2)]
            margin = min(common) if common else 0
            for y in sorted(lines):
                ws = sorted(lines[y], key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in ws)
                # A new entry starts flush with the column margin; a wrapped
                # line is indented under it.
                if ws[0]["x0"] < margin + 3:
                    if cur:
                        out.append(" ".join(cur))
                    cur = [text]
                elif cur:
                    cur.append(text)
    if cur:
        out.append(" ".join(cur))
    return [re.sub(r"\s+", " ", e).strip() for e in out]


def doi_of(entry: str) -> str:
    """The DOI at the end of a reference entry, rejoined across the line break.

    Elsevier DOIs wrap after the "10.1016/j." prefix, and the chapter's marginal
    page numbers and stray subscripts land in the gap, so the DOI arrives as
    "10.1016/j. 2 jclepro.2019.03.086. 11222299". Taking the first whitespace-
    delimited token gives "10.1016/j." and is wrong for a third of them.
    """
    m = re.search(r"doi:\s*(?:https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/\S*)(.*)$",
                  entry, re.I)
    if not m:
        return ""
    doi, rest = m.group(1), m.group(2)
    # Continue only while the DOI is obviously unfinished -- it ends on the
    # separator that split it -- and skip pure-digit tokens, which are page
    # numbers and subscripts rather than part of it.
    while doi.endswith((".", "/", "-")) and rest:
        tok, _, rest = rest.strip().partition(" ")
        if not tok:
            break
        if tok.isdigit():
            continue
        doi += tok
        break
    return doi.rstrip(".")


def main() -> int:
    try:
        import pdfplumber
    except ImportError:
        print("pdfplumber is required: pip install pdfplumber", file=sys.stderr)
        return 1
    with pdfplumber.open(PDF) as pdf:
        refs = entries(pdf)
    print(f"  reference list: {len(refs)} entries")

    rows, missed = [], []
    for short, surname, year in WANTED:
        # The chapter disambiguates same-author, same-year works with a letter
        # suffix, and the footnotes use it. Honour it: "IEA 2019f" is The Future
        # of Hydrogen, and nine other IEA 2019 entries are not.
        tail = str(year) + (r"(?![a-z])" if str(year)[-1].isdigit() else "")
        pat = re.compile(r"^" + re.escape(surname) + r"\b.{0,220}?\b" + tail + r"\s*:", re.S)
        hit = [e for e in refs if pat.match(e)]
        if not hit:
            missed.append(short)
            rows.append({"short-form": short, "full-citation": "", "doi": "",
                         "note": "not matched in the chapter's reference list"})
            continue
        for e in hit:
            rows.append({"short-form": short, "full-citation": e, "doi": doi_of(e),
                         "note": "" if len(hit) == 1 else
                                 f"{len(hit)} entries match {surname} {year}; "
                                 "the chapter's a/b suffix decides which"})
    p = HERE / f"{STEM}_cited-references.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["short-form", "full-citation", "doi", "note"])
        w.writeheader(); w.writerows(rows)
    got = sum(1 for r in rows if r["full-citation"])
    print(f"  {p.name:52} {len(rows):>4} rows, {got} matched, "
          f"{sum(1 for r in rows if r['doi'])} with a DOI")
    if missed:
        print("  not matched: " + ", ".join(missed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
