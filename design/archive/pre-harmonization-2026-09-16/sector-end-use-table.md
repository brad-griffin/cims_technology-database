# Sector and end-use table: proposal

**Status: proposal for review, 2026-09-11. The harmonized layer has not been changed.**
The record is `sector-end-use-table.csv` in this folder: one row per (sector, end use),
14 columns. This file is the readable version.

There are twelve sectors plus a cross-sector group, and 73 end uses.

The table sets out the categories to collect against: an end use per service with its own
technology set, and the technologies to find data for. Empty cells mark what is still
to be found.

**CIMS coverage:** the 14 CIMS sectors in scope are Iron and Steel, Industrial
Minerals, Chemical Products, Petroleum Refining, Pulp and Paper, Mining, Coal Mining,
Metal Smelting, Light Industrial, Ethanol, Biodiesel, Petroleum Crude, Natural Gas and
Construction. They hold 426 distinct services, and 407 map to a row. The 19 unmapped:

- 14 fuel-blend nodes (`Methane Blend`, the `OG * Blend` nodes, `Methane Fuel`)
- 2 agricultural feedstock inputs
- 3 emissions services (`Fugitive` and the two `Venting` nodes)

## Rules

1. **Cross-sector** holds the end uses common to all sectors: the three heat bands,
   on-site power-only generation, the five machine-drive categories, facility
   services, CO2 capture (concentrated and diffuse streams), direct air capture, and
   mobile equipment. CHP is a technology on the heat bands, not an end use. Hydrogen
   production, air separation and process refrigeration are sector end uses.
2. **Heat is banded by the temperature the process needs:** low < 150 °C, medium
   150–400 °C, high > 400 °C. Steam, hot water, thermal oil and direct heaters are
   technologies within a band. Steam conditions are technology parameters
   (`temperature-output`, `pressure-output`).
3. **Integral vs supplied heat.**
   - *Integral:* heat released inside the unit that transforms the material (kilns,
     blast furnaces, cracker furnaces, lime kilns, glass and reheating furnaces)
     belongs to the sector end use.
   - *Supplied:* heat from a separable system (boilers, CHP, process heaters, generic
     dryers and heaters, SAGD field boilers) is a cross-sector heat band. Each
     sector row records the band it draws on and at what temperature.
4. **A sector end use is the service the sector produces.** Competing routes sit
   inside it, e.g. blast furnace, DRI and smelting reduction in `ironmaking`. CIMS
   sub-services, product grades and size classes are process steps below the end use.
5. **Process electricity that is the process stays with the sector:** EAF,
   electrolysis, mechanical-pulping refiners, comminution, cement grinding, rolling,
   pipeline compression.
6. **What an end use calls on is a link, not a copy.** The `draws-on` column lists
   the end uses this one calls on, each with the duty in brackets - `integral (kiln)`,
   `heat-low-temp (digestion)`, `pumping (slurry and tailings)`. A sector end use
   lists only its own equipment; anything a separable cross-sector system supplies is
   a link, so the technologies stay in one place while the sector keeps its detail.
   The link records a demand: the energy stays on the end use it names. The "Heat
   source" and "Draws on" columns and each cross-sector end use's "Drawn on by" note
   are all rendered from that one column.
7. **Granularity.** Keep an end use at the most general aggregation that still
   captures a real difference in energy use **or in emissions**. Two end uses may be
   generalised together when the generalisation is natural (different casting methods
   under casting); they may not be bundled when the energy service differs, when the
   emissions differ in kind or in how they are abated, or when a policy instrument
   treats them separately.

## Changes from the current design

- The three heat bands replace `steam-and-hot-water` and the three `process-heat-*`
  end uses (supersedes D3 and the design doc §3 branch split). CHP is a technology
  supplying the low and medium bands, with electricity as a co-product; D1's
  accounting is unchanged. Each CIMS `<sector>.Steam` node splits into the bands.
- End uses are sector-scoped, except cross-sector. `material-preparation`,
  `material-conversion`, `forming-and-finishing`, `electrochemical` and
  `drying-and-separation` give way to named sector end uses. The CSV's
  `harmonized-now` column maps each current application.
- Drying is sector-specific.
- CIMS cement services (`dry-process-rotary-kiln`, `fluidized-bed`, `finish-grinding`,
  `dry-ground-cement`) move from non-metallic minerals to cement.
- On-site power-only generation is in scope (design doc §1 excluded it).
- New sectors `biofuels` and `oil-and-gas` need rows in `sector.csv`. `oil-and-gas`
  includes pipelines (NAICS 486).
- Electric smelting of ferroalloys is in non-ferrous metals (NAICS 331110 is iron and
  steel).
- Mine ventilation and mine air heating are a mining end use, not facility services.
- Machine drive follows the EIA MECS categories: pumping, fans and blowers, compressed
  air, materials handling and materials processing. The MECS residual is not carried.
- On-site hydrogen production sits with its host sector (`refinery-hydrogen`,
  `upgrader-hydrogen`); a `hydrogen` sector holds centralised production and
  distribution; biogas and RNG are a biofuels end use.
- Air separation is a sector end use (`steel-oxygen-supply`, `smelter-oxygen-supply`);
  glass oxy-fuel firing, oxy-fuel capture and merchant gases are not carried.
- Process cooling is a food and beverage end use.
- Venting and flaring, and fugitive emissions, are oil-and-gas end uses: gas disposed
  of rather than sold, with the abatement options as competing technologies.

## Heat-demand profile by sector

From NREL 118: US manufacturing fuel combustion in 2014, energy-weighted. Steam-served
heat is the boiler and CHP end uses. NREL assigns one temperature per unit process, so
iron and steel's 100% is a single assigned 177 °C.

| Sector | Steam share of fuel heat | Steam-served heat < 150 / 150–400 / > 400 °C | All fuel heat < 150 / 150–400 / > 400 °C |
| - | - | - | - |
| Iron and steel | 35% | 0 / 100 / 0 | 0 / 41 / 59 |
| Cement | 0% | — | 0 / 15 / 85 |
| Non-metallic minerals | 1% | 100 / 0 / 0 | 1 / 17 / 83 |
| Chemicals | 68% | 80 / 17 / 2 | 56 / 16 / 28 |
| Petroleum refining | 65% | 32 / 68 / 0 | 26 / 47 / 27 |
| Pulp and paper | 93% | 81 / 19 / 0 | 75 / 19 / 6 |
| Food and beverage | 84% | 99 / 1 / 0 | 98 / 2 / 0 |
| Non-ferrous metals | 20% | 100 / 0 / 0 | 22 / 2 / 76 |
| Other industry | 58% | 26 / 74 / 0 | 27 / 51 / 22 |
| Biofuels (ethanol, NAICS 325193) | 63% | 100 / 0 / 0 | 63 / 0 / 37 * |

\* NREL assigns ethanol's direct-heat temperature (788–871 °C) from SIC 2869; the
> 400 °C share is an artefact. Mining and oil and gas are not in NREL 118.

## The table

Temperatures are as each source prints them; "(steam)" marks a steam temperature. Tier
labels in *italics* are this table's assignment.

A **Technologies** table follows each sector's end-use table. Its `type` column is one
of:

- **conventional:** the incumbent in Canadian stock.
- **efficient variant:** a major efficiency step on a conventional technology.
- **alternative:** commercial (TRL 9) but not common in Canada.
- **prospective:** TRL 5–8.

TRL is on the 1–9 scale. IEA Clean Technology Guide values are as that guide reports
them; "assessed" marks a level read from project or pilot evidence rather than a
published TRL. Technologies are generic, with fuel and carrier choices listed in
Energy inputs rather than split into separate rows.

**Heat source** says where the end use's heat comes from:

- **Integral:** the heat is released inside the end use's own equipment (kiln, furnace,
  dryer, oven).
- **From `heat-…`:** the heat comes from somewhere else, supplied by that cross-sector
  heat end use (boilers, CHP, process heaters).
- **Is a source:** the row supplies heat to other end uses.
- **—:** no process heat. The Sources column lists the references for the whole row, by the keys in
the Sources section; the CSV keeps each citation beside its value. The CIMS services
each end use maps to are in the CSV's `cims-services` column.


<br>

---

