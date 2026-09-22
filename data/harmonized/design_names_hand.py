"""Hand map from a design-table label to its equipment term.

Only labels the automatic match in design_names.py cannot place.  A term
marked in NEW_EQUIPMENT is not in section 6.2 of the design document: adding
it is a modelling decision (section 6.2), so it is proposed here and reported,
never written into the vocabulary by this script.
"""

NEW_EQUIPMENT = {
    "mobile-equipment", "haul-truck", "hoist", "pickling-line",
    "annealing-furnace", "coating-line", "binder", "adsorber",
    "gas-treatment-unit", "separator", "drilling-rig", "fracturing-fleet",
    "well", "turboexpander", "liquefaction-train", "heat-exchanger",
    "paste-plant",
}

EQUIPMENT_BY_LABEL = {
    # cross-sector
    "Combined-cycle CHP": "combined-cycle",
    "Fuel-cell CHP": "fuel-cell",
    "Diesel generator set": "reciprocating-engine",
    "Waste-heat power (ORC or steam Rankine)": "steam-turbine",
    "Methane pyrolysis": "reactor",
    "Variable-speed drive": "motor",
    "Free or evaporative cooling": "cooling-tower",
    "Diesel non-road equipment": "mobile-equipment",
    "Propane or natural gas forklift": "mobile-equipment",
    "Battery-electric equipment": "mobile-equipment",
    "Hydrogen fuel-cell equipment": "mobile-equipment",
    "Diesel-electric hybrid equipment": "mobile-equipment",
    "Chemical solvent on process gas": "capture-unit",
    "Physical solvent": "capture-unit",
    "Advanced low-energy solvent": "capture-unit",
    "Calcium looping": "capture-unit",
    "Liquid-solvent DAC": "capture-unit",
    "Solid-sorbent DAC": "capture-unit",
    "Packaged air conditioner or rooftop unit": "chiller",
    "Chilled-water system": "chiller",
    # iron and steel
    "Fluidized-bed direct reduction": "shaft-furnace",
    "High-efficiency EAF": "electric-arc-furnace",
    "Acid pickling line": "pickling-line",
    "Batch (bell) annealing": "annealing-furnace",
    "Hydrogen bell annealing": "annealing-furnace",
    "Continuous annealing line": "annealing-furnace",
    "Hot-dip galvanizing line": "coating-line",
    "Electrolytic coating line": "coating-line",
    # cement and minerals
    "Blended cement with supplementary cementitious materials": "binder",
    "Calcined clay cement (LC3)": "binder",
    "Alkali-activated binder": "binder",
    "Carbonated binder": "binder",
    "Electric melter": "melting-furnace",
    # chemicals
    "Bio-ethanol dehydration to ethylene": "reactor",
    "Methanol to olefins": "reactor",
    "Electrolytic-hydrogen Haber-Bosch": "reactor",
    "CO2-to-methanol": "reactor",
    "Oxygen-depolarized cathode cell": "electrolysis-cell",
    "Sodium chlorate cell": "electrolysis-cell",
    "Catalytic N2O abatement": "reactor",
    "Plastics pyrolysis recycling": "reactor",
    "Chemical depolymerization": "reactor",
    # biofuels
    "Molecular-sieve dehydration with heat integration": "adsorber",
    "Methanol recovery with heat integration": "distillation-column",
    "Alcohol-to-jet": "reactor",
    "Pyrolysis oil upgrading": "reactor",
    "Hydrothermal liquefaction": "reactor",
    "Methanol-to-jet": "reactor",
    # refining
    "Advanced heat integration": "heat-recovery-unit",
    "Catalytic reforming": "reactor",
    "Alkylation and isomerization": "reactor",
    "Sulphur recovery and acid gas removal": "gas-treatment-unit",
    "Advanced acid gas removal": "gas-treatment-unit",
    # pulp and paper
    "Semi-chemical and sulphite pulping": "digester",
    "Low-energy refining": "pulper",
    "Chemi-thermomechanical pulping": "pulper",
    "Recycled-fibre repulping and deinking": "pulper",
    "Lignin extraction": "separator",
    "Advanced mechanical dewatering": "press",
    # mining
    "Diesel haul truck fleet": "haul-truck",
    "Battery-electric haulage": "haul-truck",
    "Trolley-assist haulage": "haul-truck",
    "Hydrogen fuel-cell haulage": "haul-truck",
    "Underground battery-electric equipment": "mobile-equipment",
    "Shaft hoisting": "hoist",
    "Sensor-based ore sorting": "separator",
    "Gravity and magnetic separation": "separator",
    "Thickening and filtration": "separator",
    "Direct lithium extraction": "adsorber",
    # oil and gas
    "Diesel drilling rig": "drilling-rig",
    "Grid-powered or electric rig": "drilling-rig",
    "Battery hybrid rig power": "drilling-rig",
    "Electric fracturing fleet": "fracturing-fleet",
    "Electric artificial lift": "pump",
    "Instrument air or electric actuation": "compressor",
    "Vapour recovery unit": "compressor",
    "Plunger lift and smart liquids unloading": "pump",
    "Solvent-assisted steam recovery": "well",
    "Solvent-only extraction": "well",
    "Direct contact steam generation": "boiler",
    "Electric steam generation": "boiler",
    "Truck-and-shovel mining": "haul-truck",
    "Hydrotransport and warm-water extraction": "separator",
    "Paraffinic froth treatment": "separator",
    "Non-aqueous extraction": "separator",
    "Electric or autonomous haul fleet": "haul-truck",
    "Partial upgrading": "reactor",
    "Amine sweetening": "gas-treatment-unit",
    "Glycol dehydration": "gas-treatment-unit",
    "Molecular-sieve dehydration": "adsorber",
    "Turboexpander NGL recovery": "turboexpander",
    "Claus sulphur recovery": "gas-treatment-unit",
    "Small-scale or modular liquefaction": "liquefaction-train",
    "Boil-off gas recovery": "compressor",
    "Drag-reducing agents": "process-improvement",
    # food and beverage
    "Steam-heated kettles, retorts and plate heat exchangers": "heat-exchanger",
    "Aseptic and UHT processing": "heat-exchanger",
    # non-ferrous metals
    "Bayer digestion on fossil steam": "digester",
    "Electrified Bayer heat": "digester",
    "Biomass-fired Bayer heat": "digester",
    "Hydrogen in the Bayer process": "digester",
    "Prebaked anode cell": "electrolysis-cell",
    "Soderberg cell": "electrolysis-cell",
    "Inert anode cell": "electrolysis-cell",
    "Multipolar or chloride cell": "electrolysis-cell",
    "Soderberg paste plant": "paste-plant",
    "Electrified or hydrogen-fired anode baking": "furnace",
    "Bio-pitch and bio-coke anodes": "process-improvement",
    "Peirce-Smith converting": "converter",
    "Continuous converting": "converter",
    "Hydrogen-fired ancillary heat": "direct-heater",
    "Pre-reduction of feed": "process-improvement",
    "Biocarbon reductant": "process-improvement",
    "Off-gas energy recovery": "heat-recovery-unit",
    # other industry
    "All-electric injection moulding and extrusion": "press",
    # automatic match lands on the wrong device for these
    "Pressure or vacuum swing adsorption": "adsorber",
    "Membrane separation": "separator",
    "Cryogenic separation": "air-separation-unit",
    "Membrane chlor-alkali cell": "electrolysis-cell",
    "Cryogenic post-combustion capture": "capture-unit",
    "Solar PV with battery storage": "solar-collector",
    "Electric thermal energy storage": "heat-recovery-unit",
    "Induction motor, standard efficiency": "motor",
    "Coupled pickling and tandem cold mill": "rolling-mill",
    "High-pressure acid leaching": "leaching-vessel",
    "Dehydration and compression": "compressor",
    "Low-pressure Haber-Bosch": "reactor",
    "Steam reforming with Haber-Bosch synthesis": "steam-reformer",
    "Electric-drive compression": "compressor",
    "Coke dry quenching": "heat-recovery-unit",
}


