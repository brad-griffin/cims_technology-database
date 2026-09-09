"""Build the source list: short form, full citation, and where each source is used.

Run from the repo root:   python data/harmonized/build-source-list.py

Writes source-list.csv, and adds it to the workbook as a banded sheet in the
same style as the wide views -- grouped by sector, so a reader can see at a
glance where a sector's numbers come from.

Full citations come from four places, in this order:
  1. source-citation.csv -- the verified record. Each row was checked against
     the publisher, repository or agency page and carries a DOI where one was
     seen verbatim, plus a verification status saying how far the check got.
     This is the citation the database prints.
  2. the References tab of the UKERC workbook, for the originals UKERC cites;
  3. the author/title/year already in data/raw-data/source-details_sources.csv, for
     the documents held locally;
  4. nothing -- the row says so rather than inventing one.

Where a verified citation exists, the string UKERC (or the manifest) recorded is
kept alongside it in citation-as-cited, so a reader can see what was corrected
and nothing is lost. A DOI is only ever what a fetched page showed: unconfirmed
means blank, never reconstructed.

The UKERC References tab is matched on its short form, which is where its typos
show up. Aliases below are cases where the tab and the data tables spell the
same document differently and the identity is not in doubt; anything less
certain is left unmatched and reported, not guessed.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workbook import apply_view

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
UKERC_XLSX = ROOT / "data" / "raw-data" / "other-reports" / "ukerc_2013_usable-energy-database.xlsx"
MANIFEST = ROOT / "data" / "raw-data" / "source-details_sources.csv"
MANIFEST_FILES = ROOT / "data" / "raw-data" / "source-details_files.csv"
CITES = (ROOT / "data" / "raw-data" / "other-reports"
         / "ukerc_2013_usable-energy-database_citations.csv")
VERIFIED = HERE / "source-citation.csv"

# Same document, spelled differently in the data tables and the References tab.
# Each is a transposition, a dropped letter or a missing 'et al'; none changes
# which document is meant.
ALIAS = {
    "IISI 1996": "ISII 1996",                       # tab transposes IISI
    "Stemmermann 2010": "Stemmermann et al. 2010",
    "Von Weizsacker 2009": "Von Weizsacker et al. 2009",
    "Duxon 2007": "Duxon and Provis 2007",
    "IIP 2012": "ITP 2012",                         # tab uses the older acronym
    "Collodi 2010": "Collodi and Wheeler 2010",     # tab keeps the mis-parsed author
}
# Full citations supplied by the modeller 2026-08-28 where the References tab
# could not resolve the short form. Recorded here, with their provenance, rather
# than left to a later reader to rediscover.
OVERRIDE = {
    "EC 2012": (
        "Joint Research Centre: Institute for Prospective Technological Studies, "
        "Aguado-Monsonet, M. A., Delgado Sancho, L., Remus, R. and Roudier, S., "
        "Best available techniques (BAT) reference document for iron and steel "
        "production - Industrial emissions Directive 2010/75/EU - Integrated "
        "pollution prevention and control, Publications Office, 2013, "
        "https://data.europa.eu/doi/10.2791/98516",
        "supplied by the modeller for the short form IPPC 2012, which was merged into EC 2012 on 2026-08-29; the References tab's nearest entry is the 2010 draft of the same BAT reference document"),
    "IEAGHG 2000": (
        'IEAGHG, "Current State of the Art Technology for Iron & Steel Production", '
        "2013-TR3, April 2013.",
        "supplied by the modeller. NOTE the short form says 2000 but the document "
        "is dated 2013 - the short form is UKERC's and is kept as the key so the "
        "data tables still resolve, but anyone citing this should use the 2013 date"),
}
UNRESOLVED = {
    "IEAGHG 2013": "cited without the a/b suffix the References tab requires; "
                   "could be either the CO2-capture overview or the iron and steel "
                   "CCS study",
}

# Ids left behind when a short form was canonicalised. They stay registered in
# the manifest (it is append-only and the history is worth keeping) but they are
# superseded, not pending.
SUPERSEDED = {
    "ietd_2013_001": "iip_2012_001", "itp_2012_001": "iip_2012_001",
    "fritzson_2006_002": "fritzson-berntsson_2006_002",
    "fritzson_2006_003": "fritzson-berntsson_2006_003",
    "novacem_2011_002": "novacem_2011_001",
    # merged 2026-08-29 after the citation check confirmed each pair is one document
    "martin_2000_003": "martin_2000_001",
    "ecra_2009_002": "ecra_2009_001",
    "novacem_2011_003": "novacem_2011_001",
    "ippc_2012_001": "ec_2012_001",
    # Renamed 2026-08-29: the issuer was misidentified, not the document.
    "nlr_2018_001": "nrel_2018_001",
    "collodi-wheeler_2010_001": "collodi_2010_001",
    # the held file is the 2024 edition, not the 2026 one it was registered as
    "iea_2026_002": "iea_2024_001",
    "nera-ea_2009_001": "nera-aea_2009_001",
    "nera_2009_001": "nera-aea_2009_001",
    "ecra_2009_003": "ecra_2009_002",
    "normal_2013_001": "norman_2013_001",
}


def key(c):
    c = re.sub(r"\s+", " ", str(c)).strip().rstrip(".")
    return c.replace("et al.", "et al").replace("IEA GHG", "IEAGHG").lower()


def ukerc_references():
    import openpyxl
    if not UKERC_XLSX.exists():
        return {}
    wb = openpyxl.load_workbook(UKERC_XLSX, read_only=True, data_only=True)
    if "References" not in wb.sheetnames:
        return {}
    out, sector = {}, ""
    for row in wb["References"].iter_rows(values_only=True):
        v = [("" if c is None else str(c).strip()) for c in row]
        a, b, c = (v + ["", "", ""])[:3]
        if a and not b and not c and a.lower() != "references":
            sector = a
            continue
        if b and c and b.lower() != "citation":
            out.setdefault(key(b), (re.sub(r"\s+", " ", c), sector))
    wb.close()
    return out


def manifest():
    src = {}
    if MANIFEST.exists():
        for d in csv.DictReader(MANIFEST.open(encoding="utf-8-sig")):
            if d.get("source_id"):
                src[d["source_id"]] = d
    files = collections.defaultdict(list)
    if MANIFEST_FILES.exists():
        for d in csv.DictReader(MANIFEST_FILES.open(encoding="utf-8-sig")):
            # A row with no file on disk is a registration, not a holding, and
            # must not make the source read as held locally.
            if d.get("source_id") and d.get("file_on_disk"):
                files[d["source_id"]].append(d["file_name"])
    return src, files


def compose(v: dict) -> str:
    """Author. Year. Title. Publisher. -- one house style for every source, so
    the list reads as one document rather than as UKERC's formatting plus ours.
    The DOI rides in its own column, not glued onto the end of the string."""
    bits = [v.get("verified-authors", ""), v.get("verified-year", ""),
            v.get("verified-title", ""), v.get("verified-publisher", "")]
    out = ". ".join(b.strip().rstrip(".") for b in bits if b.strip())
    return out + "." if out else ""


def main() -> int:
    refs = ukerc_references()
    verified = {r["source-id"]: r for r in
                csv.DictReader(VERIFIED.open(encoding="utf-8-sig"))} \
               if VERIFIED.exists() else {}
    src, files = manifest()
    cites = {r["source-id"]: r for r in csv.DictReader(CITES.open(encoding="utf-8"))
             if r["source-id"] and r["source-id"] != "unattributed"}

    R = lambda n: list(csv.DictReader((HERE / n).open(encoding="utf-8-sig")))
    nodes = {r["service-node"]: r for r in R("service-node.csv")}
    # A technology serves however many sectors it is applied to, so a source
    # behind it credits all of them, not whichever one the roster happened to
    # record first.
    tech_sectors = collections.defaultdict(set)
    for a in R("technology-application.csv"):
        sec = nodes.get(a["service-node"], {}).get("sector", "")
        if sec:
            tech_sectors[a["technology"]].add(sec)
    prio = {r["source-id"]: r for r in R("source-priority.csv")}

    used, vias, sectors = collections.Counter(), collections.Counter(), collections.defaultdict(set)
    through: dict[str, str] = {}   # original -> the compilation it came through
    # The roster counts too. A source whose only contribution is a column on the
    # technology row -- the IEA guide gives readiness levels and nothing else --
    # would otherwise read as "registered, not yet used" while sitting on 65
    # technologies.
    for r in R("technology.csv"):
        sid = (r.get("source-id") or "").strip()
        if sid:
            used[sid] += 1
            sectors[sid].update(tech_sectors.get(r["technology"], ()))
    for fn in ("tech-parameter.csv", "tech-flow.csv", "tech-constraint.csv"):
        for r in R(fn):
            sid = (r.get("source-id") or "").strip()
            if not sid:
                continue
            used[sid] += 1
            sectors[sid].update(tech_sectors.get(r["technology"], ()))
            if r.get("via-source-id"):
                vias[r["via-source-id"]] += 1
                through.setdefault(sid, r["via-source-id"])

    rows, unmatched = [], []
    for sid in sorted(set(used) | set(vias) | set(src)):
        m = src.get(sid, {})
        short = prio.get(sid, {}).get("short-name") or m.get("author") or sid
        cite_short = cites.get(sid, {}).get("citation", "")
        full, note = "", ""
        if cite_short and cite_short in OVERRIDE:
            full, note = OVERRIDE[cite_short]
        elif cite_short:
            hit = refs.get(key(cite_short)) or refs.get(key(ALIAS.get(cite_short, "")))
            if hit:
                full = hit[0]
                if cite_short in ALIAS:
                    note = (f"the References tab spells this {ALIAS[cite_short]!r} where the "
                            f"data tables spell it {cite_short!r}")
            else:
                note = UNRESOLVED.get(cite_short, "not found in the UKERC References tab")
                unmatched.append(cite_short)
        # The manifest row for a UKERC original is a registration stub, not a
        # citation. Composing one from it would put "CT 2011. CT 2011 - cited by
        # the UKERC Usable Energy Database" in a column headed full-citation.
        stub = "cited by the UKERC Usable Energy Database" in m.get("title", "")
        if not full and m and not stub:
            bits = [m.get("author", ""), m.get("year", ""), m.get("title", "")]
            inst = m.get("institution", "")
            if inst and inst != m.get("author"):
                bits.append(inst)
            full = ". ".join(b for b in bits if b)
        if sid in SUPERSEDED:
            rows.append({
                "source-id": sid, "short-name": short, "full-citation": "",
                "year": m.get("year", ""), "role": "superseded",
                "doi": "", "url": "", "verification": "",
                "held-locally": "no", "rows-in-database": 0, "sectors": "",
                "licence": "", "citation-as-cited": "",
                "note": f"superseded by {SUPERSEDED[sid]}; the short form it "
                                       "was minted from was a typo or a second name for the "
                                       "same document"})
            continue
        # "extracted directly" means a document we hold and read. A source that
        # only ever reaches the database through a compilation is cited BY it,
        # whichever compilation that is -- otherwise every original IPCC cites
        # reads as one we opened ourselves.
        via_of = through.get(sid)
        role = ("cited by UKERC" if cite_short else
                "compilation" if vias.get(sid) else
                f"cited by {prio.get(via_of, {}).get('short-name', via_of)}"
                if via_of else
                "extracted directly" if used.get(sid) else "registered, not yet used")
        v = verified.get(sid, {})
        as_cited = ""
        if v and compose(v):
            # The verified record supersedes whatever UKERC or the manifest said,
            # but only in the full-citation column: the string it replaces is kept
            # verbatim so any correction is visible rather than silent, and so a
            # reader tracing a number back to UKERC still recognises the wording.
            as_cited = full
            full = compose(v)
            if v.get("verification-note"):
                note = "; ".join(x for x in (note, v["verification-note"]) if x)
        year = (v.get("verified-year") or m.get("year", "")
                or (sid.split("_")[1] if "_" in sid else ""))
        rows.append({
            "source-id": sid, "short-name": short, "full-citation": full,
            "year": year,
            "doi": v.get("doi", ""), "url": v.get("url", ""),
            "verification": v.get("verification-status", "not checked"),
            "citation-as-cited": as_cited,
            "role": role,
            "held-locally": "yes" if files.get(sid) else "no",
            # primary attributions only: where UKERC cites several originals for
            # one value the first becomes the source and the rest are named in
            # the row's note, so a genuinely-used source can still show zero
            "rows-in-database": used.get(sid, 0) or vias.get(sid, 0),
            "sectors": ", ".join(sorted(sectors.get(sid, []))) or
                       ("all" if vias.get(sid) else ""),
            "licence": m.get("licence_type", ""),
            "note": note,
        })

    cols = ["source-id", "short-name", "full-citation", "year", "doi", "url",
            "verification", "role", "held-locally", "rows-in-database", "sectors",
            "licence", "citation-as-cited", "note"]
    with (HERE / "source-list.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    for r in rows:
        if not r["full-citation"] and not r["note"]:
            r["note"] = "no full citation available"
    have = sum(1 for r in rows if r["full-citation"])
    vc = collections.Counter(r["verification"] for r in rows if r["role"] != "superseded")
    print(f"  source-list.csv          {len(rows)} sources, {have} with a full citation")
    print(f"     {sum(1 for r in rows if r['role'] == 'cited by UKERC')} cited by UKERC, "
          f"{sum(1 for r in rows if r['held-locally'] == 'yes')} held locally")
    print(f"     verification: " + ", ".join(f"{n} {k}" for k, n in vc.most_common()))
    print(f"     {sum(1 for r in rows if r['doi'])} with a DOI, "
          f"{sum(1 for r in rows if r['url'])} with a landing page, "
          f"{sum(1 for r in rows if r['citation-as-cited'])} keeping the form as cited")
    if unmatched:
        print(f"     {len(unmatched)} short forms not matched in the References tab: "
              + ", ".join(sorted(set(unmatched))))
    add_sheet(rows, cols)
    return 0


def add_sheet(rows, cols) -> None:
    """Add the source list to the workbook, banded by sector the way the wide
    views are, so the two read as one document. A source used in several sectors
    appears under each, which is the point: the band answers 'where did this
    sector's numbers come from'."""
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb_path = HERE / "technology-database-template.xlsx"
    if not wb_path.exists():
        print("  workbook not found; CSV written only")
        return
    try:
        wb = openpyxl.load_workbook(wb_path)
    except PermissionError:
        print("  workbook is open in Excel; CSV written, sheet not added")
        return

    order = [r["sector"] for r in csv.DictReader(
        (HERE / "sector.csv").open(encoding="utf-8-sig"))]
    banded = []
    for sec in order + ["(not tied to one sector)"]:
        # Alphabetical within the sector band. The list is something a reader
        # looks a known source up in, so a name is easier to find than a rank;
        # rows-in-database is still on the row for anyone who wants the weight.
        for r in sorted(rows, key=lambda x: x["short-name"].lower()):
            secs = [s.strip() for s in r["sectors"].split(",") if s.strip()]
            if (sec in secs) or (sec == "(not tied to one sector)"
                                 and not secs):
                banded.append((sec, r))

    TEAL = PatternFill("solid", fgColor="006666")
    TEAL_D = PatternFill("solid", fgColor="004D4D")
    BAND = PatternFill("solid", fgColor="E8F0EF")
    WARN = PatternFill("solid", fgColor="FFF3CD")
    head_font = Font(sz=12, bold=True, color="FFFFFF")
    grp_font = Font(sz=10, bold=True, color="FFFFFF", italic=True)
    sector_font = Font(sz=16, bold=True, color="1F3B57")
    body_font = Font(sz=11)
    warn_font = Font(sz=11, bold=True, color="7A5C00")
    rule = Border(bottom=Side(style="thin", color="006666"))
    GROUP = {"source-id": "identity", "short-name": "identity", "year": "identity",
             "full-citation": "citation", "doi": "citation", "url": "citation",
             "verification": "citation", "citation-as-cited": "citation",
             "role": "provenance",
             "held-locally": "provenance", "rows-in-database": "provenance",
             "sectors": "provenance", "licence": "provenance", "note": "provenance"}
    WIDTH = {"source-id": 24, "short-name": 26, "full-citation": 96, "note": 60,
             "sectors": 26, "licence": 22, "doi": 28, "url": 44,
             "verification": 14, "citation-as-cited": 70}

    name = "source-list"
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2.5
    first = 2
    ws.cell(1, 2, "VIEW — generated by data/harmonized/build-source-list.py. Every source "
                  "behind the database, with its short form and full citation. A source used "
                  "in several sectors appears under each.")
    for j in range(2, min(len(cols) + 2, 10)):
        ws.cell(1, j).fill = WARN
    ws.cell(1, 2).font = warn_font
    ws.row_dimensions[1].height = 30

    for j, c in enumerate(cols, start=first):
        gc = ws.cell(3, j, GROUP.get(c, ""))
        gc.fill, gc.font = TEAL_D, grp_font
        gc.alignment = Alignment(horizontal="left", vertical="bottom", wrap_text=True)
        hc = ws.cell(4, j, c)
        hc.fill, hc.font = TEAL, head_font
        hc.alignment = Alignment(horizontal="left", vertical="bottom", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = WIDTH.get(c, 16)
    ws.row_dimensions[4].height = 30

    r_i, last = 6, None
    for sec, row in banded:
        if sec != last:
            r_i += 1
            c = ws.cell(r_i, first, sec)
            c.font = sector_font
            for j in range(first, len(cols) + first):
                ws.cell(r_i, j).fill = BAND
                ws.cell(r_i, j).border = rule
            ws.row_dimensions[r_i].height = 22
            r_i += 1
            last = sec
        for j, col in enumerate(cols, start=first):
            cell = ws.cell(r_i, j, row.get(col, ""))
            cell.font = body_font
            if col in ("full-citation", "note", "citation-as-cited", "url"):
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            if j == first:
                cell.alignment = Alignment(indent=1)
        r_i += 1
    ws.freeze_panes = ws.cell(6, first + 1).coordinate
    apply_view(wb)
    wb.save(wb_path)
    print(f"  workbook: source-list added, {len(banded)} banded rows "
          f"({len(wb.sheetnames)} sheets)")


if __name__ == "__main__":
    sys.exit(main())