### Cross-sector

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Heat, low temperature (< 150 °C)** `heat-low-temp` | Heat delivered below 150 °C from a site heat system: hot water and low-pressure steam (washing and CIP, pasteurising, bleaching, stock heating, evaporation, low-temperature drying) and generic low-temperature direct heaters. | *low-temp*<br>< 150; hot water and LP steam, boiler steam 121-177; CHP process steam 148-193, mostly serving duties below 150 | Is a source: supplies other end uses | — | natural gas, biomass, black liquor, by-product gases, electricity (electric boilers, heat pumps), solar thermal, recovered heat; CHP prime movers (gas turbines, engines, back-pressure turbines) | Commercial heat pumps reach about 150-165 °C. 84% of food, 80% of pulp and paper and 28% of chemicals indirect heat is below 100 °C. CHP-served heat is mostly used below 150 °C, in food, pulp and paper and basic chemicals, which is why cogeneration sits on this band as well. Share of steam-served heat below 150 °C: food 99%, pulp and paper 81%, chemicals 80%, non-ferrous 100%, refining 32%. CHP-served heat is mostly used below 150 °C. Drawn on by 29 end uses: `space-heating`, `co2-capture-diffuse`, `direct-air-capture`, `rolling`, `steam-cracking`, `ammonia-and-methanol` and 23 more. | NREL97 SIC 20xx, 26xx; NREL118; design doc s2; etsap_2013_002 165 °C, p.2, p.8; rtc_2023_001 heat pump < 160 °C, p.13; caelp_2024_001 p.36, p.11 |
| **Heat, medium temperature (150-400 °C)** `heat-medium-temp` | Heat delivered at 150-400 °C: medium- and high-pressure steam, thermal oil and direct heaters (distillation reboilers, digesters, stripping, polymer melting and extrusion, panel pressing, refinery distillation heaters). | *medium-temp*<br>150-400; MP/HP steam; CHP process steam 148-193 | Is a source: supplies other end uses | — | natural gas, refinery fuel gas, oil, biomass, electricity (electric boilers, resistance heaters), thermal storage; CHP prime movers (gas turbines, engines, back-pressure turbines) | 200 °C is taken as the practical heat-pump delivery bound. Cogeneration is a technology on this band, not an end use: the heat is the service and the electricity a co-product (D1). 68 PJ of iron and steel fuel goes to on-site power-plant turbines, much of it coke-oven gas and coke; the share with heat recovery is not given. Share of steam-served heat at 150-400 °C: iron and steel 100%, other industry 74%, refining 68%, pulp and paper 19%, chemicals 17%. Drawn on by 11 end uses: `cokemaking`, `other-chemicals`, `renewable-diesel-and-saf`, `crude-distillation`, `conversion-and-treating`, `chemical-pulping` and 5 more. | NREL118; epa_2017_001; caelp_2024_001 p.11 uses 200 °C as the practical delivery bound, p.11; design doc s2; nrcan_2025_001 |
| **Heat, high temperature (> 400 °C)** `heat-high-temp` | Heat above 400 °C from fired heaters and furnaces separable from the process unit (refinery process heaters, generic industrial furnaces), and superheated steam above 400 °C. Excludes heat released inside a sector's process unit. | *high-temp*<br>> 400 | Is a source: supplies other end uses | — | natural gas, refinery fuel gas, oil, hydrogen, electricity (resistance, induction, plasma) | Refinery furnaces: 200-700 °C, 79 PJ (source bands < 200 / 200-700 / > 700 °C). Steam above 400 °C is rare: 2% of chemicals steam-served heat. Drawn on by 4 end uses: `direct-air-capture`, `renewable-diesel-and-saf`, `conversion-and-treating`, `bitumen-upgrading`. | NREL118; nrcan_2025_001; design doc s2 |
| **On-site power-only generation** `on-site-power-generation` | Electricity generated on site with no useful heat recovered: diesel and gas gensets at off-grid mines and oil-and-gas sites, gas turbines and engines, condensing steam turbines, power plants firing by-product gases, and solar, wind and storage in site microgrids. | — | — | — | diesel, natural gas, by-product gases, solar, wind, batteries | At isolated northern mines diesel is over 80% of energy use. Heat recovery separates it from CHP. | Energies 2026 mining review; nrcan_2025_001 |
| **Pumping** `pumping` | Motor-, engine- and turbine-driven pumps moving liquids and slurries around a site. Excludes pipeline pumping, which is an oil-and-gas end use. | *not-applicable*<br>— | — | — | electricity; natural gas or steam where the driver is a direct drive | Excludes pipeline pumping, which is an oil-and-gas end use. Drawn on by 18 end uses: `casting`, `rolling`, `steam-cracking`, `electrochemical-products`, `ethanol-production`, `crude-distillation` and 12 more. | EIA MECS 2018 |
| **Fans and blowers** `fans-and-blowers` | Process fans, blowers and induced- and forced-draught sets. Excludes building ventilation and mine ventilation, which are their own end uses. | *not-applicable*<br>— | — | — | electricity; natural gas or steam where the driver is a direct drive | EIA MECS splits machine drive into pumps, fans, compressed air, materials handling, materials processing and a residual; these five end uses follow that split, and the MECS residual is not carried - motor-driven equipment none of the five covers is filed under materials processing. Drawn on by 22 end uses: `co2-capture-diffuse`, `direct-air-capture`, `agglomeration`, `ironmaking`, `steelmaking`, `clinker-production` and 16 more. | EIA MECS 2018 |
| **Compressed air** `compressed-air` | Compressed-air systems and the process compression that serves them. Excludes pipeline and gas-processing compression, which are oil-and-gas end uses. | *not-applicable*<br>— | — (waste heat is recoverable to heat-low-temp) | — | electricity; natural gas or steam where the driver is a direct drive | Excludes gas-processing and pipeline compression, which are oil-and-gas end uses. Drawn on by 12 end uses: `co2-capture-concentrated`, `co2-capture-diffuse`, `renewable-natural-gas`, `centralised-hydrogen-production`, `refinery-hydrogen`, `paper-forming` and 6 more. | EIA MECS 2018 |
| **Materials handling** `materials-handling` | Conveyors, cranes, hoists, stackers and reclaimers moving solids around a site. | *not-applicable*<br>— | — | — | electricity; natural gas or steam where the driver is a direct drive | EIA MECS splits machine drive into pumps, fans, compressed air, materials handling, materials processing and a residual; these five end uses follow that split, and the MECS residual is not carried - motor-driven equipment none of the five covers is filed under materials processing. Drawn on by 6 end uses: `agglomeration`, `ironmaking`, `clinker-production`, `cement-grinding-and-blending`, `comminution`, `oil-sands-mining-and-extraction`. | EIA MECS 2018 |
| **Materials processing** `materials-processing` | Motor-driven size reduction, mixing, forming and separation that is NOT already counted in a sector end use - comminution, mechanical pulping, rolling and cement grinding all stay with their sector. | *not-applicable*<br>— | — | — | electricity; natural gas or steam where the driver is a direct drive | Excludes process electricity counted in a sector end use: EAF, electrolysis, mechanical-pulping refiners, comminution, cement grinding, rolling and pipeline compression. Drawn on by 5 end uses: `rolling`, `cement-grinding-and-blending`, `mechanical-and-recycled-pulping`, `comminution`, `wood-drying-and-pressing`. | EIA MECS 2018 |
| **Space heating** `space-heating` | Heating plant buildings and warehouses: unit heaters, radiant tubes, make-up air units and building heat pumps. | *low-temp*<br>< 150; site steam 121 (160-177 at a few SICs) | Integral (fired and electric unit heaters)<br>From `heat-low-temp` (site steam) | — | natural gas, propane, oil, electricity | Mine ventilation and mine air heating are a mining end use. | NREL97; CIMS |
| **Space cooling** `space-cooling` | Cooling plant offices, control rooms and production space. | — | — | — | electricity | — | CIMS |
| **Building ventilation** `ventilation` | Supply and exhaust air handling for buildings and production space. | — | — | — | electricity | Mine ventilation is a mining end use. | CIMS |
| **Lighting** `lighting` | Interior and yard lighting, and its controls. | — | — | — | electricity | — | CIMS |
| **On-site mobile equipment** `mobile-equipment` | Non-road vehicles and equipment used on site: construction equipment, loaders, forklifts, yard trucks, slag and log handling, oil-and-gas field vehicles. | — | — | — | diesel, propane, electricity (battery) | Construction is 3.1% of Canadian industrial energy, mostly off-road diesel; pulp and paper uses 1.3 PJ diesel. Excludes mine and oil-sands haul fleets. | NRCan Trends 2017; nrcan_2025_001; CIMS |
| **CO2 capture, concentrated streams** `co2-capture-concentrated` | Capture from concentrated, nitrogen-free process streams: ammonia, methanol and hydrogen plants (shifted syngas, acid-gas removal), gas-processing acid gas, ethanol fermentation, gasifiers, oxygen-blown iron routes, indirectly heated calciners, oxy-fuel flue gas. Mainly drying and compression. | — | — | `compressed-air` (dehydration and compression) | electricity (compression, dehydration) | Up to 99% reduction, TRL 9, <= USD40/t, available today; disposal of concentrated CO2 at USD15-40/t. HIsarna and syngas DRI are sourced as concentrated; smelting reduction, Corex and top-gas recycling are unsourced. An SMR emits both concentrated (shift) and dilute (furnace flue) CO2; CIMS books one rate. Integrated routes (hisarna-ccs, shaft-furnace_syngas_ccs, calciner_ccs) stay on their sector end use. CIMS has no capture on ethanol fermentation CO2. CIMS mapping: see How CIMS's capture requests split. Rows named `<host>_ccs-concentrated` point here; the capture plant is costed once on this end use, not repeated on the host row. | ipcc_2022_001 Table 11.3 p.37-38; CIMS |
| **CO2 capture, diffuse (dilute) streams** `co2-capture-diffuse` | Post-combustion capture from flue gas where the CO2 is diluted in nitrogen: boilers, CHP, fired heaters, cement and lime kiln stacks, cracker furnaces, FCC regenerators, sinter strands and EAF off-gas. | *low-temp (solvent regeneration)*<br>regeneration temperature not in held sources | From `heat-low-temp` (solvent regeneration) | `fans-and-blowers` (flue-gas booster fans)<br>`compressed-air` (CO2 compression) | steam or natural gas (regeneration), electricity (fans, compression) | Up to 90% reduction, TRL 6-7, <= USD120/t, from 2025. Cement: <= USD40/t for calcination CO2 from an indirect calciner, <= USD120/t for fuel CO2. 'Diffuse' = 'diluted in nitrogen'. Rows named `<host>_ccs-diffuse` point here; the capture plant is costed once on this end use, and the host row carries only its own effects, such as the steam drawn for regeneration. CIMS mapping: see How CIMS's capture requests split. Reboiler duty 3,750 kJ/kg CO2; CIMS assumes 3.4-4.8 GJ natural gas per t CO2. | ukerc_2013_001 CH-SC28 via johansson_2012_001; ipcc_2022_001 Table 11.3 p.37-38; CIMS |
| **Direct air capture** `direct-air-capture` | Capture of CO2 from ambient air (liquid solvent or solid sorbent) with compression, for storage or as a carbon feedstock. | *low-temp or high-temp (depends on the process)*<br>not in held sources; high (liquid-solvent calciner) or low (solid sorbent) | From `heat-high-temp` (liquid-solvent calciner)<br>From `heat-low-temp` (solid-sorbent regeneration) | `fans-and-blowers` (air contactors) | electricity (air contactors, compression), heat (natural gas, electricity, recovered heat) | Up to 99% reduction, TRL 3, about USD94-232/t, available by 2030; listed as a carbon source for CoOxHy fuels and feedstocks. Harmonized row tp-1509 stores its abatement cost as 2.0 USD/t (extraction error). | ipcc_2022_001 Table 11.3 p.38 |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `heat-low-temp` | **Fuel-fired boiler** | conventional | Fire-tube or water-tube boiler raising hot water or low-pressure steam. | natural gas, oil, propane, biomethane, hydrogen | 9 | packaged fire-tube boilers | commercial; iea_2024_001 rows 389, 387; etsap_2010_001; CIMS |
|  | **Boiler with post-combustion capture** | prospective | The boiler above with an amine or solid-sorbent plant on the flue gas; the regeneration steam is drawn from the boiler itself.<br>*Flue gas is dilute, so the capture plant is the one on cross-sector co2-capture-diffuse and its cost and energy are not repeated here. The steam taken for regeneration is the host-side penalty and belongs on this row. Biomass firing makes it a removal.* | natural gas, oil, biomass, by-product gases; steam and electricity for the capture plant | 5 | — | iea_2024_001 row 422; 8-9 at power-station scale; CIMS |
|  | **Condensing boiler** | efficient variant | Recovers latent heat from the flue gas; needs a low return-water temperature.<br>*Hot-water duties only.* | natural gas, biomethane, hydrogen | 9 | — | commercial; CIMS |
|  | **Solid-fuel boiler** | conventional | Grate or fluidised-bed boiler firing solid fuels. | biomass (hog fuel, pellets), coal, municipal waste | 9 | mill hog-fuel boilers | iea_2024_001 row 388; CIMS |
|  | **Electric boiler** | alternative | Resistance or electrode boiler raising hot water or steam at about 99% efficiency. | electricity | 9 | electrode boilers at MW scale | iea_2024_001 row 437; lbnl_2021_001 |
|  | **Industrial heat pump** | alternative | Closed-cycle heat pump lifting waste or ambient heat to hot water or low-pressure steam.<br>*Commercial ceiling about 150-165 °C.* | electricity; recovered heat | 9 | ammonia and CO2 heat pumps on washing and drying duties | iea_2024_001 row 390; etsap_2013_002 |
|  | **Mechanical vapour recompression** | alternative | Compresses process vapour and returns it as usable heat, replacing live steam. | electricity | 9 | MVR evaporators and dryers | commercial; harmonized |
|  | **Solar thermal collectors** | alternative | Flat-plate or evacuated-tube collectors for hot water and low-pressure steam. | solar | 9 | — | iea_2024_001 row 536 |
|  | **Waste-heat recovery unit** | conventional | Economisers and heat exchangers recovering heat from flue gas or process streams. | recovered heat | 9 | — | commercial; harmonized |
|  | **Geothermal direct use** | prospective | Hot water drawn from a geothermal well.<br>*Little Canadian industrial use.* | geothermal | 8 | — | design doc s4.1 |
|  | **Direct-fired air or water heater** | conventional | Burner heating air or water directly for washing, drying and space duties. | natural gas, propane, biomethane, hydrogen | 9 | make-up air heaters, direct-contact water heaters | commercial; CIMS |
|  | **Fired heater efficiency measures, moderate** | efficient variant | Combustion and recovery measures on an existing fired heater or boiler plant.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, refinery fuel gas, oil, by-product gases | 9 | combustion-air preheat; oxygen trim and burner control; economiser; insulation and steam-trap programmes | commercial; ukerc_2013_001; harmonized |
|  | **Fired heater efficiency measures, strong** | efficient variant | Air preheat taken to recuperation or regeneration, with the heater train integrated.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, refinery fuel gas, oil, by-product gases; recovered heat | 9 | recuperative or regenerative burners; condensing economiser; pinch-designed preheat train | commercial; ukerc_2013_001; harmonized |
|  | **Back-pressure or extraction steam turbine** | conventional | Boiler raises high-pressure steam; the turbine passes it to process at lower pressure.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, oil, coal, biomass, black liquor, by-product gas | 9 | — | commercial; epa_2017_001; CIMS |
|  | **Gas turbine with heat-recovery steam generator** | conventional | Turbine exhaust raises process steam in an HRSG.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, hydrogen (TRL 8 pure, 9 blended), biogas | 9 | — | commercial; iea_2024_001 rows 255, 252; epa_2017_001; CIMS |
|  | **Combined-cycle CHP** | conventional | Gas turbine plus steam turbine, with steam extracted for process.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas | 9 | — | commercial; epa_2017_001; CIMS |
|  | **CHP with post-combustion capture** | prospective | Capture plant on the turbine or engine exhaust, with the regeneration steam taken from the unit, which cuts the heat delivered to the site.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. The heat-to-power ratio after extraction is the host-side fact this row carries. CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, biogas, by-product gases; steam and electricity for the capture plant | 8 | — | iea_2024_001 row 215; CIMS |
|  | **Reciprocating engine CHP** | conventional | Engine generator with jacket and exhaust heat recovery, at small scale.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, biogas | 9 | — | commercial; epa_2017_001; CIMS |
|  | **Fuel-cell CHP** | alternative | Solid-oxide or molten-carbonate cell producing power and usable heat.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, hydrogen, biogas | 8-9 | — | iea_2024_001 rows 256, 254 |
|  | **Biomass gasifier CHP** | prospective | Gasifier feeding an engine or turbine, with heat recovery.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | biomass, waste | 6 | — | iea_2024_001 row 274; epa_2007_001 |
|  | **Small modular reactor CHP** | prospective | Reactor supplying process steam and electricity to an industrial site. | nuclear | 7-8 | Dow Seadrift with X-energy Xe-100 | iea_2024_001 rows 451, 455; X-energy/Dow |
| `heat-medium-temp` | **Fuel-fired boiler** | conventional | Water-tube boiler raising medium- or high-pressure steam. | natural gas, oil, by-product gas, biomethane, hydrogen | 9 | — | commercial; iea_2024_001 row 379; etsap_2010_001; CIMS |
|  | **Boiler with post-combustion capture** | prospective | The boiler above with an amine or solid-sorbent plant on the flue gas; the regeneration steam is drawn from the boiler itself.<br>*Flue gas is dilute, so the capture plant is the one on cross-sector co2-capture-diffuse and its cost and energy are not repeated here. Regeneration steam at 120-150 °C competes with the medium-temperature duties this band serves.* | natural gas, oil, biomass, by-product gases; steam and electricity for the capture plant | 5 | — | iea_2024_001 row 422; 8-9 at power-station scale; CIMS |
|  | **Solid-fuel boiler** | conventional | Grate or fluidised-bed boiler firing solid fuels. | biomass, coal, waste | 9 | — | iea_2024_001 row 388 |
|  | **Electric boiler** | alternative | Electrode boiler at MW scale raising saturated steam. | electricity | 9 | — | iea_2024_001 row 437; lbnl_2021_001 |
|  | **Steam-generating heat pump** | prospective | High-temperature heat pump delivering steam to about 180-200 °C from waste heat. | electricity; recovered heat | 7 | Heaten HeatBooster (180 °C steam, Suedzucker 2025) | iea_2024_001 rows 57, 438; Heaten |
|  | **Mechanical vapour recompression** | alternative | Steam compressor upgrading low-pressure waste steam to process pressure. | electricity | 9 | — | commercial; harmonized |
|  | **Electric thermal energy storage** | prospective | Electrically charged solid or salt store discharging steam, decoupling heat from power prices. | electricity | 8 | Rondo (100 MWh, >100 bar steam, California, October 2025); Kraftblock; Antora | iea_2024_001 row 174; Rondo 2025 |
|  | **Thermal-oil heater** | conventional | Fired or electric heater circulating thermal fluid at 200-400 °C without pressure. | natural gas, oil, electricity | 9 | — | commercial; harmonized |
|  | **Fired process heater** | conventional | Direct-fired heater raising a process stream, as in refinery charge heaters and dryers. | natural gas, refinery fuel gas, oil | 9 | — | commercial; CIMS |
|  | **Fired heater efficiency measures, strong** | efficient variant | Air preheat taken to recuperation or regeneration, with the heater train integrated.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, refinery fuel gas, oil, by-product gases; recovered heat | 9 | recuperative or regenerative burners; condensing economiser; pinch-designed preheat train | commercial; ukerc_2013_001; harmonized |
|  | **Fired heater efficiency measures, moderate** | efficient variant | Combustion and recovery measures on an existing fired heater or boiler plant.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, refinery fuel gas, oil, by-product gases | 9 | combustion-air preheat; oxygen trim and burner control; economiser; insulation and steam-trap programmes | commercial; ukerc_2013_001; harmonized |
|  | **Electric process heater** | alternative | Resistance heater raising a gas or liquid stream in place of a fired heater. | electricity | 9 | large circulation heaters | commercial; CIMS |
|  | **Electromagnetic heating (microwave, radio-frequency, infrared)** | alternative | Heats the product itself rather than the surrounding air; used in drying and curing. | electricity | 9 | — | iea_2024_001 rows 382, 384, 385 |
|  | **Concentrating solar thermal** | prospective | Parabolic trough or linear Fresnel field raising steam or thermal oil. | solar | 7-9 | — | iea_2024_001 rows 535, 534 |
|  | **Back-pressure or extraction steam turbine** | conventional | Boiler raises high-pressure steam; the turbine passes it to process at lower pressure.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, oil, coal, biomass, black liquor, by-product gas | 9 | — | commercial; epa_2017_001; CIMS |
|  | **Gas turbine with heat-recovery steam generator** | conventional | Turbine exhaust raises process steam in an HRSG.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, hydrogen (TRL 8 pure, 9 blended), biogas | 9 | — | commercial; iea_2024_001 rows 255, 252; epa_2017_001; CIMS |
|  | **Combined-cycle CHP** | conventional | Gas turbine plus steam turbine, with steam extracted for process.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas | 9 | — | commercial; epa_2017_001; CIMS |
|  | **CHP with post-combustion capture** | prospective | Capture plant on the turbine or engine exhaust, with the regeneration steam taken from the unit, which cuts the heat delivered to the site.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. The heat-to-power ratio after extraction is the host-side fact this row carries. CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, biogas, by-product gases; steam and electricity for the capture plant | 8 | — | iea_2024_001 row 215; CIMS |
|  | **Reciprocating engine CHP** | conventional | Engine generator with jacket and exhaust heat recovery, at small scale.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, biogas | 9 | — | commercial; epa_2017_001; CIMS |
|  | **Fuel-cell CHP** | alternative | Solid-oxide or molten-carbonate cell producing power and usable heat.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | natural gas, hydrogen, biogas | 8-9 | — | iea_2024_001 rows 256, 254 |
|  | **Biomass gasifier CHP** | prospective | Gasifier feeding an engine or turbine, with heat recovery.<br>*CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.* | biomass, waste | 6 | — | iea_2024_001 row 274; epa_2007_001 |
|  | **Small modular reactor CHP** | prospective | Reactor supplying process steam and electricity to an industrial site. | nuclear | 7-8 | Dow Seadrift with X-energy Xe-100 | iea_2024_001 rows 451, 455; X-energy/Dow |
| `heat-high-temp` | **Fired furnace or process heater** | conventional | Burner-fired furnace or heater above 400 °C, separable from the process unit. | natural gas, oil, refinery and by-product gas, biomethane (TRL 9), hydrogen (TRL 8), ammonia (TRL 5) | 9 | — | commercial; iea_2024_001 rows 378, 379, 377; CIMS |
|  | **Fired heater or furnace with post-combustion capture** | prospective | Capture plant on the flue gas of a fired heater or furnace; the delivered duty is unchanged and the regeneration steam is imported.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. What holds this back is the number of small stacks, not the chemistry.* | natural gas, refinery fuel gas, by-product gases; steam and electricity for the capture plant | 3-4 | — | iea_2024_001 row 228; CIMS |
|  | **Regenerative or oxy-fuel burner furnace** | efficient variant | Preheats combustion air, or fires on oxygen, cutting flue-gas losses. | natural gas, oil, hydrogen; oxygen | 9 | regenerative burners; oxy-fuel glass furnaces | commercial; CIMS |
|  | **Electric resistance furnace** | alternative | Resistance elements heating the charge or chamber directly. | electricity | 9 | heat-treatment furnaces | commercial; harmonized |
|  | **Induction heating** | alternative | Induces eddy currents in the workpiece; for conductive materials. | electricity | 9 | billet and slab induction heaters | iea_2024_001 row 372; CIMS |
|  | **Electric arc or plasma heating** | prospective | Arc or plasma torch heating a gas or charge to very high temperature. | electricity | 6 | — | iea_2024_001 row 371 |
|  | **Rotodynamic heater** | prospective | Rotating machine converting electricity to heat in a gas stream at furnace temperatures. | electricity | 6 | Coolbrook RotoDynamic Heater (over 1,000 °C in pilot, Brightlands Chemelot) | iea_2024_001 row 375; Coolbrook 2024 |
|  | **Electric thermal energy storage** | prospective | Electrically charged refractory or carbon store discharging hot gas above 1,000 °C. | electricity | 8 | Rondo; Antora; Kraftblock | iea_2024_001 row 174; Rondo 2025 |
|  | **Concentrating solar for high-temperature heat** | prospective | Solar tower or dish concentrating to furnace temperatures. | solar | 6 | — | iea_2024_001 row 381 |
|  | **High-temperature gas-cooled reactor** | prospective | Small modular reactor delivering high-temperature steam or process heat. | nuclear | 8 | Dow Seadrift with X-energy Xe-100 (construction permit under review) | iea_2024_001 row 451; X-energy/Dow |
| `on-site-power-generation` | **Diesel generator set** | conventional | Reciprocating diesel generator, the standard off-grid supply. | diesel, renewable diesel | 9 | off-grid mine power plants | commercial; Energies 2026 mining review |
|  | **Generating set efficiency measures, moderate** | efficient variant | Raising the electrical efficiency of an existing on-site set.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, diesel, by-product gases | 9 | combined-cycle conversion of a simple-cycle set; lean-burn engine upgrade; turbine inlet cooling | commercial; harmonized |
|  | **Gas engine or simple-cycle gas turbine** | conventional | Gas-fired generator without heat recovery. | natural gas, associated gas | 9 | upstream oil and gas sites | iea_2024_001 row 214 |
|  | **Condensing steam turbine** | conventional | Boiler and condensing turbine producing power only. | natural gas, coal, biomass, by-product gas | 9 | steelworks power plants firing coke-oven gas | commercial; harmonized; nrcan_2025_001 |
|  | **Waste-heat power (ORC or steam Rankine)** | alternative | Converts exhaust or process heat to electricity. | recovered heat | 9 | ORC on kiln and compressor exhaust | iea_2024_001 row 516 |
|  | **Solar PV with battery storage** | alternative | Site-scale PV and storage displacing genset fuel. | solar; electricity storage | 9 | remote mine microgrids | iea_2024_001 rows 527, 580 |
|  | **Wind turbines at site** | alternative | Site wind generation, usually with storage, at remote operations. | wind | 9 | Raglan Mine (Nunavik) wind and storage | commercial; Energies 2026 mining review |
|  | **Microreactor** | prospective | Factory-built heat-pipe reactor sized for a remote site. | nuclear | 5 | Westinghouse eVinci | iea_2024_001 row 450 |
| `pumping` | **Induction motor, standard efficiency** | conventional | IE2-IE3 squirrel-cage motor driving a pump, fan or compressor. | electricity | 9 | — | commercial; CIMS |
|  | **Premium-efficiency motor** | efficient variant | IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs. | electricity | 9 | — | commercial; CIMS |
|  | **Variable-speed drive** | efficient variant | Matches motor speed to load instead of throttling. | electricity | 9 | — | commercial; CIMS |
|  | **Gas engine or gas turbine drive** | conventional | Engine or turbine driving a compressor or pump directly. | natural gas | 9 | pipeline and field compressors | iea_2024_001 row 214; CIMS |
|  | **Turbine or engine drive efficiency measures, moderate** | efficient variant | Driver upgrades and staging on gas-driven compression and pumping.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, field gas | 9 | high-efficiency gas-turbine drives; lean-burn engine retrofit; driver right-sizing and staging | commercial; harmonized |
|  | **Steam turbine drive** | conventional | Back-pressure turbine driving a large compressor or pump. | steam | 9 | refinery and chemical compressor drives | commercial; harmonized |
|  | **Pump system optimisation** | efficient variant | Right-sizing, impeller trimming and control changes on the pump system rather than the pump. | electricity | 9 | impeller trimming; parallel staging; control-valve removal | commercial; harmonized |
| `fans-and-blowers` | **Induction motor, standard efficiency** | conventional | IE2-IE3 squirrel-cage motor driving a pump, fan or compressor. | electricity | 9 | — | commercial; CIMS |
|  | **Premium-efficiency motor** | efficient variant | IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs. | electricity | 9 | — | commercial; CIMS |
|  | **Variable-speed drive** | efficient variant | Matches motor speed to load instead of throttling. | electricity | 9 | — | commercial; CIMS |
|  | **Gas engine or gas turbine drive** | conventional | Engine or turbine driving a compressor or pump directly. | natural gas | 9 | pipeline and field compressors | iea_2024_001 row 214; CIMS |
|  | **Turbine or engine drive efficiency measures, moderate** | efficient variant | Driver upgrades and staging on gas-driven compression and pumping.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, field gas | 9 | high-efficiency gas-turbine drives; lean-burn engine retrofit; driver right-sizing and staging | commercial; harmonized |
|  | **Steam turbine drive** | conventional | Back-pressure turbine driving a large compressor or pump. | steam | 9 | refinery and chemical compressor drives | commercial; harmonized |
|  | **Fan system optimisation** | efficient variant | High-efficiency fan selection with duct and damper changes. | electricity | 9 | airfoil fans; damper-to-VSD conversion; duct resizing | commercial; harmonized |
| `compressed-air` | **Induction motor, standard efficiency** | conventional | IE2-IE3 squirrel-cage motor driving a pump, fan or compressor. | electricity | 9 | — | commercial; CIMS |
|  | **Premium-efficiency motor** | efficient variant | IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs. | electricity | 9 | — | commercial; CIMS |
|  | **Variable-speed drive** | efficient variant | Matches motor speed to load instead of throttling. | electricity | 9 | — | commercial; CIMS |
|  | **Gas engine or gas turbine drive** | conventional | Engine or turbine driving a compressor or pump directly. | natural gas | 9 | pipeline and field compressors | iea_2024_001 row 214; CIMS |
|  | **Turbine or engine drive efficiency measures, moderate** | efficient variant | Driver upgrades and staging on gas-driven compression and pumping.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, field gas | 9 | high-efficiency gas-turbine drives; lean-burn engine retrofit; driver right-sizing and staging | commercial; harmonized |
|  | **Steam turbine drive** | conventional | Back-pressure turbine driving a large compressor or pump. | steam | 9 | refinery and chemical compressor drives | commercial; harmonized |
|  | **Compressed-air system management** | efficient variant | Leak management, pressure reduction and sequencing across the compressor house. | electricity | 9 | leak surveys; pressure optimisation; sequencing controls; heat recovery | commercial; harmonized |
| `materials-handling` | **Induction motor, standard efficiency** | conventional | IE2-IE3 squirrel-cage motor driving a pump, fan or compressor. | electricity | 9 | — | commercial; CIMS |
|  | **Premium-efficiency motor** | efficient variant | IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs. | electricity | 9 | — | commercial; CIMS |
|  | **Variable-speed drive** | efficient variant | Matches motor speed to load instead of throttling. | electricity | 9 | — | commercial; CIMS |
|  | **Conveying in place of truck haulage** | efficient variant | Fixed conveying and hoisting replacing engine-driven movement of solids. | electricity | 9 | in-pit crushing and conveying; overland conveyors | commercial; harmonized |
| `materials-processing` | **Induction motor, standard efficiency** | conventional | IE2-IE3 squirrel-cage motor driving a pump, fan or compressor. | electricity | 9 | — | commercial; CIMS |
|  | **Premium-efficiency motor** | efficient variant | IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs. | electricity | 9 | — | commercial; CIMS |
|  | **Variable-speed drive** | efficient variant | Matches motor speed to load instead of throttling. | electricity | 9 | — | commercial; CIMS |
| `space-heating` | **Fuel-fired space or make-up air heater** | conventional | Unit heaters, radiant tubes and make-up air units firing gas. | natural gas, propane, oil | 9 | — | commercial; CIMS |
|  | **Space-heating heat pump** | alternative | Air-source or ground-source heat pump for building heat and cooling. | electricity | 9 | — | iea_2024_001 rows 53, 75 |
|  | **Electric resistance space heating** | conventional | Unit heaters and baseboards. | electricity | 9 | — | commercial; CIMS |
| `lighting` | **Fluorescent or high-intensity discharge lighting** | conventional | The incumbent industrial lighting stock. | electricity | 9 | — | commercial; CIMS |
|  | **LED lighting with controls** | efficient variant | Solid-state lighting with occupancy and daylight controls. | electricity | 9 | — | commercial; CIMS |
| `mobile-equipment` | **Diesel non-road equipment** | conventional | Loaders, forklifts, yard trucks and construction equipment on diesel engines. | diesel, renewable diesel, biodiesel blends | 9 | — | commercial; CIMS |
|  | **Propane or natural gas forklift** | conventional | Spark-ignition industrial truck. | propane, natural gas | 9 | — | commercial; harmonized |
|  | **Battery-electric equipment** | alternative | Battery drive for forklifts, loaders and excavators. | electricity | 8-9 | — | iea_2024_001 row 135; commercial for forklifts; CIMS |
|  | **Hydrogen fuel-cell equipment** | prospective | Fuel-cell drive, commercial in forklifts and in demonstration for heavy equipment.<br>*TRL spans the two classes of equipment.* | hydrogen | 6-9 | — | commercial; demonstration; harmonized |
|  | **Diesel-electric hybrid equipment** | efficient variant | Series or parallel hybrid drive recovering braking and smoothing engine load. | diesel, electricity | 9 | — | commercial; harmonized |
| `co2-capture-concentrated` | **Dehydration and compression** | conventional | Dries and compresses an already pure CO2 stream for transport. | electricity | 9 | Alberta Carbon Trunk Line: Nutrien Redwater fertiliser plant; ethanol plants | ipcc_2022_001 Table 11.3 |
|  | **Chemical solvent on process gas** | conventional | Amine absorption on shifted syngas or acid gas, then regeneration. | steam, electricity | 9 | Quest (Shell Scotford upgrader hydrogen units) | iea_2024_001 row 285; CIMS |
|  | **Physical solvent** | conventional | Selexol or Rectisol absorption at pressure on gasifier syngas. | electricity, steam | 9 | Sturgeon refinery | commercial; harmonized |
|  | **Pressure or vacuum swing adsorption** | conventional | Adsorbent beds separating CO2 from hydrogen-plant syngas. | electricity | 9 | Air Products Port Arthur | commercial; harmonized |
|  | **Cryogenic separation** | prospective | Condenses CO2 from a pressurised stream at low temperature. | electricity | 6 | Air Liquide Cryocap | iea_2024_001 row 334 |
| `co2-capture-diffuse` | **Amine post-combustion capture** | conventional | Absorbs CO2 from flue gas into an amine solvent; steam strips it back out.<br>*TRL 9 in power, 7-8 on cement kilns.* | steam (reboiler), electricity | 7-9 | Boundary Dam (Cansolv); Entropy Glacier; Brevik cement | iea_2024_001 rows 332, 333; ipcc_2022_001 Table 11.3 |
|  | **Advanced low-energy solvent** | efficient variant | Second-generation solvents cutting reboiler duty against first-generation MEA. | steam, electricity | 8 | KS-21; Cansolv DC-103 | assessed; harmonized |
|  | **Solid sorbent capture** | prospective | Structured adsorbent beds cycling on temperature or pressure, with lower heat demand. | low-temperature heat, electricity | 6 | Svante (Lafarge Richmond pilot) | iea_2024_001 row 337; Svante |
|  | **Calcium looping** | prospective | Lime carries CO2 between a carbonator and a calciner, with high-grade heat recovery. | fuel, electricity | 7 | — | iea_2024_001 row 331 |
|  | **Cryogenic post-combustion capture** | prospective | Chills flue gas so CO2 desublimates or condenses out. | electricity | 6 | — | iea_2024_001 row 334 |
| `direct-air-capture` | **Liquid-solvent DAC** | prospective | Alkaline solution captures CO2; a high-temperature calciner regenerates it. | natural gas or electricity (calciner), electricity | 6 | Carbon Engineering (Squamish); 1PointFive Stratos | iea_2024_001 row 95; Stratos |
|  | **Solid-sorbent DAC** | prospective | Sorbent beds cycled at low temperature, suited to waste heat and modular build. | low-temperature heat, electricity | 7 | Climeworks; Deep Sky Alpha (Innisfail, Alberta, operating since August 2025) | iea_2024_001 row 96; Deep Sky 2025 |
| `space-cooling` | **Packaged air conditioner or rooftop unit** | conventional | Direct-expansion cooling with an air handler. | electricity | 9 | — | commercial; CIMS |
|  | **Chilled-water system** | conventional | Central chiller serving air handlers through chilled water. | electricity | 9 | — | commercial; harmonized |
|  | **Reversible heat pump** | alternative | One machine providing both building heat and cooling. | electricity | 9 | — | iea_2024_001 rows 53, 75 |
|  | **Free or evaporative cooling** | efficient variant | Uses ambient air or evaporation before running the refrigeration cycle. | electricity; water | 9 | — | commercial; harmonized |
| `ventilation` | **Constant-volume fan system** | conventional | Supply and exhaust fans running at fixed flow. | electricity | 9 | — | commercial; CIMS |
|  | **Variable-speed fans** | efficient variant | Fan speed follows the load instead of throttling or running flat out. | electricity | 9 | — | commercial; CIMS |
|  | **Heat-recovery ventilation** | efficient variant | Exhaust air preheats or precools the incoming supply air. | electricity; recovered heat | 9 | — | commercial; harmonized |
|  | **Demand-controlled ventilation** | efficient variant | Air flow set by occupancy or contaminant sensing. | electricity | 9 | — | commercial; harmonized |

