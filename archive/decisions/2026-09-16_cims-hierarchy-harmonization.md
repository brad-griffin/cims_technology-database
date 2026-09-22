# Harmonizing the design end uses with the CIMS hierarchy: proposal

**Status: revision 6, applied to the design table on 2026-09-16 and to
`cims_hierarchy.csv` on 2026-09-17 (744 rows became 648: the suggested paths, the 14
new nodes of section 4c, and parents rebuilt from the leaves). The hierarchy file now
sits in `design/`. The crosswalk now reads the restructured hierarchy, so its `suggested-branch`
column is empty.**

Applied: the table renames, removal and splits (section 2a); the generated
`cims-services` column (2b, via `build/cims_services.py`); Canadian spelling in the
design files (2c); the matching changes in `build/tech_rows.py`, `md_notes.py`,
`heat_source.py`, `md_head.md`, `md_tail.md` and the notes; and the end-use ids in
`data/harmonized/design_crosswalk.py`, whose review files were rebuilt. The files as
they were before are in `design/archive/pre-harmonization-2026-09-16/`.

Not applied:

- Technology data folders for the new and renamed nodes: only
  `general-services/steam` and `transportation-passenger` exist on disk, and the
  hierarchy's `data-filepath` values for new nodes follow the existing pattern
  (sector-specific, or `general-services/` for shared services).
- The harmonized layer's vocabulary spellings (`pasteuriser`, `fluidised-bed`,
  `electrolyser`, `aluminium`), which the design doc's section 6.2 and the harmonized
  technology names still use.
- The technology table's `cims-match` cells, which still use the model-input spelling
  except on the rows this pass rewrote.

Compared against `cims_hierarchy.csv` as saved 2026-09-16 13:51 PDT. Where the
hierarchy alone was ambiguous, the CIMS model inputs in `staging/cims`
(`service_request` targets) were checked to see which nodes request a service.

The governing rule is design rule 7: keep an end use at the most general aggregation
that still captures a real difference in energy use or in emissions; do not bundle when
the energy service differs, the emissions differ in kind or in abatement, or a policy
instrument treats them separately.

## Decisions recorded

Review of revision 1:

- The hierarchy keeps its `<sector>.product.*` / `<sector>.service.*` split. No
  suggested name may produce a confusing path such as `product.production`.
- Canadian spelling throughout (section 2c). `tailings-disposal`.
- Pulp and paper: option B (keep grades, one `forming` and one `drying` step each).
- `unassigned-energy` is removed from mining.
- Both coal-mining structures stay: they apply to different provinces.
- Natural gas keeps `extraction.shale` and `extraction.tight`.
- Natural-gas venting sources are grouped, but flaring stays a separate node because
  other source data separate them.
- Light industrial: one supplied-heat service.
- Add to the hierarchy: cokemaking, direct air capture, on-site power (mining),
  oil pipelines, produced water, effluent treatment, drying and low-temperature
  calcining, nitric acid, fermentation CO2 capture (section 4).
- Renewable natural gas, renewable diesel and SAF stay commodity-only for now.
- Ventilation is folded into space heating and cooling.
- Two glass end uses.
- `mobile-equipment` takes all mobile engines.
- Iron and steel: model how a process change would actually be made (section 3).
  This reverses revision 1's `molten-steel` merge.

Review of revision 2:

- Canadian spelling as set out in 2c.
- Mine ventilation (mining and coal mining) stays its own end use, not folded into HVAC.
- Haul fleets stay in their sector. The oil-field engines are stationary drives, so
  they become `direct-drive`, not `mobile-equipment` (2b).
- The design table splits `venting-and-flaring` into `venting` and `flaring` (2a).

Review of revision 3:

- Oil-sands mining gets its own fleet service, `petroleum-crude.service.mine-haulage`.
- `service.steam` keeps its name.
- Ethanol's corn and cellulosic routes collapse into one product node.
- Refinery distillation collapses; hot rolling has no flat/long split.
- Metal routes with no Canadian plant are pruned (4d).

Review of revision 4:

- The section 3 iron and steel restructure is adopted.
- A metal route is kept if a Canadian plant ran it at any time since 2000 (4d). This
  restores copper leaching, lead sinter-and-blast-furnace smelting, and all the
  magnesium routes.
- Every mine haulage node becomes a `mine-haulage` service, mirroring
  `petroleum-crude.service.mine-haulage` (4b).

Review of revision 5:

- Underground mining gets its own haulage node:
  `mining.service.mine-haulage.{open-pit, underground}` (4b).
- The Brunswick smelter made no zinc after 2000, so the zinc smelting and refining
  nodes are pruned. Zinc keeps the same structure as the other metals (4d).
- Potash solution mining's transportation node becomes `brine-transport`.

Review of revision 6 (2026-09-22), applied to the table, the hierarchy and the
crosswalk the same day; the files before it are in
`design/archive/pre-revision-7-2026-09-22/`:

- Light industrial gains `service.refrigeration`. `service.heat` carries the six
  food-and-beverage and other-industry heat end uses (part) and `service.refrigeration`
  carries food-and-beverage refrigeration. The seven product nodes become `demand`
  nodes: they request those services and carry no end use themselves. The
  light-industrial part of `heat-medium-temp` and `heat-high-temp` goes with it, since
  that heat is released in ovens, dryers, furnaces and presses (integral).
- `industrial-minerals.service.kiln-heat` covers both clinker and lime; its split
  across `clinker-production` and `lime-calcination` stands.
- Compressor drivers split by driver, as the hierarchy splits them: new end uses
  `compressor-drive-engine` and `compressor-drive-turbine`, each mapped whole to its
  node. Production, gas processing and gas pipelines keep the compression demand and
  reference the drivers through `draws-on`.
- `petroleum-crude.service.field-engines` maps whole to a new `field-engines` end use;
  drilling, production, in-situ bitumen and upgrading reference it through `draws-on`.
- Ethanol and biodiesel move into one `biofuels` hierarchy sector, with one product
  leaf per fuel: `biofuels.product.{ethanol, biodiesel, renewable-diesel-and-saf,
  renewable-natural-gas}` and one shared set of services. This reverses revision 1's
  commodity-only ruling for renewable natural gas, renewable diesel and SAF. Every
  design end use now has a hierarchy node.

## Summary

- The hierarchy has 353 leaves in the 15 industrial CIMS sectors, and all of them are
  placed: 294 map to an end use, 15 are supplied heat (the cross-sector bands), 5 are
  by-product fuel routing, 30 are fuel-blend nodes and 2 are feedstock inputs. 7 are
  removed: the 2 `unassigned-energy` leaves and 5 metal routes with no Canadian plant
  since 2000.
