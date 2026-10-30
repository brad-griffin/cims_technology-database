"""Reduce Petrinex annual volumetric totals to facility metrics and subtype statistics.

    python petrinex_summary.py <out-dir> <annual.csv> [<annual.csv> ...]

Inputs are the outputs of petrinex_annual.py (one or more provinces and years).
Writes, in <out-dir>:
  petrinex_2026_facility-metrics_ab-sk.csv   one row per facility-year (git-ignored, bulk)
  petrinex_2026_group-statistics_ab-sk.csv   quantiles by province, facility group, metric, year

Only facilities reporting a throughput in all 12 months of the year are kept, so
start-ups, shut-ins and part-year facilities do not drag the distributions down.
Gas volumes: Petrinex e3m3 converted to m3; gas energy at the ECCC NIR 2026
marketable-gas HHV 38.39 MJ/m3 (cf-ef-co2-natural-gas basis). Liquids m3.
"""
import csv, sys, os, collections, statistics

HHV = 0.03839  # GJ per m3, ECCC NIR 2026 marketable natural gas

GROUPS = {
    'gas-plant-sweet': {'401'},
    'gas-plant-sour': {'402', '403', '404', '405'},
    'gas-plant-straddle': {'406'},
    'gas-plant-fractionation': {'407'},
    'gas-gathering-system': {'621', '622'},
    'gas-battery-single-well': {'351'},
    'gas-battery-multiwell': {'361', '362', '363', '364', '365', '366', '367'},
    'crude-oil-battery-single-well': {'311', '325'},
    'crude-oil-battery-multiwell': {'321', '322', '326', '327'},
    'bitumen-battery-cold': {'331', '341', '342'},
    'in-situ-oil-sands-battery': {'344'},
    'in-situ-oil-sands-injection': {'506'},
    'water-disposal': {'503', '507', '509', '512', '518', '520'},
    'enhanced-recovery-injection': {'501', '508', '510', '511'},
}
SUB2G = {s: g for g, ss in GROUPS.items() for s in ss}
# throughput that defines "active all year" for each group
THRU = {
    'gas-plant-sweet': 'gas-received', 'gas-plant-sour': 'gas-received',
    'gas-plant-straddle': 'gas-received', 'gas-plant-fractionation': 'gas-received',
    'gas-gathering-system': 'gas-received',
    'gas-battery-single-well': 'gas-produced', 'gas-battery-multiwell': 'gas-produced',
    'crude-oil-battery-single-well': 'oil-produced', 'crude-oil-battery-multiwell': 'oil-produced',
    'bitumen-battery-cold': 'oil-produced', 'in-situ-oil-sands-battery': 'oil-produced',
    'in-situ-oil-sands-injection': 'steam-injected',
    'water-disposal': 'water-injected', 'enhanced-recovery-injection': 'water-injected',
}
# (activity, product) -> metric, factor to m3
MAP = {
    ('REC', 'GAS'): ('gas-received', 1000), ('PROD', 'GAS'): ('gas-produced', 1000),
    ('FUEL', 'GAS'): ('fuel-gas', 1000), ('FLARE', 'GAS'): ('flared-gas', 1000),
    ('VENT', 'GAS'): ('vented-gas', 1000), ('PURREC', 'GAS'): ('gas-purchased', 1000),
    ('PROD', 'OIL'): ('oil-produced', 1), ('PROD', 'COND'): ('condensate-produced', 1),
    ('PROD', 'WATER'): ('water-produced', 1), ('INJ', 'WATER'): ('water-injected', 1),
    ('REC', 'WATER'): ('water-received', 1), ('INJ', 'STEAM'): ('steam-injected', 1),
    ('REC', 'FSHWTR'): ('fresh-water-received', 1), ('REC', 'BRKWTR'): ('brackish-water-received', 1),
}
RATIOS = [  # name, numerator, denominator, scale, unit
    ('fuel-gas-per-gas-received', 'fuel-gas', 'gas-received', 1, 'm3/m3'),
    ('fuel-energy-per-gas-received', 'fuel-gas', 'gas-received', HHV, 'GJ/m3'),
    ('fuel-gas-per-gas-produced', 'fuel-gas', 'gas-produced', 1, 'm3/m3'),
    ('fuel-energy-per-oil-produced', 'fuel-gas', 'oil-produced', HHV, 'GJ/m3'),
    ('flared-gas-per-oil-produced', 'flared-gas', 'oil-produced', 1, 'm3/m3'),
    ('vented-gas-per-oil-produced', 'vented-gas', 'oil-produced', 1, 'm3/m3'),
    ('flared-gas-per-gas-received', 'flared-gas', 'gas-received', 1, 'm3/m3'),
    ('vented-gas-per-gas-received', 'vented-gas', 'gas-received', 1, 'm3/m3'),
    ('water-oil-ratio', 'water-produced', 'oil-produced', 1, 'm3/m3'),
]


def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def main(outdir, files):
    m = collections.defaultdict(lambda: collections.defaultdict(float))
    mo = collections.defaultdict(lambda: collections.defaultdict(int))
    info = {}
    for fn in files:
        for r in csv.DictReader(open(fn, encoding='utf-8')):
            g = SUB2G.get(r['subtype'])
            if not g:
                continue
            km = MAP.get((r['activity'], r['product']))
            if not km:
                continue
            k = (r['facility-id'], r['year'])
            info[k] = (r['province'], r['subtype'], r['subtype-desc'], g, r['facility-name'], r['operator'])
            m[k][km[0]] += float(r['volume']) * km[1]
            mo[k][km[0]] = max(mo[k][km[0]], int(r['months']))
    metrics = sorted({x for v in m.values() for x in v})
    os.makedirs(outdir, exist_ok=True)
    rows = []
    with open(os.path.join(outdir, 'petrinex_2026_facility-metrics_ab-sk.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['facility-id', 'year', 'province', 'subtype', 'subtype-desc', 'group', 'facility-name',
                    'operator', 'full-year'] + [x + '_m3' for x in metrics] + [r[0] + '_' + r[4] for r in RATIOS])
        for k in sorted(m):
            p = info[k]; g = p[3]; d = m[k]
            full = mo[k].get(THRU[g], 0) == 12 and d.get(THRU[g], 0) > 0
            rat = []
            for name, a, b, s, u in RATIOS:
                rat.append(round(d[a] / d[b] * s, 6) if d.get(b, 0) > 0 and a in d else '')
            w.writerow([k[0], k[1], *p, 'yes' if full else 'no'] + [round(d.get(x, 0), 1) for x in metrics] + rat)
            if full:
                rows.append((p[0], g, k[1], d, rat))
    stats = collections.defaultdict(list)
    for prov, g, yr, d, rat in rows:
        for x in metrics:
            if d.get(x, 0) > 0:
                stats[(prov, g, x + ' (annual)', 'm3/yr', yr)].append(d[x])
        for (name, a, b, s, u), v in zip(RATIOS, rat):
            if v != '':
                stats[(prov, g, name, u, yr)].append(v)
    with open(os.path.join(outdir, 'petrinex_2026_group-statistics_ab-sk.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['province', 'group', 'metric', 'unit', 'year', 'n', 'p10', 'p25', 'median', 'p75', 'p90', 'mean', 'total'])
        for k in sorted(stats):
            v = stats[k]
            if len(v) < 3:
                continue
            w.writerow([*k, len(v)] + [float('%.4g' % q(v, p)) for p in (.1, .25, .5, .75, .9)]
                       + [float('%.4g' % statistics.mean(v)), float('%.6g' % sum(v))])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
