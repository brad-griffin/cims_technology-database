"""Extract the PBL/TNO MIDDEN database (Technology Characteristics sheet) into the
ETSAP-brief shape: <stem>.csv, <stem>_nodes.csv, <stem>_flows.csv, plus
<stem>_io-as-printed.csv and <stem>_other-values.csv (not loaded).

Usage (from data/raw-data):
    python gov-nl/pbl/midden-extract.py

One example per technology card (TC). The process is the plant section of the
first plant configuration (PCD) that uses the card, with the MIDDEN report that
describes the plant. MIDDEN states all quantities per unit of capacity per year:
for a 'kt product/yr' capacity, TJ/kt = GJ/t and kt/kt = t/t, so they load as
printed. For MWth/MWe/MW/TJ-per-year capacities, inputs, outputs and emissions are
divided by the main-output energy per unit capacity (derived, with formula).

Rules applied (modeller rulings 2026-09-29):
- 0 and empty both mean 'no data' (database README).
- Capex: COST BASIS from the card's comment where it says so (additional /
  retrofit / substitution -> incremental; equipment only -> equipment; including
  installation -> installed); otherwise installed, marked as assumed.
- Capex and O&M in MEUR<year> per unit capacity: x1000 -> <year>_EUR/t-per-yr
  (kt capacity) or <year>_EUR/kW (MW capacity); O&M per kW is /kW-yr.
"""
import csv
import re
from pathlib import Path

import pandas as pd

from pathlib import Path as _Path
# This script sits beside its extractions in data/raw_data/technology_database/<publisher>/
# (the FRDR deposit) and reads its document from the same folder under primary-sources/
# (2026-11-06).
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
# Records and build outputs live in a CIMS worktree (plan D6); take their paths
# from the CIMS package, so they follow whichever CIMS this environment installs.
from CIMS.data_processing.technology_database.pipeline.common import VOCAB  # noqa: E402
_DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
DOCS, HERE = _DOCS, _HERE
STEM = "van-geene_2024_midden-database-v0-4a_pbl"
ODS = DOCS / f"{STEM}.ods"
BASIS_NOTE = ("COST BASIS: installed (assumed: MIDDEN gives no cost basis and the card's "
              "comment names none; modeller ruling 2026-09-29).")

# MIDDEN commodity (lower case) -> (vocabulary commodity, class). Only mapped when
# the MIDDEN unit matches the class (TJ for energy, kt for material).
COMMODITY = {
    "electricity": "electricity", "natural gas": "natural-gas",
    "green gas": "biomethane", "purified biogas": "biomethane",
    "biogas": "biogas", "raw biogas": "biogas",
    "refinery gas": "refinery-gas", "cog": "coke-oven-gas", "bfg": "blast-furnace-gas",
    "bofg": "basic-oxygen-furnace-gas", "coal": "coal", "coke": "coke",
    "biomass (solid)": "biomass-solid", "biomass": "biomass-solid", "wet biomass": "biomass-solid",
    "hydrogen (gas)": "hydrogen", "hydrogen": "hydrogen", "hydrogen gas": "hydrogen",
    "steam": "steam", "steam (low pressure - 1-9 bar)": "steam",
    "steam (medium pressure - 10-19 bar)": "steam", "steam (medium pressure)": "steam",
    "steam (high pressure - 20-50 bar)": "steam", "steam (high pressure)": "steam",
    "steam (high pressure - 20-30 bar)": "steam", "steam (very high pressure - 51-100 bar)": "steam",
    "steam (medium to high pressure - 10-50 bar )": "steam",
    "water (60-100c)": "hot-water", "water (30-60c)": "hot-water",
    "hot water (70 - 120 degrees c)": "hot-water", "warm water (30 degrees c)": "hot-water",
    "residual heat": "waste-heat",
    "naphtha": "naphtha", "ethane": "ethane", "water": "water", "demi water": "water",
    "oxygen": "oxygen", "oxygen (gas)": "oxygen", "air": "air",
    "iron ore": "iron-ore", "iron ore pellets": "pellets", "sinter": "sinter",
    "pig iron": "hot-metal", "dri": "direct-reduced-iron", "scrap steel": "scrap-steel",
    "crude steel": "crude-steel", "limestone": "limestone", "calcium carbonate": "limestone",
    "calcium oxide": "lime", "clinker": "clinker", "cement": "cement",
    "aluminium oxide (al2o3)": "alumina", "recovered paper": "recovered-paper",
    "ammonia": "ammonia", "methanol": "methanol", "slag": "slag", "calcium sulphate": "gypsum",
    "olivine": "olivine", "ethanol": "ethanol", "lignin": "lignin",
}


