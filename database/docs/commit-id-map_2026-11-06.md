# Commit IDs before and after the 2026-11-06 history rewrite

On 2026-11-06 `git filter-repo` removed the old versions of `technology-database.xlsx` and five large NREL source tables from the history, so every commit got a new ID. The repo docs were updated (commit after `6ab4507`). Older notes outside the repo, such as the claude.ai project notes, still use the old IDs: look them up here. The full 40-character map is in `.git/filter-repo/commit-map` until that folder is removed.

| Old | New | Date | Commit |
| - | - | - | - |
| `f333d8d` | `6ab4507` | 2026-11-06 | Stop tracking the workbook (rebuilt from the CSVs on every build) |
| `714ce6a` | `164347c` | 2026-11-06 | Repo cleanup |
| `3af5b8b` | `26835af` | 2026-11-06 | Drop the wide CSV outputs |
| `47e599d` | `178f435` | 2026-11-06 | Scrap-preheating arc furnace keeps its own carrier mix |
| `8b70b29` | `a279e73` | 2026-11-06 | Efficient variants on pooled same-source ratios; 14 distinct technologies retyped alternat |
| `f2240dd` | `1e19bc9` | 2026-11-06 | Flows on HHV, output README, boiler variant capital, two retypes |
| `184831b` | `694e862` | 2026-11-06 | Boiler efficiency variant on the host's basis |
| `531f4a7` | `8cc8843` | 2026-11-06 | Lime-kiln capture fixed O&M premium as a capture add-on extra |
| `9731803` | `dcca0f8` | 2026-11-06 | Lime-kiln capture premium as a capture add-on extra |
| `e5f92d2` | `c4b158d` | 2026-11-06 | Charcoal reference price; capture variants' fuel row |
| `65c3fff` | `ddc21ee` | 2026-11-06 | Node alignment review: rules, five rounds, titanium intake |
| `fc2f6e8` | `256dbf4` | 2026-11-05 | Rename four hierarchy sectors ahead of CIMS |
| `f4b7772` | `c648fb9` | 2026-11-04 | Workbook layout, cement-and-lime and glass-and-ceramics families, lime in review |
| `d419a86` | `2b644b7` | 2026-11-04 | Log the reviewer questions on stalled archetypes |
| `fa06955` | `f41ba8c` | 2026-11-04 | to-process intake, IEAGHG merge, new archetypes, review-package updates |
| `ce5186a` | `1572b8c` | 2026-10-30 | Reorganize into database/ and cims/ |
| `608164f` | `96fd526` | 2026-10-29 | Readme and Ember shading; sector units; pipelines; new conventional options |
| `49b407e` | `00eddac` | 2026-10-29 | Product units shown as discussed: hydrogen per t, liquid fuels per m3, flaring per 1000 m3 |
| `2b841c1` | `f3c2dc3` | 2026-10-28 | Capacity units by end use and product, CO2-eq from species, alumina split |
| `c7d3070` | `ede330f` | 2026-10-28 | Capacity units, capacity/output alignment, recovered capacities, archetype splits |
| `6bf729f` | `1b04466` | 2026-10-28 | Sanity-check rulings 2026-10-28: S07, S150-S170, medium and low findings; rebuild |
| `ad08b95` | `acb508d` | 2026-10-28 | Sanity-check S95: top-submerged lance re-based on a copper furnace section |
| `547f4fe` | `563dfab` | 2026-10-28 | Sanity-check S160 Rechberger stack CO2, S95 flash furnace gas, S121 activator as VOM |
| `29fc564` | `8b982d1` | 2026-10-28 | Sanity-check S160 Rechberger carrier, S95 smelter set-asides, S121 CIMS edit held back |
| `942fc36` | `05fbac1` | 2026-10-28 | Sanity-check S148 weighting, S160 carrier check, S121 cement restructure; S95 log |
| `7141a13` | `f782b56` | 2026-10-27 | Smelter acid-plant node and archetype (S95); blowdown recovery carriers (S161) |
| `52e68c3` | `941bb00` | 2026-10-27 | Sanity-check S155 and PB016 rulings; through-air dryer energy redrafted |
| `0829217` | `ea82036` | 2026-10-27 | Rule out IEA per-crew LDAR costs and IEA REC per-t costs (S148, S159) |
| `d0622dd` | `08d200b` | 2026-10-27 | Sanity-check items S21, S95, S127, S148-S150, S152, S154, S157 |
| `56ec2aa` | `4e98a3b` | 2026-10-27 | Sanity-check items S53, S124, S127, S148, S153, S156 |
| `7e15d5a` | `a0e5b19` | 2026-10-27 | Rebuild outputs after sanity-check batches B-H and the docs reorganization |
| `2833fdc` | `4361833` | 2026-10-27 | Reorganize docs: dated reviews in docs/reviews, sanity-check material by date in docs/sani |
| `10ae733` | `a07adb3` | 2026-10-24 | Sanity-check run: summary for Brad (what changed, how to apply, rulings needed) |
| `1abef17` | `ababa3d` | 2026-10-24 | Sanity-check run batch H: per-tonne numbers no longer double-corrected for heating value;  |
| `eefc78f` | `bfa5d4a` | 2026-10-24 | Sanity-check run batch G: energy use from efficiency on five service archetypes, variant O |
| `2067c50` | `b6ce3b5` | 2026-10-24 | Sanity-check run batch F: remaining high-severity findings (IS005, MCF004, MCF005, NFM006, |
| `d8a496a` | `c470c87` | 2026-10-24 | Sanity-check run batch E: host plants for set-aside incremental costs (S20-S67), electrifi |
| `509a237` | `f46f356` | 2026-10-24 | Sanity-check run batch D: MIDDEN reference-size costs, pneumatic and methane-control bases |
| `60bda25` | `bdacc16` | 2026-10-24 | Sanity-check run batch C: combustion CO2 where fuel is burned, fuel-cell and smelting-redu |
| `b9e51a4` | `c6736a2` | 2026-10-24 | Sanity-check run batch B: MIDDEN totals carry their own carriers; energy totals against th |
| `ec56fc3` | `cb84706` | 2026-10-24 | Nickel refinery: net heat on the printed 50-70% recovery (S145, revised) |
| `77e0208` | `695d6ef` | 2026-10-24 | Nickel refinery: gross heat input, recovered heat as an output flow (S145) |
| `45d0819` | `aa9f656` | 2026-10-24 | Sanity-check 2026-10-23 round 3: HHV ratio on the fuel share (S144), consensus split choic |
| `d5dc8a4` | `b4390bc` | 2026-10-24 | Sanity-check 2026-10-23 round 2: fill-rule limits (S142), cost scope (S139, S146), energy- |
| `11c87ce` | `b1873ae` | 2026-10-24 | Sanity-check 2026-10-23 fixes S135, S138, S140: carrier splits, capture net emissions, fue |
| `2e217e0` | `2b5392d` | 2026-10-23 | Gas product unit written 1000-m3 (e3m3 kept as an alias) |
| `0db0ba3` | `59b7c3b` | 2026-10-23 | Gas archetypes per 10^3 m3 (e3m3) |
| `3e2ff8b` | `8118cec` | 2026-10-23 | Sanity-check 2026-10-23: recommendations applied (steam turbine, frac fleet, binder, acid  |
| `744c6f9` | `1cb5cd4` | 2026-10-23 | Diffuse capture on a standard amine reference plant; co-product flows per MWh or per t of  |
| `12ad3e8` | `b837682` | 2026-10-23 | Sanity-check pass 2026-10-23: 152 findings from eight family reviews, screens, S133-S146 |
| `108a81d` | `cb7392f` | 2026-10-23 | Node split, product review, petrochemicals and chemicals restructure, new baselines, HVAC  |
| `17989c9` | `1a7887f` | 2026-10-22 | CIMS comparison; emissions per output not bridged; space-conditioning capacity factors and |
| `89c3e31` | `64b5623` | 2026-10-22 | Oil and gas regulator data: Petrinex, AER, BCER and Directive 054 decks |
| `46db8fe` | `29f446f` | 2026-10-21 | _low and _medium intake: CCI/Dunsky heat pump reports to background; JRC-IDEES-2021 duplic |
| `f62ea55` | `5c4a905` | 2026-10-21 | Nickel refinery heat net of 75% recovery; carrier-sum exceptions listed for review |
| `c909ba9` | `c6da935` | 2026-10-21 | Energy-use total sums every carrier, sourced and estimated |
| `b792eb7` | `74f2e80` | 2026-10-21 | Single-carrier totals from the pooled carrier for every archetype |
| `60040d7` | `31893e3` | 2026-10-15 | Sanity-check follow-ups: zinc on the hydrometallurgy node, Lazard LCOE restated, James 202 |
| `93c8cae` | `5b9ebab` | 2026-10-15 | Lighting in lumen-hours: general and high-bay archetypes with 2000-era incumbents |
| `9591850` | `7a5482c` | 2026-10-14 | List of this round's draft judgements and conversion factors for review |
| `8346c53` | `b2520f6` | 2026-10-14 | Lazard LCOH restated without a rate of return (cash-flow model of the Key Assumptions case |
| `496efa6` | `83eedec` | 2026-10-14 | Remaining sanity-check decisions (all recommendations): new hydrogen DRI, potash mill, hyd |
| `d68dfd1` | `6006eba` | 2026-10-14 | Ethane reference price from Alberta's monthly reference price calculations (2000-2025 Dece |
| `d878b8a` | `78a3b10` | 2026-10-14 | Hydrogen reacted into the product as feedstock; CO2-eq on AR5 GWPs with one-gas CO2-eq row |
| `4dd401e` | `fe6da6a` | 2026-10-14 | Rulings 2026-10-14: ethane cracker, emissions-biomass, per-row cement rebase, gross methan |
| `adf81bd` | `5a6c2e1` | 2026-10-14 | Sanity-check list statuses after the 2026-10-13 fixes; screens after the fixes |
| `0543271` | `c9a8db4` | 2026-10-14 | Sanity-check 2026-10-11 section 3: record fixes by family (exclusions, product-basis facto |
| `e9b41db` | `a072806` | 2026-10-14 | Section 4 rulings: gross energy use (exports as output flows, net-energy table), feedstock |
| `e335e27` | `04a68c6` | 2026-10-14 | Sanity-check 2026-10-11 section 2: inverse identity narrowed, capture add-on as steam and  |
| `510d7a0` | `83b2fdd` | 2026-10-14 | Sanity-check 2026-10-11 section 1: fraction-in-percent cell, unit aliases, one total row p |
| `1d30511` | `05881aa` | 2026-10-13 | Load IEA 2025 Renewables for Industry and JRC-IDEES-2023 |
| `7a462f8` | `868e26f` | 2026-10-13 | Name the unnamed fuel on 21 archetypes (draft judgements); fuel counts as named beside hyd |
| `932db64` | `f649e4f` | 2026-10-13 | Other fossil fuel priced as oil; levelized cost incl. energy and CO2 identity use only car |
| `2513adc` | `af1e003` | 2026-10-13 | INL Table 19 extracted; EIA SMR efficiency target restored; bioliquid price (World Bank ra |
| `3b44438` | `13f3e00` | 2026-10-13 | Decision row: SMR efficiencies |
| `fb8a803` | `3347f1c` | 2026-10-13 | SMR efficiencies: sibling rule excluded (new scope key exclude-archetype); draft judgement |
| `9053696` | `457a23c` | 2026-10-13 | RNG (FortisBC, Enbridge, Energir) and nuclear (OPG) reference prices; landfill gas interna |
| `4b0e4d2` | `6ae3043` | 2026-10-13 | Liquid-biomass price (AFDC B100); Methanex, AFDC and Cameco price sources; Cameco uranium  |
| `ab19816` | `e6601eb` | 2026-10-13 | Coke price history from Q4 Quarterly Coal Reports; ammonia, methanol, biogas and municipal |
| `e0e0f2d` | `cc02616` | 2026-10-13 | EIA bulk price extracts; SEDS industrial prices for petroleum coke, propane, naphtha and g |
| `1f81c0a` | `7f27007` | 2026-10-12 | Intake the _low folder: 11 new sources; Clearstone 2019 methane content |
| `2e393c7` | `c157e99` | 2026-10-12 | Add US EIA reference prices for coal, coke, petroleum coke, LPG and biomass |
| `9a2d869` | `83718fe` | 2026-10-10 | Complete the fill; variants consistent with hosts; calculated levelized cost |
| `9a40241` | `f10a61a` | 2026-10-09 | Loosen key rule: product names and literature temperature classes as discriminators where  |
| `662567f` | `7361992` | 2026-10-09 | Rename non-ferrous arc furnaces to electric-arc-furnace_smelting-* |
| `a10ee8a` | `a10166c` | 2026-10-09 | Discriminators on parallel archetypes: solar-concentrator_point-focus, autothermal-reforme |
| `7c7fc70` | `6b7b73f` | 2026-10-09 | Split heat pumps and solar by heat tier; retag geothermal and heat-charged storage to low  |
| `5f6e6ed` | `fd738c2` | 2026-10-09 | Repeat machine-drive archetypes under sector end uses they serve |
| `86c7c41` | `aa3fd4d` | 2026-10-09 | Place end-use repeats in the owning family; derived families column; no repeat styling |
| `b3f6738` | `d77324e` | 2026-10-09 | Band the wide sheets by family then end use (process order, repeats marked) |
| `ea08777` | `1033f3d` | 2026-10-09 | Incinerator per GJ heat; primary-product families and product names; unit-free sibling rul |
| `abd12c0` | `ef65913` | 2026-10-09 | Final-product units, product-unit review, secondary parameters, regional HHV defaults |
| `2d865a0` | `a4772eb` | 2026-10-09 | Record 2026-10-09 decisions round 2; final-product and unit-chain reviews (no rebuild) |
| `7ed1531` | `c6bd551` | 2026-10-09 | Record the 2026-10-09 wide-view decisions, S89, and proposed product-unit resolutions (no  |
| `0052c21` | `0e5ee9d` | 2026-10-08 | Restructure the wide view from the 2026-10-08 column review |
| `4f0c5e1` | `944a6b1` | 2026-10-08 | Gap-fill MECS Table 5.4, add Tables 3.2/3.5, and put the metrics on the footprint basis |
| `b747c81` | `4e5e9a3` | 2026-10-08 | Bring check-names.py up to the archetype design |
| `954f4be` | `4e6fa79` | 2026-10-08 | Take in figures sources print wrongly on assumed corrections; non-typo basis fixes |
| `39cf9b9` | `380aa85` | 2026-10-08 | Load Rootzen and Johnsson 2017; close out the to-get list |
| `8aed7d5` | `f9e6d31` | 2026-10-07 | Split CHP with capture into combustion-turbine_chp_ccs-diffuse |
| `8aa4653` | `e60722a` | 2026-10-07 | Re-add combined-cycle_ccs-diffuse for power-only NGCC with capture |
| `2ca545d` | `c0adba3` | 2026-10-07 | Move Carbon Trust CTG033 and ECG092 to unavailable.csv with their substitutes; note Meyers |
| `bfe6305` | `3fe23ea` | 2026-10-07 | Refining handbooks (Meyers 1997, Jones and Pujado 2006), Challis dairy, klimaaktiv steam g |
| `f38d224` | `0234676` | 2026-10-07 | List unobtainable sources in unavailable.csv; drop UKTM documentation from to-get |
| `51bcd84` | `0d43886` | 2026-10-07 | Keep UKERC's Johansson 2012 energy rows (user ruling) |
| `9eee921` | `9220cd4` | 2026-10-07 | Second to-get intake: GNR Canada, IETD (Wayback), PRELIM v1.6, IEA methane model, full NED |
| `ac63f0a` | `a24e9d8` | 2026-10-07 | Move the fill-methods proposal to docs/ |
| `00b6a3c` | `53a0a3e` | 2026-10-06 | Process the _high/_medium/_low intake (to-get downloads): 48 extractions, UKERC originals  |
| `12fd4ea` | `8259985` | 2026-10-06 | Sanity-check pass: fixes from three rounds of rulings; heating-value streams for all LHV a |
| `ac3e306` | `3d38379` | 2026-10-05 | Drop "glass" from the glass furnace keys; fold the regenerative pasteurizer into the steam |
| `e109149` | `f55d5ab` | 2026-10-05 | Apply the archetype naming and combination reviews (535 to 486); keep UKERC's own rows cre |
| `2690970` | `6b1536f` | 2026-10-03 | Drop UKERC rows where the original is held; N-ZIP workbook, five background sources, two g |
| `09d4116` | `b5992ba` | 2026-10-03 | Load six new _high sources: IEAGHG 2008/3, NRCan open-pit benchmark, Concawe 9/19, Ren 200 |
| `c14f56d` | `2772357` | 2026-10-03 | Hotmaps method notes and decisions entry; ignore EPA platform JSON downloads; drop _newfil |
| `54c80f8` | `52a6911` | 2026-10-03 | Load the CIMS/JCIMS folders intake (43 sources); LNG haul truck; currencies; Clearstone pn |
| `cea2f1f` | `7e95c73` | 2026-10-03 | Natural Gas STAR archetypes, ECCC NIR emission factors, source review additions |
| `3d9e7dc` | `c1c4503` | 2026-10-03 | Load the _low intake: 22 sources, 3 no-data, boiler_oxy-fuel |
| `640d951` | `9ac8657` | 2026-10-03 | Load the second _high/_medium intake batch (H18-H25, M1-M16) |
| `7b72857` | `ebaf851` | 2026-10-02 | Load 43 sources from the 2026-10-02 _high intake; 19 archetypes; capture cost by differenc |
| `75de07e` | `c11b7a1` | 2026-10-02 | Load EPA Natural Gas STAR documents; methane-control archetypes in CIMS units; CIMS to-fix |
| `41a5f25` | `8c25ded` | 2026-10-02 | Unlock excluded source data: CCS host/add-on split, capture split, currency years, factors |
| `c8ce353` | `e8c25ff` | 2026-10-02 | Restore the Haber-Bosch heating-value stream; fix the CHP efficiency bridge; unit and spel |
| `2458a3f` | `852c85b` | 2026-10-02 | DKK currency conversion via the euro; refreshed CIMS deflator and exchange tables |
| `24077ca` | `9d80314` | 2026-10-02 | Merge 48 archetypes from the combination review (531 to 483); start the sanity-check list |
| `4005c74` | `8fefa48` | 2026-10-02 | Add 103 gap-filling sources to to-get.csv |
| `d4c011e` | `f5672ae` | 2026-10-02 | Archetype combination review from the CIMS point of view (flags only, no records changed) |
| `3ee471d` | `330b79b` | 2026-10-02 | Load the _medium queue: 45 sources (steel, P&P, chemicals, cement, CCS, heat pumps) |
| `897dbce` | `970a3fb` | 2026-10-02 | CHP costs per kW electric put per kW heat with the heat-to-power ratio (all sources) |
| `8d4a0f8` | `c29de54` | 2026-10-02 | Add 40 archetypes from the _high mapping review; ADt and kcal unit definitions |
| `32924d2` | `f9938d8` | 2026-10-01 | Re-sort file manifest after the Voldsund SI rename |
| `055cfc0` | `a791aa2` | 2026-10-01 | Manifest sorted; decisions line and mapping review list for the _high queue; ENE BREF to t |
| `abd6390` | `11c5a98` | 2026-10-01 | Load _high queue 2b: NFM, LCP, FDM, CWW, WGC, WBP, WI, WT BREFs; ENERGY STAR food and phar |
| `90c4c88` | `5374fab` | 2026-10-01 | Load _high queue 2a: cement, lime, glass, ceramics, refining and foundry sources (14) |
| `eba44b1` | `4171e81` | 2026-10-01 | Load _high queue 1: DOE Liftoff x2, Boulamanti 2017, Kramer 2009, LVOC/FMP/IS/PP/LVIC-AAF/ |
| `2854b0b` | `8606c0e` | 2026-10-01 | Park the ratio fill methods (written and back-tested, not applied) |
| `974146e` | `124ff81` | 2026-10-01 | Sibling fills for lifetime, construction time and capacity factor |
| `dc16e6e` | `7373ee4` | 2026-10-01 | Fill step for empty cells; product heating values; LHV fixes; shading |
| `a354f41` | `57854bb` | 2026-09-30 | Stop tracking primary documents; keep only extracted data |
| `521bee2` | `d557dd2` | 2026-09-30 | Consolidate the steam archetypes; mark two heat-pump values for review |
| `a6d4ed2` | `f25cdb0` | 2026-09-30 | New sources, hierarchy-with-technology output, and a mapping review |
| `59d019b` | `c19ba85` | 2026-09-27 | Conversion factors: HHV basis, factor classes, efficiency bridge, reference manifest |
| `e90d6bb` | `51ea3c8` | 2026-09-27 | Extract CAELP/E3 2024 and RTC 2023; list gap-filling sources |
| `905ed52` | `aa8082b` | 2026-09-27 | Drop the electrolytic limestone decarbonation archetype |
| `85a5025` | `f85e28c` | 2026-09-27 | Rebuild outputs |
| `3598cbe` | `91bb3e0` | 2026-09-27 | Metal-smelting capture node; remove supercritical CO2 drying |
| `e3f08bb` | `9632107` | 2026-09-27 | Rebuild outputs |
| `58f9bd9` | `e879c2e` | 2026-09-27 | Tecnored, Sublime and Brimstone archetypes; skip aluminium rolling; set aside 90% reformer |
| `3e9f2d2` | `39453c6` | 2026-09-27 | Rebuild outputs |
| `683fd8b` | `47735f5` | 2026-09-27 | Build: hour lifetimes, duplicate parents, wide-view order and notes |
| `48c4f6e` | `d6b8e25` | 2026-09-27 | Mapping review: 13 archetypes, remaps and (none) decisions |
| `66e4b83` | `878cbb6` | 2026-09-26 | Rebuild outputs |
| `9a8a91c` | `b7dd52e` | 2026-09-26 | Conversion pass: unit definitions and cited product factors |
| `6dcbba5` | `d721101` | 2026-09-26 | Show levelized costs with the cost data; load them from sidecars |
| `55c069e` | `98d3651` | 2026-09-26 | Rebuild outputs |
| `1cc65bd` | `05e7e86` | 2026-09-26 | Add 19 archetypes and map the pending examples |
| `321d582` | `141754a` | 2026-09-26 | Rerun the ETSAP extractions made before the current rules |
| `a460121` | `7d7bab9` | 2026-09-25 | Rebuild outputs |
| `80d75b9` | `131956a` | 2026-09-25 | Map 743 new examples to archetypes |
| `99b9a27` | `47e2ea4` | 2026-09-25 | Load the remaining extractions in the ETSAP-brief shape |
| `81fc8ff` | `c7d47cb` | 2026-09-24 | Extract the 15 remaining ETSAP briefs |
| `17a4c6f` | `52a385b` | 2026-09-24 | Rebuild outputs |
| `d17b9c5` | `fc4c515` | 2026-09-24 | Assemble whole-plant costs from one source's component costs |
| `252528f` | `9259fa6` | 2026-09-24 | Extract and load six ETSAP briefs |
| `f92c8f5` | `a3bb67a` | 2026-09-24 | Archetypes from the ETSAP assessment; add-on, component and whole-plant rules |
| `12b074e` | `b8901d1` | 2026-09-24 | Source manifest and citations for the sources above |
| `b5508fb` | `daf093e` | 2026-09-24 | IEA and ETSAP: convention names, register and assess the held briefs |
| `5762598` | `3e599f8` | 2026-09-24 | gov-usa: extract DOE, EPA and NETL sources; rename to the naming convention |
| `09758dc` | `528522e` | 2026-09-24 | Keep downloaded documents that yield no data in a background folder |
| `7efe0b5` | `7af83d0` | 2026-09-24 | Extract newly downloaded papers and reports; list documents still to get |
| `e23eb6c` | `ef6bc7b` | 2026-09-24 | Remove Canadian calibration data outside the database's scope |
| `43ce44a` | `59a73c6` | 2026-09-23 | Legacy cement kilns, solid-fuel heaters and dryers, incremental cost basis |
| `a5a395c` | `cace286` | 2026-09-23 | Assignment review: re-home 201 examples, add 4 archetypes, correct hierarchy links |
| `108b87f` | `4e3b08e` | 2026-09-23 | Read a source's generic /unit as its own service unit; record assignment review findings |
| `5ef7909` | `80439df` | 2026-09-23 | Wide view: drop the rows for end uses no archetype serves |
| `ca7d852` | `9dd45e0` | 2026-09-23 | Wide view lists every archetype and every end use |
| `62f3fda` | `59ea404` | 2026-09-23 | Whole-plant costs for UKERC measures; re-home mis-mapped measure buckets |
| `32b9888` | `264de5b` | 2026-09-23 | Take steam-using processes off CHP; do not pool negative costs |
| `34b66ab` | `f19796a` | 2026-09-23 | Set aside UKERC costs that need an efficiency factor |
| `cae6145` | `a8fa7ed` | 2026-09-23 | Label derived duplicates; convert only with the source's own output factor |
| `b875d34` | `68fe153` | 2026-09-23 | Fold the candidate merges; one reduction-potential column; plain source-list counts |
| `46fa1db` | `fc64bc9` | 2026-09-22 | decisions.md: the open items the restructure leaves for review |
| `61acf42` | `3d9ae1a` | 2026-09-22 | A ratio printed without a unit pools as dimensionless |
| `42ff6e4` | `9a15b08` | 2026-09-22 | Build output does not depend on hash order |
| `9f4960d` | `6bfb4b1` | 2026-09-22 | Docs state the rules; the decision chain moves to archive/ |
| `56bebbb` | `fa0ebce` | 2026-09-22 | Retire the roster pipeline; park the CIMS model inputs under compare/ |
| `cd20991` | `fecdfc9` | 2026-09-22 | One build for the archetype database: build.py and its stages |
| `2c020e3` | `61349c2` | 2026-09-22 | Records for the archetype database: archetypes, services, examples |
| `861c192` | `3bdd766` | 2026-09-22 | build-source-list: split the ;-joined source-id on technology rows |
| `16e05d7` | `34d5e85` | 2026-09-22 | Adopt the design vocabulary in the harmonized layer |
| `bf4cd39` | `00c2703` | 2026-09-22 | Schema and vocabulary for the design roster |
| `eb3d06f` | `0b37401` | 2026-09-22 | Design crosswalk: device-first folds, every source context kept |
| `b6675e2` | `ca5e8ca` | 2026-09-22 | Design crosswalk: target the CIMS hierarchy directly, down to the leaf |
| `127f74f` | `023b917` | 2026-09-22 | Canadian spelling in the vocabulary, names and our own prose |
| `20620c8` | `6c1410e` | 2026-09-22 | hierarchy_crosswalk: fail on an end use no hierarchy node reaches |
| `4d8609a` | `eb1fa86` | 2026-09-22 | Reporting accounting proposal |
| `0ef1e47` | `bc2be3f` | 2026-09-22 | Crosswalk from the harmonized roster to the design vocabulary |
| `99a02c6` | `1122a84` | 2026-09-22 | Harmonize the design end uses with the CIMS hierarchy |
| `3c95a3b` | `3e1a353` | 2026-09-22 | Design: sector end-use table and technology table |
| `8f91931` | `e91d838` | 2026-09-22 | Harmonized pipeline: aggregation rules, stable ids, basis and currency checks |
| `65fb662` | `e1a0d10` | 2026-09-22 | Regenerate the harmonized tables |
| `e3bfd1f` | `694ff3c` | 2026-09-22 | Extractions: current parameter names and data fixes |
| `4fd535d` | `c254009` | 2026-09-22 | Currency conversion: deflate in the source currency, then exchange |
| `ae28740` | `80c0c34` | 2026-09-22 | Stop tracking Python bytecode |
| `5a44239` | `e37d1f5` | 2026-09-15 | .gitignore |
| `e7d5249` | `3c4086d` | 2026-09-09 | Add .gitattributes to normalize line endings |
