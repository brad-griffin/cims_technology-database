#!/usr/bin/env python3
"""
Derive share and efficiency metrics from the MECS energy-footprint CSVs.

Background
----------
Each `doe_<pub-year>_mecs-<year>-energy-footprint.csv` is a Sankey energy-flow diagram flattened into
rows.  For one manufacturing sector in one survey year, energy is:

    import              purchased from offsite (fuel, electricity, steam)
    input               delivered to an end use (process heating, facility HVAC, ...)
    input_combined      delivered to a machine-drive component (pumps, fans, ...),
                        already blended across fuel/electricity/steam
    output              produced onsite (steam from boilers, electricity from cogeneration)
    loss                energy that entered an end use but did no useful work
    export              sold or transferred offsite
    share               fuel-mix percentages, not an energy flow

In the input files `value` is TBtu for every flow except `share`.  An end use is identified either by the
three-part key `end_use_1` / `end_use_2` / `end_use_3` or by the pre-joined `end_use`
column ("process_machine drive_pumps").

This script adds five derived columns that turn those absolute flows into ratios you can
compare across sectors and years, and appends a second block of rows carrying a sixth
column, `share_of_fuel`, taken from a different source (see below).

The five derived columns (on the footprint rows)
------------------------------------------------
share_of_type
    Within one (sector, flow, energy type), how that energy divides across end uses.
    Example: of all the fuel a sector puts into end uses, the fraction going to process
    heating.  Values within a group sum to 1.

share_of_end_use
    Within one (sector, flow, end use), how that energy divides across the types
    fuel / electricity / steam.  Example: of everything reaching process heating, the
    fraction arriving as steam.  Values within a group sum to 1.

efficiency
    For a loss row, the fraction of the energy entering that end use that did useful
    work:  1 - loss / (everything delivered to the end use).
    Only computed for loss rows at or above `--threshold` (see "Why the threshold").
    Left blank on every other row.

share_of_steam
    For a steam output row, that source's share of the sector's total onsite steam.
    Reading the boiler and cogeneration rows together tells you how the sector's steam
    is raised.  Blank on other rows and below the threshold.

heat_to_power_ratio
    For cogeneration, TBtu of steam produced per TBtu of electricity produced.
    Computed from steam's share `r` of total cogeneration output as r / (1 - r), which is
    algebraically steam / electricity but keeps the arithmetic in one place.
    Blank on other rows and below the threshold.

The sixth column: share_of_fuel (on its own rows)
---------------------------------------------------
The footprint files say how much energy reached each end use, and separately what a
sector's fuel mix was, but never the two together -- they cannot tell you what share of a
sector's natural gas went to process heating.  MECS Table 5.4, "End Uses of Fuel
Consumption", does report that crossing, so this script reads it from each year's
subfolder and appends the answer as extra rows:

    flow=input, type=fuel, end_use_1/2 as in the footprint, fuel_type named,
    value_table = what Table 5.4 prints for that sector, end use and fuel (in PJ),
    value       = the gap-filled, balanced estimate (see "Gap-filled Table 5.4 rows"),
    share_of_fuel = that end use's share of the fuel, from `value`

By default these rows are tagged `data_source=table_5_4_est`, and `note`
walks from value_table to value, e.g.

    table: 2.11; -0.18 rounding balance; +0.22 End Use Not Reported (pro rata); = 2.15

value_table is the sum of the printed numbers over the sector's NAICS blocks (and over
residual + distillate for fuel oil), `*` and `--` counting as 0; it is empty when any
cell behind it is withheld ("table: withheld") or nothing behind it is printed but `*`
("table: <0.53 (*)", i.e. under 0.5 TBtu).  A blank note means value equals value_table.  The other row
kinds leave value_table empty: footprint rows' value is the footprint figure itself,
residual rows' is estimated.  With --no-estimates the rows are the printed table as is,
tagged `data_source=table_5_4`, value and value_table equal.

Points to keep in mind when using them:

* They are a DIFFERENT accounting basis and are tagged `data_source=table_5_4_est` to keep
  them apart.  Table 5.4 covers six energy sources only -- electricity, residual fuel oil,
  distillate/diesel, natural gas, HGL, coal -- so byproduct fuels, coke and biomass are
  absent and these rows will not reproduce a sector's footprint fuel mix.  Do not add
  them to footprint rows: `flow=input` is shared, and only `fuel_type` (blank on
  footprint inputs) and `data_source` distinguish them.

* "End Use Not Reported" is spread across the end uses that WERE reported, in proportion
  to their size, within each industry and fuel -- the way the DOE footprints themselves
  treat it (their electricity end uses match Table 5.4 grossed up pro rata, not with the
  unreported amount added to process heating).  So the shares still describe the
  sector's whole reported consumption, and the residual subtraction compares like with
  like.  A fuel with nothing reported at any end use falls back to process heating.
  `--unreported process-heating` restores the old rule of folding it all into process
  heating.

* Each share is `end use / the sector's REPORTED total` for that fuel, not a share of the
  re-summed end uses.  That way one withheld end use blanks only its own share instead of
  invalidating the fuel, but it also means the shares need not add to exactly 1: EIA
  prints anything under 0.5 TBtu as `*`, which is read as zero, so for a small fuel a real
  slice of the total is never allocated.  `note` records the shortfall
  where it exceeds 2%.  The shares are deliberately NOT renormalised.

* Withheld cells (Q, W, D, C) leave both `value` and the share empty, with the reason in
  `note`.  When a sector is the sum of several NAICS blocks, one withheld
  component makes the whole cell unknown.

* Every Table 5.4 found under the tables folder is used, not only the footprint years.
  2002 and 2022 have no footprint, so they get Table 5.4 rows (published and estimated)
  for the sectors of the nearest footprint year -- 2006's for 2002, 2018's for 2022, plus
  any sector a further year adds -- and no residual rows.  A sector whose NAICS blocks a
  survey does not publish is skipped with a message (2002 has no 3364 and only one of the
  two auto codes, so no aerospace or automobile rows).

Gap-filled Table 5.4 rows (data_source=table_5_4_est)
-----------------------------------------------------
The Table 5.4 rows with withheld and `*` cells estimated rather than left blank or read
as zero, so that shares add to 1.  Table 5.4 is additive in every fuel column -- end uses sum
to subtotals and subtotals to the total within an industry, 3-digit industries sum to all
manufacturing -- so most withheld cells are the only unknown in some sum and follow from
it exactly, to rounding: hiding 5% of the published cells and re-deriving them misses by
a median 0.5 TBtu, and 90% land within 1 TBtu.  Cells that share a sum with other
unknowns split its residual in proportion to the nearest other survey (median miss 0.6
TBtu, ~12%).  Every estimate is clamped to what its own industry's subtotals allow.
The reconciliation step below then pulls every withheld cell toward what the nearest
other survey(s) say (standard deviation max(0.5, half the prior) TBtu), as far as the
printed numbers allow: where a withheld cell is only loosely pinned -- say by a subtotal
it shares with several `*` cells -- the neighbouring surveys decide where it sits, while
a withheld cell boxed in by printed siblings barely moves.  Re-deriving hidden cells of
3 TBtu or less, this cuts the median miss from 0.5 to 0.36 TBtu.  Each
`*` cell gets an equal slice, capped at 0.5 TBtu, of whatever its parent row leaves
unallocated.  Finally, because EIA rounds every cell independently (a printed total of 3
over end uses of 1 + 2 + 1), each industry and fuel is reconciled: every cell is moved as
little as possible -- a printed number by at most its rounding, 0.5 TBtu -- until the end
uses add exactly to their subtotals and the subtotals to the total (rounding_balance; see
balance_table54).  Shares are divided by the end uses' own sum, which after balancing is
the total, so they add to exactly 1.  Two 2002 all-manufacturing blocks that EIA printed
inconsistently beyond rounding (distillate boiler fuel 25 over components 25 + 10;
electricity total 3297 over parts adding to 3310) cannot be reconciled and are left as
they are.  The note's steps name these: "withheld cell(s) estimated (identity, ...)",
"for * cells", "rounding balance", and "End Use Not Reported (pro rata)".  --no-estimates
turns this off.

Rows for the fuels Table 5.4 cannot see (data_source=residual)
--------------------------------------------------------------
Coke, coke oven gas, refinery fuel gas, other byproduct fuel, petroleum coke, black liquor,
biomass, hydrogen (2022) and "other" have no column in Table 5.4.  The footprint is DOE's
adjusted MECS, and these rows follow it (see the footprint methodology documents in
data/raw-data/background-no-data-extracted/doe_*_mecs-*-footprint-definitions-and-
assumptions.pdf and doe_2012_manufacturing-energy-use-and-ghg-analysis.pdf, Appendix D):

* The fuels MECS names are measured, every survey year, from Table 3.2 (coke and breeze,
  hydrogen) and Table 3.5 (blast furnace / coke oven gas, waste gas, petroleum coke,
  pulping liquor, wood chips and bark, waste oils and materials) -- see noncovered_totals.
* Coke is cut by two-thirds of Table 3.5's blast furnace / coke oven gas.  This is the
  EIA / DOE adjustment for blast furnace gas made from the coke charged to the furnace
  (counted twice in MECS); it reproduces the iron and steel footprint's coke within
  2-18 TBtu in 2006-2018.  See COKE_BFG_SHARE.
* "Other" is what puts each sector on the footprint's basis.  DOE reworks MECS "Other
  Fuels" sector by sector from "other EIA data sets, other published sources, and
  discussions with industry professionals and EIA staff" (2012 analysis, Appendix D) --
  no rule is published, and in feedstock-heavy sectors most of MECS "other" is dropped
  (chemicals 2018: footprint about 120 TBtu, MECS 420).  So in a footprint year "other"
  is the footprint's fuel total less the Table 5.4 fuels and the byproducts above, and
  the sector's fuel adds up to the footprint's (within a few TBtu, floored at zero).  In
  2002 and 2022 it is MECS "other" times the nearest footprint year's ratio of the two.

Only the split across END USES is inferred:

    residual(end use) = footprint fuel at that end use - Table 5.4 fuel at that end use

Whatever the covered fuels do not account for at an end use came from the fuels Table
5.4 cannot see; normalised, that is their end-use profile.  A footprint year uses its
own; 2002 and 2022 use the nearest footprint year's for the same sector; a sector whose
footprint residual is empty takes the split of its own Table 5.4 fuels.  Every
non-covered fuel in a sector gets the SAME profile -- neither source distinguishes coke
from coke oven gas by end use.  Each row's note gives the fuel's total and its basis,
and where its split came from.

Tables 3.2 / 3.5 also back Table 5.4 itself.  They are the same survey, and Table 3.2's
fuel totals equal Table 5.4's TOTAL rows wherever both print one (2002 differs by 1-3
TBtu in five cells).  So a Table 5.4 total that is withheld but printed in Table 3.2 --
or pinned by Table 3.2's row, total = its sources -- is taken from there (method
table_3_2), and a covered fuel Table 3.2 withholds takes the gap-filled Table 5.4 total.

DOE adjustments NOT reproduced here, because they change no fuel input: CHP electricity
output replaced for four 2018 sectors (plastics, fabricated metals, automobiles,
aluminum); onsite renewable electricity counted as offsite; grid losses net of CHP
steam.  The footprint's losses, steam allocation and machine-drive split are DOE's
assumptions, kept on the footprint rows only.

Details that are easy to get wrong
----------------------------------
* Machine-drive components carry their energy under `input_combined`, not `input`.  The
  efficiency denominator therefore counts every flow whose name STARTS WITH "input", or
  the pumps / fans / compressed-air efficiencies would all divide by zero.

* Steam distribution losses have no input rows of their own — what is being distributed
  is the sector's steam supply.  So when the normal denominator is empty and the row is a
  steam-distribution loss, the denominator becomes (onsite steam output + imported steam).

* Import and export rows have no end use at all.  Their blank `end_use` is treated as a
  real grouping key, so all the import rows for a sector pool together and
  `share_of_end_use` reports the fuel / electricity / steam split of purchased energy.

* Blank is not zero.  The two share columns are 0 when the group genuinely holds no
  energy, which is a measurement.  The other three are left EMPTY when they do not apply
  or fall below the threshold, which is an absence of one.  Keeping them distinct matters
  downstream — an empty efficiency must not be averaged in as 0.

* Grouping is on (mecs_year, sector).  NAICS codes repeat from one survey to the next, so
  keying on sector alone would silently pool 2006 and 2018 together.

Why the threshold
-----------------
Source values are published rounded to whole TBtu.  A ratio built from single-digit
numbers inherits that rounding as large relative error — a loss of 3 against an input of
4 could be anything from 0.13 to 0.57 efficiency.  Rows below `--threshold` (default 10
TBtu) are therefore left blank rather than reported as false precision.  The two share
columns already sum to 1 within their group, so they are not thresholded.

A caveat on 2006 onsite generation
----------------------------------
The 2006 source charts publish only a combined steam-plus-electricity generation loss,
which the data assigns entirely to the cogeneration row while leaving boilers at zero.
Where a sector ran mostly boilers, that loss is then divided by a very small cogeneration
input and `efficiency` comes out negative (plastics_rubber reaches -15).  This is a limit
of the 2006 source, not a fault in the calculation; 2010 onward split the loss by source
and behave normally.  Treat 2006 onsite-generation efficiencies as unusable.

One file per survey year
------------------------
Every column here is a share of a group total, so the same row arriving twice inflates
its own denominator.  Point the script at one file per year: an original and a revised
copy of the same year cannot both be used.  Scanning a directory only picks up files
named `doe_<4-digit year>_mecs-<4-digit year>-energy-footprint.csv` (in the folder or its
per-year subfolders), the output path is excluded even if
named explicitly, and any duplicate row that still gets through aborts the run.

The fuel-mix columns: share_of_end_use and share_of_heat
------------------------------------------------------
share_of_fuel reads DOWN the end uses of one fuel (where does this fuel go?).  Two
columns read ACROSS the fuels instead, pooling the Table 5.4 rows with the residual rows
so that coke, biomass and the other fuels Table 5.4 cannot see are counted:

share_of_end_use   this fuel's share of everything feeding this end use (its fuel mix).
share_of_heat      this fuel's share of the fuel feeding boilers and cogeneration together
                  (the same figure on both rows).

Electricity, a Table 5.4 source, is included.  2002 and 2022 have no residual rows, so
there the pool is the six Table 5.4 sources only.  See add_fuel_mix.

Every run also writes <output>_metadata.md, a guide to each column (write_metadata).

Output column names
-------------------
Every share column is named for what it is a share OF.  Internally the code still uses
the older names and renames on the way out (OUTPUT_NAMES):

    share_of_type     <- end_use_by_type      this end use's share of its energy type
    share_of_end_use  <- type_by_end_use      footprint: this type's share of the end use
                      <- end_use_by_fuel      Table 5.4/residual: this fuel's share of it
    share_of_fuel     <- fuel_by_end_use      this end use's share of its fuel
    share_of_heat     <- heat_by_fuel         this fuel's share of boilers + cogeneration
    share_of_steam    <- boiler_cogen_share   this source's share of onsite steam
    note              <- fuel_by_end_use_note
    efficiency        <- efficency (corrected spelling)

Units
-----
Every energy value written out is in PJ (TBTU_TO_PJ = 1.055056, the International Table
Btu); value_table and the steps in `note` too.  The arithmetic runs in TBtu, as the
sources print, so --threshold is in TBtu.  The footprint fuel-mix rows (flow=share) hold
fractions, labelled `fraction` (the source files say `%`).

Usage
-----
  python mecs_footprint_metrics.py INPUT...  [-o OUTPUT.csv] [--per-year] [--threshold 10]

  python mecs_footprint_metrics.py . -o emrg_2026_mecs-footprint-metrics.csv
  python mecs_footprint_metrics.py 20*/doe_*_mecs-*-energy-footprint.csv --per-year

Table 5.4 is looked for at <tables-dir>/<year>/eia_<pub-year>_mecs-<year>-table-5-4.xls[x],
for every <year> folder that has one;
--tables-dir defaults to the mecs folder (the parent of the per-year folder the first input
file came from, or that folder itself if it is not a year folder), and --no-fuel-by-end-use turns the pass off.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------------------

SOURCE_COLUMNS = [
    "mecs_year", "sector", "name", "flow", "type",
    "end_use_1", "end_use_2", "end_use_3", "end_use", "fuel_type", "value", "unit",
]
DERIVED_COLUMNS = [
    "end_use_by_type", "type_by_end_use", "efficiency",
    "boiler_cogen_share", "heat_to_power_ratio",
]
# Added by the Table 5.4 pass.  These live on their own rows, never alongside the five
# above: the footprint and Table 5.4 are different accounting bases and mixing their
# numbers in one row would invite exactly that mistake.
TABLE54_COLUMNS = ["fuel_by_end_use", "end_use_by_fuel", "heat_by_fuel",
                   "fuel_by_end_use_note"]
# Which file a row came from.  Also what keeps the Table 5.4 rows out of the group totals
# behind the five derived columns -- they share `flow="input"` with real footprint rows.
SOURCE_TAG = "data_source"

# Minimum TBtu for a row to get an efficiency, steam share or heat-to-power ratio.
# Below this, source rounding to whole TBtu dominates the ratio (see "Why the threshold").
DEFAULT_THRESHOLD = 10.0

# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------


# Every TBtu written out is converted to petajoules (1 Btu = 1055.056 J, the
# International Table Btu; data/harmonized/records/reference/unit-conversion.csv rounds the
# same factor to 1.0551 for MMBtu -> GJ).  All arithmetic runs in TBtu, the unit every
# source prints, so thresholds such as --threshold stay in TBtu.
TBTU_TO_PJ = 1.055056

# `value` is written to 3 significant figures, but never rounded past the units place:
# the source TBtu are whole numbers, so 1573 stays 1573 while 2.0423 becomes 2.04.
# Everything derived from `value` (shares, efficiencies, notes) is computed unrounded; the
# share columns are then rounded to 3 decimal places by round_shares, which keeps their
# sums at exactly 1.
VALUE_SIG_FIGS = 3


def round_sig(x, sig: int = VALUE_SIG_FIGS):
    """Round to `sig` significant figures, keeping at least the whole-number digits."""
    v = np.asarray(pd.to_numeric(x, errors="coerce"), dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        mag = np.floor(np.log10(np.abs(v)))
    decimals = np.where(np.isfinite(mag), np.maximum(sig - 1 - mag, 0), 0).astype(int)
    out = np.array([round(a, d) if np.isfinite(a) else a for a, d in zip(v, decimals)])
    return pd.Series(out, index=x.index) if isinstance(x, pd.Series) else out


# The share columns, and the rows each one adds to 1 over (see round_shares).
SHARE_GROUPS = {
    "end_use_by_type":    ["mecs_year", "sector", "flow", "type", "data_source"],
    "type_by_end_use":    ["mecs_year", "sector", "flow", "end_use", "data_source"],
    "boiler_cogen_share": ["mecs_year", "sector", "data_source"],
    "fuel_by_end_use":    ["mecs_year", "sector", "fuel_type", "data_source"],
    # these two pool the table_5_4_est and residual rows (see add_fuel_mix)
    "end_use_by_fuel":    ["mecs_year", "sector", "end_use"],
    "heat_by_fuel":       ["mecs_year", "sector", "end_use"],
}


SHARE_DECIMALS = 2


def round_shares(out: pd.DataFrame) -> pd.DataFrame:
    """Round every share to SHARE_DECIMALS places without breaking its sum.

    In each group whose unrounded shares add to 1, the shares are rounded by the largest
    remainder method: every share is first rounded down to the 0.001 grid, and the
    thousandths still missing go one each to the shares that lost the most.  So the
    group adds to exactly 1, and no share moves by a full 0.001.  A share under 0.0005
    can come out 0.  Groups that did not add to 1 to begin with (a share left blank
    below the threshold, say) are simply rounded.
    """
    out = out.copy()
    unit = 10 ** SHARE_DECIMALS
    for column, keys in SHARE_GROUPS.items():
        if column not in out:
            continue
        exact = pd.to_numeric(out[column], errors="coerce")
        rounded = exact.round(SHARE_DECIMALS)
        group = pd.Series(list(zip(*[_key(out[k]) for k in keys])),
                          index=out.index)
        has = exact.notna()
        total = exact[has].groupby(group[has]).transform("sum")
        rows = total.index[((total - 1).abs() < 1e-6).to_numpy()]
        if len(rows):
            scaled = exact[rows] * unit
            floor = np.floor(scaled + 1e-9)
            remainder = scaled - floor
            missing = (unit - floor.groupby(group[rows]).transform("sum")).round().astype(int)
            # rank each share's remainder within its group, largest first
            order = remainder.groupby(group[rows]).rank(method="first", ascending=False)
            floor = floor + (order <= missing).astype(float)
            rounded[rows] = floor / unit
        out[column] = rounded.round(SHARE_DECIMALS)
    return out


# Output names.  Every share column is named for what it is a share OF -- its
# denominator -- so `share_of_fuel` is "this row's share of its fuel".  The code works
# with the older internal names and renames on the way out.
OUTPUT_NAMES = {
    "end_use_by_type":      "share_of_type",     # this end use's share of its energy type
    "type_by_end_use":      "share_of_end_use",  # this type's share of the end use (footprint)
    "end_use_by_fuel":      "share_of_end_use",  # this fuel's share of the end use (Table 5.4)
    "fuel_by_end_use":      "share_of_fuel",     # this end use's share of its fuel
    "heat_by_fuel":         "share_of_heat",     # this fuel's share of boilers + cogeneration
    "boiler_cogen_share":   "share_of_steam",    # this source's share of onsite steam
    "fuel_by_end_use_note": "note",
}
OUTPUT_ORDER = [
    "mecs_year", "sector", "name", "flow", "type", "end_use_1", "end_use_2", "end_use_3",
    "end_use", "fuel_type", "value", "value_table", "unit",
    "share_of_type", "share_of_end_use", "share_of_fuel", "share_of_heat", "share_of_steam",
    "efficiency", "heat_to_power_ratio", "note", "data_source",
]


def to_output_names(out: pd.DataFrame) -> pd.DataFrame:
    """Rename to the output column names and order.

    type_by_end_use (footprint rows) and end_use_by_fuel (Table 5.4 and residual rows) are
    the same idea -- this row's share of what feeds its end use -- on rows that never
    overlap, so they become one column, share_of_end_use.  Its groups differ by
    data_source: fuel / electricity / steam on footprint rows, individual fuels on the
    others.
    """
    out = out.copy()
    out["type_by_end_use"] = out["type_by_end_use"].combine_first(out["end_use_by_fuel"])
    out = out.drop(columns="end_use_by_fuel").rename(columns=OUTPUT_NAMES)
    extra = [c for c in out.columns if c not in OUTPUT_ORDER]      # e.g. source_file
    return out[OUTPUT_ORDER + extra]


HEAT_END_USES = ("onsite generation_boilers", "onsite generation_cogeneration")


def add_fuel_mix(out: pd.DataFrame) -> pd.DataFrame:
    """Add end_use_by_fuel and heat_by_fuel to the fuel x end-use rows.

    Both read across fuels, where fuel_by_end_use reads across end uses:

    end_use_by_fuel  this fuel's share of everything feeding this end use in this sector.
    heat_by_fuel     this fuel's share of the fuel feeding boilers and cogeneration
                     together (onsite steam and CHP); the same figure on both rows.

    The pool is the Table 5.4 rows (table_5_4_est, or table_5_4 with --no-estimates) plus,
    in footprint years, the residual rows -- so coke, biomass, black liquor and the other
    fuels Table 5.4 cannot see are counted.  2002 and 2022 have no residual rows, so their
    shares cover the six Table 5.4 sources only.  Electricity is one of those sources and
    is included.  A group with any value missing, or no energy at all, is left blank.
    """
    out = out.copy()
    for c in ("end_use_by_fuel", "heat_by_fuel"):
        out[c] = np.nan
    pool = (out[SOURCE_TAG].isin([ESTIMATED_TAG, PUBLISHED_TAG, RESIDUAL_TAG])
            & out.fuel_type.notna() & out.flow.eq("input"))
    rows = out[pool]
    value = pd.to_numeric(rows.value, errors="coerce")
    keys = [rows.mecs_year, rows.sector.astype(str), rows.end_use]

    def share(numerator, group_keys):
        total = value.groupby(group_keys).transform("sum")
        missing = value.isna().groupby(group_keys).transform("any")
        return (numerator / total).where((total > 0) & ~missing)

    out.loc[rows.index, "end_use_by_fuel"] = share(value, keys)

    heat = rows.end_use.isin(HEAT_END_USES)
    h = rows[heat]
    hv = value[heat]
    by_fuel = hv.groupby([h.mecs_year, h.sector.astype(str), h.fuel_type]).transform("sum")
    by_fuel_missing = hv.isna().groupby([h.mecs_year, h.sector.astype(str),
                                         h.fuel_type]).transform("any")
    total = hv.groupby([h.mecs_year, h.sector.astype(str)]).transform("sum")
    missing = hv.isna().groupby([h.mecs_year, h.sector.astype(str)]).transform("any")
    # each fuel's boilers + cogeneration over all fuels' boilers + cogeneration: the same
    # figure on both of a fuel's rows, adding to 1 down either end use's rows
    out.loc[h.index, "heat_by_fuel"] = (by_fuel / total).where(
        (total > 0) & ~missing & ~by_fuel_missing)
    return out


# --------------------------------------------------------------------------------------
# metadata file
# --------------------------------------------------------------------------------------

METADATA_COLUMNS = [
    ("mecs_year", "all", "", "MECS survey year (2002-2022).  Footprint rows exist for 2006, "
     "2010, 2014 and 2018; Table 5.4 and residual rows for all six surveys."),
    ("sector", "all", "", "Footprint sector code, built from NAICS codes "
     "(e.g. 311_312 = food and beverage; 31_33 or 31-33 = all manufacturing).  Table 5.4 "
     "rows for a sector sum the NAICS blocks listed in TABLE54_SECTOR_PARTS."),
    ("name", "all", "", "Sector name as used in the footprint files."),
    ("flow", "all", "", "Kind of energy flow: import (purchased offsite), input (delivered "
     "to an end use), input_combined (delivered to a machine-drive component, pre-blended "
     "across types), output (produced onsite), loss (entered an end use but did no useful "
     "work), export (sold offsite), share (footprint fuel-mix percentage, not a flow).  "
     "Table 5.4 and residual rows are all `input`."),
    ("type", "all", "", "Energy type: fuel, electricity or steam.  Table 5.4 and residual "
     "rows are `fuel`, including the electricity rows of Table 5.4 (fuel_type says which)."),
    ("end_use_1", "all but import/export/share", "", "End-use group: onsite generation, "
     "process, nonprocess."),
    ("end_use_2", "all but import/export/share", "", "End use within the group, e.g. "
     "boilers, cogeneration, heating, machine drive, hvac."),
    ("end_use_3", "footprint machine-drive rows", "", "Machine-drive component (pumps, fans, "
     "compressed air, ...)."),
    ("end_use", "all but import/export/share", "", "end_use_1, end_use_2 and end_use_3 "
     "joined with underscores, e.g. `process_heating`."),
    ("fuel_type", "share, table_5_4_est, residual", "", "Fuel.  On Table 5.4 rows one of "
     "electricity, fuel oil (residual + distillate), natural gas, ngl/hgl (named as in that "
     "year's footprint; 2002 follows 2006, 2022 follows 2018), coal.  On residual rows, in "
     "every year: coke (3.2 coke and breeze less 2/3 of 3.5 blast furnace / coke oven gas, "
     "the DOE / EIA double-count adjustment), coke oven gas (3.5 blast furnace / coke oven "
     "gases), refinery fuel gas (3.5 waste gas in refining), byproduct fuel (3.5 waste gas "
     "elsewhere, waste oils and materials), petroleum coke, black liquor (3.5 pulping "
     "liquor), biomass (3.5 wood chips and bark), hydrogen (3.2, 2022 only) and other "
     "(footprint years: the footprint's fuel total less every fuel above and the Table 5.4 "
     "fuels; 2002 and 2022: MECS other scaled by the nearest footprint year's ratio).  On "
     "footprint share rows, the footprint's own names."),
    ("value", "all", "PJ (share rows: fraction)", "The energy, converted from the "
     "sources' TBtu (x 1.055056).  Footprint rows: the footprint figure.  table_5_4_est "
     "rows: Table 5.4 with withheld and `*` cells estimated, rounding reconciled and End "
     "Use Not Reported spread pro rata -- `note` shows each step from value_table.  "
     "Residual rows: the total of a fuel Table 5.4 does not cover (measured in Tables 3.2 / "
     "3.5, coke net of blast furnace gas, 'other' on the footprint's basis), times "
     "share_of_fuel.  Rounded to 3 significant figures, but never past the "
     "units place."),
    ("value_table", "table_5_4_est", "PJ", "What Table 5.4 prints for this sector, end "
     "use and fuel: the sum of the printed numbers over the sector's NAICS blocks (and over "
     "residual + distillate for fuel oil), `*` and `--` counting as 0.  Empty when any cell "
     "behind it is withheld, or nothing is printed but `*`.  Empty on other rows."),
    ("unit", "all", "", "PJ for every flow; `fraction` on footprint `share` rows (the "
     "source files label them %, but they hold fractions)."),
    ("share_of_type", "footprint", "fraction", "This end use's share of its energy type, "
     "within one sector and flow: of all the fuel (or electricity, or steam) put into end "
     "uses, the part going here.  Adds to 1 over end uses.  (Formerly end_use_by_type.)"),
    ("share_of_end_use", "footprint, table_5_4_est, residual", "fraction", "This row's "
     "share of what feeds its end use, within one sector.  Footprint rows: the split "
     "between fuel, electricity and steam (on import rows, of purchased energy).  "
     "table_5_4_est and residual rows: the split between individual fuels -- the end "
     "use's fuel mix -- pooling the Table 5.4 sources (electricity included) with the "
     "fuels Table 5.4 does not cover.  The two kinds of row form separate groups, each "
     "adding to 1; filter on data_source before summing.  Blank if the end use has no "
     "energy or a value is missing.  (Formerly type_by_end_use and end_use_by_fuel.)"),
    ("share_of_fuel", "table_5_4_est, residual", "fraction", "This end use's share of its "
     "fuel, within one sector: where the fuel goes (e.g. the part of chemicals' NGL used "
     "for onsite transportation).  Adds to 1 over end uses.  Residual rows: the inferred "
     "end-use profile shared by every non-Table-5.4 fuel.  (Formerly fuel_by_end_use.)"),
    ("share_of_heat", "table_5_4_est and residual rows for boilers and cogeneration",
     "fraction", "This fuel's share of the energy feeding boilers and cogeneration "
     "combined (onsite steam and CHP), within one sector; the same number on the boiler "
     "and the cogeneration row.  Pooled like share_of_end_use.  Adds to 1 over fuels.  "
     "(Formerly heat_by_fuel.)"),
    ("share_of_steam", "footprint steam output rows >= threshold", "fraction", "This "
     "source's share of the sector's onsite steam (boilers vs cogeneration).  "
     "(Formerly boiler_cogen_share.)"),
    ("efficiency", "footprint loss rows >= threshold", "fraction", "1 - loss / energy "
     "delivered to the end use (steam distribution: / steam supply).  Blank below the "
     "threshold (default 10 TBtu, about 10.6 PJ).  2006 onsite-generation values are "
     "unusable (see the script docstring).  (Formerly misspelt efficency.)"),
    ("heat_to_power_ratio", "footprint cogeneration steam output >= threshold", "ratio",
     "Steam per unit of electricity from cogeneration (energy over energy)."),
    ("note", "table_5_4_est, residual", "PJ", "table_5_4_est: the steps from value_table "
     "to value, in PJ, e.g. `table: 1.06; +0.04 rounding balance; +0.2 End Use Not "
     "Reported (pro rata); = 1.3` (blank when value = value_table).  Residual rows: the "
     "fuel's measured total and how any gap in it was filled, and which footprint year "
     "its end-use split comes from, with a warning where that split is approximate.  "
     "(Formerly fuel_by_end_use_note.)"),
    ("data_source", "all", "", "footprint (DOE energy-footprint CSV), table_5_4_est (MECS "
     "Table 5.4, gap-filled), residual (fuels Table 5.4 does not cover: named fuels "
     "measured in MECS Tables 3.2 / 3.5, 'other' balancing to the footprint's fuel total, "
     "split across end uses by footprint minus Table 5.4); "
     "table_5_4 (printed table as is) only with --no-estimates."),
]

METADATA_STEPS = [
    ("table: N", "the printed figure (value_table), in PJ.  All step amounts are PJ."),
    ("table: withheld", "a cell behind this row is withheld (Q, W, D); `(other cells print "
     "N)` gives the printed part."),
    ("table: <0.53 (*)", "only `*` (under 0.5 TBtu, 0.53 PJ) is printed."),
    ("withheld cell(s) estimated (method)", "the first estimate of withheld cells: "
     "table_3_2 (printed in, or pinned by, Table 3.2), identity (the only unknown in a "
     "printed sum), group_prior / group_equal (a sum's "
     "remainder shared by the nearest survey's pattern, or equally), adjacent_year (the "
     "nearest survey's value)."),
    ("for * cells", "each `*` cell gets an equal slice, at most 0.5, of what its printed "
     "parent leaves unallocated."),
    ("toward neighbouring surveys", "withheld cells pulled toward the nearest other "
     "survey's value as far as the printed numbers allow (weighted least squares)."),
    ("rounding balance", "printed and `*` cells moved within their rounding range "
     "(+-0.5, or 0-0.5 for `*`) so end uses add to subtotals and subtotals to the total."),
    ("End Use Not Reported (pro rata)", "the sector's unreported energy spread over the "
     "reported end uses in proportion to their size."),
    ("= N", "the result, equal to value."),
    ("total N PJ from SOURCE (gaps estimated: ...); end-use split: ...",
     "residual rows: the fuel's total and its basis -- MECS Table 3.2 / 3.5 (any withheld "
     "or `*` part filled as for Table 5.4), coke net of blast furnace gas, or for 'other' "
     "the footprint balance or the scaled MECS figure -- and the footprint year whose "
     "footprint-minus-Table-5.4 residual gives its end-use split (its own, or for 2002, "
     "2022 and empty residuals the nearest with one)."),
]


def write_metadata(csv_path: str) -> str:
    """Write a Markdown data dictionary beside the output CSV; return its path."""
    path = os.path.splitext(csv_path)[0] + "_metadata.md"
    name = os.path.basename(csv_path)
    lines = [
        f"# {name} -- column guide",
        "",
        f"Written by `mecs_footprint_metrics.py` alongside `{name}`; regenerated on "
        "every run.  The script's docstring has the full method.",
        "",
        "Each row is one energy flow for one MECS sector and survey year, in PJ.  "
        "`data_source` says where it comes from.  Footprint rows are DOE's diagrams; "
        "table_5_4_est and residual rows together give the same sector fuel total "
        "(within a few TBtu in 2006-2018) split by individual fuel and end use.  They "
        "describe the same energy, so never add the two together:",
        "",
        "* **footprint** -- the DOE/EIA MECS energy-footprint CSVs (2006-2018), with the "
        "derived share and efficiency columns.",
        "* **table_5_4_est** -- MECS Table 5.4, *End Uses of Fuel Consumption* "
        "(2002-2022), for its six energy sources: electricity, residual and "
        "distillate fuel oil (combined here as fuel oil), natural gas, NGL/HGL, coal.  Withheld and `*` cells "
        "are estimated so that shares add to 1; withheld totals come from Table 3.2 where "
        "it has them.",
        "* **residual** -- the fuels Table 5.4 does not cover (coke, biomass, byproduct "
        "fuel, ...).  Named fuels are measured in MECS Table 3.2 (*Fuel Consumption*) and "
        "Table 3.5 (*Selected Byproducts in Fuel Consumption*) for every year, with coke "
        "net of blast furnace gas as DOE does; 'other' is set so the sector's fuel matches "
        "the footprint (DOE reworks MECS 'Other Fuels' without a published rule).  The "
        "split across end uses is inferred from footprint minus Table 5.4 (2002 and 2022: "
        "the nearest footprint year's split, and 'other' scaled by its ratio).",
        "",
        "Every share column is named for what it is a share **of**: `share_of_fuel` is "
        "this row's share of its fuel, `share_of_end_use` its share of what feeds its end "
        "use, and so on.",
        "",
        "Share columns are rounded to "
        f"{SHARE_DECIMALS} decimal places so that each group adds to exactly 1 "
        "(largest-remainder rounding); `value` to "
        f"{VALUE_SIG_FIGS} significant figures, never past the units place.  Shares are "
        "computed before rounding.",
        "",
        "## Columns",
        "",
        "| column | rows | unit | meaning |",
        "|---|---|---|---|",
    ]
    order = {c: i for i, c in enumerate(OUTPUT_ORDER)}
    for column, rows, unit, meaning in sorted(METADATA_COLUMNS,
                                              key=lambda m: order.get(m[0], 99)):
        lines.append(f"| `{column}` | {rows} | {unit} | {meaning} |")
    lines += ["", "## What `note` says", "",
              "| step | meaning |", "|---|---|"]
    for step, meaning in METADATA_STEPS:
        lines.append(f"| `{step}` | {meaning} |")
    lines += ["", "## Reading the share columns on Table 5.4 and residual rows", "",
              "* `share_of_fuel` -- down the end uses, for one fuel: where does this "
              "fuel go?",
              "* `share_of_end_use` -- across the fuels, for one end use: what feeds this "
              "end use?",
              "* `share_of_heat` -- across the fuels, for boilers + cogeneration together: "
              "what raises this sector's steam?", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def _key(series: pd.Series) -> pd.Series:
    """Normalise a column into a grouping key.

    Missing values become the empty string rather than NaN, so that rows sharing an
    *absent* attribute group together instead of each landing in its own NaN bucket.
    This is what pools the import rows (which have no end use) into a single group.
    """
    return series.fillna("").astype(str).str.strip()


def _ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """numerator / denominator, yielding 0 where the denominator is 0.

    A zero denominator means the whole group is zero — the sector reports no energy of
    that kind at all — so a 0 share is the honest answer and avoids propagating NaN.
    """
    out = np.where(denominator != 0, numerator / denominator.replace(0, np.nan), 0.0)
    return pd.Series(out, index=numerator.index).fillna(0.0)


def build_end_use(df: pd.DataFrame) -> pd.Series:
    """Rebuild the composite end-use key from its three parts.

    Joins the non-blank parts of end_use_1 / end_use_2 / end_use_3 with underscores, so
    ("process", "machine drive", "pumps") becomes "process_machine drive_pumps" and
    ("process", "heating", "") becomes "process_heating".  Recomputed here rather than
    trusting the file's own `end_use` column, so the grouping key cannot drift from the
    three columns that define it.
    """
    parts = [_key(df[c]) for c in ("end_use_1", "end_use_2", "end_use_3")]
    joined = parts[0].copy()
    for p in parts[1:]:
        both = (joined != "") & (p != "")
        joined = np.where(both, joined + "_" + p, np.where(joined != "", joined, p))
        joined = pd.Series(joined, index=df.index)
    return joined


# --------------------------------------------------------------------------------------
# the five derived columns
# --------------------------------------------------------------------------------------


def add_metrics(df: pd.DataFrame, threshold: float = DEFAULT_THRESHOLD) -> pd.DataFrame:
    df = df.copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Grouping keys.  Every total below is computed within one sector of one survey year;
    # `grp` is that pairing, joined on a character that cannot occur in the data.
    g_year, g_sector = _key(df["mecs_year"]), _key(df["sector"])
    flow, typ = _key(df["flow"]), _key(df["type"])
    end_use = build_end_use(df)
    eu2 = _key(df["end_use_2"])
    grp = g_year + "\x00" + g_sector

    v = df["value"]

    def total_over(*keys, subset: pd.Series | None = None) -> pd.Series:
        """Group `value` by `keys` and broadcast each group's total back to every row.

        `subset` restricts which rows CONTRIBUTE to the totals without removing any rows
        from the result: a row outside the subset still receives its group's total, which
        is what lets a loss row read the input total for its own end use.
        """
        k = keys[0].astype(str)
        for extra in keys[1:]:
            k = k + "\x00" + extra.astype(str)
        contrib = v.where(subset, 0.0) if subset is not None else v
        return k.map(contrib.groupby(k).sum()).astype(float)

    # -- end_use_by_type: this end use's slice of its (flow, energy type) ---------------
    df["end_use_by_type"] = _ratio(v, total_over(grp, flow, typ))

    # -- type_by_end_use: this energy type's slice of its (flow, end use) ---------------
    df["type_by_end_use"] = _ratio(v, total_over(grp, flow, end_use))

    # -- efficiency: useful fraction of everything delivered to a loss row's end use -----
    # Denominator: every flow INTO this end use.  Plain `input` covers the end-use boxes;
    # `input_combined` covers the machine-drive components, whose energy is only ever
    # reported pre-blended.  Matching on the "input" prefix picks up both.
    is_input = flow.str.startswith("input")
    input_to_end_use = total_over(grp, end_use, subset=is_input)

    # Steam distribution is the exception: nothing is "input" to it, because what is being
    # distributed is the sector's steam supply — raised onsite plus purchased.
    steam_supply = (
        total_over(grp, subset=(flow == "output") & (typ == "steam"))
        + total_over(grp, subset=(flow == "import") & (typ == "steam"))
    )

    is_loss = (flow == "loss") & (v >= threshold)
    eff = pd.Series(np.nan, index=df.index, dtype=float)
    primary = is_loss & (input_to_end_use != 0)
    eff[primary] = 1 - v[primary] / input_to_end_use[primary]
    fallback = is_loss & (input_to_end_use == 0) & (eu2 == "steam distribution") & (steam_supply != 0)
    eff[fallback] = 1 - v[fallback] / steam_supply[fallback]
    df["efficiency"] = eff

    # -- boiler_cogen_share: this source's slice of the sector's onsite steam -----------
    steam_out_total = total_over(grp, subset=(flow == "output") & (typ == "steam"))
    is_steam_out = (flow == "output") & (typ == "steam") & (v >= threshold)
    share = pd.Series(np.nan, index=df.index, dtype=float)
    ok = is_steam_out & (steam_out_total != 0)
    share[ok] = v[ok] / steam_out_total[ok]
    df["boiler_cogen_share"] = share

    # -- heat_to_power_ratio: cogenerated steam per unit of cogenerated electricity -----
    # `cogen_out_total` is steam + electricity out of cogeneration, so r is steam's share
    # of the pair and r / (1 - r) is steam / electricity.
    cogen_out_total = total_over(grp, subset=(flow == "output") & (eu2 == "cogeneration"))
    is_cogen_steam = (flow == "output") & (eu2 == "cogeneration") & (typ == "steam") & (v >= threshold)
    htp = pd.Series(np.nan, index=df.index, dtype=float)
    ok = is_cogen_steam & (cogen_out_total != 0)
    r = pd.Series(np.nan, index=df.index, dtype=float)
    r[ok] = v[ok] / cogen_out_total[ok]
    # r == 1 means the cogeneration unit reports no electricity output, so there is
    # nothing to take a ratio against; leave the row blank rather than divide by zero.
    ok = ok & (r != 1)
    htp[ok] = r[ok] / (1 - r[ok])
    df["heat_to_power_ratio"] = htp

    return df


# --------------------------------------------------------------------------------------
# fuel_by_end_use: how each fuel splits across end uses, from MECS Table 5.4
# --------------------------------------------------------------------------------------
#
# The footprint files report energy by end use and by broad type (fuel / electricity /
# steam), and separately report a sector's fuel MIX, but never the two together -- you
# cannot tell from them what share of a sector's natural gas went to process heating.
# MECS Table 5.4 ("End Uses of Fuel Consumption") does report that crossing, so the rows
# added here fill the gap.
#
# Table 5.4 covers six energy sources only: net demand for electricity, residual fuel oil,
# distillate fuel oil and diesel, natural gas, HGL (LPG and NGL in the earlier surveys),
# and coal.  Byproduct fuels, coke and "other" are outside it, so these shares describe
# the purchased-fuel side of a sector and will not reproduce the footprint fuel mix.
#
# Its rows are a two-level hierarchy (subtotals followed by their components).  Only the
# leaves are emitted; the subtotal rows would double-count, but they are read, because
# the sums they state are what the gap-filling in estimate_table54 solves against.

TABLE54_FILE_GLOB = "eia_[0-9][0-9][0-9][0-9]_mecs-[0-9][0-9][0-9][0-9]-table-5-4.xls*"
TABLE54_SHEET = "Table 5.4"

# Table 5.4 end use -> the footprint's (end_use_1, end_use_2)
TABLE54_END_USES = {
    "Conventional Boiler Use":            ("onsite generation", "boilers"),
    "CHP and/or Cogeneration Process":    ("onsite generation", "cogeneration"),
    "Conventional Electricity Generation": ("onsite generation", "other"),
    "Process Heating":                    ("process", "heating"),
    "Process Cooling and Refrigeration":  ("process", "cooling"),
    "Machine Drive":                      ("process", "machine drive"),
    "Electro-Chemical Processes":         ("process", "electro-chemical"),
    "Other Process Use":                  ("process", "other"),
    "Facility HVAC":                      ("nonprocess", "hvac"),
    "Facility Lighting":                  ("nonprocess", "lighting"),
    "Other Facility Support":             ("nonprocess", "facility support"),
    "Onsite Transportation":              ("nonprocess", "onsite transportation"),
    "Other Nonprocess Use":               ("nonprocess", "other"),
}
# Spread pro rata over the reported end uses (see allocate_unreported) rather than dropped,
# so the shares still cover the sector's whole reported consumption.  Process heating is
# where it goes when there is nothing to pro-rate over, or with --unreported process-heating.
TABLE54_UNREPORTED = "End Use Not Reported"
TABLE54_UNREPORTED_GOES_TO = "Process Heating"
UNREPORTED_MODES = ("prorata", "process-heating")
TABLE54_TOTAL = "TOTAL FUEL CONSUMPTION"
# subtotal rows -- read for reconciliation and estimation, never emitted
TABLE54_SUBTOTALS = ["Indirect Uses-Boiler Fuel", "Direct Uses-Total Process",
                     "Direct Uses-Total Nonprocess"]

# The sums every fuel column obeys inside one NAICS block (up to rounding).  Note that
# Conventional Electricity Generation is printed under the NONPROCESS subtotal even though
# it is emitted as onsite generation.
TABLE54_HIERARCHY = {
    TABLE54_TOTAL: TABLE54_SUBTOTALS + [TABLE54_UNREPORTED],
    "Indirect Uses-Boiler Fuel": ["Conventional Boiler Use",
                                  "CHP and/or Cogeneration Process"],
    "Direct Uses-Total Process": ["Process Heating", "Process Cooling and Refrigeration",
                                  "Machine Drive", "Electro-Chemical Processes",
                                  "Other Process Use"],
    "Direct Uses-Total Nonprocess": ["Facility HVAC", "Facility Lighting",
                                     "Other Facility Support", "Onsite Transportation",
                                     "Conventional Electricity Generation",
                                     "Other Nonprocess Use"],
}
# The sums across NAICS blocks.  Only families whose children are EXHAUSTIVE belong here
# (the listed 6-digit industries under 325, say, are a sample of it, not a partition).
# None means "every 3-digit block in the table"; otherwise the first alternative whose
# codes are all present is used (the iron and steel codes were renumbered in 2014).
TABLE54_FAMILIES = [
    ("311-339", None),
    ("312", [("3121", "3122")]),
    ("331", [("331110", "3312", "3313", "3314", "3315"),
             ("331111", "331112", "3312", "3313", "3314", "3315")]),
]
# label variants that do not survive normalisation
TABLE54_LABEL_ALIASES = {
    "other boiler fuel use": "conventional boiler use",   # 2002, NAICS 334413 only
}

# the six source columns, in sheet order, and the footprint fuel_type they map to.
# Residual and distillate both land on `fuel oil`; the HGL column is `ngl` in the 2006-2014
# footprints and `hgl` in 2018, so it is resolved per year against the file's own vocabulary.
TABLE54_FUEL_COLUMNS = ["electricity", "residual fuel oil", "distillate fuel oil",
                        "natural gas", "hgl", "coal"]
TABLE54_FUEL_MAP = {
    "electricity": "electricity",
    "residual fuel oil": "fuel oil",
    "distillate fuel oil": "fuel oil",
    "natural gas": "natural gas",
    "hgl": "hgl",              # remapped to `ngl` for surveys that use that name
    "coal": "coal",
}

# Footprint sector code -> the Table 5.4 NAICS blocks that make it up.  Each part is a
# code, or a tuple of alternatives tried in order; an alternative may itself be a tuple
# of codes that must all be present.  So ("331110", "331111") is "whichever of these the
# survey uses" (iron and steel mills were renumbered between 2010 and 2014), and
# (("336111", "336112"), "336110") is "the two auto codes, or the merged 2022 code".
# Sectors Table 5.4 breaks out but the footprints do not are simply never requested.
TABLE54_SECTOR_PARTS = {
    "31_33":           ["311-339"],
    "31-33":           ["311-339"],
    "311_312":         ["311", "312"],
    "313_316":         ["313", "314", "315", "316"],
    "313_314_315_316": ["313", "314", "315", "316"],
    "321_322":         ["321", "322"],
    "32411":           ["324110"],
    "325":             ["325"],
    "32511":           ["325110"],
    "325211":          ["325211"],
    "326":             ["326"],
    # 2002 publishes glass (3272) as one block instead of its four 6-digit industries
    "3272_327993":     [(("327211", "327212", "327213", "327215"), "3272"), "327993"],
    "32731":           ["327310"],
    "33111_3312":      [("331110", "331111"), "3312"],
    "3313":            ["3313"],
    "3315":            ["3315"],
    "332":             ["332"],
    "333":             ["333"],
    "334_335":         ["334", "335"],
    "334413":          ["334413"],
    "336":             ["336"],
    "33611":           [(("336111", "336112"), "336110")],
    "3364":            ["3364"],
}

# Fuels the footprint reports that Table 5.4 has no column for.  Their end-use split is
# estimated rather than measured -- see residual_fuel_rows.
RESIDUAL_TAG = "residual"

# Table 5.4 with its withheld and `*` cells estimated -- see estimate_table54.
PUBLISHED_TAG = "table_5_4"
ESTIMATED_TAG = "table_5_4_est"
# `*` is "less than 0.5 TBtu".  The midpoint stands in for one while solving for withheld
# cells; the ceiling caps what one can be given when a residual is shared out.
STAR_MIDPOINT = 0.25
STAR_CEILING = 0.5

# EIA cell codes.  `--` is "not applicable" and `*` is "less than 0.5"; both are read as
# zero on the published rows.  The rest mean the value was withheld (Q, W, D, C), is not
# available (NA), was negative (S, 2002) or has no factor (NF, 2002 RSE rows only), and
# are read as unknown so that a share built on them comes out blank rather than wrong.
TABLE54_ZERO_CODES = {"--", "*", "", "nan", "0"}
TABLE54_WITHHELD_CODES = {"Q", "W", "D", "C", "NF", "NM", "NA", "S"}


def _t54_cell(raw):
    """Return (value, withheld, status).

    status is "num", "zero" (`--` or 0), "star" (`*`, value 0 on the published rows) or
    "withheld" (value nan).
    """
    s = str(raw).strip()
    if s == "*":
        return 0.0, False, "star"
    if s in TABLE54_ZERO_CODES:
        return 0.0, False, "zero"
    if s.upper() in TABLE54_WITHHELD_CODES:
        return float("nan"), True, "withheld"
    try:
        return float(s.replace(",", "")), False, "num"
    except ValueError:
        return float("nan"), True, "withheld"


def read_table54(path: str) -> pd.DataFrame:
    """Parse one Table 5.4 workbook into tidy (naics, end_use, fuel) rows.

    The sheet is a report, not a table: a NAICS code in the first column opens a block and
    the end-use rows beneath it carry no code of their own.  The header row is located by
    looking for "End Use" rather than assumed, since its position moved between surveys.
    """
    sheet = pd.read_excel(path, sheet_name=TABLE54_SHEET, header=None)
    header = next((i for i in range(30)
                   if str(sheet.iloc[i, 1]).strip().lower() == "end use"), None)
    if header is None:
        sys.exit(f"{path}: could not find the 'End Use' header row")

    wanted = {_t54_norm(k): k for k in
              list(TABLE54_END_USES) + [TABLE54_UNREPORTED, TABLE54_TOTAL] + TABLE54_SUBTOTALS}
    out, naics = [], None
    for i in range(header + 1, len(sheet)):
        code = sheet.iloc[i, 0]
        if pd.notna(code) and re.match(r"^\s*[0-9]", str(code)):
            naics = re.sub(r"\s+", "", str(code))
            continue
        key = wanted.get(_t54_norm(sheet.iloc[i, 1]))
        if key is None or naics is None:
            continue
        for j, fuel in enumerate(TABLE54_FUEL_COLUMNS):
            value, withheld, status = _t54_cell(sheet.iloc[i, 2 + j])
            out.append(dict(naics=naics, table_end_use=key, table_fuel=fuel,
                            value=value, withheld=withheld, status=status, method=""))
    return pd.DataFrame(out)


def _t54_norm(s) -> str:
    """Normalise an end-use label for matching.

    Drops footnote markers -- "(f)" before 2022, a bare trailing letter ("HVACf") from
    2022 -- folds the 2022 em dashes to hyphens, and folds case and whitespace.
    """
    s = str(s).replace("—", "-").replace("–", "-")
    s = re.sub(r"\s+", " ", re.sub(r"\(\w\)", "", s)).strip().lower()
    s = re.sub(r"\bhvac[a-z]$", "hvac", s)
    return TABLE54_LABEL_ALIASES.get(s, s)


# --------------------------------------------------------------------------------------
# filling Table 5.4's withheld and `*` cells (data_source=table_5_4_est)
# --------------------------------------------------------------------------------------
#
# Every column of Table 5.4 is internally additive: within a NAICS block the end uses sum
# to their subtotal and the subtotals plus "not reported" sum to the total, and across
# blocks the 3-digit industries sum to all manufacturing (and 3121 + 3122 to 312, the
# 3311-3315 codes to 331).  A withheld cell is therefore often pinned down by the cells
# around it.  The estimate is built in passes, each tagged in the row's note:
#
#   identity       the only unknown in one of those sums: the published parent minus the
#                  published children (or the reverse).  Iterated, since each solved cell
#                  can unlock another.  Hiding 5% of published cells and re-deriving them
#                  this way misses by a median 0.5 TBtu, 90% within 1 TBtu.
#   group_prior    two or more unknowns share one sum with a known parent: the residual is
#                  split between them in proportion to the same cells in the nearest other
#                  survey (group_equal if no survey has them).  Totals stay exact.
#   adjacent_year  no sum constrains the cell: the same cell from the nearest other survey,
#                  taken one cell at a time so the identities can propagate from it.
#   star_residual  a `*` cell: what its parent leaves after the published children, split
#                  equally between the `*` siblings and capped at 0.5 each.  Worked from
#                  the total down, so a `*` subtotal is filled before its own children.
#   star_midpoint  a `*` total, which has no parent to work from: what its published
#                  children add to, kept within 0.25-0.5.
#
# Sums inside one industry are used before the cross-industry ones, whose 21 rounded terms
# can be several TBtu out, and every estimate is clamped to what its own industry's
# subtotals allow (_t54_bounded).
#
# Stars stand in at the 0.25 midpoint while withheld cells are being solved, and are
# filled last, once every withheld number they sit beside is known.  Estimates are
# floored at zero.  Every survey found under the tables folder (2002 and 2022 included,
# which have no footprint) is read, both to be emitted and to serve as the "nearest other
# survey" for its neighbours.


def _t54_known(cells: dict, est: dict, key):
    """Current best value for a cell, or None while it is still unknown."""
    status, value = cells[key]
    if key in est:
        return est[key][0]
    if status == "withheld":
        return None
    if status == "star":
        return STAR_MIDPOINT
    return value


def _t54_equations(cells: dict) -> tuple[list, list]:
    """The sums the table obeys, as (parent key, [child keys]).

    Returns (within-block sums, all sums).  Sums naming a cell the sheet does not print
    are dropped rather than guessed at.
    """
    naics = sorted({k[0] for k in cells})
    block, family = [], []
    for n in naics:
        for f in TABLE54_FUEL_COLUMNS:
            for parent, children in TABLE54_HIERARCHY.items():
                block.append(((n, parent, f), [(n, c, f) for c in children]))
    labels = list(dict.fromkeys(list(TABLE54_HIERARCHY)
                                + [c for cs in TABLE54_HIERARCHY.values() for c in cs]))
    present = set(naics)
    for parent, alternatives in TABLE54_FAMILIES:
        if parent not in present:
            continue
        if alternatives is None:
            kids = [n for n in naics if re.fullmatch(r"3\d\d", n)]
        else:
            kids = next((list(a) for a in alternatives if all(c in present for c in a)), None)
            if not kids:
                continue
        for label in labels:
            for f in TABLE54_FUEL_COLUMNS:
                family.append(((parent, label, f), [(c, label, f) for c in kids]))

    def complete(eqs):
        return [(p, ch) for p, ch in eqs if p in cells and all(c in cells for c in ch)]
    block = complete(block)
    return block, block + complete(family)


def _t54_block_index(block_eqs) -> dict:
    """cell -> the within-block sums it appears in, for _t54_bounded."""
    index = {}
    for parent, children in block_eqs:
        for k in [parent] + children:
            index.setdefault(k, []).append((parent, children))
    return index


def _t54_bounded(cells, est, index, key, x) -> float:
    """Clamp an estimate to what its own NAICS block allows.

    A cell can be no larger than any known parent less its known siblings, and no smaller
    than its own known children, each with one rounding unit (0.5) of slack.  This matters
    for cells solved from the 21-industry all-manufacturing sum, where the rounding of the
    other twenty can add up to several TBtu -- more than a small cell is worth.
    """
    lo, hi = 0.0, float("inf")
    for parent, children in index.get(key, []):
        if parent == key:
            kids = [_t54_known(cells, est, c) for c in children]
            lo = max(lo, sum(v for c, v in zip(children, kids)
                             if v is not None and cells[c][0] != "star") - 0.5)
            continue
        p = _t54_known(cells, est, parent)
        if p is None:
            continue
        others = [_t54_known(cells, est, c) for c in children if c != key]
        hi = min(hi, p - sum(v for v in others if v is not None) + 0.5)
    return min(max(x, lo), max(hi, 0.0))


def _t54_identity_pass(cells, est, eqs, index) -> bool:
    """Solve every sum with exactly one unknown, repeatedly; True if anything was solved."""
    changed, solved = True, False
    while changed:
        changed = False
        for parent, children in eqs:
            unknown = [k for k in [parent] + children if _t54_known(cells, est, k) is None]
            if len(unknown) != 1:
                continue
            u = unknown[0]
            kids = sum(_t54_known(cells, est, c) for c in children if c != u)
            x = kids if u == parent else _t54_known(cells, est, parent) - kids
            est[u] = (_t54_bounded(cells, est, index, u, x), "identity")
            changed = solved = True
    return solved


def _t54_group_pass(cells, est, eqs, prior, index) -> bool:
    """Share out ONE sum's residual among its unknowns; True if it did."""
    for parent, children in eqs:
        p = _t54_known(cells, est, parent)
        if p is None:
            continue
        unknown = [c for c in children if _t54_known(cells, est, c) is None]
        if len(unknown) < 2:
            continue
        rest = max(p - sum(_t54_known(cells, est, c) for c in children if c not in unknown),
                   0.0)
        weights = [prior(c) or 0.0 for c in unknown]
        method = "group_prior"
        if sum(weights) <= 0:
            weights, method = [1.0] * len(unknown), "group_equal"
        total = sum(weights)
        for c, w in zip(unknown, weights):
            est[c] = (_t54_bounded(cells, est, index, c, rest * w / total), method)
        return True
    return False


