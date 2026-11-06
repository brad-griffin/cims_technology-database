# Node alignment review (2026-11-05)

This review checks that the archetypes at each CIMS node compete on the same footing and match the node's scope in the CIMS hierarchy and the quarto sector chapters. It also checks that the sector notes agree with the data. It covers 291 nodes, 239 of them with two or more archetypes. Nothing in the database has been changed yet.

The findings are in `node-alignment-review_2026-11-05.csv`, one per row, with a blank `ruling` column for your decisions. There are 152 findings: 60 high, 63 medium, and 29 low priority. Each row gives the finding with its numbers, a proposed resolution that keeps the source values, the CIMS service request (where one is needed, with its quantity), and the sector-note change.

## Themes

Most findings fall under seven recurring problems. Five general rules would settle most of the high-priority rows at once.

| Theme | Rows | What goes wrong |
| - | - | - |
| H: supplied heat carried inside a unit | 14 | A unit archetype carries the fuel of its own boiler or fired heater, while the sector's steam or direct-heat node also supplies that heat. Examples: SAGD and cyclic steam (OS01), refinery process units (PR01), the Bayer digester (NF01), lumber kilns (LI02), chemicals listing both steam and the fuel that raised it (CH05), and gas-processing regeneration heat (NG02). |
| R: bought intermediate with no request | 22 | Something the archetype buys has no service request, so CIMS never charges for it. Examples: DRI for electric smelting (ST02), oxygen (ST08, NF14, IM11), anodes (NF04), hydrogen (OS08, BF05, CH08), alcohol for jet fuel (BF04), grain (BF01), and captured CO2 (CH14). |
| W: whole plant against unit chain | 25 | A whole plant competes with the units inside it, or a route appears at two levels. Examples: the H2-DRI plus EAF plant (ST01), the coal mines (CM01), casting routes that skip reheating and rolling (ST04), the waterless paper machine (PP01), self-contained binders (IM03), titanium pre-reduction (NF23), and the CO2 pipeline with its compressor (TR01). |
| N: node placement or unit | 31 | An archetype sits on the wrong node, or the products at one node are not the same product. |
| F: data defects | 34 | Carrier splits that do not sum to the total; whole-mill or route rows pooled into unit flows (ST09, PP04); per-t-pulp flows on per-t-solids archetypes (PP05); and unit errors. |
| C: cost and variant rule | 14 | A variant priced off a different plant rather than as host plus add-on; a missing host; a saving that is never recorded (LI05: the variable-speed drive has the same SEC as the standard motor, so CIMS can never choose it). |
| E: emissions placement | 7 | Coal seam methane on the mines and not on the methane-control service (CM02); SF6 on the magnesium routes and not at melt-cast (NF25); missing process CO2 (IM06); urea's CO2 use (CH07). |
| X: export or calibration checks | 5 | Capture energy that the 2026-10-10 rule places on the host must be stripped by the CIMS export. Hydrogen-node calibration must exclude captive hydrogen (HY04). Pulp and paper has no CCS node (PP06). |

## Proposed general rules

1. **Supplied heat is a request (theme H).** At any node whose sector has a steam or direct-heat service, a unit archetype holds no boiler or heater fuel. The fuel becomes a steam or direct-heat request: request = fuel × the generator efficiency (the same source's, or that of the sector's base boiler or heater). The source's fuel rows stay as examples, behind a ratio conversion factor, so no value is lost. This mirrors `process-heat-efficiency.csv` and needs a new reference table, `supplied-heat-request.csv` (archetype, carrier, efficiency, request node, grade). It applies the existing integral-versus-supplied heat rule to all sectors. Downhole oxy-combustion, and nodes whose sector has no heat service (crude-oil upgrading), keep their fuel.
2. **Bought intermediates are requests (theme R).** An intermediate made at another CIMS node is held as a flow per unit of product and exported as a service request; it is never left out and never held as an energy carrier. Each request gets one line in the sector note.
3. **One framing per route (theme W).** Where a whole plant competes with the units inside it, the whole plant becomes a reference archetype and keeps its values, and its unit-scope parts go to the unit archetypes as examples where the source splits them. A route that skips a downstream step instead gets a zero (or negative) request for that step, as with the casting routes and the waterless paper machine. Such a route stays an option only where the hierarchy has no unit chain to compete with it.
4. **Hydrogen on site or bought (CH01, CH02, BF03).** Pick one footing for the electrolytic and CO2-to-X routes. The CIMS hydrogen chapter's on-site rule supports whole plants with their own electrolysers, and the ammonia examples are already on that footing. The CO2-to-methanol examples are mixed.
5. **Flows come from the same scope as the parameters (theme F).** Exclude route-level, whole-mill, and "unit-baseline-output" rows from unit-archetype flows, and normalise flow units before pooling.

