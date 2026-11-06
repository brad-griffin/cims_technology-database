# Reporting energy and emissions from CIMS: accounting design

**Status: proposal, 2026-09-21. Nothing here is implemented in CIMS yet.**

Files:

- `cims/reporting-accounting/accounting_example.py`: the worked example in section 3, runnable. It
  builds the flow ledger of section 4 and reports it under each config. Run from the
  repo root: `python cims/reporting-accounting/accounting_example.py [--ledger out.csv]`.
- `cims/reporting-accounting/configs/`: the configs used here: `resd.yaml` (energy),
  `nir-economic.yaml` (emissions, the target layout), `ipcc-2006.yaml` (emissions by
  IPCC category, kept to show a second convention) and `cims-origin.yaml` (today's
  outputs, for regression).
- `cims/reporting-accounting/context/2510002901_databaseLoadingData.csv`: StatCan RESD, Canada 2019 (TJ),
  used for the conventions in section 2.
- `cims/reporting-accounting/context/EN_GHG_Econ_Canada.xlsx`, sheet "24": ECCC's NIR emissions by
  economic category and IPCC sector, 2024; the target layout for emissions.

## 1. The problem

CIMS reports one convention: quantities and emissions traced back to the fuels a
sector buys (`requested_quantities`, `emissions_total_cumul_*`). The reports we need
to check against use others: StatCan's Report on Energy Supply and Demand (RESD) for
energy, the National Inventory Report (NIR) for emissions, and possibly more later.

The code cannot produce these because `is_supply` controls five unrelated things:

| Role | Today decided by |
| - | - |
| Traversal side and price equilibrium | `is_supply` |
| Requesters are charged the node's `emissions` factor | `is_supply` (the `child_node in supply_nodes` gates in `emissions.py`) |
| Requesters record the node itself as an energy, instead of expanding it into its inputs | `is_supply` (`quantity_aggregation._get_quantities_to_record`) |
| Where the node's own inputs are counted | structural parent for supply nodes, requesters otherwise |
| By-products (negative `service_request`) | only `quantity_distributed` at the producer |

Principle adopted (Brad, 2026-09-21): **reporting is governed by a config file.** The
model records flows once; a config decides which rows and categories they land in.
RESD for energy and NIR for emissions are the likely configs, and others must be
possible without changing the model.

## 2. Conventions to reproduce

### RESD (StatCan table 25-10-0029-01)

