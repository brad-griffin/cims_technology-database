# Sector descriptions: alignment with the new CIMS hierarchy

Review and execution plan, 2026-10-30.

## 1. What I compared

- **Documentation:** 25 sector chapters plus `sector_overview.qmd` in `quarto_docs/cims/docs` (about 3,100 lines; 110 to 190 lines per chapter; `sector_carbon_dioxide_removal.qmd` and `sector_lulucf.qmd` are stubs). Each chapter has one hand-coded hierarchy figure in `images/*_flow_model.svg`.
- **New hierarchy:** `tech_data/database/harmonized/output/cims_hierarchy.csv` (722 nodes, 515 leaves). It matches `records/cims_hierarchy.csv` apart from a byte-order mark; the tech_data README names the `records/` copy as definitive.
- **Supporting tables:** `archetype.csv` (522 archetypes, each with a label, type, TRL, and one-line description), `archetype-application.csv` (which archetype serves which node), `hierarchy-annotation.csv` (end-use definitions, units, and temperature bands), `family.csv`, and `cims/hierarchy-change-requests.md`. `cims/iron-and-steel-hierarchy.html` is probably out of date, so the plan doesn't use it; `cims_hierarchy.csv` is the only structural source.

## 2. Changes needed

### 2.1 The sector list

| Hierarchy sector | Current chapter | Change needed |
| - | - | - |
| `biofuels` | `sector_ethanol`, `sector_biodiesel` | Merge into one Biofuels chapter. Add renewable diesel and SAF, renewable natural gas, and solid biofuel (the biodiesel chapter calls renewable diesel a gap). |
| `chemicals` | `sector_chemical_products` | Rename. Add urea, fertilizer, and nitric acid as products; split petrochemicals into olefins, aromatics, polymers, and derivatives; add the chlor-alkali steps and the distillation and N₂O-abatement services. |
| `direct-air-capture` | `sector_carbon_dioxide_removal` (stub) | Write the chapter around the `co2-removal` product. |
| `transmission.co2-pipeline-and-storage` (seven corridors) | none (`ccus.qmd` is a stub) | New content; best placed in the CCUS general-service chapter. |
| `natural-gas-market` | none | Describe the market supply, transmission, and distribution nodes in the Natural Gas chapter. |
| `common-energy`, `vom` | none | Cross-reference `common-energy` (38 carriers) from Energy Supply and Demand; `vom` needs a definition from you or stays undocumented. |
| none | `sector_lulucf` (stub) | Not in the hierarchy. |

### 2.2 Structure within sectors

A keyword check found hierarchy nodes that the chapters never mention. The largest gaps:

