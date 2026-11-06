# Unattended sanity-check run (2026-10-24)

Brad switched his computer off and asked for this run. Each remaining open item gets a review and a proposed fix. A Fable reviewer then decides APPLY, APPLY WITH CHANGES, or DO NOT APPLY, and approved fixes are applied, rebuilt, and checked. This file records every problem, proposal, verdict, and result, for Brad to review.

How it was run:
- The work was done in a cloud copy of the repo (a snapshot of cb84706, build inputs only, no source PDFs).
- Each batch is one commit with no output files. On Brad's return, the patches are applied to `C:\_dev\tech_data`, then the build runs and outputs are committed there.
- Every item that needs a source re-read or a ruling is in "For Brad" below.

## Summary for Brad

**What was done.** Seven batches (B to H), each a commit in the cloud copy and a patch in the project (`claude/sanity-run-patches/0001` to `0007`, plus `0008` with this summary):
- **B:** MIDDEN totals carry their own carriers.
- **C:** combustion CO2 where fuel is burned.
- **D:** the older open items S87-S103.
- **E:** host plants for the set-aside incremental costs, S20-S67.
- **F:** the remaining high-severity findings of the 2026-10-23 review.
- **G:** what a triage of all 63 high findings left.
- **H:** the medium findings, plus a heating-value defect.

Every build passes all checks, and the totals that disagree with their carriers went from 10 to 3. Of the 2026-10-23 review's 63 high findings, 48 are resolved; the rest are rulings, listed below. Every change was proposed, reviewed by a Fable reviewer, applied only as the reviewer approved, and rebuilt and diffed.

**To apply on C:\_dev\tech_data** (on top of cb84706):
1. Run `git am --keep-cr 0001-*.patch ... 0008-*.patch` on the patches downloaded from the project. `--keep-cr` is needed because parameter-remap.csv has CRLF line endings.
2. Run `python database/harmonized/build.py`.
3. Commit the outputs.

The series was tested: it applies cleanly to the snapshot of cb84706 and reproduces the cloud copy exactly.

**Largest value changes to look at first:**
- Per-tonne numbers on GJ archetypes had a double HHV/LHV correction (batch H). Hydrogen per-tonne CO2 and costs rise 18%, ethanol 11%, methane products 11%.
- The pneumatic devices' capex is now per facility: 1.5-3.0 CAD per 1000 m3/yr, was 1,000-1,973.
- MIDDEN cards printed the reference plant's total as a per-capacity cost: electrolyzers 20x, heat pumps and digesters 2-5.5x. These are corrected as marked typos.
- Methane controls take capacity factor 100%, so their levelized costs fall 15-54%.
- Five energy-service archetypes take energy use = 100 / pooled efficiency. The fuel-fired boiler goes from 1.43 to 1.23.
- A capture add-on from the same source is rebased per t CO2. The recovery boiler's add-on falls from 410 to 145.
- Variants' fixed O&M follows the host's own ratio. Coke dry quenching goes from 29 to 52.

**For Brad: rulings and source re-reads** (all are rows of database/reviews/sanity-checks/sanity-check-list.csv):

