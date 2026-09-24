# ETSAP brief assessment, 2026-09-23

The 29 registered ETSAP briefs that had not been assessed. Each was read against the rendered
pages, with dense tables resolved by x-coordinate. Verdicts: **EXTRACT** (worth a full
extraction), **PARTIAL** (a few in-scope rows), **BACKGROUND** (nothing usable in scope).

**Two rules for anyone extracting these.**

- In almost every brief the summary table disagrees with its own body tables at least once.
  Take the body tables as the source of record and note the conflict.
- The three 2010 briefs by Lako (E04, E05, E07) share one summary template. In each, merged
  cells span columns, the rightmost projection column is cut off, and "Output: Electricity"
  is printed across heat-only columns.

## Status after the modeller's decisions (2026-09-23/24)

- **Extracted and loaded** (in `ETSAP_BRIEFS`): E04, E05, E13, P05, P07/08 (mining only), P11. Size bands,
  plants and cover types within one table are one example each; the case is named in each row's note.
- **Moved to background:** E21, E18, P01, T02, T03 (the five), and, following the decisions below, E11
  (PV without storage), T05 and T09 (automotive components). Recorded in `background-register.csv`.
- **Decisions:** a PV system without storage is not an example of `photovoltaic-array_battery-storage`;
  storage components are add-on measures (`incremental`, pooled only with the base system's cost from the
  same source); road-vehicle components are not proxies for mobile equipment. All 16 proposed archetypes
  were added, including the optional biogas upgrader.
- **Extracted 2026-09-24, not yet loaded:** E07, E02, E10, E17, E14, P12, I09, P02, P03, P04, P06, I12, I13, P09, P10.
  Each main file holds only the in-scope rows; utility power, transport, levelized costs, life-cycle
  emissions, projections and anything without an archetype went to sidecars, listed in each `_meta.csv`.
  Content with no archetype, reported rather than forced: geothermal CHP (E07), sorption/thermochemical
  waste-heat storage (E17), CO2 transport and storage (E14), partial-oxidation hydrogen (P12), coal-to-methanol
  (I09), direct coal liquefaction (P06), LNG regasification (P03), thermal desalination MSF/MED (I12).
  P04 gives no numbers by refinery complexity class; its whole-refinery rows are on `refinery_oil`.

## Summary

