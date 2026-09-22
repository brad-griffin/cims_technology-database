# Harmonized technology database

A template for assembling technology data for CIMS and for other
energy-economy models. It sits between the per-source extractions in
`data/raw-data/` and the CIMS YAMLs in `data/service-technology-map/`:

```
data/raw-data/<publisher>/…      one long CSV per source, as extracted
        |                        (marimo template, design doc 6.1)
        v
data/harmonized/                 THIS LAYER
        |                        sources reconciled, grouped by sector and
        |                        end use, every number still pointing home
        v
data/processed/  ->  data/service-technology-map/**.yaml
```

Nothing here replaces the extraction layer. A raw extraction stays a faithful
record of one document; this layer is where several of them become one roster.

Two representations of the same tables:

- `technology-database-template.xlsx` — the authoring surface. Dropdowns,
  header notes, frozen panes.
- `*.csv` — the same tables, one file per table, header row identical to the
  workbook sheet. What scripts read.

The scripts that build and check this layer, in order:

```
python data/harmonized/extract-cims-roster.py    # CIMS model inputs -> cims-roster.csv
python data/harmonized/build-cims-map.py         # roster -> cims-map.csv (rules engine)
python data/harmonized/build-template.py         # schema -> empty tables + workbook
python data/harmonized/populate.py               # roster + extractions -> populated tables,
                                                 #   then adopt.py: design vocabulary + hierarchy
python data/harmonized/build-cims-review.py      # map -> cims-review.md
python data/harmonized/build-currency.py         # BoC + StatCan -> currency factors
python data/harmonized/build-wide.py             # long tables -> wide views
python data/raw-data/check-data.py               # validate the built tables (gate)
```

`build-template.py` **preserves rows that are already there**: a populated
table keeps its data and gains any new columns blank, and the workbook is built
from what the CSVs actually hold. Dictionary tables (`sector`, `end-use`,
`parameter`, `commodity`, `vocabulary`) are always re-seeded from the script,
which is their source of truth. `--force` resets every table to the empty
template and discards data.

Edit the schema in `build-template.py`, not in Excel, and re-run.

---

## 1. Structure

### Grouping: sector → end use → hierarchy leaf → technology

```
sector                the design table's 13 sectors plus cross-sector (14)
  end-use             design/sector-end-use-table.csv, sector-scoped (94);
                      generic services -- heat bands, machine drive, space
                      conditioning, CO2 capture -- held once on cross-sector
    process-step      a leaf of design/cims_hierarchy.csv, which sets the
                      level of detail below the end use (265)
      service-node    one per (end use, hierarchy leaf); `branch` is the leaf,
                      exactly as the hierarchy writes it (280)
        technology    a row of design/end-use-technology-table.csv, named
                      equipment_discriminator, held once and applied to
                      every service node it serves (448)
```

**The vocabulary is the design tables, not the sources (adopted 2026-09-22).**
`populate.py` first builds the roster the sources grew -- their own
equipment_carrier_variant names, on the old twelve global end uses -- and then
`adopt.py` replaces it: every source name folds onto a design technology,
every application moves onto the hierarchy leaves of its design end use, and
every fact moves onto its design technology while keeping the source's own
name in `roster-technology`. The roster as it stood before adoption is kept
in `source-roster/`, and the crosswalk that did the folding, with its review,
beside this file (section 5c).

`service-node` is the join to CIMS: one design end use at one leaf of the
hierarchy, holding that leaf in `branch` and the unit demand is measured in.
A leaf split across end uses (`light-industrial.service.heat` feeds six) gives
one node per end use.

**A technology can serve several of them** (design doc D10). The roster holds
it once and `technology-application` records every node it serves. 448 design
technologies hold 2,762 applications: those a source placed, on the leaves the
crosswalk chose, and those only the design table places, on every leaf of the
end use. 124 technologies carry data; the wide view shows them as 463 rows,
one per source name folded in (section 2a).

### Tables