<br>

---

### Iron and steel

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Cokemaking** `cokemaking` | Coke ovens and the by-product plant. | *high-temp*<br>coal heated to 1000-1100, flue gas 1150-1350; coking 1427; by-product plant steam 177 | Integral (ovens)<br>From `heat-medium-temp` (by-product plant) | — | coking coal; coke-oven and blast-furnace gas for underfiring | 16.9 PJ coke and coke-oven gas at > 700 °C. | etsap_2010_002 p.2; NREL97 SIC 3312; nrcan_2025_001 |
| **Sintering and pelletising** `agglomeration` | Sinter plants and pellet induration at the steelworks. | *high-temp*<br>sintering 1371, pelletizing 1316; pelletizing 1000-1200 | Integral (sinter strand and induration furnace) | `fans-and-blowers` (windboxes and cooler fans)<br>`materials-handling` (feed and product) | coke breeze, natural gas, oil, electricity | Most Canadian pellets are made at the mine; see mining pelletising, which uses the same technologies. | NREL97 SIC 3312; rtc_2023_001 p.75 |
| **Ironmaking** `ironmaking` | Reduction of iron ore: blast furnace with hot stoves, direct reduction (shaft furnace with reformer or hydrogen), smelting reduction. The routes compete to supply the same service. | *high-temp*<br>blast furnace 2200-2300; plasma blast furnace flame 2150; site steam 177 (NREL-assigned) | Integral (blast furnace and stoves, DRI shaft, smelter) | `fans-and-blowers` (blast-furnace blowers)<br>`steel-oxygen-supply` (enrichment)<br>`materials-handling` (burden and product) | coke and PCI coal as reductant and fuel; natural gas (DRI, injection); hydrogen (future DRI); electricity (plasma, electric smelting) | Blast furnaces 40.7 PJ; DRI methane reformer 14.4 PJ natural gas. CIMS does not split ironmaking from steelmaking. | rtc_2023_001 p.75; etsap_2010_002 p.4; NREL118; nrcan_2025_001 |
| **Steelmaking** `steelmaking` | BOF and EAF (scrap and DRI charge), ladle metallurgy and ladle preheating. | *high-temp*<br>BOF 1600, EAF 1800 | Integral (converter and arc) | `steel-oxygen-supply` (BOF blowing and EAF lancing)<br>`fans-and-blowers` (fume extraction) | electricity (EAF); oxygen; chemical heat of hot metal; natural gas (ladle preheat, oxy-fuel burners); charge carbon | Scrap availability bounds the EAF share. | rtc_2023_001 p.36, p.75; nrcan_2025_001 |
| **Oxygen supply** `steel-oxygen-supply` | Cryogenic and adsorption air separation supplying oxygen to the basic oxygen furnace, the electric arc furnace and the blast furnace, on site or over the fence. | *not-applicable*<br>— | — (the air compressors are the process) | — | electricity (compression) | Serves BOF and EAF steelmaking and blast-furnace enrichment. Oxygen for glass oxy-fuel firing, oxy-fuel capture and merchant industrial gases is not carried as an end use (3% of US chemical-sector energy, 96 TBtu, sits in merchant plants). Drawn on by 2 end uses: `ironmaking`, `steelmaking`. | nrcan_2025_001 |
| **Casting** `casting` | Ingot, continuous, thin-slab and strip casting of liquid steel into semis. | *high-temp*<br>liquid steel about 1600 | Integral (tundish and mould, and ingot soaking pits) | `pumping` (mould and machine cooling water) | electricity, water; natural gas and oil (ingot soaking pits) | — | rtc_2023_001 p.36; CIMS |
| **Reheating** `reheating` | Reheating slabs, billets and blooms to rolling temperature, and hot charging that avoids it. | *high-temp*<br>reheating to 1000-1300; heating 1316 | Integral (reheating furnaces) | — | natural gas, coke-oven and blast-furnace gas, oil, electricity (induction) | High-temperature furnaces 45.9 PJ (natural gas, coal, coke-oven gas) at > 700 °C. | rtc_2023_001 p.75; NREL97 SIC 3312; nrcan_2025_001 |
| **Hot and cold rolling** `rolling` | Roughing and finishing stands, section, bar, rod and tube mills, tandem and reversing cold mills, acid pickling and skin pass. | *low-temp*<br>pickling and rinse baths; pickling steam 160 | From `heat-low-temp` (pickling and cleaning baths) | `materials-processing` (mill drives)<br>`pumping` (roll cooling and hydraulics) | electricity (mill drives, electrolytic cleaning), steam, acid | Rolling heat comes from reheating. | NREL97 SIC 3312; CIMS; ukerc_2013_001 |
| **Annealing and coating** `annealing-and-coating` | Batch and continuous annealing, tempering, electrical-steel treatment, hot-dip galvanising, electro-galvanising and tin plating. | *high-temp*<br>annealing 760 (fuel); annealing steam 160; molten zinc about 460 | Integral (annealing and line furnaces, zinc pots) | — | natural gas, oil, electricity; hydrogen or nitrogen atmosphere; zinc, tin | Zinc-bath temperature is not in held or checked sources. | NREL97 SIC 3312; CIMS |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `cokemaking` | **By-product coke oven battery** | conventional | Slot ovens carbonising coal, with the gas cleaned and recovered as coke-oven gas and chemicals. | coking coal; coke-oven and blast-furnace gas (underfiring) | 9 | ArcelorMittal Dofasco coke plant (Hamilton); Algoma ovens decommissioned January 2026 | commercial; etsap_2010_002; Algoma 2025; GEM Dofasco |
|  | **Coke oven efficiency measures, strong** | efficient variant | Recovering the heat now lost in quenching and in the raw gas, the measures the roster files as the strong bucket.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column. Dry quenching raises steam and cuts coke breeze, and is the measure this bucket is usually named for.* | coke-oven gas; recovered heat (raises steam) | 9 | coke dry quenching; coke-oven gas sensible-heat recovery | commercial; ukerc_2013_001; harmonized |
|  | **Coke oven efficiency measures, moderate** | efficient variant | Battery housekeeping and control, each worth a few per cent of heating fuel.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coke-oven gas, blast-furnace gas, natural gas | 9 | reduced air leakage; battery insulation; heating control and pressure regulation | commercial; ukerc_2013_001; harmonized |
|  | **Heat-recovery coke oven** | alternative | Non-recovery ovens burning the volatiles on site and raising steam for power.<br>*No Canadian stock.* | coking coal | 9 | — | commercial; harmonized |
| `agglomeration` | **Sinter strand** | conventional | Travelling-grate strand fusing ore fines, fluxes and coke breeze into sinter. | coke breeze, natural gas, electricity | 9 | — | commercial; CIMS; etsap_2010_002 |
|  | **Sinter plant efficiency measures, strong** | efficient variant | Recirculating part of the waste gas and recovering cooler heat.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coke breeze, natural gas; recovered heat | 9 | waste-gas recirculation (EPOSINT, EOS); sinter-cooler exhaust gas heat recovery | commercial; ukerc_2013_001; harmonized |
|  | **Sinter plant efficiency measures, moderate** | efficient variant | Charging, bed and sealing measures on an existing sinter strand.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coke breeze, natural gas | 9 | improved charging; increased bed depth; reduced air leakage; ignition-hood control | commercial; ukerc_2013_001; harmonized |
|  | **Pellet induration (straight-grate, grate-kiln)** | conventional | Hardens green pellets on a travelling grate or grate-kiln.<br>*Most Canadian pelletising is at the mines; see mining pelletising.* | heavy oil, natural gas, coke/coal, electricity | 9 | — | commercial; nrcan_2025_001 |
|  | **Plasma or electric induration** | prospective | Replaces the burner with plasma torches or electric heating in the induration furnace. | electricity | 5 | LKAB plasma trials | iea_2024_001 row 409 |
| `ironmaking` | **Blast furnace** | conventional | Coke-based counter-current shaft reducing iron ore to hot metal, with hot stoves. | coke, pulverised coal, natural gas; hydrogen injection (TRL 7), biomass or charcoal injection (TRL 9) | 9 | Stelco Lake Erie; ArcelorMittal Dofasco BF2 and BF4 (retirement scheduled 2030) | commercial; iea_2024_001 rows 406, 410; CIMS; GEM Dofasco |
|  | **Blast furnace efficiency measures, strong** | efficient variant | Heat recovery off the stoves and the slag, the measures the roster separates as the strong bucket.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coke, coal, natural gas, by-product gases; recovered heat | 9 | hot stove waste-heat recovery; slag heat recovery; top-gas heat recovery | commercial; ukerc_2013_001; harmonized |
|  | **Blast furnace efficiency measures, moderate** | efficient variant | Incremental measures on an existing blast furnace, each worth a few per cent of fuel.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coke, coal, natural gas, by-product gases | 9 | top-pressure recovery turbine; improved burden distribution; higher pulverised coal injection; dry gas cleaning | commercial; ukerc_2013_001; harmonized |
|  | **Blast furnace with post-combustion capture** | prospective | Capture on the blast-furnace gas, or on the stoves and power plant that burn it.<br>*Blast-furnace gas is about a fifth CO2, so this is the dilute plant on cross-sector co2-capture-diffuse. Top-gas recycling concentrates the stream instead and is its own row.* | coke, coal, natural gas; steam and electricity for the capture plant | 5 | — | iea_2024_001 row 412; CIMS |
|  | **Top-gas recycling oxygen blast furnace** | prospective | Oxygen blast with CO2 stripped from the recycled top gas, which also concentrates the CO2.<br>*Recycling concentrates the top gas, so capture sits on cross-sector co2-capture-concentrated rather than the dilute plant a conventional blast furnace needs.* | coke, coal, oxygen; electricity | 6 | ULCOS experimental blast furnace; COURSE50 | ukerc_2013_001 via harmonized; iea_2024_001 row 412; CIMS |
|  | **Shaft-furnace direct reduction** | conventional | Reduces pellets in a shaft with reformed gas or hydrogen, giving solid DRI for an EAF. | natural gas (TRL 9), hydrogen (TRL 6-7) | 9 | MIDREX; Energiron; ArcelorMittal Contrecoeur; Dofasco Energiron ZR project (2.5 Mt/yr, announced); HYBRIT; Stegra | iea_2024_001 rows 394, 392, 395; CIMS; GEM Dofasco |
|  | **Gas-based direct reduction with capture on the CO2 removal unit** | alternative | A gas-based DRI plant already strips CO2 from the recycled top gas, so capture is dehydration and compression on a nearly pure stream.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. The reformer and heater flue gas is a separate, dilute stream.* | natural gas; electricity for compression | 9 | Al Reyadah, Abu Dhabi | iea_2024_001 row 394; CIMS |
|  | **Fluidised-bed direct reduction** | prospective | Reduces ore fines directly, skipping pelletising. | hydrogen, natural gas | 6 | HYFOR; Circored | assessed (Primetals HYFOR pilot; Circored operated commercially); HYFOR |
|  | **Bath smelting reduction** | prospective | Smelts coal and ore fines in one vessel, with no coke ovens or sinter plant; off-gas is CO2-rich.<br>*Oxygen blowing concentrates the off-gas, so capture sits on cross-sector co2-capture-concentrated rather than the dilute plant a blast furnace needs.* | coal, oxygen | 6 | HIsarna pilot at Tata Steel IJmuiden (60 kt/yr) | ukerc_2013_001 via harmonized; iea_2024_001 row 415; GEM HIsarna |
|  | **Two-stage smelting reduction** | alternative | Pre-reduction shaft plus a melter-gasifier running on coal, avoiding coke ovens.<br>*No Canadian stock.* | coal, oxygen | 9 | Corex; Finex | commercial; etsap_2010_002; CIMS |
|  | **Electric smelting furnace for DRI** | prospective | Melts DRI made from lower-grade ore into hot metal for a BOF, removing gangue as slag. | electricity, carbon | 6-7 | NeoSmelt (Kwinana); Primetals Smelter | assessed (NeoSmelt pilot study 2025-26; the furnace type is commercial in ferroalloys); ARENA NeoSmelt; CIMS |
|  | **Molten oxide electrolysis** | prospective | Electrolyses iron oxide above 1,500 °C, giving liquid iron and oxygen. | electricity | 5 | Boston Metal (demonstration cell) | iea_2024_001 row 402; Boston Metal |
|  | **Low-temperature iron electrowinning** | prospective | Dissolves ore in an aqueous electrolyte and plates out iron near ambient temperature. | electricity | 5 | Electra (demonstration plant, about 500 t/yr, 2026); Siderwin | iea_2024_001 row 408; Electra |
| `steelmaking` | **Basic oxygen furnace** | conventional | Blows oxygen through hot metal to burn out carbon; scrap is the coolant. | hot metal chemical energy, oxygen, scrap | 9 | — | commercial; etsap_2010_002; CIMS |
|  | **Basic oxygen furnace efficiency measures, strong** | efficient variant | Recovering the converter gas and its sensible heat instead of flaring it.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | oxygen, electricity; by-product gases | 9 | converter gas collection and use; sensible heat recovery on the off-gas hood | commercial; ukerc_2013_001; harmonized |
|  | **Basic oxygen furnace efficiency measures, moderate** | efficient variant | Drive and control measures on the converter and its gas-cleaning plant.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | oxygen, electricity; by-product gases | 9 | variable-speed drives on fan motors; improved gas cleaning; lining and ladle management | commercial; ukerc_2013_001; harmonized |
|  | **Electric arc furnace** | conventional | Melts scrap or DRI with graphite electrodes, with oxy-fuel burners and chemical energy. | electricity, oxygen, natural gas, charge carbon | 9 | Algoma (first EAF July 2025, second in 2026); ArcelorMittal Dofasco; Gerdau Whitby | commercial; ukerc_2013_001; Algoma 2025; CIMS |
|  | **High-efficiency EAF** | efficient variant | Ultra-high power with scrap preheating or continuous charging, cutting electricity and tap-to-tap time. | electricity, oxygen, natural gas | 9 | Consteel; Quantum; EcoArc | commercial; harmonized; CIMS |
|  | **Ladle metallurgy furnace** | conventional | Arc-heated ladle station for alloying, desulphurisation and temperature control. | electricity, argon | 9 | — | commercial; CIMS |
|  | **Ladle preheating** | conventional | Gas burners drying and preheating ladle refractory; oxy-fuel and electric units are the alternatives. | natural gas; oxygen; electricity | 9 | — | commercial; CIMS |
| `casting` | **Continuous casting** | conventional | Casts liquid steel into slabs, blooms or billets in a continuous strand. | electricity, water | 9 | — | commercial; CIMS |
|  | **Ingot casting** | conventional | Casts into ingots, reheated in soaking pits before rolling.<br>*Legacy route; CIMS keeps it for the remaining stock.* | natural gas, oil, electricity | 9 | — | commercial; CIMS |
|  | **Thin-slab casting with direct rolling** | efficient variant | Casts a thin slab and rolls it hot in line, cutting reheating and rolling passes. | natural gas, electricity | 9 | CSP; Arvedi ESP | commercial; CIMS |
|  | **Strip casting** | alternative | Casts near-net-shape strip directly from liquid steel.<br>*No Canadian stock.* | electricity | 9 | Castrip | commercial; CIMS |
| `reheating` | **Reheating furnace, fuel-fired** | conventional | Walking-beam or pusher furnace heating semis to about 1,200 °C before rolling. | natural gas, coke-oven and blast-furnace gas, oil; hydrogen | 9 | — | commercial; iea_2024_001 row 379; CIMS |
|  | **Reheating furnace efficiency measures, moderate** | efficient variant | Control and insulation measures on an existing reheating furnace.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, by-product gases | 9 | oxygen and air-flow control; increased insulation; scheduling and skid design | commercial; ukerc_2013_001; harmonized |
|  | **Reheating furnace efficiency measures, strong** | efficient variant | Combustion air preheated against the flue gas, taken to recuperation or regeneration.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column. Hot charging is the other measure the roster files as strong; it is its own row here because it depends on the caster and mill being coupled.* | natural gas, by-product gases; recovered heat | 9 | recuperative burners; regenerative burners; furnace sealing and insulation package | commercial; ukerc_2013_001; harmonized |
|  | **Hot charging and direct rolling** | efficient variant | Charges hot semis straight from casting, avoiding full reheating. | natural gas, electricity | 9 | — | commercial; CIMS |
|  | **Induction reheating** | alternative | Electric induction heaters in place of, or boosting, a fired reheating furnace. | electricity | 9 | — | iea_2024_001 row 372; CIMS |
| `rolling` | **Hot rolling mill** | conventional | Roughing and finishing stands, plus section, bar, rod and tube mills. | electricity | 9 | — | commercial; CIMS; ukerc_2013_001 |
|  | **Hot rolling mill efficiency measures, moderate** | efficient variant | Mill-side measures cutting rolling power and reheat losses.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | electricity; natural gas (reheat) | 9 | coil box; endless rolling; automatic gauge and flatness control; mill lubrication systems | commercial; ukerc_2013_001; harmonized |
|  | **Acid pickling line** | conventional | Removes scale in hydrochloric or sulphuric acid, with acid regeneration. | steam, electricity, acid | 9 | — | commercial; CIMS |
|  | **Cold rolling mill** | conventional | Tandem or reversing mill reducing strip thickness cold. | electricity | 9 | — | commercial; CIMS |
|  | **Coupled pickling and tandem cold mill** | efficient variant | Pickling line and tandem mill joined in one continuous line, avoiding re-coiling and re-heating. | electricity, steam, acid | 9 | — | commercial; harmonized |
| `annealing-and-coating` | **Batch (bell) annealing** | conventional | Coils annealed under a hood in a protective atmosphere over long cycles. | natural gas, oil | 9 | — | commercial; CIMS |
|  | **Hydrogen bell annealing** | efficient variant | 100% hydrogen atmosphere improves heat transfer and shortens the cycle. | natural gas or electricity (heating); hydrogen (atmosphere) | 9 | HICON/H2 | commercial; harmonized |
|  | **Continuous annealing line** | alternative | Strip annealed in line at high speed rather than in batches. | natural gas, electricity | 9 | — | commercial; CIMS |
|  | **Hot-dip galvanising line** | conventional | Strip heated and passed through a molten zinc bath. | natural gas, electricity; zinc | 9 | — | commercial; CIMS |
|  | **Electrolytic coating line** | conventional | Electro-galvanising and tin plating from solution. | electricity | 9 | — | commercial; CIMS |
|  | **Induction strip heating** | alternative | Induction heaters for annealing and galvanising lines in place of fired furnaces. | electricity | 9 | — | iea_2024_001 row 372 |
| `steel-oxygen-supply` | **Cryogenic air separation unit** | conventional | Distils liquefied air into oxygen, nitrogen and argon at large scale. | electricity | 9 | on-site ASUs at steelworks and smelters | commercial; CIMS |
|  | **Pressure or vacuum swing adsorption** | conventional | Adsorbent beds producing oxygen or nitrogen at smaller scale and lower purity. | electricity | 9 | — | commercial; harmonized |
|  | **Membrane separation** | conventional | Polymer membranes producing nitrogen or oxygen-enriched air. | electricity | 9 | — | commercial; harmonized |

<br>

---

