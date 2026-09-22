"""Where each existing service node and roster technology lands in the design
vocabulary of design/sector-end-use-table.csv.

The rules below are transcribed from the `harmonized-now` column of that table,
which is the user's own statement of where each design end use sits in the
current layer.  That column is prose -- it names process steps, end uses and
roster technologies in the same cell -- so it is read once, here, into tables
that can be applied and audited, rather than parsed at run time.

Nothing in this module writes to the harmonized CSVs.  It is the crosswalk the
review file reports on, and the same tables an adoption pass would apply.
"""
from __future__ import annotations

# --- sectors -------------------------------------------------------------
# The design table adds biofuels and oil-and-gas.  Nothing in the current
# layer carries either: the rows that belong to them arrived through CIMS and
# were parked on chemicals and other-industry, so they are recognized by the
# CIMS sector they came from.
SECTOR_MAP = {s: s for s in (
    "cross-sector", "iron-and-steel", "non-ferrous-metals", "cement",
    "non-metallic-minerals", "chemicals", "petroleum-refining",
    "pulp-and-paper", "food-and-beverage", "mining", "other-industry")}

# A CIMS sector is not on its own enough to move a row: `Ethanol.Steam` is
# cross-sector heat in the design table, not a biofuels end use.  The move is
# decided per service, in CIMS_SERVICE_END_USE below.

# --- technology-level rules ---------------------------------------------
# These fire before the node rules, because the design table splits some
# cross-sector nodes by what the technology IS, not by where it sits: the
# `*_chp` entries on steam-and-hot-water, the prime movers run without heat
# recovery, and the three capture end uses.
TECH_END_USE = {
    "capture-unit": ("cross-sector", "co2-capture-concentrated"),
    "capture-unit_hydrogen": ("cross-sector", "co2-capture-concentrated"),
    "capture-unit_methanol": ("cross-sector", "co2-capture-concentrated"),
    "capture-unit_top-gas-recycling-ccs": ("cross-sector", "co2-capture-concentrated"),
    "capture-unit_ccs": ("cross-sector", "co2-capture-diffuse"),
    "capture-unit_natural-gas_ccs": ("cross-sector", "co2-capture-diffuse"),
    "capture-unit_coal_ccs": ("cross-sector", "co2-capture-diffuse"),
    "capture-unit_by-product-gas_ccs": ("cross-sector", "co2-capture-diffuse"),
    "capture-unit_direct": ("cross-sector", "direct-air-capture"),
    "steam-turbine_steam_condensing": ("cross-sector", "on-site-power-generation"),
}
# prime movers on steam-and-hot-water with no chp variant: power-only
POWER_ONLY_EQUIPMENT = {"combined-cycle", "reciprocating-engine", "microturbine",
                        "fuel-cell", "combustion-turbine", "steam-turbine"}
# Only equipment that actually makes hydrogen or syngas. `reactor`,
# `electrolysis-cell` and `fuel-cell` are deliberately out: they have homes in
# the chemicals, steel and power end uses, and sweeping them in here filed an
# ammonia reformer and a steel electrowinning cell as merchant hydrogen.
HYDROGEN_SUPPLY_EQUIPMENT = {"electrolyzer", "steam-reformer", "autothermal-reformer",
                             "gasifier"}
# biogas and RNG are a biofuels product, not a site service (2026-09-14)
RNG_EQUIPMENT = {"anaerobic-digester", "fermenter"}

# Where on-site hydrogen production lands now that the cross-sector end use is
# retired: the host sector where there is one, the hydrogen sector otherwise.
HYDROGEN_BY_SECTOR = {"petroleum-refining": ("petroleum-refining", "refinery-hydrogen"),
                      "oil-and-gas": ("oil-and-gas", "upgrader-hydrogen")}
HYDROGEN_DEFAULT = ("hydrogen", "centralized-hydrogen-production")
RNG_END_USE = ("biofuels", "renewable-natural-gas")

