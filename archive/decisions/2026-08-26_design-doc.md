# Industrial heat technology database — design

Status: draft, 2026-08-26; revised 2026-08-27 after the folder reorganization;
scope widened beyond heat on 2026-08-27 (§9, D6). Defines scope, branch structure, technology roster,
naming, and parameter conventions for the industrial heat technologies in this
repo. No values are recorded here — this is the specification the extraction and
YAML work follows.

Companion notes: `data/service-technology-map/README.md` (YAML entry fields) and
`technology-readiness-levels.md` (TRL definitions — the ladder this database
calls `trl-1-9`, and the authority for it);
`data/deriving capex and opex for ccs in steelmaking.md` (cost inversion method).

---

## 1. Scope

**Widened 2026-08-27 (§9, D6).** This document began as a heat-production
specification and the sections below still speak in those terms; that part is
now the *heat* portion of a whole-sector industrial technology database. Where
§§2–4 say "heat technology", read "heat technology" — those tiers, branches and
rosters are unchanged. What changed is that non-heat industrial process
technologies are no longer excluded.

**In scope:**

1. **Heat production** for industrial use, across the full temperature range —
   indirect heat (steam, hot water) and direct process heat (furnaces, kilns,
   dryers, direct electric heating), for every energy carrier (fossil fuel,
   biomass, hydrogen, electricity, solar thermal, geothermal, nuclear,
   recovered waste heat). This is what §§2–4 specify in detail.
2. **Industrial process technologies** that transform materials — ironmaking
   and steelmaking routes, clinker kilns, steam crackers and reformers,
   pulping and papermaking, electrolytic reduction — including the process
   redesigns (H2-DRI, electrolytic cement) previously excluded.
3. **Other industrial energy services** — machine drive, refrigeration and
   cooling, facility services — where a source reports them as competing
   technologies.

The grouping for everything outside heat is `sector → end-use → process-step`
in `data/harmonized/`, not the `.steam` / `.process-heat.*` branch structure of
§3, which stays as it is.

**Still out of scope:**

| Excluded | Why | Where it belongs |
| - | - | - |
| Heat distribution and steam trap / insulation efficiency | Demand-side, applies to delivered steam not generation | A separate `.steam` distribution node |
| Thermal energy storage as a standalone service | Shifts heat in time rather than producing it | Own branch; but *paired* TES-electric heating is in scope (see roster) |
| Power-only generation | Not a heat service, and the electricity supply side is modelled elsewhere | Electricity supply branches |
| Downstream fabrication and assembly | Beyond the primary material producers | Not modelled at technology detail |
| CHP | Produces both, but steam is the service being met | **In scope**, on `.steam`, with electricity as a secondary output (§9, D1) |

---

## 2. Temperature tiers

Three tiers, boundaries at **150 °C** and **400 °C**:

| Tier | Range | Rationale |
| - | - | - |
| `low-temp` | < 150 °C | The 2022 DOE Industrial Decarbonization Roadmap uses 150 °C as the low-temperature process heat boundary; it is also roughly the ceiling for commercial industrial heat pumps and the bulk of food/paper/textile demand. |
| `medium-temp` | 150 – 400 °C | Upper bound matches the NREL/GHGRP band break and the practical ceiling of industrial steam. |
| `high-temp` | > 400 °C | Matches the IEA Clean Technology Guide's "High temperature" industrial heating split and the NREL `>400°C` band. |

### Source band mismatches — must be handled, not ignored

Sources do **not** agree on these boundaries. Record the source's own band label
verbatim in the `note` field of every extracted row, and re-bin only where the
source exposes a continuous temperature.

- `nrel_2018_industrial-process-heat-demand.csv` (`data/raw-data/gov-usa/nrel/91_2018/`) uses
  `Temp_Band` values `<100°C`, `100 - 400°C`, `>400°C`. **The 100 °C break is not
  our 150 °C break.** Re-derive low vs medium from the continuous `Temp_degC`
  column; do not map `<100°C` onto `low-temp` and call it done. Note the file is
  latin-1 encoded, not UTF-8.
- IEA Clean Technology Guide (`iea_2023_clean-tech-guide.csv`) collapses low and
  medium into one "Low to medium temperature" class. Its TRLs therefore apply to
  our `low-temp` and `medium-temp` tiers jointly — flag as such, do not silently
  duplicate the TRL into both tiers as if independently sourced. Also latin-1.
- NREL 97 (`97_2018/Process_temperatures.csv`) and NREL 118
  (`118_2019/mfg_eu_temps_*`) give continuous
  `Temp_C` by unit process — these are the re-binning sources of record.

Every technology entry additionally carries its own `temperature_max` parameter
(°C, as reported), so the tier assignment can be recomputed if boundaries change.

---

## 3. Branch structure

Heat is split first by **delivery mode** (indirect via a working fluid vs direct
to the process), then — for direct heat only — by temperature tier. This mirrors
the MECS energy footprint split between `onsite generation_boilers` and
`process_heating`, which is how the demand side is measured.

```
data/service-technology-map/
  general-services/                    (dir; not itself a branch segment)
    steam/
      technology/                      branch: ".steam"
        boiler_natural-gas.yaml        (exists, empty template)
        boiler_electricity.yaml
        ...
    process-heat/
      low-temp/technology/             branch: ".process-heat.low-temp"
      medium-temp/technology/          branch: ".process-heat.medium-temp"
      high-temp/technology/            branch: ".process-heat.high-temp"
```

A branch string is the folder path with `/` replaced by `.`, skipping grouping
folders (`general-services`) and the `technology/` leaf. No character
translation is needed — folder names and branch segments are spelled
identically.

Rationale for not tiering steam: steam is a carrier, not a temperature class. A
boiler meets a demand for steam regardless of what the downstream process does
with it, and industrial steam sits almost entirely inside 150–400 °C anyway.
Steam grade (LP/MP/HP) is not distinguished: the demand side does not
differentiate it, so `.steam` stays a single branch and steam conditions are
recorded as `temperature-output` and `pressure-output` on the technology (§9, D3).

Unit: `GJ` throughout, matching the existing `boiler_natural-gas.yaml` and the
`unit` / `output` convention in `README.md`. Hot water is folded into `.steam`
for now (MECS lumps it under boilers); split it out if the demand side ever
distinguishes it.

## 4. Technology roster

TRL column is the IEA Clean Technology Guide `trl2023` value where the guide
covers the technology; `—` means no roster-level TRL source yet. "Source" names
the *best local* source for cost/performance parameters, not the only one.

### 4.1 Steam and hot water — `.steam`

| Technology | Carrier | TRL | Source |
| - | - | - | - |
| `boiler_natural-gas` | natural gas | 9 | ETSAP I01; LBNL 2021 (as `boiler_fossil`) |
| `boiler_coal` | coal | 9 | ETSAP I01 |
| `boiler_oil` | fuel oil | 9 | ETSAP I01 |
| `boiler_biomass` | solid biomass | 9 | EPA 2007 biomass CHP catalog; IEA (fluidized-bed, 9) |
| `boiler_black-liquor_recovery` | black liquor | 9 | ETSAP I07 pulp & paper |
| `boiler_biomethane` | biomethane | 9 | IEA (low-temp, 9) |
| `boiler_hydrogen` | hydrogen | 9 | IEA (low-temp, 9) — cost gap, see §7 |
| `boiler_electricity` | electricity | 8 | LBNL 2021 (extracted) |
| `boiler_electricity_tes` | electricity | — | gap — see §7 |
| `heat-pump_electricity` | electricity | 9 (6 in pulp & paper) | ETSAP E19; IEA |
| `vapour-recompressor_electricity` | electricity | — | gap |
| `solar-collector_solar` | solar | 7–9 (LFR 7, trough 9) | ETSAP E10 (CSP); IEA |
| `geothermal-well_geothermal` | geothermal | 8–9 | ETSAP E07 |
| `reactor_nuclear_smr` | nuclear | 4–8 by design | IEA (water-cooled SMR 7, HTGR 8) |
| `heat-recovery-unit_waste-heat` | recovered | 9 | DOE waste heat to power |
| `boiler_natural-gas_ccs` | natural gas + CCS | 5 | ETSAP E14; `deriving capex and opex for ccs in steelmaking.md` |
| `boiler_biomass_ccs` | biomass + CCS | 5 | IEA ("boilers fitted with CO2 capture", 5) |

