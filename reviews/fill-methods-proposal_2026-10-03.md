# Estimating missing archetype values: review and proposed methods (2026-10-03; redrafted 2026-10-04; reviewed against the 2026-10-09 build)

> **Implemented 2026-10-10.** Rulings 2026-10-09: materiality classes, pool minimums and judgement range rules as proposed; the entire fill completed, not a first batch; every check runnable without and with fills. What was built: `pipeline/fill.py` (grades sourced, identity, estimated, proxy, guess; the `not-applicable` marker; rules, then judgements, then rules), `records/fill/equipment-class.csv`, `fill-assumption.csv`, the rules in `fill-rule.csv`, 973 judgement drafts in `fill-judgement.csv`, `output/unfilled/`, `output/coverage.csv`. Result: every CIMS cell on every archetype holds a value or a marker except fossil combustion CO2 on 45 archetypes with a blank carriers cell (`database/reviews/carrier-proposals_2026-10-09.csv`) and on reformers, gasifiers and reactors by design. Design s6a states the rules now in force; this document is the reasoning behind them.

Scope: the parameters CIMS needs to characterise a technology — capex, fixed and variable O&M, energy use or efficiency, lifetime, annual output and TRL. Build reviewed: `database/harmonized/output/` at commit 7d7fed7 (2026-10-09), 491 archetypes (423 quantified, 53 estimated, 10 gap, 3 not pooled, 2 named).

Rulings carried in (Brad, 2026-10-04): the existing CIMS model-input values are not used in any way — not as proxies, class defaults or plant sizes; the database replaces them. Annual output from this database fills the CIMS `output` parameter. CIMS has a variable O&M field, so variable O&M is filled where it is a real and material cost, and folded into fixed O&M or ignored where it is real but small. A `proxy` grade, a not-applicable marker and judgement drafts are all wanted.

## 0. What changed between 2026-10-03 and 2026-10-09, and what it does to the proposal

Six days of sanity-check fixes, intakes, the naming and combination reviews, the wide-view restructure and the final-product-unit change have moved the ground under the first draft. The methods survive; several of their inputs and counts do not.

- **The archetype set is different.** 535 became 491 (merges, splits, renames; CHP with capture split out; solar and heat pumps split by tier). Every count below is recomputed. Status is cleaner: 10 gaps instead of 25.
- **Part of E3 is already built.** UKERC's efficiency buckets are now stored as savings and the variant's SEC is derived as base total × (1 − median member saving) (`pipeline/ukercsaving.py`, stage 7c; 34 derived). That is the bucket-saving rule for UKERC members. What remains for E3 is the same rule for variants whose saving comes from another source, or from the bucket definition.
- **The sibling rule is unit-free for lifetime, construction time and capacity factor** (ruling 2026-10-09). Missing lifetimes fell from 99 to 71 without a new rule; capacity factor now reaches 260 archetypes. L1 is a wider sibling rule, so it inherits this.
- **Efficiency-chp is gone.** CHP archetypes carry their total efficiency in `efficiency`; `efficiency_electricity` and `efficiency_heat` exist only on archetypes making both. E1 and E4 are written against `efficiency` and must respect the CHP label when inverting (a CHP total is not 100/SEC of heat).
- **Carriers are one consistent split per archetype** (stage 8a: electricity, steam, heat, fuel as shares of the total; named fuels as a sub-split of fuel). E2's inverse (SEC from emissions) and E1's carrier condition are now well-defined against that split.
- **Final-product units changed the cost basis of several families** (2026-10-09): biofuels per GJ, refining per m3, smelters per t metal, dryers per t dried product. Dryers lost 13 UKERC/Bataille capex rows given per GJ-yr, because no GJ/t sits in the same example; `dryer_direct-fired`, `dryer_solid-fuel`, `dryer_rotary-direct-fired`, `dryer_ceramic-hot-air`, `dryer_through-air` have no capex. This is a new, well-defined fill case (K0 below).
- **Secondary products.** Dual-output archetypes are classified by primary product with a negative CIMS service request for the secondary. No fill touches a secondary product; vom and energy rules read the primary unit only.
- **Assumed corrections exist** (`records/reference/source-correction.csv`, 2026-10-08): a value a source prints wrongly is taken on an assumed corrected basis, marked. That is a provenance class of its own and sits beside the proxy grade in the shading scheme (section 2).
- **The to-get list is closed out** (2026-10-07/08) and `unavailable.csv` records what cannot be had. K6's "targeted sources" lever is smaller than it was: the remaining gaps are more likely to be filled by judgement than by a document still to come, so the judgement pass carries more weight.
- **Hours-based lifetimes** now take species `stack` or `component`; lifetime fills must look only at the plant lifetime (blank target), which the rule already does.
- **Open items that interact with fills:** S89 (haul-truck SEC basis, t ore vs t material), the 23 per-t-water-evaporated rows set aside (food evaporator, lumber kiln, MVR), the SMR concentrated-capture design mix, and the open hierarchy requests (mine-water, metal-mine ventilation, light industrial). None blocks a rule; each marks an archetype whose filled value should be re-read once the item closes.

