"""Dump Table 11.3 of IPCC AR6 WGIII Chapter 11 faithfully, one row per row.

Run from the repo root:   python data/raw-data/peer-reviewed/ipcc-dump.py
Needs pdfplumber (pip install pdfplumber).

Table 11.3, "Technological potentials and costs for deep decarbonisation of
basic industries", is the chapter's quantitative technology table: 47 rows over
two pages, giving for each option a potential GHG reduction, a NASA TRL, an
abatement cost in USD2019 per tonne CO2-eq, and a year it is expected to be
available. It is the only table in the chapter at technology resolution.

The table is ruled, so pdfplumber's line-based detection reads it cleanly and no
column geometry has to be guessed. Two things still need handling:

  * A bare sector name on its own row opens a block (Iron and steel, Cement and
    concrete, ...). Forward-filled into a column here.
  * The continuation page repeats the header row. Dropped by matching the header
    text, not by row number, so the dump does not break if pagination changes.

Superscript footnote letters are glued onto the option text by the PDF's own
encoding ("Hisarna with concentrated CO2 captureb"). They are split off into
their own column and the footnote bodies are dumped beside them, because each
names the primary literature the row's numbers come from and that is the
two-level attribution the database wants (design doc D7).

Splitting them on the TEXT is not safe and quietly corrupts data: the first
attempt stripped a trailing letter a-o, which turned "availability of DRI for
dilution" into "...dilutio" with a footnote "n" that does not exist. The marker
is identified by TYPOGRAPHY instead -- a character set markedly smaller than the
cell's body size. Subscripts are small too, so the rule also requires the
character to be a letter; every subscript in this table is a digit (CO2, CH4).
Nor is the marker last in reading order: a raised character sorts above the line
it belongs to, so "CO2 captureb" yields its "b" first and its subscript "2"
last.

Everything else is written exactly as the cell holds it. The chapter prints
subscripts and superscripts as ordinary characters, so "tCO-eq t-1 2" in a
header is the PDF's rendering of tCO2-eq per tonne, not a typo introduced here.
"""
from __future__ import annotations

import collections
import csv
import re
import statistics
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

COLS = ["option", "current-intensity", "potential-ghg-reduction", "nasa-trl",
        "abatement-cost", "year-available"]
# The blocks that open a sector, exactly as the table prints them.
SECTORS = {
    "Iron and steel", "Cement and concrete",
    "Aluminium and other non-ferrous metals",
    # Printed with a trailing "i" at FULL size, not as a raised marker, so the
    # typographic rule above cannot strip it and the band text keeps it.
    "Chemicals (see also cross-cutting feedstocks above)i",
    "Pulp and paper", "Other manufacturing",
    "Cross-cutting (CCUS, H2, net zero CoOxHy fuels/feedstocks)",
}
MARKERS = set("abcdefghijklmno")   # the letters Table 11.3 actually uses
SMALL = 0.85                       # of the cell's body size: below this is raised


def option_and_marker(page, cell) -> tuple[str, str]:
    """The option text and its footnote letter, read from the glyphs.

    Both come out of the same character list so the marker can be dropped by
    identity. Cutting it out of the extracted string instead removes the first
    letter that looks like it, which turned "(e.g., SIDERWIN)" into "(.g.,
    SIDERWIN)" and "multi-sized" into "multi-size".
    """
    from pdfplumber.utils import extract_text
    chars = page.crop(cell).chars
    if not chars:
        return "", ""
    body = collections.Counter(round(c["size"], 2) for c in chars).most_common(1)[0][0]
    # Small AND RAISED. "Subscripts are digits" is not true here: the o in
    # "CoOxHy" is a lowered letter, and stripping it as a marker turned the
    # cross-cutting sector band into "net zero COxHy". The two are cleanly
    # separated by where they sit relative to the baseline of the body text on
    # the same line: in this PDF a marker's bottom is about 3pt above it and a
    # subscript's about 0.9pt below.
    def baseline(c):
        near = [f["bottom"] for f in chars
                if round(f["size"], 2) >= body * SMALL
                and abs(f["bottom"] - c["bottom"]) < body]
        return statistics.median(near) if near else None

    def raised(c):
        b = baseline(c)
        return b is not None and c["bottom"] < b - 1.0
    small = [c for c in chars
             if c["size"] < body * SMALL and c["text"].lower() in MARKERS and raised(c)]
    note = small[-1]["text"].lower() if small else ""
    keep = [c for c in chars if c is not (small[-1] if small else None)]
    return clean(extract_text(keep)), note


def clean(c) -> str:
    return re.sub(r"\s+", " ", (c or "").replace("\n", " ")).strip()