- The proposal adds 15 hierarchy nodes (section 4c).
- The design table goes from 86 to **91 end uses**. With the new nodes, 89 have at
  least one CIMS node; `renewable-natural-gas` and `renewable-diesel-and-saf` stay
  commodity-only.
- 168 of the 353 existing leaves get a suggested new path or removal.
- The full mapping is `design/cims-hierarchy-crosswalk.csv`, written by
  `design/build/hierarchy_crosswalk.py`. Each row gives the design end use, the
  suggested hierarchy path and the change to the table's `cims-services` cell. Re-run
  the script after every hierarchy change: a new or renamed leaf prints as
  `UNMAPPED`, and a proposed node flips from `proposed-new` to `existing` once it is
  added.

## 1. Naming

Case by case. The design id names the **service**, and must be unique across sectors
(the `draws-on` column refers to ids alone). A hierarchy node is named within its
parent and keeps the `product` / `service` split: a `product` node is named for what
the sector makes, a `service` node for what it supplies to other nodes. Where the
hierarchy name is a CIMS artefact, a single-technology name, or ambiguous, a new name
is suggested.

| Concept | Design table id | Hierarchy node now | Proposal |
| - | - | - | - |
| Pumps (MECS) | `pumping` | `service.machine-drive.pumps` | **Table → `pumps`** |
| Fans and blowers (MECS) | `fans-and-blowers` | `service.machine-drive.fans` | Hierarchy → `fans-and-blowers` |
| Kraft chemical recovery | `chemical-recovery` | `service.black-liquor` | Hierarchy → `service.chemical-recovery` |
| Steam cracking | `steam-cracking` | `product.other-petrochemicals.pyrolysis` | Hierarchy → `product.petrochemicals.steam-cracking` (`pyrolysis` also means biomass pyrolysis) |
| Merchant hydrogen | `centralised-hydrogen-production` | `hydrogen.product.process` | **Table → `centralized-hydrogen-production`**; hierarchy → `hydrogen.product.centralized-hydrogen` |
| Hydrogen distribution | `hydrogen-distribution` | `hydrogen.service.infrastructure` | Hierarchy → `hydrogen.service.distribution` |
| LNG | `lng-liquefaction` | `product.supply.lng-compression` | Hierarchy → `product.supply.lng-liquefaction` |
| Anodes | `anode-production` | `service.pre-bake-anode`, `service.soderberg-anode` | Hierarchy → one `service.anode-production` |
| Air separation | `steel-oxygen-supply`, `smelter-oxygen-supply` | `service.oxygen.cryogenics` | Hierarchy → `service.oxygen` (cryogenic is one technology; adsorption competes). Table keeps its prefixed ids for uniqueness |
| Pellets | `pelletising` | `open-pit.iron.agglomeration` | **Table → `pelletizing`**; hierarchy → `open-pit.pelletizing` (`agglomeration` is sintering in iron and steel) |
| Primary aluminum | `aluminium-smelting` | `aluminum.primary-aluminum.electrolysis` | **Table → `aluminum-smelting`** |
| Non-ferrous metallurgy | `pyrometallurgy`, `hydrometallurgy` | `metallurgy.pyro`, `metallurgy.hydro` | Hierarchy → `{metal}.pyrometallurgy`, `{metal}.hydrometallurgy` |
| Kiln fuel (cement, lime) | — | `industrial-minerals.service.heat` | Hierarchy → `service.kiln-heat` (requested only by the clinker and lime kilns) |
| Reheat furnaces | `reheating` | `service.reheating.reheators` | Hierarchy → `service.reheating` |
| Lime kiln (minerals) | `lime-calcination` | `product.lime.{kilns, dolomitic}` | Hierarchy → `product.lime.kiln`, as `ceramics.kiln`. Table keeps its id (`lime-kiln` is taken by pulp and paper) |
| Oil-field engines | — | `petroleum-crude.service.industrial-engines` | Hierarchy → `service.field-engines` (they are stationary drives, see 2b and 4b-2) |
| Everything else in the crosswalk | — | — | Names already agree, or the table name is kept and the hierarchy name reads correctly in context (`bitumen.in-situ`, `cement.clinker`) |

## 2. Proposed changes to the design table

### 2a. End uses

| Change | Now | Proposed | CIMS nodes | Why |
| - | - | - | - | - |
| Rename | `cross-sector/pumping` | `pumps` | `service.machine-drive.pumps` | MECS and hierarchy name |
| Rename (spelling) | `centralised-hydrogen-production`, `aluminium-smelting`, `pelletising` | `centralized-hydrogen-production`, `aluminum-smelting`, `pelletizing` | — | Canadian spelling |
| Remove | `cross-sector/ventilation` | — | — | Folded into `space-heating` and `space-cooling`: supply and exhaust air handling becomes part of the HVAC service |
| Keep | `ironmaking`, `steelmaking` | unchanged | see section 3 | Revision 1's merge is withdrawn |
| Split | `non-metallic-minerals/melting-and-firing` | `glass-melting` | `glass.preparation`, `glass.furnaces` | Glass melting (regenerative tanks at ~1500 °C, carbonate process CO2, oxy-fuel and electric boosting) and ceramic firing (tunnel kilns at ~1000 °C) have different technology sets. Mineral wool melting goes here |
| | | `glass-forming-and-finishing` | `glass.form-and-finish` | Forming, annealing lehrs (~550 °C) and tempering are a different energy service from melting |
| | | `ceramic-firing` | `ceramics.kiln` | Brick, tile and refractory firing |
| Split | `pulp-and-paper/mechanical-and-recycled-pulping` | `mechanical-pulping` | `pulp.pulping-mechanical` | Refiners use several times the electricity of repulping, with steam recovery; the technologies do not compete |
| | | `recycled-pulping` | `pulp.pulping-recycled` | Pulpers, deinking, screening |
| New | (in `chemical-pulping`) | `pulp-and-paper/wood-preparation` | `pulp.wood-preparation` | Debarking, chipping and log thawing serve every virgin-fibre route |
| New | (in `other-chemicals`) | `chemicals/nitric-and-adipic-acid` | `product.adipic-acid`, new `product.nitric-acid` | N2O process emissions, abated by catalytic destruction |
| Split | `oil-and-gas/venting-and-flaring` | `venting` | `supply.venting.*` (with controls, blowdowns, liquid unloading), `natural-gas.service.pumping` | Other source data report venting and flaring separately, and the hierarchy keeps them apart. Technologies: gas-driven pneumatic controllers and pumps; instrument air or electric actuation; vapour recovery; plunger lift and smart liquids unloading; blowdown gas recompression; enclosed combustor. Draws on `compressed-air` (vapour recovery and instrument air) |
| | | `flaring` | `supply.flaring` | Solution-gas and process flaring. Technologies: flare with continuous pilot; flare gas recovery; high-efficiency flare. Draws on `integral` (flare pilots and purge gas) |