# On `cross-sector` there is no sector to claim the device, so the wider set
# applies: an electrolysis cell or a reactor sitting there is making hydrogen.
# A fuel cell is consuming it, and belongs with on-site power generation.
CROSS_SECTOR_HYDROGEN = HYDROGEN_SUPPLY_EQUIPMENT | {"electrolysis-cell", "reactor"}

# Air separation followed the oxygen to the two sectors that size it.
OXYGEN_BY_SECTOR = {"iron-and-steel": ("iron-and-steel", "steel-oxygen-supply"),
                    "non-ferrous-metals": ("non-ferrous-metals", "smelter-oxygen-supply")}

# Process cooling is a food and beverage end use now; the user's decision was
# that this is the one sector where it is a real energy service.
REFRIGERATION_END_USE = ("food-and-beverage", "refrigeration")

# Machine drive splits into the six EIA MECS categories. The device decides
# which one; a driver that turns a compressor or a pump is written to both.
MACHINE_DRIVE = {
    "pump": ["pumps"],
    "fan": ["fans-and-blowers"],
    "ventilation-unit": ["fans-and-blowers"],
    "compressor": ["compressed-air"],
    "conveyor": ["materials-handling"],
    "hoist": ["materials-handling"],
    "crusher": ["materials-processing"],
    "grinding-mill": ["materials-processing"],
    "press": ["materials-processing"],
    "mixer": ["materials-processing"],
    "combustion-turbine": ["pumps", "compressed-air"],
    "reciprocating-engine": ["pumps", "compressed-air"],
    "steam-turbine": ["pumps", "compressed-air"],
    "motor": ["materials-processing"],
    "management-system": ["materials-processing"],
}
# The MECS residual is not carried as an end use (2026-09-14): anything the
# five named categories do not cover is motor-driven process equipment.
MACHINE_DRIVE_DEFAULT = ["materials-processing"]
FACILITY_SPLIT = {"space-heater": "space-heating", "heat-pump": "space-heating",
                  "chiller": "space-cooling", "cooling-tower": "space-cooling",
                  "ventilation-unit": "space-cooling", "fan": "space-cooling",
                  "lighting": "lighting"}

