# emrg_2026_mecs-footprint-metrics.csv -- column guide

Written by `mecs_footprint_metrics.py` alongside `emrg_2026_mecs-footprint-metrics.csv`; regenerated on every run.  The script's docstring has the full method.

Each row is one energy flow for one MECS sector and survey year, in PJ.  `data_source` says where it comes from.  Footprint rows are DOE's diagrams; table_5_4_est and residual rows together give the same sector fuel total (within a few TBtu in 2006-2018) split by individual fuel and end use.  They describe the same energy, so never add the two together:

* **footprint** -- the DOE/EIA MECS energy-footprint CSVs (2006-2018), with the derived share and efficiency columns.
* **table_5_4_est** -- MECS Table 5.4, *End Uses of Fuel Consumption* (2002-2022), for its six energy sources: electricity, residual and distillate fuel oil (combined here as fuel oil), natural gas, NGL/HGL, coal.  Withheld and `*` cells are estimated so that shares add to 1; withheld totals come from Table 3.2 where it has them.
* **residual** -- the fuels Table 5.4 does not cover (coke, biomass, byproduct fuel, ...).  Named fuels are measured in MECS Table 3.2 (*Fuel Consumption*) and Table 3.5 (*Selected Byproducts in Fuel Consumption*) for every year, with coke net of blast furnace gas as DOE does; 'other' is set so the sector's fuel matches the footprint (DOE reworks MECS 'Other Fuels' without a published rule).  The split across end uses is inferred from footprint minus Table 5.4 (2002 and 2022: the nearest footprint year's split, and 'other' scaled by its ratio).

Every share column is named for what it is a share **of**: `share_of_fuel` is this row's share of its fuel, `share_of_end_use` its share of what feeds its end use, and so on.

Share columns are rounded to 2 decimal places so that each group adds to exactly 1 (largest-remainder rounding); `value` to 3 significant figures, never past the units place.  Shares are computed before rounding.

## Columns