# energy units as printed -> TJ
TJ_PER = {"TJ": 1.0, "PJ": 1000.0, "GJ": 1e-3, "MJ": 1e-6}
# inputs of low-grade heat taken up by heat pumps and similar: not counted as energy
# input when deriving an efficiency
AMBIENT = re.compile(r"heat|water \(|hot water|warm water", re.I)
# cards whose printed energy quantities are internally inconsistent: no SEC,
# efficiency or per-GJ emissions are derived from them
SUSPECT = {
    "TC0039": "electricity input printed as 0.244 TJ per kt of hydrogen, about 1000 times below any electrolyser",
    "TC0427": "main output printed as 0.0315 TJ per MWth, 1000 times below a year at full load (31.5 TJ)",
    "TC0428": "main output printed as 0.0315 TJ per MWth, 1000 times below a year at full load (31.5 TJ)",
    "TC0429": "main output printed as 0.0315 TJ per MWth, 1000 times below a year at full load (31.5 TJ)",
}


# cards whose printed numbers carry a unit slip in the source, corrected here (re-read
# 2026-10-05 against the card and its material balance; user ruling 2026-10-05):
#   inputs     every input amount (energy and material) and the emissions are per
#              TONNE of output entered as per kt: the material inputs are 1/1000 of
#              any possible yield (1.05 kt PET per kt flakes printed 0.00105)
#   capex/opex the cost scale printed in EUR (or kEUR) where the column is MEUR
CARD_SCALE = {
    "TC0484": {"inputs": 1000, "emissions": 1000,
               "why": "PET tray waste printed 0.00105 kt per kt flakes at a stated 95% material "
                      "efficiency (1.05 kt per kt); every input and the CO2 are 1000x low"},
    "TC0487": {"inputs": 1000, "emissions": 1000,
               "why": "PE+PP waste printed 0.00116 kt per kt naphtha (pyrolysis needs about 1.16); "
                      "inputs and CO2 are 1000x low"},
    "TC0488": {"inputs": 1000, "emissions": 1000,
               "why": "RDF printed 0.00239 kt per kt methanol (Iaquaniello 2017: 2.39 t RDF per t); the "
                      "natural-gas comment converts 2.87 t gas to '4.22 m3' (4,220 m3), so the gas is "
                      "3.5 GJ per t methanol; inputs and CO2 are 1000x low"},
    "TC0100": {"capex": 1e6,
               "why": "capex printed 4e-06 MEUR per MWth (3e-06 to 7e-06): 4,000 EUR/kW (3,000-7,000) "
                      "is the digester-CHP range and matches the card's O&M of 26 EUR/kW-yr; the "
                      "entry is in EUR per kW in a MEUR per MW column"},
    "TC0530": {"capex": 1000, "opex": 1000,
               "why": "capex 0.000305 and O&M 1.1e-05 MEUR per MWth: 305 EUR/kW and 11 EUR/kW-yr "
                      "(3.6%/yr) are an upgrader's range; the entries are in kEUR per MW"},
}
# cards whose printed O&M limits do not belong to the printed O&M (re-read 2026-10-05):
# a factor the limits are divided by, or None to drop them
OPEX_LIMIT_FIX = {
    "TC0437": (1000, "limits printed 20.3-33.7 MEUR around 0.027 MEUR: the limits are in kEUR"),
    "TC0436": (None, "limits 20.3-33.7 kEUR are TC0437's; this card's O&M is 2% of its own capex "
                     "(0.00965 MEUR), so the limits are dropped"),
    "TC0434": (None, "limits 0.00417-0.0146 MEUR do not bracket the printed 0.464 MEUR (5.5% of capex); "
                     "the limits are dropped"),
}
# heat pumps and vapour recompression: the steam or vapour recompressed is the heat
# source, not an energy input, so the COP is output over electricity (re-read
# TC0315 2026-10-05: 31.5 TJ out / 14.3 TJ electricity, not / (27 steam + 14.3))
HEAT_PUMP = re.compile(r"heat pump|mvr|recompression", re.I)


