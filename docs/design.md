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
- That archetype holds host-side facts only: regeneration steam, and
  `share-to-capture`, the share of its CO2 sent to the capture plant. In CIMS it differs from its host only by a service request
  to the capture archetype, so its costs are the host plant's, assumed the same
  with and without capture unless a source shows a significant difference
  (modeller 2026-10-02; fill rules `est-ccs-host-*`, graded estimated). A cost a
  source gives on it is capture cost and is set aside (`set-aside = ccs-add-on`,
  worklist `output/ccs-addon-cost.csv`) to move to the capture archetype.
- The capture plant itself is a `capture-unit` archetype serving the matching
  `service.ccs.*` node. Its `capture-rate` is the share of the CO2 entering it that
  it captures.
- The plant-level capture rate is `share-to-capture` x `capture-rate` and is not
  recorded (modeller 2026-10-02). A plant-level rate a source gives on a host is
  recorded as its `share-to-capture`; one mapped to a capture plant is excluded
  (`records/reference/plant-level-capture-rate.csv`). A capture rate with no
  species named is of CO2.
- A route that concentrates its own stream keeps its archetype: oxy-fuel kilns,
  top-gas recycling, bath smelting.

**Standalone values.** Every archetype carries absolute values. None is stored as
a delta against a baseline. A negative cost is a saving against a baseline and is
not pooled. An efficiency measure's cost (the cost of adding it to a plant) pools
only as a **whole-plant cost**: the host plant's cost from the same source plus the
measure's. `records/reference/ukerc-host-baseline.csv` names which archetype is
which UKERC host step. A measure whose source gives no host cost is set aside
(`set-aside = needs-host-cost`, listed in `output/set-aside-host-cost.csv`).

**Add-ons and components.**
- Storage added to a base system (a battery on PV, a thermal store on an electric
  heater) is an add-on measure: its cost is `incremental` and pools only as a
  whole-plant cost with the base system's cost from the same source, as above.
- An example has every part its archetype names. A PV system without storage is not
  an example of `photovoltaic-array_battery-storage`.
- Road-vehicle components (engines, batteries, drivetrains) are not proxies for
  mobile equipment.

**Whole-plant archetypes** (a whole mine, refinery or upgrader) are alternatives to
the unit archetypes inside them. A model uses one framing or the other, never both.

**Components and assembled whole-plant costs.**
- A `component` archetype (type `component`) is a part priced only to build
  whole-plant costs: `anaerobic-digester`, `separator_biogas-upgrading`. It serves no
  hierarchy node and is never offered to the model; the build refuses a component
  that links to a node. Components are shown in the wide views with `applies-to`
  reading `no connection` (2026-09-30; they were left out before).
- `records/reference/whole-plant-assembly.csv` lists each whole-plant cost to build
  from components: the whole-plant archetype, the source, the parameter and unit,
  and the component rows (example, case, and a multiplier where the denominators
  differ). The build writes the sum as a derived row (`tp-<source-id>-aNNN`) whose
  `derived-from` names every component row.
- Capture plants by difference (2026-10-02). The same file, with `kind` =
  `difference`, gives a capture plant's cost as the same source's plant WITH capture
  less the same plant WITHOUT it; with `kind` = `rebase`, it puts a retrofit cost the
  source gives per unit of host product per t CO2 captured. The multiplier is the
  source's own captured CO2 (nameplate t/yr for capex and fixed O&M, actual t for
  variable O&M); rows are `tp-<source-id>-dNNN` on the capture archetype. Pairs are
  listed case against case by hand, never by archetype; the result covers capture,
  compression and any host changes the source counts. Variable O&M is differenced
  only where the source excludes fuel from it. Where the source prints only the
  emissions with and without capture, avoided CO2 stands for captured CO2 (column
  `assumption` = `avoided-co2-for-captured`, conversion class `assumption`).
- Components are added only within one source, and a different denominator is
  reconciled only with that source's own factor. Components from different sources,
  different currency-years or an unreconciled unit stop the build.
- Where the source also prints the total, the assembled row is a consistency check:
  a duplicate of the printed row, not pooled.
- An example whose source prices the whole plant (digester and engine together) is
  an example of the whole-plant archetype (`anaerobic-digester_chp`), not of a part.