- **Iron and steel:** the chapter describes Integrated and Recycled routes and a Slabs, Blooms, and Billets chain. The hierarchy instead has coke, agglomeration, hot metal (blast furnace, HIsarna, Corex or Finex, electric smelting), direct-reduced iron, oxygen, ladle preheating and refining, reheating, and a process-gas fuel blend; molten steel (BOF, EAF on scrap, EAF on DRI); and a continuous-cast chain of casting, hot rolling, pickling, cold rolling, and annealing and coating.
- **Mining:** products now split by commodity and mine type (aggregate, diamond, metal, potash conventional and solution, uranium). Services become unit operations: extraction, haulage, crushing, milling, separation, leaching, crystallization, drying, pelletizing, compaction, tailings disposal, steam, and on-site power.
- **Coal mining:** extraction, ventilation, and mine methane; coal preparation (washing, drying, tailings); size reduction; mine haulage.
- **Metal smelting:** alumina (digestion, calcination), electrolysis, and recycling for aluminium; pyrometallurgy (roasting, smelting, converting, refining), hydrometallurgy, and melt-cast for copper, nickel, lead, zinc, and titanium slag; electrolysis and thermal reduction for magnesium; anode-production, acid-plant, and oxygen services.
- **Industrial minerals:** cement (clinker, grinding, binder, calcined clay, ground slag), lime, glass (furnaces, forming and finishing), ceramics (dryer, kiln; replaces bricks), gypsum, and a kiln-heat service.
- **Pulp and paper:** wood preparation, four pulping routes, washing, bleaching, and drying; five paper grades, each with forming and drying; chemical recovery (evaporator, recovery furnace, lime kiln); effluent treatment.
- **Petroleum crude:** bitumen (in situ; mining with extraction and froth treatment; primary and secondary upgrading), heavy, light-medium (onshore, offshore), exploration, completion, and crude transmission; field engines, artificial lift, treating, produced water, pumping, tailings, and haulage services.
- **Petroleum refining:** distillation, hydrotreating (desulphurization, sulphur recovery), coking, hydrocracking, asphalt, lubes, alkylation, isomerization, reforming, and synthetic fuels; direct-heat, hydrogen, steam, and still-gas services.
- **Natural gas:** a detailed supply chain (drilling, completion, well tests, four extraction types, three processing steps, formation CO₂, compression, LNG liquefaction, direct heat, and fugitive, flaring, and five venting sources); compressor drives by engine and turbine.
- **Light industrial:** seven product groups; heat split into seven end uses (drying, process heating, cleaning, baking-frying-roasting, forming-pressing, metal melting, heat treatment).
- **Residential and commercial:** building type × code vintage × climate (cold, marine) for residential; eleven building segments × climate for commercial; new nodes for solar PV, clothes drying, and non-appliance hot water.
- **Electricity, hydrogen, transport, agriculture, waste, construction, forestry:** small changes (CCS by fuel, storage by duration, freight land split into heavy and light-medium, hydrogen distribution, renamed nodes).
- **Every industrial sector:** the same service set now recurs: fuel blend, HVAC (heating, cooling), lighting, five MECS machine-drive end uses, steam, and CCS (concentrated, diffuse). The chapters each describe these differently.

### 2.3 Archetypes

- 489 of the 522 archetypes serve hierarchy nodes. All have a label and a one-line description (median 81 characters), so the database can supply the text directly.
- 48 archetypes serve every sector through wildcard links (boilers, CHP, heat pumps, motors, pumps, fans, compressors, HVAC, and capture units). They belong in the General Services chapters, written once.
- Sector-specific archetype counts: iron and steel 64, chemicals 56, natural gas 55, metal smelting 54, industrial minerals 53, pulp and paper 48, mining 47, light industrial 43, petroleum crude 43, refining 38, coal mining 27, biofuels 22, hydrogen 14, construction 6, direct air capture 2.
- The database holds **no archetypes** for residential, transportation, electricity, agriculture, waste, or forestry, and only two for commercial. Those sectors need another source, such as the CIMS model-input files in `cims/data/model_inputs/`.

### 2.4 Figures

- The current figures are hierarchy trees, not process flows. They use the old node names, hard-code their styling in each file, and some have layout faults (in the iron and steel figure, the machine-drive box overlaps Reheating).
- No shared figure style exists. `style.css` adds a white backplate to SVGs so they stay legible in dark mode.

### 2.5 Length

The longest chapters (iron and steel, chemicals, mining) run 24 to 26 KB. Adding 45 to 65 archetype rows to each would roughly double them, so archetype lists need their own pages.

### 2.6 Other items to fold in

- Your notes file asks for bold text on processes only, less repetitive language, the Oxford comma, and more space after tables and figures. Every chapter opens with the same paragraph of boilerplate.
- Existing file names use underscores only (`sector_iron_and_steel.qmd`), which conflicts with your kebab-snake convention.
- `CLAUDE.md` requires `.qmd` edits through Write and Edit, never bash.
- Open change requests (lighting in Mlm-h with a general and high-bay split; on-site power beyond mining; ferroalloys) affect what the chapters should say.

## 3. Plan

### 3.1 Page layout (revised after your answers)