| Table | Kind | What it holds |
| - | - | - |
| `sector` | registry | 13 sectors plus `cross-sector`, with UKTM / NAICS / ISIC crosswalks. Seeded. |
| `end-use` | registry | The design table's 94 end uses, each with its sector, service type, unit and temperature tier. Seeded from the design table. |
| `process-step` | registry | The CIMS hierarchy leaves the end uses are made of. Written by `adopt.py`. |
| `service-node` | registry | One per (end use, hierarchy leaf), with the leaf in `branch`. Written by `adopt.py`. |
| `technology-application` | link | Where each technology applies: one row per technology × service node. Empty. |
| `technology` | roster | One row per design technology, with its label, carrier list and the source names folded into it (`aggregated-from`). |
| `parameter` | dictionary | 27 parameters: definition, unit dimension, CIMS target, optimization use. Seeded. |
| `commodity` | dictionary | 73 energy carriers, materials and emission species. Seeded. |
| `tech-parameter` | fact | The main table. One row per number. Empty. |
| `tech-flow` | fact | Input/output vectors. One row per non-zero flow. Empty. |
| `tech-constraint` | fact | Adoption, stock and capacity limits. Empty. |
| `changelog` | log | What changed, when, why. |
| `vocabulary` | dictionary | Every controlled list, long format. Generated. |

Alongside the tables:

| File | What it is |
| - | - |
| `cims-roster.csv` | Every distinct technology in the CIMS model inputs, region-collapsed. |
| `cims-map.csv` | Each CIMS technology mapped onto the harmonized naming, with an action and a confidence. |
| `cims-review.md` | The rename / merge / remove / add advice, generated from that map against `source-roster/`. |
| `source-roster/` | The roster the sources grew, before adoption: `technology`, `technology-application`, `service-node` and `process-step` in the same schema. |
| `design-crosswalk-technology.csv` | Each source roster name and the design technology it folds onto, with the rule that chose it. |
| `design-crosswalk-application.csv` | Each source application and the design end use it lands on. |
| `design-crosswalk-branch.csv` | The same, taken down to the hierarchy leaf, with how the leaf was chosen. |
| `design-crosswalk-review.md` | The crosswalk explained: coverage, folds, empty end uses, the leaf level. |
| `wide-technology.csv` | Wide view: one row per technology **per source name folded into it, per (sector, end use)** that source placed it on, one column per parameter plus `_min` / `_max`. |
| `wide-flow.csv` | Wide view: one row per technology per (sector, end use), one column per commodity, `in_` and `out_` prefixed. |

Rows are technologies with data; `placeholder` and `unquantified` entries are
left out (R7 above). `technology-label` and `status` are not shown: the label
held only the first CIMS name that claimed a technology, and status read
`draft` on every row precisely because of that filter.

**One row per (technology, sector, end use)** — the process steps the technology
serves within that end use are joined into the `process-step` cell rather than
split across rows (user, 2026-09-10). Every fact column is keyed on the
technology alone, so a technology serving six steps used to be six rows
repeating the same numbers, which made it look six times as common as it is.
Rows sort sector → end use → technology → process step, and the sheet bands on
sector and end use only, so each band reads as one alphabetical run of names.

**Since the adoption, one row per source name as well** (2026-09-22). A design
technology holds the facts of every source name folded into it --
`boiler_fuel-fired` carries `boiler_natural-gas`, `boiler_oil` and the rest --
so the views key each fact on both names, print the second in
`roster-technology`, and show a source name only under the end uses its own
source placed it on. One cell per parameter would otherwise pick one fuel's
number and hide the others.
| `unit-conversion.csv` | Physical conversions used by the wide views. Exact constants. |
| `trl-scale-map.csv` | Crosswalk from each source's readiness scale to the common 1-9 ladder, with the band definitions and where they came from. |
| `reference-exchange-rate.csv` | Bank of Canada annual average rates to CAD, 2000–2025, USD and GBP. |
| `reference-cpi.csv` | Statistics Canada all-items CPI, Canada, 2002=100, monthly and annual, 2000–2025. |
| `currency-conversion.csv` | `YEAR_CUR` → `2025_CAD`, derived from those two by `build-currency.py`. |
| `source-priority.csv` | Which source supplies a central estimate: broadest first, then most recent. |

## 2a. The wide views

