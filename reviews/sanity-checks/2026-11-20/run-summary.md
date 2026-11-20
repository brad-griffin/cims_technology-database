# Sanity check, 2026-11-20, with Seton Stiebert's review

This run covers the build after today's source intake (commit 7c0d267), Seton's 12 cell comments, and his three general questions. Seton reviewed the heat, cement, steel, and chemicals sectors. His file is `reviews/expert-reviews/wide-view_whole-database - Seton Stiebert Review Nov 20, 2026.xlsx`. He added the comments in column B, plus ratio columns EI-ER (high over low for capacity, capex, and levelized cost).

**State:** the build, `--check`, `check_manifest.py`, and `check_names.py` all pass. The 2026-11-07 internal-consistency check found 78 findings. Two were new, and both came from today's intake. I fixed both (section 1), and the rerun has 76 findings, all covered by earlier rulings. Nothing in this run is committed.

**Files in this folder:**
- `spread_analysis.py`, which writes `spread-by-archetype.csv`, `capex-scale.csv`, and `capex-basis-mix.csv`
- `levelized_compare.py`, which writes `levelized-compare.csv`
- `reprint_check.py`, which writes `identical-values.csv`
- `internal-consistency.csv`

## 1. Fixed in this run (from the intake)

| id | Archetype | What was wrong | Fix |
| - | - | - | - |
| IC001 | reactor_hydrotreating-lipids | Efficiency was 66% (DEA's jet case, top-ranked from only two examples). Energy use plus feed from the new median SEC (0.054 GJ/GJ, now with Xu 2022) gives 1.22 GJ/GJ, which means 82%. | Added an `eff-identity` row to `efficiency-fix.csv`. Efficiency is now 81.8%, between DEA's diesel case (85%) and Xu (about 83%). |
| IC002 | transesterification-unit_acid-catalyzed | Xu's high-FFA plants burn natural gas, but natural gas was not in the archetype's carrier list. | Added natural-gas to `carriers` in `archetype.csv`. |

**Intake effects worth knowing:**
- **HEFA (reactor_hydrotreating-lipids):** energy use fell from 0.375 to 0.054 GJ/GJ. The old value was DEA's jet case alone, and it counted 0.18 GJ/GJ of lipid feed going to co-products as energy. The new value is a median of 3 examples.
- **Solid-sorbent DAC:** the capacity median fell from 360 to 182 kt/yr, because Sievert adds Orca (4 kt/yr), an actual plant. This follows the ruling of 2026-11-12 (actual facilities over reference plants).
- **Liquid-solvent DAC:** the sourced levelized cost rose from 367 to 456 CAD/t. Sievert's figure is per t **net removed** and includes transport and storage, so it is not on the captured basis. See question 3 and S176.

## 2. Seton's general questions

### Q1. Wide ranges, outliers, and weighting the central value

**What the data show:**
- **Capex:** across 134 archetypes with 3 or more capex examples, 59 have a high/low ratio above 5 and 31 above 10. But only 6 have an interquartile ratio (p75/p25) above 5, and 19 above 3.
  - The wide ranges come from a few extreme examples. The middle of each pool is fairly tight.
  - The wide view's `_low` and `_high` columns show the extremes (the full min-max), which makes the spread look worse than it is.
- **Trimming outliers barely moves the central value.** Removing values beyond 1.5 times the interquartile range changes the capex median by more than 25% for only 4 of the 134 archetypes. The median is already robust to outliers.
- **Capacity is where the spread is real.** 29 of 101 archetypes have a capacity interquartile ratio above 5. The examples range from small packaged units to utility-scale plants.
- **Scale effects in capex are weak in the sources:**
  - Only 29 archetypes have 5 or more examples that give both capex and capacity.
  - Their fitted scale exponent has a median of 0.89 (0.6-0.7 is the textbook value).
  - The fit explains more than 30% of the variance for only 38% of them. Differences in cost basis, region, and year swamp the scale effect.
- **Boiler_fuel-fired, Seton's example:**
  - 33 capex examples, from 1.1 to 53.9 CAD per GJ/yr (a ratio of 50). The interquartile range is 3.3-12.6, and the median is 7.1 in the analysis pool (7.44 in the archetype).
  - Only 9 of the 33 examples state a capacity. Weighting those 9 by capacity gives 19.8, but that result rests on one 290 MW captive power-and-steam plant (IEAGHG 2013).
  - Capacity weighting is not workable when most examples give no size.
  - The spread also comes from mixed pooling. The pool includes hydrogen boilers (Element Energy, MPP) and the captive power plant. Without them the median is 5.9 (n=29). See S177.

**Answer for Seton:**
- We do not drop outliers. The median already resists them, and trimming would change little.
- Weighting the examples by their own capacity is not workable: most examples give no size, and the few that do give an unstable result.
- To make the central value represent Canadian stock, we take the size from Canadian facilities. We already do this for steel, cement, chemicals, and LNG (GEM rulings, 2026-11-12).
- Weighting the stock itself, where large units dominate the heat delivered, belongs in the CIMS share calibration, not in the archetype's central value.

**Proposals (rulings needed, S172-S174):**
- **S172: show the interquartile range, not min-max.** In the wide view, `_low`/`_high` would become p25/p75 where n is 4 or more, with the full range kept in the long tables. This is a display change; the central values do not move.
- **S173: size the archetypes that are sensitive to scale from Canadian stock.** This covers boilers, CHP, heat pumps, and compressors. Their capacity would come from Canadian facility data (GHGRP or CIEEDAC boiler sizes), and the examples' capex would be scaled to that size with a stated exponent (0.7 by default, the archetype's own fit where r² is at least 0.3).
  - The alternative is to split size classes (packaged and field-erected boilers).