# Labels whose generated name reads badly, lands on the wrong device, or
# collides.  The name is written out in full here.
HAND_NAME = {
    "Solar thermal collectors": "solar-collector",
    "Solar PV with battery storage": "photovoltaic-array_battery-storage",
    "Wind turbines at site": "wind-turbine",
    "Electric thermal energy storage": "heat-recovery-unit_thermal-storage",
    "Absorption chiller": "chiller_absorption",
    "Fired process heater": "direct-heater_fired-process",
    "Direct-fired air or water heater": "direct-heater_air-water",
    "Electric process heater": "direct-heater_electric-process",
    "Electric air heating": "direct-heater_electric-air",
    "Fired line heater and treater": "direct-heater_line-heater",
    "Electric or heat-pump treating": "heat-pump_oil-treating",
    "Turboexpander at pressure let-down": "turboexpander_pressure-let-down",
    "Shaft-furnace direct reduction": "shaft-furnace_direct-reduction",
    "Fluidized-bed direct reduction": "shaft-furnace_fluidised-bed-direct-reduction",
    "Pellet induration (straight-grate, grate-kiln)": "pellet-plant_induration",
    "Gas turbine with heat-recovery steam generator":
        "combustion-turbine_heat-recovery-steam-generator",
    "Cogeneration supplying steam and power": "combined-cycle_cogeneration",
    "Oxygen delignification with ECF bleaching": "reactor_oxygen-delignification",
    "Thickened or dry-stack tailings": "separator_thickened-dry-stack-tailings",
    "Gas-fired hood, infrared or air dryer": "dryer_gas-fired-hood",
    "Nuclear steam supply": "reactor_nuclear-steam",
    "High-temperature gas-cooled reactor": "reactor_htgr",
    "Rotary lime kiln with preheater": "kiln_rotary-lime-with-preheater",
    "Fluid catalytic cracking": "reactor_fluid-catalytic-cracking",
    "Ebullated-bed hydrocracking": "reactor_ebullated-bed-hydrocracking",
    "Diesel non-road equipment": "mobile-equipment_diesel-non-road",
    "Propane or natural gas forklift": "mobile-equipment_forklift",
    "Molecular-sieve dehydration with heat integration":
        "adsorber_molecular-sieve-ethanol",
    "Grain dry-mill fermentation and distillation": "fermenter_grain-dry-mill",
    "Truck-and-shovel mining": "haul-truck_truck-and-shovel",
    "Electric artificial lift": "pump_artificial-lift",
    "Advanced low-energy solvent": "capture-unit_advanced-solvent",
    "Water electrolysis, low temperature": "electrolysis-cell_water-low-temperature",
    "Atmospheric leaching with solvent extraction and electrowinning":
        "electrolysis-cell_sx-ew",
    "Cryogenic separation": "air-separation-unit_cryogenic-separation",
    "Cryogenic air separation unit": "air-separation-unit",
    "High-pressure processing": "press_high-pressure-food",
}