`build-wide.py` pivots the long tables into two wide sheets, and adds both to
the workbook. They are **views, not tables**: the long `tech-parameter`,
`tech-flow` and `tech-constraint` stay the record, and anything typed into a
wide sheet is lost on the next run. Regenerate them after any change to the
long tables.

**The workbook sheets are laid out like the UKTM sheet of the Bataille
database**, and are meant to look nothing like the database sheets:

- a teal header band with the column names, and a second band above it naming
  each column's group — `identity`, `technical`, `cost`, `emissions`,
  `deployment`, or `inputs` / `outputs` on the flow sheet;
- each sector as a large bold row on a tinted band, with a blank row before it;
- each end use as a bold row beneath it, prefixed with `*` as UKTM does;
- the technologies indented under their end use, starting in column B with
  column A left narrow and empty;
- a banner in row 1 saying what the sheet is.

The banding is the point, not decoration. A sheet with section rows in it
cannot be sorted or filtered without breaking the grouping, so it does not
invite being used as a working table — which is exactly what these views must
not become. Sorting and filtering belong on the long tables.

The **CSVs stay flat**: no banner, no band rows, one header line, sorted by
sector then end use then name. They are the machine-readable form of the same
view, and a script reading `wide-technology.csv` sees an ordinary rectangle.

**Units are harmonized here and only here.** The long tables keep every value
in the unit its source reported (§6.3); the wide view is where they are made
comparable, which is a different job and a lossy one.

- Technical values convert to the parameter's dictionary unit, or failing that
  to whichever unit most of that parameter's rows already use — which folds
  `MJ/unit` into `GJ/unit` without a rule per parameter.
- Monetary values convert to `2025_CAD` through `currency-conversion.csv`,
  which `build-currency.py` derives from the two reference tables:

      factor(YYYY_XXX -> 2025_CAD) = fx(XXX->CAD, YYYY) x CPI(2025) / CPI(YYYY)

  Convert at the source year's annual average rate, then deflate in Canadian
  dollars. That keeps one price index in play instead of two, which is why only
  Canadian CPI is needed; deflating in the source currency first and converting
  at today's rate would need US and UK deflators as well, and would embed
  whatever real exchange-rate drift happened in between. A currency with no
  factor keeps its own column and the run says so.
- A **unit row** sits under the header. There are no unit columns, because
  every value in a column now shares one unit.
**Costs are put on one basis where they can be.** Every source prices its
technology against a different denominator — per kW, per tonne of annual
product, per GJ, or as an absolute sum — and those are not interconvertible
without knowing how much the thing makes. Dividing by specific energy
consumption or annual output supplies exactly that, and is the only step in the
view that is not arithmetic on the source's own numbers. A money parameter
therefore lands in at most four columns, each a different **quantity** rather
than a different spelling of one:

| Column | What it is | Why a row lands here |
| - | - | - |
| `capex` | 2025_CAD per GJ of annual output capacity | the common basis; 68 of 101 costed technologies |
| `capex-per-product` | 2025_CAD per unit of annual product | no energy throughput to divide by. `product-unit` names the unit — t, m³, £k |
| `capex-nameplate` | 2025_CAD per GJ/yr at nameplate | a per-kW cost with no capacity factor to convert it at actual output |

The divisor is only used when it is positive and above 0.05 GJ per unit. A
technology whose net energy is negative — blast furnace gas recovery, for
instance — would otherwise come back with a negative cost per GJ.

### Costs are per unit of output

Every cost rate is expressed **per unit of the technology's own output** — a
tonne for a process technology, a GJ for an energy service — as one column per
cost parameter, read against `product-unit` (design doc D13, 2026-09-10).

The previous basis manufactured a GJ denominator for every cost by dividing a
per-tonne rate by `specific-energy-consumption`, which is final energy INPUT
per tonne, while the absolute and per-kW routes divided by annual OUTPUT. One
column mixed the two, and they differ by the technology's efficiency. Dropping
the division also makes the figure the source's own: 262 of the 784 cost rows
are natively per tonne.

**Do not sort, average or chart a cost column across end-use bands.** Within a
band the unit is effectively constant — the energy services are all GJ, the
process technologies all t — which is what makes a single column workable.
Across bands the numbers are not commensurable. The same caution applies to
`efficiency`, which since the COP fold spans 4.92 to 700 and mixes combustion
efficiency, heating COP and one cooling COP.