## 1. Where the database stands (2026-10-09)

Coverage counts archetypes with a central value of any grade. "Energy" means a specific energy consumption or an efficiency; "output" means a capacity or an annual output.

| Parameter | Have | Missing | Of the have: sourced / identity / estimated |
| - | - | - | - |
| capex | 283 | 208 | 239 / – / 44 |
| opex-fixed | 172 | 319 | 139 / – / 33 |
| opex-variable (or opex-total) | 123 | 368 | 89+28 / – / 17+3 |
| energy (SEC or efficiency) | 329 | 162 | 293+124 / 29 / – |
| lifetime | 420 | 71 | 220 / – / 200 |
| output (capacity or annual output) | 202 | 289 | 200+30 / – / – |
| trl | 491 | 0 | mostly "commercial", rest assessed or IEA-scaled |

The gaps are still concentrated: oil and gas (62 archetypes; 31 without capex, 43 without energy), non-ferrous metals (40; 24, 15) and mining (26; 20, 17) hold 75 of the 208 missing capex values and 75 of the 162 missing energy values. 111 archetypes have neither a cost nor an energy value. Heat supply, power generation, hydrogen, cement, biofuels and CO2 capture are nearly complete on costs.

## 2. Provenance: one addition to the grades

The four grades in design §6a (sourced, identity, estimated, guess) cover everything except a constant taken from an outside catalogue or handbook that is not extracted as a source of this database — a 3% O&M share, a 25-year process-plant life, a typical plant size from a sector benchmark. I propose a fifth grade, `proxy`, ranked between estimated and guess:

| Grade | Reached by | Shading |
| - | - | - |
| sourced | pooled examples | none (purple if an external factor; the source-correction marker where the value rests on an assumed correction) |
| identity | a definition or physical relation on the archetype's own values | blue |
| estimated | borrowed or scaled from another archetype, or a class rule fitted on this database's own values | orange |
| proxy | a class constant or stand-in value from a named outside catalogue or handbook, not extracted as a source | yellow |
| guess | a judgement with a range, rationale and author | red |

Every class constant lives in one new record, `records/fill/fill-assumption.csv` (id, parameter, class, value, low, high, applies-to, source-id, rationale, decided). Its sources are registered in `source-details_reference.csv`, as the conversion factors and currency series are, so the design's rule holds that reference data is not evidence about a technology. The wide view's `filled` column, the workbook shading and the `inputs` column then show what each cell rests on.

A second marker, `not-applicable`, closes a cell deliberately: the parameter does not characterise this archetype (the energy use of a leak-detection programme; the variable O&M of a boiler). It is written with a reason, counts as covered in the coverage report, and the CIMS exporter writes nothing for it.

## 3. Methods by parameter

Each method is a `fill-rule.csv` row with the usual back-test (run on cells that have a sourced value; the widen fraction set so about 90% fall inside the range). "Would fill" is counted against the 2026-10-09 build; rules run as a cascade, first hit wins, so counts for later rules are upper bounds.

### 3.1 Lifetime (71 missing)

