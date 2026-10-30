# Technology database

The database of industrial technologies: each archetype, the source examples behind
it, and one summarised value set per parameter. The top-level README describes the
three layers and how to build.

| Folder | Contents |
| - | - |
| `raw-data/` | Layer 1: source documents (not tracked), the source manifest, and one extraction per source. Checks: `check-manifest.py`, `check-names.py`. Register a source with `register_source.py`. |
| `harmonized/` | Layers 2 and 3: `records/` (edited: archetypes, mappings, fill rules, judgements, reference tables), `pipeline/` and `build.py`, and `output/` (generated: the long tables, the wide views, and `technology-database.xlsx`). |
| `docs/` | The rules (`design.md`), the build (`pipeline.md`), the decision log (`decisions.md`), and the generated vocabulary (`vocabulary.md`). |
| `reviews/` | Dated review and proposal files the decisions link to; `sanity-checks/` holds each sanity-check run and `sanity-check-list.csv`. |

What the database asks of CIMS is in `../cims/`.
