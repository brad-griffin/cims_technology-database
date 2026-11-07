# Rulings made while fixing the 2026-11-07 consistency findings

Brad asked for every consistency problem to be fixed. Where a fix needed a decision, a Fable reviewer made it under Brad's rules, and Claude recorded it here for Brad to review. Each row says who decided: **Brad**, **Fable**, or **Claude** (a mechanical consequence, or an override of a Fable call that contradicted an earlier ruling of Brad's).

## Batch 1: stale exclusion keys (commit d6ca579)

- **Claude.** Re-keyed the 26 entries by matching each old row's example, parameter, target, value, and unit to its current id.
  - UKERC dryer rows 0169-0175 had three candidates. The old ids ran in blocks of four (combustion, process, captured, total), so each maps to the matching row of the same block (+20).
  - tp-duxon_2007_001-0003 now points at the same row as an existing entry (tp-ukerc_2013_001-0215). The two reasons are merged into one row.
- **Claude.** New guard: `reference/record-key.csv` holds what each keyed record id stands for, and the build fails if an id moves onto another row. Run `build --record-keys` after keying a new record.

## Batch 2: carriers (your decision of 2026-11-07)

**Brad's rules:**
1. The wide view shows one value for the most likely fuel, and the splits add up.
2. Alternatives go in a separate table outside the wide view, with a ranking where possible and the efficiency difference for purchased steam.
3. A note in the readme.
4. Most likely fuel = Canadian-typical for the technology, then the fuel most examples name.
5. Co-fired mixtures keep every fuel the process needs.

**Fable** made the per-archetype calls, which are in `data/technology_database/reference/fuel-choice.csv` (95 rows, with a reason for each). Variants with no row of their own take their host's call.

**Fable's least certain calls, for Brad to review first:**
- **Cement and lime kilns.** Cement kilns are on single coal, and lime kilns on single natural gas. Canadian cement plants co-fire coal and petroleum coke, so `mix` coal and petroleum coke is a defensible alternative.
- **boiler_oxy-fuel.** Single natural gas on Canadian practice, against three sourced coal examples (power-sector studies). Flip it to coal if you read this archetype as a coal CCS retrofit.
- **blast-furnace.** Coke plus PCI coal only. The stove and by-product gases (BFG, COG, BOFG) are self-generated, so they go to the alternatives table.
- **Refinery steam beside heat.** APART steam beside fired heat is added as stripping steam (delayed coking, hydroprocessing). APART heat beside steam is not added (alkylation, isomerization). The asymmetry is a judgement call.
- **shaft-furnace_hydrogen-direct-reduction.** Keeps the natural-gas guess as carburizing make-up beside hydrogen.
- **shaft-furnace_electrolytic-hydrogen.** Single biomass over coal (n2), because the fuel nearly equals the biomass value.
- **steam-turbine_back-pressure.** Biomass, on the pulp-mill fleet. A gas-fired industrial CHP reading would choose natural gas.
- **Bioliquid.** Kept as a co-fired fuel in HEFA, but dropped as a substitute in alkali transesterification.
- **refinery_deep-conversion.** Keeps petroleum coke as a process need (the fluid-coker burn).

**Overridden by Claude:** electric-arc-furnace_scrap-preheating. Fable proposed `mix` natural gas plus coal. That would have cut natural gas from 0.59 to about 0.32 GJ/t, against your 2026-11-06 own-carrier ruling (electricity 1.20, natural gas 0.59). It is kept at natural gas, and coal goes to the alternatives table.