def _t54_adjacent_pass(cells, est, prior, index, leaves_only: bool) -> bool:
    """Fill ONE unconstrained cell from the nearest other survey; True if it did."""
    for key in sorted(cells):
        if _t54_known(cells, est, key) is not None:
            continue
        if leaves_only and key[1] in TABLE54_HIERARCHY:
            continue
        value = prior(key)
        if value is not None:
            est[key] = (_t54_bounded(cells, est, index, key, value), "adjacent_year")
            return True
    return False


def _t54_star_pass(cells, est, block_eqs) -> None:
    """Give every `*` cell a share of its parent's unallocated residual (top down)."""
    order = {label: i for i, label in enumerate(TABLE54_HIERARCHY)}   # TOTAL first
    for parent, children in sorted(block_eqs, key=lambda e: (e[0][0], e[0][2],
                                                             order[e[0][1]])):
        if cells[parent][0] == "star" and parent not in est:
            # a `*` total has no parent of its own; what its published children add to
            # (rounded up, so at most 0.5) is the best evidence, else the midpoint
            kids = sum(_t54_known(cells, est, c) or 0.0 for c in children
                       if cells[c][0] != "star")
            est[parent] = (min(max(kids, STAR_MIDPOINT), STAR_CEILING), "star_midpoint")
        stars = [c for c in children if cells[c][0] == "star" and c not in est]
        if not stars:
            continue
        p = _t54_known(cells, est, parent)
        others = [_t54_known(cells, est, c) for c in children if c not in stars]
        if p is None or any(v is None for v in others):
            for c in stars:
                est[c] = (STAR_MIDPOINT, "star_midpoint")
            continue
        each = min(max(p - sum(others), 0.0) / len(stars), STAR_CEILING)
        for c in stars:
            est[c] = (each, "star_residual")


