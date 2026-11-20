# Follow-up to the 2026-11-20 sanity check: Brad's rulings

Brad approved every recommendation in `run-summary.md` except S173, S179, and S184, which he asked about, and S176, S178, S181, and S185, which he changed. This file records what I applied and answers his three questions.

**State:** the build, `--check`, `check_manifest.py`, and `check_names.py` all pass. The internal-consistency check has 76 findings, all covered by earlier rulings. Nothing is committed.

## 1. Applied

| Item | What changed | Where |
| - | - | - |
| S175 | The capex and fixed O&M of whole cement plants on kiln_dry-precalciner are now on the clinker-line basis, × 0.725. The factor comes from IEAGHG 2008 Table 5-1: cement milling (20) and packing and loading (13) make up 33 of the 120 EUR M of equipment. There are 8 rebase rows: IEAGHG 2008 (both cases), Gardarsdottir 2019, Vattenfall 2018 (installed and total), and the IEA reference plant in ETSAP I03. I left out CSI-ECRA's reference plants and ECRA's scale ladder, because they do not say whether cement grinding is included. | `source-correction.csv` sc-228 to sc-235; `conversion-factor.csv` (one same-source factor, one ratio factor) |
| S177 | 10 fluidized-bed kiln examples moved to a new archetype, `kiln_fluidized-bed`. I made it a **reference** type so that your 2026-10-02 merge (C29) still holds for the model's choices. Change the type to alternative if you want the model to offer it. I excluded 10 cost rows: Bataille's two fluidized-bed rows, which share an example with the rotary kiln; the costs of three hydrogen-boiler examples; and the 290 MW captive power-plant boiler. The captive boiler's capacity stays in the pool. | `archetype.csv`, `source-example.csv`, `excluded-row.csv` |
| S178 | A figure that two sources give identically is now pooled once. The earlier source, then the higher-ranked one, keeps it. To avoid excluding a coincidence, a match counts only when one of these holds: the value has 4 or more significant digits; it has 3 and both sources print it in the same unit; or the two examples match on 3 or more parameters. Lifetimes, capacity factors, readiness levels, temperatures, and other conventionally round parameters count only on the third test. A pair you judge to be independent goes in `cross-source-distinct.csv`, which is empty for now. The rule caught 66 rows on 31 archetypes. | `normalise.py` (`_cross_source_repeats`); `cross-source-repeats.csv` in this folder |
| S172 | The wide view's `_low`/`_high` now show the 25th and 75th percentiles where 4 or more examples give a pooled median. Elsewhere they still show the full range. `archetype-parameter.csv` keeps low and high as the full range and adds `p25`/`p75`. The readme and the column notes explain the change. | `summarise.py`, `views.py`, `build.py`, `workbook.py` |
| S174 | A new `wide-pools` column names each parameter whose middle half spans more than 3× (capex, fixed and variable O&M, energy use, capacity). | `views.py` |
| S176 | Sourced levelized costs are off every wide view. The new `levelized-check.csv` has one row per source figure. Each row gives the calculated cost with and without energy, their ratio, a flag where the ratio falls outside 0.5-2, and the figure's basis read from its note: whether it includes feedstock or a selling price, a return, transport and storage, a CO2 price, or by-products not credited, and whether it is net removed, excludes energy, comes from market prices, or is a projection. The file has 390 rows; 54 are flagged. | `placement.py`, `levelized_check.py` |
| S180 | A new `fuel-basis` column names the fuel the energy use and emissions are on (natural gas for the fuel-fired boiler, biomass for the solid-fuel boiler). | `views.py` |
| S181 | Boilers repeated under the medium- and high-temperature bands carry a judged adjustment. It applies to the fuel-fired boiler, its efficient and capture variants, and the solid-fuel boiler. The multipliers are below. Energy use and emissions scale with 1/efficiency, and the calculated levelized costs are restated to match. This is in the workbook only: the CSVs and CIMS keep the pooled values, because CIMS has one steam node. | `heat-tier-adjustment.csv`; `bands.py` |
| S182 | kiln_legacy is relabelled "Older kiln routes (wet, semi-dry, long dry), existing stock". It gets `year-unavailable` 2000, so the model can keep it as existing stock but cannot build new ones. | `archetype.csv`, `fill-judgement.csv` |
| S185 | The blast furnace lifetime is now the campaign between relinings: 20 years (17-20), from van Geene 2024, with 17 from Seton. The efficiency variants and the capture variant follow at 20. | `central-choice.csv` |
| S183 | The workbook has a new service-requests sheet, banded by family. It shows, for example, the LC3 binder's 0.50 t clinker, 0.30 t calcined clay, and finish grinding. | `build.py` |
| S186 | Flows per kg, per gallon, or per m3 on archetypes measured in GJ are now put per GJ. The bridge uses the product's energy content (and its density for a volume) where the example states its product in that unit. Mass units other than kg and t, such as lb, are now converted too. 52.8% of flows are now normalized (it was 50%). | `normalise.py` |