# --- node rules ----------------------------------------------------------
# (sector, process-step) -> design end use.  Steps are matched exactly, and a
# leading '*' matches any suffix, which is how the design table writes the
# CIMS structural-shape and drying families.
STEP_END_USE = {
    ("iron-and-steel", "coke-oven"): "cokemaking",
    ("iron-and-steel", "sinter-plant"): "agglomeration",
    ("iron-and-steel", "pelletization"): "agglomeration",
    ("iron-and-steel", "agglomeration"): "agglomeration",
    ("iron-and-steel", "blast-furnace"): "ironmaking",
    ("iron-and-steel", "direct-reduction"): "ironmaking",
    ("iron-and-steel", "smelting-reduction"): "ironmaking",
    ("iron-and-steel", "iron-manufacture"): "ironmaking",
    ("iron-and-steel", "integrated-steelworks"): "ironmaking",
    ("iron-and-steel", "basic-oxygen-furnace"): "steelmaking",
    ("iron-and-steel", "electric-arc-furnace"): "steelmaking",
    ("iron-and-steel", "ladle-preheat"): "steelmaking",
    ("iron-and-steel", "casting"): "casting",
    ("iron-and-steel", "continuous-casting"): "casting",
    ("iron-and-steel", "billet-casting"): "casting",
    ("iron-and-steel", "bloom-casting"): "casting",
    ("iron-and-steel", "reheating"): "reheating",
    ("iron-and-steel", "reheators"): "reheating",
    ("iron-and-steel", "hot-rolling"): "rolling",
    ("iron-and-steel", "roughing-mills"): "rolling",
    ("iron-and-steel", "finishing-mills"): "rolling",
    ("iron-and-steel", "cold-roll"): "rolling",
    ("iron-and-steel", "skin-pass"): "rolling",
    ("iron-and-steel", "electrocleancomp"): "rolling",
    ("iron-and-steel", "bar"): "rolling",
    ("iron-and-steel", "rod"): "rolling",
    ("iron-and-steel", "tubes"): "rolling",
    ("iron-and-steel", "*-structural-shapes"): "rolling",
    ("iron-and-steel", "anneal-temper"): "annealing-and-coating",
    ("iron-and-steel", "galvanize"): "annealing-and-coating",
    ("iron-and-steel", "tin-plate"): "annealing-and-coating",
    ("cement", "kiln"): "clinker-production",
    ("cement", "dry-kiln"): "clinker-production",
    ("cement", "wet-kiln"): "clinker-production",
    ("cement", "semi-dry-kiln"): "clinker-production",
    ("cement", "semi-wet-kiln"): "clinker-production",
    ("cement", "clinker-cooler"): "clinker-production",
    ("cement", "precalciner"): "clinker-production",
    ("cement", "finish-grinding"): "cement-grinding-and-blending",
    ("cement", "alternative-binder"): "cement-grinding-and-blending",
    ("chemicals", "benzene-separation-process"): "other-chemicals",
    ("petroleum-refining", "vacuum"): "crude-distillation",
    ("petroleum-refining", "direct-heat"): "crude-distillation",
    ("petroleum-refining", "desulphurization"): "conversion-and-treating",
    ("pulp-and-paper", "pulping-chemical"): "chemical-pulping",
    ("pulp-and-paper", "pulping-mechanical"): "mechanical-pulping",
    ("pulp-and-paper", "pulping-recycled"): "recycled-pulping",
    ("pulp-and-paper", "evaporator"): "chemical-recovery",
    ("pulp-and-paper", "recovery-furnace"): "chemical-recovery",
    ("pulp-and-paper", "energy-recovery"): "chemical-recovery",
    ("pulp-and-paper", "lime-kiln"): "lime-kiln",
    ("pulp-and-paper", "paper-machine"): "paper-forming",
    ("pulp-and-paper", "*-forming-pressing-finishing"): "paper-forming",
    ("pulp-and-paper", "*-drying"): "paper-drying",
    ("pulp-and-paper", "pulp-drying"): "paper-drying",
    ("mining", "extraction"): "extraction-and-haulage",
    ("mining", "primary-crushing"): "comminution",
    ("mining", "secondary-crushing"): "comminution",
    ("mining", "primary-milling"): "comminution",
    ("mining", "secondary-milling"): "comminution",
    ("mining", "crush-and-screen"): "comminution",
    ("mining", "cleaning"): "separation-and-processing",
    ("mining", "washing"): "separation-and-processing",
    ("mining", "drying"): "product-drying",
    ("mining", "agglomeration"): "pelletizing",
    # mine ventilation and mine air heating are a mining end use in the design
    # table, not the cross-sector ventilation service R2 merged them into
    ("mining", "ventilation"): "ventilation-and-air-heating",
    ("mining", "mine-ventilation"): "ventilation-and-air-heating",
    # mine space heating is generic space heating (2026-09-16), so it falls
    # through to the cross-sector facility rule
    ("food-and-beverage", "dairy"): "thermal-processing",
    ("food-and-beverage", "meat-heating-systems"): "thermal-processing",
    ("food-and-beverage", "bakery"): "baking-frying-and-roasting",
    ("food-and-beverage", "bakery-ovens"): "baking-frying-and-roasting",
    ("food-and-beverage", "bakery-indirect-ovens"): "baking-frying-and-roasting",
    ("food-and-beverage", "drying-systems"): "drying",
    ("non-ferrous-metals", "alumina-refining"): "alumina-refining",
    ("non-ferrous-metals", "electrolysis"): "aluminum-smelting",
    ("non-ferrous-metals", "anode-production"): "anode-production",
    ("non-ferrous-metals", "roast"): "pyrometallurgy",
    ("non-ferrous-metals", "smelt"): "pyrometallurgy",
    ("non-ferrous-metals", "continuous-smelting"): "pyrometallurgy",
    ("non-ferrous-metals", "refine"): "pyrometallurgy",
    ("non-ferrous-metals", "hydro-metallurgy"): "hydrometallurgy",
    ("non-ferrous-metals", "melt-cast"): "melting-casting-and-fabrication",
    ("non-ferrous-metals", "secondary-melting"): "melting-casting-and-fabrication",
    ("non-ferrous-metals", "convert"): "pyrometallurgy",
    ("non-ferrous-metals", "pre-bake-anode"): "anode-production",
    # steps still spelled the CIMS way in cims-map.csv, which R3 resolved in
    # the harmonized layer but which arrive here on `other-services`
    ("chemicals", "ammonia-synthesis"): "ammonia-and-methanol",
    ("chemicals", "methanol-synthesis"): "ammonia-and-methanol",
    ("chemicals", "combined-ammonia-methanol-synthesis"): "ammonia-and-methanol",
    ("chemicals", "btx-reforming"): "other-chemicals",
    ("iron-and-steel", "ladle-refining"): "steelmaking",
    ("iron-and-steel", "recycled"): "steelmaking",
    ("mining", "flotation"): "separation-and-processing",
    ("non-metallic-minerals", "dolomitic"): "lime-calcination",
    ("petroleum-refining", "coking"): "conversion-and-treating",
    ("petroleum-refining", "cracking"): "conversion-and-treating",
    ("petroleum-refining", "reforming"): "conversion-and-treating",
    ("pulp-and-paper", "bleaching-fully"): "chemical-pulping",
    ("pulp-and-paper", "bleaching-semi"): "chemical-pulping",
    ("pulp-and-paper", "cut-and-chip"): "wood-preparation",
    ("pulp-and-paper", "debark"): "wood-preparation",
    ("pulp-and-paper", "pulping-semi-chemical"): "chemical-pulping",
    ("pulp-and-paper", "*-stock-prep"): "paper-forming",
}

