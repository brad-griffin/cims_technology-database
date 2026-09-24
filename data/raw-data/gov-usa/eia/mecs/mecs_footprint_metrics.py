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

`value` is TBtu for every flow except `share`.  An end use is identified either by the
three-part key `end_use_1` / `end_use_2` / `end_use_3` or by the pre-joined `end_use`
column ("process_machine drive_pumps").

This script adds five derived columns that turn those absolute flows into ratios you can
compare across sectors and years, and appends a second block of rows carrying a sixth
column, `fuel_by_end_use`, taken from a different source (see below).

The five derived columns (on the footprint rows)
------------------------------------------------
end_use_by_type
    Within one (sector, flow, energy type), how that energy divides across end uses.
    Example: of all the fuel a sector puts into end uses, the fraction going to process
    heating.  Values within a group sum to 1.

type_by_end_use
    Within one (sector, flow, end use), how that energy divides across the types
    fuel / electricity / steam.  Example: of everything reaching process heating, the
    fraction arriving as steam.  Values within a group sum to 1.

efficency
    For a loss row, the fraction of the energy entering that end use that did useful
    work:  1 - loss / (everything delivered to the end use).
    Only computed for loss rows at or above `--threshold` (see "Why the threshold").
    Left blank on every other row.

boiler_cogen_share
    For a steam output row, that source's share of the sector's total onsite steam.
    Reading the boiler and cogeneration rows together tells you how the sector's steam
    is raised.  Blank on other rows and below the threshold.

heat_to_power_ratio
    For cogeneration, TBtu of steam produced per TBtu of electricity produced.
    Computed from steam's share `r` of total cogeneration output as r / (1 - r), which is
    algebraically steam / electricity but keeps the arithmetic in one place.
    Blank on other rows and below the threshold.

The sixth column: fuel_by_end_use (on its own rows)
---------------------------------------------------
The footprint files say how much energy reached each end use, and separately what a
sector's fuel mix was, but never the two together -- they cannot tell you what share of a
sector's natural gas went to process heating.  MECS Table 5.4, "End Uses of Fuel
Consumption", does report that crossing, so this script reads it from each year's
subfolder and appends the answer as extra rows:

    flow=input, type=fuel, end_use_1/2 as in the footprint, fuel_type named,
    value = the Table 5.4 TBtu, fuel_by_end_use = that end use's share of the fuel

Points to keep in mind when using them:

* They are a DIFFERENT accounting basis and are tagged `data_source=table_5_4` to keep
  them apart.  Table 5.4 covers six energy sources only -- electricity, residual fuel oil,
  distillate/diesel, natural gas, HGL, coal -- so byproduct fuels, coke and biomass are
  absent and these rows will not reproduce a sector's footprint fuel mix.  Do not add
  them to footprint rows: `flow=input` is shared, and only `fuel_type` (blank on
  footprint inputs) and `data_source` distinguish them.

* "End Use Not Reported" is folded into process heating, so the shares still describe the
  sector's whole reported consumption.

* Each share is `end use / the sector's REPORTED total` for that fuel, not a share of the
  re-summed end uses.  That way one withheld end use blanks only its own share instead of
  invalidating the fuel, but it also means the shares need not add to exactly 1: EIA
  prints anything under 0.5 TBtu as `*`, which is read as zero, so for a small fuel a real
  slice of the total is never allocated.  `fuel_by_end_use_note` records the shortfall
  where it exceeds 2%.  The shares are deliberately NOT renormalised.

* Withheld cells (Q, W, D, C) leave both `value` and the share empty, with the reason in
  `fuel_by_end_use_note`.  When a sector is the sum of several NAICS blocks, one withheld
  component makes the whole cell unknown.

