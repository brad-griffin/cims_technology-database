"""Sector-note content for the packages added 2026-11-04: oil, gas, biofuels, hydrogen, mining, aluminum, refining.

Same shape as SECTORS and EXAMPLES in docx_sector_notes.py, which merges these in.
"""

EXAMPLES_MORE = {
    # conventional oil and natural gas field work
    "fracturing-fleet_diesel": "Conventional diesel frac spreads",
    "fracturing-fleet_dual-fuel": "Dual-fuel (diesel and natural gas) frac pump engines",
    "fracturing-fleet_electric": "Electric frac fleets on gas-turbine generators",
    "reciprocating-engine_dual-fuel": "Bi-fuel rig and pump engines on field gas",
    "direct-heater_line-heater": "Indirect-fired line heaters; heater-treaters",
    "pump_artificial-lift": "Beam pumps; progressive-cavity pumps; electric submersible pumps",
    "separator_warm-lime-softening": "SAGD produced-water treatment plants",
    "well_disposal-injection": "Produced-water disposal wells",
    "evaporator_crystallizer-produced-water": "Evaporators and crystallizers for zero liquid discharge",
    "separator_produced-water-recycling": "Flowback and produced-water reuse for fracturing",
    "pipeline_crude-oil": "Crude and bitumen-blend trunk pipelines",
    "pump_electric-station": "Motor-driven mainline pump stations",
    "pump_electric-station_efficiency-moderate": "Drag-reducing agent injection",
    "drilling-rig_diesel": "Diesel-electric drilling rigs",
    "drilling-rig_electric": "Grid-powered drilling rigs",
    "separator_reduced-emission-completion": "Green completions",
    "gas-treatment-unit_amine-sweetening": "Amine sweetening units at sour gas plants",
    "gas-treatment-unit_glycol-dehydration": "Triethylene glycol (TEG) dehydrators",
    "turboexpander_ngl-recovery": "Deep-cut turboexpander plants",
    "gas-treatment-unit_amine-sweetening_ccs-concentrated": "Acid gas injection in Alberta",
    "adsorber_molecular-sieve": "Molecular sieve dehydrators ahead of cryogenic plants",
    "gas-treatment-unit_sulphur-recovery": "Claus units with tail-gas treatment",
    "liquefaction-train_base-load": "LNG Canada (Kitimat)",
    "liquefaction-train_base-load_efficiency-moderate": "Boil-off gas recompression",
    "liquefaction-train_electric": "Woodfibre LNG; Cedar LNG",
    "liquefaction-train_floating": "Floating LNG vessels (e.g. Prelude)",
    "liquefaction-train_small-scale": "FortisBC Tilbury",
    "pneumatic-device_gas-driven": "High-bleed pneumatic controllers and chemical-injection pumps",
    "pneumatic-device_low-bleed": "Low-bleed pneumatic controllers",
    "pneumatic-device_non-emitting": "Instrument air; electric actuators; solar chemical-injection pumps",
    "compressor_vapour-recovery": "Vapour recovery units on tanks",
    "process-improvement_nru-optimization": "Nitrogen rejection unit monitoring and tray upgrades",
    "pump_plunger-lift": "Plunger lift systems",
    "compressor_blowdown-recovery": "Portable recompression; hot taps; composite wrap repairs",
    "flare_enclosed-combustor": "Enclosed vapour combustors",
    "process-improvement_automatic-shutoff": "Excess flow valves; automatic shut-off valves",
    "flare": "Elevated solution-gas and process flares",
    "compressor_flare-gas-recovery": "Flare gas recovery units",
    "flare_high-efficiency": "Air-assisted flare tips",
    "management-system_leak-detection": "Optical gas imaging surveys; continuous methane monitoring",
    "compressor_low-emission-seal": "Dry gas seals; low-emission rod packing",
    "pipeline_plastic-liner": "Insert liners in cast-iron and steel mains",
    "process-improvement_low-emission-components": "Bellows-sealed valves; low-emission packing; welded connections",
    # oil sands
    "well_sagd": "Steam-assisted gravity drainage (e.g. Christina Lake, Foster Creek)",
    "well_cyclic-steam": "Cyclic steam stimulation at Cold Lake",
    "well_electromagnetic-heating": "ESEIEH pilot",
    "well_in-situ-oxy-combustion": "Downhole oxy-fuel steam generation pilots",
    "well_solvent-assisted": "Solvent-assisted SAGD pilots and projects",
    "well_solvent-only": "N-Solv",
    "separator_warm-water-extraction": "Hot-water extraction at mineable oil sands plants",
    "separator_naphthenic-froth-treatment": "Naphthenic froth treatment (Syncrude, Suncor)",
    "separator_paraffinic-froth-treatment": "Paraffinic froth treatment (Kearl, Fort Hills, Albian Sands)",
    "haul-truck_diesel": "Ultra-class diesel haul trucks",
    "haul-truck_battery-electric": "Battery-electric underground loaders and trucks",
    "haul-truck_dual-fuel": "LNG dual-fuel haul truck conversions",
    "haul-truck_hydrogen-fuel-cell": "Anglo American nuGen (Mogalakwena)",
    "haul-truck_trolley-assist": "Trolley-assist haul roads (e.g. Boliden Aitik)",
    "reactor_delayed-coking": "Delayed cokers at upgraders and refineries",
    "reactor_fluid-coking": "Syncrude fluid cokers; Flexicoking",
    "reactor_ebullated-bed-hydrocracking": "LC-Fining (Shell Scotford); H-Oil",
    "reactor_hydroprocessing": "Hydrocrackers and hydrotreaters",
    "steam-reformer_methane": "Refinery and upgrader hydrogen plants",
    "steam-reformer_methane_ccs-concentrated": "Quest (Shell Scotford, Alberta)",
    "electrolyzer_low-temperature": "Refinery electrolyzers (e.g. REFHYNE, Shell Rheinland)",
    "separator_thickening-filtration": "Thickeners and filter presses",
    "separator_dry-stack-tailings": "Filtered dry-stack tailings",
    # biofuels
    "fermenter_grain-dry-mill": "Corn and wheat ethanol plants",
    "fermenter_grain-dry-mill_efficiency-moderate": "Molecular-sieve dehydration with heat integration",
    "fermenter_grain-dry-mill_ccs-concentrated": "ADM Decatur (Illinois)",
    "fermenter_lignocellulosic-enzymatic": "Raízen second-generation ethanol (Brazil)",
    "fermenter_syngas": "LanzaTech",
    "transesterification-unit_alkali-catalyzed": "FAME biodiesel plants",
    "transesterification-unit_acid-catalyzed": "Acid pretreatment of high free-fatty-acid waste oils",
    "transesterification-unit_heterogeneous-catalyst": "Axens Esterfip-H",
    "reactor_hydrotreating-lipids": "Neste NEXBTL; Tidewater Renewables (Prince George)",
    "reactor_alcohol-to-jet": "LanzaJet Freedom Pines",
    "reactor_hydrothermal-liquefaction": "Steeper Energy (Hydrofaction)",
    "process-improvement_landfill-gas-recovery": "Landfill gas to renewable natural gas plants",
    "anaerobic-digester_biomethane-upgrading": "Renewable natural gas plants on digesters",
    "gasifier_biomass-methanation": "GoBiGas (Gothenburg)",
    "pellet-plant_wood": "Pinnacle Renewable Energy (British Columbia)",
    # hydrogen
    "autothermal-reformer_hydrogen_ccs-concentrated": "Air Products net-zero hydrogen complex (Edmonton)",
    "electrolyzer_low-temperature-central": "Air Liquide Bécancour (Quebec)",
    "electrolyzer_solid-oxide": "Topsoe and Bloom Energy solid-oxide electrolyzers",
    "gasifier_biomass-waste": "Enerkem (Varennes)",
    "reactor_methane-pyrolysis": "Monolith; Hazer",
    "pipeline_hydrogen": "Industrial hydrogen pipeline networks (e.g. U.S. Gulf Coast)",
    "liquefaction-train_hydrogen": "Hydrogen liquefiers serving merchant markets",
    "process-improvement_hydrogen-blending": "ATCO Fort Saskatchewan hydrogen blending",
    "storage-cavern_hydrogen": "Salt-cavern storage (e.g. Clemens Dome, Texas)",
    # mining
    "mine_open-pit-coal": "Elk Valley metallurgical coal mines",
    "hoist": "Shaft hoists at deep underground mines",
    "conveyor_in-pit-crushing": "In-pit crushing and conveying; overland conveyors",
    "fan_mine-ventilation": "Main ventilation fans; ventilation on demand",
    "grinding-mill_sag-ball": "SAG and ball mill circuits",
    "grinding-mill_hpgr": "High-pressure grinding rolls (e.g. Huckleberry)",
    "grinding-mill_stirred": "IsaMill; Vertimill",
    "separator_ore-sorting": "Sensor-based ore sorting",
    "flotation-cell_froth": "Froth flotation circuits",
    "separator_gravity-magnetic": "Spirals and magnetic separators for iron ore",
    "adsorber_direct-lithium": "Direct lithium extraction pilots",
    "leaching-vessel_heap-atmospheric": "Heap leaching with solvent extraction and electrowinning",
    "leaching-vessel_high-pressure-acid": "High-pressure acid leaching of laterites (e.g. Moa)",
    "leaching-vessel_in-situ": "In-situ recovery of uranium",
    "flotation-cell_potash": "Conventional underground potash mills in Saskatchewan",
    "evaporator_crystallizer": "Solution potash mines (e.g. Belle Plaine)",
    "dryer_rotary-direct-fired": "Rotary concentrate and mineral dryers",
    "dryer_direct-fired_efficiency-moderate": "Dryer improvement options (UK TIMES)",
    "pellet-plant_induration_efficiency-moderate": "Cooling-zone heat returned to drying and preheating",
    "gas-treatment-unit_vam-oxidiser": "Regenerative thermal oxidisers on ventilation air",
    "process-improvement_coal-mine-methane-drainage": "Seam gas drainage with engines or flares",
    # aluminum
    "digester_bayer": "Bayer alumina refineries (e.g. Vaudreuil, Quebec)",
    "digester_bayer_electric-heating": "Mechanical vapour recompression in Bayer refineries",
    "calciner_gas-suspension": "Gas-suspension and circulating fluidized-bed calciners",
    "calciner_hydrogen-fired": "Hydrogen calcination pilot (Yarwun, Australia)",
    "furnace_anode-baking": "Open and closed ring baking furnaces",
    "paste-plant_soderberg": "Söderberg paste plants",
    "electrolysis-cell_prebaked-anode": "Prebake potlines (e.g. Alouette, Kitimat)",
    "electrolysis-cell_soderberg": "Söderberg potlines (legacy)",
    "electrolysis-cell_inert-anode": "ELYSIS (Quebec)",
    "melting-furnace_reverberatory-rotary": "Reverberatory and rotary melting furnaces",
    "melting-furnace_regenerative-oxy-fuel": "Regenerative and oxy-fuel burners; stack melters",
    "melting-furnace_reverberatory-rotary_efficiency-strong": "Better lining, preheat hearth, and metal circulation",
    "melting-furnace_twin-chamber": "Twin-chamber furnaces for coated scrap",
    # petroleum refining
    "gasifier_coal-fischer-tropsch": "Sasol Secunda",
    "reactor_gas-to-liquids": "Shell Pearl GTL (Qatar)",
    "distillation-column_atmospheric-vacuum": "Crude and vacuum distillation units",
    "distillation-column_atmospheric-vacuum_efficiency-strong": "Pinch-designed preheat trains; fouling control",
    "reactor_alkylation": "Sulphuric acid and HF alkylation units",
    "reactor_catalytic-reforming": "Continuous catalytic reforming (CCR) units",
    "reactor_fluid-catalytic-cracking": "Fluid catalytic crackers",
    "reactor_isomerization": "Light naphtha isomerization (e.g. Penex)",
    "steam-reformer_methane_efficiency-moderate": "Pre-reforming; convection-section heat recovery; hydrogen recovery",
}