# CIMS grades `Petroleum Refining.Direct Heat` as high, medium and low; the
# design table reads those as the cross-sector heat bands.
REFINING_HEAT_GRADE = {"high": "heat-high-temp", "medium": "heat-medium-temp",
                       "low": "heat-low-temp"}

# A step that moves to a cross-sector end use whatever sector it sits in.
# `cryogenics` now resolves through OXYGEN_BY_SECTOR and the fuel-blend steps
# through RNG_END_USE / HYDROGEN_BY_SECTOR, so nothing is left that moves to a
# cross-sector end use on the strength of its process step alone.
STEP_TO_CROSS_SECTOR = {}

# (sector, end use) -> design end use, where the whole end use moves as one.
EU_END_USE = {
    ("cross-sector", "process-heat-low-temp"): "heat-low-temp",
    ("cross-sector", "process-heat-medium-temp"): "heat-medium-temp",
    ("cross-sector", "process-heat-high-temp"): "heat-high-temp",
    ("cross-sector", "drying-and-separation"): "heat-low-temp",
    ("non-metallic-minerals", "drying-and-separation"): "drying-and-low-temp-calcining",
    ("non-metallic-minerals", "process-heat-low-temp"): "drying-and-low-temp-calcining",
    ("chemicals", "electrochemical"): "electrochemical-products",
    ("chemicals", "drying-and-separation"): "other-chemicals",
    ("chemicals", "process-heat-low-temp"): "other-chemicals",
    ("chemicals", "process-heat-medium-temp"): "other-chemicals",
    ("chemicals", "process-heat-high-temp"): "other-chemicals",
    ("petroleum-refining", "material-conversion"): "conversion-and-treating",
    ("petroleum-refining", "process-heat-high-temp"): "crude-distillation",
    ("petroleum-refining", "process-heat-medium-temp"): "crude-distillation",
    ("pulp-and-paper", "drying-and-separation"): "paper-drying",
    ("pulp-and-paper", "forming-and-finishing"): "paper-forming",
    ("mining", "drying-and-separation"): "product-drying",
    ("mining", "material-preparation"): "comminution",
    ("food-and-beverage", "process-heat-low-temp"): "thermal-processing",
    ("food-and-beverage", "process-heat-medium-temp"): "thermal-processing",
    ("food-and-beverage", "process-heat-high-temp"): "baking-frying-and-roasting",
    ("food-and-beverage", "drying-and-separation"): "drying",
    ("non-ferrous-metals", "electrochemical"): "aluminum-smelting",
    ("non-ferrous-metals", "process-heat-high-temp"): "pyrometallurgy",
    ("other-industry", "process-heat-high-temp"): "metal-melting-and-heat-treatment",
    ("other-industry", "process-heat-low-temp"): "drying-curing-and-forming",
    ("other-industry", "process-heat-medium-temp"): "drying-curing-and-forming",
    ("other-industry", "drying-and-separation"): "drying-curing-and-forming",
    ("other-industry", "forming-and-finishing"): "drying-curing-and-forming",
    ("iron-and-steel", "process-heat-high-temp"): "reheating",
    ("mining", "process-heat-high-temp"): "pelletizing",
    ("pulp-and-paper", "process-heat-high-temp"): "lime-kiln",
    ("pulp-and-paper", "electrochemical"): "chemical-pulping",
    ("cement", "process-heat-high-temp"): "clinker-production",
    ("cement", "material-conversion"): "clinker-production",
    ("cement", "forming-and-finishing"): "cement-grinding-and-blending",
    ("cement", "material-preparation"): "cement-grinding-and-blending",
    ("pulp-and-paper", "material-conversion"): "chemical-recovery",
    ("mining", "forming-and-finishing"): "separation-and-processing",
    ("non-ferrous-metals", "material-conversion"): "pyrometallurgy",
    ("non-ferrous-metals", "material-preparation"): "pyrometallurgy",
    ("non-ferrous-metals", "forming-and-finishing"): "melting-casting-and-fabrication",
    ("non-ferrous-metals", "drying-and-separation"): "alumina-refining",
    ("iron-and-steel", "material-conversion"): "ironmaking",
    ("iron-and-steel", "material-preparation"): "agglomeration",
    ("iron-and-steel", "forming-and-finishing"): "rolling",
    ("iron-and-steel", "drying-and-separation"): "agglomeration",
    ("non-metallic-minerals", "material-conversion"): "lime-calcination",
    ("non-metallic-minerals", "material-preparation"): "lime-calcination",
    ("non-metallic-minerals", "forming-and-finishing"): "glass-forming-and-finishing",
    ("food-and-beverage", "material-conversion"): "thermal-processing",
    ("food-and-beverage", "forming-and-finishing"): "thermal-processing",
    ("pulp-and-paper", "material-preparation"): "chemical-pulping",
    ("chemicals", "material-preparation"): "other-chemicals",
    ("petroleum-refining", "material-preparation"): "conversion-and-treating",
    ("mining", "material-conversion"): "separation-and-processing",
    ("other-industry", "material-conversion"): "metal-melting-and-heat-treatment",
    ("other-industry", "material-preparation"): "metal-melting-and-heat-treatment",
}