Estimated rows for the fuels Table 5.4 cannot see (data_source=residual)
-----------------------------------------------------------------------
Byproduct fuel, coke, biomass, black liquor, coke oven gas, refinery fuel gas and "other"
have no column in Table 5.4, but the footprint says how much of each a sector burned.
Subtracting Table 5.4's covered fuels from the footprint's fuel-by-end-use leaves a
residual, and whatever the covered fuels do not account for at an end use must have come
from the fuels Table 5.4 cannot see.  Normalising that residual gives one end-use profile;
each non-covered fuel is assumed to follow it, with its own tonnage taken from the
footprint fuel-mix share.  So the fuel TOTALS are measured and only the SHAPE is inferred.

The results are physically sensible where they can be judged -- 2018 forest products puts
98% of its black liquor and biomass into cogeneration and boilers, cement puts 99% of its
petroleum coke into process heating -- but two limitations are real, and both are recorded
in `fuel_by_end_use_note`:

* The residual also absorbs covered fuel that Table 5.4 never allocated (`*` cells under
  0.5 TBtu, and withheld cells), so it overstates the non-covered energy and dilutes the
  profile.  The note names the size of the discrepancy whenever the residual exceeds the
  footprint's stated non-covered share by more than 5 points.
* Every non-covered fuel in a sector necessarily gets the SAME profile.  Neither source
  distinguishes coke from coke oven gas by end use.

Note also that the residual is computed from the SUM OF REPORTED Table 5.4 cells, treating
a withheld cell as zero, whereas the emitted `table_5_4` rows blank a cell entirely if any
NAICS component of it was withheld.  The two rules differ on purpose: for a value you
publish, all-or-nothing is right; for a subtraction, a partial figure beats none.

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
  `type_by_end_use` reports the fuel / electricity / steam split of purchased energy.

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
input and `efficency` comes out negative (plastics_rubber reaches -15).  This is a limit
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

Usage
-----
  python mecs_footprint_metrics.py INPUT...  [-o OUTPUT.csv] [--per-year] [--threshold 10]

  python mecs_footprint_metrics.py . -o emrg_2026_mecs-footprint-metrics.csv
  python mecs_footprint_metrics.py 20*/doe_*_mecs-*-energy-footprint.csv --per-year

Table 5.4 is looked for at <tables-dir>/<year>/eia_<pub-year>_mecs-<year>-table-5-4.xls[x];
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
    "end_use_by_type", "type_by_end_use", "efficency",
    "boiler_cogen_share", "heat_to_power_ratio",
]
# Added by the Table 5.4 pass.  These live on their own rows, never alongside the five
# above: the footprint and Table 5.4 are different accounting bases and mixing their
# numbers in one row would invite exactly that mistake.
TABLE54_COLUMNS = ["fuel_by_end_use", "fuel_by_end_use_note"]
# Which file a row came from.  Also what keeps the Table 5.4 rows out of the group totals
# behind the five derived columns -- they share `flow="input"` with real footprint rows.
SOURCE_TAG = "data_source"

# Minimum TBtu for a row to get an efficiency, steam share or heat-to-power ratio.
# Below this, source rounding to whole TBtu dominates the ratio (see "Why the threshold").
DEFAULT_THRESHOLD = 10.0

# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------


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

    # -- efficency: useful fraction of everything delivered to a loss row's end use -----
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
    df["efficency"] = eff

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
# leaves are read; the subtotal rows would double-count.

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
# Folded into process heating rather than dropped, so the shares still cover the sector's
# whole reported consumption.
TABLE54_UNREPORTED = "End Use Not Reported"
TABLE54_UNREPORTED_GOES_TO = "Process Heating"
TABLE54_TOTAL = "TOTAL FUEL CONSUMPTION"
# subtotal rows -- read for reconciliation, never emitted
TABLE54_SUBTOTALS = ["Indirect Uses-Boiler Fuel", "Direct Uses-Total Process",
                     "Direct Uses-Total Nonprocess"]

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

