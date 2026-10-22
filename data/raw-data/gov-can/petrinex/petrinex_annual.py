"""Collapse Petrinex public conventional volumetric files to annual totals.

Reads the monthly Vol_YYYY-MM-<PR>.csv.zip files inside the Petrinex public-data
download zip (nested zips are read in memory, nothing is unpacked) and writes one
row per (facility, year, activity, product, from-to type) with the summed volume
and energy and the number of months reported.

    python petrinex_annual.py <download.zip> <out.csv> [YYYY ...]

Temperature activities (BH*, WHI*, WHO*) are skipped. Volumes keep Petrinex
units: gas e3m3, liquids m3, energy GJ. The output is a bulk extract (git-ignored);
petrinex_summary.py reduces it to the tracked subtype tables.
"""
import csv, io, sys, zipfile, collections

SKIP = ('BH', 'WHI', 'WHO')
KEEP_FROMTO = {'REC', 'DISP', 'INJ', 'PURREC', 'PURDISP'}


def main(src, out, years):
    z = zipfile.ZipFile(src)
    names = sorted(n for n in z.namelist() if n.startswith('Vol_'))
    if years:
        names = [n for n in names if n[4:8] in years]
    vol = collections.defaultdict(float)
    eng = collections.defaultdict(float)
    months = collections.defaultdict(set)
    fac = {}
    for n in names:
        inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
        for member in inner.namelist():
            with inner.open(member) as fh:
                rd = csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace'))
                for r in rd:
                    a = (r['ActivityID'] or '').strip()
                    if not a or a.startswith(SKIP):
                        continue
                    fid = r['ReportingFacilityID']
                    fac[fid] = (r['ReportingFacilityProvinceState'], r['ReportingFacilityType'],
                                r['ReportingFacilitySubType'], r['ReportingFacilitySubTypeDesc'],
                                r['ReportingFacilityName'], r['OperatorName'])
                    ft = r['FromToIDType'].strip() if a in KEEP_FROMTO else ''
                    k = (fid, r['ProductionMonth'][:4], a, (r['ProductID'] or '').strip(), ft)
                    try:
                        vol[k] += float(r['Volume'] or 0)
                    except ValueError:
                        pass
                    try:
                        eng[k] += float(r['Energy'] or 0)
                    except ValueError:
                        pass
                    months[k].add(r['ProductionMonth'])
        print(n, len(vol), flush=True)
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['facility-id', 'province', 'type', 'subtype', 'subtype-desc', 'facility-name',
                    'operator', 'year', 'activity', 'product', 'from-to-type', 'volume', 'energy-gj',
                    'months'])
        for k in sorted(vol):
            p = fac[k[0]]
            w.writerow([k[0], *p, k[1], k[2], k[3], k[4], round(vol[k], 3), round(eng[k], 3),
                        len(months[k])])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], set(sys.argv[3:]))
