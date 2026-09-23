# Design

The rules the database follows. The reasoning behind each rule is in the dated
records in `archive/decisions/`, indexed in [decisions.md](decisions.md). This page
states the rules only.

---

## 1. Scope

- **In scope:**
  - industrial technologies that provide an end use in the CIMS hierarchy:
    - heat supply at every temperature and for every energy carrier;
    - the process technologies that transform materials;
    - machine drive, refrigeration, space conditioning and lighting;
    - on-site power generation, including power-only;
    - mobile equipment at industrial sites;
    - CO2 capture and direct air capture;
    - methane venting, flaring and fugitive controls;
    - water and effluent handling.
  - Existing stock and future options both. A legacy type is included while it is
    still in Canadian stock.
  - Prospective options generally at TRL 5–6 or higher.
- **Out of scope:**
  - heat distribution and steam-trap efficiency;
  - downstream fabrication and assembly;
  - residential, commercial and transport end uses;
  - non-GHG pollutants.
- **Scope 1 only.** Purchased electricity is priced by the model, not by the database.

## 2. Archetypes and examples

An **archetype** is a technology option a model chooses between. It provides one or
more end uses. An **example** is one technology as one source presents it, in one of
that source's own contexts (a process or table band). Every example belongs to one
archetype, or is marked `(none)`, deliberately out of scope.

**A new archetype needs one of these:**

- energy use differing by roughly 15% or more from its nearest archetype;
- emissions that differ in kind, or in how they are abated;
- a legacy type that is still in Canadian stock.

Otherwise it is an example of an existing archetype. Size classes, vintages, regions,
vendor designs and product names are never archetypes.

**Carriers.**
- Carriers are a list on the archetype, not a separate archetype.
- The exception is a carrier that changes the equipment itself: a solid-fuel
  boiler, an electrode boiler, a heat pump.
- Differences between carriers on one archetype show up as the range of its values.

**Efficiency.**
- Incremental measures on one device are bucketed into two modifiers:
  `efficiency-moderate` (up to about 15% saving) and `efficiency-strong` (more).
- The measures in a bucket are named in the archetype's `examples-named`.
- An option a model would choose in its own right is an archetype, not a bucket:
  a condensing boiler, a shoe press, a heat-pump dryer, a variable-speed drive.

**Capture.**
- A host that can carry CO2 capture gets its own archetype with a capture modifier:
  `ccs-concentrated` or `ccs-diffuse`.
- That archetype holds host-side facts only: regeneration steam, the capture rate
  the host can reach.
- The capture plant itself is a `capture-unit` archetype serving the matching
  `service.ccs.*` node.
- A route that concentrates its own stream keeps its archetype: oxy-fuel kilns,
  top-gas recycling, bath smelting.

**Standalone values.** Every archetype carries absolute values. None is stored as
a delta against a baseline. A negative cost is a saving against a baseline and is
not pooled. An efficiency measure's cost (the cost of adding it to a plant) pools
only as a **whole-plant cost**: the host plant's cost from the same source plus the
measure's. `records/reference/ukerc-host-baseline.csv` names which archetype is
which UKERC host step. A measure whose source gives no host cost is set aside
(`set-aside = needs-host-cost`, listed in `output/set-aside-host-cost.csv`).

## 3. Naming

**The one rule, everywhere:** `-` joins words within a component; `_` separates
components. Folders, files, archetype keys, parameters and branch segments all
follow it.

**Archetype key:** `equipment[_discriminator][_modifier...]`

| Part | Rule | Vocabulary |
| - | - | - |
| equipment | One term, always present. Closed list. | `records/vocabulary/equipment.csv` |
| discriminator | At most one component: the single distinction that makes this a different option, such as a route or operating principle. Each term is listed with a one-line definition. | `records/vocabulary/discriminator.csv` |
| modifier | Zero or more, in the fixed order: `efficiency-moderate`, `efficiency-strong`, `ccs-concentrated`, `ccs-diffuse`, `retrofit`. | `records/vocabulary/modifier.csv` |

Examples: `boiler_fuel-fired`, `kiln_dry-precalciner_efficiency-moderate`,
`blast-furnace_top-gas-recycling`, `steam-reformer_methane_ccs-concentrated`.

**Never in a key:**
- a carrier, unless it changes the equipment;
- a size class, vintage, region or product name;
- a temperature tier.

**`label`** is the human-readable name beside the key ("Heat-pump dryer").

**Extraction names** keep the form the extractor gave them,
`equipment_carrier_variant`, using the terms in
`data/raw-data/extraction-vocabulary.csv`. They are the example's name
(`source-technology`) and are never renamed to fit the database.