- **Sidebar:** replace the single "Sector Descriptions" part with grouped parts: Energy supply, Heavy industry, Buildings, Transportation, and Land, waste, and removals. `sector_overview.qmd` opens the first group.
- **Sector chapter:** short introduction, scope, **Context** (renamed from "Real-world context" and trimmed), process flowchart, then the process description. Each process step gets its technologies right beside it, in a visually distinct block (a styled technology card or callout listing each archetype with a one-line summary, type, and TRL). No separate technologies pages.
- **Sub-sector chapters** where a sector's product branches are independent and one chapter would exceed about 150 lines: likely metal smelting (aluminium; base metals), chemicals (nitrogen chain; chlor-alkali and oxidants; petrochemicals and methanol), and petroleum crude (oil sands; conventional). Each sits under its sector's part with a short parent chapter that holds the sector-wide flowchart and services.
- **Archetype detail:** chapters carry only the important summary details. A single link to the archetype wide-view table (`wide-archetype.csv`) goes in the sector overview; until you give me its published location, it carries a TODO.
- **General Services:** document the 48 shared archetypes once; add HVAC and lighting and on-site power; give CCUS the CO₂ transport and storage corridors.

### 3.2 Flowchart system

- `docs/flowcharts/flowchart_style.yml`: palette (light and dark), fonts, sizes, line weights, arrow styles, and one shape per role (purchased input, process stage, service, product, emission).
- `docs/flowcharts/icons/`: about 40 pictograms in one stroke style (mine, truck, crusher, kiln, furnace, boiler, motor, pump, electrolysis cell, tank, pipeline, building, and so on).
- `docs/flowcharts/<sector>.yml`: stages, icons, material flows (solid lines), and energy or service flows (dashed lines). Each stage carries its hierarchy branch.
- `docs/flowcharts/build_flowcharts.py` (run with `uv run`): lays out each chart, writes light and dark SVGs to `images/flowcharts/`, and fails if a tagged branch is missing from `cims_hierarchy.csv`. That check keeps the figures aligned when the hierarchy changes.
- Document the style in a new appendix, `appendix_figure-style.qmd`, with swatches, the icon gallery, and how to change a setting and rebuild. Embed figures with Quarto's `.light-content` and `.dark-content` classes.

### 3.3 Steps for each sector

1. Pull the sector's subtree, archetypes, annotations, and open change requests.
2. Rewrite the model-structure section to match the nodes, in plain language.
3. Update scope and cross-links (for example, coal-mine methane now sits in coal mining).
4. Write the flowchart spec and build the figure.
5. Write the technology blocks beside each process step.
6. Remove boilerplate and apply your style notes.
7. Run the checks in section 3.5.
8. Commit (section 3.6).

### 3.4 Order

0. **Renames:** rename every docs file to the naming convention (Appendix A) with `git mv`, and update every reference to the old names. No content changes, so the commit is a pure rename.
1. **Setup:** generator, style file, icons, appendix, chapter template, and the General Services shared-archetype tables.
2. **Pilot:** iron and steel, built from `cims_hierarchy.csv` alone. It sets the template for the rest.
3. **Heavy industry:** industrial minerals, metal smelting, pulp and paper, chemicals, mining, coal mining, and light industrial.
4. **Energy supply:** petroleum crude, refining, natural gas (with the market nodes), hydrogen, biofuels, and electricity.
5. **Buildings, transport, and the rest:** residential, commercial, both transport chapters, construction, forestry, agriculture, waste, and direct air capture.
6. **Wrap-up:** sector overview, `_quarto.yml`, cross-references, a render check, a changelog entry, and a list of retired figures ready for removal.

I save progress notes to the project after each batch, so a new session can resume where the last one stopped.

### 3.5 Checks

- A script lists, for each sector, any hierarchy leaf the pages never mention and any archetype missing from the tables. Both lists must be empty or have a stated reason.
- A full book render in the cloud workspace (Quarto is not installed in the Linux VM on your machine) to catch broken cross-references and figure paths.
- A visual check of every flowchart in light and dark mode.
- A closing report listing what changed and what remains open.

### 3.6 Commits

