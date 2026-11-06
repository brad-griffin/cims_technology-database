# Commit IDs before and after the 2026-11-06 history rewrite

On 2026-11-06 `git filter-repo` removed the old versions of `technology-database.xlsx` and the large NREL source tables (every file over 30 MB) from the history, before the first push to GitHub, so every commit got a new ID. The repo docs use the new IDs. Older notes outside the repo, such as the claude.ai project notes, still use the old IDs: look them up here. Commits made after the rewrite are not listed.

| Old | New | Date | Commit |
| - | - | - | - |
| `33b05d4` | `0d6a795` | 2026-11-06 | Old-to-new commit ID table for the 2026-11-06 history rewrite |
| `e88c9be` | `0fc7ba3` | 2026-11-06 | Update commit IDs in the docs after the history rewrite |
| `f333d8d` | `6003256` | 2026-11-06 | Stop tracking the workbook (rebuilt from the CSVs on every build) |
| `714ce6a` | `45ec9bd` | 2026-11-06 | Repo cleanup |
| `3af5b8b` | `6554946` | 2026-11-06 | Drop the wide CSV outputs |
| `47e599d` | `47c4682` | 2026-11-06 | Scrap-preheating arc furnace keeps its own carrier mix |
| `8b70b29` | `f614d4b` | 2026-11-06 | Efficient variants on pooled same-source ratios; 14 distinct technologies retyped alternat |
| `f2240dd` | `f92cab1` | 2026-11-06 | Flows on HHV, output README, boiler variant capital, two retypes |
| `184831b` | `45917b1` | 2026-11-06 | Boiler efficiency variant on the host's basis |
| `531f4a7` | `45650f1` | 2026-11-06 | Lime-kiln capture fixed O&M premium as a capture add-on extra |
| `9731803` | `8511af4` | 2026-11-06 | Lime-kiln capture premium as a capture add-on extra |
| `e5f92d2` | `cf3c350` | 2026-11-06 | Charcoal reference price; capture variants' fuel row |
| `65c3fff` | `81fb6ea` | 2026-11-06 | Node alignment review: rules, five rounds, titanium intake |
| `fc2f6e8` | `4d9b6b4` | 2026-11-05 | Rename four hierarchy sectors ahead of CIMS |
| `f4b7772` | `c0be6e1` | 2026-11-04 | Workbook layout, cement-and-lime and glass-and-ceramics families, lime in review |
| `d419a86` | `9403346` | 2026-11-04 | Log the reviewer questions on stalled archetypes |
| `fa06955` | `2fc1d2b` | 2026-11-04 | to-process intake, IEAGHG merge, new archetypes, review-package updates |
| `ce5186a` | `202fd3f` | 2026-10-30 | Reorganize into database/ and cims/ |
| `608164f` | `6ac5c1f` | 2026-10-29 | Readme and Ember shading; sector units; pipelines; new conventional options |
| `49b407e` | `7dfcf06` | 2026-10-29 | Product units shown as discussed: hydrogen per t, liquid fuels per m3, flaring per 1000 m3 |
| `2b841c1` | `a42447c` | 2026-10-28 | Capacity units by end use and product, CO2-eq from species, alumina split |
| `c7d3070` | `969f90d` | 2026-10-28 | Capacity units, capacity/output alignment, recovered capacities, archetype splits |
| `6bf729f` | `640b396` | 2026-10-28 | Sanity-check rulings 2026-10-28: S07, S150-S170, medium and low findings; rebuild |
| `ad08b95` | `58568ac` | 2026-10-28 | Sanity-check S95: top-submerged lance re-based on a copper furnace section |
| `547f4fe` | `c62c386` | 2026-10-28 | Sanity-check S160 Rechberger stack CO2, S95 flash furnace gas, S121 activator as VOM |
| `29fc564` | `801a675` | 2026-10-28 | Sanity-check S160 Rechberger carrier, S95 smelter set-asides, S121 CIMS edit held back |
| `942fc36` | `2bf495f` | 2026-10-28 | Sanity-check S148 weighting, S160 carrier check, S121 cement restructure; S95 log |
| `7141a13` | `59f59bb` | 2026-10-27 | Smelter acid-plant node and archetype (S95); blowdown recovery carriers (S161) |
| `52e68c3` | `7f8fc3c` | 2026-10-27 | Sanity-check S155 and PB016 rulings; through-air dryer energy redrafted |
| `0829217` | `7313ef6` | 2026-10-27 | Rule out IEA per-crew LDAR costs and IEA REC per-t costs (S148, S159) |
| `d0622dd` | `837e56a` | 2026-10-27 | Sanity-check items S21, S95, S127, S148-S150, S152, S154, S157 |
| `56ec2aa` | `9a5c325` | 2026-10-27 | Sanity-check items S53, S124, S127, S148, S153, S156 |
| `7e15d5a` | `d553079` | 2026-10-27 | Rebuild outputs after sanity-check batches B-H and the docs reorganization |
| `2833fdc` | `523fde8` | 2026-10-27 | Reorganize docs: dated reviews in docs/reviews, sanity-check material by date in docs/sani |
| `10ae733` | `9a8c52f` | 2026-10-24 | Sanity-check run: summary for Brad (what changed, how to apply, rulings needed) |
| `1abef17` | `494566e` | 2026-10-24 | Sanity-check run batch H: per-tonne numbers no longer double-corrected for heating value;  |
| `eefc78f` | `65b69c1` | 2026-10-24 | Sanity-check run batch G: energy use from efficiency on five service archetypes, variant O |
| `2067c50` | `b21262c` | 2026-10-24 | Sanity-check run batch F: remaining high-severity findings (IS005, MCF004, MCF005, NFM006, |
| `d8a496a` | `dbe6a7f` | 2026-10-24 | Sanity-check run batch E: host plants for set-aside incremental costs (S20-S67), electrifi |
| `509a237` | `d603269` | 2026-10-24 | Sanity-check run batch D: MIDDEN reference-size costs, pneumatic and methane-control bases |
| `60bda25` | `59d813b` | 2026-10-24 | Sanity-check run batch C: combustion CO2 where fuel is burned, fuel-cell and smelting-redu |
| `b9e51a4` | `9e43c8a` | 2026-10-24 | Sanity-check run batch B: MIDDEN totals carry their own carriers; energy totals against th |
| `ec56fc3` | `e9c33ed` | 2026-10-24 | Nickel refinery: net heat on the printed 50-70% recovery (S145, revised) |
| `77e0208` | `4d84a57` | 2026-10-24 | Nickel refinery: gross heat input, recovered heat as an output flow (S145) |
| `45d0819` | `cbc948b` | 2026-10-24 | Sanity-check 2026-10-23 round 3: HHV ratio on the fuel share (S144), consensus split choic |
| `d5dc8a4` | `eed3c8b` | 2026-10-24 | Sanity-check 2026-10-23 round 2: fill-rule limits (S142), cost scope (S139, S146), energy- |
| `11c87ce` | `931c448` | 2026-10-24 | Sanity-check 2026-10-23 fixes S135, S138, S140: carrier splits, capture net emissions, fue |
| `2e217e0` | `b78ecbc` | 2026-10-23 | Gas product unit written 1000-m3 (e3m3 kept as an alias) |
| `0db0ba3` | `d6e8020` | 2026-10-23 | Gas archetypes per 10^3 m3 (e3m3) |
| `3e2ff8b` | `f2e3775` | 2026-10-23 | Sanity-check 2026-10-23: recommendations applied (steam turbine, frac fleet, binder, acid  |
| `744c6f9` | `6d3e92e` | 2026-10-23 | Diffuse capture on a standard amine reference plant; co-product flows per MWh or per t of  |
| `12ad3e8` | `c0ba3f4` | 2026-10-23 | Sanity-check pass 2026-10-23: 152 findings from eight family reviews, screens, S133-S146 |
| `108a81d` | `dca09dc` | 2026-10-23 | Node split, product review, petrochemicals and chemicals restructure, new baselines, HVAC  |
| `17989c9` | `6e54a7f` | 2026-10-22 | CIMS comparison; emissions per output not bridged; space-conditioning capacity factors and |
| `89c3e31` | `19a7fad` | 2026-10-22 | Oil and gas regulator data: Petrinex, AER, BCER and Directive 054 decks |
| `46db8fe` | `9731fa3` | 2026-10-21 | _low and _medium intake: CCI/Dunsky heat pump reports to background; JRC-IDEES-2021 duplic |
| `f62ea55` | `f0eda1b` | 2026-10-21 | Nickel refinery heat net of 75% recovery; carrier-sum exceptions listed for review |
| `c909ba9` | `5e6f335` | 2026-10-21 | Energy-use total sums every carrier, sourced and estimated |
| `b792eb7` | `e453bf7` | 2026-10-21 | Single-carrier totals from the pooled carrier for every archetype |
| `60040d7` | `f7775d3` | 2026-10-15 | Sanity-check follow-ups: zinc on the hydrometallurgy node, Lazard LCOE restated, James 202 |
| `93c8cae` | `f0731ce` | 2026-10-15 | Lighting in lumen-hours: general and high-bay archetypes with 2000-era incumbents |
| `9591850` | `3ea4bf9` | 2026-10-14 | List of this round's draft judgements and conversion factors for review |
| `8346c53` | `b30231e` | 2026-10-14 | Lazard LCOH restated without a rate of return (cash-flow model of the Key Assumptions case |
| `496efa6` | `dd80f74` | 2026-10-14 | Remaining sanity-check decisions (all recommendations): new hydrogen DRI, potash mill, hyd |
| `d68dfd1` | `8e9e037` | 2026-10-14 | Ethane reference price from Alberta's monthly reference price calculations (2000-2025 Dece |
| `d878b8a` | `9edd459` | 2026-10-14 | Hydrogen reacted into the product as feedstock; CO2-eq on AR5 GWPs with one-gas CO2-eq row |
| `4dd401e` | `7436042` | 2026-10-14 | Rulings 2026-10-14: ethane cracker, emissions-biomass, per-row cement rebase, gross methan |
| `adf81bd` | `7d49212` | 2026-10-14 | Sanity-check list statuses after the 2026-10-13 fixes; screens after the fixes |
| `0543271` | `e122290` | 2026-10-14 | Sanity-check 2026-10-11 section 3: record fixes by family (exclusions, product-basis facto |
| `e9b41db` | `b452619` | 2026-10-14 | Section 4 rulings: gross energy use (exports as output flows, net-energy table), feedstock |
| `e335e27` | `ca2c4a7` | 2026-10-14 | Sanity-check 2026-10-11 section 2: inverse identity narrowed, capture add-on as steam and  |
| `510d7a0` | `693060c` | 2026-10-14 | Sanity-check 2026-10-11 section 1: fraction-in-percent cell, unit aliases, one total row p |
| `1d30511` | `cefd432` | 2026-10-13 | Load IEA 2025 Renewables for Industry and JRC-IDEES-2023 |
| `7a462f8` | `9865406` | 2026-10-13 | Name the unnamed fuel on 21 archetypes (draft judgements); fuel counts as named beside hyd |
| `932db64` | `f3a336c` | 2026-10-13 | Other fossil fuel priced as oil; levelized cost incl. energy and CO2 identity use only car |
| `2513adc` | `de82414` | 2026-10-13 | INL Table 19 extracted; EIA SMR efficiency target restored; bioliquid price (World Bank ra |
| `3b44438` | `36c5326` | 2026-10-13 | Decision row: SMR efficiencies |
| `fb8a803` | `69b50e6` | 2026-10-13 | SMR efficiencies: sibling rule excluded (new scope key exclude-archetype); draft judgement |
| `9053696` | `d6df15f` | 2026-10-13 | RNG (FortisBC, Enbridge, Energir) and nuclear (OPG) reference prices; landfill gas interna |
| `4b0e4d2` | `704f712` | 2026-10-13 | Liquid-biomass price (AFDC B100); Methanex, AFDC and Cameco price sources; Cameco uranium  |
| `ab19816` | `9f447b5` | 2026-10-13 | Coke price history from Q4 Quarterly Coal Reports; ammonia, methanol, biogas and municipal |
| `e0e0f2d` | `6ac282a` | 2026-10-13 | EIA bulk price extracts; SEDS industrial prices for petroleum coke, propane, naphtha and g |
| `1f81c0a` | `cbbaa89` | 2026-10-12 | Intake the _low folder: 11 new sources; Clearstone 2019 methane content |
| `2e393c7` | `edd0da9` | 2026-10-12 | Add US EIA reference prices for coal, coke, petroleum coke, LPG and biomass |
| `9a2d869` | `93da2b1` | 2026-10-10 | Complete the fill; variants consistent with hosts; calculated levelized cost |
| `9a40241` | `7d7fed7` | 2026-10-09 | Loosen key rule: product names and literature temperature classes as discriminators where  |
| `662567f` | `588a612` | 2026-10-09 | Rename non-ferrous arc furnaces to electric-arc-furnace_smelting-* |
| `a10ee8a` | `2b1456e` | 2026-10-09 | Discriminators on parallel archetypes: solar-concentrator_point-focus, autothermal-reforme |
| `7c7fc70` | `a44335a` | 2026-10-09 | Split heat pumps and solar by heat tier; retag geothermal and heat-charged storage to low  |
| `5f6e6ed` | `416c678` | 2026-10-09 | Repeat machine-drive archetypes under sector end uses they serve |
| `86c7c41` | `169423d` | 2026-10-09 | Place end-use repeats in the owning family; derived families column; no repeat styling |
| `b3f6738` | `9e64afa` | 2026-10-09 | Band the wide sheets by family then end use (process order, repeats marked) |
| `ea08777` | `040cb51` | 2026-10-09 | Incinerator per GJ heat; primary-product families and product names; unit-free sibling rul |
| `abd12c0` | `95c3947` | 2026-10-09 | Final-product units, product-unit review, secondary parameters, regional HHV defaults |
| `2d865a0` | `c705db7` | 2026-10-09 | Record 2026-10-09 decisions round 2; final-product and unit-chain reviews (no rebuild) |
| `7ed1531` | `e78d524` | 2026-10-09 | Record the 2026-10-09 wide-view decisions, S89, and proposed product-unit resolutions (no  |
| `0052c21` | `acc0719` | 2026-10-08 | Restructure the wide view from the 2026-10-08 column review |
| `4f0c5e1` | `9100a17` | 2026-10-08 | Gap-fill MECS Table 5.4, add Tables 3.2/3.5, and put the metrics on the footprint basis |
| `b747c81` | `da97c41` | 2026-10-08 | Bring check-names.py up to the archetype design |
| `954f4be` | `1400da1` | 2026-10-08 | Take in figures sources print wrongly on assumed corrections; non-typo basis fixes |
| `39cf9b9` | `e501ba5` | 2026-10-08 | Load Rootzen and Johnsson 2017; close out the to-get list |
| `8aed7d5` | `ca8f991` | 2026-10-07 | Split CHP with capture into combustion-turbine_chp_ccs-diffuse |
| `8aa4653` | `567f16d` | 2026-10-07 | Re-add combined-cycle_ccs-diffuse for power-only NGCC with capture |
| `2ca545d` | `f9944d8` | 2026-10-07 | Move Carbon Trust CTG033 and ECG092 to unavailable.csv with their substitutes; note Meyers |
| `bfe6305` | `78d776f` | 2026-10-07 | Refining handbooks (Meyers 1997, Jones and Pujado 2006), Challis dairy, klimaaktiv steam g |
| `f38d224` | `6dfb406` | 2026-10-07 | List unobtainable sources in unavailable.csv; drop UKTM documentation from to-get |
| `51bcd84` | `b7cfa36` | 2026-10-07 | Keep UKERC's Johansson 2012 energy rows (user ruling) |
| `9eee921` | `a786b13` | 2026-10-07 | Second to-get intake: GNR Canada, IETD (Wayback), PRELIM v1.6, IEA methane model, full NED |
| `ac63f0a` | `90280b1` | 2026-10-07 | Move the fill-methods proposal to docs/ |
| `00b6a3c` | `78da77f` | 2026-10-06 | Process the _high/_medium/_low intake (to-get downloads): 48 extractions, UKERC originals  |
| `12fd4ea` | `508b24b` | 2026-10-06 | Sanity-check pass: fixes from three rounds of rulings; heating-value streams for all LHV a |
| `ac3e306` | `faa7705` | 2026-10-05 | Drop "glass" from the glass furnace keys; fold the regenerative pasteurizer into the steam |
| `e109149` | `48e340a` | 2026-10-05 | Apply the archetype naming and combination reviews (535 to 486); keep UKERC's own rows cre |
| `2690970` | `70cea5b` | 2026-10-03 | Drop UKERC rows where the original is held; N-ZIP workbook, five background sources, two g |
| `09d4116` | `04b7c88` | 2026-10-03 | Load six new _high sources: IEAGHG 2008/3, NRCan open-pit benchmark, Concawe 9/19, Ren 200 |
| `c14f56d` | `12a0f37` | 2026-10-03 | Hotmaps method notes and decisions entry; ignore EPA platform JSON downloads; drop _newfil |
| `54c80f8` | `d90881c` | 2026-10-03 | Load the CIMS/JCIMS folders intake (43 sources); LNG haul truck; currencies; Clearstone pn |
| `cea2f1f` | `5f551ab` | 2026-10-03 | Natural Gas STAR archetypes, ECCC NIR emission factors, source review additions |
| `3d9e7dc` | `d23fbe2` | 2026-10-03 | Load the _low intake: 22 sources, 3 no-data, boiler_oxy-fuel |
| `640d951` | `0e18f7d` | 2026-10-03 | Load the second _high/_medium intake batch (H18-H25, M1-M16) |
| `7b72857` | `c7bd733` | 2026-10-02 | Load 43 sources from the 2026-10-02 _high intake; 19 archetypes; capture cost by differenc |
| `75de07e` | `fb829b2` | 2026-10-02 | Load EPA Natural Gas STAR documents; methane-control archetypes in CIMS units; CIMS to-fix |
| `41a5f25` | `2a1c095` | 2026-10-02 | Unlock excluded source data: CCS host/add-on split, capture split, currency years, factors |
| `c8ce353` | `a02d43f` | 2026-10-02 | Restore the Haber-Bosch heating-value stream; fix the CHP efficiency bridge; unit and spel |
| `2458a3f` | `3a8f380` | 2026-10-02 | DKK currency conversion via the euro; refreshed CIMS deflator and exchange tables |
| `24077ca` | `9376705` | 2026-10-02 | Merge 48 archetypes from the combination review (531 to 483); start the sanity-check list |
| `4005c74` | `ad0956b` | 2026-10-02 | Add 103 gap-filling sources to to-get.csv |
| `d4c011e` | `2cddedd` | 2026-10-02 | Archetype combination review from the CIMS point of view (flags only, no records changed) |
| `3ee471d` | `8f78371` | 2026-10-02 | Load the _medium queue: 45 sources (steel, P&P, chemicals, cement, CCS, heat pumps) |
| `897dbce` | `f671567` | 2026-10-02 | CHP costs per kW electric put per kW heat with the heat-to-power ratio (all sources) |
| `8d4a0f8` | `9f79550` | 2026-10-02 | Add 40 archetypes from the _high mapping review; ADt and kcal unit definitions |
| `32924d2` | `bd22319` | 2026-10-01 | Re-sort file manifest after the Voldsund SI rename |
| `055cfc0` | `32d2863` | 2026-10-01 | Manifest sorted; decisions line and mapping review list for the _high queue; ENE BREF to t |
| `abd6390` | `79d902e` | 2026-10-01 | Load _high queue 2b: NFM, LCP, FDM, CWW, WGC, WBP, WI, WT BREFs; ENERGY STAR food and phar |
| `90c4c88` | `70507da` | 2026-10-01 | Load _high queue 2a: cement, lime, glass, ceramics, refining and foundry sources (14) |
| `eba44b1` | `69e06bf` | 2026-10-01 | Load _high queue 1: DOE Liftoff x2, Boulamanti 2017, Kramer 2009, LVOC/FMP/IS/PP/LVIC-AAF/ |
| `2854b0b` | `a0bce91` | 2026-10-01 | Park the ratio fill methods (written and back-tested, not applied) |
| `974146e` | `860fee6` | 2026-10-01 | Sibling fills for lifetime, construction time and capacity factor |
| `dc16e6e` | `fa31966` | 2026-10-01 | Fill step for empty cells; product heating values; LHV fixes; shading |
| `a354f41` | `e8c9ea4` | 2026-09-30 | Stop tracking primary documents; keep only extracted data |
| `521bee2` | `7d1d22c` | 2026-09-30 | Consolidate the steam archetypes; mark two heat-pump values for review |
| `a6d4ed2` | `720a1df` | 2026-09-30 | New sources, hierarchy-with-technology output, and a mapping review |
| `59d019b` | `e23b22e` | 2026-09-27 | Conversion factors: HHV basis, factor classes, efficiency bridge, reference manifest |
| `e90d6bb` | `0a918f7` | 2026-09-27 | Extract CAELP/E3 2024 and RTC 2023; list gap-filling sources |
| `905ed52` | `58ed1c2` | 2026-09-27 | Drop the electrolytic limestone decarbonation archetype |
| `85a5025` | `01cc8f4` | 2026-09-27 | Rebuild outputs |
| `3598cbe` | `4a00bfc` | 2026-09-27 | Metal-smelting capture node; remove supercritical CO2 drying |
| `e3f08bb` | `efc56ca` | 2026-09-27 | Rebuild outputs |
| `58f9bd9` | `8ea2cf4` | 2026-09-27 | Tecnored, Sublime and Brimstone archetypes; skip aluminium rolling; set aside 90% reformer |
| `3e9f2d2` | `6e0b5da` | 2026-09-27 | Rebuild outputs |
| `683fd8b` | `b826f8a` | 2026-09-27 | Build: hour lifetimes, duplicate parents, wide-view order and notes |
| `48c4f6e` | `922ea8c` | 2026-09-27 | Mapping review: 13 archetypes, remaps and (none) decisions |
| `66e4b83` | `2d5d129` | 2026-09-26 | Rebuild outputs |
| `9a8a91c` | `338492b` | 2026-09-26 | Conversion pass: unit definitions and cited product factors |
| `6dcbba5` | `c9d7800` | 2026-09-26 | Show levelized costs with the cost data; load them from sidecars |
| `55c069e` | `37b5f07` | 2026-09-26 | Rebuild outputs |
| `1cc65bd` | `a78fced` | 2026-09-26 | Add 19 archetypes and map the pending examples |
| `321d582` | `8373e32` | 2026-09-26 | Rerun the ETSAP extractions made before the current rules |
| `a460121` | `4684be3` | 2026-09-25 | Rebuild outputs |
| `80d75b9` | `80393ee` | 2026-09-25 | Map 743 new examples to archetypes |
| `99b9a27` | `678f3e2` | 2026-09-25 | Load the remaining extractions in the ETSAP-brief shape |
| `81fc8ff` | `a5e9560` | 2026-09-24 | Extract the 15 remaining ETSAP briefs |
| `17a4c6f` | `78eaf3b` | 2026-09-24 | Rebuild outputs |
| `d17b9c5` | `6bca45f` | 2026-09-24 | Assemble whole-plant costs from one source's component costs |
| `252528f` | `50f31f8` | 2026-09-24 | Extract and load six ETSAP briefs |
| `f92c8f5` | `41c07d5` | 2026-09-24 | Archetypes from the ETSAP assessment; add-on, component and whole-plant rules |
| `12b074e` | `9c9ec43` | 2026-09-24 | Source manifest and citations for the sources above |
| `b5508fb` | `1e56703` | 2026-09-24 | IEA and ETSAP: convention names, register and assess the held briefs |
| `5762598` | `2d191cb` | 2026-09-24 | gov-usa: extract DOE, EPA and NETL sources; rename to the naming convention |
| `09758dc` | `cf711c8` | 2026-09-24 | Keep downloaded documents that yield no data in a background folder |
| `7efe0b5` | `fde99fd` | 2026-09-24 | Extract newly downloaded papers and reports; list documents still to get |
| `e23eb6c` | `821b74e` | 2026-09-24 | Remove Canadian calibration data outside the database's scope |
| `43ce44a` | `b3428cd` | 2026-09-23 | Legacy cement kilns, solid-fuel heaters and dryers, incremental cost basis |
| `a5a395c` | `312e5b4` | 2026-09-23 | Assignment review: re-home 201 examples, add 4 archetypes, correct hierarchy links |
| `108b87f` | `bd2b228` | 2026-09-23 | Read a source's generic /unit as its own service unit; record assignment review findings |
| `5ef7909` | `d0e3327` | 2026-09-23 | Wide view: drop the rows for end uses no archetype serves |
| `ca7d852` | `8e3ad54` | 2026-09-23 | Wide view lists every archetype and every end use |
| `62f3fda` | `a9b0070` | 2026-09-23 | Whole-plant costs for UKERC measures; re-home mis-mapped measure buckets |
| `32b9888` | `31acf49` | 2026-09-23 | Take steam-using processes off CHP; do not pool negative costs |
| `34b66ab` | `031c171` | 2026-09-23 | Set aside UKERC costs that need an efficiency factor |
| `cae6145` | `f667f97` | 2026-09-23 | Label derived duplicates; convert only with the source's own output factor |
| `b875d34` | `f5f3a44` | 2026-09-23 | Fold the candidate merges; one reduction-potential column; plain source-list counts |
| `46fa1db` | `6810f07` | 2026-09-22 | decisions.md: the open items the restructure leaves for review |
| `61acf42` | `a0a488e` | 2026-09-22 | A ratio printed without a unit pools as dimensionless |
| `42ff6e4` | `0ccbcf1` | 2026-09-22 | Build output does not depend on hash order |
| `9f4960d` | `5329583` | 2026-09-22 | Docs state the rules; the decision chain moves to archive/ |
| `56bebbb` | `44d3a75` | 2026-09-22 | Retire the roster pipeline; park the CIMS model inputs under compare/ |
| `cd20991` | `bed39d1` | 2026-09-22 | One build for the archetype database: build.py and its stages |
| `2c020e3` | `eca3f74` | 2026-09-22 | Records for the archetype database: archetypes, services, examples |
| `861c192` | `b647efb` | 2026-09-22 | build-source-list: split the ;-joined source-id on technology rows |
| `16e05d7` | `833b5ff` | 2026-09-22 | Adopt the design vocabulary in the harmonized layer |
| `bf4cd39` | `f6b9fb1` | 2026-09-22 | Schema and vocabulary for the design roster |
| `eb3d06f` | `0bb6971` | 2026-09-22 | Design crosswalk: device-first folds, every source context kept |
| `b6675e2` | `04c5647` | 2026-09-22 | Design crosswalk: target the CIMS hierarchy directly, down to the leaf |
| `127f74f` | `4b5b949` | 2026-09-22 | Canadian spelling in the vocabulary, names and our own prose |
| `20620c8` | `13d69e7` | 2026-09-22 | hierarchy_crosswalk: fail on an end use no hierarchy node reaches |
| `4d8609a` | `f9eb917` | 2026-09-22 | Reporting accounting proposal |
| `0ef1e47` | `238f1e7` | 2026-09-22 | Crosswalk from the harmonized roster to the design vocabulary |
| `99a02c6` | `e14ef51` | 2026-09-22 | Harmonize the design end uses with the CIMS hierarchy |
| `3c95a3b` | `bd08a1f` | 2026-09-22 | Design: sector end-use table and technology table |
| `8f91931` | `f9b9a28` | 2026-09-22 | Harmonized pipeline: aggregation rules, stable ids, basis and currency checks |
| `65fb662` | `ad1c82a` | 2026-09-22 | Regenerate the harmonized tables |
| `e3bfd1f` | `053a12b` | 2026-09-22 | Extractions: current parameter names and data fixes |
| `4fd535d` | `219232c` | 2026-09-22 | Currency conversion: deflate in the source currency, then exchange |
| `ae28740` | `1d9ff5b` | 2026-09-22 | Stop tracking Python bytecode |
| `5a44239` | `bb16808` | 2026-09-15 | .gitignore |
| `e7d5249` | `c3fd5d0` | 2026-09-09 | Add .gitattributes to normalize line endings |
