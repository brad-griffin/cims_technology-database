"""Build the harmonized technology-database template.

Run from the repo root:   python data/harmonized/build-template.py

Writes, into data/harmonized/:
  * one header-only CSV per table (the tables themselves; seeded tables carry
    their dictionary rows)
  * technology-database-template.xlsx -- the same tables as an authoring
    workbook, with dropdown validation, header notes, frozen panes

Nothing here invents a second register.  Three vocabularies are read from
elsewhere and must not be edited in this file:
  * equipment / carrier / variant  <- design/industrial heat technology
    database design.md, section 6.2
  * source-id                      <- data/raw-data/source-details_sources.csv
  * CIMS YAML parameters           <- data/service-technology-map/README.md
Everything else is declared in SCHEMA and SEEDS below.

Naming follows the repo rule: '-' joins words within a component, '_'
separates components.  Table names, sheet names and column names are single
components.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workbook import apply_view

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DESIGN_DOC = ROOT / "design" / "industrial heat technology database design.md"
MANIFEST = ROOT / "data" / "raw-data" / "source-details_sources.csv"
MANIFEST_FILES = ROOT / "data" / "raw-data" / "source-details_files.csv"
WORKBOOK = HERE / "technology-database-template.xlsx"

# --- controlled lists declared here -------------------------------------
# (equipment, carrier and variant are NOT here -- they come from the design
# document.  source-id is NOT here -- it comes from the manifest.)
LISTS: dict[str, list[str]] = {
    "sector": [],            # filled from the sector seed
    "end-use": [],           # filled from the end-use seed
    "commodity": [],         # filled from the commodity seed
    "parameter": [],         # filled from the parameter seed
    "service-type": ["heat-supply", "process", "other-service"],
    "temperature-tier": ["low-temp", "medium-temp", "high-temp", "not-applicable"],
    # Two scales are in the database at once and they do not mean the same thing.
    # the scales sources report on; the crosswalk to the common 1-9 ladder is
    # data, in trl-scale-map.csv, not a rule in code
    "trl-scale": ["trl-1-9", "nasa-1-9", "iea-etp"],
    "heat-output-type": ["steam", "hot-water", "direct", "not-applicable"],
    "role": ["baseline", "incumbent", "new", "improvement", "alternative-route"],
    "relationship-to-baseline": ["additional", "replacement", "standalone"],
    "state-of-development": ["existing", "commercial", "pilot", "r-and-d", "conceptual"],
    "value-type": ["reported", "derived", "assumed", "proxy", "placeholder"],
    "cost-basis": ["equipment", "installed", "total-plant", "overnight", "not-applicable"],
    "capacity-basis": ["thermal-input", "thermal-output", "product-output", "electric-output"],
    "uncertainty-type": ["reported-range", "assumed-range", "standard-deviation",
                         "percent-of-central", "expert-judgement"],
    "direction": ["input", "output"],
    "commodity-class": ["energy", "material", "emission"],
    "parameter-class": ["technical", "cost", "emissions", "deployment"],
    "constraint": ["current-adoption-share", "max-adoption-share", "market-share-new-max",
                   "market-share-new-min", "market-share-total", "growth-rate-max",
                   "applicability-to-stock", "retirement-rate", "capacity-max",
                   "capacity-min", "refit-required"],
    "constraint-basis": ["of-baseline-stock", "of-new-sales", "of-sector-output", "absolute"],
    "yes-no": ["yes", "no"],
    "confidence": ["high", "medium", "low"],
    "status": ["placeholder", "unquantified", "draft", "review", "final",
               "superseded"],
}

# --- table definitions ---------------------------------------------------
# (column, list-name-or-None, note)  -- list-name drives the Excel dropdown
SCHEMA: dict[str, dict] = {}


def table(name, kind, purpose, columns):
    SCHEMA[name] = {"kind": kind, "purpose": purpose, "columns": columns}


table("sector", "registry",
      "The industrial sectors the database covers. The top grouping level.",
      [("sector", None, "Key. Lowercase hyphenated, one component."),
       ("sector-label", None, "Display name."),
       ("description", None, "What the sector covers, and what it excludes."),
       ("uktm-code", None, "UKTM sector prefix, for crosswalk to the Bataille UKTM sheet."),
       ("naics-2017", None, "NAICS code(s), semicolon separated. Statistical concordance."),
       ("isic-rev4", None, "ISIC Rev.4 code(s), semicolon separated."),
       ("note", None, "")])

table("end-use", "registry",
      "The energy service or process function a technology delivers. Global "
      "vocabulary: the same end use recurs across sectors.",
      [("end-use", None, "Key."),
       ("end-use-label", None, "Display name."),
       ("service-type", "service-type", "heat-supply, process, or other-service."),
       ("service-unit-default", None, "Unit the service demand is measured in (GJ, t)."),
       ("temperature-tier", "temperature-tier", "Tier where the end use is tier-specific."),
       ("description", None, ""),
       ("note", None, "")])

table("process-step", "registry",
      "Sector-specific production stages, where a sector decomposes into steps "
      "that each carry their own material balance. Optional: an end use needs "
      "no process step to be modelled.",
      [("process-step", None, "Key. Unique within the sector."),
       ("sector", "sector", "FK to sector."),
       ("process-step-label", None, "Display name."),
       ("product", "commodity", "FK to commodity: the step's main output."),
       ("product-unit", None, "Unit of the main output (t, GJ)."),
       ("upstream-step", None, "FK to process-step: the step feeding this one."),
       ("description", None, ""),
       ("note", None, "")])

table("service-node", "registry",
      "sector x end-use (x process-step): the demand node technologies compete "
      "at, and the join point to the CIMS branch tree.",
      [("service-node", None, "Key. Convention: sector_end-use[_process-step]."),
       ("sector", "sector", "FK to sector."),
       ("end-use", "end-use", "FK to end-use."),
       ("process-step", None, "FK to process-step. Blank where the end use is not step-specific."),
       ("branch", None, "CIMS branch string, dotted (see design doc section 3). Blank if not in CIMS."),
       ("service-unit", None, "Unit of service demand at this node. Technology output must match."),
       ("service-description", None, "What is demanded here, in one line."),
       ("note", None, "")])

table("technology-application", "link",
      "Where each technology applies: one row per technology and service node. "
      "A technology is one thing wherever it is installed -- a natural gas dryer "
      "is the same dryer in food and in chemicals -- so the roster holds it once "
      "and this table says which sectors and end uses it serves. Without it the "
      "roster would have to either repeat the technology per sector or keep only "
      "the first sector that claimed it.",
      [("technology", "technology", "FK to technology."),
       ("service-node", "service-node", "FK to service-node."),
       ("sector", "sector", "Denormalised from the service node, for reading."),
       ("end-use", "end-use", "Denormalised from the service node, for reading."),
       ("process-step", None, "Denormalised from the service node, for reading."),
       ("source-id", "source-id", "Which source places the technology at this node."),
       ("reported-sectors", None,
        "For a generic end use held once on cross-sector (aggregate.py, R2): the sectors the "
        "sources actually reported it for, semicolon separated. Keeps the collapse reversible."),
       ("reported-steps", None,
        "For the same rows: the process steps the sources named, semicolon separated. These are "
        "source wording (motor size bands, 'CHP plants'), not a controlled vocabulary, which is "
        "why they do not survive as process-step."),
       ("note", None, "")])

table("technology", "roster",
      "One row per technology. The detail level is the Bataille UKTM sheet: "
      "distinct equipment/carrier/variant combinations, not individual plant "
      "designs.",
      [("technology", None, "Key. equipment_carrier_variant, per design doc section 5."),
       ("equipment", "equipment", "Restates name component 1. Never split the name to recover it."),
       ("energy-carrier", "carrier", "Restates name component 2."),
       ("variant", "variant", "Restates name component 3."),
       ("description", None, "What the technology is and how it differs from the baseline."),
       ("role", "role", "baseline, incumbent, new, improvement, alternative-route."),
       ("relationship-to-baseline", "relationship-to-baseline",
        "additional (adds to a baseline plant), replacement (displaces it), standalone."),
       ("baseline-technology", "technology", "FK to technology: what this improves on or replaces."),
       ("competes-with", None, "FK list, semicolon separated. Mutually exclusive options."),
       ("requires", None, "FK list, semicolon separated. Must be present for this to apply."),
       ("state-of-development", "state-of-development", ""),
       ("trl", None, "Readiness level 1-9 on the common ladder, which is the one "
        "defined in data/service-technology-map/technology-readiness-levels.md. "
        "Comparable across sources: whatever scale a source used is mapped here "
        "through trl-scale-map.csv, which also carries that file's industrial-process "
        "reading of each level. A range is carried at its lower bound."),
       ("trl-as-reported", None, "Exactly what the source printed, including a range "
        "(\"6-7\") or a scale-specific rung (\"9B\"). Never parse trl from this; it is "
        "here so the mapping can be checked."),
       ("trl-scale", "trl-scale", "The scale the source used, which trl was mapped FROM. "
        "Required whenever trl is set."),
       ("year-available", None, "From the TRL rule (design doc section 9, D5). Justify in note."),
       ("capacity-basis", "capacity-basis", ""),
       ("capacity-unit", None, "Unit capacity is expressed in (MW, Mt/yr)."),
       ("heat-output-type", "heat-output-type", ""),
       ("temperature-tier", "temperature-tier", ""),
       ("retrofit-applicable", "yes-no",
        "Retrofit and greenfield are separate technologies (D4); this flags that a retrofit twin exists."),
       ("source-id", "source-id", "Primary source for the roster entry itself."),
       ("aggregated-from", None,
        "The source names this general name aggregates, semicolon separated (aggregate.py, R4). "
        "Blank where the name was always this general. Every aggregated technology keeps every "
        "contributing source's fact rows, told apart by source-id and ranked by source-priority; "
        "nothing is dropped on a merge."),
       ("status", "status", ""),
       ("note", None, "")])

table("parameter", "dictionary",
      "The parameter dictionary. Defines every parameter name usable in "
      "tech-parameter, its unit dimension, and where it lands in each model.",
      [("parameter", None, "Key."),
       ("parameter-label", None, "Display name."),
       ("parameter-class", "parameter-class", ""),
       ("definition", None, "What the number means. Precise enough to stop two sources being pooled wrongly."),
       ("unit-dimension", None, "Dimension, not a specific unit (currency/capacity, GJ/GJ, fraction)."),
       ("unit-default", None, "Unit to use unless the source's own unit is kept."),
       ("basis-required", None, "Flag column that must be filled alongside this parameter."),
       ("requirement", None, "required, recommended, or optional for a complete technology entry."),
       ("cims-parameter", None, "Target field in the CIMS YAML. Blank where CIMS has no field."),
       ("optimization-use", None, "How a TIMES/MESSAGE-type model uses it. Blank if unused."),
       ("note", None, "")])

table("commodity", "dictionary",
      "Energy carriers, materials and emission species used in tech-flow. "
      "One list so an input in one sector matches an output in another.",
      [("commodity", None, "Key."),
       ("commodity-label", None, "Display name."),
       ("commodity-class", "commodity-class", "energy, material, or emission."),
       ("unit-default", None, "GJ for energy, t for material, t for emission."),
       ("energy-carrier", "carrier", "FK to the section 6.2 carrier vocabulary, where one applies."),
       ("biogenic", "yes-no", "Biogenic carbon routes to emissions-biomass, not emissions."),
       ("note", None, "")])

table("tech-parameter", "fact",
      "The main fact table. One row per number. Long format: adding a "
      "parameter never adds a column.",
      [("record-id", None, "Stable key, tp-<source-id>-NNNN, e.g. tp-ukerc_2013_001-0042. Numbered within the source so an edit to one extraction does not renumber another. Cited by derived-from and by the changelog."),
       ("technology", "technology", "FK to technology."),
       ("parameter", "parameter", "FK to parameter."),
       ("context", None, "CIMS entry field. Include if applicable."),
       ("sub-context", None, "CIMS entry field. Include if applicable."),
       ("target", None, "CIMS entry field. For service-request and emissions, the carrier or species."),
       ("region", None, "Blank = region independent."),
       ("year", None, "Blank = time independent."),
       ("value", None, "The central value."),
       ("unit", None, "The source's own unit, verbatim. Never converted here (design doc 6.3)."),
       ("value-min", None, "Low end. Blank if the source gives no range."),
       ("value-max", None, "High end."),
       ("uncertainty-type", "uncertainty-type", "How min/max were arrived at. Required if either is filled."),
       ("value-type", "value-type", "reported, derived, assumed, proxy, placeholder."),
       ("formula", None, "Python expression if derived. Parameter names use underscores here only."),
       ("derived-from", None, "record-id list, semicolon separated. Required when value-type is derived."),
       ("cost-basis", "cost-basis", "REQUIRED with every capex. equipment/installed/total-plant/overnight."),
       ("capacity-basis", "capacity-basis", "Required with every capacity-denominated value."),
       ("currency", None, "YEAR_DENOMINATION, e.g. 2018_USD. Required with every monetary value."),
       ("discount-rate", None, "The source study's rate, where the value was levelised or inverted."),
       ("source-id", "source-id", "FK to source-details_sources.csv. Required unless value-type is assumed."),
       ("source-file", None, "File within that source (its file_name in the manifest)."),
       ("source-locator", None, "Page, table, or sheet!cell. Must land a reader on the number."),
       ("extraction-file", None, "Path to the raw-data long CSV this was harmonized from, if any."),
       ("via-source-id", "source-id",
        "The compilation the value was read out of, when source-id names an original "
        "that is not held locally. Blank when source-id is the document read."),
       ("via-locator", None, "Where in the compilation: sheet!cell, row id, or page."),
       ("confidence", "confidence", ""),
       ("status", "status", ""),
       ("note", None, "")])

table("tech-flow", "fact",
      "Input and output vectors: energy carriers, materials and emission "
      "species per unit of activity. UKERC carries this as 100+ sparse "
      "columns; here it is one row per non-zero flow.",
      [("record-id", None, "Stable key, tf-<source-id>-NNNN, e.g. tf-ukerc_2013_001-0042."),
       ("technology", "technology", "FK to technology."),
       ("direction", "direction", "input or output."),
       ("commodity", "commodity", "FK to commodity."),
       ("value", None, "Quantity per unit of the denominator named in per-unit."),
       ("unit", None, "Unit of the quantity (GJ, t, Nm3)."),
       ("per-unit", None, "The denominator: GJ-heat-output, t-crude-steel, unit-capacity."),
       ("value-min", None, ""),
       ("value-max", None, ""),
       ("uncertainty-type", "uncertainty-type", ""),
       ("co-product", "yes-no",
        "yes marks a secondary output (CHP electricity, blast furnace gas) so it is not double counted."),
       ("value-type", "value-type", ""),
       ("formula", None, ""),
       ("derived-from", None, "record-id list, semicolon separated."),
       ("region", None, ""),
       ("year", None, ""),
       ("source-id", "source-id", ""),
       ("source-file", None, ""),
       ("source-locator", None, ""),
       ("via-source-id", "source-id",
        "The compilation the value was read out of, when source-id names an original "
        "that is not held locally. Blank when source-id is the document read."),
       ("via-locator", None, "Where in the compilation: sheet!cell, row id, or page."),
       ("status", "status", ""),
       ("note", None, "")])

table("tech-constraint", "fact",
      "Adoption, stock and capacity limits. Feeds CIMS market-share bounds and "
      "the bound constraints of an optimization model.",
      [("record-id", None, "Stable key, tc-<source-id>-NNNN, e.g. tc-ukerc_2013_001-0042."),
       ("technology", "technology", "FK to technology."),
       ("constraint", "constraint", ""),
       ("region", None, ""),
       ("year", None, "Blank = applies throughout."),
       ("value", None, ""),
       ("unit", None, "fraction, %, or a capacity unit."),
       ("constraint-basis", "constraint-basis", "What the share is a share OF. Required for share constraints."),
       ("value-min", None, ""),
       ("value-max", None, ""),
       ("value-type", "value-type", ""),
       ("source-id", "source-id", ""),
       ("source-file", None, ""),
       ("source-locator", None, ""),
       ("via-source-id", "source-id",
        "The compilation the value was read out of, when source-id names an original "
        "that is not held locally. Blank when source-id is the document read."),
       ("via-locator", None, "Where in the compilation: sheet!cell, row id, or page."),
       ("status", "status", ""),
       ("note", None, "")])

table("changelog", "log",
      "What changed, when and why. The repo is not under version control, so "
      "edits to a value are recorded here rather than inferred.",
      [("date", None, "YYYY-MM-DD."),
       ("who", None, ""),
       ("table", None, "Table the change landed in."),
       ("record-id", None, "Row affected. Blank for a structural change."),
       ("change", None, "What changed, old value to new value."),
       ("reason", None, "Why. A source correction names the source."),
       ("note", None, "")])

table("vocabulary", "dictionary",
      "Every controlled list in one place, long format. Drives the workbook's "
      "dropdowns. Lists sourced elsewhere (equipment, carrier, variant, "
      "source-id) are merged in at build time and marked in origin.",
      [("list-name", None, "Which list the term belongs to."),
       ("term", None, "The term itself."),
       ("origin", None, "declared-here, design-doc-6.2, or source-manifest."),
       ("note", None, "")])


# --- seed rows for the dictionary tables --------------------------------
# These are structure, not data: they define what may be recorded, not what
# any technology's numbers are.

SECTORS = [
    ("cross-sector", "Cross-sector",
     "Technologies that supply the same service in any industrial sector - boilers, CHP units, "
     "motors, lighting, space conditioning, refrigeration. Held once here rather than copied "
     "into every sector. The generic end uses (aggregate.py, R2) live only on this sector, and "
     "the sectors a source reported them for stay in technology-application.reported-sectors.",
     "", "", ""),
    # sector, label, description, uktm, naics, isic
    ("iron-and-steel", "Iron and steel",
     "Coke making, ironmaking, steelmaking, casting and hot rolling. Excludes downstream fabrication.",
     "IIS", "3311;3312", "241"),
    ("non-ferrous-metals", "Non-ferrous metals",
     "Primary and secondary aluminium, copper, zinc, nickel and other non-ferrous smelting and refining.",
     "INF", "3313;3314", "242"),
    ("cement", "Cement",
     "Clinker production, grinding and blending. Split from non-metallic minerals because the kiln dominates.",
     "ICM", "32731", "2394"),
    ("non-metallic-minerals", "Non-metallic minerals",
     "Lime, glass, ceramics, gypsum and other mineral products. Cement is its own sector.",
     "INM", "327", "239"),
    ("chemicals", "Chemicals",
     "Petrochemicals, industrial gases, ammonia and fertiliser, and other bulk and fine chemicals.",
     "ICH", "325", "20"),
    ("petroleum-refining", "Petroleum refining",
     "Crude distillation, conversion, treating and utilities at refineries.",
     "", "32411", "192"),
    ("pulp-and-paper", "Pulp and paper",
     "Pulping, papermaking, drying and converting.",
     "IPP", "322", "17"),
    ("food-and-beverage", "Food and beverage",
     "Food processing, beverage production and tobacco.",
     "IFD", "311;312", "10;11;12"),
    ("mining", "Mining and mineral extraction",
     "Metal and non-metal mining, milling and on-site processing. Excludes oil and gas extraction.",
     "", "212", "07;08"),
    ("other-industry", "Other industry",
     "Manufacturing not covered by another sector: machinery, vehicles, textiles, wood products, construction.",
     "IOI", "", ""),
]

END_USES = [
    # end-use, label, service-type, unit, tier, description
    ("steam-and-hot-water", "Steam and hot water", "heat-supply", "GJ", "not-applicable",
     "Indirect heat raised in a boiler or CHP unit and distributed as steam or hot water. "
     "One branch, not tiered (design doc D3); steam conditions ride as temperature-output and "
     "pressure-output. CHP sits here with electricity as a secondary output (D1)."),
    ("process-heat-low-temp", "Process heat, low temperature", "heat-supply", "GJ", "low-temp",
     "Direct heat delivered below 150 degC."),
    ("process-heat-medium-temp", "Process heat, medium temperature", "heat-supply", "GJ", "medium-temp",
     "Direct heat delivered between 150 and 400 degC."),
    ("process-heat-high-temp", "Process heat, high temperature", "heat-supply", "GJ", "high-temp",
     "Direct heat delivered above 400 degC."),
    ("drying-and-separation", "Drying and separation", "heat-supply", "GJ", "not-applicable",
     "Moisture removal and thermal separation. Kept distinct from process heat because both "
     "sources treat it as its own service and non-thermal routes compete here."),
    ("material-preparation", "Material preparation", "process", "t", "not-applicable",
     "Upstream conditioning of feed: sintering, pelletising, coke making, crushing and grinding."),
    ("material-conversion", "Material conversion", "process", "t", "not-applicable",
     "The chemical or metallurgical transformation at the core of the sector: reduction, "
     "calcination, cracking, reforming, pulping, smelting."),
    ("forming-and-finishing", "Forming and finishing", "process", "t", "not-applicable",
     "Casting, rolling, drawing, sheet forming, coating and finishing."),
    ("electrochemical", "Electrochemical processing", "process", "t", "not-applicable",
     "Electrolytic reduction and electrowinning."),
    ("machine-drive", "Machine drive", "other-service", "GJ", "not-applicable",
     "Motors, pumps, fans, compressors and conveying."),
    ("refrigeration-and-cooling", "Refrigeration and cooling", "other-service", "GJ", "not-applicable",
     "Process cooling, chilling and refrigeration."),
    ("facility-services", "Facility services", "other-service", "GJ", "not-applicable",
     "Space conditioning, lighting and other non-process site energy use."),
]

PARAMETERS = [
    # parameter, label, class, definition, unit-dimension, unit-default,
    # basis-required, requirement, cims, optimization-use
    ("lifetime", "Lifetime", "technical",
     "Expected technical service life of the installed equipment.",
     "time", "years", "", "required", "lifetime", "Vintage retirement age."),
    ("capacity", "Capacity", "technical",
     "Rated capacity of one unit, on the basis named in capacity-basis.",
     "capacity", "MW", "capacity-basis", "required", "",
     "Unit size for integer or lumpy investment; otherwise the cost denominator."),
    ("capacity-factor", "Capacity factor", "technical",
     "Annual output as a fraction of output at rated capacity running continuously.",
     "fraction", "%", "", "required", "", "Availability factor bounding annual activity."),
    ("annual-output", "Annual output", "technical",
     "Useful output of one unit over a year. Equals capacity x capacity-factor x 8760 where both are known.",
     "energy or mass", "GJ", "capacity-basis", "recommended", "output", ""),
    ("efficiency", "Efficiency", "technical",
     "Useful output per unit of energy input, on the basis named in note (HHV or LHV). "
     "For multi-carrier technologies record one tech-flow row per input instead.",
     "fraction", "%", "", "required", "service-request",
     "Inverted to an input coefficient in the activity matrix."),
    ("efficiency-chp", "CHP overall efficiency", "technical",
     "Combined heat and electricity output per unit of fuel input.",
     "fraction", "%", "", "optional", "", ""),
    ("heat-to-power-ratio", "Heat-to-power ratio", "technical",
     "Useful heat output per unit of electricity output for a CHP unit.",
     "dimensionless", "dimensionless", "", "optional", "",
     "Fixes the joint-output proportion."),
    ("specific-energy-consumption", "Specific energy consumption", "technical",
     "Total final energy input per unit of product output. The UKERC SEC, on a final-energy basis.",
     "energy/mass", "GJ/t", "", "recommended", "", "Benchmark for calibrating the activity matrix."),
    ("temperature-output", "Output temperature", "technical",
     "Temperature of the delivered heat. Governs tier assignment.",
     "temperature", "degC", "", "required", "", ""),
    ("temperature-min", "Output temperature, minimum", "technical",
     "Low end where the source gives a range.", "temperature", "degC", "", "optional", "", ""),
    ("temperature-max", "Output temperature, maximum", "technical",
     "High end where the source gives a range.", "temperature", "degC", "", "optional", "", ""),
    ("pressure-output", "Output pressure", "technical",
     "Pressure of delivered steam. Record the source's own unit.",
     "pressure", "psig", "", "optional", "", ""),
    ("availability", "Annual availability", "technical",
     "Percentage of the hours in a year the unit is ABLE to run, after planned and "
     "unplanned outages. It is a property of the equipment, not of how it is operated: "
     "capacity-factor is what it actually produced, and is bounded above by this. A boiler "
     "at 90% availability and a 60% capacity factor was available for 90% of the year and "
     "run for 60% of it.",
     "fraction", "%", "", "recommended", "",
     "Upper bound on annual activity, separate from the dispatch decision."),
    ("load-range-min", "Minimum stable load", "technical",
     "Lowest sustained output as a fraction of rated capacity.",
     "fraction", "%", "", "optional", "", "Lower bound on operation when committed."),
    ("degradation-rate", "Performance degradation rate", "technical",
     "Annual fractional loss of efficiency or capacity over the lifetime.",
     "fraction/time", "%/yr", "", "optional", "", ""),
    ("capex", "Capital cost", "cost",
     "Overnight capital cost per unit of capacity, on the basis named in cost-basis.",
     "currency/capacity", "", "cost-basis", "required", "fcc",
     "Investment cost coefficient."),
    ("opex-fixed", "Fixed operating cost", "cost",
     "Annual operating and maintenance cost that does not vary with output.",
     "currency/capacity/time", "", "capacity-basis", "required", "fom", "Fixed O&M coefficient."),
    ("opex-variable", "Variable operating cost", "cost",
     "Operating cost per unit of output, excluding purchased energy and feedstock.",
     "currency/output", "", "", "recommended", "", "Variable O&M coefficient."),
    ("opex-total", "Total operating cost", "cost",
     "Fixed and variable operating cost reported TOGETHER, where the source does not "
     "split them. Say in the row note exactly what it includes - sources differ on "
     "whether fuel, electricity, materials and depreciation are inside. Never record an "
     "opex-fixed or opex-variable on top of an opex-total for the same technology and source.",
     "currency/output", "", "cost-basis", "optional", "", "Operating cost coefficient."),
    ("capital-recovery", "Capital recovery factor", "cost",
     "Annualisation factor applied to capex. Record the source study's own factor, not the model's.",
     "fraction/time", "%/yr", "", "optional", "capital-recovery", ""),
    ("discount-rate", "Discount rate", "cost",
     "Financial rate used by the source when levelising. Recorded so a levelised cost can be "
     "inverted without double-counting the model's own hurdle rate.",
     "fraction", "%", "", "recommended", "", ""),
    ("construction-time", "Construction lead time", "cost",
     "Years from investment decision to commissioning.",
     "time", "years", "", "optional", "", "Investment lag."),
    ("cost-learning-rate", "Learning rate", "cost",
     "Fractional capex reduction per doubling of cumulative installed capacity.",
     "fraction", "%", "", "optional", "", "Endogenous learning curve."),
    ("decommissioning-cost", "Decommissioning cost", "cost",
     "End-of-life cost per unit of capacity.", "currency/capacity", "", "cost-basis", "optional", "", ""),
    # Scope 1 only, four parameters, set by the user 2026-09-10 (D13). Species
    # stays in `target` and is NOT converted to CO2e: co2, co2e and pfc are all
    # carried as reported, because an explicit species is worth more columns
    # than a single converted one. Non-GHG species are out of scope entirely.
    ("emissions-combustion", "Combustion emissions factor", "emissions",
     "Emissions from burning fuel at the technology, per unit of energy input or product "
     "output. Species named in target. Excludes the process reaction, which is "
     "emissions-process, and excludes purchased energy, which is out of scope.",
     "mass/energy", "t/GJ", "", "required", "emissions", "Emission coefficient."),
    ("emissions-process", "Process emissions factor", "emissions",
     "Emissions from the chemical reaction rather than fuel combustion, per unit of product.",
     "mass/mass", "t/t", "", "recommended", "emissions", ""),
    ("emissions-total", "Total direct emissions factor", "emissions",
     "Combustion plus process emissions together, per unit of product, where a source "
     "reports only the combined figure. Scope 1. NEVER record this alongside "
     "emissions-combustion and emissions-process for the same technology and source - it "
     "is the sum of them, and the three together double count.",
     "mass/mass", "t/t", "", "optional", "emissions", ""),
    ("emissions-captured", "Captured emissions factor", "emissions",
     "Emissions captured rather than released, per unit of energy input or product output. "
     "Species named in target. The counterpart of capture-rate as an absolute quantity.",
     "mass/mass", "t/t", "", "optional", "emissions-removal", ""),
    ("capture-rate", "Capture rate", "emissions",
     "Fraction of the CO2 stream captured.", "fraction", "%", "", "optional",
     "emissions-removal", ""),
    ("abatement-cost", "Abatement cost", "economic",
     "Cost of avoiding one tonne of CO2-eq by using this technology instead of the "
     "incumbent, as the source reports it. NOT a capital or operating cost and never "
     "interchangeable with one: it already nets the technology's costs against the "
     "incumbent's and divides by the emissions avoided, so the incumbent it was "
     "measured against belongs in the note. Added 2026-08-29 for IPCC AR6 Chapter 11 "
     "Table 11.3, which reports costs only in this form.",
     "currency/mass", "2019_USD/t-CO2-eq", "", "optional", "",
     "A marginal abatement cost curve point; not a substitute for capex and opex."),
    ("emissions-reduction-potential", "Emissions reduction potential", "emissions",
     "Reduction in GHG emissions this option can deliver relative to current practice, "
     "as a percentage. A ceiling on what the option can do, not a projection of what it "
     "will do. Where a source says these are multiplicative rather than additive across "
     "options -- as IPCC AR6 Table 11.3 does -- they must not be summed.",
     "fraction", "%", "", "optional", "",
     "Bounds the share of a service this option can decarbonise."),
    ("year-available", "First available year", "deployment",
     "Earliest year the technology may be built. From the TRL rule (design doc D5) where "
     "pre-commercial; a region-specific override goes here, the default on the technology row.",
     "year", "year", "", "recommended", "available", "Investment window opening."),
    ("year-unavailable", "Last available year", "deployment",
     "Year after which the technology may no longer be built.",
     "year", "year", "", "optional", "unavailable", "Investment window closing."),
]

COMMODITIES = [
    # commodity, label, class, unit, carrier, biogenic
    ("coal", "Coal", "energy", "GJ", "coal", "no"),
    # materials and utilities the ETSAP industry briefs flow in and out; they were
    # in tech-flow before they were in this list
    ("air", "Air", "material", "t", "", "no"),
    ("oil", "Fuel oil", "energy", "GJ", "oil", "no"),
    ("bauxite", "Bauxite", "material", "t", "", "no"),
    ("red-mud", "Red mud", "material", "t", "", "no"),
    ("salt-slag", "Salt slag", "material", "t", "", "no"),
    ("coking-coal", "Coking coal", "energy", "GJ", "coal", "no"),
    ("coke", "Coke", "energy", "GJ", "coal", "no"),
    ("coke-breeze", "Coke breeze", "energy", "GJ", "coal", "no"),
    ("coke-oven-gas", "Coke oven gas", "energy", "GJ", "coal", "no"),
    ("blast-furnace-gas", "Blast furnace gas", "energy", "GJ", "coal", "no"),
    ("basic-oxygen-furnace-gas", "Basic oxygen furnace gas", "energy", "GJ", "coal", "no"),
    ("benzole-and-tars", "Benzole and tars", "energy", "GJ", "coal", "no"),
    ("petroleum-coke", "Petroleum coke", "energy", "GJ", "petroleum-coke", "no"),
    ("natural-gas", "Natural gas", "energy", "GJ", "natural-gas", "no"),
    ("biomethane", "Biomethane", "energy", "GJ", "biomethane", "yes"),
    ("refinery-gas", "Refinery gas", "energy", "GJ", "oil", "no"),
    ("lpg", "Liquefied petroleum gas", "energy", "GJ", "oil", "no"),
    ("kerosene", "Kerosene", "energy", "GJ", "oil", "no"),
    ("light-fuel-oil", "Light fuel oil", "energy", "GJ", "oil", "no"),
    ("heavy-fuel-oil", "Heavy fuel oil", "energy", "GJ", "oil", "no"),
    ("diesel", "Diesel", "energy", "GJ", "oil", "no"),
    ("biomass-solid", "Solid biomass", "energy", "GJ", "biomass", "yes"),
    ("charcoal", "Charcoal", "energy", "GJ", "biomass", "yes"),
    ("black-liquor", "Black liquor", "energy", "GJ", "black-liquor", "yes"),
    ("biogas", "Biogas", "energy", "GJ", "biogas", "yes"),
    ("landfill-gas", "Landfill gas", "energy", "GJ", "landfill-gas", "yes"),
    ("bioliquid", "Liquid biofuel", "energy", "GJ", "biomass", "yes"),
    ("municipal-solid-waste", "Municipal solid waste", "energy", "GJ", "biomass", "no"),
    ("hydrogen", "Hydrogen", "energy", "GJ", "hydrogen", "no"),
    ("ammonia-fuel", "Ammonia as fuel", "energy", "GJ", "ammonia", "no"),
    ("electricity", "Electricity", "energy", "GJ", "electricity", "no"),
    ("steam", "Steam", "energy", "GJ", "waste-heat", "no"),
    ("hot-water", "Hot water", "energy", "GJ", "waste-heat", "no"),
    ("waste-heat", "Recovered waste heat", "energy", "GJ", "waste-heat", "no"),
    ("solar-thermal", "Solar thermal heat", "energy", "GJ", "solar", "no"),
    ("geothermal-heat", "Geothermal heat", "energy", "GJ", "geothermal", "no"),
    ("nuclear-heat", "Nuclear process heat", "energy", "GJ", "nuclear", "no"),
    ("iron-ore", "Iron ore", "material", "t", "", "no"),
    ("pellets", "Iron ore pellets", "material", "t", "", "no"),
    ("sinter", "Sinter", "material", "t", "", "no"),
    ("hot-metal", "Hot metal", "material", "t", "", "no"),
    ("direct-reduced-iron", "Direct reduced iron", "material", "t", "", "no"),
    ("scrap-steel", "Steel scrap", "material", "t", "", "no"),
    ("liquid-steel", "Liquid steel", "material", "t", "", "no"),
    ("crude-steel", "Crude steel", "material", "t", "", "no"),
    ("hot-rolled-steel", "Hot rolled steel", "material", "t", "", "no"),
    ("limestone", "Limestone", "material", "t", "", "no"),
    ("dolomite", "Dolomite", "material", "t", "", "no"),
    ("lime", "Lime", "material", "t", "", "no"),
    ("raw-meal", "Cement raw meal", "material", "t", "", "no"),
    ("clinker", "Clinker", "material", "t", "", "no"),
    ("cement", "Cement", "material", "t", "", "no"),
    ("supplementary-cementitious-material", "Supplementary cementitious material", "material", "t", "", "no"),
    ("alumina", "Alumina", "material", "t", "", "no"),
    ("aluminium", "Aluminium", "material", "t", "", "no"),
    ("oxygen", "Oxygen", "material", "t", "", "no"),
    ("electrodes", "Carbon electrodes", "material", "t", "", "no"),
    ("wood-pulp", "Wood pulp", "material", "t", "", "yes"),
    ("recovered-paper", "Recovered paper", "material", "t", "", "yes"),
    ("paper", "Paper and paperboard", "material", "t", "", "yes"),
    ("naphtha", "Naphtha", "material", "t", "", "no"),
    ("ethane", "Ethane", "material", "t", "", "no"),
    ("high-value-chemicals", "High value chemicals", "material", "t", "", "no"),
    ("ammonia", "Ammonia", "material", "t", "", "no"),
    ("methanol", "Methanol", "material", "t", "", "no"),
    ("slag", "Slag", "material", "t", "", "no"),
    ("gypsum", "Gypsum", "material", "t", "", "no"),
    ("water", "Water", "material", "t", "", "no"),
    ("waste-plastic", "Waste plastic", "material", "t", "", "no"),
    ("burning-oil", "Burning oil", "energy", "GJ", "oil", "no"),
    ("gas-oil", "Gas and diesel oil", "energy", "GJ", "oil", "no"),
    ("propane", "Propane", "energy", "GJ", "lpg", "no"),
    ("methane", "Methane as feedstock", "material", "t", "", "no"),
    ("ethanol", "Ethanol", "material", "t", "", "yes"),
    ("carrier-gas-coal", "Carrier gas coal", "energy", "GJ", "coal", "no"),
    ("fossil-waste", "Fossil waste fuel", "energy", "GJ", "municipal-waste", "no"),
    ("non-renewable-waste", "Non-renewable waste fuel", "energy", "GJ", "municipal-waste", "no"),
    ("renewable-fuel", "Renewable fuel, unspecified", "energy", "GJ", "biomass", "yes"),
    ("petrochemical-feedstock", "Petrochemical feedstock, other", "material", "t", "", "no"),
    ("ggbfs", "Ground granulated blast furnace slag", "material", "t", "", "no"),
    ("pulverised-fuel-ash", "Pulverised fuel ash", "material", "t", "", "no"),
    ("olivine", "Olivine or serpentine", "material", "t", "", "no"),
    ("quartz", "Quartz", "material", "t", "", "no"),
    ("sodium-hydroxide", "Sodium hydroxide", "material", "t", "", "no"),
    ("solvent-amine", "Amine solvent", "material", "t", "", "no"),
    ("co2", "Carbon dioxide, fossil", "emission", "t", "", "no"),
    ("nox", "Nitrogen oxides", "emission", "t", "", "no"),
    ("so2", "Sulphur dioxide", "emission", "t", "", "no"),
    ("co", "Carbon monoxide", "emission", "t", "", "no"),
    ("voc", "Volatile organic compounds", "emission", "t", "", "no"),
    ("pm", "Particulate matter", "emission", "t", "", "no"),
    ("co2-biogenic", "Carbon dioxide, biogenic", "emission", "t", "", "yes"),
    ("co2-captured", "Carbon dioxide captured", "emission", "t", "", "no"),
    ("ch4", "Methane", "emission", "t", "", "no"),
    ("n2o", "Nitrous oxide", "emission", "t", "", "no"),
    ("co2e", "Carbon dioxide equivalent", "emission", "t", "", "no"),
]

SEEDS = {
    "sector": [dict(zip(
        ["sector", "sector-label", "description", "uktm-code", "naics-2017", "isic-rev4", "note"],
        list(r) + [""])) for r in SECTORS],
    "end-use": [dict(zip(
        ["end-use", "end-use-label", "service-type", "service-unit-default",
         "temperature-tier", "description", "note"],
        list(r) + [""])) for r in END_USES],
    "parameter": [dict(zip(
        ["parameter", "parameter-label", "parameter-class", "definition", "unit-dimension",
         "unit-default", "basis-required", "requirement", "cims-parameter",
         "optimization-use", "note"],
        list(r) + [""])) for r in PARAMETERS],
    "commodity": [dict(zip(
        ["commodity", "commodity-label", "commodity-class", "unit-default",
         "energy-carrier", "biogenic", "note"],
        list(r) + [""])) for r in COMMODITIES],
}


# --- vocabularies read from elsewhere -----------------------------------

def design_doc_vocabularies() -> dict[str, list[str]]:
    """equipment / carrier / variant, parsed from section 6.2 of the design
    document.  That section is the single source of truth (design doc 6.2);
    this function must never fall back to a hard-coded copy."""
    if not DESIGN_DOC.exists():
        sys.exit(f"design document not found at {DESIGN_DOC}")
    text = DESIGN_DOC.read_text(encoding="utf-8")
    try:
        section = text[text.index("### 6.2 Controlled vocabularies"):text.index("### 6.3")]
    except ValueError:
        sys.exit("could not locate section 6.2 in the design document")
    token = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    out: dict[str, list[str]] = {}
    parts = re.split(r"\*\*(Equipment|Carrier|Variant)\*\*", section)
    for i in range(1, len(parts), 2):
        name, body = parts[i].lower(), parts[i + 1]
        out[name] = sorted({t for t in re.findall(r"`([^`]+)`", body) if token.match(t)})
    missing = {"equipment", "carrier", "variant"} - out.keys()
    if missing:
        sys.exit(f"vocabularies not found in section 6.2: {sorted(missing)}")
    return out


def manifest_source_ids() -> list[str]:
    """source-id values, read from the raw-data manifest.  That workbook stays
    the one register of sources; nothing here duplicates it."""
    ids: set[str] = set()
    for path in (MANIFEST, MANIFEST_FILES):
        if not path.exists():
            print(f"  warning: manifest not found at {path}; source-id list incomplete")
            continue
        for row in csv.DictReader(path.open(encoding="utf-8-sig")):
            if row.get("source_id"):
                ids.add(row["source_id"].strip())
    return sorted(ids)


# --- writers -------------------------------------------------------------

def resolve_lists() -> dict[str, list[str]]:
    lists = {k: list(v) for k, v in LISTS.items()}
    lists.update(design_doc_vocabularies())
    lists["source-id"] = manifest_source_ids()
    lists["sector"] = [r["sector"] for r in SEEDS["sector"]]
    lists["end-use"] = [r["end-use"] for r in SEEDS["end-use"]]
    lists["parameter"] = [r["parameter"] for r in SEEDS["parameter"]]
    lists["commodity"] = [r["commodity"] for r in SEEDS["commodity"]]
    return lists


def vocabulary_rows(lists: dict[str, list[str]]) -> list[dict]:
    origin = {"equipment": "design-doc-6.2", "carrier": "design-doc-6.2",
              "variant": "design-doc-6.2", "source-id": "source-manifest"}
    seeded = {"sector", "end-use", "parameter", "commodity"}
    rows = []
    for name in sorted(lists):
        if name == "source-id":
            continue          # too many, and they belong to the manifest
        note = "read from its own table" if name in seeded else ""
        for term in lists[name]:
            rows.append({"list-name": name, "term": term,
                         "origin": origin.get(name, "declared-here"), "note": note})
    return rows


def existing_rows(path: Path) -> list[dict]:
    """Rows already in a table, or [] if it is absent or header-only."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csvs(lists: dict[str, list[str]], force: bool = False) -> dict[str, list[dict]]:
    """Write each table, PRESERVING rows that are already there.

    A populated table keeps its rows and gains any new columns (blank); only
    its header is rewritten.  Dictionary tables are re-seeded, since the seed
    in this file is their source of truth.  --force restores every table to
    the empty template, discarding data.
    """
    seeds = dict(SEEDS)
    seeds["vocabulary"] = vocabulary_rows(lists)
    out: dict[str, list[dict]] = {}
    for name, spec in SCHEMA.items():
        cols = [c[0] for c in spec["columns"]]
        path = HERE / f"{name}.csv"
        seeded = name in seeds
        current = [] if force else existing_rows(path)
        if seeded or not current:
            rows, kept = seeds.get(name, []), ""
        else:
            rows, kept = current, "  (kept)"
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for row in rows:
                w.writerow({c: row.get(c, "") for c in cols})
        out[name] = rows
        print(f"  {path.name:24s} {len(cols):3d} columns, {len(rows):5d} rows{kept}")
    return out