The unit-free sibling rule has done what it can. The 71 left have no sibling with a sourced lifetime at all: annealing furnaces, melting furnaces (cupola, induction, reverberatory, crucible, twin-chamber), grinding mills, kraft and sulphite digesters, refineries (hydroskimming, conversion, deep-conversion, nickel matte, sugar beet), leaching vessels, converters, drilling rigs, chillers, mobile equipment (6), fans, turboexpanders, heat-recovery units.

- **L1 `est-class-lifetime`** (estimated). `records/fill/lifetime-class.csv` assigns each `equipment` term to a class: process plant and furnaces; boilers and fired heaters; turbines, engines and CHP; motors, pumps, fans and compressors; drives and controls; instruments and programmes; mobile equipment; wells and pipelines. The class central and range are fitted on this database — the median and span of sourced plant lifetimes across the class — so the rule is a wider sibling rule and the back-test checks it the same way. The classes the database populates (furnaces, mills, digesters, fans, chillers, refineries by analogy with upgraders and gas plants) cover roughly 55 of the 71.
- **L2 `proxy-class-lifetime`** (proxy) for classes the database does not populate: a published engineering life from a registered reference — the DEA technology catalogues for heat and process equipment, the EPA CHP catalogue for engines and turbines, the ETSAP briefs' stated lifetimes where we hold them, equipment-depreciation conventions for mobile equipment and drilling rigs. One row per class in `fill-assumption.csv`. Covers the rest, mobile equipment above all (6 archetypes, no sourced plant lifetime in the family; the hours-based lifetimes are now on species `stack`/`component` and can anchor a conversion at a stated utilisation).

### 3.2 Annual output (289 missing)

Annual output feeds CIMS `output` directly, so it needs a value on every archetype that serves a node. Three tiers.

- **O1 `id-annual-output-from-capacity`** (identity): annual-output = capacity × capacity-factor × 8760 (× 3.6 for MW to GJ; kt/yr × capacity-factor for t). Would fill 106 now (capacity and capacity factor present) and a further 66 where the capacity factor is estimated (those inherit grade estimated). The 2026-10-08 roll-in already merges a source's own annual output into the base column, so O1 sees the full set.
- **O2 `est-sibling-annual-output`** (estimated): the median annual output of siblings with the same equipment and discriminator, else the same equipment, and the same product unit (output is in product units, so here the unit must match, unlike the relaxed lifetime rule); range the siblings' span. Plant scale is set by the process and the product, not by the carrier or variant. Back-tested on archetypes with a sourced output.
- **O3 `proxy-typical-plant-size`** (proxy) for the rest: a typical Canadian unit size per end use from registered benchmark references, in `fill-assumption.csv`. The CIPEC benchmarking studies now held (steel, cement, pulp and paper, lime, mining) state typical plant capacities; NPRI and the federal GHGRP give facility-level emissions, and production = emissions / emissions per tonne gives a facility-scale median per sector; NRCan and StatCan capacity data cover refineries, upgraders, smelters and gas plants. For energy-service archetypes the unit size is the typical boiler, turbine or motor rating, which the ETSAP briefs and the EPA CHP catalogue give. One row per end use or equipment class, with source and derivation. Since the 2026-10-09 banding, an archetype that serves several end uses is repeated under each; it still has one annual output, and the row's end use is the primary one.
- **O4 judgement** where no benchmark exists (section 3.7).

Costs are per unit of annual capacity, so `fcc = capex × output` and an uncertain output does not move the cost per unit the model competes on; it sets the number of units in the stock and the scale that declining capital cost acts on. A typical size, graded honestly, is enough.

### 3.3 Fixed O&M (319 missing; 115 where a capex is present)

- **F1 `est-cost-ratio-opex-fixed`** — un-park it, with tighter pools: the share of capex pooled by equipment and product unit together, with at least 3 archetypes carrying both sourced; else by family with at least 5; else all. The 2026-10-01 back-test gave a typical error of ×1.7; pooling by product unit and reporting the pool's interquartile range as low–high should tighten it, and the back-test will say by how much. Would fill 115 now, and every archetype that later gains a capex.
- **F2 `proxy-class-om-share`** (proxy) where no pool reaches the minimum: a published fixed-O&M share of capex per class — 2–3% a year for boilers, heaters and power equipment (DEA catalogue, EPA CHP catalogue), 3–5% for process plant (NETL and IEAGHG costing conventions), 1–2% for wells and pipelines — one row per class in `fill-assumption.csv`.
- The 204 archetypes with neither capex nor O&M take an O&M only once a capex exists; O&M is never filled on its own.

