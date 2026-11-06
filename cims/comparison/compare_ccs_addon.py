"""Compare only the CCS portion of CIMS's capture hosts with the database's capture add-on.

CIMS prices a host 'with CCS' as its own plant plus a service request (t CO2 per unit of
product) to the sector's CCS node, whose technology carries the capture cost per t CO2. The
database's _ccs variant carries host plus add-on; output/ccs-variant.csv gives the add-on.

CIMS CCS portion per unit of product
  = request x (CCS node capex/t-yr x CRF(8%, node lifetime) + fixed O&M/t + VOM/t)
  + the host's own increment over its sibling without CCS (capex annualised, fixed O&M), where
    a sibling exists in the same branch.
Database CCS portion per unit of product
  = add-on capex / capacity factor x CRF(8%, variant lifetime) + add-on fixed O&M / capacity
    factor + add-on variable O&M.
Both are also stated per t CO2 captured (CIMS request; database emissions-captured). Energy:
CIMS node natural gas x request (+ the host's energy increment); database variant SEC less
host SEC. Costs in 2025 CAD (CIMS 2020 CAD x 1.244).

Writes comparison/ccs-addon-comparison.csv and comparison/ccs-node-comparison.csv.
"""
import csv, glob, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'comparison')
H = os.path.join(ROOT, 'data', 'processed_data', 'technology_database')
RATE, INFL = 0.08, 124.400255 / 100.0
UNIT = {('tonne', 't'): 1, ('GJ', 'GJ'): 1, ('m3 of RPP', 'm3'): 1, ('kt', 't'): 1e-3, ('tCO2', 't'): 1}

def crf(r, n):
    return r / (1 - (1 + r) ** -n)

def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def g(x, d=4):
    return '' if x is None else f'{x:.{d}g}'

arch = {r['archetype']: r for r in csv.DictReader(open(os.path.join(H, 'archetype.csv'), encoding='utf-8-sig'))}
par = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(H, 'archetype-parameter.csv'), encoding='utf-8-sig')):
    par[r['archetype']][(r['parameter'], r['target'])] = r
def dv(a, p, t=''):
    return f(par[a].get((p, t), {}).get('central'))
addon = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(H, 'ccs-variant.csv'), encoding='utf-8-sig')):
    addon[r['archetype']][r['parameter']] = r

cv = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(OUT, 'cims-values.csv'), encoding='utf-8')):
    cv[(r['cims-sector'], r['cims-branch'], r['cims-technology'])][r['quantity']] = r
def q(k, name):
    return f(cv.get(k, {}).get(name, {}).get('median'))
def energy(k):
    tot = 0.0
    for name, r in cv.get(k, {}).items():
        if name.startswith('request|') and r['unit'] == 'GJ' and 'Feedstock' not in name:
            v = f(r['median'])
            if v and v > 0:
                tot += v
    return tot

maps = {(r['cims-sector'], r['cims-branch'], r['cims-technology']): r
        for p in glob.glob(os.path.join(OUT, 'mapping', '*.csv')) for r in csv.DictReader(open(p, encoding='utf-8'))}
techs_by_branch = collections.defaultdict(set)
for (s, b, t) in cv:
    techs_by_branch[(s, b)].add(t)

def node_key(sector):
    for (s, b, t) in cv:
        if s == sector and t == 'CCS' and b.endswith('.CCS'):
            return (s, b, t)

def sibling(s, b, t):
    base = re.sub(r'(\s*(\+|with)?\s*CCS|_CCS)$', '', t).strip()
    base = re.sub(r'_centralised$', '_centralised', base)
    return base if base != t and base in techs_by_branch[(s, b)] else None

# ---- 1. the sector CCS nodes against the capture archetype of their stream type -------
node_rows = []
for k, m in sorted(maps.items()):
    if k[2] != 'CCS' or not k[1].endswith('.CCS') or not m['archetype']:
        continue
    a = m['archetype']; cf = (dv(a, 'capacity-factor') or 100) / 100
    L = q(k, 'lifetime') or 30; La = dv(a, 'lifetime') or 25
    c_cap = q(k, 'capex-per-unit') * INFL; d_cap = (dv(a, 'capex') or 0) / cf
    row = {'cims-sector': k[0], 'archetype': a, 'stream': m['new-node'].split('.')[-1],
           'capex_cims': g(c_cap), 'capex_db': g(d_cap),
           'capex-annualised_cims': g(c_cap * crf(RATE, L)), 'capex-annualised_db': g(d_cap * crf(RATE, La)),
           'opex-fixed_cims': g(q(k, 'fom-per-unit') * INFL), 'opex-fixed_db': g((dv(a, 'opex-fixed') or 0) / cf),
           'opex-variable_cims': g((q(k, 'request|vom|VOM') or 0) * INFL), 'opex-variable_db': g(dv(a, 'opex-variable')),
           'energy_cims': g(energy(k)), 'energy_db': g(dv(a, 'specific-energy-consumption')),
           'energy-electricity_db': g(dv(a, 'specific-energy-consumption', 'electricity')),
           'capture-rate_cims': g((q(k, 'emissions-removal|Process|CO2') or 0) * 100),
           'capture-rate_db': g(dv(a, 'capture-rate', 'co2')),
           'lifetime_cims': g(L), 'lifetime_db': g(La),
           'transport-request_cims': g(next((f(r['median']) for n, r in cv[k].items() if 'ccs-transport' in n), None)),
           'unit': '2025_CAD per t CO2 (capex per t-yr); GJ per t CO2', 'note': m['note']}
    node_rows.append(row)
