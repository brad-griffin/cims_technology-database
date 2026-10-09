"""The Excel workbook: written last, from the outputs, and never read back.

Banded sheets (the wide views, the archetype list and the source list) are laid
out like the UKTM sheet of the Bataille database: a teal header band with a
group band above it and a unit row below, each family as a large bold band row,
each equipment term as a bold `*` row beneath it, the rows indented under it.
The banding is the point: a banded sheet cannot be sorted or filtered without
breaking it, so it does not invite being used as a working table. The CSVs are
the machine-readable form. Every sheet opens at 75% zoom.
"""
from __future__ import annotations

import warnings

from .common import OUTPUT

ZOOM = 75
BOOK = OUTPUT / "technology-database.xlsx"
NUM_FORMAT = [(1000, "#,##0"), (100, "#,##0"), (10, "#,##0.0"),
              (1, "#,##0.00"), (0.1, "0.000"), (0.01, "0.0000")]
PLAIN_INT = {"trl", "year-available", "n-examples", "n"}
# identifiers and counts, not measurements: no thousands separator, no decimals
GENERAL = {"year", "rows-in-database"}
# columns whose values are left-justified whatever their type (trl mixes 9 and "5-8")
LEFT = {"trl"}
DETAIL = ("_low", "_high", "_n")


def _fmt(v, col):
    if col in GENERAL:
        return "General"
    if col in PLAIN_INT or col.endswith("_n"):
        return "0"
    a = abs(v)
    if a == 0:
        return "0"
    for lo, f in NUM_FORMAT:
        if a >= lo:
            return f
    return "0.00E+00"


def _cell(v):
    if not isinstance(v, str) or v == "":
        return v
    try:
        return int(v) if v.lstrip("-").isdigit() else float(v)
    except ValueError:
        return v


def _put(ws, r, j, v):
    """Write a cell; a string beginning with `=` stays text (openpyxl would
    otherwise store it as a formula, which Excel rejects on opening)."""
    cell = ws.cell(r, j, v)
    if isinstance(v, str) and v.startswith("="):
        cell.data_type = "s"
    return cell


