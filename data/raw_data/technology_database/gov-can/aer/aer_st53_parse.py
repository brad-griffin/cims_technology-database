"""Flatten AER ST53 (Alberta In Situ Oil Sands Summary) December workbooks to one long CSV.

    python aer_st53_parse.py <out.csv> <ST53_YYYY-12.xls> [...]

Sheets BITUMEN, WATER, STEAM (rates per calendar day, m3), WELLS (counts), SOR and WSR
(ratios). For each scheme row writes operator, scheme, area, approval, recovery method,
year, sheet, the 12 monthly values' mean and the number of months with data.
"""
import sys, csv, re, warnings
import pandas as pd

warnings.filterwarnings('ignore')
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def parse(path, w):
    xl = pd.ExcelFile(path)
    for sh in xl.sheet_names:
        df = xl.parse(sh, header=None)
        title = ' '.join(str(x) for x in df.iloc[:2, 0].tolist())
        m = re.search(r'(20\d\d)', title)
        year = m.group(1) if m else ''
        hdr = None
        for i in range(min(10, len(df))):
            row = [str(x).strip() for x in df.iloc[i].tolist()]
            if 'Operator' in row and 'Jan' in row:
                hdr = i; cols = row; break
        if hdr is None:
            continue
        mi = [cols.index(x) for x in MONTHS if x in cols]
        for i in range(hdr + 1, len(df)):
            r = df.iloc[i]
            op = r.iloc[cols.index('Operator')]
            if not isinstance(op, str) or op.lower().startswith(('total', 'note', '(')):
                continue
            vals = [r.iloc[j] for j in mi]
            vals = [float(v) for v in vals if isinstance(v, (int, float)) and not pd.isna(v)]
            if not vals:
                continue
            g = lambda k: r.iloc[cols.index(k)] if k in cols else ''
            w.writerow([year, sh, op.strip(), g('Scheme Name'), g('Area'), g('Approval Number'),
                        g('Recovery Method'), round(sum(vals) / len(vals), 4), len(vals)])


if __name__ == '__main__':
    with open(sys.argv[1], 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['year', 'sheet', 'operator', 'scheme', 'area', 'approval', 'recovery-method',
                    'monthly-mean', 'months'])
        for p in sys.argv[2:]:
            parse(p, w)
