# Entry fields
context / sub-context / target: include if applicable
value-type: -- choose one
    (default="fixed" if blank)
    - fixed: value entered directly in yaml
    - csv: point to file in data/processed/; parameter, context, sub-context, target, by-year, and by-region will be used to index the value
    - calculation: point to marimo notebook where calculation process is documented, but enter calculated value directly in yaml
    - ref: point to proxy technology and parameter (e.g., "baseboard_electricity.service-request.target[".electricity"].value")
    - formula: include reference parameters and formula for Python to resolve (e.g., "baseboard_electricity.service-request.target[".electricity"].value / 2.5")
by-year:
    (default=FALSE if blank)
    - true: use annual year-value pairs included in csv file
    - false: use constant time-independent value
by-region:
    (default=FALSE if blank)
    - true: use region-value pairs included in csv file
    - false: use region-independent value
source: include source of data, assumption, or reason for use of proxy technology
note: include if applicable
currency: should be in the format YEAR_3-CHAR-DENOMINATION (e.g., "2015_USD"); fcc and fom need to be in this currency

# Notes
--> if no value is entered, the default parameter value will be used in the simulation
--> tech unit should match the service-provide unit of the parent branch node
--> output is in the same unit as the tech unit
--> repeat parameters service-request, emissions, emissions-biomass, emissions-removal as needed
--> for service-request note if units change from tech unit

# Naming
All names here follow one rule: `-` joins words within a component, `_` separates
components. Parameter and field names are single components (`value-type`,
`by-year`, `service-request`). Technology names are
`equipment_carrier_variant` (`boiler_natural-gas`, `combustion-turbine_biogas`),
and a technology's filename is its name. A branch string is the folder path
dotted, dropping grouping folders and the `technology/` leaf.

Currency and unit values keep the underscore as their component separator by the
same rule (`2015_CAD`, `k_pkm`).

The full statement of the rule is in `database/docs/design.md` (Naming). Extraction names
use the terms in `database/raw-data/extraction-vocabulary.csv`; archetype names use the
vocabularies in `database/harmonized/records/vocabulary/`. Run
`python database/raw-data/check-names.py` from the repo root to check the tree.