| Brief | Source id | Verdict | Serves (existing archetypes unless noted) | Rows |
| - | - | - | - | - |
| E04 Combined Heat and Power | etsap_2010_004 | EXTRACT | combustion-turbine_heat-recovery-steam-generator, combined-cycle_chp, steam-turbine_back-pressure, reciprocating-engine_chp | 75-85 |
| E05 Biomass for Heat and Power | etsap_2010_005 | EXTRACT (modest) | steam-turbine_back-pressure / boiler_solid-fuel (biomass CHP); reciprocating-engine_chp on biogas (AD-CHP) | ~30 |
| E13 Stationary Fuel Cells | etsap_2013_004 | EXTRACT | fuel-cell_chp (SOFC, MCFC, PAFC) | ~45 |
| P05 Syngas from Coal | etsap_2010_011 | EXTRACT | gasifier_coal-petroleum-coke, gasifier_ccs-concentrated; coal-to-SNG needs a new archetype | 55-70 |
| P11 Biogas and Bio-syngas | etsap_2013_012 | EXTRACT | anaerobic-digester_biomethane-upgrading, anaerobic-digester_effluent, process-improvement_landfill-gas-recovery, gasifier_biomass-methanation | 60-80 |
| P07/08 Coal Mining and Logistics | etsap_2014_002 | EXTRACT (mining only) | NEW: surface coal mine, underground coal mine, coal-mine methane drainage | 45-50 |
| E07 Geothermal Heat and Power | etsap_2010_006 | PARTIAL | geothermal-well_direct-use (heat plant); binary power needs a new archetype | 9-11 |
| E02 Gas-Fired Power | etsap_2010_008 | PARTIAL (borderline) | combustion-turbine_simple-cycle (OCGT only) | 10-12 |
| E10 Concentrating Solar Power | etsap_2013_001 | PARTIAL | solar-concentrator_thermal, solar-concentrator_high-temperature (temperature, lifetime only) | ~15 |
| E11 Photovoltaic Solar Power | etsap_2013_003 | PARTIAL | photovoltaic-array_battery-storage (PV side only; decision needed) | 12-15 |
| E17 Thermal Energy Storage | etsap_2013_005 | PARTIAL | thermal-storage_electric (storage side); sorption waste-heat store needs a new archetype | 15-20 |
| E14 CO2 Capture and Storage | etsap_2010_007 | PARTIAL | sector abatement costs for ~12 capture archetypes; transport and storage cost adders | 25-35 |
| P12 Hydrogen Production and Distribution | etsap_2014_003 | PARTIAL | steam-reformer_methane, electrolyzer_low-temperature, compressor_hydrogen-pipeline, liquefaction-train_hydrogen | 30-40 |
| I09 (printed I08) Bio-methanol | etsap_2013_007 | PARTIAL | gasifier_biomass-methanol, reactor_co2-to-methanol, reactor_syngas-methanol | 20-25 |
| P02 Unconventional Oil and Gas | etsap_2010_010 | PARTIAL | NEW: SAGD / CSS; separator_warm-water-extraction | 8-12 |
| P03 Oil and Gas Logistics | etsap_2011_001 | PARTIAL | chiller_gas-turbine (LNG), compressor_gas-turbine-drive | 15-20 |
| P04 Oil Refineries | etsap_2014_001 | PARTIAL | NEW: whole refinery by complexity; oil-sands upgrader | 30-45 |
| P06 Liquid Fuels from Coal and Gas | etsap_2010_012 | PARTIAL (leaning background) | NEW: fossil Fischer-Tropsch (CTL, GTL) | 15-75 |
| I12 Renewable Desalination | etsap_2013_008 | PARTIAL (thin) | separator_reverse-osmosis (RO, ED electricity only) | 6-10 |
| I13 Bio-ethylene | etsap_2013_009 | PARTIAL | reactor_ethanol-to-ethylene | 5-8 |
| P09 Biomass Production and Logistics | etsap_2013_010 | PARTIAL | NEW: wood pellet mill, torrefaction (not the iron-ore pellet-plant archetypes) | 25-35 |
| P10 Liquid Biofuels | etsap_2013_011 | PARTIAL | fermenter_grain-dry-mill, fermenter_lignocellulosic-enzymatic, transesterification-unit_alkali-catalyzed, gasifier_fischer-tropsch, reactor_hydrotreating-lipids | 25-35 |
| T05 Electric and Plug-in Hybrid Vehicles | etsap_2010_015 | PARTIAL (proxy) | battery-electric mobile equipment / haul trucks (battery $/kWh, drive efficiency) | ~4 |
| T09 Heavy Trucks | etsap_2011_002 | PARTIAL (proxy) | mobile-equipment_diesel, mobile-equipment_diesel-electric, battery-electric learning rates | 6-9 |
| E21 Biomass Co-firing | etsap_2013_006 | BACKGROUND | utility coal-plant retrofits; projections copied from E05 | 0 |
| E18 Electricity Storage | etsap_2012_002 | BACKGROUND | grid-scale; battery rows only if storage components are admitted | 0 (20) |
| P01 Conventional Oil and Gas | etsap_2010_009 | BACKGROUND | regional and sector statistics only | 0 |
| T02 Advanced Diesel Engines | etsap_2010_013 | BACKGROUND | per-car figures only | 0 |
| T03 LPG and Natural Gas Engines | etsap_2010_014 | BACKGROUND | per-car conversion costs only | 0 |

## Decisions these assessments raise

1. **New archetypes that several briefs need before they can be extracted:**
   - surface and underground coal mines, and coal-mine methane drainage (P07/08);
   - wood pellet mill and torrefaction (P09);
   - whole refinery by complexity and oil-sands upgrader (P04);
   - SAGD and CSS thermal in-situ recovery (P02);
   - coal-to-SNG (P05);
   - fossil Fischer-Tropsch, coal-to-liquids and gas-to-liquids (P06);
   - geothermal binary power (E07);
   - a standalone biogas upgrader (P11, optional).