**Reference archetypes.** Type `reference` keeps the numbers for a step the CIMS hierarchy does not resolve (food evaporation). Like a component it serves no hierarchy node, and it is shown in the wide view.

**No connection.** Any archetype that serves no hierarchy node (a component, a reference archetype, or one whose route the hierarchy leaves out, such as coal gasification to SNG) stays in the database; its `applies-to` reads `no connection`. It has no row in `cims_hierarchy_technology.csv`.

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
- only values the source prints, or values derived using only values the source
  prints (a sum, ratio or unit conversion), stored as `derived` with the `formula` and
  a note naming the printed inputs. Never a midpoint invented for a printed range, an
  outside factor or an assumption. A whole-plant cost the build assembles from
  component rows is not also summed by hand in the extraction;
- the source's own unit;
- money in `YEAR_CUR` (`2013_GBP`), with `currency` holding the currency-year only;
- no deflation or exchange.

**Basis flags:**
- `cost-basis` (equipment / installed / total-plant / overnight) and
  `capacity-basis` are required wherever `records/vocabulary/parameter.csv` says so.
- A row missing its required basis is marked `review`, with the note
  `BASIS NOT RECORDED`. It is not pooled until the basis is read back out of the
  source.
- 2026-10-02 read-back: capacity bases were set from what the extraction notes
  record of the source (a capacity in tonnes of the archetype's product is
  `product-output`; "thermal output", "steam output", "MWe", "electric input" and
  the like as stated), and for the EPA 2007 and 2017 CHP catalogs from the
  catalogs themselves (systems are rated by electric capacity; the 2007 annual
  outputs equal capacity x 8760 h x the stated capacity factor). The tag added to
  the note ends "basis read back 2026-10-02". A capacity the source does not
  qualify (an engine rating, an "energy" MW) stays in review. Cost bases the
  extractor recorded as `COST BASIS NOT STATED` cannot be read back: the source
  does not say. A capex with no stated cost basis is taken as installed (modeller
  2026-10-02); the note says `COST BASIS ASSUMED: installed`.

**Product unit.**
- Each archetype declares one `product-unit`: `t` for a process archetype, `GJ` for
  an energy service, `m3` where the product is a volume.
- Every example is converted to it. What cannot be converted is excluded, with the
  reason on the row.
- A source's generic `/unit` denominator is read as the service unit that source
  reports for the step (UKERC: t of product, GJ or m3), and as the product unit only
  when the source names none. A service unit that is not a physical product (UKERC's
  per £k of output) is never pooled.
- Incremental costs and hosts (modeller 2026-10-02): host-plant costs are needed
  where a competition holds both the host and the host plus an add-on, so an
  efficiency variant's incremental cost is added to its host's (the fill rule
  `est-host-increment-*`, hosts in `records/fill/host-archetype.csv`: the archetype
  name less its last modifier, else the only conventional archetype with the same
  equipment and product unit). The host's cost is assumed the same with and
  without the add-on. CCS is counted only in the CCS competition: a capture plant's
  (co2-capture family) incremental cost is its own cost and pools as it stands; a
  host plant with capture holds only the host's cost (see Capture). Archetypes with
  no host are open items in `docs/sanity-check-list.csv`.
- A cost the source states as the cost of adding an improvement to an existing
  plant (UKERC measures, UK TIMES "improvement technologies" and add-ons via
  Bataille) is incremental: `cost-basis` is `incremental`. UK TIMES rows are marked
  from their notes at extraction; any other example is listed, with its reason, in
  `records/reference/incremental-cost.csv` (with `case` set where only one case of
  the example is incremental: a leading `[case]` in the note, or UKERC's row code). It is set aside as `needs-host-cost`
  unless the same source gives the host plant's cost, in which case a whole-plant
  row is derived.
- A cost per GJ of energy is put per tonne with specific energy consumption (or a
  per-tonne cost per GJ by dividing by it) only when both count the same GJ: the
  same stream (the same fuel, heat or electricity), the same side (input or
  output) and the same scope (the equipment the cost covers, not the whole host
  process). The check is stated per example and the converted value is graded
  `identity`. Otherwise it is not converted: that would mix input and output
  bases (D13). A cost per GJ of a product's own energy content (per MWh of
  methanol) is not this case; it converts with the product's heating value.
  Amended 2026-09-30; no example qualifies yet.
