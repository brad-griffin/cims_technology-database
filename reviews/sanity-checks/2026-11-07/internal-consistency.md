# Internal consistency of each archetype (2026-11-07)

**Status after the fixes (same day):** every finding below is fixed or accepted by a ruling.

- **The rerun on the rebuilt database** (`internal-consistency-after.csv`) finds no open high, medium, or low findings. 77 rows remain, all marked `ruled`, each with the ruling that accepts it: 26 wide bands, 32 scope-explained combustion rows, 10 zero-energy rulings, 5 not-applicable cells, 3 levelized costs for a source re-read, and 1 variant above its host by your own-carrier ruling.
- **The fixes** are in five commits on `source-review-2026-09`: d6ca579, 0525c8e, d3f8c96, eebdec2, and the reviews commit.
- **The rulings and what to look at first** are in `rulings.md`.
- **The review packages** are regenerated from the fixed database (build label 2026-11-07).

The findings below are the original run, before the fixes.

This check tests whether each archetype's own values agree with each other. It reads the committed build (`data/processed_data/technology_database/archetype-parameter.csv` at 2ff4e88) and changes nothing. `internal_consistency.py` reruns it. `internal-consistency.csv` lists every finding (id, archetype, check, severity, value, expected, ratio, detail), and `misdirected-exclusions.csv` lists the stale exclusion keys.

**Result:** 417 findings on 252 of 537 archetypes. 40 are high, 111 medium, and 266 low. The high and medium findings fall on 118 archetypes. Most low findings are bookkeeping (carrier lists, carriers pooled apart, wide bands).

## What it checks

| Check | Rule | High | Med | Low |
| - | - | - | - | - |
| band-order, sign, bounds | low <= central <= high; no negative capex, size, or lifetime; percentages within 0-100; efficiency within 5-100% (heat pumps and chillers up to 700%) | 0 | 10 | 1 |
| size-identity | annual output = capacity x capacity factor (x 1,000 for kt/yr, x 31,536 for MW) | 0 | 7 | 4 |
| sec-carriers, fuel-split | carriers sum to the total; named fuels sum to `fuel` (rows pooled apart left out) | 7 | 6 | 4 |
| efficiency-vs-sec | on GJ archetypes, energy use + feedstock = 100 / efficiency | 8 | 8 | 6 |
| chp-hpr, chp-total | heat efficiency / electric efficiency = heat-to-power ratio; overall = heat + electricity | 0 | 8 | 0 |
| combustion-co2 | combustion CO2 = fossil fuel x its ECCC factor, within the factor's range (+10% / -20%) | 16 | 17 | 0 |
| combustion-co2-scope | the same, where reductant, feed, or exported gas can explain the gap | 0 | 34 | 0 |
| emissions-total, emissions-net | total >= combustion + process; on a capture variant, net = gross - captured, and captured <= gross | 9 | 14 | 0 |
| capture-share | captured / gross <= share-to-capture | 0 | 3 | 0 |
| levelized | stored calculated cost = (capex x CRF(8%) + fixed O&M) / CF + variable O&M; incl.-energy = that + carriers x price | 0 | 0 | 0 |
| levelized-vs-sourced | sourced levelized within 3x of the calculated one | 0 | 3 | 1 |
| variant-ccs, variant-efficient | variant against its host: same size, CCS costs and energy >= host, emissions <= host | 0 | 1 | 7 |
| carrier-list, pooled-apart, band-width, missing | bookkeeping | 0 | 0 | 243 |

The calculated levelized costs all reproduce from their inputs. Every capacity, capacity factor, and annual output agrees within 2% except the 11 listed. Every CCS variant carries its host's size.

## Main findings

### 0. Exclusions that now hit the wrong rows (root cause of three regressions)

Commit 2fc1d2b (2026-11-04, to-process intake and IEAGHG merge) renumbered some record ids, mostly UKERC rows and a few AEA, DECC, Duxon, and Premkumar rows. 26 entries in `reference/excluded-row.csv` predate that commit and still carry the old ids. They now rule out unrelated rows, and the rows they were written for are back in the pools. `misdirected-exclusions.csv` lists each one with the row it was meant for and that row's current id.

