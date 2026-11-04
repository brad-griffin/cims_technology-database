"""Shared python-docx helpers for the review-package documents.

Content is a list of blocks:
    ("h1" | "h2" | "h3" | "p" | "lead", text)   lead = a paragraph kept with the next block
    ("bullets", items)                           items may nest one level (a list inside the list)
    ("numbered", items)
    ("table", widths_in_dxa, header, rows)
    ("gap",)
Inline markup in any text: **bold**, `code`, [[placeholder]] (highlighted).
"""
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Inches, Pt, RGBColor

FONT, MONO = "Arial", "Consolas"
EMBER, DARK, GREY = "971E00", "5A0C00", "7F7F7F"
DXA = 635  # EMU per twentieth of a point
KEEP_WHOLE_MAX_ROWS = 15  # tables with more body rows than this may break across pages
MARKUP = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\[\[[^\]]+\]\])")


def _rgb(hexs):
    return RGBColor.from_string(hexs)


def runs(par, text, size=None, bold=False, color=None):
    """Add text to a paragraph, honouring the inline markup."""
    for part in MARKUP.split(text):
        if not part:
            continue
        if part.startswith("**"):
            r = par.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`"):
            r = par.add_run(part[1:-1])
            r.font.name = MONO
            r.font.size = Pt((size or 10.5) - 1)
        elif part.startswith("[["):
            r = par.add_run("[" + part[2:-2] + "]")
            r.bold = True
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            r = par.add_run(part)
        if bold:
            r.bold = True
        if size and not part.startswith("`"):
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = _rgb(color)
    return par


def _style(doc, name, size, color, before, after, bold=True, keep=True):
    st = doc.styles[name]
    st.font.name, st.font.size, st.font.bold = FONT, Pt(size), bold
    st.font.color.rgb = _rgb(color)
    rfonts = st.element.get_or_add_rPr().get_or_add_rFonts()
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(k), FONT)
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(k)) is not None:
            del rfonts.attrib[qn(k)]
    pf = st.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    pf.keep_with_next = keep
    pf.keep_together = True


def _field(par, instr):
    for kind, text in (("begin", None), (None, instr), ("separate", None), (None, "1"), ("end", None)):
        r = par.add_run()
        r.font.size, r.font.color.rgb = Pt(8), _rgb(GREY)
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        elif text == instr:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = f" {instr} "
        else:
            el = OxmlElement("w:t")
            el.text = text
        r._r.append(el)


def _bottom_border(par, color=EMBER, size=8):
    ppr = par._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", str(size)), ("w:space", "6"), ("w:color", color)):
        b.set(qn(k), v)
    bdr.append(b)
    ppr.append(bdr)


def make_doc(title, subtitle, footer_text):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(1))
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(10.5)
    normal.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    _style(doc, "Title", 20, DARK, 0, 6)
    _style(doc, "Heading 1", 15, EMBER, 18, 7)
    _style(doc, "Heading 2", 12, DARK, 12, 5)
    _style(doc, "Heading 3", 10.5, "333333", 9, 4)
    for name in ("List Bullet", "List Bullet 2", "List Number"):
        doc.styles[name].font.name = FONT
        doc.styles[name].paragraph_format.space_after = Pt(3)
    doc.core_properties.title = title
    doc.core_properties.author = "EMRG technology database"
    # the default template draws a rule under Title; the subtitle carries ours
    tppr = doc.styles["Title"].element.get_or_add_pPr()
    for bdr in tppr.findall(qn("w:pBdr")):
        tppr.remove(bdr)
    t = doc.add_paragraph(style="Title")
    runs(t, title)
    st = doc.add_paragraph()
    runs(st, subtitle, size=11, color="5A5A5A")
    st.paragraph_format.space_after = Pt(12)
    _bottom_border(st)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = fp.add_run(f"{footer_text}  |  page ")
    r.font.size, r.font.color.rgb = Pt(8), _rgb(GREY)
    _field(fp, "PAGE")
    return doc


def _shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def table(doc, widths, header, rows):
    t = doc.add_table(rows=1, cols=len(widths))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    t.autofit = False
    tblpr = t._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, v in (("top", 50), ("bottom", 50), ("left", 100), ("right", 100)):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblpr.append(mar)
    hdr = t.rows[0]
    trpr = hdr._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trpr.append(th)
    for row in [header] + [list(r) for r in rows]:
        cells = hdr.cells if row is header else t.add_row().cells
        for i, (c, w) in enumerate(zip(cells, widths)):
            c.width = Emu(w * DXA)
            par = c.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
            if row is header:
                runs(par, str(row[i]), size=9, bold=True, color="FFFFFF")
                _shade(c, EMBER)
            else:
                runs(par, "" if row[i] is None else str(row[i]), size=9)
    for col, w in zip(t.columns, widths):
        col.width = Emu(w * DXA)
    # a row never breaks across pages; every row but the last keeps with the next, so a table that
    # fits on one page moves whole to the next page rather than splitting (Brad 2026-11-04)
    last = len(t.rows) - 1
    keep_whole = last <= KEEP_WHOLE_MAX_ROWS   # a long table starts where it is and breaks between rows
    for i, row in enumerate(t.rows):
        cs = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().insert(0, cs)   # cantSplit comes before tblHeader in the schema
        if keep_whole and i < last:
            for c in row.cells:
                for par in c.paragraphs:
                    par.paragraph_format.keep_with_next = True
    return t


def render(doc, blocks):
    for b in blocks:
        kind = b[0]
        if kind in ("h1", "h2", "h3"):
            doc.add_heading(b[1], level=int(kind[1]))
        elif kind in ("p", "lead"):
            par = runs(doc.add_paragraph(), b[1])
            if kind == "lead":
                par.paragraph_format.keep_with_next = True
        elif kind == "bullets":
            for item in b[1]:
                if isinstance(item, list):
                    for sub in item:
                        runs(doc.add_paragraph(style="List Bullet 2"), sub)
                else:
                    runs(doc.add_paragraph(style="List Bullet"), item)
        elif kind == "numbered":
            for item in b[1]:
                runs(doc.add_paragraph(style="List Number"), item)
        elif kind == "table":
            table(doc, b[1], b[2], b[3])
        elif kind == "gap":
            doc.add_paragraph().paragraph_format.space_after = Pt(0)
        else:
            raise ValueError(f"unknown block {kind}")
