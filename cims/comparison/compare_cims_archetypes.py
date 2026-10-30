"""Compare CIMS model-input technology values with the database archetypes they map to.

Inputs : comparison/cims-values.csv (extract_cims_values.py), comparison/mapping/*.csv,
         database/harmonized/output/archetype*.csv
Outputs: comparison/comparison-long.csv       one row per CIMS technology x quantity
         comparison/comparison-archetype.csv  one row per archetype x quantity (same/close matches)

Bases (2026-10-14 rulings): CIMS values are the median across provinces; capital is
annualised at 8% for both sides, each with its own lifetime. CIMS costs are 2020 CAD,
deflated to 2025 CAD with the database's CAD GDP deflator. CIMS fcc and fom are per
unit of actual annual output; the database's capex and fixed O&M are per unit of
nameplate annual capacity, so they are divided by the archetype's capacity factor
to put both per unit of output.
"""
import csv, glob, os, statistics, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'comparison')
RATE = 0.08
INFL = 124.400255 / 100.0   # CAD GDP deflator 2025/2020 (records/reference/reference-currency-deflator.csv)

def crf(r, n):
    return r / (1 - (1 + r) ** -n)

def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

H = os.path.join(ROOT, 'database', 'harmonized', 'output')
arch = {r['archetype']: r for r in csv.DictReader(open(os.path.join(H, 'archetype.csv'), encoding='utf-8-sig'))}
par = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(H, 'archetype-parameter.csv'), encoding='utf-8-sig')):
    par[r['archetype']][(r['parameter'], r['target'])] = r

# a CCS variant's capex and fixed O&M include the capture add-on; CIMS prices the host
# plant only and buys capture from the CCS node, so compare against the host value
HOSTV = {}
for r in csv.DictReader(open(os.path.join(H, 'ccs-variant.csv'), encoding='utf-8-sig')):
    if f(r['host-value']) is not None:
        HOSTV[(r['archetype'], r['parameter'])] = f(r['host-value'])

def dbv(a, p, t=''):
    if not t and (a, p) in HOSTV and p in ('capex', 'opex-fixed', 'opex-variable'):
        r = dict(par[a].get((p, t)) or {})
        r.update({'central': HOSTV[(a, p)], 'low': '', 'high': '', 'grade': (r.get('grade', '') + ' (host plant only)').strip()})
        return HOSTV[(a, p)], r
    r = par[a].get((p, t))
    return (f(r['central']), r) if r and f(r['central']) is not None else (None, None)

cv = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(OUT, 'cims-values.csv'), encoding='utf-8')):
    cv[(r['cims-sector'], r['cims-branch'], r['cims-technology'])][r['quantity']] = r

CARRIER = {
    'Electricity': 'electricity', 'Natural Gas': 'natural-gas', 'Methane Blend': 'natural-gas',
    'Methane Fuel': 'natural-gas', 'OG Methane Blend': 'natural-gas', 'Renewable Natural Gas': 'natural-gas',
    'Methane_Agriculture': 'natural-gas', 'Natural Gas Feedstock': 'feedstock',
    'Thermal Coal': 'coal', 'Metallurgical Coal': 'coal', 'Coke': 'coke', 'Petroleum Coke': 'petroleum-coke',
    'Heavy Fuel Oil': 'oil', 'Light Fuel Oil': 'oil', 'Diesel': 'diesel', 'Diesel_Industrial': 'diesel',
    'OG Diesel Blend': 'diesel', 'Diesel_Transportation': 'diesel', 'Biodiesel': 'diesel',
    'Solid Biomass': 'biomass', 'Black Liquor': 'black-liquor', 'Waste': 'municipal-waste',
    'Still Gas': 'refinery-gas', 'Refinery Fuel Gas': 'refinery-gas', 'Still Gas Steam': 'refinery-gas',
    'Iron Process Gas': 'by-product-gas', 'Hydrogen': 'hydrogen', 'Propane': 'oil', 'LPG': 'oil',
    'Gasoline': 'oil', 'OG Gasoline Blend': 'oil', 'Ethanol': 'oil', 'Renewable Diesel': 'diesel',
    'Renewable Gasoline': 'oil', 'Uranium': 'other',
}

