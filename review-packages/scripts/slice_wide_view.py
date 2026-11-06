"""Write one review package's wide-view slice from the built workbook.

    python review-packages/scripts/slice_wide_view.py <package> [build-label]

Reads data/processed_data/technology_database/technology-database.xlsx (never edits it) and
writes review-packages/review-package_<package>/wide-view_<package>.xlsx.
"""
import copy
import csv
import sys
import warnings

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension

from package_map import EXCLUDE_BANDS, HARM, OUTPUT, PACKAGES, ROOT, load, row_nodes

warnings.filterwarnings("ignore")
FIRST_BODY = 8          # rows 1-7 are the banner and the header block
HEAD_ROW, GROUP_ROW = 4, 3
# the main workbook already splits energy, emissions and feedstocks (2026-11-04)
WIDE = ("archetypes", "energy", "emissions", "feedstocks")
# columns left out of the review files (Brad 2026-11-04)
DROP_COLS = {"families", "end-uses", "discriminator", "modifiers", "applies-to", "external-conversions",
             "source-corrections"}
BAND_LABELS = set()      # family labels, filled in main()


def keep_rows(ws, test, ctx, skip=()):
    """Row numbers to keep, plus (archetype, band) for each kept archetype row."""
    rows, fam, sub = {}, None, None
    kind = {}
    families = set(ctx[5])
    for r in range(FIRST_BODY, ws.max_row + 1):
        b, c = ws.cell(r, 2).value, ws.cell(r, 3).value
        if b is None:
            kind[r] = "blank"
        elif str(b).startswith("*"):
            kind[r], sub = "sub", str(b)[1:]
        elif c is None or b in families:   # a family band may carry a note in column C
            kind[r], fam = "family", b
        else:
            kind[r] = "row"
            nodes = row_nodes(str(b), sub, ctx, fam)
            if sub not in skip and (test is None or any(test(n) for n in nodes)):
                rows[r] = (str(b), sub)
    keep = set(range(1, FIRST_BODY)) | set(rows)
    # keep a band row when anything beneath it (before the next band of its level) is kept
    order = sorted(kind)
    for i, r in enumerate(order):
        if kind[r] in ("family", "sub"):
            for r2 in order[i + 1:]:
                if kind[r2] == "family" or (kind[r] == "sub" and kind[r2] == "sub"):
                    break
                if r2 in rows:
                    keep.add(r)
                    break
    # a blank spacer survives only when it separates two kept rows
    kept = sorted(keep)
    for r in order:
        if kind[r] == "blank":
            before = [k for k in kept if k < r]
            after = [k for k in kept if k > r]
            if before and after and before[-1] >= FIRST_BODY:
                keep.add(r)
    return keep, rows


def drop_rows(ws, keep):
    heights = {r: ws.row_dimensions[r].height for r in range(1, ws.max_row + 1)}
    drop = [r for r in range(1, ws.max_row + 1) if r not in keep]
    # delete in runs, bottom up
    runs, start, prev = [], None, None
    for r in drop:
        if start is None:
            start = prev = r
        elif r == prev + 1:
            prev = r
        else:
            runs.append((start, prev))
            start = prev = r
    if start is not None:
        runs.append((start, prev))
    for a, b in reversed(runs):
        ws.delete_rows(a, b - a + 1)
    for k in list(ws.row_dimensions):
        ws.row_dimensions[k].height = None
    for new, old in enumerate(sorted(keep), start=1):
        if heights.get(old):
            ws.row_dimensions[new].height = heights[old]


