# CIMS model inputs: the later comparison stage

Parked here on 2026-09-23. **Nothing in this folder feeds the database.** The CIMS
hierarchy (`database/harmonized/records/cims_hierarchy.csv`) is the definitive list of
CIMS services and end uses. The CIMS model inputs predate it and are out of date,
so they are not used to decide which technologies the database holds.

This stage runs later. It maps the CIMS model-input technologies onto archetypes as
a special kind of example, then reports where the model's values differ from the
database's.

| File | What it is |
| - | - |
| `extract-cims-roster.py` | Reads the model inputs in the `data_processing_calibration` repo (`cims/data/model_inputs/model/`) and writes `cims-roster.csv`, one row per distinct technology, region-collapsed. |
| `build-cims-map.py` | A rules engine that names each CIMS technology in the extraction form `equipment_carrier_variant`. It writes `cims-map.csv`. |
| `cims-map.csv`, `cims-roster.csv` | Its output as of 2026-08-27. |
| `build-cims-review.py`, `cims-review.md` | The rename / merge / remove advice as of 2026-09-22. |

## Before this stage is picked up again

- `build-cims-review.py` compares against the retired source roster (`source-roster/`,
  deleted 2026-09-23 and still in git at the tag `pre-archetype-restructure`). It
  needs rewriting against `records/archetype.csv` and `output/archetype-parameter.csv`.
- Two findings from the retired pipeline belong here:
  - **fuel nodes**: CIMS models a bare fuel choice as a technology, which becomes a
    flow on an archetype, not an example of one;
  - **merge-review**: CIMS sub-types (motor, fan, pump and compressor types) have no
    slot in an archetype name. They would be examples of one archetype.
- `classify()` in `build-cims-map.py` also names technologies in four extractors
  (`database/raw-data/other-reports/ukerc-extract.py`, `bataille-extract.py`,
  `database/raw-data/iea/iea-guide-extract.py`, `database/raw-data/peer-reviewed/ipcc-extract.py`),
  which load it from here. If this folder is ever removed, move `classify()` and its
  rule tables into `database/raw-data/` first.
- `build-cims-map.py` validates names against `database/raw-data/extraction-vocabulary.csv`.

## 2026-10-14: the comparison

Run from this folder: `python extract_cims_values.py <model_inputs/model path>`, then
`python build_cims_summary.py`, then `python compare_cims_archetypes.py`. The mapping in
`comparison/mapping/` is hand judgement and is not regenerated. Findings:
`comparison/cims-comparison-2026-10-14.md`.

2026-10-21: `python compare_ccs_addon.py` adds `comparison/ccs-node-comparison.csv` (each
sector CCS node against the capture archetype of its NETL stream type) and
`comparison/ccs-addon-comparison.csv` (the CCS portion only of each host with capture).
