# Unattended sanity-check run (2026-10-24)

Brad switched his computer off and asked for this run. Each remaining open item gets a review and a proposed fix. A Fable reviewer then decides APPLY, APPLY WITH CHANGES, or DO NOT APPLY, and approved fixes are applied, rebuilt, and checked. This file records every problem, proposal, verdict, and result, for Brad to review.

How it was run:
- The work was done in a cloud copy of the repo (a snapshot of ec56fc3, build inputs only, no source PDFs).
- Each batch is one commit with no output files. On Brad's return, the patches are applied to `C:\_dev\tech_data`, then the build runs and outputs are committed there.
- Every item that needs a source re-read or a ruling is listed under "For Brad" at the end.

## Batch B: energy totals that disagree with their carriers (S117, S120-S132)

All checks pass, and totals disagreeing with their carriers went from 10 to 3.

| Item | Problem | Proposal | Fable verdict | Result |
| - | - | - | - | - |
| S122, S125, S126, S128, S131 | Totals disagreed with their carriers | Close: the 2026-10-23/24 fixes already resolved them | Close | Closed |
| S120, S124, S129, S132 (and S117) | A MIDDEN card's total is the sum of its energy inputs, but its carriers never became energy-use rows, so the split borrowed another source's partial carriers | Parse each MIDDEN total's formula into carrier rows (`pipeline/middencarriers.py`) | Apply with changes: map every one of the 45 labels and fail on an unknown one; use deterministic ids; carrier rows go with their total; 'fuel gas' -> process-off-gas; HP004 retired | Applied. 396 MIDDEN totals now carry 793 carrier rows. The ATR (S120) splits from its own card: natural gas 0.30, heat 0.32, electricity 0.035 GJ/GJ |
| S123 | The CO2 compression total (1.88 GJ/t) came from MIDDEN whole-CCS cards | Rule out TC0017 and TC0481-0483 (capture-unit scope) | Apply | Total 0.38 GJ/t, from 31 electricity examples |
| S127 | Pardo 0.222 (net of process gases) against DOE 0.77 | Rule out Pardo | Do not apply: the 'net of process gases' note covers the whole table, Pardo agrees with Gielen, and DOE may include acid regeneration | No change; for Brad |
| S130 | Worrell's incremental +1.5 kWh/t was the split example | Rule out the increment | Apply | The variant takes the host's mix |
| S129 | Plasma-torch electricity split a thermal-pyrolysis total; Amin's reaction enthalpy counted as heat | Rule out plasma and Amin | Apply with changes: Amin only, because plasma (Monolith) is inside the archetype by its examples | Amin ruled out; TC0360's natural gas splits the total |
| S132 | MIDDEN TC0289 (steam-assisted, 0.90 GJ/t water) set the MVR total | Rule it out | Apply, reworded as another scope | Total 0.22 GJ/t from the MVR examples |
| S121 | E-crete 0.51 against activated slag cement 2.55 | No change; ask Brad | Refer, with a sharper question | For Brad |
| S124 | Direct-fired dryer: MIDDEN dairy cards are steam and hot-water heated; DOE dry milk 0.27 GJ/t looks 20x low | No change now | Flagged as a P-B1 side effect | Nine dairy cards set aside from dryer_direct-fired and its moderate variant pending a remap. Total 6.75 = electricity 1.14 + natural gas 5.6 |

Side effects of the MIDDEN carriers, found in review and fixed:
- **Pellet plant:** the MIDDEN IJmuiden card (BOF gas) became the fuel split, which cut combustion CO2 from 0.031 to 0.001 t/t. The card is ruled out, per Brad's 2026-10-23 mine-site ruling, and CO2 is back to 0.033.
- **Haber-Bosch loop:**
  - The card's hydrogen moves to feedstock.
  - The split no longer gives "the rest" to a feedstock carrier.
  - Where an archetype's only energy carrier has 3 or more examples, its pool sets a total that comes from fewer examples, whichever is larger. The total is 3.24 GJ/t. This also moved electricity-only devices by 0-6% (molten-oxide cell 14.2 to 13.3, low-temperature electrolyzer 1.36 to 1.32).