**Source files** are named `author_year_slug[_source]`. A `_meta` sidecar marker is
stripped before the components are counted.

**Parameters** are one component: `capacity-factor`, `emissions-process`. Currency
and unit values keep `_` as their separator: `2013_GBP`.

## 4. Services: the CIMS hierarchy

**The hierarchy.**
- `records/cims_hierarchy.csv` is the definitive list of services and end uses.
- Replace the file with the latest copy whenever it changes.
- The build stamps the snapshot it used, reports the nodes added and removed since
  the last build, and fails on any record pointing at a path the snapshot lacks.
- Changes the database needs from the hierarchy go in
  [hierarchy-change-requests.md](hierarchy-change-requests.md).

**`records/archetype-service.csv`** links each archetype to the hierarchy nodes it
serves, many to many.
- A path is written exactly as the hierarchy writes it
  (`<sector>.iron-and-steel.service.hot-metal`), or as a pattern in which `*`
  stands for one segment (`<sector>.*.service.steam`: every sector's steam node).
- A pattern must match at least one node.

**Families** (`records/family.csv`) group archetypes for display and banding. They
are not service keys.

| Kind | Families |
| - | - |
| Services shared across sectors | `heat-supply`, `power-generation`, `machine-drive`, `space-conditioning`, `lighting`, `mobile-equipment`, `co2-capture` |
| Sector families | One per sector, for integral process equipment |

**Heat.**
- **Tiers** are banded on the temperature the process needs: `low-temp` below
  150 °C, `medium-temp` 150–400 °C, `high-temp` above 400 °C.
- A heat-supply archetype lists the tiers it reaches in `heat-tier`.
- **Integral heat** is released inside the unit doing the transformation (a kiln, a
  blast furnace, an oven). Its equipment is a sector archetype.
- **Supplied heat** comes from a separable system (a boiler, CHP, a fired heater).
  Its equipment is a `heat-supply` archetype on the `service.steam` or
  `direct-heat` nodes.
- CHP is a heat-supply archetype. Its electricity is an output flow, never a second
  technology.

**Annotations.** `records/hierarchy-annotation.csv` records what the database knows
about the nodes it serves, grouped as the former design end uses were. Each group
has the paths it covers and the following fields:
- what it covers;
- its service unit;
- heat demand temperature;
- steam conditions;
- **draws-on**: the groups whose heat or drive the process takes, written
  `target (duty); target (duty)`. A link is a demand, not a second place the energy
  is counted.

Granularity follows **rule 7**: keep a service at the most general aggregation that
still captures a real difference in energy use or emissions. Do not bundle services
when the energy service differs, when the emissions differ in kind or in how they
are abated, or when a policy instrument treats them separately.

## 5. Parameters, units and bases

**Layer 1 keeps values as reported:**
- the source's own unit;
- money in `YEAR_CUR` (`2013_GBP`), with `currency` holding the currency-year only;
- no deflation or exchange.

**Basis flags:**
- `cost-basis` (equipment / installed / total-plant / overnight) and
  `capacity-basis` are required wherever `records/vocabulary/parameter.csv` says so.
- A row missing its required basis is marked `review`, with the note
  `BASIS NOT RECORDED`. It is not pooled until the basis is read back out of the
  source.

**Product unit.**
- Each archetype declares one `product-unit`: `t` for a process archetype, `GJ` for
  an energy service, `m3` where the product is a volume.
- Every example is converted to it. What cannot be converted is excluded, with the
  reason on the row.
- A source's generic `/unit` denominator is read as the product unit.
- A cost per GJ of energy use is never turned into a cost per tonne by dividing by
  specific energy consumption: that mixes input and output bases.
- A number in another unit is converted only with a factor **the same source gives
  for the same example**, on an output basis: an output capacity (`capacity-basis`
  thermal-, electric- or product-output), an annual output, a capacity factor. A
  factor from another source, or an energy input standing in for an output, is never
  used.
- A derived row that restates another row of the same example in another unit is
  a **duplicate**. It names that row in `duplicate-of` and is not pooled.
- **Set aside until an efficiency is known.** UKERC costs on energy-service
  archetypes are stated per tonne of the host plant's product, with only its fuel
  use per tonne, and UKERC's per-GJ restatements are per GJ of fuel input. Neither
  pools until an efficiency factor is established. They carry
  `set-aside = needs-efficiency`, and `output/set-aside-efficiency.csv` lists them.

**Target units** (pu is the product unit):

| Parameter | Unit |
| - | - |
| `capex`, `opex-fixed` | 2025_CAD per (pu/yr of capacity). A per-kW rating is taken at the stated capacity factor, else at nameplate. |
| `opex-variable`, `opex-total` | 2025_CAD per pu |
| `abatement-cost` | 2025_CAD per t CO2-eq |
| `specific-energy-consumption` | GJ per pu |
| `emissions-*` | t per pu. An emission factor per GJ of fuel is not a factor per GJ of output and is not pooled with one. |
| `capacity` | MW when pu is GJ; kt/yr when pu is t (t/d at 365 days) |
| shares, efficiencies, rates | %. A COP is a % efficiency. |
| `lifetime`, `construction-time` | years |

**Currency:** deflate in the source currency with its GDP deflator, then exchange at
the 2025 rate.

    factor(YYYY_XXX -> 2025_CAD) = deflator[XXX][2025] / deflator[XXX][YYYY] x exchange[CAD_per_XXX][2025]

- Convert once, from the published currency. The factor is not reversible.
- The reference tables come from the CIMS repository and are refreshed there.

**Emissions** are four parameters, kept separate:
- `emissions-combustion`;
- `emissions-process`;
- `emissions-total`, only where a source reports fuel and process together;
- `emissions-captured`.

Species stay explicit in `target` (`co2`, `co2e`, `pfc`) and are not converted to
CO2e. The exception is `emissions-reduction-potential`: it is one percentage,
whether the source counted CO2 alone or CO2-equivalent, so its species are pooled
into one column.

**Discount rates:** record the source study's own rate and replicate it when
inverting a levelized cost. Apply the model's hurdle rate only afterwards.

## 6. Summarising examples into an archetype

For each archetype and parameter:

| Field | Rule |
| - | - |
| central | The median of the examples' values when three or more examples carry one. Otherwise the value from the example whose source ranks highest in `records/reference/source-priority.csv`. A value reached through a compilation carries the compilation's rank. |
| low, high | The smallest and largest value any example gives, including ranges the sources report themselves. Written only where the values spread. |
| n | The number of examples behind the numbers. Always shown. |

Within one example, an as-reported value is preferred to one derived from it. Several
rows for the same quantity (sizes, cases) count as one example, taking their median.

## 7. Traceability

Every fact row carries:
- `source-id`, the original the number belongs to;
- `via-source-id`, the compilation it was read from (UKERC, IPCC);
- `source-file` and `source-locator`, which must land a reader on the number;
- `extraction-file`;
- `value-type`: `reported`, `derived`, `assumed`, `proxy` or `placeholder`.

A `derived` row carries its `formula` and the `record-id` it was derived from.

**Record ids** are `tp-`, `tf-` or `tc-` followed by the source-id and a four-digit
number, numbered within the source (`tp-ukerc_2013_001-0042`), so an edit to one
source never renumbers another.

**Registration.** Every source is registered in `data/raw-data/source-details_sources.csv`
and `source-details_files.csv`. The build takes source ids from there.

## 8. Readiness

**One ladder.**
- `trl` is on the common 1–9 ladder of
  `data/service-technology-map/technology-readiness-levels.md`, using its
  industrial-process reading.
- Other scales (IPCC's NASA TRL, the IEA ETP scale) map through
  `records/reference/trl-scale-map.csv`.
- A reported range is carried at its lower bound.

**Availability rule, for the CIMS `available` parameter:**

| TRL | Available |
| - | - |
| 9 | now |
| 7–8 | in 5 years |
| 5–6 | in 10 years |
| ≤ 4 | in 15 years, or unavailable |

## 9. Reading the outputs

- `wide-archetype.csv` has one row per archetype with pooled numbers.
  `archetype.csv` lists every archetype and its status:
  - `quantified`: it has pooled numbers;
  - `named`: a source names it without numbers;
  - `not pooled`: its numbers could not be pooled;
  - `gap`: it has no example yet.
- **Never sort, average or chart a cost or intensity column across families.** It
  holds CAD per tonne on a kiln row and CAD per GJ on a boiler row. Read it against
  `product-unit`.
- The long tables (`example-parameter.csv` and the other `example-*` files) are the
  record of every number. The wide views and the workbook are views, and anything
  typed into them is lost on the next build.

## 10. The CIMS YAML layer

| Database | CIMS YAML |
| - | - |
| `capex` (with `cost-basis`) | `fcc` |
| `opex-fixed` | `fom` |
| `lifetime` | `lifetime` |
| `capacity` × `capacity-factor` × 8760 | `output` |
| `efficiency`, or input flows | `service-request`, one per carrier |
| `emissions-*` | `emissions`, `emissions-biomass`, `emissions-removal` |
| `trl` → rule above | `available` |
| constraint shares | `market-share-new-max`, `market-share-new-min`, `market-share-total` |

Field names for the YAML files are in `data/service-technology-map/README.md`.