with open(os.path.join(OUT, 'ccs-node-comparison.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(node_rows[0])); w.writeheader(); w.writerows(node_rows)

# ---- 2. the CCS portion of each host with capture -------------------------------------
rows = []
for k, m in sorted(maps.items()):
    req = q(k, 'request|ccs|CCS')
    a = m['archetype']
    if req is None or cv[k]['request|ccs|CCS']['unit'] != 'tCO2' or not a or a not in addon:
        continue
    du = arch[a]['product-unit']; cu = cv[k].get('output', {}).get('unit', '')
    uf = UNIT.get((cu, du))
    nk = node_key(k[0])
    if uf is None or nk is None:
        continue
    req_u = req * uf
    Ln = q(nk, 'lifetime') or 30
    node_t = (q(nk, 'capex-per-unit') * INFL * crf(RATE, Ln) + q(nk, 'fom-per-unit') * INFL
              + (q(nk, 'request|vom|VOM') or 0) * INFL)
    c_node = req_u * node_t
    sib = sibling(*k)
    c_host = e_host = None
    if sib:
        sk = (k[0], k[1], sib)
        Lh = q(k, 'lifetime') or 30
        dcap = ((q(k, 'capex-per-unit') or 0) - (q(sk, 'capex-per-unit') or 0)) * INFL * uf
        dfom = ((q(k, 'fom-per-unit') or 0) - (q(sk, 'fom-per-unit') or 0)) * INFL * uf
        c_host = dcap * crf(RATE, Lh) + dfom
        e_host = (energy(k) - energy(sk)) / uf
    c_tot = c_node + (c_host or 0)
    e_cims = req_u * energy(nk) + (e_host or 0)
    cf = (dv(a, 'capacity-factor') or 100) / 100; La = dv(a, 'lifetime') or 25
    ad = {p: f(addon[a].get(p, {}).get('add-on')) for p in ('capex', 'opex-fixed', 'opex-variable')}
    d_tot = ((ad['capex'] or 0) / cf * crf(RATE, La) + (ad['opex-fixed'] or 0) / cf + (ad['opex-variable'] or 0))
    cap_d = f(addon[a].get('capex', {}).get('co2-captured')) or dv(a, 'emissions-captured', 'co2')
    host = addon[a].get('capex', {}).get('host', '')
    e_db = None
    if dv(a, 'specific-energy-consumption') is not None and host and dv(host, 'specific-energy-consumption') is not None:
        e_db = dv(a, 'specific-energy-consumption') - dv(host, 'specific-energy-consumption')
    rows.append({
        'cims-sector': k[0], 'cims-branch': k[1], 'cims-technology': k[2], 'archetype': a, 'match': m['match'],
        'stream': 'concentrated' if 'concentrated' in a else 'diffuse', 'unit': f'per {du}',
        'co2-captured_cims': g(req_u), 'co2-captured_db': g(cap_d),
        'ccs-cost_cims': g(c_tot), 'ccs-cost_cims_node-part': g(c_node), 'ccs-cost_cims_host-increment': g(c_host),
        'cims-sibling': sib or '', 'ccs-cost_db': g(d_tot), 'ratio-cost': g(c_tot / d_tot if d_tot else None, 3),
        'ccs-cost-per-t_cims': g(c_tot / req_u if req_u else None), 'ccs-cost-per-t_db': g(d_tot / cap_d if cap_d else None),
        'ccs-energy_cims': g(e_cims), 'ccs-energy_db': g(e_db),
        'ccs-energy-per-t_cims': g(e_cims / req_u if req_u else None), 'ccs-energy-per-t_db': g(e_db / cap_d if (e_db is not None and cap_d) else None),
        'db-addon-tier': addon[a].get('capex', {}).get('tier', ''), 'db-addon-grade': addon[a].get('capex', {}).get('grade', ''),
    })
with open(os.path.join(OUT, 'ccs-addon-comparison.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(node_rows), 'nodes;', len(rows), 'hosts')
