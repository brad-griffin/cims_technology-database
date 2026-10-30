"""Map the CIMS technology roster onto the harmonized naming convention.

Run from the repo root:   python database/harmonized/build-cims-map.py

Reads  database/harmonized/cims-roster.csv   (built by extract-cims-roster.py)
Writes database/harmonized/cims-map.csv      one row per CIMS technology

This is a rules engine, not a hand-made list, so the mapping is reproducible
and every judgement is visible in one place.  Rows it cannot map confidently
are marked action=review rather than guessed; that column is what the
CIMS review document is built from.

Vocabulary terms come from section 6.2 of the design document -- the mapper
checks its own output against them and fails loudly on an unlisted term.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
VOCAB = ROOT / "database" / "raw-data" / "extraction-vocabulary.csv"

# --- carrier detection: first match wins, so order matters -----------------
CARRIER = [
    (r"\brenewable natural gas\b|\brng\b",           "renewable-natural-gas"),
    (r"\bnatural gas\b|\bng\b",                      "natural-gas"),
    (r"\bstill gas\b",                               "still-gas"),
    (r"iron process gas|blast furnace gas|\bbfg\b",  "blast-furnace-gas"),
    (r"coke oven gas|\bcog\b",                       "coke-oven-gas"),
    (r"refinery gas",                                "refinery-gas"),
    (r"\bheavy fuel oil\b|\bhfo\b|\bfuel oil\b",     "oil"),
    (r"\bpetcoke\b|petroleum coke",                  "petroleum-coke"),
    (r"\bthermal coal\b|\bcoal\b",                   "coal"),
    (r"\bcoke\b",                                    "coke"),
    (r"liquid biomass|\bbio-?oil\b",                 "liquid-biomass"),
    (r"\bbiomass\b|\bhog fuel\b|\bwood\b",           "biomass"),
    (r"black liquor",                                "black-liquor"),
    (r"\bbiogas(es)?\b|landfill gas",                     "biogas"),
    (r"\bbiodiesel\b|\bethanol\b",                   "biomass"),
    (r"\bhydrogen\b|\bh2\b",                         "hydrogen"),
    (r"\bammonia\b",                                 "ammonia"),
    (r"\bpropane\b|\blpg\b|liqu[ei]fied petroleum gas", "lpg"),
    (r"\bdiesel\b",                                  "diesel"),
    (r"\bbenzole\b|coal tar|\btars\b",              "benzole-and-tars"),
    (r"\bnaphtha\b",                                 "naphtha"),
    (r"\bmethanol\b",                                "methanol"),
    (r"\bsolar\b",                                   "solar"),
    (r"\bgeothermal\b",                              "geothermal"),
    (r"\bnuclear\b|\bsmr\b",                         "nuclear"),
    (r"waste heat|\bheat recovery\b|\bhrsg\b",       "waste-heat"),
    (r"municipal (solid )?waste|\bmsw\b",            "municipal-waste"),
    (r"\bsteam\b",                                   "steam"),
    (r"\belectric\b|\belectrical\b|\belectricity\b|"
     r"\bac motor\b|\bdc motor\b|\belectrolytic\b|\belectrolysis\b", "electricity"),
    (r"\boil\b",                                     "oil"),
]

# --- equipment detection: first match wins ---------------------------------
EQUIPMENT = [
    (r"\bbpst\b|back ?pressure steam turbine|steam turbine",      "steam-turbine"),
    (r"\bscgt\b|\bccgt\b|combined cycle",                         "combined-cycle"),
    (r"gas turbine|combustion turbine|\bsimple cycle\b",          "combustion-turbine"),
    (r"microturbine",                                             "microturbine"),
    (r"reciprocating engine|spark ignition|\bgenset\b",           "reciprocating-engine"),
    (r"fuel cell",                                                "fuel-cell"),
    (r"\bcogen\w*\b|\bchp\b",                                     "combined-cycle"),
    (r"\bboilers?\b",                                            "boiler"),
    (r"heat pump",                                                "heat-pump"),
    (r"\bhr and reg burner\b|heat recovery|\bhrsg\b|recuperat",   "heat-recovery-unit"),
    (r"\beaf\b|electric arc furnace",                             "electric-arc-furnace"),
    (r"\bbof\b|basic oxygen",                                     "basic-oxygen-furnace"),
    (r"bf-bof|blast furnace|\bbf\b",                              "blast-furnace"),
    (r"\bdri\b|\bhdri\b|direct reduc|\bmidrex\b|shaft furnace",   "shaft-furnace"),
    (r"smelter|smelting|\bcorex\b|\bhisarna\b|flash furnace",     "smelting-vessel"),
    (r"coke oven|coke making|coke plant",                         "coke-oven"),
    (r"sinter",                                                   "sinter-plant"),
    (r"\bpellet",                                                 "pellet-plant"),
    (r"precalciner",                                              "precalciner"),
    (r"preheater",                                                "preheater"),
    (r"\bkilns?\b|cement plant|cement subsector",                 "kiln"),
    (r"calcin",                                                   "calciner"),
    (r"steam cracker|\bcracker\b|cracking",                       "steam-cracker"),
    (r"autothermal reform",                                       "autothermal-reformer"),
    (r"reform",                                                   "steam-reformer"),
    (r"electroly",                                                "electrolysis-cell"),
    (r"gasific|gasifier",                                         "gasifier"),
    (r"\bcasting\b|\bcaster\b|casting",                           "caster"),
    (r"rolling|\bmill\b|\brolls?\b",                              "rolling-mill"),
    (r"grinding|\bgrinder\b",                                     "grinding-mill"),
    (r"crush",                                                    "crusher"),
    (r"flotation",                                                "flotation-cell"),
    (r"leach",                                                    "leaching-vessel"),
    (r"roast",                                                    "roaster"),
    (r"\bconverter\b",                                            "converter"),
    (r"refin",                                                    "refining-furnace"),
    (r"melt",                                                     "melting-furnace"),
    (r"anneal|galvaniz|reheat|\bsoaking pit\b|\bfurnace\b|"
     r"\bburner\b|\bcalciner\b",                                  "furnace"),
    (r"\bovens?\b",                                                "oven"),
    (r"pasteuris|\bpaust\b",                                       "pasteurizer"),
    (r"stock preparation|\bpulpers?\b|pulping",                    "pulper"),
    (r"\bcip\b|clean[- ]in[- ]place|\bcleaning\b",                 "cleaning-system"),
    (r"energy management|preventative maintenance|good practice|"
     r"improve shutdown|shutdown during production|housekeeping|"
     r"^ ?(sub)?sector ?$|undefined sector",                       "management-system"),
    (r"integrated steelworks",                                     "blast-furnace"),
    (r"steam system",                                              "boiler"),
    (r"\bwires?\b",                                                "rolling-mill"),
    (r"benzene separation|dividing wall column",                   "distillation-column"),
    (r"otswald|ostwald|nitric acid",                               "reactor"),
    (r"\bdigesters?\b",                                           "digester"),
    (r"paper machine|\bpaper\b",                                  "paper-machine"),
    (r"\bpress\b|pressing",                                       "press"),
    (r"\bdry(ing|er)?\b",                                         "dryer"),
    (r"evaporat",                                                 "evaporator"),
    (r"distillat",                                                "distillation-column"),
    (r"air separation|air compression and distillation|\basu\b",  "air-separation-unit"),
    (r"\bccs\b|carbon capture|\bcapture\b",                       "capture-unit"),
    # before the generic compressor rule, or a rotary compression HEATER
    # is read as a compressor
    (r"rotary compression",                                       "rotary-compression-heater"),
    (r"\bcompressors?\b|\bcomp\b|compression|compressed air",     "compressor"),
    (r"\bpumps?\b|vacuum system",                                 "pump"),
    (r"\bfans?\b|\bblowers?\b",                                   "fan"),
    (r"\bconveyors?\b|\bbelt\b|conveyance",                      "conveyor"),
    (r"\bmotors?\b|\bdrives?\b",                                  "motor"),
    (r"\blighting\b|\blights\b|\bluminaire",                                 "lighting"),
    (r"space cooling|\bchiller\b|refrigerat|air condition",       "chiller"),
    (r"space heat",                                               "hvac-heater"),
    (r"ventilat",                                                 "ventilation-unit"),
    (r"\bfermenter\b|fermentation",                               "fermenter"),
    (r"transesterif",                                             "transesterification-unit"),
    (r"anaerobic",                                                "anaerobic-digester"),
    (r"resistance heat",                                          "resistance-heater"),
    (r"induction",                                                "induction-heater"),
    # Novel electric heating. These six terms were declared in design doc 6.2
    # for the heat roster but never given a pattern, so no source could ever
    # match them. Added 2026-08-29 for the IEA Clean Energy Technology Guide,
    # which profiles all of them. They sit AFTER electric-arc-furnace above, so
    # "electric arc and plasma arc furnaces" stays an arc furnace.
    (r"microwave",                                                "microwave-heater"),
    (r"radio ?wave|radio.?frequency|\brf heating\b",              "radio-frequency-heater"),
    (r"ultra.?violet|\buv (curing|heating)\b",                    "ultraviolet-curer"),
    (r"photochemical",                                            "photochemical-heater"),
    (r"plasma torch|plasma arc|plasma heat",                      "plasma-torch"),
    (r"arc heater",                                               "arc-heater"),
    (r"\bdirect heat\b|direct fired",                             "direct-heater"),
]

# --- variant detection: all matches accumulate, then are ranked -------------
VARIANT = [
    (r"\bccs\b|carbon capture|\+ ?ccs",              "ccs"),
    (r"top gas recycl|\btgr\b",                       "top-gas-recycling"),
    (r"\bhisarna\b",                                 "hisarna"),
    (r"\bmidrex\b",                                  "midrex"),
    (r"\bulcored\b",                                 "ulcored"),
    (r"\bulcowin\b",                                 "ulcowin"),
    (r"oxy[- ]?fuel|oxy[- ]?combustion",             "oxyfuel"),
    (r"post[- ]combustion",                          "post-combustion"),
    (r"pre[- ]combustion",                           "pre-combustion"),
    (r"\bbat\b|best available",                      "bat"),
    (r"\bcogen\w*\b|\bchp\b|\bbpst\b|\bhrsg\b|h:p ratio", "chp"),
    (r"\bretrofit\b",                                "retrofit"),
    (r"variable speed|\bvsd\b|\basds?\b|speed ctrl", "variable-speed"),
    (r"\bpreheat\b|scrap preheat",                   "preheat"),
    (r"semi[- ]dry",                                 "semi-dry"),
    (r"semi[- ]wet",                                 "semi-wet"),
    (r"\bdry process\b|\bdry kiln\b",                "dry"),
    (r"\bwet process\b|\bwet kiln\b",                "wet"),
    (r"\btes\b|thermal (energy )?storage",           "tes"),
]
# efficiency tier -- CIMS's own wording, mapped to the section 6.2 buckets
EFF = [
    (r"\bmost eff\w*\b|\bhigh eff\w*\b|\bultra power\b|\bhigh power\b", "efficiency-strong"),
    (r"\bmore eff\w*\b|\bmed eff\w*\b|\beff\w*\b|\befficient\b",        "efficiency-moderate"),
    (r"\bstd\b|\bstandard\b|\blow eff\w*\b|\bbase\b|\bconventional\b",  "efficiency-base"),
]
# variant precedence when several fire: process route beats capture beats
# configuration beats efficiency tier
RANK = ["hisarna", "midrex", "ulcored", "ulcowin", "top-gas-recycling", "oxyfuel",
        "post-combustion", "pre-combustion", "ccs", "chp", "retrofit", "bat",
        "dry", "wet", "semi-dry", "semi-wet", "tes", "preheat", "variable-speed",
        "efficiency-strong", "efficiency-moderate", "efficiency-base"]

# --- end use, from the CIMS service name -----------------------------------
END_USE = [
    (r"\bsteam\b|\bboiler\b|\bcogen\b|\bchp\b",                    "steam-and-hot-water"),
    (r"\bdirect heat\b|\bheat\b|\bkiln|\bsmelt|\bmelt|\bcalcin|"
     r"\breheat|\banneal|\broast|\brefine\b|\bfurnace\b",          "process-heat-high-temp"),
    (r"\bdry|\bevaporat|\bseparation\b|\bdistil",                  "drying-and-separation"),
    (r"\bventilation\b|\blighting\b|\bspace heating\b|"
     r"\bspace cooling\b|\bhvac\b",                                "facility-services"),
    (r"\bconveyance\b|\bdirect drive\b|\bpump|\bcompress|\bfan\b|"
     r"\bmotor\b|\bsize \d",                                       "machine-drive"),
    (r"\bcooling\b|\brefrigerat",                                  "refrigeration-and-cooling"),
    (r"\bcasting\b|\bmill\b|\bfinish|\bgalvaniz|\bform\b|"
     r"\bcold roll\b|\brolling\b|\bskin pass\b|\btube",            "forming-and-finishing"),
    (r"\bagglomerat|\bsinter|\bgrinding\b|\bcrush|\bcleaning\b",   "material-preparation"),
    (r"\belectroly|\bhydro metallurgy\b",                          "electrochemical"),
    (r"\bintegrated\b|\bsmelt\b|\bproduction\b|\bprocessing\b|"
     r"\bextraction\b|\brefine\b|\bleach|\bin-situ\b",             "material-conversion"),
]

_EFFWORDS = re.compile(r"\b(std|standard|low|med|medium|high|more|most|eff|efficient|"
                       r"efficiency|base|new|adv|advanced|conventional)\b")


def _core(name: str) -> str:
    """A technology name stripped of efficiency wording, for deciding whether
    two CIMS rows are the same device or two different sub-types."""
    n = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    n = _EFFWORDS.sub(" ", n)
    return re.sub(r"\s+", " ", n).strip()


SECTOR = {
    "Iron and Steel": "iron-and-steel", "Metal Smelting": "non-ferrous-metals",
    "Industrial Minerals": "non-metallic-minerals", "Chemical Products": "chemicals",
    "Pulp and Paper": "pulp-and-paper", "Petroleum Refining": "petroleum-refining",
    "Mining": "mining", "Coal Mining": "mining", "Light Industrial": "other-industry",
    "Construction": "other-industry", "Petroleum Crude": "other-industry",
    "Natural Gas": "other-industry", "Ethanol": "chemicals", "Biodiesel": "chemicals",
    "Hydrogen": "chemicals", "Waste": "other-industry",
}


def vocabularies() -> dict[str, set[str]]:
    """The extraction-name vocabularies (equipment, carrier, variant)."""
    out: dict[str, set[str]] = {"equipment": set(), "carrier": set(), "variant": set()}
    with VOCAB.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["list"], set()).add(r["term"])
    return out


NEGATED = re.compile(r"\b(non|no|without)\b[ -]?$")


def first(rules, text):
    """First rule whose pattern matches, skipping matches immediately preceded
    by a negation ('Non electrolysis' is not an electrolysis cell)."""
    for pat, term in rules:
        for m in re.finditer(pat, text):
            if NEGATED.search(text[:m.start()]):
                continue
            return term
    return ""


def classify(sector, service, tech):
    t = " " + re.sub(r"[^a-z0-9:+ ]", " ", tech.lower()) + " "
    t = re.sub(r"\s+", " ", t)
    s = " " + re.sub(r"[^a-z0-9 ]", " ", service.lower()) + " "
    both = t + s

    equipment = first(EQUIPMENT, t) or first(EQUIPMENT, s)
    carrier = first(CARRIER, t)
    # The negation guard has to cover variants too: "TGR-BF steelworks without
    # CCS" and "... with CCS" are different technologies, and matching \bccs\b
    # in both collapses them onto one name.
    def hit(pat, text):
        for m in re.finditer(pat, text):
            if not NEGATED.search(text[:m.start()]):
                return True
        return False

    hits = {term for pat, term in VARIANT if hit(pat, both)}
    eff = first(EFF, t)
    if eff and not hit(next(p for p, e in EFF if e == eff), t):
        eff = ""
    if eff:
        hits.add(eff)
    # A process route AND capture is one compound variant, hyphenated inside
    # the single variant component (design doc D4) -- otherwise "TGR-BF with
    # CCS" and "TGR-BF without CCS" collapse onto the same name.
    ROUTES = ("hisarna", "midrex", "ulcored", "ulcowin", "top-gas-recycling", "oxyfuel")
    route = next((r for r in ROUTES if r in hits), "")
    if route and "ccs" in hits:
        variant = route + "-ccs"
    else:
        variant = next((v for v in RANK if v in hits), "")
    end_use = first(END_USE, s) or first(END_USE, t) or "other-services"

    notes, conf, kind = [], "high", "technology"
    ELECTRIC_BY_TYPE = ("motor", "pump", "fan", "compressor", "conveyor", "lighting",
                        "chiller", "ventilation-unit", "electrolysis-cell")
    if not equipment:
        if carrier:
            # CIMS models a fuel choice as a technology at some nodes ('NG',
            # 'Electric', 'H2', 'Renewable Natural Gas'). There is no device to
            # name: in the harmonized layer these are tech-flow input rows on
            # the parent technology, not technologies of their own.
            kind, conf = "fuel-node", "high"
            notes.append("CIMS models a fuel choice as a technology here; no device is named")
        else:
            kind, conf = "unmapped", "low"
            notes.append("no equipment or carrier keyword matched")
    elif not carrier:
        if equipment in ELECTRIC_BY_TYPE:
            carrier, conf = "electricity", "medium"
            notes.append("carrier inferred as electricity from the equipment type")
        else:
            conf = "medium"
            notes.append("carrier not named; the fuel is set by the parent service node, "
                         "so the technology name is left at one component")
    if len(hits) > 1:
        notes.append("several variants matched (" + ", ".join(sorted(hits)) + "); "
                     "highest-ranked kept")
    return equipment, carrier, variant, end_use, conf, "; ".join(notes), kind


def main() -> int:
    vocab = vocabularies()
    src = HERE / "cims-roster.csv"
    if not src.exists():
        sys.exit("cims-roster.csv not found -- run extract-cims-roster.py first")
    rows = list(csv.DictReader(src.open(encoding="utf-8")))

    out, bad = [], []
    for r in rows:
        sector_key = SECTOR.get(r["cims-sector"], "")
        equipment, carrier, variant, end_use, conf, note, kind = classify(
            r["cims-sector"], r["cims-service"], r["cims-technology"])
        name = "_".join(x for x in (equipment, carrier, variant) if x) if kind == "technology" else ""
        for slot, term in (("equipment", equipment), ("carrier", carrier), ("variant", variant)):
            if term and term not in vocab[slot]:
                bad.append(f"{term!r} is not in the {slot} vocabulary "
                           f"(from {r['cims-technology']!r})")
        if not sector_key:
            action = "out-of-scope"          # residential, commercial, transport, electricity
        elif kind == "fuel-node":
            action = "fuel-node"
        elif kind == "unmapped":
            action = "review"
        else:
            action = "retain"
        step = re.sub(r"[^a-z0-9]+", "-", r["cims-service"].lower()).strip("-")
        out.append({
            "cims-sector": r["cims-sector"], "cims-service": r["cims-service"],
            "cims-technology": r["cims-technology"], "cims-branch": r["cims-branch"],
            "regions": r["regions"], "cims-parameters": r["parameters"],
            "sector": sector_key, "end-use": end_use, "process-step": step,
            "equipment": equipment,
            "energy-carrier": carrier, "variant": variant, "technology": name,
            "confidence": conf, "action": action, "duplicate-of": "", "note": note,
        })

    # mark rows whose proposed name collides -- the same CIMS service reaching
    # the same harmonized name means the two CIMS rows are the same technology
    seen: dict[tuple, str] = {}
    for r in out:
        if not r["technology"] or r["action"] == "out-of-scope":
            continue
        k = (r["sector"], r["end-use"], r["process-step"], r["technology"])
        if k in seen:
            r["duplicate-of"] = seen[k]
            if _core(r["cims-technology"]) == _core(seen[k]):
                r["action"] = "merge"
                r["note"] = (r["note"] + "; " if r["note"] else "") + \
                            f"same service node and name as {seen[k]!r}; differs only by " \
                            "efficiency wording, which the variant already carries"
            else:
                r["action"] = "merge-review"
                r["note"] = (r["note"] + "; " if r["note"] else "") + \
                            f"collapses onto {seen[k]!r}: CIMS draws a sub-type distinction " \
                            "the harmonized name does not carry. Either add a variant term " \
                            "or accept the merge"
        else:
            seen[k] = r["cims-technology"]

    dst = HERE / "cims-map.csv"
    with dst.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    if bad:
        print(f"{len(bad)} vocabulary violations:")
        for b in sorted(set(bad))[:20]:
            print("  " + b)
        return 1
    import collections
    c = collections.Counter(r["action"] for r in out)
    q = collections.Counter(r["confidence"] for r in out)
    print(f"{len(out)} CIMS technologies mapped -> {dst.name}")
    print("  action:     " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    print("  confidence: " + ", ".join(f"{k}={v}" for k, v in sorted(q.items())))
    print(f"  distinct harmonized names: {len({r['technology'] for r in out if r['technology']})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