- A number in another unit is converted with exact unit definitions (Btu, lb, short
  ton, barrel; `pipeline/convert.py`), with a factor **the same source gives for the
  same example** on an output basis (an output capacity, an annual output, a capacity
  factor), or with a **product factor** from `records/reference/conversion-factor.csv`
  (amended 2026-09-26). Each product factor is a physical property with its source:
  a heating value (t or Nm3 of hydrogen to GJ), a density (m3 of ethanol to t), an
  energy content (t of LNG to MMBtu), or a product ratio (t of alumina per t of
  aluminium). It applies to the archetypes its `applies-to` names, or to the
  examples `records/reference/example-conversion.csv` names; there `none` marks an
  example reported per a product the archetype does not make, which is not pooled.
  The row names the factor in `conversion`. An energy input standing in for an
  output is never used, and no factor is written inline in code or in a note.
  A conversion may chain at most two factors (kW of hydrogen -> GJ/yr -> t/yr).
- **Every factor has a class** (amended 2026-09-26), and every converted row
  records the weakest class it rests on (`conversion-class`) and the factors
  themselves (`conversion-factors`): `unit` (a definition, or the currency method),
  `same-source` (the same source's own output, capacity, capacity factor or
  efficiency for the example), `property` (a heating value, density or molar
  mass), `ratio` (a typical process ratio), `internal` (a value pooled in this
  database from other examples), `assumption` (a value chosen where no source
  fixes it). From `property` on the factor is **external** to the source. The
  archetype summaries count the examples that rest on an external factor
  (`n-external`) and name the factors (`external-factors`); the wide view lists
  them in one column, `external-conversions`, and the workbook shades those values
  purple (italics until 2026-09-30). `output/conversion-factor-use.csv` says how many pooled rows each
  factor carries.
- **Reference sources are registered apart** from the technology sources, in
  `data/raw-data/source-details_reference.csv`: the constants, densities and
  ratios behind the factors, and the deflator and exchange-rate series behind the
  currency conversion (`used_for` says which), are not evidence about a technology.
  `currency-conversion.csv` names the series each currency factor rests on. Each factor's
  `source-id` resolves there (or, for a factor a technology source prints about its
  own product, in the main manifest); an id may not be in both, and a reference
  source that backs no factor fails the build. `output/reference-source-list.csv`
  lists them with the factors each backs.
- **Energy is on a higher heating value (HHV)** (amended 2026-09-26). A number the
  source states on HHV is used as it is; one whose basis the source does not state
  is read as HHV; one stated on LHV is converted with the HHV/LHV ratios of the fuel
  in and the product out that `records/reference/heating-value-stream.csv` names
  for the archetype (`pipeline/heating.py`), and is not pooled on an archetype with
  no row there. `heating-value` records the basis as the source gave it (HHV, LHV
  or `not stated`) on every row whose value depends on it. Every energy factor in
  `conversion-factor.csv` is on HHV.
  Amended 2026-09-30: an LHV specific energy use takes the ratio of the carrier it
  names in `target` (1 for electricity, heat and steam), not the archetype's fuel;
  before, an LHV electricity or steam use was raised by the fuel's ratio. On a
  per-tonne archetype a cost per kW or MWh of the product's own energy, and a
  MWh-per-MWh energy use, are put on HHV (divided by the product's ratio) before
  the product's HHV per tonne puts them per tonne, which returns the source's own
  LHV per tonne exactly. A cost per kW of an INPUT (`capacity-basis` thermal- or
  electric-input) on a per-tonne archetype is never put per tonne with the
  product's heating value.
  Steam given as a mass is put in GJ with `cf-steam-enthalpy` (saturated steam at
  10 bar(a), 2.777 GJ/t, the most common industrial condition; its note records the
  convention and range). Pulp is counted in air-dry tonnes (90% dry), the common
  unit in pulp and paper data; a figure per oven-dry tonne is converted per example
  (`ODt=ODt-pulp` in `example-conversion.csv`).
  Ratios on file beyond the pure fuels (2026-10-02): black liquor from Larson 2006's
  own LHV and HHV; coke-oven and blast-furnace gas derived from the IEAGHG 2013
  Table C-11 compositions (the water each forms x 44.0 kJ/mol).
  Amended 2026-10-02: an LHV energy use per tonne that names its carrier needs no
  `heating-value-stream.csv` row; the carrier's own ratio applies.
  `heating-value-stream.csv` may hold one row per archetype (a second row used to
  replace the first silently; the build now fails on it).
- **The efficiency bridge** (amended 2026-09-26 and 2026-10-02; `pipeline/bridge.py`).
  An example uses its own efficiency, a derived one where it reports none. It
  counts as CHP only if its archetype is named so or it reports a total CHP
  efficiency: a heat-only boiler on a boiler-or-CHP archetype is bridged by its
  own efficiency, not by the archetype's total less electric (which, as two
  medians of different plants, had come out at 0.3% and inflated emission factors
  several hundredfold). A number
  stated per unit of energy input -- an emission factor per GJ of fuel, a cost per
  kW of input capacity (`capacity-basis` thermal-input or electric-input), a
  capacity rated on its input -- is put per GJ of output with the efficiency: the
  example's own where the same source gives one, otherwise the archetype's pooled
  central value (class `internal`). For a CHP archetype the efficiency is the total
  less the electric one, since its product is the heat. A number per tonne of a
  host plant's product with only the plant's fuel use per tonne (UKERC) is bridged
  only for the examples marked `yes` in `records/reference/efficiency-bridge.csv`:
  the per-tonne number must be the equipment's own, not the whole host process's.
  A specific energy use is never bridged; it would only restate the efficiency.