# Equipment that decides the split where one current end use feeds two design
# ones.  non-metallic-minerals process-heat-high-temp is the lime kiln against
# the glass and ceramic furnaces; chemicals material-conversion is the cracker
# against the reformers and the electrochemical cells.
EQUIPMENT_SPLIT = {
    ("non-metallic-minerals", "process-heat-high-temp"): (
        {"kiln", "calciner", "precalciner", "clinker-cooler"}, "lime-calcination",
        "glass-melting"),
    ("chemicals", "material-conversion"): (
        {"steam-cracker"}, "steam-cracking", "ammonia-and-methanol"),
}
CHEMICALS_CONVERSION = {
    "steam-cracker": "steam-cracking",
    "steam-reformer": "ammonia-and-methanol",
    "autothermal-reformer": "ammonia-and-methanol",
    "reactor": "ammonia-and-methanol",
    "electrolysis-cell": "electrochemical-products",
    "electrolyzer": "electrochemical-products",
    "gasifier": "ammonia-and-methanol",
}

# A cross-sector heat technology with no temperature of its own serves both
# bands.  The design table bands on the temperature the PROCESS needs, and a
# boiler or a CHP unit raises steam for either, so the application is written
# to both rather than guessed onto one.
BOTH_HEAT_BANDS = ("heat-low-temp", "heat-medium-temp")