def cims_energy(q):
    """Energy in per unit of output, by group: electricity (direct + aux motor services), steam, heat, fuel."""
    g = collections.Counter(); aux = 0
    for k, r in q.items():
        if not k.startswith('request|') or r['unit'] != 'GJ':
            continue
        _, cls, name = k.split('|', 2)
        v = f(r['median'])
        if v < 0:                      # a negative request is an output (CHP electricity)
            g['_out_' + cls + '|' + name.split('.')[-1]] += -v
            continue
        if cls == 'fuel':
            c = CARRIER.get(name.split('.')[-1], 'other')
            if c == 'feedstock':
                continue
            g['electricity' if c == 'electricity' else 'fuel'] += v
        elif cls == 'aux-service':
            g['electricity'] += v; aux += v
        elif cls == 'steam':
            g['steam'] += v
        elif cls == 'heat-service':
            g['heat'] += v
    return g, aux

UNIT = {('tonne', 't'): 1, ('GJ', 'GJ'): 1, ('m3 of RPP', 'm3'): 1, ('kt', 't'): 1e-3, ('tCO2', 't'): 1, ('m3', 'm3'): 1}

maps = [r for p in sorted(glob.glob(os.path.join(OUT, 'mapping', '*.csv'))) for r in csv.DictReader(open(p, encoding='utf-8'))]
long = []

def add(m, a, q, unit, c, d, drow=None, note='', basis=''):
    rec = {'cims-sector': m['cims-sector'], 'cims-branch': m['cims-branch'], 'cims-technology': m['cims-technology'],
           'archetype': a, 'match': m['match'], 'quantity': q, 'unit': unit,
           'cims': '' if c is None else f'{c:.6g}', 'database': '' if d is None else f'{d:.6g}',
           'database-low': '', 'database-high': '', 'database-n': '', 'database-grade': '',
           'ratio-cims-to-db': '', 'cims-in-db-range': '', 'basis': basis, 'note': note}
    if drow is not None:
        rec['database-grade'] = drow.get('grade', ''); rec['database-n'] = drow.get('n', '')
    if c is not None and d not in (None, 0):
        rec['ratio-cims-to-db'] = f'{c / d:.4g}'
    long.append(rec)
    return rec

def band(rec, lo, hi, c):
    if lo is not None and hi is not None:
        rec['database-low'], rec['database-high'] = f'{lo:.6g}', f'{hi:.6g}'
        if c is not None:
            rec['cims-in-db-range'] = 'yes' if lo * 0.999 <= c <= hi * 1.001 else ('above' if c > hi else 'below')