`mining/ventilation-and-air-heating` stays: underground ventilation is a production
service, not building HVAC. The model's `Mining.Ventilation` and
`Coal Mining.Ventilation` services turned out to hold the same eight fan technologies
as the shared machine-drive fan service (airfoil, backward-inclined, radial,
vane-axial), so they are fans, not a separate service: no sector ventilation service
was added on 2026-09-17, the coal mine-air duty stays the product step
`raw-product.mine-ventilation`, and the fan technologies stay shared. Metal mining has
no mine-air duty node, which the design table records as a gap.

The venting split divides two technology rows: "Vapour recovery and flare gas
recovery" becomes vapour recovery (venting) and flare gas recovery (flaring), and
"Enclosed combustor or high-efficiency flare" becomes enclosed combustor (venting: it
destroys tank and process vapours that would otherwise be vented) and high-efficiency
flare (flaring). The 2026-09-15 note that "flaring competes with venting as a
destruction route" is retired; the enclosed combustor now carries that competition
inside `venting`.

**Cascade.**

- Renaming `pumping` changes 18 `draws-on` links; `centralised-hydrogen-production`
  has 1.
- The other renames, the removal and the splits (including `venting-and-flaring`) retire ids that
  `build/tech_rows.py`, `build/md_notes.py` and `build/heat_source.py` key on, so
  those dicts change in the same pass.
- The splits need their technology rows divided.
- Two `md_notes` notes contradict the decisions and need rewording:
  - `oil-and-gas-production` ("Field compressor drives are machine drive")
  - `ironmaking` ("CIMS does not split ironmaking from steelmaking"), which stops
    being true under section 3.

### 2b. Corrections to `cims-services`

Every part of every cell is rewritten as a hierarchy path so the crosswalk script can
check it. The substantive corrections:

| End use | Remove | Add | Why |
| - | - | - | - |
| `cement/clinker-production`, `non-metallic-minerals/lime-calcination` | — | `industrial-minerals.service.heat` (part each) | In the model it is requested only by the dry-process kiln and the lime kilns: integral kiln fuel |
| `non-metallic-minerals/melting-and-firing` (split), `drying-and-low-temp-calcining` | `Industrial Minerals.Heat (part)` | `drying-and-low-temp-calcining`: new `ceramics.dryer`, `gypsum` | As above |
| `oil-and-gas/oil-and-gas-production` | `Supply.Controls`, `Blowdowns`, `Liquid Unloading`, `Supply.Pumping` | `supply.direct-drive` (part) | Stale after the venting split. Direct drive is the compressor driver for extraction, processing and transmission compression |
| `oil-and-gas/gas-processing`, `gas-pipelines` | `Supply.Processing` (no such leaf) | `supply.direct-drive` (part) | As above |
| `oil-and-gas/venting` (new) | — | `supply.controls`, `supply.venting.*`, `testing-and-maintenance.{blowdowns, liquid-unloading}`, `supply.pumping` | Pumping is requested by processing and transmission, not production. Its technologies are pneumatic vs electric pumps, so it is a venting substitution like the pneumatic controllers |
| `oil-and-gas/flaring` (new) | — | `supply.flaring` | |
| `cross-sector/pumps` | `Natural Gas.Production.Supply.Pumping` | — | As above |
| `cross-sector/compressed-air` | `Supply.Extraction.Compression` | — | Gas-field compression is not plant air; it stays with production |
| `drilling-and-well-services`, `oil-and-gas-production`, `in-situ-bitumen`, `bitumen-upgrading` | — | `petroleum-crude.service.industrial-engines` (part each) | Stationary drives, not vehicles: the technologies have a 20-year life and a capital cost per GJ of shaft work, half the stock runs on propane (typical of wellsite engines), and they are requested per well drilled, per m3 produced, and by upgraders and in-situ plants, which run no vehicle fleets at that intensity. Drilling rigs are diesel-engine driven (drawworks, mud pumps, generators), so the drilling share fits direct drive. The oil-sands mining request (0.16 GJ/m3) is treated as the mine fleet and moves to its own service |
| `oil-and-gas/oil-sands-mining-and-extraction` | — | new `petroleum-crude.service.mine-haulage` | The mine fleet, requested by `bitumen.mining` in place of its engine request. Haul fleets stay in their sector |
| `oil-and-gas/in-situ-bitumen` | `Petroleum Crude.Steam` | — | Steam generators are supplied heat (rule 3); in-situ draws on the bands |
| `non-ferrous-metals/electric-smelting` | `Titanium.Metallurgy.*` | `titanium.metallurgy.pyro.*` | Titanium hydro belongs to `hydrometallurgy` only |
| `mining/ventilation-and-air-heating` | `Mining.HVAC.Space Heating`, `Coal Mining.HVAC.Space Heating` | `coal-mining.product.raw-product.mine-ventilation`; new `mining.service.ventilation`, `coal-mining.service.ventilation` | The model's mining space-heating technologies are generic space heaters, so they stay with `space-heating` |
| `mining/water-and-tailings-management` | "none" | the four `tailings-disposal` leaves | Moved from `separation-and-processing` |
| `cross-sector/space-heating`, `space-cooling` | `Light Industrial.Water Heating (space duties)`; `…HVAC.Ventilation AC` parts | `light-industrial.service.hvac` (part each) | Water heating is requested by all seven light-industry products: process hot water, so `heat-low-temp` |
| `other-industry/drying-curing-and-forming` | `Light Industrial.Heat.Indirect (part)` | — | Merged into light-industry supplied heat |
| `hydrogen/hydrogen-distribution` | "none" | `hydrogen.service.infrastructure` | Requested by hydrogen production |
| `cross-sector/co2-capture-concentrated` | — | `hydrogen.service.ccs` | Hydrogen: requested by production (process CO2). Ethanol fermentation capture was proposed as `ccs_fermentation` and dropped on 2026-09-18: ethanol keeps one `service.ccs` |
| `other-industry/metal-melting-and-heat-treatment` | — | `iron-and-steel.product.foundry` | The row already covers foundry melting |
| `biofuels/renewable-natural-gas`, `renewable-diesel-and-saf` | `Natural Gas.OG Methane Blend; <sector>.Methane Fuel`; `Fuel Blends.Diesel_Industrial` | `common-energy.renewable-natural-gas`; `common-energy.renewable-diesel`, `common-energy.saf` | Commodity-only. Fuel-blend nodes blend a commodity into supply; they are not production |
| Rows with no CIMS node today | "none" | the new nodes in section 4 | `cokemaking`, `direct-air-capture`, `on-site-power-generation`, `oil-pipelines`, `produced-water-handling`, `effluent-treatment` |