def estimate_table54(tables: dict, known: dict | None = None) -> dict:
    """Return {year: table} with every withheld and `*` cell estimated where possible.

    The returned frames have the layout of read_table54's, with `value` filled, `withheld`
    true only where no estimate could be made, and `method` naming how each estimated
    cell was obtained ("" for a published one).  See the comment block above for the
    methods.
    """
    cells = {y: {(r.naics, r.table_end_use, r.table_fuel): (r.status, r.value)
                 for r in t.itertuples()} for y, t in tables.items()}
    eqs = {y: _t54_equations(c) for y, c in cells.items()}
    est = {y: {} for y in tables}
    # withheld Table 5.4 totals that Table 3.2 prints (same survey, same number)
    for y, values in (known or {}).items():
        for key, value in values.items():
            if y in cells and key in cells[y] and cells[y][key][0] == "withheld":
                est[y][key] = (value, "table_3_2")

    index = {y: _t54_block_index(eqs[y][0]) for y in tables}

    # identities first, everywhere, so each survey can lend its neighbours a fuller table
    for y in tables:
        _t54_identity_pass(cells[y], est[y], eqs[y][0], index[y])
        _t54_identity_pass(cells[y], est[y], eqs[y][1], index[y])
    snapshot = {y: {k: v for k in cells[y]
                    if (v := _t54_known(cells[y], est[y], k)) is not None}
                for y in tables}

    def prior_for(year):
        def prior(key):
            found = [(abs(int(o) - int(year)), snapshot[o][key])
                     for o in snapshot if o != year and key in snapshot[o]]
            if not found:
                return None
            nearest = min(d for d, _ in found)
            values = [v for d, v in found if d == nearest]
            return sum(values) / len(values)
        return prior

    # Then, per survey, the tighter evidence first: sums inside one industry before the
    # 21-term cross-industry sums, which carry far more rounding.
    for y in tables:
        c, e, (block_eqs, all_eqs), prior, ix = (cells[y], est[y], eqs[y], prior_for(y),
                                                 index[y])
        while True:
            if _t54_identity_pass(c, e, block_eqs, ix):
                continue
            if _t54_group_pass(c, e, block_eqs, prior, ix):
                continue
            if _t54_identity_pass(c, e, all_eqs, ix):
                continue
            if _t54_group_pass(c, e, all_eqs, prior, ix):
                continue
            if (_t54_adjacent_pass(c, e, prior, ix, leaves_only=True)
                    or _t54_adjacent_pass(c, e, prior, ix, leaves_only=False)):
                continue
            break
        _t54_star_pass(c, e, block_eqs)

    out = {}
    for y, t in tables.items():
        t = t.copy()
        keys = list(zip(t.naics, t.table_end_use, t.table_fuel))
        filled = [est[y].get(k) for k in keys]
        t["value"] = [f[0] if f else v for f, v in zip(filled, t.value)]
        t["method"] = [f[1] if f else "" for f in filled]
        t["withheld"] = t["value"].isna()
        t["value_filled"] = t["value"]          # before balancing, for the step notes
        # what the nearest other survey(s) say about each withheld cell -- the anchor
        # balance_table54 pulls it toward
        prior = prior_for(y)
        t["prior"] = [prior(k) if st == "withheld" and m != "table_3_2" else np.nan
                      for k, st, m in zip(keys, t.status, t.method)]
        t.attrs["year"] = y
        out[y] = balance_table54(t)
    return out