# Equipment terms only the hand names above introduce.
NEW_EQUIPMENT |= {"photovoltaic-array", "wind-turbine"}

# Labels that name the same technology in different sectors.  Under D10 a
# technology is ONE roster row serving many nodes, so these collapse onto the
# first spelling and the other spellings become applications of it.
MERGE_LABEL = {
    "Electric or heat-pump drying": "Electric or heat-pump dryer",
    "Heat-pump drying": "Heat-pump dryer",
}


# The sector and cross-sector CCS rows added 2026-09-14.  The suffix IS the
# pointer: `_ccs-diffuse` says the capture plant is the one on cross-sector
# co2-capture-diffuse and `_ccs-concentrated` the one on
# co2-capture-concentrated, so no capture cost or energy is repeated on the
# host row (the user, 2026-09-14).
HAND_NAME.update({
    "Boiler with post-combustion capture": "boiler_ccs-diffuse",
    "Fired heater or furnace with post-combustion capture":
        "direct-heater_ccs-diffuse",
    "CHP with post-combustion capture": "combined-cycle_ccs-diffuse",
    "Steam methane reformer with capture on the shift gas":
        "steam-reformer_ccs-concentrated",
    "Blast furnace with post-combustion capture": "blast-furnace_ccs-diffuse",
    "Gas-based direct reduction with capture on the CO2 removal unit":
        "shaft-furnace_ccs-concentrated",
    "Cement kiln with post-combustion capture": "kiln_ccs-diffuse",
    "Lime kiln with post-combustion capture": "kiln_lime_ccs-diffuse",
    "Ammonia plant with capture on the process CO2":
        "steam-reformer_ammonia_ccs-concentrated",
    "Steam cracker with capture on the furnace flue gas":
        "steam-cracker_ccs-diffuse",
    "FCC regenerator with post-combustion capture":
        "reactor_fluid-catalytic-cracking_ccs-diffuse",
    "Recovery boiler with post-combustion capture": "boiler_recovery_ccs-diffuse",
    "Acid gas removal with CO2 compression and injection":
        "gas-treatment-unit_ccs-concentrated",
    "Fermentation CO2 capture and compression": "fermenter_ccs-concentrated",
})