CHP, on `.steam` with electricity as a secondary output (§9, D1):
`combustion-turbine_natural-gas_chp`,
`reciprocating-engine_natural-gas_chp`, `combined-cycle_natural-gas_chp`,
`steam-turbine_biomass_chp`, `gasifier_biomass_chp`. Sources: EPA 2017 CHP
catalog, EPA 2007 biomass CHP catalog (partly extracted), ETSAP E04.

### 4.2 Direct process heat — low temperature `.process-heat.low-temp` (< 150 °C)

| Technology | Carrier | TRL | Source |
| - | - | - | - |
| `direct-heater_natural-gas_low-temp` | natural gas | 9 | MECS; ETSAP I01 by analogy |
| `direct-heater_biomass_low-temp` | solid biomass | 9 | EPA 2007 catalog |
| `direct-heater_hydrogen_low-temp` | hydrogen | 9 | IEA |
| `resistance-heater_electricity_low-temp` | electricity | 9 | LBNL 2021 by analogy |
| `heat-pump_electricity_direct` | electricity | 9 | ETSAP E19 |
| `microwave-heater_electricity` | electricity | 9 | IEA |
| `radio-frequency-heater_electricity_low-temp` | electricity | 9 | IEA |
| `ultraviolet-curer_electricity` | electricity | 9 | IEA |
| `photochemical-heater_electricity_low-temp` | electricity | 9 | IEA |
| `solar-collector_solar_low-temp` | solar | 9 | ETSAP E10 |
| `heat-recovery-unit_waste-heat_direct` | recovered | 9 | DOE waste heat to power; ORNL |

### 4.3 Direct process heat — medium temperature `.process-heat.medium-temp` (150–400 °C)

| Technology | Carrier | TRL | Source |
| - | - | - | - |
| `direct-heater_natural-gas_medium-temp` | natural gas | 9 | MECS; NREL 91 unit types |
| `direct-heater_biomass_medium-temp` | solid biomass | 9 | EPA 2007 catalog |
| `direct-heater_hydrogen_medium-temp` | hydrogen | 9 | IEA (low-to-medium class) |
| `direct-heater_biomethane_medium-temp` | biomethane | 9 | IEA (low-to-medium class) |
| `resistance-heater_electricity_medium-temp` | electricity | 9 | gap for costs |
| `radio-frequency-heater_electricity_medium-temp` | electricity | 9 | IEA |
| `heat-pump_electricity_medium-temp` | electricity | 6 | IEA (pulp & paper, 6) |
| `rotary-compression-heater_electricity` | electricity | 6 | IEA (listed under high-temp) |
| `solar-collector_solar_medium-temp` | solar | 9 | ETSAP E10 |

### 4.4 Direct process heat — high temperature `.process-heat.high-temp` (> 400 °C)

| Technology | Carrier | TRL | Source |
| - | - | - | - |
| `furnace_natural-gas` | natural gas | 9 | NREL 91 unit types; sector ETSAP briefs |
| `furnace_coal` | coal | 9 | ETSAP I02, I03 |
| `kiln_petroleum-coke` | pet coke | 9 | ETSAP I03 cement |
| `furnace_biomass` | solid biomass | 9 | IEA (biomethane 9, pyrolysis 9) |
| `furnace_hydrogen` | hydrogen | 7 | IEA (high-temp, 7) |
| `furnace_ammonia` | ammonia | 5 | IEA (high-temp, 5) |
| `arc-heater_electricity` | electricity | 3 | IEA (electric/plasma arc for *heating*, 3) — distinct from EAF steelmaking, which is TRL 9 and out of scope |
| `induction-heater_electricity` | electricity | 9 | IEA (high-temp, 9) |
| `plasma-torch_electricity` | electricity | 5 | IEA (pelletization, 5) |
| `resistance-heater_electricity_high-temp` | electricity | — | gap |
| `photochemical-heater_electricity_high-temp` | electricity | 6 | IEA |
| `solar-concentrator_solar` | solar | 6 | IEA (direct heat from VRE, 6) |
| `reactor_nuclear_htgr` | nuclear | 8 | IEA (HTGR SMR, 8) |

---

## 5. Naming conventions

**One rule, everywhere — folders, filenames, technology names, branch segments,
parameter names:**

> `-` joins words within a component. `_` separates components.

`split('_')` yields components; `split('-')` yields the words inside one. Both
characters are legal on Windows and POSIX, neither is special to YAML or CSV, and
no meaning is carried by letter case — which matters because Windows filesystems
are case-insensitive. Every name in this repo is read as a string and matched
against a list, so none of them needs to be a valid Python identifier.

| Context | Form | Example |
| - | - | - |
| Folder | one component | `raw-data/`, `process-heat/low-temp/` |
| Source data file | `author_year_slug[_source]` | `epa_2007_biomass-chp-technologies-catalog.csv`, `bataille_2019_pathways-to-net-zero-industry_wires.pdf` |
| Meta sidecar | `..._meta.csv` | `epa_2007_biomass-chp-technologies-catalog_meta.csv` |

The fourth filename component is optional and names the *publication venue* —
a journal, a series, a program — where the first component alone does not
identify the document: `bataille_2019_pathways-to-net-zero-industry_wires.pdf`.
The word `meta` is reserved: it is stripped as the sidecar marker before the
components are counted, so no `source` component may be called `meta`. Note the
first component is an author code for a paper (`bataille`) and an institution
code for a report (`epa`, `lbnl`, `nrel`) — whichever is how the document is
normally cited.
| Technology name, extraction | `equipment_carrier_variant` | `combustion-turbine_landfill-gas`, `boiler_natural-gas_ccs` |
| Technology name, harmonized roster | `equipment_discriminator` | `boiler_fuel-fired`, `compressor_reciprocating-gas` |
| Technology YAML file | = the technology name | `boiler_natural-gas.yaml` |
| Branch string | = the folder path, dotted | `.process-heat.low-temp` |
| Parameter name | one component | `capacity-factor`, `temperature-output` |

**Two technology name forms (2026-09-22).** An extraction names a technology the
way its source does, equipment_carrier_variant, and those names stay on the fact
rows as roster-technology. The harmonized roster is the design technology table
(design/end-use-technology-table.csv), whose rows are named
equipment_discriminator: the carrier is not a name component there but a list on
the row, because one design technology takes many fuels, and the discriminator is
the word that tells it apart from the other rows of the same equipment. Both
forms obey the one rule above; the rest of this section describes the extraction
form.

Technology names run **general to specific**: equipment, then the carrier that
discriminates within it, then any further variant. Carrier and variant are both
optional — `microturbine` and `boiler_biomass` are as valid as
`boiler_natural-gas_ccs`.

**The slots are optional, not positional (clarified 2026-08-27).** A
two-component name's second component is read as a carrier *or* a variant,
whichever vocabulary it belongs to. This matters because many process
technologies have a variant but no carrier the source names — `blast-furnace_ccs`,
`electric-arc-furnace_efficiency-moderate`, `capture-unit_post-combustion`,
`gasifier_chp`. Forcing a placeholder carrier into the middle slot would put a
fuel where the source states none. The three vocabularies are disjoint, so
reading the middle slot by lookup is unambiguous; `design/validate-names.py`
does exactly that. A three-component name is still strictly
equipment, carrier, variant. Equipment-first also groups a roster usefully when
sorted: `combustion-turbine_biogas`, `combustion-turbine_landfill-gas` and
`combustion-turbine_natural-gas` sit together instead of scattering across the
alphabet.

