"""Sector notes for the review packages: hand-written judgement calls plus facts from sector-facts.json.

The notes describe archetypes as the real processes they stand for. Keep model and hierarchy terms out of
them, and keep decision dates out too (Brad 2026-11-04).
"""
from docx_lib import make_doc, render
from docx_sector_notes_more import EXAMPLES_MORE, SECTORS_MORE

FAMILY_LABEL = {"heat-supply": "heat supply", "power-generation": "on-site power", "machine-drive": "machine drive",
                "space-conditioning": "space conditioning", "lighting": "lighting",
                "mobile-equipment": "mobile equipment", "co2-capture": "CO2 capture"}

# Real-life examples: named technologies, plants, products, and the measures an efficiency bucket holds.
# Blank where no named example is well established.
EXAMPLES = {
    # cement
    "kiln_dry-precalciner": "Standard modern clinker line: cyclone preheater, precalciner, short rotary kiln",
    "kiln_legacy": "Wet, semi-wet, Lepol grate, and long dry kilns",
    "kiln_dry-precalciner_efficiency-moderate": "Burner and combustion control; less false air; kiln shell insulation",
    "kiln_dry-precalciner_efficiency-strong": "Extra preheater stages; high-efficiency grate cooler; low-pressure-drop gas path",
    "kiln_dry-precalciner_ccs-diffuse": "Heidelberg Materials Brevik, Norway",
    "calciner_indirect": "LEILAC pilots (Lixhe, Belgium; Hannover, Germany)",
    "kiln_calcium-looping": "CLEANKER pilot (Vernasca, Italy)",
    "kiln_calcium-silicate-feed": "Brimstone",
    "kiln_electric-plasma": "CemZero (Cementa and Vattenfall)",
    "blast-furnace_biogenic-carbon": "Charcoal blast furnaces in Minas Gerais (Brazil); CanmetENERGY biocarbon injection trials",
    "kiln_charcoal-retort": "Lambiotte continuous retort",
    "steam-turbine_back-pressure_ccs-diffuse": "Stockholm Exergi biomass CHP with capture (Värtaverket, Sweden)",
    "kiln_oxy-fuel": "CI4C oxyfuel project (Colleferro, Italy)",
    "grinding-mill_ball": "Closed-circuit ball mills",
    "grinding-mill_vertical-roller": "Vertical roller mills; high-pressure grinding rolls",
    "binder_portland-cement": "General-use cement (CSA A3001 GU)",
    "binder_alkali-activated": "Geopolymer and alkali-activated slag binders (e.g. E-Crete)",
    "binder_blended-cement": "Portland-limestone cement (CSA GUL); slag and fly-ash cements",
    "binder_calcined-clay": "LC3 (limestone calcined clay cement)",
    "binder_carbonated": "Solidia",
    "binder_electrochemical": "Sublime Systems",
    "binder_hydrothermal-silicate": "Celitement",
    "binder_sulphoaluminate": "Calcium sulphoaluminate cements; belite-ye'elimite-ferrite (BYF) clinker",
    "grinding-mill_slag": "Ground granulated blast-furnace slag (GGBFS) plants",
    # iron and steel
    "reactor_steel-offgas-chemicals": "Carbon2Chem (Duisburg); Steelanol (Ghent, gas fermentation)",
    "air-separation-unit": "On-site air separation units at integrated steelworks",
    "annealing-furnace_batch-bell": "Bell (batch) annealing furnaces for cold-rolled coils",
    "annealing-furnace_continuous": "Continuous annealing lines",
    "annealing-furnace_hydrogen-bell": "HICON/H2 (Ebner)",
    "coating-line_electrolytic": "Electro-galvanizing and tinplate lines",
    "coating-line_hot-dip": "Continuous hot-dip galvanizing lines",
    "basic-oxygen-furnace": "Basic oxygen (LD) converters",
    "basic-oxygen-furnace_efficiency-strong": "Converter gas recovery; off-gas hood heat recovery; variable-speed fan drives",
    "electric-arc-furnace": "Algoma; ArcelorMittal Dofasco; Gerdau Whitby",
    "electric-arc-furnace_scrap-preheating": "Consteel; Quantum; EcoArc",
    "furnace_ladle-metallurgy": "Ladle furnaces at secondary-steelmaking stations",
    "shaft-furnace_electrolytic-hydrogen": "Stegra (Boden, Sweden)",
    "blast-furnace": "Stelco Lake Erie; ArcelorMittal Dofasco",
    "blast-furnace_efficiency-moderate": "Top-pressure recovery turbine; burden distribution control; more pulverized coal injection; dry gas cleaning",
    "blast-furnace_efficiency-strong": "Hot stove waste-heat recovery; slag heat recovery; top-gas heat recovery",
    "blast-furnace_top-gas-recycling": "ULCOS experimental blast furnace; COURSE50",
    "electrolysis-cell_molten-oxide": "Boston Metal (demonstration cell)",
    "melting-furnace_electric-smelting": "NeoSmelt (Kwinana, Australia)",
    "smelting-vessel_low-shaft": "Tecnored",
    "smelting-vessel_smelting-reduction": "Corex; Finex; HIsarna",
    "caster_continuous": "Slab, bloom, and billet continuous casters",
    "caster_strip": "Castrip",
    "rolling-mill_thin-slab": "CSP; Arvedi ESP",
    "coke-oven_by-product": "ArcelorMittal Dofasco coke plant (Hamilton)",
    "coke-oven_by-product_efficiency-moderate": "Less air leakage; battery insulation; heating and pressure control",
    "coke-oven_by-product_efficiency-strong": "Coke dry quenching; coke-oven gas sensible-heat recovery",
    "coke-oven_heat-recovery": "SunCoke heat-recovery ovens",
    "melting-furnace_cupola": "Cokeless and coke-fired cupolas in iron foundries",
    "melting-furnace_induction": "Coreless and channel induction furnaces",
    "electrolysis-cell_iron-electrowinning": "Electra; Siderwin",
    "furnace_rotary-hearth-direct-reduction": "Fastmet; Inmetco; ITmk3",
    "shaft-furnace_direct-reduction": "MIDREX; Energiron; ArcelorMittal Contrecoeur",
    "shaft-furnace_direct-reduction_ccs-concentrated": "Al Reyadah (Abu Dhabi)",
    "shaft-furnace_hydrogen-direct-reduction": "HYBRIT; Stegra; Circored",
    "furnace_reheating": "Walking-beam and pusher furnaces",
    "furnace_reheating_efficiency-moderate": "Oxygen and air-flow control; more insulation; scheduling and skid design",
    "furnace_reheating_efficiency-strong": "Recuperative and regenerative burners; furnace sealing and insulation",
    "pellet-plant_induration": "Straight-grate and grate-kiln pellet plants",
    "pellet-plant_plasma-electric": "LKAB plasma trials",
    "sinter-plant": "Travelling-grate sinter strands",
    "sinter-plant_efficiency-moderate": "Better charging; deeper bed; less air leakage; ignition-hood control",
    "sinter-plant_efficiency-strong": "Waste-gas recirculation (EPOSINT, EOS); sinter-cooler heat recovery",
    "pickling-line_acid": "Hydrochloric acid pickling lines with acid regeneration",
    "rolling-mill_cold": "Tandem and reversing cold mills",
    "rolling-mill_cold_efficiency-moderate": "Coupled pickling and tandem cold mill lines",
    "rolling-mill_hot": "Hot strip, plate, section, bar, and rod mills",
    "rolling-mill_hot_efficiency-moderate": "Coil box; endless rolling; gauge and flatness control; mill lubrication",
    # pulp and paper
    "anaerobic-digester_effluent": "UASB and internal-circulation (IC) reactors",
    "fan_activated-sludge": "Surface aerators; coarse-bubble diffusers",
    "fan_activated-sludge_efficiency-moderate": "Fine-bubble diffusers; dissolved-oxygen control; turbo blowers",
    "separator_clarifier": "Primary clarifiers with belt or screw presses",
    "separator_membrane-bioreactor": "Submerged-membrane bioreactors",
    "boiler_recovery": "Tomlinson kraft recovery boilers",
    "boiler_recovery-high-solids": "High dry-solids, high-pressure recovery boilers",
    "evaporator_multiple-effect": "Falling-film multiple-effect evaporator trains",
    "gasifier_black-liquor": "Chemrec DP-1 pilot (Piteå, Sweden)",
    "gasifier_black-liquor-fuels": "Chemrec DP-1 pilot (Piteå, Sweden); Domsjö BioDME design (cancelled 2012)",
    "pulp-mill_kraft": "Canadian market kraft mills",
    "paper-machine_with-dryer-section": "Whole newsprint, board, and tissue machines",
    "vapour-recompressor_evaporation": "Mechanical vapour recompression evaporators",
    "debarker_drum": "Drum debarkers with disc chippers",
    "digester_batch-kraft": "Displacement batch cooking (SuperBatch, RDH)",
    "digester_continuous-kraft": "Kamyr-type continuous digesters",
    "digester_sulphite": "Sulphite and dissolving-pulp mills",
    "reactor_ecf-bleaching": "Elemental-chlorine-free bleach plants",
    "reactor_oxygen-delignification": "Oxygen delignification stages ahead of bleaching",
    "dryer_market-pulp": "Airborne (flakt) pulp dryers; cylinder pulp dryers",
    "dryer_steam-heated": "Steam-cylinder dryer sections; Yankee dryers",
    "dryer_steam-heated_efficiency-moderate": "Less air infiltration; hood humidity control; condensate return; flash-steam use; heat recovery",
    "dryer_steam-heated_efficiency-strong": "Hot press ahead of the dryer section",
    "dryer_heat-pump": "Exhaust-air heat pumps on paper machine hoods (pilots)",
    "dryer_through-air": "Through-air-dried (TAD) premium tissue machines",
    "kiln_lime-rotary": "Lime-mud rotary kilns in kraft mills",
    "kiln_lime-rotary_efficiency-strong": "Better cooler, chain section, and lime-mud drying",
    "paper-machine": "Fourdrinier and gap-former paper machines",
    "paper-machine_efficiency-moderate": "Wire-section drainage and vacuum; felt and press optimization; moisture control",
    "paper-machine_efficiency-strong": "Steam boxes ahead of the press",
    "paper-machine_waterless": "Foam forming (VTT pilots); dry forming",
    "pulper_chemi-thermomechanical": "CTMP lines",
    "pulper_groundwood": "Stone groundwood and pressure groundwood mills",
    "pulper_refiner-low-energy": "RTS refining; low-energy refiner segments",
    "pulper_thermomechanical": "TMP lines with refiner heat recovery",
    "pulper_recycled-fibre": "Recycled-fibre and deinking lines",
    # chemicals
    "gasifier_coal-ammonia": "Coal-based ammonia plants in China",
    "reactor_haber-bosch-electrolytic": "Low-pressure Haber-Bosch loops on electrolytic hydrogen",
    "steam-reformer_ammonia": "Natural-gas ammonia plants (Haber-Bosch synthesis)",
    "steam-reformer_ammonia_ccs-concentrated": "Enid, Oklahoma",
    "steam-reformer_ammonia_efficiency-moderate": "Reformer revamps; heat recovery",
    "steam-reformer_ammonia_efficiency-strong": "Best-practice reforming, synthesis, and heat integration",
    "distillation-column": "Steam-reboiled and fired-heater distillation trains",
    "distillation-column_heat-integrated": "Divided-wall and heat-integrated columns",
    "distillation-column_heat-pumped": "Propylene-propane splitters with vapour recompression",
    "electrolysis-cell_chlor-alkali-diaphragm": "Diaphragm cells (legacy North American plants)",
    "electrolysis-cell_chlor-alkali-membrane": "Ion-exchange membrane cells",
    "electrolysis-cell_chlor-alkali-mercury": "Mercury-cathode cells (legacy)",
    "electrolysis-cell_oxygen-depolarized": "Oxygen-depolarized cathode cells (Covestro and thyssenkrupp)",
    "electrolysis-cell_sodium-chlorate": "Sodium chlorate plants supplying pulp-mill bleaching",
    "evaporator_caustic-soda": "Multiple-effect caustic soda evaporators",
    "vapour-recompressor_evaporation@chemicals": "Mechanical vapour recompression caustic evaporators",
    "reactor_ethanol-to-ethylene": "Braskem green ethylene (Triunfo, Brazil)",
    "reactor_methanol-to-olefins": "DMTO; UOP/Hydro MTO",
    "reactor_propane-dehydrogenation": "Oleflex; Catofin",
    "steam-cracker_catalytic-naphtha": "ACO process (KBR and SK)",
    "steam-cracker_electric": "BASF, SABIC, and Linde demonstration (Ludwigshafen)",
    "steam-cracker_fired-tubular": "Ethane and naphtha steam crackers",
    "steam-cracker_fired-tubular_efficiency-moderate": "Dividing-wall columns; hybrid membrane-distillation separation",
    "reactor_co2-to-methanol": "Carbon Recycling International (Iceland)",
    "gasifier_biomass-methanol": "Enerkem (Edmonton)",
    "steam-reformer_methanol": "Methanex Medicine Hat",
    "reactor_catalytic-n2o": "Secondary and tertiary N2O catalysts (e.g. EnviNOx)",
    "reactor_adipic-acid": "Nitric-acid oxidation adipic acid plants",
    "reactor_ammonium-nitrate": "Ammonium nitrate and calcium ammonium nitrate plants",
    "reactor_anthraquinone-autoxidation": "Anthraquinone hydrogen peroxide plants",
    "reactor_chemical-depolymerization": "Loop Industries (PET); Agilyx (polystyrene)",
    "reactor_ethylene-oxidation": "Ethylene oxide and glycol plants",
    "reactor_nitric-acid": "Ostwald-process nitric acid plants",
    "reactor_polymerization-extrusion": "Polyethylene, polypropylene, PVC, and PET plants",
    "reactor_urea-synthesis": "CO2-stripping urea plants (Stamicarbon, Saipem)",
    "separator_aromatics-extraction": "Sulfolane extraction units",
    # breweries
    "chiller_absorption": "Lithium bromide and ammonia absorption chillers",
    "chiller_high-efficiency": "Magnetic-bearing and variable-speed centrifugal chillers",
    "chiller_vapour-compression": "Ammonia or glycol refrigeration plants for fermenter and cellar cooling",
    "cleaning-system": "Clean-in-place systems; keg and bottle washers",
    "cleaning-system_efficiency-strong": "Final-rinse reuse; heat recovery from clean-in-place returns; cycle optimization",
    "heat-exchanger_aseptic-uht": "UHT and aseptic processing lines",
    "heat-exchanger_steam-heated": "Mash tuns, wort kettles, and plate pasteurizers",
    "heat-exchanger_steam-heated_efficiency-strong": "Regenerative pasteurizers; heat recovery and insulation on kettles",
    "press_high-pressure-processing": "High-pressure pasteurization of juices",
    "radio-frequency-heater_food": "Microwave, radio-frequency, ohmic, and infrared heating",
    "oven_fuel-fired": "Tunnel and deck ovens",
    "oven_fuel-fired_efficiency-moderate": "Burner control and modulation; heat-transfer optimization; lighter baking tins",
    "oven_electric": "Electric tunnel ovens",
}