# --------------------------------------------------------------------------------------
# closing the rounding gaps (method "rounding_balance")
# --------------------------------------------------------------------------------------
#
# EIA rounds every cell to whole TBtu independently, so a printed total of 3 can sit over
# end uses printed as 1 + 2 + 1.  For a large fuel that is noise; for a 3 TBtu fuel it is
# a 25% disagreement, and shares built on it come out odd.  Each NAICS block and fuel is
# therefore reconciled: every cell is moved as little as possible, within what its
# printed value allows, until the end uses add to their subtotals and the subtotals to
# the total.  Formally, the weighted least-squares adjustment
#
#     minimise  sum (x_i - v_i)^2 / var_i   subject to  the TABLE54_HIERARCHY sums,
#                                                      lo_i <= x_i <= hi_i
#
# solved by Dykstra's alternating projections (exact on the sums, clipped to the
# bounds).  The bounds and variances say how far each kind of cell may move:
#
#     printed number v    [v - 0.5, v + 0.5]   var 1/12 (uniform rounding error)
#     `*`                 [0, 0.5]             var 1/48
#     `--` or 0           fixed at 0
#     withheld, with a    [0, inf)             target = the nearest other survey(s),
#       neighbour value                        var max(0.5, prior/2)^2 (neighbour_prior)
#     withheld, none      [0, inf)             var 1 + (v/4)^2  -- absorbs most of it
#
# Blocks with a withheld cell are always run, even when their sums already close, so
# that the neighbour pull applies.
#
# A block whose sums cannot all be met inside those bounds (rare: the printed numbers
# would have to be inconsistent beyond rounding) is left as it was, and its rows keep
# the "end uses sum to N% of the total" note.