# --- CIMS services the design table places outside their CIMS sector -----
# R2 merged the generic end uses onto cross-sector and dropped the process
# step, so a CIMS service like `Natural Gas.LNG Compression` is no longer
# distinguishable in technology-application.csv -- it survives only as one
# entry in a joined `reported-steps` cell.  The design table's oil-and-gas end
# uses need that distinction back, so CIMS-derived placements are resolved
# from cims-map.csv, keyed on the CIMS sector and the process step the mapper
# recorded, not from the merged application row.
CIMS_BRANCH_END_USE = {
    # the step alone is ambiguous: `compression` is field compression under
    # Extraction, plant compression under Processing and pipeline compression
    # under Transmission, and the design table puts the three in different end
    # uses.  So these are keyed on the branch.
    "Natural Gas.Production.Supply.Extraction.Compression":
        ("oil-and-gas", "oil-and-gas-production"),
    "Natural Gas.Production.Supply.Extraction.Drilling":
        ("oil-and-gas", "drilling-and-well-services"),
    "Natural Gas.Production.Supply.Extraction.Off road transport":
        ("cross-sector", "mobile-equipment"),
    "Natural Gas.Production.Supply.Testing and Maintenance.Blowdowns":
        ("oil-and-gas", "venting"),
    "Natural Gas.Production.Supply.Venting": ("oil-and-gas", "venting"),
    "Natural Gas.Production.Supply.Fugitive": ("oil-and-gas", "fugitive-emissions"),
    "Natural Gas.Production.Supply.Testing and Maintenance.Well Tests":
        ("oil-and-gas", "drilling-and-well-services"),
    "Natural Gas.Production.Supply.Testing and Maintenance.Liquid Unloading":
        ("oil-and-gas", "venting"),
    "Natural Gas.Production.Supply.Flaring": ("oil-and-gas", "flaring"),
    "Natural Gas.Production.Supply.Controls": ("oil-and-gas", "venting"),
    # pneumatic vs electric pumps, requested by processing and transmission (2026-09-16)
    "Natural Gas.Production.Supply.Pumping": ("oil-and-gas", "venting"),
    "Natural Gas.Production.Supply.Direct Drive Large":
        ("oil-and-gas", "oil-and-gas-production"),
    "Natural Gas.Production.Supply.Direct Drive Small":
        ("oil-and-gas", "oil-and-gas-production"),
    "Natural Gas.Production.Supply.Formation CO2":
        ("cross-sector", "co2-capture-concentrated"),
    "Natural Gas.Production.Supply.Processing.Compression":
        ("oil-and-gas", "gas-processing"),
    "Natural Gas.Production.Supply.Processing": ("oil-and-gas", "gas-processing"),
    "Natural Gas.Production.Supply.LNG Compression":
        ("oil-and-gas", "lng-liquefaction"),
    "Natural Gas.Production.Transmission.Compression":
        ("oil-and-gas", "gas-pipelines"),
    "Natural Gas.Production.Transmission": ("oil-and-gas", "gas-pipelines"),
    "Natural Gas.Production.Distribution": ("oil-and-gas", "gas-pipelines"),
    "Natural Gas.OG Methane Blend": ("biofuels", "renewable-natural-gas"),
    "Petroleum Crude.Production.Bitumen.Upgrading":
        ("oil-and-gas", "bitumen-upgrading"),
    "Petroleum Crude.Production.Bitumen.In-Situ": ("oil-and-gas", "in-situ-bitumen"),
    "Petroleum Crude.Production.Bitumen.Mining":
        ("oil-and-gas", "oil-sands-mining-and-extraction"),
    "Petroleum Crude.Production.Exploration":
        ("oil-and-gas", "drilling-and-well-services"),
    "Petroleum Crude.Production.Light Medium":
        ("oil-and-gas", "oil-and-gas-production"),
    "Petroleum Crude.Hydrogen": ("oil-and-gas", "upgrader-hydrogen"),
    "Petroleum Refining.Hydrogen": ("petroleum-refining", "refinery-hydrogen"),
    # CIMS carries a Hydrogen sector of its own; it is the merchant plant
    "Hydrogen": ("hydrogen", "centralized-hydrogen-production"),
    # stationary drives shared by the crude end uses (2026-09-16); one row can
    # name one end use, so it goes to the largest requester
    "Petroleum Crude.Industrial Engines": ("oil-and-gas", "oil-and-gas-production"),
    "Ethanol.Production": ("biofuels", "ethanol-production"),
    "Ethanol.Methane Fuel": ("biofuels", "renewable-natural-gas"),
    "Biodiesel.Production": ("biofuels", "biodiesel-production"),
    "Biodiesel.Methane Fuel": ("biofuels", "renewable-natural-gas"),
    "Light Industrial.Manufacturing.Wood Products":
        ("other-industry", "wood-drying-and-pressing"),
    "Construction.Transport": ("cross-sector", "mobile-equipment"),
}


