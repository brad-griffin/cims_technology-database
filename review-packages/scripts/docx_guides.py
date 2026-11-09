"""Reviewer guides for the review packages."""
from docx_lib import make_doc, render

SECTORS = {"breweries": "Breweries", "steel": "Iron and steel", "pulp-and-paper": "Pulp and paper",
           "cement-and-lime": "Cement and lime", "chemicals": "Chemicals", "conventional-oil": "Conventional oil production",
           "oil-sands": "Oil sands", "natural-gas": "Natural gas production", "biofuels": "Biofuels",
           "hydrogen": "Hydrogen", "mining": "Mining", "aluminum": "Aluminum",
           "petroleum-refining": "Petroleum refining"}
EXTRA_OUT_OF_SCOPE = {
    "cement-and-lime": "Glass, ceramics, and gypsum, which share the industrial-minerals sector.",
    "natural-gas": "Gas transmission pipelines and distribution. We can provide them on request; see the sector note.",
    "conventional-oil": "Methane venting, flaring, and leak controls at oil sites, which the database holds with natural gas production.",
    "aluminum": "Copper, nickel, lead, zinc, magnesium, and titanium smelting.",
}
DEADLINE = "27 November 2026"
CONTACT = "Brad Griffin at bradford_griffin@sfu.ca"

PROBLEMS = ("table", [3200, 6160], ["Potential problem", "Example"], [
    ["A value that looks wrong", "Capital cost looks about twice too high for a new North American plant; see [author, year], p. 12."],
    ["A basis, unit, or scope problem", "This energy use seems to include the reheat furnace, not the rolling mill alone."],
    ["Archetypes to merge or split", "Split this into wet and semi-dry kilns; Canadian plants still run both, at very different energy use."],
    ["A missing technology or example", "There is no archetype for CO2 recovery from fermentation, which most large breweries run."],
    ["A better or missing source", "[Author, year] has measured Canadian figures for this step."],
    ["Anything else", "This label is not the term the industry uses."],
])

CHECK_WHOLE = [
    "**Archetype boundaries for a technology-choice model.** Are the archetypes the options a model should choose between? Look at the test for a new archetype (about 15% difference in energy use, a different kind of emissions or abatement, or a legacy type still in Canadian stock), the efficiency buckets, and the merges in each family.",
    "**Framing.** Whole-plant archetypes compete with the unit archetypes inside them, and capture variants carry their host's size and costs plus a capture add-on. Does this let the CIMS model compete options fairly without double counting?",
    "**The central-value and fill rules.** Is a median of three or more examples, else the value from the top-ranked source, a sound central value? Are the fill grades, the back-tested borrowing rules, and the judgement ranges defensible?",
    "**Consistency across families.** Do costs per unit of annual capacity, the calculated levelized cost (8% real discount rate, over the archetype's lifetime), capacity factors, and lifetimes sit in sensible relation to each other?",
    "**Conventions.** Energy on a higher heating value basis throughout, gross energy input with recovered energy recorded as an output, feedstock held apart from energy use, direct (on-site) emissions only, and costs converted by deflating then exchanging, with no adjustment for Canadian location. Where do these conventions mislead?",
    "**The cross-cutting families:** heat supply (boilers, combined heat and power, heat pumps, and electric and solar heat), on-site power, machine drive, space conditioning, lighting, mobile equipment, and CO2 capture.",
    "**Coverage.** Missing technologies, thin archetypes (one or two examples, or filled values only), and major sources missing from the source list.",
    "**Readiness.** Technology readiness levels, and how they translate into the year an option becomes available in the model.",
    "**Options that may have stalled.** We have kept these for now: black liquor gasification (`gasifier_black-liquor`; its developer, Chemrec, now only licenses its patents), the electrified plasma clinker kiln (`kiln_electric-plasma`; feasibility study finished 2019), the hydrothermal calcium hydrosilicate binder (`binder_hydrothermal-silicate`), radio-frequency heating of oil sands (`well_electromagnetic-heating`; pilot about 2015 to 2017), and the microwave-assisted ceramic kiln (`kiln_ceramic-microwave-assisted`). Should a technology-choice model keep options whose development has stopped?",
    "**Source error.** If a value traces to a misread source, tell us and we will check the transcription.",
]


def check_sector(lname):
    return [
        f"**The {lname} archetypes.** Is each one a real option in Canadian facilities, now or in the future? Is anything missing, merged that should be separate, or separate that should be merged? The sector note lists the calls we most want tested.",
        "**The central values and ranges** for energy use, efficiency, emissions, capital and operating costs, lifetime, capacity, and capacity factor. Are they plausible for the technology? Are they on the right basis: per tonne of the right product, for the right scope of equipment, and with energy on a higher heating value basis?",
        '**The filled values.** The shading shows which values came from sources and which the database estimated or guessed. We most want your view on guessed values (grey italic on the lightest tint) and on archetypes with few core values sourced (the sector note counts them).',
        "**Sources.** Better, newer, or Canadian sources for any archetype, especially the thin ones.",
        "**The cross-cutting rows** (boilers, combined heat and power, motors, heating and cooling, lighting, and CO2 capture) that serve your sector. Tell us whether they fit how your sector uses them. A detailed check of their values is optional.",
        "**Readiness.** The technology readiness level of emerging options.",
        "**Source error.** If a value traces to a misread source, tell us and we will check the transcription.",
    ]