### 2c. Canadian spelling

Canadian usage, as in the Canadian Press style and the Canadian Oxford Dictionary (confirmed):

- `-ize` / `-ization`: `centralized`, `pelletizing`, `fluidized`, `optimization`,
  `crystallization`
- `aluminum`
- `-our`, `-re` (`fibre`, `centre`)
- `sulphur`

The hierarchy already follows this, apart from the typo `crystalization`
(→ `crystallization`) and `tailing-disposal` (→ `tailings-disposal`).

The design files do not. There are about 390 `-ise` / `-isation` / `aluminium` forms
across both CSVs, the build scripts, `md_head.md`, `md_tail.md`, the notes, and
`industrial heat technology database design.md`. The most common are `centralised`,
`aluminium`, `pelletising`, `fluidised`, `pressurised`, `galvanising`,
`optimisation` and `economiser`.

Some are in technology names (`fluidised-bed`), so the sweep also touches harmonized
technology ids and the section 6.2 vocabulary. It should be one scripted pass with a
word list, not a blind `-ise` → `-ize` replace: `raise`, `precise` and `premise` must
not change.

## 3. Iron and steel: one end use or two? (adopted)

The question is which modelling choice best represents how a plant would actually
change process. The routes differ in how tightly the iron step is tied to the steel
step:

| Route | Iron step | Steel step | How tightly coupled |
| - | - | - | - |
| BF-BOF | Blast furnace, fed by coke ovens and sinter | BOF | Tight. The BOF needs liquid hot metal (about 75–90% of its charge), and the site gas balance (BF, coke-oven and BOF gas) runs through reheating and steam |
| Smelting reduction-BOF (HIsarna, Corex, Finex) | Smelting vessel | BOF | The smelter replaces the blast furnace but still supplies hot metal, so the **BOF is kept** |
| DRI-EAF | Shaft furnace (natural gas or hydrogen) | EAF | Loose. DRI and HBI are solid, storable and traded, and an EAF can run on any mix of DRI, scrap and pig iron |
| DRI-electric smelter-BOF | Shaft furnace, then an electric smelting furnace | BOF | The route several European integrated mills are taking: the blast furnace is replaced and the **BOF is kept** |
| Recycled EAF | None (scrap) | EAF | No iron step. The EAF is the same furnace as in DRI-EAF, with a different charge |

So combining the two steps suits BF-BOF, but not the others. Three of the transition
routes swap the iron step and keep the steel furnace, or keep the furnace and change
its charge. A combined end use can only show them as whole-route technologies. That
hides the fact that the BOF (or EAF) stock is kept, and it multiplies the routes
(BF-BOF, BF-BOF-CCS, SR-BOF, DRI-ESF-BOF, DRI-EAF, scrap-EAF, mixed-charge EAF, …).

Stock turnover also differs: a blast furnace is replaced or abandoned at a reline,
while the BOF shop runs on. Separate nodes let CIMS retire the two on their own
schedules.

What does couple the steps is the **physical form of the iron**: liquid hot metal for
the BOF, solid DRI or scrap for the EAF. That coupling can be written into the service
requests instead of into route technologies.

**Adopted.** Keep `ironmaking` and `steelmaking` as separate design end uses, and
restructure the hierarchy by iron form:

| Node | Technologies | Requests | Design end use |
| - | - | - | - |
| `iron-and-steel.product.molten-steel` | BOF; EAF on scrap; EAF on DRI (or charge-mix variants) | `service.hot-metal` (BOF); `service.direct-reduced-iron` (DRI-EAF); scrap (commodity); `service.oxygen`; `service.ladle-preheating`; `service.ladle-refining` | `steelmaking` |
| `iron-and-steel.service.hot-metal` (new) | Blast furnace (with top-gas recycling, hydrogen or gas injection, CCS variants); HIsarna; Corex/Finex; electric smelting furnace | `service.coke`, `service.agglomeration` (BF); `service.direct-reduced-iron` (electric smelter); `service.oxygen` | `ironmaking` |
| `iron-and-steel.service.direct-reduced-iron` (new) | Shaft furnace on natural gas, hydrogen, natural gas with CCS | Pellets (commodity, or `mining…pelletizing`) | `ironmaking` |
| `iron-and-steel.service.coke` (new) | By-product coke ovens, heat-recovery ovens | — (purchased coke stays a commodity) | `cokemaking` |
| `iron-and-steel.service.agglomeration` | Sinter plant | — | `agglomeration` |
| `iron-and-steel.service.fuel-blend_process-gas` | Routes blast-furnace, coke-oven and BOF gas | — | (fuel routing, G4) |

- Today's `molten-steel.integrated` route technologies split across the three new
  nodes; `molten-steel.recycled` becomes the scrap-EAF technology.
- The scrap-availability bound moves from a node to a market-share limit on that
  technology.
- `continuous-cast.ladle-preheat` and `ladle-refining` move to `service.*`, requested
  by every steelmaking technology.

## 4. Suggested changes to cims_hierarchy

Collapsing product nodes means the parent's `service_request` becomes the
output-weighted sum of the children's, as was done for glass. Where the children carry
separate demand drivers, they stay.

### 4a. General

**G1. Shared data for HVAC and lighting.** Point `service.hvac.space-heating`,
`service.hvac.space-cooling` and `service.lighting` at `general-services/`, as steam
and machine drive already are.

- **What stays in each sector:** the service nodes in the model. Each sector keeps its
  own branch (`<sector>.chemicals.service.hvac.space-heating`), demand, calibration
  and market shares.
- **What moves:** only `data-filepath`. The processed technology data is kept once,
  exactly as `<sector>.chemicals.service.steam` → `general-services/steam` works
  today.
- **Residential and commercial are separate.** Residential heating is structured by
  building type, vintage and shell, and commercial by climate zone. Their equipment
  (furnaces, boilers, rooftop units) and demand drivers differ from industrial unit
  heaters, radiant tubes and make-up air units.
- **Borrowing buildings data:** the industrial `general-services/hvac/space-heating`
  folder would serve the industrial sectors only. Where a buildings technology is a
  fair proxy, the README's `ref` value type can point to it without merging the
  folders. Commercial is the closer proxy.

**G2.** `machine-drive.fans` → `machine-drive.fans-and-blowers` (MECS name).