def insert_comment_column(ws, at=2):
    """A reviewer-comment column just before the archetype name, frozen with it (Brad 2026-11-04)."""
    dims = {}
    for k, d in ws.column_dimensions.items():
        lo, hi = d.min or openpyxl.utils.column_index_from_string(k), d.max or openpyxl.utils.column_index_from_string(k)
        for i in range(lo, hi + 1):
            dims[i] = (d.width, d.outlineLevel, d.hidden)
    ws.insert_cols(at)
    ws.column_dimensions.clear()
    for i, (w, lvl, hid) in sorted(dims.items()):
        j = i + 1 if i >= at else i
        cd = ColumnDimension(ws, index=get_column_letter(j), width=w, outlineLevel=lvl, hidden=hid)
        ws.column_dimensions[get_column_letter(j)] = cd
    ws.column_dimensions[get_column_letter(at)] = ColumnDimension(ws, index=get_column_letter(at), width=48)
    src_h, src_g = ws.cell(HEAD_ROW, at + 1), ws.cell(GROUP_ROW, at + 1)
    for r, src, val in ((HEAD_ROW, src_h, "reviewer-comment"), (GROUP_ROW, src_g, "review")):
        c = ws.cell(r, at)
        c.value = val
        c._style = copy.copy(src._style)
    for r in (5, 6, 7):
        ws.cell(r, at)._style = copy.copy(ws.cell(r, at + 1)._style)
    fill = PatternFill("solid", fgColor="FFFBEA")
    for r in range(FIRST_BODY, ws.max_row + 1):
        c = ws.cell(r, at)
        if ws.cell(r, 4).value is not None and ws.cell(r, 3).value not in BAND_LABELS:  # archetype rows
            c.fill = fill
            c.alignment = Alignment(wrap_text=True, vertical="top")
        else:                                       # band and spacer rows keep the band's look
            c._style = copy.copy(ws.cell(r, at + 1)._style)
    ws.freeze_panes = ws.cell(6, at + 2).coordinate


# the sector's own family goes in the top band (Brad 2026-11-03)
SECTOR_FAMILY = {"breweries": "food-and-beverage", "steel": "iron-and-steel", "pulp-and-paper": "pulp-and-paper",
                 "cement-and-lime": "cement-and-lime", "chemicals": "chemicals", "conventional-oil": "oil-and-gas",
                 "oil-sands": "oil-and-gas", "natural-gas": "oil-and-gas", "biofuels": "biofuels",
                 "hydrogen": "hydrogen", "mining": "mining", "aluminum": "non-ferrous-metals",
                 "petroleum-refining": "petroleum-refining"}
SPLIT = (("energy", "specific-energy-consumption",
          "Energy use by carrier, per product-unit, for the same rows as the archetypes sheet. The all-carrier "
          "total is on the archetypes sheet. Do not add the columns up: fuel is the sum of the named fuels beside it."),
         ("emissions", "emissions-",
          "Emissions by type and species, per product-unit, for the same rows as the archetypes sheet. "
          "CO2-equivalent totals are on the archetypes sheet."),
         ("feedstocks", "feedstock-consumption",
          "Feedstock use by carrier (feed whose energy ends up in the product, not counted as energy use), "
          "per product-unit, for the same rows as the archetypes sheet."))
IDENTITY_COLS = 5        # A spacer, archetype, label, product-unit, product


def _snapshot_row(ws, r, ncol):
    return [(c.value, copy.copy(c._style), c.comment, c.hyperlink)
            for c in (ws.cell(r, j) for j in range(1, ncol + 1))], ws.row_dimensions[r].height


def sector_family_first(ws, family_label, families):
    """Move the band of one family (with its sub-bands and rows) to the top of the body."""
    ncol, last = ws.max_column, ws.max_row
    kinds = {}
    for r in range(FIRST_BODY, last + 1):
        b, c = ws.cell(r, 2).value, ws.cell(r, 3).value
        kinds[r] = "blank" if b is None else ("family" if (c is None and not str(b).startswith("*")) or b in families
                                              else "other")
    starts = [r for r in range(FIRST_BODY, last + 1) if kinds[r] == "family"]
    if not starts or ws.cell(starts[0], 2).value == family_label:
        return
    blocks = []
    for i, a in enumerate(starts):
        b = (starts[i + 1] - 1) if i + 1 < len(starts) else last
        while b > a and kinds[b] == "blank":
            b -= 1
        blocks.append((a, b))
    sep = starts[1] - blocks[0][1] - 1 if len(starts) > 1 else 2
    target = [blk for blk in blocks if ws.cell(blk[0], 2).value == family_label]
    if not target:
        return
    order = target + [blk for blk in blocks if blk not in target]
    blank = _snapshot_row(ws, blocks[0][1] + 1, ncol) if sep else None
    new = []
    for i, (a, b) in enumerate(order):
        if i:
            new += [blank] * sep
        new += [_snapshot_row(ws, r, ncol) for r in range(a, b + 1)]
    for k, (cells, height) in enumerate(new):
        r = FIRST_BODY + k
        for j, (v, st, cm, hl) in enumerate(cells, start=1):
            cell = ws.cell(r, j)
            cell.value, cell._style = v, copy.copy(st)
            cell.comment = copy.copy(cm) if cm else None
            cell.hyperlink = hl
        ws.row_dimensions[r].height = height
    for r in range(FIRST_BODY + len(new), last + 1):
        for j in range(1, ncol + 1):
            ws.cell(r, j).value = None