- **S174: flag wide pools in the workbook.** Shade an archetype whose capex interquartile ratio is above 3 (19 archetypes), so reviewers see where the central value is weak.

### Q2. What capex means: equipment or whole plant

**What the column means:**
- Capex is the overnight capital cost per unit of capacity, on the example's own cost basis.
- The basis can be equipment, installed, total-plant, or overnight, and examples on different bases are pooled together.
- 26 of 252 capex pools mix equipment-only examples with installed or plant examples (list in `capex-basis-mix.csv`). Among them are boiler_fuel-fired, boiler_solid-fuel, the electrolyzers, and heat-pump_industrial.

**Our intention:**
- Capex should be the full installed cost of a new unit (equipment, civil works, erection, engineering, and owner's costs; no land). CIMS chooses new capacity, so equipment-only costs would understate it.
- Equipment-only examples should be brought up to an installed basis before they are pooled. Haas 2006 shows the size of the gap: installation was 200% of the equipment cost.

**The precalciner kiln (Seton's row 204):**
- The central capex is 492 CAD per t clinker-yr, from 19 examples, which is about 492 million CAD for a 1 Mt/yr line. Seton is right that this is a whole-plant cost.
- Nearly every example is total-plant or installed.
- Several are **whole cement plants**, from raw-material preparation to grinding and packing: IEAGHG 2008, the IEAGHG/Gardarsdottir reference plant, the ETSAP IEA reference plant, Vattenfall, and NEDO.
- The archetype's scope, by Brad's ruling of 2026-11-05 (IM14), is the clinker line: raw-meal preparation to the cooler. Finish grinding sits at its own node (grinding-mill_vertical-roller, 34 CAD per t-yr).
- So the cost of the grinding mill is counted twice in the cement chain.

**Two mapping problems in the same pool:**
- The four UK TIMES fluidized-bed kiln rows (598 and 617) are not precalciner kilns.
- Two UK TIMES figures are pooled twice: 598.39 from Bataille and UKERC, and 854.84 from Bataille and ECRA via UKERC.

**Proposals:**
- **S175: put the cement-plant examples on the clinker-line scope.** Use the existing capital-share rule in reverse: subtract the grinding, packing, and dispatch share, taken from the cost breakdowns in IEAGHG 2008 and Vattenfall.
- **S177: move the fluidized-bed rows out of the kiln pool**, to (none) or to a fluidized-bed kiln archetype.
- **S178: pool the reprinted figures once.**
- **S179: an equipment-to-installed bridge.** Equipment-only capex would be multiplied by an installation factor (sourced per family where possible, otherwise a stated class factor) before pooling, graded "converted".

### Q3. Sourced levelized cost (column CB) against the calculated one (column CJ)

**How well they agree:**
- 78 archetypes have both. The median ratio of CB to CJ is 1.17.
  - 40 are within a factor of 1.5.
  - CB is more than 1.5 times CJ on 23.
  - CB is less than 0.67 times CJ on 15.
- The log correlation within units is 0.89 per GJ and 0.92 per t (raw Pearson 0.77 and 0.65).
- They agree on broad levels, but individual archetypes can differ by a factor of 2 to 5.
- The two columns measure different things, so they should not match exactly.

**What the two columns are:**

| | CB, sourced | CJ, calculated with energy |
| - | - | - |
| What it is | The levelized or production cost a source prints, converted to 2025 CAD | Our capex, fixed and variable O&M, and energy and feedstock use, priced at 2025 Canadian prices |
| Discount rate | The source's own | 8% real, with the archetype's lifetime and capacity factor |
| Energy prices | The source's own region and year (EU gas and naphtha, carbon prices) | Canadian: natural gas 10.28 CAD/GJ, ethane 2.71 CAD/GJ, electricity 22.36 CAD/GJ |
| Scope | Varies: selling prices with a return, some without by-product credits, some with CO2 transport and storage or per t net removed | Never includes transport or a return |
| Sources | Often one old source (n=1 on 31 of 78) | Built on pooled values |

**Where they differ most:**
- **Biomass flash pyrolysis (CB 3,300 against CJ 630):** CB is Gielen 1996's total cost per t ethylene. It does not deduct the by-products (propylene and aromatics), while the archetype counts per t of high-value chemicals. The equipment-versus-plant question does not explain it: our capex is already total-plant (Joosten 1998).
- **Electric steam cracker (1,567 against 668):** CB comes from EU cost studies. Layritz 2021 is the pooled value, and Agora 2021 is in the same pool: its 2050 cost includes naphtha at 752 EUR/t. CJ prices Canadian ethane feed at 2.71 CAD/GJ, so the gap is mostly the feed price.
- **Gas-to-methanol (963 against 536), Seton's row 270:** Seton is right. CB is Bazzanella 2017, with EU 2015 gas and the CO2 price included, against Canadian gas in CJ.
- **Base-load LNG (133 against 912):** CB is Kidnay's 2003 liquefaction tolling cost, per GJ of LNG, without the gas. CJ prices the liquefaction fuel and power at Canadian prices.

**Answer for Seton:**
- CB is kept as a check on CJ, not as a model input. CIMS gets capex, O&M, and energy use, and computes its own costs.
- Where the two differ by more than a factor of 2, the cause is nearly always a difference in basis (prices, region, scope, or return). It is rarely an error in our capex.

**Proposals:**
- **S176: tag each sourced levelized cost with its basis.** The tags would say whether it includes energy, feedstock, a return, or transport and storage, whether it is per t net removed, and which region's prices it uses.
  - Compare CB with CJ only where the bases match, and show a flag column in the workbook where CB/CJ falls outside 0.5-2, naming the cause.
  - Sievert's net-removed DAC costs would carry the "net removed, incl. T&S" tag and leave the captured-basis comparison.

## 3. Seton's cell comments

| Row | Archetype | Comment | Finding | Action |
| - | - | - | - | - |
| 10, 11 | boiler_fuel-fired, boiler_solid-fuel | Which "baseline" carrier is behind emissions column DD? | Per the ruling of 2026-11-07, the wide view carries the single most likely Canadian fuel. That is natural gas for the fuel-fired boiler and biomass (hog fuel) for the solid-fuel boiler. For the solid-fuel boiler, DD (0.0005 t/GJ) is CH4 and N2O only; biogenic CO2 is on the emissions sheet. The archetypes sheet does not name the fuel. | S180: add a `fuel-basis` column beside the emissions in the review workbook and the wide view. |
| 71 | boiler_fuel-fired | Why are the data the same for low-, medium- and high-temperature heat? | By design, one archetype serves all three heat end uses, so it repeats with the same values. Only 3 of the examples give a steam temperature or pressure, and none of them gives a capex as well. The sources cannot support costs by pressure. | S181: hold one archetype, but consider a judgement adjustment for high pressure (efficiency down 2-4 points with less economizer recovery, capex up for field-erected high-pressure units), or ask the boiler reviewers for pressure-specific costs. |
| 204 | kiln_dry-precalciner | Column BL looks like full cement plant costs | Confirmed (Q2). | S175, S177, S178 |
| 205 | kiln_legacy | Is legacy defined? | It is defined as the wet, semi-wet, semi-dry, and long dry routes that are older than the precalciner and use more than 15% more fuel. It stands for existing stock, not a technology anyone would build: 3 of its core values are filled, and its capex (550) is a judgement. | S182: relabel it "Older kiln routes (wet, semi-dry, long dry), existing stock" and have the CIMS export offer it for existing stock only, with no new builds. |
| 228 | binder_calcined-clay | Would an LC3 binder call 50% clinker, 30% calcined clay, and about 20% limestone and gypsum? | Yes. The service requests are 0.50 t clinker (0.45-0.55), 0.30 t calcined clay, and finish grinding, per t cement. Limestone and gypsum are raw materials, not service requests. The review workbook does not show service requests, which is why the stacking is hard to see. | S183: add a service-requests sheet (from `archetype-service-request.csv`) to the review packages and the workbook. This also answers Seton's general point about how archetypes stack. |
| 241 | steam-cracker_fired-tubular | Is this just the cracking furnace? | No. It is the whole cracker: furnaces, quench, compressors, and separation. The capex examples are whole-plant (IEA 2018, Joosten, Layritz, and others), and the energy use includes the compressors. The emissions are the furnace fuel. | Make this explicit in the description and the sector note (S183, with the service-requests sheet). |
| 244, 249 | reactor_biomass-flash-pyrolysis, steam-cracker_electric | CB far from CJ: is it equipment against full plant? | No (Q3): the causes are the by-products that are not credited and EU feed prices. | S176 |
| 270 | methanol | Spread from the country of production? | Yes (Q3). | S176 |
| 274 | gasifier_coal-methanol | 5.0 t CO2e/t looks high; closer to 3 | Seton is right. 5.02 is the median of two IPCC 2006 defaults (5.29 and 5.02, through Boulamanti 2017) and IEA 2013 (2.83, scope 1 and 2). A carbon balance on the archetype's own energy, (25.3 + 22.7 GJ/t) x 0.0889 t CO2/GJ less 1.375 t CO2 in the methanol, gives 2.9 t/t. The IPCC defaults imply roughly 70 GJ/t of coal (old or lignite plants). | S184: make emissions-total a carbon-balance identity (2.9 t/t) and keep the IPCC rows as sourced, but not as the central value. |
| 412 | blast-furnace | A lifetime of 25 years: relining comes at about 17 years | The 25 years is a median of mixed bases: van Geene 20 (relining campaign), Daniels 20 and Gielen 25 (depreciation), Gielen 30, and Arens 50 (technical life of the shell). | S185: choose the basis. Either the lifetime is the campaign (about 17-20 years, with relining as the renewal capex), or it is the technical life (40-50 years), with relining annualized into fixed O&M. CIMS's retirement logic suits the campaign basis better. |

## 4. Other findings

- **S178, reprinted figures across sources.** The same normalized value from two or more sources on the same archetype and parameter occurs in 440 groups, 17 of them costs (`identical-values.csv`).
  - Examples: Ager 2023 and IEA HPT 2023 (heat pumps), DEA catalogues 2026_001 and 2026_006, CERI 2017 parts 1 and 2 (SAGD), Bataille and UKERC (UK TIMES).
  - The pooled-once rule of 2026-09-26 works within a source but not across sources. This proposes a check across sources with a reviewed list of exceptions. Many efficiency and temperature matches are coincidental round numbers.
- **S186, flows on GJ-product archetypes.** Per-kg and per-gallon flows on archetypes measured in GJ are not normalized ("per kg, but the archetype's product is measured in GJ"). The SEC bridge converts them, but the flows bridge does not.
  - This affects today's Xu and Wu flows and older ones (Haas, West, Zhang).
  - The product energy content (`cf-fame-hhv-mass`, `cf-paraffinic-diesel-hhv-mass`) is already in the conversion factors, so the bridge could reuse it.

## 5. Decisions needed (in order of effect)

1. **S175, S177, S178: rebase the cement kiln capex to the clinker line.** Subtract the grinding share, move the fluidized-bed rows out, and pool the reprints once.
2. **S184: coal methanol emissions by carbon balance** (2.9 t/t).
3. **S179: the equipment-to-installed bridge** for the 26 mixed capex pools.
4. **S176: basis tags for sourced levelized costs**, and the CB-against-CJ flag.
5. **S172, S174, S180, S183: workbook changes.** Show p25-p75 instead of min-max, flag wide pools, add a fuel-basis column, and add a service-requests sheet.
6. **S173, S181: sizing and pressure for the scale-sensitive heat archetypes.**
7. **S182 and S185: legacy kiln as existing stock only, and the basis of the blast furnace lifetime.**

Follow-up section 5 (2026-11-20): Option 1 boiler sizing from GHGRP and MSAPR unit counts. Results are upper bounds; awaiting a ruling.
