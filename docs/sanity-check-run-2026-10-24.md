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

## Batch D: the older open items (S87-S103, S68, S69, S110, S117)

All checks pass. Ten items were already resolved by earlier rounds and are closed after a re-check; the others were changed.

| Item | Problem | Proposal | Fable verdict | Result |
| - | - | - | - | - |
| S87 | Capex on two bases (rated against delivered); the electrolyzer's band ran 12-3,396 | The 2026-10-10 nameplate ruling settles the basis. Correct MIDDEN's electrolyzer cards, rule out Lazard's stack-only rows and DOE's net-of-tax-credit wind row | Apply with changes: all 26 Lazard stack rows; keep the ranges. The reviewer found the same slip on other MIDDEN cards | MIDDEN TC0365/TC0366 printed 20x their own per-MW comments (the 20 MW reference size), in capex and fixed O&M; corrected. The same reference-size slip is corrected on two heat-pump and three digester cards. Electrolyzer capex 64 (12.6-194). Wind 45-71 |
| S90 | Pneumatic-device capex priced a site at about CAD 81 million | Rule out ICF's per-pump rows; draft per facility from EPA 2006 over the Petrinex site | Apply | Capex 1.5 / 2.1 / 3.0 CAD per 1000-m3/yr (gas-driven, low-bleed, non-emitting; guesses). Levelized cost 0.6-1.0 CAD per 1000 m3 (was 425-702) |
| Batch C side effect | Gas-driven pneumatics got combustion CO2 from the gas they vent | Exclude them from the fuel-CO2 identity | Apply | No combustion CO2; their methane stays in process CH4 |
| S91 | Methane-control capacities looked small | The reading is right (methane avoided per installation per year), but a capacity factor was applied on top | Apply | Capacity factor 100% by definition on 11 methane controls. Flare 1,486 CAD/t CH4 (was 3,223); leak detection 1,900 (was 4,122) |
| S94 | Carriers lists named steam on a 900 degC calciner, solar on a converter, coke on a paste plant, and feedstock gases on a chemicals plant | Correct the four lists; split the converter's blower electricity; reject the zero rows | Apply with changes: the steel off-gas plant lists steam only, and its zero hydrogen row goes too | No total changes. Peirce-Smith combustion CO2 0.073 t/t (was 0.109) |
| S95 | Flash smelting capex 17,733 looked whole-plant | Rule out Schlesinger's figure as mine-to-cathode | Do not apply: Table 22.1 lists the smelter (with acid plant) apart from the mine, concentrator and refinery | No value change; the drafts' rationale corrected. For Brad |
| S103, S100 | A same-source capture add-on carried the source plant's CO2 captured per unit | Rebase it per t CO2 with the same source's captured CO2 | Apply with changes: the same example first, the guard after the rebase | 10 variants rebased: recovery boiler capex add-on 410 to 145, SMR concentrated 23.7 to 14.5, fuel-fired boiler 29.6 to 14.5. The lime kiln rises 448 to 603, because its source captures less than the database's host |
| S69 | Landfill methane collection held as a CO2 capture rate | A new collection-efficiency parameter | Apply with changes: use emissions-reduction-potential, as the other methane measures do | Remapped (75%, 35-90) |
| S102 | Calculated against sourced levelized cost, now that fuels are priced | Report | Keep open for the solar concentrators | Median 0.85 on 57 archetypes; 46 within 2x. The solar concentrators had a fired plant's 86% capacity factor; now 25% (guess), and their levelized cost is 17 and 43 against sourced 21 and 56. For Brad: the hydrogen pipeline's capex has no length basis (13x) |
| S93, S96-S99, S101, S110, S68, S117 | (see docs/sanity-check-list.csv) | Close | Agree | Closed. S117's three remaining disagreements are for Brad |

Side effects, all checked:
- Fixed O&M from the capex-ratio rule moved about 5% on a dozen archetypes, because the ratio pool changed with the corrected MIDDEN rows.
- The solar concentrators' annual output now comes from the end-use median (21,000 and 63,000 GJ), not capacity x factor, because a guessed factor ranks below an estimated output. Annual output sets only the stock count.
- Still listed in the build log, and unchanged by this batch: direct-heater_fuel-fired_efficiency-moderate 1.21 GJ/GJ above its host's 1.09.

## Batch E: host plants for set-aside incremental costs (S20-S67)

All checks pass. For each archetype with set-aside incremental costs, the question was whether to name the host plant or confirm there is none. The Fable reviewer first checked what a host does: the variant takes the host's size where the host has one, and an increment fills a cost only where the variant has none and the increment has a usable unit.

| Group | Items | Proposal | Fable verdict | Result |
| - | - | - | - | - |
| Stale | S24, S26, S34, S35, S40, S43, S44, S46, S51, S52, S54, S64; S50 | Close: merged or renamed since 2026-10-02 | Apply, and give S50 and two more successors a status | Closed |
| Conversions from another technology | S20, S23, S25, S28-S30, S32, S33, S36, S38, S39, S42, S45, S48, S49, S55-S63, S65-S67, and the successors | No host (status `off`): the rows price converting another plant (ingot to continuous casting, mercury to membrane, Soderberg to prebaked, and so on), or are plant totals with no size, or a generic capture cost per t CO2 | Apply; move S41 here | 36 archetypes `off`. Their rows stay in output/set-aside-host-cost.csv as retrofit costs |
| Same plant plus a measure | S31 ODC cell; motor_variable-speed | Name a host | Apply. Fable found that S31's increments have no unit, so the capex stays a judgement, and added the variable-speed drive | ODC: host membrane cell; capex judgement 2,280 (was 2,600); capacity 640 kt/yr from the host. Variable-speed drive: host standard motor; capex 22.6 (was a guess of 18) from McKane's drive increments |
| | S41 VRM | Host ball mill | Do not apply: a different mill, and the ball mill's guessed size would overwrite VRM's | `off` |
| | S53 low-energy refiner | Host TMP refiner | Apply | Reverted after the build: the UKERC saving rows rebuilt the total on the host (8.89 GJ/t) against Hekkert's 3.2 GJe/t. For Brad |
| | S21 calcined clay | Host Portland binder if the binders are grinding nodes | Do not apply; for Brad | `off`. The LC3 retrofit figures include the calciner (about 10-14 CAD/t-yr) against the judgement of 100 |
| | S27 | `off` | Do not apply: its host is already named (CH015) | Closed with the host kept |
| New: electrified and hydrogen-fuelled refinery cards (P-E4) | reactor_hydroprocessing, reactor_catalytic-reforming | Rule out the pooled rows of the MIDDEN electrified-furnace cards | Apply, plus the two hydrogen-as-fuel hydrotreating cards | Both archetypes' fixed O&M had come from these cards; it is now estimated. Catalytic-reforming electricity 0.066 (was 0.16). The hydrogen fuel no longer shows as hydroprocessing feedstock. Variants for Brad (S149) |
| Found after the build | the same two archetypes | Reject the 70/30 natural-gas name for their fuel: their MIDDEN cards name it refinery gas (the batch-B alkylation precedent) | (precedent) | Natural gas no longer priced beside refinery gas. Catalytic reforming incl. energy 39.8 (was 42.6) |
| New: incremental costs on abatement options (P-E5) | about 400 rows on methane controls and others | For Brad | Agree; a safe route exists (read incremental as the whole cost, as for capture), but it is a cost-basis ruling | S148 |

Side effects: the capex-ratio fixed O&M fell about 35% on about 40 oil-and-gas and refinery archetypes, because the two electrified-card O&M values had been in the ratio pool. That is a correct consequence, but it is large, so it is listed here.
