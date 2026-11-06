"""Alberta drilling: metres and wells per year (ST59) and rigs active per year (ST49).

    python aer_drilling_summary.py <out.csv> <st59-folder> <st49-folder>

ST59 'AB Drilling Activity' sheet: the GRAND TOTAL row gives wells and metres by well type;
the last two columns are the all-type totals. ST49 daily spud lists (spudYYYY.zip of monthly
zips of daily .txt reports): each 'Drill To LD' or 'Resumption' line names a contractor and
rig number; a rig counts as active in a year if it has at least one such line. Lines
'Set Surface' are surface-casing pre-set rigs and are counted separately. ST59 counts legs and recompletions as wells (stated on
the AER ST59 page), so wells per rig overstates holes per rig; metres per rig is the
usable figure. ST59 well counts jump from 2021 to 2022, so read 2017-2021 with care.
"""
import sys, os, re, io, csv, glob, zipfile, collections, warnings
import pandas as pd

warnings.filterwarnings('ignore')
LINE = re.compile(r'^\S{2}/\S{2}-\S{2}-\S{3}-\S{3}\S*\s+.{33}\s+\d{7}\s+(\S{4})\s+(.{30})\s+(\d+)\s+(\d{2} \w{3} (\d{4}))'
                  r'.*?(Drill To LD|Resumption|Set Surface|Re-entry)\s*$')


def st59(folder):
    out = {}
    for f in glob.glob(os.path.join(folder, '*st59*.xls*')):
        y = re.search(r'_(20\d\d)_', os.path.basename(f)).group(1)
        df = pd.read_excel(f, sheet_name='AB Drilling Activity', header=None)
        for i in range(len(df)):
            if str(df.iloc[i, 0]).strip().upper() == 'GRAND TOTAL':
                vals = [v for v in df.iloc[i, 1:].tolist() if isinstance(v, (int, float)) and not pd.isna(v)]
                out[y] = (vals[-2], vals[-1])  # wells, metres (all types)
    return out


def st49(folder):
    rigs = collections.defaultdict(lambda: collections.Counter())
    for f in glob.glob(os.path.join(folder, '*st49*.zip')):
        z = zipfile.ZipFile(f)
        for n in z.namelist():
            inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
            for m in inner.namelist():
                for line in inner.read(m).decode('latin-1').splitlines():
                    mm = LINE.match(line)
                    if mm:
                        rigs[mm.group(5)][(mm.group(1), mm.group(3), mm.group(6))] += 1
    return rigs


if __name__ == '__main__':
    out = sys.argv[1]
    a = st59(sys.argv[2]); r = st49(sys.argv[3])
    with open(out, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['year', 'st59-wells', 'st59-metres', 'st49-rigs-drilling', 'st49-spud-lines-drilling',
                    'st49-rigs-set-surface', 'metres-per-active-rig', 'wells-per-active-rig'])
        for y in sorted(set(a) & set(r)):  # years with both reports
            drill = {(c, n) for (c, n, t) in r.get(y, {}) if t in ('Drill To LD', 'Resumption', 'Re-entry')}
            lines = sum(v for (c, n, t), v in r.get(y, {}).items() if t in ('Drill To LD', 'Re-entry'))
            ss = {(c, n) for (c, n, t) in r.get(y, {}) if t == 'Set Surface'}
            if len(drill) < 50:  # a year whose spud zip is missing leaves stray lines only
                continue
            wl, mt = a.get(y, ('', ''))
            w.writerow([y, wl, mt, len(drill) or '', lines or '', len(ss) or '',
                        round(mt / len(drill)) if mt and drill else '', round(wl / len(drill), 1) if wl and drill else ''])
