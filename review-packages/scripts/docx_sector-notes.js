const { lead, p, h1, h2, bullets, table, gap, doc, save } = require("./docx_lib");
const F = require("./sector-facts.json");
const OUTDIR = process.argv[2];

const famLabel = { "heat-supply": "heat supply", "power-generation": "on-site power", "machine-drive": "machine drive",
  "space-conditioning": "space conditioning", "lighting": "lighting", "mobile-equipment": "mobile equipment", "co2-capture": "CO2 capture" };

// Hand-written content per sector: scope, judgement calls, and gaps.
const S = {
  steel: {
    title: "Iron and steel",
    nodes: "every node under `iron-and-steel`: agglomeration, cokemaking, hot metal, direct-reduced iron, oxygen, molten steel, ladle preheating and refining, reheating, casting, hot and cold rolling, pickling, annealing and coating, and foundry",
    calls: [
      ["Merged", [
        "Fines-based direct reduction (Circored, Finmet) is pooled into `shaft-furnace_direct-reduction`. It skips pelletizing, which CIMS sees on the agglomeration node. Should it stand apart?",
        "Membrane air separation (low-purity oxygen) is pooled into `air-separation-unit`.",
        "Fermentation of steel off-gas is pooled into `reactor_steel-offgas-chemicals`, so steel off-gas use is held once.",
        "The foundry electric arc furnace is pooled into `electric-arc-furnace`. Foundry heats are smaller and tap hotter, but the energy gap measured under 15%.",
        "Coupled pickling and cold rolling are pooled into `rolling-mill_cold`, which also absorbs the separate pickling line on that node.",
      ]],
      ["Kept apart", [
        "Induction heating for heat treatment and for reheating (lower temperatures for hardening and annealing).",
        "Moderate and strong efficiency buckets on the blast furnace, BOF, coke oven, sinter plant, reheating furnace, and hot mill. Sources give 10–30% savings for recuperative or regenerative burners. Pooling across furnace ages may hide the difference between the reheating buckets.",
      ]],
      ["Framing", [
        "`shaft-furnace_electrolytic-hydrogen` is a whole plant (hydrogen DRI plus EAF), an alternative to the unit archetypes. Some of its sourced route costs include a return or the electrolyser; whole-route production costs from Material Economics 2019 and Draxler 2021 were ruled out.",
        "Ironmaking has two product sub-bands: iron (t), for blast furnaces and smelting reduction, and reduced iron (t), for DRI. Check that each archetype sits on the right one.",
        "Energy use is gross input. Recovered BOF gas, coke-oven gas, and steam are output flows, not credits; net figures from sources were grossed up or excluded.",
        "The capture variants (blast furnace, smelting reduction, and DRI with capture) take their host's size and costs, plus a capture add-on.",
      ]],
      ["Scope and accounting", [
        "Rolling-mill energy pools rows covering the mill plus its reheat furnace or annealing; off-scope rows were ruled out. Check that what remains is the mill alone.",
        "The heat-recovery coke oven burns its volatiles, while the by-product oven exports gas, so the two count energy differently.",
      ]],
    ],
    gaps: [
      "No sourced examples: `induction-heater_strip-heating` and `rolling-mill_cold_efficiency-moderate`; every value is filled.",
      "One or two examples: `melting-furnace_isothermal`, `melting-furnace_crucible-gas-fired`, `annealing-furnace_hydrogen-bell`, and `pellet-plant_plasma-electric`.",
      "Low-readiness routes with mainly guessed costs: molten oxide electrolysis, low-temperature electrowinning (readiness level 5), and electric smelting of DRI.",
    ],
  },
  cement: {
    title: "Cement",
    nodes: "the cement nodes under `industrial-minerals.product.cement` (clinker, grinding, binder, calcined clay, and ground slag) and the industrial-minerals service nodes (kiln heat, capture, machine drive, heating and cooling, and lighting)",
    calls: [
      ["Binders are recipes", [
        "Since 27 October 2026 the binder archetypes (Portland, blended, calcined clay or LC3, alkali-activated, sulphoaluminate, carbonated, hydrothermal, and electrochemical) are recipes. Each requests clinker, grinding, and supplementary materials from the nodes that make them, rather than carrying their energy itself. New nodes for calcined clay and ground slag were added to the CIMS hierarchy for this. Check that the binder values hold only the blending step, and that each recipe's ratios are sound.",
      ]],
      ["Merged", [
        "The fluidized-bed kiln (a niche demonstration) and flash or fluid calciners (part of a precalciner line) are pooled into `kiln_dry-precalciner`.",
        "High-pressure grinding rolls are pooled into `grinding-mill_vertical-roller` for cement.",
        "`kiln_legacy` holds wet, semi-dry, and long dry kilns together. Is one legacy archetype enough for Canadian stock?",
      ]],
      ["Capture and electrification", [
        "Oxy-fuel and calcium-looping kilns keep their own archetypes, since they concentrate their own CO2 stream. Post-combustion capture is the variant `kiln_dry-precalciner_ccs-diffuse`, which takes the host kiln's size and costs plus a capture add-on. On a capture variant, total emissions are net.",
        "Electrified routes are `calciner_indirect` (readiness level 6) and `kiln_electric-plasma` (readiness level 4–5, two examples).",
      ]],
      ["Bases", [
        "Clinker and cement are separate products. Where a source printed a value per tonne of cement that is really per tonne of clinker, the database takes it on an assumed correction, listed in `source-corrections`. Check the clinker-to-cement basis of the kiln rows.",
        "The kiln efficiency buckets come partly from UKERC savings applied to the base kiln's pooled energy use.",
      ]],
    ],
    gaps: [
      "No sourced examples: `kiln_calcium-silicate-feed` and `grinding-mill_slag`.",
      "One example: `binder_electrochemical`. Most binder archetypes have guessed capital and operating costs (eight guessed cells each).",
      "Two examples: `kiln_electric-plasma`.",
    ],
    extra: [h2("Lime: an optional add-on"),
      p("This review covers cement nodes only. Lime and dolime calcination sits on its own node (`industrial-minerals.product.lime`), with five archetypes: long rotary, rotary with preheater (and its capture variant), shaft, and oxy-fuel kilns, plus the indirect calciner, which also serves the clinker node. The kiln-heat service node is shared by cement and lime. If you also know lime kilns and are willing to review them, tell us and we will send the lime kilns in the same format.")],
  },
  "pulp-and-paper": {
    title: "Pulp and paper",
    nodes: "every node under `pulp-and-paper`: wood preparation, chemical, mechanical, semi-chemical, and recycled pulping, bleaching, pulp drying, forming and drying for each paper grade (coated, uncoated, newsprint, linerboard, and tissue), chemical recovery (evaporator, recovery furnace, and lime kiln), effluent treatment, and steam",
    calls: [
      ["Units", [
        "Pulp is counted in air-dry tonnes (90% dry); figures per oven-dry tonne are converted per example. Recovery boilers and evaporators are per tonne of black liquor solids, converted from per-ADt figures with each source's own solids ratio. The lime kiln is per tonne of lime.",
        "Biogenic CO2 from black liquor (about 1.1 t per t of solids) and from kraft lime-kiln calcination (about 0.58 t per t) is held as biogenic, with fossil CO2 at zero.",
      ]],
      ["Paper grades", [
        "Each paper grade has its own forming and drying nodes, but one set of paper-machine and dryer archetypes serves all grades. Do grade differences (tissue against newsprint, for example) need separate values?",
        "`dryer_market-pulp` stays separate from the paper dryer, on the pulp drying node.",
      ]],
      ["Merged", [
        "Dryer hood heat recovery is in the moderate dryer efficiency bucket.",
        "Mechanical vapour recompression for black liquor and for caustic evaporation is one archetype, shared with chemicals.",
        "The gas-fired Yankee hood is pooled into `dryer_direct-fired`. On the tissue node a hood works with the steam cylinder, so it may complement rather than replace it.",
      ]],
      ["Kept apart", [
        "Stone groundwood and thermomechanical pulping stay separate: groundwood is a legacy type in Canadian stock, and TMP recovers refiner heat.",
      ]],
      ["Scope", [
        "Groundwood pulping uses no steam, following NRCan's 2008 survey of 49 Canadian mills; the U.S. area allocations in Jacobs 2006 and Kramer 2009 were ruled out.",
        "Steam-heated dryer energy pools sources with different section boundaries; check that values cover the dryer section only.",
      ]],
    ],
    gaps: [
      "No sourced examples: activated-sludge aeration (base and moderate) and clarification; every value is filled.",
      "Two examples: `dryer_heat-pump`, `dryer_through-air`, and `kiln_lime-electric`.",
      "Deep eutectic solvent pulping and waterless forming are at readiness level 4.",
      "Anaerobic effluent treatment has seven examples, several from food and brewery sources; check that it suits mill effluent.",
    ],
  },
  chemicals: {
    title: "Chemicals",
    nodes: "every node under `chemicals`: ammonia, methanol, urea, other fertilizers, nitric and adipic acid, N2O abatement, chlor-alkali (chlorine electrolysis and caustic evaporation), sodium chlorate, hydrogen peroxide, petrochemicals (olefins, aromatics, olefin derivatives, and polymers), and distillation",
    calls: [
      ["Merged", [
        "Heat-pumped distillation and vapour-recompression distillation are one archetype, `distillation-column_heat-pumped`.",
        "Rotodynamic (turbo) cracking is pooled into `steam-cracker_electric`; the two differ by about the 15% threshold once on the same basis.",
        "Low-pressure Haber-Bosch loops for variable hydrogen are pooled into `reactor_haber-bosch-electrolytic`.",
        "Total-recycle urea is pooled into `reactor_urea-synthesis`; a claimed 5.5 GJ/t against 3.1–3.8 GJ/t does not show in the pooled totals.",
      ]],
      ["Framing", [
        "The fossil and biomass ammonia and methanol routes are whole plants (reforming or gasification plus synthesis). Electrolytic Haber-Bosch is the synthesis loop alone, buying hydrogen. Check that the two framings compete fairly and do not double count with the hydrogen sector's reformers.",
        "Feedstock whose energy ends up in the product is recorded as `feedstock-consumption`, not as energy use, for crackers, reformers, and gasifiers. Check that the energy columns hold process energy only.",
        "The petrochemical nodes (olefins, aromatics, derivatives, and polymers) were chosen to suit Canada. One polymerization and extrusion archetype covers all polymers, from 128 examples. Is one enough?",
        "Each N2O abatement node has a zero-cost, zero-energy no-abatement option, set entirely by judgement.",
      ]],
      ["Products and units", [
        "Chlor-alkali cells are per tonne of chlorine; caustic evaporation is per tonne of water evaporated, on its own sub-node.",
        "Mercury and diaphragm cells remain as legacy types. Are they still in Canadian stock?",
      ]],
      ["Energy scope", [
        "For several archetypes the sourced total and its carrier split come from sources with different scopes, notably `gasifier_coal-methanol` and `gasifier_biomass-ethylene`. Check which scope the total holds.",
      ]],
    ],
    gaps: [
      "One example: `electrolysis-cell_sodium-chlorate` (nine guessed cells) and `gasifier_coal-methanol_ccs-concentrated`.",
      "Two or three examples: autothermal ammonia (with and without capture), biomass gasification to ammonia, hydrogen peroxide, and thermal N2O destruction.",
      "Capture on the cracker furnace flue gas is at readiness level 3–4.",
    ],
  },
  breweries: {
    title: "Breweries",
    nodes: "the light-industry service nodes that brewing draws on: steam, process heating (cooking, pasteurizing, and sterilizing), cleaning, refrigeration, machine drive, heating and cooling, and lighting. Light-industry drying, metal melting, heat treatment, and forming and pressing are left out",
    calls: [
      ["No brewery node", [
        "CIMS has no brewery node. Breweries are part of light industry's food, tobacco, and beverage product, and light industry's service nodes are shared by every light industry. So the values on these archetypes pool brewery data with dairy, juice, canning, and other food sources. Do brewery values differ enough to need their own archetypes?",
        "The ovens (baking, frying, and roasting) appear because they serve the same light-industry heat nodes; they are not brewery equipment, and you can skip them.",
      ]],
      ["How brewery data enters", [
        "`heat-exchanger_steam-heated` (kettles, retorts, and plate heat exchangers) is measured per tonne of product. Brewery figures per barrel or hectolitre are converted with a wort-and-beer density of 1.03 t/m3 (range 1.01–1.05). This covers the Galitsky 2003 mash and wort-kettle rows, the Giner-Santonja 2019 brewhouse rows, and, from this build, the DOE 2017 bandwidth study's current-typical brewhouse figure (0.585 GJ/t).",
        "Galitsky prints brewhouse heat as boiler fuel. The archetype carries steam, so those rows are converted at Galitsky's own 85% boiler efficiency.",
        "Regenerative pasteurizers are in the strong efficiency bucket of the steam-heated archetype, not a separate archetype.",
        "Keg washing is on `cleaning-system`.",
      ]],
      ["Brewery examples set aside", [
        "DOE 2017 state-of-the-art brewhouse: only 5% below current typical, and the archetype has no moderate efficiency variant.",
        "DOE 2017 space heating, refrigeration, lighting, compressed air, and boiler rows: per barrel of beer, with no way to turn them into GJ of heat or cooling, lumen-hours, or shaft work. DOE's packaging, utilities, and other rows cover whole lines with no matching archetype, and its practical-minimum tier is R&D.",
        "Giner-Santonja 2019 bottling: combines bottle washing with tunnel pasteurizing.",
        "Whole-site brewery benchmarks (Giner-Santonja 2019 and Galitsky's average U.S. brewery) are kept as calibration data only, since no whole-plant food archetype exists.",
        "Galitsky's fermentation CO2, microfiltration, and dealcoholisation rows: no matching archetype or node.",
      ]],
      ["Refrigeration", [
        "`chiller_vapour-compression` is process refrigeration (product cooling, 60% capacity factor); space cooling moved to its own `chiller_hvac` archetype. `chiller_high-efficiency` still prices from commercial air-conditioning equipment.",
      ]],
    ],
    gaps: [
      "No archetype for brewery-specific options: wort boiling systems, fermentation, CO2 recovery, packaging lines, or malt kilning.",
      "Brewery effluent: anaerobic treatment with biogas recovery is in the database, but only on the pulp-and-paper effluent node, so it is not included here.",
      "One example: `chiller_high-efficiency` and `press_high-pressure-processing`.",
    ],
  },
};

