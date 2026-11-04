const { lead, p, h1, h2, bullets, numbered, table, gap, doc, save } = require("./docx_lib");
const F = require("./sector-facts.json")._totals;

const OUT = process.argv[2];
const body = [
  p(`This summary explains how the technology database is built and how to read it. The full rules are in the repository's \`database/docs/\` folder: \`design.md\` (the rules), \`pipeline.md\` (the build), \`decisions.md\` (one line per decision, with its date), and \`vocabulary.md\` (every archetype, family, and term). Where this summary and those files differ, the files govern.`),

  h1("1. What the database is"),
  p(`The database describes the industrial technologies that can provide each industrial end use in the CIMS energy-economy model, summarised from published sources. It covers heat supply at every temperature, the process equipment that transforms materials, machine drive, refrigeration, space conditioning, lighting, on-site power, mobile equipment at industrial sites, CO2 capture, methane controls, and water and effluent handling. It holds existing stock and future options, generally from technology readiness level (TRL) 5–6 upward. A legacy type stays in while it remains in Canadian stock.`),
  p(`It counts **Scope 1 only**: purchased electricity is an energy input, priced by the model, not by the database. Residential, commercial, and transport end uses, heat distribution and steam traps, downstream fabrication, and non-GHG pollutants are out of scope.`),
  lead(`This build holds ${F.archetypes} archetypes (${F.status.quantified} with values pooled from sources, ${F.status.estimated} with filled values only), drawn from ${F.mapped.toLocaleString("en-CA")} source examples. The database has three layers:`),
  table([2000, 4000, 3360], ["Layer", "What it holds", "Rule"], [
    ["1. Extractions", "Each source as reported: one long table per source, in the source's own units, currency, and names.", "Never edited to fit the database. Only printed values, or values derived from printed values alone."],
    ["2. Examples", "One row per technology as a source presents it, mapped to the archetype it is an example of, with its facts converted to that archetype's basis.", "Every example belongs to one archetype or is marked (none), with the reason."],
    ["3. Archetypes", "One summarised value set per archetype and parameter, and the CIMS nodes each archetype serves.", "Rebuilt from layers 1 and 2 on every build."],
  ]),
  gap(),
  p(`A single build script rebuilds the whole database from the extractions and the hand-edited records, and stops on any broken rule. The wide view and the workbook are generated views: anything typed into them is lost on the next build. Your comments therefore go back to us, and we change the records.`),

  h1("2. Archetypes and examples"),
  p(`An **archetype** is a technology option the model chooses between, such as a fuel-fired boiler, a dry precalciner kiln, or a blast furnace with top-gas recycling. An **example** is one technology as one source presents it. The database summarises what the examples say about each archetype; it does not reproduce every source's detail.`),
  h2("When a technology gets its own archetype"),
  p(`A technology becomes a new archetype only if it meets one of three tests:`),
  bullets([
    "its energy use differs by roughly 15% or more from its nearest archetype;",
    "its emissions differ in kind, or in how they are abated;",
    "it is a legacy type still in Canadian stock.",
  ]),
  p(`Otherwise it is an example of an existing archetype. Size classes, vintages, regions, vendor designs, and product names are never archetypes. Earlier review rounds merged many near-duplicates on this test; each sector note lists the merges a sector expert should check.`),
  h2("Carriers, efficiency, and capture"),
  bullets([
    "**Carriers** are a list on the archetype, not separate archetypes. The exception is a carrier that changes the equipment itself (a solid-fuel boiler, an electrode boiler, a heat pump). Differences between carriers on one archetype show up as the range of its values.",
    "**Efficiency measures** on one device go into two buckets: `efficiency-moderate` (up to about 15% saving) and `efficiency-strong` (more). An option a model would choose in its own right, such as a condensing boiler, a shoe press, or a variable-speed drive, is its own archetype rather than a bucket.",
    "**Capture variants** (`ccs-concentrated`, `ccs-diffuse`) are the host plant with capture. Each takes its host's size (annual output, capacity, and capacity factor), and its costs, energy use, and emissions are the host's plus a capture add-on. The add-on comes from the same source where possible; otherwise it is the median cost of the matching capture plants per tonne of CO2, times the CO2 captured per unit of product. In CIMS the variant differs from its host by a service request to the capture node. The capture plant itself is a separate `capture-unit` archetype.",
    "Routes that concentrate their own CO2 stream keep their own archetype: oxy-fuel kilns, top-gas recycling, and bath smelting.",
  ]),
  h2("Values stand alone"),
  p(`Every archetype carries absolute values, never a difference from a baseline. A source's cost for adding a measure to an existing plant is incremental. It pools only as a whole-plant cost: the same source's host-plant cost plus the measure's. An incremental cost with no host cost from the same source is set aside. **Whole-plant archetypes** (a whole mine, refinery, or integrated route) are alternatives to the unit archetypes inside them: a model uses one framing or the other, never both.`),
  p(`Some archetypes serve no CIMS node: **components** priced only to build whole-plant costs, **reference** archetypes for steps the hierarchy does not resolve, and routes the hierarchy leaves out. They stay in the database with \`applies-to\` reading "no connection" They are not tied to any sector.`),
  h2("Names"),
  p(`Archetype keys follow one pattern, \`equipment[_discriminator][_modifier...]\`: one equipment term, at most one discriminator (the single distinction that makes it a different option), and modifiers in a fixed order. Examples: \`boiler_fuel-fired\`, \`kiln_dry-precalciner_efficiency-moderate\`, \`steam-reformer_methane_ccs-concentrated\`. A bare equipment key is a base, and keys that add a discriminator are its variants. Hyphens join words within a component; underscores separate components. The \`label\` column gives the plain-language name.`),

  h1("3. Where an archetype sits: the CIMS hierarchy"),
  p(`The services and end uses are the nodes of the CIMS hierarchy, which is the definitive list. Each archetype links to the nodes it serves, many to many, either directly (for example, iron-and-steel hot metal) or through a pattern such as "every sector's steam node". The rows for each sector are drawn from these links.`),
  bullets([
    "**Families** group archetypes for display only. Seven are services shared across sectors (heat supply, on-site power generation, machine drive, space conditioning, lighting, mobile equipment, and CO2 capture). The rest are one per sector, for integral process equipment.",
    "**Heat** is banded on the temperature the process needs: low below 150 °C, medium from 150 to 400 °C, and high above 400 °C. **Integral heat**, released inside the unit doing the transformation (a kiln, a blast furnace, an oven), belongs to a sector archetype. **Supplied heat** from a separable system (a boiler, CHP, a fired heater) belongs to a heat-supply archetype on the steam or direct-heat nodes. CHP is a heat-supply archetype; its electricity is an output flow, not a second technology.",
    "Services are kept at the most general level that still captures a real difference in energy use or emissions. Where an end use's archetypes cover sub-parts of a process (dryers and presses, for example), the hierarchy was split into step nodes rather than mixing sub-process values. A sector keeps either the chain of step nodes or a single whole-plant node, never both.",
  ]),

  h1("4. The central value and its range"),
  lead(`For each archetype and parameter the build writes a central value, a low, a high, and a count:`),
  table([1600, 7760], ["Field", "Rule"], [
    ["central", "The median of the examples' values when three or more examples carry one. With fewer, the value from the example whose source ranks highest in the source-priority list. A value read through a compilation carries the compilation's rank."],
    ["low, high", "The smallest and largest values any example gives, including ranges the sources print themselves. Written only where the values spread."],
    ["n", "The number of examples behind the value. Always shown; 0 for a filled value."],
  ]),
  gap(),
  p(`Several rows for the same quantity in one example (sizes, cases) count as one example, at their median. A figure a source prints more than once is pooled once. Where the original document is held, its own figure is used and a compilation's reprint of it is dropped.`),
  p(`**Figures a source prints wrongly.** Where a figure cannot be right as printed (a slipped decimal, a wrong unit, a row shifted against its label) and the source itself shows what was meant, the corrected figure is used. The correction is recorded once, with the evidence, and every value resting on it is listed in the \`source-corrections\` column.`),

  h1("5. Filling empty cells"),
  lead(`The aim is a value, or a deliberate marker, in every cell CIMS reads: capital cost, fixed and variable O&M, energy use or efficiency, lifetime, annual output, and TRL. Where no example gives one, a fill step writes a value and grades it by how it was reached. A fill never overwrites a sourced value, and the build recomputes it every time, so a new source displaces it with no hand edit.`),
  table([1700, 5160, 2500], ["Grade", "What it means", "Workbook shading"], [
    ["Sourced", "Pooled from examples (section 4).", "Darkest tint"],
    ["Sourced, converted", "Sourced, but converted with a factor from outside the source (a heating value, density, process ratio, or assumption).", "Second tint; see the external-conversions column"],
    ["Identity", "Calculated from the archetype's own values by a definition or physical relation: 100 ÷ efficiency, fuel use × emission factor, capacity × capacity factor.", "Third tint"],
    ["Estimated", "Borrowed or scaled from another archetype, or set by a class rule fitted on this database: a host plant's cost plus an increment, a sibling's lifetime, a class median, a cost ratio.", "Fourth tint"],
    ["Proxy", "A class constant from a named outside catalogue or handbook.", "Lightest tint"],
    ["Guess", "A judgement, with a stated range, rationale, and basis. Ranges are at least a factor of two for costs, ±30% for energy use, and a factor of three for plant size.", "Grey italic, unshaded"],
    ["not applicable", "The parameter does not characterise the archetype (the energy use of a leak-detection programme, the variable O&M of a boiler).", "Light grey"],
  ]),
  gap(),
  p(`A fill takes the weakest grade among its rule and its inputs. Each borrowing rule is back-tested on cells that do have a sourced value, as if they had none. The build also writes every table without any fill (\`output/unfilled/\`), so you can judge the sourced values alone.`),
  p(`Two calculated values appear on every archetype:`),
  bullets([
    "**Variants consistent with their hosts.** Every efficiency or capture variant takes its host's annual output, capacity, and capacity factor. A capture variant's costs, energy, and emissions are the host's plus the add-on. Where a variant's own sources gave different values, they are kept beside it as target `as-sourced`.",
    "**Calculated levelized cost**, `cost-levelized_calculated`: (capex × capital recovery factor + fixed O&M) ÷ capacity factor + variable O&M, at the archetype's lifetime and an 8% real reference discount rate. The `_calculated-incl-energy` column adds each carrier's energy use at a reference 2025 Canadian price. Neither includes transport or a rate of return. A levelized cost a source prints stays in `cost-levelized`.",
  ]),

  h1("6. Units and conversions"),
  h2("Product unit"),
  lead(`Each archetype declares one product unit: \`t\` for a process archetype, \`GJ\` for an energy service, \`m3\` where the product is a volume, or the unit of the stream an abatement or treatment service handles (tonnes of CH4, cubic metres of effluent). Units are the end use's final product, so all archetypes on an end use share one product. Every example is converted to the archetype's unit; what cannot be converted is excluded, with the reason.`),
  table([3000, 6360], ["Parameter", "Unit (pu = product unit)"], [
    ["capex, opex-fixed", "2025 CAD per (pu per year of nameplate capacity). A per-kW rating is put per year at 8,760 hours."],
    ["opex-variable, opex-total", "2025 CAD per pu"],
    ["abatement-cost", "2025 CAD per t CO2-eq"],
    ["specific-energy-consumption", "GJ per pu, gross input, on a higher heating value (HHV) basis"],
    ["emissions-*", "t per pu, by species"],
    ["capacity", "In each industry's own unit, named in capacity-unit (MW, kt/yr, and so on)"],
    ["efficiencies, shares, rates", "%. A COP is a % efficiency."],
    ["lifetime, construction-time", "years"],
  ]),
  gap(),
  h2("Conversion rules"),
  bullets([
    "Exact unit definitions (Btu, short ton, barrel) apply freely. Beyond those, a value converts only with a factor the same source gives for the same example, or with a registered **product factor**: a heating value, density, energy content, or process ratio, each with its own reference source. A conversion chains at most two factors.",
    "Every converted value records the weakest factor class it rests on: unit, same-source, property, ratio, internal (a value pooled in this database), or assumption. From property onward a factor is external to the source. The wide view names those factors in the `external-conversions` column, and the workbook shades the values.",
    "A cost per GJ is put per tonne through specific energy consumption only when both count the same GJ: the same stream, the same side (input or output), and the same scope.",
    "**Energy is on HHV.** A value the source states on HHV is used as it is. One stated on LHV is converted with the HHV/LHV ratio of the carrier it names. A source that does not state its basis takes its publisher region's convention.",
    "**Specific energy consumption is gross input.** Energy recovered and exported (BOF gas, exported steam, recovered power) is recorded as an output flow, not netted off. Feedstock whose energy ends up in the product is recorded as `feedstock-consumption`, not as energy use.",
    "**Emissions** are kept as separate parameters: combustion, process, total (only where a source reports them together), and captured. Species stay explicit and are not converted to CO2-eq, except in `emissions-reduction-potential`. On a capture variant, total emissions are net; total plus captured equals the host's gross. Biogenic CO2 is recorded apart from fossil CO2.",
    "A value per unit of energy input (an emission factor per GJ of fuel, a cost per kW of input) is put per unit of output with an efficiency: the example's own where the source gives one, otherwise the archetype's pooled value. CHP costs per kW of electricity are put per kW of heat with the heat-to-power ratio.",
  ]),
  h2("Currency"),
  p(`Every cost is converted once, from the currency and year the source publishes in: deflate in the source currency with its GDP deflator, then exchange at the 2025 rate.`),
  p(`\`factor(YYYY_XXX → 2025_CAD) = deflator[XXX][2025] ÷ deflator[XXX][YYYY] × exchange[CAD per XXX][2025]\``),
  p(`The deflator and exchange series come from the CIMS repository and are registered as reference sources. Where a source states no price year, its publication year is used, and the extraction notes say so. Costs are used as reported: they are not adjusted for Canadian labour, materials, or location.`),

  h1("7. Readiness"),
  p(`TRL is on one 1–9 ladder, using its industrial-process reading. Other scales (for example, the IEA's) map onto it, and a reported range is carried at its lower bound. CIMS reads TRL as availability: TRL 9 is available now, 7–8 in five years, 5–6 in ten years, and 4 or less in fifteen years or not at all.`),

  h1("8. The wide view and the detailed tables"),
  p(`The database file you are reviewing is the **wide view**: one row per archetype in each end use, with a column for each parameter's central value and folded columns for its low, high, and number of examples. It is a summary built for reading.`),
  lead(`Behind it, the build writes a set of **disaggregated CSV tables**, one row per value. They hold everything the wide view summarises, and more:`),
  table([3300, 6060], ["Table", "What it holds"], [
    ["example.csv", "Every source example, the archetype it is mapped to (or why it is set aside), and the readiness its source reports."],
    ["example-parameter.csv, example-flow.csv", "Every figure each source prints, as printed and converted to the archetype's basis, with its page or table, conversion factors, and the reason for any exclusion."],
    ["archetype-parameter.csv, archetype-flow.csv", "The summaries, one row per archetype, parameter, and target: central, low, high, and n, and for filled values the grade, rule, inputs, and rationale."],
    ["archetype-application.csv", "Every CIMS node each archetype serves."],
    ["wide-archetype-secondary-parameter.csv", "Values by stream or part, and other parameters left out of the wide view."],
    ["unfilled/", "The same tables before any fill, with sourced values only."],
  ]),
  gap(),
  p(`Use the wide view to judge whether a value is plausible. Use the detailed tables to trace a value to the source figures behind it. They are not in the review package, but we can send the rows for any archetype on request.`),
  h1("9. How to read the wide view"),
  numbered([
    "**One row per archetype in each end use it serves.** An archetype serving several end uses repeats under each; the `end-uses` and `families` columns list them all. The rows are banded by family (shared services first, then sectors), then by end use in process order. Within an end use the order is conventional technologies, efficient variants, capture variants, and low-carbon alternatives. Machine drive is banded by equipment instead.",
    "**Read every cost and intensity against product-unit.** A cost column holds CAD per tonne on a kiln row and CAD per GJ on a boiler row. Never sort, average, or chart a cost or intensity column across families.",
    "**Fold out the range.** Each parameter shows its central value; the `_low`, `_high`, and `_n` columns are grouped beside it and folded when the workbook opens. Use the + above a column to show them.",
    "**Read the shading** (section 5) for how certain a value is, and the `filled` column for which parameters were filled and how. `external-conversions` and `source-corrections` name the values resting on an outside factor or a corrected figure. `sources` lists every source behind the row.",
    "**Check status.** `quantified` means at least one value came from examples; `estimated` means every value was filled. `n-examples` counts the examples behind the archetype.",
    "**Energy by carrier and emissions by species** are on the `wide-carriers-species` sheet, for the same rows. The carriers there are one example's shares of the pooled total, so do not add the columns: `fuel` is the sum of the named fuels beside it.",
    "**Some end uses restate an archetype in another unit** (per GJ of process heat, hydrogen per tonne, liquid fuels per m3). The `filled` column names the factor; the long tables keep the archetype's own unit.",
    "The `column-legend` sheet defines every column; hovering over a column heading shows the same definition.",
  ], "numbers"),
];

save(doc("Technology database: methodology summary", "Technology database review  |  build of 3 November 2026", "Methodology summary", body), OUT);