HAND_NAME["Gasification with capture on the shift gas"] = "gasifier_ccs-concentrated"


# The efficiency-bucket rows added 2026-09-14.  The design row is named for the
# roster variant it corresponds to, so a roster bucket lands on its own bucket
# rather than on the conventional device; the individual measures live in the
# design table's examples column.
HAND_NAME.update({
    "Blast furnace efficiency measures, moderate": "blast-furnace_efficiency-moderate",
    "Blast furnace efficiency measures, strong": "blast-furnace_efficiency-strong",
    "Basic oxygen furnace efficiency measures, moderate":
        "basic-oxygen-furnace_efficiency-moderate",
    "Basic oxygen furnace efficiency measures, strong":
        "basic-oxygen-furnace_efficiency-strong",
    "Coke oven efficiency measures, moderate": "coke-oven_efficiency-moderate",
    "Coke oven efficiency measures, strong": "coke-oven_efficiency-strong",
    "Sinter plant efficiency measures, strong": "sinter-plant_efficiency-strong",
    "Fired heater efficiency measures, moderate": "direct-heater_efficiency-moderate",
    "Fired heater efficiency measures, strong": "direct-heater_efficiency-strong",
    "Reformer efficiency measures, moderate": "steam-reformer_efficiency-moderate",
    "Generating set efficiency measures, moderate": "combined-cycle_efficiency-moderate",
    "Turbine or engine drive efficiency measures, moderate":
        "combustion-turbine_efficiency-moderate",
    "Clean-in-place efficiency measures, moderate": "cleaning-system_efficiency-moderate",
    "Cement kiln efficiency measures, moderate": "kiln_efficiency-moderate",
    "Cement kiln efficiency measures, strong": "kiln_efficiency-strong",
    "Reheating furnace efficiency measures, moderate": "furnace_efficiency-moderate",
    "Reheating furnace efficiency measures, strong": "furnace_efficiency-strong",
    "Hot rolling mill efficiency measures, moderate": "rolling-mill_efficiency-moderate",
    "Smelting efficiency measures, moderate": "smelting-vessel_efficiency-moderate",
    "Smelting efficiency measures, strong": "smelting-vessel_efficiency-strong",
})

HAND_NAME["Sinter plant efficiency measures, moderate"] = "sinter-plant_efficiency-moderate"


# The venting, flaring and fugitives end use (2026-09-15).
NEW_EQUIPMENT |= {"flare"}
HAND_NAME.update({
    "Flare with continuous pilot": "flare",
    "Enclosed combustor": "flare_enclosed-combustor",
    "High-efficiency flare": "flare_high-efficiency",
    "Flare gas recovery": "compressor_flare-gas-recovery",
    "Leak detection and repair": "management-system_leak-detection",
    "Continuous methane monitoring": "management-system_methane-monitoring",
    "Blowdown gas recompression": "compressor_blowdown-recovery",
})

HAND_NAME.update({
    "Low-emission valves and connectors": "process-improvement_low-emission-components",
    "Dry gas seals on centrifugal compressors": "compressor_dry-gas-seal",
})

# The water end uses (2026-09-15).
HAND_NAME.update({
    "Activated sludge aeration": "fan_activated-sludge",
    "Fine-bubble diffused aeration": "fan_fine-bubble",
    "Anaerobic treatment with biogas recovery": "anaerobic-digester_effluent",
    "Clarification and sludge dewatering": "separator_clarifier",
    "Mine dewatering pumping": "pump_mine-dewatering",
    "Tailings thickening and water reclaim": "separator_tailings-reclaim",
    "Paste and dry-stack tailings": "separator_paste-dry-stack",
    "Mine water treatment plant": "separator_mine-water-treatment",
    "Reverse osmosis and evaporative concentration": "separator_reverse-osmosis",
    "Disposal well injection": "well_disposal-injection",
    "De-oiling and warm lime softening": "separator_warm-lime-softening",
    "Evaporators and crystallizers": "evaporator_produced-water",
    "Produced water recycling for makeup": "separator_produced-water-recycling",
})