def write_book(banded: dict, flat: dict, families: dict, notes: dict | None = None,
               flags: dict | None = None, grades: dict | None = None,
               grouped: set | None = None, band_notes: dict | None = None) -> str:
    """`grouped`: sheets whose _low, _high and _n columns are put in an Excel
    outline group beside their central column, folded when the book opens.
    `flags`: {sheet: {(archetype, column)}} -- cells shaded purple because
    their value rests on a conversion factor from outside the source.
    `grades`: {sheet: {(archetype, column): grade}} -- cells the fill step wrote,
    shaded by grade (identity blue, estimated orange, guess red)."""
    warnings.filterwarnings("ignore")
    import openpyxl
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    TEAL, TEAL_D = PatternFill("solid", fgColor="006666"), PatternFill("solid", fgColor="004D4D")
    # header of the folded _low/_high/_n columns (modeller 2026-10-09)
    DET, DET_D = PatternFill("solid", fgColor="5C7F9C"), PatternFill("solid", fgColor="45637C")
    BAND, WARN = PatternFill("solid", fgColor="E8F0EF"), PatternFill("solid", fgColor="FFF3CD")
    f_head, f_grp = Font(sz=12, bold=True, color="FFFFFF"), Font(sz=10, bold=True, color="FFFFFF", italic=True)
    f_unit, f_band = Font(sz=10, color="D6E6E6"), Font(sz=16, bold=True, color="1F3B57")
    f_sub, f_body = Font(sz=11, bold=True, color="0E5A4E"), Font(sz=11)
    f_warn = Font(sz=11, bold=True, color="7A5C00")
    f_note = Font(sz=10, italic=True, color="1F3B57")
    f_repeat = Font(sz=11, italic=True, color="7F7F7F")
    rule = Border(bottom=Side(style="thin", color="006666"))
    EXT_FILL = PatternFill("solid", fgColor="E4DFEC")      # sourced, external factor
    GRADE_FILL = {"identity": PatternFill("solid", fgColor="DDEBF7"),
                  "estimated": PatternFill("solid", fgColor="FCE4D6"),
                  "guess": PatternFill("solid", fgColor="F8CBAD")}

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name, (cols, rows, groups, units, band, sub, banner) in banded.items():
        ws = wb.create_sheet(name)
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 2.5
        first = 2
        ws.cell(1, 2, banner).font = f_warn
        for j in range(2, min(len(cols) + 2, 16)):
            ws.cell(1, j).fill = WARN
        ws.row_dimensions[1].height = 30
        for j, c in enumerate(cols, start=first):
            det = name in (grouped or ()) and c.endswith(DETAIL)
            for row_i, val, fill, font in ((3, groups.get(c, ""), DET_D if det else TEAL_D, f_grp),
                                           (4, c, DET if det else TEAL, f_head),
                                           (5, units.get(c, ""), DET if det else TEAL, f_unit)):
                cell = ws.cell(row_i, j, val)
                cell.fill, cell.font = fill, font
                cell.alignment = Alignment(horizontal="left", vertical="bottom", wrap_text=True)
                note = ((notes or {}).get(name) or {}).get(c) if row_i == 4 else None
                if note:
                    cell.comment = Comment(note, "technology database", width=320, height=160)
            ws.column_dimensions[get_column_letter(j)].width = (
                36 if j == first else 60 if c in ("full-citation", "applies-to", "description", "note")
                else max(10, min(20, len(c) + 3)))
        ws.row_dimensions[4].height = 46
        r, last_b, last_s = 7, None, None
        for row in rows:
            b, s = row.get(band, ""), row.get(sub, "") if sub else ""
            if b != last_b:
                r += 1
                ws.cell(r, first, families.get(b, b) or "(none)").font = f_band
                for j in range(first, len(cols) + first):
                    ws.cell(r, j).fill, ws.cell(r, j).border = BAND, rule
                if (band_notes or {}).get(b) and band == "family":
                    ws.cell(r, first + 1, band_notes[b]).font = f_note
                ws.row_dimensions[r].height = 22
                r += 1
                last_b, last_s = b, None
            if sub and s != last_s:
                ws.cell(r, first, f"*{s}").font = f_sub
                r += 1
                last_s = s
            for j, col in enumerate(cols, start=first):
                val = _cell(row.get(col, ""))
                cell = _put(ws, r, j, val)
                cell.font = f_repeat if row.get("_repeat") else f_body
                g = (grades or {}).get(name, {}).get((row.get("archetype"), col))
                if g in GRADE_FILL:
                    cell.fill = GRADE_FILL[g]
                elif (row.get("archetype"), col) in (flags or {}).get(name, ()):
                    cell.fill = EXT_FILL
                if j == first:
                    cell.alignment = Alignment(indent=1)
                elif isinstance(val, (int, float)) and not isinstance(val, bool):
                    cell.number_format = _fmt(val, col)
                    cell.alignment = Alignment(horizontal="left" if col in LEFT else "right")
                elif col in LEFT:
                    cell.alignment = Alignment(horizontal="left")
            r += 1
        ws.freeze_panes = ws.cell(6, first + 1).coordinate
        if name in (grouped or ()):
            # fold each parameter's _low/_high/_n run under its central column
            ws.sheet_properties.outlinePr.summaryRight = False
            run = []
            for j, c in enumerate(cols + [""], start=first):
                if c.endswith(DETAIL):
                    run.append(j)
                    continue
                if run:
                    ws.column_dimensions.group(get_column_letter(run[0]), get_column_letter(run[-1]),
                                               outline_level=1, hidden=True)
                    run = []
    for name, (cols, rows) in flat.items():
        ws = wb.create_sheet(name)
        ws.append(cols)
        for c in ws[1]:
            c.fill, c.font = TEAL, f_head
        for i, row in enumerate(rows, start=2):
            for j, c in enumerate(cols, start=1):
                _put(ws, i, j, _cell(row.get(c, "")))
        ws.freeze_panes = "B2"
        for j, c in enumerate(cols, start=1):
            ws.column_dimensions[get_column_letter(j)].width = max(10, min(40, len(c) + 4))
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = ZOOM
        ws.sheet_view.zoomScaleNormal = ZOOM
    try:
        wb.save(BOOK)
    except PermissionError:
        return "workbook is open in Excel; CSVs written, workbook not rebuilt"
    return f"{BOOK.name}: {len(wb.sheetnames)} sheets"