**S181 multipliers**, relative to the pooled values (mostly low-pressure process boilers):

| Band | Efficiency | Capex | Fixed O&M |
| - | - | - | - |
| Medium temperature | × 0.988 (about −1 point) | × 1.10 | none |
| High temperature | × 0.963 (about −3 points) | × 1.35 | × 1.15 |

The fuel-fired boiler at high temperature, for example, shows efficiency 78.9% (81.9% pooled), capex 8.2 CAD per GJ/yr (6.1), and levelized cost with energy 15.8 CAD/GJ (14.6).

**Effects on central values** (`value-changes-after-rulings.csv`, all central values that moved more than 5%):

| What changed | Before | After | Cause |
| - | - | - | - |
| kiln_dry-precalciner capex | 492 | 333 | S175 rebase, S177, S178 |
| kiln_dry-precalciner capture variant capex | 703 | 633 | Follows the host |
| boiler_fuel-fired capex | 7.44 | 6.10 | S177 |
| boiler_fuel-fired fixed O&M | 0.185 | 0.123 | S177 |
| blast-furnace and variants, lifetime | 25 | 20 years | S185 |
| reactor_adipic-acid energy use | 24.9 | 18.5 GJ/t | S178 |
| 55 archetypes filled with the process-plant class lifetime | 23.75 | 20 years | Knock-on (below) |
| Variable O&M filled from the class ratio (about 40 archetypes) | | +19.5% | Knock-on: the ratio rose from 0.037 to 0.044, mainly because the kiln capex fell |
| Fixed O&M filled from cost ratios on heat and cement archetypes | | −6.5% and +9.4% | Same cause |

**A fragility worth knowing.** The class lifetime for process plants is the median of 147 archetypes, and it sits on a knife edge between 20 and 25 years. A single change moves every lifetime filled from it by 16%.
- If you want it stable, I can make it a fixed class value (for example 25 years, the common design life) or use the mean.
- I left it as it is.

## 2. Answers to your questions

### S173: Would any archetypes use their own size-scaling fit?

The test: 5 or more examples give both capex and capacity, capacities span 3× or more, the fit explains at least 30% of the variance (r² ≥ 0.3), and the exponent is below 1 (economies of scale). Nine archetypes pass:

| Archetype | Exponent | r² | Examples | Sources |
| - | - | - | - | - |
| compressor_co2-dehydration | 0.59 | 0.36 | 22 | 7 |
| steam-turbine_waste-heat | 0.69 | 0.89 | 6 | 4 |
| electrolyzer_solid-oxide | 0.79 | 0.58 | 7 | 4 |
| caster_continuous | 0.63 | 0.81 | 5 | 3 |
| gasifier_biomass-methanation | 0.52 | 0.86 | 5 | 3 |
| reactor_plastics-pyrolysis | 0.61 | 0.71 | 5 | 2 |
| solar-concentrator_point-focus | 0.80 | 0.70 | 10 | 1 (SAW 2023) |
| incinerator_waste-to-energy | 0.63 | 0.56 | 5 | 1 (Neuwahl 2019) |
| compressor_vapour-recovery | 0.36 | 1.00 | 5 | 1 (ICF 2015) |

- **The last three each rest on one source's size curve.** That curve is a sound scale law, but it shows only one source's view. I would require 2 or more sources before an archetype uses its own fit, which leaves the first six.
- **Excluded:** steam-turbine_condensing shows diseconomies of scale (exponent 1.71, r² 0.73), which points to mixed cost bases.
- **Of the scale-sensitive heat archetypes S173 was about, only the CO2 compressor has a usable fit.**
  - Boilers: fuel-fired 1.26, r² 0.14; solid-fuel 0.71, r² 0.29.
  - CHP: gas turbine 0.87, r² 0.19; engines 0.94.
  - Heat pumps: 0.95, r² 0.03.
  - These would all use the 0.7 default.