`capex-total` and `reference-capacity.csv` were removed in the same pass. The
total was a derived column only, never a stored parameter, and every capacity
cell in the table behind it was blank, so the route never fired. The table is
archived under `data/raw-data/superseded/`.

## 2. Traceability

Every fact row carries five columns that together let anyone walk a number back
to its page:

| Column | What it does |
| - | - |
| `source-id` | Foreign key to `data/raw-data/source-details_sources.csv`. |
| `source-file` | Which file within that source (its `file_name` in the manifest). |
| `source-locator` | Page, table, or `sheet!cell`. Must land a reader on the number itself. |
| `extraction-file` | Path to the raw-data long CSV this was harmonized from, where one exists. |
| `value-type` | `reported`, `derived`, `assumed`, `proxy`, or `placeholder`. |

`value-type` is the honest part. Only `reported` means the source states the
number. `derived` requires `formula` and `derived-from` (a list of `record-id`s
in this same layer), so a chain of derivation is walkable without rerunning
anyone's arithmetic. `assumed` is the only value type that may sit without a
`source-id`, and its `note` must say who assumed it and why.

`record-id` exists so that a value can be cited, superseded and logged. It is
`<prefix>-<source-id>-NNNN`, prefixed by table — `tp-ukerc_2013_001-0042`,
`tf-...`, `tc-...` — and numbered within each source's own block. A single
run-wide counter meant adding one line to an early extraction renumbered every
row below it, so no id was safe to cite in a note, an issue or a paper; the
per-source number keeps an edit's blast radius inside the source it edits.
`populate.py` renumbers in one pass at the end of the run and rewrites every
`derived-from` through the same old → new map, failing the run if a reference
stops resolving.

**The source register is `data/raw-data/source-details_sources.csv` plus
`source-details_files.csv`, and this layer does not copy it.**
`build-template.py` reads the `source_id` column out of both at build time and
turns it into the `source-id` list. If an id you need is missing, the fix is to
register the source in the manifest and re-run the build — not to type a free id
here.

It was a workbook (`source_details.xlsx`) until 2026-08-29. The workbook carried
an x14 dropdown and a hidden dynamic-array sheet that openpyxl destroyed on any
round-trip, which is why edits had to go through bespoke XML-editing helpers;
CSV removes that fragility entirely. The workbook is kept unchanged in
`data/raw-data/superseded/`. `python data/raw-data/check-manifest.py` validates
the manifest against the disk and against this layer, and exits non-zero on a
failure. Beside it, `python data/raw-data/check-data.py` validates this layer
against its own conventions — parameters defined in `parameter.csv`, the basis
each one requires, `currency` as a bare currency-year, record-id shape and
uniqueness, and every `derived-from` resolving — and also exits non-zero, so
either can gate a commit. Neither runs the pipeline; both read what is on disk.

Three flags stop the silent-pooling failures the design doc calls out:

- `cost-basis` — `equipment` / `installed` / `total-plant` / `overnight`. An
  equipment cost and an installed cost differ by up to a factor of two and look
  identical in a spreadsheet.
- `capacity-basis` — `thermal-input` / `thermal-output` / `product-output` /
  `electric-output`. A $/MW that does not say which is unusable.
- `currency` — the currency-year and **only** that: `2018_USD`, never
  `2018_USD/kW`. What the money is per belongs to `unit`, which already carries
  it. Required with every monetary value. **Values stay as reported**: no
  deflation, no currency conversion, no Canada adjustment in this layer (design
  doc §6.3, decision D2). Conversion happens once, at the CIMS `currency`
  parameter.

Which parameters require which basis is declared in `parameter.csv`, in its
`basis-required` column — not hard-coded in the loader. `populate.py` reads that
column, and a quantified row missing its declared basis is marked
`status=review` with a `BASIS NOT RECORDED` note rather than dropped or guessed.
Extractions that predate the basis rules are working through that backlog;
`check-data.py` reports its size per source rather than failing on it.
- `discount-rate` — the *source study's* rate, recorded whenever a value was
  levelized or inverted, so the model's own hurdle rate is not applied twice.

---

## 3. Detail level