- Commit on the current `quarto_docs` branch after each step that stands on its own: the rename, the flowchart system, General Services, then one commit per sector (or sub-sector group) and one for the wrap-up. I don't push.
- Each commit stages only the paths that step changed. The untracked `results/` files and the root `uv.lock` stay untouched.
- Author: Brad Griffin <bradford_griffin@sfu.ca>, matching your existing commits, with a Claude co-author trailer.
- `CLAUDE.md` says bash is read-only. I use bash only for git (`git mv`, `git add`, `git commit`), as you asked. All `.qmd` content edits still go through Write and Edit.

## 4. Decisions needed before I start

Asked at the start of the session (answers recorded in section 6):

1. Flowchart approach and icon style.
2. Page layout and sidebar structure.
3. Archetype source for sectors with no database archetypes.
4. What happens to the existing indicative cost tables, maturity tables, and real-world context.

Defaults I will apply unless you say otherwise:

- **Sector set follows the hierarchy:** merge ethanol and biodiesel into Biofuels, rename Chemical Products to Chemicals and Carbon Dioxide Removal to Direct Air Capture, and put CO₂ transport and storage in CCUS. Leave the LULUCF stub as it is and skip `vom`.
- **File names (revised):** all files in `docs/` follow kebab-snake case, existing files included (Appendix A). Python files use underscores. Quarto's fixed names stay as they are (`_quarto.yml`, `_brand.yml`, `_quarto-watermark.yml`). Renamed chapters get `aliases:` front matter so old URLs on the published site still resolve. The root `README.md` logo paths get updated too.
- **Nodes added ahead of CIMS** appear as part of the structure without a marker; the changelog lists them.
- **Archetype text** comes from the database descriptions, edited lightly into plain language. I won't add numbers the database doesn't hold.
- **Old figures (revised):** renamed and moved to `images/retired/` so they're easy to remove later. The chapters stop referencing them, and the wrap-up lists which ones nothing uses any more. I won't delete them.
- **Git (revised):** commit as I go (section 3.6).
- **Lighting:** describe the current single node in GJ and note the pending Mlm-h and high-bay change.

## 5. Permissions

- **Read:** both folders (already granted). tech_data stays read-only.
- **Write in `quarto_docs/cims/docs`:** overwrite the sector, overview, and General Services chapters, `_quarto.yml`, and `style.css`; create `flowcharts/`, `images/flowcharts/`, and new `.qmd` pages. Following `CLAUDE.md`, I stage each `.qmd`, edit it with Edit, and write it back with a modification-time guard so I never overwrite a newer edit of yours.
- **Delete:** granted for `C:\_dev\quarto_docs` for this session. I use it only for git's own lock files and for `git mv` removing old paths, and I don't delete any other file.
- **Cloud workspace:** install Quarto and Python packages there for the render check. Nothing gets installed on your machine apart from what `uv run --with` caches for the figure script.

## 6. Answers

1. **Flowcharts:** YAML specs plus a Python generator (`build_flowcharts.py`), one style file, a custom pictogram set, and light and dark SVGs, with the style documented in an appendix.
2. **Layout:** regroup the sectors into several parts, with sub-sector chapters where needed. Keep the technologies beside their process descriptions and set them apart visually.
3. **Sectors with no database archetypes:** use the technologies in the current CIMS model inputs, described briefly and flagged as pending the database.
4. **Existing content:** rename "Real-world context" to "Context" and trim it. Replace the maturity tables with type and TRL, drop the indicative cost tables, include only important summary details from the archetypes, and link once to the archetype wide-view table.

Follow-up instructions (2026-10-30):

5. The iron and steel diagram in tech_data is probably out of date, so don't use it.
6. Name all files according to the naming convention, existing ones included.
7. The old figures can probably be removed eventually, so retire them rather than delete them.
8. Commit as I go.

All other choices follow the defaults in section 4. No further input is needed to run the plan.

## Appendix A. Rename map

The rule: hyphens join the words of one component, and underscores separate components (subject, variant, medium). Sector chapters take the hierarchy's sector names.

**Chapters**