2. **Can a PV system without storage be an example of `photovoltaic-array_battery-storage`** (E11)? And
   are storage-component rows admissible without a whole-system cost (E17 stores, E18 batteries)?
3. **Transport proxies (T05, T09).** Should automotive component figures be admitted for the
   mobile-equipment archetypes with a low-quality flag?

## Per brief

### E04 Combined Heat and Power — EXTRACT

- **Coverage:** four industrial CHP types with full cost and performance data and 2020/2030
  projections. The costs are US$2008, stated in the Highlights only.
- **Table 3 (p.5), gas turbine / combined cycle:**
  - electric efficiency 30-36 / 42-47%, thermal efficiency 50-44 / 38-33%;
  - capex 900-1,500 (typical 1,000) / 1,100-1,800 (typical 1,300) $/kW;
  - O&M 40 / 50 $/kW/a;
  - availability 95 / 90-95%;
  - technical lifetime 25 yr, economic lifetime 20 yr.
- **Table 4, fluidised-bed coal or biomass / gas engine:**
  - electric efficiency 24-28 / 30-42%;
  - capex 3,000-4,000 (typical 3,250) / 850-1,950 (typical 1,150) $/kW;
  - O&M 90-120 / 200-300 $/kW/a;
  - lifetime 40+ / 20 yr.
- **Table 2 (p.3):** three gas engines, of 68, 800 and 3,000 kWe.
- **Traps:**
  - Thermal efficiency is printed high-to-low, and it pairs with the electric range (30 with 50).
  - Lifetime, construction time and interest rate are merged across GT and CCGT.
  - In Table 2, "Landfill gas" is one cell spanning the 800 and 3,000 kWe columns.
  - The 68 kWe column is internally inconsistent: its fuel input implies 37.8% electric, not 33-35%.
  - Gas-engine size mixes MWe and kWe.
  - Fluidised-bed capex is per condensing-mode kWe.
  - CO2 in kg/MWh has no stated basis.
  - Gas-engine O&M of 200-300 is high (the text says about 250); record it as printed and flag it.

### E05 Biomass for Heat and Power — EXTRACT (modest)

- **Coverage:** two in-scope columns in Table 4 (p.7, US$2008), biomass steam CHP ("BP") and AD-CHP.
  - electric efficiency 16-36 / 26-32%, total 40-85%;
  - capex 3,000-6,000 / 3,700-5,300 $/kW;
  - O&M 100 / 300 $/kW/a;
  - availability 93 / 80%;
  - technical lifetime 25 yr, economic lifetime 20 yr;
  - projections BP 3,750 / 3,100 / 2,750 and ADCHP 4,500 / 3,700 / 3,300 $/kW.
- **Out of scope:** co-firing (the third column) is utility power.
- **Traps:**
  - The projection block is missing its 2030 co-firing column, and the 2020 co-firing efficiency cell is blank.
  - "2,75 / 0" wraps across two lines and reads 2,750.
  - Two tables are numbered "Table 3"; the water table is a later insertion.
  - AD-CHP capex is 3,000-5,000 in the Highlights but 3,700-5,300 in the body.
  - AD-CHP capex includes the digester, which needs a note or a new archetype.
  - Earlier findings: in Table 1, "Hungary/DBM/2009/VG/19.8" is 19.8 MWe with the efficiency blank, and "Europe/37.5/259/Atwood" is 37.5% efficiency.

### E13 Stationary Fuel Cells — EXTRACT

- **Table 3 summary (p.8), 2010 US$:**
  - electrical efficiency (LHV) MCFC 45-50%, SOFC 47%;
  - overall efficiency 80 / 85-90 / 72% (MCFC / SOFC / PAFC);
  - lifetime 40,000 / 30,000 / 60,000 hours;
  - availability 95-97%;
  - SOFC temperature 650-1100 degC;
  - capex MCFC 4,000, PAFC 4,500, SOFC 7,000-12,500 $/kWe (above 100 kWe);
  - 2020 and long-term capex blocks.
