# Industrial technology database

A database of the technologies that can provide each industrial end use in the CIMS
model, summarised from published sources. Each technology is an **archetype**: an
option a model chooses between, such as a fuel-fired boiler, a dry precalciner kiln
or a blast furnace with top-gas recycling. The technologies the sources describe are
**examples** of those archetypes. The database summarises what the examples say
about each archetype. It does not reproduce every source's detail.

The services and end uses are the CIMS hierarchy, `data/technology_database/cims-hierarchy.csv`,
which is the definitive list.

## Three layers

| Layer | What it holds | Where |
| - | - | - |
| 1. Extractions | Each source as reported, one long CSV per source. Never edited to fit the database. | `data/raw_data/technology_database/` |
| 2. Examples | One row per technology as a source presents it, and the archetype it is an example of. Its facts sit beside it, converted to the archetype's basis. | `data/technology_database/source-example.csv` (the mapping); `data/processed_data/technology_database/example-*.csv` (the facts) |
| 3. Archetypes | The vocabulary, the hierarchy nodes each archetype serves, and one summarised value set per archetype and parameter. | `data/technology_database/archetype*.csv`; `data/processed_data/technology_database/archetype-*.csv` |

The Excel workbook, `data/processed_data/technology_database/technology-database.xlsx`, is the wide view: one row
per archetype, blank ones included, banded by family. `data/processed_data/technology_database/README.md` says what
each output CSV is for.

## Build

Install the package once (`pip install -e .`), then, from anywhere in the repo:

```
python -m technology_database.build            # everything; fails on any broken rule
python -m technology_database.build --check    # the checks only
python src/technology_database/extraction/check_manifest.py     # the source manifest against the disk
python src/technology_database/extraction/check_names.py        # names in the extraction layer
```

Edit the records in `data/technology_database/`. Never edit `data/processed_data/`: the build
rewrites it.

## Where things are

The layout mirrors the CIMS repo, so the build and its records copy into CIMS as they are:
`src/technology_database/` goes to `src/CIMS/data_processing/technology_database/`, and
`data/technology_database/` to `data/technology_database/`.

| Folder | Contents | In CIMS |
| - | - | - |
| `src/technology_database/` | The build (`build.py`, `pipeline/`), the extraction code (`extraction/`: the manifest and name checks, `register_source.py`, the marimo input template), and the docs (`docs/`): [design.md](src/technology_database/docs/design.md), the rules; [pipeline.md](src/technology_database/docs/pipeline.md), the build and how to add a source; [decisions.md](src/technology_database/docs/decisions.md), one line per decision. | yes |
| `data/technology_database/` | The hand-edited records: archetypes, services, the source-to-archetype mapping, the CIMS hierarchy snapshot, `fill/`, `reference/` and `vocabulary/`. | yes |
| `data/raw_data/technology_database/` | Layer 1, the FRDR deposit: the source manifest (`source-details_*.csv`, with each source's licence), `background-register.csv` (the documents read that held no usable figures), the currency downloads (`currency/`), the extraction vocabulary, every extraction CSV in its publisher folder, and the script that made it where a source needed one. | from FRDR (not committed) |
| `data/processed_data/technology_database/` | What the build writes: the example and archetype tables, the reviews, `unfilled/`, `vocabulary.md`, and the workbook (not tracked). | written by the build |
| `primary-sources/` | The source documents (PDFs, workbooks, saved pages, bulk downloads) in the same publisher folders as the extractions; `to-process/` is the intake inbox. Not tracked: too large for git, and not on FRDR. | no |
| `source-intake/` | The intake lists: `to-get.csv` (documents still to obtain), `unavailable.csv` (those that cannot be had), and `background-no-data-extracted/` (the `_meta.csv` and any tables of the documents that held no usable figures). | no |
| `reviews/` | Dated review files behind each decision; `sanity-checks/` holds each sanity-check run and the running issue list, `sanity-check-list.csv`. | no |
| `review-packages/` | The external review packages and the scripts that build them. | no |
| `cims/` | What the database work asks of CIMS or changes in it. See [cims/README.md](cims/README.md). | no |
| `archive/` | The decision records behind the earlier design, superseded scripts and snapshots, and `intake-records/`. Git holds the exact state before the 2026-09-23 restructure at tag `pre-archetype-restructure`. | no |