# Per sector: title, what the review covers, judgement calls (heading, bullets), known gaps, optional extra blocks.
SECTORS = {
    "steel": {
        "title": "Iron and steel",
        "covers": "the archetypes that make iron and steel products (agglomeration, cokemaking, ironmaking, "
                  "direct reduction, steelmaking, ladle preheating and refining, casting, reheating, hot and "
                  "cold rolling, pickling, annealing and coating, and foundry melting) and provide more general "
                  "services to iron and steel plants (steam, oxygen, capture, machine drive, heating and "
                  "cooling, and lighting)",
        "calls": [
            ("Biocarbon in the blast furnace", [
                "`blast-furnace_biogenic-carbon` is a blast furnace with part of its injected coal or coke replaced "
                "by charcoal or other biocarbon. Its energy use comes from one example, a Brazilian furnace that runs "
                "on charcoal alone, not one that injects some biocarbon beside coke. Is that a fair stand-in, and "
                "what share of coal or coke can biocarbon replace in a large furnace?",
                "The charcoal comes from `kiln_charcoal-retort`, whose capital cost and energy use are judgements "
                "from one retort maker's figures and one study's wood yields.",
            ]),
            ("Merged", [
                "Fines-based direct reduction (Circored, Finmet) is pooled into `shaft-furnace_direct-reduction`. "
                "It skips pelletizing, which the database treats as a separate step. Should it stand apart?",
                "Membrane air separation (low-purity oxygen) is pooled into `air-separation-unit`.",
                "Fermentation of steel off-gas is pooled into `reactor_steel-offgas-chemicals`, so steel off-gas "
                "use is held once. It is kept for reference only, not as a capture option: it makes methanol or "
                "ethanol and needs hydrogen, which the database does not record, and those products have their own "
                "nodes in chemicals and biofuels.",
                "The foundry electric arc furnace is pooled into `electric-arc-furnace`. Foundry heats are "
                "smaller and tap hotter, but the energy gap measured under 15%.",
                "Coupled pickling and cold rolling are pooled into `rolling-mill_cold`, which also absorbs the "
                "separate pickling line.",
            ]),
            ("Kept apart", [
                "Induction heating for heat treatment and for reheating (lower temperatures for hardening and "
                "annealing).",
                "Moderate and strong efficiency buckets on the blast furnace, basic oxygen furnace, coke oven, "
                "sinter plant, reheating furnace, and hot mill. Sources give 10–30% savings for recuperative or "
                "regenerative burners. Pooling across furnace ages may hide the difference between the reheating "
                "buckets.",
            ]),
            ("Framing", [
                "The hydrogen route reaches the model as a chain: hydrogen direct reduction "
                "(`shaft-furnace_hydrogen-direct-reduction`, buying about 6.8 GJ of hydrogen per t of reduced iron "
                "from the hydrogen sector) feeds the electric arc furnace. The whole plant "
                "(`shaft-furnace_electrolytic-hydrogen`: electrolysers, shaft furnace, and electric arc furnace) is "
                "kept for reference, so the route is not offered twice. Its values are compared with the chain: "
                "the chain uses about 10% more electricity and some natural gas. Its capital cost came to about 16% "
                "less than the whole plant's, and hydrogen storage adds only about 2%, so the rest (hydrogen "
                "handling at the shaft and site integration) is added to hydrogen direct reduction as a capital "
                "share (x 1.5). The chain and the whole plant now cost the same. Is that share reasonable?",
                "Some of the whole plant's sourced route costs include a return or the electrolyser; whole-route "
                "production costs from Material Economics 2019 and Draxler 2021 were ruled out.",
                "Ironmaking has two products: iron (t), from blast furnaces and smelting reduction, and reduced "
                "iron (t), from direct reduction. Check that each archetype makes the right one.",
                "Energy use is gross input. Recovered converter gas, coke-oven gas, and steam are outputs, not "
                "credits; net figures from sources were grossed up or excluded.",
                "The capture variants (blast furnace, smelting reduction, and direct reduction with capture) "
                "take their host's size and costs, plus a capture add-on.",
            ]),
            ("What each furnace buys", [
                "Each archetype asks the other steel nodes for what it uses, per tonne of its product. The blast "
                "furnace buys coke (its coke energy, about 0.4 t), about 1.45 t of pellets and 0.1 t of sinter, "
                "and about 0.05 t of oxygen. That is a Canadian burden of mostly fluxed pellets; the sources' "
                "European burden (about 1.1 t of sinter and 0.55 t of pellets) stays in their rows. "
                "Smelting reduction buys about 0.7 t of oxygen, the basic oxygen furnace about 0.07 t, and the "
                "electric arc furnaces about 0.05 t.",
                "The arc furnace charged with reduced iron (`electric-arc-furnace_reduced-iron-charge`) buys about "
                "1.0 t of reduced iron per t of steel from the direct-reduction step.",
                "The electric smelting furnace melts bought reduced iron, about 1.1 t per t of iron.",
                "Pellets come from the mines, which make most Canadian pellets, so pellet plants serve the mining "
                "sector only and steel's agglomeration step holds sinter plants. Direct reduction buys about "
                "1.4 t of pellets per t of reduced iron.",
                "Casting routes that skip a later step ask for none of it. The thin-slab caster rolls in line and "
                "the strip caster casts near final thickness, so neither asks for hot rolling or reheating. "
                "Ingot casting reheats in its own soaking pits, so it asks for hot rolling but not reheating.",
                "Is each quantity right for a Canadian plant?",
            ]),
            ("Scope and accounting", [
                "Rolling-mill energy pools rows covering the mill plus its reheat furnace or annealing; "
                "off-scope rows were ruled out. Check that what remains is the mill alone.",
                "The heat-recovery coke oven burns its volatiles, while the by-product oven exports gas, so the "
                "two count energy differently.",
                "The electric arc furnace is split by charge. `electric-arc-furnace` melts mostly scrap (up to about "
                "a third reduced iron or pig iron) and uses about 2.1 GJ/t. "
                "`electric-arc-furnace_reduced-iron-charge` takes the examples charged half or more with reduced "
                "iron or hot-briquetted iron and uses about 3.6 GJ/t, since the gangue and lower metallisation "
                "of reduced iron add electricity and slag. One source's biomass-carbon furnace no longer sets the "
                "carrier split, since the database has no biomass-carbon arc furnace.",
            ]),
        ],
        "gaps": [
            "No sourced examples: `induction-heater_strip-heating` and `rolling-mill_cold_efficiency-moderate`; "
            "every value is filled.",
            "One or two examples: `melting-furnace_isothermal`, `melting-furnace_crucible-gas-fired`, "
            "`annealing-furnace_hydrogen-bell`, and `pellet-plant_plasma-electric`.",
            "Low-readiness routes with mainly guessed costs: molten oxide electrolysis, low-temperature "
            "electrowinning (readiness level 5), and electric smelting of direct-reduced iron.",
        ],
    },
    "cement-and-lime": {
        "title": "Cement and lime", "adj": "cement and lime",
        "covers": "the archetypes that create cement products (clinker, grinding, binder, calcined clay, and "
                  "ground slag), the archetypes that calcine lime and dolime, and those that provide more general "
                  "services to mineral plants (kiln heat, capture, machine drive, heating and cooling, and "
                  "lighting)",
        "calls": [
            ("Lime kilns", [
                "Lime and dolime calcination has five kiln archetypes: long rotary, rotary with preheater (and "
                "its post-combustion capture variant), shaft (mixed-feed and annular), and oxy-fuel kilns. All are "
                "per tonne of lime. The indirectly heated calciner is held per tonne of clinker, on the clinker "
                "archetypes and the kiln-heat service; it is not yet a lime kiln option.",
                "Process CO2 from calcination (0.785 t per t of quicklime, the stoichiometric value) is held "
                "separately from combustion CO2. Check the quicklime and dolime bases of the kiln rows.",
                "Lime-mud kilns in kraft pulp mills are a different process and are not included here.",
            ]),
            ("Options that may have stalled", [
                "Development of these options may have stalled. We have kept them for now; tell us whether they are still being pursued, and whether the database should keep them as options.",
                "`kiln_electric-plasma`: the electrified clinker kiln studied by Cementa and Vattenfall (CemZero). "
                "The feasibility study finished in 2019, and we found no later plan to build a plant.",
                "`binder_hydrothermal-silicate`: the hydrothermal calcium hydrosilicate binder (Celitement). Its "
                "developer became part of Schwenk Zement in 2020, ahead of a decision on a first industrial plant; we "
                "found no later news.",
            ]),
            ("Binders: recipes and binder plants", [
                "Four binders are recipes: Portland, blended (slag), calcined clay (LC3), and alkali-activated. "
                "Each holds only its own blending step and buys the rest from the archetypes that make it. Per "
                "tonne of cement, Portland cement buys 0.95 t of clinker, the blended cement 0.55 t of clinker "
                "and 0.40 t of ground slag, and LC3 0.50 t of clinker and 0.30 t of calcined clay; all three buy "
                "finish grinding for the whole tonne. The alkali-activated binder buys 0.85 t of ground slag and "
                "pays for its activator as an operating cost.",
                "Four binders are plants that make their own binder: sulphoaluminate, carbonated, hydrothermal, "
                "and electrochemical. Their energy and costs include firing (or electrolysis) and grinding, so "
                "they buy no clinker and no finish grinding. The hydrothermal binder also buys the 0.18 t of "
                "Portland clinker per tonne that its source blends in.",
                "One source's capital cost for an alkali-activated binder covers a whole geopolymer works "
                "(about 620 dollars per tonne-year); it is kept in the detailed tables but not used, since the "
                "slag grinding is counted with the ground slag. Check that each recipe's ratios are sound, and "
                "that the binder plants' energy covers their whole process.",
            ]),
            ("Merged", [
                "The fluidized-bed kiln (a niche demonstration) and flash or fluid calciners (part of a "
                "precalciner line) are pooled into `kiln_dry-precalciner`.",
                "High-pressure grinding rolls are pooled into `grinding-mill_vertical-roller` for cement.",
                "`kiln_legacy` holds wet, semi-dry, and long dry kilns together. Is one legacy archetype enough "
                "for Canadian stock?",
            ]),
            ("Capture and electrification", [
                "Oxy-fuel and calcium-looping kilns keep their own archetypes, since they concentrate their own "
                "CO2 stream. They send that CO2 to a concentrated-stream capture service, which purifies and "
                "compresses it: per tonne of clinker, about 0.77 t from the oxy-fuel kiln and 1.0 t from the "
                "calcium-looping kiln. Their energy use leaves out the CO2 purification unit (about 0.35 to 0.43 "
                "GJ of electricity per tonne of clinker), which the capture service carries. They also buy their "
                "oxygen from the oxygen service (about 0.25 t per tonne of clinker for the oxy-fuel kiln and "
                "0.38 t for the calcium-looping kiln), so their energy use leaves out the air separation unit "
                "too (about 0.22 and 0.31 GJ per tonne of clinker). The sources do not split these units' capital "
                "cost, so it is taken off as a judged share: about 80% of the oxy-fuel kiln's capital above the "
                "base kiln and about 30% of the calcium-looping kiln's. Are those shares reasonable? The oxy-fuel lime kiln (about 0.93 t CO2 per tonne of lime) and the "
                "indirectly heated calciner (about 0.50 t of process CO2 per tonne of clinker) use the same "
                "service.",
                "Post-combustion capture is the variant `kiln_dry-precalciner_ccs-diffuse`, which takes the host "
                "kiln's size and costs plus a capture add-on. On a capture variant, total emissions are net.",
                "Electrified routes are `calciner_indirect` (readiness level 6) and `kiln_electric-plasma` "
                "(readiness level 4–5, two examples).",
            ]),
            ("Bases", [
                "Clinker covers raw-meal preparation through the clinker cooler; finish grinding is separate. "
                "A few legacy-kiln sources leave out raw milling or count the whole plant to finished cement; the "
                "difference is small beside the kiln's fuel, so they are kept.",
                "Clinker and cement are separate products. Where a source printed a value per tonne of cement "
                "that is really per tonne of clinker, the database takes it on an assumed correction, flagged in "
                "the detailed tables. Check the clinker-to-cement basis of the kiln rows.",
                "The kiln efficiency buckets come partly from UKERC savings applied to the base kiln's pooled "
                "energy use.",
            ]),
        ],
        "gaps": [
            "No sourced examples: `kiln_calcium-silicate-feed` and `grinding-mill_slag`.",
            "One example: `binder_electrochemical`. Most binder archetypes have guessed capital and operating "
            "costs (eight guessed cells each).",
            "Two examples: `kiln_electric-plasma`.",
            "One example: `kiln_lime-oxy-fuel`; its capital cost, energy use, and emissions are judgements.",
        ],
    },
    "pulp-and-paper": {
        "title": "Pulp and paper",
        "covers": "the archetypes that make pulp and paper products (wood preparation; chemical, mechanical, "
                  "semi-chemical, and recycled pulping; bleaching; pulp drying; and forming and drying for "
                  "coated, uncoated, newsprint, linerboard, and tissue grades) and provide more general services "
                  "to pulp and paper mills (chemical recovery, effluent treatment, steam, machine drive, heating "
                  "and cooling, and lighting)",
        "calls": [
            ("An option that may have stalled", [
                "Development of these options may have stalled. We have kept them for now; tell us whether they are still being pursued, and whether the database should keep them as options.",
                "`gasifier_black-liquor`: black liquor gasification, as developed by Chemrec. Chemrec now only "
                "licenses its patents. Its commercial project at Domsjö stopped in 2012, and its pilot plant at "
                "Piteå was mothballed in 2016. No commercial plant has been built.",
            ]),
            ("Units", [
                "Pulp is counted in air-dry tonnes (90% dry); figures per oven-dry tonne are converted per "
                "example. Recovery boilers and evaporators are per tonne of black liquor solids, converted from "
                "per-air-dry-tonne figures with each source's own solids ratio. The lime kiln is per tonne of "
                "lime.",
                "Biogenic CO2 from black liquor (about 1.1 t per t of solids) and from kraft lime-kiln "
                "calcination (about 0.58 t per t) is held as biogenic, with fossil CO2 at zero.",
            ]),
            ("Paper grades", [
                "Each paper grade has its own forming and drying steps, but one set of paper-machine and dryer "
                "archetypes serves all grades. Do grade differences (tissue against newsprint, for example) need "
                "separate values?",
                "`dryer_market-pulp` stays separate from the paper dryer, for drying market pulp.",
            ]),
            ("Merged", [
                "Dryer hood heat recovery is in the moderate dryer efficiency bucket.",
                "Mechanical vapour recompression for black liquor and for caustic evaporation is one archetype, "
                "shared with chemicals.",
                "The gas-fired Yankee hood is pooled into `dryer_direct-fired`. On a tissue machine a hood works "
                "with the steam cylinder, so it may complement rather than replace it.",
            ]),
            ("Kept apart", [
                "Stone groundwood and thermomechanical pulping stay separate: groundwood is a legacy type in "
                "Canadian stock, and thermomechanical pulping recovers refiner heat.",
            ]),
            ("Whole mills and whole machines", [
                "The model builds a mill from its steps, so whole-mill figures are not options in it. They are kept "
                "as reference archetypes and compared with the sum of the steps: `pulp-mill_kraft` (a whole kraft "
                "pulp mill per air-dry tonne) and `paper-machine_with-dryer-section` (forming, pressing, and drying "
                "together, per tonne of paper). The steps reached about two thirds of the whole mill's capital cost and "
                "0.85 of the whole paper machine's, because causticizing, washing, screening, stock preparation, "
                "and offsites have no archetype. That capital is added back as a share: x 1.63 on the kraft "
                "steps (cooking, bleaching, evaporation, the recovery furnace, and the lime kiln) and x 1.53 on "
                "the paper machine of every grade. Are these the missing pieces, and is the share reasonable?",
                "Dry or foam forming (`paper-machine_waterless`) removes most of the water before the dryer, and its "
                "energy and cost include the drying. In the model it gives back the drying its paper grade asks for "
                "(minus 1 tonne of dried paper per tonne).",
                "Black liquor gasification competes as a combined-cycle (power) route. The fuel routes (DME, "
                "methanol, FT liquids, mixed alcohols) are kept as the reference `gasifier_black-liquor-fuels`, "
                "since the model has no outlet for the fuels at the recovery boiler.",
                "Sulphite cooking is the cooking stage only; sulphite mills ask the lime kiln for nothing.",
            ]),
            ("What each step buys and gives back", [
                "Each step buys its steam from the mill's steam service, which chooses how the steam is made. "
                "Steps that raise steam give it back: the recovery boiler (about 10.6 GJ per tonne of solids), the "
                "high-solids recovery boiler (about 11.2), the "
                "black liquor gasifier (about 7 GJ of steam and 4 GJ of electricity), and the refiners of "
                "thermomechanical (2.5 GJ per air-dry tonne), low-energy (2.1), and chemi-thermomechanical (2.7) "
                "pulping.",
                "The make-up biomass a gasifier burns to replace the recovery boiler's steam is bought as steam "
                "from the steam service, not burned in the gasifier.",
                "Heat-pump-assisted drying (`dryer_heat-pump`) is the steam-heated dryer section with a heat pump "
                "added: 1.26 GJ of steam and 1.12 GJ of electricity per tonne, from the same source's dryer less the "
                "2.7 GJ the pump returns. Its capital cost is the dryer's plus the heat pump's.",
                "Anaerobic effluent treatment gives back its biogas as fuel, about 0.05 GJ per m3 of high-strength "
                "effluent; this is a judgement, since no source gives the yield.",
                "Capture on the recovery boiler and the lime kiln sends its CO2 to the mill's capture service.",
            ]),
            ("Scope", [
                "Groundwood pulping uses no steam, following NRCan's 2008 survey of 49 Canadian mills; the U.S. "
                "area allocations in Jacobs 2006 and Kramer 2009 were ruled out.",
                "Steam-heated dryer energy pools sources with different section boundaries; check that values "
                "cover the dryer section only.",
            ]),
        ],
        "gaps": [
            "No sourced examples: activated-sludge aeration (base and moderate) and clarification; every value "
            "is filled.",
            "Two examples: `dryer_through-air` and `kiln_lime-electric`. `dryer_heat-pump` rests on one source's "
            "heat pump added to its own dryer.",
            "Deep eutectic solvent pulping and waterless forming are at readiness level 4.",
            "Anaerobic effluent treatment has seven examples, several from food and brewery sources; check that "
            "it suits mill effluent.",
        ],
    },
    "chemicals": {
        "title": "Chemicals",
        "covers": "the archetypes that make chemical products (ammonia, methanol, urea, other fertilizers, "
                  "nitric and adipic acid, chlorine and caustic soda, sodium chlorate, hydrogen peroxide, "
                  "olefins, aromatics, olefin derivatives, and polymers) and provide more general services to "
                  "chemical plants (distillation, N2O abatement, steam, capture, machine drive, heating and "
                  "cooling, and lighting)",
        "calls": [
            ("Merged", [
                "Heat-pumped distillation and vapour-recompression distillation are one archetype, "
                "`distillation-column_heat-pumped`.",
                "Rotodynamic (turbo) cracking is pooled into `steam-cracker_electric`; the two differ by about "
                "the 15% threshold once on the same basis.",
                "Low-pressure Haber-Bosch loops for variable hydrogen are pooled into "
                "`reactor_haber-bosch-electrolytic`.",
                "Total-recycle urea is pooled into `reactor_urea-synthesis`; a claimed 5.5 GJ/t against "
                "3.1–3.8 GJ/t does not show in the pooled totals.",
            ]),
            ("Framing", [
                "All ammonia and methanol routes are whole plants that make their own hydrogen: reforming or "
                "gasification plus synthesis, or on-site electrolysers plus synthesis for "
                "`reactor_haber-bosch-electrolytic` and `reactor_co2-to-methanol`. None of them buys hydrogen. "
                "The synthesis loops priced alone (`reactor_haber-bosch-loop` and `reactor_methanol-loop`) are "
                "kept only to check the whole plants: the loop plus a central electrolyser comes within about "
                "10% of the whole plant's energy use and about 10-30% of its capital cost. Check that the "
                "electrolytic plants do not double count with the hydrogen sector.",
                "`reactor_co2-to-methanol` buys captured CO2 (1.4 t per t methanol) from the capture service.",
                "Biomass reaches olefins through `gasifier_biomass-methanol` and `reactor_methanol-to-olefins`, "
                "which buys 2.3 t of methanol per tonne of high-value chemicals. The whole biomass-to-olefins "
                "plant is kept for comparison only. Flash pyrolysis of biomass to olefins "
                "(`reactor_biomass-flash-pyrolysis`) is a route of its own.",
                "Feedstock whose energy ends up in the product is recorded as `feedstock-consumption`, not as "
                "energy use, for crackers, reformers, and gasifiers. Check that the energy columns hold process "
                "energy only.",
                "The petrochemical steps (olefins, aromatics, derivatives, and polymers) were chosen to suit "
                "Canadian industry. One polymerization and extrusion archetype covers all polymers, from 128 "
                "examples. Is one enough?",
                "Each N2O abatement step has a zero-cost, zero-energy no-abatement option, set entirely by "
                "judgement.",
            ]),
            ("Products and units", [
                "Chlor-alkali cells are per tonne of chlorine and hold the electrolysis alone. The steam that "
                "concentrates their caustic to 50% is on the caustic-evaporation step, per tonne of water "
                "evaporated. Each cell asks that step for its water: 1.27 t per tonne of chlorine for membrane "
                "and oxygen-depolarized cells, 6.8 t for diaphragm cells, and none for mercury cells, which make "
                "50% caustic directly. Do these quantities match your plants?",
                "Plants that include their own separation columns (aromatics extraction, steam crackers, and "
                "ethylene oxide) do not also ask the distillation service for them.",
                "Steam is bought from the steam service. Where a source gave fuel that includes the steam it "
                "raises, alongside other sources giving that steam separately (adipic acid), the combined fuel "
                "figure is kept as an example but not pooled.",
                "Mercury and diaphragm cells remain as legacy types. Are they still in Canadian stock?",
            ]),
            ("Energy scope", [
                "For several archetypes the sourced total and its carrier split come from sources with "
                "different scopes, notably `gasifier_coal-methanol`. Check which scope the total holds.",
            ]),
        ],
        "gaps": [
            "One example: `electrolysis-cell_sodium-chlorate` (nine guessed cells) and "
            "`gasifier_coal-methanol_ccs-concentrated`.",
            "Two or three examples: autothermal ammonia (with and without capture), biomass gasification to "
            "ammonia, hydrogen peroxide, and thermal N2O destruction.",
            "Capture on the cracker furnace flue gas is at readiness level 3–4.",
        ],
    },
    "breweries": {
        "title": "Breweries",
        "covers": "the archetypes that provide the process services brewing draws on (steam, process heating "
                  "for cooking, pasteurizing, and sterilizing, cleaning, refrigeration, machine drive, heating "
                  "and cooling, and lighting). Light-industry drying, metal melting, heat treatment, and forming "
                  "and pressing are left out",
        "calls": [
            ("No separate brewery process", [
                "The database does not treat brewing as a process of its own. Breweries fall under light "
                "industry's food, tobacco, and beverage products, and the light-industry services are shared by "
                "every light industry. So the values on these archetypes pool brewery data with dairy, juice, "
                "canning, and other food sources. Do brewery values differ enough to need their own archetypes?",
                "The ovens (baking, frying, and roasting) appear because they serve the same light-industry "
                "heat services; they are not brewery equipment, and you can skip them.",
            ]),
            ("How brewery data enters", [
                "`heat-exchanger_steam-heated` (kettles, retorts, and plate heat exchangers) is measured per "
                "tonne of product. Brewery figures per barrel or hectolitre are converted with a wort-and-beer "
                "density of 1.03 t/m3 (range 1.01–1.05). This covers the Galitsky 2003 mash and wort-kettle rows, "
                "the Giner-Santonja 2019 brewhouse rows, and the DOE 2017 bandwidth study's current-typical "
                "brewhouse figure (0.585 GJ/t).",
                "Galitsky prints brewhouse heat as boiler fuel. The archetype carries steam, so those rows are "
                "converted at Galitsky's own 85% boiler efficiency.",
                "Regenerative pasteurizers are in the strong efficiency bucket of the steam-heated archetype, "
                "not a separate archetype.",
                "Keg washing is on `cleaning-system`.",
                "Process heat is bought as steam from the light-industry steam service: aseptic and UHT "
                "processing asks for 0.77 GJ of steam per tonne of product.",
            ]),
            ("Brewery examples set aside", [
                "DOE 2017 state-of-the-art brewhouse: only 5% below current typical, and the archetype has no "
                "moderate efficiency variant.",
                "DOE 2017 space heating, refrigeration, lighting, compressed air, and boiler rows: per barrel of "
                "beer, with no way to turn them into GJ of heat or cooling, lumen-hours, or shaft work. DOE's "
                "packaging, utilities, and other rows cover whole lines with no matching archetype, and its "
                "practical-minimum tier is R&D.",
                "Giner-Santonja 2019 bottling: combines bottle washing with tunnel pasteurizing.",
                "Whole-site brewery benchmarks (Giner-Santonja 2019 and Galitsky's average U.S. brewery) are kept "
                "as calibration data only, since no whole-plant food archetype exists.",
                "Galitsky's fermentation CO2, microfiltration, and dealcoholisation rows: no matching archetype.",
            ]),
            ("Refrigeration", [
                "`chiller_vapour-compression` is process refrigeration (product cooling, 60% capacity factor); "
                "space cooling has its own `chiller_hvac` archetype. `chiller_high-efficiency` still prices from "
                "commercial air-conditioning equipment.",
            ]),
        ],
        "gaps": [
            "No archetype for brewery-specific options: wort boiling systems, fermentation, CO2 recovery, "
            "packaging lines, or malt kilning.",
            "Brewery effluent: anaerobic treatment with biogas recovery is in the database, but only for "
            "pulp-and-paper effluent, so it is not included here.",
            "One example: `chiller_high-efficiency` and `press_high-pressure-processing`.",
        ],
    },
}


