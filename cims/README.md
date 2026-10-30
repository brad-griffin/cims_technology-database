# CIMS

What the technology database asks of the CIMS model, and the work done on the model
itself. The database (`../database/`) does not read anything here, except that its
hierarchy, `database/harmonized/records/cims_hierarchy.csv`, is the definitive list of
CIMS services and end uses.

| Item | Kind | What it is |
| - | - | - |
| [hierarchy-change-requests.md](hierarchy-change-requests.md) | request | Nodes the database needs CIMS to add or change, including those added to the database's hierarchy ahead of CIMS. |
| [to-fix.md](to-fix.md) | defect | Errors and open questions in the CIMS model inputs found while building the database. |
| `model-changes/` | model change | Scripts that change the CIMS model inputs, each with its revert (the inputs are not tracked in the CIMS repo, so these scripts are the record). |
| `comparison/` | analysis | The CIMS model-input technologies mapped onto the database's archetypes, and where their values differ. See its README. |
| `reporting-accounting/` | proposal | The design for reporting CIMS energy and emissions under several accounting conventions, its worked example, configs, and the StatCan inputs in `context/`. |
| `parameter-derivations/` | analysis | Methods for deriving CIMS technology parameters (CCS in steelmaking: capex and opex from a levelized cost of capture). |
| [iron-and-steel-hierarchy.html](iron-and-steel-hierarchy.html) | diagram | The iron and steel branch of the CIMS hierarchy. |
| `service-technology-map/` | prototype | CIMS YAML technology files in the planned format, with the field guide and the readiness-level scale. |