| Item | Question |
| - | - |
| S21 | LC3 capex: the retrofit figures, about 10-14 CAD/t-yr, include the calciner. The judgement is 100 |
| S53 | Low-energy refiner: Hekkert's 3.2 GJe/t against the TMP host's 8.3; re-read before naming the host |
| S95 | Smelting vessels: whole smelter (17,733) or furnace section (2,660)? |
| S121 | Alkali-activated binder: E-crete 0.51 against activated slag 2.55; which scope? |
| S124 | Nine MIDDEN dairy spray-dryer cards (steam-heated), set aside pending a remap |
| S127 | Pickling line: Pardo 0.22 against DOE 0.77 (acid regeneration?) |
| S148 | Abatement options: read "incremental" cost as the option's whole cost? About 400 rows |
| S149 | Electrified and hydrogen-fired variants of refinery units and crackers (their MIDDEN cards are set aside) |
| S150 | H2 shaft furnace: Devlin's additive electricity rows are medianed (7.74 against 8.65); Rechberger's natural gas is unconverted |
| S151 | Pump station: per m3-km unit, and the pressure gradient |
| S152 | Hybrid glass furnace: Rehfeldt's flat-glass, 68%-electric case is the central; no host comparator (P-C9) |
| S153 | Engine CH4 and N2O are per GJ of fuel; they need an engine efficiency before they can be bridged |
| S154 | Motor moderate variant pinned at 97% by a system-level UKERC saving |
| S155 | HPCH004 (coal CFB on the gas-boiler capture variant), NFM003, PB003, IS010, and the high-solids boiler capex |
| S156 | Factors to source: OME3-5 heating value, moist wood-chip HHV/LHV, gasoline CO2 factor |
| S157 | OG008 (CERI's 0.83 t/m3 benchmark), PB016 (partial-capture designs), MCF019 (a heat-to-steam alias) |
| S158 | Code items and rulings from the medium triage |
| Batch C | Fluid coker combustion CO2, drafted at 0.17 t/m3; Hu's gross combustion on smelting reduction (IS008); aluminium PFC basis (NFM005); the integrated upgrader's double-counted hydrogen-plant gas; methane pyrolysis blends thermal and plasma routes |
| Batch B | S127 Pardo; S121 scope |

**Drafted values to confirm** (all graded guess, author claude-draft, 2026-10-24 in records/fill/fill-judgement.csv):
- pneumatic-device capex (3 rows);
- electric ceramic kiln energy 2.5 GJ/t;
- solar concentrators' capacity factor 25%;
- CO2-to-FT efficiency 56%;
- ODC cell capex 2,280;
- fluid coker combustion CO2 0.17;
- Peirce-Smith electricity 0.5 / oil 1.0.

**Not covered:** the 18 low-severity findings of the 2026-10-23 review.

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
| S93, S96-S99, S101, S110, S68, S117 | (see database/reviews/sanity-checks/sanity-check-list.csv) | Close | Agree | Closed. S117's three remaining disagreements are for Brad |

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

## Batch F: the remaining high-severity findings of the 2026-10-23 review

All checks pass. Ids are from database/reviews/sanity-checks/2026-10-23/review.csv.

| Finding | Problem | Proposal | Fable verdict | Result |
| - | - | - | - | - |
| IS005 | The hydrogen DR shaft's hydrogen (Rechberger 8.09 GJ/t) was split 57/43 hydrogen/natural gas on Otto's Circored mix, putting hydrogen below stoichiometry | Rule out Otto's Circored energy rows (a fluidized-bed process that fires gas for heat). A general fix (the split example's own fuels first) was prototyped and reverted: it made the cement kiln 100% coal and the tunnel kiln 100% gas | Apply; the reviewer corrected the expected total | Total 7.74 (Devlin), hydrogen 6.82, electricity 0.91. No natural gas, so combustion CO2 is not written. For Brad: S150 |
| MCF004 | The electric ceramic kiln had no energy use | Draft 1.6 GJ/t | Apply with changes: 2.5 (1.8-3.5), from WSP 2015's own +666% electricity on this archetype | 2.5 GJ/t (guess) |
| MCF005 | The hybrid furnace mixes flat and container glass | Rule out Worrell's flat-glass rows | Apply; the central does not move (Rehfeldt is top-ranked) | High end 7.56 to 6.61. For Brad with P-C9: S152 |
| NFM006 | The Bayer digester's capex looked mine-to-metal | Rule it out | Do not apply: Gielen Table 5.2 lists refining alone, per t aluminium; convert it instead | cf-alumina-per-aluminium on that example: capex 3,160 (was 6,030) |
| NFM007 | HPAL capex pooled per-metal and per-feed rows | Rule out the per-feed row | Apply | 21,673 (was 11,940) |
| NFM009 | The anode-baking high end was per t aluminium | Rule out ETSAP's row | Apply | Band 2.29-4.62 |
| PB001 | The drum debarker's capex was an aggregate UKTM row | Rule it out | Apply | 33 (was 691); log thawing 34 (was 693) |
| PB008 | The effluent digester (m3) took the biogas digester's size (GJ) | Host off, plus a guard | Apply with changes: a check that fails an active host on another product unit | Its own judgements stand: annual output 3 million m3 |
| PB010 | Alcohol-to-jet efficiency was a mass yield | Rule out Geleynse; add a heating-value stream | Apply | 90.3% (Tao, HHV) |
| OG005 | Pump-station drafts are per m3-km on an m3 archetype | For Brad | Agree | S151 |
| RX006 | Acid-gas removal on two product bases | Close: restated 2026-10-23 | Agree | Closed |

Found in the build check: reactor_co2-to-fischer-tropsch's sibling efficiency rose from 66% to 82% once alcohol-to-jet's efficiency was on an energy basis. Its siblings are biofuel upgrading units, so it is now excluded from that rule and drafted at 56% from its own energy use (1.78 GJ of electricity per GJ).

## Batch G: what the triage of the high-severity findings left

A triage of all 63 high-severity findings of the 2026-10-23 review against the current build found 48 resolved, 11 partly resolved and 4 open. This batch fixed the ones a data change could settle. All checks pass, and the build log's one "variant above host" warning is gone.