- **Alkylation:** the 70/30 refinery-gas/natural-gas judgements became non-zero beside MIDDEN's sourced refinery gas, so both were rejected.
- **Named fuels when fuel is pooled apart:** they are no longer split, since that put them in totals that leave the fuel out.
- **Variants:** host-copy and capture-energy rules no longer copy carriers the host pools apart. This is a pre-existing bug. For example, boiler capture had added the boiler's pooled-apart hydrogen 1.09 GJ/GJ, and its levelized cost including energy falls from 50.8 to 31.4.
- **Hydrogen-fired cracker cards:** three cards (TC0265, TC0410, TC0433) on the conventional cracker are set aside pending a hydrogen-fired variant.
- **Ruled-out totals:** a MIDDEN total that is ruled out, a twin, or a repeat now takes its carrier rows with it. One case: the coke plant's coking coal, 38.6 GJ/t, had come back as a carrier.
- **Ruled-out totals in examples:** an example whose own total is ruled out no longer gets a derived total.

Changes against the pre-batch build: 157 values moved more than 5%, mostly energy-use carriers. The list is in the run's working notes.

## Batch C: combustion CO2, emissions totals against their parts, gaps

All checks pass.

| Item | Problem | Proposal | Fable verdict | Result |
| - | - | - | - | - |
| S141, MCF013, NFM012 | The fuel-CO2 identity was skipped wherever process CO2 existed and on every reformer, gasifier and reactor, so fuel-burning archetypes had no combustion CO2 | Drop both conditions; guard against sourced totals | Apply with changes: keep gasifiers and ATRs excluded (feed oxidised in the process stream), guard combustion plus process, no zero rows from zero guesses, exclude the electrolytic-hydrogen shaft (charge coal already in process CO2) | 28 archetypes gain combustion CO2 (kiln_legacy 0.38, binder_carbonated 0.13, silicothermic 8.8, SMR methanol 0.56, upgrader 0.21, plastics pyrolysis 0.22 t/t). Four conflicts are listed in the build log and not written: GTL, electrolytic Haber-Bosch, hydrotreating lipids, methane pyrolysis. Five older exceedances are listed for review: furnace_oxy-fuel, calcium looping, tunnel kiln, reverberatory furnace, hydrogen DRI |
| OG004 | The fluid coker showed zero combustion CO2 although its coke burner heats the reactor | Add coke burned as energy use (1.6 GJ/m3) | Do not apply as drafted: the coke is own-produced (the FCC regenerator precedent) | Zero identity stopped. Drafted combustion CO2 of 0.17 t/m3 (0.12-0.24) for Brad to confirm |
| S140 leftover | Fuel cell: CO2 0 from a hydrogen cell beside natural-gas energy use | Rule out the hydrogen rows | Apply (plus two DEA zeros) | Combustion CO2 0.16 t/GJ |
| IS008 | The smelting-reduction total was below its parts | Rule out Material Economics and Gielen | Apply with changes: Material Economics only. Gielen's "excludes CO in off-gases" is the unit's scope-1 basis (the export gas is an output flow), and Hu's 2.17 combustion is gross of the export gas | Total 1.2 t/t. For Brad: Hu's combustion row against the net-of-export basis |
| NFM005 | Aluminium process CO2e is PFC only, on SAR GWPs or 1990s factors | For Brad | Agreed (a `pfc` target already exists) | For Brad |
| Gap | Biomass CHP had no energy use | CHP identity: 100 / heat efficiency | Apply with changes: estimated grade, 15-80% bound, not on anaerobic-digester CHP; use efficiency-chp for the total | 1.88 GJ biomass per GJ heat |
| Gap | Coal-to-methanol capture host has no CO2 row | Fall back to the CO2-eq total | Apply with a guard | The capture variant's net total is 2.82 t/t (captured stays the 2.2 judgement: no share) |
| Gap | Conversion archetypes lost sibling efficiencies | Identity: 100 / (energy use + energy in product) | Apply with changes; narrowed further to non-variants with a sourced energy use | Methane pyrolysis 45.6% (to hydrogen only). Transesterification units 83-94% (from 90.3 sibling estimates) |
| P-C9 | The hybrid furnace has no comparator | For Brad | Agreed; also its 68% electricity looks all-electric | For Brad |

Missed in review and left for Brad:
- reactor_integrated-upgrader counts natural gas "including hydrogen plant feed" and also a separate hydrogen feedstock, which double counts energy and cost.
- reactor_methane-pyrolysis blends the thermal and plasma routes.