- **CHP costs per kW of electricity** (amended 2026-10-01). On a heat-supply
  archetype whose product is the heat, a cost or capacity rated per kW (or MW)
  of electric output is put per kW of heat with the heat-to-power ratio: the
  example's own (its printed ratio, else its heat over its electric efficiency,
  else its total less its electric efficiency over its electric efficiency;
  class `same-source`), otherwise the median of the archetype's examples' own
  ratios (class `internal`, factor `hpr:<archetype>`). Applies to every source.
- An absolute cost is put per unit of capacity with the same source's capacity for
  the same case (a leading `[case]` in the note, or UKERC's row code); a capacity
  rated on input is then bridged.
- A methane slip (a % of the methane handled that is lost) is put per GJ of methane
  delivered as s/(1-s) divided by the heating value.
- A fixed O&M a source gives as a percentage of capital per year is put on the same
  example's pooled capital cost.
- **Levelized costs** (`cost-levelized`) are shown with the costs. They are pooled
  only with each other, never with capex or opex, and a levelized cost per unit of
  electricity is not pooled on an archetype whose product is heat.
- A derived row that restates another row of the same example in another unit is
  a **duplicate**. It names that row in `duplicate-of` and is not pooled.
- **Set aside until an efficiency is known.** UKERC costs on energy-service
  archetypes are stated per tonne of the host plant's product, with only its fuel
  use per tonne. They carry `set-aside = needs-efficiency` until the example is
  reviewed in `efficiency-bridge.csv`, and `set-aside = not-bridged` (with the
  reason) where the review found the per-tonne numbers to be the host process's.
  UKERC's per-GJ restatements (per GJ of fuel input) are duplicates of the
  per-tonne rows. `output/set-aside-efficiency.csv` lists both.

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
into one column. A cost per t CO2 (abatement or capture cost) stands for a cost per
t CO2-eq (ruling 2026-10-02).

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

## 6a. Filling empty cells

The aim is a value in most or all parameters. Where the examples give none, the
fill step (`pipeline/fill.py`, after the summaries) may write one, graded by how
it was reached. Adopted 2026-09-30.

| Grade | What it means |
| - | - |
| `sourced` | Pooled from examples, as in section 6. |
| `identity` | Calculated from the archetype's own values by a definition or a physical relation: 100 / efficiency, fuel use times its emission factor, combustion plus process emissions. |
| `estimated` | Borrowed or scaled from another archetype, or set by a class rule: a host plant's cost plus an increment, a sibling's lifetime. |
| `guess` | A judgement with a range and a rationale, in `records/fill/fill-judgement.csv`. |

Rules:
- A fill is written only where there is no sourced value, and is recomputed on
  every build, so a new source displaces it with no edit. Examples and extractions
  are never changed.
- A fill takes the worst grade among its rule and its inputs. Estimated rules take
  sourced inputs only; an identity may use a filled input and inherits its grade.
- Every rule is a row of `records/fill/fill-rule.csv`: grade, method, scope,
  formula, rationale, and `status` (active or off). A rule found to give wrong
  values is turned off with the reason, not deleted.
- Section 5 still binds: units and product units must match, a cost per GJ goes
  per tonne only under the same-GJ condition, and no regional adjustment.
- A filled row has `n` = 0, `central-from` saying how it was reached, and `inputs`
  naming the cells and factors it used with their grades.
- A guess needs `central` within a stated `low`-`high`, a rationale and an author.
  A guess on a cell that has since gained a sourced or calculated value is not
  used.

Rules in force (2026-09-30):
- `id-sec-from-efficiency`: energy use per GJ of output = 100 / efficiency, on
  energy-service archetypes other than CHP.
- `id-efficiency-from-sec`: OFF. A pooled energy use with no carrier is not
  reliably the total input per GJ of output, so its inverse gave a 7% motor
  efficiency and 154% for the methane reformer.
- `id-combustion-co2-from-fuel`: carrier-specific fossil energy use times the
  carrier's CO2 factor on HHV (`cf-ef-co2-<carrier>` in `conversion-factor.csv`).
  Emission factors come from ECCC's National Inventory Report (Annex 6) where it
  gives one, and from IPCC 2006 defaults only where it does not (2026-10-03). NIR
  factors are per physical unit; they are put per GJ HHV with the ECCC CFR HHVs
  (natural gas, diesel, fuel oils) or the StatCan RESD energy contents (coal, coke,
  coke oven gas, petroleum coke, still gas, LPG). Blast furnace gas uses the IPCC
  default because the NIR gives none. Not where process emissions are recorded, where an
  unnamed `fuel` is part of the energy use, or on reformers, gasifiers and
  reactors, whose fuel may be a feedstock.
- `id-total-from-parts`: total emissions = combustion + process, same species.
- `est-host-increment-capex`, `est-host-increment-opex-fixed`: an incremental
  cost (`set-aside-host-cost.csv`) plus the pooled cost of the host plant named
  in `records/fill/host-archetype.csv`. Hosts were proposed by name (the
  archetype less its last modifier) and need confirming; the rest are
  `unmapped`.
- `est-sibling-lifetime`, `est-sibling-construction-time`,
  `est-sibling-capacity-factor` (2026-10-01): the median sourced value of the
  nearest siblings (same equipment and discriminator, else same equipment; same
  product unit). The range spans the siblings' values and at least +/-25% of the
  central. These parameters depend little on carrier or variant; capex and O&M
  are not copied between siblings without a ratio from a source that prices both.
Parked methods (written and back-tested, status `off`; set a rule `active` to use it):
- `est-modifier-ratio-capex` (parked 2026-10-01; would fill 4 cells): a variant (`<base>_<modifier>`) takes
  its base archetype's sourced capex times the median variant/base ratio from
  sources that price both a base and its variant with the same modifier (two
  pairs or more). The O&M version is off: it filled nothing and caught 2 of 5.
  Costs are not copied between siblings that differ by carrier: no source in
  the database prices both members of such a pair on a usable basis.
- `est-cost-ratio-opex-fixed` (parked 2026-10-01; would fill 42 cells): capex times the median fixed-O&M
  share of capex among archetypes with both sourced (same equipment, else
  family, else all; pools of five or more); range is the pool's smallest to
  largest share. Weak: typical error a factor of 1.7, so these are placeholders.
Methods to try (not written; ideas for when data runs short). From the
Hotmaps D2.3 open data set (Pezzutto et al. 2018; review in the project note
`hotmaps-review-2026-10-02`). None is coded; one would need a rule, a back-test
and a ruling before use. Hotmaps cost data itself is not loaded (2026-10-02).
- **Cost-capacity power law.** Where a source prices one size only, scale
  specific capex to other sizes with an exponent: specific cost proportional to
  size^b. Hotmaps implies b for 1-50 MW_th of about -0.12 (gas boiler), -0.13
  (gas turbine), -0.15 (steam-turbine CHP), -0.09 (engine CHP), -0.07 (electric
  heat pump), -0.16 (solar district heat), about 0 (combined cycle). Better to
  fit b from sources in this database that price several sizes.
- **Regional cost transfer with indices.** Reference-region cost x labour-cost
  index x equipment price-level index (Hotmaps: Danish Energy Agency costs x
  Eurostat construction labour cost and PPP price levels, held constant over
  time). Conflicts with section 5 (no regional adjustment); would need that
  rule changed first.
- **Cost decline for immature technologies only.** Future capex falls for heat
  pumps, fuel cells, biomass boilers and solar heat; mature equipment held flat.
- **Pool process energy use across countries.** Hotmaps assumes no country
  difference in specific energy consumption, because plants are run by
  multinationals with global technology suppliers. Supports pooling non-Canadian
  process data.
- **Benchmark x activity.** Energy use = production x specific energy
  consumption; split by heating share and temperature-band share; excess heat =
  energy use x excess-heat share per band.
- **Production from emissions.** Where production is missing, production =
  reported emissions / emissions per tonne (Hotmaps: EU ETS; here: GHGRP), else
  a national average.
- **Top-down check.** Compare benchmark totals with national energy balances
  (here: CEUD, RESD); treat averaged products (e.g. paper) as +/-50%.
- **Back-test.** Every borrowing rule is also run on the cells that have a sourced
  value, as if they had none (`output/fill-backtest.csv`; the build prints the
  hit rates). The widen fraction is set so about 90% of sourced values fall in
  the range. At 25% (2026-10-01): lifetime 96/108, construction time 29/32,
  capacity factor 15/17; 71% of centrals within 25% of the sourced value.
  The parked ratio rules tested at: modifier-ratio capex 9/10 (3 within 25%);
  O&M share 71/87 (24 within 25%). The build back-tests active rules only.

## 7. Traceability

Every fact row carries:
- `source-id`, the original the number belongs to;
- `via-source-id`, the compilation it was read from (UKERC, IPCC);
- `source-file` and `source-locator`, which must land a reader on the number;
- `extraction-file`;
- `value-type`: `reported`, `derived`, `assumed`, `proxy` or `placeholder`.

A `derived` row carries its `formula` and the `record-id` it was derived from.

**A compilation's row never stands beside the original it cites.** When the
original is held, its own figure is used and the compilation's row is dropped,
unless the compilation states a reason for its different number (2026-10-03).
A figure the original does not contain at all is the compilation's own and is
credited to the compilation.
For UKERC the row-by-row outcome is `records/reference/ukerc-original-reconciliation.csv`;
for a compilation extracted afresh (N-ZIP over IFS) the extractor leaves the
reprinted rows out of the main file and lists them in `_other-values`.

**Record ids** are `tp-`, `tf-` or `tc-` followed by the source-id and a four-digit
number, numbered within the source (`tp-ukerc_2013_001-0042`), so an edit to one
source never renumbers another.

**Registration.** Every source is registered in `data/raw-data/source-details_sources.csv`
and `source-details_files.csv`; a reference source (a constant, a conversion
factor's source, a currency series) in `source-details_reference.csv` instead. The build takes source ids from there. The
manifest records what the database draws on: sources that provide data, the
originals a compilation cites (registered but not held), and sources queued for
extraction.

**Documents to get.** Documents worth obtaining are listed in
`data/raw-data/to-get.csv`, with priority, the source that cites each one, and
what it would supply. A document leaves the list when it is downloaded and
registered.

**Background documents.** A downloaded document that yields nothing for the
database goes to `data/raw-data/background-no-data-extracted/` and is recorded
in `data/raw-data/background-register.csv` (why it has no data, what little it
has), not in `source-details_files.csv`. Its source row stays only if a
compilation cites it as an original.

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

- `wide-archetype.csv` has one row per archetype, including blank ones and
  those that serve no hierarchy node (`applies-to` reads `no connection`). `end-uses`
  names the annotation groups each archetype serves. `status` (also in
  `archetype.csv`) is one of:
  - `quantified`: it has pooled numbers;
  - `named`: a source names it without numbers;
  - `estimated`: it has no sourced numbers, only filled ones (section 6a);
  - `not pooled`: its numbers could not be pooled;
  - `gap`: it has no example yet.
- `filled` lists the parameters the fill step wrote and their grade; in the
  workbook those cells are shaded (identity blue, estimated orange, guess red;
  purple marks a sourced value converted with an external factor)
  and their `_n` is 0.
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