Deliberately between the two starting points.

**Technology detail: the Bataille UKTM sheet.** Distinct equipment × carrier ×
variant combinations — "MEA post-combustion CCS, new plant" and "…, retrofit"
are two technologies; individual vendor plant designs are not. Roughly 15–45
technologies per sector.

**Parameter detail: below UKERC, above Bataille.**

Kept from UKERC:

- **Input/output vectors**, but in `tech-flow` as one row per non-zero flow
  rather than 100+ mostly-empty columns. Adding a commodity never adds a
  column, and an input in one sector matches an output in another because both
  name the same `commodity` key.
- **Uncertainty**, as `value-min` / `value-max` / `uncertainty-type` on the one
  value row. UKERC repeats min/max across baseline, technology and delta
  blocks; here the central value and its range live together, once.
- **Adoption and stock constraints**, in `tech-constraint`: current and maximum
  adoption share, growth limits, applicability to existing stock, refit
  requirement. `constraint-basis` records what a share is a share *of*, which
  UKERC leaves to a column header.

Dropped from UKERC:

- The **baseline / technology / reduction / net-change** quadruplication. Only
  the technology's own absolute values are stored; the delta against a baseline
  is computed from `baseline-technology` on the roster. Storing both is how the
  two drift apart.
- **Per-cost-block lifetimes and comment fields** repeated for baseline and
  technology.
- The **UK-specific baseline output** columns (sector totals belong to a
  calibration dataset, not a technology database).

Added beyond both:

- `parameter` as a real dictionary, with each parameter's CIMS target and its
  role in an optimization model, so the mapping is data rather than a table in
  a design note.
- `record-id`, `value-type`, `formula`, `derived-from` — Bataille has free-text
  references only, UKERC a reference string per block; neither can express
  "this number was derived from those two".
- `changelog`, because the repo is not under version control.

---

## 4. Model targets

`parameter.csv` carries a `cims-parameter` and an `optimization-use` column for
every parameter. The short version:

| This layer | CIMS YAML | Optimization / CGE |
| - | - | - |
| `capex` (+ `cost-basis`, `currency`) | `fcc` | investment cost coefficient |
| `opex-fixed` | `fom` | fixed O&M |
| `opex-variable` | — | variable O&M |
| `lifetime` | `lifetime` | vintage retirement age |
| `capacity` × `capacity-factor` × 8760 | `output` | annual activity bound |
| `efficiency`, or `tech-flow` input rows | `service-request`, one per carrier | input coefficients in the activity matrix |
| `tech-flow` material rows | — | material balance rows |
| `emissions-combustion` / `emissions-process` / `emissions-total` / `emissions-captured` (target = species) | `emissions` / `emissions-biomass` / `emissions-removal` | emission coefficients, scope 1, species kept explicit |
| `year-available` | `available` | investment window |
| `tech-constraint` shares | `market-share-new-max` / `-min`, `market-share-total` | bound constraints |
| `construction-time`, `cost-learning-rate` | — | investment lag, endogenous learning |
| `value-min` / `value-max` | — | scenario and sensitivity ranges |

Where CIMS has no field, the parameter is still recorded — it is why this layer
is not shaped like the YAML.

CHP follows decision D1: a CHP unit is a technology under the
`steam-and-hot-water` end use with variant `chp`, and its electricity is a
`tech-flow` output row with `co-product = yes`, so it is never counted as a
second technology on the electricity branch.

---

## 5. Conventions

Naming follows the one repo rule (design doc §5): `-` joins words within a
component, `_` separates components. Table names, sheet names, column names and
list terms are all single components.

Three vocabularies are **not** declared in this layer and must not be edited
here — `build-template.py` reads them at build time:

| List | Read from |
| - | - |
| `equipment`, `carrier`, `variant` | design doc §6.2 |
| `source-id` | `data/raw-data/source-details_sources.csv` |
| CIMS parameter names | `data/service-technology-map/README.md` |

Everything else is in the `LISTS` dict at the top of `build-template.py`, and
lands in `vocabulary.csv` with an `origin` column saying where it came from.
Adding a term is a modelling decision: change the source of truth, re-run the
build.

## 5a. The source list

