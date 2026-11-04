# Industrial technology database

A database of the technologies that can provide each industrial end use in the CIMS
model, summarised from published sources. Each technology is an **archetype**: an
option a model chooses between, such as a fuel-fired boiler, a dry precalciner kiln
or a blast furnace with top-gas recycling. The technologies the sources describe are
**examples** of those archetypes. The database summarises what the examples say
about each archetype. It does not reproduce every source's detail.

The services and end uses are the CIMS hierarchy, `database/harmonized/records/cims_hierarchy.csv`,
which is the definitive list.

## Three layers

| Layer | What it holds | Where |
| - | - | - |
| 1. Extractions | Each source as reported, one long CSV per source. Never edited to fit the database. | `database/raw-data/` |
| 2. Examples | One row per technology as a source presents it, and the archetype it is an example of. Its facts sit beside it, converted to the archetype's basis. | `database/harmonized/records/source-example.csv` (the mapping); `database/harmonized/output/example-*.csv` (the facts) |
| 3. Archetypes | The vocabulary, the hierarchy nodes each archetype serves, and one summarised value set per archetype and parameter. | `database/harmonized/records/archetype*.csv`; `database/harmonized/output/archetype-*.csv` |

The wide view, `database/harmonized/output/wide-archetype.csv`, has one row per archetype, blank ones included.
The Excel workbook, `database/harmonized/output/technology-database.xlsx`, holds the same
tables with the wide views banded by family.

## Build

```
python database/harmonized/build.py            # everything; fails on any broken rule
python database/harmonized/build.py --check    # the checks only
python database/raw-data/check-manifest.py     # the source manifest against the disk
python database/raw-data/check-names.py        # names in the extraction layer
```

Edit the records in `database/harmonized/records/`. Never edit `output/`: the build
rewrites it.

## Where things are

The repo has two areas: the database itself, and what the database work asks of
CIMS or changes in it.

| Folder | Contents |
| - | - |
| `database/` | The technology database. See [database/README.md](database/README.md). |
| `database/raw-data/` | Source documents, the source manifest (`source-details_*.csv`), and the extractions (layer 1). `to-get.csv` lists documents still to obtain; `unavailable.csv` lists those that cannot be had; `background-register.csv` records downloaded documents that yielded no data, kept in `background-no-data-extracted/`. |
| `database/harmonized/` | The build: `records/` (edited), `pipeline/` and `build.py` (code), `output/` (generated, including the workbook). |
| `database/docs/` | [design.md](database/docs/design.md): the rules. [pipeline.md](database/docs/pipeline.md): the build, and how to add a source or change a mapping. [decisions.md](database/docs/decisions.md): one line per decision, linked to its record. [vocabulary.md](database/docs/vocabulary.md): generated from the records. |
| `database/reviews/` | Dated review files behind each decision; `sanity-checks/` holds each sanity-check run and the running issue list, `sanity-check-list.csv`. |
| `cims/` | Everything about the CIMS model. See [cims/README.md](cims/README.md). |
| `archive/` | The decision records behind the earlier design, superseded scripts and snapshots, and `intake/` (the finished intake working folders, not tracked). Git holds the exact state before the 2026-09-23 restructure at tag `pre-archetype-restructure`. |