def keep_columns(ws, keep):
    """Keep only the 1-based column numbers in `keep`, carrying widths and outline groups along."""
    dims = {}
    for k, d in ws.column_dimensions.items():
        lo = d.min or openpyxl.utils.column_index_from_string(k)
        hi = d.max or lo
        for i in range(lo, hi + 1):
            dims[i] = (d.width, d.outlineLevel, d.hidden)
    drop = [j for j in range(1, ws.max_column + 1) if j not in keep]
    runs = []
    for j in drop:
        if runs and j == runs[-1][1] + 1:
            runs[-1][1] = j
        else:
            runs.append([j, j])
    for a, b in reversed(runs):
        ws.delete_cols(a, b - a + 1)
    ws.column_dimensions.clear()
    for new, old in enumerate(sorted(keep), start=1):
        if old in dims:
            w, lvl, hid = dims[old]
            L = get_column_letter(new)
            ws.column_dimensions[L] = ColumnDimension(ws, index=L, width=w, outlineLevel=lvl, hidden=hid)


def split_carriers(wb, src_name):
    src = wb[src_name]
    made = []
    for name, prefix, banner in SPLIT:
        ws = wb.copy_worksheet(src)
        ws.title = name
        keep = set(range(1, IDENTITY_COLS + 1)) | {j for j in range(IDENTITY_COLS + 1, src.max_column + 1)
                                                   if str(src.cell(HEAD_ROW, j).value or "").startswith(prefix)}
        # copy_worksheet does not carry comments in every version; copy header notes by hand
        for j in keep:
            if src.cell(HEAD_ROW, j).comment:
                ws.cell(HEAD_ROW, j).comment = copy.copy(src.cell(HEAD_ROW, j).comment)
        keep_columns(ws, keep)
        ws["B1"].value = banner
        ws.freeze_panes = src.freeze_panes or "C6"
        ws.sheet_view.zoomScale = 75
        made.append(name)
    del wb[src_name]
    return made


def widen_notes(wb):
    """Header notes big enough to read the whole definition."""
    for ws in wb.worksheets:
        for c in ws[HEAD_ROW] if ws.max_row >= HEAD_ROW else []:
            if c.comment:
                n = len(c.comment.text)
                c.comment.width = 400  # VML pixels
                c.comment.height = max(90, 16 * (n // 45 + 2))


def legend_sheet(wb, sheets):
    ws = wb.create_sheet("column-legend", 1)
    rows = []
    for r in csv.DictReader(open(OUTPUT / "column-legend.csv", encoding="utf-8-sig")):
        if r["column"] in DROP_COLS:
            continue
        if r["sheet"] == "archetypes":
            rows.append(r)
        elif r["sheet"] == "carriers-species":
            for name, prefix, _ in SPLIT:
                if r["column"].startswith(prefix):
                    rows.append(dict(r, sheet=name))
    hdr = ["sheet", "column", "group", "unit", "note"]
    ws.append(["Column legend: every column of the database sheets, its group, unit, and definition. "
               "Columns ending _low, _high, and _n are folded beside their central column."])
    ws.append([])
    ws.append(hdr)
    ws.append(["archetypes", "reviewer-comment", "review", "", "Your comments on the row: see the reviewer guide."])
    for r in rows:
        ws.append([r[h] for h in hdr])
    ws["A1"].font = Font(sz=11, italic=True)
    head = PatternFill("solid", fgColor="971E00")
    for c in ws[3]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), head
    for col, w in zip("ABCDE", (22, 48, 16, 18, 110)):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=4):
        row[4].alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "C4"
    ws.sheet_view.zoomScale = 75