- **Scope:** PEMFC is residential micro-CHP and out of scope. PAFC is more than 15% below the others on electrical efficiency.
- **Traps:**
  - Lifetimes are hours, partly stack life (an MCFC stack lasts about 5 yr).
  - The SOFC capex cell stacks two values: $25,000 is per 0.7 kWe system, not per kWe.
  - MCFC and PAFC O&M have no size basis, so they are unusable.
  - The 2020 MCFC/PAFC capex of $3,000 contradicts its own cited source, which gives about 4,900-5,900 in 2020.
  - Table 1 wraps "650 - 1100", which can shift the PAFC 200 degC into the wrong column.
  - Heat-to-power ratio must be derived as (overall - electrical) / electrical.

### P05 Syngas from Coal — EXTRACT

- **Source:** one consistent source (NETL-401), US$2005.
- **Table 1 (p.4), two BGL gasification plants, Illinois #6 and Wyodak:**
  - capacity 310 / 207 MWth;
  - efficiency 74.7 / 72.8%;
  - total plant cost 118.7 / 101.3 M$;
  - capex 13.5 / 17.2 $/GJ;
  - fixed O&M 6.0 / 5.8 M$/yr;
  - variable O&M 1.4 / 1.6 $/GJ.
- **Table 2 summary (p.5)**, for syngas, syngas with H2, and SNG:
  - efficiency 73-75 / 73-75 / 60%;
  - lifetime 20 yr, load factor 90%;
  - CO2 55 / 55 / 78 kt/PJ;
  - capex 17.2-13.5 / 18.3-14.1 / 27.2-20.1 $/GJ;
  - 2020, 2030 and 2050 projections.
- **Traps:**
  - European number format: "800 - 1.200" is 1,200 and "17,2" is 17.2.
  - Ranges run high-to-low, and the direction flips between columns.
  - "$/GJ output" means $ per GJ/yr of capacity at 8,760 h (checked: 118.7M / (1005 x 8760) = 13.48, about $425/kW).
  - 310 MWth does not equal 1005 GJ/h, and 74.7% does not reconcile with the flows, so do not derive efficiency from the flows.
  - "Load factor and availability" is one merged row.
  - The Table 2 syngas column is the range of the two Table 1 plants, so do not double-count them.

### P11 Biogas and Bio-syngas — EXTRACT

- **Table 6 (p.8), five upgrading technologies:**
  - capex in USD1000 per m3/h, for plants below 500 and for 500-2,000 m3/h;
  - O&M 2-4% of capex;
  - availability 0.95-0.98;
  - electricity 0.12-0.30 kWh/m3, plus 0.55 kWh heat for amine;
  - methane slip from 0.04% (amine) to 0.5-20% (membrane).
- **Figures 1-2:** digester capex 5,050-7,500 and upgrader capex 1,950-6,490, in 2012 USD per Nm3/h.
- **Text:**
  - digester lifetime 15-20 yr, fixed O&M 2-7%, process energy about 15% of the biogas;
  - gasification USD2011 60-70M for 1,000 dry t/d, cold-gas efficiency 65-80%;
  - landfill gas capture 35/65/85/90% depending on the cover.
- **Traps:**
  - The summary capex column is headed "USD/kW" but holds USD per Nm3/h, and its currency year is shown only on the figure axes.
  - The summary energy column holds "Up to 15%".
  - The landfill cost "6.9-1.8" is reversed.
  - Table 5 has "2.54 Nm3/yr" (millions) and "MWh/hr" (per year).
  - The beef-cattle row in Table 4 is copied from pigs.
  - The summary yield formula fails for leaves, grass and maize.
  - Table 8 is labelled PJ but its values are EJ.

### P07/08 Coal Mining and Logistics — EXTRACT (mining sections only; needs new archetypes)

- **Table 13 (p.8), open-pit mines, 2008 USD converted from AUD:**
  - opex and capex for 5 production rates x 3 seam thicknesses;
  - for example 196,000 t/d is 14.3 $/t and 1,999 M$, and 1,800 t/d is 71.6 $/t and 180 M$.