for m in maps:
    a = m['archetype']
    if not a or m['match'] in ('none', 'not-a-technology'):
        continue
    q = cv.get((m['cims-sector'], m['cims-branch'], m['cims-technology']), {})
    du = arch[a]['product-unit']
    cu = q['output']['unit'] if 'output' in q else ''
    uf = UNIT.get((cu, du))
    unote = '' if uf is not None else f'units differ: CIMS per {cu or "unstated unit"}, database per {du}; per-unit values not compared'
    cl = f(q.get('lifetime', {}).get('median'))
    dl, dlr = dbv(a, 'lifetime')
    r = add(m, a, 'lifetime', 'years', cl, dl, dlr)
    if dlr: band(r, f(dlr['low']), f(dlr['high']), cl)
    cfv, _ = dbv(a, 'capacity-factor')
    cf = cfv / 100 if cfv else None
    cfnote = f'database / capacity factor {cfv:g}%' if cf else 'no database capacity factor'
    cc = f(q.get('capex-per-unit', {}).get('median')); cfom = f(q.get('fom-per-unit', {}).get('median'))
    dc, dcr = dbv(a, 'capex'); dfo, dfor = dbv(a, 'opex-fixed'); dvo, dvor = dbv(a, 'opex-variable')
    ucost = f'2025_CAD/{du}'
    cims_cost = lambda x: x * INFL * uf if (x is not None and uf is not None) else None
    db_out = lambda x: x / cf if (x is not None and cf) else None
    c_cap, d_cap = cims_cost(cc), db_out(dc)
    r = add(m, a, 'capex-per-unit-output', ucost + '-per-yr', c_cap, d_cap, dcr, '; '.join(x for x in (unote, cfnote) if x),
            'CIMS fcc/output; database capex/capacity factor')
    if dcr and cf: band(r, db_out(f(dcr['low'])), db_out(f(dcr['high'])), c_cap)
    c_ann = c_cap * crf(RATE, cl) if (c_cap is not None and cl) else None
    d_ann = d_cap * crf(RATE, dl) if (d_cap is not None and dl) else None
    r = add(m, a, 'capex-annualised-8pct', ucost, c_ann, d_ann, dcr, unote, 'capex per unit output x CRF(8%, own lifetime)')
    if dcr and cf and dl and f(dcr['low']) is not None and f(dcr['high']) is not None:
        band(r, db_out(f(dcr['low'])) * crf(RATE, dl), db_out(f(dcr['high'])) * crf(RATE, dl), c_ann)
    c_fom, d_fom = cims_cost(cfom), db_out(dfo)
    r = add(m, a, 'opex-fixed-per-unit-output', ucost, c_fom, d_fom, dfor, unote, 'CIMS fom/output; database opex-fixed/capacity factor')
    if dfor and cf: band(r, db_out(f(dfor['low'])), db_out(f(dfor['high'])), c_fom)
    cvom = f(q.get('request|vom|VOM', {}).get('median'))
    c_vom = cims_cost(cvom)
    if c_vom is not None or dvo is not None:
        r = add(m, a, 'opex-variable', ucost, c_vom, dvo, dvor,
                unote if cvom is not None else 'CIMS has no VOM request on this technology', 'CIMS VOM request; database opex-variable')
        if dvor: band(r, f(dvor['low']), f(dvor['high']), c_vom)
    if c_ann is not None:
        clev = c_ann + (c_fom or 0) + (c_vom or 0)
        dlev, dlevr = dbv(a, 'cost-levelized', 'calculated')
        r = add(m, a, 'cost-levelized-non-energy', ucost, clev, dlev, dlevr, unote,
                'annualised capex + fixed O&M + variable O&M per unit output, 8%')
        if dlevr: band(r, f(dlevr['low']), f(dlevr['high']), clev)
    g, aux = cims_energy(q)
    eout = sum(v for k, v in g.items() if k.startswith('_out_'))
    g = collections.Counter({k: v for k, v in g.items() if not k.startswith('_out_')})
    ctot = sum(g.values()) if g else None
    ds, dsr = dbv(a, 'specific-energy-consumption')
    se = ctot / uf if (ctot is not None and uf) else None
    snote = (f'CIMS includes {aux:.3g} GJ of auxiliary motor services, counted as electricity' if aux else '')
    if ctot is not None or ds is not None:
        r = add(m, a, 'specific-energy-consumption', f'GJ/{du}', se, ds, dsr,
                '; '.join(x for x in (unote if ctot is not None else '', snote) if x), 'gross energy in per unit output')
        if dsr: band(r, f(dsr['low']), f(dsr['high']), se)
        dshare = {}
        if ds:
            # only the top-level split counts: rows the build wrote as a share of the total
            # (named fuels are a sub-split of `fuel`; rows 'pooled apart' are not in the split)
            for (p, t), rr in par[a].items():
                if (p == 'specific-energy-consumption' and t and f(rr['central']) is not None
                        and 'of the total' in rr.get('central-from', '')):
                    grp = t if t in ('electricity', 'steam', 'heat') else 'fuel'
                    dshare[grp] = dshare.get(grp, 0) + f(rr['central']) / ds
        if ctot:
            for grp in ('electricity', 'steam', 'heat', 'fuel'):
                cs = g.get(grp, 0) / ctot
                d = dshare.get(grp, 0.0) if dshare else None
                if cs or d:
                    add(m, a, f'energy-share_{grp}', 'share', cs, d, None,
                        '' if dshare else 'archetype has no carrier split', 'carrier group / total energy in')
        if du == 'GJ' and cu == 'GJ' and ctot and g.get('steam', 0) == 0 and g.get('heat', 0) == 0:
            if eout:
                for tgt, cval in (('heat', 100 / ctot), ('electricity', 100 * eout / ctot)):
                    de, der = dbv(a, 'efficiency', tgt)
                    r = add(m, a, f'efficiency_{tgt}', '%', cval, de, der,
                            'CHP: CIMS heat output 1 GJ and electricity output as a negative request, per GJ in', 'output / energy in')
                    if der: band(r, f(der['low']), f(der['high']), cval)
            else:
                de, der = dbv(a, 'efficiency')
                r = add(m, a, 'efficiency', '%', 100 / ctot, de, der,
                        'CIMS implied = output / energy in (CIMS assumed HHV, as the database)', '1 / SEC')
                if der: band(r, f(der['low']), f(der['high']), 100 / ctot)
    # energy including feedstock, where either side has feedstock
    cfeed = sum(f(r['median']) for k, r in q.items() if k.startswith('request|fuel|') and 'Feedstock' in k and r['unit'] == 'GJ')
    dfeed = [f(rr['central']) for (p, t), rr in par[a].items() if p == 'feedstock-consumption' and f(rr['central']) is not None
             and rr['unit'].startswith('GJ/')]
    if (cfeed or dfeed) and (ctot is not None or ds is not None):
        cin = (ctot + cfeed) / uf if (ctot is not None and uf) else None
        din = (ds or 0) + sum(dfeed)
        add(m, a, 'energy-incl-feedstock', f'GJ/{du}', cin, din, None,
            'CIMS requests incl. Natural Gas Feedstock; database SEC + feedstock-consumption (GJ rows)', 'energy and feedstock in per unit output')
    for gas in ('CO2', 'CH4'):
        ce = f(q.get(f'emissions|Process|{gas}', {}).get('median'))
        de, der = dbv(a, 'emissions-process', gas.lower())
        if ce is not None or (de is not None and gas == 'CO2'):
            cev = ce * uf if (ce is not None and uf) else None
            r = add(m, a, f'emissions-process_{gas.lower()}', f't/{du}', cev, de, der,
                    unote if ce is not None else 'CIMS gives no process emissions on this technology', 'process emissions per unit output')
            if der: band(r, f(der['low']), f(der['high']), cev)
    cc_ = f(q.get('request|ccs|CCS', {}).get('median'))
    dcap, dcapr = dbv(a, 'emissions-captured', 'co2')
    if cc_ is not None or dcap is not None:
        ccv = cc_ * uf if (cc_ is not None and uf) else None
        r = add(m, a, 'co2-captured', f't/{du}', ccv, dcap, dcapr, unote, 'CIMS request to the CCS node; database emissions-captured')
        if dcapr: band(r, f(dcapr['low']), f(dcapr['high']), ccv)
    crr = f(q.get('emissions-removal|Process|CO2', {}).get('median'))
    drr, drrr = dbv(a, 'capture-rate', 'co2')
    if crr is not None or drr is not None:
        r = add(m, a, 'capture-rate', '%', crr * 100 if crr is not None else None, drr, drrr, '', 'CIMS emissions_removal; database capture-rate')
        if drrr: band(r, f(drrr['low']), f(drrr['high']), crr * 100 if crr is not None else None)
    st, str_ = dbv(a, 'share-to-capture', 'co2')
    if st is not None and cc_ is not None:
        add(m, a, 'share-to-capture', '%', None, st, str_,
            'no CIMS counterpart: emissions_removal applies the capture rate to all host CO2 (cims/to-fix.md #4)')