BALANCE_TAG = "rounding_balance"
PRIOR_TAG = "neighbour_prior"
PRIOR_SD_FLOOR = 0.5
PRIOR_SD_REL = 0.5


def prior_variance(prior: float) -> float:
    """How far a withheld cell may stray from what the nearest other survey says.

    A standard deviation of max(PRIOR_SD_FLOOR, PRIOR_SD_REL x prior) TBtu: wide enough
    that a tight identity (a withheld cell boxed in by printed siblings) still wins, narrow
    enough that where the printed cells only loosely pin a cell -- several `*` siblings,
    each anywhere in [0, 0.5) -- the neighbouring surveys decide where in that range it
    sits.
    """
    return max(PRIOR_SD_FLOOR, PRIOR_SD_REL * prior) ** 2
BALANCE_TOL = 1e-3       # TBtu: a sum closer than this already holds
BALANCE_ITERATIONS = 5000


def _dykstra(v, lo, hi, var, A):
    """Weighted projection of v onto {A x = 0} intersected with the box [lo, hi]."""
    D = np.diag(var)
    M = D @ A.T @ np.linalg.pinv(A @ D @ A.T)

    def onto_sums(z):
        return z - M @ (A @ z)

    x, p, q = v.copy(), np.zeros_like(v), np.zeros_like(v)
    for _ in range(BALANCE_ITERATIONS):
        y = onto_sums(x + p)
        p = x + p - y
        x_next = np.clip(y + q, lo, hi)
        q = y + q - x_next
        done = np.abs(x_next - x).max() < 1e-9
        x = x_next
        if done:
            break
    return x, np.abs(A @ x).max()


def balance_table54(t: pd.DataFrame) -> pd.DataFrame:
    """Reconcile each NAICS block and fuel of a gap-filled Table 5.4 to its own sums.

    Blocks with a cell still unknown are skipped; so is any block that already adds up.
    A cell that moves is tagged `rounding_balance` (appended to any method it had).
    """
    t = t.copy()
    labels = list(dict.fromkeys(list(TABLE54_HIERARCHY)
                                + [c for cs in TABLE54_HIERARCHY.values() for c in cs]))
    position = {label: i for i, label in enumerate(labels)}
    A_full = np.zeros((len(TABLE54_HIERARCHY), len(labels)))
    for r, (parent, children) in enumerate(TABLE54_HIERARCHY.items()):
        A_full[r, position[parent]] = 1.0
        for c in children:
            A_full[r, position[c]] = -1.0

    skipped = 0
    for _, idx in t.groupby(["naics", "table_fuel"]).groups.items():
        g = t.loc[idx]
        g = g[g.table_end_use.isin(position)]
        if len(g) != len(labels) or g.withheld.any():
            continue                     # a block missing rows, or still unknown
        g = g.set_index("table_end_use").loc[labels]
        v = g.value.to_numpy(float)
        anchored = (g.status.eq("withheld") & g.prior.notna()).to_numpy() \
            if "prior" in g else np.zeros(len(g), bool)
        if np.abs(A_full @ v).max() <= BALANCE_TOL and not anchored.any():
            continue
        target = v.copy()
        lo, hi, var = np.zeros_like(v), np.zeros_like(v), np.zeros_like(v)
        for i, (status, method, value) in enumerate(zip(g.status, g.method, v)):
            # by what was PRINTED, not by method: a `*` cell carries an estimation
            # method too, but must still stay under 0.5
            if anchored[i]:                              # withheld: lean on neighbours
                target[i] = g.prior.iloc[i]
                lo[i], hi[i], var[i] = 0.0, np.inf, prior_variance(target[i])
            elif method == "table_3_2":                  # printed in Table 3.2 instead
                lo[i], hi[i], var[i] = max(value - 0.5, 0.0), value + 0.5, 1 / 12
            elif status == "withheld":                   # withheld, no other survey
                lo[i], hi[i], var[i] = 0.0, np.inf, 1.0 + (value / 4) ** 2
            elif status == "num":
                lo[i], hi[i], var[i] = max(value - 0.5, 0.0), value + 0.5, 1 / 12
            elif status == "star":
                lo[i], hi[i], var[i] = 0.0, STAR_CEILING, 1 / 48
            else:                                        # "--" or a printed 0
                lo[i], hi[i], var[i] = 0.0, 0.0, 1e-12
        x, miss = _dykstra(target, lo, hi, var, A_full)
        if miss > 0.01:
            skipped += 1
            continue
        moved = np.abs(x - v) > 1e-6
        rows = idx[t.loc[idx, "table_end_use"].isin(position).to_numpy()]
        new = dict(zip(labels, x))
        tag = {label: (PRIOR_TAG if anchored[i] else BALANCE_TAG)
               for i, label in enumerate(labels) if moved[i]}
        for i in rows:
            label = t.at[i, "table_end_use"]
            t.at[i, "value"] = new[label]
            if label in tag:
                m = t.at[i, "method"]
                t.at[i, "method"] = f"{m},{tag[label]}" if m else tag[label]
    if skipped:
        year = t.attrs.get("year", "")
        print(f"  {year} {skipped} block-fuel(s) could not be balanced within their rounding "
              f"bounds and were left as estimated", file=sys.stderr)
    return t


# --------------------------------------------------------------------------------------
# MECS Tables 3.2 and 3.5: the fuel totals Table 5.4 does not cover
# --------------------------------------------------------------------------------------
#
# Table 3.2 ("Fuel Consumption") gives each NAICS block's total use of every energy
# source, including the two Table 5.4 has no column for: coke and breeze, and "other".
# Table 3.5 ("Selected Byproducts in Fuel Consumption") splits most of "other" into
# blast furnace / coke oven gas, waste gas, petroleum coke, pulping (black) liquor, wood
# chips and bark, and waste oils and materials.  Both are the same survey as Table 5.4,
# and their fuel totals agree with Table 5.4's TOTAL rows wherever both print a number.
#
# They are used three ways:
#   * a withheld Table 5.4 TOTAL is taken from Table 3.2 where 3.2 prints it
#     (method table_3_2);
#   * the measured totals of the fuels Table 5.4 cannot see -- the residual rows -- in
#     every survey year, footprint or not (see noncovered_totals);
#   * nothing else: the footprint rows remain DOE's own figures.
#
# Withheld and `*` cells in Tables 3.2 / 3.5 are filled the same way as Table 5.4's:
# each row adds across (total = its sources), the 3-digit industries add to all
# manufacturing, a covered fuel withheld in 3.2 takes the gap-filled Table 5.4 total, and
# what is still open leans on the nearest other survey.

TABLE3_FILE_GLOB = "eia_[0-9][0-9][0-9][0-9]_mecs-[0-9][0-9][0-9][0-9]-table-3-{n}.xls*"
# column -> header pattern (headers are matched after footnote markers are dropped)
TABLE32_COLUMNS = [
    ("total", r"^total$"), ("electricity", r"electricity"),
    ("residual fuel oil", r"^residual"), ("distillate fuel oil", r"^distillate"),
    ("natural gas", r"^natural gas"), ("hgl", r"^(lpg|hgl)"), ("coal", r"^coal$"),
    ("coke and breeze", r"^coke and breez"), ("hydrogen", r"^hydrogen"), ("other", r"^other"),
]
TABLE35_COLUMNS = [
    ("total", r"^total$"), ("bfg cog", r"blast furnace"), ("waste gas", r"^waste gas"),
    ("petroleum coke", r"^petroleum cok"), ("pulping liquor", r"^pulping liquor"),
    ("wood chips bark", r"^wood chips"), ("waste oils materials", r"^waste oils"),
]
# Table 3.2 columns that are Table 5.4 sources (electricity is not: 3.2 prints net
# electricity, 5.4 net DEMAND for electricity, a different quantity)
TABLE3_COVERED = ["residual fuel oil", "distillate fuel oil", "natural gas", "hgl", "coal"]
TABLE3_SOURCE_NOTE = "MECS Table 3.2 / 3.5"


def read_table3(path: str, columns: list) -> pd.DataFrame:
    """Parse the national block of a Table 3.2 or 3.5 workbook into tidy cells.

    Rows: (naics, column, value, withheld, status) with the read_table54 cell codes.  The
    unlabelled all-manufacturing "Total" row at the foot of the block becomes 311-339.
    The census-region blocks below it are not read.
    """
    sheet = pd.read_excel(path, sheet_name=0, header=None, dtype=str)
    us = next(i for i in range(len(sheet))
              if "united states" in str(sheet.iloc[i, 2]).lower())
    top = next(i for i in range(us) if re.search(r"naics", str(sheet.iloc[i, 0]), re.I))
    labels = {}
    for j in range(2, sheet.shape[1]):
        text = " ".join(str(sheet.iloc[i, j]).strip() for i in range(max(top - 3, 0), us)
                        if str(sheet.iloc[i, j]).strip() not in ("nan", ""))
        text = re.sub(r"\s+", " ", re.sub(r"\(\w\)", "", text)).strip().lower()
        labels[j] = text
    where = {}
    for name, pattern in columns:
        hit = [j for j, text in labels.items() if re.search(pattern, text)]
        if hit:
            where[name] = hit[0]
    out = []
    for i in range(us + 1, len(sheet)):
        if "region" in str(sheet.iloc[i, 2]).lower():
            break
        code = str(sheet.iloc[i, 0]).strip()
        if re.match(r"^[0-9]", code):
            naics = re.sub(r"\s+", "", code)
        elif str(sheet.iloc[i, 1]).strip().lower() == "total":
            naics = "311-339"
        else:
            continue
        for name, j in where.items():
            value, withheld, status = _t54_cell(sheet.iloc[i, j])
            out.append(dict(naics=naics, column=name, value=value, withheld=withheld,
                            status=status))
    return pd.DataFrame(out)


