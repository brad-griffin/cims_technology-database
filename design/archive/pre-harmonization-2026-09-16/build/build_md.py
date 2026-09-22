"""Render design/sector-end-use-table.md from the two design CSVs.

Run from anywhere:   python design/build/build_md.py

Every path is resolved from this file's own location, not from the working
directory and not from a home directory: the inputs sit beside the script in a
fixed layout, so the script can find them itself. The paths used to be spelled
~/mnt/tech_data/..., which is where the repo happens to be mounted in one
environment -- that made the script unrunnable anywhere else, including on the
machine the repo actually lives on.
"""
import sys, csv, re, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent      # design/build
DESIGN = HERE.parent                        # design

# the sibling modules are imported by name, so this script must be able to find
# them whatever the working directory is
sys.path.insert(0, str(HERE))
import md_notes, heat_source, draws_on, tech_rows

P = DESIGN / 'sector-end-use-table.csv'
OUT = DESIGN / 'sector-end-use-table.md'
TECH_CSV = DESIGN / 'end-use-technology-table.csv'
R = list(csv.DictReader(open(P, encoding='utf-8')))
ids = [r['end-use'] for r in R]; assert len(ids) == len(set(ids))
for d in (md_notes.NOTE, heat_source.HD, heat_source.NOTE_ADD):
    for k in d: assert k in ids, k
# the draws-on column replaced heat_source.HS: one validated list per end use,
# rendered into the Heat source and Draws on columns and reversed into
# "Drawn on by" (the user, 2026-09-15)
draws_on.check(R)
DRAWN_ON_BY = draws_on.drawn_on_by(R)

BR = re.compile(r'\s*\[([^\]]+)\]')
PAREN = {' (Oil Sands Magazine)': 'Oil Sands Magazine', ' (historical, Alberta Energy Heritage)': 'Alberta Energy Heritage'}
CELLS = ('covers', 'heat-demand-temp', 'draws-on', 'steam', 'energy-inputs', 'cims-services', 'note')

def strip(v):
    v = BR.sub('', v)
    for p in PAREN: v = v.replace(p, ' (historical)' if 'historical' in p else '')
    return re.sub(r'\s+([.;,])(\s|$)', r'\1\2', v).strip()

def norm(keys):
    loc = collections.OrderedDict()
    def add(base, l):
        loc.setdefault(base, [])
        for x in l:
            if x and x not in loc[base]: loc[base].append(x)
    for k in keys:
        k = re.sub(r'\s*\([^)]*\)', '', k).strip()
        k = k.replace('NRCan Energy Use in Canada: Trends 2017', 'NRCan Trends 2017')
        k = k.replace('UKERC CH-SC28 via johansson_2012_001', 'ukerc_2013_001 CH-SC28 via johansson_2012_001')
        if k.startswith(('NREL97', 'SIC ')):
            add('NREL97', [('row ' + m) if k.startswith('NREL97 row') else m for m in re.findall(r'\b(\d{6}|\d{4}|\d{2}xx)\b', k)]); continue
        m = re.match(r'([a-z-]+_\d{4}_\d{3})\s*(.*)$', k)
        if m:
            base, rest = m.group(1), m.group(2)
            if base == 'ipcc_2022_001':
                add(base, [rest] if not loc.get(base) else []); continue
            add(base, [x.strip() for x in re.split(r',\s*(?=p\.)', rest) if x.strip()] if rest else []); continue
        m = re.match(r'(NREL118)\s*(.*)$', k)
        if m: add('NREL118', [m.group(2)] if m.group(2) else []); continue
        add(k, [])
    out = []
    for base, l in loc.items():
        if base == 'NREL97' and l: out.append('NREL97 SIC ' + ', '.join(l))
        else: out.append((base + ' ' + ', '.join(l)).strip())
    return '; '.join(out).replace('NREL97 SIC row', 'NREL97 row').replace('Ferroglobe Becancour', 'Ferroglobe Bécancour')