with open(os.path.join(OUT, 'comparison-long.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(long[0])); w.writeheader(); w.writerows(long)

agg = collections.defaultdict(list)
for r in long:
    if r['ratio-cims-to-db'] and r['match'] in ('same', 'close'):
        agg[(r['archetype'], r['quantity'])].append(r)
summ = []
for (a, q), rs in sorted(agg.items()):
    ratios = [float(r['ratio-cims-to-db']) for r in rs]
    cvals = [float(r['cims']) for r in rs]
    summ.append({'archetype': a, 'family': arch[a]['family'], 'quantity': q, 'unit': rs[0]['unit'],
                 'database': rs[0]['database'], 'database-low': rs[0]['database-low'], 'database-high': rs[0]['database-high'],
                 'database-grade': rs[0]['database-grade'], 'database-n': rs[0]['database-n'],
                 'cims-median': f'{statistics.median(cvals):.6g}', 'cims-min': f'{min(cvals):.6g}', 'cims-max': f'{max(cvals):.6g}',
                 'ratio-median': f'{statistics.median(ratios):.3g}', 'n-cims-techs': len(rs),
                 'n-in-db-range': sum(r['cims-in-db-range'] == 'yes' for r in rs),
                 'cims-techs': ' | '.join(sorted({f"{r['cims-sector']}: {r['cims-technology']}" for r in rs}))[:500]})
with open(os.path.join(OUT, 'comparison-archetype.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)
print(len(long), 'long rows;', len(summ), 'archetype x quantity rows')