SECTORS_MORE = {
    "conventional-oil": {
        "title": "Conventional oil production", "adj": "conventional oil",
        "covers": "the archetypes that drill, complete, and produce conventional oil (drilling and fracturing, "
                  "field engines, artificial lift, oil treating, produced-water handling, and crude pipelines and "
                  "pumping) and provide more general services to oil production (steam, capture, and machine "
                  "drive)",
        "calls": [
            ("How production is represented", [
                "The database has no archetype for a whole producing oil well, light, medium, or heavy, onshore "
                "or offshore. Production is represented by the equipment around the well: drilling, fracturing, "
                "artificial lift, line heaters and treaters, field engines, and water handling. Is that enough to "
                "describe the energy use and emissions of Canadian oil production?",
                "Drilling rigs, fracturing fleets, line heaters, and artificial lift serve oil and gas wells "
                "alike, so their values pool oil and gas sources.",
                "Methane venting, flaring, and leak controls at oil sites are not covered here; the database "
                "holds them with natural gas production.",
            ]),
            ("Units", [
                "Drilling is per metre drilled, fracturing per GJ of hydraulic work, and produced water per "
                "cubic metre handled. Crude pipelines and their pump stations are per cubic metre moved over a "
                "set distance.",
            ]),
            ("Fracturing fleets", [
                "Diesel, dual-fuel, and electric fleets are kept apart. The electric fleet runs on on-site "
                "gas-turbine generators, so it burns field gas rather than buying grid power. Check that the "
                "fuel displacement (about 70–75% for dual fuel) matches Canadian practice.",
            ]),
            ("Sources", [
                "One source, Aune et al. 2020, supplies most of the examples behind these archetypes. Tell us "
                "about other sources, especially Canadian ones.",
            ]),
        ],
        "gaps": [
            "No sourced examples: warm lime softening, evaporation and crystallization of produced water, "
            "produced-water recycling, the crude pipeline, and drag-reducing agent injection; every value is "
            "filled.",
            "One example: `heat-pump_oil-treating`, `reciprocating-engine_dual-fuel`, `well_disposal-injection`, "
            "and `pump_electric-station`.",
        ],
    },
    "oil-sands": {
        "title": "Oil sands", "adj": "oil sands",
        "covers": "the archetypes that produce bitumen (in-situ recovery, mining and extraction, froth treatment, "
                  "and upgrading) and provide more general services to oil sands operations (upgrader hydrogen, "
                  "mine haulage, tailings, produced water, steam, and capture)",
        "calls": [
            ("An option that may have stalled", [
                "Development of these options may have stalled. We have kept them for now; tell us whether they are still being pursued, and whether the database should keep them as options.",
                "`well_electromagnetic-heating`: radio-frequency heating with solvent, as tested by the ESEIEH "
                "consortium at the Dover site from about 2015 to 2017. We found no later plan to take it further.",
            ]),
            ("In-situ recovery", [
                "The SAGD and cyclic steam archetypes cover the whole recovery process, including the once-through "
                "steam generators that supply them. The boiler and CHP rows under heat supply are separate steam "
                "suppliers. Check that the two framings do not double count steam.",
                "Solvent-assisted SAGD, solvent-only recovery, electromagnetic heating, and downhole oxy-fuel "
                "steam generation are kept as separate prospective options, each with few examples. Are their "
                "steam-to-oil ratios and costs plausible?",
            ]),
            ("Mining and extraction", [
                "Haul trucks are per tonne of ore, with waste rock counted through each mine's waste-to-ore "
                "ratio. Extraction and froth treatment are per cubic metre of bitumen.",
                "Naphthenic and paraffinic froth treatment are kept apart, since paraffinic treatment rejects "
                "asphaltenes and gives a cleaner product. Both rest on few or no sourced examples.",
            ]),
            ("Upgrading", [
                "Upgrading uses the same unit archetypes as refining (delayed coking, hydroprocessing), so their "
                "values pool upgrader and refinery sources. Fixed-bed hydrotreating is pooled into "
                "`reactor_hydroprocessing`. Do upgrader units differ enough from refinery units to need their "
                "own values?",
                "Partial upgrading is a prospective field-scale option that meets pipeline specification without "
                "full upgrading.",
                "Upgrader hydrogen comes from on-site reformers, coke gasification, or electrolysis. Steam "
                "reforming with capture on the shifted syngas is the Quest design.",
            ]),
        ],
        "gaps": [
            "No sourced examples: naphthenic froth treatment, non-aqueous extraction, warm lime softening, "
            "evaporation and crystallization of produced water, and produced-water recycling.",
            "One example: warm-water extraction, paraffinic froth treatment, ebullated-bed hydrocracking, "
            "dry-stack tailings, and disposal injection.",
        ],
    },
    "natural-gas": {
        "title": "Natural gas production", "adj": "natural gas",
        "covers": "the archetypes that drill, complete, produce, and process natural gas (drilling and "
                  "completions, gas processing and sulphur recovery, LNG liquefaction, compression, and venting, "
                  "flaring, and leak controls) and provide more general services to gas production (direct heat, "
                  "mobile equipment, machine drive, and capture)",
        "calls": [
            ("Methane abatement", [
                "Venting, flaring, leak, and well-test controls are measured per tonne of methane they handle "
                "or avoid; pneumatic devices are per thousand cubic metres of gas handled. Each of these steps "
                "also has a zero-cost, zero-energy no-abatement option, set entirely by judgement.",
                "Most methane-control costs come from U.S. sources (EPA Natural Gas STAR and technical support "
                "documents, and the IEA methane tracker, which uses U.S. base costs). Do they hold for Canadian "
                "sites and regulations?",
            ]),
            ("Merged", [
                "Continuous methane monitoring is pooled into the leak detection and repair archetype, with "
                "survey frequency left to its range.",
                "Hot taps and composite wrap repairs are pooled into `compressor_blowdown-recovery`, since both "
                "avoid venting a line before maintenance.",
                "Claus sulphur recovery is one archetype with refining.",
                "Gas-turbine and electric-motor refrigeration drives are folded into the LNG trains; the "
                "all-electric train is kept apart.",
            ]),
            ("Processing", [
                "Amine sweetening with capture sends the separated CO2 to injection instead of venting it, as "
                "acid gas injection does in Alberta.",
            ]),
            ("Scope", [
                "Transmission pipelines and distribution systems are not part of this review.",
            ]),
        ],
        "gaps": [
            "No sourced examples: boil-off gas recompression on LNG trains.",
            "One or two examples, with mostly guessed costs: the drilling rigs (diesel, battery hybrid, and "
            "electric) and advanced acid-gas removal.",
        ],
        "extra": [
            ("h2", "Transmission and distribution: an optional add-on"),
            ("p", "Gas transmission pipelines and pressure let-down in distribution have their own archetypes "
                  "(pipelines, turboexpanders, and let-down valves). If you also know them and are willing to "
                  "review them, tell us and we will send them in the same format."),
        ],
    },
    "biofuels": {
        "title": "Biofuels",
        "covers": "the archetypes that make biofuels (ethanol, biodiesel, renewable diesel and sustainable "
                  "aviation fuel, renewable natural gas, and wood pellets) and provide more general services to "
                  "biofuel plants (steam and capture)",
        "calls": [
            ("Charcoal", [
                "`kiln_charcoal-retort` is an industrial retort making charcoal per tonne, firing its own pyrolysis "
                "gas. It supplies biocarbon to blast furnaces. Its capital cost (about 250 dollars per tonne-year) "
                "and energy use (about 40 GJ of wood energy per tonne of charcoal, beyond what ends up in the "
                "charcoal) are judgements. Are they reasonable for a Canadian plant?",
            ]),
            ("Whole plants", [
                "Each archetype is a whole plant, measured per GJ of fuel produced. Feedstock whose energy ends "
                "up in the fuel is recorded as feedstock use, not energy use.",
                "Molecular-sieve dehydration and distillers' grain dryers are part of the grain dry-mill plant, "
                "not separate archetypes. Methanol recovery is part of the transesterification plants.",
            ]),
            ("Merged", [
                "Methanol-to-jet is pooled into `reactor_alcohol-to-jet`; ethanol is dehydrated directly while "
                "methanol goes through olefins first.",
                "Biological conversion of hydrogen and CO2 is pooled into `reactor_co2-to-ethanol`.",
                "Syngas fermentation of steel-mill off-gas is held with steelmaking, so `fermenter_syngas` "
                "covers gasified biomass and waste.",
            ]),
            ("Readiness", [
                "Many of the advanced routes (Fischer-Tropsch, CO2-to-fuels, hydrothermal liquefaction, "
                "supercritical transesterification) rest on one or a few examples. Are their readiness levels "
                "and costs plausible?",
            ]),
        ],
        "gaps": [
            "One example: grain dry-mill efficiency measures, heterogeneous-catalyst and supercritical "
            "transesterification, Fischer-Tropsch with capture, and hydrothermal liquefaction.",
            "No archetype for co-processing of bio-feeds in petroleum refineries.",
        ],
    },
    "hydrogen": {
        "title": "Hydrogen",
        "covers": "the archetypes that produce hydrogen at central plants (steam and autothermal reforming, "
                  "gasification, electrolysis, and methane pyrolysis, with and without capture) and provide more "
                  "general services to hydrogen supply (pipelines, liquefaction, storage, blending, and capture)",
        "calls": [
            ("Shared with on-site hydrogen", [
                "Steam reformers and gasifiers also supply hydrogen inside refineries and upgraders, so their "
                "values pool central and on-site plants. Electrolysis is split by size: central plants of about "
                "100 MW to 1 GW here, and smaller on-site units elsewhere.",
                "Hydrogen is measured per GJ on a higher heating value basis.",
            ]),
            ("Capture", [
                "Steam reforming with capture is kept as two variants: capture on the shifted syngas, where the "
                "CO2 is concentrated (as at Quest), and capture on the reformer flue gas, which is dilute. "
                "Autothermal reforming is designed for high capture rates.",
            ]),
            ("Delivery", [
                "Pipelines, liquefaction, cavern storage, and blending into the gas system are each a way to "
                "deliver hydrogen. Blending rests on one example.",
            ]),
        ],
        "gaps": [
            "One example: hydrogen blending into the gas system.",
            "No archetype for compressed-gas trucking or for ammonia as a hydrogen carrier.",
        ],
    },
    "mining": {
        "title": "Mining",
        "covers": "the archetypes that mine and process metal ore, potash, uranium, and coal (extraction and "
                  "haulage, crushing and grinding, separation, leaching, drying, pelletizing, tailings, "
                  "ventilation, and coal-mine methane) and provide more general services to mines (on-site power, "
                  "steam, machine drive, heating and cooling, and lighting)",
        "calls": [
            ("Haulage and extraction", [
                "Haul trucks are per tonne of ore, with waste rock counted through each mine's waste-to-ore "
                "ratio. Diesel, trolley-assist, dual-fuel LNG, battery-electric, and fuel-cell trucks are kept "
                "apart.",
                "Coal mines are whole-mine archetypes (open-pit and underground), while metal mines are built "
                "from unit archetypes. Is that difference sensible?",
            ]),
            ("Merged", [
                "Overland conveyors are pooled into in-pit crushing and conveying.",
                "Tank bioleaching is pooled into heap leaching.",
                "High-pressure grinding rolls for ore stay apart from those for cement, since a tonne of ore and "
                "a tonne of cement are different products.",
            ]),
            ("Remote mines", [
                "Twelve on-site power archetypes serve mines: gas turbines and combined cycles, steam "
                "turbines, wind, solar with storage, geothermal, and small nuclear. There is no diesel or gas "
                "reciprocating genset among them. Check that they cover northern and off-grid sites.",
            ]),
            ("Products", [
                "Potash is counted per tonne of K2O; uranium leaching per tonne of uranium; pellets per tonne of "
                "pellets.",
            ]),
        ],
        "gaps": [
            "No sourced examples: stirred mills, in-pit crushing and conveying, gravity and magnetic "
            "separation, in-situ leaching, and pellet-plant heat recovery.",
            "One example: hoists, the underground coal mine, dry-stack tailings, and potash flotation.",
        ],
    },
    "aluminum": {
        "title": "Aluminum", "adj": "aluminum",
        "covers": "the archetypes that make aluminum (alumina digestion and calcination, anode production, "
                  "smelting, and melting and casting of primary and recycled metal) and provide more general "
                  "services to aluminum plants (steam, capture, machine drive, heating and cooling, and lighting)",
        "calls": [
            ("Merged and kept apart", [
                "Electric, hydrogen, and biomass heat for Bayer digestion are carriers on `digester_bayer`, not "
                "separate archetypes. Mechanical vapour recompression in the Bayer refinery is kept apart, since "
                "it changes the process.",
                "The hydrogen-fired calciner is kept apart from the gas-suspension calciner because its emissions "
                "differ in kind.",
                "Regenerative burners for foundries are pooled into `melting-furnace_regenerative-oxy-fuel`.",
            ]),
            ("Smelting", [
                "Prebake and Söderberg cells are both conventional; Söderberg is the older Canadian stock. Inert "
                "anodes (ELYSIS) are prospective.",
                "Process emissions include perfluorocarbons, kept by species rather than as CO2-equivalent.",
                "The value of smelter power modulation (varying amperage to follow the grid) is not represented.",
            ]),
            ("Whole refinery", [
                "A whole alumina refinery is kept as reference values only, since the database splits it into "
                "digestion and calcination.",
            ]),
        ],
        "gaps": [
            "No sourced examples: the Söderberg paste plant, electric and biogenic-carbon anode baking, and "
            "capture on the alumina calciner.",
            "One example: chloride and multipolar cells, the twin-chamber furnace, and isothermal melting.",
        ],
    },
    "petroleum-refining": {
        "title": "Petroleum refining", "adj": "refining",
        "covers": "the archetypes that refine crude oil (crude distillation, conversion, upgrading and treating "
                  "units, sulphur recovery, and synthetic fuels) and provide more general services to refineries "
                  "(fired heaters, steam, on-site hydrogen, capture, machine drive, heating and cooling, and "
                  "lighting)",
        "calls": [
            ("Units, not whole refineries", [
                "Whole refineries (hydroskimming, conversion, and deep conversion) are kept as reference values "
                "only; the database represents refining by its process units. Most units are per cubic metre of "
                "refined products, and sulphur recovery per tonne of sulphur.",
                "Fired heaters are heat-supply rows of their own, split from fired heaters in other industries. "
                "They carry much of a refinery's fuel use, so please review them with the process units.",
            ]),
            ("Merged", [
                "Fixed-bed hydrotreating is pooled into `reactor_hydroprocessing`, which covers hydrocracking and "
                "hydrotreating together. Should they stand apart?",
                "Claus sulphur recovery is one archetype with gas processing.",
            ]),
            ("Low-carbon options", [
                "Electric-heated and hydrogen-fired versions of hydroprocessing and catalytic reforming rest on "
                "one source (the MIDDEN database).",
                "Capture on the fluid catalytic cracker is kept as a post-combustion variant and an oxy-fuel "
                "variant; the oxy-fuel variant includes an air separation unit.",
                "Delayed coking and hydroprocessing are shared with oil sands upgraders, so their values pool "
                "both.",
            ]),
        ],
        "gaps": [
            "One or two examples: electric-heated catalytic reforming, hydrogen-fired hydroprocessing, the "
            "efficient steam reformer, and gas-to-liquids.",
            "No archetype for lubricant or asphalt production, or for co-processing of bio-feeds.",
        ],
    },
}