### 3.4 Variable O&M (368 missing)

CIMS carries a variable O&M field, so the question is where variable non-fuel O&M matters. Energy is never in it: fuel and electricity go through the service request, including the negative request for a secondary product.

- **V1 `id-opex-variable-from-total`** (identity): opex-total − opex-fixed where a source gives the total only (31 archetypes carry an opex-total; those with a fixed O&M beside it qualify).
- **V2 materiality classes.** `records/fill/vom-class.csv` assigns each equipment term one of three classes, with the reason:
  - *material*: consumables and reagents are a real share of operating cost — electrolysis cells (electrodes, membranes), leaching and flotation vessels (reagents), capture units (solvent make-up), water and effluent treatment (chemicals), kilns and furnaces with refractory and catalyst replacement, reactors with catalysts, mobile equipment and haul trucks (tyres, parts, maintenance per operating hour), drilling rigs and fracturing fleets (consumables per metre), anaerobic digesters (feedstock handling);
  - *minor*: real but small — boilers, heaters, dryers, CHP, motors, pumps, fans, compressors, space conditioning, lighting;
  - *none*: no meaningful variable cost — programmes, controls, seals, pipeline liners, storage.
- **V3 `na-opex-variable-minor`**: for *minor* and *none* classes with no sourced value, the cell gets `not-applicable` with the reason "folded into fixed O&M" or "no variable cost", and the exporter writes no variable O&M.
- **V4 `est-cost-ratio-opex-variable`** (estimated) for *material* classes: opex-variable per unit of product = capex per unit of annual capacity × the median variable-to-capex ratio among same-equipment archetypes with both sourced (pool of 3 or more), else family. Back-tested like F1; expect a weak fit that stands in until a source or a judgement replaces it.
- **V5 judgement** for *material* classes with no pool, drawn where possible from held sources that state consumables separately (the capture-cost derivations, the Intergroup haul-truck study, the H2A workbooks, the EPA Natural Gas STAR PRO sheets, the refining handbooks taken in 2026-10-07).

### 3.5 Energy use and efficiency (162 missing: 95 per t, 34 per GJ, 28 per m3, 5 per m)

- **E1 `id-efficiency-from-sec`, re-enabled with a carrier condition** (identity). It was turned off because a pooled SEC with no carrier was not reliably the total input. With the carrier split now one consistent set of shares per archetype, the condition is checkable: GJ-product archetypes whose SEC total is backed by a split summing to it, and that are not CHP-labelled (a CHP total efficiency is not 100/SEC of heat). Would fill a few of the 34 GJ archetypes.
- **E2 `id-sec-from-emissions`** (identity): fuel SEC = emissions-combustion (CO2) / the CO2 factor of the named carrier, the inverse of `id-combustion-co2-from-fuel`, with the ECCC NIR factors. Only 5 candidates now; cheap to add.
- **E3 `est-bucket-saving`, generalised** (estimated): the UKERC stage already derives a variant's SEC from its base and the members' savings. Extend the same relation to the 23 variants whose base has energy but which have no UKERC saving: s is the variant's own sourced `emissions-reduction-potential` (40 of the 162 carry one), on the stated assumption that for a same-fuel measure the emission saving equals the energy saving; otherwise the bucket definition — moderate 8% (range 0–15%), strong 25% (range 15–40%) — in `fill-assumption.csv`. Back-tested on variants with both a sourced SEC and a sourced base SEC. The combination-review items S01–S05 were closed by the UKERC savings change; this rule writes nothing over a sourced cell.
- **E4 `est-sibling-efficiency`** (estimated), for GJ-product archetypes only: efficiency is set by the equipment class far more than by the carrier, so a direct heater, engine, turbine drive or fan takes the median sourced efficiency of siblings with the same equipment and discriminator, else the same equipment; range the siblings' span and at least ±10 points. E1 then gives an SEC. Not applied to per-tonne process archetypes, where a route change is the whole reason they are separate, and not from a CHP-labelled sibling to a heat-only one. Would fill about 15 of the 34 GJ archetypes (the reciprocating-engine, combustion-turbine, direct-heater and steam-reformer variants).
- **E5 `na-energy-not-characterising`** (marker): the methane-control archetypes on venting, fugitive and flaring nodes (16 of the 162) have a CIMS service request in t CH4 or 1000 m3 of gas, and the device's own energy use is negligible or is the gas it saves. These get `not-applicable` in the energy columns with the reason. Where a control does draw power — vapour-recovery, instrument-air and electric-drive reciprocating compressors — the value comes from E4 or a judgement using the Natural Gas STAR PRO sheets.
- **E6 `proxy-motor-class-efficiency`** (proxy): machine-drive archetypes distinguished by motor efficiency class take the IEC 60034-30 / NEMA Premium bands for the typical size range, registered as a reference. NEMA Premium now sits on `motor_induction-standard` (ruling 2026-10-07), so this covers the variable-speed and premium variants only, 2–3 archetypes.
- **E7 power-generation and storage archetypes** (wind turbine, PV with battery storage, small nuclear, solar concentrators, hydrogen pipeline and cavern): the characterising quantity is not an SEC but a capacity factor, a round-trip efficiency or a transport loss. These get `not-applicable` for SEC with the reason, and the capacity factor or efficiency they do have is what the exporter uses.
- What remains after E1–E7 is around 100 per-tonne and per-m3 process archetypes in oil and gas, mining, non-ferrous and chemicals (leaching vessels, froth treatment, crystallisers, bioleaching, upgrader reactors, converters, paste plants). For these an estimated SEC would be a number with no basis. With the to-get list closed, the realistic path is a judgement with a wide range and a named analogue (section 3.7), citing the CIPEC and LBNL/Worrell sector studies now held for the process-step energy use where they give one.

