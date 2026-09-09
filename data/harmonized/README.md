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

Four scripts build this layer, in order:

```
python data/harmonized/extract-cims-roster.py    # CIMS model inputs -> cims-roster.csv
python data/harmonized/build-cims-map.py         # roster -> cims-map.csv (rules engine)
python data/harmonized/build-template.py         # schema -> empty tables + workbook
python data/harmonized/populate.py               # roster + extractions -> populated tables
python data/harmonized/build-cims-review.py      # map -> cims-review.md
python data/harmonized/build-currency.py         # BoC + StatCan -> currency factors
python data/harmonized/build-wide.py             # long tables -> wide views
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

### Grouping: sector → end use → technology

```
sector                iron-and-steel, cement, chemicals, … (10)
  end-use             the service delivered: steam-and-hot-water,
                      process-heat-high-temp, material-conversion, … (13)
    process-step      optional, sector-specific: blast-furnace,
                      clinker-kiln, steam-cracker …
      service-node    the demand node where technologies compete;
                      carries the CIMS branch string
        technology    equipment_carrier_variant, held once and applied
                      to every service node it serves
```

`end-use` is a *global* vocabulary — "high temperature heat" means the same
thing in chemicals and in non-metallic minerals, exactly as in the Bataille
UKTM sheet, so technologies are comparable across sectors. Anything genuinely
sector-specific goes in `process-step`, which is where a material balance
attaches (sinter → hot metal → liquid steel).

`service-node` is the join to CIMS: it is one sector × end use (× step), and it
holds the `branch` string and the unit that demand is measured in.

**A technology can serve several of them** (design doc D10). A natural gas dryer
is the same dryer in food and in chemicals, so the roster holds it once and
`technology-application` records every node it serves — one row per (technology,
service node). Sector and end use are still never stored on the technology
itself; anything that needs them joins through that table. 424 technologies
currently hold 1,216 applications, 142 of them serving more than one sector.

The wide views therefore show a technology under each sector it serves, which is
the same idiom the source list uses for a source cited in several sectors.

### Tables

| Table | Kind | What it holds |
| - | - | - |
| `sector` | registry | 10 industrial sectors, with UKTM / NAICS / ISIC crosswalks. Seeded. |
| `end-use` | registry | 13 end uses, their service type, unit and temperature tier. Seeded. |
| `process-step` | registry | Sector-specific production stages. Empty. |
| `service-node` | registry | sector × end-use × step, and the CIMS branch. Empty. |
| `technology-application` | link | Where each technology applies: one row per technology × service node. Empty. |
| `technology` | roster | One row per technology. Empty. |
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
| `cims-review.md` | The rename / merge / remove / add advice, generated from that map. |
| `wide-technology.csv` | Wide view: one row per technology **per sector it serves**, one column per parameter plus `_min` / `_max`. |
| `wide-flow.csv` | Wide view: one row per technology, one column per commodity, `in_` and `out_` prefixed. |
| `unit-conversion.csv` | Physical conversions used by the wide views. Exact constants. |
| `trl-scale-map.csv` | Crosswalk from each source's readiness scale to the common 1-9 ladder, with the band definitions and where they came from. |
| `reference-exchange-rate.csv` | Bank of Canada annual average rates to CAD, 2000–2025, USD and GBP. |
| `reference-cpi.csv` | Statistics Canada all-items CPI, Canada, 2002=100, monthly and annual, 2000–2025. |
| `currency-conversion.csv` | `YEAR_CUR` → `2025_CAD`, derived from those two by `build-currency.py`. |
| `source-priority.csv` | Which source supplies a central estimate: broadest first, then most recent. |
| `reference-capacity.csv` | Typical plant size per sector and process step, for turning a per-product rate into a total. Blank until filled. |

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

**Units are harmonised here and only here.** The long tables keep every value
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
| `capex-total` | 2025_CAD, absolute | **the capital cost of one unit at its working size** — a boiler, a kiln, a plant. `reference-capacity` and `reference-capacity-unit` say what size |

The divisor is only used when it is positive and above 0.05 GJ per unit. A
technology whose net energy is negative — blast furnace gas recovery, for
instance — would otherwise come back with a negative cost per GJ.

### capex-total: one unit at its working size

`capex-total` is the number a modeller usually wants first — what one boiler,
kiln or plant costs. It is formed either from a whole-unit sum the source
stated, or by multiplying a rate by that technology's own capacity, and
`reference-capacity` always says what size the total is for. Currently 18 of
101 costed technologies have one: a 3.6 MW packaged boiler at 92,043 CAD
(ETSAP I01), a 1,121 kW engine at 3.65M CAD (EPA 2017), a 9,950 kW gas turbine
at 27.1M CAD.

Two rules keep it honest:

**A rate must meet a scale from the same source.** Pairing UKERC's cost per
GJ/yr with an EPA plant size produces a total that reads as one source's
finding and is neither's. Where the scale comes from a different source the
total is not formed.

**Totals are never manufactured from a sector-wide rate.** Multiplying a UKERC
rate by *its* own scale gives the cost of deploying across the whole UK sector
— its integrated-steelworks baseline is 11.4 Mt/yr — not the cost of a plant.
Numbers six orders of magnitude apart in one column would look comparable and
are not.

That is why the other 83 technologies have no total: UKERC prices per unit of
annual product and never states a plant size. `reference-capacity.csv` lists
the 44 process steps waiting for a typical plant capacity — cement dry kiln,
integrated steelworks, steam cracker, and so on. Fill a row there and those
technologies gain a `capex-total` on the next run. The rows are deliberately
blank: nothing in that file is guessed.

**Every source for a parameter folds into one column.** Derived and
as-reported values sit together. The central value is the one from the
highest-ranked source in `source-priority.csv`; `_min` and `_max` span every
source's value and its own reported range. There is no source-id column — the
long tables carry the ids.

Two columns name the provenance, because a compilation is not a source:

- `sources` — who produced the number. For anything reaching us through UKERC
  that is the original UKERC cites: `IEAGHG 2013b` for top-gas-recycling with
  capture, `CE Delft 2010, Link 2008` for HIsarna, `IISI 1998, Worrell et al
  1999` for the sinter measures.
- `via` — the compilation it came through, where there is one. UKERC 2013
  appears here and nowhere else.

UKERC's own reference strings are parsed into source identifiers by
`data/raw-data/other-reports/ukerc-citations.py`, which mints one id per
distinct original and registers all 69 in the manifest as documents we do not
hold (design doc D7). It is fiddly parsing: `;` always separates citations and
`,` usually does, but `Worrell et al 1999, 2010` is two Worrell papers rather
than a second author, `Novacem 2011a, b` is two papers with the second written
as a bare letter (both turned out to be the same paper as `Novacem 2011`, and
all three are now one id), and the same source appears as both `IEA GHG 2008`
and `IEAGHG 2008`. The mapping is written to
`ukerc_2013_usable-energy-database_citations.csv` with the raw forms beside it
so it can be checked, and seven ids are flagged as possibly one document —
`NERA 2009`, `NERA and AEA 2009` and `NERA and EA 2009` are almost certainly
the same report with a typo, but merging them is a reading of the source rather
than a parsing rule.

Ranking still follows the compilation: a value UKERC selected and harmonised
carries UKERC's standing even though the number belongs to whoever UKERC cited.

A parameter that names a **target** still gets one column per target, so
`emissions-factor_co2` and `emissions-factor_nox` do not displace each other.
Only parameters and commodities that carry data get columns, so the sheets
track the database rather than the full dictionary.

Column-by-column definitions are on the `readme` sheet of the workbook and as
hover notes on each header cell.

---

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

`record-id` exists so that a value can be cited, superseded and logged. Prefix
by table: `tp-0001`, `tf-0001`, `tc-0001`.

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
failure.

Three flags stop the silent-pooling failures the design doc calls out:

- `cost-basis` — required with every `capex`. `equipment` / `installed` /
  `total-plant` / `overnight`. An equipment cost and an installed cost differ
  by up to a factor of two and look identical in a spreadsheet.
- `capacity-basis` — `thermal-input` / `thermal-output` / `product-output` /
  `electric-output`. A $/MW that does not say which is unusable.
- `currency` — `YEAR_DENOMINATION`, e.g. `2018_USD`. Required with every
  monetary value. **Values stay as reported**: no deflation, no currency
  conversion, no Canada adjustment in this layer (design doc §6.3, decision
  D2). Conversion happens once, at the CIMS `currency` parameter.
- `discount-rate` — the *source study's* rate, recorded whenever a value was
  levelised or inverted, so the model's own hurdle rate is not applied twice.

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
| `emissions-factor` (target = species) | `emissions` / `emissions-biomass` / `emissions-removal` | emission coefficients |
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
visible in the roster instead of being absent from it. 42 of the current
technologies are placeholders, concentrated in electric and hydrogen heat,
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