**G3.** Drop the lone `.process` child: `chemicals.product.adipic-acid`,
`hydrogen-peroxide`, `sodium-chlorate`. Hydrogen's `product.process` is renamed
`product.centralized-hydrogen`, not dropped, since `hydrogen.product` is a grouping
level.

**G4. By-product fuel routing.** Replace these with
`service.fuel-blend_process-gas` and `service.fuel-blend_still-gas` feeding the
ordinary `reheating`, `steam` and `direct-heat` nodes:

- `iron-and-steel.service.iron-process-gas.{reheating, steam}`
- `petroleum-refining.service.still-gas.{heater, steam}`
- `petroleum-crude.service.still-gas-steam`

These nodes route a by-product fuel, and the service is the same as the node beside
them. The by-product use constraint moves to the fuel-blend node.

**G5. Flatten single-child levels:**

- `natural-gas.product.transmission.compression` → `transmission`
- `supply.processing.compression` → `processing`
- `oxygen.cryogenics` → `oxygen`
- `reheating.reheators` → `reheating`
- `cement.portland-cement.*` → `cement.*`
- `other-petrochemicals.petrochemicals.*` → `petrochemicals.*`
- `alkylates.isoparaffins.isomerization` → `product.isomerization`, beside
  `product.reforming`; `alkylates.alkylation` → `product.alkylates`
- Flattened on 2026-09-17: `industrial-minerals.product.lime.kiln` → `lime`,
  `light-industrial.service.heat.direct` → `service.heat`,
  `petroleum-refining.product.alkylates.alkylation` → `alkylates`.
  `metal-smelting.product.zinc.pyrometallurgy.roasting` keeps its level (the user)

**G6. Services named as products.**

- `natural-gas.product.supply.{direct-drive, ccs, pumping}` → `natural-gas.service.*`.
  Each is requested by other nodes, so it is a service under the product/service split.
- Light industrial: `service.heat.indirect` and `service.water-heating` merge into
  `service.steam`, the one supplied-heat service (`heat.direct` stays).
- `service.steam` keeps its name, though it also covers hot water and thermal oil.

### 4b. By sector

