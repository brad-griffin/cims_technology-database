"""Propose a roster name for every technology in the design table.

The design table (design/end-use-technology-table.csv) names technologies in
prose -- "Fuel-fired boiler" -- and carries the carriers as a list.  The roster
names them `equipment_carrier_variant` (design doc section 5).  The user's
decision of 2026-09-14 is that the DESIGN ROW BECOMES THE ROSTER ROW, so the
carrier is no longer a name component: it survives as the `energy-carrier`
list on the row, and a technology that differs only by the fuel it burns is one
technology.

So a proposed name here is `equipment` plus, where the label carries one, a
`variant`.  Equipment and variant terms are checked against the section 6.2
vocabularies (read from vocabulary.csv, which build-template.py writes from the
design document).  A label needing a term the vocabulary does not hold is NOT
renamed around -- it is reported, because a new term is a modelling decision
(design doc section 6.2).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DESIGN = ROOT / "design"
SEU = DESIGN / "sector-end-use-table.csv"
TECHTABLE = DESIGN / "end-use-technology-table.csv"
VOCAB = HERE / "vocabulary.csv"


def slug(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (x or "").lower()).strip("-")


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def vocabularies() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for r in read_csv(VOCAB):
        out.setdefault(r["list-name"], set()).add(r["term"])
    return out


# --- equipment hints -----------------------------------------------------
# A label's own words carry the equipment term often enough to be worth trying
# first; these are the cases where the source wording and the vocabulary term
# differ.  Longest phrase wins, so the order of the dict does not matter.
EQUIPMENT_HINT = {
    "cogeneration": "combined-cycle", "combined heat and power": "combined-cycle",
    "gas turbine": "combustion-turbine", "turbine": "combustion-turbine",
    "steam turbine": "steam-turbine", "back-pressure": "steam-turbine",
    "engine": "reciprocating-engine", "genset": "reciprocating-engine",
    "heat pump": "heat-pump", "vapour recompression": "vapour-recompressor",
    "vapor recompression": "vapour-recompressor",
    "electrolyzer": "electrolyzer", "electrolyzer": "electrolyzer",
    "electrolysis": "electrolysis-cell", "electrowinning": "electrolysis-cell",
    "fuel cell": "fuel-cell", "solar thermal": "solar-collector",
    "concentrating solar": "solar-concentrator",
    "resistance": "resistance-heater", "induction": "induction-heater",
    "microwave": "microwave-heater", "radio-frequency": "radio-frequency-heater",
    "infrared": "resistance-heater", "plasma": "plasma-torch",
    "arc furnace": "electric-arc-furnace", "electric arc": "electric-arc-furnace",
    "basic oxygen": "basic-oxygen-furnace", "blast furnace": "blast-furnace",
    "shaft furnace": "shaft-furnace", "melting furnace": "melting-furnace",
    "holding furnace": "melting-furnace", "reheat furnace": "furnace",
    "refining furnace": "refining-furnace", "anode furnace": "refining-furnace",
    "coke oven": "coke-oven", "sinter": "sinter-plant",
    "pellet": "pellet-plant", "induration": "pellet-plant",
    "calciner": "calciner", "precalciner": "precalciner",
    "clinker cooler": "clinker-cooler", "kiln": "kiln",
    "boiler": "boiler", "steam generator": "boiler",
    "dryer": "dryer", "drying": "dryer", "dry": "dryer",
    "oven": "oven", "fryer": "oven", "roaster": "roaster",
    "pasteuris": "pasteurizer", "pasteuriz": "pasteurizer",
    "digester": "digester", "anaerobic": "anaerobic-digester",
    "fermenter": "fermenter", "fermentation": "fermenter",
    "pulper": "pulper", "refiner": "pulper", "paper machine": "paper-machine",
    "press": "press", "evaporator": "evaporator", "evaporation": "evaporator",
    "distillation": "distillation-column", "column": "distillation-column",
    "reformer": "steam-reformer", "autothermal": "autothermal-reformer",
    "gasifier": "gasifier", "gasification": "gasifier",
    "cracker": "steam-cracker", "cracking": "steam-cracker",
    "reactor": "reactor", "synthesis": "reactor", "hydrotreat": "reactor",
    "coking": "reactor", "leach": "leaching-vessel",
    "flotation": "flotation-cell", "smelt": "smelting-vessel",
    "converter": "converter", "roast": "roaster",
    "crusher": "crusher", "crushing": "crusher",
    "mill": "grinding-mill", "grinding": "grinding-mill",
    "rolling": "rolling-mill", "caster": "caster", "casting": "caster",
    "motor": "motor", "pump": "pump", "fan": "fan", "compressor": "compressor",
    "conveyor": "conveyor", "conveying": "conveyor",
    "chiller": "chiller", "refrigerat": "chiller", "cooling tower": "cooling-tower",
    "ventilation": "ventilation-unit", "lighting": "lighting",
    "space heat": "space-heater", "air heating": "direct-heater",
    "air separation": "air-separation-unit", "cryogenic": "air-separation-unit",
    "adsorption": "air-separation-unit", "membrane": "air-separation-unit",
    "capture": "capture-unit", "absorption": "capture-unit",
    "heat recovery": "heat-recovery-unit", "waste heat": "heat-recovery-unit",
    "economizer": "heat-recovery-unit", "economizer": "heat-recovery-unit", "regenerat": "heat-recovery-unit",
    "thermal energy storage": "heat-recovery-unit", "storage": "heat-recovery-unit",
    "geothermal": "geothermal-well", "nuclear": "reactor",
    "energy management": "management-system", "management system": "management-system",
    "maintenance": "management-system", "control": "management-system",
    "process heater": "direct-heater", "fired heater": "direct-heater",
    "direct-fired": "direct-heater", "burner": "direct-heater",
    "heater": "direct-heater", "furnace": "furnace",
    "transesterification": "transesterification-unit",
    "ultraviolet": "ultraviolet-curer", "uv": "ultraviolet-curer",
    "preheat": "preheater", "curing": "ultraviolet-curer",
    "cleaning": "cleaning-system", "washing": "cleaning-system",
}

# Variant terms the label spells differently from the vocabulary.
VARIANT_HINT = {
    "carbon capture": "ccs", "with ccs": "ccs", "ccs": "ccs",
    "retrofit": "retrofit", "greenfield": "greenfield",
    "cogeneration": "chp", "combined heat and power": "chp", "chp": "chp",
    "oxyfuel": "oxyfuel", "oxy-fuel": "oxyfuel",
    "variable speed": "variable-speed", "variable-speed": "variable-speed",
    "high efficiency": "efficiency-strong", "high-efficiency": "efficiency-strong",
    "premium efficiency": "efficiency-strong", "condensing": "efficiency-strong",
    "best available": "bat", "dry": "dry", "wet": "wet",
    "hisarna": "hisarna", "corex": "corex", "midrex": "midrex", "hyl": "hyl",
    "top-gas": "top-gas-recycling", "tecnored": "tecnored",
    "ulcored": "ulcored", "ulcowin": "ulcowin", "hismelt": "hismelt",
    "plasma": "plasma", "fluidized bed": "fluidized-bed",
    "fluidized bed": "fluidized-bed", "vertical roller": "vertical-roller",
    "high-pressure roll": "high-pressure-roll", "geopolymer": "geopolymer",
    "lepol": "lepol", "long dry": "long-dry", "semi-dry": "semi-dry",
    "semi-wet": "semi-wet", "preheat": "preheat", "direct": "direct",
    "low-temperature": "low-temp", "medium-temperature": "medium-temp",
    "high-temperature": "high-temp",
}

# Words that mark the carrier, not the device.  They are dropped from the name
# (the carrier is a list column now) but kept to seed `energy-carrier`.
CARRIER_WORD = {
    "electric": "electricity", "electrified": "electricity",
    "electrically": "electricity", "hydrogen": "hydrogen",
    "biomass": "biomass", "biomethane": "biomethane", "biogas": "biogas",
    "solar": "solar", "geothermal": "geothermal", "nuclear": "nuclear",
    "natural gas": "natural-gas", "gas-fired": "natural-gas",
    "fuel-fired": "fossil", "oil": "oil", "coal": "coal",
    "solid-fuel": "biomass", "black liquor": "black-liquor",
    "waste heat": "waste-heat", "steam": "steam",
}


def propose(label: str, energy_inputs: str, vocab: dict[str, set[str]]) -> dict:
    """Return the proposed name and its components for one design label."""
    low = " " + label.lower() + " "
    equip = ""
    for phrase in sorted(EQUIPMENT_HINT, key=len, reverse=True):
        if phrase in low:
            equip = EQUIPMENT_HINT[phrase]
            break
    if not equip:
        for term in sorted(vocab.get("equipment", ()), key=len, reverse=True):
            if term.replace("-", " ") in low:
                equip = term
                break
    variants = []
    for phrase in sorted(VARIANT_HINT, key=len, reverse=True):
        if phrase in low and VARIANT_HINT[phrase] not in variants:
            variants.append(VARIANT_HINT[phrase])
    carriers = [c.strip() for c in energy_inputs.split(",") if c.strip()]
    return {"label": label, "equipment": equip,
            "variant": variants[0] if variants else "",
            "variants-seen": variants, "carriers": carriers}


# --- name assembly -------------------------------------------------------
STOP = {"with", "and", "or", "the", "a", "an", "for", "on", "in", "to", "of",
        "by", "its", "from", "unit", "system", "plant", "process", "line",
        "technology", "based"}

def _discriminator(label: str, equip: str, keep: int = 4) -> list[str]:
    """The label's words with the equipment's own words and filler removed.

    The discriminator is what tells two design rows on the same device apart --
    `boiler_fuel-fired` against `boiler_electric` -- now that the carrier is no
    longer a name component.  Words are kept in the label's own order so the
    name reads the way the design table says it."""
    words = re.split(r"[^a-z0-9]+", label.lower())
    drop = set(equip.split("-")) | STOP
    # a device word the hint table reached the equipment term through
    for phrase, term in EQUIPMENT_HINT.items():
        if term == equip:
            drop |= set(phrase.split())
    out = [w for w in words if w and w not in drop]
    return out[:keep] if keep else out


def build_names(rows: list[dict], vocab: dict[str, set[str]],
                hand: dict[str, str] | None = None,
                merge: dict[str, str] | None = None,
                fixed: dict[str, str] | None = None) -> dict[str, dict]:
    """label -> {name, equipment, variant, carriers, sectors, flags}."""
    hand = hand or {}
    merge = merge or {}
    first: dict[str, dict] = {}
    for r in rows:
        first.setdefault(merge.get(r["technology"], r["technology"]), r)
    out: dict[str, dict] = {}
    for label, r in first.items():
        p = propose(label, r["energy-inputs"], vocab)
        equip = hand.get(label) or p["equipment"]
        flags = []
        if not equip:
            equip = "process-improvement"
            flags.append("no equipment term matched; parked on process-improvement")
        if equip not in vocab.get("equipment", ()):
            flags.append(f"equipment {equip!r} is not in section 6.2")
        out[label] = {"label": label, "name": "", "equipment": equip,
                      "discriminator": "", "carriers": p["carriers"],
                      "flags": flags}
    # a hand-written name settles the row before the generator runs
    for label, name in (fixed or {}).items():
        if label in out:
            out[label]["name"] = name
            out[label]["discriminator"] = name.split("_", 1)[1] if "_" in name else ""
            out[label]["equipment"] = name.split("_", 1)[0]
            out[label]["settled"] = True
            out[label]["flags"] = [f for f in out[label]["flags"]
                                   if not f.startswith("equipment ")]
            if out[label]["equipment"] not in vocab.get("equipment", ()):
                out[label]["flags"].append(
                    f"equipment {out[label]['equipment']!r} is not in section 6.2")
    # assemble, lengthening the discriminator until the name is unique
    for keep in (2, 3, 4, 6, 0):
        taken: dict[str, list[str]] = {}
        for label, d in out.items():
            if d["name"] and d.get("settled"):
                taken.setdefault(d["name"], []).append(label)
        for label, d in out.items():
            if d.get("settled"):
                continue
            disc = "-".join(_discriminator(label, d["equipment"], keep))
            name = f"{d['equipment']}_{disc}" if disc else d["equipment"]
            d["discriminator"], d["name"] = disc, name
            taken.setdefault(name, []).append(label)
        for name, labels in taken.items():
            if len(labels) == 1:
                out[labels[0]]["settled"] = True
    for label, d in out.items():
        if not d.get("settled"):
            d["flags"].append("name still collides; needs a hand name")
        d.pop("settled", None)
        v = d["discriminator"]
        if v and v not in vocab.get("variant", ()) and v not in vocab.get("energy-carrier", ()):
            d["flags"].append("new discriminator")
    return out
