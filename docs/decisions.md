# Decisions

One line per decision, newest first. **Current** decisions are stated as rules in
[design.md](design.md). Superseded ones are kept so the chain can be followed. The
reasoning is in the linked record.

Records:

- [D]: `archive/decisions/2026-08-26_design-doc.md` §9
- [AGG]: `archive/decisions/2026-09-10_aggregation-review.md`
- [WV]: `archive/decisions/2026-09-10_wide-view-review.md`
- [SEU]: `archive/decisions/2026-09-11_sector-end-use-table.md`, with its notes file
- [TT]: `archive/decisions/2026-09-11_technology-table-notes.md`
- [HH]: `archive/decisions/2026-09-16_cims-hierarchy-harmonization.md`
- [DX]: `archive/decisions/2026-09-22_design-crosswalk-review.md`
- [HL]: `archive/decisions/2026-09-22_harmonized-layer-readme.md`

The restructure of 2026-09-23 is recorded in the commit history from tag
`pre-archetype-restructure`.

| Date | Decision | Status | Record |
| - | - | - | - |
| 2026-09-26 | UKERC whole-process rows remapped: CH-SC30-33 and the two UK TIMES twins to `steam-cracker_ccs-diffuse`; CH-SC9, 13, 14 and 22 to `reactor_methanol-to-olefins`; CH-SC23-27 to `reactor_ethanol-to-ethylene` (their capex equals the feedstock siblings', so they price the conversion step); CH-SC15 `(none)` (upstream CCS, repeats CH-SC13). The capture retrofits CH-SC30/32/34/36 are incremental (per-case `incremental-cost.csv`). `boiler_ccs-diffuse` and `combined-cycle_ccs-diffuse` lose their only numbers. | current | modeller 2026-09-26 |
| 2026-09-26 | The four currency series (World Bank and ECB deflators, Bank of Canada and Statistics Canada exchange rates) moved from the main manifest to the reference manifest, with the two held tables; `currency-conversion.csv` names the series behind each factor. | current | modeller 2026-09-26 |
| 2026-09-26 | Energy is on HHV: LHV numbers are converted with cited HHV/LHV ratios (`heating-value-stream.csv`), unstated ones read as HHV. Every conversion factor has a class (unit, same-source, property, ratio, internal, assumption) and a source-id in the separate reference manifest `data/raw-data/source-details_reference.csv`; rows record `conversion-class` and `conversion-factors`, summaries `n-external`, the wide view one `external-conversions` column (italics in the workbook). Efficiency bridge for numbers per unit of input; per-host-tonne numbers only for examples approved in `efficiency-bridge.csv` (none: the UKERC CH-SC and IS-HR2 examples are whole host processes). | current | modeller 2026-09-26 |
| 2026-09-26 | Extracted and loaded CAELP/E3 2024 and RTC 2023. IPCC AR6 Table 11.3 stands; nothing from Bataille 2019 is added (Table 1 kept only as a not-loaded comparison sidecar). A figure printed more than once in a source is pooled once (CAELP RNG and H2 boilers `(none)`). CAELP CHP `(none)` until the EPA 2013 fact sheet gives its basis; CAELP 140-200 degC heat pumps on `heat-pump_steam-generating`. 112 gap-filling sources for iron and steel, chemicals and pulp and paper added to `to-get.csv`. | current | modeller 2026-09-26 |
| 2026-09-26 | `electrolysis-cell_limestone-decarbonation` dropped; the Sublime route (`binder_electrochemical`) is the electrochemical cement option. | current | modeller 2026-09-26 |
| 2026-09-26 | Metal-smelting capture node added to the hierarchy snapshot; `dryer_supercritical-co2` removed (TRL 2, below scope). | current | modeller 2026-09-26 |
| 2026-09-26 | Added `smelting-vessel_low-shaft` (Tecnored), `binder_electrochemical` (Sublime) and `kiln_calcium-silicate-feed` (Brimstone). Aluminium rolling skipped. E14 whole-chain abatement costs stay on their host archetypes with a note; reformer examples at about 90% capture are set aside (`example-conversion.csv`, factor-id `set-aside`). | current | modeller 2026-09-26 |
| 2026-09-26 | Mapping review: 13 archetypes added (10 IEA-guide routes, electrolytic non-ferrous smelting, heat-charged thermal storage, and `evaporator_food` of new type `reference`); UKERC alternative binders split onto `binder_*`; DOE crude and vacuum distillation assembled onto `distillation-column_atmospheric-vacuum` with the study's own throughputs; DOE chlor-alkali, propylene and per-product rows on energy-service archetypes set to `(none)`; Philibert blast furnace with CCS moved to the post-combustion variant; `heat-exchanger_steam-heated` measured in t. Lifetimes in hours become years; unconvertible parents restated by pooled derived rows are duplicates. Wide view: families alphabetical, a note per parameter column. | current | modeller 2026-09-26 |
| 2026-09-26 | `cost-levelized` is a cost parameter shown with capex and opex; levelized costs of examples were moved out of sidecars into the main files (current values only; projections stay). Unpooled values are recovered with exact unit definitions and cited product factors in `records/reference/conversion-factor.csv` (with `example-conversion.csv` for examples reported per another product); this relaxes the same-source-only factor rule. Money units with `-thousand`/`-million` now scale correctly. | current | modeller 2026-09-26 |
| 2026-09-25 | Extractions hold only printed values or values derived using only printed values (sums, ratios, unit conversions), as `derived` with a formula. The ETSAP extractions made before the 2026-09-24 rules were rerun or audited against them (E04, E05, P05, P11, P07/08, I02, I03, I07, I10, heat pumps; E13 conformed). | current | modeller 2026-09-25 |
| 2026-09-25 | 19 archetypes added: the 16 from the 2026-09-24 mapping review, `pipeline_co2` and `well_co2-storage` (complements, not alternatives, at `<root>.transmission.co2-pipeline-and-storage.*`; new parameter `cost-levelized` for per-tonne transport and storage costs) and `geothermal-well_enhanced`. Table 1 "CO2 abatement" in ETSAP E14 is a capture rate. Pre-commercial options (TRL 5-6 or higher) stay in scope. | current | modeller 2026-09-25 |
| 2026-09-24 | The 39 held extractions in the ETSAP-brief shape are loaded (15 ETSAP briefs; DOE bandwidth studies; DOE 2022, EPA 2022, NETL 2022; four IEA reports; eight papers; two reports). DOE bandwidth tiers: current typical → conventional archetype, state of the art → the efficiency variant by its saving, else the conventional archetype with detail "SOA tier"; practical minimum → `(none)` (R&D, not a commercial option). 46 examples await decisions on 16 proposed archetypes. | current | mapping review 2026-09-24 |
| 2026-09-24 | Component archetypes (type `component`, no hierarchy node) and whole-plant costs assembled from them within one source (`records/reference/whole-plant-assembly.csv`, `pipeline/assembly.py`). `anaerobic-digester` added as a component and `separator_biogas-upgrading` made one; `anaerobic-digester_chp` added as the whole-plant heat-supply archetype, taking the AD-CHP examples off `reciprocating-engine_chp`. The Figure 2 digester-plus-upgrader capex of etsap_2013_012 is now assembled by the build instead of hand-derived. | current | [design.md](design.md) §2 |
| 2026-09-23 | Storage components are add-on measures (`incremental`, pooled only with the base system's cost from the same source). A PV system without storage is not an example of PV with storage. Road-vehicle components are not proxies for mobile equipment. | current | [design.md](design.md) §2 |
| 2026-09-23 | 16 archetypes added from the ETSAP brief assessment: SAGD and CSS, integrated upgrader, three whole-refinery types, open-pit and underground coal mines, coal-mine methane drainage, wood pellet mill, torrefaction, coal-to-SNG, coal-to-liquids, gas-to-liquids, geothermal binary power, biogas upgrader. Whole-plant archetypes are alternatives to the unit archetypes inside them. New equipment terms `mine` and `refinery`. | current | `data/raw-data/iea/etsap/brief-assessment.md` |
| 2026-09-23 | Documents to obtain are listed in `data/raw-data/to-get.csv` (replaces the lost `data/harmonized/download-wishlist.md` of D7). Downloaded documents that yield no data move to `data/raw-data/background-no-data-extracted/` and are recorded in `data/raw-data/background-register.csv`, not in the file manifest; their source rows stay only if a compilation cites them. | current | [design.md](design.md) §7 |
| 2026-09-23 | Legacy cement kilns (wet, semi-wet, Lepol, wet-precalciner, long dry) get one archetype, `kiln_legacy`: still operating in Canada after 2000. Solid-fuel direct heaters and dryers (and their strong-efficiency variants) split from gas-fired. UKERC's duplicate BAT-kiln rows marked (none). A cost with `cost-basis` incremental is set aside for a host cost; the Bataille kiln post-combustion cost is listed as incremental in `records/reference/incremental-cost.csv`. Script `archive/scripts/followup_2026-09-23_kilns-solid-fuel.py`. | current | [assignment-review-2026-09-23.md](assignment-review-2026-09-23.md) |
| 2026-09-23 | Assignment review: 201 examples re-homed, 4 archetypes added (HIsarna and COREX with capture, direct-fired dryer strong, paper machine moderate), 10 archetypes' hierarchy links corrected; `/unit` read as the source's own service unit; UK TIMES add-on costs set aside for a host cost. Script `archive/scripts/review_2026-09-23_assignments.py`. | current | [docs/assignment-review-2026-09-23.md](assignment-review-2026-09-23.md) |
| 2026-09-23 | The wide view lists every archetype, blank ones included (end uses no archetype serves are not listed). Each service link names its end use (`archetype-service.csv`, `end-use` column). Supersedes the 2026-09-10 rule that the view shows quantified technologies only. | current | this restructure |
| 2026-09-23 | UKERC measure costs pool only as whole-plant costs (UKERC's own baseline for the host step plus the measure), for the 7 archetypes in `ukerc-host-baseline.csv`. The rest are set aside for a host-plant cost. 23 UKERC and Bataille measure buckets remapped (`archive/scripts/remap_2026-09-23_ukerc-buckets.py`): 7 new host efficiency-bucket archetypes, 7 examples marked `(none)` as organizational or out-of-scope measures. | current | this restructure |
| 2026-09-23 | Bataille's six "technology based on low-temperature steam" rows are not examples of `combined-cycle_chp` (`(none)`). Negative costs are savings against a baseline and are not pooled. | current | this restructure |
| 2026-09-23 | UKERC costs on energy-service archetypes that need an efficiency factor are set aside (`set-aside = needs-efficiency`), both the per-tonne rows and their per-GJ-of-fuel restatements, until factors are established. | current | this restructure |
| 2026-09-23 | Costs in another unit convert only with the same source's own output factor; no second-basis columns and no hand-set bridge factors. Derived rows that restate another row are labelled duplicates (99 UKERC per-GJ costs). | current | this restructure |
| 2026-09-23 | The 14 candidate merges are applied: 15 archetypes folded into their pairs (`archive/scripts/archetype-merges-2026-09-23.csv`). None had examples. | current | this restructure |
| 2026-09-23 | `emissions-reduction-potential` pools CO2 and CO2e into one percentage. | current | this restructure |
| 2026-09-23 | Hierarchy nodes plus family tags: archetypes link to hierarchy paths directly. The former cross-sector end uses become families; the sector/end-use table becomes annotations on hierarchy paths. | current | this restructure |
| 2026-09-23 | Central value: the median of three or more examples, else the top-ranked source. Low and high span all examples and reported ranges. n is always shown. | current | this restructure |
| 2026-09-23 | Ordered multiple modifiers: `efficiency-*`, then `ccs-*`, then `retrofit` (`blast-furnace_top-gas-recycling_ccs-diffuse` is legal). This settles the open question on D4. | current | this restructure |
| 2026-09-23 | Archetype key `equipment[_discriminator][_modifier...]`: closed equipment and modifier lists, one listed discriminator. 172 keys renamed (`archive/scripts/archetype-renames-2026-09-23.csv`). | current | this restructure |
| 2026-09-23 | Test for a new archetype: energy use about 15% or more apart, emissions differing in kind or abatement, or a legacy type in Canadian stock. | current | this restructure |
| 2026-09-23 | Examples map to archetypes in one file, `source-example.csv`. The rename chain (canon_tech, R1–R7, the design crosswalk, adopt.py) is retired. | current | this restructure |
| 2026-09-23 | Each archetype has one `product-unit`. Examples in another unit are excluded with a reason, never converted through specific energy. | current | this restructure |
| 2026-09-23 | Rationale lives in archived records; the current documents state rules only. | current | this restructure |
| 2026-09-22 | `cims_hierarchy.csv` is the definitive list of CIMS services and end uses. | current | [HH] |
| 2026-09-22 | CIMS model-input technologies are not used to decide database technologies. They are parked for a later comparison stage. | current | `compare/cims-model-inputs/README.md` |
| 2026-09-22 | Database and model technologies are archetypes that provide end uses; sources give examples of them. The database summarises and does not keep every source detail. | current | this restructure |
| 2026-09-22 | One row per archetype in the wide view. Supersedes one row per (technology, sector, end use). | current | this restructure |
| 2026-09-22 | Adoption pass: the design tables replace the roster, and the service node becomes (end use, hierarchy leaf). | superseded 2026-09-23 | [DX], [HL] |
| 2026-09-22 | Biofuels become one hierarchy sector. Light industrial gains refrigeration. Compressor drive splits by driver. Field engines get their own node. | current (in the hierarchy) | [HH] |
| 2026-09-16 to 09-18 | Hierarchy harmonization rulings: the product/service split kept, Canadian spelling, paper grades (option B), CCS split by stream, machine drive pruned to the model, metal routes pruned where no Canadian plant has run since 2000, nodes added (coke, DAC, on-site power, oil pipelines, produced water, effluent, ceramics dryer, gypsum, nitric acid). | current (in the hierarchy) | [HH] |
| 2026-09-15 | Granularity rule 7 widened to emissions and policy treatment. Venting, flaring and fugitives are separate. `draws-on` replaces the heat-delivery column. Three water end uses added. | current (annotations) | [SEU] |
| 2026-09-14 | CCS host rows `<host>_ccs-concentrated` or `_ccs-diffuse` carry host-side facts only. The capture plant is on the capture service. | current (as modifiers) | [TT] |
| 2026-09-14 | Efficiency buckets on the technology table: measures in the examples column. Options a model would choose are not bucketed. | current | [TT] |
| 2026-09-14 | Roster names fold onto the nearest design technology, and nothing is dropped. | carried into `source-example.csv` seeds; each fold is now an editable row | [DX] |
| 2026-09-14 | CHP is a heat-supply technology on the low- and medium-temperature bands, not an end use. | current | [SEU] |
| 2026-09-11 | Heat is banded on the temperature the process needs, at 150 and 400 °C, not on steam grade. | current | [SEU] |
| 2026-09-11 | Integral against supplied heat: heat released inside the transforming unit stays with the sector; heat from a separable system is supplied. | current | [SEU] |
| 2026-09-11 | On-site power-only generation is in scope, reversing the design doc's §1 exclusion. | current | [SEU] |
| 2026-09-11 | Technology table rules: include conventional and prospective options (TRL ≥ 5–6); use generic names; examples in their own column; one row per device with a carrier list unless the equipment differs; legacy only if in Canadian stock; four type labels. | current | [TT] |
| 2026-09-10 | D13: costs per unit of the technology's own output; emissions are four scope-1 parameters with species explicit; `capex-total` removed; min and max only where values spread. | current, except one row per (technology, sector, end use), which is superseded | [D], [WV] |
| 2026-09-10 | D11 and D12: roster aggregation rules R1–R7 (cross-sector, fuel groups, one ccs variant, unquantified status). | superseded 2026-09-23 | [D], [AGG] |
| 2026-09-10 | Scope covers existing stock as well as future options. Legacy sub-types are kept. | current | [AGG] |
| 2026-09-09 | Currency: deflate in the source currency, then exchange at 2025 (method from CIMS). | current | [D] §6.3 |
| 2026-08-29 | D10: a technology applies to many nodes and is held once. | current (`archetype-service.csv`) | [D] |
| 2026-08-29 | D5a: one readiness ladder, with the crosswalk as data. | current | [D] |
| 2026-08-29 | The source manifest is two CSVs, not a workbook. | current | [HL] |
| 2026-08-27 | D9: CIMS is the spine of the roster. | superseded 2026-09-14 and 2026-09-22 | [D] |
| 2026-08-27 | D8: standalone technologies (current); efficiency buckets (current, as modifiers, with `efficiency-base` dropped); placeholders written (superseded: a gap is an archetype with no examples). | partly current | [D] |
| 2026-08-27 | D7: two-level attribution: the original is `source-id`, the compilation is `via-source-id`. | current | [D] |
| 2026-08-27 | D6: scope widened from heat to whole-sector industry. | current | [D] |
| 2026-08-26 | D5: TRL availability rule. | current | [D] |
| 2026-08-26 | D4: retrofit and greenfield are separate technologies. | current (as the `retrofit` modifier) | [D] |
| 2026-08-26 | D3: steam grade not distinguished; `.steam` / `.process-heat.*` branches. | superseded 2026-09-11 and 2026-09-23 | [D] |
| 2026-08-26 | D2: costs used as reported and flagged; no Canada adjustment. | current | [D] |
| 2026-08-26 | D1: CHP on steam, with electricity a co-product. | current | [D] |
| 2026-08-26 | One naming rule: `-` within a component, `_` between components. | current | [D] §5 |

## Open

Decisions the restructure left for review. The build's
`data/harmonized/output/mapping-review.md` keeps the live lists.

- **Discriminator definitions.** All of them are seeded from the archetype labels
  and marked `reviewed = no` in `records/vocabulary/discriminator.csv`.
- **Examples to check.** The mapping review lists 147 seeded mappings where the
  example's own name points elsewhere. Of these, 73 are Bataille rows whose device
  was assumed at extraction. The rest are folds the retired crosswalk made with no
  better archetype available, for example oven and management-system efficiency
  measures on `heat-recovery-unit_oven-exhaust`, and dryer efficiency buckets on
  `kiln_lumber-continuous`.
- **Efficiency factors for the set-aside UKERC costs.** 65 rows on 13
  energy-service archetypes wait for an efficiency factor
  (`output/set-aside-efficiency.csv`).
- **Host-plant costs for the set-aside UKERC measures.** 68 rows wait for a
  host cost (`output/set-aside-host-cost.csv`): blast furnace, hot rolling, coke
  oven, sinter, BOF, EAF, bakery ovens and others.
- **UKERC's paper dryer baseline.** `dryer_steam-heated_efficiency-*` pool at about
  1,310 CAD per t/yr because UKERC's "Dryer" baseline is £500/t. The host archetype
  `dryer_steam-heated` has one other example at 22 CAD. Check what UKERC's baseline
  covers (the whole paper machine?) before relying on either.
- **Costs with no output factor.** About 55 cost rows and 121 flow rows are
  stated per tonne of a host plant's product (or per m3, per GBP k) and their
  source gives no output factor, so they are not pooled.
- **Service links with nothing to narrow them.** Archetypes linked to every node
  of a former end use. Remove the links that do not apply.
- **Solid-fuel direct heaters.** `direct-heater_solid-fuel` spans 9.8 to 94 CAD
  per GJ/yr: UK TIMES prices its high-temperature and other-services solid-fuel
  heaters like gas units (9.8-19) and only its low-temperature ones at 54-94.
- **UK TIMES dry sheet forming** now sets the `paper-machine_fourdrinier-gap`
  central; it is an alternative route, not a standard machine.
- **Carriers carried over from folded names.** Some are implausible, such as
  `nuclear` on `boiler_ccs-diffuse`. Review the `carriers` column of
  `records/archetype.csv`.
