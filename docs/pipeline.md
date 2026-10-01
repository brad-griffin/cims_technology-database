# Pipeline

One entry point, run from the repo root:

```
python data/harmonized/build.py              # everything
python data/harmonized/build.py --check      # stop after the checks
python data/harmonized/build.py --quantified-only   # the wide view lists only archetypes with pooled numbers
```

It reads `data/raw-data/` and `data/harmonized/records/`. It writes
`data/harmonized/output/` and `docs/vocabulary.md`, and it appends new examples to
`records/source-example.csv`. A broken rule stops it with a non-zero exit, so it can
gate a commit.

## Stages

| # | Stage | Module | What it does |
| -: | - | - | - |
| 1 | hierarchy | `pipeline/hierarchy.py` | Loads `records/cims_hierarchy.csv`, stamps it (`output/hierarchy-stamp.csv`), and lists the nodes added and removed since the last build against `output/cims_hierarchy.csv`, the copy the last build wrote. |
| 2 | records | `pipeline/records.py` | Loads the archetypes, service links, annotations and vocabularies, and checks each archetype key and path. |
| 3 | extract | `pipeline/extract.py` | Reads every extraction as reported and keeps each source's own technology name. |
| 4 | clean | `pipeline/facts.py` | Evaluates arithmetic-only formulas, spells each unit one way, writes fractions as %, links derived rows to their source rows, flags missing bases, and numbers records within each source. |
| 5 | examples | `pipeline/examples.py` | Attaches each example to the archetype `records/source-example.csv` names. Appends new examples with a blank archetype. |
| 5b | whole-plant | `pipeline/wholeplant.py` | Adds UKERC's host baseline cost to each measure cost where `records/reference/ukerc-host-baseline.csv` allows, as a derived row (`tp-<source>-wNNN`). It sets the other measure costs aside. |
| 5c | assembly | `pipeline/assembly.py` | Sums one source's component costs into a whole-plant cost as listed in `records/reference/whole-plant-assembly.csv`, as a derived row (`tp-<source>-aNNN`). Stops the build on components from another source, another currency-year or an unreconciled unit. |
| 6 | checks | `pipeline/checks.py` | The gate. |
| 7 | normalise | `pipeline/normalise.py`, `pipeline/currency.py`, `pipeline/convert.py`, `pipeline/heating.py`, `pipeline/bridge.py` | Puts every fact on its archetype's basis, or excludes it with the reason. Unit definitions and the product factors in `records/reference/conversion-factor.csv` (per example: `example-conversion.csv`) bridge units the plain table cannot. LHV numbers go to HHV (`heating-value-stream.csv`); numbers per unit of input go per GJ of output by the efficiency bridge (`efficiency-bridge.csv`). Each row records its `conversion-class` and `conversion-factors`. |
| 8 | summarise | `pipeline/summarise.py` | One value set per archetype and parameter: central, low, high, n. |
| 8b | fill | `pipeline/fill.py` | Grades every summary `sourced`, then writes graded values (identity, estimated, guess) into empty cells by the rules in `records/fill/fill-rule.csv`, the hosts in `records/fill/host-archetype.csv` and the judgements in `records/fill/fill-judgement.csv`. Never overwrites a sourced value. |
| 9 | views | `pipeline/views.py` | Writes `archetype.csv`, `archetype-application.csv`, `cims_hierarchy.csv`, `cims_hierarchy_technology.csv`, `wide-archetype.csv` and `wide-flow.csv`. |
| 10 | reports | `pipeline/sources.py`, `pipeline/reports.py` | Writes `source-list.csv`, `citation-review.md`, `mapping-review.md` and `docs/vocabulary.md`. |
| 11 | workbook | `pipeline/workbook.py` | Writes `technology-database.xlsx`, last. It is never read back. |

## Records (edited by hand)

| File | One row per | Key |
| - | - | - |
| `records/archetype.csv` | archetype | `archetype` |
| `records/archetype-service.csv` | archetype × hierarchy path or pattern | both |
| `records/source-example.csv` | example | `example-id` = `<source-id>:<source-technology>[@<process>]` |
| `records/family.csv` | display family | `family` |
| `records/hierarchy-annotation.csv` | annotation group of hierarchy paths | `annotation` |
| `records/cims_hierarchy.csv` | hierarchy node (the CIMS snapshot) | `branch` |
| `records/vocabulary/*.csv` | term: equipment, discriminator, modifier, carrier, the other lists, parameter, commodity | the term |
| `records/reference/*.csv` | source priority, source citations, TRL scale map, unit conversions, currency references, conversion factors (with class and source-id), the heating-value streams per archetype, the efficiency-bridge review | |
| `records/fill/fill-rule.csv` | fill rule: grade, method, scope, formula, rationale, status | `rule-id` |
| `records/fill/host-archetype.csv` | archetype with incremental costs, and the host plant they are added to | `archetype` |
| `records/fill/fill-judgement.csv` | a guessed value: central within low-high, rationale, author | `archetype`, `parameter`, `target` |
| `data/raw-data/source-details_reference.csv` | reference source behind a conversion factor or the currency conversion (kept apart from the technology sources; `used_for` says which, `file_on_disk` names a held table) | `source_id` |