- **Energy (p.5):** 0.391 GJ/t mined.
- **Methane (pp.5-6):**
  - underground 10-25 m3/t, plus 0.4-4.0 post-mining;
  - surface 0.3-2.0, plus 0-0.2 post-mining;
  - Table 5 gives country coefficients.
- **Out of scope:** transport, Tables 6-10 and 15-18.
- **Traps:**
  - The Table 13 stripping-ratio header is split over three lines.
  - The opex basis is presumably per t of coal but is not stated.
  - 512 PJ / 0.391 GJ/t exceeds US coal output, probably a short-ton issue.
  - Table 11 surface-mine electricity is six times underground, which is implausible.
  - The summary switches to short tons.
  - The Highlights' cost shares do not match Tables 17-18.

### E07 Geothermal Heat and Power — PARTIAL

- **Heat plant column of Table 5 (p.5, US$2008):**
  - capex 1,000-3,000 $/kWth;
  - O&M 20-60 $/kW/a;
  - load factor 55%, availability 95%;
  - lifetime 30-50+ yr;
  - projections 1,800 (2010) and 1,500 (2020).
- **Binary power:** 8-15% efficiency and 3,400-4,500 $/kW capex; only needed if a geothermal-power archetype is added.
- **Traps:**
  - Table 1's column headed "O&M cost [M$]" is actually total investment.
  - The 2030 heat-plant projection is missing.
  - "Typical size, MWe" is wrong for the heat plant.
  - Two Guadeloupe rows, the first copied from the Azores.

### E02 Gas-Fired Power — PARTIAL (borderline)

- **OCGT only, from Table 3 (p.4, US$2008):**
  - efficiency 35-42%;
  - capex 800-1,000 (typical 900) $/kW;
  - O&M 36 $/kW/a;
  - technical lifetime 30 yr, economic lifetime 25 yr, availability 92%.
- **Out of scope:** the power-only CCGT.
- **Traps:**
  - OCGT production cost is 210 in one place and "100" in the projections.
  - The load factors are peaking and utility duty, so they are not industrial.
  - CCGT NOx is 10x below Table 2.

### E10 Concentrating Solar Power — PARTIAL (performance rows only)

- **All costs** are 14-370 MWe power plants, including the power block, so none are usable for heat.
- **Usable:**
  - maximum heat-transfer-fluid temperature: trough 390, trough with salt 550, tower with salt 565, dish above 800 degC;
  - lifetime above 30 / 30 / above 15 yr;
  - construction time 1-3 yr.
- **Currency:** US$2010 at EUR 1 = 1.3.
- **Traps:**
  - Table 1 cells wrap ("55-70", "22-24").
  - Table 1 and the summary disagree on several cells.
  - There are two "Table 4"s.

### E11 Photovoltaic Solar Power — PARTIAL

- **Table 8 summary (p.11):**
  - commercial system capex 1,900-2,500 $/kW;
  - O&M 1% of capex per year;
  - lifetime 25 (30) yr;
  - capacity factor 9-16%;
  - module efficiency 13-19% (single-crystal silicon).
- **Traps:**
  - The currency year conflicts: 2012 USD in the summary, 2010 USD in footnote 3.
  - The column layout changes inside the summary.
  - Table 2 shifts one column left as text.
  - There are no battery data, so decision 2 applies.

### E17 Thermal Energy Storage — PARTIAL

- **Table 1 (p.3), sensible / phase-change / thermochemical:**
  - capacity 10-50 / 50-150 / 120-250 kWh/t;
  - efficiency 50-90 / 75-90 / 75-100%;
  - cost 0.1-10 / 10-50 / 8-100 EUR/kWh (no currency year).
- **p.5:** one industrial case, a mobile zeolite waste-heat store (3 MWh, 500 kW, EUR 55/MWh delivered).
- **Traps:**
  - The summary's phase-change cost reads "ott-50", a spreadsheet date corruption of 10-50.
  - The summary's US$2008 per-kW block contradicts the body (a 100 MWe, 18 GW thermochemical store); do not take it.
  - Table 6's cost column is the maximum affordable cost, not a cost.

### E14 CO2 Capture and Storage — PARTIAL