const status = (r) => r.status === "estimated" ? "filled only" : "sourced";
for (const [key, s] of Object.entries(S)) {
  const adj = key === "breweries" ? "brewery" : s.title.toLowerCase();
  const f = F[key];
  const crossTxt = Object.entries(f.cross_families).map(([k, v]) => `${famLabel[k] || k} (${v})`).join(", ");
  const tbl = table([2000, 2900, 2560, 1100, 800], ["End use (band)", "Archetype", "Label", "Examples", "Readiness level"],
    f.table.map((r, i) => [i && f.table[i - 1].band === r.band ? "" : r.band, "`" + r.archetype + "`",
      r.label + (r.status === "estimated" ? " (filled only)" : ""), r.n, r.trl]));
  const src = table([2500, 5760, 1100], ["Source", "Citation", "Examples"],
    f.top.map((t) => [t.short, t.citation, t.n]));
  const body = [
    p(`This note is for the ${adj} reviewer. It lists the sector's archetypes, the sources behind them, and the judgement calls we most want a sector expert to test. Read it with the methodology summary and the database file.`),
    h1("1. What this review covers"),
    p(`The database file holds the rows that serve ${s.nodes}.`),
    p(`It has ${f.rows} rows for ${f.archetypes} archetypes: **${f.own} ${adj} archetypes** and ${f.cross} cross-cutting archetypes that serve the same nodes, by family: ${crossTxt}. The cross-cutting rows stay in their own families. Comment on whether they fit the sector; a detailed check of their values is optional.`),
    h1(`2. The ${adj} archetypes`),
    lead(`"Examples" counts the source examples behind each archetype. An archetype marked "filled only" has no sourced values; every value comes from the fill rules.`),
    tbl,
    h1("3. Main sources"),
    lead(`${f.n_sources} sources supply the ${f.n_examples} examples behind the ${adj} archetypes. The ten that supply the most:`),
    src,
    gap(),
    h1("4. Judgement calls to test"),
    p("These are the choices most likely to need a sector expert's view. Tell us where you would decide differently, and why."),
    ...s.calls.flatMap(([head, items]) => [h2(head), ...bullets(items)]),
    h1("5. Known gaps"),
    ...bullets(s.gaps),
    p("Tell us about missing technologies, or better sources for thin archetypes, in the reviewer-comment column or in your covering note."),
    ...(s.extra || []),
  ];
  save(doc(`Sector note: ${s.title}`, `Technology database review package  |  build of 3 November 2026`, `Sector note: ${s.title}`, body),
    `${OUTDIR}/review-package_${key}/sector-note_${key}.docx`);
}