### 3.6 Capex (208 missing)

This is where estimation runs out soonest. Of the 208, 12 are variants whose host has a capex, 5 carry a levelized cost, and the rest share at most an equipment term with a priced archetype. The 2026-10-01 ruling that costs are not copied between siblings without a source that prices both is right: a sibling kiln or reactor on a different route is not a cost proxy.

- **K0 `id-capex-per-gj-to-per-t`** (identity, class internal): new since the final-product-unit change. A capex given per GJ-yr of heat output on a per-tonne archetype (the five dryers, and any future case) goes per t-yr with the archetype's own pooled SEC, under the same-GJ condition of design §5 — same stream (the heat the dryer delivers), same side (output) and same scope (the dryer). The design allows the conversion only with the same example's SEC; this extends it to the archetype's pooled SEC with class `internal`, exactly as the efficiency bridge already does for input-rated costs. Grade identity with the internal factor named, or estimated if you would rather not call a pooled factor an identity. Recovers the 13 set-aside rows and gives capex to 5 dryer archetypes.
- **K1 `est-modifier-ratio-capex`** — un-park (fills 4 at the last test; re-test on the new set).
- **K2 `est-bucket-increment-capex`** (estimated) as the fallback for variants whose host has a capex but no same-source pair: host capex × (1 + i), with i the median incremental-to-host ratio from this database's own set-aside measure costs (`set-aside-host-cost.csv` against each host's capex), pooled by bucket; low and high the pool's quartiles. Fills the 12 variants with a priced host today, and every later one.
- **K3 `est-capex-from-levelized`** (estimated): invert a levelized cost with the study's own discount rate and lifetime (design §5: replicate the study's rate) and the archetype's O&M and fuel cost where known: capex = (LCO − fuel − O&M) / CRF, per unit of annual capacity. 5 candidates; expect 2–3 fills, on prospective technologies where any anchored number is valuable. The inputs column names every assumption.
- **K4 `proxy-cost-scaling`** (proxy): where a registered reference prices the same equipment at a different scale or duty, scale with a cost-capacity exponent (0.6–0.7 for process plant, fitted on this database's own multi-size sources where possible). Each application is a row in `fill-assumption.csv` naming the stand-in and the exponent; a small set (crystallisers from evaporators, converters from furnaces of the same duty).
- **K5 judgement drafts.** The remaining block, about 180 today, is the one this question is really about, and with the to-get list closed it is the main lever. I draft `fill-judgement.csv` rows in batches by family, each with central, low, high, a rationale naming the analogue and the reasoning, and author `claude-draft`; you review and set status. The build already refuses a guess without a range and rationale, and drops it the moment a sourced or calculated value appears. A first batch of 20 to agree the level of detail and range widths.
- **K6 sources** still matter where `unavailable.csv` does not close the door: the dense blocks are oil sands extraction and upgrading, produced-water handling, drilling, comminution and leaching, converters and paste plants. A K5 guess marks each as a placeholder; the recompute-on-build rule retires it without an edit when a source lands.

Abatement-cost inversion is not proposed: it needs the baseline's cost and emissions and the study's own framing, and the result is a delta, which design §2 keeps out.

### 3.7 Judgement drafts: ground rules

- one row per archetype and parameter; central, low and high in the archetype's target unit (the final-product unit of 2026-10-09), with low–high at least a factor of two apart on a cost and ±30% on an energy use unless the rationale says why narrower;
- the rationale names the analogue (an archetype in this database, a held source's figure for a related step, or a standard engineering relation) and the step from it to the number, in one or two sentences a reviewer can check;
- a `basis` column: `analogue-archetype`, `held-source-figure`, `engineering-relation` or `experience`, so the weakest guesses are findable;
- `author` = `claude-draft` until you accept; `status` = draft, accepted, changed or rejected; a rejected row stays with the reason so it is not redrafted;
- a judgement on an archetype with an open sanity-check item (S89 and the others in section 0) says so in its rationale, so it is re-read when the item closes;
- drafted in family batches of about 20, costs first (the largest block), then process energy use, then plant sizes and material variable O&M.

### 3.8 TRL (0 missing)

Every archetype has a TRL, and the availability rule maps it to `available`. Two tidy-ups rather than fills: `trl-basis` reads "commercial" on most archetypes, an assertion rather than a citation (fine for a dry kiln; worth a source line for anything at 7–9); and the availability rule needs a base year (open since 2026-09-30) — the build year, written into the hierarchy stamp.

## 4. Expected position after the cascade

Rough, against the 2026-10-09 build, before any new source or judgement:

| Parameter | Missing now | Identity / estimated | Proxy or marker | Left for judgement or source |
| - | - | - | - | - |
| lifetime | 71 | ~55 (L1) | ~16 (L2) | 0 |
| annual output | 289 | ~172 (O1) + sibling (O2) | benchmark sizes (O3) | small remainder (O4) |
| opex-fixed | 319 | 115 (F1/F2) | – | 204, which follow capex |
| opex-variable | 368 | ~10 (V1) + V4 where pools exist | ~270 not-applicable (V3) | ~50–80 material classes (V5) |
| energy | 162 | ~45 (E1–E4) | ~16 n/a (E5), ~10 n/a (E7), 2–3 (E6) | ~90, mostly process SEC |
| capex | 208 | ~20 (K0–K3) | a few (K4) | ~180 (K5) |

Capex and process energy use remain the two parameters that will not reach every archetype without the judgement pass.

## 5. Implementation order

1. Rules that need no outside data: K0, O1, O2, V1, E1 (carrier condition, CHP guard), E2, E3 (generalised), E4, F1 (re-tuned), K1, K2, K3, L1, V4. One build, back-tests reported.
2. The `proxy` grade and `not-applicable` marker in `fill.py`, the workbook shading and `design.md` §6a; `vom-class.csv`, `lifetime-class.csv` and `fill-assumption.csv` with the class constants (L2, F2, O3, E6, bucket savings), each cited to a registered reference; V3, E5 and E7 markers applied.
3. Judgement drafts: first batch of 20 capex rows from oil and gas and mining to agree the format; then the remaining capex, process energy, plant sizes and material variable O&M in batches.
4. A coverage report in the build (`output/coverage.csv`: archetype × parameter × grade or marker) so the red and yellow cells are findable by family, and the next source intake is driven by where they sit.

Decisions still open: whether K0 is graded identity (pooled factor, class internal) or estimated; the materiality classes in `vom-class.csv`; minimum pool sizes for F1 and V4; and the range-width rules for judgements in 3.7.