Each component comes from a controlled vocabulary (§6.2). Names are globally
unique across the whole service map. Add a tier variant (`low-temp`,
`medium-temp`, `high-temp`) only when the same equipment-and-carrier pair appears
in more than one tier branch — the tier is already in the branch, so
`induction-heater_electricity` needs no suffix while
`resistance-heater_electricity_low-temp` does.

*Known inconsistency:* the LBNL extraction's `boiler_fossil` is a generic
combustion boiler the source never attributes to a fuel. Resolve it to
`boiler_natural-gas` on the way into `data/processed/`; leave the raw extraction
as the source reported it.

**The one translation in the whole project** is the extraction template's formula
column, where a parameter name becomes a formula variable — `capacity-factor` is
written `capacity_factor` inside a `formula` cell, because that expression really
is evaluated as Python. `resolve_fields` does the mapping; nothing else in the
repo translates a name.

## 6. Parameters and units

### 6.1 Extraction layer (per-source long CSV)

Columns are fixed by the marimo input template
(`data/raw-data/tech_data_input_template.py`):
`process, technology, parameter, unit, value, formula, reference, note`.
Calculation constants available to `formula`: `hours_per_year=8760`,
`GJ_per_MWh=3.6`, `GJ_per_MMBtu=1.0551`.

Standard parameters, as declared in the template's `PARAMETERS` list:
`description`, `trl`, `state-of-development` (one of: existing, commercial,
pilot, R&D, conceptual), `year-available-commercially`, `lifetime`, `capacity`,
`capacity-factor`, `annual-output`, `capex`, `opex`, `efficiency`.

*Formula variables are the one exception to §5.* A `formula` cell really is
evaluated as Python, so parameter names are translated into identifiers there:
`resolve_fields` maps hyphens (and spaces) to underscores, and a formula
referring to the parameter `capacity-factor` writes `capacity_factor`. Write
parameter names with hyphens; write formulas with underscores.