### Cement

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Clinker production** `clinker-production` | Raw meal preparation and drying, preheater and precalciner, rotary kiln, clinker cooler. | *high-temp*<br>kiln 1400-1500; raw materials ~250, calciner ~900, kiln ~1400; calcining 1482 | Integral (kiln, precalciner and cooler) | `fans-and-blowers` (induced-draught, cooler and preheater fans)<br>`materials-handling` (raw meal and clinker) | coal, petroleum coke, natural gas, alternative fuels, electricity (raw mill, fans); process CO2 from calcination | Calciners 55.5 PJ at > 700 °C. Includes raw milling. | etsap_2010_003; rtc_2023_001 p.47; NREL97 SIC 3241; NREL118; nrcan_2025_001 |
| **Cement grinding and blending** `cement-grinding-and-blending` | Finish grinding, supplementary cementitious material preparation and blending, alternative binders. | — | — | `materials-processing` (finish mills)<br>`materials-handling` (clinker, additions and cement) | electricity | The clinker ratio is set here. | CIMS; harmonized |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `clinker-production` | **Dry rotary kiln with preheater and precalciner** | conventional | Multi-stage cyclone preheater and precalciner ahead of a short rotary kiln, with a grate cooler. | coal, petroleum coke, natural gas, waste-derived and biomass fuels; hydrogen firing (TRL 6) | 9 | — | commercial; iea_2024_001 row 330; etsap_2010_003; CIMS |
|  | **Cement kiln efficiency measures, moderate** | efficient variant | Combustion and sealing measures on an existing kiln line.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coal, petroleum coke, natural gas, waste fuels | 9 | burner and combustion control; reduced false air; kiln shell insulation | commercial; harmonized |
|  | **Cement kiln with post-combustion capture** | prospective | Amine or solid-sorbent capture on the kiln stack, taking the process and combustion CO2 together.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. The regeneration steam is large enough that the plant needs a heat source of its own, which is the host-side fact this row carries. Oxy-fuel and direct-separation kilns concentrate the stream instead and are their own rows.* | coal, petroleum coke, natural gas, waste fuels; steam and electricity for the capture plant | 7 | Heidelberg Brevik | iea_2024_001 row 332; row 333 gives 8 for partial capture below 50%; CIMS |
|  | **Cement kiln efficiency measures, strong** | efficient variant | The preheater, cooler and gas-path upgrades that together take a kiln line well below its current fuel use.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | coal, petroleum coke, natural gas, alternative fuels | 9 | extra preheater stages; high-efficiency grate cooler; low-pressure-drop gas path | commercial; harmonized |
|  | **Fluidised-bed kiln** | alternative | Sinters clinker in a fluidised bed rather than a rotating kiln, at lower temperature. | coal, natural gas | 6-7 | — | assessed (demonstration scale; modelled in CIMS); CIMS |
|  | **Oxy-fuel kiln** | prospective | Fires on oxygen and recycled flue gas, so the kiln gas is CO2-rich.<br>*Oxy-firing concentrates the kiln gas, so the capture plant is the one on cross-sector co2-capture-concentrated and is not repeated here; the air separation unit is the host-side cost.* | coal, natural gas, oxygen | 7 | — | iea_2024_001 row 338 |
|  | **Electrified or indirectly heated calciner** | prospective | Calcines the meal with electric heat or an indirectly heated vessel, separating process CO2 from flue gas. | electricity; natural gas (kiln burner) | 6 | LEILAC | iea_2024_001 rows 328, 335 |
| `cement-grinding-and-blending` | **Ball mill** | conventional | Tumbling mill grinding clinker and additions to cement fineness. | electricity | 9 | — | commercial; CIMS |
|  | **Vertical roller mill or high-pressure grinding rolls** | efficient variant | Bed comminution in place of impact grinding, at much lower specific power. | electricity | 9 | — | commercial; harmonized |
|  | **Blended cement with supplementary cementitious materials** | alternative | Replaces clinker with slag, fly ash or ground limestone. | electricity | 9 | — | commercial; harmonized |
|  | **Calcined clay cement (LC3)** | alternative | Clay calcined at about 800 °C replaces part of the clinker. | natural gas or electricity (clay calciner), electricity | 9 | — | iea_2024_001 rows 318, 324 |
|  | **Alkali-activated binder** | alternative | Geopolymer binder from slag or ash with an alkali activator, without clinker. | electricity; chemical activators | 9 | — | iea_2024_001 row 317 |
|  | **Carbonated binder** | prospective | Calcium silicate binder cured with CO2 rather than water. | electricity; CO2 | 8 | — | iea_2024_001 row 319 |

<br>

---

### Non-metallic minerals

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Lime and dolime calcination** `lime-calcination` | Lime and dolomitic lime kilns. | *high-temp*<br>calcining 1454 | Integral (kiln) | `fans-and-blowers` (combustion and cooling air) | natural gas, coal, petroleum coke; process CO2 | Lime calciners 10.7 PJ at > 700 °C. | NREL97 SIC 3274; nrcan_2025_001 |
| **Glass, ceramic and mineral wool melting and firing** `melting-and-firing` | Glass melting, refining, forming and annealing; brick, tile and refractory firing; mineral wool melting. | *high-temp*<br>glass melting 1538-1593, refining 816-1260, annealing 593-649; ceramic firing 1149; mineral wool melting 1593; mineral wool boilers 160 (steam) | Integral (glass and ceramic furnaces) | `fans-and-blowers` (combustion air) | natural gas, electricity (boosting, all-electric melters), oxygen | — | NREL97 SIC 3211, 3221, 3229, 3251, 3296 |
| **Drying and low-temperature calcining** `drying-and-low-temp-calcining` | Gypsum calcining to stucco, clay and brick drying, other mineral product drying. | *medium-temp*<br>gypsum calcining 171, drying 227; ceramic drying 316 | Integral (direct-fired dryers and calciners) | `fans-and-blowers` (dryer air) | natural gas | — | NREL97 SIC 3275, 3251 |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `lime-calcination` | **Rotary lime kiln with preheater** | conventional | Rotating kiln calcining limestone, with a preheater and product cooler. | natural gas, coal, petroleum coke, alternative fuels | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Lime kiln with post-combustion capture** | prospective | Capture on the lime kiln stack. Two thirds of the CO2 is process CO2 off the limestone, which no fuel switch can reach.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. A lime kiln has no waste heat to spare for regeneration, so the capture plant needs its own heat source - that is the host-side fact this row carries.* | natural gas, coal, petroleum coke, biomass; steam and electricity for the capture plant | 7 | — | iea_2024_001 row 332 |
|  | **Parallel-flow regenerative shaft kiln** | efficient variant | Two shafts alternate firing and preheating, cutting fuel use well below a rotary kiln. | natural gas, coal | 9 | — | commercial; harmonized |
|  | **Dolomitic lime kiln** | conventional | Calcines dolomite to dolomitic lime. | natural gas, coal | 9 | — | commercial; CIMS |
|  | **Oxy-fuel lime kiln** | prospective | Fires on oxygen and recycled gas so the kiln gas is CO2-rich.<br>*Oxy-firing concentrates the stream: capture sits on cross-sector co2-capture-concentrated.* | natural gas, oxygen | 7 | — | iea_2024_001 row 338 |
|  | **Electrified or indirectly heated calciner** | prospective | Electric or indirect heating separates process CO2 from combustion gas. | electricity | 6 | LEILAC | iea_2024_001 rows 328, 335 |
| `melting-and-firing` | **Air-fuel regenerative glass furnace** | conventional | Cross- or end-fired furnace with regenerators preheating combustion air. | natural gas, oil | 9 | — | commercial; NREL97 |
|  | **Oxy-fuel glass furnace** | efficient variant | Fires on oxygen, cutting flue-gas volume and fuel use. | natural gas, oxygen | 9 | — | commercial; harmonized |
|  | **Electric melter** | alternative | All-electric cold-top furnace melting the batch with immersed electrodes. | electricity | 9 | — | commercial; harmonized |
|  | **Hybrid furnace with electric boosting** | efficient variant | Fuel firing with electrode boosting, raising pull and cutting fuel per tonne. | natural gas, electricity | 9 | — | commercial; harmonized |
|  | **Hydrogen-fired furnace** | prospective | Burners fired on hydrogen for high-temperature melting or firing. | hydrogen | 8 | — | iea_2024_001 row 379 |
|  | **Tunnel or roller kiln** | conventional | Continuous kiln firing brick, tile and refractories. | natural gas | 9 | — | commercial; CIMS |
|  | **Electric kiln** | alternative | Resistance-heated kiln for ceramics and technical products. | electricity | 9 | — | commercial; harmonized |
| `drying-and-low-temp-calcining` | **Direct-fired rotary dryer or calciner** | conventional | Hot gas in direct contact with the mineral, for drying and gypsum calcining. | natural gas | 9 | — | commercial; CIMS; NREL97 |
|  | **Flash or fluid-bed calciner** | efficient variant | Short residence time in suspension or a fluidised bed, with better heat transfer. | natural gas | 9 | — | commercial; harmonized |
|  | **Kiln waste-heat drying** | efficient variant | Uses kiln or cooler exhaust to dry raw materials and additions. | recovered heat | 9 | — | commercial; harmonized |
|  | **Electric or heat-pump dryer** | alternative | Electric air heating, or a heat pump where the duty is below about 150 °C. | electricity | 7-9 | — | iea_2024_001 rows 436, 438 |

<br>

---

### Chemicals

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Steam cracking** `steam-cracking` | Olefin pyrolysis furnaces and cold-end separation. | *high-temp*<br>reactors 500-900; cracking 1538, preheating 649; stripping steam 54-116 | Integral (furnaces, and the cold-box refrigeration that is part of the process)<br>From `heat-low-temp` (separation) | `pumping` (reflux and quench) | ethane or naphtha feedstock; by-product fuel gas; natural gas; electricity (compressors, future e-cracker) | — | rtc_2023_001 p.55; NREL97 row 281331 |
| **Ammonia, methanol and hydrogen** `ammonia-and-methanol` | Reforming (SMR, ATR), shift and synthesis for ammonia and methanol, including the hydrogen made on the way. | *high-temp*<br>reforming 788-843; reformer process steam 816 (reactant) | Integral (reformer firebox, synthesis loop and its refrigeration)<br>From `heat-low-temp` (CO2 removal reboilers) | — | natural gas as feedstock and fuel; electricity (electrolytic hydrogen, compressors) | The reformer is the same technology as hydrogen-and-fuel-supply. | NREL97 SIC 2873, 2869, 2813 |
| **Chlor-alkali and sodium chlorate** `electrochemical-products` | Chlorine-caustic electrolysis, caustic evaporation, sodium chlorate cells. | *low-temp*<br>caustic evaporation 104-121 (steam) | From `heat-low-temp` (evaporators) | `pumping` (brine and electrolyte) | electricity (dominant), steam | Sodium chlorate supplies pulp bleaching. | NREL97 SIC 2812 |
| **Other chemicals** `other-chemicals` | Polymers, aromatics (BTX), organic intermediates, hydrogen peroxide, adipic and nitric acid, other bulk and fine chemicals: reactors, distillation, stripping, drying, extrusion. | *low-temp; medium-temp; high-temp*<br>drying ~150-200, distillation ~100-300, reactors ~500-900; polymer melting and extrusion 138-274 (steam); boiler steam 121-316 | From `heat-low-temp` (distillation, stripping and drying)<br>From `heat-medium-temp` (polymer processing)<br>Integral (some fired heaters) | — | natural gas, steam, electricity | Adipic and nitric acid are N2O process-emission sources. The largest steam user in chemicals: steam-served heat 80% < 150 °C, 17% at 150-400 °C. | rtc_2023_001 p.55; NREL97 SIC 2821, 28xx; NREL118; caelp_2024_001 p.36 |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `steam-cracking` | **Fired tubular steam cracker** | conventional | Hydrocarbon feed cracked in fired tubular coils, then quenched and separated. | ethane, propane, naphtha, gas oil feed; fuel gas, natural gas | 9 | — | iea_2024_001 row 355; CIMS |
|  | **Steam cracker with capture on the furnace flue gas** | prospective | Capture on the cracking furnace stacks, which are numerous and dilute.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. Oxy-fuel cracking (iea_2024_001 row 226, TRL 5) concentrates it instead.* | natural gas, by-product gases; steam and electricity for the capture plant | 3-4 | — | iea_2024_001 row 227; CIMS |
|  | **Electrified cracker furnace** | prospective | Electric heating of the cracking coils in place of burners. | electricity; hydrocarbon feed | 5 | BASF, SABIC and Linde demonstration at Ludwigshafen (4 t/h, 6 MW, 2024) | iea_2024_001 row 357; BASF e-cracker |
|  | **Rotodynamic cracking reactor** | prospective | Rotating machine heating the process gas directly with electricity. | electricity; hydrocarbon feed | 6 | Coolbrook RotoDynamic Reactor | iea_2024_001 row 375; Coolbrook 2024 |
|  | **Catalytic cracking of naphtha** | alternative | Catalysis lowers the cracking temperature against a thermal cracker. | naphtha; fuel gas | 9 | — | iea_2024_001 row 355 |
|  | **Bio-ethanol dehydration to ethylene** | alternative | Dehydrates ethanol to ethylene, bypassing cracking. | ethanol; steam | 9 | — | iea_2024_001 row 351 |
|  | **Methanol to olefins** | alternative | Converts methanol to ethylene and propylene over a zeolite catalyst. | methanol | 9 | — | assessed; harmonized |
| `ammonia-and-methanol` | **Steam reforming with Haber-Bosch synthesis** | conventional | Reformed natural gas feeds ammonia synthesis at pressure. | natural gas (feedstock and fuel), electricity | 9 | — | iea_2024_001 row 347; CIMS |
|  | **Ammonia plant with capture on the process CO2** | alternative | The CO2 removal step ahead of synthesis already delivers a pure stream; capture is dehydration and compression, and part of it is already sold for urea.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. This is the cheapest capture in the sector and should not be averaged with flue-gas capture. Full capture needs a second, dilute plant on the reformer flue gas.* | natural gas; electricity for compression | 9 | Enid, Oklahoma | iea_2024_001 row 347; row 346 gives 6 for full capture; CIMS |
|  | **Electrolytic-hydrogen Haber-Bosch** | prospective | Electrolysis replaces the reformer; synthesis is unchanged. | electricity, water, nitrogen | 8 | — | iea_2024_001 row 345 |
|  | **Autothermal reforming with full capture** | prospective | Oxygen-blown reforming designed for high capture rates.<br>*The oxygen-blown route gives one concentrated stream, held on cross-sector co2-capture-concentrated; there is no dilute flue gas to treat separately.* | natural gas, oxygen | 6 | — | iea_2024_001 row 346 |
|  | **Low-pressure Haber-Bosch** | prospective | Synthesis loop at lower pressure, better matched to variable electrolytic hydrogen. | electricity, hydrogen, nitrogen | 5 | — | iea_2024_001 row 348 |
|  | **Syngas methanol synthesis** | conventional | Reformed gas converted to methanol over a copper catalyst. | natural gas, electricity | 9 | — | iea_2024_001 row 362; CIMS |
|  | **CO2-to-methanol** | prospective | Hydrogenates captured CO2 to methanol, directly or through reverse water-gas shift. | hydrogen, CO2, electricity | 6-7 | — | iea_2024_001 rows 358, 359 |
|  | **Biomass or waste gasification to methanol** | prospective | Gasifies biomass or waste to syngas, then synthesises methanol. | biomass, waste, oxygen | 8 | — | iea_2024_001 row 360 |
| `electrochemical-products` | **Membrane chlor-alkali cell** | conventional | Ion-exchange membrane cell producing chlorine, caustic soda and hydrogen. | electricity, salt | 9 | — | commercial; CIMS |
|  | **Oxygen-depolarised cathode cell** | efficient variant | Feeds oxygen to the cathode, cutting cell voltage and power use, with no hydrogen co-product. | electricity, salt, oxygen | 8 | — | assessed; harmonized |
|  | **Sodium chlorate cell** | conventional | Electrolytic cell making sodium chlorate for pulp bleaching. | electricity, salt | 9 | — | commercial; CIMS |
|  | **Caustic evaporation with mechanical vapour recompression** | efficient variant | Recompresses vapour in place of multiple-effect steam evaporation. | electricity, steam | 9 | — | commercial; CIMS |
| `other-chemicals` | **Fired heater and distillation train** | conventional | Reboilers and fired heaters driving separation columns. | natural gas, refinery fuel gas, steam | 9 | — | commercial; CIMS |
|  | **Heat-integrated or divided-wall column** | efficient variant | Column internals and heat integration cutting reboiler duty against a conventional train. | steam, natural gas | 9 | — | commercial; harmonized |
|  | **Heat-pumped distillation** | alternative | Vapour recompression or a closed-cycle heat pump replaces the reboiler steam. | electricity | 9 | — | commercial; harmonized |
|  | **Polymerisation reactor and extrusion** | conventional | Reactor trains and extruders making polymers and compounds. | electricity, steam, cooling | 9 | — | commercial; CIMS |
|  | **Catalytic N2O abatement** | efficient variant | Secondary or tertiary catalyst destroying N2O in nitric and adipic acid plants.<br>*Abates process emissions rather than energy.* | electricity | 9 | — | commercial; CIMS |
|  | **Plastics pyrolysis recycling** | alternative | Pyrolyses mixed plastic waste to a cracker feedstock. | natural gas, electricity; plastic waste | 9 | — | iea_2024_001 row 363 |
|  | **Chemical depolymerisation** | prospective | Depolymerises PET or polystyrene back to monomer. | steam, electricity; solvents | 8-9 | — | iea_2024_001 rows 364, 365 |

<br>

---

### Biofuels

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Ethanol production** `ethanol-production` | Grain (corn, wheat) dry milling, liquefaction and cooking, fermentation, distillation and dehydration, stillage evaporation, distillers-grain drying; cellulosic ethanol. | *low-temp; high-temp*<br>steam-served heat p10/p50/p90 88/119/135; direct heat 788-871 (NREL-assigned from SIC 2869, not ethanol-specific) | From `heat-low-temp` (cooking, distillation and evaporation)<br>Integral (grain dryers) | `pumping` (mash and beer) | natural gas, electricity, biomass; grain or cellulosic feedstock | Canada: about 1,900 million L/yr ethanol capacity. US: ethyl alcohol is 10% of chemical-sector energy (307 TBtu). Fermentation CO2 goes to co2-capture-concentrated. CIMS Ethanol.Agricultural Input is out of scope. All steam-served heat is below 150 °C. | NREL118 NAICS 325193; CER bioenergy overview; DOE 2015 chemicals bandwidth study |
| **Biodiesel production** `biodiesel-production` | Oil and fat pretreatment, transesterification, methanol recovery, glycerin refining, biodiesel distillation. | *low-temp*<br>steam p50 119 (NAICS 325199 value, not biodiesel-specific) | From `heat-low-temp` (transesterification and methanol recovery) | — | natural gas, electricity, methanol; vegetable oil, tallow or used cooking oil feedstock | Canada: about 700 million L/yr biodiesel capacity. | NREL118; CER bioenergy overview |
| **Renewable diesel and SAF** `renewable-diesel-and-saf` | Dedicated hydrotreating (HEFA/HVO) units, including converted refineries, that make renewable diesel and sustainable aviation fuel from vegetable oils, tallow and used cooking oil: feed pretreatment, hydrodeoxygenation, isomerisation, fractionation. | *medium-temp; high-temp*<br>as refinery hydroprocessing, reactors ~260-480; not specific to renewable diesel | From `heat-medium-temp` (fired heaters)<br>From `heat-high-temp` (fired heaters) | `centralised-hydrogen-production` (hydrotreating hydrogen) | hydrogen (large), natural gas, electricity; lipid feedstock | Canada produced about 687 million L of renewable diesel in 2024; planned capacity could triple. Co-processing in existing refinery hydrotreaters stays in refining. | rtc_2023_001 p.97; CER bioenergy overview |
| **Renewable natural gas** `renewable-natural-gas` | Biogas raised from anaerobic digestion or landfill and upgraded to pipeline specification, and biomass gasification to methane. | *not-applicable*<br>digesters held at 35-55 | From `heat-low-temp` (digester heating) | `compressed-air` (upgrading and injection compression) | biomass, manure, municipal and landfill waste; electricity, low-temperature heat | Moved out of the cross-sector hydrogen-and-fuel-supply end use (2026-09-14): RNG is produced for sale into the gas system, which makes it a biofuels product rather than a site service. |  |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `ethanol-production` | **Grain dry-mill fermentation and distillation** | conventional | Mills, cooks and ferments starch, then distils and dehydrates the beer and dries the stillage. | natural gas (steam and dryers), electricity; corn or wheat | 9 | — | iea_2024_001 row 499; CIMS |
|  | **Fermentation CO2 capture and compression** | alternative | Fermentation off-gas is about 99% CO2, so capture is dehydration and compression.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. Biogenic, so it is a removal. The distillation and drying heat is unchanged and still comes from the heat bands.* | electricity for compression | 9 | ADM Decatur, Illinois | iea_2024_001 row 498; CIMS |
|  | **Distillation with mechanical vapour recompression** | efficient variant | Recompresses overhead vapour to drive the reboiler, cutting steam use. | electricity | 9 | — | commercial; harmonized |
|  | **Molecular-sieve dehydration with heat integration** | efficient variant | Pressure-swing sieves plus heat integration replace azeotropic distillation. | steam, electricity | 9 | — | commercial; harmonized |
|  | **Lignocellulosic enzymatic fermentation** | alternative | Pretreats and enzymatically hydrolyses biomass before fermentation. | biomass residues; steam, electricity | 9 | — | iea_2024_001 row 497; CIMS |
|  | **Syngas fermentation** | prospective | Microbes convert gasified biomass or waste gas to ethanol. | biomass, waste or industrial off-gas | 8 | LanzaTech | iea_2024_001 row 500 |
|  | **Distillers-grain drying with heat recovery or heat pumps** | efficient variant | Recovers dryer exhaust heat, or uses a heat pump, on the largest gas load in the plant. | natural gas, electricity, recovered heat | 7-9 | — | iea_2024_001 rows 390, 436 |
| `biodiesel-production` | **Alkali-catalysed transesterification** | conventional | Reacts oils or fats with methanol over a homogeneous catalyst to fatty acid methyl esters. | vegetable oil, tallow or used cooking oil; methanol; steam, electricity | 9 | — | iea_2024_001 row 495; CIMS |
|  | **Heterogeneous-catalyst transesterification** | alternative | Solid catalyst avoids the washing and neutralisation steps and gives cleaner glycerin. | oils and fats; methanol; steam, electricity | 8 | Axens Esterfip-H | assessed; harmonized |
|  | **Methanol recovery with heat integration** | efficient variant | Recovers and recycles methanol with column heat integration or vapour recompression. | steam, electricity | 9 | — | commercial; harmonized |
| `renewable-diesel-and-saf` | **Hydrotreating of oils and fats (HEFA/HVO)** | conventional | Hydrodeoxygenates and isomerises lipids to diesel and jet range fuels. | hydrogen, natural gas, electricity; vegetable oil, tallow, used cooking oil | 9 | — | iea_2024_001 row 491 |
|  | **Alcohol-to-jet** | prospective | Dehydrates and oligomerises ethanol or isobutanol to jet fuel. | ethanol or isobutanol; hydrogen | 7-8 | — | iea_2024_001 row 483 |
|  | **Gasification with Fischer-Tropsch synthesis** | prospective | Gasifies biomass or waste and synthesises liquid hydrocarbons. | biomass, waste, oxygen; hydrogen | 7 | — | iea_2024_001 row 486 |
|  | **Pyrolysis oil upgrading** | prospective | Fast pyrolysis of biomass then hydroprocessing of the oil. | biomass; hydrogen | 7 | — | iea_2024_001 row 492 |
|  | **Hydrothermal liquefaction** | prospective | Converts wet biomass to bio-crude in hot pressurised water, then upgrades it. | wet biomass; hydrogen | 5 | — | iea_2024_001 row 487 |
|  | **Methanol-to-jet** | prospective | Converts methanol, including e-methanol, to jet fuel. | methanol; hydrogen | 5 | — | iea_2024_001 row 298 |
| `renewable-natural-gas` | **Anaerobic digestion with upgrading** | alternative | Digests organic feed to biogas and upgrades it to pipeline-quality gas. | organic waste, manure | 9 | RNG plants on landfills and digesters | iea_2024_001 row 477 |
|  | **Landfill gas recovery and upgrading** | conventional | Collects landfill gas and upgrades it to pipeline specification. | landfill gas; electricity (compression) | 9 | — | iea_2024_001 row 477 |
|  | **Biomass gasification with methanation** | prospective | Gasifies solid biomass and methanates the syngas to pipeline-quality gas. | biomass, waste; electricity | 5 | — | iea_2024_001 row 482; CIMS |