`source-list.csv`, and a `source-list` sheet in the workbook, hold every source
behind the database — 103 of them — with its short form, full citation, role,
whether the document is held locally, how many rows it contributes and which
sectors it informs. The sheet is banded by sector like the wide views, so a
source used in several sectors appears under each: the band answers "where did
this sector's numbers come from".

Full citations come from three places, in order: the **References tab of the
UKERC workbook** for the originals UKERC cites; the author, title and year
already in `source-details_sources.csv` for documents held locally; and otherwise
nothing — the row says it has no citation rather than inventing one. Ten
sources are in that last state.

**Matching the References tab exposes its typos.** Five are certain enough to
alias, because the identity of the document is not in doubt — the tab writes
`ISII 1996` for `IISI 1996` and `NERA and AEA 2009` where the tables write
`NERA and EA 2009`, and it drops `et al.` from Stemmermann and Von Weizsäcker.
The rest were resolved with the modeller: `IETD 2013` and `ITP 2012` are the
tab's one Institute for Industrial Productivity database under two acronyms,
`IEAGHG 2000` and `IPPC 2012` were supplied directly, and `Normal 2013` is a
typo for Norman 2013 — the UKERC author's own PhD thesis, confirmed against the
report's reference list. Four short forms turned out to name a document the
data already cited under another name and were merged on 2026-08-29:
`Martin et al 2000b` → `Martin et al 2000`, `ECRA 2009a` → `ECRA 2009`,
`Novacem 2011b` → `Novacem 2011` and `IPPC 2012` → `EC 2012`. One is still
open: `IEAGHG 2013` is cited without the a/b suffix the tab requires.

One worth knowing about: **the References tab and the report PDF disagree on
which IEAGHG 2013 report is `a` and which is `b`.** The tab has `2013a` as the
CO₂-capture overview and `2013b` as the iron and steel CCS study; the PDF
reference list has them the other way round. The data cites `IEAGHG 2013b` for
top-gas-recycling with capture, and both documents are plausible for it, so the
citation shown follows the tab and the disagreement is recorded rather than
resolved.


## 5b. Aggregation

The roster is kept general on purpose. Four rules — R1 to R4, set out in design
doc **D11** and implemented in `aggregate.py` — rename `all-industry` to
`cross-sector`, hold the generic services (machine drive, facility services,
refrigeration, steam and hot water including CHP) once on that sector instead
of repeating them under every sector, retire the `other-services` residual bin,
and generalize technology names by dropping the carrier from an efficiency
bucket and the tier suffix from a name whose end use already carries the tier.

Two things make this safe to re-run and safe to argue with:

- **`aggregation-review.md` is regenerated on every `populate.py` run** and
  lists every reassignment with the evidence behind it, plus every general name
  and the source names it aggregates.
- **Nothing is discarded.** The three fact tables are unchanged in length and
  re-pointed at the general name, so a merged technology carries each source's
  rows side by side, told apart by `source-id` and ranked by
  `source-priority.csv`. The roster's `aggregated-from` column names what
  collapsed into each entry, and `technology-application.reported-sectors` /
  `reported-steps` keep the sector and step wording the sources actually used,
  so R2 can be reversed without re-extracting.

**R5 and R6 (design doc D12)** extend this: carriers collapse into fuel
groups where they behave the same as a source of heat, and `post-combustion` /
`oxyfuel` / `oxyfuel-ccs` collapse into one `ccs` variant. Both are
deliberately conservative — `coke` stays out of `coal`, `black-liquor` out of
`biomass`, `ammonia` and `methanol` out of any group, and the `-ccs` process
routes (`hisarna-ccs`, `corex-ccs`, `ulcored-ccs`, `top-gas-recycling-ccs`)
stay whole, because this database describes the plant stock that exists as well
as the options that might replace it.

**R7 — the roster and the views answer different questions.** 170 entries carry
no parameter, flow or constraint row: 17 are `placeholder` (the design document
declared them in scope, nothing extracted yet) and 153 are `unquantified` (a
source named the technology and reported no number). They stay in
`technology.csv`, because the CIMS names among them are what `cims-map.csv`
points at, and the wide views leave them out. **The roster says what the
database has been asked to cover; the view says what it knows.** The view
filters on the presence of fact rows rather than on the status column, so it
cannot drift from what `populate.py` labelled.

