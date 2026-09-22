# Sector and end-use table: proposal

**Status: proposal for review, 2026-09-11; aligned with the CIMS service hierarchy on 2026-09-16 (`cims-hierarchy-harmonization.md`). The harmonized layer has not been changed.**
The record is `sector-end-use-table.csv` in this folder: one row per (sector, end use),
14 columns. This file is the readable version.

There are 13 sectors plus a cross-sector group, and 94 end uses.

The table sets out the categories to collect against: an end use per service with its own
technology set, and the technologies to find data for. Empty cells mark what is still
to be found.

**CIMS coverage:** the end uses are aligned with the CIMS service hierarchy
(`design/cims_hierarchy.csv`, restructured to match on 2026-09-17). Its 15 industrial
sectors, plus the new direct-air-capture sector, hold 311 services:

- 263 map to an end use
- 16 supply heat to the cross-sector heat bands or route a by-product fuel
- 30 are fuel-blend nodes and 2 are agricultural feedstock inputs, which are not end uses

The per-node mapping is `cims-hierarchy-crosswalk.csv`, and the CSV's `cims-services`
column is generated from it.

## Rules

1. **Cross-sector** holds the end uses common to all sectors: the three heat bands,
   on-site power-only generation, the five machine-drive categories, facility
   services (space heating and space cooling, each including building ventilation, and
   lighting), CO2 capture (concentrated and diffuse streams), direct air capture, and
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
   generalized together when the generalization is natural (different casting methods
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
- Machine drive follows the EIA MECS categories: pumps, fans and blowers, compressed
  air, materials handling and materials processing. The MECS residual is not carried.
- On-site hydrogen production sits with its host sector (`refinery-hydrogen`,
  `upgrader-hydrogen`); a `hydrogen` sector holds centralized production and
  distribution; biogas and RNG are a biofuels end use.
- Air separation is a sector end use (`steel-oxygen-supply`, `smelter-oxygen-supply`);
  glass oxy-fuel firing, oxy-fuel capture and merchant gases are not carried.
- Process cooling is a food and beverage end use.
- Venting, flaring and fugitive emissions are three oil-and-gas end uses: gas disposed
  of rather than sold, with the abatement options as competing technologies.
- Building ventilation is part of space heating and space cooling.
- Glass melting, glass forming and finishing, and ceramic firing are separate end uses,
  as are mechanical and recycled-fibre pulping.
- Wood preparation is a pulp and paper end use; nitric and adipic acid are a chemicals
  end use.
- The `cims-services` column names CIMS hierarchy paths.

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