# Footprint sector code -> the Table 5.4 NAICS blocks that make it up.  A tuple means
# "whichever of these the survey uses" (the iron and steel mills code was renumbered
# 331111 -> 331110 between 2010 and 2014).  Sectors Table 5.4 breaks out but the
# footprints do not are simply never requested.
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
    "3272_327993":     ["327211", "327212", "327213", "327215", "327993"],
    "32731":           ["327310"],
    "33111_3312":      [("331110", "331111"), "3312"],
    "3313":            ["3313"],
    "3315":            ["3315"],
    "332":             ["332"],
    "333":             ["333"],
    "334_335":         ["334", "335"],
    "334413":          ["334413"],
    "336":             ["336"],
    "33611":           ["336111", "336112"],
    "3364":            ["3364"],
}

# EIA cell codes.  `--` is "not applicable" and `*` is "less than 0.5"; both are read as
# zero.  The rest mean the value was withheld, and are read as unknown so that a share
# built on them comes out blank rather than wrong.
# Fuels the footprint reports that Table 5.4 has no column for.  Their end-use split is
# estimated rather than measured -- see residual_fuel_rows.
RESIDUAL_TAG = "residual"
RESIDUAL_NOTE = ("estimated: non-Table 5.4 fuels share the end-use profile of the "
                 "footprint-minus-Table-5.4 residual")

TABLE54_ZERO_CODES = {"--", "*", "", "nan", "0"}
TABLE54_WITHHELD_CODES = {"Q", "W", "D", "C", "NF", "NM"}


def _t54_cell(raw):
    """Return (value, withheld).  Withheld cells give (nan, True)."""
    s = str(raw).strip()
    if s in TABLE54_ZERO_CODES:
        return 0.0, False
    if s.upper() in TABLE54_WITHHELD_CODES:
        return float("nan"), True
    try:
        return float(s.replace(",", "")), False
    except ValueError:
        return float("nan"), True


def read_table54(path: str) -> pd.DataFrame:
    """Parse one Table 5.4 workbook into tidy (naics, end_use, fuel) rows.

    The sheet is a report, not a table: a NAICS code in the first column opens a block and
    the end-use rows beneath it carry no code of their own.  The header row is located by
    looking for "End Use" rather than assumed, since its position moved between surveys.
    """
    sheet = pd.read_excel(path, sheet_name=TABLE54_SHEET, header=None)
    header = next((i for i in range(30) if str(sheet.iloc[i, 1]).strip() == "End Use"), None)
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
            value, withheld = _t54_cell(sheet.iloc[i, 2 + j])
            out.append(dict(naics=naics, table_end_use=key, table_fuel=fuel,
                            value=value, withheld=withheld))
    return pd.DataFrame(out)


