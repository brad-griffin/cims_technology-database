# Estimating missing archetype values: review and proposed methods (2026-10-03, redrafted 2026-10-04)

Scope: the parameters CIMS needs to characterise a technology — capex, fixed and variable O&M, energy use or efficiency, lifetime, annual output and TRL. Build reviewed: `data/harmonized/output/` as of 2026-10-03, 535 archetypes (438 quantified, 56 estimated, 8 named, 8 not pooled, 25 gap).

Rulings taken into this redraft (Brad, 2026-10-04): the existing CIMS model-input values are not used in any way — not as proxies, not as class defaults, not to seed plant sizes; the database replaces them. Annual output from this database fills the CIMS `output` parameter. CIMS does have a variable O&M field, so variable O&M is filled where it is a real and material cost, and folded into fixed O&M or ignored where it is real but small. A `proxy` grade, a not-applicable marker and judgement drafts are all wanted.

## 1. Where the database stands

Coverage counts archetypes with a central value of any grade. "Energy" means a specific energy consumption, an efficiency or a CHP efficiency; "output" means a capacity or an annual output.

| Parameter | Have | Missing | Of the have: sourced / identity / estimated |
| - | - | - | - |
| capex | 277 | 258 | 242 / – / 35 |
| opex-fixed | 174 | 361 | 148 / – / 26 |
| opex-variable (or opex-total) | 117 | 418 | 92+22 / – / 14+2 |
| energy (SEC, efficiency, CHP eff.) | 353 | 182 | 306+137+11 / 31 / – |
| lifetime | 436 | 99 | 227 / – / 210 |
| output (capacity or annual output) | 192 | 343 | 190+30 / – / – |
| trl | 535 | 0 | 318 "commercial", rest assessed or IEA-scaled |

The gaps are concentrated. Oil and gas (78 archetypes; 47 without capex, 57 without energy), mining (32; 27, 20) and non-ferrous metals (42; 26, 17) account for 100 of the 258 missing capex values and 94 of the 182 missing energy values. Heat supply, power generation, hydrogen, cement and CO2 capture are nearly complete. 135 archetypes have neither a cost nor an energy value; 33 of those are gaps or named-only. For that block the honest method is often a targeted source rather than an estimate, and the proposals say where that line falls.

## 2. Provenance: one addition to the grades

The four grades in design §6a (sourced, identity, estimated, guess) cover everything except a constant taken from an outside catalogue or handbook that is not extracted as a source of this database — a 3% O&M share, a 25-year process-plant life, a typical plant size from a sector benchmark. I propose a fifth grade, `proxy`, ranked between estimated and guess:

| Grade | Reached by | Shading |
| - | - | - |
| sourced | pooled examples | none (purple if an external factor) |
| identity | a definition or physical relation on the archetype's own values | blue |
| estimated | borrowed or scaled from another archetype, or a class rule fitted on this database's own values | orange |
| proxy | a class constant or stand-in value from a named outside catalogue or handbook, not extracted as a source | yellow |
| guess | a judgement with a range, rationale and author | red |

Every class constant lives in one new record, `records/fill/fill-assumption.csv` (id, parameter, class, value, low, high, applies-to, source-id, rationale, decided). Its sources are registered in `source-details_reference.csv`, the same way the conversion factors and currency series are, so the design's rule holds that reference data is not evidence about a technology. The wide view's `filled` column, the workbook shading and the `inputs` column then show what each cell rests on, and a reader can sort by grade and see which numbers are sourced, which follow from them, and which we chose.

A second marker, `not-applicable`, closes a cell deliberately: the parameter does not characterise this archetype (the energy use of a leak-detection programme; the variable O&M of a boiler). It is written with a reason, counts as covered in the coverage report, and the CIMS exporter writes nothing for it.

## 3. Methods by parameter

Each method is a `fill-rule.csv` row with the usual back-test (run on cells that have a sourced value; the widen fraction set so about 90% fall inside the range). "Would fill" is counted against the 2026-10-03 build; rules run as a cascade, first hit wins, so counts for later rules are upper bounds.