<br>

---

### Hydrogen (centralised production and distribution)

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Centralised hydrogen production** `centralised-hydrogen-production` | Merchant hydrogen produced for sale rather than for an on-site process: steam methane and autothermal reformers with and without capture, gasification, and grid- or dedicated-renewable electrolysis at plant scale. | *not-applicable*<br>reforming 788-843; steam is a reactant | Integral (reformer firebox) | `compressed-air` (product compression) | natural gas, coal, petroleum coke, biomass, electricity | Merchant production for sale. CIMS carries a Hydrogen sector whose production service maps here. Drawn on by 1 end use: `renewable-diesel-and-saf`. |  |
| **Hydrogen distribution** `hydrogen-distribution` | Compression, pipeline transmission and distribution of hydrogen to industrial users, including booster compression, and liquefaction and trucking where there is no pipeline. | *not-applicable*<br>— | — (the compression is the process) | — | electricity (compression, liquefaction) | New sector, 2026-09-14. Distribution energy is a real cost of centralised supply and is what distinguishes it from production at the point of use. |  |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `centralised-hydrogen-production` | **Steam methane reformer** | conventional | Reforms natural gas with steam, then shifts to hydrogen and CO2. | natural gas, refinery fuel gas | 9 | refinery and ammonia hydrogen plants | iea_2024_001 row 285; CIMS |
|  | **Steam methane reformer with capture on the shift gas** | alternative | Capture on the shifted syngas, where the CO2 is already at high partial pressure. Taking the reformer flue gas as well needs a second, dilute-stream plant.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. Partial capture takes only the shift gas and reaches about 60% of the plant total; full capture adds a diffuse-stream plant on the reformer flue gas.* | natural gas; steam and electricity for the capture plant | 9 | Quest, Alberta | iea_2024_001 row 285; row 284 gives 6 for high capture rates; CIMS |
|  | **Autothermal reformer** | prospective | Partial oxidation with oxygen in one vessel; suits high capture rates.<br>*Commercial for syngas; the IEA TRL is for the CCUS-enabled hydrogen configuration.* | natural gas, oxygen | 5 | Air Products Alberta net-zero hydrogen complex (Edmonton) | iea_2024_001 row 276 |
|  | **Water electrolysis, low temperature** | alternative | Alkaline or PEM stacks splitting water with electricity. | electricity, water | 9 | — | iea_2024_001 rows 261, 263 |
|  | **Solid-oxide electrolysis** | prospective | High-temperature steam electrolysis with higher electrical efficiency. | electricity, steam | 8 | — | iea_2024_001 row 264 |
|  | **Methane pyrolysis** | prospective | Splits methane into hydrogen and solid carbon, with no CO2 to capture. | natural gas, electricity | 7-8 | Monolith; Hazer | iea_2024_001 rows 287, 290 |
|  | **Biomass or waste gasification** | prospective | Gasifies biomass or waste to syngas for fuels or hydrogen. | biomass, waste, oxygen | 6 | Enerkem (Varennes) | iea_2024_001 row 274 |
|  | **Gasification with capture on the shift gas** | prospective | Gasifier with a shift reactor and physical-solvent capture, giving one concentrated stream; biomass or waste feed makes it a removal.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated.* | biomass, waste, coal, petroleum coke; electricity and steam for the capture plant | 5 | — | iea_2024_001 row 277; row 280 gives 9 for coal gasification at partial capture rates; CIMS |
| `hydrogen-distribution` | **Pipeline compression and transmission** | conventional | Compressors moving hydrogen through a dedicated pipeline to industrial users. | electricity; natural gas (gas-driven compressors) | 9 | — | commercial |
|  | **Hydrogen liquefaction and road transport** | alternative | Liquefies hydrogen for trucking where there is no pipeline; liquefaction takes about a third of the hydrogen's energy. | electricity | 9 | — | commercial |
|  | **Blending into the natural gas network** | prospective | Injects hydrogen into the existing gas system at a limited volume share, delivering it to users as a blended fuel. | electricity (compression) | 8 | — | assessed; blending trials at 5-20% by volume; CIMS |

<br>

---

### Petroleum refining

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Crude distillation** `crude-distillation` | Desalting, atmospheric and vacuum distillation. | *medium-temp*<br>distillation ~150-370; stripping and ejector steam | From `heat-medium-temp` (crude and vacuum heaters, stripping steam) | `pumping` (crude charge and reflux)<br>`fans-and-blowers` (air coolers) | refinery fuel gas, natural gas, steam, electricity | Refinery steam-served heat: 32% < 150 °C, 68% at 150-400 °C (49% at 200-250 °C). | rtc_2023_001 p.97; NREL118; nrcan_2025_001 |
| **Conversion, upgrading and treating** `conversion-and-treating` | FCC, hydrocracking, coking, catalytic reforming, alkylation, isomerisation, asphalt and lubes, hydrotreating and sulphur recovery. Co-processing bio-feedstock in an existing hydrotreater stays here as a feedstock choice; dedicated renewable diesel and SAF units are in biofuels. | *medium-temp; high-temp*<br>reactors ~260-480; refinery furnaces 200-700 | From `heat-medium-temp` (process heaters)<br>From `heat-high-temp` (process heaters)<br>Integral (FCC regenerator) | `refinery-hydrogen` (hydrotreating and hydrocracking) | refinery fuel gas, natural gas, petroleum coke (FCC coke), hydrogen, electricity | FCC catalyst regeneration burns 50.8 PJ of petroleum coke as captive combustion. | rtc_2023_001 p.97; nrcan_2025_001 |
| **On-site hydrogen production** `refinery-hydrogen` | Hydrogen made at the refinery for hydrotreating and hydrocracking: steam methane and autothermal reformers with and without capture, petroleum-coke gasification, and electrolysis. | *not-applicable*<br>reforming 788-843; steam is a reactant | Integral (reformer firebox) | `compressed-air` (make-up and recycle compression) | natural gas, refinery fuel gas, petroleum coke, electricity | Refinery methane reformers: 37.6 PJ, booked as a non-energetic input. Excludes reformers integral to ammonia and methanol plants and to DRI, which stay with those end uses. Drawn on by 1 end use: `conversion-and-treating`. | nrcan_2025_001 |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `crude-distillation` | **Atmospheric and vacuum distillation with fired heaters** | conventional | Crude heated in fired heaters and fractionated at atmospheric pressure, then under vacuum. | refinery fuel gas, natural gas, steam, electricity | 9 | — | commercial; CIMS; rtc_2023_001 p.97 |
|  | **Advanced heat integration** | efficient variant | Pinch-designed preheat train and better fouling control, cutting furnace duty. | refinery fuel gas, natural gas | 9 | — | commercial; harmonized |
|  | **Progressive or divided-wall distillation** | efficient variant | Splits the separation across columns or one shell to cut reboiler and furnace duty. | refinery fuel gas, steam | 8 | — | assessed; harmonized |
|  | **Electrified crude heater** | prospective | Electric resistance or rotodynamic heating replaces the fired crude heater. | electricity | 6 | Coolbrook RotoDynamic Heater | iea_2024_001 row 375; CIMS |
| `conversion-and-treating` | **Fluid catalytic cracking** | conventional | Cracks gas oil over a circulating catalyst; coke burnt off in the regenerator supplies the heat. | coke on catalyst (captive), refinery fuel gas, steam, electricity | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **FCC regenerator with post-combustion capture** | prospective | Capture on the catalytic cracker regenerator flue gas, the largest single stack in a refinery.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. Oxy-fuel regeneration is its own row and gives a concentrated stream.* | coke burnt off the catalyst; steam and electricity for the capture plant | 3-4 | — | iea_2024_001 row 227; CIMS |
|  | **Hydroprocessing (hydrocracking and hydrotreating)** | conventional | Hydrogen-driven cracking and sulphur or nitrogen removal at pressure. | hydrogen, refinery fuel gas, natural gas, electricity | 9 | — | commercial; CIMS |
|  | **Delayed coking** | conventional | Thermally cracks residue to lighter products and petroleum coke. | refinery fuel gas, steam | 9 | — | commercial; CIMS |
|  | **Catalytic reforming** | conventional | Upgrades naphtha to high-octane reformate, producing hydrogen. | refinery fuel gas, electricity | 9 | — | commercial; CIMS |
|  | **Alkylation and isomerisation** | conventional | Combines or rearranges light ends into high-octane blendstock. | refinery fuel gas, steam, electricity; acid catalyst | 9 | — | commercial; CIMS |
|  | **Sulphur recovery and acid gas removal** | conventional | Amine treating plus a Claus unit and tail-gas treatment. | steam, electricity | 9 | — | commercial; CIMS |
|  | **Advanced acid gas removal** | efficient variant | Selective solvents or membranes cutting regeneration energy. | steam, electricity | 9 | — | iea_2024_001 row 225 |
|  | **Oxy-fuel FCC regeneration** | prospective | Burns catalyst coke in oxygen so the regenerator flue gas is CO2-rich.<br>*Oxy-firing the regenerator concentrates the stream: capture sits on cross-sector co2-capture-concentrated.* | oxygen, refinery fuel gas | 5 | — | iea_2024_001 row 226 |
| `refinery-hydrogen` | **Steam methane reformer** | conventional | Reforms natural gas with steam, then shifts to hydrogen and CO2. | natural gas, refinery fuel gas | 9 | refinery and ammonia hydrogen plants | iea_2024_001 row 285; CIMS |
|  | **Reformer efficiency measures, moderate** | efficient variant | Heat integration and feed conditioning on an existing reformer.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas; recovered heat | 9 | pre-reforming; convection-section heat recovery; combustion-air preheat; hydrogen recovery from purge gas | commercial; harmonized |
|  | **Steam methane reformer with capture on the shift gas** | alternative | Capture on the shifted syngas, where the CO2 is already at high partial pressure. Taking the reformer flue gas as well needs a second, dilute-stream plant.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. Partial capture takes only the shift gas and reaches about 60% of the plant total; full capture adds a diffuse-stream plant on the reformer flue gas.* | natural gas; steam and electricity for the capture plant | 9 | Quest, Alberta | iea_2024_001 row 285; row 284 gives 6 for high capture rates; CIMS |
|  | **Autothermal reformer** | prospective | Partial oxidation with oxygen in one vessel; suits high capture rates.<br>*Commercial for syngas; the IEA TRL is for the CCUS-enabled hydrogen configuration.* | natural gas, oxygen | 5 | Air Products Alberta net-zero hydrogen complex (Edmonton) | iea_2024_001 row 276 |
|  | **Coal or petroleum-coke gasification** | conventional | Partial oxidation of solid feed to syngas, then shift. | coal, petroleum coke, oxygen | 9 | — | iea_2024_001 row 280; CIMS |
|  | **Water electrolysis, low temperature** | alternative | Alkaline or PEM stacks splitting water with electricity. | electricity, water | 9 | — | iea_2024_001 rows 261, 263 |

<br>

---

### Pulp and paper

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Chemical pulping and bleaching** `chemical-pulping` | Debarking and chipping, kraft and semi-chemical digesting, washing, oxygen delignification and bleaching. | *medium-temp; low-temp*<br>digesting 171 (steam); chemical preparation 60-200, bleaching 60-150 | From `heat-medium-temp` (digester)<br>From `heat-low-temp` (washing and bleaching) | `pumping` (stock and liquor) | steam, electricity, bleaching chemicals | — | NREL97 SIC 2611; rtc_2023_001 p.88 |
| **Mechanical and recycled pulping** `mechanical-and-recycled-pulping` | Thermomechanical and groundwood refining, recycled-fibre repulping and deinking. | *low-temp*<br>recycled pulping 60 (steam) | From `heat-low-temp` (repulping and deinking) | `materials-processing` (refiners) | electricity (refiners, dominant), steam | Electricity-intensive. | NREL97 SIC 2621, 2631 |
| **Black liquor evaporation and recovery** `chemical-recovery` | Multiple-effect evaporators and the recovery furnace. | *low-temp*<br>evaporating 66-110 (steam) | Integral (recovery furnace)<br>From `heat-low-temp` (evaporators) | `fans-and-blowers` (combustion air and precipitator) | black liquor; steam | The recovery furnace is itself a large steam source, credited to the heat end uses; its steam conditions are not in held sources. | NREL97 SIC 2611, 2621; etsap_2015_001 |
| **Lime kiln** `lime-kiln` | Recausticising lime kiln. | *high-temp*<br>re-causticizing 800-1200; > 700; calcining 649 | Integral (kiln) | `fans-and-blowers` (combustion air) | natural gas, oil; biomass gasification, tall oil and pitch as alternatives | 22.6 PJ natural gas and oil at > 700 °C, the mill's main direct fossil heat. | rtc_2023_001 p.88; nrcan_2025_001; NREL97 SIC 2611 |
| **Stock preparation, forming and pressing** `paper-forming` | Stock preparation and refining, headbox and wire, press section, and sheet finishing for all grades. | *low-temp*<br>stock heating 60-150 | From `heat-low-temp` (stock heating) | `pumping` (stock and white water)<br>`compressed-air` (showers and doctoring) | electricity (refiners, vacuum pumps, drives), steam | Electricity-dominated; the dryer section is a separate end use. | rtc_2023_001 p.88; CIMS |
| **Paper and pulp drying** `paper-drying` | Dryer section (steam cans, hoods, infrared), coating dryers and market-pulp drying. | *low-temp; medium-temp*<br>drying 70-150; steam dryer cans 38-116; direct-fired dryers 200-700 | From `heat-low-temp` (steam dryer cans)<br>Integral (gas-fired dryers and hoods) | `fans-and-blowers` (hood supply and exhaust) | steam, natural gas (hoods, IR, air dryers), electricity | Dryers 7.5 PJ at 200-700 °C. CIMS paper grades stay as process steps. Pulp and paper steam-served heat: 81% < 150 °C, 19% at 150-400 °C. | rtc_2023_001 p.88; NREL97 SIC 26xx; nrcan_2025_001; NREL118 |
| **Effluent treatment** `effluent-treatment` | Primary clarification, biological treatment and sludge handling on mill effluent: aeration basins, activated sludge, anaerobic reactors, clarifiers, presses and dryers. | *low-temp*<br>anaerobic reactors 35-55 | From `heat-low-temp` (anaerobic reactor heating) | `fans-and-blowers` (aeration blowers)<br>`pumping` (effluent and sludge) | electricity (aeration blowers, pumps, presses); low-temperature heat (anaerobic reactors); biogas recovered | Added 2026-09-15. Aeration is one of the largest single electricity loads in a kraft mill after the refiners and the paper machine, and anaerobic treatment turns part of the load into recovered biogas, so it is a real technology choice rather than generic pumping. |  |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `chemical-pulping` | **Continuous kraft digester** | conventional | Continuous vessel cooking chips in white liquor, with heat recovery from the flash steam. | steam, electricity; white liquor | 9 | — | commercial; CIMS; NREL97 |
|  | **Batch kraft digester with displacement heating** | efficient variant | Batch cooking with hot-liquor displacement recovering most of the cooking heat. | steam, electricity | 9 | — | commercial; harmonized |
|  | **Semi-chemical and sulphite pulping** | conventional | Milder chemical cooking for corrugating medium and specialty pulps. | steam, electricity; chemicals | 9 | — | commercial; CIMS |
|  | **Oxygen delignification with ECF bleaching** | efficient variant | Removes lignin with oxygen before bleaching, cutting chemical and steam use. | oxygen, steam, electricity; chlorine dioxide | 9 | — | commercial; CIMS |
| `mechanical-and-recycled-pulping` | **Thermomechanical pulping refiners** | conventional | Steam-pressurised disc refiners fibrillating chips; refiner heat is recovered as steam. | electricity; recovered steam | 9 | — | commercial; CIMS |
|  | **Low-energy refining** | efficient variant | Advanced segments, RTS conditions or pre-treatment cutting refiner electricity. | electricity | 9 | — | commercial; harmonized |
|  | **Chemi-thermomechanical pulping** | alternative | Mild chemical pre-treatment before refining, at lower electricity per tonne. | electricity, steam; chemicals | 9 | — | commercial; harmonized |
|  | **Recycled-fibre repulping and deinking** | conventional | Pulpers, screens and flotation cells recovering fibre from recovered paper. | electricity, steam, chemicals | 9 | — | commercial; CIMS |
| `chemical-recovery` | **Recovery boiler** | conventional | Burns concentrated black liquor, recovering smelt and raising high-pressure steam. | black liquor | 9 | — | commercial; CIMS; etsap_2015_001 |
|  | **Recovery boiler with post-combustion capture** | prospective | Capture on the recovery boiler stack. The CO2 is biogenic, so this is a removal rather than an avoided emission.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. The mill steam balance is what binds, and that is the host-side fact this row carries.* | black liquor; steam and electricity for the capture plant | 5 | — | iea_2024_001 row 422; row 501 gives 6 for post-combustion capture on biomass combustion; CIMS |
|  | **High-solids firing and high-pressure recovery boiler** | efficient variant | Higher liquor dry solids and steam conditions, raising power and steam yield. | black liquor | 9 | — | commercial; harmonized |
|  | **Multiple-effect evaporators** | conventional | Concentrates weak black liquor in a train of effects on live steam. | steam, electricity | 9 | — | commercial; CIMS; NREL97 |
|  | **Mechanical vapour recompression evaporation** | efficient variant | Recompresses vapour to drive the evaporator, replacing most live steam with electricity. | electricity | 9 | — | commercial; harmonized |
|  | **Black liquor gasification** | alternative | Gasifies liquor to syngas for fuels, chemicals or a gas turbine, in place of a recovery boiler. | black liquor, oxygen | 9 | — | iea_2024_001 row 432 |
|  | **Lignin extraction** | alternative | Precipitates lignin from the liquor as a fuel or chemical feedstock, debottlenecking the boiler. | CO2, acid, electricity | 9 | LignoBoost | iea_2024_001 row 434 |
| `lime-kiln` | **Rotary lime kiln** | conventional | Calcines lime mud back to lime for causticising. | natural gas, oil; tall oil and pitch | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Lime kiln with post-combustion capture** | prospective | Capture on the kraft mill lime kiln stack; the calcination CO2 comes back round the causticising loop, so most of it is biogenic.<br>*Dilute stream, held once on cross-sector co2-capture-diffuse. Small beside the recovery boiler, but on the same steam balance.* | natural gas, oil, biomass; steam and electricity for the capture plant | 7 | — | iea_2024_001 row 332 |
|  | **Lime kiln with product cooler and improved drying** | efficient variant | Better cooler, chain section and mud drying, cutting fuel per tonne of lime. | natural gas, oil | 9 | — | commercial; harmonized |
|  | **Biomass-gasifier-fired lime kiln** | alternative | On-site gasifier supplies producer gas to the kiln burner in place of fossil fuel. | biomass (bark, residues) | 8 | — | assessed; harmonized |
|  | **Electrified lime kiln** | prospective | Plasma or electric heating of the calcination zone. | electricity | 5-6 | — | iea_2024_001 rows 328, 409 |
| `paper-forming` | **Fourdrinier or gap former with press section** | conventional | Headbox, wire and press section dewatering the sheet mechanically. | electricity (drives, vacuum), steam | 9 | — | commercial; CIMS |
|  | **Shoe (extended-nip) press** | efficient variant | Longer nip raises sheet dryness into the dryer section, cutting drying steam. | electricity | 9 | — | commercial; harmonized |
|  | **Advanced mechanical dewatering** | prospective | Impulse or pressurised dewatering removing more water before the dryers. | electricity, steam | 5 | — | iea_2024_001 row 425 |
| `paper-drying` | **Steam-heated cylinder dryer section** | conventional | Steam-filled cans drying the web, with condensate return. | steam | 9 | — | commercial; CIMS; NREL97 |
|  | **High-efficiency hood with heat recovery** | efficient variant | Closed hood and air system recovering exhaust heat to the machine and mill. | steam, electricity, recovered heat | 9 | — | commercial; harmonized |
|  | **Gas-fired hood, infrared or air dryer** | conventional | Direct-fired Yankee hoods, infrared and air dryers on tissue and coating. | natural gas | 9 | — | commercial; nrcan_2025_001 |
|  | **Electric air heating** | alternative | Electric heaters replace the gas burner on hoods and air dryers. | electricity | 9 | — | iea_2024_001 row 436 |
|  | **Heat-pump drying** | prospective | Heat pump upgrades dryer exhaust heat back into the drying air. | electricity, recovered heat | 7 | — | iea_2024_001 row 438 |
| `effluent-treatment` | **Activated sludge aeration** | conventional | Surface aerators or coarse-bubble diffusers holding an aeration basin at the oxygen demand of the effluent. | electricity | 9 | — | commercial |
|  | **Fine-bubble diffused aeration** | efficient variant | Fine-bubble diffusers with blower control on dissolved oxygen, at a fraction of the power of surface aeration. | electricity | 9 | dissolved-oxygen trim; turbo blowers | commercial; harmonized |
|  | **Anaerobic treatment with biogas recovery** | alternative | Anaerobic reactors on high-strength streams, cutting aeration load and recovering biogas as fuel.<br>*Turns part of the treatment load into a fuel, which is why it is a technology choice rather than generic pumping.* | low-temperature heat (reactor); electricity; biogas recovered | 9 | UASB and IC reactors | commercial; harmonized |
|  | **Clarification and sludge dewatering** | conventional | Primary clarifiers with belt or screw presses, and dryers where the sludge is burnt. | electricity; low-temperature heat (sludge drying) | 9 | — | commercial; harmonized |

<br>

---