## Outputs (generated)

| File | What it is |
| - | - |
| `example.csv` | Every example, with its archetype, its source's context and the readiness it reports. |
| `example-parameter.csv`, `example-flow.csv`, `example-constraint.csv` | Every fact as reported, and converted to the archetype's basis (`*-norm`), or `excluded` with the reason. |
| `archetype.csv` | Every archetype with its parsed key, the nodes it applies to, its examples and its status. |
| `archetype-parameter.csv`, `archetype-flow.csv` | The summaries; `archetype-parameter.csv` also holds the filled rows, with `grade`, `method`, `rule-id`, `inputs` and `rationale`. |
| `archetype-application.csv` | Every hierarchy node each archetype serves, patterns expanded. |
| `cims_hierarchy.csv`, `cims_hierarchy_technology.csv` | The CIMS hierarchy snapshot the build used, and the same with `technology` as the second column: each node repeated once per archetype serving it, blank where none does. |
| `wide-archetype.csv`, `wide-flow.csv` | The wide views, one row per archetype; `wide-archetype.csv` includes blank archetypes. `wide-archetype-columns.csv` gives each column's group and unit. |
| `source-list.csv`, `citation-review.md` | Every source, its citation and where it is used. |
| `set-aside-host-cost.csv` | UKERC measure costs set aside until a host-plant cost is established. |
| `set-aside-efficiency.csv` | UKERC numbers per tonne of a host plant's product: `needs-efficiency` (not yet reviewed for the bridge) or `not-bridged` (reviewed; the reason is in `excluded`), with each example's fuel use per tonne. |
| `conversion-factor-use.csv` | Each conversion factor, pooled efficiency and assumption, with its class and the pooled rows, examples and archetypes that rest on it. |
| `reference-source-list.csv` | Each reference source, the factors it backs (or `currency-conversion.csv`) and the pooled rows that rest on it. |
| `mapping-review.md` | How examples reach archetypes, what was not pooled, and what needs a decision. |
| `currency-conversion.csv`, `hierarchy-stamp.csv` | The factors and the snapshot the build used. |
| `technology-database.xlsx` | The workbook. |

## How to

**Add a source.** Pick it from `data/raw-data/to-get.csv` where it is listed there,
and remove it from that list once it is held. If the document turns out to hold
nothing usable, move it to `data/raw-data/background-no-data-extracted/` and add
a row to `data/raw-data/background-register.csv` instead of registering it.
1. Register it in `data/raw-data/source-details_sources.csv` and `_files.csv`.
2. Extract it to a long CSV in the template format (`data/raw-data/tech_data_input_template.py`). A multi-context source also gets a `_nodes.csv`.
3. Add its loader to `pipeline/extract.py`: a file in the template format needs one line in `TEMPLATE_FILES`. A file in the ETSAP-brief shape (process/technology rows with `_nodes` and optional `_flows`) needs one line in `ETSAP_BRIEFS`, or in `BRIEF_SHAPE` with the region of its data for a non-ETSAP source.
4. Build. The new examples are appended to `records/source-example.csv` with a blank archetype.
5. Fill in each new example's `archetype` (or `(none)`), then build again.
6. Give the source a row in `records/reference/source-priority.csv`.

**Change a mapping.** Edit the `archetype` cell in `records/source-example.csv`.

**Add an archetype.**
1. Apply the test in [design.md](design.md) §2.
2. Add the row to `records/archetype.csv`, a new discriminator (with its definition) to `vocabulary/discriminator.csv`, and its hierarchy paths to `records/archetype-service.csv`.
3. A new equipment term is a modelling decision. Add it to `vocabulary/equipment.csv` deliberately.

**Update the hierarchy.**
1. Replace `records/cims_hierarchy.csv` and build.
2. `mapping-review.md` lists the nodes added and removed.
3. The build fails on any service link or annotation whose path has gone. Repoint those, then rebuild.

**Refresh currency.** Copy the two reference tables from the CIMS repository
(`data/processed_data/deflator_exchange/`) into `records/reference/` and build.

## Other checks

- `python data/raw-data/check-manifest.py`: the source manifest against the disk and against the build's outputs.
- `python data/raw-data/check-names.py`: names in the extraction layer and the YAML tree.