- Transformation is booked on the **input** fuel ("Transformed to coke and
  manufactured gases", "... to electricity by utilities / by industry", "... to
  refined petroleum products", "... to steam generation"). Outputs appear as
  **Production** of a secondary fuel.
- Final demand by sector counts every fuel used directly, primary or secondary, and
  never the transformed inputs.
- Canada 2019, coal to coke: 92,807 TJ of coal transformed; coke production 70,010
  and COG production 23,969 TJ (outputs are 101.3% of input, so expect a statistical
  difference). Iron and steel final demand: coal 11,271, coke 76,821, COG 22,119 TJ.
  Blast-furnace and BOF gas are not RESD fuels; their energy stays inside coke use.
- Arithmetic checks: coal availability 596,515 − 462,782 − 92,807 = 40,926 ≈ net supply
  40,925; COG 23,969 − 1,850 (to electricity by industry) = 22,119 net supply.
- Stock variation: a negative value is a draw on stocks, i.e. it adds to availability
  (coke: 70,010 − 3,493 + 19,238 + 3,304 = 89,059).

**How StatCan splits inputs between outputs.** It has no formula; it takes the split
respondents report, under survey rules on where fuel is booked:

- Industrial generation (survey 2196) asks plants to "report only the amount of fuel
  used for the generation of electricity", with useful heat reported separately. No
  method is prescribed.
- Industrial Consumption of Energy (survey 5047): fuel that raises steam which then
  drives a turbine is reported as fuel (final demand), not as fuel for electricity.
  So boiler plus steam-turbine cogeneration stays in the industry's final demand; only
  fuel burned directly in a generator (gas turbine, engine) is transformation. (Taken
  from a summary of the guide; confirm the wording.)
- Steam for sale: only steam delivered to another establishment. For cogeneration,
  RESD notes that "only an estimate of the fuels used for steam for sale generation
  may be made."
- Coke ovens: the whole coal charge is transformed; outputs are not apportioned.
- Refineries: crude feed and natural gas for refinery hydrogen are transformed; a
  refinery burning its own still gas is Producer consumption.

### Cogeneration: incremental fuel to electricity (adopted)

Decision (Brad, 2026-09-21): for now, energy and emissions of cogeneration are split
between electricity and heat by the **incremental fuel to electricity** method, with
an **80% efficient reference boiler**. The heat is charged the fuel a reference boiler
would need to deliver the same useful heat; the rest of the fuel, and the same share of
the emissions, is the increment attributed to electricity:

    fuel to heat        = useful heat / 0.80
    fuel to electricity = total fuel − fuel to heat
    electricity share   = 1 − useful heat / (0.80 × total fuel)   (clamped to 0-1)

In RESD terms the electricity share of each fuel goes to "Transformed to electricity
by industry" and the rest stays in the sector's final demand; the electricity is
Production of secondary electricity. In the NIR economic layout the electricity share
of emissions goes to "Industrial Cogeneration (Electricity)". Each config sets the
method, so a different one (StatCan's tech-type rule, output energy shares) can be
swapped in later.

**Which techs are cogeneration** (decision, 2026-09-21): any tech that delivers heat or
steam and produces electricity as a by-product (a negative request to electricity).
Configs select them by that pattern, not by name.

Note that the method charges all of cogeneration's efficiency gain to electricity: a
back-pressure steam turbine delivering much heat and little power can show an
incremental electric efficiency above 100%.

### NIR by economic category (the target for emissions)

Decision (Brad, 2026-09-21): emissions are reported like ECCC's table of NIR emissions
by economic category (`EN_GHG_Econ_Canada.xlsx`, sheet "24"). Its rows are economic
categories (Oil and Gas, Electricity, Transport, Heavy Industry, Buildings,
Agriculture, Waste, Coal Production, Light Manufacturing ...); its columns split each
row by IPCC sub-sector:

- Energy: Stationary Combustion (stationary; industrial cogeneration, electricity and
  steam for sale), Transport, Fugitive (unintentional, flaring, venting)
- IPPU: Mineral Products, Chemical Industry, Metal Production, halocarbons,
  Non-Energy Products from Fuels and Solvent Use, Other Product Manufacture
- Agriculture, Waste, CO2 captured

Heavy Industry covers "stationary combustion, onsite transportation, electricity and
steam production, and process emissions". Iron and Steel, 2024 (Mt CO2 eq):
stationary 4.30, industrial cogeneration (electricity) 0.31, transport 0.21, fugitive
0.02, metal production 9.69, non-energy products 0.17; total 14.69.

**Coke ovens report in the Iron and Steel row** (decision, 2026-09-21). ECCC's
description of the row lists pelletizing, blast furnaces, DRI, EAF and BOF but not
coke ovens, and Coal Production covers mines only, so confirm the ECCC mapping if the
numbers are to be matched exactly.

### IPCC 2006 categories (UNFCCC layout)

IPCC 2006 Vol. 3 ch. 4.2: coke production is energy use of fuel (1.A); all carbon
charged to the blast furnace is process emissions (IPPU 2.C.1); by-product gases
burned elsewhere follow the process they came from. Canada's NIR reports reductant
coke under 2.C.1.b pig iron because the reductant share cannot be disaggregated
(Annex A1); chapter 4 should be checked before the Canadian defaults are fixed.

## 3. Worked example: 100 GJ of coal through an integrated BF-BOF plant

Quantities are illustrative. Emission factors are IPCC 2006 defaults in kg CO2/GJ:
coking coal 94.6, coke 107, COG 44.4, blast-furnace gas 260, BOF gas 182, natural gas
56.1; coal tar 90 is an assumption. Carbon is in t CO2.

Nodes, using the redesigned hierarchy: coke ovens `service.coke`; blast furnace
`service.hot-metal`; BOF `product.molten-steel`; by-product carriers for COG
(`common-energy.coke-oven-gas`), BFG and BOF gas; `service.fuel-blend.process-gas`
blending the three gases, topped up with natural gas. Every burner draws on the
process-gas pool: oven underfiring (6.4 GJ), the blast furnace's hot-blast stoves
(10 GJ), reheating furnaces (25 GJ) and a cogeneration unit (15 GJ, delivering
8.25 GJ of steam to the plant and 3.75 GJ of electricity). 80 GJ of coal goes to the
ovens and 20 GJ is injected in the blast furnace.

By-products and own use are kept apart by giving them different real nodes (option 1
in section 6, adopted 2026-09-21): a producer sends its gas to the carrier with a
negative request, and its own burners take fuel from the pool like any other user.
The ovens and stoves therefore burn the pooled mix, not pure COG or BFG, which is
close to how integrated plants run.

### 3a. Physical flows (script output)

Fuel burned at a process emits all its carbon there (combustion). Other inputs (coal
charged to the ovens, coke and injected coal in the blast furnace, hot metal in the
BOF) pass their carbon to the outputs, and what does not leave in an output is lost
at the process (leaks, quenching, reduction).

| Process | In | Out | C in | C out | Emitted |
| - | - | - | -: | -: | -: |
| coke ovens | coal 80; process gas 6.4 (underfiring) | coke 57.6; COG 17.6; tar 3.2 | 8.61 | 7.23 | 1.37 (underfiring 1.04, leaks and quenching 0.34) |
| blast furnace | coke 57.6; coal 20; process gas 10 (stoves) | hot metal 5.76 t; BFG 27.3 | 9.68 | 8.06 | 1.62 (stoves) |
| BOF | hot metal 5.76 t | steel 6.4 t; BOF gas 5.0 | 0.95 | 0.93 | 0.02 |
| process-gas pool | COG 17.6; BFG 27.3; BOF gas 5.0; natural gas 6.5 | process gas 56.4 | 9.16 | 9.16 | 0 |
| reheating | process gas 25 | heat | 4.06 | 0 | 4.06 |
| cogeneration | process gas 15 | steam 8.25; electricity 3.75 | 2.44 | 0 | 2.44 |

Carbon in 9.823 (coal 9.46 + natural gas 0.36) = emitted 9.512 + stored 0.311 (tar
0.29, steel 0.02). The pool is 31% COG, 48% BFG, 9% BOF gas and 11% natural gas by
energy; 87.5% of its carbon (8.02 of 9.16 t) came through the blast furnace.

### 3b. How the staging code accounts for it today

| Tech | Requests |
| - | - |
| ovens | coal +80; COG carrier −17.6; process gas +6.4 |
| blast furnace | coke +57.6; coal +20; BFG carrier −27.3; process gas +10 |
| BOF | hot metal +5.76; BOF gas carrier −5.0 |
| process gas | one tech per gas: COG +17.6, BFG +27.3, BOF gas +5.0, natural gas +6.5 |
| carriers | requested +x by the pool and −x by the producer, so net output 0 and net share 0 |

- **Direct emissions.** Only supply nodes carry a factor, and only positive requests
  are charged: ovens 7.57 (all the coal carbon), blast furnace 1.89 (injected coal;
  `service.coke` has no factor), natural-gas tech 0.36. Reheating, cogeneration and
  the BOF: 0. Total 9.82 = all carbon in, so the 0.31 t stored in tar and steel is
  counted as emitted, and emissions sit where the carbon enters, not where it is
  burned.
- **Cumulative attribution.** The blast furnace picks up all 7.57 through the coke
  request, which passes to hot metal and steel. The carriers have net output 0, so
  the pool's per-unit rate is only its natural gas (0.36 over 56.4 GJ), shared among
  the burners (underfiring 0.04, stoves 0.06, reheating 0.16, cogeneration 0.10). The
  sector total balances at 9.82; by-product gas carbon stays with coke and steel.
- **Quantities.** Ovens coal 80; blast furnace coal 20 direct plus 80 through
  `service.coke`, so 100; the burners natural gas 6.5 between them. Sector: coal 100,
  natural gas 6.5. No coke, COG, BFG or BOF gas; the gases appear only as
  `quantity_distributed` at their producers (17.6, 27.3, 5.0).

### 3c. The same flows under the configs (script output)

The cogeneration unit's electricity share under incremental fuel to electricity:
fuel to heat 8.25 / 0.80 = 10.31 GJ, fuel to electricity 15 − 10.31 = 4.69 GJ, so
31.25% of its fuel and emissions (2.44 × 0.3125 = 0.76 t CO2).

**RESD** (`resd.yaml`). The ovens are a transformation process with coal as feed;
the cogeneration unit's fuel is split as above; the process-gas pool is expanded into
the gases it is made of; BFG and BOF gas are not reported.

| Row (GJ) | Coal | Coke | COG | Natural gas | Secondary electricity, thermal |
| - | -: | -: | -: | -: | -: |
| Production | | 57.6 | 17.6 | | 3.75 |
| Transformed to coke and manufactured gases | 80.0 | | | | |
| Transformed to electricity by industry | | | 1.46 | 0.54 | |
| Iron and steel manufacturing | 20.0 | 57.6 | 16.14 | 5.94 | |

Coal checks: 80 + 20 = 100 bought; COG checks: 17.6 produced = 16.14 + 1.46 used. The
4.69 GJ of cogeneration fuel for electricity is split by the pool mix (31% COG, 11%
natural gas); its BFG and BOF gas share (2.69 GJ) is not a RESD fuel and is left out.
The ovens' underfiring counts as iron and steel final demand of the gases in the
pool. The ovens convert 94% of the coal energy.

**NIR by economic category** (`nir-economic.yaml`). Every process at the plant is in
the Iron and Steel row; the column comes from rules on where the carbon was emitted,
whether it was burned for heat or lost another way, which processes it passed
through, and whether it is the electricity share of cogeneration.

| Economic category (t CO2) | Energy: Stationary Combustion | Energy: Industrial Cogeneration (Electricity) | Energy: Fugitive | IPPU: Metal Production | Total |
| - | -: | -: | -: | -: | -: |
| Heavy Industry: Iron and Steel | 1.05 | 0.10 | 0.34 | 8.03 | 9.51 |

- Stationary combustion 1.05: the COG and natural gas carbon burned for heat:
  underfiring 0.13, stoves 0.20, reheating 0.51, heat share of cogeneration 0.21.
- Industrial cogeneration (electricity) 0.10: the electricity share (31.25%) of the
  COG and natural gas carbon burned in cogeneration. Cogeneration emits 2.44 t, of
  which 0.76 t is the electricity share, but 87.5% of that is BFG and BOF gas carbon.
  **BFG and BOF gas are reported as metal production wherever they are burned**
  (decision, 2026-09-21), so the blast-furnace rule comes before the cogeneration
  rule.
- Industrial cogeneration (steam for sale) is not reported: CIMS does not model steam
  sold to other sites (decision, 2026-09-21).
- Fugitive 0.34: coke-oven carbon lost other than by burning (leaks, pushing,
  quenching; IPCC 1.B.1.b).
- Metal production 8.03: all carbon charged to the blast furnace (coke 6.16 +
  injected coal 1.89) minus the 0.02 left in steel, wherever it is finally emitted:
  underfiring 0.91, stoves 1.42, reheating 3.55, cogeneration 2.13, BOF 0.02. This
  follows Canada's treatment of reductant coke as 2.C.1.b. A parcel's path lists the
  processes its carbon passed through, not where it was burned, so COG and natural
  gas burned in the stoves are not counted as metal production.

**IPCC 2006 categories** (`ipcc-2006.yaml`), the same ledger in the UNFCCC layout,
shown to confirm a second convention needs only a config: 1.A.1.c.i manufacture of
solid fuels 0.47 (oven leaks 0.34 + the COG and natural gas share of underfiring
0.13); 1.A.2.a iron and steel combustion 1.01; 2.C.1 iron and steel production 8.03;
total 9.51.

**CIMS current** (`cims-origin.yaml`). Reproduces today's outputs from the ledger:
coal 100 and natural gas 6.5 GJ; coal 9.46 and natural gas 0.36 t CO2 (total 9.82,
with stored carbon counted as emitted). This config is the regression check for the
new reporting code.

## 4. What the model must record: the flow ledger

The configs only work if the model records, after each year's equilibrium:

1. **Every flow into and out of each node/tech**, with quantity, unit and role: `in`
   as fuel, feed, material or blend component; `out` as product, by-product or
   stored. By-product production and own use are separate rows because they go to
   different nodes (COG −17.6 to its carrier; underfiring +6.4 from the pool).
2. **Carbon content on energy carriers**, not only supply nodes: coke, COG, BFG, BOF
   gas, and optionally hot metal. That is what lets carbon be followed from the
   process that makes a carrier to the one that burns it.
3. **Emissions with their origin kept**: the purchased fuel the carbon came from and
   the processes it passed through (in the script, a parcel key of fuel + path), and
   whether it was burned for heat (`combustion`) or lost another way (`process`:
   reduction, leaks, quenching). Pools such as process gas pass their inputs' parcels
   through in proportion. The NIR economic layout needs the combustion/process split
   to separate stationary combustion from fugitive and process columns.
4. **Carbon leaving in products** (tar, steel, feedstocks) as flows, not emissions.

The script's `--ledger` option writes the example ledger in this shape.

## 5. Config format

Each config has an `energy` section, an `emissions` section, or both:

- `commodities`: node → reporting fuel (`report_as`), class (primary, secondary,
  internal, material, non-energy), `expand` for pools reported as their inputs, and
  optional `check_disposition` rows that must add up to what was bought.
- `processes`: node → final-demand `account`; `transformation` with its `row` and the
  `feed` commodities booked there; `report: false` for pools.
- `rules` (emissions): ordered matches on `emitted_at`, `kind`, `path_includes` and
  `fuel`, each giving a `category`, or a `column` when `layout: matrix`.
- `layout: matrix` (the NIR economic layout): `rows` maps processes to economic
  categories (in CIMS, hierarchy branches such as `<region>.iron-and-steel.*`), with a
  `default`; `columns` lists the IPCC sub-sector columns in the published order.
- `stored_carbon`: none, separate or emitted. `group_by: fuel` gives the
  purchased-fuel view.
- `cogeneration` (in the energy or emissions section): `heat_outputs` and
  `electricity_output` select the cogeneration processes (a heat or steam product plus
  an electricity by-product); `method: incremental_fuel_to_electricity` and
  `reference_boiler_efficiency` set the split; `electricity_row` is where the energy
  config books the electricity fuel. Emission rules can match `use: electricity` or
  `use: heat`.

Still to add for full coverage: region and year scoping, and other cogeneration
methods.

## 6. Proposed code changes (CIMS, `staging` branch)

### Phase 1: record the ledger (no change to results)

**Status (2026-09-21): implemented, uncommitted.** In `staging/cims`: new
`src/CIMS/ledger.py`; `Model.run` builds `model.ledger[year]` after the aggregation
traversals; `CIMS.log_ledger(model, flows_file)` writes `results_flows.csv` and
`results_flows_emissions.csv`, and `scenarios/Reference.py` calls it; `carbon_content`
added to `PARAM` and to the local `data/model_inputs/defaults/defaults_Parameters.csv`
(that file is not in git). Here: `common-energy.{blast-furnace-gas, bof-gas,
coke-oven-gas}` added to `cims-hierarchy.csv` (crosswalk unchanged: common-energy is
out of its scope). Not yet done: the process-gas technologies (one per gas, plus
natural gas), which need the technology data folders; and `carbon_content` values.

Reference BC check: `results_general.csv` and `results_tech.csv` identical to the run
without the ledger; 51,151 flow rows (31,364 uses, 17,835 products, 1,952 by-products)
and 10,277 emission rows. The ledger's direct net emissions equal the region's
cumulative total in 2000, but are 0.4-1.3% higher in later years (2020: 42.43 vs
42.00 Mt), mostly at fuel-blend nodes and Residential. The likely cause is inside
CIMS, not the ledger (read from the code, not yet confirmed numerically): stock
allocation sets each child's quantity with vintage-weighted `service_request` ratios
(`stock_allocation._record_provided_quantities`), while the cumulative aggregation
edge attributes the child's emissions with the current year's ratio
(`_find_cumulative_rate_via_request_provide_edge`), so the two diverge once older
vintages are in the stock and agree in the base year. Separately, a tech's direct
fuel-combustion rate also uses the current year's ratio. To be resolved before
phase 2 checks totals against the ledger.

Carbon fallback check (Reference BC, 2020): the carbon the ledger puts on fuel flows
(quantity x CO2 Combustion factor) matches the direct CO2 Combustion emissions keyed
by that fuel to within 0.001% for every fuel, fossil and biogenic (natural gas 19.73
Mt, black liquor 17.10 Mt biogenic, ...). So direct emissions agree with the flow
quantities, which points the gap above at the cumulative attribution. (Direct
combustion rates do use the current year's ratio, but most fuel is burned at
fuel-blend techs whose requests are a fixed 1:1, so vintage weighting makes no
difference there.)

1. **New module `src/CIMS/ledger.py`.** Build the ledger per year from what the model
   already holds after equilibrium: `ProvidedQuantity` entries (keyed
   `node[tech]` → amount, including negatives) give every request flow and its sign;
   a node's provided quantity × `market_share_total` gives each tech's output; the
   `emissions_rate_direct_*` values × output give each tech's emissions, keyed by
   source, GHG and emission type. CIMS's existing emission types (Combustion,
   Process, ...) supply the ledger's combustion/process `kind`. Call it in `Model.run` after the aggregation traversals (beside
   `_warn_net_negative_provision`), store it on the model, and write it with the
   results (`results_flows.csv`).