# Which sheet+column a foreign key dropdown should point at, for keys whose
# list is a table the user fills in rather than a fixed vocabulary.
TABLE_LISTS = {"sector": ("sector", "A"), "end-use": ("end-use", "A"),
               "commodity": ("commodity", "A"), "parameter": ("parameter", "A"),
               "technology": ("technology", "A"), "service-node": ("service-node", "A")}
TABLE_ROWS = 3000        # dropdown range depth on those sheets


def write_workbook(lists: dict[str, list[str]], data: dict[str, list[dict]] | None = None) -> None:
    import openpyxl
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    seeds = dict(data) if data is not None else dict(SEEDS)
    if data is None:
        seeds["vocabulary"] = vocabulary_rows(lists)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    head_fill = PatternFill("solid", fgColor="1F3B57")
    key_fill = PatternFill("solid", fgColor="0E5A4E")
    head_font = Font(color="FFFFFF", bold=True, size=10)
    body_font = Font(size=10)

    # readme sheet -------------------------------------------------------
    ws = wb.create_sheet("readme")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 110
    ws.append(["Industrial technology database template"])
    ws["A1"].font = Font(bold=True, size=14)
    intro = [
        "",
        "Grouping:  sector -> end-use (-> process-step) -> service-node -> technology.",
        "Facts hang off a technology in three long-format tables: tech-parameter, tech-flow, tech-constraint.",
        "Every fact row carries source-id + source-file + source-locator, so any number can be walked back to its page.",
        "Detail level: technology roster at the Bataille UKTM level; parameters between Bataille and UKERC.",
        "Names follow the repo rule: '-' joins words within a component, '_' separates components.",
        "Regenerate this workbook and the CSVs with:  python data/harmonized/build-template.py",
        "",
    ]
    for line in intro:
        ws.append([line])
    ws.append(["table", "kind", "purpose"])
    for c in ws[ws.max_row]:
        c.fill, c.font = head_fill, head_font
    for name, spec in SCHEMA.items():
        ws.append([name, spec["kind"], spec["purpose"]])
        ws.cell(ws.max_row, 3).alignment = Alignment(wrap_text=True, vertical="top")
    ws.append([])
    ws.append(["table", "column", "definition"])
    for c in ws[ws.max_row]:
        c.fill, c.font = head_fill, head_font
    for name, spec in SCHEMA.items():
        for col, listname, note in spec["columns"]:
            hint = f"[list: {listname}] " if listname else ""
            ws.append([name, col, hint + note])
            ws.cell(ws.max_row, 3).alignment = Alignment(wrap_text=True, vertical="top")
    ws.sheet_view.showGridLines = False

    # data sheets --------------------------------------------------------
    for name, spec in SCHEMA.items():
        ws = wb.create_sheet(name)
        cols = spec["columns"]
        for j, (col, listname, note) in enumerate(cols, start=1):
            cell = ws.cell(1, j, col)
            cell.fill = key_fill if j == 1 else head_fill
            cell.font = head_font
            cell.alignment = Alignment(vertical="center", wrap_text=False)
            body = note or ""
            if listname:
                body = f"Allowed values: list '{listname}'.\n{body}"
            if body:
                cell.comment = Comment(body, "template")
            width = 40 if col in ("description", "definition", "note", "purpose",
                                 "service-description", "change", "reason") else \
                    max(12, min(28, len(col) + 4))
            ws.column_dimensions[get_column_letter(j)].width = width
        for i, row in enumerate(seeds.get(name, []), start=2):
            for j, (col, _, _) in enumerate(cols, start=1):
                c = ws.cell(i, j, row.get(col, ""))
                c.font = body_font
                c.alignment = Alignment(vertical="top", wrap_text=col in
                                        ("description", "definition"))
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}1"
        ws.sheet_view.showGridLines = False

    # hidden list sheet + validation -------------------------------------
    lst = wb.create_sheet("lists")
    fixed = [n for n in sorted(lists) if n not in TABLE_LISTS]
    where: dict[str, str] = {}
    for j, name in enumerate(fixed, start=1):
        L = get_column_letter(j)
        lst.cell(1, j, name).font = Font(bold=True)
        for i, term in enumerate(lists[name], start=2):
            lst.cell(i, j, term)
        depth = max(2, len(lists[name]) + 1)
        where[name] = f"lists!${L}$2:${L}${depth}"
    for name, (sheet, col) in TABLE_LISTS.items():
        where[name] = f"'{sheet}'!${col}$2:${col}${TABLE_ROWS}"
    lst.sheet_state = "hidden"

    for name, spec in SCHEMA.items():
        if name in ("vocabulary", "readme"):
            continue
        ws = wb[name]
        first = 2          # seeded rows get the dropdown too
        for j, (col, listname, _) in enumerate(spec["columns"], start=1):
            if not listname or listname not in where:
                continue
            L = get_column_letter(j)
            dv = DataValidation(type="list", formula1=f"={where[listname]}",
                                allow_blank=True, showDropDown=False)
            dv.error = f"Value must come from the '{listname}' list."
            dv.errorTitle = "Not in the controlled list"
            dv.prompt = f"Choose from '{listname}'."
            ws.add_data_validation(dv)
            dv.add(f"{L}{first}:{L}{TABLE_ROWS}")

    apply_view(wb)
    try:
        wb.save(WORKBOOK)
    except PermissionError:
        # build-wide.py and build-source-list.py already degrade this way. This
        # one did not, so an open Excel window aborted the run AFTER the CSVs
        # were rewritten -- the tables were current and the workbook was not,
        # with a traceback that looked like the whole build had failed.
        print(f"  {WORKBOOK.name} is open in Excel; CSVs written, workbook not "
              f"rebuilt. Close it and re-run to refresh the sheets.")
        return
    print(f"  {WORKBOOK.name:24s} {len(wb.sheetnames)} sheets")


def main() -> int:
    lists = resolve_lists()
    print(f"vocabularies: {len(lists)} lists "
          f"({len(lists['equipment'])} equipment, {len(lists['carrier'])} carrier, "
          f"{len(lists['variant'])} variant from the design document; "
          f"{len(lists['source-id'])} source-id from the manifest)")
    force = "--force" in sys.argv
    if force:
        print("--force: every table will be reset to the empty template")
    print("tables:")
    data = write_csvs(lists, force=force)
    write_workbook(lists, data)
    populated = sum(len(v) for k, v in data.items() if k not in SEEDS and k != "vocabulary")
    if populated:
        print(f"done. {populated} data rows preserved and carried into the workbook.")
    else:
        print("done. No technology data written -- every fact table is empty.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
