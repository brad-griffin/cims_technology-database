"""Collapse the CIMS model-input technologies to one row per technology with the
values the database comparison needs. Median across provinces; min and max kept.

Reads data_processing_calibration/cims/data/model_inputs/model (path as argument).
Writes comparison/cims-values.csv (one row per technology x quantity).
"""
import csv, glob, os, re, statistics, sys, collections

MODEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/mnt/staging/cims/data/model_inputs/model')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comparison', 'cims-values.csv')
SKIP = {'residential', 'commercial', 'transportation_freight', 'transportation_passenger',
        'CIMS_base', 'exogenous_demand', 'exogenous_prices', 'fuels', 'market_share_limits',
        'DCC', 'DIC', 'electricity'}
OVERLAY = {'FIC'}
YEAR = '2025'
REG = re.compile(r'^CIMS\.CAN\.([A-Z]{2})\.')

def strip(b):
    return REG.sub('', b)

def region(r):
    m = REG.match(r['Branch'])
    return m.group(1) if m else r['Region']

def pick(rows):
    """Value for the comparison year: the 2025 row, else the undated row, else the latest <= 2025."""
    by = {r['Year']: r for r in rows}
    for y in (YEAR, ''):
        if y in by:
            return by[y]['Value']
    ys = sorted(y for y in by if y and y <= YEAR)
    return by[ys[-1]]['Value'] if ys else None

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def target_class(t):
    s = strip(t)
    last = s.split('.')[-1]
    if s.startswith('CIMS.Generic Fuels.'):
        return ('vom', last) if last == 'VOM' else ('fuel', last)
    if s.startswith('CIMS.Transmission.CCS TS'):
        return ('ccs-transport', 'CCS TS')
    if last in ('CCS',):
        return ('ccs', last)
    if last in ('Electricity',):
        return ('fuel', 'Electricity')
    if last in ('Methane Blend', 'Methane Fuel', 'OG Methane Blend', 'Methane_Agriculture', 'Diesel_Industrial',
                'OG Diesel Blend', 'Diesel_Transportation', 'OG Gasoline Blend', 'Biodiesel', 'Ethanol',
                'Hydrogen', 'Still Gas', 'Iron Process Gas', 'Still Gas Steam'):
        return ('fuel', last)
    if last in ('Machine Drive', 'Pumping', 'Conveyance', 'Ventilation', 'Direct Drive', 'Compression',
                'Direct Drive Small', 'Direct Drive Large', 'HVAC', 'Lighting', 'Motive Power',
                'Industrial Engines'):
        return ('aux-service', last)
    if last in ('Steam',):
        return ('steam', last)
    if last in ('Direct Heat', 'Heat', 'Water Heating'):
        return ('heat-service', last)
    return ('other-service', s)

def main():
    rows = collections.defaultdict(list)   # (sector, branch, tech) -> rows
    node = collections.defaultdict(list)   # (sector, branch) -> rows
    for f in sorted(glob.glob(os.path.join(MODEL, '*', '*.csv'))):
        folder = os.path.basename(os.path.dirname(f))
        if folder in SKIP:
            continue
        with open(f, encoding='utf-8-sig', newline='') as fh:
            for r in csv.DictReader(fh):
                if not r.get('Branch', '').startswith('CIMS.CAN.'):
                    continue
                b = strip(r['Branch'])
                sector = b.split('.')[0]
                r['_reg'] = region(r)
                if r['Technology']:
                    rows[(sector, b, r['Technology'])].append(r)
                else:
                    node[(sector, b)].append(r)
    def node_param(sector, b, p, reg):
        """Walk up the branch for a node-level parameter (e.g. discount rate)."""
        parts = b.split('.')
        while parts:
            key = (sector, '.'.join(parts))
            vals = [x for x in node.get(key, []) if x['Parameter'] == p and x['_reg'] == reg]
            if vals:
                return pick(vals), vals[0]['Unit']
            parts.pop()
        return None, None
    out = []
    for (sector, b, tech), rs in sorted(rows.items()):
        per = collections.defaultdict(dict)  # quantity -> region -> value
        units = {}
        regs = sorted({r['_reg'] for r in rs})
        for reg in regs:
            rr = [r for r in rs if r['_reg'] == reg]
            g = collections.defaultdict(list)
            for r in rr:
                g[(r['Parameter'], r['Context'], r['Sub_Context'], r['Target'])].append(r)
            vals = {}
            for (p, c, sc, t), grp in g.items():
                v = num(pick(grp))
                if v is None:
                    continue
                if p in ('fcc', 'fom', 'fic', 'lifetime', 'output'):
                    vals[p] = v
                elif p == 'market_share_total':
                    v2 = num(next((x['Value'] for x in grp if x['Year'] == '2000'), None))
                    if v2 is not None:
                        vals['market-share-2000'] = v2
                elif p == 'service_request':
                    cls, name = target_class(t)
                    q = f'request|{cls}|{name}'
                    vals[q] = vals.get(q, 0) + v
                    units[q] = grp[0]['Unit']
                elif p == 'emissions':
                    q = f'emissions|{sc or "?"}|{c}'
                    vals[q] = v; units[q] = grp[0]['Unit']
                elif p == 'emissions_removal':
                    vals[f'emissions-removal|{sc}|{c}'] = v
                elif p == 'emissions_biomass':
                    vals[f'emissions-biomass|{c}'] = v
            if vals.get('output'):
                o = vals['output']
                if 'fcc' in vals: vals['capex-per-unit'] = vals['fcc'] / o
                if 'fom' in vals: vals['fom-per-unit'] = vals['fom'] / o
            dr, _ = node_param(sector, b, 'discount_rate_financial', reg)
            if num(dr) is not None:
                vals['discount-rate-financial'] = num(dr)
            su, _ = node_param(sector, b, 'service_provide', reg)
            units['output'] = su or ''
            for q, v in vals.items():
                per[q][reg] = v
        for q, d in per.items():
            v = list(d.values())
            out.append({
                'cims-sector': sector, 'cims-branch': b, 'cims-technology': tech, 'quantity': q,
                'unit': units.get(q, ''), 'median': statistics.median(v), 'min': min(v), 'max': max(v),
                'n-regions': len(v), 'regions': ';'.join(sorted(d)),
            })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    print(len(rows), 'technologies;', len(out), 'rows ->', OUT)

if __name__ == '__main__':
    main()