## Decisions needed before any change

- Rules 1 to 5: adopt as written, or amend.
- Hydrogen footing (rule 4): (A) whole plant with on-site electrolysis, or (B) buy hydrogen, with the electrolyser subtracted from the examples.
- Cement and lime capture (IM02): (A) capture-ready lines that request transport and storage only, or (B) a new `industrial-minerals.service.ccs.concentrated` node.
- Hierarchy requests the findings imply: `pulp-and-paper.service.ccs.diffuse`, `industrial-minerals.service.oxygen`, `direct-air-capture.service.heat`, `industrial-minerals.product.glass.mineral-wool`, an anode-paste node under aluminum anode production, and possibly a distribution fugitive node.

## Sector notes

Every row that changes what a sector note says has its new wording in `sector-note-change`. Notes that contradict the data now are CH01, MN04, IM01, IM03, NF02, PP02, PP09, and BF01. The notes would change in `review-packages/scripts/docx_sector_notes*.py` once the rulings are in, and the packages would then be rebuilt.

## Rulings and implementation (2026-11-05)

Brad approved rules 1 to 5, with three changes. Rule 1 holds only where the sector's steam node offers the generation options the unit's sources describe. Rule 3 also adds major components the chain lacks and validates each chain against its reference plant. Rule 4 uses the footing the sources describe, which is on-site electrolysis. For cement and lime capture he chose option B. The `ruling` and `implemented` columns of the CSV record, row by row, what was decided and what was done; 73 rows fall under a ruling and 79 are still pending.

New in the database:

- `records/reference/supplied-heat.csv` and `pipeline/suppliedheat.py`: 15 archetypes now buy steam or fired heat.
- `records/reference/service-request.csv`: 112 requests, written to `output/archetype-service-request.csv`.
- `records/reference/chain-validation.csv` and `pipeline/chainvalidation.py`: 16 chains, written to `output/chain-validation.csv`.
- `records/reference/excluded-flow.csv`: flow rows ruled out or rebased. Flow volumes of oxygen, nitrogen, CO2, hydrogen, and air are now converted to tonnes by density.
- Hierarchy nodes added: pulp-and-paper ccs and ccs.diffuse, industrial-minerals ccs.concentrated and oxygen, direct-air-capture heat, and natural-gas distribution fugitive. Mineral wool and aluminum anode paste got no node, because the data do not support one: the cupola has two examples and no competing melter, and the paste plant has no sourced values. Both are now reference archetypes.

## Open for Brad (updated after the third round, 2026-11-05)

- **Methanol capital cost.** RESOLVED in the fourth round, below. DEA 2026 (CO2 and hydrogen to methanol) and Schemme 2020 give loop costs per kW. Ren 2009 gives fossil and biomass plant costs per t of methanol a year. All are ruled out only because the build has no factor to convert their units. Registering a methanol energy-content factor would restore them.
- **Acid-plant requests.** RESOLVED in the fourth round, below. One request row serves the copper, lead and nickel nodes, and copper's value is not a fair proxy for the other two:

  | Metal | H2SO4 per t metal | Copper proxy |
  | - | - | - |
  | Copper | about 3 t | matches |
  | Lead | about 0.5 t | about 6 times too high |
  | Nickel (Sudbury ores) | about 6-9 t | 2-3 times too low |

  A per-node column in `service-request.csv` would fix this.
- **Pulp and paper steps.** RESOLVED in the fourth round, below. Washing and causticizing need no archetypes: they use little energy, have no competing technologies, and their capital is now in the kraft share. Stock preparation (refining) is worth one if CIMS will choose between refiner technologies, but only one source (UKERC) has it.
- **Heat-pump dryer.** RESOLVED in the fourth round, below. The energy is plausible but optimistic: a coefficient of performance of 3 and a 68% steam saving are at the top of reported ranges. The capital likely understates integration with the hood exhaust. Suggested ranges: steam 1.26 (1.26-2.4) GJ/t and capital 1,500 (1,500-1,750) per t-yr.
- **Titanium slag.** RESOLVED in the fourth round, below. Keep it. Rio Tinto Fer et Titane in Sorel-Tracy emitted about 0.96 Mt CO2e in 2021 (its 670 kt BlueSmelting cut is 70% of that), but the data are thin: the base furnace has no examples. Adding RTFT and BlueSmelting sources would fill it.
- **Still open from before:** capture units whose sources may already include compression; methanol capital resting on one example. The 79 pending findings were applied on 2026-11-05 (fifth round, below).

