// Shared helpers for the review-package documents (docx-js).
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, LevelFormat, Footer, Header, PageNumber, BorderStyle, HeadingLevel,
} = require("docx");

const FONT = "Arial";
const MONO = "Consolas";
const W = 9360; // text width on US Letter with 1-inch margins (DXA)
const EMBER = "971E00";

// inline markup: **bold**, `code`, [[placeholder]] (highlighted)
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\[\[[^\]]+\]\])/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: 19, ...base }));
    else out.push(new TextRun({ text: "[" + t.slice(2, -2) + "]", highlight: "yellow", bold: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

const p = (t, o = {}) => new Paragraph({ children: runs(t), spacing: { after: 120 }, ...o });
const lead = (t) => p(t, { keepNext: true });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const h3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const bullets = (items, level = 0) => items.map((t) => Array.isArray(t)
  ? bullets(t, level + 1) : new Paragraph({ numbering: { reference: "bullets", level }, children: runs(t), spacing: { after: 60 } })).flat();
const numbered = (items, ref = "numbers") => items.map((t) =>
  new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), spacing: { after: 60 } }));

const border = { style: BorderStyle.SINGLE, size: 4, color: "BFB5AE" };
const borders = { top: border, bottom: border, left: border, right: border };

// widths: array of DXA summing to W; header: array of strings; rows: array of arrays of strings
function table(widths, header, rows, opts = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, head) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { fill: EMBER, type: ShadingType.CLEAR, color: "auto" } : (opts.shade ? { fill: opts.shade, type: ShadingType.CLEAR, color: "auto" } : undefined),
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: runs(String(t ?? ""), head ? { bold: true, color: "FFFFFF", size: 18 } : { size: 18 }) })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, widths[i], false)) }))],
  });
}
const gap = () => new Paragraph({ children: [], spacing: { after: 120 } });

function doc(title, subtitle, footerText, children) {
  const heading = (size, before, after, color = EMBER) => ({
    run: { font: FONT, size, bold: true, color }, paragraph: { spacing: { before, after }, keepNext: true, keepLines: true },
  });
  return new Document({
    creator: "EMRG technology database", title,
    styles: {
      default: { document: { run: { font: FONT, size: 21 }, paragraph: { spacing: { line: 276 } } } },
      paragraphStyles: [
        { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONT, size: 40, bold: true, color: "5A0C00" }, paragraph: { spacing: { before: 0, after: 120 } } },
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, ...heading(30, 360, 140), paragraph: { spacing: { before: 360, after: 140 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, ...heading(24, 240, 100, "5A0C00"), paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, ...heading(21, 180, 80, "333333"), paragraph: { spacing: { before: 180, after: 80 }, keepNext: true, keepLines: true, outlineLevel: 2 } },
      ],
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [0, 1].map((l) => ({ level: l, format: LevelFormat.BULLET, text: l ? "–" : "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360 * (l + 1), hanging: 260 } } } })) },
        ...["numbers", "numbers2", "numbers3"].map((ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] })),
      ],
    },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
        new TextRun({ text: footerText + "  |  page ", size: 16, color: "7F7F7F" }),
        new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "7F7F7F" })] })] }) },
      children: [
        new Paragraph({ style: "Title", children: [new TextRun(title)] }),
        new Paragraph({ children: [new TextRun({ text: subtitle, color: "5A5A5A", size: 22 })], spacing: { after: 240 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: EMBER, space: 6 } } }),
        ...children,
      ],
    }],
  });
}

async function save(d, path) {
  fs.mkdirSync(require("path").dirname(path), { recursive: true });
  fs.writeFileSync(path, await Packer.toBuffer(d));
  console.log("wrote", path);
}

module.exports = { lead, p, h1, h2, h3, bullets, numbered, table, gap, doc, save, W };