| Old | New |
| - | - |
| `appendix_file_formats.qmd` | `appendix_file-formats.qmd` |
| `building_tree.qmd` | `building-tree.qmd` |
| `data_inputs.qmd` | `data-inputs.qmd` |
| `data_processing.qmd` | `data-processing.qmd` |
| `demand_feedbacks.qmd` | `demand-feedbacks.qmd` |
| `district_energy.qmd` | `district-energy.qmd` |
| `energy_storage.qmd` | `energy-storage.qmd` |
| `energy_supply_demand.qmd` | `energy-supply-demand.qmd` |
| `low_temp_industrial_heat.qmd` | `low-temp-industrial-heat.qmd` |
| `machine_drive.qmd` | `machine-drive.qmd` |
| `post_processing.qmd` | `post-processing.qmd` |
| `running_scenario.qmd` | `running-scenario.qmd` |
| `sector_carbon_dioxide_removal.qmd` | `sector_direct-air-capture.qmd` |
| `sector_chemical_products.qmd` | `sector_chemicals.qmd` |
| `sector_coal_mining.qmd` | `sector_coal-mining.qmd` |
| `sector_ethanol.qmd` + `sector_biodiesel.qmd` | `sector_biofuels.qmd` (the merge happens in the energy-supply batch; until then they're renamed `sector_biofuels_ethanol.qmd` and `sector_biofuels_biodiesel.qmd`) |
| `sector_industrial_minerals.qmd` | `sector_industrial-minerals.qmd` |
| `sector_iron_and_steel.qmd` | `sector_iron-and-steel.qmd` |
| `sector_light_industrial.qmd` | `sector_light-industrial.qmd` |
| `sector_metal_smelting.qmd` | `sector_metal-smelting.qmd` |
| `sector_natural_gas.qmd` | `sector_natural-gas.qmd` |
| `sector_petroleum_crude.qmd` | `sector_petroleum-crude.qmd` |
| `sector_petroleum_refining.qmd` | `sector_petroleum-refining.qmd` |
| `sector_pulp_and_paper.qmd` | `sector_pulp-and-paper.qmd` |
| `sector_transportation_freight.qmd` | `sector_transportation-freight.qmd` |
| `sector_transportation_passenger.qmd` | `sector_transportation-passenger.qmd` |

Single-word names (for example `ccus.qmd`, `sector_mining.qmd`, `appendix_acronyms.qmd`) already comply. New sub-sector chapters follow the same pattern, for example `sector_metal-smelting_aluminum.qmd`.

**Images kept in use**

| Old | New |
| - | - |
| `cims_logo.pptx` | `cims-logo.pptx` |
| `cims_logo_dark_screen.svg` | `cims-logo_dark_screen.svg` |
| `cims_logo_light_screen.svg` | `cims-logo_light_screen.svg` |
| `cims_logo_favicon.svg` | `cims-logo_favicon.svg` |
| `consumer_surplus.png` | `consumer-surplus.png` |
| `demand_supply_feedbacks.svg` | `demand-supply-feedbacks.svg` |
| `final_intermediate_primary_flow.png` | `final-intermediate-primary-flow.png` |
| `general_model_structure.svg` | `general-model-structure.svg` |
| `stock_retirement_existing.svg` | `stock-retirement_existing.svg` |
| `stock_retirement_new.svg` | `stock-retirement_new.svg` |
| `stock_total.svg` | unchanged |

**Retired sector figures** move to `images/retired/` as `<hierarchy-sector>_flow-model.svg` (for example `iron-and-steel_flow-model.svg`, `industrial-minerals_flow-model.svg`, `biofuels_ethanol_flow-model.svg`). The four route figures become `chemicals_ammonia-routes.svg`, `iron-and-steel_routes.svg`, `mining_potash-sk.svg`, and `pulp-and-paper_recovery.svg`.

**New files:** `flowcharts/flowchart_style.yml`, `flowcharts/build_flowcharts.py`, `flowcharts/icons/<icon-name>.svg`, `flowcharts/<hierarchy-sector>.yml`, `images/flowcharts/<hierarchy-sector>_process-flow_light.svg` and `_dark.svg`, and `appendix_figure-style.qmd`.

Every reference to an old name gets updated: `_quarto.yml`, `_brand.yml`, `style.css`, cross-chapter links, figure paths, and the root `README.md`.