Settled in the third round:

- Direct-contact steam generation is set aside.
- Hydrogen reaches fired heaters and boilers through the fuel blend.
- CO2 for use comes from the capture node.
- The MIDDEN caustic evaporators are kept: 1.0-1.4 GJ of steam per t of water across 5 to 2 effects fits the latent heat of 2.26 GJ/t. The cell sources' implied 0.4 GJ/t is the less likely figure.
- The biomass-to-olefins reference plant is left as it is. Its two sources are thinner than the chain's, it has no capital cost, and it serves no node.

## Follow-up (2026-11-05)

Brad asked for these changes, and all are applied:

- **Capital the chains miss** is added back as a capital share on each route's own units, using `records/reference/capital-share.csv` and `pipeline/capitalshare.py`. The multipliers:

  | Units | Multiplier |
  | - | - |
  | Refining and upgrading process units | x 2.39 |
  | Oil sands extraction and froth treatment | x 2.51 |
  | Kraft steps | x 1.63 |
  | Paper machines | x 1.53 |
  | Hydrogen direct reduction | x 1.5 |

  Chain capital is now within about 5% of each reference plant, except the conversion refinery, which comes out 1.46 times its own because one multiplier covers all three refineries.
- **New nodes:** `crude-oil.service.direct-heat`, served by the refinery heaters, and a CO2 compression node under each pipeline route. `pipeline_co2` asks the compression node for 1 t per t of CO2 it carries.
- **Blast furnaces** buy a Canadian burden: 1.45 t of pellets and 0.1 t of sinter per t of iron (a judgement).
- **The electric arc furnace is split by charge:**
  - `electric-arc-furnace`, mostly scrap: 2.12 GJ/t, capital 235.
  - `electric-arc-furnace_reduced-iron-charge`: 3.60 GJ/t, capital 355; it buys 1.0 t of reduced iron per t of steel.

## Third round (2026-11-05)

- **Oxy-fuel and calcium-looping kilns** buy oxygen: 0.248 and 0.376 t per t of clinker, from Voldsund 2019 Tables 8 and 13.
  - Their air separation unit's power is off their electricity (0.22 and 0.31 GJ per t of clinker).
  - A judged capital share takes the air separation and CO2 purification units off their capital: x 0.81 for oxy-fuel (647 to 524) and x 0.873 for calcium looping (851 to 743).
  - The double count was moderate, about 10-15% of the kilns' capital.
- **Data defects fixed:**
  - The stray hydrogen carrier on the fuel-fired boiler and heater (Element Energy hydrogen-firing rows) is ruled out.
  - UKERC per-t-cement flows on the cement kilns and MIDDEN composition flows on the grinding mills are ruled out.
  - Hekkert's whole-sawmill O&M, mostly labour, is ruled out on the lumber kiln. That was the source of the lumber kiln's operating cost of 459.7 against a capital cost of 70.
- **The CIMS quarto chapters now match the rulings:** 12 files, plus a changelog entry.

## Fourth round (2026-11-05)

- **Coal extraction step:** the detailed chain's extraction node now has `mine_open-pit-coal-excavation` (0.12 GJ/t coal: electricity 0.06 and diesel 0.06; capital 40) and `mine_underground-coal-cutting` (0.03 GJ/t of electricity; capital 120). Both are judgements, based on BCS 2007's shares for drilling, digging, and haulage. The open-pit chain now matches the whole mine on energy (ratio 1.00) and comes to 0.92 of its capital. The underground chain uses 1.41 times the whole mine's energy, because the ventilation fans carry metal-mine values, and comes to 0.84 of its capital.
- **Methanol:** the methanol energy content now applies to the methanol loop and the coal-to-methanol plant, and units of t of a product per year read as the archetype's own tonne. Capital costs that now count:
  - Methanol loop: DEA 2026 (1,612) and Schemme 2020 (282) join van Geene, for 3 examples with a central value of 1,140.
  - Ren 2009 plant costs: reformer methanol 763 (n=4), coal methanol 1,602 (n=2), and biomass methanol 1,297.
  - The whole CO2-to-methanol plant still has one capital example (Bazzanella). It cannot be assembled from DEA, because the loop and the electrolysers are in different currency years. The chain check (loop plus electrolyser) is the cross-check.