- **Back in the pools:**
  - dryer_steam-heated: combustion CO2, PB007.
  - fuel-cell_chp: the hydrogen cell's CO2 0, P-C3.
  - The steam-cracker capture and efficiency rows.
  - The combined-cycle moderate-variant cost rows.
  - binder_alkali-activated: fixed O&M.
  - motor_induction-standard_efficiency-moderate: lifetime.
- **Wrongly ruled out:**
  - oven_fuel-fired: lifetime.
  - reactor_nitric-acid: N2O.
  - binder_sulphoaluminate: process CO2.
  - steam-turbine_back-pressure: efficiency and heat-to-power ratio.
  - distillation-column: capacity.
  - gasifier_biomass-chp: capex and other rows.
  - capture-unit_amine, reactor_ethanol-to-ethylene, and binder_blended-cement: one row each.

The other id-keyed tables (source-correction, pair-saving, ccs-host-energy, emission-basis, and the rest) are not affected. A check that each keyed entry still matches its example id would stop this happening again.

### 1. Combustion CO2 that the energy rows cannot explain (16 high)

- **No fossil fuel in the energy rows, yet combustion CO2 is non-zero:**
  - dryer_steam-heated and both variants (0.15 t/t, UKERC). The PB007 exclusion now misses these rows (section 0).
  - reactor_polymerization-extrusion and its strong variant (0.08, electricity and bought heat only).
  - reactor_catalytic-n2o (1.83 t/t on an electric N2O unit).
  - coke-oven_heat-recovery (1.23 t/t; the coal it burns is not an energy row).
  - reactor_fluid-coking (the 0.17 draft from batch C, still awaiting your ruling).
- **CHP per-GJ basis:** combustion-turbine_chp (0.097 against 3.10 GJ gas x 0.0506 = 0.157 t/GJ heat), its capture variant, and reciprocating-engine_chp (0.11 against 0.161). The CO2 looks like it is per GJ of total output, while the energy is per GJ of heat.
- **Fuel row and CO2 disagree:** furnace_reheating and both variants (CO2 0.055 against gas 1.70 = 0.086), kiln_lime-rotary_efficiency-strong (0.31 against 0.20), and boiler_oxy-fuel (0.007 against 0.099).
- **Zero or missing CO2 beside a fossil fuel (medium):**
  - fuel-cell_chp (CO2 0 with gas 2.8 GJ/GJ). The P-C3 exclusion now misses this row too (section 0).
  - steam-turbine_back-pressure (gas 1.61).
  - capture-unit_advanced-solvent (gas 2.7).
  - The gasifiers and ATRs have no combustion CO2, by the batch C exclusion. The question is whether their process or total rows carry that carbon instead.

### 2. Emissions totals against their parts (9 high, 14 medium)

Most capture-variant gaps come from the host. A variant's net total is the host's total less captured CO2, so when the host's total disagrees with its own combustion + process, the variant inherits that gap. Examples:
- boiler_fuel-fired: total 0.066 against combustion 0.0695.
- smelting-vessel_smelting-reduction: 1.3 against 2.3 (the IS008 question).
- steam-reformer_methanol: 0.57 against 0.61.

Variant-specific findings:
- **reactor_fluid-catalytic-cracking_ccs-diffuse:** captures 0.246 t/t against gross 0.147. The rule took "the host's gross CO2" from a different row than the combustion row it shows.
- **electrolysis-cell_prebaked-anode_ccs-diffuse:** keeps its own sourced combustion CO2 (0.43, MPP) instead of the host's, so its gross and net disagree.
- **fermenter_grain-dry-mill_ccs-concentrated:** captures 0.029 against fossil gross 0.005. The captured CO2 is fermentation (biogenic) CO2 with no biogenic row beside it.
- **boiler_solid-fuel:** CO2-eq total 0 (UKERC, biogenic reading) beside fossil combustion CO2 0.113.

### 3. Named fuels and carriers that do not add up (7 high)