def load_table3(tables_dir: str) -> dict:
    """{year: {"3.2": frame, "3.5": frame}} for every year folder holding both tables."""
    found = {}
    for n, columns in (("2", TABLE32_COLUMNS), ("5", TABLE35_COLUMNS)):
        for path in sorted(glob.glob(os.path.join(tables_dir, "[0-9][0-9][0-9][0-9]",
                                                  TABLE3_FILE_GLOB.format(n=n)))):
            year = int(os.path.basename(os.path.dirname(path)))
            found.setdefault(year, {})[f"3.{n}"] = read_table3(path, columns)
            print(f"  read {os.path.relpath(path, tables_dir):<38} "
                  f"{found[year][f'3.{n}'].naics.nunique():>3} NAICS rows", file=sys.stderr)
    return {y: t for y, t in found.items() if len(t) == 2}


def estimate_table3(tables3: dict, filled54: dict) -> dict:
    """Fill the withheld and `*` cells of Tables 3.2 and 3.5.

    Returns {year: {(naics, table, column): (value, method)}} for every cell, published
    or estimated (method "" when published).  Keys use table "3.2" or "3.5".
    """
    cells, eqs, index, est = {}, {}, {}, {}
    for y, t in tables3.items():
        c = {}
        for table, frame in t.items():
            for r in frame.itertuples():
                c[(r.naics, table, r.column)] = (r.status, r.value)
        cells[y] = c
        naics = sorted({k[0] for k in c})
        block, family = [], []
        for n in naics:
            for table, frame in t.items():
                parts = [(n, table, col) for col in frame.column.unique() if col != "total"]
                if (n, table, "total") in c:
                    block.append(((n, table, "total"), [k for k in parts if k in c]))
        three = [n for n in naics if re.fullmatch(r"3\d\d", n)]
        for parent, kids in [("311-339", three), ("312", ["3121", "3122"])]:
            if parent in naics and all(k in naics for k in kids):
                for table, frame in t.items():
                    for col in frame.column.unique():
                        key = (parent, table, col)
                        children = [(k, table, col) for k in kids]
                        if key in c and all(ch in c for ch in children):
                            family.append((key, children))
        eqs[y] = (block, block + family)
        index[y] = _t54_block_index(block)
        e = {}
        # a covered fuel 3.2 withholds is the gap-filled Table 5.4 total (same survey)
        t54 = filled54.get(y)
        if t54 is not None:
            tot = t54[t54.table_end_use == TABLE54_TOTAL].set_index(["naics", "table_fuel"])
            for (n, table, col), (status, _) in c.items():
                if table == "3.2" and col in TABLE3_COVERED and status == "withheld" \
                        and (n, col) in tot.index and pd.notna(tot.value[(n, col)]):
                    e[(n, table, col)] = (float(tot.value[(n, col)]), "table_5_4")
        est[y] = e
        _t54_identity_pass(c, e, block, index[y])
        _t54_identity_pass(c, e, block + family, index[y])

    snapshot = {y: {k: v for k in cells[y]
                    if (v := _t54_known(cells[y], est[y], k)) is not None} for y in cells}

    def prior_for(year):
        def prior(key):
            found = [(abs(o - year), snapshot[o][key]) for o in snapshot
                     if o != year and key in snapshot[o]]
            if not found:
                return None
            nearest = min(d for d, _ in found)
            values = [v for d, v in found if d == nearest]
            return sum(values) / len(values)
        return prior

    out = {}
    for y in cells:
        c, e, (block, both), ix, prior = cells[y], est[y], eqs[y], index[y], prior_for(y)
        while True:
            if _t54_identity_pass(c, e, block, ix) or _t54_group_pass(c, e, block, prior, ix):
                continue
            if _t54_identity_pass(c, e, both, ix) or _t54_group_pass(c, e, both, prior, ix):
                continue
            if _t54_adjacent_pass(c, e, prior, ix, leaves_only=True) \
                    or _t54_adjacent_pass(c, e, prior, ix, leaves_only=False):
                continue
            break
        # `*` cells: an equal slice of what their row total leaves, at most 0.5 each
        for parent, children in block:
            stars = [k for k in children if c[k][0] == "star" and k not in e]
            if not stars:
                continue
            p = _t54_known(c, e, parent)
            rest = [_t54_known(c, e, k) for k in children if k not in stars]
            if p is None or any(v is None for v in rest):
                each, how = STAR_MIDPOINT, "star_midpoint"
            else:
                each = min(max(p - sum(rest), 0.0) / len(stars), STAR_CEILING)
                how = "star_residual"
            for k in stars:
                e[k] = (each, how)
        for k in c:
            if c[k][0] == "star" and k not in e:
                e[k] = (STAR_MIDPOINT, "star_midpoint")
        out[y] = {k: (e[k] if k in e else (c[k][1], "")) for k in c}
    return out


# Footprint-style names for the fuels Table 5.4 cannot see, built from Tables 3.2 / 3.5.
# One vocabulary for every survey (the 2018 footprint's, plus hydrogen from 2022), so a
# fuel means the same thing in every year:
#   coke               <- 3.2 coke and breeze less 2/3 of 3.5 BFG/COG (see COKE_BFG_SHARE)
#   coke oven gas      <- 3.5 blast furnace / coke oven gases
#   refinery fuel gas  <- 3.5 waste gas in petroleum refining (NAICS 324 / 324110)
#   byproduct fuel     <- 3.5 waste gas elsewhere, and waste oils / tars / materials
#   petroleum coke     <- 3.5 petroleum coke
#   black liquor       <- 3.5 pulping liquor
#   biomass            <- 3.5 wood chips and bark
#   other              <- 3.2 other less the 3.5 total (what 3.5 does not name)
#   hydrogen           <- 3.2 hydrogen (2022 only)
# Coke and blast furnace gas double-count: MECS assumes every fuel is fully consumed, but
# the blast furnace gas burned in iron and steel is made from the coke charged to the
# furnace.  EIA's MECS methodology note, adopted by DOE in every footprint, removes the
# double count by cutting coke and breeze by the heat content of the blast furnace gas;
# MECS prints BFG only combined with coke oven gas, "about two-thirds" of it BFG.
# Reproduces the iron and steel footprint's coke within 2-18 TBtu in 2006-2018.
COKE_BFG_SHARE = 2 / 3

NONCOVERED_FUELS = ["biomass", "black liquor", "byproduct fuel", "coke", "coke oven gas",
                    "hydrogen", "other", "petroleum coke", "refinery fuel gas"]
REFINING_CODES = ("324110", "324")


def noncovered_totals(est3: dict, codes: list) -> tuple[dict, dict]:
    """TBtu of each fuel outside Table 5.4 for a sector's NAICS blocks, and per fuel the
    methods behind any estimated cell in it.

    est3 is one year of estimate_table3.  A block missing from the tables contributes
    nothing.
    """
    def cell(n, table, col):
        v = est3.get((n, table, col))
        return (v[0] if v and v[0] == v[0] else 0.0), ({v[1]} if v and v[1] else set())

    totals = dict.fromkeys(NONCOVERED_FUELS, 0.0)
    methods = {f: set() for f in NONCOVERED_FUELS}

    def add(fuel, n, table, col, sign=1.0):
        value, m = cell(n, table, col)
        totals[fuel] += sign * value
        if value:
            methods[fuel].update(m)

    for n in codes:
        add("coke", n, "3.2", "coke and breeze")
        add("coke", n, "3.5", "bfg cog", -COKE_BFG_SHARE)
        add("hydrogen", n, "3.2", "hydrogen")
        add("other", n, "3.2", "other")
        add("other", n, "3.5", "total", -1.0)
        add("coke oven gas", n, "3.5", "bfg cog")
        add("petroleum coke", n, "3.5", "petroleum coke")
        add("black liquor", n, "3.5", "pulping liquor")
        add("biomass", n, "3.5", "wood chips bark")
        add("byproduct fuel", n, "3.5", "waste oils materials")
        if n in REFINING_CODES:
            add("refinery fuel gas", n, "3.5", "waste gas")
        elif n == "311-339":
            refining = next((r for r in REFINING_CODES if (r, "3.5", "waste gas") in est3),
                            None)
            add("byproduct fuel", n, "3.5", "waste gas")
            if refining:
                add("refinery fuel gas", refining, "3.5", "waste gas")
                add("byproduct fuel", refining, "3.5", "waste gas", -1.0)
        else:
            add("byproduct fuel", n, "3.5", "waste gas")
    # "other" less the 3.5 total can go a hair negative on rounding
    totals = {f: max(v, 0.0) for f, v in totals.items()}
    return totals, methods


# --------------------------------------------------------------------------------------
# emitting the Table 5.4 rows
# --------------------------------------------------------------------------------------


def _resolve_parts(parts, available):
    """Pick this survey's NAICS codes for a sector; (codes, None) or (None, missing part)."""
    codes = []
    for part in parts:
        for option in (part if isinstance(part, tuple) else (part,)):
            group = option if isinstance(option, tuple) else (option,)
            if all(c in available for c in group):
                codes.extend(group)
                break
        else:
            return None, part
    return codes, None


def _sectors_for_year(footprint: pd.DataFrame, year) -> tuple[list, set]:
    """The (sector, name) pairs to emit for a survey year, and the fuel vocabulary.

    A footprint year uses its own sectors.  A Table-5.4-only year (2002, 2022) borrows
    them from the nearest footprint year, adding any sector a further footprint year
    defines that the nearer ones did not -- so 2002 gets 2006's sectors plus 2018's
    petrochemicals, resins and semiconductors.  Sectors are matched on the NAICS blocks
    they are built from, so "31_33" and "31-33" do not both appear.
    """
    fp_years = sorted(footprint["mecs_year"].unique(), key=lambda f: (abs(int(f) - int(year)), f))
    nearest = fp_years[0]
    vocab = set(footprint.loc[footprint.mecs_year == nearest, "fuel_type"].dropna())
    if int(nearest) == int(year):
        rows = footprint[footprint.mecs_year == nearest]
        return [tuple(x) for x in rows[["sector", "name"]].drop_duplicates().values], vocab
    out, seen = [], set()
    for fy in fp_years:
        rows = footprint[footprint.mecs_year == fy]
        for sector, name in rows[["sector", "name"]].drop_duplicates().values:
            parts = TABLE54_SECTOR_PARTS.get(str(sector))
            if parts is None or repr(parts) in seen:
                continue
            seen.add(repr(parts))
            out.append((sector, name))
    return out, vocab


def allocate_unreported(table: pd.DataFrame, mode: str = "prorata") -> pd.DataFrame:
    """Spread each block's "End Use Not Reported" over its reported end uses.

    Works per NAICS block and fuel, BEFORE blocks are summed into sectors, so each
    industry's unreported energy follows that industry's own end-use mix.  The amount is
    shared in proportion to the end uses that have a value (withheld ones are skipped, so
    on the published table a withheld end use gets none of it); if none has a value it
    goes to process heating instead, and if that is withheld too it is left where it is.
    An allocated "not reported" cell is set to 0.  A withheld one is left withheld, and
    the rows downstream say the end uses exclude it.  Subtotal rows are not touched.
    The allocation is not tagged in `method`: it is a rule applied to every year alike.
    """
    if mode == "process-heating":
        return table
    t = table.copy()
    leaves = set(TABLE54_END_USES)
    for _, idx in t.groupby(["naics", "table_fuel"]).groups.items():
        g = t.loc[idx]
        nr = g[g.table_end_use == TABLE54_UNREPORTED]
        if nr.empty or nr.withheld.iloc[0] or not nr.value.iloc[0] > 0:
            continue
        amount = nr.value.iloc[0]
        known = g[g.table_end_use.isin(leaves) & ~g.withheld]
        base = known.value.sum()
        if base > 0:
            t.loc[known.index, "value"] += amount * known.value / base
        else:
            ph = known[known.table_end_use == TABLE54_UNREPORTED_GOES_TO]
            if ph.empty:
                continue
            t.loc[ph.index, "value"] += amount
        t.loc[nr.index, "value"] = 0.0
    return t


def _sector_cells(table: pd.DataFrame, codes: list) -> dict:
    """Sum the component NAICS blocks: {(end use, fuel): (value, withheld, methods)}.

    One withheld component makes the whole cell unknown.
    """
    block = table[table.naics.isin(codes)]
    agg = block.groupby(["table_end_use", "table_fuel"]).agg(
        value=("value", "sum"), withheld=("withheld", "any"),
        method=("method", lambda s: frozenset(x for m in s if m for x in m.split(",")))
    ).reset_index()
    return {(r.table_end_use, r.table_fuel): (r.value, r.withheld, r.method)
            for r in agg.itertuples()}


def _stage_cells(raw: pd.DataFrame, est: pd.DataFrame | None,
                 alloc: pd.DataFrame | None, codes: list) -> dict:
    """Per (end use, fuel column), how a sector's value is built up from the printed table.

    Returns {(label, column): dict} with
      printed       sum of the printed numbers (`*` and `--` as 0) over the NAICS blocks
      any_withheld  a block's cell is withheld (value_table must be empty)
      any_printed   some block prints a number or `--` (else, if only `*`, empty too)
      withheld      estimate given to the withheld cells           (est only)
      star          estimate given to the `*` cells                (est only)
      prior         change pulling withheld cells toward the neighbouring surveys
      balance       change made by rounding_balance to the other cells (est only)
      unreported    End Use Not Reported spread onto this cell     (est only)
      methods       how the withheld cells were estimated
    """
    out = {}
    r = raw[raw.naics.isin(codes)].set_index(["naics", "table_end_use", "table_fuel"])
    e = est[est.naics.isin(codes)].set_index(r.index.names) if est is not None else None
    a = alloc[alloc.naics.isin(codes)].set_index(r.index.names) if alloc is not None else None
    for (label, column), g in r.groupby(level=["table_end_use", "table_fuel"]):
        printed_mask = g.status.isin(["num", "zero"])
        d = dict(printed=float(g.value[printed_mask].sum()),
                 any_withheld=bool(g.withheld.any()), any_printed=bool(printed_mask.any()),
                 withheld=0.0, star=0.0, prior=0.0, balance=0.0, unreported=0.0,
                 methods=set())
        if e is not None:
            eg = e.loc[g.index]
            w, st = g.status.eq("withheld").to_numpy(), g.status.eq("star").to_numpy()
            d["withheld"] = float(eg.value_filled[w].sum())
            d["star"] = float(eg.value_filled[st].sum())
            moved = (eg.value - eg.value_filled).to_numpy()
            d["prior"] = float(moved[w].sum())
            d["balance"] = float(moved[~w].sum())
            d["unreported"] = float((a.loc[g.index].value - eg.value).sum())
            d["methods"] = {x for m in eg.method[w] if m for x in m.split(",")
                            if x not in (BALANCE_TAG, PRIOR_TAG)}
        out[(label, column)] = d
    return out


