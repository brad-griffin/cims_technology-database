"""Proposed crosswalk between cims_hierarchy.csv and the design end uses.

Written for design/cims-hierarchy-harmonization.md (revision 6), applied to the design
table and to cims_hierarchy.csv on 2026-09-16/17. The rules accept both the old and the
new paths; suggested-branch is empty for a node already in its new form. Every end-use id it names must exist in sector-end-use-table.csv;
the script fails if one does not. cims_services.py then writes the table's
`cims-services` column from the output.

Run from the repo root:  python design/build/hierarchy_crosswalk.py [output.csv]
Writes design/cims-hierarchy-crosswalk.csv with one row per in-scope hierarchy leaf,
plus one row per node the proposal adds to the hierarchy (status proposed-new, or
existing once it appears). Prints leaves that match no rule; exits 1 if there are any.
Re-run whenever cims_hierarchy.csv changes.

Columns
  branch            the hierarchy leaf, or the proposed new node
  status            existing | proposed-new
  end-use           design end use(s), "; "-separated when one CIMS service is split
  share             whole | part (blank for nodes that are not end uses)
  role              end-use | heat-supply | fuel-routing | fuel-blend | feedstock
  suggested-branch  the proposal's simplified hierarchy path; blank = unchanged,
                    "(remove)" = drop the node
  table-change      what the proposal changes in the design table's cims-services cell
  note
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "design"
HIER = DESIGN / "cims_hierarchy.csv"
OUT = DESIGN / "cims-hierarchy-crosswalk.csv"

IN_SCOPE = {"biodiesel", "chemicals", "coal-mining", "construction", "direct-air-capture",
            "ethanol", "hydrogen", "industrial-minerals", "iron-and-steel",
            "light-industrial", "metal-smelting", "mining", "natural-gas",
            "petroleum-crude", "petroleum-refining", "pulp-and-paper"}

X = "cross-sector/"
LM = [X + "heat-low-temp", X + "heat-medium-temp"]
MH = [X + "heat-medium-temp", X + "heat-high-temp"]
MOB = [X + "mobile-equipment"]

# ---------------------------------------------------------------------------
# End-use rules: (regex on "<cims-sector>.<rest>", [targets], role, table-change, note)
# First match wins.
# ---------------------------------------------------------------------------
R = [
    # not end uses
    (r"\.service\.fuel-blend\.(process-gas|still-gas)$", [], "fuel-routing", "",
     "by-product fuel; its heat is counted on the steam, reheating and direct-heat nodes it feeds"),
    (r"\.service\.fuel-blend(\.|$)", [], "fuel-blend", "renewable-natural-gas, renewable-diesel-and-saf: drop",
     "blends a commodity into supply"),
    (r"\.service\.agricultural-input$", [], "feedstock", "", ""),
    # by-product fuel routing
    (r"^iron-and-steel\.service\.iron-process-gas\.reheating$", ["iron-and-steel/reheating"], "fuel-routing", "", "G4"),
    (r"^iron-and-steel\.service\.iron-process-gas\.steam$", LM, "fuel-routing", "", "G4"),
    (r"^petroleum-refining\.service\.still-gas\.heater$", MH, "fuel-routing", "", "G4"),
    (r"^petroleum-refining\.service\.still-gas\.steam$", LM, "fuel-routing", "", "G4"),
    (r"^petroleum-crude\.service\.still-gas-steam$", LM, "fuel-routing", "", "G4"),
    # supplied heat
    (r"\.service\.steam$", LM, "heat-supply", "in-situ-bitumen: drop petroleum-crude steam", ""),
    (r"^petroleum-refining\.service\.direct-heat$", MH, "heat-supply", "", ""),
    (r"^natural-gas\.product\.supply\.direct-heat$", LM, "heat-supply", "", ""),
    (r"^light-industrial\.service\.(heat\.indirect|water-heating)$", [X + "heat-low-temp"], "heat-supply",
     "space-heating: drop water heating; drying-curing-and-forming: drop heat.indirect",
     "merged into light-industrial.service.steam"),
    (r"^light-industrial\.service\.heat(\.direct)?$",
     [X + "heat-medium-temp", X + "heat-high-temp", "other-industry/metal-melting-and-heat-treatment",
      "other-industry/drying-curing-and-forming"], "heat-supply", "", ""),
    (r"^industrial-minerals\.service\.(heat|kiln-heat)$",
     ["cement/clinker-production", "non-metallic-minerals/lime-calcination"], "end-use",
     "add here; drop from melting-and-firing and drying-and-low-temp-calcining",
     "requested only by the clinker and lime kilns"),
    # machine drive and facility services
    (r"\.service\.machine-drive\.pumps$", [X + "pumps"], "end-use", "id pumping -> pumps", ""),
    (r"\.service\.machine-drive\.fans(-and-blowers)?$", [X + "fans-and-blowers"], "end-use", "", ""),
    (r"\.service\.machine-drive\.compressed-air$", [X + "compressed-air"], "end-use", "", ""),
    (r"\.service\.machine-drive\.materials-handling$", [X + "materials-handling"], "end-use", "", ""),
    (r"\.service\.machine-drive\.materials-processing$", [X + "materials-processing"], "end-use", "", ""),
    (r"^light-industrial\.service\.machine-drive$", [X + "materials-processing"], "end-use", "",
     "CIMS light industry has one undifferentiated motive-power service, not the five MECS categories"),
    (r"\.service\.hvac\.space-heating$", [X + "space-heating"], "end-use",
     "ventilation-and-air-heating: drop mining space heating", ""),
    (r"\.service\.hvac\.space-cooling$", [X + "space-cooling"], "end-use", "", ""),
    (r"^light-industrial\.service\.hvac$", [X + "space-heating", X + "space-cooling"], "end-use",
     "ventilation folded into space heating and cooling", "combined HVAC system"),
    (r"\.service\.lighting$", [X + "lighting"], "end-use", "", ""),
    # mobile engines
    (r"^construction\.product\.transport$", MOB, "end-use", "", ""),
    (r"^natural-gas\.product\.supply\.(extraction\.)?off-road-transport$", MOB, "end-use", "", ""),
    # CO2 capture
    (r"\.service\.ccs\.concentrated$", [X + "co2-capture-concentrated"], "end-use",
     "one node per stream since 2026-09-18, so no end use takes only part of a CCS service", ""),
    (r"\.service\.ccs\.diffuse$", [X + "co2-capture-diffuse"], "end-use", "", ""),
    (r"\.service\.ccs$", [], "grouping", "", "parent of the stream-named capture services"),
    (r"^natural-gas\.product\.supply\.formation-co2$", ["oil-and-gas/gas-processing"], "end-use",
     "moved 2026-09-18", "the CO2 in the raw gas and the capture-or-vent decision at the plant; the capture itself is natural-gas.service.ccs_concentrated"),
    (r"^direct-air-capture\.", [X + "direct-air-capture"], "end-use", "", ""),
    (r"^mining\.service\.on-site-power$", [X + "on-site-power-generation"], "end-use", "", ""),
    # iron and steel
    (r"^iron-and-steel\.service\.coke$", ["iron-and-steel/cokemaking"], "end-use", "", ""),
    (r"^iron-and-steel\.service\.agglomeration$", ["iron-and-steel/agglomeration"], "end-use", "", ""),
    (r"^iron-and-steel\.service\.(hot-metal|direct-reduced-iron)$", ["iron-and-steel/ironmaking"], "end-use", "", ""),
    (r"^iron-and-steel\.product\.molten-steel\.integrated$",
     ["iron-and-steel/ironmaking", "iron-and-steel/steelmaking"], "end-use", "",
     "route technologies; split into hot-metal, direct-reduced-iron and molten-steel"),
    (r"^iron-and-steel\.product\.molten-steel(\.recycled)?$", ["iron-and-steel/steelmaking"], "end-use", "", ""),
    (r"^iron-and-steel\.(product\.continuous-cast\.ladle-|service\.ladle-)", ["iron-and-steel/steelmaking"],
     "end-use", "", ""),
    (r"^iron-and-steel\.service\.oxygen\b", ["iron-and-steel/steel-oxygen-supply"], "end-use", "", ""),
    (r"^iron-and-steel\.product\.continuous-cast\.(.*\.)?(casting|billet-casting|bloom-casting)$",
     ["iron-and-steel/casting"], "end-use", "", ""),
    (r"^iron-and-steel\.service\.reheating\b", ["iron-and-steel/reheating"], "end-use", "", ""),
    (r"^iron-and-steel\.product\.continuous-cast\..*(electroclean\.(anneal-temper|electric-steel|tin-plate)|galvanize|annealing-and-coating)$",
     ["iron-and-steel/annealing-and-coating"], "end-use", "", ""),
    (r"^iron-and-steel\.product\.continuous-cast\.", ["iron-and-steel/rolling"], "end-use", "", ""),
    (r"^iron-and-steel\.product\.foundry$", ["other-industry/metal-melting-and-heat-treatment"],
     "end-use", "add", "the row covers foundry melting"),
    # cement and non-metallic minerals
    (r"^industrial-minerals\.product\.cement\.(.*clinker\.|clinker$)", ["cement/clinker-production"], "end-use", "", ""),
    (r"^industrial-minerals\.product\.cement\.", ["cement/cement-grinding-and-blending"], "end-use", "", ""),
    (r"^industrial-minerals\.product\.lime(\.|$)", ["non-metallic-minerals/lime-calcination"], "end-use", "", ""),
    (r"^industrial-minerals\.product\.glass\.(preparation|furnaces)$",
     ["non-metallic-minerals/glass-melting"], "end-use", "new end use", ""),
    (r"^industrial-minerals\.product\.glass\.form-and-finish$",
     ["non-metallic-minerals/glass-forming-and-finishing"], "end-use", "new end use", ""),
    (r"^industrial-minerals\.product\.(bricks|ceramics)\.kiln$", ["non-metallic-minerals/ceramic-firing"], "end-use",
     "new end use", ""),
    (r"^industrial-minerals\.product\.((bricks|ceramics)\.dryer|gypsum)$",
     ["non-metallic-minerals/drying-and-low-temp-calcining"], "end-use", "", ""),
    # chemicals
    (r"^chemicals\.product\..*(pyrolysis|steam-cracking)$", ["chemicals/steam-cracking"], "end-use", "", ""),
    (r"^chemicals\.product\.ammonia-methanol\.", ["chemicals/ammonia-and-methanol"], "end-use", "", ""),
    (r"^chemicals\.product\.(chlor-alkali|sodium-chlorate)\b", ["chemicals/electrochemical-products"], "end-use", "", ""),
    (r"^chemicals\.product\.(adipic|nitric)-acid\b", ["chemicals/nitric-and-adipic-acid"], "end-use",
     "new end use", "N2O process emissions"),
    (r"^chemicals\.product\.", ["chemicals/other-chemicals"], "end-use", "", ""),
    # biofuels and hydrogen
    (r"^ethanol\.product\.", ["biofuels/ethanol-production"], "end-use", "", ""),
    (r"^biodiesel\.product\.", ["biofuels/biodiesel-production"], "end-use", "", ""),
    (r"^hydrogen\.product\.", ["hydrogen/centralized-hydrogen-production"], "end-use",
     "id centralised -> centralized", ""),
    (r"^hydrogen\.service\.(infrastructure|distribution)$", ["hydrogen/hydrogen-distribution"], "end-use",
     "add (was none)", ""),
    # refining
    (r"^petroleum-refining\.product\..*distillation(\.|$)", ["petroleum-refining/crude-distillation"], "end-use", "", ""),
    (r"^petroleum-refining\.product\.", ["petroleum-refining/conversion-and-treating"], "end-use", "", ""),
    (r"^petroleum-refining\.service\.hydrogen$", ["petroleum-refining/refinery-hydrogen"], "end-use", "", ""),
    # pulp and paper
    (r"^pulp-and-paper\.product\..*(log-preparation\.|pulp\.wood-preparation$)", ["pulp-and-paper/wood-preparation"], "end-use",
     "new end use (was in chemical-pulping)", ""),
    (r"^pulp-and-paper\.product\..*(pulping-(chemical|semi-chemical)|washing\.washer|bleaching\.(fully|semi)|pulp\.(washing|bleaching))$",
     ["pulp-and-paper/chemical-pulping"], "end-use", "", ""),
    (r"^pulp-and-paper\.product\..*pulping-mechanical$", ["pulp-and-paper/mechanical-pulping"], "end-use",
     "new end use (split)", ""),
    (r"^pulp-and-paper\.product\..*pulping-recycled$", ["pulp-and-paper/recycled-pulping"], "end-use",
     "new end use (split)", ""),
    (r"^pulp-and-paper\.service\.(black-liquor|chemical-recovery)\..*lime-kiln$", ["pulp-and-paper/lime-kiln"], "end-use", "", ""),
    (r"^pulp-and-paper\.service\.(black-liquor|chemical-recovery)\.", ["pulp-and-paper/chemical-recovery"], "end-use", "", ""),
    (r"^pulp-and-paper\.service\.effluent-treatment$", ["pulp-and-paper/effluent-treatment"], "end-use", "", ""),
    (r"^pulp-and-paper\.product\.(paper\..*drying|pulp\.drying)$", ["pulp-and-paper/paper-drying"], "end-use", "", ""),
    (r"^pulp-and-paper\.product\.paper\.", ["pulp-and-paper/paper-forming"], "end-use", "", ""),
    # mining
    (r"^(mining|coal-mining)\.product\..*unassigned-energy$", [], "remove", "drop", "allocate, then remove"),
    # mining after the 2026-09-18 restructure: products are commodity x mine type and
    # the process steps are services, so the end uses map onto the services
    (r"^mining\.service\.(extraction|mine-haulage)(\.|$)",
     ["mining/extraction-and-haulage"], "end-use", "", ""),
    (r"^mining\.service\.(crushing|milling)$", ["mining/comminution"], "end-use", "", ""),
    (r"^mining\.service\.(separation|leaching|crystallization|compaction)$",
     ["mining/separation-and-processing"], "end-use", "", ""),
    (r"^mining\.service\.drying$", ["mining/product-drying"], "end-use", "", ""),
    (r"^mining\.service\.pelletizing$", ["mining/pelletizing"], "end-use", "", ""),
    (r"^mining\.service\.tailings-disposal$", ["mining/water-and-tailings-management"], "end-use", "", ""),
    (r"^mining\.product\.", ["mining/extraction-and-haulage"], "end-use", "",
     "the mine itself; its energy sits on the services it requests"),
    (r"^(mining|coal-mining)\.product\..*tailings?-disposal$", ["mining/water-and-tailings-management"],
     "end-use", "move from separation-and-processing", ""),
    (r"^mining\.product\..*(iron\.agglomeration|open-pit\.pelletizing)$", ["mining/pelletizing"], "end-use", "id pelletising -> pelletizing", ""),
    (r"^coal-mining\.product\.raw-product\.mine-ventilation$|^(mining|coal-mining)\.service\.ventilation$",
     ["mining/ventilation-and-air-heating"], "end-use", "", ""),
    (r"^(mining|coal-mining)\.service\.mine-haulage(\.|$)", ["mining/extraction-and-haulage"], "end-use", "", ""),
    (r"^coal-mining\.product\.coal-preparation\.washing$", ["mining/separation-and-processing"], "end-use", "",
     "wash mill, on electricity"),
    (r"^coal-mining\.product\.coal-preparation\.drying$", ["mining/product-drying"], "end-use", "",
     "rotary, spray and fluidized-bed dryers on gas, coal or electricity (the old metallurgical-finishing.cleaning node)"),
    (r"^(mining|coal-mining)\.product\..*(extraction|transportation|simplified-production|brine-transport)$",
     ["mining/extraction-and-haulage"], "end-use", "", ""),
    (r"^(mining|coal-mining)\.product\..*(crushing|milling|crush-and-screen)$", ["mining/comminution"], "end-use", "", ""),
    (r"^mining\.product\.potash\.drying$", ["mining/product-drying"], "end-use", "", ""),
    (r"^(mining|coal-mining)\.product\.", ["mining/separation-and-processing"], "end-use", "", ""),
    # oil and gas
    (r"^natural-gas\.product\.supply\.(controls|venting\.|testing-and-maintenance\.(blowdowns|liquid-unloading))",
     ["oil-and-gas/venting"], "end-use",
     "new end use (split from venting-and-flaring); drop controls, blowdowns and liquid unloading from production",
     "pumping: pneumatic vs electric, requested by processing and transmission"),
    (r"^natural-gas\.product\.supply\.flaring$", ["oil-and-gas/flaring"], "end-use",
     "new end use (split from venting-and-flaring)", ""),
    (r"^natural-gas\.product\.supply\.fugitive$", ["oil-and-gas/fugitive-emissions"], "end-use", "", ""),
    (r"^natural-gas\.product\.supply\.((extraction\.)?(drilling|well-tests)|testing-and-maintenance\.well-tests)$|^petroleum-crude\.product\.exploration$",
     ["oil-and-gas/drilling-and-well-services"], "end-use", "", ""),
    (r"^natural-gas\.product\.supply\.(extraction\.|gas-compression$)", ["oil-and-gas/oil-and-gas-production"], "end-use",
     "compressed-air: drop extraction compression", ""),
    (r"^petroleum-crude\.product\.(heavy|light-medium\.)", ["oil-and-gas/oil-and-gas-production"], "end-use", "", ""),
    (r"^petroleum-crude\.service\.(industrial-engines|direct-drive|field-engines)$",
     ["oil-and-gas/drilling-and-well-services", "oil-and-gas/oil-and-gas-production",
      "oil-and-gas/in-situ-bitumen", "oil-and-gas/bitumen-upgrading"], "end-use", "add (was unmapped)",
     "stationary engines (20-year life; requested per well, per m3 and by upgraders); "
     "the oil-sands mining request moves to service.mine-haulage"),
    (r"^petroleum-crude\.service\.mine-haulage$", ["oil-and-gas/oil-sands-mining-and-extraction"], "end-use",
     "add", "mine fleet; haul fleets stay in their sector"),
    (r"^petroleum-crude\.service\.produced-water$", ["oil-and-gas/produced-water-handling"], "end-use", "", ""),
    (r"^natural-gas\.(product\.supply|service)\.(direct-drive|compressor-drive)(\.(engine|turbine))?$",
     ["oil-and-gas/oil-and-gas-production", "oil-and-gas/gas-processing", "oil-and-gas/gas-pipelines"],
     "end-use", "add",
     "compressor drivers for extraction, processing and transmission compression; "
     "`.engine` is the reciprocating fleet (10-year life) and `.turbine` the "
     "centrifugal one (30-year life), each with an electric-motor alternative, and "
     "the three compression nodes request exogenous shares of the two"),
    (r"^natural-gas\.product\.supply\.processing(\.|$)", ["oil-and-gas/gas-processing"], "end-use", "", ""),
    (r"^natural-gas\.product\.supply\.lng-(compression|liquefaction)$", ["oil-and-gas/lng-liquefaction"], "end-use", "", ""),
    (r"^natural-gas\.product\.(transmission(\.|$)|distribution$)", ["oil-and-gas/gas-pipelines"], "end-use", "", ""),
    (r"^petroleum-crude\.product\.transmission$", ["oil-and-gas/oil-pipelines"], "end-use", "", ""),
    (r"^petroleum-crude\.product\.bitumen\.in-situ$", ["oil-and-gas/in-situ-bitumen"], "end-use", "", ""),
    (r"^petroleum-crude\.product\.bitumen\.mining$", ["oil-and-gas/oil-sands-mining-and-extraction"], "end-use", "", ""),
    (r"^petroleum-crude\.product\.bitumen\.upgrading$", ["oil-and-gas/bitumen-upgrading"], "end-use", "", ""),
    (r"^petroleum-crude\.service\.hydrogen$", ["oil-and-gas/upgrader-hydrogen"], "end-use", "", ""),
    # light industrial products
    (r"^light-industrial\.product\.food-tobacco-and-beverage$",
     ["food-and-beverage/thermal-processing", "food-and-beverage/baking-frying-and-roasting",
      "food-and-beverage/drying", "food-and-beverage/refrigeration"], "end-use", "", "aggregate only"),
    (r"^light-industrial\.product\.(transportation-equipment|furniture-printing-and-machinery)$",
     ["other-industry/metal-melting-and-heat-treatment"], "end-use", "", "product-to-process approximation"),
    (r"^light-industrial\.product\.(leather-and-textiles|rubber-and-plastics|electronics-and-other)$",
     ["other-industry/drying-curing-and-forming"], "end-use", "", "product-to-process approximation"),
    (r"^light-industrial\.product\.wood-products$", ["other-industry/wood-drying-and-pressing"], "end-use", "", ""),
    # non-ferrous
    (r"^metal-smelting\.product\.lead\.metallurgy\.hydro$", [], "remove", "drop",
     "no Canadian plant since 2000"),
    (r"^metal-smelting\.product\.zinc\.metallurgy\.pyro\.(process\.(continuous|conventional\.smelt)|refine)$",
     [], "remove", "drop", "no Canadian plant since 2000: zinc is roast-leach-electrowin"),
    (r"^metal-smelting\.product\.titanium\.metallurgy\.pyro\.refine$", [], "remove", "drop",
     "no Canadian titanium metal refining since 2000"),
    (r"^metal-smelting\.product\.aluminum\.primary-aluminum\.alumina$", ["non-ferrous-metals/alumina-refining"], "end-use", "", ""),
    (r"^metal-smelting\.product\.aluminum\.primary-aluminum\.electrolysis$", ["non-ferrous-metals/aluminum-smelting"],
     "end-use", "id aluminium -> aluminum", ""),
    (r"^metal-smelting\.service\.((pre-bake|soderberg)-anode|anode-production)$", ["non-ferrous-metals/anode-production"], "end-use", "", ""),
    (r"^metal-smelting\.service\.oxygen\b", ["non-ferrous-metals/smelter-oxygen-supply"], "end-use", "", ""),
    (r"^metal-smelting\.product\.magnesium\.(metallurgy\.pyro\.refine|electrolysis)$",
     ["non-ferrous-metals/hydrometallurgy"], "end-use",
     "hydrometallurgy: widen electrowinning to cover molten-salt electrolysis",
     "molten-salt MgCl2 cells (Magnola to 2003, Norsk Hydro Becancour to 2007); "
     "carries an SF6 cover-gas factor of 0.001565 t per unit"),
    (r"^metal-smelting\.product\.magnesium\.(metallurgy\.pyro\.process\..*|thermal-reduction)$",
     ["non-ferrous-metals/pyrometallurgy"], "end-use", "",
     "silicothermic retort (Timminco Haley, to about 2008)"),
    (r"^metal-smelting\.product\.[a-z-]+\.(metallurgy\.hydro|hydrometallurgy)$", ["non-ferrous-metals/hydrometallurgy"], "end-use",
     "", "titanium-slag keeps its leach: the roast-leach upgrade to UGS slag is real"),
    (r"^metal-smelting\.product\.(titanium|titanium-slag)\.(metallurgy\.pyro|pyrometallurgy)\.",
     ["non-ferrous-metals/electric-smelting"], "end-use", "",
     "Rio Tinto Fer et Titane, Sorel-Tracy: ilmenite smelted to titanium slag in "
     "electric furnaces, pig iron taken as a co-product carrying no energy of its own"),
    (r"^metal-smelting\.product\.[a-z-]+\.(metallurgy\.pyro|pyrometallurgy)\.", ["non-ferrous-metals/pyrometallurgy"], "end-use", "", ""),
    (r"^metal-smelting\.product\.(aluminum\.recycle|[a-z-]+\.melt-cast)$",
     ["non-ferrous-metals/melting-casting-and-fabrication"], "end-use", "",
     "magnesium melt-cast carries the SF6 cover-gas factor (0.0078 t per unit, five "
     "times the cell factor): the emission the NIR keeps reporting after 2007"),
]

# ---------------------------------------------------------------------------
# Suggested hierarchy paths: (regex, replacement), applied in order with re.sub to
# "<cims-sector>.<rest>". A replacement of "(remove)" drops the node.
# ---------------------------------------------------------------------------
S = [
    # general
    (r"\.machine-drive\.fans$", ".machine-drive.fans-and-blowers"),
    (r"^chemicals\.product\.(adipic-acid|hydrogen-peroxide|sodium-chlorate)\.process$", r"chemicals.product.\1"),
    (r"^iron-and-steel\.service\.iron-process-gas\..*$", "iron-and-steel.service.fuel-blend_process-gas"),
    (r"^petroleum-refining\.service\.still-gas\..*$", "petroleum-refining.service.fuel-blend_still-gas"),
    (r"^petroleum-crude\.service\.still-gas-steam$", "petroleum-crude.service.fuel-blend_still-gas"),
    # hydrogen
    (r"^hydrogen\.product\.process$", "hydrogen.product.centralized-hydrogen"),
    (r"^hydrogen\.service\.infrastructure$", "hydrogen.service.distribution"),
    # industrial minerals
    (r"^industrial-minerals\.product\.cement\.portland-cement\.clinker\..*$", "industrial-minerals.product.cement.clinker"),
    (r"^industrial-minerals\.product\.cement\.portland-cement\.(dry-ground-cement|finish-grinding)$",
     "industrial-minerals.product.cement.grinding"),
    (r"^industrial-minerals\.product\.lime\..*$", "industrial-minerals.product.lime"),
    (r"^industrial-minerals\.service\.heat$", "industrial-minerals.service.kiln-heat"),
    # iron and steel
    (r"^iron-and-steel\.product\.molten-steel\.integrated$",
     "iron-and-steel.product.molten-steel; iron-and-steel.service.hot-metal; iron-and-steel.service.direct-reduced-iron"),
    (r"^iron-and-steel\.product\.molten-steel\.recycled$", "iron-and-steel.product.molten-steel"),
    (r"^iron-and-steel\.product\.continuous-cast\.ladle-preheat$", "iron-and-steel.service.ladle-preheating"),
    (r"^iron-and-steel\.product\.continuous-cast\.ladle-refining$", "iron-and-steel.service.ladle-refining"),
    (r"^iron-and-steel\.service\.oxygen\.cryogenics$", "iron-and-steel.service.oxygen"),
    (r"^iron-and-steel\.service\.reheating\.reheators$", "iron-and-steel.service.reheating"),
    (r"^iron-and-steel\.product\.continuous-cast\..*(\.casting|billet-casting|bloom-casting)$",
     "iron-and-steel.product.continuous-cast.casting"),
    (r"^iron-and-steel\.product\.continuous-cast\..*(roughing-mills|finishing-mills|billets\.(bar|rod|light-structural-shapes)|blooms\.(heavy-structural-shapes|tubes))$",
     "iron-and-steel.product.continuous-cast.hot-rolling"),
    (r"^iron-and-steel\.product\.continuous-cast\..*(cold-roll|skin-pass|pickled-slabs|electrocleancomp)$",
     "iron-and-steel.product.continuous-cast.cold-rolling"),
    (r"^iron-and-steel\.product\.continuous-cast\..*(anneal-temper|electric-steel|tin-plate|galvanize)$",
     "iron-and-steel.product.continuous-cast.annealing-and-coating"),
    # chemicals
    (r"^chemicals\.product\.other-petrochemicals\.pyrolysis$", "chemicals.product.petrochemicals.steam-cracking"),
    (r"^chemicals\.product\.other-petrochemicals\.petrochemicals\.", "chemicals.product.petrochemicals."),
    (r"^chemicals\.product\.ammonia-methanol\.(ammonia|methanol)-synthesis$", r"chemicals.product.ammonia-methanol.\1"),
    (r"^chemicals\.product\.ammonia-methanol\.combined-ammonia-methanol-synthesis$",
     "(remove: allocate to ammonia and methanol by output)"),
    (r"^chemicals\.product\.chlor-alkali\.caustic-sodium\..*$", "chemicals.product.chlor-alkali.caustic-evaporation"),
    # refining
    (r"^(petroleum-refining\.product\.petroleum-fractions\.cracked-gas-oil\.hydrocracking)\..*$", r"\1"),
    (r"^(petroleum-refining\.product\.petroleum-fractions\.distillation)\..*$", r"\1"),
    (r"^petroleum-refining\.product\.alkylates\.isoparaffins\.isomerization$", "petroleum-refining.product.isomerization"),
    (r"^petroleum-refining\.product\.alkylates\.alkylation$", "petroleum-refining.product.alkylates"),
    # pulp and paper
    (r"^pulp-and-paper\.product\.pulp\.bleached\.washing\.raw\.log-preparation\..*$", "pulp-and-paper.product.pulp.wood-preparation"),
    (r"^pulp-and-paper\.product\.pulp\.bleached\.washing\.raw\.(pulping-[a-z-]+)$", r"pulp-and-paper.product.pulp.\1"),
    (r"^pulp-and-paper\.product\.pulp\.bleached\.washing\.washer$", "pulp-and-paper.product.pulp.washing"),
    (r"^pulp-and-paper\.product\.pulp\.bleached\.bleaching\..*$", "pulp-and-paper.product.pulp.bleaching"),
    (r"^(pulp-and-paper\.product\.paper\.[a-z]+)\.[a-z]+-(stock-prep|forming-pressing-finishing|prep-form-press-finish)$",
     r"\1.forming"),
    (r"^(pulp-and-paper\.product\.paper\.[a-z]+)\.[a-z]+-drying$", r"\1.drying"),
    (r"^pulp-and-paper\.service\.black-liquor\.concentrated-black-liquor\.", "pulp-and-paper.service.chemical-recovery."),
    (r"^pulp-and-paper\.service\.black-liquor\.", "pulp-and-paper.service.chemical-recovery."),
    # mining
    (r"^.*unassigned-energy$", "(remove)"),
    (r"^mining\.product\.metal\.open-pit\..*\.transportation$", "mining.service.mine-haulage.open-pit"),
    # the 2026-09-18 restructure: old mining product steps -> process services
    (r"^mining\.product\..*\.(crushing|crush-and-screen)$", "mining.service.crushing"),
    (r"^mining\.product\..*\.milling$", "mining.service.milling"),
    (r"^mining\.product\..*\.(mineral-separation|cleaning|flotation)$", "mining.service.separation"),
    (r"^mining\.product\..*\.(crystallization|compaction)$", r"mining.service.\1"),
    (r"^mining\.product\..*\.dissolution$", "mining.service.crystallization"),
    (r"^mining\.(product|service)\..*brine-transport$", "(remove: the solution product node requests the shared pump service)"),
    (r"^(chemicals|coal-mining|industrial-minerals|iron-and-steel|metal-smelting|mining|pulp-and-paper)\.service\.direct-drive$",
     "(remove: an efficiency variant of the motor technologies)"),
    (r"^mining\.product\..*\.tailings?-disposal$", "mining.service.tailings-disposal"),
    (r"^mining\.product\.potash\.drying$", "mining.service.drying"),
    (r"^mining\.product\..*\.(extraction)$", "mining.service.extraction"),
    (r"^mining\.product\.(metal\.underground|potash\..*conventional-mining)\..*transportation$",
     "mining.service.mine-haulage.underground"),
    (r"^(mining\.product\.potash\..*solution-mining)\.transportation$", r"\1.brine-transport"),
    (r"^coal-mining\.product\.raw-product\.transportation$", "coal-mining.service.mine-haulage"),
    (r"^(mining\.product\.metal\.open-pit)\.(iron|non-iron)\.(primary|secondary)-crushing$", r"\1.crushing"),
    (r"^(mining\.product\.metal\.open-pit)\.non-iron\.primary-milling$", r"\1.milling"),
    (r"^(mining\.product\.metal\.open-pit)\.(iron|non-iron)\.raw-product\.", r"\1."),
    (r"^(mining\.product\.metal\.open-pit)\.iron\.agglomeration$", r"\1.pelletizing"),
    (r"^(mining\.product\.metal\.underground)\.processing\.(primary|secondary)-crushing$", r"\1.crushing"),
    (r"^(mining\.product\.metal\.underground)\.processing\.primary-milling$", r"\1.milling"),
    (r"^(mining\.product\.metal\.underground)\.processing\.raw-product\.", r"\1."),
    (r"tailing-disposal$", "tailings-disposal"),
    (r"crystalization$", "crystallization"),
    (r"^(coal-mining\.product\.size-reduced-product)\.primary-crushing$", r"\1.crushing"),
    (r"^(coal-mining\.product\.size-reduced-product)\.(primary|secondary)-milling$", r"\1.milling"),
    (r"^coal-mining\.product\.metallurgical-finishing\.cleaning$", "coal-mining.product.coal-preparation.drying"),
    (r"^coal-mining\.product\.metallurgical-finishing\.washing$", "coal-mining.product.coal-preparation.washing"),
    (r"^coal-mining\.product\.metallurgical-finishing\.tailings-disposal$", "coal-mining.product.coal-preparation.tailings-disposal"),
    # the fan technologies are the shared machine-drive fan service, so the coal
    # mine-air duty stays a product step and no sector ventilation service is added

    # natural gas
    (r"^industrial-minerals\.product\.glass\.preparation$", "(remove: folded into glass.furnaces)"),
    (r"^industrial-minerals\.product\.bricks(\.|$)", r"industrial-minerals.product.ceramics\1"),
    (r"^natural-gas\.product\.supply\.controls$", "natural-gas.product.supply.venting.controls"),
    (r"^natural-gas\.product\.supply\.extraction\.compression$", "natural-gas.product.supply.gas-compression"),
    (r"^natural-gas\.product\.supply\.(extraction\.)?(drilling|off-road-transport)$", r"natural-gas.product.supply.\2"),
    (r"^natural-gas\.product\.supply\.venting\.(point|diffuse)-venting$", r"natural-gas.product.supply.venting.other-\1-venting"),
    (r"^natural-gas\.product\.supply\.testing-and-maintenance\.(blowdowns|liquid-unloading)$",
     r"natural-gas.product.supply.venting.\1"),
    (r"^natural-gas\.product\.supply\.(extraction\.)?(testing-and-maintenance\.)?well-tests$", "natural-gas.product.supply.well-tests"),
    (r"^natural-gas\.(product\.supply|service)\.direct-drive$", "natural-gas.service.compressor-drive"),
    (r"^natural-gas\.product\.supply\.direct-drive-(small|large)$", "natural-gas.service.compressor-drive.{engine, turbine}"),
    (r"^(chemicals|iron-and-steel|petroleum-refining|petroleum-crude)\.service\.ccs$",
     r"\1.service.ccs.concentrated; \1.service.ccs.diffuse"),
    (r"^natural-gas\.(product\.supply|service)\.ccs$",
     "natural-gas.service.ccs.concentrated; natural-gas.service.ccs.diffuse"),
    (r"^hydrogen\.service\.ccs$", "hydrogen.service.ccs.concentrated"),
    (r"^(industrial-minerals|ethanol|biodiesel)\.service\.ccs$", r"\1.service.ccs.diffuse"),
    (r"^natural-gas\.(product\.supply|service)\.pumping$", "natural-gas.service.machine-drive.pumps"),
    (r"^light-industrial\.service\.machine-drive\..+$", "(remove: CIMS light industry has one motive-power service)"),
    (r"^petroleum-refining\.service\.machine-drive\.materials-handling$", "(remove: no conveyance service in the model)"),
    (r"^natural-gas\.product\.supply\.lng-compression$", "natural-gas.product.supply.lng-liquefaction"),
    (r"^natural-gas\.product\.supply\.processing\.compression$", "natural-gas.product.supply.processing"),
    (r"^natural-gas\.product\.transmission\.compression$", "natural-gas.product.transmission"),
    # petroleum crude
    (r"^petroleum-crude\.service\.(industrial-engines|direct-drive)$", "petroleum-crude.service.field-engines"),
    # metal smelting: prune routes with no Canadian plant
    (r"^metal-smelting\.product\.lead\.metallurgy\.hydro$", "(remove: no Canadian plant since 2000)"),
    (r"^metal-smelting\.product\.zinc\.metallurgy\.pyro\.(process\.(continuous|conventional\.smelt)|refine)$",
     "(remove: no Canadian plant since 2000)"),
    (r"^metal-smelting\.product\.titanium\.metallurgy\.pyro\.refine$", "(remove: no Canadian plant since 2000)"),
    # metal smelting
    (r"^metal-smelting\.service\.(pre-bake|soderberg)-anode$", "metal-smelting.service.anode-production"),
    (r"^metal-smelting\.service\.oxygen\.cryogenics$", "metal-smelting.service.oxygen"),
    (r"^metal-smelting\.product\.titanium(\.|$)", r"metal-smelting.product.titanium-slag\1"),
    (r"^metal-smelting\.product\.magnesium\.metallurgy\.hydro$", "(remove: magnesium is not leached)"),
    (r"^metal-smelting\.product\.magnesium\.metallurgy\.pyro\.process\.conventional\.roast$",
     "(remove: magnesium is not roasted)"),
    (r"^metal-smelting\.product\.magnesium\.metallurgy\.pyro\.refine$", "metal-smelting.product.magnesium.electrolysis"),
    (r"^metal-smelting\.product\.magnesium\.metallurgy\.pyro\.process\.", "metal-smelting.product.magnesium.thermal-reduction"),
    (r"^(metal-smelting\.product\.[a-z-]+)\.metallurgy\.hydro$", r"\1.hydrometallurgy"),
    (r"^(metal-smelting\.product\.[a-z-]+)\.metallurgy\.pyro\.process\.(continuous|conventional\.(smelt|convert))$",
     r"\1.pyrometallurgy.smelting"),
    (r"^(metal-smelting\.product\.[a-z-]+)\.metallurgy\.pyro\.process\.conventional\.roast$", r"\1.pyrometallurgy.roasting"),
    (r"^(metal-smelting\.product\.[a-z-]+)\.metallurgy\.pyro\.refine$", r"\1.pyrometallurgy.refining"),
    # ethanol
    (r"^ethanol\.product\.(corn|cellulosic)$", "ethanol.product.fermentation"),
    # light industrial
    (r"^light-industrial\.service\.(heat\.indirect|water-heating)$", "light-industrial.service.steam"),
    (r"^light-industrial\.service\.heat\.direct$", "light-industrial.service.heat"),
    (r"^light-industrial\.service\.hvac$", "light-industrial.service.hvac.space-heating; light-industrial.service.hvac.space-cooling"),
]

# Nodes the proposal adds to the hierarchy (section 4 of the proposal)
NEW = [
    "iron-and-steel.service.coke",
    "iron-and-steel.service.hot-metal",
    "iron-and-steel.service.direct-reduced-iron",
    "industrial-minerals.product.ceramics.dryer",
    "industrial-minerals.product.gypsum",
    "chemicals.product.nitric-acid",
    "direct-air-capture.product.co2-removal",
    "mining.service.on-site-power",
    "petroleum-crude.product.transmission",
    "petroleum-crude.service.produced-water",
    "petroleum-crude.service.mine-haulage",
    "pulp-and-paper.service.effluent-treatment",
]

R = [(re.compile(p), t, role, ch, n) for p, t, role, ch, n in R]
S = [(re.compile(p), r) for p, r in S]


def leaves(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        br = [r["branch"] for r in csv.DictReader(f)]
    s = set(br)
    return [b for b in br if not any(o.startswith(b + ".") for o in s)]


def classify(rest):
    for rx, t, role, ch, n in R:
        if rx.search(rest):
            return t, role, ch, n
    return None


def suggest(rest):
    new = rest
    for rx, rep in S:
        if rx.search(new):
            new = rx.sub(rep, new)
            if new.startswith("(remove"):
                return new
    return "" if new == rest else new


def row(branch, rest, status):
    t, role, ch, n = classify(rest)
    share = "" if not t else ("whole" if len(t) == 1 else "part")
    return [branch, status, "; ".join(t), share, role, suggest(rest), ch, n]


def main():
    rows, unmapped, out_of_scope = [], [], 0
    present = set()
    for b in leaves(HIER):
        parts = b.split(".", 1)
        if len(parts) < 2:
            continue
        rest = parts[1]
        present.add(rest)
        if rest.split(".")[0] not in IN_SCOPE:
            out_of_scope += 1
            continue
        if classify(rest) is None:
            unmapped.append(rest)
            continue
        rows.append(row(b, rest, "existing"))
    for rest in NEW:
        if rest in present:
            continue
        if classify(rest) is None:
            unmapped.append(rest + " (proposed)")
            continue
        rows.append(row("<sector>." + rest, rest, "proposed-new"))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    table = ROOT / "design/sector-end-use-table.csv"
    with open(table, encoding="utf-8", newline="") as f:
        ids = {f"{r['sector']}/{r['end-use']}" for r in csv.DictReader(f)}
    stray = sorted({x for r in rows for x in r[2].split("; ") if x and x not in ids})
    if stray:
        print("  END USES NOT IN THE TABLE:", ", ".join(stray))
        return 1
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["branch", "status", "end-use", "share", "role", "suggested-branch", "table-change", "note"])
        w.writerows(rows)
    ex = [r for r in rows if r[1] == "existing"]
    used = {x for r in rows for x in r[2].split("; ") if x}
    print(f"{len(ex)} in-scope leaves mapped, {len(rows) - len(ex)} proposed new nodes, "
          f"{len(unmapped)} unmapped, {out_of_scope} out of scope; {len(used)} end uses receive a CIMS node")
    for u in unmapped:
        print("  UNMAPPED", u)
    return 1 if unmapped else 0


if __name__ == "__main__":
    sys.exit(main())