EXAMPLES.update(EXAMPLES_MORE)
SECTORS.update(SECTORS_MORE)


def example_for(archetype, key):
    return EXAMPLES.get(f"{archetype}@{key}", EXAMPLES.get(archetype, ""))


def build(outdir, facts):
    for key, s in SECTORS.items():
        adj = s.get("adj") or ("brewery" if key == "breweries" else s["title"].lower())
        f = facts[key]
        cross = ", ".join(f"{FAMILY_LABEL.get(k, k)} ({v})" for k, v in f["cross_families"].items())
        rows, prev = [], None
        for r in f["table"]:
            rows.append(["" if r["band"] == prev else r["band"], "`" + r["archetype"] + "`",
                         r["label"] + (" (filled only)" if r["status"] == "estimated" else ""),
                         example_for(r["archetype"], key), r["n"], r["trl"]])
            prev = r["band"]
        body = [
            ("p", "This note lists the sector's archetypes, the sources behind them, and the judgement calls we "
                  "most want a sector expert to test. Read it with the methodology summary and the database "
                  "file."),
            ("h1", "1. What this review covers"),
            ("p", f"The database file holds {s['covers']}."),
            ("p", f"It has {f['rows']} rows for {f['archetypes']} archetypes: **{f['own']} {adj} archetypes** and "
                  f"{f['cross']} cross-cutting archetypes that serve the same processes, by family: {cross}. The "
                  "cross-cutting rows stay in their own families. Comment on whether they fit the sector; a "
                  "detailed check of their values is optional."),
            ("h1", f"2. The {adj} archetypes"),
            ("lead", "Each archetype stands for a real process or piece of equipment. Within each step the "
                     "table runs from conventional technologies to efficient variants, capture variants, and "
                     "then low-carbon alternatives and prospective options. \"Real-life examples\" names plants, "
                     "technologies, or measures that the archetype represents. \"Source examples\" counts the "
                     "examples from published sources behind it; an archetype marked \"filled only\" has no "
                     "sourced values, so every value is estimated."),
            ("table", [1250, 1950, 1650, 2160, 1050, 1300],
             ["Step", "Archetype", "Label", "Real-life examples", "Source examples", "Readiness level"], rows),
            ("h1", "3. Main sources"),
            ("lead", f"{f['n_sources']} sources supply the {f['n_examples']} examples behind the {adj} archetypes. "
                     "The ten that supply the most:"),
            ("table", [2500, 5760, 1100], ["Source", "Citation", "Examples"],
             [[t["short"], t["citation"], t["n"]] for t in f["top"]]),
            ("gap",),
            ("h1", "4. Judgement calls to test"),
            ("p", "These are the choices most likely to need a sector expert's view. Tell us where you would decide "
                  "differently, and why."),
        ]
        for head, items in s["calls"]:
            body += [("h2", head), ("bullets", items)]
        body += [("h1", "5. Known gaps"), ("bullets", s["gaps"]),
                 ("p", "Tell us about missing technologies, or better sources for thin archetypes, in the "
                       "reviewer-comment column or in your covering note.")]
        body += [tuple(b) for b in s.get("extra", [])]
        doc = make_doc(f"Sector note: {s['title']}", "Technology database review package  |  build of 4 November 2026",
                       f"Sector note: {s['title']}")
        render(doc, body)
        doc.save(outdir / f"review-package_{key}" / f"sector-note_{key}.docx")