def _steps_note(st: dict, value: float, unreported: str) -> str:
    """'table: 3.17; +0.26 for * cells; -0.22 rounding balance; ... = 3.21' -- in PJ."""
    st = {k: (v * TBTU_TO_PJ if k in ("printed", "withheld", "star", "prior", "balance",
                                       "unreported") else v) for k, v in st.items()}
    value = value * TBTU_TO_PJ
    printed = float(round_sig(np.array([st["printed"]]))[0])
    withheld = st.get("any_withheld", False)
    parts = ["table: withheld" if withheld else
             "table: <0.53 (*)" if st["blank"] else f"table: {printed:g}"]
    if withheld and st["printed"]:
        parts[0] += f" (other cells print {printed:g})"
    if withheld or abs(st["withheld"]) >= 0.005:
        parts.append(f"{st['withheld']:+.2f} withheld cell(s) estimated "
                     f"({', '.join(sorted(st['methods'])) or 'estimated'})")
    if abs(st["star"]) >= 0.005:
        parts.append(f"{st['star']:+.2f} for * cells")
    if abs(st["prior"]) >= 0.005:
        parts.append(f"{st['prior']:+.2f} toward neighbouring surveys")
    if abs(st["balance"]) >= 0.005:
        parts.append(f"{st['balance']:+.2f} rounding balance")
    if abs(st["unreported"]) >= 0.005:
        how = "pro rata" if unreported == "prorata" else "into process heating"
        parts.append(f"{st['unreported']:+.2f} End Use Not Reported ({how})")
    if len(parts) == 1 and not st["blank"]:
        return ""                                  # value is exactly the table value
    return "; ".join(parts) + f"; = {float(round_sig(np.array([value]))[0]):g}"


def _emit_sector(year, sector, name, cell, fuel_name, source,
                 unreported: str = "prorata", stages: dict | None = None) -> list:
    """The fuel x end-use rows for one sector from one (published or estimated) table.

    `stages` (from _stage_cells) supplies value_table and, on estimated rows, the note
    that walks from it to `value`.
    """

    def staged(label: str, fuel: str) -> dict:
        """Combine _stage_cells entries over the columns that share one fuel name."""
        acc = dict(printed=0.0, withheld=0.0, star=0.0, prior=0.0, balance=0.0,
                   unreported=0.0, methods=set())
        found = any_withheld = any_printed = False
        for column in TABLE54_FUEL_COLUMNS:
            if fuel_name(column) != fuel or (label, column) not in (stages or {}):
                continue
            found = True
            st = stages[(label, column)]
            for k in ("printed", "withheld", "star", "prior", "balance", "unreported"):
                acc[k] += st[k]
            any_withheld = any_withheld or st["any_withheld"]
            any_printed = any_printed or st["any_printed"]
            acc["methods"] |= st["methods"]
        # empty when anything behind it is withheld, or when nothing is printed but `*`
        acc["blank"] = any_withheld or not any_printed or not found
        acc["any_withheld"] = any_withheld
        return acc

    def combined(label: str, fuel: str):
        """Sum the source columns that share one footprint fuel name."""
        total, missing, methods = 0.0, False, set()
        for column in TABLE54_FUEL_COLUMNS:
            if fuel_name(column) != fuel:
                continue
            value, withheld, m = cell.get((label, column), (float("nan"), True, frozenset()))
            missing = missing or withheld
            methods |= m
            total += 0.0 if withheld else value
        return (float("nan"), True, methods) if missing else (total, False, methods)

    estimated = source == ESTIMATED_TAG
    label_of = {v: k for k, v in TABLE54_END_USES.items()}
    rows = []
    for fuel in dict.fromkeys(fuel_name(c) for c in TABLE54_FUEL_COLUMNS):
        total, total_withheld, total_methods = combined(TABLE54_TOTAL, fuel)

        # Whatever "not reported" is left here is folded into process heating: all of it
        # under --unreported process-heating, and otherwise only the odd block that had
        # no reported end use to spread it over (allocate_unreported zeroes the rest).
        # Only the unreported crumb being withheld must not discard a perfectly good
        # end-use figure -- keep what was published and say the fold-in is incomplete:
        # on process heating alone under the old rule, on every end use under pro rata.
        extra, extra_withheld, extra_methods = combined(TABLE54_UNREPORTED, fuel)
        entries = []
        for label, (eu1, eu2) in TABLE54_END_USES.items():
            value, withheld, methods = combined(label, fuel)
            partial_fold = False
            if unreported == "prorata" or label == TABLE54_UNREPORTED_GOES_TO:
                partial_fold = extra_withheld and not withheld
            if label == TABLE54_UNREPORTED_GOES_TO and not extra_withheld:
                value = value + extra
                if unreported == "process-heating" or extra > 0:
                    methods = methods | extra_methods
            entries.append((eu1, eu2, value, withheld, methods, partial_fold))

        # The published rows divide by the published total, so one withheld end use
        # blanks only its own share.  The estimated rows, once every end use is known,
        # divide by the end uses' own sum instead, so the shares add to exactly 1; the
        # rounding gap to the published total goes in the note when it exceeds 2%.
        denominator, gap = total, ""
        if estimated and not any(w for _, _, _, w, _, _ in entries):
            summed = sum(v for _, _, v, _, _, _ in entries)
            if summed > 0:
                denominator = summed
                if not total_withheld and total > 0 and abs(summed / total - 1) > 0.02:
                    gap = (f"end uses sum to {summed / total:.0%} of the total; "
                           f"shares are of their sum")
            total_withheld = total_withheld and summed <= 0

        suffix = "; no estimate possible" if estimated else ""
        for eu1, eu2, value, withheld, methods, partial_fold in entries:
            if withheld:
                note = "withheld by EIA" + suffix
            elif total_withheld:
                note = "sector total withheld by EIA" + suffix
            elif denominator == 0:
                note = "fuel not consumed by this sector"
            elif partial_fold:
                note = "excludes End Use Not Reported (withheld by EIA)"
            else:
                note = ""
            st = staged(label_of[(eu1, eu2)], fuel)
            if label_of[(eu1, eu2)] == TABLE54_UNREPORTED_GOES_TO and not extra_withheld:
                # what is left on the "not reported" row is folded in here (see above)
                nr = staged(TABLE54_UNREPORTED, fuel)
                st["unreported"] += (nr["printed"] + nr["withheld"] + nr["star"]
                                     + nr["prior"] + nr["balance"] + nr["unreported"])
            value_table = None if st["blank"] else st["printed"]
            if estimated:
                parts = [note] if note else []
                if not withheld and stages is not None:
                    steps = _steps_note(st, value, unreported)
                    if steps:
                        parts.append(steps)
                if gap:
                    parts.append(gap)
                note = "; ".join(parts)
            share = (value / denominator) \
                if not (withheld or total_withheld or denominator == 0) else None
            rows.append(dict(
                mecs_year=year, sector=sector, name=name,
                flow="input", type="fuel",
                end_use_1=eu1, end_use_2=eu2, end_use_3=None,
                end_use=f"{eu1}_{eu2}", fuel_type=fuel,
                value=(None if withheld else value), value_table=value_table, unit="TBtu",
                fuel_by_end_use=share, fuel_by_end_use_note=note,
                data_source=source,
            ))
    return rows


def _covered_by_end_use(table: pd.DataFrame, codes: list) -> dict:
    """Table 5.4 fuel (electricity excluded) per footprint end use, for the residual.

    Counts only cells with a value.  Unlike the emitted rows this sums the known parts
    instead of discarding the cell, because for the residual a partial figure beats none.
    """
    reported = table[table.naics.isin(codes) & ~table.withheld
                     & (table.table_fuel != "electricity")]
    out = {}
    for label, (eu1, eu2) in TABLE54_END_USES.items():
        amount = reported.loc[reported.table_end_use == label, "value"].sum()
        if label == TABLE54_UNREPORTED_GOES_TO:
            amount += reported.loc[reported.table_end_use == TABLE54_UNREPORTED, "value"].sum()
        out[f"{eu1}_{eu2}"] = float(amount)
    return out


def fuel_by_end_use_rows(footprint: pd.DataFrame, tables_dir: str,
                         estimate: bool = True,
                         unreported: str = "prorata") -> pd.DataFrame:
    """Build the fuel x end-use rows for every survey with a Table 5.4.

    That is every footprint year plus any other year whose Table 5.4 sits under
    `tables_dir` (2002 and 2022 have no footprint; they get table_5_4 and table_5_4_est
    rows for the sectors of the nearest footprint year, and no residual rows).

    "End Use Not Reported" is first spread over each block's reported end uses
    (allocate_unreported; `unreported="process-heating"` folds it into process heating
    instead).  For each sector the component NAICS blocks are then summed, and each end use is divided by the sector's reported TOTAL FUEL
    CONSUMPTION for that fuel.  Using the reported total as the denominator -- rather than
    re-summing the end uses -- means one withheld end use only blanks its own share
    instead of invalidating the whole fuel.

    Residual and distillate fuel oil are two columns in the source but one `fuel oil` in
    the footprint vocabulary.  They are combined BEFORE the division: adding their two
    separately-computed shares would give a column that sums to 2.

    With `estimate`, a second, complete set of rows tagged table_5_4_est is emitted from
    estimate_table54's gap-filled tables, and the residual rows are computed from it.
    """
    paths = {}
    for path in sorted(glob.glob(os.path.join(tables_dir, "[0-9][0-9][0-9][0-9]",
                                              TABLE54_FILE_GLOB))):
        paths.setdefault(int(os.path.basename(os.path.dirname(path))), path)
    fp_years = {int(y) for y in footprint["mecs_year"].unique()}
    for year in sorted(fp_years - set(paths)):
        print(f"  no Table 5.4 found for {year} under {tables_dir} — "
              f"fuel_by_end_use skipped for that year", file=sys.stderr)
    if not paths:
        return pd.DataFrame(columns=SOURCE_COLUMNS + TABLE54_COLUMNS + [SOURCE_TAG])

    tables = {}
    for year, path in sorted(paths.items()):
        tables[year] = read_table54(path)
        print(f"  read {os.path.relpath(path, tables_dir):<38} "
              f"{tables[year].naics.nunique():>3} NAICS blocks"
              + ("" if year in fp_years else "  (no footprint: Table 5.4 rows only)"),
              file=sys.stderr)
    # Tables 3.2 / 3.5 first, on the printed Table 5.4 alone: a fuel both tables withhold
    # is often pinned by Table 3.2's row (total = its sources), and that figure -- printed,
    # or solved by an identity -- then stands in for the withheld Table 5.4 total.
    tables3 = load_table3(tables_dir)
    known = {}
    for year, cells3 in estimate_table3(tables3, tables).items():
        known[year] = {(n, TABLE54_TOTAL, col): value
                       for (n, table, col), (value, method) in cells3.items()
                       if table == "3.2" and col in TABLE3_COVERED
                       and method in ("", "identity") and value == value}
    filled = estimate_table54(tables, known) if estimate else {}
    if estimate:
        for year, t in filled.items():
            m = t.method[t.method != ""].str.split(",").explode().value_counts().to_dict()
            print(f"  {year} estimated cells: {m}"
                  + (f"; {int(t.withheld.sum())} still unknown" if t.withheld.any() else ""),
                  file=sys.stderr)

    est3 = estimate_table3(tables3, filled)
    for year, cells3 in sorted(est3.items()):
        m = pd.Series([v[1] for v in cells3.values() if v[1]]).value_counts().to_dict()
        print(f"  {year} Tables 3.2/3.5 estimated cells: {m}", file=sys.stderr)

    rows = []
    profiles = {}            # (year, sector parts) -> footprint residual profile or None
    pending = []             # every sector-year, for its residual rows
    for year in sorted(paths):
        table = allocate_unreported(tables[year], unreported)
        table_est = allocate_unreported(filled[year], unreported) if estimate else None
        year_value = next((y for y in footprint["mecs_year"].unique() if int(y) == year), year)
        sectors, vocab = _sectors_for_year(footprint, year)
        hgl_name = "hgl" if "hgl" in vocab else "ngl"

        def fuel_name(column: str) -> str:
            mapped = TABLE54_FUEL_MAP[column]
            return hgl_name if mapped == "hgl" else mapped

        available = set(table.naics)
        for sector, name in sectors:
            parts = TABLE54_SECTOR_PARTS.get(str(sector))
            if parts is None:
                print(f"  {year} {sector}: no Table 5.4 mapping — skipped", file=sys.stderr)
                continue
            codes, missing = _resolve_parts(parts, available)
            if codes is None:
                print(f"  {year} {sector}: NAICS {missing} absent from Table 5.4 — skipped",
                      file=sys.stderr)
                continue

            # With estimates, only the gap-filled rows are emitted: their value_table
            # column carries the printed figure the published rows would have shown.
            if estimate:
                stages = _stage_cells(tables[year], filled[year], table_est, codes)
                rows.extend(_emit_sector(year_value, sector, name,
                                         _sector_cells(table_est, codes),
                                         fuel_name, ESTIMATED_TAG, unreported, stages))
            else:
                stages = _stage_cells(tables[year], None, None, codes)
                rows.extend(_emit_sector(year_value, sector, name, _sector_cells(table, codes),
                                         fuel_name, PUBLISHED_TAG, unreported, stages))

            covered = _covered_by_end_use(table_est if estimate else table, codes)
            diag = (0.0, 0.0, None)
            if year in fp_years:
                year_rows = footprint[footprint["mecs_year"] == year_value]
                sector_rows = year_rows[year_rows.sector == sector]
                profile, pool, footprint_fuel = residual_profile(sector_rows, covered)
                profiles[(year, repr(parts))] = profile
                # what the footprint has beyond the Table 5.4 fuels -- "other" balances to it
                footprint_noncovered = footprint_fuel - sum(covered.values())
                diag = (pool, footprint_fuel, footprint_noncovered)
            pending.append((year, year_value, sector, name, repr(parts), codes, covered, diag))

    rows.extend(build_residual_rows(pending, profiles, est3, fp_years))

    if not rows:
        return pd.DataFrame(columns=SOURCE_COLUMNS + TABLE54_COLUMNS + [SOURCE_TAG])

    out = pd.DataFrame(rows)

    # Flag the sector-fuel groups whose end uses do not add back to the reported total.
    # Under 100%, the cause is the source's own suppression: cells below 0.5 TBtu print as `*` and are read
    # as zero, so for a small fuel a real slice of the total is simply never allocated.
    # The shares are left as-is -- renormalising them would invent precision -- but the
    # shortfall is recorded so it cannot be mistaken for a calculation error.  (The
    # estimated rows carry their own note, written in _emit_sector.)
    keys = ["mecs_year", "sector", "fuel_type"]
    measured = out[SOURCE_TAG].eq(PUBLISHED_TAG)
    published = out[measured]
    totals = published.groupby(keys)["fuel_by_end_use"].transform("sum")
    complete = published.groupby(keys)["fuel_by_end_use"].transform(lambda s: s.notna().all())
    off = complete & (totals - 1).abs().gt(0.02) & published.fuel_by_end_use_note.eq("")
    # Short of 100% is the unallocated `*` cells; over it can only be EIA's independent
    # rounding.  Either way the balanced table_5_4_est rows of the same group add to 1.
    cause = np.where(totals[off] < 1, "sub-0.5 TBtu cells", "independent rounding")
    out.loc[off[off].index, "fuel_by_end_use_note"] = (
        "end uses cover " + (totals[off] * 100).round(0).astype("Int64").astype(str)
        + "% of the reported fuel total (" + cause + "; table_5_4_est rows add to 100%)")
    return out


