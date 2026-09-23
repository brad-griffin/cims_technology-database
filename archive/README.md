# Archive

This folder keeps the records behind the current design. Nothing here is read by
the build. [docs/decisions.md](../docs/decisions.md) indexes the decisions, and
[docs/design.md](../docs/design.md) states the rules now in force.

The exact tree before the 2026-09-23 restructure is at the git tag
`pre-archetype-restructure`. That includes the generated tables deleted then:
`technology.csv`, `tech-parameter.csv`, the wide views, `source-roster/` and the
crosswalk outputs.

## decisions/

The documents that recorded each decision, dated by when the work started:

| File | What it is |
| - | - |
| `2026-08-26_design-doc.md` | The original design document, including §9 decisions D1–D13. Its §1 scope, §3 branches, §4 heat roster and §6.2 vocabularies are superseded. |
| `2026-09-10_aggregation-review.md` | The generated review of roster aggregation rules R1–R7, in its last state. |
| `2026-09-10_wide-view-review.md` | The hand-kept queue of comments on the wide view that set D13. |
| `2026-09-11_sector-end-use-table.{md,csv}` | The sector and end-use table, in its final form. Its content is now `data/harmonized/records/hierarchy-annotation.csv`. |
| `2026-09-11_sector-end-use-table-notes.md` | The decision log kept beside that table. |
| `2026-09-11_end-use-technology-table.csv`, `2026-09-11_technology-table-notes.md` | The design technology table and its notes. Its rows are now `records/archetype.csv`. |
| `2026-09-16_cims-hierarchy-harmonization.md`, `2026-09-16_cims-hierarchy-crosswalk.csv` | The hierarchy harmonization proposal (revision 6, applied) and its crosswalk from end uses to hierarchy nodes. |
| `2026-09-22_design-crosswalk-review.md` | The generated review of the roster-to-design crosswalk, as of the adoption pass. |
| `2026-09-22_harmonized-layer-readme.md` | The harmonized layer's README as of the adoption pass. |

## scripts/

| Path | What it is |
| - | - |
| `migrate_2026-09-23_archetypes.py` | The one-time migration that wrote `data/harmonized/records/` from the design tables and the adopted roster. It refuses to run again. |
| `archetype-renames-2026-09-23.csv` | Every archetype key renamed by that migration, with the reason. |
| `merge_2026-09-23_candidates.py`, `archetype-merges-2026-09-23.csv` | The one-time fold of the candidate merges the user approved, and its log. |
| `sector-2026-09-22.csv` | The retired sector dictionary the families were seeded from. |
| `retired-pipeline/` | The build before the restructure: `populate.py`, `aggregate.py`, `adopt.py`, the design crosswalk, `build-template.py`, `build-wide.py` and the rest. |
| `design-build/` | The scripts that generated the design tables and their markdown. |

## snapshots/

Copies of the design files taken before two earlier revisions:
`2026-09-16_pre-harmonization` and `2026-09-22_pre-revision-7`.