2. **Carbon content parameters.** `carbon_content` and `carbon_content_biomass` (t CO2
   per unit of fossil and biogenic carbon, any node, not only supply nodes). In phase 1
   they are only used by the ledger to put carbon on flows (`t_co2`, `t_co2_biomass`,
   with `carbon_basis` saying where the value came from). When both are blank the
   ledger falls back to the node's CO2 Combustion emission factors, `emissions`
   (fossil) and `emissions_biomass` (biogenic): for a fuel that is burned these equal
   its carbon, since inventory factors assume complete oxidation. Process factors are
   not used, because they are net of the carbon stored in products (Natural Gas
   Feedstock is 0.00102 t/GJ against about 0.05 of carbon), so feedstocks and
   transformed carriers (coke, COG, BFG, BOF gas, hot metal) need explicit values.
   No CO2 factors were found for metallurgical coal or coke in `fuels_CIMS.csv`.
3. **Model data for by-products** (tech_data hierarchy):
   - Give by-product gases their own carrier nodes: `common-energy.coke-oven-gas`
     (secondary, a RESD fuel) and internal carriers for BFG and BOF gas under
     iron-and-steel. Producers request them negatively; `process-gas` has one tech
     per gas requesting its carrier, plus natural gas.
   - Own use (oven underfiring, stoves) must not be netted into the by-product row,
     or gross production is lost; `service_request` is keyed by target, so a tech
     can't request the same node both negatively and positively. **Adopted
     (2026-09-21): option 1, no temporary nodes.** By-products go to their carrier
     node with a negative request (−17.6 to `common-energy.coke-oven-gas`); own use
     is a positive request to the pool (+6.4 from `service.fuel-blend.process-gas`),
     like any other burner. Not adopted: a reporting-only `own_use` parameter for
     techs burning their own by-product directly, and keying requests by (target,
     context), which touches the reader, `node_utils`, the validator's
     `duplicate_service_requests` and every `service_request` lookup.
   - Carbon leaving in products: tar as a by-product to a non-energy node, steel carbon
     as a `carbon_content` on the product.

