"""Write the Petrinex extraction (ETSAP-brief shape) from the summary tables.

    python petrinex_extract.py

Reads, beside this script: petrinex_2026_facility-metrics_ab-sk.csv (petrinex_summary.py),
petrinex_2026_in-situ-scheme-intensity.csv, the public-data zips (well-to-facility links),
and ../aer/st50/aer_2026_st50a-gas-processing-plants.csv (to find ethane-recovery plants).
Writes petrinex_2026_upstream-facility-statistics_ab-sk{,_nodes,_other-values}.csv.

One example per facility group: the central value is the median over facilities that
reported the throughput in all 12 months of 2024 (Alberta and Saskatchewan together),
value-min and value-max are the 25th and 75th percentiles. Brad 2026-10-21: archetype
sizes are the median of existing facilities, and Petrinex values are graded sourced.
Gas volumes stay in m3; the build converts them (records/reference/example-conversion.csv).
"""
import csv, io, os, zipfile, collections, statistics

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = str(_DOCS), str(_HERE)
STEM = 'petrinex_2026_upstream-facility-statistics_ab-sk'
YEAR = '2024'


def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def g3(x):
    return float('%.4g' % x)


def load_metrics():
    out = {}
    for r in csv.DictReader(open(os.path.join(HERE, 'petrinex_2026_facility-metrics_ab-sk.csv'), encoding='utf-8-sig')):
        if r['year'] == YEAR:
            out[r['facility-id']] = r
    return out


def num(r, k):
    try:
        return float(r.get(k) or 0)
    except ValueError:
        return 0.0