- **Decision for you:** whether to apply S173 on that basis. The Canadian reference sizes would come from GHGRP or CIEEDAC facility data, which I have not yet loaded for boilers.

### S179: Can we state both equipment-only and installed capex, or give a markup?

**Both for all or most archetypes: no.**
- Only 72 of about 1,600 pooled capex figures are equipment-only. They fall on 31 archetypes, and 26 of those also have installed examples.
- Only 41 examples, from 9 sources on 12 archetypes, print both bases for the same plant.

**A rough markup: yes.** Installed cost over equipment cost in those 41 pairs has a median of 2.4 (1.9-3.0 in the middle half; 1.5-8 overall), and it varies by equipment class:

| Equipment class | Installed over equipment | Sources |
| - | - | - |
| Gas-turbine CHP and steam turbines | 1.5-1.75 | Kranz 2001, DOE 2006 and 2012 |
| Industrial heat pumps | 1.5 | Element Energy 2018 |
| Electrolyzers | 1.9-3.0 | Lazard 2021, NREL 2026 |
| Boilers and electric heaters | 2.1-2.9 | Element Energy 2018. Its small electric boilers reach 4-8, which looks like a minimum installation charge on a small unit. |
| Grinding mills | 4.4-4.6 | Wang 2013 |
| Cement plant | 1.96 | IEAGHG 2008: 235 installed on 120 equipment |
| Cement plant | 1.45 | Vattenfall 2018: 210 on 145 |
| Biodiesel plant | 3.0 | Haas 2006: installation at 200% of equipment |

**A workable design:** a class table of installed-over-equipment ratios, sourced where pairs exist, otherwise a generic factor of about 2.5. It would do two things:
1. Bring equipment-only examples up to installed before pooling, graded "converted". This is S179 as proposed.
2. Add an `equipment-share` column (1/markup) to the wide view, so a reader can see a rough equipment-only cost for every archetype as capex × share.

I have not built this; it waits for your yes.

### S184: Would emissions-total be an identity for all archetypes now?

**No.** Today emissions-total (CO2) is:
- sourced on 56 archetypes;
- an identity on 49 (combustion plus process, or fixed to match the energy rows);
- estimated on 25;
- a guess on 19.

**Proposed scope.** The carbon-balance identity I proposed for coal methanol would cover only one class: conversion plants whose product holds part of the feed's carbon.
- That class includes the gasifiers (coal to methanol, ammonia, Fischer-Tropsch, methanation, and hydrogen), the autothermal reformers, and gas-to-liquids.
- The CO2 identity (fuel × emission factor) deliberately leaves these 12 archetypes out today, because carbon leaves in the product. So they have no consistency check.
- The balance would be the carbon in the feed and fuel, less the carbon in the product, less the CO2 captured.
- Two uses:
  - It would check every sourced total in the class.
  - It would replace a sourced total only where the two disagree by more than ±30%, as coal methanol does (5.02 against 2.9 t/t).
- Every other archetype would keep its sourced emissions-total, and the existing combustion identity would keep checking it.

**Decision for you:** whether to build the identity for that class and apply the ±30% replacement.

## 3. Second round (Brad, 2026-11-20 afternoon)

Brad approved S179 and asked for the S184 carbon-balance check on every archetype. He also asked whether a size-scaling fit needs two or more sources.

**State:** the build, `--check`, `check_manifest.py`, `check_names.py`, and the internal-consistency check (76 findings, all covered by earlier rulings) all pass. Nothing is committed.

### S173: does the fit need two or more sources?

**No.** What matters is whether the points are independent costings, not how many sources they come from. The three single-source fits differ:

- **SAW 2023, solar towers:** nine separate site designs (Pinjarra, the hybrid calciner, and others). These are independent engineering estimates, so the fit is good evidence (r² 0.70).
- **Neuwahl 2019, waste incineration:** the BREF's own cost table by plant size (100, 200, and 300 kt/yr, by flue-gas cleaning type). It is real scale evidence, but the scale law is the source's, and its r² of 0.56 partly reflects the flue-gas cases rather than size.
- **ICF 2015, vapour recovery:** five design sizes from one cost table. The fit is perfect (r² 1.00) because the table itself follows a curve. It describes ICF's scaling, not the spread of real units.

