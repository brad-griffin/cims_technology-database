"""Write the BCER extraction (ETSAP-brief shape) from the held BCER data files.

    python bcer_extract.py

bcer_2026_gas-plant-capacity.csv: design raw-gas capacity of BC gas plants whose
process names an amine (MDEA, DEA, amine) -> capacity of gas-treatment-unit_amine-sweetening.
bcer_2026_drilling-data.zip (drill_ev.csv) and bcer_2026_hydraulic-fracture-data.zip
(hydraulic_fracture.csv): metres per active rig (the
contractor field carries the rig number) -> drilling-rig_diesel annual output; fracturing
size per well to _other-values only (no fleet identifier).
"""
import csv, io, os, zipfile, statistics, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = 'bcer_2026_gas-plant-and-well-statistics'


def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def g(x):
    return float('%.4g' % x)


def fnum(s):
    try:
        return float((s or '').replace(',', ''))
    except ValueError:
        return None


def main():
    lines = open(os.path.join(HERE, 'bcer_2026_gas-plant-capacity.csv'), encoding='latin-1').read().splitlines()
    amine = []
    for r in csv.DictReader(io.StringIO('\n'.join(lines[2:]))):
        v = fnum(r['Raw Gas (e3m3/d)'])
        pr = (r['Plant Process'] or '').lower()
        if v and v > 0 and ('amine' in pr or 'mdea' in pr or 'diethanol' in pr):
            amine.append(v)
    pr = 'British Columbia amine gas plants: design raw-gas capacity (BCER extract 16 Oct 2026)'
    T = 'gas-treatment-unit_amine-sweetening'
    rows = [[pr, T, 'description', '', '', 'Design raw-gas capacity of BC gas plants whose listed process is an amine.', '', '', '', '', ''],
            [pr, T, 'capacity', '', 'm3/d', g(q(amine, .5) * 1000), g(q(amine, .25) * 1000), g(q(amine, .75) * 1000),
             'median (p25-p75) of Raw Gas (e3m3/d) x 1000 over %d plants' % len(amine), 'BCER gas processing plants in British Columbia',
             'Design capacity, not throughput; operating status not given in the file. CAPACITY BASIS: product-output (gas processed).']]
    nodes = [[pr, T, 'oil-and-gas', 'natural-gas processing', '', 'm3']]
    other = []
    # drilling: metres per active rig (the contractor field carries the rig number, e.g. "PRECISION 533")
    z = zipfile.ZipFile(os.path.join(HERE, 'bcer_2026_drilling-data.zip'))
    rig_m = collections.defaultdict(lambda: collections.defaultdict(float)); depth = collections.defaultdict(list)
    with z.open('drill_ev.csv') as f:
        t = io.TextIOWrapper(f, encoding='latin-1'); t.readline()
        for r in csv.DictReader(t):
            try:
                b = datetime.datetime.strptime(r['Rig Rels Date'], '%Y%m%d')
            except (ValueError, KeyError):
                continue
            td = fnum(r['Td Depth (m)']); rig = ' '.join((r.get('Contrctr') or '').split())
            if td and td > 0 and rig and any(ch.isdigit() for ch in rig) and b.year in (2022, 2023, 2024, 2025):
                rig_m[b.year][rig] += td; depth[b.year].append(td)
    per = {y: sum(v.values()) / len(v) for y, v in rig_m.items()}
    prd = 'British Columbia drilling, metres per active rig, 2022-2025 (BCER drill_ev.csv)'
    rows += [[prd, 'drilling-rig_diesel', 'description', '', '', 'BC rigs: measured depth of wells released in the year, summed per rig (contractor and rig number), averaged over rigs.', '', '', '', '', ''],
             [prd, 'drilling-rig_diesel', 'annual-output', '', 'm', g(statistics.median(per.values())), g(min(per.values())), g(max(per.values())),
              'median over years of total measured depth / rigs that released a well (%s)' % '; '.join('%d: %d m / %d rigs' % (y, round(sum(rig_m[y].values())), len(rig_m[y])) for y in sorted(rig_m)),
              'BCER drill_ev.csv (Td Depth, Rig Rels Date, Contrctr)', 'Measured depth credited to the rig and year of rig release; a rig counts once per year. CAPACITY BASIS: product-output (metres drilled).']]
    nodes.append([prd, 'drilling-rig_diesel', 'oil-and-gas', 'drilling', '', 'm'])
    for y in sorted(rig_m):
        other.append([prd, 'drilling-rig_diesel', 'metres per active rig %d' % y, g(per[y]), 'm/yr', 'BCER drill_ev.csv',
                      '%d rigs; median well measured depth %s m' % (len(rig_m[y]), g(q(depth[y], .5)))])
    # fracturing
    z = zipfile.ZipFile(os.path.join(HERE, 'bcer_2026_hydraulic-fracture-data.zip'))
    wells = collections.defaultdict(lambda: [0.0, 0, 0.0, None])
    with z.open('hydraulic_fracture.csv') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='latin-1')):
            try:
                d = datetime.datetime.strptime(r['COMPLTN DATE'], '%d-%b-%y')
            except ValueError:
                continue
            if d.year not in (2022, 2023, 2024, 2025):
                continue
            w = wells[(r['WA NUM'], r['COMPLTN EVENT'])]
            w[0] += fnum(r['TOTAL FLUID PUMPED (m3)']) or 0; w[1] += 1
            w[2] += sum(fnum(r[k]) or 0 for k in ('PROPPANT TYPE1 PLACED (t)', 'PROPPANT TYPE2 PLACED (t)', 'PROPPANT TYPE3 PLACED (t)', 'PROPPANT TYPE4 PLACED (t)'))
            w[3] = d.year
    by = collections.defaultdict(list)
    for w in wells.values():
        by[w[3]].append(w)
    for y in sorted(by):
        v = by[y]
        other.append(['British Columbia hydraulic fracturing by completion year (hydraulic_fracture.csv)', 'fracturing-fleet_electric', 'wells fractured, %d' % y, len(v), 'wells',
                      'BCER hydraulic_fracture.csv', 'Median per well: %s stages, %s m3 fluid, %s t proppant. Not loaded: no fleet identifier.' % (
                          g(q([x[1] for x in v], .5)), g(q([x[0] for x in v], .5)), g(q([x[2] for x in v], .5)))])
    H = ['process', 'technology', 'parameter', 'target', 'unit', 'value', 'value-min', 'value-max', 'formula', 'reference', 'note']
    for suf, hdr, data in (('.csv', H, rows), ('_nodes.csv', ['process', 'technology', 'sector', 'end-use', 'process-step', 'service-unit'], nodes),
                           ('_other-values.csv', ['process', 'technology', 'item', 'value', 'unit', 'reference', 'note'], other)):
        with open(os.path.join(HERE, STEM + suf), 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh, lineterminator='\n'); w.writerow(hdr); w.writerows(data)
    for r in rows[1:] + other:
        print(r)


if __name__ == '__main__':
    main()