**Rename (to do, 2026-09-21):** `emissions` → `emission_factor` and
`emissions_biomass` → `emission_factor_biomass`, in the model inputs, the defaults
file and the code (`PARAM.emissions`, `PARAM.emissions_biomass` and their uses in
`emissions.py`, the readers and the validator). They are emission factors charged to
whoever uses a supply node, not emissions, and the new names keep them distinct from
`carbon_content`. A TODO marks them in `utils/parameter/list.py`.

### Phase 2: config-driven reporting package

4. **`src/CIMS/reporting/`**: config loader, ledger → energy balance and emission
   categories, parcel tracing through pools, and a `CIMS.report(model, config)` entry
   point. Port the functions in `accounting_example.py`, including the cogeneration
   selection (a heat or steam product plus a negative request to electricity) and
   split. Use TOML (standard library
   `tomllib`; CIMS requires Python ≥ 3.11) to avoid a new dependency, or YAML if the
   nested rules read better; the prototype uses YAML.
5. **Verification against published tables**: loaders for StatCan 25-10-0029-01 and
   ECCC's economic-category table (`EN_GHG_Econ_Canada.xlsx` and the provincial
   `EN_GHG_Econ_Can_Prov_Terr.xlsx` in `database/raw-data/gov-can/eccc/nir/`), a comparison report by fuel and row, and handling for suppressed
   cells (".."; the coal subtypes are all suppressed, so compare at Total coal).