### Mining (including coal mining)

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Extraction and haulage** `extraction-and-haulage` | Drilling, blasting, loading, hauling and hoisting in open-pit and underground metal, coal and potash mines; solution-mining extraction. | — | — | — | diesel (haul trucks, loaders, drills), electricity (hoists, trolley assist, battery equipment) | Diesel in mining equipment, trucks and trains: iron ore 7.6 PJ, gold and silver 17.1 PJ. | nrcan_2025_001; CIMS |
| **Crushing and grinding** `comminution` | Primary and secondary crushing, milling and grinding, crush-and-screen. | — | — | `materials-processing` (mill drives)<br>`materials-handling` (feed conveying)<br>`pumping` (mill and cyclone slurry) | electricity | The largest electricity use in metal mining. | CIMS |
| **Mineral separation and processing** `separation-and-processing` | Flotation and other separation, cleaning and washing, potash dissolution and crystallisation, compaction, tailings disposal. | *low-temp*<br>potash processing steam; temperature not in held sources | From `heat-low-temp` (potash crystallisation and dissolution) | `pumping` (slurry and tailings)<br>`fans-and-blowers` (flotation blowers) | electricity (pumps, flotation cells), steam, natural gas | — | CIMS |
| **Concentrate and product drying** `product-drying` | Potash, concentrate and coal drying. | *medium-temp (unconfirmed)*<br>not in held sources | Integral (direct-fired dryers) | `fans-and-blowers` (dryer air) | natural gas | Tier unconfirmed. | CIMS |
| **Iron ore pelletising** `pelletising` | Pellet induration at the mine. | *high-temp*<br>pelletizing 1316; 1000-1200 | Integral (induration furnace) | `fans-and-blowers` (induration and cooler fans) | heavy oil, natural gas; coke and coal as additives; electricity | 23.4 PJ in pelletizing furnaces (13.7 PJ oil at > 700 °C). Same technologies as iron-and-steel agglomeration. Iron-ore sites run small boilers below 200 °C. | NREL97 SIC 3312; rtc_2023_001 p.75; nrcan_2025_001 |
| **Mine ventilation and air heating** `ventilation-and-air-heating` | Underground ventilation fans, mine air heating (and cooling in deep mines). | *low-temp*<br>mine air heating, near ambient; no held source gives a figure | Integral (direct-fired mine air heaters) | — | electricity (fans), natural gas and propane (air heaters) | Gold and silver mine space heating 3.8 PJ below 200 °C. | nrcan_2025_001; CIMS |
| **Water and tailings management** `water-and-tailings-management` | Mine dewatering, water treatment before discharge or reuse, process-water reclaim, and tailings transport, thickening and storage. | *not-applicable*<br>— | — | `pumping` (dewatering, reclaim and tailings)<br>`fans-and-blowers` (aeration) | electricity (dewatering and reclaim pumps, thickeners, treatment plant); natural gas (evaporative concentration) | Added 2026-09-15. Separated from comminution and separation because the driver is the site water balance and the discharge permit, not the ore throughput, and because dewatering pumping runs whether or not the mill does. |  |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `extraction-and-haulage` | **Diesel haul truck fleet** | conventional | Diesel trucks, loaders and drills moving ore and waste. | diesel, renewable diesel | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Battery-electric haulage** | prospective | Battery trucks and loaders with fast charging or battery swap. | electricity | 8 | — | iea_2024_001 row 135 |
|  | **Trolley-assist haulage** | alternative | Overhead catenary powers trucks on the ramp, cutting diesel on the loaded climb. | electricity, diesel | 9 | — | assessed; harmonized |
|  | **In-pit crushing and conveying** | efficient variant | Crushes at the face and conveys ore out, replacing truck haulage. | electricity | 9 | — | commercial; CIMS |
|  | **Hydrogen fuel-cell haulage** | prospective | Fuel-cell trucks in demonstration at mine scale. | hydrogen | 6 | — | assessed; harmonized |
|  | **Underground battery-electric equipment** | alternative | Battery LHDs, trucks and drills, which also cut ventilation demand. | electricity | 9 | — | iea_2024_001 row 135 |
|  | **Shaft hoisting** | conventional | Hoists lifting ore from depth in place of ramp haulage. | electricity | 9 | — | commercial; harmonized |
| `comminution` | **SAG and ball mill circuit** | conventional | Semi-autogenous grinding followed by ball milling, the standard hard-rock circuit. | electricity | 9 | — | commercial; CIMS |
|  | **High-pressure grinding rolls** | efficient variant | Bed comminution in place of part of the milling duty, at lower specific energy. | electricity | 9 | — | commercial; harmonized |
|  | **Stirred fine grinding mills** | efficient variant | Vertical or horizontal stirred mills for fine and regrind duties. | electricity | 9 | — | commercial; harmonized |
|  | **Sensor-based ore sorting** | alternative | Rejects waste rock before milling, cutting the tonnes ground. | electricity | 9 | — | commercial; harmonized |
| `separation-and-processing` | **Froth flotation** | conventional | Reagents and air separate value minerals from gangue in flotation cells. | electricity; reagents | 9 | — | commercial; CIMS |
|  | **Gravity and magnetic separation** | conventional | Density and magnetic separation for iron ore and heavy minerals. | electricity | 9 | — | commercial; harmonized |
|  | **Thickening and filtration** | conventional | Dewaters concentrate and tailings before drying or disposal. | electricity; flocculants | 9 | — | commercial; CIMS |
|  | **Heap and atmospheric leaching with SX-EW** | conventional | Leaches metal into solution, then solvent extraction and electrowinning. | electricity; acid | 9 | — | commercial; harmonized |
|  | **Bioleaching** | alternative | Bacteria oxidise sulphides at low temperature in heaps or tanks. | electricity; air | 9 | — | iea_2024_001 row 126 |
|  | **High-pressure acid leaching** | alternative | Autoclave leaching of laterite and refractory ores. | steam, electricity; acid | 9 | — | iea_2024_001 row 128 |
|  | **In-situ leaching** | alternative | Leaches the orebody in place, with no mining or milling. | electricity; lixiviant | 9 | — | iea_2024_001 row 129; CIMS |
|  | **Potash crystallisation and flotation** | conventional | Separates potash by flotation, or crystallises it from hot brine. | steam, electricity | 9 | — | commercial; CIMS |
|  | **Direct lithium extraction** | prospective | Sorbents or membranes recover lithium from brine without evaporation ponds. | electricity, heat | 6 | — | iea_2024_001 row 127 |
| `product-drying` | **Direct-fired rotary or fluid-bed dryer** | conventional | Hot combustion gas drying concentrate, potash or coal. | natural gas, oil | 9 | — | commercial; CIMS |
|  | **Mechanical dewatering before drying** | efficient variant | Filters and centrifuges removing water mechanically instead of thermally. | electricity | 9 | — | commercial; harmonized |
|  | **Dryer heat recovery** | efficient variant | Recirculates exhaust or preheats feed air from the dryer stack. | recovered heat | 9 | — | commercial; harmonized |
|  | **Electric or heat-pump drying** | alternative | Electric air heating, or a heat pump on low-temperature duties. | electricity | 7-9 | — | iea_2024_001 rows 436, 438 |
| `pelletising` | **Straight-grate induration** | conventional | Green pellets dried, fired and cooled on one travelling grate. | heavy oil, natural gas, coke breeze, electricity | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Grate-kiln induration** | conventional | Travelling grate for drying and preheating, then a rotary kiln for firing. | heavy oil, natural gas, coal, electricity | 9 | — | commercial; nrcan_2025_001 |
|  | **Induration with cooler heat recovery** | efficient variant | Returns cooling-zone heat to drying and preheating zones. | recovered heat | 9 | — | commercial; harmonized |
|  | **Plasma or electric induration** | prospective | Plasma torches or electric heating replace the oil or gas burner. | electricity | 5 | LKAB plasma trials | iea_2024_001 row 409 |
| `ventilation-and-air-heating` | **Fixed-flow ventilation with direct-fired air heater** | conventional | Main fans at constant flow, with a gas or propane mine air heater. | electricity, natural gas, propane | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Ventilation on demand** | efficient variant | Fan and regulator control following where equipment and people are. | electricity | 9 | — | commercial; harmonized |
|  | **Electric or heat-pump mine air heating** | alternative | Electric heaters, or heat pumps on mine water or exhaust air. | electricity | 8 | — | assessed; harmonized |
|  | **Exhaust-air heat recovery** | efficient variant | Glycol loops or ice-stope storage recovering heat from exhaust air. | recovered heat, electricity | 7 | — | assessed; harmonized |
| `water-and-tailings-management` | **Mine dewatering pumping** | conventional | Pumping groundwater and surface water out of the pit or workings, and to treatment or discharge.<br>*Runs on the site water balance, not on ore throughput.* | electricity | 9 | — | commercial; harmonized |
|  | **Tailings thickening and water reclaim** | conventional | Thickeners and reclaim barges returning process water to the mill. | electricity | 9 | — | commercial; harmonized |
|  | **Paste and dry-stack tailings** | alternative | Dewaters tailings mechanically before placement, cutting pond volume and reclaim pumping. | electricity | 9 | filtered dry stack; paste thickeners | commercial |
|  | **Mine water treatment plant** | conventional | Lime treatment, settling and polishing before discharge. | electricity; reagents | 9 | — | commercial |
|  | **Reverse osmosis and evaporative concentration** | alternative | Membrane or thermal concentration where the discharge permit needs it, at much higher energy per cubic metre. | electricity; low-temperature heat (evaporation) | 9 | — | commercial; harmonized |

<br>

---

### Oil and gas (extraction, processing and pipelines)

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Drilling and well services** `drilling-and-well-services` | Drilling rigs, completions and hydraulic fracturing, well testing and servicing. | — | — | — | diesel, natural gas (dual-fuel and gas engines), electricity (grid-powered rigs) | Fracturing pump spreads are among the largest diesel loads in the sector; electric fleets compete. | CIMS |
| **Conventional oil and gas production** `oil-and-gas-production` | Light, medium, heavy and offshore oil and conventional, tight, shale and coalbed-methane gas wells: artificial lift, field compression, heater-treaters and line heaters, wellsite dehydration, pneumatic controllers and pumps, liquids unloading, enhanced oil recovery. | *low-temp*<br>heater-treaters and line heaters; not in held or checked sources | From `heat-low-temp` (heater-treaters and line heaters)<br>Integral (artificial lift and field gathering compression) | — | natural gas (fuel gas, gas-driven pneumatics), electricity, diesel | CIMS models electric replacements for gas-driven pneumatics. Field compressor drives are machine drive. | CIMS |
| **Produced water handling** `produced-water-handling` | Separation, treatment, recycling and disposal of produced and flowback water: disposal-well injection, de-oiling and softening for steam generation, evaporators and crystallisers, and recycling for makeup. | *low-temp*<br>softening and evaporation below 150 | From `heat-low-temp` (softening and evaporation)<br>Integral (fired evaporators) | `pumping` (disposal and recycle injection) | electricity (injection and transfer pumps, treatment); natural gas (evaporators, heaters) | Added 2026-09-15. In-situ bitumen recycles most of its produced water, so the water plant is part of what sets the steam-to-oil ratio; disposal injection carries its own energy and its own regulatory constraint. Kept out of in-situ-bitumen because it also serves conventional production and fracturing. Drawn on by 1 end use: `in-situ-bitumen`. |  |
| **Venting and flaring** `venting-and-flaring` | Gas deliberately disposed of rather than sold, and the equipment that captures or avoids it: solution-gas and process flaring, pneumatic and process venting, blowdowns for maintenance, liquids unloading, and tank vapours. | *not-applicable*<br>— | Integral (flare pilots and purge gas) | `compressed-air` (vapour recovery and instrument air) | natural gas (the gas vented or flared, plus flare pilot and purge gas and pneumatic supply gas); electricity (vapour recovery, instrument air) | Pipeline transport, processing and production vented and flared 8.3 Mt CO2e in 2019; leaks added 2.4 Mt. | nrcan_2025_001 |
| **Fugitive emissions** `fugitive-emissions` | Unintentional leaks from valves, flanges, connectors, seals, compressor packings and storage, and the survey, monitoring and component programmes that find and cut them. | *not-applicable*<br>— | — | — | natural gas (the gas leaked); electricity (survey and monitoring equipment) | Leaks added 2.4 Mt CO2e in 2019, against 8.3 Mt vented and flared. | nrcan_2025_001 |
| **In-situ bitumen recovery** `in-situ-bitumen` | SAGD, cyclic steam stimulation, solvent-assisted and hybrid thermal-solvent recovery: steam generation and injection, produced-water treatment and recycling, bitumen treating. | *medium-temp (unconfirmed)*<br>saturated injection steam; temperature not in held or checked sources | From `heat-medium-temp` (once-through field boilers and cogeneration) | `pumping` (injection and produced fluids)<br>`produced-water-handling` (makeup and recycle) | natural gas (steam generation), electricity; solvents; produced gas | Solvent routes compete by cutting steam demand. CIMS offers electric, hydrogen and nuclear steam. Lifecycle steam-to-oil ratio about 3.5 (SAGD) and 6.0 (CSS). | Oil Sands Magazine; CIMS |
| **Oil sands mining and extraction** `oil-sands-mining-and-extraction` | Truck-and-shovel mining, ore preparation and hydrotransport, hot- or warm-water bitumen extraction, froth treatment, tailings handling. | *low-temp*<br>hot-water extraction 80-85 (historical Clark process); modern plants cooler, not quantified | From `heat-low-temp` (process water heating) | `pumping` (hydrotransport and tailings)<br>`materials-handling` (ore conveying) | diesel (haul trucks, shovels), natural gas, electricity | Includes the haul fleet. | Alberta Energy Heritage; CIMS |
| **Bitumen upgrading** `bitumen-upgrading` | Upgraders that turn bitumen into synthetic crude: coking, hydrocracking, hydrotreating, sulphur recovery. | *medium-temp; high-temp*<br>as petroleum-refining conversion (reactors ~260-480); not upgrader-specific | From `heat-medium-temp` (fired heaters)<br>From `heat-high-temp` (fired heaters) | `upgrader-hydrogen` (hydroconversion) | natural gas, still gas and coke, hydrogen, electricity | Same technologies as petroleum-refining conversion-and-treating; CIMS models upgraders in Petroleum Crude. | rtc_2023_001 p.97; CIMS |
| **On-site hydrogen production** `upgrader-hydrogen` | Hydrogen made at a bitumen upgrader for hydroconversion: steam methane reformers with and without capture, and gasification of asphaltenes or petroleum coke. | *not-applicable*<br>reforming 788-843; steam is a reactant | Integral (reformer firebox) | `compressed-air` (make-up compression) | natural gas, petroleum coke, electricity | Moved out of the cross-sector hydrogen-and-fuel-supply end use (2026-09-14). Quest captures from these reformers, which is why the concentrated-stream capture row sits here. Drawn on by 1 end use: `bitumen-upgrading`. |  |
| **Natural gas processing** `gas-processing` | Sweetening (amine), dehydration (glycol), sulphur recovery, NGL extraction and fractionation, inlet and sales compression. | *low-temp; medium-temp*<br>amine and glycol regeneration (reboiler steam or direct-fired); not in held or checked sources | From `heat-low-temp` (reboilers)<br>From `heat-medium-temp` (reboilers)<br>Integral (plant refrigeration and compression) | — | natural gas, electricity | Acid gas stripped from raw gas goes to co2-capture-concentrated. | CIMS |
| **LNG liquefaction** `lng-liquefaction` | Gas pre-treatment, refrigeration-cycle compression and liquefaction, boil-off handling. | — | From `heat-low-temp` (amine pre-treatment)<br>Integral (refrigerant compression) | — | natural gas (gas-turbine compressor drives) or electricity (electric-drive trains) | LNG Canada (Kitimat, two trains, 14 Mtpa) shipped its first cargo in 2025. The drive choice, gas turbine or electric, is the main technology decision. | Shell 2025; CIMS |
| **Natural gas transmission and distribution** `gas-pipelines` | Compressor stations on transmission pipelines; gas-distribution systems, including line heaters at pressure let-down stations. | — | Integral (compressor stations) | — | natural gas drawn from the pipeline (turbine and engine compressor drives), electricity (electric-drive compressors), waste-heat recovery | Pipeline transport emitted 8.3 Mt CO2e in 2019, mostly from compressor-station combustion; leaks added 2.4 Mt. Includes compressor drives. | CER 2022 pipeline market snapshot; CIMS |
| **Crude oil and liquids pipelines** `oil-pipelines` | Pump stations on crude, bitumen blend and refined-product pipelines, plus drag-reducing and heating where used. | — | Integral (pump stations) | — | electricity (pump motors); some engine-driven pumps | Mostly electric motors. | CER 2022 pipeline market snapshot |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `drilling-and-well-services` | **Diesel drilling rig** | conventional | Diesel-electric rig powering the drawworks, mud pumps and camp. | diesel | 9 | — | commercial; CIMS |
|  | **Grid-powered or electric rig** | alternative | Rig drawing from the grid or a field electrical system. | electricity | 9 | — | iea_2024_001 row 218 |
|  | **Dual-fuel or natural-gas engines** | efficient variant | Field or well gas displaces part of the diesel in rig and pump engines. | natural gas, diesel | 9 | — | commercial; harmonized |
|  | **Electric fracturing fleet** | alternative | Electric pumps on grid or turbine power replace diesel pump spreads. | electricity, natural gas | 9 | — | assessed; harmonized |
|  | **Battery hybrid rig power** | efficient variant | Battery smooths engine load, cutting fuel and run hours. | diesel, electricity | 8 | — | assessed; harmonized |
| `oil-and-gas-production` | **Electric artificial lift** | conventional | Beam pumps, progressive-cavity and electric submersible pumps on motors. | electricity | 9 | — | iea_2024_001 row 218; CIMS |
|  | **Fired line heater and treater** | conventional | Burner heating produced fluids to break emulsions and prevent hydrates. | natural gas | 9 | — | commercial; harmonized |
|  | **Electric or heat-pump treating** | alternative | Electric heaters, or heat pumps, on low-temperature treating duties. | electricity | 8 | — | assessed; harmonized |
| `venting-and-flaring` | **Gas-driven pneumatic controllers and pumps** | conventional | Well-site instruments driven by pipeline gas, which vents methane. | natural gas | 9 | — | commercial; CIMS |
|  | **Instrument air or electric actuation** | efficient variant | Compressed air or electric actuators replace gas-driven devices. | electricity | 9 | — | iea_2024_001 row 219; CIMS |
|  | **Vapour recovery and flare gas recovery** | efficient variant | Compresses tank and flare gas back into the sales line. | electricity | 9 | — | iea_2024_001 row 220; CIMS |
|  | **Plunger lift and smart liquids unloading** | efficient variant | Unloads liquids without blowing the well down to atmosphere. | natural gas, electricity | 9 | — | commercial; CIMS |
|  | **Flare with continuous pilot** | conventional | Elevated flare burning solution and process gas that is not captured; the incumbent disposal route. | natural gas (the gas flared, plus pilot and purge gas) | 9 | — | commercial; CIMS |
|  | **Enclosed combustor or high-efficiency flare** | alternative | Enclosed or air-assisted combustion raising destruction efficiency and cutting unburnt methane.<br>*Abates the methane slip from an ordinary flare, not the flaring itself.* | natural gas (pilot and purge) | 9 | enclosed vapour combustors; air-assisted flare tips | commercial; CIMS |
|  | **Blowdown gas recompression** | alternative | Recompresses depressurisation gas into the line instead of venting it before maintenance.<br>*The harmonized `capture-unit` entry for this service is filed as CO2 capture; it is methane recovery.* | electricity, natural gas (compressor drive) | 9 | portable recompression units; pressurised pipeline transfer | commercial; CIMS |
| `fugitive-emissions` | **Leak detection and repair** | conventional | Scheduled surveys finding and fixing leaking components.<br>*Frequency is what sets the abatement; an annual programme and a quarterly one are different technologies in practice.* | electricity (survey equipment) | 9 | optical gas imaging surveys; Method 21 screening | commercial; CIMS |
|  | **Continuous methane monitoring** | alternative | Fixed sensors, or aerial and satellite screening, finding leaks between surveys; it also catches vent events, but it substitutes for survey frequency, which is why it sits here. | electricity | 8 | site sensor networks; aerial and satellite screening | assessed; commercial deployments on production sites |
|  | **Low-emission valves and connectors** | alternative | Bellows-sealed and low-leak valve and connector designs cutting the leak rate of new and replaced components. | — | 9 | bellows-sealed valves; low-e packing; welded connections | commercial |
|  | **Dry gas seals on centrifugal compressors** | alternative | Replaces wet seals, whose degassing vents methane continuously, on centrifugal compressors.<br>*Wet-seal degassing is one of the largest single fugitive sources at a compressor station.* | electricity (seal gas conditioning) | 9 | dry gas seal retrofits; seal gas recovery on wet seals | commercial |
| `in-situ-bitumen` | **Once-through field boiler** | conventional | Field boiler raising 75-80% quality steam from treated produced water; known in the field as a once-through steam generator (OTSG). | natural gas | 9 | — | commercial; CIMS |
|  | **Cogeneration supplying steam and power** | alternative | Gas turbine with a heat-recovery generator serving the steam demand and exporting power. | natural gas | 9 | — | commercial; CIMS |
|  | **Solvent-assisted steam recovery** | prospective | Co-injects a solvent with steam, cutting the steam-to-oil ratio. | natural gas, solvent | 7 | — | assessed; CIMS |
|  | **Solvent-only extraction** | prospective | Dissolves bitumen with solvent and little or no steam. | solvent, electricity | 6 | — | assessed; CIMS |
|  | **Direct contact steam generation** | prospective | Burns fuel in the water stream, producing steam and CO2 together for injection. | natural gas, oxygen | 6 | — | assessed; harmonized |
|  | **Electric steam generation** | prospective | Electrode or resistance boilers raising injection steam. | electricity | 7 | — | assessed; iea_2024_001 row 437; CIMS |
|  | **Nuclear steam supply** | prospective | Small modular reactor raising steam for injection. | nuclear | 7 | — | iea_2024_001 row 455; CIMS |
| `oil-sands-mining-and-extraction` | **Truck-and-shovel mining** | conventional | Electric shovels loading large diesel haul trucks. | diesel, electricity | 9 | — | commercial; CIMS |
|  | **Hydrotransport and warm-water extraction** | conventional | Slurries ore in warm water, separating bitumen froth in gravity vessels. | natural gas (water heating), electricity | 9 | — | commercial; CIMS; Alberta Energy Heritage |
|  | **Paraffinic froth treatment** | alternative | Paraffinic solvent rejects asphaltenes, giving a cleaner bitumen product. | solvent, natural gas, electricity | 9 | — | commercial; harmonized |
|  | **Non-aqueous extraction** | prospective | Solvent-based extraction without hot water, cutting heat and tailings. | solvent, electricity | 5-6 | — | assessed; harmonized |
|  | **Electric or autonomous haul fleet** | prospective | Battery or trolley trucks, often with autonomous haulage control. | electricity, diesel | 7-8 | — | iea_2024_001 row 135 |
|  | **Thickened or dry-stack tailings** | efficient variant | Dewaters tailings mechanically, cutting pond volume and recycled-water heating. | electricity; flocculants | 8 | — | assessed; harmonized |
| `bitumen-upgrading` | **Delayed coking** | conventional | Thermally cracks bitumen to lighter products and petroleum coke. | refinery fuel gas, steam | 9 | — | commercial; CIMS |
|  | **Fluid or flexi-coking** | conventional | Fluidised thermal cracking, with the coke partly gasified for fuel gas. | petroleum coke (captive), steam | 9 | — | commercial; CIMS |
|  | **Ebullated-bed hydrocracking** | conventional | Hydrogen addition in a moving catalyst bed for high conversion of residue. | hydrogen, natural gas, electricity | 9 | — | commercial; CIMS |
|  | **Fixed-bed hydrotreating** | conventional | Hydrogen treating to remove sulphur and stabilise synthetic crude. | hydrogen, natural gas | 9 | — | commercial; harmonized |
|  | **Partial upgrading** | prospective | Field-scale treatment that meets pipeline specification without full upgrading. | natural gas, electricity | 6-7 | — | assessed; harmonized |
| `gas-processing` | **Amine sweetening** | conventional | Amine absorption removing H2S and CO2, with a steam-heated regenerator. | steam or fired heat, electricity | 9 | — | commercial; CIMS |
|  | **Acid gas removal with CO2 compression and injection** | alternative | The amine unit already separates CO2 along with the H2S, so capture is compression, dehydration and injection instead of venting.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. Reservoir CO2 separated here is the cheapest capture in the database and should not be averaged with flue-gas capture.* | electricity for compression; the amine unit's own reboiler heat | 9 | acid gas injection, Alberta | commercial; Alberta acid gas injection schemes; CIMS |
|  | **Advanced acid gas removal** | efficient variant | Selective solvents or membranes cutting regeneration energy and losses. | steam, electricity | 9 | — | iea_2024_001 row 225 |
|  | **Glycol dehydration** | conventional | TEG contactor with a fired reboiler regenerating the glycol. | natural gas | 9 | — | commercial; harmonized |
|  | **Molecular-sieve dehydration** | alternative | Adsorbent beds regenerated with hot gas, to cryogenic-plant dryness. | natural gas, electricity | 9 | — | commercial; harmonized |
|  | **Turboexpander NGL recovery** | conventional | Expansion refrigeration recovering ethane and heavier liquids. | electricity, natural gas | 9 | — | commercial; CIMS |
|  | **Claus sulphur recovery** | conventional | Converts H2S to elemental sulphur, with tail-gas treating. | natural gas, electricity | 9 | — | commercial; harmonized |
|  | **Electric-drive compression** | alternative | Motor-driven compressors in place of gas turbines or engines. | electricity | 9 | — | iea_2024_001 row 218; CIMS |
| `lng-liquefaction` | **Gas-turbine-driven refrigeration** | conventional | Aero-derivative or heavy-duty turbines driving the refrigerant compressors. | natural gas | 9 | — | commercial; CIMS |
|  | **Electric-motor-driven refrigeration** | alternative | Large motors drive the compressors, moving the emissions to the grid. | electricity | 9 | Woodfibre LNG; Cedar LNG | iea_2024_001 row 218; CIMS |
|  | **Small-scale or modular liquefaction** | alternative | Modular trains for peak shaving and remote supply. | natural gas, electricity | 9 | — | iea_2024_001 row 213 |
|  | **Boil-off gas recovery** | efficient variant | Recompresses boil-off gas back into the process instead of flaring or fuelling. | electricity | 9 | — | commercial; harmonized |
|  | **Turbine waste-heat recovery** | efficient variant | Recovers turbine exhaust heat for process and utility duties. | recovered heat | 9 | — | commercial; harmonized |
| `gas-pipelines` | **Gas-turbine compressor station** | conventional | Turbine-driven compressors burning pipeline gas. | natural gas | 9 | — | iea_2024_001 row 214; CIMS |
|  | **Reciprocating gas-engine compressor** | conventional | Engine-driven reciprocating compressors, common on gathering systems. | natural gas | 9 | — | commercial; CIMS |
|  | **Electric-drive compressor** | alternative | Motor-driven compressors on grid power. | electricity | 9 | — | iea_2024_001 row 218 |
|  | **Compressor-station waste-heat power** | efficient variant | Organic Rankine cycle on turbine exhaust generating station power. | recovered heat | 9 | — | iea_2024_001 row 516 |
|  | **Turboexpander at pressure let-down** | efficient variant | Recovers pressure energy as power instead of throttling, with line heating. | natural gas (line heaters), electricity | 8 | — | assessed; harmonized |
| `oil-pipelines` | **Electric pump station** | conventional | Motor-driven mainline pumps moving crude and products. | electricity | 9 | — | commercial; CER 2022 pipeline market snapshot |
|  | **Variable-speed pump drives** | efficient variant | Speed control replaces throttling and station cycling. | electricity | 9 | — | commercial; harmonized |
|  | **Drag-reducing agents** | efficient variant | Polymer injection cuts friction, raising throughput per unit of pumping power. | electricity; chemical | 9 | — | commercial; harmonized |
|  | **Gas-engine driven pumps** | conventional | Engine-driven pumps on lines without grid supply. | natural gas, diesel | 9 | — | commercial; harmonized |
| `upgrader-hydrogen` | **Steam methane reformer** | conventional | Reforms natural gas with steam, then shifts to hydrogen and CO2. | natural gas, refinery fuel gas | 9 | refinery and ammonia hydrogen plants | iea_2024_001 row 285; CIMS |
|  | **Steam methane reformer with capture on the shift gas** | alternative | Capture on the shifted syngas, where the CO2 is already at high partial pressure. Taking the reformer flue gas as well needs a second, dilute-stream plant.<br>*Concentrated stream, held once on cross-sector co2-capture-concentrated. Partial capture takes only the shift gas and reaches about 60% of the plant total; full capture adds a diffuse-stream plant on the reformer flue gas.* | natural gas; steam and electricity for the capture plant | 9 | Quest, Alberta | iea_2024_001 row 285; row 284 gives 6 for high capture rates; CIMS |
|  | **Coal or petroleum-coke gasification** | conventional | Partial oxidation of solid feed to syngas, then shift. | coal, petroleum coke, oxygen | 9 | — | iea_2024_001 row 280; CIMS |
|  | **Water electrolysis, low temperature** | alternative | Alkaline or PEM stacks splitting water with electricity. | electricity, water | 9 | — | iea_2024_001 rows 261, 263 |
| `produced-water-handling` | **Disposal well injection** | conventional | Pumps produced and flowback water to a disposal formation. | electricity (injection pumps) | 9 | — | commercial; harmonized |
|  | **De-oiling and warm lime softening** | conventional | Skim tanks, induced gas flotation and warm lime softening conditioning produced water for steam generation.<br>*The water plant is part of what sets the steam-to-oil ratio.* | electricity; low-temperature heat | 9 | SAGD water plants | commercial |
|  | **Evaporators and crystallisers** | alternative | Mechanical vapour recompression evaporators producing distilled makeup and a small residual for disposal. | electricity (vapour recompression); natural gas | 9 | — | commercial; harmonized |
|  | **Produced water recycling for makeup** | alternative | Treats and reuses produced and flowback water as fracturing or steam makeup instead of disposing of it.<br>*Cuts both disposal energy and freshwater draw.* | electricity | 9 | — | commercial |

