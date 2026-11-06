"""Write the AER statistical-report extractions (ETSAP-brief shape).

    python aer_extract.py

From files beside this script (st39/, st49/, st50/, st59/, st60b/) and
../petrinex/petrinex_2026_facility-metrics_ab-sk.csv. Writes, each with _nodes and
_other-values:
  st39/aer_2026_st39-oil-sands-mine-statistics            (aer_2026_001)
  st59/aer_2026_alberta-drilling-statistics               (aer_2026_005; rigs from ST49, aer_2026_002)
  st50/aer_2026_st50a-gas-plant-licensed-capacity         (aer_2026_003)
  st60b/aer_2025_st60b-pneumatic-venting                  (aer_2025_001)
Brad 2026-10-21: archetype sizes are the median of existing facilities; regulator
statistics are graded sourced (as Petrinex). Year 2024 throughout unless stated.
"""
import csv, io, os, statistics, collections
from openpyxl import load_workbook

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
RECORDS = REPO_ROOT / "data" / "technology_database"
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = str(_DOCS), str(_HERE)
H = ['process', 'technology', 'parameter', 'target', 'unit', 'value', 'value-min', 'value-max', 'formula', 'reference', 'note']
NH = ['process', 'technology', 'sector', 'end-use', 'process-step', 'service-unit']
OH = ['process', 'technology', 'item', 'value', 'unit', 'reference', 'note']


def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def g(x):
    return float('%.4g' % x)