6. **Regression test**: the `cims-origin` config must reproduce the existing
   `requested_quantities` and `emissions_total_cumul_*` for the Reference run; the
   worked example becomes a unit test with the section 3 numbers as expected values.

### Phase 3: model behaviour (decisions needed)

7. **Carrier carbon in competition.** Today's rule (2026-09-21) gives a by-product's
   producer no emissions impact, so by-product gas carbon stays with the producer and
   burners of process gas see only its natural gas as carbon. That is fine for totals
   and is kept in phase 1-2, where reporting moves the carbon. If the emissions cost
   burners see should include by-product carbon (e.g. process gas vs electricity in
   reheating), add a per-carrier `carbon_transfer` option: the producer is credited
   `carbon_content` × |request| and requesters are charged. This changes LCCs and
   market shares, so it needs a decision and a Reference comparison.
8. **Stored-carbon credit.** Charging all coal carbon at the ovens overstates their
   emissions cost by the tar carbon (and feedstocks elsewhere). A credit for carbon
   leaving in non-energy products fixes it in the model, not just in reports.
9. **By-product availability.** Fuel-blend techs using a by-product (COG, BFG, still
   gas) need a limit tied to production (design G4), and surplus needs a flare tech;
   today the new warning only reports a surplus.
10. **`quantity_aggregate`.** It routes all of a child's quantities to one parent
    (weight 1, others 0). It stays for market nodes, but reporting should not depend
    on it: an aggregation edge is fixed in the graph, so it can express only one
    convention, while configs need several side by side.