def branch_rule(branch: str):
    """Longest branch prefix wins, so Processing.Compression beats Processing."""
    for b in sorted(CIMS_BRANCH_END_USE, key=len, reverse=True):
        if branch == b or branch.startswith(b + "."):
            return CIMS_BRANCH_END_USE[b]
    return None
# `<sector>.Steam` is a separable steam system, so the design table puts it on
# the cross-sector heat bands whatever sector raises it (the integral-vs-
# supplied rule).  `Natural Gas.Production.Supply.Direct Heat` is listed there
# too, and the CIMS mapper files it as high-temperature process heat.
CIMS_STEP_TO_HEAT_BANDS = {"direct-heat", "steam", "still-gas-steam"}

# --- which hierarchy leaf a device belongs on -------------------------------
# Only for the end uses whose leaves split one route from another, where the
# words of a roster name do not say which (`blast-furnace` does not contain
# "hot metal").  Keyed by (design sector, end use), then equipment -> the
# leaf's trailing path.  Everything else is chosen by sector and by words.
LEAF_BY_EQUIPMENT = {
    ("iron-and-steel", "ironmaking"): {
        "blast-furnace": "hot-metal", "converter": "hot-metal",
        "smelting-vessel": "hot-metal", "shaft-furnace": "direct-reduced-iron",
        "rotary-kiln": "direct-reduced-iron"},
    ("iron-and-steel", "steelmaking"): {
        "basic-oxygen-furnace": "molten-steel", "electric-arc-furnace": "molten-steel",
        "melting-furnace": "molten-steel", "furnace": "ladle-preheating",
        "refining-furnace": "ladle-refining"},
    ("pulp-and-paper", "chemical-recovery"): {
        "evaporator": "evaporator", "boiler": "recovery-furnace",
        "gasifier": "recovery-furnace"},
    ("cement", "clinker-production"): {
        "kiln": "clinker", "calciner": "clinker", "precalciner": "clinker",
        "grinding-mill": "clinker", "direct-heater": "kiln-heat"},
    ("non-metallic-minerals", "lime-calcination"): {
        "kiln": "lime", "direct-heater": "kiln-heat"},
}