| column | rows | unit | meaning |
|---|---|---|---|
| `mecs_year` | all |  | MECS survey year (2002-2022).  Footprint rows exist for 2006, 2010, 2014 and 2018; Table 5.4 and residual rows for all six surveys. |
| `sector` | all |  | Footprint sector code, built from NAICS codes (e.g. 311_312 = food and beverage; 31_33 or 31-33 = all manufacturing).  Table 5.4 rows for a sector sum the NAICS blocks listed in TABLE54_SECTOR_PARTS. |
| `name` | all |  | Sector name as used in the footprint files. |
| `flow` | all |  | Kind of energy flow: import (purchased offsite), input (delivered to an end use), input_combined (delivered to a machine-drive component, pre-blended across types), output (produced onsite), loss (entered an end use but did no useful work), export (sold offsite), share (footprint fuel-mix percentage, not a flow).  Table 5.4 and residual rows are all `input`. |
| `type` | all |  | Energy type: fuel, electricity or steam.  Table 5.4 and residual rows are `fuel`, including the electricity rows of Table 5.4 (fuel_type says which). |
| `end_use_1` | all but import/export/share |  | End-use group: onsite generation, process, nonprocess. |
| `end_use_2` | all but import/export/share |  | End use within the group, e.g. boilers, cogeneration, heating, machine drive, hvac. |
| `end_use_3` | footprint machine-drive rows |  | Machine-drive component (pumps, fans, compressed air, ...). |
| `end_use` | all but import/export/share |  | end_use_1, end_use_2 and end_use_3 joined with underscores, e.g. `process_heating`. |
| `fuel_type` | share, table_5_4_est, residual |  | Fuel.  On Table 5.4 rows one of electricity, fuel oil (residual + distillate), natural gas, ngl/hgl (named as in that year's footprint; 2002 follows 2006, 2022 follows 2018), coal.  On residual rows, in every year: coke (3.2 coke and breeze less 2/3 of 3.5 blast furnace / coke oven gas, the DOE / EIA double-count adjustment), coke oven gas (3.5 blast furnace / coke oven gases), refinery fuel gas (3.5 waste gas in refining), byproduct fuel (3.5 waste gas elsewhere, waste oils and materials), petroleum coke, black liquor (3.5 pulping liquor), biomass (3.5 wood chips and bark), hydrogen (3.2, 2022 only) and other (footprint years: the footprint's fuel total less every fuel above and the Table 5.4 fuels; 2002 and 2022: MECS other scaled by the nearest footprint year's ratio).  On footprint share rows, the footprint's own names. |
| `value` | all | PJ (share rows: fraction) | The energy, converted from the sources' TBtu (x 1.055056).  Footprint rows: the footprint figure.  table_5_4_est rows: Table 5.4 with withheld and `*` cells estimated, rounding reconciled and End Use Not Reported spread pro rata -- `note` shows each step from value_table.  Residual rows: the total of a fuel Table 5.4 does not cover (measured in Tables 3.2 / 3.5, coke net of blast furnace gas, 'other' on the footprint's basis), times share_of_fuel.  Rounded to 3 significant figures, but never past the units place. |
| `value_table` | table_5_4_est | PJ | What Table 5.4 prints for this sector, end use and fuel: the sum of the printed numbers over the sector's NAICS blocks (and over residual + distillate for fuel oil), `*` and `--` counting as 0.  Empty when any cell behind it is withheld, or nothing is printed but `*`.  Empty on other rows. |
| `unit` | all |  | PJ for every flow; `fraction` on footprint `share` rows (the source files label them %, but they hold fractions). |
| `share_of_type` | footprint | fraction | This end use's share of its energy type, within one sector and flow: of all the fuel (or electricity, or steam) put into end uses, the part going here.  Adds to 1 over end uses.  (Formerly end_use_by_type.) |
| `share_of_end_use` | footprint, table_5_4_est, residual | fraction | This row's share of what feeds its end use, within one sector.  Footprint rows: the split between fuel, electricity and steam (on import rows, of purchased energy).  table_5_4_est and residual rows: the split between individual fuels -- the end use's fuel mix -- pooling the Table 5.4 sources (electricity included) with the fuels Table 5.4 does not cover.  The two kinds of row form separate groups, each adding to 1; filter on data_source before summing.  Blank if the end use has no energy or a value is missing.  (Formerly type_by_end_use and end_use_by_fuel.) |
| `share_of_fuel` | table_5_4_est, residual | fraction | This end use's share of its fuel, within one sector: where the fuel goes (e.g. the part of chemicals' NGL used for onsite transportation).  Adds to 1 over end uses.  Residual rows: the inferred end-use profile shared by every non-Table-5.4 fuel.  (Formerly fuel_by_end_use.) |
| `share_of_heat` | table_5_4_est and residual rows for boilers and cogeneration | fraction | This fuel's share of the energy feeding boilers and cogeneration combined (onsite steam and CHP), within one sector; the same number on the boiler and the cogeneration row.  Pooled like share_of_end_use.  Adds to 1 over fuels.  (Formerly heat_by_fuel.) |
| `share_of_steam` | footprint steam output rows >= threshold | fraction | This source's share of the sector's onsite steam (boilers vs cogeneration).  (Formerly boiler_cogen_share.) |
| `efficiency` | footprint loss rows >= threshold | fraction | 1 - loss / energy delivered to the end use (steam distribution: / steam supply).  Blank below the threshold (default 10 TBtu, about 10.6 PJ).  2006 onsite-generation values are unusable (see the script docstring).  (Formerly misspelt efficency.) |
| `heat_to_power_ratio` | footprint cogeneration steam output >= threshold | ratio | Steam per unit of electricity from cogeneration (energy over energy). |
| `note` | table_5_4_est, residual | PJ | table_5_4_est: the steps from value_table to value, in PJ, e.g. `table: 1.06; +0.04 rounding balance; +0.2 End Use Not Reported (pro rata); = 1.3` (blank when value = value_table).  Residual rows: the fuel's measured total and how any gap in it was filled, and which footprint year its end-use split comes from, with a warning where that split is approximate.  (Formerly fuel_by_end_use_note.) |
| `data_source` | all |  | footprint (DOE energy-footprint CSV), table_5_4_est (MECS Table 5.4, gap-filled), residual (fuels Table 5.4 does not cover: named fuels measured in MECS Tables 3.2 / 3.5, 'other' balancing to the footprint's fuel total, split across end uses by footprint minus Table 5.4); table_5_4 (printed table as is) only with --no-estimates. |

## What `note` says

| step | meaning |
|---|---|
| `table: N` | the printed figure (value_table), in PJ.  All step amounts are PJ. |
| `table: withheld` | a cell behind this row is withheld (Q, W, D); `(other cells print N)` gives the printed part. |
| `table: <0.53 (*)` | only `*` (under 0.5 TBtu, 0.53 PJ) is printed. |
| `withheld cell(s) estimated (method)` | the first estimate of withheld cells: table_3_2 (printed in, or pinned by, Table 3.2), identity (the only unknown in a printed sum), group_prior / group_equal (a sum's remainder shared by the nearest survey's pattern, or equally), adjacent_year (the nearest survey's value). |
| `for * cells` | each `*` cell gets an equal slice, at most 0.5, of what its printed parent leaves unallocated. |
| `toward neighbouring surveys` | withheld cells pulled toward the nearest other survey's value as far as the printed numbers allow (weighted least squares). |
| `rounding balance` | printed and `*` cells moved within their rounding range (+-0.5, or 0-0.5 for `*`) so end uses add to subtotals and subtotals to the total. |
| `End Use Not Reported (pro rata)` | the sector's unreported energy spread over the reported end uses in proportion to their size. |
| `= N` | the result, equal to value. |
| `total N PJ from SOURCE (gaps estimated: ...); end-use split: ...` | residual rows: the fuel's total and its basis -- MECS Table 3.2 / 3.5 (any withheld or `*` part filled as for Table 5.4), coke net of blast furnace gas, or for 'other' the footprint balance or the scaled MECS figure -- and the footprint year whose footprint-minus-Table-5.4 residual gives its end-use split (its own, or for 2002, 2022 and empty residuals the nearest with one). |

## Reading the share columns on Table 5.4 and residual rows

* `share_of_fuel` -- down the end uses, for one fuel: where does this fuel go?
* `share_of_end_use` -- across the fuels, for one end use: what feeds this end use?
* `share_of_heat` -- across the fuels, for boilers + cogeneration together: what raises this sector's steam?