def load_vocab():
    p = VOCAB / "commodity.csv"
    return {r["commodity"]: r["commodity-class"] for r in csv.DictReader(open(p, encoding="utf-8-sig"))}


def num(v):
    s = str(v).strip()
    if s in ("", "0", "nan", "None", "0.0"):
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    return None if f == 0 else f


def txt(v):
    s = str(v).strip()
    return "" if s in ("", "0", "nan", "None") else s


def slug(s, n=60):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n].rstrip("-")


def g(v):
    return f"{v:.6g}"


def sheet(name):
    x = pd.read_excel(ODS, engine="odf", sheet_name=name, header=None, dtype=str)
    hr = next(i for i in range(12) if any(str(v).endswith("_id") for v in x.iloc[i].tolist()))
    d = x.iloc[hr + 1:].copy()
    d.columns = [str(c) for c in x.iloc[hr].tolist()]
    return d.dropna(how="all")


def sector_of(nace):
    n = (nace or "").lower()
    rules = [("iron and steel", "iron-and-steel"), ("aluminium", "non-ferrous-metals"),
             ("zinc", "non-ferrous-metals"), ("non-ferrous", "non-ferrous-metals"),
             ("refined petroleum", "petroleum-refining"), ("paper", "pulp-and-paper"),
             ("cement", "cement"), ("glass", "non-metallic-minerals"),
             ("bricks", "non-metallic-minerals"), ("non-metallic", "non-metallic-minerals"),
             ("dair", "food-and-beverage"), ("beer", "food-and-beverage"), ("malt", "food-and-beverage"),
             ("potato", "food-and-beverage"), ("starch", "food-and-beverage"), ("sugar", "food-and-beverage"),
             ("oils and fats", "food-and-beverage"), ("food", "food-and-beverage"),
             ("waste", "other-industry"), ("tyre", "other-industry"), ("rubber", "other-industry"),
             ("chemic", "chemicals"), ("fertilis", "chemicals"), ("gases", "chemicals"),
             ("plastics", "chemicals"), ("organic", "chemicals"), ("inorganic", "chemicals")]
    for k, s in rules:
        if k in n:
            return s
    return "other-industry"


def end_use_of(cap_unit, name, out_name):
    u, t = cap_unit.lower(), (name + " " + out_name).lower()
    if "mwe" in u or "electricity" in out_name.lower():
        return "power-generation"
    if re.search(r"\bccs\b|capture|co2 compression|carbon dioxide", t):
        return "co2-capture"
    if "mwth" in u or re.search(r"\bsteam\b|boiler|\bchp\b|heat pump|hot water", t):
        return "steam-and-hot-water"
    if re.search(r"dryer|drying|evaporat|distill|separat|concentrat", t):
        return "drying-and-separation"
    return "material-conversion"


# cards whose comment mentions 'additional', 'extra', 'retrofit' or 'add-on' but whose
# printed value is a complete new installation (checked against the comment by hand)
BASIS_OVERRIDE = {
    "TC0012": "the value is the 150 EUR/t furnace plus the 40 EUR/t Optimelt add-on the comment describes",
    "TC0014": "the value is the 150 EUR/t furnace plus the 40 EUR/t Optimelt add-on the comment describes",
    "TC0050": "a new furnace scaled from 15 MEUR per 10 MW plus the hydrogen burners",
    "TC0051": "a new electric furnace with infrastructure and project costs",
    "TC0095": "a complete additional production line",
    "TC0482": "the same complete capture plant as the CCS add-on card (TC0481)",
    "TC0538": "the central value is a new capture unit; only the upper limit is a retrofit",
    "TC0539": "the central value is a new capture unit; only the upper limit is a retrofit",
    "TC0541": "the central value is a new installation; only the upper limit is a retrofit",
}