**Suggested rule.** An archetype uses its own fit when:
- its points are separate designs or plants (any number of sources);
- they meet the S173 tests (5 or more examples, capacities spanning 3× or more, r² of at least 0.3, exponent below 1); and
- the fit is not a single cost table's size curve.

On that rule, 7 of the 9 qualify: everything except Neuwahl and ICF, which would take the 0.7 default unless you prefer their tables. S173 itself is still not applied.

### S179: equipment-only capex put on the installed basis (applied)

**The factors.** `records/reference/installation-factor.csv` holds one installed-over-equipment factor per equipment lifetime class (`records/fill/equipment-class.csv`). Each factor is the median of the same-example pairs, taking one value per source and archetype:

| Class | Factor | Range | Sources |
| - | - | - | - |
| Electrochemical | 2.23 | 1.88-2.76 | Lazard 2021, NREL 2026 |
| Heat equipment | 2.60 | 1.48-6.00 | Element Energy 2018 |
| Power equipment | 1.75 | 1.66-1.75 | Kranz 2001, DOE 2006 and 2012 |
| Process plant | 3.00 | 1.45-4.64 | Vattenfall 2018, IEAGHG 2008, Haas 2006, Wang 2013 |
| Mobile equipment | 1.0 | (judgement) | Vehicles are bought ready to run |
| Default (rotating equipment, controls and programmes, wells and pipelines) | 2.2 | | Median of all the pairs |

**How the pipeline uses them** (`normalise.py`, `_equipment_to_installed`):
- 23 equipment-only rows whose example also prints an installed capex are pooled once, on the installed figure.
- 42 other equipment-only rows on 22 archetypes are multiplied by their class factor before pooling. They count as converted (external) and are shaded so.
- Mobile equipment stays as printed.
- A new wide-view column, `capex-equipment-share` (1/factor), gives a rough equipment-only cost as capex × share. For example: boiler 0.385, kiln 0.333, electrolyzer 0.448, haul truck 1.

**Capex central values that moved more than 5%** (`capex-changes-s179.csv`). Most are moderate:

| Archetype | Change |
| - | - |
| Electric boiler | +29% |
| Simple-cycle gas turbine | +13% |
| Solid-oxide electrolyzer | +19% |
| Fuel-cell CHP | +12% |
| Reduced-iron electric arc furnace | +17% |
| Air separation unit | +49% |
| Fuel-fired boiler | −10% (an equipment row now pooled once) |

**Large moves to look at.** These archetypes rest mostly on equipment-only figures, so the class factor dominates:

| Archetype | Before | After | Examples | Factor |
| - | - | - | - | - |
| Electric furnace | 1,111 | 2,634 | 4 | Process plant 3.0 |
| Reduced-emission completion | 240 | 721 | 1 | |
| Turboexpander | 139 | 306 | 3 | |
| Blowdown recovery | 230 | 455 | | |
| HPGR and SAG mills | | +63-65% | | Wang's own pairs |

The process-plant factor (3.0) rests partly on Wang's grinding mills (4.4-4.6). If it looks high for furnaces and separators, the furnace and separator equipment could move to the heat-equipment (2.6) or default (2.2) class in `equipment-class.csv`.

### S184: carbon-balance check on every archetype (applied as a check)

**What it does** (`pipeline/carbon_balance.py`; it writes `carbon-balance-check.csv` on every build and changes no value):
- It takes the fossil carbon going in: each carrier's energy use and feedstock × its CO2 factor, with biogenic carriers counting 0.
- It subtracts the carbon leaving in the product (`records/reference/product-carbon.csv`) and the CO2 captured. The product's carbon counts only against the fossil feedstock it comes from, so a crude-oil, coking-coal, or biomass feed outside the feedstock rows passes through outside the balance.
- It compares the CO2 total with what is left:
  - **above balance:** the total exceeds 1.3 × (balance + process CO2), plus 2% of the carbon in;
  - **below balance:** the total is under 0.7 × the balance.
- I added CO2 factors for methanol and ethane (NIST heats of combustion and stoichiometry), so the methanol and cracker feeds count.