def readme(ws, package, title, build, sheets, n_rows, n_arch):
    # the main readme's sheet list and CSV section start at row 29; the package
    # writes its own sheet list there (merged paragraph rows unmerged first)
    for m in [m for m in ws.merged_cells.ranges if m.min_row >= 29]:
        ws.unmerge_cells(str(m))
    for row in ws.iter_rows(min_row=29, max_row=ws.max_row):
        for c in row:
            c.value = None
    ws["B2"].value = f"Technology database review package: {title}"
    ws["B4"].value = (f"A read-only extract of the technology database for external review, built {build}. "
                      f"It holds {n_arch} archetypes in {n_rows} rows (an archetype serving several "
                      "end uses appears under each). Write comments in the reviewer-comment column of "
                      "the archetypes sheet, and see the reviewer guide for what to check.")
    ws["B4"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["B12"].value = "Hover over a column heading for its definition, or see the column-legend sheet."
    if str(ws["B17"].value or "").startswith("The bands break sorting"):
        ws["B17"].value = ("The bands break sorting and filtering, so the sheets are for reading. Ask us if you "
                           "would like the values as flat tables.")
    if package in SECTOR_FAMILY and ws["B15"].value:
        ws["B15"].value = ("In this file the sector's own family is the top band, followed by the shared services "
                           "and any other families. " + ws["B15"].value)
    bold = copy.copy(ws["B19"]._style)
    ws["B29"].value, ws["B29"]._style = "Sheets", bold
    notes = {"archetypes": "One row per archetype in each end use: the main parameters, with the reviewer-comment column.",
             "column-legend": "Every column, its group, unit, and definition.",
             "energy": "Energy use by carrier, for the same rows.",
             "emissions": "Emissions by type and species, for the same rows.",
             "feedstocks": "Feedstock use by carrier, for the same rows.",
             "source-list": "Every source in the database, by the family it informs."}
    for i, s in enumerate(sheets):
        ws.cell(30 + i, 2).value = s
        ws.cell(30 + i, 3).value = notes[s]


def main(package, build):
    title, test = PACKAGES[package]
    ctx = load()
    wb = openpyxl.load_workbook(OUTPUT / "technology-database.xlsx")
    wanted = ["readme", *WIDE] + (["source-list"] if package == "whole-database" else [])
    for s in list(wb.sheetnames):
        if s not in wanted:
            del wb[s]
    counts = {}
    for s in WIDE:
        ws = wb[s]
        keep, rows = keep_rows(ws, test, ctx, EXCLUDE_BANDS.get(package, set()))
        drop_rows(ws, keep)
        counts[s] = rows
    if package in SECTOR_FAMILY:
        famlabel = {v: k for k, v in ctx[5].items()}[SECTOR_FAMILY[package]]
        for s in WIDE:
            sector_family_first(wb[s], famlabel, set(ctx[5]))
    wa = wb["archetypes"]
    keep_columns(wa, {j for j in range(1, wa.max_column + 1) if wa.cell(HEAD_ROW, j).value not in DROP_COLS})
    BAND_LABELS.update(ctx[5])
    insert_comment_column(wa)
    wb["archetypes"]["B1"].value = None           # the comment column; the banner moved to C1
    wb["archetypes"]["C1"].value = ("One row per archetype in each end use it serves. Capacity is in the unit named in "
                                    "capacity-unit; energy use by carrier, emissions by species, and feedstocks are on "
                                    "the energy, emissions, and feedstocks sheets.")
    split = [name for name, _, _ in SPLIT]
    legend_sheet(wb, WIDE)
    widen_notes(wb)
    for n in ["archetypes", *split]:
        wb[n].sheet_view.showGridLines = False
    sheets = ["column-legend", "archetypes", *split] + (
        ["source-list"] if package == "whole-database" else [])
    rows = counts["archetypes"]
    readme(wb["readme"], package, title, build, sheets, len(rows), len({a for a, _ in rows.values()}))
    # sheet order: readme, column-legend, archetypes, energy, emissions, feedstocks[, source-list]
    wb._sheets = [wb[s] for s in ["readme"] + sheets]
    wb.active = 2
    out = ROOT / "review-packages" / f"review-package_{package}" / f"wide-view_{package}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    arch = sorted({a for a, _ in rows.values()})
    with open(out.parent.parent / "scripts" / f"rows_{package}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["archetype", "band"])
        w.writerows(sorted(rows.values()))
    print(package, "rows", len(rows), "archetypes", len(arch), "->", out.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "2026-11-03")
