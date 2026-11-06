#!/usr/bin/env python3
"""
Split the 2006 onsite-generation losses across boilers, cogeneration and other generation.

The problem
-----------
The 2006 footprint charts publish only two generation-loss totals per sector -- one for
steam generation and one for electricity generation -- with no breakdown by source.
doe_2012_mecs-2006-energy-footprint.csv books that whole combined figure against `cogeneration`
and leaves `boilers` and `other` at zero.  Any efficiency derived from those rows is
therefore meaningless, and negative wherever a sector ran mostly boilers.  From 2010
onward the charts split the loss by source themselves, so only 2006 needs this treatment.

The method: implied balance
---------------------------
Every conversion step must satisfy  input - loss = output.  Both sides of that identity
are already reported per source, so the loss follows directly:

    boilers       loss = (fuel in + electricity in) - steam out
    cogeneration  loss =  fuel in - (steam out + electricity out)
    other         loss =  fuel in - electricity out

No weighting or assumption is involved -- each source's loss is whatever its own flows
imply, and every per-source energy balance closes by construction.

Because all source values are whole TBtu, the implied losses are whole TBtu too, so no
rounding is applied and no rounding error is introduced.

The one exception: renewable generation
---------------------------------------
"Other electricity generation" also covers onsite renewable, non-combustion generation,
whose output the charts report without any corresponding fuel input.  A sector with more
of that than of fuelled other-generation produces a NEGATIVE implied loss, which is not a
loss at all but uncounted renewable input.  Those are clamped to zero and listed on
completion, since a negative loss would poison any efficiency computed from it.  In the
2006 data this affects forest_products alone.

Inputs and outputs
------------------
Reads  doe_2012_mecs-2006-energy-footprint.csv  (no PDF or spreadsheet dependency; the flows this
calculation relies on were checked against the flowchart PDFs in a separate pass).
Writes doe_2012_mecs-2006-energy-footprint-realloc.csv and a per-row change log
(doe_2012_mecs-2006-generation-loss-realloc-log.csv), beside this script.
"""

import csv
import io
import os
import sys

import pandas as pd

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
SRC = os.path.join(HERE, 'doe_2012_mecs-2006-energy-footprint.csv')
OUT = os.path.join(HERE, 'doe_2012_mecs-2006-energy-footprint-realloc.csv')
LOG = os.path.join(HERE, 'doe_2012_mecs-2006-generation-loss-realloc-log.csv')

raw = open(SRC, newline='').read()
rows = list(csv.reader(io.StringIO(raw)))
hdr, body = rows[0], rows[1:]
C = {c: i for i, c in enumerate(hdr)}

SECTORS = sorted({r[C['name']] for r in body})


def find(sector, flow, typ, end_use_2):
    """Locate the single row for one sector / flow / type / generation source."""
    hits = [i for i, r in enumerate(body)
            if r[C['name']] == sector and r[C['flow']] == flow and r[C['type']] == typ
            and r[C['end_use_1']] == 'onsite generation' and r[C['end_use_2']] == end_use_2]
    assert len(hits) == 1, (sector, flow, typ, end_use_2, len(hits))
    return hits[0]


def val(sector, flow, typ, end_use_2):
    return float(body[find(sector, flow, typ, end_use_2)][C['value']])


log, clamped = [], []
for sec in SECTORS:
    # --- what each source consumes and produces -----------------------------------
    sources = {
        'boilers': (
            val(sec, 'input', 'fuel', 'boilers') + val(sec, 'input', 'electricity', 'boilers'),
            val(sec, 'output', 'steam', 'boilers'),
        ),
        'cogeneration': (
            val(sec, 'input', 'fuel', 'cogeneration'),
            val(sec, 'output', 'steam', 'cogeneration') + val(sec, 'output', 'electricity', 'cogeneration'),
        ),
        'other': (
            val(sec, 'input', 'fuel', 'other'),
            val(sec, 'output', 'electricity', 'other'),
        ),
    }

    for label, (src_in, src_out) in sources.items():
        implied = src_in - src_out                      # the loss this source's balance implies
        loss = max(implied, 0.0)                        # see "The one exception" above
        if implied < 0:
            clamped.append((sec, label, implied, src_in, src_out))
        assert loss == int(loss), (sec, label, loss)

        old = val(sec, 'loss', 'combined', label)
        body[find(sec, 'loss', 'combined', label)][C['value']] = '%d' % loss
        log.append(dict(
            mecs_year=2006, sector=sec, flow='loss', type='combined',
            end_use_1='onsite generation', end_use_2=label,
            old_value=int(old), new_value=int(loss),
            source_input=int(src_in), source_output=int(src_out),
            note='loss = input - output for this source'
                 + ('; negative implied loss clamped to 0 (uncounted renewable output)' if implied < 0 else ''),
        ))

out = io.StringIO()
w = csv.writer(out, lineterminator='\r\n')          # the source file is CRLF
w.writerow(hdr)
w.writerows(body)
open(OUT, 'w', newline='').write(out.getvalue())

df = pd.DataFrame(log)
df.to_csv(LOG, index=False)

changed = int((df.old_value != df.new_value).sum())
print(f'wrote {OUT} and {LOG}', file=sys.stderr)
print(f'  {changed} of {len(df)} generation-loss rows changed', file=sys.stderr)

if clamped:
    print(f'\n  {len(clamped)} source(s) with a negative implied loss, clamped to 0:', file=sys.stderr)
    for sec, label, implied, src_in, src_out in clamped:
        print(f'    {sec} / {label}: {src_in:.0f} in, {src_out:.0f} out '
              f'-> implied {implied:+.0f}; output exceeds fuel input because onsite '
              f'renewable generation carries none', file=sys.stderr)