- **Acid-plant requests by metal** (new `at-node` column), in t H2SO4 per t metal:

  | Metal | Smelter | Converter |
  | - | - | - |
  | Copper | 2.0 | 0.9 |
  | Lead | 0.45 | none |
  | Nickel | 5.0 | 2.5 |

- **Titanium slag:** I registered Bisaka 2016 (SAIMM) and Song 2025 (Results in Engineering) as not held; both are on the to-get list to download and verify. New values:
  - Open-arc DC furnace: 11.7 GJ/t (electricity 8.7, sourced).
  - Submerged-arc furnace: electricity 9.17 (sourced).
  - The pre-reduction route now rests on titanium data: 10.2 GJ/t, of which 4.2 is electricity (sourced) and 6.0 coal (judgement). It drops the ferrochrome rows.
  - The efficiency variant keeps its own judgement (10.2), because the bucket rule skips it.
- **Pulp and paper:** no archetypes for washing, causticizing, or stock preparation. Their capital stays in the kraft (x 1.63) and paper-machine (x 1.53) shares.
- **Heat-pump dryer:** ranges widened to steam 1.26-2.4 GJ/t and capital 1,440-1,750.
- **CIMS docs:** the coal-mining chapter's extraction TODO now describes the two new technologies.

## Titanium intake (2026-11-05)

Brad placed four titanium files in to-process. Everything else on the to-get list (19 rows, including the 2012 30 MVA DC smelter paper) moved to unavailable.csv as "user: assume unavailable"; to-get.csv is now empty.

- **Bisaka 2016** (SAIMM, held): every value read online matched the PDF. Notes and citation are now confirmed.
- **Song 2025** (Results in Engineering, CC BY-NC-ND, held): re-extracted from Table 12. The Pangang 25.5 MVA furnace is AC shielded-arc, so the raw-concentrate rows stay on the submerged-arc furnace:
  - batch feeding 2,547 kWh/t slag and 0.21 t coke;
  - continuous feeding 2,252 kWh/t and 0.19 t coke;
  - oxidized pellets 2,219 kWh/t and 0.22 t coke, kept as a record only (the pellet roast is outside the figure).
  - Coke is loaded as energy at 28.83 GJ/t (StatCan), as the ferroalloy rows carry their reductant.
- **Pistorius c. 2009** (University of Pretoria manuscript, new source `pistorius_2009_001`): typical DC ilmenite smelter about 1,000 kWh/t ilmenite, put per t slag through `cf-slag-per-ilmenite`. Table 5 enthalpies and 89 kg C/t ilmenite are in other-values. The manuscript prints no year or venue.
- **Rio Tinto 2022 release:** background only (RTFT about 0.96 Mt CO2e in 2021; BlueSmelting claimed 95% lower GHG; 40 kt/yr ilmenite demonstration plant).

Values now, per t titania slag:

