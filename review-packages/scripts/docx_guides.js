const { lead, p, h1, h2, bullets, numbered, table, gap, doc, save } = require("./docx_lib");
const F = require("./sector-facts.json");
const OUTDIR = process.argv[2];

const SECTORS = { breweries: "Breweries", steel: "Iron and steel", "pulp-and-paper": "Pulp and paper", cement: "Cement", chemicals: "Chemicals" };
const DEADLINE = "27 November 2026";
const CONTACT = "Brad Griffin at bradford_griffin@sfu.ca";

const problems = table([3200, 6160], ["Potential problem", "Example"], [
  ["A value that looks wrong", "Capital cost looks about twice too high for a new North American plant; see [author, year], p. 12."],
  ["A basis, unit, or scope problem", "This energy use seems to include the reheat furnace, not the rolling mill alone."],
  ["Archetypes to merge or split", "Split this into wet and semi-dry kilns; Canadian plants still run both, at very different energy use."],
  ["A missing technology or example", "There is no archetype for CO2 recovery from fermentation, which most large breweries run."],
  ["A better or missing source", "[Author, year] has measured Canadian figures for this step."],
  ["Anything else", "This label is not the term the industry uses."],
]);

function guide(key) {
  const whole = key === "whole-database";
  const name = whole ? "Whole database" : SECTORS[key];
  const lname = key === "breweries" ? "brewery" : name.toLowerCase();
  const f = F[key];
  const files = whole
    ? [["reviewer-guide_whole-database.docx", "This guide."],
       ["methodology-summary.docx", "How the database is built and how to read it."],
       ["wide-view_whole-database.xlsx", `The database: ${f.archetypes} archetypes in ${f.rows} rows, with energy use by carrier, emissions by species, the source list, and a column legend.`]]
    : [[`reviewer-guide_${key}.docx`, "This guide."],
       ["methodology-summary.docx", "How the database is built and how to read it."],
       [`sector-note_${key}.docx`, `The ${lname} archetypes, their main sources, and the judgement calls we most want you to test.`],
       [`wide-view_${key}.xlsx`, `The ${lname} part of the database: ${f.archetypes} archetypes in ${f.rows} rows, with energy use by carrier, emissions by species, and a column legend.`]];

  const check = whole ? [
    "**Archetype boundaries for a technology-choice model.** Are the archetypes the options a model should choose between? Look at the test for a new archetype (about 15% difference in energy use, a different kind of emissions or abatement, or a legacy type still in Canadian stock), the efficiency buckets, and the merges in each family.",
    "**Framing.** Whole-plant archetypes compete with the unit archetypes inside them, and capture variants carry their host's size and costs plus a capture add-on. Does this let the CIMS model compete options fairly without double counting?",
    "**The central-value and fill rules.** Is a median of three or more examples, else the value from the top-ranked source, a sound central value? Are the fill grades, the back-tested borrowing rules, and the judgement ranges defensible?",
    "**Consistency across families.** Do costs per unit of annual capacity, the calculated levelized cost (8% real discount rate, over the archetype's lifetime), capacity factors, and lifetimes sit in sensible relation to each other?",
    "**Conventions.** Energy on a higher heating value basis throughout, gross energy input with recovered energy recorded as an output, feedstock held apart from energy use, direct (on-site) emissions only, and costs converted by deflating then exchanging, with no adjustment for Canadian location. Where do these conventions mislead?",
    "**The cross-cutting families:** heat supply (boilers, combined heat and power, heat pumps, and electric and solar heat), on-site power, machine drive, space conditioning, lighting, mobile equipment, and CO2 capture.",
    "**Coverage.** Missing technologies, thin archetypes (one or two examples, or filled values only), and major sources missing from the source list.",
    "**Readiness.** Technology readiness levels, and how they translate into the year an option becomes available in the model.",
  ] : [
    `**The ${lname} archetypes.** Is each one a real option in Canadian plants, now or in the future? Is anything missing, merged that should be separate, or separate that should be merged? The sector note lists the calls we most want tested.`,
    "**The central values and ranges** for energy use, efficiency, emissions, capital and operating costs, lifetime, capacity, and capacity factor. Are they plausible for the technology? Are they on the right basis: per tonne of the right product, for the right scope of equipment, and with energy on a higher heating value basis?",
    "**The filled values.** The shading shows which values came from sources and which the database estimated or guessed. We most want your view on guessed values (grey italic) and on archetypes marked \"filled only\" in the sector note.",
    "**Sources.** Better, newer, or Canadian sources for any archetype, especially the thin ones.",
    "**The cross-cutting rows** (boilers, combined heat and power, motors, heating and cooling, lighting, and CO2 capture) that serve your sector. Tell us whether they fit how your sector uses them. A detailed check of their values is optional.",
    "**Readiness.** The technology readiness level of emerging options.",
  ];

  const outOfScope = [
    "Purchased electricity and the emissions from generating it: the model prices electricity, not the database.",
    "How each source was transcribed. If a value traces to a misread source, tell us and we will check the transcription.",
    ...(key === "cement" ? ["Lime, glass, ceramics, and gypsum, which share the industrial-minerals sector. We can provide the lime kilns on request; see the sector note."] : []),
  ];

  const body = [
    p(`Thank you for reviewing the technology database. ${whole
      ? "This package is for energy-economy technology modellers. It asks you to review the database as a whole: its structure, its rules, and its fitness as an input to a technology-choice model."
      : `This package asks you to review the ${lname} part of the database as a sector expert.`} The database describes the industrial technologies that can provide each end use in the CIMS energy-economy model, summarised from published sources (${F._totals.sources} in its source list).`),
    p("**If another format would suit you better, ask us.** For example, we can provide the information as a Word document instead of a database table."),
    p(`Please return your comments by **${DEADLINE}**.`),
    h1("1. What is in this package"),
    table([3600, 5760], ["File", "What it is"], files),
    gap(),
    p(whole ? "Start with the methodology summary, then the database." : "Start with the methodology summary, then the sector note, then the database."),
    h1("2. What to check"),
    ...bullets(check),
    p("You do not need to check every row. A careful look at the rows you know best is worth more than a quick pass over all of them."),
    h1("3. What is out of scope"),
    ...bullets(outOfScope),
    h1("4. How to read the database"),
    ...bullets([
      "Open the `wide-archetype` sheet first. Each row is one archetype under one end use; an archetype serving several end uses repeats under each.",
      "Read every cost and energy use against the `product-unit` column: a kiln row is per tonne and a boiler row is per GJ. Do not sort the sheet, because that breaks the grouping of rows.",
      "Use the + above a column to show its `_low`, `_high`, and `_n` (number of examples) columns.",
      "The shading shows how certain a value is; the key is on the `readme` sheet. The `filled` column says which values were filled and how.",
      "The `column-legend` sheet defines every column.",
    ]),
    h1("5. How to return comments"),
    h2("Row comments"),
    lead("Write comments on a row in the **reviewer-comment** column of the `wide-archetype` sheet (column C, the shaded column beside the archetype name). Say which column you mean. The kinds of problem we hope you will find, with examples:"),
    problems,
    gap(),
    ...bullets([
      "Do not change values in the other columns. Write the value you would expect in your comment instead, with its unit and basis.",
      "When you suggest a source, give as much information as you can about it: the full citation, a link, or the file itself.",
    ]),
    h2("General comments"),
    p(`Put comments on the structure, the methodology${whole ? "" : ", or the sector note"} in a short covering note, or as Word comments on the documents.`),
    h2("Sending them back"),
    ...numbered([
      `Add your surname or your association's name to the file names, for example \`wide-view_${key}_surname.xlsx\`.`,
      `Send the database file, with any covering note or commented documents, to ${CONTACT}.`,
      `Send them by ${DEADLINE}. If you need more time, or want to discuss anything first, contact Brad at the same address.`,
    ]),
  ];
  return save(doc(`Reviewer guide: ${name}`, `Technology database review package  |  build of 3 November 2026`, `Reviewer guide: ${name}`, body),
    `${OUTDIR}/review-package_${key}/reviewer-guide_${key}.docx`);
}

(async () => { for (const k of [...Object.keys(SECTORS), "whole-database"]) await guide(k); })();