def write(stem, rows, nodes, other):
    for suf, hdr, data in (('.csv', H, rows), ('_nodes.csv', NH, nodes), ('_other-values.csv', OH, other)):
        with open(os.path.join(HERE, stem + suf), 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(hdr); w.writerows(data)
    print(stem, len(rows), 'rows')


def metrics():
    out = {}
    for r in csv.DictReader(open(os.path.join(HERE, '..', 'petrinex', 'petrinex_2026_facility-metrics_ab-sk.csv'), encoding='utf-8-sig')):
        if r['year'] == '2024':
            out[r['facility-id']] = r
    return out


def st39():
    d = collections.defaultdict(float)
    for r in csv.DictReader(open(os.path.join(HERE, 'st39', 'aer_2026_st39-mineable-oil-sands-plant-statistics_long.csv'), encoding='utf-8-sig')):
        if r['year'] == '2024':
            d[(r['facility-id'], r['section'], r['line'])] += float(r['annual-total'])
    sites = [('Kearl (ABOS0101871)', ['ABOS0101871']), ('Fort Hills (ABOS0104948)', ['ABOS0104948']),
             ('Athabasca Oil Sands Project: Muskeg River and Jackpine mines together (ABOS0077303, ABOS0098351); Jackpine draws its heat from the Muskeg River site, so the two are one site', ['ABOS0077303', 'ABOS0098351']),
             ('Syncrude Aurora (ABOS0080249)', ['ABOS0080249'])]
    rows, nodes, other = [], [], []
    T = 'mine_open-pit-oil-sands'
    for name, ids in sites:
        s = lambda sec, line: sum(d.get((i, sec, line), 0.0) for i in ids)
        bit = s('Crude Bitumen', 'Production')
        gas = (s('Purchased Natural Gas', 'Fuel') + s('Purchased Natural Gas', 'Plant Use')) * 1000
        pur = s('Electricity', 'Purchased'); exp = s('Electricity', 'Exported'); gen = s('Electricity', 'Generated')
        sco = s('Synthetic Crude Oil', 'Fuel') + s('Diluent Naphtha', 'Fuel')
        pr = '%s, 2024 (ST39 annual totals)' % name
        ref = 'AER ST39 2024, facility block(s) %s' % ', '.join(ids)
        nodes.append([pr, T, 'oil-and-gas', 'bitumen mining', '', 'm3'])
        rows.append([pr, T, 'description', '', '', 'Oil sands mine with hot-water extraction and froth treatment: ST39 production, fuel gas and electricity for the year.', '', '', '', '', ''])
        rows.append([pr, T, 'annual-output', '', 'm3/yr', g(bit), '', '', 'Crude Bitumen Production' + (' summed over both mines' if len(ids) > 1 else ''), ref, 'CAPACITY BASIS: product-output (bitumen).'])
        rows.append([pr, T, 'specific-energy-consumption', 'natural-gas', 'm3/m3', g(gas / bit), '', '', '(Purchased Natural Gas Fuel + Plant Use) x 1000 / bitumen', ref,
                     'Gross fuel gas, incl. gas burned in on-site cogeneration. Gas at 15 degC; the build converts to GJ HHV at the ECCC NIR marketable-gas factor. heating-value basis: HHV.'])
        rows.append([pr, T, 'specific-energy-consumption', 'electricity', 'MWh/m3', g(pur / bit), '', '', 'Electricity Purchased / bitumen', ref,
                     'Purchased electricity only (power generated on site comes from the gas counted above). heating-value basis: not applicable.'])
        other.append([pr, T, 'electricity generated on site / exported', '%s / %s' % (g(gen), g(exp)), 'MWh', ref, 'Exported power is a co-product of the cogeneration fuel.'])
        if sco:
            other.append([pr, T, 'synthetic crude and naphtha burned as fuel (not in the SEC)', g(sco), 'm3', ref, 'No heating value printed; left out of the SEC, so the SEC understates this site.'])
    write(os.path.join('st39', 'aer_2026_st39-oil-sands-mine-statistics'), rows, nodes, other)


def drilling():
    r = list(csv.DictReader(open(os.path.join(HERE, 'st59', 'aer_2026_alberta-drilling-metres-per-rig.csv'), encoding='utf-8-sig')))
    yrs = [x for x in r if x['year'] in ('2022', '2023', '2024', '2025')]
    v = [float(x['metres-per-active-rig']) for x in yrs]
    pr = 'Alberta drilling, metres per active rig, 2022-2025 (ST59 metres over ST49 rigs)'
    T = 'drilling-rig_diesel'
    rows = [[pr, T, 'description', '', '', 'Alberta land rigs: metres drilled in the year divided by rigs that spudded at least one well.', '', '', '', '', ''],
            [pr, T, 'annual-output', '', 'm', g(statistics.median(v)), g(min(v)), g(max(v)),
             'median over years of ST59 metres / ST49 active rigs (%s)' % '; '.join('%s: %s/%s' % (x['year'], round(float(x['st59-metres'])), x['st49-rigs-drilling']) for x in yrs),
             'AER ST59 grand totals; AER ST49 daily spud lists', 'ST59 metres include legs. A rig counts as active in a year with at least one Drill To LD, Resumption or Re-entry line. CAPACITY BASIS: product-output (metres drilled).']]
    nodes = [[pr, T, 'oil-and-gas', 'drilling', '', 'm']]
    other = [[pr, T, 'metres per active rig %s' % x['year'], x['metres-per-active-rig'], 'm/yr', 'ST59/ST49', 'wells per rig %s (ST59 wells include legs and recompletions)' % x['wells-per-active-rig']] for x in r]
    write(os.path.join('st59', 'aer_2026_alberta-drilling-statistics'), rows, nodes, other)


def st50(M):
    p = os.path.join(HERE, 'st50', 'aer_2026_st50a-gas-processing-plants.csv')
    lines = open(p, encoding='latin-1').read().splitlines()
    i = [n for n, l in enumerate(lines) if l.startswith('Reporting Facility ID')][0]
    grp = collections.defaultdict(list)
    for r in csv.DictReader(io.StringIO('\n'.join(lines[i:]))):
        fid = r['Reporting Facility ID']
        m = M.get(fid)
        if not m or m['full-year'] != 'yes':
            continue
        f = lambda k: float((r.get(k) or '0').replace(',', '') or 0) if (r.get(k) or '').strip() not in ('', 'None') else 0.0
        cap = f('Raw Gas E3m3/d')
        if cap <= 0:
            continue
        if f('C2 m3/d') + f('C2 Mix m3/d') > 0:
            grp['ethane'].append(cap)
        if m['subtype'] in ('402', '403', '404', '405'):
            grp['sour'].append(cap)
        elif m['subtype'] == '401':
            grp['sweet'].append(cap)
    rows, nodes = [], []
    for key, techs, label in (('sour', ['gas-treatment-unit_amine-sweetening'], 'sour gas plants (subtypes 402-405)'),
                              ('sweet', ['gas-treatment-unit_glycol-dehydration'], 'sweet gas plants (subtype 401)'),
                              ('ethane', ['turboexpander_ngl-recovery', 'adsorber_molecular-sieve'], 'plants licensed to recover ethane')):
        v = grp[key]
        pr = 'Alberta %s operating all of 2024: licensed raw-gas capacity (ST50A, 30 Sep 2026)' % label
        for t in techs:
            nodes.append([pr, t, 'oil-and-gas', 'natural-gas processing', '', 'm3'])
            rows.append([pr, t, 'description', '', '', 'Licensed raw-gas inlet capacity of Alberta %s.' % label, '', '', '', '', ''])
            rows.append([pr, t, 'capacity', '', 'm3/d', g(q(v, .5) * 1000), g(q(v, .25) * 1000), g(q(v, .75) * 1000),
                         'median (p25-p75) of Raw Gas E3m3/d x 1000 over %d plants' % len(v), 'AER ST50A',
                         'Licensed (approved) capacity, not throughput; plants that reported throughput in all 12 months of 2024 in Petrinex. CAPACITY BASIS: product-output (gas processed).'])
    write(os.path.join('st50', 'aer_2026_st50a-gas-plant-licensed-capacity'), rows, nodes, [])


def st60b(M):
    wb = load_workbook(os.path.join(DOCS, 'st60b', 'aer_2025_st60b-upstream-petroleum-industry-emissions.xlsx'), read_only=True)
    ws = wb['2024 OneStop']
    hdr = None; vals = []; groups = collections.Counter()
    for row in ws.iter_rows(values_only=True):
        if row and row[0] == 'Year':
            hdr = [str(c) for c in row]; continue
        if not hdr or not row or row[0] is None:
            continue
        r = dict(zip(hdr, row))
        m = M.get(r['Reporting Facility'])
        if not m or m['full-year'] != 'yes':
            continue
        pn = float(r.get('PNEUMATICINSTRUMENT') or 0) + float(r.get('PNEAMATICPUMP') or 0)
        gas = max(float(m.get('gas-received_m3') or 0), float(m.get('gas-produced_m3') or 0))
        if pn > 0 and gas > 0:
            vals.append(pn / gas); groups[m['group']] += 1
    pr = 'Alberta upstream facilities reporting pneumatic venting, 2024 (ST60B OneStop venting joined to Petrinex gas handled)'
    T = 'pneumatic-device_gas-driven'
    rows = [[pr, T, 'description', '', '', 'Gas vented by pneumatic instruments and pumps per m3 of gas handled at the facility; Alberta fleet mix of high- and low-bleed devices.', '', '', '', '', ''],
            [pr, T, 'emissions-process', 'ch4', 'm3/m3', g(q(vals, .5)), g(q(vals, .25)), g(q(vals, .75)),
             'median (p25-p75) over %d facilities of (PNEUMATICINSTRUMENT + PNEAMATICPUMP vented m3) / max(gas received, gas produced)' % len(vals),
             'AER ST60B 2025 workbook, sheet 2024 OneStop; Petrinex 2024',
             'Whole gas vented, put in t CH4 by the build at the Alberta upstream gas methane content (cf-ng-production-ch4-mass). Facilities with no pneumatic venting are left out, so non-emitting sites do not pull the median down. Facility groups: %s.' % ', '.join('%s %d' % kv for kv in groups.most_common())]]
    nodes = [[pr, T, 'oil-and-gas', 'natural-gas supply venting', '', 'm3']]
    write(os.path.join('st60b', 'aer_2025_st60b-pneumatic-venting'), rows, nodes, [])


if __name__ == '__main__':
    M = metrics()
    st39(); drilling(); st50(M); st60b(M)