<br>

---

### Food and beverage

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Cooking, pasteurising and sterilising** `thermal-processing` | Cooking, blanching, scalding, pasteurising, sterilising and retorting, evaporating and concentrating, brewing, washing and CIP. | *low-temp*<br>pasteurizing 60-140, sterilizing 110-120, washing 60-90, cooking 95-200; pasteurisation 73, retort 100-121, evaporating 52-121; boiler steam 121-177 | From `heat-low-temp` (cooking, pasteurising and clean-in-place) | `pumping` (product transfer)<br>`compressed-air` (packaging and controls) | natural gas, electricity, biomass | 99% of steam-served heat is below 150 °C. | rtc_2023_001 p.66; NREL97 SIC 2026, 2033, 2046, 2075, 20xx; NREL118; caelp_2024_001 p.36 |
| **Baking, frying and roasting** `baking-frying-and-roasting` | Ovens, fryers and roasters. | *medium-temp; low-temp*<br>baking 100-232; roasting 93; cooking up to 200; proofing steam 38 | Integral (ovens, fryers and roasters) | `fans-and-blowers` (oven air and exhaust) | natural gas, electricity | Harmonized files ovens under process-heat-high-temp; the sources put them at 100-232 °C. | NREL97 SIC 2051, 2052, 2046; rtc_2023_001 p.66 |
| **Food drying** `drying` | Spray, drum, belt and grain drying; sugar and pulp drying. | *low-temp; medium-temp*<br>drying 30-90; drying 38-121; sugar calcining 316; steam dryers 54-93 | Integral (direct-fired dryers)<br>From `heat-low-temp` (steam dryers) | `fans-and-blowers` (dryer air) | natural gas, steam, electricity (heat pump and MVR dryers) | — | rtc_2023_001 p.66; NREL97 SIC 20xx, 2063 |
| **Refrigeration and cold storage** `refrigeration` | Chilling, freezing and cold storage: vapour-compression plant, ammonia and CO2 systems, spiral and blast freezers, and the cold rooms they serve. | *not-applicable*<br>— | From `heat-low-temp` (absorption machines) | — | electricity; low-temperature heat (absorption machines) | Moved out of the cross-sector process-cooling-and-refrigeration end use (2026-09-14): food and beverage is where process cooling is a real energy service. Chemical-plant and gas-plant refrigeration stays inside the process end use it serves. | nrcan_2025_001 |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `thermal-processing` | **Steam-heated kettles, retorts and plate heat exchangers** | conventional | Jacketed vessels, retorts and plate pasteurisers on site steam and hot water. | steam, hot water | 9 | — | commercial; CIMS; NREL97 |
|  | **Regenerative heat recovery on pasteurisers** | efficient variant | Product-to-product regeneration recovering most of the heating duty. | steam, electricity | 9 | — | commercial; harmonized |
|  | **Clean-in-place efficiency measures, moderate** | efficient variant | Recovery and control on cleaning and clean-in-place systems, which carry much of a plant's hot-water load.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column. The roster carries a moderate and a strong cleaning bucket; both sit here until a source separates them.* | steam, hot water, electricity | 9 | final-rinse reuse; heat recovery from CIP returns; cycle time and temperature optimisation | commercial; ukerc_2013_001; harmonized |
|  | **Heat pump for hot water and clean-in-place** | alternative | Heat pump supplies wash, CIP and low-temperature process water. | electricity | 9 | — | iea_2024_001 row 390 |
|  | **Ohmic, microwave or infrared heating** | alternative | Heats the product directly, without a steam loop. | electricity | 9 | — | iea_2024_001 rows 382, 384 |
|  | **Aseptic and UHT processing** | alternative | Short high-temperature treatment with regeneration, in place of in-container sterilising. | steam, electricity | 9 | — | commercial; harmonized |
|  | **High-pressure processing** | alternative | Non-thermal pasteurisation by pressure rather than heat. | electricity | 9 | — | commercial; harmonized |
| `baking-frying-and-roasting` | **Direct-fired tunnel or deck oven** | conventional | Burners firing into the baking chamber. | natural gas, propane | 9 | — | commercial; CIMS; NREL97 |
|  | **Indirect-fired oven** | conventional | Radiant tubes or heat exchangers keep combustion products out of the chamber. | natural gas | 9 | — | commercial; harmonized |
|  | **Electric oven, fryer or roaster** | alternative | Resistance elements in place of burners. | electricity | 9 | — | commercial; harmonized |
|  | **Microwave or radio-frequency assisted baking** | alternative | Volumetric heating shortens the bake and cuts oven length. | electricity | 9 | — | iea_2024_001 rows 382, 384 |
|  | **Oven exhaust heat recovery** | efficient variant | Recovers oven and fryer exhaust heat to make-up air or process water. | recovered heat | 9 | — | commercial; harmonized |
| `drying` | **Direct-fired spray, drum or belt dryer** | conventional | Hot gas drying liquids, solids and grain. | natural gas | 9 | — | commercial; CIMS; NREL97 |
|  | **Mechanical vapour recompression evaporation** | alternative | Concentrates the product before drying, with electricity instead of steam. | electricity | 9 | — | commercial; harmonized |
|  | **Dryer exhaust heat recovery and recirculation** | efficient variant | Recovers exhaust heat and recycles part of the drying air. | recovered heat | 9 | — | commercial; harmonized |
|  | **Heat-pump dryer** | alternative | Closed-loop heat pump drying at low temperature with dehumidification. | electricity | 8 | — | iea_2024_001 rows 390, 438 |
|  | **Electric air heating** | alternative | Electric heaters replace the dryer burner. | electricity | 9 | — | iea_2024_001 row 436 |
|  | **Microwave or radio-frequency drying** | alternative | Volumetric drying for finishing and low-moisture duties. | electricity | 9 | — | iea_2024_001 rows 382, 384 |
| `refrigeration` | **Vapour-compression chiller or refrigeration plant** | conventional | Electric compressor cycle delivering chilled water, brine or refrigeration. | electricity; ammonia, CO2 or HFC refrigerant | 9 | — | commercial; harmonized |
|  | **High-efficiency chiller** | efficient variant | Variable-speed or magnetic-bearing centrifugal machine, often on natural refrigerants. | electricity | 9 | — | commercial; harmonized |
|  | **Absorption chiller** | alternative | Heat-driven cycle using waste heat or steam instead of electricity. | recovered heat, steam, natural gas | 9 | — | iea_2024_001 row 85 |
|  | **Free or evaporative cooling** | conventional | Cooling towers and ambient air, without a refrigeration cycle. | electricity (fans, pumps); water | 9 | — | commercial; harmonized |

<br>

---

### Non-ferrous metals

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Alumina refining** `alumina-refining` | Bayer digestion, clarification, precipitation and calcination. | *low-temp; high-temp*<br>digesting 146 (steam), calcining 1204; calciner > 700 | From `heat-low-temp` (digestion)<br>Integral (calciner) | `pumping` (slurry and liquor) | natural gas, electricity | 7.4 PJ (boiler 3.0, calciner 4.5). | NREL97 SIC 2819; nrcan_2025_001 |
| **Aluminium smelting** `aluminium-smelting` | Hall-Heroult electrolysis (prebake and Soderberg cells); inert-anode cells. | *high-temp (resistive)*<br>bath ~960 | Integral (resistive cell heat) | `fans-and-blowers` (pot gas and dry scrubbing) | electricity; carbon anodes consumed | 45.0 PJ petroleum coke consumed as anode carbon (non-energetic). | etsap_2012_001 p.1; nrcan_2025_001 |
| **Anode production** `anode-production` | Prebake anode baking and Soderberg paste. | *high-temp*<br>baking 1204; > 700 | Integral (baking furnace) | — | natural gas, oil; pitch and coke as feed | 5.4 PJ. | NREL97 SIC 3334; nrcan_2025_001 |
| **Fuel-fired roasting, smelting and refining** `pyrometallurgy` | Roasting, flash, continuous and conventional smelting, converting and fire refining for copper, nickel, lead, zinc and magnesium. | *high-temp*<br>smelting 793, melting 538-1316, refining 1121; melting 1204 | Integral (smelting and converting) | `smelter-oxygen-supply` (enrichment)<br>`fans-and-blowers` (off-gas handling) | natural gas, coke, coal, electricity, oxygen | — | NREL97 SIC 3341, 3331 |
| **Oxygen supply** `smelter-oxygen-supply` | Cryogenic and adsorption air separation supplying oxygen enrichment to flash and bath smelting and to converting. | *not-applicable*<br>— | — (the air compressors are the process) | — | electricity (compression) | Serves flash and bath smelting and converting; enrichment is what sets smelter fuel use. Drawn on by 1 end use: `pyrometallurgy`. | nrcan_2025_001 |
| **Electric smelting (silicon, ferroalloys, titanium slag)** `electric-smelting` | Submerged-arc and electric smelting furnaces for silicon metal, ferrosilicon and other ferroalloys, and titanium slag from ilmenite. | *high-temp*<br>heating 816, drying 204; furnace temperatures not in held sources | Integral (electric furnace) | — | electricity (dominant); coal, coke, charcoal and wood chips as reductants | Becancour: two 24 MW and one 32 MW furnaces (silicon metal, ferrosilicon). Rio Tinto Fer et Titane (Sorel-Tracy): about 1.35 Mt/yr titanium slag capacity. NAICS codes ferroalloys to 331110 (iron and steel). | NREL97 SIC 3313; Ferroglobe Bécancour; QIT-Fer et Titane |
| **Leaching and electrowinning** `hydrometallurgy` | Leaching, solvent extraction, electrowinning and electrorefining. | *low-temp*<br>electrolyte and refining heat 60 (steam) | From `heat-low-temp` (electrolyte heating) | `pumping` (leach and electrolyte circulation) | electricity, steam | Non-ferrous steam-served heat is 100% below 150 °C. | NREL97 SIC 3331; NREL118 |
| **Melting, casting, rolling and extrusion** `melting-casting-and-fabrication` | Secondary aluminium, melt and cast shops, holding and reheating furnaces, homogenising, hot and cold rolling, extrusion. | *high-temp*<br>melting 316-1316; reheating > 700 | Integral (melting and holding furnaces) | `compressed-air` (casting and handling) | natural gas, electricity (induction) | Aluminium reheating furnaces 2.7 PJ. Semi-fabrication is about 20% of US aluminium energy (hot rolling 10.1%, extrusion 5.3%, cold rolling 4.7%). | NREL97 SIC 3341; nrcan_2025_001; DOE 2017 aluminium bandwidth study |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `alumina-refining` | **Bayer digestion on fossil steam** | conventional | Caustic digestion of bauxite under pressure, with steam from gas or oil boilers. | natural gas, oil (steam), electricity | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Gas-suspension calciner** | efficient variant | Suspension calcination of hydrate, at lower fuel use than a rotary calciner. | natural gas | 9 | — | commercial; harmonized |
|  | **Electrified Bayer heat** | prospective | Electric boilers or heaters supply digestion heat. | electricity | 7 | — | iea_2024_001 row 307 |
|  | **Biomass-fired Bayer heat** | prospective | Biomass replaces a high share of the fossil fuel raising digestion steam. | biomass | 7 | — | iea_2024_001 row 309 |
|  | **Solar thermal in the Bayer process** | prospective | Concentrating solar raises part of the digestion heat. | solar | 6 | — | iea_2024_001 row 312 |
|  | **Hydrogen in the Bayer process** | prospective | Hydrogen firing for digestion and calcination heat. | hydrogen | 5 | — | iea_2024_001 row 311 |
| `aluminium-smelting` | **Prebaked anode cell** | conventional | Centre-worked prebake Hall-Heroult cells with point feeding. | electricity; carbon anodes | 9 | — | commercial; etsap_2012_001; CIMS |
|  | **Soderberg cell** | conventional | Self-baking anode cells, the older Canadian stock. | electricity; anode paste | 9 | — | commercial; CIMS |
|  | **Inert anode cell** | prospective | Non-consumable anodes give oxygen instead of CO2 at the anode. | electricity | 7 | ELYSIS (Quebec) | iea_2024_001 row 303 |
|  | **Multipolar or chloride cell** | prospective | Cell geometry or chloride chemistry cutting cell voltage and footprint. | electricity | 5 | — | iea_2024_001 rows 302, 304 |
|  | **Smelter power modulation** | efficient variant | Controlled amperage swings let the potline follow the grid without losing production. | electricity | 9 | — | iea_2024_001 rows 306, 301 |
| `anode-production` | **Prebake anode baking furnace** | conventional | Open or closed ring furnace baking green anodes. | natural gas, oil | 9 | — | commercial; CIMS; nrcan_2025_001 |
|  | **Soderberg paste plant** | conventional | Mixes and pastes anode material for self-baking cells. | natural gas, electricity; pitch, coke | 9 | — | commercial; CIMS |
|  | **Electrified or hydrogen-fired anode baking** | prospective | Electric or hydrogen heat replaces the fossil burner on the baking furnace. | electricity, hydrogen | 6-8 | — | iea_2024_001 rows 308, 310 |
|  | **Bio-pitch and bio-coke anodes** | prospective | Biogenic binder and filler replacing fossil pitch and petroleum coke. | biomass-derived pitch and coke | 6 | — | assessed; harmonized |
| `pyrometallurgy` | **Flash smelting furnace** | conventional | Oxygen-enriched flash smelting of sulphide concentrate, with a waste-heat boiler. | oxygen, natural gas, coal; sulphide oxidation heat | 9 | — | commercial; CIMS; NREL97 |
|  | **Smelting efficiency measures, moderate** | efficient variant | Incremental measures on an existing smelter off-gas and feed system.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, oxygen, electricity | 9 | feed drying with off-gas heat; improved hooding; oxygen control | commercial; harmonized |
|  | **Top-submerged-lance bath smelting** | conventional | Bath smelting with a submerged lance, for concentrates and secondary feed. | natural gas, oxygen, coal | 9 | — | commercial; harmonized |
|  | **Peirce-Smith converting** | conventional | Batch converting of matte to blister metal. | oxygen; matte oxidation heat | 9 | — | commercial; CIMS |
|  | **Continuous converting** | efficient variant | Continuous flash or bath converting, cutting fugitive losses and fuel per tonne. | oxygen, natural gas | 9 | — | commercial; CIMS |
|  | **Smelting efficiency measures, strong** | efficient variant | Higher oxygen enrichment with a waste-heat boiler on the off-gas.<br>*Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.* | natural gas, oxygen; recovered heat | 9 | higher oxygen enrichment; waste-heat boiler on the off-gas; off-gas heat to feed drying | commercial; harmonized |
|  | **Hydrogen-fired ancillary heat** | prospective | Hydrogen burners on holding, roasting and refining furnaces. | hydrogen | 6 | — | iea_2024_001 row 310 |
| `electric-smelting` | **Submerged-arc furnace** | conventional | Electrodes buried in the charge, smelting silicon, ferroalloys or titania slag. | electricity; coal, coke, charcoal, wood chips | 9 | — | commercial; NREL97; CIMS |
|  | **Open-arc DC furnace** | alternative | Direct-current open arc, taking finer feed and a wider reductant range. | electricity; carbon reductant | 9 | — | commercial; harmonized |
|  | **Pre-reduction of feed** | efficient variant | Reduces the ore before smelting, cutting furnace electricity per tonne. | natural gas or hydrogen; electricity | 6-7 | BlueSmelting (Rio Tinto Fer et Titane) | assessed; Rio Tinto |
|  | **Biocarbon reductant** | alternative | Charcoal or biocoke replaces fossil carbon in the charge. | biocarbon; electricity | 8 | — | assessed; iea_2024_001 row 400 |
|  | **Off-gas energy recovery** | efficient variant | Recovers CO-rich furnace gas as fuel or power. | recovered gas | 9 | — | commercial; harmonized |
| `hydrometallurgy` | **Atmospheric leaching with solvent extraction and electrowinning** | conventional | Leach, solvent extraction and electrowinning producing cathode metal. | electricity; acid, steam | 9 | — | commercial; CIMS; NREL97 |
|  | **High-pressure acid leaching** | alternative | Autoclave leaching of laterites and refractory concentrates. | steam, electricity; acid | 9 | — | iea_2024_001 row 128 |
|  | **Bioleaching** | alternative | Bacterial oxidation of sulphides at low temperature. | electricity; air | 9 | — | iea_2024_001 row 126 |
|  | **Electrowinning with advanced anodes and energy control** | efficient variant | Lower-overpotential anodes and current control cutting cell power. | electricity | 8 | — | assessed; harmonized |
|  | **Direct lithium extraction** | prospective | Sorbent or membrane recovery of lithium from brine. | electricity, heat | 6 | — | iea_2024_001 row 127 |
| `melting-casting-and-fabrication` | **Reverberatory or rotary melting furnace** | conventional | Gas-fired melting of ingot, scrap and returns before casting. | natural gas, oil | 9 | — | commercial; CIMS; NREL97 |
|  | **Regenerative or oxy-fuel melting** | efficient variant | Air preheat or oxygen firing cutting melting fuel per tonne. | natural gas, oxygen | 9 | — | commercial; harmonized |
|  | **Twin-chamber furnace with decoating** | efficient variant | Burns off coatings and melts in separate chambers, raising recovery and cutting fuel. | natural gas | 9 | — | iea_2024_001 row 305 |
|  | **Induction melting and holding** | alternative | Electric induction melting and holding in place of fired furnaces. | electricity | 9 | — | iea_2024_001 row 372 |
|  | **Homogenising and reheat furnaces** | conventional | Heat treatment of billets and slabs before extrusion or rolling. | natural gas, electricity | 9 | — | commercial; harmonized |
|  | **Continuous casting and rolling** | efficient variant | Casts and rolls in one line, avoiding a reheating step. | electricity, natural gas | 9 | — | commercial; harmonized |
| `smelter-oxygen-supply` | **Cryogenic air separation unit** | conventional | Distils liquefied air into oxygen, nitrogen and argon at large scale. | electricity | 9 | on-site ASUs at steelworks and smelters | commercial; CIMS |
|  | **Pressure or vacuum swing adsorption** | conventional | Adsorbent beds producing oxygen or nitrogen at smaller scale and lower purity. | electricity | 9 | — | commercial; harmonized |
|  | **Membrane separation** | conventional | Polymer membranes producing nitrogen or oxygen-enriched air. | electricity | 9 | — | commercial; harmonized |

