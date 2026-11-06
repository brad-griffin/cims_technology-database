"""Flatten AER ST39 (Alberta Mineable Oil Sands Plant Statistics) workbooks to one long CSV.

    python aer_st39_parse.py <out.csv> <ST39-YYYY.xls> [...]

Each workbook's data sheet stacks one block per facility ("Operator - FacilityID Name"),
each with product sections ("Crude Bitumen (m³)", "Purchased Natural Gas (10³m³)",
"Electricity (MWh)", ...) and line items (Production, Fuel, Purchased, ...) by month with
an annual total in the last column. Writes facility-id, facility, operator, year, section,
unit, line, annual total.
"""
import re, sys, csv, warnings
import pandas as pd

warnings.filterwarnings('ignore')
HEAD = re.compile(r'^(?P<op>.+?) - (?P<id>ABOS\d+) (?P<name>.+)$')
SEC = re.compile(r'^(?P<sec>.+?) \((?P<unit>[^)]+)\)$')


def parse(path, w):
    xl = pd.ExcelFile(path)
    sheet = [s for s in xl.sheet_names if s.lower() != 'document map'][0]
    df = xl.parse(sheet, header=None)
    fac = sec = unit = year = None
    for _, r in df.iterrows():
        a = r.iloc[0]
        if isinstance(r.iloc[1], str) and r.iloc[1] == 'January':
            y = r.iloc[df.shape[1] - 1]
            year = str(int(y)) if not isinstance(y, str) else y
            continue
        if not isinstance(a, str):
            continue
        a = a.strip()
        m = HEAD.match(a)
        if m and pd.isna(r.iloc[1]):
            fac = m.groupdict(); sec = None; continue
        m = SEC.match(a)
        if m and pd.isna(r.iloc[1]):
            sec, unit = m['sec'], m['unit']; continue
        if fac and sec and year:
            tot = r.iloc[df.shape[1] - 1]
            if isinstance(tot, (int, float)) and not pd.isna(tot):
                w.writerow([fac['id'], fac['name'], fac['op'], year, sec, unit, a, tot])


if __name__ == '__main__':
    with open(sys.argv[1], 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['facility-id', 'facility', 'operator', 'year', 'section', 'unit', 'line', 'annual-total'])
        for p in sys.argv[2:]:
            parse(p, w)