# --- roster technologies the rules cannot place -------------------------
# Folded onto the nearest design technology (the user, 2026-09-14).  The note
# says what the fold costs, where it costs something.
HAND_TECH = {
    # CIMS Natural Gas "Compression" (electric). Its design row moved from gas
    # processing to the reciprocating compressor-drive end use on 2026-09-22; left
    # to the rules it fell to the recovery boiler, the conventional row of its
    # pulp-and-paper application.
    "compressor_electricity": ("compressor_electric-drive-compression",
        "the CIMS compression service is driver-neutral; the electric alternative "
        "sits on compressor-drive-engine, where the processing row it matched moved"),
    "oven": ("direct-heater_tunnel-deck", ""),
    "oven_efficiency-moderate": ("heat-recovery-unit_oven-exhaust", ""),
    "pasteurizer": ("heat-exchanger_steam-heated", ""),
    "pasteurizer_efficiency-moderate":
        ("heat-recovery-unit_regenerative-pasteurizers", ""),
    "pasteurizer_efficiency-strong":
        ("heat-recovery-unit_regenerative-pasteurizers",
         "the moderate and strong buckets both land here; the design table has one "
         "efficient variant for pasteurizing"),
    "cleaning-system": ("heat-exchanger_steam-heated",
                        "its application is mining drying, not food clean-in-place"),
    "cleaning-system_efficiency-moderate": ("heat-exchanger_steam-heated",
        "the design table has no efficient variant for cleaning and clean-in-place"),
    "cleaning-system_efficiency-strong": ("heat-exchanger_steam-heated",
        "the design table has no efficient variant for cleaning and clean-in-place"),
    "paper-machine_kraft-paperboard": ("press_fourdrinier-gap",
        "the grade is dropped; the design table has one paper machine"),
    "paper-machine_newsprint": ("press_fourdrinier-gap",
        "the grade is dropped; the design table has one paper machine"),
    "microturbine": ("combustion-turbine_engine-simple", ""),
    "microturbine_natural-gas_chp":
        ("combustion-turbine_heat-recovery-steam-generator", ""),
    "clinker-cooler": ("kiln_efficiency-strong",
        "the cooler upgrade is one of the measures this bucket groups"),
    "refining-furnace": ("converter_peirce-smith", ""),
    "refining-furnace_efficiency-moderate": ("converter_continuous-converting", ""),
    "refining-furnace_electricity": ("converter_continuous-converting",
        "an electric refining furnace has no design row"),
    "space-heater_electricity": ("resistance-heater_electric-space", ""),
    "space-heater_natural-gas": ("direct-heater_fuel-space", ""),
    "space-heater_oil": ("direct-heater_fuel-space", ""),
    "space-heater_steam": ("direct-heater_fuel-space",
        "a steam unit heater has no design row"),
    "crusher": ("grinding-mill_sag-ball", ""),
    "photochemical-heater_electricity": ("ultraviolet-curer_infrared", ""),
    # ccs names the stream-tagged rows do not reach on their own
    "smelting-vessel_ccs": ("smelting-vessel_bath-reduction",
        "the oxygen-blown route concentrates the stream, so the capture plant is "
        "co2-capture-concentrated"),
    "caster_efficiency-strong": ("rolling-mill_thin-slab",
        "thin-slab casting with direct rolling is the strong option on casting; "
        "the design table names it rather than bucketing it"),
    "evaporator_efficiency-moderate": ("vapour-recompressor_mechanical-evaporation",
        "mechanical vapour recompression is the named efficient option on "
        "chemical recovery"),
    "combined-cycle_coal_ccs": ("combined-cycle_ccs-diffuse",
        "its application is power-only generation, where the design table carries "
        "no capture row; the chp row is the nearest"),
}