| Item | Problem | Proposal | Fable verdict | Result |
| - | - | - | - | - |
| NFM008 | The oxy-fuel melter's lifetime (6 years) was a refractory lining | Rule it out | Apply | 25 years (class) |
| HPCH006 | A variant's carrier drafts summed to the old total | Reject them | Apply with changes: also name its host, or nothing replaces them | Host named; coal 0.46, biomass 0.36, coke 0.15, tars 0.05 (sum 1.031); CO2 0.058 t/GJ |
| IS007 and 10 more | Variants' fixed O&M from a pooled ratio, far from their host's own | New rule: host's O&M x capex ratio | Apply | Coke dry quenching 28.9 to 51.9 (now above its host); lime strong 50 to 3.2; aromatics 34.6 to 2.0; ODC 73 to 299 |
| PB007 | Steam-heated dryer carried its boiler's CO2 (0.24 t/t) from UKERC | Rule it out | Apply, with the same card's CO2e total | 0 on the host and both variants |
| Batch B side effect | The zeolite dairy cards' cost rows were still pooled on the direct-fired dryer variant | Rule them out | Apply | Variant capex 67.4 (was 37.7, below its host) |
| P-G6 | Five energy-service archetypes' energy use contradicted their efficiency | 100 / pooled efficiency where the total rests on one or two examples and the efficiency on 15 or more | Apply: the scope reaches exactly these five, and the results agree with the carrier pools | Fuel-fired boiler 1.43 to 1.23; solid-fuel boiler 1.39 to 1.20; direct heater 1.09 to 1.28; condensing turbine 3.56 to 2.73; very-high-temperature heat pump 0.53 to 0.45 |
| RX001 | Engine CH4 and N2O per GJ of fuel, beside CO2 per GJ of shaft work | A one-token unit fix (Fable's suggestion) | (tried) | Reverted: it fixed the turbine but dropped the reciprocating engines' rows (no efficiency to bridge by). S153 |
| RX005, HPCH004, NFM003, PB003, IS010, high-solids boiler capex | | For Brad | Agree | S154, S155 |

Side effects:
- The pooled cost ratio moved about 7% (fixed O&M on about 90 archetypes), because the zeolite cards' O&M left the pool.
- The zero-combustion identity had been blocked by an as-sourced row on the heat pump; fixed.

## Batch H: the medium-severity findings

The triage of all 71 medium findings found 11 resolved, 11 partly resolved and 49 open. Each open one was classed A (a safe data fix), B (code) or C (a ruling). The tables are in database/reviews/sanity-checks/2026-10-24/medium-triage.md and, for the high findings, database/reviews/sanity-checks/2026-10-24/high-triage.md. All checks pass.

**A code defect (P-H1).** On per-GJ archetypes, a number per tonne of product had its HHV/LHV ratio applied twice: once by the HHV mass factor, then again. Per-tonne hydrogen emissions were 18% low. The fix is in `heating.kind`, and absolute sums on a mass capacity are covered too, per the Fable reviewer. It moved 84 values on 28 archetypes, each by exactly the fuel's ratio:
- autothermal reformer CO2 0.049 to 0.058 t/GJ;
- steam methane reformer CO2 0.057 to 0.063 t/GJ;
- methane-pyrolysis capex 50 to 59;
- annual outputs in GJ up 8-18%.

**Class-A fixes applied** (Fable checked each; the changes it asked for are included):

| Finding | Change | Result |
| - | - | - |
| CHEM005, CHEM008 | Ruled out a naphtha-route row on the gas reformer and a membranes-only capex | |
| CHEM011 | Same-source factor of 2.11 t HVC per t ethylene on Joosten's MTO datasheet | MTO total 12.5 to 7.3 GJ/t; combustion CO2 0.47 to 0.28 |
| CHEM013 | Ruled out IPCC text cells loaded as 2.0; remapped the olefins example | HB electrolytic abatement 209 to 415 |
| HPCH009 | Ruled out JRC CHP rows with an unknown denominator | Gas-turbine CHP CO2e 0.064 to 0.098 |
| HPCH013, HPCH015, HPCH016 | Negative capture totals out; biogenic CO2 to emissions-biomass; the chlor-alkali CHP bucket out | Combined-cycle moderate capex 138 to 56 |
| IS012, IS015 | Heat-to-steel shares out of efficiency; ETSAP $/t-yr to fixed O&M; de Beer operating totals out | Variable O&M's pooled ratio moved, so about 150 archetypes' variable O&M changed (BOF 11.9 to 3.6) |
| MCF007, MCF010, MCF012, MCF015 | A base-plant electricity share, steel-mill lime-plant rows, process-only MIDDEN emissions, and a direct-fired absorption chiller ruled out | Lime shaft kiln total CO2 1.10; absorption chiller 71.5% |
| MCF008, OG011, OG012, OG014, RX016 | Judgements that sat outside their totals rejected or restated; carriers corrected | HVAC heater natural gas 0.93 to 1.12 |
| NFM013, NFM014, OG007, OG009 | Another product, step or reprint ruled out | SAGD total 7.76 to 8.84 GJ/m3 |
| RX012, RX014 | Hosts named; the host-ratio O&M rule moved after the bucket capex | Reverberatory strong fixed O&M 60 to 154 |
| RX021 | Cooling tower carriers set to electricity | Combustion CO2 0 |

Found and fixed in the build checks:
- A ruled-out set-aside increment still fed the host-increment capex (HPCH016); it no longer does.
- A variant whose only fuel row is unnamed now takes its host's named-fuel shares. Naming the reverberatory variant's host had cost it its natural gas. The same rule now names fuel on four other variants (BOF strong, hot-mill moderate, precalciner strong, crude-unit strong).

Not applied:
- MCF019: a re-target is not a source error.
- CHEM012, HPCH014, RX021 engine: each needs a sourced factor (S156).
- OG008, PB016: Brad's call (S157).
- The class-B and class-C items: S158.
