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
- **Costs with no output factor.** About 55 cost rows and 121 flow rows are
  stated per tonne of a host plant's product (or per m3, per GBP k) and their
  source gives no output factor, so they are not pooled.
- **Service links with nothing to narrow them.** Archetypes linked to every node
  of a former end use. Remove the links that do not apply.
- **Carriers carried over from folded names.** Some are implausible, such as
  `nuclear` on `boiler_ccs-diffuse`. Review the `carriers` column of
  `records/archetype.csv`.