**Result:** 409 archetypes consistent, 33 flagged, 17 not checked. The unchecked ones are:
- two by-product gases with no CO2 factor (process-off-gas, sinter-plant by-product gas);
- the naphtha feed of the fired steam cracker;
- archetypes whose energy use names no fuel.

The flags are in `carbon-balance-flags.csv`, grouped here by likely cause:

| Likely cause | Archetypes |
| - | - |
| **Double counting.** The total carries emissions that another node already counts. | `binder_blended-cement` (0.815 t/t, sourced: includes the clinker kiln's CO2, which also comes through its clinker service request); `steam-turbine_back-pressure` and its capture variant (0.08 t/GJ on a steam-driven turbine: the boiler's CO2) |
| **Total too high for the carbon going in** | `gasifier_coal-methanol` (5.02 against 2.9 t/t) and its capture variant (2.82 against 0.69); `coke-oven_by-product_efficiency-strong` (0.78 against 0.33); `refinery_alumina` (1.00 against 0.47, an identity); `calciner_gas-suspension` (1.34×); `melting-furnace_reverberatory-rotary` (1.44×); `mine_open-pit-oil-sands` (1.46×) |
| **Process carbon with no carrier.** Coke burn-off or carbonate is not counted in the process row. | `reactor_fluid-catalytic-cracking` (0.27 against 0.14), `reactor_fluid-coking`, `binder_hydrothermal-silicate`, `binder_sulphoaluminate` |
| **Biogenic CO2 recorded as fossil** | `gasifier_biomass-methanol` (0.76 t/t), `kiln_charcoal-retort` (1.95, estimated), probably `incinerator_waste-to-energy` (the fossil share of the waste has no carrier factor) |
| **Small sourced CO2 with no fuel carrier.** Probably purchased power (scope 2), or a missing natural-gas carrier. | `coating-line_electrolytic`, `pickling-line_acid`, `rolling-mill_cold`, `electrolysis-cell_inert-anode`, `electrolysis-cell_iron-electrowinning`, `electrolyzer_solid-oxide`, `reactor_chemical-depolymerization`, `fermenter_grain-dry-mill_ccs-concentrated` |
| **Variant total well below its host's** | `blast-furnace_efficiency-moderate` (0.44, estimated, against the host's 1.16, for a saving of a few percent); `steam-reformer_ammonia_efficiency-moderate` (0.56 against a balance of 1.82: the feed's process CO2 is missing); `steam-reformer_methane_efficiency-moderate` (0.027 against 0.065) |
| **Below balance as expected.** Carbon leaves in exported gas or a co-product. | `blast-furnace_biogenic-carbon` and `blast-furnace_top-gas-recycling` (blast-furnace gas exported), `reactor_methane-pyrolysis` (solid carbon), `shaft-furnace_hydrogen-direct-reduction` (carbon in the reduced iron), `reactor_gas-to-liquids`, `autothermal-reformer_hydrogen_ccs-concentrated` |

**Decision for you:** whether to fix the first five groups. The fixes:
- replace the coal-methanol totals with the carbon balance (2.9, and 0.69 with capture);
- take the clinker CO2 out of the blended-cement total;
- set the steam-driven turbine's CO2 to 0;
- move the biogenic CO2 to `emissions-biomass`;
- let the efficiency variants take the host's emissions scaled by the energy saving.

The last group needs no change.

## 5. Boiler size from GHGRP and MSAPR (Option 1)

Script: `boiler_size_ghgrp.py`; result: `boiler-size-ghgrp.csv`. The script divides each MSAPR sector's GHGRP fossil CO2 by the CO2 factor for natural gas (0.05064 t/GJ, HHV), the sector's MSAPR unit count, and 7,344 full-load hours (2016 RIAS: 90% load, 340 days a year).

Unit counts come from the 2016 MSAPR RIAS, Table 5 (819 units in the 2015 inventory, by sector), and the 2025 amendments RIAS (about 1,300 units in more than 300 facilities, with sector shares).

| Sector | Years | Units | Mean rated input, upper bound (MW) |
|---|---|---|---|
| Pulp and paper | 2015 / 2022–24 | 67 / 86 | 43.8 / 43.8 |
| Base metal smelting | 2015 | 50 | 22.7 |
| Potash | 2015 / 2022–24 | 39 / 27 | 26.8 / 59.2 |
| Chemicals | 2015 / 2022–24 | 60 / 91 | 114 / 84 |
| Oil sands and upstream oil and gas | 2015 / 2022–24 | 566 / 1,001 | 101 / 80 |

Limits:

- The public GHGRP file gives facility totals only, with no split by source category. Every figure is an upper bound: facility CO2 also covers kilns, dryers, engines, turbines, flares, and process CO2. MSAPR also excludes crackers, SMRs, and reheat furnaces, but their CO2 stays in the facility totals.
- The method gives a mean, not a median. Unit sizes skew right, so the typical unit is smaller.
- MSAPR covers only gas-fired units of at least 10.5 GJ/h (2.9 MW input). It says nothing about the many smaller boilers in food, light manufacturing, and buildings.
- The oil and gas, oil sands, and chemicals figures mix in so much non-boiler combustion that they don't make useful evidence. Pulp and paper (stable at about 44 MW across both periods), base metals, and potash (2015) are the cleanest. They point to a mean of about 20–45 MW input, or about 15–35 MW output at 82% efficiency, for large gas-fired industrial units.

Current `boiler_fuel-fired` reference capacity: 5 MW (median of 15 examples). Moving it to about 25 MW would lower scaled capex per unit of capacity by roughly (25/5)^-0.3 ≈ 0.62 under the 0.7 default exponent.

Ruling (Brad 2026-11-20): size boilers by sector. The database's reference size for `boiler_fuel-fired` and its variants is now 25 MW (`records/reference/reference-size.csv`, with a central choice on capacity). Light industry uses 5 MW in the export to CIMS only (`records/reference/sector-size.csv`; the build writes `archetype-sector-size.csv`, with capex x 1.621 at the 0.7 exponent). The three sources are registered in `source-details_reference.csv`, and the GHGRP CSV moved to `primary-sources/gov-can/eccc/`.

Effect: annual output follows the capacity (74,110 to 370,548 GJ a year at 47%). The pooled capex central stays at $6.10/GJ-per-yr: 12 of the 26 pooled examples carry a capacity and now scale to 25 MW, but the median falls on an example with no capacity. The low end moves from $0.96 to $0.82.

Rerun on stationary fuel combustion (eccc_2026_004, 2022-2023; `boiler-size-ghgrp-by-source.csv`). Dropping process, flaring, venting, transport, and waste CO2 barely moves the boiler-heavy sectors, because their CO2 is almost all combustion:

| Sector | Stationary share of facility CO2 | Mean rated input, upper bound (MW) |
|---|---|---|
| Pulp and paper | 98% | 44.6 |
| Base metal smelting (2015 unit count) | 66% | 13.8 |
| Potash | 99% | 58.2 |
| Chemicals | 85% | 66.7 |
| Oil sands and upstream oil and gas | 86% | 66.1 |

Stationary combustion still includes kilns, dryers, turbines, and engines, so these figures remain upper bounds. The cleanest sectors span about 14-45 MW input (about 11-37 MW output), so the 25 MW default stands.


## 6. Every example scales (Brad 2026-11-20, 13:45)

The capex median of `boiler_fuel-fired` did not move at 25 MW, because 14 of its 26 pooled examples state no size. `_scale_to_reference_size` now finds each example's own size in three steps:

1. **Its capacity rows.** These now include rows on the archetype's own product: the IEA 2025 EU electric boiler (3 MW, target heat) was being missed. Where a row gives only a range, the scaling uses its midpoint: DEA's district-heating gas boiler (0.5-10 MW) and NERA's large commercial boiler (350-3,600 kW).
2. **A stated or judged size** in `records/reference/example-size.csv`. Five sizes are stated by the source outside a capacity row: Element Energy's sheet bases (4, 43, 45, and 50 MW) and Van Geene's 20 MWth card. Three are judged: the MPP alumina-refinery boilers at 50 MW.
3. **Otherwise, the median own size of the archetype's sized examples.** The grade shows the size is assumed. This step covers the generic per-kW figures that carry no size: UK TIMES via Bataille, Rissman, CA ELP, Zühlsdorf, Saygin, and most Van Geene cards.

Of 464 scaled capex rows on the 18 archetypes, 8 take a stated or judged size, and 131 take the assumed size.

| Archetype | Capex before | After | Change |
|---|---|---|---|
| boiler_fuel-fired | 6.10 | 4.59 | -25% |
| boiler_fuel-fired_efficiency-moderate | 6.69 | 5.18 | -22% |
| boiler_fuel-fired_ccs-diffuse | 20.97 | 19.46 | -7% |
| boiler_electric | 7.28 | 6.84 | -6% |
| boiler_solid-fuel | 37.98 | 37.98 | 0% |
| heat-pump_industrial | 58.7 | 71.9 | +22% |
| heat-pump_very-high-temperature | 69.5 | 83.5 | +20% |
| steam-turbine_waste-heat | 152.9 | 180.7 | +18% |
| compressor_vapour-recovery | 750 | 609 | -19% |
| Other 9 archetypes | | | within 3% |

The light-industry boiler in `archetype-sector-size.csv` is now 7.45 (5 MW), against 4.59 at 25 MW.

Step 3 already applies to all 18 archetypes. Judged sizes (step 2) exist only for the boilers so far; the CHP, heat pump, and turbine archetypes are next.

Rulings (Brad 2026-11-20, 13:55): keep step 3 on all 18 archetypes. Exclude the CA ELP gas and electric boiler capex rows (tp-caelp_2024_001-0025, -0035): CA ELP reprints Energy Innovation (2022), whose figures are Rissman's, and Rissman is loaded directly (`excluded-row.csv`). Effect: boiler_fuel-fired capex 4.59 to 4.40 (its variants -0.20 each), boiler_electric 6.84 to 6.64, light-industry boiler in the export 7.12. CA ELP's thermal-storage row stays: Rissman has no thermal-storage figure, so it is not a repeat.

## 7. Scale screen of the other archetypes (Brad 2026-11-20, 14:05: approved)

The screen (`scale-screen-other-archetypes.csv`) fitted capex per unit against size on every other archetype with 4 or more sized capex examples spanning 3x or more. Eight archetypes were added to `scale-exponent.csv`. Six are process plants whose scale economies the source spread hides, at the 0.7 default: capture-unit_amine, capture-unit_chemical-solvent, steam-reformer_methane, combined-cycle, gasifier_coal-methanation, and distillation-column_atmospheric-vacuum. The two low-temperature electrolyzers take a judged 0.85, because they are built from repeated stacks. Left out:
- the oil and gas methane measures, whose "size" is methane avoided, not equipment;
- reactor_catalytic-n2o, whose fit reflects plant type;
- steam-turbine_condensing and process-improvement_low-emission-components, whose exponents above 1 point to mixed bases;
- the leak-detection programme, which already uses judged site sizes;
- the geothermal well, whose cost grows in proportion to size.

`example-size.csv` gains 32 sizes that the sources state outside a capacity row: 20 IEAGHG 2017 and other capture cases (CO2 captured a year), NCCP's 200 MW combined cycle, Aranda's 1 GW-input average (about 670 MW of SNG), Wallace's 3.2 MW truck electrolyzer, Philibert's 400 MW, and DOE's 500 MW project. Of 238 scaled capex rows on the eight archetypes, 32 take a stated size and 53 an assumed one.

| Archetype | Capex before | After | Change |
|---|---|---|---|
| capture-unit_amine (per t/yr) | 440.8 | 395.6 | -10% |
| capture-unit_chemical-solvent (per t/yr) | 338.0 | 358.6 | +6% |
| combined-cycle (and its efficient variant) | 55.0 | 44.6 | -19% |
| distillation-column_atmospheric-vacuum (per m3/yr) | 73.5 | 86.2 | +17% |
| electrolyzer_low-temperature | 104.1 | 109.0 | +5% |
| electrolyzer_low-temperature-central | 76.0 | 79.5 | +5% |
| gasifier_coal-methanation | 76.5 | 96.3 | +26% |
| steam-reformer_methane (and its efficient variant) | 22.5 | 21.3 | -5% |

The capture variants follow the amine add-on: combined-cycle_ccs-diffuse -10%, direct-heater_refinery_ccs-diffuse -7%, and the others within 4%. The coal-methanation gasifier rises because most of Aranda's Chinese plants (4.4-6.7 GW) are larger than the 2.2 GW reference, so scaling raises their cost per unit.