def footnotes(pdf, pages: list[int]) -> list[dict]:
    """The a-o notes printed under the table, each naming the primary sources.

    Bounded by LAYOUT, not by line count or type size. The notes are set at the
    same size as the body text that follows them, but they run the full width of
    the page where the body is in two columns. The block therefore ends at the
    first line that starts in the right-hand column. Reading whole lines to the
    end of the page instead let the last note swallow the paragraph after it.
    """
    text = ""
    for i in pages:
        page = pdf.pages[i]
        below = max((t.bbox[3] for t in page.find_tables()), default=0)
        mid = page.width / 2
        # Cluster words into visual lines with a tolerance. A superscript sits a
        # point or two above the line it belongs to, so keying on the exact top
        # splits "a" onto a line of its own and the footnote it labels onto the
        # next -- which makes every note look unlabelled.
        left = min((t.bbox[0] for t in page.find_tables()), default=0)
        words = sorted((w for w in page.extract_words()
                        if w["top"] > below and w["x0"] > left - 10),
                       key=lambda w: w["top"])
        lines, cur, anchor = [], [], None
        for w in words:
            if anchor is not None and w["top"] - anchor > 3:
                lines.append(cur); cur = []
            if not cur:
                anchor = w["top"]
            cur.append(w)
        if cur:
            lines.append(cur)
        # Orphaned subscripts land on lines of their own (a "2" from tCO2-eq that
        # sits too low to cluster), and one of them starts right of centre. Used
        # raw as the column test they end the block six notes early, so a break
        # needs a line with real words on it.
        merged = []
        for ws in lines:
            if merged and len(ws) == 1 and len(ws[0]["text"]) <= 2:
                merged[-1].extend(ws)
            else:
                merged.append(list(ws))
        # Two ways the block ends, and the last note needs both. The body may
        # resume in the right-hand column, or -- as it does here after note o --
        # in the left, separated only by white space. So also stop at the first
        # gap much larger than the block's own line spacing.
        tops = [min(w["top"] for w in ws) for ws in merged]
        gaps = [b - a for a, b in zip(tops, tops[1:])]
        typical = statistics.median(gaps) if gaps else 0
        for k, ws in enumerate(merged):
            if len(ws) >= 4 and min(w["x0"] for w in ws) > mid:
                break                            # the two-column body has begun
            if k and typical and (tops[k] - tops[k - 1]) > typical * 1.8:
                break                            # a paragraph break, not a wrap
            text += " ".join(w["text"] for w in sorted(ws, key=lambda w: w["x0"])) + "\n"
    out, cur, letter = [], [], ""
    for line in text.splitlines():
        m = re.match(r"^\s*([a-o])\s+(?=[A-Z(])(.*)$", line)
        if m:
            if letter:
                out.append({"footnote": letter, "text": clean(" ".join(cur))})
            letter, cur = m.group(1), [m.group(2)]
        elif letter and line.strip() and not line.strip().startswith("Table 11.3"):
            cur.append(line)
    if letter:
        out.append({"footnote": letter, "text": clean(" ".join(cur))})
    return out


def main() -> int:
    try:
        import pdfplumber
    except ImportError:
        print("pdfplumber is required: pip install pdfplumber", file=sys.stderr)
        return 1
    if not PDF.exists():
        print(f"not found: {PDF}", file=sys.stderr)
        return 1

    rows, sector, pages = [], "", []
    with pdfplumber.open(PDF) as pdf:
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ""
            if "Table 11.3 |" in t or "Direct air capture for short" in t:
                pages.append(i)
        for i in pages:
            for tbl in pdf.pages[i].find_tables():
                extracted = tbl.extract()
                for ri, r in enumerate(extracted):
                    cells = [clean(c) for c in r]
                    if cells[0] == "Sector":          # the repeated header
                        continue
                    opt, note = cells[0], ""
                    box = tbl.rows[ri].cells[0] if ri < len(tbl.rows) else None
                    if box:
                        got, note = option_and_marker(pdf.pages[i], box)
                        opt = got or opt
                    # A sector band carries a footnote marker too -- the
                    # Chemicals band is printed "...feedstocks above)i" -- so it
                    # has to be stripped before the band is recognised, not
                    # after, or the band never matches and its whole block is
                    # dropped.
                    if opt in SECTORS or (opt and not any(cells[1:])):
                        sector = opt
                        continue
                    rows.append({"page": i + 1, "sector": sector, "option": opt,
                                 "footnote": note,
                                 **{c: cells[j] for j, c in enumerate(COLS)
                                    if c != "option" and j < len(cells)}})
        notes = footnotes(pdf, pages)

    field = ["page", "sector", "option", "footnote"] + COLS[1:]
    p = HERE / f"{STEM}_table-11-3.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=field)
        w.writeheader(); w.writerows(rows)
    print(f"  {p.name:52} {len(rows):>4} rows")

    p = HERE / f"{STEM}_table-11-3-footnotes.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["footnote", "text"])
        w.writeheader(); w.writerows(notes)
    print(f"  {p.name:52} {len(notes):>4} rows")

    with (HERE / f"{STEM}_meta.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parameter", "value"])
        w.writerow(["source-id", "ipcc_2022_001"])
        w.writerow(["table", "Table 11.3"])
        w.writerow(["currency", "2019_USD"])
        w.writerow(["cost-note", "costs are per tonne of CO2-eq abated, not per "
                                 "unit of capacity or output"])
        w.writerow(["potential-note", "percentages of maximum reduction are "
                                      "multiplicative, not additive (table caption)"])
        w.writerow(["trl-note", "the table's TRL scale is the NASA scale, stated "
                                "in the column heading"])

    have = sum(1 for r in rows if r["nasa-trl"])
    print(f"\n  {len(rows)} options across {len({r['sector'] for r in rows})} sectors, "
          f"{have} with a TRL, {sum(1 for r in rows if r['footnote'])} with a footnote")
    return 0


if __name__ == "__main__":
    sys.exit(main())
