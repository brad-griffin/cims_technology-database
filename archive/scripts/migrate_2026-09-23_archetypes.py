"""One-time migration (2026-09-23): the design tables and the adopted roster
become the archetype records in data/harmonized/records/.

Run once from the repo root, on the tree tagged `pre-archetype-restructure`
(plus the pipeline package): it reads the outputs of the retired pipeline and
writes the hand-edited records that replace it. Kept here as the record of how
every archetype, service link and example mapping was seeded; it is not part
of the build and is not meant to be run again.

Writes
  records/archetype.csv            one row per archetype (from the design
                                   technology table, grouped by label)
  records/archetype-service.csv    archetype x hierarchy path (or pattern)
  records/family.csv               display families
  records/hierarchy-annotation.csv the sector/end-use table, keyed on the
                                   hierarchy paths each end use was made of
  records/source-example.csv       every example -> its archetype
  records/vocabulary/{equipment,discriminator,modifier,carrier,lists}.csv
  archive/scripts/archetype-renames-2026-09-23.csv   old -> new key, reason
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
DB = ROOT / "data" / "harmonized"
sys.path.insert(0, str(DB))
from pipeline import extract, facts  # noqa: E402
from pipeline.common import read, write, split_list  # noqa: E402

DESIGN = ROOT / "design"
REC = DB / "records"
VOC = REC / "vocabulary"
HIER = REC / "cims_hierarchy.csv"

# ---------------------------------------------------------------------------
# 1. Renames. Reason codes:
#    T  the discriminator was cut short or garbled by the label-to-name rule
#    E  the equipment term named the wrong device
#    M  a capture or efficiency step moves to the modifier slot, after the
#       host's own discriminator
#    D  the discriminator only repeated the equipment
# ---------------------------------------------------------------------------
RENAME = {
 "adsorber_pressure-vacuum": ("adsorber_pressure-swing", "T"),
 "air-separation-unit_cryogenic-separation": ("capture-unit_cryogenic-condensation", "E"),
 "capture-unit_cryogenic-post": ("capture-unit_cryogenic-flue-gas", "T"),
 "anaerobic-digester_digestion-upgrading": ("anaerobic-digester_biomethane-upgrading", "T"),
 "autothermal-reformer_reforming-full": ("autothermal-reformer_ccs-concentrated", "M"),
 "blast-furnace_top-gas": ("blast-furnace_top-gas-recycling", "T"),
 "boiler_electric-generation": ("boiler_electric-injection-steam", "T"),
 "boiler_high-solids": ("boiler_recovery-high-solids", "T"),
 "calciner_electrified-indirectly": ("calciner_indirect", "T"),
 "capture-unit_amine-post": ("capture-unit_amine", "T"),
 "capture-unit_liquid-solvent": ("capture-unit_dac-liquid-solvent", "T"),
 "capture-unit_solid-sorbent-dac": ("capture-unit_dac-solid-sorbent", "T"),
 "chiller_packaged-air": ("chiller_packaged", "T"),
 "coke-oven_product-battery": ("coke-oven_by-product", "T"),
 "combustion-turbine_engine-simple": ("combustion-turbine_simple-cycle", "T"),
 "combined-cycle_efficiency-moderate": ("combustion-turbine_simple-cycle_efficiency-moderate", "E"),
 "combustion-turbine_engine-drive": ("combustion-turbine_drive", "T"),
 "combustion-turbine_efficiency-moderate": ("combustion-turbine_drive_efficiency-moderate", "M"),
 "combustion-turbine_high-efficiency": ("combustion-turbine_drive-high-efficiency", "T"),
 "compressor_boil-off": ("compressor_boil-off-recovery", "T"),
 "compressor_dehydration-compression": ("compressor_co2-dehydration", "T"),
 "compressor_electric-drive": ("compressor_electric-drive-centrifugal", "T"),
 "compressor_electric-drive-compression": ("compressor_electric-drive-reciprocating", "T"),
 "compressor_gas-turbine": ("compressor_gas-turbine-drive", "T"),
 "compressor_reciprocating-gas": ("compressor_gas-engine-drive", "T"),
 "compressor_station-waste": ("heat-recovery-unit_compressor-station-power", "E"),
 "converter_continuous-converting": ("converter_continuous", "D"),
 "conveyor_pit-crushing": ("conveyor_in-pit-crushing", "T"),
 "conveyor_place-truck": ("conveyor_overland", "T"),
 "digester_bayer-digestion": ("digester_bayer", "D"),
 "digester_biomass-fired": ("digester_bayer-biomass", "T"),
 "digester_electrified-bayer": ("digester_bayer-electric", "T"),
 "digester_hydrogen-bayer": ("digester_bayer-hydrogen", "T"),
 "direct-heater_electric-heat": ("direct-heater_mine-air-electric", "T"),
 "direct-heater_fixed-flow": ("direct-heater_mine-air-fired", "T"),
 "direct-heater_fuel-space": ("space-heater_fuel-fired", "E"),
 "direct-heater_hot-press": ("press_hot-platen", "E"),
 "direct-heater_indirect-oven": ("oven_indirect-fired", "E"),
 "direct-heater_tunnel-deck": ("oven_tunnel-deck", "E"),
 "direct-heater_dryer-curing": ("dryer_direct-fired", "E"),
 "direct-heater_rotary-dryer": ("dryer_rotary-direct-fired", "E"),
 "direct-heater_rotary-fluid": ("dryer_rotary-fluid-bed", "E"),
 "direct-heater_spray-drum": ("dryer_spray-drum-belt", "E"),
 "direct-heater_veneer-strand": ("dryer_veneer-strand", "E"),
 "direct-heater_electric-air": ("dryer_electric-air", "E"),
 "distillation-column_progressive-divided": ("distillation-column_progressive", "T"),
 "dryer_electric-heat": ("dryer_electric", "T"),
 "dryer_kiln-waste": ("dryer_kiln-waste-heat", "T"),
 "dryer_lime-kiln": ("kiln_lime-product-cooler", "E"),
 "dryer_mechanical-dewatering": ("press_dewatering", "E"),
 "press_advanced-mechanical": ("press_dewatering-advanced", "T"),
 "electric-arc-furnace_plasma-heating": ("plasma-torch", "E"),
 "electric-arc-furnace_submerged": ("electric-arc-furnace_submerged-arc", "T"),
 "furnace_open-arc": ("electric-arc-furnace_open-arc-dc", "E"),
 "electrolysis-cell_low-temperature": ("electrolysis-cell_iron-electrowinning", "T"),
 "electrolysis-cell_membrane-chlor": ("electrolysis-cell_chlor-alkali-membrane", "T"),
 "electrolysis-cell_water-low-temperature": ("electrolyzer_low-temperature", "E"),
 "electrolysis-cell_solid-oxide": ("electrolyzer_solid-oxide", "E"),
 "evaporator_produced-water": ("evaporator_crystallizer", "T"),
 "furnace_efficiency-moderate": ("furnace_reheating_efficiency-moderate", "M"),
 "furnace_efficiency-strong": ("furnace_reheating_efficiency-strong", "M"),
 "furnace_reheating-fuel": ("furnace_reheating", "D"),
 "furnace_electrified-hydrogen": ("furnace_anode-baking-electric", "T"),
 "furnace_prebake-anode": ("furnace_anode-baking", "T"),
 "furnace_fuel-fired": ("furnace_heat-treatment", "T"),
 "furnace_homogenizing-furnaces": ("furnace_homogenizing", "D"),
 "furnace_hybrid-electric": ("furnace_glass-hybrid-electric", "T"),
 "furnace_oxy-fuel": ("furnace_glass-oxy-fuel", "T"),
 "heat-recovery-unit_air-fuel": ("furnace_glass-regenerative", "E"),
 "heat-recovery-unit_regenerative-oxy-fuel-melting": ("melting-furnace_regenerative-oxy-fuel", "E"),
 "heat-recovery-unit_regenerative-oxy-fuel-burner": ("furnace_regenerative-oxy-fuel", "E"),
 "heat-recovery-unit_regenerative-recuperative": ("furnace_regenerative-burners", "E"),
 "heat-recovery-unit_parallel-flow": ("kiln_lime-parallel-flow", "E"),
 "heat-recovery-unit_oxy-fuel": ("reactor_fluid-catalytic-cracking-oxy-fuel", "E"),
 "heat-recovery-unit_induration-cooler": ("pellet-plant_cooler-heat-recovery", "E"),
 "heat-recovery-unit_high-efficiency": ("dryer_hood-heat-recovery", "E"),
 "heat-recovery-unit_distillers-grain": ("dryer_distillers-grain", "E"),
 "heat-recovery-unit_continuous-kiln": ("kiln_lumber-continuous", "E"),
 "heat-recovery-unit_thermal-storage": ("thermal-storage_electric", "E"),
 "heat-recovery-unit_regenerative-pasteurizers": ("pasteurizer_regenerative", "E"),
 "heat-recovery-unit_turbine": ("heat-recovery-unit_turbine-exhaust", "T"),
 "induction-heater_electric-heat": ("induction-heater_heat-treatment", "T"),
 "induction-heater_heating": ("induction-heater", "D"),
 "kiln_ccs-diffuse": ("kiln_dry-precalciner_ccs-diffuse", "M"),
 "kiln_efficiency-moderate": ("kiln_dry-precalciner_efficiency-moderate", "M"),
 "kiln_efficiency-strong": ("kiln_dry-precalciner_efficiency-strong", "M"),
 "precalciner_dry-rotary": ("kiln_dry-precalciner", "E"),
 "kiln_rotary-lime": ("kiln_lime-rotary", "T"),
 "kiln_rotary-lime-with-preheater": ("kiln_lime-rotary-preheater", "T"),
 "kiln_dolomitic-lime": ("kiln_lime-dolomitic", "T"),
 "kiln_electrified-lime": ("kiln_lime-electric", "T"),
 "kiln_oxy-fuel-lime": ("kiln_lime-oxy-fuel", "T"),
 "gasifier_biomass-fired": ("kiln_lime-gasifier-fired", "E"),
 "kiln_electric": ("kiln_ceramic-electric", "T"),
 "kiln_hydrogen-fired": ("kiln_ceramic-hydrogen", "T"),
 "kiln_dehumidification-heat": ("kiln_lumber-heat-pump", "T"),
 "kiln_steam-thermal": ("kiln_lumber-steam", "T"),
 "leaching-vessel_situ": ("leaching-vessel_in-situ", "T"),
 "leaching-vessel_high-pressure": ("leaching-vessel_high-pressure-acid", "T"),
 "lighting_fluorescent-high": ("lighting_fluorescent-hid", "T"),
 "management-system_gas-driven": ("pneumatic-device_gas-driven", "E"),
 "melting-furnace_cupola-gas": ("melting-furnace_cupola", "T"),
 "melting-furnace_flash-smelting": ("smelting-vessel_flash", "E"),
 "mobile-equipment_diesel-non-road": ("mobile-equipment_diesel", "D"),
 "mobile-equipment_forklift": ("mobile-equipment_gas-forklift", "T"),
 "mobile-equipment_hydrogen-fuel": ("mobile-equipment_hydrogen-fuel-cell", "T"),
 "haul-truck_hydrogen-fuel": ("haul-truck_hydrogen-fuel-cell", "T"),
 "preheater_ladle-preheating": ("preheater_ladle", "D"),
 "press_compressed-air": ("compressor_air-system-management", "E"),
 "press_pipeline-compression": ("compressor_hydrogen-pipeline", "E"),
 "press_high-pressure-food": ("press_high-pressure-processing", "T"),
 "press_fourdrinier-gap": ("paper-machine_fourdrinier-gap", "E"),
 "process-improvement_ammonia-oxidation": ("reactor_nitric-acid", "E"),
 "process-improvement_nitric-acid": ("reactor_adipic-acid", "E"),
 "process-improvement_thermal-n2o": ("reactor_thermal-n2o-destruction", "E"),
 "process-improvement_electric-annealing": ("furnace_lehr-electric", "E"),
 "process-improvement_gas-fired": ("furnace_lehr", "E"),
 "process-improvement_hydrogen-liquefaction": ("liquefaction-train_hydrogen", "E"),
 "process-improvement_blending-into": ("process-improvement_hydrogen-blending", "T"),
 "process-improvement_drag-reducing": ("process-improvement_drag-reducing-agent", "T"),
 "process-improvement_log-chip": ("process-improvement_log-thawing", "T"),
 "process-improvement_landfill-gas": ("process-improvement_landfill-gas-recovery", "T"),
 "pulper_low-energy": ("pulper_refiner-low-energy", "T"),
 "pulper_thermomechanical-pulping": ("pulper_thermomechanical", "D"),
 "radio-frequency-heater_electromagnetic-heating": ("radio-frequency-heater_electromagnetic", "D"),
 "radio-frequency-heater_microwave-assisted": ("radio-frequency-heater_baking", "T"),
 "radio-frequency-heater_microwave-drying": ("radio-frequency-heater_drying", "D"),
 "reactor_alcohol-jet": ("reactor_alcohol-to-jet", "T"),
 "reactor_methanol-jet": ("reactor_methanol-to-jet", "T"),
 "reactor_methanol-olefins": ("reactor_methanol-to-olefins", "T"),
 "reactor_bio-ethanol": ("reactor_ethanol-to-ethylene", "T"),
 "reactor_co2-methanol": ("reactor_co2-to-methanol", "T"),
 "reactor_delayed": ("reactor_delayed-coking", "T"),
 "reactor_fluid-flexi": ("reactor_fluid-coking", "T"),
 "reactor_electrolytic-hydrogen": ("reactor_haber-bosch-electrolytic", "T"),
 "reactor_low-pressure": ("reactor_haber-bosch-low-pressure", "T"),
 "reactor_fixed-bed": ("reactor_hydrotreating-fixed-bed", "T"),
 "reactor_hydroprocessing-hydrocracking": ("reactor_hydroprocessing", "D"),
 "reactor_hydrotreating-oils": ("reactor_hydrotreating-lipids", "T"),
 "reactor_htgr": ("reactor_nuclear-htgr", "T"),
 "reactor_microreactor": ("reactor_nuclear-micro", "T"),
 "reactor_small-modular": ("reactor_nuclear-small-modular", "T"),
 "reciprocating-engine_electric-motor": ("motor_field-electric", "E"),
 "reciprocating-engine_gas-driven": ("reciprocating-engine_pump-drive", "T"),
 "resistance-heater_electric-furnace": ("resistance-heater_furnace", "D"),
 "resistance-heater_electric-space": ("resistance-heater_space", "D"),
 "rolling-mill_efficiency-moderate": ("rolling-mill_hot_efficiency-moderate", "M"),
 "roaster_electric-oven": ("oven_electric", "E"),
 "separator_membrane-separation": ("air-separation-unit_membrane", "E"),
 "separator_paraffinic-froth": ("separator_paraffinic-froth-treatment", "T"),
 "separator_hydrotransport-warm": ("separator_warm-water-extraction", "T"),
 "separator_sensor-ore": ("separator_ore-sorting", "T"),
 "separator_thickened-dry-stack-tailings": ("separator_dry-stack-tailings", "D"),
 "separator_paste-dry-stack": ("separator_paste-tailings", "T"),
 "shaft-furnace_ccs-concentrated": ("shaft-furnace_direct-reduction_ccs-concentrated", "M"),
 "shaft-furnace_fluidized-bed-direct-reduction": ("reactor_fluidized-bed-direct-reduction", "E"),
 "smelting-vessel_top-submerged": ("smelting-vessel_top-submerged-lance", "T"),
 "smelting-vessel_smelter-power": ("electrolysis-cell_power-modulation", "E"),
 "steam-cracker_electrified-furnace": ("steam-cracker_electric", "D"),
 "steam-cracker_rotodynamic-reactor": ("steam-cracker_rotodynamic", "D"),
 "steam-reformer_reforming-haber": ("steam-reformer_ammonia", "T"),
 "steam-reformer_ccs-concentrated": ("steam-reformer_methane_ccs-concentrated", "M"),
 "vapour-recompressor_mechanical": ("vapour-recompressor", "D"),
 "vapour-recompressor_mechanical-evaporation": ("vapour-recompressor_evaporation", "D"),
 "vapour-recompressor_distillation-mechanical": ("vapour-recompressor_distillation", "D"),
 "ventilation-unit_demand": ("ventilation-unit_mine-on-demand", "T"),
 "gasifier_biomass-waste-methanol": ("gasifier_biomass-methanol", "T"),
 "gasifier_coal-petroleum": ("gasifier_coal-petroleum-coke", "T"),
 "grinding-mill_high-pressure": ("grinding-mill_high-pressure-rolls", "T"),
 "grinding-mill_stirred-fine": ("grinding-mill_stirred", "D"),
 "gas-treatment-unit_advanced-acid": ("gas-treatment-unit_acid-gas-advanced", "T"),
 "gas-treatment-unit_claus-sulphur": ("gas-treatment-unit_claus", "D"),
}
REASON = {"T": "discriminator cut short or garbled", "E": "equipment named the wrong device",
          "M": "capture or efficiency step moved to the modifier slot",
          "D": "discriminator repeated the equipment"}
NEW_EQUIPMENT = {"thermal-storage": "An energy store charged with heat or electricity and discharged as steam or hot gas.",
                 "pneumatic-device": "A gas- or air-driven controller, actuator or pump at a well site or facility."}

MODIFIERS = [("efficiency-moderate", 1, "A bucket of measures on the host saving up to about 15% of its energy use."),
             ("efficiency-strong", 2, "A bucket of measures on the host saving more than about 15% of its energy use."),
             ("ccs-concentrated", 3, "The host with CO2 capture on a concentrated stream; the capture plant itself is a capture-unit archetype."),
             ("ccs-diffuse", 4, "The host with CO2 capture on a dilute flue gas; the capture plant itself is a capture-unit archetype."),
             ("retrofit", 5, "The step fitted to existing stock rather than built new.")]

# family of each cross-sector end use; a sector end use's family is its sector
FAMILY_OF = {"heat-low-temp": "heat-supply", "heat-medium-temp": "heat-supply",
             "heat-high-temp": "heat-supply", "on-site-power-generation": "power-generation",
             "pumps": "machine-drive", "fans-and-blowers": "machine-drive",
             "compressed-air": "machine-drive", "materials-handling": "machine-drive",
             "materials-processing": "machine-drive", "space-heating": "space-conditioning",
             "space-cooling": "space-conditioning", "lighting": "lighting",
             "mobile-equipment": "mobile-equipment", "co2-capture-concentrated": "co2-capture",
             "co2-capture-diffuse": "co2-capture", "direct-air-capture": "co2-capture"}
FAMILIES = [
 ("heat-supply", "service", "Heat supply", "Separable systems that raise steam, hot water, thermal oil or hot gas for a process: boilers, CHP, heat pumps, electric and solar heat, fired heaters. The temperature band an archetype reaches is its heat-tier."),
 ("power-generation", "service", "On-site power generation", "Electricity-only generation at an industrial site."),
 ("machine-drive", "service", "Machine drive", "Motors, drives and the systems they turn: pumps, fans and blowers, compressed air, materials handling and processing."),
 ("space-conditioning", "service", "Space conditioning", "Space heating, cooling and ventilation of industrial buildings."),
 ("lighting", "service", "Lighting", "Industrial lighting."),
 ("mobile-equipment", "service", "Mobile equipment", "Off-road vehicles and mobile machinery at a site."),
 ("co2-capture", "service", "CO2 capture", "Capture plants on concentrated or dilute streams, and direct air capture. The stream is the hierarchy node an archetype serves."),
]
STEAM_SERVICE_EXCLUDE = {"direct-heater", "furnace", "induction-heater", "resistance-heater",
                         "plasma-torch", "microwave-heater", "radio-frequency-heater", "oven",
                         "space-heater"}
HEAT_TIER = {"heat-low-temp": "low-temp", "heat-medium-temp": "medium-temp",
             "heat-high-temp": "high-temp"}


def parse(name, modifiers):
    p = name.split("_")
    mods = []
    while len(p) > 1 and p[-1] in modifiers:
        mods.insert(0, p.pop())
    return p[0], "_".join(p[1:]), mods


def _tokens(text):
    return {w for w in re.split(r"[^a-z0-9]+", text.lower()) if len(w) >= 3}


def words_match(a, leaves):
    """Leaves whose distinguishing words appear in the archetype's key or label.
    Words every leaf shares say nothing, so only the differences count."""
    segs = {b: _tokens(".".join(b.split(".")[2:])) for b in leaves}
    common = set.intersection(*segs.values()) if segs else set()
    mine = _tokens(a["archetype"] + " " + a["label"])
    stems = {w[:5] for w in mine}
    hit = [b for b, t in segs.items()
           if any(w in mine or w[:5] in stems for w in t - common)]
    return hit if 0 < len(hit) < len(leaves) else []


def product_unit(su):
    s = (su or "").strip()
    if s.startswith("GJ"):
        return "GJ"
    if s.startswith("t CO2"):
        return "t"
    if s.startswith(("t ", "t")) or s.startswith("L or t"):
        return "t"
    if s.startswith("m3"):
        return "m3"
    if s.startswith("m drilled"):
        return "m"
    return s


def main():
    if (REC / "archetype.csv").exists() and "--force" not in sys.argv:
        sys.exit("records/archetype.csv exists: the records are hand-edited now and this "
                 "migration would overwrite them. It ran once, on 2026-09-23.")
    tt = read(DESIGN / "end-use-technology-table.csv")
    seu = {r["end-use"]: r for r in read(DESIGN / "sector-end-use-table.csv")}
    seu_order = [r["end-use"] for r in read(DESIGN / "sector-end-use-table.csv")]
    xw = read(DESIGN / "cims-hierarchy-crosswalk.csv")
    techs = read(DB / "technology.csv")
    apps = read(DB / "technology-application.csv")
    hier = [r["branch"] for r in read(HIER)]
    hset = set(hier)
    vocab = read(DB / "vocabulary.csv")

    name_of = {t["technology-label"]: t["technology"] for t in techs}
    import design_names_hand
    for a, b in design_names_hand.MERGE_LABEL.items():
        name_of.setdefault(a, name_of.get(b))
    trow = {t["technology"]: t for t in techs}
    new = lambda old: RENAME.get(old, (old, ""))[0]
    newnames = [new(t["technology"]) for t in techs]
    dup = [k for k, v in collections.Counter(newnames).items() if v > 1]
    assert not dup, f"renames collide: {dup}"
    mods = {m for m, _, _ in MODIFIERS}

    # ---- end use -> hierarchy leaves ---------------------------------------
    leaves = collections.defaultdict(list)
    for r in xw:
        for e in split_list(r["end-use"]):
            leaves[e.split("/", 1)[1]].append(r["branch"])

    # ---- archetypes -----------------------------------------------------
    rows_by = collections.defaultdict(list)
    for r in tt:
        rows_by[name_of[r["technology"]]].append(r)
    arche = []
    for old, rows in rows_by.items():
        t = trow[old]
        key = new(old)
        first = rows[0]
        eus = [r["end-use"] for r in rows]
        fam = FAMILY_OF.get(eus[0], first["sector"])
        tiers = [HEAT_TIER[e] for e in eus if e in HEAT_TIER]
        notes = []
        for r in rows:
            if r["note"] and r["note"] not in [n.split("] ", 1)[-1] for n in notes]:
                notes.append(r["note"] if len(rows) == 1 else f"[{r['end-use']}] {r['note']}")
        uniq = lambda col: "; ".join(dict.fromkeys(x for r in rows for x in split_list(r[col])))
        arche.append({
            "archetype": key, "label": first["technology"], "family": fam,
            "type": first["type"], "carriers": t["energy-carrier"],
            "heat-tier": "; ".join(dict.fromkeys(tiers)),
            "product-unit": product_unit(seu[eus[0]]["service-unit"]),
            "product": seu[eus[0]]["service-unit"],
            "trl": first["trl"], "trl-basis": first["trl-basis"],
            "description": first["description"],
            "examples-named": uniq("examples"), "sources": uniq("sources"),
            "note": " ".join(notes), "_eus": eus, "_old": old, "_equip": parse(key, mods)[0]})
    fam_order = [f for f, *_ in FAMILIES] + list(dict.fromkeys(
        r["sector"] for r in read(DESIGN / "sector-end-use-table.csv") if r["sector"] != "cross-sector"))
    arche.sort(key=lambda a: (fam_order.index(a["family"]), a["archetype"]))

    # ---- archetype -> hierarchy paths --------------------------------------
    # sectors whose hierarchy has each service suffix, for collapsing to a pattern
    by_suffix = collections.defaultdict(set)
    for b in hier:
        p = b.split(".")
        if len(p) > 2 and p[0] == "<sector>":
            by_suffix[".".join(p[2:])].add(p[1])
    chosen = collections.defaultdict(set)   # (tech, end use) -> leaves a source chose
    nodes_eu = {}
    for a in apps:
        if a["note"].startswith("design table placement") or "expanded" in a["note"]:
            continue
        chosen[(a["technology"], a["end-use"])].add("<sector>." + a["process-step"])
    sys.path.insert(0, str(DB))
    import design_crosswalk as dcw
    svc, review = [], []
    for a in arche:
        paths = []
        for r in rows_by[a["_old"]]:
            eu, sector = r["end-use"], r["sector"]
            ls = list(leaves[eu])
            how = "every leaf of the end use"
            if eu in HEAT_TIER:
                steam = a["_equip"] not in STEAM_SERVICE_EXCLUDE
                ls = [b for b in ls if b.endswith(".steam") == steam] or ls
                how = "steam leaves" if steam else "direct-heat leaves"
            elif len(ls) > 1 and sector != "cross-sector":
                rule = dcw.LEAF_BY_EQUIPMENT.get((sector, eu), {}).get(a["_equip"])
                pick = [b for b in ls if rule and b.endswith("." + rule)]
                src = [b for b in ls if b in chosen.get((a["_old"], eu), set())]
                words = words_match(a, ls)
                if pick:
                    ls, how = pick, "the device's route"
                elif words:
                    ls, how = words, "the leaf its name or label names"
                elif src:
                    ls, how = src, "the leaves its sources placed it on"
                else:
                    review.append((a["archetype"], eu, len(ls)))
                    how = f"every leaf of {sector}/{eu}; no evidence to narrow it"
            for b in ls:
                if b not in [p for p, _ in paths]:
                    paths.append((b, f"{sector}/{eu}: {how}"))
        # collapse a service repeated in every sector that has it into a pattern
        out, used = [], set()
        groups = collections.defaultdict(list)
        for b, note in paths:
            p = b.split(".")
            if len(p) > 3 and p[0] == "<sector>":
                groups[(".".join(p[2:]), note)].append((b, p[1]))
        for (suf, note), items in groups.items():
            secs = {s for _, s in items}
            if len(secs) > 1 and secs == by_suffix[suf]:
                out.append({"archetype": a["archetype"], "branch": f"<sector>.*.{suf}",
                            "note": note})
                used.update(b for b, _ in items)
        for b, note in paths:
            if b not in used:
                out.append({"archetype": a["archetype"], "branch": b, "note": note})
        svc.extend(out)

    # ---- hierarchy annotation ------------------------------------------------
    ann = []
    for eu in seu_order:
        r = seu[eu]
        bs = leaves[eu]
        groups = collections.defaultdict(set)
        for b in bs:
            p = b.split(".")
            groups[".".join(p[2:])].add(p[1])
        pats = []
        for b in bs:
            p = b.split(".")
            suf = ".".join(p[2:])
            if r["sector"] == "cross-sector" and len(groups[suf]) > 1 and groups[suf] == by_suffix[suf]:
                pat = f"<sector>.*.{suf}"
            else:
                pat = b
            if pat not in pats:
                pats.append(pat)
        shares = {x["branch"]: x["share"] for x in xw}
        part = [b for b in bs if shares.get(b) == "part"]
        ann.append({"annotation": eu, "branches": "; ".join(pats), "sector": r["sector"],
                    "label": r["end-use-label"], "covers": r["covers"],
                    "service-unit": r["service-unit"], "heat-tier": r["heat-tier"],
                    "heat-demand-temp": r["heat-demand-temp"], "steam": r["steam"],
                    "draws-on": r["draws-on"], "energy-inputs": r["energy-inputs"],
                    "shared-nodes": "; ".join(part), "note": r["note"], "sources": r["sources"]})
    for role, label, covers in (
            ("fuel-blend", "Fuel blending", "Nodes that blend a commodity into supply. No technology serves them."),
            ("fuel-routing", "By-product fuel routing", "By-product fuels whose heat is counted on the steam, reheating and direct-heat nodes they feed."),
            ("demand", "Light-industry demand nodes", "Product nodes that request heat, refrigeration, steam and machine drive; those services carry the energy."),
            ("feedstock", "Agricultural feedstock", "Feedstock supply to biofuels.")):
        bs = [x["branch"] for x in xw if x["role"] == role]
        groups = collections.defaultdict(set)
        for b in bs:
            p = b.split(".")
            groups[".".join(p[2:])].add(p[1])
        pats = []
        for b in bs:
            p = b.split(".")
            suf = ".".join(p[2:])
            pat = f"<sector>.*.{suf}" if len(groups[suf]) > 1 and groups[suf] == by_suffix[suf] else b
            if pat not in pats:
                pats.append(pat)
        ann.append({"annotation": role, "branches": "; ".join(pats), "sector": "",
                    "label": label, "covers": covers, "service-unit": "",
                    "heat-tier": "", "heat-demand-temp": "", "steam": "", "draws-on": "",
                    "energy-inputs": "", "shared-nodes": "", "note": "not served by the database",
                    "sources": ""})

    # ---- vocabularies --------------------------------------------------------
    used_eq = collections.Counter(a["_equip"] for a in arche)
    eq_terms = [r["term"] for r in vocab if r["list-name"] == "equipment"] + list(NEW_EQUIPMENT)
    eq = []
    for term in sorted(set(eq_terms)):
        labels = [a["label"] for a in arche if a["_equip"] == term][:3]
        eq.append({"equipment": term,
                   "definition": NEW_EQUIPMENT.get(term, ""),
                   "examples": "; ".join(labels), "note": "" if used_eq[term] else "no archetype uses it"})
    disc = collections.defaultdict(list)
    for a in arche:
        d = parse(a["archetype"], mods)[1]
        if d:
            disc[d].append(a)
    dis = [{"discriminator": d, "definition": "; ".join(dict.fromkeys(a["label"] for a in v)),
            "reviewed": "no"} for d, v in sorted(disc.items())]
    lists = [{"list": r["list-name"], "term": r["term"], "note": r["note"]} for r in vocab
             if r["origin"] == "declared-here" and r["list-name"] not in
             ("commodity", "end-use", "parameter", "sector", "role", "relationship-to-baseline",
              "heat-output-type", "service-type", "status")]
    lists += [{"list": "type", "term": t, "note": n} for t, n in (
        ("conventional", "the incumbent in Canadian stock"),
        ("efficient variant", "a major step on a conventional technology"),
        ("alternative", "commercial (TRL 9) but not common in Canada"),
        ("prospective", "TRL 5-8"))]
    lists += [{"list": "status", "term": t, "note": n} for t, n in (
        ("draft", "as extracted"), ("review", "needs a decision before it is pooled"),
        ("unquantified", "the source rates the option without a number"),
        ("final", "checked"), ("superseded", "kept for the record, not used"))]
    carriers = sorted({c for a in arche for c in split_list(a["carriers"])} |
                      {r["term"] for r in vocab if r["list-name"] == "carrier"}
                      - {"oxyfuel-ccs", "fossil"})

    # ---- examples -----------------------------------------------------------
    L = extract.load()
    facts.clean(L.facts, L.flows, L.cons)
    old_by_rec = {}
    for fn in ("tech-parameter.csv", "tech-flow.csv", "tech-constraint.csv"):
        for r in read(DB / fn):
            old_by_rec[r["record-id"]] = r["technology"]
    ex_arch = collections.defaultdict(collections.Counter)
    for r in L.facts + L.flows + L.cons:
        o = old_by_rec.get(r["record-id"])
        if o:
            ex_arch[r["example-id"]][o] += 1
    # an example with no fact rows: the old chain, name -> roster -> design
    import aggregate
    aggregate._VOCAB_PATH[0] = DB / "vocabulary.csv"
    alias = {}
    for r in read(DB / "source-roster" / "technology.csv"):
        for x in split_list(r["aggregated-from"]):
            alias.setdefault(x, r["technology"])
        alias.setdefault(r["technology"], r["technology"])
    xtech = {r["roster-technology"]: r["design-technology"]
             for r in read(DB / "design-crosswalk-technology.csv")}
    exs, conflicts = [], []
    for e in L.examples.values():
        c = ex_arch.get(e["example-id"])
        how = ""
        if c:
            old = c.most_common(1)[0][0]
            how = "fact rows"
            if len(c) > 1:
                conflicts.append((e["example-id"], dict(c)))
        else:
            canon = aggregate.canon_tech(e["source-technology"])
            roster = alias.get(canon, alias.get(e["source-technology"], canon))
            old = xtech.get(roster, "")
            how = "name" if old else "unmapped"
        exs.append({"example-id": e["example-id"], "source-id": e["source-id"],
                    "source-technology": e["source-technology"], "process": e["process"],
                    "archetype": new(old) if old else "", "detail": "",
                    "seeded-by": how, "note": ""})
    # Folds the retired crosswalk made where an archetype of the example's own
    # route exists. Keyed on (source-id, source-technology): every process of it.
    CORRECT = {
        ("etsap_2010_002", "smelting-vessel_coal_hismelt"): "smelting-vessel_bath-reduction",
        ("bataille_2017_001", "blast-furnace_hisarna-ccs"): "smelting-vessel_bath-reduction",
        ("etsap_2010_002", "smelting-vessel_coal_corex-ccs"): "smelting-vessel_two-stage",
        ("ukerc_2013_001", "compressor_electricity_efficiency-moderate"): "compressor_air-system-management",
        ("etsap_2013_002", "heat-pump_electricity"): "heat-pump_industrial",
        ("etsap_2013_002", "heat-pump_electricity_medium-temp"): "heat-pump_industrial",
        ("ipcc_2022_001", "heat-pump_electricity"): "heat-pump_industrial",
        ("bataille_2017_001", "caster"): "caster_continuous",
        ("etsap_2012_001", "caster"): "caster_continuous",
        ("ukerc_2013_001", "caster"): "caster_continuous",
        ("iea_2024_001", "shaft-furnace"): "shaft-furnace_direct-reduction",
        ("ukerc_2013_001", "reactor_efficiency-moderate"): "reactor_nitric-acid",
        ("etsap_2010_003", "reactor_geopolymer"): "binder_alkali-activated",
    }
    for r in exs:
        fix = CORRECT.get((r["source-id"], r["source-technology"]))
        if fix and fix != r["archetype"]:
            r["note"] = f"was {r['archetype']} (retired crosswalk fold), corrected 2026-09-23"
            r["archetype"], r["seeded-by"] = fix, "corrected"
    exs.sort(key=lambda r: (r["source-id"], r["source-technology"], r["process"]))

    # ---- product-unit: follow the sources where they agree -------------------
    # The seed is the service unit of the archetype's first end use. For a
    # process archetype where at least two thirds of the cost rows its examples
    # carry are per one other unit (dryers priced per GJ of drying heat), it
    # takes that unit instead, so most of its numbers pool without a conversion
    # D13 rules out. An energy-service archetype stays in GJ. Rows in any other
    # unit are left out of the summary and listed in the mapping review.
    arch_of = {r["example-id"]: r["archetype"] for r in exs}
    denoms = collections.defaultdict(collections.Counter)
    for r in L.facts:
        u = r.get("unit", "")
        if not re.match(r"^\d{4}_[A-Z]{3}/", u) or not r["parameter"].startswith(("capex", "opex")):
            continue
        d = u.split("/", 1)[1].replace("-per-yr", "").replace("tonnes of mixed product", "t")
        d = {"kW": "GJ", "kWh": "GJ"}.get(d, d)
        denoms[arch_of.get(r["example-id"], "")][d] += 1
    flipped = []
    service_family = {f for f, *_ in FAMILIES}
    for a in arche:
        c = denoms.get(a["archetype"])
        if not c or a["family"] in service_family:
            continue    # an energy service is measured in GJ, whatever a source priced it per
        d, n = c.most_common(1)[0]
        if n / sum(c.values()) >= 2 / 3:
            if d in ("GJ", "t", "m3") and d != a["product-unit"]:
                flipped.append((a["archetype"], a["product-unit"], d))
                a["note"] = (a["note"] + " " if a["note"] else "") + (
                    f"product-unit {d}: most of its sources price it per {d} "
                    f"(its end use is measured in {a['product']}).")
                a["product-unit"] = d
    print(f"product-unit follows the sources on {len(flipped)} archetypes: "
          + ", ".join(f"{k} {o}->{n}" for k, o, n in flipped))

    # ---- write --------------------------------------------------------------
    write(REC / "archetype.csv", ["archetype", "label", "family", "type", "carriers",
                                  "heat-tier", "product-unit", "product", "trl", "trl-basis",
                                  "description", "examples-named", "sources", "note"], arche)
    write(REC / "archetype-service.csv", ["archetype", "branch", "note"], svc)
    write(REC / "hierarchy-annotation.csv", list(ann[0]), ann)
    fam_rows = [{"family": f, "kind": k, "label": l, "description": d} for f, k, l, d in FAMILIES]
    for s in read(ROOT / "archive" / "scripts" / "sector-2026-09-22.csv"):
        if s["sector"] != "cross-sector":
            fam_rows.append({"family": s["sector"], "kind": "sector", "label": s["sector-label"],
                             "description": s["description"], "uktm-code": s["uktm-code"],
                             "naics-2017": s["naics-2017"], "isic-rev4": s["isic-rev4"],
                             "note": s["note"]})
    write(REC / "family.csv", ["family", "kind", "label", "description", "uktm-code",
                               "naics-2017", "isic-rev4", "note"], fam_rows)
    write(VOC / "equipment.csv", ["equipment", "definition", "examples", "note"], eq)
    write(VOC / "discriminator.csv", ["discriminator", "definition", "reviewed"], dis)
    write(VOC / "modifier.csv", ["modifier", "order", "definition"],
          [{"modifier": m, "order": o, "definition": d} for m, o, d in MODIFIERS])
    write(VOC / "carrier.csv", ["carrier"], [{"carrier": c} for c in carriers])
    write(VOC / "lists.csv", ["list", "term", "note"], lists)
    write(REC / "source-example.csv", ["example-id", "source-id", "source-technology", "process",
                                       "archetype", "detail", "seeded-by", "note"], exs)
    write(ROOT / "archive" / "scripts" / "archetype-renames-2026-09-23.csv",
          ["old", "new", "reason"],
          [{"old": o, "new": n, "reason": REASON[c]} for o, (n, c) in sorted(RENAME.items())])
    print(f"\narchetypes {len(arche)}, service rows {len(svc)}, annotations {len(ann)}, "
          f"examples {len(exs)} ({collections.Counter(r['seeded-by'] for r in exs)})")
    print(f"{len(review)} (archetype, end use) pairs spread over every leaf: "
          + ", ".join(f"{a}@{e}({n})" for a, e, n in review[:40]))
    print(f"examples whose facts sat on more than one archetype: {conflicts[:10]}")
    bad = [s["branch"] for s in svc if "*" not in s["branch"] and s["branch"] not in hset]
    print("service paths not in hierarchy:", bad[:10])


if __name__ == "__main__":
    main()