def guide(outdir, key, facts):
    whole = key == "whole-database"
    name = "Whole database" if whole else SECTORS[key]
    lname = "brewery" if key == "breweries" else name.lower()
    f = facts[key]
    if whole:
        files = [["reviewer-guide_whole-database.docx", "This guide."],
                 ["methodology-summary.docx", "How the database is built and how to read it."],
                 ["wide-view_whole-database.xlsx", f"The database: {f['archetypes']} archetypes in {f['rows']} rows, with sheets for energy use by carrier, emissions by species, feedstocks, heat, and sources, and a column legend."],
                 ["sector-notes folder", f"One note per sector ({len(SECTORS)}): each sector's archetypes, their main sources, and the judgement calls we most want sector experts to test. Read the notes for the sectors you know; comments on them are welcome but optional."]]
    else:
        files = [[f"reviewer-guide_{key}.docx", "This guide."],
                 ["methodology-summary.docx", "How the database is built and how to read it."],
                 [f"sector-note_{key}.docx", f"The {lname} archetypes, their main sources, and the judgement calls we most want you to test."],
                 [f"wide-view_{key}.xlsx", f"The {lname} part of the database: {f['archetypes']} archetypes in {f['rows']} rows, with sheets for energy use by carrier, emissions by species, feedstocks, and heat, and a column legend."]]
    # Out of scope appears only where a sector has its own exclusion (user edit 2026-11-05).
    out_of_scope = [EXTRA_OUT_OF_SCOPE[key]] if key in EXTRA_OUT_OF_SCOPE else []
    sec = iter(range(3, 9))
    intro = ("This package is for energy-economy technology modellers. It asks you to review the database as a whole: its structure, its rules, and its fitness as an input to a technology-choice model."
             if whole else f"This package asks you to review the {lname} part of the database as a sector expert.")
    body = [
        ("p", f"Thank you for reviewing the technology database. {intro} The database describes the industrial technologies that can provide each end use in the CIMS energy-economy model, summarised from published sources ({facts['_totals']['sources']} in its source list)."),
        ("p", "**If another format would suit you better, ask us.** For example, we can provide the information as a Word document instead of a database table."),
        ("p", f"Please return your comments by **{DEADLINE}**."),
        ("h1", "1. What is in this package"),
        ("table", [3600, 5760], ["File", "What it is"], files),
        ("gap",),
        ("p", "Start with the methodology summary, then the database." if whole else
              "Start with the methodology summary, then the sector note, then the database."),
        ("h1", "2. What to check"),
        ("bullets", CHECK_WHOLE if whole else check_sector(lname)),
        ("p", "You do not need to check every row. A careful look at the rows you know best is worth more than a quick pass over all of them."),
        *([("h1", f"{next(sec)}. What is out of scope"), ("bullets", out_of_scope)] if out_of_scope else []),
        ("h1", f"{next(sec)}. How to read the database"),
        ("bullets", [
            "Open the `archetypes` sheet first. Each row is one archetype under one end use; an archetype serving several end uses repeats under each." + ("" if whole else " Your sector's own family is the top band."),
            "Read every cost and energy use against the `product-unit` column: a kiln row is per tonne and a boiler row is per GJ. Do not sort the sheet, because that breaks the grouping of rows.",
            "Use the + above a column to show its `_low`, `_high`, and `_n` (number of examples) columns.",
            "The shading shows how certain a value is; the key is on the `readme` sheet. The `filled` column says which values were filled and how.",
            "The `column-legend` sheet defines every column.",
        ]),
        ("h1", f"{next(sec)}. How to return comments"),
        ("h2", "Row comments"),
        ("lead", "Write comments on a row in the **reviewer-comment** column of the `archetypes` sheet (column B, the shaded column just before the archetype name). Say which column you mean. The kinds of problem we hope you will find, with examples:"),
        PROBLEMS,
        ("gap",),
        ("bullets", [
            "Do not change values in the other columns. Write the value you would expect in your comment instead, with its unit and basis.",
            "When you suggest a source, give as much information as you can about it: the full citation, a link, or the file itself.",
        ]),
        ("h2", "General comments"),
        ("p", "Put comments on the structure, the methodology" + ("" if whole else ", or the sector note") + " in a short covering note, or as Word comments on the documents."),
        ("h2", "Sending them back"),
        ("numbered", [
            f"Add your surname or your association's name to the file names, for example `wide-view_{key}_surname.xlsx`.",
            f"Send the database file, with any covering note or commented documents, to {CONTACT}.",
            f"Send them by {DEADLINE}. If you need more time, or want to discuss anything first, contact Brad at the same address.",
        ]),
    ]
    doc = make_doc(f"Reviewer guide: {name}", "Technology database review package  |  build of 4 November 2026",
                   f"Reviewer guide: {name}")
    render(doc, body)
    doc.save(outdir / f"review-package_{key}" / f"reviewer-guide_{key}.docx")


def build(outdir, facts):
    for key in [*SECTORS, "whole-database"]:
        guide(outdir, key, facts)