| Archetype | Before | Now |
| - | - | - |
| Submerged-arc furnace | 12.5 GJ/t: electricity 9.17 (n=1), coke 3.0 (judgement) | 15.2 GJ/t: electricity 9.17 (8.19-9.17), coke 6.05 (5.40-6.05), both sourced, n=2 |
| Open-arc DC furnace | 11.7 GJ/t: electricity 8.7 (n=2), coke 3.0 (judgement) | 14.3 GJ/t: electricity 8.7 (n=3), coke 5.56 (5.1-6.1, judgement from Pistorius' 89 kg C/t ilmenite) |
| Submerged-arc, efficiency variant | 10.2 GJ/t | 12.9 GJ/t (judgement restated: host less 2-3 GJ/t of off-gas) |
| Submerged-arc, biogenic carbon | 13.0 GJ/t | 16.1 GJ/t (judgement restated: host with coke replaced by 10% more biocarbon) |

The reductant was the gap: both measured sources give about 0.2 t coke per t slag, twice the 0.1 t the old judgements assumed. Combustion CO2 on the submerged-arc furnace rises to 0.67 t/t slag. Capital is still judgement on every titanium archetype.

Open: the variant split keeps the host's electricity-to-coke proportions, so the biogenic-carbon variant shows slightly more electricity than its host (9.5 against 9.2 GJ/t). Brad accepted this, and judgement-only titanium capital, as they stand (2026-11-05).

## Fifth round: the pending findings (2026-11-05)

Brad asked to apply the 80 findings left blank in the `implemented` column, as suggested or by judgement, adding as few archetypes and nodes as possible. Two had his comments: CH07 (approved; check whether CIMS allows negative process emissions) and PP02 (build a judgement electric paper dryer). The `implemented` column now says what was done for each. 16 rows start "CHANGED FROM SUGGESTION".

**Carriers.** `biomass-solid` now pools with `biomass` (`normalise.CARRIER_ALIAS`): CIMS has one solid biomass fuel, and the commodity vocabulary already mapped it there.

**New archetypes (2):** `dryer_electric-paper` (PP02: 3.6 GJ/t electricity, rather than the suggested 2.0, because direct electric drying cannot go below the latent heat; capital 1,520) and `calciner_gypsum` (IM12: 1.05 GJ/t). No new nodes.

**Reference archetypes (4):** the brine lithium adsorber, hydrogen storage caverns, hydrogen blending, and PET depolymerization.

**Restated per unit handled:**
- Coal-mine methane options per t CH4 (no abatement 1 t/t, VAM 0.31, drainage 0.61). The detailed-chain excavation and cutting request 0.00021 and 0.0072 t CH4 per t coal; the whole mines on simplified extraction keep their own CH4.
- N2O abatement per t N2O. Nitric and adipic acid request 0.0085 and 0.30 t N2O; their own N2O rows are excluded.

**CIMS check (CH07).** `CIMS/emissions.py` takes technology emissions as given, with no floor, so urea's negative process CO2 (-0.695 t/t) flows into the emissions cost and net emissions. A negative service request carries no emissions, because emissions are only added for requests above zero, so the credit has to sit on the technology. No code change is needed for this; crediting biogenic anode carbon at the aluminium cell (NF06) would need one.

**Not done (4):** HY02 (the ATR's 'heat' rows; excluding them broke the MIDDEN total's fuel split), BF02 (the DEA lignocellulosic row is not netted of its feed; a correction double-netted it), NF25 (SF6 at melt-cast needs a new magnesium archetype), and PR06 (needs the CIMS export).

**Partly done because the build allows one review-view override per archetype and end use:** NF12 (per-metal melting factors), NF22 (lead refining), NF27 (Bessemer matte), and NG08 (gas-equivalent units). The factors are recorded on each row of `archetype-service.csv` as CIMS input factors.

The quarto chapters were updated to match (18 chapters and the changelog).

## Follow-up to the fifth round (2026-11-06)

- **HY02 (autothermal reformer):** the MIDDEN card's total is corrected to leave out its heat input, and its gas and electricity are restated as their own rows: 0.32 GJ per GJ of hydrogen on top of the feed (was 0.65).
- **BF02:** the lignocellulosic fermenter was not double counted. DEA's plant converts only about 30% of its biomass energy, so its 2.28 GJ/GJ is real. The syngas fermenter now carries Handler 2016's biomass input, 0.74 GJ/GJ on top of the feed, and buys no steam.
- **NF25 (magnesium SF6):** new node `non-ferrous-metals.product.magnesium.cover-gas` with `no-abatement_sf6` and `process-improvement_magnesium-cover-gas` (99.5% less SF6). The cells and retorts request their SF6 there.
- **PR06:** the CIMS export rule is in design.md: the capture technology is the host plus the capture-node request, plus only what the capture node lacks (`ccs-addon-extra.csv`). A fix in the capture-energy fill gives capture carriers that the host pools apart their add-on. The steam reformer variant now sums (gas 0.291, electricity 0.039, steam 0.214). The last three variants are fixed too (2026-11-06): the fill now writes the variant's `fuel` from the host's named fuels where the host has no `fuel` row. That moves Irlam's whole-plant fuel (2.19) on combined cycle with capture to as-sourced. The refinery heater and the Fischer-Tropsch gasifier had added up already, but had no `fuel` row. All 29 capture variants now add up.
- **Charcoal price:** 18.75 CAD per GJ (14.65-26.46) in `energy-price.csv`, from the two held charcoal sources (Feliciano-Bruzual and Mathews 2013; Norgate and Langberg 2009) at 29.7 GJ/t.
- **IM18 units:** the cement and lime chapter now gives the capture add-on's capital as about 550 CAD (2025) per t CO2 captured a year on lime kilns against about 290 on cement kilns (603 per t/yr of lime against 215 per t/yr of clinker). The lime figure is IEAGHG 2016's capture on a kraft-mill lime kiln.