- **Coverage:** no technology table, but useful as a source of sector abatement-cost values.
- **Table 1 (p.11), $/tCO2 avoided, US$2008:**
  - cement 75-100;
  - synfuels 60-100 (150);
  - iron and steel (25) 65-75;
  - also gas processing 5-15 and ammonia 30-35.
- **Capture rates:** 85-90% (power, gas processing), 50-75% (iron and steel), about 65% (cement, plant-wide).
- **Transport and storage adders:**
  - transport $2-6/t at 2 Mt/y and $1-3/t at 5-10 Mt/y, per 100 km of pipeline;
  - storage $5-10/t onshore, $10-25/t offshore.
- **Traps:**
  - Mixed currency years: the investment row is US$2006.
  - Text and table disagree on ship transport, power costs and iron-and-steel capture rate.
  - "Physical adsorption" means physical-solvent absorption.
  - Only the avoided-cost row is abatement-cost.

### P12 Hydrogen Production and Distribution — PARTIAL

- **Table 2 (p.8), EUR2011:** efficiency SMR 70-85%, partial oxidation 60-78%, electrolysis 62-82%, gasification 50-70%.
- **Table 1 (p.6), pipeline cost:** 0.261 EUR/kg at 5 Gm3/y, 0.139 EUR/kg at 30 Gm3/y.
- **p.5:**
  - compression 10-15% of HHV;
  - liquefaction 30-40% of energy content.
- **Not usable:** there is no production capex; the production cost is levelized.
- **Traps:**
  - "Lifetime 2-5 yr" is catalyst life, and "40,000 hours" is electrolyser stack life.
  - "0.8 EUR/MWh" is an electricity price error.
  - Electrolysis kWh/kg does not reconcile with its efficiency on either HHV or LHV.
  - Gasification efficiency is 35-50% in the text but 50-70% in the table.

### I09 (printed I08) Bio-methanol — PARTIAL

- **Table 2 (p.8), capex in USD per t/yr, no year:** Chemrec 4,400, Varmlands 5,400, CRI 9,500, natural gas 650-1,300.
- **Table 3:** LHV efficiency 60-70% for natural gas, 50-60% for the others.
- **Canadian context:** Enerkem, and Al-Pac's recovery of methanol from pulping.
- **Traps:**
  - The GHG values are cradle-to-gate life cycle, not Scope 1.
  - Chemrec's 100 kt is combined DME and methanol.
  - The header says I08.

### P02 Unconventional Oil and Gas — PARTIAL

- **Oil-sands values, all second-hand** (Alberta fact sheet, GHGenius, Charpentier 2009):
  - steam-to-oil ratio SAGD 3.2, CSS 3.4;
  - SAGD 1-1.25 GJ natural gas per bbl;
  - water 2-3 bbl per bbl;
  - pathway emissions 62-176 kg/bbl.
- **Route:** the primary sources would be a better route.
- **Trap:** "CCS" means cyclic steam stimulation throughout, not CO2 capture.

### P03 Oil and Gas Logistics — PARTIAL

- **LNG liquefaction capex series, Table 5 (p.4):** 10.6 (1988) to 3.8 (2003) US$2005 per MMBtu per year.
- **LNG plant:** fuel use 15% (future 11%), lifetime 25 yr.
- **Compression:** capex 1,484 $/kW; energy 1.8-2.7% per 1000 km.
- **Trap:** the summary Table 9 has several copy errors (meter for km, diesel 29 against 129, lost per-year bases), so check every row against the body.

### P04 Oil Refineries — PARTIAL

- **Coverage:** whole-refinery and upgrader values, so they need a new archetype.
- **Table 10:** capex for 11 projects in k$ per b/d, no year, including four Alberta upgraders and North West Redwater with CCS.
- **Tables 11-12:** opex.
- **Emissions:**
  - US refineries 48.7 kg CO2e/bbl;
  - 0.61-1.04 t/m3 for heavy crude and oil sands.
- **Traps:**
  - Table 10 arithmetic errors: Kitimat 23.6 printed as 26.0, India 4.8 printed as 10.3.
  - Table 9 units are wrong by orders of magnitude.
  - The summary labels kg/bbl as gCO2eq/kWh.