- **Named fuel at 0 beside a non-zero `fuel`:** caster_strip, rolling-mill_continuous-casting, reactor_ammonium-nitrate, and reactor_co2-to-methanol.
- **Named fuels well below `fuel`:** furnace_rotary-hearth-direct-reduction (10.9 against 17.6), gasifier_black-liquor (13.7 against 22.3), and melting-furnace_crucible-gas-fired (7.56 against 10.47; its combustion identity then uses neither).
- **Named fuels above `fuel`:** steam-cracker_fired-tubular_efficiency-moderate (11.7 against 9.2) and rolling-mill_thin-slab (gas 0.756 against fuel 0.151; the CO2 identity used the 0.151).
- **Total above its carriers:** grinding-mill_stirred (0.062 against electricity 0.044), electrolysis-cell_soderberg, melting-furnace_cupola, and melting-furnace_rotary-oxy-fuel.
- **Carriers pooled apart:** 46 archetypes show carriers that are not part of their total or fuel split, flagged as "pooled apart" in central-from. Examples are the blast furnace's HFO, BFG, and COG, and the lime kiln's oil 6.2 and HFO 5.1 beside a 6.45 fuel total. They are labelled, but a CIMS reader of the wide view could add them. Should they leave the wide view, or move to the sidecar?

### 4. Efficiency against energy use (8 high, 8 medium)

- **chiller_absorption:** efficiency 100% (Norman) against heat 1.6 GJ/GJ, a COP of about 0.6. The 2026-10-24 run had 71.5%.
- **Conversion archetypes whose efficiency counts a feedstock that has no row:** fermenter_grain-dry-mill and its variant, reactor_pyrolysis-oil, reactor_co2-to-ethanol, and separator_biogas-upgrading. Also gasifier_biomass-methanation and fermenter_lignocellulosic-enzymatic, where the feedstock row does not close the gap.
- **combustion-turbine_simple-cycle:** energy use 2.61 implies 38%, against an efficiency of 31.5%.
- **motor_variable-speed:** 0.82 GJ/GJ, above 100% (a system saving, the S154 issue).
- **turboexpander_pressure-let-down:** 1.17 against 96%.
- **CCS variants (low):** they keep the host's efficiency while their energy use includes capture. This follows the design, but the efficiency column then overstates them.

### 5. CHP streams (8 medium)

- On all four CHP archetypes, the overall efficiency is below heat + electricity. The gaps run from 4.8 points (combustion turbine) to 8.6 points (reciprocating engine).
- On all four, heat / electric efficiency is 5-15% off the heat-to-power ratio. For example, the back-pressure turbine has 2.70 against 3.13.
- Each stream was pooled separately, so the three no longer close.

### 6. Smaller items

- **Size (7 medium):** the fermenters, the HTL reactor, the amine capture unit, the electrorefinery, and the reciprocating engine are 5-9% off capacity x CF. The recovery boilers are 3% off.
- **Zero energy use (10 medium):** the binders, the no-abatement options, and the pipelines show zero by ruling (energy sits on other nodes). These are listed only so you can confirm.
- **Sourced against calculated levelized cost (3 medium):**
  - liquefaction-train_base-load: 133 against 913.
  - pipeline_hydrogen: 1.0 against 13 (the length-basis issue from S102).
  - reactor_biomass-flash-pyrolysis: 3,300 against 630.
- **Efficient variant above its host:** electric-arc-furnace_scrap-preheating has combustion CO2 0.058, against the host's 0.009.
- **CCS variant lifetimes (7 low):** they differ from their hosts, for example combined-cycle CCS at 40 years against the host's 22.5. The 2026-10-10 rule says a variant shares the host's underlying plant.

## Suggested order

1. Re-key the 26 misdirected exclusions (section 0) and add a build check that each keyed entry still matches its example id. This fixes the steam-heated dryer and fuel-cell regressions. The absorption chiller's 100% efficiency needs its own look.
2. Fix the host totals against their parts (section 2). That clears most of the capture-variant findings too.
3. Fix the zero named-fuel rows and the CHP per-GJ CO2 basis.
4. Rule on whether carriers pooled apart stay in the wide view.