| Sector | Now | Suggested | Why |
| - | - | - | - |
| industrial-minerals | `clinker.{dry-process-rotary-kiln, fluidized-bed}` | `cement.clinker` | Kiln types compete as technologies |
| | `dry-ground-cement`, `finish-grinding` | `cement.grinding` | One service: mill drives |
| | `lime.{kilns, dolomitic}` | `lime` | Dolomitic is a grade; process CO2 differs in size, not kind. Flattened onto `lime` on 2026-09-17: the kiln node was the only child, so no competition happened at `lime` |
| | `product.glass.preparation` | folded into `product.glass.furnaces` (2026-09-18) | Batch weighing, mixing and cullet handling is generic machine drive, and batch preheating is a furnace-efficiency measure |
| | `service.heat` | `service.kiln-heat` | Requested by the dry-process clinker kiln and one lime technology. **Note (2026-09-17):** the other ~20 lime kilns request their fuel directly (`Methane Blend`, thermal coal, petcoke, heavy fuel oil), so `kiln-heat` is not yet the fuel-choice service its name implies. The name stays; the service requests are to be revisited when the sector is reviewed |
| iron-and-steel | see section 3 | | |
| | `{slabs.casting, billets.billet-casting, blooms.bloom-casting}` | `continuous-cast.casting` | Casting methods generalize (rule 7's own example) |
| | `slab-roughing.roughing-mills`, `slab-finishing.finishing-mills`, `billets.{bar, rod, light-structural-shapes}`, `blooms.{heavy-structural-shapes, tubes}` | `continuous-cast.hot-rolling` | Same service and technologies; no flat/long split |
| | `cold-rolled.{cold-roll, skin-pass}`, `pickled-slabs`, `electroclean.electrocleancomp` | `continuous-cast.cold-rolling` | Pickling, rolling and cleaning line |
| | `electroclean.{anneal-temper, electric-steel, tin-plate}`, `cold-rolled.galvanize` | `continuous-cast.annealing-and-coating` | `electroclean` is not a real step above annealing and coating |
| chemicals | `ammonia-methanol.{ammonia-synthesis, methanol-synthesis}` | `ammonia-methanol.{ammonia, methanol}` | Drop the suffix |
| | `ammonia-methanol.combined-ammonia-methanol-synthesis` | Remove; allocate to `ammonia` and `methanol` by output | A plant configuration, not a service |
| | `chlor-alkali.caustic-sodium.{caustic-process, chlor-alkali-evaporation}` | `chlor-alkali.caustic-evaporation` | One steam-driven concentration step |
| petroleum-refining | `hydrocracking.{cracking, high, medium, low}` | `hydrocracking` | Severity is a process variant |
| | `distillation.{atmospheric, vacuum}` | `distillation` | Same heater and column technologies; the atmospheric-to-vacuum throughput ratio goes into the weighted service request |
| pulp-and-paper | `pulp.bleached.washing.raw.*` chain | `pulp.{wood-preparation, pulping-chemical, pulping-semi-chemical, pulping-mechanical, pulping-recycled, washing, bleaching, drying}` | The chain encodes flow, not services, and hides that wood preparation serves every route |
| | `log-preparation.{cut-and-chip, debark}` | `pulp.wood-preparation` | One motor-driven service |
| | `bleaching.{fully, semi}` | `pulp.bleaching` | Grade |
| | `paper.{grade}.{grade}-stock-prep`, `…-forming-pressing-finishing`, `…-drying` | `paper.{grade}.forming`, `paper.{grade}.drying` (option B) | Stock prep and forming are one motor-driven service (newsprint already combines them). Grades keep their own demand and drying intensity |
| | `service.black-liquor.concentrated-black-liquor.*`, `black-liquor.evaporator` | `service.chemical-recovery.{evaporator, recovery-furnace, lime-kiln}` | Name the service, flatten |
| mining | `open-pit.{iron, non-iron}.{primary-crushing, secondary-crushing, raw-product.extraction}` | `open-pit.{crushing, milling, extraction}`, `open-pit.pelletizing` | Same equipment; only pelletizing is iron-specific |
| | `underground.processing.{primary-crushing, secondary-crushing, primary-milling, raw-product.extraction}` | `underground.{crushing, milling, extraction}` | Same collapse; `processing` is a single-purpose level |
| | `open-pit.{iron, non-iron}.raw-product.transportation` | `mining.service.mine-haulage.open-pit` | Mirrors `petroleum-crude.service.mine-haulage`. Haul trucks (diesel, trolley-assist, battery-electric) and in-pit conveyors |
| | `underground.processing.raw-product.transportation`, `potash…conventional-mining.transportation` | `mining.service.mine-haulage.underground` | Underground haulage has its own equipment: load-haul-dump machines, underground trucks, hoists and conveyors, where ventilation limits diesel and battery-electric equipment competes differently. Saskatchewan conventional potash mines are underground, so their haulage goes here. The model now gives both nodes the same three technologies (diesel truck, biodiesel truck, conveyance); the split leaves room for underground-specific technologies |
| | `potash…solution-mining.transportation` | `potash…solution-mining.brine-transport` | Not haulage: its one technology is a brine pipeline, which requests conveyance and pumping. Stays a product step (decided) |
| | `open-pit.unassigned-energy`, `underground.unassigned-energy` | Remove (allocate first) | Not a service |
| | `tailing-disposal`, `potash.processing.crystalization` | `tailings-disposal`, `crystallization` | Spelling |
| coal-mining | `size-reduced-product.{primary-crushing}`, `{primary, secondary}-milling` | `size-reduced-product.{crushing, milling}` | Stages of one service |
| | `metallurgical-finishing.washing` | `coal-preparation.washing` | The wash mill, on electricity. The branch is renamed because it was reading as if only metallurgical coal were produced: it is in the AB and BC files only, but thermal coal is modelled, with SK lignite stopping at `size-reduced-product` and NB and NS on the simplified nodes |
| | `metallurgical-finishing.cleaning` | `coal-preparation.drying` | Thermal drying: rotary, spray and fluidized-bed dryers on gas, coal or electricity. It stays separate from the wash mill (a different energy service and different emissions) and maps to `mining/product-drying`, beside potash drying |
| | `metallurgical-finishing.tailings-disposal` | `coal-preparation.tailings-disposal` | Follows the rename |
| | `product.raw-product.mine-ventilation` | unchanged | The mine-air duty, per tonne of coal; its fans are the shared machine-drive fan service |
| | `product.raw-product.transportation` | `coal-mining.service.mine-haulage` | Mirrors petroleum crude and mining; same three technologies |
| | `simplified-*` and `raw-product.*` | Keep both | They apply to different provinces |
| natural-gas | `supply.controls`, `testing-and-maintenance.{blowdowns, liquid-unloading}`, `venting.{point-venting, diffuse-venting}` | `supply.venting.{controls, blowdowns, liquid-unloading, point-venting, diffuse-venting}` | All vent gas; the abatement options are equipment substitutions |
| | `supply.flaring` | unchanged, beside `supply.venting` | Separate in other source data |
| | `testing-and-maintenance.well-tests` | `supply.extraction.well-tests` | Completes the move out of `testing-and-maintenance` |
| | `supply.lng-compression` | `supply.lng-liquefaction` | Names the service |
| | `extraction.{shale, tight}` | unchanged | |
| petroleum-crude | `service.industrial-engines` | `service.field-engines` | Stationary drives (see 2b); renamed again 2026-09-18, see 4b-2 |
| | `product.bitumen.mining` engine request | new `service.mine-haulage` | The mine fleet gets its own service, so direct drive holds only stationary engines |
| metal-smelting | `service.{pre-bake-anode, soderberg-anode}` | `service.anode-production` | Both requested by electrolysis only; the Söderberg node holds a placeholder technology. Keep Söderberg as a technology under the merged node: Söderberg potlines ran in Canada after 2000 (Kitimat before its 2015 modernization, among others), so the base-year calibration needs it |
| | `{metal}.metallurgy.pyro.process.{continuous, conventional.{smelt, convert}}` | `{metal}.pyrometallurgy.smelting` | Continuous vs conventional are competing routes, so technologies; converting is part of matte smelting |
| | `{metal}.metallurgy.pyro.process.conventional.roast`, `pyro.refine` | `{metal}.pyrometallurgy.roasting`, `.refining` | Roasting (SO2 to acid plant) and refining are distinct steps |
| | metal and route pairs with no Canadian plant | Prune (4d) | |
| light-industrial | `service.hvac` | `service.hvac.{space-heating, space-cooling}` | Consistent with the other sectors; ventilation folds into both |
| ethanol | `product.{corn, cellulosic}` | `product.fermentation`, with corn and cellulosic as technologies | Competing routes to one product; named for the process, as `biodiesel.product.transesterification` is |

### 4b-2. Changes of 2026-09-18

**Machine drive pruned to what each sector's model file has.** The five MECS children
were given to every industrial sector; the model does not carry them everywhere:

| Sector | In the model | In the hierarchy now |
| - | - | - |
| chemicals, coal-mining, industrial-minerals, iron-and-steel, metal-smelting, mining, pulp-and-paper | Compression, Conveyance, Machine Drive, Pumping, Ventilation, Direct Drive | the five MECS children only |
| petroleum-refining | Compression, Machine Drive, Pumping, Ventilation | the four; `materials-handling` removed |
| light-industrial | one undifferentiated `Motive Power` | one `service.machine-drive` leaf, no children |
| natural-gas | Compression, Pumping, Direct Drive (sized) | `service.machine-drive.pumps`, `service.direct-drive`, and gas compression in the supply chain |
| ethanol, biodiesel, hydrogen, petroleum-crude, construction | none | none |

CIMS's `Direct Drive` service is motor speed control and drive type (V-belt against
variable speed). It is not a service competing with the motors: a plant buys both. So
it is not carried as a node; it is an efficiency variant of the motor technologies,
which the technology table already holds ("variable-speed drive", "premium-efficiency
motor") on each machine-drive end use. Machine drive is simplified to the nodes the
hierarchy lists. Natural gas and petroleum crude keep `service.direct-drive`: theirs
are gas turbines and engines driving compressors and field equipment, a fuel choice
rather than a motor accessory, and they map to the oil-and-gas end uses.

**Natural gas.** `extraction` holds resource types only; `gas-compression`, `drilling`,
`well-tests` and `off-road-transport` moved up beside it. Gas compression is not MECS
compressed air, so it is named for what it is rather than filed under machine drive.
`supply.pumping` is the MECS pump service and moved to `service.machine-drive.pumps`:
its pneumatic-against-electric choice is now a technology attribute, so the methane it
vents is recorded there rather than in the `venting` end use, which keeps the pneumatic
controllers. The two venting nodes became `other-point-venting` and
`other-diffuse-venting`, since the other three children name equipment and these two
are the residual inventory categories.

**Mining restructured.** Products are commodity by mine type and the process steps are
services the products request, so adding a commodity is one product node plus its
service requests rather than a new chain of steps:

- `product.{metal, potash, uranium, diamond, aggregate}.{open-pit, underground, conventional, solution}`
- `service.{extraction, mine-haulage.{open-pit, underground}, crushing, milling,
  separation, leaching, crystallization, compaction, pelletizing, drying,
  tailings-disposal}`

Dissolution folds into `crystallization` (both are the potash solution circuit, and
nothing else requests dissolution) and brine transport is dropped: its one technology
is a pipeline, so the solution product node requests the shared pump service.
`crushing` and `milling` stay apart although they are one end use - grinding is ten to
twenty kWh/t against a couple for crushing, and it is where the technology choice
bites.

The mining end uses now map onto the services almost one to one. Uranium, diamond and
aggregate have no data in the model files yet; potash keeps dissolution,
crystallization, compaction and brine transport, iron keeps pelletizing, and uranium
adds leaching.

**CCS split by stream (2026-09-18).** CIMS prices one `CCS` service per sector
however pure the stream is, so a sector with both a process stream and a flue-gas
stream gets one price for both: chemicals is costed as concentrated (1.0 GJ/t, $153
per t-per-yr) while its boilers request the same service, and refining, iron and
steel and petroleum crude are costed as dilute (3.4-4.8 GJ/t, $514-692) while their
reformers request it. Each sector's node is now named for its stream:

| Sector | Nodes |
| - | - |
| chemicals, iron-and-steel, petroleum-refining, petroleum-crude, natural-gas | `service.ccs.{concentrated, diffuse}` |
| hydrogen | `service.ccs.concentrated` |
| industrial-minerals, ethanol, biodiesel | `service.ccs.diffuse` |
| electricity | `service.ccs.{diffuse_biomass, diffuse_coal, diffuse_natural-gas}` - post-combustion on flue gas, with the fuel kept so the parasitic energy stays right |

Composite names are nested rather than joined with `_` (the user, 2026-09-18):
`service.ccs.{concentrated, diffuse}` and `service.fuel-blend.{diesel, gasoline,
methane, process-gas, still-gas}`, across every sector including the ones outside the
industrial scope. That sometimes leaves a parent with one child, which is accepted as
the price of a consistent shape. Every capture end use now maps to whole services rather than parts of one. Natural
gas keeps `product.supply.formation-co2`: it is the CO2 in the raw gas and the
capture-or-vent decision at the plant, so it maps to `gas-processing`, and its
`Formation CCS` technology requests the concentrated service. The two cost sets still
have to be entered.

**`bricks` renamed `ceramics` (the user, 2026-09-18).** Brick, structural tile,
sanitaryware and refractories are fired in the same periodic and tunnel kilns on the
same fuels, so the branch is named for the product family rather than one of its
products: `industrial-minerals.product.ceramics.{kiln, dryer}`. Nothing else moves -
the two design end uses (`ceramic-firing`, `drying-and-low-temp-calcining`) and the
technology rows are unchanged apart from the path. Whether the family is large enough
to keep its own branch in every province is still unverified; NRCan's NAICS 3271
industrial energy series is the place to settle it.

**Magnesium simplified, and titanium renamed for its product (the user,
2026-09-18).** The magnesium branch carried zinc's technology list verbatim - the same
leaching, roasting and electrolytic-refining names - so it was spending real magnesium
demand on zinc equipment. CIMS already represents the industry's history correctly on
the demand side: the sector share falls year by year from 2000 and flattens at 2007 in
every province (Quebec 1.03% in 2000, 0.72% in 2003 when Magnola closed, 0.109% from
2007 when Norsk Hydro Becancour closed), so only the technology side needed fixing.

| Was (7 nodes) | Now (4 nodes) |
| - | - |
| `magnesium`, `.hydrometallurgy`, `.melt-cast`, `.pyrometallurgy`, `.pyrometallurgy.{roasting, smelting, refining}` | `magnesium`, `.electrolysis`, `.thermal-reduction`, `.melt-cast` |

`.electrolysis` is the molten-salt MgCl2 cell (Magnola to 2003, Norsk Hydro Becancour to
2007) and takes the old `pyrometallurgy.refining` node's SF6 cover-gas factor of
0.001565 t per unit; `.thermal-reduction` is the silicothermic retort (Timminco Haley,
to about 2008). Leaching and roasting go: magnesium is made by neither.

`melt-cast` stays, and is the reason the post-2007 residual is not an error. It carries
an SF6 factor of 0.007804 t per unit - five times the cell factor - and casting and
alloying continue after primary production ends, which is the magnesium emission the
National Inventory Report keeps reporting. This is what the rule recorded in 4d
("melt-cast nodes stay for every metal, since casting and alloying plants exist
independently of primary production") was protecting.

**Gap to close:** the SF6 factors are present only in the Alberta and Ontario model
files. Quebec, British Columbia and Manitoba carry a magnesium demand share with no
emission factor at all, so their casting emissions are currently zero. Quebec is the
province that mattered most for magnesium, so its factor is the first to add.

Titanium is renamed `metal-smelting.product.titanium-slag`, a product name like the other
branches. Rio Tinto Fer et Titane smelts ilmenite to slag and upgrades it by roast and
leach; no titanium metal has been made in Canada. `melt-cast` is dropped - slag is
tapped, not cast - and the remaining nodes map to `non-ferrous-metals/electric-smelting`
as before. Its pig iron (about 1 Mt/yr) is taken as a co-product carrying no energy of
its own: one furnace makes both, the reductant CO2 belongs to the ilmenite reduction,
and the same reasoning already recorded for ferroalloys ("the energy use is electric
smelting, not steelmaking") applies. The iron appears on the demand side as foundry
feed. The branch still has no demand series - a single `0.0` with no year - so
Sorel-Tracy and Ferroglobe Becancour remain absent from the model until one is added.

**Natural gas compressor drives split by prime mover (the user, 2026-09-18).**
`service.direct-drive` becomes `service.compressor-drive.{engine, turbine}`. The model's
`Direct Drive Small` and `Direct Drive Large` are not a competition: `Compression` and
`Compression Efficient` both request both sizes, at shares that are the same in all
fifteen provincial files and differ only by node - 94.8/5.2 at extraction, 68.5/31.5 at
processing, 26.1/73.9 at transmission (`Compression Efficient` is a flat 0.8 multiplier
on every request, so it is an efficiency variant rather than a second driver). The split
is therefore an exogenous allocation of duty between two drive fleets, and it is kept:
the compression nodes go on requesting shares of each, and the nodes are named for the
prime mover the fleet is built around rather than for size, since `direct-drive` now
means the motor speed-control accessory everywhere else.

| Node | Technologies (per unit of drive service) | Life |
| - | - | - |
| `service.compressor-drive.engine` | Reciprocating compressor 5.679 GJ methane, $161 capital, $16 fixed O&M; Efficient 5.110 GJ, $200; Electric 2.152 GJ electricity, $242, $8 | 10 yr |
| `service.compressor-drive.turbine` | Natural gas turbine 3.85 GJ methane, $116, $12, with vintage steps 2.82 / 2.67 / 2.60 at unchanged capital; Std AC motor 500 hp 1.064 GJ electricity, $175, $6; Eff AC motor 1.053 GJ, $188 | 30 yr |

Each fleet carries its own electrification alternative, which is the point of keeping
them apart: electrifying field reciprocating compression is a different proposition
from electrifying mainline turbine stations, on cost, on service life and on where the
duty sits. Note that the gas figures are fuel into a prime mover while the electric
figures are delivered electricity, so the gap between them is mostly the site boundary
moving to the generator, not drive efficiency.

**`petroleum-crude.service.direct-drive` renamed `service.field-engines` (the user,
2026-09-18).** CIMS's `Petroleum Crude.Industrial Engines` carries three technologies
- diesel, gasoline and propane - and is requested by nearly every production node:
exploration and drilling, light-medium onshore and offshore, heavy, all four in-situ
bitumen routes, bitumen mining and upgrading. It is a site-wide stationary engine
fleet whose only competition is fuel, not the motor-accessory `Direct Drive` that the
other seven sectors carried, so it keeps a node of its own under a name that says so.

### 4c. Nodes to add

| New node | Design end use | Notes |
| - | - | - |
| `iron-and-steel.service.coke` | `iron-and-steel/cokemaking` | Requested by the blast furnace. Purchased coke stays `common-energy.coke` |
| `iron-and-steel.service.hot-metal`, `service.direct-reduced-iron` | `iron-and-steel/ironmaking` | Section 3 |
| `industrial-minerals.product.ceramics.dryer` | `non-metallic-minerals/drying-and-low-temp-calcining` | Green-ware drying, often on kiln waste heat |
| `industrial-minerals.product.gypsum` | `non-metallic-minerals/drying-and-low-temp-calcining` | Stucco calcining and wallboard drying |
| `chemicals.product.nitric-acid` | `chemicals/nitric-and-adipic-acid` | N2O; fertilizer-linked |
| `direct-air-capture.product.co2-removal` (new sector, beside `transmission.co2-pipeline-and-storage`) | `cross-sector/direct-air-capture` | DAC serves no single industrial sector |
| `mining.service.on-site-power` | `cross-sector/on-site-power-generation` | Off-grid metal mines (northern regions). Offshore platforms are the other candidate; oil-sands cogeneration is CHP, so it stays on the heat bands |
| `petroleum-crude.product.transmission` | `oil-and-gas/oil-pipelines` | Mirrors `natural-gas.product.transmission`; pump-station drives |
| `petroleum-crude.service.produced-water` | `oil-and-gas/produced-water-handling` | Requested by `heavy`, `light-medium.*` and `bitumen.in-situ` (in-situ water treatment and recycling) |
| `pulp-and-paper.service.effluent-treatment` | `pulp-and-paper/effluent-treatment` | Aeration and pumping |
| `petroleum-crude.service.mine-haulage` | `oil-and-gas/oil-sands-mining-and-extraction` | Mine fleet: diesel haul trucks, and trolley-assist or battery-electric alternatives. Requested by `product.bitumen.mining` |

### 4d. Metal routes to prune

A route is pruned only if no Canadian plant has run it since 2000, the model's base
year. Routes whose plants closed after 2000 stay, so the historical calibration has a
node for them. `melt-cast` nodes stay for every metal, since casting and alloying
plants exist independently of primary production.

| Metal | Keep | Prune | Canadian basis, 2000 to 2026 |
| - | - | - | - |
| aluminum | alumina, electrolysis, recycle | — | Vaudreuil alumina refinery; Quebec and B.C. smelters |
| copper | `pyrometallurgy.smelting`, `.refining`; **`hydrometallurgy`** | — | Horne smelter (Rouyn-Noranda) and the CCR refinery (Montréal); Kidd Creek and Flin Flon smelters until 2010. Gibraltar's SX-EW cathode plant ran 1986–1999 and again from its 2007 refurbishment, so the leach route is kept |
| lead | `pyrometallurgy.smelting` (continuous and conventional), **`.roasting`**, `.refining` | `metallurgy.hydro` | Trail smelts lead in a continuous flash (Kivcet) furnace. The Brunswick smelter (Belledune, N.B.) made primary lead until it closed in 2019, which keeps the conventional roast (sinter) and smelt nodes; its exact furnace type is not confirmed in the sources checked. No lead leach plant |
| magnesium | **all of `metallurgy.*`**, `melt-cast` | — | Norsk Hydro Bécancour (electrolytic, closed 2007), Magnola (Asbestos, electrolytic, closed 2003) and Timminco (Haley, Pidgeon thermal reduction, closed about 2008) all ran after 2000. No primary magnesium is made today; the Alliance Magnésium demonstration plant (Danville) is in insolvency proceedings |
| nickel | `pyrometallurgy.smelting`, `.refining`; `hydrometallurgy` | — | Sudbury smelters and refineries; Thompson smelter until 2018; Long Harbour and (until June 2026) Fort Saskatchewan hydrometallurgical plants |
| titanium | `pyrometallurgy.smelting` (electric smelting), `.roasting`; `hydrometallurgy` | `pyro.refine` | Rio Tinto Fer et Titane: ilmenite smelted to slag, then roasted and leached to upgraded slag. No titanium metal refining since 2000 |
| zinc | `pyrometallurgy.roasting`; `hydrometallurgy` | `pyro.process.continuous`, `pyro.process.conventional.smelt`, `pyro.refine` | Trail, Valleyfield, Kidd Creek (until 2010) and Flin Flon are or were electrolytic plants. The Brunswick smelter made no zinc after 2000 (confirmed). Zinc keeps the same structure as the other metals: `zinc.pyrometallurgy.roasting`, `zinc.hydrometallurgy`, `zinc.melt-cast` |

Seven nodes are pruned in total: the five above and the two `unassigned-energy`
leaves. The check covered the main primary plants, not every small or secondary
facility.

## 5. What stays without a CIMS node

`renewable-natural-gas` and `renewable-diesel-and-saf` (commodity-only by decision).
Partial gaps remain:

- ferroalloys and silicon metal in `electric-smelting` (only titanium slag is in CIMS)
- mine air heating
- food and beverage process steps (CIMS has the aggregate only)

## 6. Open decisions

None. The proposal is ready to apply to the design table and to hand over as the
hierarchy change list (the `suggested-branch` column of the crosswalk).