def links(zipname, prov):
    z = zipfile.ZipFile(os.path.join(DOCS, zipname))
    inner = zipfile.ZipFile(io.BytesIO(z.read(f'Well to Facility Link-{prov}.csv.zip')))
    per = collections.defaultdict(list)
    with inner.open(inner.namelist()[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig', errors='replace')):
            per[r['LinkedFacilityID']].append((r['WellStatusFluid'], r['WellStatusMode']))
    return per


def ethane_plants():
    p = os.path.join(HERE, '..', 'aer', 'st50', 'aer_2026_st50a-gas-processing-plants.csv')
    lines = open(p, encoding='latin-1').read().splitlines()
    i = [n for n, l in enumerate(lines) if l.startswith('Reporting Facility ID')][0]
    out = set()
    for r in csv.DictReader(io.StringIO('\n'.join(lines[i:]))):
        def f(k):
            try:
                return float((r.get(k) or '0').replace(',', '') or 0)
            except ValueError:
                return 0.0
        if f('C2 m3/d') + f('C2 Mix m3/d') > 0:
            out.add(r['Reporting Facility ID'])
    return out


def main():
    M = load_metrics()
    full = {k: r for k, r in M.items() if r['full-year'] == 'yes'}
    rows, nodes, other = [], [], []

    def example(proc, techs, sector, end_use, unit_svc, desc, values):
        for t in techs:
            nodes.append([proc, t, sector, end_use, '', unit_svc])
            rows.append([proc, t, 'description', '', '', desc, '', '', '', '', ''])
            for v in values:
                rows.append([proc, t] + v)

    def dist(vals, param, unit, target='', note='', ref=''):
        return [param, target, unit, g3(q(vals, .5)), g3(q(vals, .25)), g3(q(vals, .75)),
                'median (p25-p75) of %d facilities' % len(vals), ref, note]

    REF = 'Petrinex public data, conventional volumetrics %s (activity/product totals per reporting facility)' % YEAR

    def grp(groups, metric, cond=None):
        return [num(r, metric) for r in full.values() if r['group'] in groups and num(r, metric) > 0
                and (cond is None or cond(r))]

    # gas plants
    sour = grp({'gas-plant-sour'}, 'gas-received_m3')
    example('Sour gas plants (Petrinex subtypes 402-405), AB and SK, %s' % YEAR,
            ['gas-treatment-unit_amine-sweetening'], 'oil-and-gas', 'natural-gas processing', 'm3',
            'Alberta and Saskatchewan sour gas plants (acid gas flaring, acid gas injection or sulphur recovery): inlet gas received per plant.',
            [dist(sour, 'annual-output', 'm3/yr', ref=REF + '; REC GAS',
                  note='Inlet gas received (REC GAS, e3m3 x 1000) per plant, full-year plants. CAPACITY BASIS: product-output (gas processed). Whole plant, of which the amine unit is one part.')])
    sweet = grp({'gas-plant-sweet'}, 'gas-received_m3')
    example('Sweet gas plants (Petrinex subtype 401), AB and SK, %s' % YEAR,
            ['gas-treatment-unit_glycol-dehydration'], 'oil-and-gas', 'natural-gas processing', 'm3',
            'Alberta and Saskatchewan sweet gas plants (dehydration and dew-point control): inlet gas received per plant.',
            [dist(sweet, 'annual-output', 'm3/yr', ref=REF + '; REC GAS',
                  note='Inlet gas received per plant, full-year plants. CAPACITY BASIS: product-output (gas processed).')])
    eth = ethane_plants()
    deep = [num(full[k], 'gas-received_m3') for k in eth if k in full and num(full[k], 'gas-received_m3') > 0]
    example('Ethane-recovery gas plants (ST50A licensed C2 capacity > 0), AB, %s' % YEAR,
            ['turboexpander_ngl-recovery', 'adsorber_molecular-sieve'], 'oil-and-gas', 'natural-gas processing', 'm3',
            'Alberta gas plants licensed to recover ethane (deep-cut, turboexpander plants with molecular-sieve dehydration): inlet gas received per plant.',
            [dist(deep, 'annual-output', 'm3/yr', ref=REF + '; REC GAS; plant list from AER ST50A',
                  note='Plants with licensed C2 or C2-mix capacity in AER ST50A (aer_2026_003), joined on facility ID. CAPACITY BASIS: product-output (gas processed).')])
    # gathering systems -> pneumatic devices
    ggs = grp({'gas-gathering-system'}, 'gas-received_m3')
    example('Gas gathering systems (Petrinex subtypes 621-622), AB and SK, %s' % YEAR,
            ['pneumatic-device_gas-driven', 'pneumatic-device_low-bleed', 'pneumatic-device_non-emitting'],
            'oil-and-gas', 'natural-gas supply venting', 'm3',
            'Gas gathering systems and compressor sites, the field sites where pneumatic devices sit: gas received per site.',
            [dist(ggs, 'annual-output', 'm3/yr', ref=REF + '; REC GAS',
                  note='Gas received per gathering system, full-year sites. CAPACITY BASIS: product-output (gas handled). The site throughput the pneumatic devices serve.')])
    # oil batteries -> line heater / oil treating
    bat = grp({'crude-oil-battery-multiwell'}, 'oil-produced_m3')
    example('Crude oil multiwell batteries (Petrinex subtypes 321, 322, 326, 327), AB and SK, %s' % YEAR,
            ['direct-heater_line-heater', 'heat-pump_oil-treating'], 'oil-and-gas', 'crude oil production treating', 'm3',
            'Crude oil multiwell group and proration batteries, where line heaters and treaters heat the produced emulsion: oil produced per battery.',
            [dist(bat, 'annual-output', 'm3/yr', ref=REF + '; PROD OIL',
                  note='Oil produced per battery, full-year batteries. CAPACITY BASIS: product-output (oil treated).')])
    fe = grp({'crude-oil-battery-multiwell'}, 'fuel-energy-per-oil-produced_GJ/m3')
    other.append(['Crude oil multiwell batteries, AB and SK, %s' % YEAR, 'direct-heater_line-heater', 'whole-battery fuel gas per m3 oil (HHV 38.39 MJ/m3)',
                  '%s (%s-%s), n=%d' % (g3(q(fe, .5)), g3(q(fe, .25)), g3(q(fe, .75)), len(fe)), 'GJ/m3', REF,
                  'Not loaded: battery fuel also feeds engines, compressors and treaters, so it is not the line heater alone.'])
    # flares
    fl = grp({'crude-oil-battery-multiwell', 'crude-oil-battery-single-well', 'bitumen-battery-cold'}, 'flared-gas_m3')
    example('Oil and cold-bitumen batteries that flared (Petrinex subtypes 311-342), AB and SK, %s' % YEAR,
            ['flare', 'flare_high-efficiency'], 'oil-and-gas', 'natural-gas supply flaring', 't',
            'Solution-gas flares at oil and cold-bitumen batteries: gas flared per flaring battery.',
            [dist(fl, 'annual-output', 'm3/yr', ref=REF + '; FLARE GAS',
                  note='Gas flared per battery that flared, full-year batteries; the build puts it in t CO2 at the ECCC NIR marketable-gas factor (records/reference/example-conversion.csv). CAPACITY BASIS: product-output (CO2 from flaring). Solution gas is richer than marketable gas, so the CO2 is a lower bound.')])
    # disposal
    dsp = grp({'water-disposal'}, 'water-injected_m3')
    example('Water disposal facilities (Petrinex subtypes 503, 507, 509 and SK equivalents), AB and SK, %s' % YEAR,
            ['well_disposal-injection'], 'oil-and-gas', 'produced water disposal', 'm3',
            'Produced and waste water disposal facilities: water injected per facility.',
            [dist(dsp, 'annual-output', 'm3/yr', ref=REF + '; INJ WATER',
                  note='Water injected per disposal facility, full-year facilities. A facility can serve more than one well. CAPACITY BASIS: product-output (water handled).')])
    # artificial lift: AB single-well batteries whose only linked well is a pumping oil well
    lk = links('petrinex_2026_public-data_ab.zip', 'AB')
    lift = [num(r, 'oil-produced_m3') for k, r in full.items()
            if r['subtype'] == '311' and r['province'] == 'AB' and num(r, 'oil-produced_m3') > 0
            and len(lk.get(k, [])) == 1 and lk[k][0] == ('CR-OIL', 'PUMP')]
    example('Pumping oil wells on single-well batteries (Petrinex subtype 311, well mode PUMP), AB, %s' % YEAR,
            ['pump_artificial-lift'], 'oil-and-gas', 'crude oil production lifting', 'm3',
            'Alberta single-well crude oil batteries whose one linked well is a pumping oil well: oil lifted per well.',
            [dist(lift, 'annual-output', 'm3/yr', ref=REF + '; PROD OIL; Well to Facility Link (mode PUMP)',
                  note='Oil produced per pumping well. The well mode is the current (2026) status from the link file. CAPACITY BASIS: product-output (oil lifted).')])
    # in-situ schemes
    ins = [r for r in csv.DictReader(open(os.path.join(HERE, 'petrinex_2026_in-situ-scheme-intensity.csv'), encoding='utf-8-sig'))
           if r['full-year'] == 'yes']
    for proc, tech, label in (('sagd', 'well_sagd', 'SAGD'), ('css', 'well_cyclic-steam', 'cyclic steam')):
        out24 = [float(r['bitumen-produced_m3']) for r in ins if r['recovery-process'] == proc and r['year'] == YEAR]
        by = collections.defaultdict(list)
        for r in ins:
            if r['recovery-process'] == proc and r['cogeneration'] == 'no' and r['year'] in ('2022', '2023', '2024'):
                by[r['scheme']].append(r)
        sec = [statistics.mean(float(x['fuel-energy-per-bitumen_GJ-HHV-per-m3']) for x in v) for v in by.values()]
        fuel_m3 = [statistics.mean(float(x['fuel-gas_m3']) / float(x['bitumen-produced_m3']) for x in v) for v in by.values()]
        sor = [statistics.mean(float(x['steam-oil-ratio']) for x in v) for v in by.values()]
        pr = '%s schemes (Petrinex battery 344 paired with injection facility 506), AB and SK' % label
        example(pr, [tech], 'oil-and-gas', 'bitumen in-situ', 'm3',
                'In-situ %s schemes: bitumen produced per scheme or plant, and scheme fuel gas per m3 of bitumen.' % label,
                [dist(out24, 'annual-output', 'm3/yr', ref=REF + '; PROD OIL at the 344 battery',
                      note='Bitumen produced per scheme or plant in %s, all paired schemes incl. cogeneration sites (petrinex_2026_in-situ-scheme-pairs.csv). CAPACITY BASIS: product-output (bitumen).' % YEAR),
                 dist(fuel_m3, 'specific-energy-consumption', 'm3/m3', target='natural-gas', ref='Petrinex conventional volumetrics 2022-2024; FUEL GAS at the 344 and 506 facilities',
                      note='Scheme fuel gas (battery plus injection facility) per m3 of bitumen, mean of 2022-2024 per scheme, then median across %d schemes without on-site cogeneration (at cogeneration sites the turbine fuel is not booked as FUEL at the scheme). Gas volume at 15 degC; the build converts to GJ HHV at the ECCC NIR marketable-gas factor. heating-value basis: HHV (Alberta measurement convention).' % len(fuel_m3)),
                 dist(fuel_m3, 'specific-energy-consumption', 'm3/m3', ref='as the natural-gas row',
                      note='Total: the scheme fuel gas, the only energy Petrinex reports (no electricity), so the total is the fuel alone. heating-value basis: HHV.')])
        other.append([pr, tech, 'steam-oil ratio (m3 cold-water-equivalent per m3), 2022-2024 per-scheme mean', '%s (%s-%s), n=%d' % (g3(q(sor, .5)), g3(q(sor, .25)), g3(q(sor, .75)), len(sor)), 'm3/m3', 'Petrinex INJ STEAM / PROD OIL', 'Schemes without cogeneration.'])
        other.append([pr, tech, 'fuel energy per m3 bitumen at HHV 38.39 MJ/m3', '%s (%s-%s)' % (g3(q(sec, .5)), g3(q(sec, .25)), g3(q(sec, .75))), 'GJ/m3', 'derived', 'Same schemes; check on the converted SEC.'])
    H = ['process', 'technology', 'parameter', 'target', 'unit', 'value', 'value-min', 'value-max', 'formula', 'reference', 'note']
    for name, hdr, data in ((STEM + '.csv', H, rows),
                            (STEM + '_nodes.csv', ['process', 'technology', 'sector', 'end-use', 'process-step', 'service-unit'], nodes),
                            (STEM + '_other-values.csv', ['process', 'technology', 'item', 'value', 'unit', 'reference', 'note'], other)):
        with open(os.path.join(HERE, name), 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(hdr); w.writerows(data)
    for r in rows:
        if r[2] != 'description':
            print(r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])


if __name__ == '__main__':
    main()