<br>

---

### Other industry

| End use | Covers | Heat demand (°C) | Heat source | Draws on | Energy inputs | Notes | Sources |
| - | - | - | - | - | - | - | - |
| **Metal melting and heat treatment** `metal-melting-and-heat-treatment` | Foundry melting, forging, heat treating and annealing in fabricated metals, machinery and transport equipment. | *high-temp*<br>foundry melting 1593, forging 1316, annealing 427 | Integral (melting and heat-treatment furnaces) | `compressed-air` (quenching and handling) | natural gas, electricity (induction, arc), coke (cupolas) | — | NREL97 SIC 3321, 3462, 3353 |
| **Drying, curing and forming** `drying-curing-and-forming` | Textile drying and finishing, paint curing, plastics and rubber moulding and extrusion, other product drying. | *low-temp; medium-temp*<br>textile drying 82-121, singeing 204-260; paint drying 82-149; moulding 121-149 | Integral (dryers, ovens and presses)<br>From `heat-low-temp` (steam-heated dryers)<br>From `heat-medium-temp` (moulding and extrusion) | `compressed-air` (moulding and conveying) | natural gas, steam, electricity | Most of other industry's energy sits in the cross-sector end uses, including construction diesel in mobile-equipment. Steam-served heat: plastics mostly 150-200 °C, textiles mostly < 150 °C, transport equipment < 100 °C. | NREL97 SIC 2221, 2262, 3711, 3069; NREL118 |
| **Wood drying and panel pressing** `wood-drying-and-pressing` | Lumber dry kilns, veneer and strand dryers, hot presses for plywood, OSB and MDF, wood pellet drying. | *medium-temp; low-temp*<br>drying 177-193, pressing 191, digesting 188; steam ~191 (NREL-assigned, one SIC) | Integral (direct-fired dryers)<br>From `heat-medium-temp` (steam kilns and press platens) | `materials-processing` (sawing and planing drives) | wood residues (hog fuel, sawdust), natural gas, electricity | Wood products are 2.9% of Canadian manufacturing energy. Sawing and planing are machine drive. NREL's temperatures come from one SIC; no held source gives lumber kiln temperatures. | NREL97 SIC 2499; NREL118 NAICS 321; NRCan Trends 2017 |

**Technologies**

| End use | Technology | Type | What it is | Energy inputs | TRL | Examples | Sources |
| - | - | - | - | - | - | - | - |
| `metal-melting-and-heat-treatment` | **Cupola or gas-fired melting furnace** | conventional | Coke cupola or gas-fired furnace melting iron and non-ferrous metal in foundries. | coke, natural gas | 9 | — | commercial; CIMS; NREL97 |
|  | **Induction melting furnace** | alternative | Coreless or channel induction melting, common in modern foundries. | electricity | 9 | — | iea_2024_001 row 372 |
|  | **Electric arc melting furnace** | alternative | Arc melting for steel and iron castings. | electricity | 9 | — | commercial; harmonized |
|  | **Fuel-fired heat-treatment furnace** | conventional | Batch and continuous furnaces for annealing, normalising and forging heat. | natural gas, propane | 9 | — | commercial; CIMS; NREL97 |
|  | **Electric or induction heat treatment** | alternative | Resistance or induction heating for hardening, forging and annealing. | electricity | 9 | — | iea_2024_001 row 372 |
|  | **Regenerative or recuperative burners** | efficient variant | Air preheat on melting and heat-treatment furnaces. | natural gas | 9 | — | commercial; harmonized |
| `drying-curing-and-forming` | **Direct-fired dryer or curing oven** | conventional | Gas-fired ovens for paint curing, textile finishing and product drying. | natural gas | 9 | — | commercial; CIMS; NREL97 |
|  | **Infrared or ultraviolet curing** | alternative | Radiant or photochemical curing in place of hot-air ovens. | electricity | 9 | — | iea_2024_001 rows 383, 385 |
|  | **Electric air heating** | alternative | Electric heaters replace the oven or dryer burner. | electricity | 9 | — | iea_2024_001 row 436; CIMS |
|  | **Heat-pump drying** | prospective | Closed-loop heat pump drying and dehumidification below about 150 °C. | electricity | 7-8 | — | iea_2024_001 rows 390, 438 |
|  | **All-electric injection moulding and extrusion** | efficient variant | Servo-electric machines replacing hydraulic drives, with electric barrel heating. | electricity | 9 | — | commercial; CIMS |
|  | **Oven and dryer heat recovery** | efficient variant | Recovers exhaust heat to make-up air or process water. | recovered heat | 9 | — | commercial; harmonized |
| `wood-drying-and-pressing` | **Steam or thermal-oil lumber kiln** | conventional | Batch kilns heated by hog-fuel boilers through steam or thermal oil. | biomass (hog fuel), natural gas; electricity (fans) | 9 | — | commercial; CIMS; NREL97 |
|  | **Continuous kiln with heat recovery** | efficient variant | Continuous drying with zone heat recovery, at lower energy per cubic metre. | biomass, natural gas, recovered heat | 9 | — | commercial; harmonized |
|  | **Direct-fired veneer and strand dryer** | conventional | Hot gas from a burner or boiler drying veneer, strands and particles. | biomass, natural gas | 9 | — | commercial; NREL97 |
|  | **Hot press with thermal-oil heater** | conventional | Heated platens curing resin in plywood, OSB and MDF panels. | biomass, natural gas (thermal oil) | 9 | — | commercial; harmonized |
|  | **Dehumidification or heat-pump kiln** | alternative | Heat-pump kiln recovering latent heat from the drying air. | electricity | 8 | — | iea_2024_001 rows 390, 438 |
|  | **Radio-frequency or vacuum drying** | prospective | Volumetric drying for thick stock and specialty products. | electricity | 7 | — | iea_2024_001 row 384 |

## Sources

| Key | What it is | Where |
| - | - | - |
| NREL97 | NREL county-level industrial energy use: `Process_temperatures.csv`, one temperature per unit process by SIC code, split by heat type (fuel, steam, water, electric) | `data/raw-data/gov-usa/nrel/97_2018/`, **not yet registered** |
| NREL118 | NREL Manufacturing Thermal Energy Use in 2014: `mfg_eu_temps_*.csv`, 3.2 M rows. The shares above are energy-weighted by 4-digit NAICS and computed for this table | `data/raw-data/gov-usa/nrel/118_2019/`, **not yet registered** |
| nrcan_2025_001 | NRCan sub-process fossil fuel distribution for heavy industry (Canada), with its own bands < 200 / 200–700 / > 700 °C | `data/raw-data/gov-can/nrcan/nrcan_2025_energy-mapping-canada.xlsx` |
| rtc_2023_001 | RTC Industrial Thermal Decarbonization Package. Process temperatures by sector from DOE 2022 and BCG; page numbers are PDF pages; its bands are < 130 / 130–500 / > 500 °C | `data/raw-data/other-reports/`, registered, not extracted |
| caelp_2024_001 | CAELP/E3 *Measuring Economic Potential for Decarbonizing Industrial Heat* | `data/raw-data/other-reports/`, registered, not extracted |
| etsap_2010_002, etsap_2010_003, etsap_2012_001, etsap_2013_002, etsap_2015_001 | ETSAP I02, I03, I10, E19, I07, via their extractions | `data/raw-data/iea/etsap/` |
| iea_2024_001 | IEA ETP Clean Energy Technology Guide, 2024 edition; `row N` is its row number, and TRLs are as the guide reports them | `data/raw-data/iea/iea_2024_clean-tech-guide_rows.csv` |
| etsap_2010_001, lbnl_2021_001 | ETSAP I01 industrial boilers; LBNL electrification of boilers | `data/raw-data/` |
| epa_2017_001 | EPA CHP catalogue (steam-turbine process steam conditions) | harmonized `tech-parameter` |
| epa_2007_001 | EPA biomass CHP catalogue | harmonized `tech-parameter` |
| ipcc_2022_001 | IPCC AR6 WGIII Chapter 11, Table 11.3 (capture options; cites keith_2018_001, fasihi_2019_001) | `data/raw-data/peer-reviewed/` |
| ukerc_2013_001 / johansson_2012_001 | UKERC CH-SC28 reboiler duty | harmonized `tech-flow` |
| design doc | `design/industrial heat technology database design.md` | this repo |
| harmonized | the current harmonized layer | `data/harmonized/` |
| CIMS | CIMS model inputs, regions stripped | `C:\_dev\staging\cims\data\model_inputs\model\`, via `cims-roster.csv` |

Web sources checked 2026-09-11, not held in the repo:

| Source | Used for |
| - | - |
| [DOE 2015 chemicals bandwidth study](https://www.energy.gov/sites/prod/files/2015/08/f26/chemical_bandwidth_report.pdf) | ethanol 10% and industrial gases 3% of US chemicals energy |
| [DOE 2017 aluminium bandwidth study](https://www.energy.gov/sites/prod/files/2017/12/f46/Aluminum_bandwidth_study_2017.pdf) | semi-fabrication shares |
| [DOE 2015 iron and steel bandwidth study](https://www.energy.gov/sites/default/files/2015/08/f26/iron_and_steel_bandwidth_report_0.pdf) | coverage check only |
| [NRCan Trends 2017](https://oee.nrcan.gc.ca/publications/statistics/trends/2017/industrial.cfm) | subsector shares: wood products 2.9%, construction 3.1%, upstream 36.5% |
| [CER bioenergy overview](https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/renewable-energy-canada/an-overview-of-bioenergy.html) | ethanol, biodiesel and renewable diesel capacity |
| [Energies 2026 mining review](https://www.mdpi.com/1996-1073/19/8/1890) | mine energy breakdown; diesel over 80% at isolated mines |
| [Ferroglobe Bécancour](https://www.ferroglobe.com/about-ferroglobe/industrial-footprint/b%C3%A9cancour) | furnace sizes |
| [QIT-Fer et Titane](https://en.wikipedia.org/wiki/QIT-Fer_et_Titane) | slag capacity |
| [Oil Sands Magazine](https://www.oilsandsmagazine.com/news/2024/10/24/sagd-vs-css-thermal-in-situ-recovery-differences) | SAGD and CSS steam-to-oil ratios |
| [Alberta Energy Heritage](https://www.history.alberta.ca/energyheritage/sands/unlocking-the-potential/the-scientific-and-industrial-research-council-of-alberta/the-hot-water-separation-process.aspx) | Clark process water temperatures |
| [Shell 2025](https://www.shell.com/news-and-insights/newsroom/news-and-media-releases/2025/first-cargo-leaves-lng-canada.html) | LNG Canada capacity and first cargo |
| [CER 2022 pipeline market snapshot](https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/market-snapshots/2022/market-snapshot-greening-canadas-pipeline-infrastructure.html) | pipeline emissions; gas pipelines use gas-driven compressors, oil pipelines use electric pumps |
| [Algoma 2025 sustainability report summary](https://www.stocktitan.net/news/ASTL/algoma-steel-releases-2025-sustainability-f731fifk23lf.html) | first EAF July 2025; blast furnace and coke ovens decommissioned January 2026 |
| [GEM Dofasco](https://www.gem.wiki/ArcelorMittal_Dofasco_steel_plant) | Energiron ZR DRI project, blast furnace retirement dates |
| [GEM HIsarna](https://www.gem.wiki/HIsarna_process) | HIsarna pilot scale at IJmuiden |
| [ARENA NeoSmelt](https://arena.gov.au/projects/project-neosmelt/) | DRI-ESF pilot study, 2025-26 |
| [Canary Media: Electra](https://www.canarymedia.com/articles/green-steel/electra-clean-iron-investment-electrowinning) | low-temperature iron electrowinning demonstration |
| [Boston Metal](https://www.bostonmetal.com/moe-steel/) | molten oxide electrolysis demonstration |
| [Primetals HYFOR](https://www.primetals.com/en/portfolio/solutions/ironmaking/direct-reduction/hyfor/) | fluidised-bed hydrogen direct reduction pilot |
| [Rondo 2025](https://www.rondo.com/news-press/rondo-powers-up-worlds-largest-industrial-heat-battery) | 100 MWh heat battery, steam above 100 bar, October 2025 |
| [Heaten](https://heaten.com/) | steam-generating heat pump to 180 degC |
| [Coolbrook 2024](https://www.thechemicalengineer.com/news/coolbrook-primed-for-industry-use-after-rotodynamic-heater-pilot-tests-reach-over-1-000-c/) | RotoDynamic Heater pilot above 1,000 degC |
| [X-energy/Dow](https://x-energy.com/news/nrc-issues-environmental-assessment-with-finding-of-no-significant-impact-for-dow-and-x-energys-propsed-advanced-nuclear-project-in-texas/) | HTGR for industrial steam and power |
| [Deep Sky 2025](https://www.deepskyclimate.com/blog/history-made-deep-sky-alpha-begins-operations-with-north-americas-first-co2-storage-via-direct-air-capture-2) | Deep Sky Alpha, Innisfail, operating August 2025 |
| [Stratos](https://www.qcintel.com/carbon/article/stratos-dac-timeline-unclear-after-commissioning-issue-found-64333.html) | liquid-solvent DAC commissioning status |
| [BASF e-cracker](https://www.thechemicalengineer.com/news/world-first-electric-steam-cracker-demo-starts-operations-in-push-to-slash-emissions-by-90/) | electric steam-cracker demonstration at Ludwigshafen |
| [Rio Tinto](https://www.riotinto.com/en/can/canada-operations/rio-tinto-fer-et-titane) | BlueSmelting pre-reduction at Sorel-Tracy |
| [Svante / Lafarge Richmond](https://www.svanteinc.com/press-releases/lafarge-canada-collaborates-with-svante-and-dimensional-energy-to-begin-utilization-of-co2-captured-at-richmond-cement-plant/) | solid-sorbent capture pilot on a cement plant |

NREL, NRCan and RTC bands are not mapped onto ours; tiers are assigned from continuous
temperatures (NREL 97 and 118) or stated process temperatures.

In the technology tables, "commercial" means the level is taken from wide deployment
rather than a published TRL, and "assessed" means it is read from project or pilot
evidence. "harmonized" means the technology is already in the roster.

## How CIMS's capture requests split

CIMS has one `CCS` service per sector, costed from NETL/DOE 2022 *Cost of Capturing
CO2 from Industrial Sources*:

| CIMS node | Natural gas (GJ/t CO2) | Capex ($ per t-per-yr) |
| - | - | - |
| Chemical Products.CCS | 1.0 | 153 |
| Iron and Steel.CCS | 4.29 | 514 |
| Industrial Minerals.CCS | 4.84 | 589 |
| Petroleum Refining.CCS | 3.38 | 692 |

Technologies requesting CCS, by stream:

| Concentrated | Diffuse |
| - | - |
| Chemicals: `Adv reforming reactors CCS` (ammonia, methanol) | Chemicals: `NG CCS`, `Coal CCS`, `BPST NG 30 MW CCS` (Steam); `Product gas CCS` (Pyrolysis) |
| Refining: `NG steam reforming Eff CCS`, `petcoke gasification CCS` (Hydrogen) | Refining: Steam, Still Gas boiler / cogen / heater, `NG Eff CCS` (Direct Heat), `Fluidized catalytic cracking CCS`, `Coking soaker visbreaking CCS` |
| Iron and steel: `HIsarna CCS`, `DRI + EAF + CCS`, `Smelter + EAF + CCS`, `Corex smelter + CCS`, `Top gas recycling CCS` | Iron and steel: Steam `NG CCS`, `Coal CCS`, `BPST NG 30 MW CCS`; `Iron sinter agglomeration CCS`; `Ultra power EAF + O2 + CCS` |
| Natural gas: `Formation CCS` (acid gas at processing plants) | Industrial minerals: `New preheat Eff with CCS` (cement kiln), `Rotary Coal/NG with CCS` (lime), `NG Eff` / `Coal Std with CCS` (Heat) |
| Petroleum crude: `SMR CCS` (Hydrogen), `Upgrading ELDAR CCS` | Petroleum crude: Steam and Still Gas Steam boilers and cogen |
| | Natural gas: `Boiler Efficient CCS` (Direct Heat), `Flaring CCS` |
| | Ethanol and biodiesel: Steam boilers only (CIMS has no fermentation-CO2 capture) |

Smelting reduction, Corex and top-gas recycling are unsourced as concentrated (IPCC
names only HIsarna and syngas DRI). An SMR emits both kinds; CIMS books one rate.

## Technology table

`end-use-technology-table.csv` holds the technology rows in full: type, description,
energy inputs, TRL and its basis, examples, matching roster and CIMS names, sources
and notes. The .md shows a shortened view.

`specific-energy-use` is empty everywhere for now. Each technology, efficient variants
included, is to carry its own energy use once a source is found, rather than a saving
against a base technology.

Coverage: all thirteen sector groups, 393 technologies. Empty `roster-match` and
`cims-match` cells mark technologies the database and CIMS do not yet carry.

## Found along the way

- **CIMS defect:** in the NB and NL petroleum-refining files, the service
  `Distillation.Atmospheric` reads `Distillation.NBmospheric` and
  `Distillation.NLmospheric`. It looks like a find-and-replace of a region code. It
  lives in `staging/cims/.../petroleum_refining/petroleum_refining_{nb,nl}.csv` and
  splits those provinces' atmospheric distillation onto a separate service.
- **CIMS defect:** `Petroleum Refining.Steam` technology `NG CCS` requests 66.5 t CO2
  per unit from the CCS service. Every other boiler requests about 0.06 t, including
  `NG Eff CCS` on the same node. It looks like a factor-of-1000 unit slip.
- **Harmonized extraction error:** `tp-1509` stores the direct-air-capture abatement
  cost as 2.0 USD/t. The IPCC Table 11.3 cell reads "about USD94–232 t–1", so the
  number was probably taken from a stray "2" in the cell. The fix belongs in the IPCC
  extraction, not in the generated CSV.
- **Harmonized naming clash:** the roster entry `capture-unit` carries both the CIMS
  natural-gas blowdown capture (methane) and IPCC's "CCUS of concentrated CO2". They
  are different things under one name.
- **Temperatures missing for the new sector:** no held or checked source gives
  temperatures for SAGD steam, heater-treaters, amine and glycol regeneration, or
  modern warm-water oil-sands extraction. Those cells say so, and `in-situ-bitumen` is
  marked as an unconfirmed tier.
- **Food ovens are filed under `process-heat-high-temp`** in the harmonized layer. The
  sources put baking at 100–232 °C (NREL 97), which is medium tier.
- **No held source gives a temperature** for potash drying and crystallisation, mine
  air heating, capture solvent regeneration, or recovery-boiler steam conditions.
  `mining/product-drying` is marked as an unconfirmed tier.
- NREL 97 and NREL 118 now carry real weight: they are the only continuous-temperature
  sources. Registering them in the manifest is overdue.