def _t54_norm(s) -> str:
    """Normalise an end-use label for matching: drop footnote markers and fold whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"\(\w\)", "", str(s))).strip().lower()


def fuel_by_end_use_rows(footprint: pd.DataFrame, tables_dir: str) -> pd.DataFrame:
    """Build the fuel x end-use rows for every (year, sector) present in the footprint data.

    For each sector the component NAICS blocks are summed, "End Use Not Reported" is added
    to process heating, and each end use is divided by the sector's reported TOTAL FUEL
    CONSUMPTION for that fuel.  Using the reported total as the denominator -- rather than
    re-summing the end uses -- means one withheld end use only blanks its own share
    instead of invalidating the whole fuel.

    Residual and distillate fuel oil are two columns in the source but one `fuel oil` in
    the footprint vocabulary.  They are combined BEFORE the division: adding their two
    separately-computed shares would give a column that sums to 2.
    """
    rows = []
    for year in sorted(footprint["mecs_year"].unique()):
        matches = sorted(glob.glob(os.path.join(tables_dir, str(year), TABLE54_FILE_GLOB)))
        if not matches:
            print(f"  no Table 5.4 found for {year} under {tables_dir} — "
                  f"fuel_by_end_use skipped for that year", file=sys.stderr)
            continue
        table = read_table54(matches[0])
        print(f"  read {os.path.relpath(matches[0], tables_dir):<38} "
              f"{table.naics.nunique():>3} NAICS blocks", file=sys.stderr)

        # the survey's own name for the HGL column, taken from the footprint fuel mix
        year_rows = footprint[footprint["mecs_year"] == year]
        vocab = set(year_rows["fuel_type"].dropna())
        hgl_name = "hgl" if "hgl" in vocab else "ngl"

        def fuel_name(column: str) -> str:
            mapped = TABLE54_FUEL_MAP[column]
            return hgl_name if mapped == "hgl" else mapped

        available = set(table.naics)
        for sector, name in year_rows[["sector", "name"]].drop_duplicates().values:
            parts = TABLE54_SECTOR_PARTS.get(str(sector))
            if parts is None:
                print(f"  {year} {sector}: no Table 5.4 mapping — skipped", file=sys.stderr)
                continue
            codes = []
            for p in parts:
                found = [c for c in (p if isinstance(p, tuple) else (p,)) if c in available]
                if not found:
                    print(f"  {year} {sector}: NAICS {p} absent from Table 5.4 — skipped",
                          file=sys.stderr)
                    codes = None
                    break
                codes.append(found[0])
            if codes is None:
                continue

            # sum the component NAICS blocks; a withheld part makes the whole cell unknown
            block = table[table.naics.isin(codes)]
            agg = block.groupby(["table_end_use", "table_fuel"]).agg(
                value=("value", "sum"), withheld=("withheld", "any")).reset_index()
            cell = {(r.table_end_use, r.table_fuel): (r.value, r.withheld)
                    for r in agg.itertuples()}

            # covered-fuel TBtu per end use, counting only what was actually published.
            # Unlike the emitted rows this sums the reported parts instead of discarding
            # the cell, because for the residual a partial figure beats none at all.
            reported = block[(~block.withheld)
                             & (block.table_fuel != "electricity")]
            covered_by_end_use = {}
            for label, (eu1, eu2) in TABLE54_END_USES.items():
                amount = reported.loc[reported.table_end_use == label, "value"].sum()
                if label == TABLE54_UNREPORTED_GOES_TO:
                    amount += reported.loc[
                        reported.table_end_use == TABLE54_UNREPORTED, "value"].sum()
                covered_by_end_use[f"{eu1}_{eu2}"] = float(amount)

            def combined(label: str, fuel: str):
                """Sum the source columns that share one footprint fuel name."""
                total, missing = 0.0, False
                for column in TABLE54_FUEL_COLUMNS:
                    if fuel_name(column) != fuel:
                        continue
                    value, withheld = cell.get((label, column), (float("nan"), True))
                    missing = missing or withheld
                    total += 0.0 if withheld else value
                return (float("nan"), True) if missing else (total, False)

            for fuel in dict.fromkeys(fuel_name(c) for c in TABLE54_FUEL_COLUMNS):
                total, total_withheld = combined(TABLE54_TOTAL, fuel)

                for label, (eu1, eu2) in TABLE54_END_USES.items():
                    value, withheld = combined(label, fuel)
                    partial_fold = False
                    if label == TABLE54_UNREPORTED_GOES_TO:
                        extra, extra_withheld = combined(TABLE54_UNREPORTED, fuel)
                        # Only the unreported crumb being withheld must not discard a
                        # perfectly good process-heating figure -- keep what was published
                        # and say the fold-in is incomplete.
                        if extra_withheld:
                            partial_fold = not withheld
                        else:
                            value = value + extra

                    if withheld:
                        note = "withheld by EIA"
                    elif total_withheld:
                        note = "sector total withheld by EIA"
                    elif total == 0:
                        note = "fuel not consumed by this sector"
                    elif partial_fold:
                        note = "excludes End Use Not Reported (withheld by EIA)"
                    else:
                        note = ""
                    share = (value / total) if not (withheld or total_withheld or total == 0) \
                        else None
                    rows.append(dict(
                        mecs_year=year, sector=sector, name=name,
                        flow="input", type="fuel",
                        end_use_1=eu1, end_use_2=eu2, end_use_3=None,
                        end_use=f"{eu1}_{eu2}", fuel_type=fuel,
                        value=(None if withheld else value), unit="TBtu",
                        fuel_by_end_use=share, fuel_by_end_use_note=note,
                        data_source="table_5_4",
                    ))

            covered_names = {fuel_name(c) for c in TABLE54_FUEL_COLUMNS} - {"electricity"}
            rows.extend(residual_fuel_rows(
                footprint,
                year_rows[year_rows.sector == sector],
                covered_by_end_use,
                covered_names,
            ))

    if not rows:
        return pd.DataFrame(columns=SOURCE_COLUMNS + TABLE54_COLUMNS + [SOURCE_TAG])

    out = pd.DataFrame(rows)

    # Flag the sector-fuel groups whose end uses do not add back to the reported total.
    # Cause is the source's own suppression: cells below 0.5 TBtu print as `*` and are read
    # as zero, so for a small fuel a real slice of the total is simply never allocated.
    # The shares are left as-is -- renormalising them would invent precision -- but the
    # shortfall is recorded so it cannot be mistaken for a calculation error.
    keys = ["mecs_year", "sector", "fuel_type"]
    measured = out.data_source.eq("table_5_4")
    out_measured = out[measured]
    totals = out.groupby(keys)["fuel_by_end_use"].transform("sum").where(measured)
    complete = out.groupby(keys)["fuel_by_end_use"].transform(lambda s: s.notna().all())
    off = measured & complete & (totals - 1).abs().gt(0.02)
    out.loc[off & out.fuel_by_end_use_note.eq(""), "fuel_by_end_use_note"] = (
        "end uses cover " + (totals[off & out.fuel_by_end_use_note.eq("")] * 100).round(0)
        .astype("Int64").astype(str) + "% of the reported fuel total (sub-0.5 TBtu cells)")
    return out


def residual_fuel_rows(footprint: pd.DataFrame, sector_rows: pd.DataFrame,
                       table_end_use: dict, covered: set) -> list:
    """Estimate the end-use split of the fuels Table 5.4 has no column for.

    Table 5.4 measures six energy sources.  A sector's byproduct fuel, coke, biomass,
    black liquor and so on are therefore invisible to it, even though the footprint says
    how much of each the sector burned.  What the two sources together DO pin down is
    where that missing energy went:

        residual(end use) = footprint fuel at that end use
                          - Table 5.4 fuel at that end use (the covered fuels)

    Whatever the covered fuels do not account for at an end use must have been supplied
    by the fuels Table 5.4 cannot see.  Normalising the residual gives one end-use
    profile, and each non-covered fuel is assumed to follow it; its own tonnage comes
    from the footprint's fuel-mix share.  So the TOTALS are measured and only the SHAPE
    is inferred.

    Two honest limitations, both recorded in the note column:

    * The residual also absorbs covered fuel that Table 5.4 never allocated -- cells
      printed as `*` (under 0.5 TBtu) and cells withheld -- so it overstates the
      non-covered energy.  Where the residual is much larger than the footprint's own
      non-covered share, the profile is correspondingly diluted.
    * All non-covered fuels in a sector necessarily receive the SAME profile.  Nothing in
      either source distinguishes, say, coke from coke oven gas by end use.
    """
    fuel_rows = sector_rows[(sector_rows.flow == "input") & (sector_rows.type == "fuel")]
    footprint_by_end_use = fuel_rows.set_index("end_use")["value"]
    total_fuel = float(footprint_by_end_use.sum())

    shares = sector_rows[sector_rows.flow == "share"].set_index("fuel_type")["value"]
    non_covered = {f: float(v) for f, v in shares.items() if f not in covered}
    if not non_covered or total_fuel <= 0:
        return []

    # residual per end use, floored at zero: a negative one means Table 5.4 reports more
    # for the covered fuels than the footprint has in total, which is rounding noise
    residual, measured = {}, 0.0
    for end_use, value in footprint_by_end_use.items():
        covered_here = table_end_use.get(end_use, 0.0)
        measured += covered_here
        residual[end_use] = max(float(value) - covered_here, 0.0)
    pool = sum(residual.values())
    if pool <= 0:
        return []

    # how far the residual is from what the footprint itself says is non-covered
    implied = pool / total_fuel
    stated = sum(non_covered.values())
    note = RESIDUAL_NOTE
    if abs(implied - stated) > 0.05:
        note += (f"; residual is {implied:.0%} of sector fuel against a stated "
                 f"{stated:.0%} non-covered share, so the profile is diluted by "
                 f"unallocated Table 5.4 fuel")

    year = sector_rows["mecs_year"].iloc[0]
    sector = sector_rows["sector"].iloc[0]
    name = sector_rows["name"].iloc[0]
    out = []
    for fuel, share in sorted(non_covered.items()):
        fuel_total = share * total_fuel
        for label, (eu1, eu2) in TABLE54_END_USES.items():
            key = f"{eu1}_{eu2}"
            profile = residual.get(key, 0.0) / pool
            out.append(dict(
                mecs_year=year, sector=sector, name=name,
                flow="input", type="fuel",
                end_use_1=eu1, end_use_2=eu2, end_use_3=None,
                end_use=key, fuel_type=fuel,
                value=round(fuel_total * profile, 3), unit="TBtu",
                fuel_by_end_use=profile, fuel_by_end_use_note=note,
                data_source=RESIDUAL_TAG,
            ))
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
                    help="minimum TBtu for efficency / boiler_cogen_share / heat_to_power_ratio "
                         "to be computed (default: %(default)s)")
    ap.add_argument("--tables-dir", default=None,
                    help="folder holding the per-year subfolders with Table 5.4 "
                         "(default: the mecs folder the first input file sits in or under)")
    ap.add_argument("--no-fuel-by-end-use", action="store_true",
                    help="skip the Table 5.4 pass and emit footprint rows only")
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
        extra = fuel_by_end_use_rows(df, tables_dir)
        if len(extra):
            out = pd.concat([out, extra], ignore_index=True)
            print(f"  added {len(extra)} fuel x end-use rows", file=sys.stderr)

    cols = (SOURCE_COLUMNS + DERIVED_COLUMNS + TABLE54_COLUMNS + [SOURCE_TAG]
            + (["source_file"] if args.keep_source_file else []))
    for c in cols:
        if c not in out.columns:
            out[c] = None
    # Footprint rows keep their input-file order; the Table 5.4 block is appended after.
    # Re-sorting would gain nothing and would break row-for-row comparison with the source
    # files and the reference workbook.
    out = out[cols]

    if args.per_year:
        base, ext = os.path.splitext(args.output)
        for year, chunk in out.groupby("mecs_year", sort=True):
            path = f"{base}_{year}{ext}"
            chunk.to_csv(path, index=False)
            print(f"wrote {path}  ({len(chunk)} rows)", file=sys.stderr)
    else:
        out.to_csv(args.output, index=False)
        print(f"wrote {args.output}  ({len(out)} rows, {len(cols)} columns)", file=sys.stderr)

    # Blank counts are the quickest smoke test: the two share columns should be fully
    # populated, the other three only sparsely.
    filled = out[DERIVED_COLUMNS + ["fuel_by_end_use"]].notna().sum()
    print("\nnon-blank cells per derived column:", file=sys.stderr)
    for c in DERIVED_COLUMNS + ["fuel_by_end_use"]:
        print(f"  {c:<20} {filled[c]:>5}", file=sys.stderr)
    counts = out[SOURCE_TAG].value_counts().to_dict()
    print(f"rows by source: {counts}", file=sys.stderr)


if __name__ == "__main__":
    main()
