# Industrial technology database

A database of the technologies that can provide each industrial end use in the CIMS
model, summarised from published sources. Each technology is an **archetype**: an
option a model chooses between, such as a fuel-fired boiler, a dry precalciner kiln
or a blast furnace with top-gas recycling. The technologies the sources describe are
**examples** of those archetypes. The database summarises what the examples say
about each archetype. It does not reproduce every source's detail.

The services and end uses are the CIMS hierarchy, `data/harmonized/records/cims_hierarchy.csv`,
which is the definitive list.

## Three layers

| Layer | What it holds | Where |
| - | - | - |
| 1. Extractions | Each source as reported, one long CSV per source. Never edited to fit the database. | `data/raw-data/` |
| 2. Examples | One row per technology as a source presents it, and the archetype it is an example of. Its facts sit beside it, converted to the archetype's basis. | `data/harmonized/records/source-example.csv` (the mapping); `data/harmonized/output/example-*.csv` (the facts) |
| 3. Archetypes | The vocabulary, the hierarchy nodes each archetype serves, and one summarised value set per archetype and parameter. | `data/harmonized/records/archetype*.csv`; `data/harmonized/output/archetype-*.csv` |

The wide view, `data/harmonized/output/wide-archetype.csv`, has one row per archetype, blank ones included.
The Excel workbook, `data/harmonized/output/technology-database.xlsx`, holds the same
tables with the wide views banded by family.

## Build

```
python data/harmonized/build.py            # everything; fails on any broken rule
python data/harmonized/build.py --check    # the checks only
python data/raw-data/check-manifest.py     # the source manifest against the disk
python data/raw-data/check-names.py        # names in the extraction layer
```

Edit the records in `data/harmonized/records/`. Never edit `output/`: the build
rewrites it.

## Where things are

| Folder | Contents |
| - | - |
| `docs/` | [design.md](docs/design.md): the rules. [pipeline.md](docs/pipeline.md): the build, and how to add a source or change a mapping. [vocabulary.md](docs/vocabulary.md): generated from the records. [decisions.md](docs/decisions.md): one line per decision, linked to its record. [hierarchy-change-requests.md](docs/hierarchy-change-requests.md): what the database asks of the CIMS hierarchy. |
| `data/raw-data/` | Source documents, the source manifest and the extractions (layer 1). |
| `data/harmonized/` | The database: `records/` (edited), `pipeline/` and `build.py` (code), `output/` (generated). |
| `data/service-technology-map/` | The CIMS YAML technology files. |
| `compare/cims-model-inputs/` | A later stage, parked: CIMS model-input technologies to be compared with the database. Not an input to it. |
| `archive/` | The decision records behind the current design, and superseded scripts and snapshots. Git holds the exact state before the 2026-09-23 restructure at tag `pre-archetype-restructure`. |