for r in R:
    e = r['end-use']
    # 1. sources, from the ORIGINAL cells before any display override
    refs = []
    for col in CELLS:
        for m in BR.findall(r[col]): refs += [x.strip() for x in m.split(';')]
        for p, k in PAREN.items():
            if p in r[col]: refs.append(k)
    refs += md_notes.SRC.get(e, [])
    refs += [x.strip().replace(' (web)', '') for x in r['sources'].split(';') if x.strip()]
    r['_src'] = norm([x for i, x in enumerate(refs) if x and x not in refs[:i]])
    # 2. display overrides
    for (fe, fc), v in md_notes.FIELD.items():
        if fe == e: r[fc] = v
    if e in md_notes.NOTE: r['note'] = md_notes.NOTE[e]
    r['note'] = strip(r['note'])
    if e in heat_source.NOTE_ADD: r['note'] = (r['note'] + ' ' + heat_source.NOTE_ADD[e]).strip()
    r['_hd'] = heat_source.HD.get(e, strip(r['heat-demand-temp']))
    parts = draws_on.parse(r['draws-on'])
    heat = [(t_, d) for t_, d in parts if t_.startswith('heat-') or t_ == 'integral'
            or (t_ == 'none' and 'source' in d)]
    other = [(t_, d) for t_, d in parts if (t_, d) not in heat and t_ != 'none']
    hs = []
    for t_, d in heat:
        if t_ == 'integral':
            hs.append(f'Integral ({d})')
        elif t_ == 'none':
            hs.append('Is a source: supplies other end uses')
        else:
            hs.append(f'From `{t_}` ({d})')
    if not hs:
        rest = [d for t_, d in parts if t_ == 'none' and d]
        hs = [f'— ({rest[0]})'] if rest else ['—']
    r['_hs'] = '<br>'.join(hs)
    r['_draws'] = '<br>'.join(f'`{t_}` ({d})' for t_, d in other) or '—'
    users = DRAWN_ON_BY.get(e, [])
    if users:
        shown = users if len(users) <= 6 else users[:6]
        more = '' if len(users) <= 6 else f' and {len(users) - 6} more'
        r['note'] = (r['note'] + ' ' if r['note'] else '') + (
            f"Drawn on by {len(users)} end use{'s' if len(users) > 1 else ''}: "
            + ', '.join(f'`{u}`' for u in shown) + more + '.')
    for col in ('covers', 'energy-inputs'): r[col] = strip(r[col])

def c(s): return s.replace('<sector>', '[sector]').replace('degC', '°C').replace('degF', '°F').replace('|', '/')
FROM_RX = re.compile(r'(^|<br>|, or |\(absorption chillers: |\(amine pre-treatment: )([Ff])rom `')
def hsrc(r):
    return c(r['_hs'])
def heat(r):
    tier = r['heat-tier'].strip()
    if tier.lower().startswith('none'): return '—'
    return f"*{c(tier)}*" + (f"<br>{c(r['_hd'])}" if r['_hd'] else '')

# the technology table is generated from tech_rows.py, so it is rebuilt here
# rather than read as found: one command then rebuilds both outputs, and an
# edit to tech_rows.py cannot reach the .md while leaving the .csv stale
print(f"  end-use-technology-table.csv  {tech_rows.write()} rows")
TECH = list(csv.DictReader(open(TECH_CSV, encoding='utf-8')))
_eu_label = {r['end-use']: r['end-use-label'] for r in R}
for _t in TECH:
    assert _t['end-use'] in _eu_label, _t['end-use']
    _t['_src'] = norm([x.strip() for x in (_t['trl-basis'] + '; ' + _t['sources']).split(';') if x.strip()])
LABEL = {'cross-sector': 'Cross-sector', 'iron-and-steel': 'Iron and steel', 'cement': 'Cement', 'non-metallic-minerals': 'Non-metallic minerals',
 'chemicals': 'Chemicals', 'biofuels': 'Biofuels', 'petroleum-refining': 'Petroleum refining', 'pulp-and-paper': 'Pulp and paper',
 'mining': 'Mining (including coal mining)', 'oil-and-gas': 'Oil and gas (extraction, processing and pipelines)',
 'food-and-beverage': 'Food and beverage', 'non-ferrous-metals': 'Non-ferrous metals', 'other-industry': 'Other industry',
 'hydrogen': 'Hydrogen (centralised production and distribution)'}
out = [open(HERE / 'md_head.md', encoding='utf-8').read()]
order = []
for r in R:
    if r['sector'] not in order: order.append(r['sector'])
for s in order:
    out.append(f"\n<br>\n\n---\n\n### {LABEL[s]}\n")
    out.append("| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |\n| - | - | - | - | - | - | - | - |")
    for r in [x for x in R if x['sector'] == s]:
        out.append(f"| **{c(r['end-use-label'])}** `{r['end-use']}` | {c(r['covers'])} | {heat(r)} | {hsrc(r)} | {c(r['_draws'])} | {c(r['energy-inputs'])} | {c(r['note']) or '—'} | {c(r['_src'])} |")
    techs = [x for x in TECH if x['sector'] == s]
    if techs:
        out.append(f"\n**Technologies**\n")
        out.append("| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |\n| - | - | - | - | - | - | - | - |")
        prev = None
        for x in techs:
            label = f"`{x['end-use']}`" if x['end-use'] != prev else ''
            prev = x['end-use']
            out.append(f"| {label} | **{c(x['technology'])}** | {c(x['type'])} | {c(x['description'])}{('<br>*' + c(x['note']) + '*') if x['note'] else ''} | {c(x['energy-inputs'])} | {c(x['trl']) or '—'} | {c(x['examples']) or '—'} | {c(x['_src'])} |")
out.append(open(HERE / 'md_tail.md', encoding='utf-8').read())
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('written', sum(1 for _ in open(OUT, encoding='utf-8')))