def residual_profile(sector_rows: pd.DataFrame, table_end_use: dict):
    """End-use profile of the fuels Table 5.4 cannot see, from one footprint year.

    residual(end use) = footprint fuel at that end use - Table 5.4 fuel at that end use

    Whatever the covered fuels do not account for at an end use was supplied by the fuels
    Table 5.4 cannot see; normalised, that is their profile.  Floored at zero (a negative
    residual is rounding).  Returns (profile or None, residual pool, footprint fuel), all
    TBtu.
    """
    fuel_rows = sector_rows[(sector_rows.flow == "input") & (sector_rows.type == "fuel")]
    by_end_use = fuel_rows.groupby("end_use")["value"].sum()
    total_fuel = float(by_end_use.sum())
    residual = {eu: max(float(v) - table_end_use.get(eu, 0.0), 0.0)
                for eu, v in by_end_use.items()}
    pool = sum(residual.values())
    if pool <= 0:
        return None, 0.0, total_fuel
    return {eu: r / pool for eu, r in residual.items()}, pool, total_fuel


def residual_rows(year, sector, name, totals: dict, profile: dict, note: str,
                  methods: dict, basis: dict | None = None) -> list:
    """One row per fuel outside Table 5.4 and end use: the measured total, profiled."""
    out = []
    for fuel, total in sorted(totals.items()):
        if total <= 0:
            continue
        source = (basis or {}).get(fuel, TABLE3_SOURCE_NOTE)
        fuel_note = (f"total {total * TBTU_TO_PJ:.3g} PJ from {source}"
                     + (f" (gaps estimated: {', '.join(sorted(methods[fuel]))})"
                        if methods.get(fuel) else "")
                     + f"; {note}")
        for label, (eu1, eu2) in TABLE54_END_USES.items():
            key = f"{eu1}_{eu2}"
            share = profile.get(key, 0.0)
            out.append(dict(
                mecs_year=year, sector=sector, name=name,
                flow="input", type="fuel",
                end_use_1=eu1, end_use_2=eu2, end_use_3=None,
                end_use=key, fuel_type=fuel,
                value=total * share, unit="TBtu",
                fuel_by_end_use=share, fuel_by_end_use_note=fuel_note,
                data_source=RESIDUAL_TAG,
            ))
    return out


def build_residual_rows(pending: list, profiles: dict, est3: dict, fp_years: set) -> list:
    """Residual rows for every sector and survey: measured totals, footprint profiles.

    pending holds (year, year_value, sector, name, parts, codes, covered, diag) per
    sector-year.  The totals come from Tables 3.2 / 3.5 (noncovered_totals).  The end-use
    profile is the sector's own footprint-minus-Table-5.4 residual in a footprint year;
    otherwise -- 2002, 2022, or a footprint year whose residual was empty -- the nearest
    footprint year's for the same sector; failing that, the split of the sector's own
    Table 5.4 fuels (electricity excluded).
    """
    # "Other" puts the sector on the footprint's basis.  In a footprint year it is what the
    # footprint's fuel total leaves after the Table 5.4 fuels and the byproducts MECS
    # names -- so DOE's undocumented rework of MECS "Other Fuels" is followed, and the
    # sector's fuel adds up to the footprint's.  Elsewhere it is MECS "other" times the
    # nearest footprint year's ratio of the two.
    other_basis = {}
    for year, _, _, _, parts, codes, _, diag in pending:
        if year in est3 and diag[2] is not None:
            totals = noncovered_totals(est3[year], codes)[0]
            named = sum(v for f, v in totals.items() if f != "other")
            other_basis[(year, parts)] = (max(diag[2] - named, 0.0), totals["other"])

    out = []
    for year, year_value, sector, name, parts, codes, covered, diag in pending:
        if year not in est3:
            print(f"  {year} {sector}: no Tables 3.2 / 3.5 — residual rows skipped",
                  file=sys.stderr)
            continue
        totals, methods = noncovered_totals(est3[year], codes)
        mecs_other = totals["other"]
        basis = {"coke": "MECS Table 3.2 coke and breeze less 2/3 of Table 3.5 blast "
                         "furnace / coke oven gas (DOE / EIA double-count adjustment)"}
        if (year, parts) in other_basis:
            totals["other"] = other_basis[(year, parts)][0]
            methods["other"] = set()
            basis["other"] = (f"the {year} footprint: its fuel total less the Table 5.4 "
                              f"fuels and the byproducts MECS names (DOE reworks MECS "
                              f"'Other Fuels'; MECS Tables 3.2 / 3.5 give "
                              f"{mecs_other * TBTU_TO_PJ:.3g} PJ)")
        else:
            near = sorted((y for (y, p), (fp, mecs) in other_basis.items()
                           if p == parts and mecs > 0), key=lambda y: (abs(y - year), y))
            if near and mecs_other > 0 and other_basis[(near[0], parts)][0] > 0:
                fp, mecs = other_basis[(near[0], parts)]
                totals["other"] = mecs_other * fp / mecs
                basis["other"] = (f"MECS Table 3.2 / 3.5 'other' ({mecs_other * TBTU_TO_PJ:.3g} "
                                  f"PJ) scaled to the footprint basis by the {near[0]} "
                                  f"footprint / MECS ratio ({fp / mecs:.2f})")
        if not any(v > 0 for v in totals.values()):
            continue
        own = profiles.get((year, parts))
        if own is not None:
            profile, note = own, f"end-use split: footprint minus Table 5.4, {year}"
            pool, footprint_fuel, _ = diag
            measured = sum(totals.values())
            covered_fuel = sum(covered.values())
            if footprint_fuel > 0 and measured + covered_fuel > 0:
                implied, stated = pool / footprint_fuel, measured / (measured + covered_fuel)
                if abs(implied - stated) > 0.05:
                    note += (f" (residual is {implied:.0%} of footprint fuel against a "
                             f"measured {stated:.0%}, so the split is approximate)")
        else:
            near = sorted((y for (y, p), prof in profiles.items()
                           if p == parts and prof is not None and y in fp_years),
                          key=lambda y: (abs(y - year), y))
            if near:
                profile = profiles[(near[0], parts)]
                note = (f"end-use split: footprint minus Table 5.4, {near[0]} "
                        f"(nearest footprint year with one)")
            else:
                pool = sum(covered.values())
                if pool <= 0:
                    continue
                profile = {k: v / pool for k, v in covered.items()}
                note = "end-use split: assumed that of the sector's Table 5.4 fuels"
        out.extend(residual_rows(year_value, sector, name, totals, profile, note, methods,
                                 basis))
    return out


# --------------------------------------------------------------------------------------
# io
# --------------------------------------------------------------------------------------


                                 # a scanned directory yields YEAR files only, never
                                 # this script's own output or a derived copy sitting
                                 # in the same folder
YEAR_FILE_GLOB = "doe_[0-9][0-9][0-9][0-9]_mecs-[0-9][0-9][0-9][0-9]-energy-footprint.csv"


def expand_inputs(paths: list[str], exclude: str | None = None) -> list[str]:
    """Resolve the command line into a de-duplicated list of CSV paths.

    Accepts explicit files, shell-style globs, or a directory.  A directory is scanned
    with a deliberately strict pattern -- `doe_<year>_mecs-<year>-energy-footprint.csv`, at
    its top level or one folder down (the per-year folders) --
    so that outputs of this script, `_corrected` / `_realloc` variants and anything else
    derived from the year files are not swept up alongside them.  Reading the same rows
    twice would silently double every denominator.

    `exclude` (the output path) is dropped even if named explicitly, for the same reason.
    Office lock files (~$...) are skipped.
    """
    files: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, YEAR_FILE_GLOB))
                            + glob.glob(os.path.join(p, "*", YEAR_FILE_GLOB)))
        elif any(ch in p for ch in "*?["):
            files += sorted(glob.glob(p))
        else:
            files.append(p)

    blocked = os.path.abspath(exclude) if exclude else None
    seen, out = set(), []
    for f in files:
        key = os.path.abspath(f)
        if key in seen or os.path.basename(f).startswith("~$"):
            continue
        if blocked and key == blocked:
            print(f"  skipping {os.path.basename(f)} (it is the output file)", file=sys.stderr)
            continue
        seen.add(key)
        out.append(f)
    if not out:
        sys.exit("no input files matched")
    return out


def load(files: list[str]) -> pd.DataFrame:
    """Read and stack the input files, failing loudly on an unexpected layout.

    Columns are selected by name and in a fixed order, so files that carry extra columns
    or list them differently still concatenate cleanly.
    """
    frames = []
    for f in files:
        d = pd.read_csv(f)
        missing = [c for c in SOURCE_COLUMNS if c not in d.columns]
        if missing:
            sys.exit(f"{f}: missing expected column(s): {', '.join(missing)}")
        d = d[SOURCE_COLUMNS]
        d[SOURCE_TAG] = "footprint"
        d["source_file"] = os.path.basename(f)
        frames.append(d)
        print(f"  read {os.path.basename(f):<38} {len(d):>5} rows", file=sys.stderr)
    stacked = pd.concat(frames, ignore_index=True)

    # Every metric here is a share of a group total, so a row appearing twice inflates
    # its own denominator and quietly corrupts the whole column -- the two share columns
    # even keep summing to 1, which hides it.  Refuse to continue instead.
    id_cols = ["mecs_year", "sector", "flow", "type",
               "end_use_1", "end_use_2", "end_use_3", "fuel_type"]
    dups = stacked[stacked.duplicated(id_cols, keep=False)]
    if len(dups):
        where = dups.groupby("source_file").size().to_dict()
        sample = dups.sort_values(id_cols).head(3)[id_cols + ["value", "source_file"]]
        sys.exit(
            f"{len(dups)} duplicated row(s) across the inputs — the same flow is present "
            f"more than once, which would double-count it.\n"
            f"  rows per file: {where}\n"
            f"  first examples:\n{sample.to_string(index=False)}\n"
            f"Pass one file per survey year (an original and a revised copy of the same "
            f"year cannot both be used)."
        )
    return stacked


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Add share and efficiency metrics to the MECS energy-footprint CSVs.",
    )
    ap.add_argument("inputs", nargs="+",
                    help="CSV files, a glob, or a directory containing doe_*_mecs-*-energy-footprint.csv")
    ap.add_argument("-o", "--output", default="emrg_2026_mecs-footprint-metrics.csv",
                    help="output CSV path (default: %(default)s)")
    ap.add_argument("--per-year", action="store_true",
                    help="write one output file per input year instead of a single combined file")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                    help="minimum TBtu for efficiency / boiler_cogen_share / heat_to_power_ratio "
                         "to be computed (default: %(default)s)")
    ap.add_argument("--tables-dir", default=None,
                    help="folder holding the per-year subfolders with Table 5.4 "
                         "(default: the mecs folder the first input file sits in or under)")
    ap.add_argument("--no-fuel-by-end-use", action="store_true",
                    help="skip the Table 5.4 pass and emit footprint rows only")
    ap.add_argument("--unreported", choices=UNREPORTED_MODES, default="prorata",
                    help="where Table 5.4's End Use Not Reported goes: spread pro rata over "
                         "the reported end uses (default), or all into process heating")
    ap.add_argument("--no-estimates", action="store_true",
                    help="do not fill Table 5.4's withheld and `*` cells: emit no "
                         "table_5_4_est rows and build the residual from published cells only")
    ap.add_argument("--keep-source-file", action="store_true",
                    help="keep the source_file column in the output")
    args = ap.parse_args()

    files = expand_inputs(args.inputs, exclude=None if args.per_year else args.output)
    print(f"reading {len(files)} file(s)", file=sys.stderr)
    df = load(files)

    out = add_metrics(df, threshold=args.threshold)

    if not args.no_fuel_by_end_use:
        first_dir = os.path.dirname(os.path.abspath(files[0]))
        if re.fullmatch(r"\d{4}", os.path.basename(first_dir)):   # a per-year folder
            first_dir = os.path.dirname(first_dir)
        tables_dir = args.tables_dir or first_dir
        print(f"reading Table 5.4 from {tables_dir}", file=sys.stderr)
        extra = fuel_by_end_use_rows(df, tables_dir, estimate=not args.no_estimates,
                                     unreported=args.unreported)
        if len(extra):
            out = pd.concat([out, extra], ignore_index=True)
            print(f"  added {len(extra)} fuel x end-use rows", file=sys.stderr)

    # value_table sits beside value: the printed Table 5.4 figure behind a table_5_4_est
    # (or table_5_4) row, blank for footprint and residual rows
    source_cols = SOURCE_COLUMNS[:SOURCE_COLUMNS.index("value") + 1] + ["value_table"] \
        + SOURCE_COLUMNS[SOURCE_COLUMNS.index("value") + 1:]
    cols = (source_cols + DERIVED_COLUMNS + TABLE54_COLUMNS + [SOURCE_TAG]
            + (["source_file"] if args.keep_source_file else []))
    for c in cols:
        if c not in out.columns:
            out[c] = None
    # Footprint rows keep their input-file order; the Table 5.4 block is appended after.
    # Re-sorting would gain nothing and would break row-for-row comparison with the source
    # files and the reference workbook.
    out = add_fuel_mix(out[cols])
    tbtu = out["unit"].eq("TBtu")
    out.loc[tbtu, "value"] = pd.to_numeric(out.loc[tbtu, "value"]) * TBTU_TO_PJ
    out["value_table"] = pd.to_numeric(out["value_table"]) * TBTU_TO_PJ
    out.loc[tbtu, "unit"] = "PJ"
    out.loc[out["unit"].eq("%"), "unit"] = "fraction"   # footprint fuel-mix rows hold fractions
    out["value"] = round_sig(out["value"])
    out["value_table"] = round_sig(out["value_table"])
    out = round_shares(out)
    out = to_output_names(out)
    cols = list(out.columns)

    if args.per_year:
        base, ext = os.path.splitext(args.output)
        for year, chunk in out.groupby("mecs_year", sort=True):
            path = f"{base}_{year}{ext}"
            chunk.to_csv(path, index=False)
            print(f"wrote {path}  ({len(chunk)} rows)", file=sys.stderr)
    else:
        out.to_csv(args.output, index=False)
        print(f"wrote {args.output}  ({len(out)} rows, {len(cols)} columns)", file=sys.stderr)
    print(f"wrote {write_metadata(args.output)}", file=sys.stderr)

    # Blank counts are the quickest smoke test: the share columns should be well
    # populated, the efficiency and ratio columns only sparsely.
    derived = [c for c in OUTPUT_ORDER if c.startswith("share_of")
               or c in ("efficiency", "heat_to_power_ratio")]
    filled = out[derived].notna().sum()
    print("\nnon-blank cells per derived column:", file=sys.stderr)
    for c in derived:
        print(f"  {c:<20} {filled[c]:>5}", file=sys.stderr)
    counts = out[SOURCE_TAG].value_counts().to_dict()
    print(f"rows by source: {counts}", file=sys.stderr)


if __name__ == "__main__":
    main()