def basis(comment, tid=""):
    if tid in BASIS_OVERRIDE:
        return "installed", f"COST BASIS: installed ({BASIS_OVERRIDE[tid]})."
    c = comment.lower()
    if re.search(r"additional|extra cost|retrofit|substitut|on top of|add-on|conversion of|"
                 r"replacement of|replacing", c):
        return "incremental", "COST BASIS: incremental (the card's comment: additional/retrofit cost)."
    if re.search(r"equipment cost|equipment only|excl\w*\.? (of )?install", c) and "incl" not in c:
        return "equipment", "COST BASIS: equipment (the card's comment)."
    if re.search(r"incl\w*\.? (of )?(the )?install|including install|installation costs? (are )?incl|"
                 r"\btotal (plant|investment|installed)|turnkey|\bepc\b|\btic\b", c):
        return "installed", "COST BASIS: installed (the card's comment)."
    return "installed", BASIS_NOTE


def main():
    vocab = load_vocab()
    tc, pcd, mid = sheet("TC"), sheet("PCD"), sheet("MIDDEN")
    plant = mid.drop_duplicates("plant_id").set_index("plant_id")
    first = pcd.drop_duplicates("technology_id").set_index("technology_id")
    rows, nodes, flows, io, other = [], [], [], [], []

    def add(proc, tech, param, unit, value, vmin="", vmax="", target="", formula="", ref="", note=""):
        rows.append([proc, tech, param, target, unit, value, vmin, vmax, formula, ref, note])

    for _, r in tc.iterrows():
        tid, name = txt(r["technology_id"]), txt(r["technology"])
        if not tid or not name:
            continue
        cap = txt(r["capacity_unit"])
        capl = cap.lower()
        # the card's section: the most common among its plant configurations (the first
        # one is misaligned for several Shell Pernis refinery cards in v0.4a)
        uses = pcd[pcd["technology_id"] == tid]
        if len(uses):
            sec_mode = uses["section"].fillna("").str.strip().value_counts().index[0]
            f = uses[uses["section"].fillna("").str.strip() == sec_mode].iloc[0]
        else:
            f = None
        section = txt(f["section"]) if f is not None else "unassigned"
        pid = txt(f["plant_id"]) if f is not None else ""
        report = txt(plant.loc[pid, "report"]) if pid in plant.index else "MIDDEN"
        nace = txt(plant.loc[pid, "NACE_name"]) if pid in plant.index else ""
        pname = txt(f["plant_name"]) if f is not None else ""
        proc = f"{section} [{report}]"
        tech = f"{tid.lower()}_{slug(name, 55)}"
        ref = f"TC sheet, {tid}"
        outn = txt(r["main_output_name"])
        # capacity kind
        is_kt = capl.startswith("kt") or " kt" in capl
        is_mw = capl in ("mwth", "mwe", "mw")
        is_tj = capl.startswith("tj ")
        per_unit = "t" if is_kt else "GJ"
        nodes.append([proc, tech, sector_of(nace), end_use_of(cap, name, outn), "", per_unit])
        desc = txt(r["technology_description"])
        add(proc, tech, "description", "", (desc or name)[:900], ref=ref,
            note=f"MIDDEN {tid}; capacity unit '{cap}'; main output '{outn}'; first used at {pname} ({report}).")

        # main-output energy per unit capacity, for MW / TJ capacities
        main_tj = None
        if not is_kt:
            for y in range(1, 13):
                nm = txt(r.get(f"name_of_output_{y}", ""))
                uu = txt(r.get(f"output_{y}_unit", ""))
                if nm and nm.lower() == outn.lower() and uu in TJ_PER and num(r.get(f"output_{y}_amount")):
                    main_tj = num(r.get(f"output_{y}_amount")) * TJ_PER[uu]
                    break
            if main_tj is None and is_tj:
                main_tj = 1.0
        if tid.upper() in SUSPECT:
            main_tj = None
            other.append([tid, name, "defect", "", "", ref, SUSPECT[tid.upper()] + "; no SEC, efficiency or per-GJ values derived"])

        # capex (new)
        fix = CARD_SCALE.get(tid.upper(), {})
        cx, cu = num(r["investment_per_unit_of_capacity_new_amount"]), txt(r["investment_per_unit_of_capacity_new_unit"])
        cy = re.match(r"MEUR\s*(\d{4})", cu, re.I)
        if cx and cy:
            yr = cy.group(1)
            lo, hi = num(r["investment_per_unit_of_capacity_new_lower_limit"]), num(r["investment_per_unit_of_capacity_new_upper_limit"])
            com = txt(r["investment_per_unit_of_capacity_new_comment"])
            if fix.get("capex"):
                k_ = fix["capex"]
                cx, lo, hi = cx * k_, (lo * k_ if lo else lo), (hi * k_ if hi else hi)
                com = f"SOURCE UNIT CORRECTED x{k_:g} (2026-10-05): {fix['why']}. " + com
            b, bnote = basis(com, tid)
            if is_kt or is_mw:
                unit = f"{yr}_EUR/t-per-yr" if is_kt else f"{yr}_EUR/kW"
                capb = "product-output" if is_kt else ("electric-output" if capl == "mwe" else "thermal-output")
                add(proc, tech, "capex", unit, g(cx * 1000), g(lo * 1000) if lo else "", g(hi * 1000) if hi else "",
                    formula=f"{g(cx)} MEUR per {cap} x 1000", ref=ref,
                    note=f"{bnote} CAPACITY BASIS: {capb}. Card comment: {com}"[:1200])
            else:
                other.append([tid, name, "capex (new)", f"{cu} per {cap}", g(cx), ref, com])
        rx = num(r["investment_per_unit_of_capacity_refurbishment_amount"])
        if rx:
            other.append([tid, name, "capex (refurbishment)", f"{txt(r['investment_per_unit_of_capacity_refurbishment_unit'])} per {cap}",
                          g(rx), ref, txt(r["investment_per_unit_of_capacity_refurbishment_comment"])])
        # O&M
        k = "annual_operating_and_maintenance_costs_per_unit_of_capacity"
        ox, ou = num(r[f"{k}_amount"]), txt(r[f"{k}_unit"])
        oy = re.match(r"MEUR\s*(\d{4})", ou, re.I)
        if ox and oy:
            yr = oy.group(1)
            lo, hi = num(r[f"{k}_amount_lower_limit"]), num(r[f"{k}_amount_upper_limit"])
            com = txt(r[f"{k}_amount_comment"])
            if tid.upper() in OPEX_LIMIT_FIX:
                f_, why_ = OPEX_LIMIT_FIX[tid.upper()]
                lo, hi = ((lo / f_ if lo else lo), (hi / f_ if hi else hi)) if f_ else (None, None)
                com = f"O&M LIMITS CORRECTED (2026-10-05): {why_}. " + com
            if fix.get("opex"):
                k_ = fix["opex"]
                ox, lo, hi = ox * k_, (lo * k_ if lo else lo), (hi * k_ if hi else hi)
                com = f"SOURCE UNIT CORRECTED x{k_:g} (2026-10-05): {fix['why']}. " + com
            if is_kt or is_mw:
                unit = f"{yr}_EUR/t-per-yr" if is_kt else f"{yr}_EUR/kW-yr"
                capb = "product-output" if is_kt else ("electric-output" if capl == "mwe" else "thermal-output")
                add(proc, tech, "opex-fixed", unit, g(ox * 1000), g(lo * 1000) if lo else "", g(hi * 1000) if hi else "",
                    formula=f"{g(ox)} MEUR per {cap} per year x 1000", ref=ref,
                    note=f"annual O&M excluding energy and materials. CAPACITY BASIS: {capb}. Card comment: {com}"[:1200])
            else:
                other.append([tid, name, "O&M per year", f"{ou} per {cap}", g(ox), ref, com])
        # lifetime
        lt = num(r["technical_lifetime_amount"])
        if lt:
            lo, hi = num(r["technical_lifetime_lower_limit"]), num(r["technical_lifetime_upper_limit"])
            add(proc, tech, "lifetime", "years", g(lt), g(lo) if lo else "", g(hi) if hi else "", ref=ref,
                note=txt(r["technical_lifetime_comment"])[:600])
        # year and TRL
        yv = num(r["year"])
        if yv:
            add(proc, tech, "year-available", "year", str(int(yv)), ref=ref,
                note="MIDDEN 'year of availability of technology (estimate)'")
        trl = txt(r["trl_value"])
        if trl and re.fullmatch(r"\d", trl):
            add(proc, tech, "trl", "", trl, ref=ref, note=txt(r["trl_comment"])[:600])
        elif trl and re.fullmatch(r"\d\s*(-|to)\s*\d", trl):
            a, b2 = re.findall(r"\d", trl)
            add(proc, tech, "trl", "", "", a, b2, ref=ref, note=f"printed '{trl}'. " + txt(r["trl_comment"])[:500])

        # inputs / outputs
        e_in, e_parts, e_eff, e_eff_parts = 0.0, [], 0.0, []
        for d in ("input", "output"):
            for y in range(1, 13):
                nm = txt(r.get(f"name_of_{d}_{y}", ""))
                am = num(r.get(f"{d}_{y}_amount"))
                if not nm or am is None:
                    continue
                un = txt(r.get(f"{d}_{y}_unit", ""))
                lo, hi = num(r.get(f"{d}_{y}_lower_limit")), num(r.get(f"{d}_{y}_upper_limit"))
                com = txt(r.get(f"{d}_{y}_comment", ""))
                if d == "input" and fix.get("inputs"):
                    k_ = fix["inputs"]
                    am, lo, hi = am * k_, (lo * k_ if lo else lo), (hi * k_ if hi else hi)
                    com = f"SOURCE UNIT CORRECTED x{k_:g} (2026-10-05): {fix['why']}. " + com
                io.append([tid, name, cap, d, nm, g(am), un, g(lo) if lo else "", g(hi) if hi else "",
                           txt(r.get(f"{d}_{y}_source", "")), com])
                if d == "output" and nm.lower() == outn.lower():
                    continue
                c = COMMODITY.get(nm.lower())
                cls = vocab.get(c, "")
                ok = c and ((cls == "energy" and un in TJ_PER) or (cls == "material" and un.lower() == "kt"))
                if ok and un in TJ_PER and un != "TJ":
                    am, lo, hi = am * TJ_PER[un], (lo * TJ_PER[un] if lo else None), (hi * TJ_PER[un] if hi else None)
                    com = f"converted from {un} to TJ. " + com
                    un = "TJ"
                if d == "input" and un in TJ_PER:
                    e_in += am * TJ_PER[un]
                    e_parts.append(f"{nm} {g(am)} {un}")
                    if not (AMBIENT.search(nm) or (HEAT_PUMP.search(name) and re.search(r"steam|vapou?r", nm, re.I))):
                        e_eff += am * TJ_PER[un]
                        e_eff_parts.append(f"{nm} {g(am)} {un}")
                if not ok:
                    continue
                if is_kt:
                    val, vlo, vhi, formula = am, lo, hi, ""
                    unit = "GJ/unit" if un.upper() == "TJ" else "t/unit"
                elif main_tj:
                    val = am / main_tj
                    vlo, vhi = (lo / main_tj if lo else None), (hi / main_tj if hi else None)
                    unit = "GJ/unit" if un.upper() == "TJ" else "t/unit"
                    formula = f"{g(am)} {un} / {g(main_tj)} TJ main output" + (" x 1000" if un.lower() == "kt" else "")
                    if un.lower() == "kt":
                        val, vlo, vhi = val * 1000, (vlo * 1000 if vlo else None), (vhi * 1000 if vhi else None)
                else:
                    continue
                flows.append([proc, tech, d, c, g(val), unit, per_unit, g(vlo) if vlo else "", g(vhi) if vhi else "",
                              "", formula, ref, "", f"MIDDEN '{nm}' ({un}). {com}"[:800]])
        # SEC / efficiency from the TJ inputs
        if e_in and tid.upper() not in SUSPECT:
            if is_kt:
                add(proc, tech, "specific-energy-consumption", "GJ/t", g(e_in), formula=" + ".join(e_parts) + " (in TJ; TJ/kt = GJ/t)",
                    ref=ref, note="DERIVED: sum of the card's energy inputs (TJ per kt capacity), final-energy basis; "
                                  "heating-value basis not stated")
            elif main_tj and e_eff:
                amb = [p for p in e_parts if p not in e_eff_parts]
                outs = {}
                for y in range(1, 13):
                    nm, uu = txt(r.get(f"name_of_output_{y}", "")), txt(r.get(f"output_{y}_unit", ""))
                    if nm and uu in TJ_PER and num(r.get(f"output_{y}_amount")):
                        outs[nm] = num(r.get(f"output_{y}_amount")) * TJ_PER[uu]
                has_el = any("electric" in k.lower() for k in outs)
                has_heat = any(re.search(r"steam|heat|water", k, re.I) for k in outs)
                eff = main_tj / e_eff * 100
                chp = sum(outs.values()) / e_eff * 100
                if has_el and has_heat and chp > 100:
                    other.append([tid, name, "CHP output over energy input", "%", g(chp), ref,
                                  "not loaded: the card's fuel is not among its energy inputs "
                                  f"({' + '.join(e_parts)})"])
                elif has_el and has_heat:
                    add(proc, tech, "efficiency-chp", "%", g(sum(outs.values()) / e_eff * 100),
                        formula=f"({' + '.join(f'{k} {g(v)}' for k, v in outs.items())}) TJ / ({' + '.join(e_eff_parts)}) x 100",
                        ref=ref, note="DERIVED: electricity plus heat outputs over energy inputs; heating-value basis not stated")
                elif eff > 100 and not re.search(r"heat pump|mvr|recompression", name, re.I):
                    other.append([tid, name, "output over energy input", "%", g(eff), ref,
                                  "not loaded as efficiency: the card's primary heat or fuel source is not an energy input "
                                  f"on the card ({' + '.join(e_parts)})"])
                else:
                    add(proc, tech, "efficiency", "%", g(eff),
                    formula=f"{g(main_tj)} TJ {outn} / ({' + '.join(e_eff_parts)}) x 100", ref=ref,
                    note="DERIVED: main energy output over the sum of energy inputs; heating-value basis not stated"
                         + (f". Low-grade heat inputs not counted: {', '.join(amb)}" if amb else ""))
        # emissions
        for sp, col in (("co2", "co2_emissions"), ("ch4", "ch4_emissions"), ("n2o", "n2o_emissions")):
            ev = num(r[f"{col}_amount"])
            if not ev:
                continue
            eu = txt(r[f"{col}_unit"])
            com = txt(r[f"{col}_comment"])
            if fix.get("emissions"):
                ev = ev * fix["emissions"]
                com = f"SOURCE UNIT CORRECTED x{fix['emissions']:g} (2026-10-05): {fix['why']}. " + com
            if is_kt and eu.lower() == "kt":
                add(proc, tech, "emissions-total", "t/t", g(ev), target=sp, ref=ref,
                    note=f"direct fossil {sp.upper()} per tonne of capacity output (kt/kt). {com}"[:800])
            elif main_tj and eu.lower() == "kt":
                add(proc, tech, "emissions-total", "kg/GJ", g(ev / main_tj * 1000), target=sp,
                    formula=f"{g(ev)} kt / {g(main_tj)} TJ x 1000", ref=ref,
                    note=f"direct fossil {sp.upper()} per GJ of main output. {com}"[:800])
            else:
                other.append([tid, name, f"{sp} emissions", f"{eu} per {cap}", g(ev), ref, com])
        fg = num(r["f_gases_emissions_amount"])
        if fg:
            other.append([tid, name, "F-gas emissions", f"{txt(r['f_gases_emissions_unit'])} per {cap}", g(fg), ref,
                          txt(r["f_gases_emissions_comment"])])

    def write(suffix, header, data):
        with open(HERE / f"{STEM}{suffix}.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            w.writerows(data)

    write("", ["process", "technology", "parameter", "target", "unit", "value", "value-min", "value-max",
               "formula", "reference", "note"], rows)
    write("_nodes", ["process", "technology", "sector", "end-use", "process-step", "service-unit"], nodes)
    write("_flows", ["process", "technology", "direction", "commodity", "value", "unit", "per-unit", "value-min",
                     "value-max", "co-product", "formula", "reference", "source-original", "note"], flows)
    write("_io-as-printed", ["technology-id", "technology", "capacity-unit", "direction", "commodity", "amount",
                             "unit", "lower", "upper", "source", "comment"], io)
    write("_other-values", ["technology-id", "technology", "item", "unit", "value", "reference", "comment"], other)
    print(len(nodes), "cards,", len(rows), "rows,", len(flows), "flows,", len(io), "io rows,", len(other), "other values")


if __name__ == "__main__":
    main()