## 7. Open questions

- Coke-oven emissions: decided, Iron and Steel row (NIR economic layout). Still to
  confirm against ECCC's mapping, since the row description does not name coke
  ovens.
- Cogeneration: decided (2026-09-21). Split by incremental fuel to electricity with an
  80% reference boiler; techs delivering heat or steam with an electricity by-product
  are cogeneration; BFG and BOF gas report as metal production wherever burned; steam
  for sale is not reported. Still to check: how the heat and steam services are named
  in the redesigned hierarchy, so `heat_outputs` matches them.
- Whether hot metal carries carbon in the model (it matters for CCS placement and the
  IPPU/energy split, not for totals).

## Sources

- StatCan RESD definitions: https://www150.statcan.gc.ca/n1/pub/57-003-x/2017002/technote-notetech1-eng.htm
- StatCan RESD explanatory information (2025): https://www150.statcan.gc.ca/n1/pub/57-003-x/57-003-x2025001-eng.htm
- Survey 2196 reporting guide (2025): https://www.statcan.gc.ca/en/statistical-programs/document/2196_D1_T1_V12
- Survey 5047 guide: https://www.statcan.gc.ca/en/statistical-programs/document/5047_D2_V15
- IPCC 2006 Vol. 3 ch. 4: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/3_Volume3/V3_4_Ch4_Metal_Industry.pdf
- ECCC, GHG emissions by economic category and IPCC sector: `cims/reporting-accounting/context/EN_GHG_Econ_Canada.xlsx`
- Canada NIR 1990-2022 Part 2: https://unfccc.int/sites/default/files/resource/2024NIR%20-%20Part%202.pdf
