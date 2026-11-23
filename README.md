# Industrial technology database

A database of the technologies that can provide each industrial end use in the CIMS
model, summarised from published sources. Each technology is an **archetype**: an
option a model chooses between, such as a fuel-fired boiler, a dry precalciner kiln
or a blast furnace with top-gas recycling. The technologies the sources describe are
**examples** of those archetypes. The database summarises what the examples say
about each archetype. It does not reproduce every source's detail.

The services and end uses are the CIMS hierarchy, `data/technology_database/cims-hierarchy.csv`
in CIMS, which is the definitive list.

**Since 2026-11-20 the database is built in CIMS** (plan D6). The code and the hand-edited
records live in the CIMS repository (EMRG-SFU/cims); this repository keeps the extractions,
their scripts, and the review work. Their history up to the move stays here (commit `97a29cf`).

## Three layers

| Layer | What it holds | Where |
| - | - | - |
| 1. Extractions | Each source as reported, one long CSV per source. Never edited to fit the database. | Here: `data/raw_data/technology_database/` (the authoring copy). CIMS: the same path, copied from here until the FRDR deposit, then fetched from FRDR. |
| 2. Examples | One row per technology as a source presents it, and the archetype it is an example of. Its facts sit beside it, converted to the archetype's basis. | CIMS: `data/technology_database/source-example.csv` (the mapping); `data/processed_data/technology_database/example-*.csv` (the facts) |
| 3. Archetypes | The vocabulary, the hierarchy nodes each archetype serves, and one summarised value set per archetype and parameter. | CIMS: `data/technology_database/archetype*.csv`; `data/processed_data/technology_database/archetype-*.csv` |

The Excel workbook, `data/processed_data/technology_database/technology-database.xlsx` in CIMS, is the
wide view: one row per archetype, blank ones included, banded by family.
`src/CIMS/data_processing/technology_database/docs/outputs.md` says what each output CSV is for.

## Where to make changes

| Change | Where |
| - | - |
| The build, the checks, the extraction tools (`register_source.py`, the input template), the docs | CIMS: `src/CIMS/data_processing/technology_database/` |
| Records: archetypes, the source-to-archetype mapping, fill rules, reference tables, vocabulary, hierarchy | CIMS: `data/technology_database/` |
| A new or corrected extraction, and the script that makes it | Here: `data/raw_data/technology_database/<publisher>/` |
| Reviews, review packages, source intake, the archive, `cims/` | Here |

A new source starts here and ends in CIMS (plan section 2.4):

1. Put the document in `primary-sources/`.
2. Extract it into `data/raw_data/technology_database/<publisher>/` with the CIMS package's
   `register_source` and input template. The manifest rows go with the extraction; the record rows
   (citation, priority, source-example lines) go to a CIMS branch.
3. Copy the extractions into the CIMS worktree (below), build there, and map the new examples.
4. Deposit the new extractions to FRDR; once published, pin the version in CIMS.

## Setup and build

This project installs CIMS, editable, from a CIMS worktree beside it
(`../cims/data-processing-calibration`, set in `pyproject.toml`; point it at another worktree to
work against a branch):

```
uv sync
```

The build runs in the CIMS worktree, against the extractions there. Until the FRDR deposit, copy
this repository's extractions into it first:

```
cp -r data/raw_data/technology_database/. ../cims/data-processing-calibration/data/raw_data/technology_database/
cd ../cims/data-processing-calibration
uv run python -m CIMS.data_processing.technology_database.build            # everything; fails on any broken rule
uv run python -m CIMS.data_processing.technology_database.build --check    # the checks only
```

The review and comparison scripts here take the records and build outputs from that worktree
through the CIMS package, so run them with `uv run` from this repository.

## Where things are

| Folder | Contents | In CIMS |
| - | - | - |
| `data/raw_data/technology_database/` | Layer 1, the FRDR deposit: the source manifest (`source-details_*.csv`, with each source's licence), `background-register.csv` (the documents read that held no usable figures), the currency downloads (`currency/`), the extraction vocabulary, every extraction CSV in its publisher folder, and the script that made it where a source needed one. | copied from here, then from FRDR (not committed) |
| `primary-sources/` | The source documents (PDFs, workbooks, saved pages, bulk downloads) in the same publisher folders as the extractions; `to-process/` is the intake inbox. Not tracked: too large for git, and not on FRDR. | no |
| `source-intake/` | The intake lists: `to-get.csv` (documents still to obtain), `unavailable.csv` (those that cannot be had), and `background-no-data-extracted/` (the `_meta.csv` and any tables of the documents that held no usable figures). | no |
| `reviews/` | Dated review files behind each decision; `sanity-checks/` holds each sanity-check run and the running issue list, `sanity-check-list.csv`. Dated scripts there read the paths of their day. | no |
| `review-packages/` | The external review packages and the scripts that build them. | no |
| `cims/` | What the database work asks of CIMS or changes in it. See [cims/README.md](cims/README.md). | no |
| `archive/` | The decision records behind the earlier design, superseded scripts and snapshots, and `intake-records/`. Git holds the exact state before the 2026-09-23 restructure at tag `pre-archetype-restructure`. | no |
| `data/processed_data/` | Not tracked. A local copy of build outputs, if any, is a snapshot. | written by the build |