### 3.1 Lifetime (99 missing)

The sibling rule has done what it can; the remaining 99 have no sibling with a sourced lifetime (32 oil and gas, 14 mining, 7 pulp and paper, 6 each in mobile equipment, food, other industry and non-ferrous).

- **L1 `est-class-lifetime`** (estimated). A table `records/fill/lifetime-class.csv` assigns each `equipment` term to a class: process plant and furnaces; boilers and fired heaters; turbines, engines and CHP; motors, pumps, fans and compressors; drives and controls; instruments and programmes; mobile equipment; wells and pipelines. The class central and range are fitted on this database — the median and span of sourced lifetimes across the class — so the rule is a wider sibling rule, and the back-test checks it the same way. Would fill the classes the database already populates, around 70 of the 99.
- **L2 `proxy-class-lifetime`** (proxy) for classes the database does not populate: a published engineering life from a registered reference — the Danish Energy Agency technology catalogues for heat and process equipment, the EPA CHP catalogue for engines and turbines, the ETSAP briefs' stated lifetimes where we hold them, equipment-depreciation conventions for mobile equipment and wells. One row per class in `fill-assumption.csv`. Would fill the rest.

### 3.2 Annual output (343 missing)

Annual output feeds CIMS `output` directly, so it needs a value on every archetype that serves a node. Three tiers.

- **O1 `id-annual-output-from-capacity`** (identity): annual-output = capacity x capacity-factor x 8760 (x 3.6 for MW to GJ; kt/yr x capacity-factor for t). Would fill 84 now, and a further 78 once the sibling capacity-factor rule supplies the factor (those inherit grade estimated).
- **O2 `est-sibling-annual-output`** (estimated): the median annual output of siblings with the same equipment and discriminator, else the same equipment, and the same product unit; range the siblings' span. Plant scale is set by the process and the product, not by the carrier or variant, which is the same reasoning as the sibling lifetime rule, and a variant of a kiln serves the same plant as the kiln. Back-tested on the archetypes with a sourced output. Would fill most of the per-tonne process variants.
- **O3 `proxy-typical-plant-size`** (proxy) for the rest: a typical Canadian unit size per node from registered benchmark references, in `fill-assumption.csv`. The Canadian sources already in hand or on the to-get list cover much of it: the CIPEC benchmarking studies (steel, cement, pulp and paper, lime, mining) state typical plant capacities; NPRI and the federal GHGRP give facility-level emissions, and production = emissions / emissions per tonne (the Hotmaps method in the 2026-10-02 review) gives a facility-scale median per sector; NRCan and StatCan capacity surveys cover refineries, upgraders, smelters and gas plants. For energy-service archetypes the unit size is the typical boiler, turbine or motor rating per node, which the ETSAP briefs and the EPA CHP catalogue give. One row per node or equipment class, with the source and the derivation.
- **O4 judgement** where no benchmark exists: a guessed size with a range, in `fill-judgement.csv`, following section 3.7.

Costs in the database are per unit of annual capacity, so `fcc = capex x output` and an uncertain output does not move the cost per unit the model competes on. It does set the number of units in the stock and the scale that declining capital cost acts on, which is why a typical size, graded honestly, is enough.

### 3.3 Fixed O&M (361 missing; 107 where a capex is present)

- **F1 `est-cost-ratio-opex-fixed`** — un-park it, with tighter pools: the share of capex is pooled by equipment and product unit together (a share per tonne and a share per GJ behave differently), with at least 3 archetypes carrying both sourced; else by family with at least 5; else all. The 2026-10-01 back-test gave a typical error of x1.7, which is why it was parked; pooling by product unit and reporting the pool's interquartile range as low–high rather than its extremes should tighten it, and the back-test will say by how much. Would fill 107 now, and every archetype that later gains a capex.
- **F2 `proxy-class-om-share`** (proxy) where no pool reaches the minimum: a published fixed-O&M share of capex per class — 2–3% a year for boilers, heaters and power equipment (DEA catalogue, EPA CHP catalogue), 3–5% for process plant (NETL and IEAGHG costing conventions), 1–2% for wells and pipelines — one row per class in `fill-assumption.csv`.
- The 254 archetypes with neither capex nor O&M take an O&M only once a capex exists; O&M is never filled on its own.

