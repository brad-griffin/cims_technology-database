"""One row per CIMS technology with its key values in readable form, for mapping work."""
import csv, collections, os
here = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(here, 'comparison', 'cims-values.csv'), encoding='utf-8')))
t = collections.OrderedDict()
CROSS = ('Steam', 'Machine Drive', 'Pumping', 'Compression', 'HVAC', 'Lighting', 'CCS', 'Ventilation', 'Conveyance',
         'Direct Drive', 'Oxygen', 'Fuel Blends', 'Methane Blend', 'Diesel', 'Heat', 'Direct Heat', 'Motive Power',
         'Industrial Engines', 'Gasoline', 'Blend')
def cross(b):
    parts = b.split('.')[1:]
    return 'cross-cutting' if parts and any(parts[0].startswith(c) or parts[0].endswith(c) for c in CROSS) else 'process'
for r in rows:
    k = (r['cims-sector'], r['cims-branch'], r['cims-technology'])
    d = t.setdefault(k, {'cims-sector': k[0], 'cims-branch': k[1], 'cims-technology': k[2], 'group': cross(k[1]),
                         'output-unit': '', 'lifetime': '', 'capex-per-unit_2020CAD': '', 'fom-per-unit_2020CAD': '',
                         'market-share-2000': '', 'requests': []})
    q = r['quantity']; m = float(r['median'])
    if q == 'output': d['output-unit'] = r['unit']
    elif q == 'lifetime': d['lifetime'] = f'{m:g}'
    elif q == 'capex-per-unit': d['capex-per-unit_2020CAD'] = f'{m:.4g}'
    elif q == 'fom-per-unit': d['fom-per-unit_2020CAD'] = f'{m:.4g}'
    elif q == 'market-share-2000': d['market-share-2000'] = f'{m:.3g}'
    elif q.startswith('request|'):
        _, cls, name = q.split('|', 2)
        d['requests'].append(f'{name.split(".")[-1]}={m:.3g} {r["unit"]}')
    elif q.startswith('emissions'):
        d['requests'].append(f'{q}={m:.3g} {r["unit"]}')
for d in t.values():
    d['requests'] = '; '.join(d['requests'])
with open(os.path.join(here, 'comparison', 'cims-technology-summary.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(next(iter(t.values()))))
    w.writeheader(); w.writerows(t.values())
c = collections.Counter((d['group'], d['cims-sector']) for d in t.values())
for k, v in sorted(c.items()): print(k, v)