### P06 Liquid Fuels from Coal and Gas — PARTIAL (leaning background)

- **Table 1:** the NETL CTL plant, US$2006.
- **Table 2:** CTL and GTL at three scales:
  - capex 15.7-22.7 / 6.5-7.5 $/GJ;
  - CO2 122 / 28 kt/PJ;
  - lifetime 30 yr.
- **Fit:** no archetype and no Canadian stock.
- **Trap:** Table 1 implies about $39/GJa against Table 2's 15.7-22.7.

### I12 Renewable Desalination — PARTIAL (thin)

- **Table 3, electricity per m3:** reverse osmosis 3.5-5.0 kWh/m3, electrodialysis 1.5-4.0 kWh/m3.
- **Summary capex:** 800-1,500 USD per m3/day for every technology.
- **Fit:** seawater, so only a proxy for industrial water treatment.
- **Trap:** the summary's thermal column is kWh/m3, not the kJ/kg of its heading.

### I13 Bio-ethylene — PARTIAL

- **Ethanol dehydration capex:** 1,100-1,400 USD per t/yr. Plant examples: Braskem 1,390, Dow/Mitsui 1,140.
- **Conversion:** 1.74 t hydrated ethanol per t ethylene, with 99% conversion and 97% selectivity.
- **Not usable:** the 1.6 GJ/t is a theoretical minimum; Table 2 is life cycle; Table 3 production costs are levelized.

### P09 Biomass Production and Logistics — PARTIAL (needs new archetypes)

- **Table 4 (p.8), two examples each for wood and torrefied pellets:**
  - electricity 171 / 263 kWh/t;
  - investment 19.5 / 29 MUSD.
- **Table 5:** a 40 kt/yr sawdust plant, step by step.
- **Summary:** investment 0.07-0.28 kUSD per t/yr.
- **No currency year** anywhere.
- **Traps:**
  - "Mt" is printed where tonnes are meant.
  - The Table 5 maintenance unit is off by 1000.
  - Energy use is electricity only.
  - Do not map to the iron-ore pellet-plant archetypes.

### P10 Liquid Biofuels — PARTIAL

- **Summary (Table 4):**
  - lifetime 25 yr;
  - capex 1.7-2.5 $ per l/yr (2010 US$);
  - conversion efficiencies and plant sizes for six routes.
- **Traps:**
  - The summary contradicts Table 1 (bagasse 0.25 against 2.5 kg/l).
  - Capacity factor is in hr/yr.

### T05 Electric and Plug-in Hybrid Vehicles — PARTIAL (proxy)

- **Li-ion cost:** EUR 670-1,340/kWh, projected 170-200, no currency year.
- **Drive efficiency:** 65% battery-electric against 18-23% combustion.
- **Proxy quality:** weak to moderate, since these are automotive cells and drive cycles.

### T09 Heavy Trucks — PARTIAL (proxy)

- **Heavy-duty diesel engine efficiency:** 40-42%, potential 50-55%.
- **Hybrid savings:** 20-30% urban, 4-10% long-haul.
- **Battery-electric progress ratios:** 0.90 / 0.85 / 0.80. Record them as learning rates of 10 / 15 / 20%.
- **Traps:**
  - Currency years are mixed (EUR2007 and EUR2010).
  - Citation numbers are shifted by one.

### Background: E21, E18, P01, T02, T03

- **E21 Biomass Co-firing:** co-firing retrofits of 50-700 MWe utility coal plants. Its 2020/2030 projections are
  copied exactly from E05's biomass-CHP and AD-CHP columns.
- **E18 Electricity Storage:** grid-scale storage with conflicting cost figures. Its battery rows
  (Li-ion 500-1,500 $/kWh, 90% DC) would be taken only under decision 2.
- **P01 Conventional Oil and Gas:** regional statistics only, such as energy input in GJ/toe, lifting cost in $/boe and flaring by country.
- **T02 Advanced Diesel Engines and T03 LPG and Natural Gas Engines:** per-car figures only.