### 3.4 Variable O&M (418 missing)

CIMS carries a variable O&M field, so the question is where variable non-fuel O&M matters. Energy is never in it: fuel and electricity go through the service request.

- **V1 `id-opex-variable-from-total`** (identity): opex-total − opex-fixed, where a source gives the total only (9 archetypes).
- **V2 materiality classes.** A table `records/fill/vom-class.csv` assigns each equipment term one of three classes, with the reason:
  - *material*: consumables and reagents are a real share of operating cost — electrolysis cells (electrodes, membranes), leaching and flotation vessels (reagents), capture units (solvent make-up), water and effluent treatment (chemicals), kilns and furnaces with refractory and catalyst replacement, reactors with catalysts, mobile equipment and haul trucks (tyres, parts, maintenance per operating hour), drilling rigs and well services (consumables per metre), anaerobic digesters (feedstock handling);
  - *minor*: real but small — boilers, heaters, dryers, CHP, motors, pumps, fans, compressors, space conditioning, lighting;
  - *none*: no meaningful variable cost — programmes, controls, seals, pipeline liners, storage.
- **V3 `na-opex-variable-minor`**: for *minor* and *none* classes with no sourced value, the cell gets `not-applicable` with the reason "folded into fixed O&M" or "no variable cost", and the exporter writes no variable O&M. A guessed small number would add a red-graded value the model would not distinguish from zero.
- **V4 `est-cost-ratio-opex-variable`** (estimated) for *material* classes: opex-variable per unit of product = capex per unit of annual capacity x the median variable-to-capex ratio among same-equipment archetypes with both sourced (pool of 3 or more), else family. Back-tested like F1. Expect a weak fit; it stands in until a source or a judgement replaces it.
- **V5 judgement** for *material* classes with no pool: a range and rationale per archetype in `fill-judgement.csv` (reagent cost per tonne of ore, solvent make-up per tonne CO2, tyre and maintenance cost per tonne hauled), drawn where possible from sources already held that state consumables separately (the capture-cost derivations, the Intergroup haul-truck study, the H2A workbooks, the EPA Natural Gas STAR PRO sheets).

### 3.5 Energy use and efficiency (182 missing)

The 182 fall into recognisable groups, and the method differs by group.

- **E1 `id-efficiency-from-sec`, re-enabled with a carrier condition** (identity). It was turned off because a pooled SEC with no carrier is not reliably the total input: the 7% motor and 154% reformer came from `not-stated` and partial-carrier rows. Restricted to GJ-product archetypes whose SEC is a single named carrier (or `total`) covering the whole input, it is sound. Would fill a handful of the 46 GJ archetypes.
- **E2 `id-sec-from-emissions`** (identity): fuel SEC = emissions-combustion (CO2) / the CO2 factor of the named carrier, the inverse of `id-combustion-co2-from-fuel`, with the same ECCC NIR factors. Would fill up to 10.
- **E3 `est-bucket-saving`** (estimated): a variant's SEC = its host's SEC x (1 − s). Where the variant carries a sourced `emissions-reduction-potential` (29 of the 182 do), s is that value, on the stated assumption that for a same-fuel measure the emission saving equals the energy saving; otherwise s is the bucket's own definition — moderate 8% (range 0–15%), strong 25% (range 15–40%) — recorded in `fill-assumption.csv`. Back-tested on variants that have both a sourced SEC and a sourced host SEC. Would fill 19 variants once their hosts have energy. The four archetypes the combination review flagged (S01–S04, variants with a higher SEC than their base) stay on the sanity-check list; this rule does not touch sourced cells.
- **E4 `est-sibling-efficiency`** (estimated), for GJ-product archetypes only: efficiency is set by the equipment class far more than by the carrier, so a dryer, direct heater, fan or engine takes the median sourced efficiency of siblings with the same equipment and discriminator, else the same equipment; range the siblings' span and at least ±10 points. E1 then turns it into an SEC. Costs are not copied between siblings; efficiency is the one quantity that is nearly invariant across them. Not applied to per-tonne process archetypes, where a route change is the whole reason they are separate. Would fill about 25 of the 46 GJ archetypes.
- **E5 `na-energy-not-characterising`** (marker): the methane-control archetypes on venting, fugitive and flaring nodes (17 of the 182, plus some in gas processing) have a CIMS service request in t CH4 or 1000 m3 of gas, and the device's own energy use is negligible or is the gas it saves. These get `not-applicable` in the energy columns with the reason. Where a control does draw power — vapour-recovery, instrument-air and electric-drive reciprocating compressors — the value comes from E4 or from a judgement using the EPA Natural Gas STAR PRO sheets already held.
- **E6 `proxy-motor-class-efficiency`** (proxy): machine-drive archetypes distinguished by motor efficiency class (premium-efficiency, variable-speed) take the IEC 60034-30 / NEMA premium efficiency bands for the typical size range, registered as a reference. Covers 2–4 archetypes but with a standard everyone recognises.
- What remains after E1–E6 is mostly per-tonne process archetypes in mining, non-ferrous, chemicals and oil sands (leaching vessels, froth treatment, crystallisers, bioleaching, upgrader reactors), around 80–100. For these an estimated SEC would be a number with no basis; the options are a targeted source (the CIPEC benchmarking reports and the LBNL/Worrell sector studies state process-step energy use and are extractable, not proxies) or a judgement with a wide range and a named analogue (section 3.7).