To change a grouping decision, edit the rule tables at the top of
`aggregate.py` and re-run — never the generated CSVs.

## 5c. The design vocabulary and the CIMS hierarchy

`adopt.py` runs inside `populate.py`, after the aggregation post-pass, and
does five things: writes the pre-adoption roster to `source-roster/`; runs
`build-design-crosswalk.py` on those rows; replaces the roster with the design
technology table; replaces the service nodes and process steps with the
hierarchy leaves; and rewrites every application and fact onto them.

- **A source name folds onto the nearest design technology** and is listed in
  that row's `aggregated-from`; nothing is dropped. The rule that chose each
  fold is in `design-crosswalk-technology.csv`: the design table's own
  `roster-match` column first, then hand maps and efficiency buckets, then the
  same device on the same end use, over a generic band, or in the same sector,
  and only then the end use's conventional row. Each fact keeps the name it
  arrived under in `roster-technology`, so a design technology's
  carrier-specific numbers stay apart.
- **The carrier is a list on the row, not a name component.** `energy-carrier`
  holds every section 6.2 carrier a folded source name or the design row's
  energy inputs name; `variant` holds the name's discriminator.
- **The hierarchy is the definitive mapping.** `cims-map.csv` is not rebuilt
  against it: the CIMS model inputs predate it, so its rows stay as the record
  of where the CIMS-sourced roster came from, and a row's legacy branch is used
  only as evidence when choosing a leaf.
- **Where a source does not say which leaf**, the application is applied on
  every leaf of the end use and flagged `expanded` in the crosswalk -- a
  generic boiler on every sector's steam leaf, for instance. The application's
  `note` says how its leaf was chosen.
- **Placeholders are the design rows no source quantifies** (263), and
  `unquantified` the ones a source names without a number (61). Both stay in
  the roster and out of the wide views.

`check-data.py` holds the adoption to this: end uses equal to the design
table's, every technology carrying a design-table label, every node on a
hierarchy leaf, every application and fact pointing at a technology and node
that exist, and every fact carrying its `roster-technology`.

## 6. Two rules about shape

**Every technology is standalone.** `baseline-technology` is left blank and each
row carries absolute values. An innovation is not stored as a delta against a
baseline it points at — that is how the two drift apart, and it makes a
technology unreadable without also loading its ancestor.

**Incremental efficiency options are bucketed**, into the `efficiency-base`,
`efficiency-moderate` and `efficiency-strong` variants defined in §6.2 of the
design document. CIMS already names technologies this way (Std / Eff / High
Eff) and the UKERC technology tables are largely a catalogue of such measures.
The buckets are technologies in their own right; the specific measures rolled
into each one are named in that row's note, so nothing is discarded — a bucket
is a grouping for the model, not a bin.

**Placeholders.** A technology a source names as relevant but does not quantify
is written with `status = placeholder` and no fact rows. The gap is then
visible in the roster instead of being absent from it. 17 of the current
technologies are placeholders, and a further 153 are `unquantified` (R7), concentrated in electric and hydrogen heat,
industrial heat pumps, mechanical vapour recompression, solar thermal and
nuclear process heat.

## 7. Known follow-ups

- `design/validate-names.py` walks `data/raw-data/` and
  `data/service-technology-map/` only. It does not yet check this folder —
  extending it to validate `technology.csv` keys and `vocabulary.csv` terms is
  the obvious next step.
- `service-node.branch` is the hand-off to CIMS, and the branch tree beyond
  `.steam` and `.process-heat.*` is not yet decided, so every `branch` is blank.
- `tech-flow` and `tech-constraint` are still empty: they are filled by the
  UKERC and Bataille extractions, which are not done.
- 11 `capex` rows carry `status = review` because the EPA 2007 and LBNL
  extractions predate the `cost-basis` rule. They need the basis read back out
  of their sources before those costs are pooled with anything.
- A technology name holds one variant, so a CHP unit with capture becomes
  `steam-turbine_natural-gas_ccs` and loses `chp`. The mapper notes it whenever
  several variants match; a compound variant term would fix it.