**Additional parameters for heat technologies** (custom entries until the
template's `PARAMETERS` list absorbs them):

| Parameter | Unit | Notes |
| - | - | - |
| `temperature-output` | °C | Governs tier assignment. In use in the EPA 2007 extraction |
| `temperature-min` | °C | Where the source gives a range |
| `pressure-output` | psig | In use in the EPA 2007 extraction |
| `heat-output-type` | — | `steam`, `hot-water`, `direct` |
| `energy-carrier` | — | The input carrier(s), from the §6.2 carrier vocabulary |
| `equipment` | — | From the §6.2 equipment vocabulary |
| `variant` | — | From the §6.2 variant vocabulary |
| `emissions-factor` | t/GJ | Species named in `note` |
| `efficiency-chp` | % | Overall CHP efficiency, where the source reports one |
| `heat-to-power-ratio` | — | Already a MECS footprint column |
| `cost-basis` | — | **Required with every capex.** One of `equipment`, `installed`, `total-plant`, `overnight` |
| `capacity-basis` | — | `thermal-input` or `thermal-output` |

`equipment`, `energy-carrier` and `variant` deliberately restate the three
components of the technology name. The name is a key for humans to read and for
files to be called; these fields are what anything queries. Nothing should ever
split a technology name to recover them.

The `cost-basis` flag is not optional. The existing LBNL extraction applies a
100 % equipment-to-installed markup inside the `capex` formula and records that
only in a free-text note — that is exactly the kind of assumption that silently
double-counts once several sources are pooled.

### 6.2 Controlled vocabularies

Every technology name is built from these terms. Extend the lists deliberately —
a new term is a modelling decision, not a typo fix, and the validator
(`design/validate-names.py`) fails on anything not listed here.

**Expanded 2026-08-27 for whole-sector scope (§9, D6)** — process equipment,
utility equipment, process-route variants and the efficiency-tier variants
below were added so that CIMS technologies, the UKTM sheet of the Bataille
database and the UKERC technology tables can all be named. Terms were added
because a source needed them, not speculatively.

**Equipment** — the device that produces the heat or performs the process (101 terms):

`air-separation-unit`        `anaerobic-digester`         `arc-heater`
`basic-oxygen-furnace`       `blast-furnace`              `boiler`
`calciner`                   `capture-unit`               `caster`
`chiller`                    `coke-oven`                  `combined-cycle`
`combustion-turbine`         `compressor`                 `converter`
`conveyor`                   `cooling-tower`              `crusher`
`digester`                   `direct-heater`              `distillation-column`
`dryer`                      `electric-arc-furnace`       `electrolyzer`
`electrolysis-cell`          `evaporator`                 `fan`
`fermenter`                  `flotation-cell`             `fuel-cell`
`furnace`                    `gasifier`                   `geothermal-well`
`grinding-mill`              `heat-pump`                  `heat-recovery-unit`
`induction-heater`           `kiln`                       `leaching-vessel`
`lighting`                   `melting-furnace`            `microturbine`
`microwave-heater`           `motor`                      `paper-machine`
`pellet-plant`               `photochemical-heater`       `plasma-torch`
`precalciner`                `preheater`                  `press`
`pump`                       `radio-frequency-heater`     `reactor`
`reciprocating-engine`       `refining-furnace`           `resistance-heater`
`roaster`                    `rolling-mill`               `rotary-compression-heater`
`shaft-furnace`              `sinter-plant`               `smelting-vessel`
`solar-collector`            `solar-concentrator`         `space-heater`
`steam-cracker`              `steam-reformer`             `steam-turbine`
`transesterification-unit`   `ultraviolet-curer`          `vapour-recompressor`
`ventilation-unit`           `oven`                       `pasteurizer`
`pulper`                     `cleaning-system`            `management-system`
`autothermal-reformer`       `clinker-cooler`       `process-improvement`

`adsorber`                   `annealing-furnace`          `binder`
`coating-line`               `drilling-rig`               `flare`
`fracturing-fleet`           `gas-treatment-unit`         `haul-truck`
`heat-exchanger`             `hoist`                      `liquefaction-train`
`mobile-equipment`           `paste-plant`                `photovoltaic-array`
`pickling-line`              `separator`                  `turboexpander`
`well`                       `wind-turbine`

The last twenty were added 2026-09-22 with the adoption of the design technology
table as the harmonized roster: they are the devices that table names in the
sectors it brought into scope (oil and gas, mining, on-site power, finishing
lines) and that no earlier source needed.

The management-system term is the one entry that is not a device. Sources
record organizational measures — energy management systems, preventative
maintenance, general good practice — as competing options with their own costs
and savings, and the naming convention has no other slot for them. Added
2026-08-27 for the UKERC Sector and Subsector rows; oven, pasteurizer, pulper
and cleaning-system were added in the same pass for the food, drink and paper
tables. The process-improvement term is the second non-device entry, added
2026-09-10: the Bataille pulp-and-paper sheet has an "Other production steps
(including improvement processes)" band whose rows name only an efficiency
bucket and no equipment at all, and without a term those rows parsed as an
equipment called efficiency-base.

*Prose in this section must not use backticks: the validator harvests every
backticked token after each heading into that heading's vocabulary.*

**Carrier** — the energy input (34 terms):

`ammonia`                    `benzole-and-tars`           `biogas`
`biomass`                    `biomethane`                 `black-liquor`
`blast-furnace-gas`          `coal`                       `coke`
`coke-oven-gas`              `diesel`                     `electricity`
`fossil`                     `geothermal`                 `hydrogen`
`landfill-gas`               `liquid-biomass`             `lpg`
`methanol`                   `municipal-waste`            `naphtha`
`natural-gas`                `nuclear`                    `oil`
`petroleum-coke`             `refinery-gas`               `renewable-natural-gas`
`solar`                      `steam`                      `still-gas`
`syngas`                     `waste-heat`                 `by-product-gas`
`oxyfuel-ccs`

`by-product-gas` was added 2026-09-10 as the fuel group that blast-furnace gas,
coke-oven gas, still gas and syngas collapse into (D12, R5). The four remain
listed because an extraction still records what the source printed; the group
name is what the harmonized roster uses. `oxyfuel-ccs` is listed as a carrier
only so the validator stops reporting the two extraction rows that spell it
that way; the harmonized layer moves it into the variant and folds it into the
ccs variant (D12, R6), and no new name should use it. The backticks are off
that word deliberately: this section's own rule is that prose must not use
them, and this one leak put ccs in the carrier list as well as the variant
list, which is why split_name filed it in whichever it read first.

`benzole-and-tars` and `liquid-biomass` were added 2026-08-29 for the Bataille
UKTM sheet. Benzole and tars are coking by-products burnt as fuel; both are real
carriers in UK TIMES, not catch-alls. `liquid-biomass` is separate from `biomass`
because UKTM prices the two about seven times apart, so collapsing them would
average a real distinction away.

`fossil` is deliberate: it marks a source that reports a combustion technology
without attributing it to a fuel. It should not survive into `data/processed/`.
`steam` and `still-gas` are purchased or internally recovered carriers, used
where a source treats them as the input to a competing technology.

**Variant** — any further discriminator (70 terms):

`bat`                        `ccs`                        `ccs-retrofit`
`chp`                        `direct`                     `dry`
`efficiency-base`            `efficiency-moderate`        `efficiency-strong`
`greenfield`                 `high-temp`                  `hisarna`
`htgr`                       `low-temp`                   `medium-temp`
`midrex`                     `oxyfuel`                    `post-combustion`
`pre-combustion`             `preheat`                    `recovery`
`retrofit`                   `semi-dry`                   `semi-wet`
`smr`                        `tes`                        `top-gas-recycling`
`ulcored`                    `ulcowin`                    `variable-speed`
`top-gas-recycling-ccs`      `ulcored-ccs`                `hisarna-ccs`
`wet`                        `corex`                      `corex-ccs`
`hyl`                        `tecnored`                   `tecnored-chp`
`hismelt`                    `plasma`
`long-dry`                   `lepol`                      `wet-precalciner`
`fluidized-bed`              `vertical-roller`            `high-pressure-roll`
`geopolymer`                 `bleached-dried`             `bleached-slush`
`unbleached-dried`           `unbleached-slush`           `tmp-dried`
`tmp-slush`                  `recycled-slush`             `newsprint`
`kraft-paperboard`           `back-pressure`              `condensing`
`motor-fuel`                 `lignin-extraction`          `prebake`
`prebake-no-scrubber`        `soderberg`                  `soderberg-modified`
`soderberg-vss`              `bayer`                      `anode-baking`
`secondary`                  `inert-anode`

`low-temp` / `medium-temp` / `high-temp` are used only where the tier is needed
for uniqueness; `direct` distinguishes a direct-fired unit from the steam-raising
version of the same equipment. The variant is a single component, so a compound
discriminator is spelled with a hyphen inside it — `ccs-retrofit`, not a fourth
component.

The seven named iron-making routes were added 2026-09-02 for ETSAP I02, which
costs each of them separately: corex, tecnored and hismelt are smelting
reduction processes, hyl is the HYL/Energiron direct reduction family the
brief calls Hylsa, and plasma is the plasma-heated blast furnace. corex-ccs
and tecnored-chp follow the existing compound spelling. The alternative was to
collapse them into one smelting-reduction technology, which would have averaged
a capex range of 98 to 320 USD2000 per t-yr into a single meaningless number.

Seven more followed on the same day for ETSAP I03, which prices and rates the
cement kiln types separately: long-dry, lepol, wet-precalciner and
fluidized-bed name kiln configurations the brief's own tables distinguish by
thermal energy, capacity and air flow; vertical-roller and high-pressure-roll
are the two state-of-the-art cement grinding mills; geopolymer is the
alkali-activated binder. clinker-cooler joined the equipment list in the same
pass - the grate cooler carries its own electricity, lifetime, capacity and
heat recovery efficiency, and no existing term fits a device that cools a
solid to recover its heat.

Thirteen more for ETSAP I07. Nine name a pulp or paper product, because the
brief's Table 4 gives each of them a complete and very different energy
profile: bleached-dried, bleached-slush, unbleached-dried, unbleached-slush,
tmp-dried, tmp-slush, recycled-slush, newsprint and kraft-paperboard. The
dried/slush split is the one that would hurt most to lose - 17.2 against 12.0
GJ/t for the same bleached kraft pulp, because a slush delivery to an
integrated mill skips the pulp dryer. The other four - back-pressure,
condensing, motor-fuel and lignin-extraction - name the ways the brief's Table 3
lets a kraft mill spend a steam surplus.

Nine more for ETSAP I10. prebake, prebake-no-scrubber, soderberg,
soderberg-modified and soderberg-vss name the five aluminum cell
configurations the brief's Table 1 gives separate emissions to; the scrubber
pair is kept apart because it changes SO2 by an order of magnitude, 0.88-3.5
against 10-30 kg/t. inert-anode is the emerging carbon-free cell. bayer,
anode-baking and secondary name the alumina refinery, the anode plant and the
scrap remelt furnace.

**Efficiency tiers.** `efficiency-base`, `efficiency-moderate` and
`efficiency-strong` bucket the large population of incremental efficiency
options — CIMS already names them this way ("Low Eff", "Eff", "High Eff"), and
the UKERC technology tables are largely a catalogue of them. The buckets are
technologies in their own right, carrying absolute values, not deltas against a
baseline. Boundaries, applied to energy saving against the sector's incumbent
unit:

| Variant | Energy saving vs incumbent | CIMS equivalents | UKERC examples |
| - | - | - | - |
| `efficiency-base` | 0 — the incumbent | Std, Low Eff, unqualified | the baseline column of each technology table |
| `efficiency-moderate` | up to about 15% | Eff, Med Eff, More Eff | sinter plant improved charging, reducing air leakages, increased bed depth; hot rolling lubrication systems, increased insulation, oxygen and air-flow control; EAF advanced control systems, flue gas monitoring, eccentric bottom tapping |
| `efficiency-strong` | more than about 15% | High Eff, Most Eff | coke dry quenching; sinter cooler exhaust gas heat recovery; blast furnace hot stove and slag heat recovery; EAF scrap preheat (Consteel, shaft furnace); hot charging; recuperative burners |

The threshold is a bucketing convention, not a source value. Where a source
gives a measure's own saving, that number is recorded on the technology; the
bucket only decides which technology it belongs to. Every measure rolled into a
bucket is named in that technology's note field, so nothing is lost — the bucket is
a grouping for the model, not a discard.

### 6.3 Units and currency — values stay as reported

**Rule: never convert or deflate in the raw or processed layers. Flag instead.**

- `unit` holds the source's own unit verbatim.
- Monetary values use the `YEAR_DENOMINATION` format from `README.md`:
  `2018_USD`, `2007_USD`. The existing extractions already do this.
- Conversion to a common currency happens only when a parameter enters CIMS, via
  the YAML `currency` parameter.

**Conversion method, adopted 2026-09-09 from the CIMS repository so the two
projects agree.** This REPLACED the earlier method (convert at the source year's
exchange rate, then deflate with Canadian CPI); the two differ by about 3% on a
2000_USD value, so factors built before that date are not comparable with
factors built after it.

    factor(YYYY_XXX to 2025_CAD)
        = deflator[XXX][2025] / deflator[XXX][YYYY]     deflate, inside XXX
          x exchange[CAD_per_XXX][2025]                 then exchange, at 2025

Deflate first, within the SOURCE currency, then exchange at the TARGET year's
rate. Rebasing inside the source currency with that country's GDP deflator at
market prices keeps the estimate's real meaning against the price level of the
output it was measured in, and stops one country's inflation being mixed with
another's; the exchange step then moves a real value across currencies, so time
effects and space effects stay separate. The GDP deflator is the right index
here, not CPI: these are producer capital and operating costs, not a consumer
basket.

**The factor is not symmetric, and must never be chained or reversed.**
Converting 2010_USD to 2025_CAD and back does not return the original number,
because the two directions deflate in different currencies and exchange in
different years. Convert once, from the currency the estimate was published in.

`data/harmonized/build-currency.py` implements this against two reference tables
copied verbatim from the CIMS repository - `reference-currency-deflator.csv` and
`reference-currency-exchange.csv` - and emits a factor for every currency-year
that actually appears in the database, discovered from the data rather than
hard-coded. Coverage is 2000-2025 for CAD, USD, GBP, EUR, JPY, INR and CNY; a
year or currency outside that is reported and left unconverted, never
approximated. The twelve factors in use were checked against
`CIMS.unit_conversion.CurrencyConverter` itself and agree to nine decimal
places. The retired CPI-based tables are in `data/raw-data/superseded/`.
- Do the same for discount rates: replicate the source study's CRF when inverting
  a levelized cost, and apply the CIMS behavioural hurdle rate only afterwards.
  See `deriving capex and opex for ccs in steelmaking.md` — doing both at once
  double-counts.

### 6.4 CIMS YAML layer

The YAML parameter set is fixed by `service-technology-map/README.md`, and now
follows §5 like everything else. Mapping from extraction:

| Extracted | YAML parameter | Note |
| - | - | - |
| `capex` | `fcc` | Must be in the currency named by the `currency` parameter |
| `opex` | `fom` | |
| `lifetime` | `lifetime` | |
| `capacity` × `capacity-factor` × 8760 | `output` | In GJ, matching the branch unit |
| `year-available-commercially` | `available` | |
| `efficiency` | `service-request` | Carrier input per GJ of heat = 1 / efficiency; one `service-request` block per input carrier |
| `emissions-factor` | `emissions` / `emissions-biomass` / `emissions-removal` | Biogenic and captured streams go to the separate parameters |
| `trl`, `state-of-development` | (no direct field) | Record in `note`; they justify the `available` year and any `market-share-new-max` ramp |

For pre-commercial technologies, `available` is a modelling judgement, not a
source value: set it from TRL with the rule recorded in `note` rather than
leaving it to the default. **The rule (§9, D5):** TRL 9 → available now;
TRL 7–8 → +5 years; TRL 5–6 → +10 years; TRL ≤ 4 → +15 years or unavailable.
Record the TRL and the resulting year in `note` for every entry that uses it, so
the judgement is visible rather than implied.

---

## 7. Data pipeline and current coverage

```
data/raw-data/<publisher>/          original documents (PDF, XLSX), registered
                                    in raw-data/source-details_sources.csv
        |  manual extraction via raw-data/tech_data_input_template.py (marimo)
        v
data/raw-data/<publisher>/<pub>_<year>_<slug>.csv  + _meta.csv
        |  harmonize names, resolve duplicates, add tier + basis flags
        v
data/processed/heat_technologies.csv     <-- does not exist yet
        |  referenced by YAML value_type: "csv"
        v
data/service-technology-map/general-services/.../technology/*.yaml
```

`data/processed/` is referenced in `README.md` but has not been created. It is
the missing link for every `value_type: "csv"` entry.

Every source belongs in `raw-data/source-details_sources.csv`: a row there
(`source_id`, author, institution, title, year, licence) and one row per file in
`files` (`source_id`, `file_name`, `file_path`, `file_source` URL,
`date_accessed`, `csv_data_extract`). The manifest, not the folder tree, is the
record of provenance — keep it current when files move.

### Extraction status

*Superseded by project memory `extraction_progress.md`, which is kept current.
The table below is the position as of the folder reorganization and is retained
for the source list, not the status column. Note that this environment has no
network access, so following citations to download originals is not possible —
see §9, D7.*

| Source | Location | Status |
| - | - | - |
| LBNL 2021 Electrification of Boilers | `gov-usa/lbnl/` | Extracted — 2 techs. `annual-output` unit bug fixed 2026-08-27; parameter names hyphenated |
| EPA 2007 Biomass CHP Catalog | `gov-usa/epa/` | Extracted — 10 techs (boiler, gasifier, steam turbine, 3 combustion turbines, ICE, microturbine, fuel cell). Citation restored; parameter names hyphenated |
| EPA 2017 CHP Catalog | `gov-usa/epa/` | **Not extracted** — the earlier CSV was LBNL content mis-filed here and has been removed. Only the PDF remains. Unblocked by D1; now the next extraction after ETSAP I01 |
| ETSAP I01 Industrial Combustion Boilers | `iea/etsap/` | Not extracted — highest priority, anchors the whole steam branch |
| ETSAP E19 Heat Pumps, E10 CSP, E07 Geothermal, E04 CHP, E14 CCS, E05 Biomass, I07 Pulp & Paper | `iea/etsap/` | Not extracted |
| IEA 2023 Clean Technology Guide | `iea/iea_2023_clean-tech-guide.csv` | Raw CSV present; TRLs used in §4, no cost data in source. Registered in the manifest as `iea_2026_002` — year mismatch |
| NREL 91 / 97 / 118 | `gov-usa/nrel/91_2018`, `97_2018`, `118_2019` | Raw present — demand-side, used for tier binning not tech parameters |
| DOE 2022 Industrial Decarbonization Roadmap | `gov-usa/doe/` | Not extracted — narrative, few hard numbers |
| UKERC Usable Energy Database | `other-reports/ukerc_2013_usable-energy-database.xlsx` | Not extracted — `Steam Table` has lifetimes and applicability shares, plus per-industry technology tables. UK basis |
| RTC Renewable Thermal Vision | `other-reports/rtc_2023_renewable-thermal-vision.pdf` | Not extracted — now the full report, not the 2-pager |
| CAELP/E3 Decarbonizing Industrial Heat | `other-reports/caelp-e3_2024_decarbonizing-industrial-heat.pdf` | Not extracted |
| Bataille 2017 heavy industry database | `other-reports/` | Not extracted |
| MECS energy footprint | `gov-usa/eia/mecs/` | Processed — demand-side structure and efficiency/boiler shares |

### Known parameter gaps (no local source)

`boiler_electricity_tes`, `vapour-recompressor_electricity`,
`resistance-heater_electricity_high-temp`, `boiler_hydrogen` and `hydrogen-direct-heater-*`
costs, `rotary-compression-heater_electricity`. These need external sources; do not fill them
with proxies without a `source` note saying so.

---

## 8. Data integrity issues

Resolved: `raw_data_heat/` folded into the publisher tree and its duplicates
removed; files renamed to `publisher_year_slug`; ETSAP moved under `iea/etsap/`;
background-only documents separated into `background-no-data-extracted/`. Then
on 2026-08-27: the mis-filed `epa_2017_chp-technologies-catalog.csv` (which held
LBNL content under an EPA citation) removed; EPA 2007 and LBNL citations
restored; the LBNL `annual-output` unit bug corrected to 1,857,470 GJ; formulas
stored without the leading `=`, so Excel no longer evaluates them into `#NAME?`;
the LBNL `state-of-development` value corrected from `commcercial` to
`commercial`; and the LBNL `boiler_electricity` efficiency reference corrected
from page 41 to page 2, where the source gives "95-99 % efficiency" against
"70-80 %" for combustion boilers. Then the naming pass of §5 applied across the
whole repo — folders, files, technology names, branch strings, parameter names,
the template's `PARAMETERS` list, and this document's roster; then the CIMS YAML
layer, converting `service-technology-map/README.md` and all five technology
YAMLs (`value-type`, `sub-context`, `by-year`, `by-region`, `service-request`,
`emissions-biomass`, `emissions-removal`, `market-share-*`, `capital-recovery`,
`service-provide`) together with the branch references and paths held inside
their values. Currency and unit values (`2015_CAD`, `k_pkm`) keep their
underscore, which is the component separator doing its job.

Open, in rough priority order:

1. **Manifest drift — deferred deliberately.** To be reconciled in one pass once
   more sources have been added, rather than piecemeal. In
   `raw-data/source-details_files.csv`: it uses
   `nrel_2018_001` where `sources` has `nlr_2018_001`, so that join fails. Five
   `file_path` values point at directories that no longer exist, and they now
   carry the old underscore spellings as well
   (`raw_data/cer/energy_commodities`, `raw_data/nrcan`, `raw_data/iea/etp`,
   `raw_data/iea/clean_tech_guide`, `raw_data/gov_usa/eia/nems`); one row has a
   date in the path column. Unregistered entirely: `gov-usa/epa`, `gov-usa/doe`,
   `gov-usa/nrel/*`, `iea/etsap` (66 files), `other-reports`, `ceedc`,
   `gov-can/eccc`, and `background-no-data-extracted`. Only the MECS year
   folders, `gov-usa/lbnl` and `peer-reviewed` still resolve. The IEA clean tech
   guide file is `iea_2023_clean-tech-guide.csv` but registered as
   `iea_2026_002`. The manifest is the only thing in the repo the naming passes
   did not touch — every `file_path` in it needs rewriting to the new folder
   spellings, and it has no column for the optional fourth filename component.

2. **Carrier unassigned on three EPA 2007 technologies.** `reciprocating-engine`,
   `microturbine` and `fuel-cell` were left as single-component names because the
   source names no carrier for them, though each row's note says "syngas from
   thermal gasification". Fill the carrier in from the source rather than
   inferring it, then extend the names.

3. **Upstream-original filenames.** 205 files keep their publisher's own names
   (the MECS tables, the CER exports, the ETSAP briefs, the NREL bulk data).
   Keeping them aids traceability and the manifest has a `file_original_name`
   column for it; the validator skips them by directory and reports the count.
   One file falls outside that scheme and needs a decision:
   `gov-usa/lbnl/201-003-044_IND_CCRD_PublicRev59_20221220.xlsm`, the NETL CCRD
   workbook. `data/deriving capex and opex for ccs in steelmaking.md` cites it by
   this exact path, so renaming it means updating that note in the same commit.

4. **Still no version control.** `git init` before the roster fills out — every
   issue above is a silent-drift problem that a diff would have surfaced.

Run `python design/validate-names.py` from the repo root after any renaming; it
checks technology names against §6.2, source filenames against
`publisher_year_slug`, branch strings against the folder tree, and parameter
names against the template.

---

## 9. Decisions

Settled 2026-08-27. Recorded here with their consequences; the body of this
document already reflects them.

**D1 — CHP sits on `.steam`.** A CHP unit is modelled on the steam branch with
electricity as a secondary output, not on the electricity supply branch and not
duplicated under an allocation rule. Steam is the service being met; the power is
a co-product. Consequence: the five CHP technologies in §4.1 are in scope, and
the EPA 2017 CHP Catalog extraction is unblocked. Each CHP entry needs
`heat-to-power-ratio` and `efficiency-chp` alongside the ordinary parameters, and
the electricity co-product recorded so it is not double-counted against the
electricity supply branch.

**D2 — Costs are used as reported, flagged, never adjusted.** No Canada
adjustment factor at any stage of the pipeline. Every monetary value carries its
`YEAR_DENOMINATION` flag (`2018_USD`, `2007_USD`, `2015_CAD`) and conversion
happens only where the parameter enters CIMS, via the YAML `currency` parameter.
Consequence: US and UK sources are usable as-is; §6.3 is the operative rule and
needs no regional caveat.

**D3 — Steam grade is not distinguished.** The demand side does not differentiate
LP / MP / HP steam, so `.steam` stays a single branch rather than splitting into
pressure sub-branches. Consequence: the roster does not triple; steam conditions
are carried as `temperature-output` and `pressure-output` parameters on the
technology, as the EPA 2007 extraction already does for `boiler_biomass`.

**D4 — Retrofit and greenfield are documented as separate technologies.** Where a
technology can be either built new or retrofitted onto existing plant — fuel
switching, CCS — record both rather than averaging them, since their capital
costs differ sharply. Use the `retrofit` and `greenfield` variants; because the
variant is a single component, compounds are hyphenated inside it, so a retrofit
CCS boiler is `boiler_natural-gas_ccs-retrofit` against
`boiler_natural-gas_ccs`. Leave the variant off where the distinction does not
apply. *Open sub-question:* how retrofits are integrated into CIMS — as competing
technologies, as a stock-turnover constraint, or as a cost adjustment on the
existing stock — is still being considered. Documenting both options now keeps
that decision cheap later, and is the only part of these five that is not
finished.

**D6 — Scope widened from heat production to whole-sector industrial
technologies (2026-08-27).** The original scope covered heat production only,
and pushed process redesign — H2-DRI, electrolytic cement — to sector branches
that were never built. Three of the sources now being extracted (the UKERC
Usable Energy Database, the UKTM sheet of the Bataille database, IPCC AR6 WGIII
Chapter 11) are whole-sector by construction, and filtering them down to heat
would have discarded most of their content and left the process technologies
with nowhere to live. Consequence: §1 is rewritten above; the
`material-preparation`, `material-conversion`, `forming-and-finishing`,
`electrochemical`, `machine-drive` and `refrigeration-and-cooling` end uses in
`data/harmonized/end-use.csv` become live; and the §6.2 equipment and variant
vocabularies must grow to cover process equipment. Vocabulary terms are added
*as a source requires them*, not speculatively, and every addition is listed in
§6.2 — a new term remains a modelling decision. The heat sections (§§2–4) are
unaffected: tiers, the `.steam` / `.process-heat.*` branch structure and the
heat roster all stand.

**D7 — Two-level source attribution (2026-08-27).** UKERC and the Bataille
database are compilations: their rows cite originals (IEA GHG 2013b, Worrell et
al. 1999, CE Delft 2010) that are not held locally and cannot be downloaded from
this environment. Rather than crediting the compilation for numbers it did not
generate, the harmonized fact tables carry `source-id` for the *original* cited
source and `via-source-id` for the compilation actually read, with
`via-locator` giving the row or cell. Consequence: originals appear in the
manifest as registered-but-unheld sources; a prioritized list of documents worth
obtaining is maintained at `data/harmonized/download-wishlist.md`.

**D8 — Three rules on the shape of the harmonized roster (2026-08-27).**
(a) *Every technology is standalone.* `baseline-technology` stays blank and each
row carries absolute values; an innovation is not stored as a delta against a
baseline it points at. (b) *Incremental efficiency options are bucketed* into
the `efficiency-base` / `efficiency-moderate` / `efficiency-strong` variants of
§6.2, with the specific measures rolled into each bucket named in that
technology's note field. CIMS already names technologies this way and the UKERC
tables are largely a catalogue of such measures; carrying all ~190 of them
separately would swamp the roster without changing any model result. (c)
*Placeholders are written, not omitted.* A technology a source names as relevant
but does not quantify gets `status = placeholder` and no fact rows, so the gap
is visible in the roster rather than absent from it.

**D9 — CIMS is the spine of the roster (2026-08-27).** Every CIMS technology
that is retained must appear in the database, so the CIMS model inputs are
mapped in first and the source extractions attach to that skeleton. The mapping
is a rules engine (`data/harmonized/build-cims-map.py`), not a hand list, so it
is reproducible and every judgement is inspectable. Consequence: the roster
inherits CIMS's service names as `process-step`, which preserves the size
classes CIMS models as separate nodes; and the rename / merge / remove advice
falls out of the same map as `data/harmonized/cims-review.md`.

**Open question on D4, raised 2026-08-27.** Whether a name may carry more than
one variant *component* — `blast-furnace_top-gas-recycling_ccs` — instead of
hyphenating them into one, as D4 requires. Separate components would make each
variant filterable by exact match rather than by substring, and would fold
`ccs-retrofit` into `ccs_retrofit`. It would also mean a name is equipment, an
optional carrier, then one or more variants, each identified by vocabulary
lookup rather than by position — a further step in the direction §5 already
took. Deferred: the compound form stands until the database has been reviewed.
Roughly 40 names across the CIMS and UKERC rosters would change.

**D5 — The TRL availability rule stands.** TRL 9 → available now; TRL 7–8 → +5
years; TRL 5–6 → +10 years; TRL ≤ 4 → +15 years or unavailable. Applied when
setting the YAML `available` parameter, with the TRL and resulting year recorded
in `note`. See §6.4.

**D5a — One readiness column, with the crosswalk as data.** Settled 2026-08-29.
Sources report readiness on different scales — IPCC AR6 Table 11.3 names the
NASA 1–9 ladder, the IEA ETP Clean Energy Technology Guide uses the ETP scale —
and for a while the database kept each source's number as printed, with a
`trl-scale` column saying which ladder it was on. That made `trl` unsortable and
unusable in a comparison view, and D5 above needs one number.

`technology.trl` is now a single value on the **common 1–9 ladder**, mapped
through `data/harmonized/trl-scale-map.csv`. The crosswalk is a table, not a
rule in code, and it carries each level's definition with its provenance.

**The common ladder is `trl-1-9`: the one already defined in
`data/service-technology-map/technology-readiness-levels.md`**, which this
database now treats as the authority. It was briefly labelled `nasa-1-9`, which
was wrong — that file is the EU/Horizon wording ("industrially relevant
environment in the case of key enabling technologies" on 5–6, "competitive
manufacturing … or in space" on 9), and NASA's own text differs at several
rungs. The two are numerically identical, so nothing remaps; only the name was
inaccurate.

That file also supplies something the generic labels do not, and it is the
reason it is the authority rather than a convenience: an **industrial-process
reading of each level**, carried in the map's `definition-industrial-process`
column. TRL 6 is a pilot at 1/100th of commercial scale with engineering-scale
equivalents of every operation; TRL 7 is that pilot run continuously over a
relevant timeframe; TRL 8 is a demonstration plant at 1/10th scale operated
outside normal parameters; TRL 9 is a commercial plant across the full range of
operating conditions. For a DRI route or a cement kiln that is decidable where
"demonstrated in a relevant environment" is not, and it is what should govern
both how a reader reads `trl` and how D5 above turns a level into a year.

**A scale label is only applied where a source names one.** IPCC AR6 Table 11.3
heads its column "NASA TRL", so its 25 values are recorded as `nasa-1-9` and
mapped across (identity). The IEA guide's 42 are `iea-etp`. UKERC, Bataille and
the technology-brief extractions print a plain 1–9 and never claim a scale, so
their 112 values are recorded as `trl-1-9` directly rather than being
attributed to NASA, which they do not claim to be.

Three things the mapping has to get right, all of them real in the data:
- **A range is carried at its lower bound.** IPCC prints `6–7`, `3–6`, `6–9`;
  the lower bound is the conservative reading and does not overstate how far a
  technology has got. `trl-as-reported` keeps the range.
- **A rung is not always a number.** ETP charts subdivide level 9 into 9A / 9B /
  9C for market uptake; all three map to 9. The Guide itself does not use the
  subdivision and reports a plain 9 — an earlier note in this repo that the IEA
  scale "runs to 11" was wrong, and all three ladders agree rung for rung at
  1–9.
- **Two sources disagreeing is not a scale problem.** Where both have mapped to
  the common ladder and still differ, the better-ranked source in
  `source-priority.csv` wins — the same order the wide views use to pick a
  central estimate — and the loser's value goes in the note. Resolving by load
  order would make the answer depend on the order of blocks in `populate.py`.
  34 technologies are currently in this state.

Consequence: `trl` is comparable and appears in the wide views;
`trl-as-reported` and `trl-scale` stay on the roster row so the mapping can be
audited without re-reading the source.

**D10 — A technology may be applied to many sectors.** Settled 2026-08-29. A
technology is one thing wherever it is installed: a natural gas dryer is the
same dryer in food and in chemicals, and its cost and efficiency do not change
because of the fence around the site. The roster therefore holds each technology
**once**, and a link table `technology-application` records every service node it
serves — one row per (technology, service node), carrying the sector, end use and
process step for reading.

The alternative, keying the roster on (sector, technology), was rejected: it
would repeat one technology's parameters across up to nine rows, so a correction
would have to be made nine times and could be made inconsistently.

Consequence: `technology.csv` no longer carries a `service-node` column, and
anything that needs a technology's sector joins through `technology-application`.
The wide views show a technology under each sector it serves — the same idiom the
source list already uses, where a source used in several sectors appears under
each. 424 technologies currently hold 1,216 applications; 142 of them serve more
than one sector and the widest serve nine.

What forced it: before this, `add_tech` kept the first service node that claimed
a technology and wrote every later one into a note as prose. Loading Bataille's
UKTM sheet, where the same CHP unit and the same dryer appear under six or seven
sectors, put `combined-cycle_natural-gas_chp` on a **mining** node because an
unrelated extraction happened to register it first. The sector attribution was
arbitrary and the data was in a note where nothing could read it.

**D11 — The roster is aggregated, and `aggregate.py` is where that happens.**
Settled 2026-09-10. The roster had reached 506 technologies over 1,365
applications, past the point where a reader could hold it in view, so four
rules generalize it. They live in `data/harmonized/aggregate.py`, applied by
`populate.py`, and the full effect of each run is written to
`data/harmonized/aggregation-review.md`.

- **R1 — the `all-industry` sector is renamed `cross-sector`,** and sorts first
  in the sector vocabulary so the shared services head the wide views.
- **R2 — the generic end uses are held once, on `cross-sector`.** Machine
  drive, facility services (lighting, space conditioning, ventilation),
  refrigeration and cooling, and steam and hot water including CHP are the
  same equipment wherever they are installed, and repeating them under every
  sector added 419 applications that said nothing a reader did not already
  know: machine drive alone held 218 applications of 21 technologies. The
  sectors and process steps the sources reported are kept in
  `reported-sectors` and `reported-steps` on the application row, so the
  collapse is reversible without re-extracting.
- **R3 — `other-services` is retired.** Its own definition called it a residual
  for balancing a sector's energy total, but it had become the default landing
  place for anything a source did not label, holding 121 technologies including
  blast furnaces, kilns, electric arc furnaces and steam crackers. Each is
  reassigned to the end use that the same technology, or the same equipment in
  the same sector, already has; a short hand map in `aggregate.py` covers the
  equipment with no evidence either way. The four flat extractions that used to
  default to it are boiler and CHP catalogues and now default to
  `steam-and-hot-water`.
- **R4 — names generalize, sources aggregate.** The carrier is dropped from an
  efficiency-bucket variant, because a bucket is a set of measures and not a
  fuel-specific device: `dryer_coal_efficiency-base` and
  `dryer_natural-gas_efficiency-base` are one unimproved dryer, and the carrier
  survives on the fact rows. A temperature-tier suffix is dropped because the
  end use already carries the tier — the application at that tier is kept, so
  the roster still offers a gas heater at medium temperature. A bare equipment
  name whose only other form is its `_electricity` form is the same device
  named twice by two sources.

**Nothing is discarded on a merge.** `tech-parameter`, `tech-flow` and
`tech-constraint` are unchanged in length and re-pointed at the general name, so
an aggregated technology carries every contributing source's rows side by side,
told apart by `source-id` and ranked by `source-priority.csv`. The source names
that collapsed into each general name are listed in the roster's
`aggregated-from` column. Where two roster rows gave different values for the
same field, the survivor's value is kept and the other is recorded in its note.

Result: 415 technologies over 795 applications and 191 service nodes, from 506
over 1,365 and 402.

A consequence worth its own note: splitting a name into equipment, carrier and
variant by POSITION was wrong, and the collapse made it visible. The carrier is
optional, so the second component is a carrier in `boiler_natural-gas` and a
variant in `boiler_ccs`; 129 roster rows had ccs, oxyfuel, hisarna and every
efficiency bucket sitting in the `energy-carrier` column. `aggregate.split_name`
now decides from the §6.2 vocabularies instead, leaving only the two
`oxyfuel-ccs` names that the validator already reports as an unlisted compound
variant.

**D12 — Fuel groups, one capture variant, and a status for the unquantified.**
Settled 2026-09-10, extending D11 after the roster was still crowded: 29 boiler
entries in `cross-sector` alone.

- **R5 — carriers collapse into fuel groups** where they behave the same as a
  source of heat: `lpg` into `natural-gas`, `liquid-biomass` into `biomass`,
  `landfill-gas` into `biogas`, `naphtha` and `benzole-and-tars` into `oil`,
  `petroleum-coke` into `coal`, and blast-furnace gas, coke-oven gas, still gas
  and syngas into a new `by-product-gas`. **The grouping is deliberately
  conservative**, because this database has to describe the plant stock that
  exists as well as the options that might replace it. Merges that were costed
  and rejected on that ground: `coke` into `coal` (in a blast furnace coke is
  the reductant, not a fuel); `black-liquor` into `biomass` (the recovery
  boiler is the defining unit of a kraft mill); `ammonia` and `methanol` into a
  fuel group (on a reformer or reactor these name the product, so the merge
  would rename the process); `steam` into `waste-heat` (purchased or site steam
  is not recovered heat and the cost basis differs); and `biogas`,
  `biomethane` and `municipal-waste` into `biomass` (different carbon
  intensity, different treatment under a clean fuel standard). Those six
  exceptions cost about six roster entries and are worth it.
- **R6 — one `ccs` variant.** `post-combustion`, `oxyfuel` and `oxyfuel-ccs`
  fold into `ccs`: how the CO2 is caught is a plant-engineering choice, not a
  technology the model picks between. **The process routes that end in `-ccs`
  are not in this set** — `hisarna-ccs`, `corex-ccs`, `ulcored-ccs` and
  `top-gas-recycling-ccs` are the alternative ironmaking routes the model
  exists to choose between, and folding them into a generic `ccs` would gut it.
- **R7 — `status = unquantified`.** 153 roster entries are named by the CIMS
  roster or by a source's own list and carry no parameter, flow or constraint
  row. They are not `placeholder`, which means the design document declared the
  technology in scope and no source has been extracted yet; these were offered
  by a source that then said nothing measurable. **They stay in the roster** —
  the CIMS names among them are what `cims-map.csv` points at, so deleting them
  would break D9 — but the wide views leave them out. The roster then says what
  the database has been asked to cover and the view says what it knows, and the
  gap is a number either can report.

The wide views filter on the presence of fact rows rather than on the status
column, so the view cannot drift from what `populate.py` labelled.

Result: **387 technologies** (217 draft, 153 unquantified, 17 placeholder) over
759 applications; the wide view is **377 rows**, from 653. Boilers go from 29 to
22 in the roster and 15 in the view.

**Not adopted (2026-09-10):** a stricter archetype schema that would have folded
`efficiency-moderate` and `efficiency-strong` into one `efficient` variant and
dropped the legacy plant sub-types — `kiln_wet`, `kiln_lepol`, `kiln_semi-wet`,
`kiln_long-dry`, the Soderberg and prebake pot lines, the pulp slush and dried
grades. It would have reached about 172 technologies. Rejected because the
database is meant to cover **existing** technologies as well as future
decarbonization options, and those sub-types are what the existing stock is
made of. Do not propose it again without that scope changing.

**D13 — What the wide view shows, and the bases behind it.** Settled
2026-09-10 over a review of the `wide-technology` sheet. The full queue of
comments, with the reasoning and the options rejected, is in
`data/harmonized/wide-view-review.md`.

- **Costs are per unit of the technology's OWN output** — a tonne for a process
  technology, a GJ for an energy service — as one column per cost parameter,
  read against `product-unit`. This reversed `to_common_basis`, which used to
  manufacture a GJ denominator by dividing a per-tonne rate by
  `specific-energy-consumption`, i.e. final energy INPUT per tonne, while the
  absolute and per-kW routes divided by annual OUTPUT. One column therefore
  mixed cost per GJ of input with cost per GJ of output, quantities that differ
  by the efficiency, and 84 of the 86 populated cells were the input kind while
  the code claimed the output kind. Converting the input ones was impossible:
  of the 49 technologies on that route, one carries an efficiency. Dropping the
  division fixes it and is more faithful — 262 of the 784 cost rows say
  per-tonne natively.
- **`capex-total` and `reference-capacity.csv` are gone.** The total was a
  derived column only, never a stored parameter, and every capacity cell in the
  table it depended on was blank, so the route never once fired. With costs
  held per unit of output the total is not a step in the harmonization. The
  table is archived under `data/raw-data/superseded/`.
- **Emissions are scope 1 and four parameters:** `emissions-combustion`,
  `emissions-process`, `emissions-total`, `emissions-captured`.
  `emissions-indirect` is dropped entirely — the model prices grid electricity
  itself. **Species stay explicit in `target` and are NOT converted to CO2e**:
  `co2`, `co2e` and `pfc` are carried as reported, because an explicit species
  is worth more columns than a converted one, and it avoids choosing a GWP set
  and a CF4/C2F6 split. Non-GHG species — nox, so2, pm, total-fluoride, hf,
  pah — are out of scope and deleted. `emissions-total` exists because ETSAP
  I03 reports cement emissions as fuel plus calcination together; recording
  that on the combustion term double-counted what `emissions-process` already
  held.
- **One row per (technology, sector, end use)**, process steps joined into one
  cell; **technologies alphabetical within each end-use band**; `_min` / `_max`
  written only where the values behind the cell actually spread, and empty
  pairs dropped; Excel number formats chosen per cell from the value's own
  magnitude, with `year-available` and `trl` as plain integers.
- **`technology-label` and `status` are out of the view.** The label carried
  only the first CIMS name that claimed a technology, chosen by load order,
  where up to 29 stood behind it; CIMS names live in `cims-map.csv` until CIMS
  is properly connected. `status` read `draft` on every row because the view
  already filters `placeholder` and `unquantified` out.
- **Units collapse onto one column per quantity where, and only where, the
  denominator is genuinely the same.** `specific-energy-consumption` is GJ/t
  with a `__gj-unit` residual for the £k, m3 and GJ-denominated rows; capacity
  folds kW into MW and t/d into kt/yr at **365 operating days**, a nameplate
  rating that `capacity-factor` derates separately; `COP` folds into
  `efficiency` at x100. Emissions are deliberately NOT collapsed this way — a
  unit difference there can hide a scope difference.

**Two rules the review established that outlive it.** A cost or efficiency
column must not be sorted, averaged or charted **across end-use bands**: within
a band the unit and the basis are effectively constant, across bands they are
not. And **two units must never share a column by accident** — `build-wide.py`
now falls back to the unit suffix on a name collision, after `opex-variable`
appeared twice in the header with both copies reading the same cell, silently
overwriting one unit's values with the other's.