### 3.6 Capex (258 missing)

This is where estimation runs out soonest. Of the 258, only 8 are variants whose host has a capex, 8 carry a levelized cost, 13 carry an abatement cost, and 33 are gaps or named-only. 207 share an equipment term with a priced archetype, but the 2026-10-01 ruling that costs are not copied between siblings without a source that prices both is right: a sibling kiln or reactor on a different route is not a cost proxy.

- **K1 `est-modifier-ratio-capex`** — un-park (fills 4; back-test 9/10 inside).
- **K2 `est-bucket-increment-capex`** (estimated) as the fallback for variants whose host has a capex but no same-source pair: host capex x (1 + i), with i the median incremental-to-host ratio from this database's own set-aside measure costs (`set-aside-host-cost.csv` against each host's capex), pooled by bucket; low and high the pool's quartiles. Fills the 8 variants with a priced host today, and every later one.
- **K3 `est-capex-from-levelized`** (estimated): invert a levelized cost with the study's own discount rate and lifetime (design §5 says to replicate the study's rate) and the archetype's O&M and fuel cost where known: capex = (LCO − fuel − O&M) / CRF, per unit of annual capacity. 8 candidates; most will fail for want of the study's fuel price, so expect 3–5 fills, but these are prospective technologies (electric plasma kiln, CO2-to-DME, indirect calciner) where any anchored number is valuable. The inputs column names every assumption.
- **K4 `proxy-cost-scaling`** (proxy): where a registered reference prices the same equipment at a different scale or duty, scale with the cost-capacity exponent (0.6–0.7 for process plant, fitted on this database's own multi-size sources where possible, as the Hotmaps review suggested). This is a conversion of a stand-in, not a sibling copy, and it is only as good as the stand-in; it applies to a small set (crystallisers from evaporators, converters from furnaces of the same duty) and each application is a row in `fill-assumption.csv` naming the stand-in and the exponent.
- **K5 judgement guesses.** The remaining block, roughly 200 today, is the one this question is really about. I draft `fill-judgement.csv` rows for them in batches by family, each with central, low, high, a rationale that names the analogue and the reasoning (a plunger lift is a few thousand dollars a well; a crystalliser is priced like an evaporator of the same duty; a Peirce-Smith converter is a small share of smelter capital), and author `claude-draft`; you review and set status to accepted, changed or rejected, and `author` becomes you on acceptance. The build already refuses a guess without a range and rationale, and drops it the moment a sourced or calculated value appears. A first batch of 20 to agree the level of detail and how wide the ranges should be.
- **K6 targeted sources, not estimates**, for the dense blocks: oil and gas (oil sands extraction, upgrading reactors, produced-water handling, drilling), mining (comminution, leaching, haulage variants), non-ferrous (converters, paste plants, electrolysis cells). The to-get list already names some; the EMRG library sources held back on 2026-10-03 (ETSAP, EPA wastewater, ORNL CHP) cover other families. A K5 guess marks these as placeholders until a source lands; the recompute-on-build rule means the guess disappears without an edit.

Abatement-cost inversion (13 cells) is not proposed: it needs the baseline's cost and emissions and the study's own framing, and the result is a delta, which design §2 keeps out.

### 3.7 Judgement drafts: how they are made

Since you want them, the ground rules I propose for `fill-judgement.csv`, so that a guess is as transparent as an estimate:

- one row per archetype and parameter; central, low and high in the archetype's target unit, with low–high at least a factor of two apart on a cost and ±30% on an energy use unless the rationale says why narrower;
- the rationale names the analogue (an archetype in this database, a held source's figure for a related step, or a standard engineering relation) and the step from it to the number, in one or two sentences a reviewer can check;
- a `basis` column: `analogue-archetype`, `held-source-figure`, `engineering-relation` or `experience`, so the weakest guesses are findable;
- `author` = `claude-draft` until you accept; `status` = draft, accepted, changed or rejected; a rejected row stays with the reason so it is not redrafted;
- drafted in family batches of about 20, costs first (the largest block), then process energy use, then plant sizes and material variable O&M.

### 3.8 TRL (0 missing)

Every archetype has a TRL, and the availability rule maps it to `available`. Two points to tidy rather than fill: `trl-basis` reads "commercial" on 318 archetypes, an assertion rather than a citation (fine for a dry kiln; worth a source line for anything at 7–9); and the availability rule needs a base year (open since 2026-09-30) — I suggest the build year, written into the hierarchy stamp.

## 4. Expected position after the cascade

Rough, against the 2026-10-03 build, before any new source:

| Parameter | Missing now | Identity / estimated | Proxy or marker | Left for judgement or source |
| - | - | - | - | - |
| lifetime | 99 | ~70 (L1) | ~29 (L2) | 0 |
| annual output | 343 | ~162 (O1) + sibling (O2) | benchmark sizes (O3) | small remainder (O4) |
| opex-fixed | 361 | 107 (F1/F2) | – | 254, which follow capex |
| opex-variable | 418 | 9 (V1) + V4 where pools exist | ~300 not-applicable (V3) | ~50–80 material classes (V5) |
| energy | 182 | ~60 (E1–E4) | ~17 n/a (E5), 2–4 (E6) | ~90, mostly process SEC |
| capex | 258 | ~15 (K1–K3) | a few (K4) | ~200 (K5 drafts; K6 sources) |

Capex and process energy use are the two parameters where every archetype will not get a value without the judgement pass, and where new sources will keep replacing judgements for some time. Everything else closes with rules and a small number of cited constants.

## 5. Implementation order

1. Rules that need no outside data: O1, O2, V1, E1 (carrier condition), E2, E3, E4, F1 (re-tuned), K1, K2, K3, L1, V4. One build, back-tests reported.
2. The `proxy` grade and `not-applicable` marker in `fill.py`, the workbook shading and `design.md`; `vom-class.csv`, `lifetime-class.csv` and `fill-assumption.csv` with the class constants (L2, F2, O3, E6, bucket savings), each cited to a registered reference; V3 and E5 markers applied.
3. Judgement drafts: first batch of 20 capex rows from the oil-and-gas and mining families for review of the format; then the remaining capex, process energy, plant sizes and material variable O&M in batches.
4. Refresh `to-get.csv` with the families where judgements stand in for sources, so the queue is driven by where the red cells are.

Decisions still open: the materiality classes in `vom-class.csv` (I propose them; you rule), the minimum pool sizes for F1 and V4, and the width rules for judgements in 3.7.