**Mechanical rules (Claude), all in `pipeline/fuel_choice.py`:**
- **Named fuels that disagree with `fuel`.**
  - If `fuel` itself is a derived sum (identity, or n=0 pooled), it is raised to the named fuels.
  - Otherwise the named fuels are scaled to `fuel`.
  - steam-cracker_fired-tubular_efficiency-moderate follows the first case. Its fuel was a derived sum, so it rose to its named fuels (9.17 to 10.42 GJ/t, still below the host's 12.66), rather than Fable's rescale.
- **Level-1 carriers that disagree with the total.** This applies only where the carriers can be added (no fuel beside the steam it raised, and no two names for one heat).
  - A sourced total pooled from more examples than any carrier keeps its value, and the carriers scale up to it.
  - Otherwise the total becomes the carrier sum.
  - Changed: distillation-column_heat-integrated 2.62 to 1.36, melting-furnace_cupola 5.02 to 3.79, melting-furnace_rotary-oxy-fuel 3.50 to 2.80, grinding-mill_stirred 0.062 to 0.044, pickling-line_acid 0.222 to 0.21, and geothermal-well_direct-use (now 1.08, was marked not-applicable). electrolysis-cell_soderberg's electricity scales up to its 61 GJ/t total.
- **Zero-valued carrier guesses** (drafted carriers scaled to 0, or "could burn this" rows) leave the carriers. They go to the alternatives table as "listed possible fuel, no quantity".
- **Alternative fuels that were a share of a fleet mix** are shown at the wide view's fuel total: the same energy on that fuel alone. The share they had in the mix is in `comparison`.
- **Purchased steam or heat** shows the boiler fuel it needs at boiler_fuel-fired's pooled efficiency (82%). On-site firing shows the steam it raises at the same efficiency.

## Batch 3: emissions (Fable review round 1; `reference/emission-fix.csv`)

Each archetype's row in `emission-fix.csv` gives the action and the reason. The rules behind them:

- **M: capture variants (Fable: apply).**
  - Each variant takes its host's combustion and process rows. A sourced row of its own that the host lacks moves aside as as-sourced.
  - Net = gross - captured.
  - The hosts were made consistent first, so the variants inherit consistent values.
- **R1: identity replaces the pooled combustion CO2 (Fable: apply).** Applied to boiler_fuel-fired, furnace_reheating, fuel-cell_chp, combustion-turbine_chp, reciprocating-engine_chp, kiln_lime-rotary, kiln_lime-long-rotary, caster_continuous, electric-arc-furnace_scrap-preheating, reactor_ethanol-to-ethylene, and boiler_oxy-fuel. Efficient variants of these hosts take the identity on their own fuel.
  - **CHP:** all unit CO2 sits on the heat product, with no allocation to electricity. The pooled values were per GJ of total output.
  - **boiler_oxy-fuel:** captured = share-to-capture x gross. The sourced 0.086 exceeded the gross.
- **R2: combustion CO2 to 0 (Fable: apply).**
  - reactor_polymerization-extrusion (+strong): bought heat only (PB007).
  - reactor_catalytic-n2o: the 1.83 is kept as as-sourced. **Fable: it matches unabated nitric-acid N2O as CO2-eq. For Brad: should it become an N2O row?**
- **R3 (Fable: apply).** coke-oven_heat-recovery's 1.23 t/t moves to process CO2 (it comes from the coal feed).
- **R4: process = total - combustion (Fable: apply).**
  - FCC: 0.126, the regenerator coke burn.
  - Top-gas-recycling BF: 0.747. **For Brad: if the 0.79 source is a ULCOS case with storage, the total is already net.**
  - Blast furnace: process 0.588 to 0.697 (a judgement).
  - By-product coke oven: combustion = identity 0.443, process 0.332.
- **R5 (Fable: apply).** Smelting reduction: combustion = total - process = 1.162, net of the export gas (close to the coal identity of 1.19). **This closes IS008.**
- **R6: total = parts (Fable: apply).**
  - steam-reformer_methanol.
  - reactor_haber-bosch-electrolytic: combustion 0.074. **For Brad: Fable flags the 1.45 GJ/t gas row on an all-electric unit as suspect.**
  - reactor_hydrotreating-lipids.
  - boiler_solid-fuel: biomass, so fossil CO2 is 0. No biogenic factor is registered, so emissions-biomass is not written.
- **R7: accepted as scope-consistent, no change.**
  - Blast-furnace family reductant, EAF charge carbon, and SMR tail gas.
  - Steam cracker and MTO off-gas: no factor for process off-gas.
  - Gasifiers, ATR, and GTL: feed carbon carried in the total.
  - Urea's negative process CO2.
  - **reactor_fluid-coking's 0.17 draft is still pending Brad.**
- **Open items, decided by Fable:**
  - **steam-reformer_ammonia:** combustion = total - process = 0.68. The furnace burns loop purge gas too. **For Brad: the 16.4 GJ/t fuel row looks high.**
  - **shaft-furnace_hydrogen-direct-reduction:** accept 0.04, since the make-up gas carbon goes into the DRI.
  - **furnace_rotary-hearth-direct-reduction:** combustion = gas identity 0.173; process = coal reductant 1.26.
  - **kiln_oxy-fuel:** net = gross - captured = 0.042. The sourced net 0.094 (n8) is kept as as-sourced. **For Brad: look at this one first.**
- **Claude overrides of Fable:**
  - **fermenter_grain-dry-mill_ccs-concentrated.** Fable proposed a fossil net of -0.024. Claude kept your 2026-10-14 rule instead: captured biogenic CO2 comes off emissions-biomass. The host now carries emissions-biomass 0.032 t/GJ (a judgement from glucose-to-ethanol stoichiometry), and the variant captures 0.029 of it.
  - **Lime kilns now on natural gas.** For kiln_lime-rotary-preheater and kiln_lime-shaft, total = parts. Their totals were range midpoints from coal-fired kilns.

## Batch 4: efficiency and CHP (Fable review round 2; `reference/efficiency-fix.csv`)

- **E1: conversion archetypes.** feed = 100/efficiency - energy use, which gives the gross feed with conversion losses included. Where that would put the feed below 1 GJ/GJ, the efficiency is recomputed instead.
  - **Feed rows:** anaerobic digester 1.447, biomass methanation 1.468, grain dry mill 1.761 (no DDGS credit), and pyrolysis oil 1.279.
  - **Recomputed efficiencies:** ATR 75.8% (the 85.2% looks gas-only), biogas upgrading 89.9% (the 96.3% is methane recovery), alcohol-to-jet 80.1%, CO2-to-gasoline 68.7%, CO2-to-ethanol 50%, CO2-to-FT 69.8% (**it may be missing a hydrogen feed row**), and acid transesterification 79.1% (Claude, same rule).
  - **Lignocellulosic fermenter.** It keeps its 42.1% efficiency. Its 2.279 GJ/GJ biomass energy row is set aside as likely internal lignin burn, and the feed is 2.375. **For Brad: check that row's carrier.**
- **E2, E4: energy use = 100/efficiency.** Simple-cycle turbine 2.61 to 3.17, and turboexpander 1.17 to 1.04.
- **E3: motor_variable-speed (S154).** Energy 1.099 GJ per GJ shaft (motor efficiency 91%). The 0.82 system saving is kept as as-sourced. **For Brad: how should CIMS carry the system saving?**
- **E5: chiller_absorption.** Efficiency 62.5% (COP 0.63). Norman's 100% is kept as as-sourced.
- **E6: CHP (Fable replaced Claude's proposal).** The values are anchored on the pooled overall efficiency and HPR: electricity = overall/(1+HPR), heat = overall x HPR/(1+HPR), and energy per GJ heat = 100/heat efficiency.

  | Archetype | Electricity | Heat | Energy per GJ heat |
  | - | - | - | - |
  | Gas-turbine CHP | 33.3% | 40.7% | 3.10 to 2.46 |
  | Engine CHP | 33.3% | 43.3% | 3.17 to 2.31 |
  | Back-pressure turbine | 21.6% | 67.8% | 1.08 to 1.47 |
  | Fuel-cell CHP | 41.8% | 33.1% | |

  **For Brad: look at this one first.** Before this change, the gas turbine's energy row matched none of its pooled efficiencies.
- **E7: capture variants.** Efficiency net of capture = 100/(energy + feed), and the host keeps its own. Claude extended this from the energy-service variants to every capture variant with an efficiency (SMR, ATR, fermenter). Conversion variants use their host's feed. Examples: the boiler with capture 81.9% to 68.9%, and combined cycle with capture 49.2% to 41.7%.
- **E8: steam cracker.** Total = parts 0.598. The 0.748 (n12) is kept as as-sourced, and likely includes utility boilers or flaring.
- **E9: totals above their parts.**
  - **Process = total - combustion (17 archetypes with an evident process source):** BOF, BOF strong, indirect calciner, EAF, EAF reduced-iron, anode baking, hybrid and oxy-fuel glass furnaces, legacy cement kiln, pellet plant, plastics pyrolysis, the three refineries, sinter plant (+strong), and top-submerged lance.
  - **Left as they are and reported (no evident process source):** clay flash calciner, electrolytic coating line, the two direct-fired dryers, reverberatory furnace, methane pyrolysis, and coal-to-ammonia gasifier (R7).
- **E10.** The scrap-preheating EAF's combustion CO2 sits above its host's, because of your own-carrier ruling (gas replaces electricity). Accepted.
- **Size closure (Claude, your 2026-10-28 ruling).** Capacity x capacity factor = annual output on 15 archetypes. The capacity factor follows the output; where that would pass 100%, the capacity follows instead.

## Batch 5: the remaining findings (Fable review round 3)

- **F1: carrier lists.** Carriers with a non-zero energy row are appended to the archetype's declared carrier list in `records/archetype.csv` (248 additions on 194 archetypes).
  - Four carriers are not in `vocabulary/carrier.csv`, so they were not added: heat, charcoal, process-off-gas, and bioliquid. Adding them to the vocabulary is your call.
  - `carrier-list-additions.csv` lists every addition. Its `group` column separates additions whose energy row is sourced (133) from those whose row is a guess or derived (148). **For Brad: check the second group, since there the row may be the error rather than the list.**
  - One value moved because of this: delayed coking's electricity went from 0.082 to 0.140 GJ/m3. Listing electricity let one more example give a total, which changed the split example.
- **F2: bands spanning over 100x (25 archetypes).** Accepted, with no trimming rule. They are source spreads, not contradictions. The finding list shows the band, the central value, and n for each.
- **F3: missing core values.** Each is now a judgement in `fill-judgement.csv`, graded guess or proxy:
  - distillation-column_heat-pumped: capex 106 and fixed O&M 1.89 per t/yr (heat-integrated column plus industrial heat pump for 1.83 GJ/t of upgraded heat).
  - flotation-cell_potash: capex 1,200 and fixed O&M 43 per t K2O/yr (froth-flotation proxy at 4 t ore per t K2O). **For Brad: this is one of the most speculative drafts, with no Canadian source.**
  - separator_mine-water-treatment: capex 1.0 and fixed O&M 0.05 per m3/yr. **For Brad: also speculative, with no source.**
  - reactor_co2-to-methanol: lifetime 25 years (the class median; the sourced lower bound is kept as the band's low end).
  - steam-turbine_drive: steam 1.54 GJ per GJ shaft (65% isentropic-to-shaft).
  - **Accepted with no change:** fermenter_lignocellulosic-enzymatic has no energy row (the lignin burn covers it), and the no-abatement options are not-applicable by ruling.
- **F4.** Zero energy use is accepted by ruling (binders, no-abatement options, pipelines, magnesium cover gas).
- **F5: capture variants take their host's lifetime.** Seven changed. **For Brad: Fable flags the combined-cycle host's 22.5 years as short for an NGCC (25-30 is usual), so the host may be the value to fix.**
- **F6: levelized cost.** The check now compares a sourced levelized cost with the calculated cost both with and without feedstock (a liquefaction fee excludes the gas; a biodiesel cost includes the oil), and flags it only if it is far from both. **For Brad, each needing a source re-read:**
  - pipeline_hydrogen: S102.
  - reactor_biomass-flash-pyrolysis: 3,300 against 630. A per-t-oil against per-t-biomass mix explains at most 1.5x.
  - reactor_co2-to-dme: 2,827 against 838.
- **F7.** A 1% tolerance in the variant-against-host check absorbs fuel-share rounding.
