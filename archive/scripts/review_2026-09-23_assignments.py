"""One-time edit (2026-09-23): the assignment review.

Re-homes examples that sat on the wrong archetype, adds the four archetypes
the review found missing, and corrects hierarchy links that named the wrong
leaf. Findings and reasons: docs/assignment-review-2026-09-23.md.

Each REMAP key is a regular expression matched against the whole example-id;
every pattern must match at least one example. A blank target leaves the
example unmapped (a user decision, or no archetype describes it); "(none)"
marks it deliberately out of scope. Run from the repo root; --dry-run prints
what would change.
"""
import csv
import re
import sys
from pathlib import Path

REC = Path.cwd() / "data" / "harmonized" / "records"
DAY = "2026-09-23"

# new key: (host, label, type, description, examples named, sources, note)
NEW = {
    "smelting-vessel_bath-reduction_ccs-concentrated": (
        "smelting-vessel_bath-reduction", "Bath smelting reduction with capture",
        "prospective", "Bath smelting reduction (HIsarna) with its oxygen-blown, CO2-rich off-gas "
        "dried, compressed and stored.", "HIsarna with CCS (UKERC IS-IW, IPCC Table 11.3)",
        "ukerc_2013_001; ipcc_2022_001; bataille_2017_001",
        "Split from the plant without capture: capture roughly doubles its cost."),
    "smelting-vessel_two-stage_ccs-concentrated": (
        "smelting-vessel_two-stage", "Two-stage smelting reduction with capture",
        "prospective", "COREX-type two-stage smelting reduction with CO2 removed from the "
        "export gas and stored.", "COREX with CCS (ETSAP I02)", "etsap_2010_002",
        "Split from the plant without capture: capture roughly doubles its cost."),
    "dryer_direct-fired_efficiency-strong": (
        "dryer_direct-fired", "Direct-fired dryer efficiency measures, strong",
        "efficient variant", "The direct-fired dryer or curing oven with incremental "
        "efficiency measures applied.", "UK TIMES advanced dryer option (Bataille 2017)",
        "bataille_2017_001",
        f"Added {DAY} as the bucket for the UK TIMES advanced drying option."),
    "paper-machine_fourdrinier-gap_efficiency-moderate": (
        "paper-machine_fourdrinier-gap", "Paper machine efficiency measures, moderate",
        "efficient variant", "The fourdrinier or gap former with press section with "
        "incremental efficiency measures applied.",
        "wire-section drainage and vacuum practice, felt and press steam optimisation, "
        "online moisture management (UKERC PP-W, PP-P3, PP-P7, PP-VWPD1)",
        "ukerc_2013_001; bataille_2017_001",
        f"Added {DAY} as the bucket for wire- and press-section measures."),
}

B, U, E, I, P, G = ("bataille_2017_001:", "ukerc_2013_001:", "etsap_20[0-9]{2}_00[0-9]:",
                    "iea_2024_001:", "ipcc_2022_001:", "epa_20(07|17)_001:")
BLANK = ""
REMAP = [
    # biofuels, chemicals, hydrogen
    (I + r"fermenter@ethylene", "reactor_ethanol-to-ethylene", "ethanol dehydration to ethylene"),
    (I + r"fermenter_biomass@high-value-chemicals", "fermenter_syngas", "gas fermentation"),
    (I + r"electrolysis-cell_hydrogen@ammonia", "reactor_haber-bosch-electrolytic", "Haber-Bosch on electrolytic hydrogen"),
    (P + r"reactor_natural-gas@cross-cutting.*", "reactor_methane-pyrolysis", "IPCC: CH4 pyrolysis or catalytic cracking"),
    (P + r"reactor_electricity@chemicals.*", BLANK, "IPCC electrocatalysis to several products; no archetype describes it"),
    (I + r"gasifier_coal@thermal-processes", "gasifier_ccs-concentrated", "coal gasification with high capture"),
    (I + r"gasifier_biomass@methanol", "gasifier_biomass-methanol", "biomass gasification to methanol"),
    (I + r"gasifier_biomass@thermal-processes", "gasifier_biomass-waste", "biomass-waste gasification to hydrogen"),
    (I + r"gasifier@ethylene", BLANK, "gasification route to ethylene; no archetype describes it"),
    (B + r"gasifier_efficiency-base@all-industry", BLANK, "a generic gasifier, not a methane reformer"),
    # electrolysis
    (I + r"electrolysis-cell_electricity@electrolysis", "electrolyzer_low-temperature", "IEA: alkaline electrolyser"),
    (I + r"electrolysis-cell_electricity@(manufacturing|other-production-techniques)", "electrolysis-cell_molten-oxide", "IEA: molten oxide electrolysis"),
    (I + r"electrolysis-cell_electricity@shift-in-energy.*", "electrolysis-cell_iron-electrowinning", "IEA: low-temperature iron electrolysis"),
    (P + r"electrolysis-cell_electricity@aluminium.*", "electrolysis-cell_inert-anode", "IPCC: inert electrodes"),
    (E + r"electrolysis-cell_electricity_soderberg-(modified|vss)@electrolysis", "electrolysis-cell_soderberg", "a Soderberg cell"),
    (I + r"smelting-vessel_electricity@other-production-techniques", "electrolysis-cell_multipolar-chloride", "IEA: chloride electrolysis"),
    (I + r"smelting-vessel@other-production-techniques", "electrolysis-cell_power-modulation", "IEA: firmed renewables for aluminium smelting"),
    (I + r"smelting-vessel@with-carbon-capture", BLANK, "aluminium smelting with capture; no archetype describes it"),
    (P + r"smelting-vessel_electricity@aluminium.*", BLANK, "IPCC hydro/electrolytic smelting; no archetype describes it"),
    # cement
    (E + r"grinding-mill_electricity_high-pressure-roll@cement-grinding", "grinding-mill_vertical-roller", "high-pressure grinding rolls"),
    (I + r"grinding-mill@other-production-techniques", "grinding-mill_vertical-roller", "IEA: advanced grinding"),
    (E + r"kiln_(wet|semi-wet|lepol|wet-precalciner|long-dry)@clinker-kiln", BLANK, "a legacy kiln type (energy use >15% above a precalciner kiln): user decision"),
    (U + r"kiln_dry@dry-kiln", "kiln_fluidized-bed", "UKERC C-DK4 is a fluidised-bed kiln"),
    (U + r"kiln@cement-subsector-2030-kiln-efficiency", BLANK, "UKERC C-CS2 to C-CS6 are alternative binders (Novacem, E-crete, Celitement, Aether) pooled in one example"),
    (I + r"kiln@other-production-techniques", BLANK, "IEA: electrolyser-based decarbonation; no archetype describes it"),
    (P + r"kiln_biomass@cement-and-concrete", "kiln_dry-precalciner", "a cement kiln, not a lime kiln"),
    (B + r"precalciner@production-processes-improvement-technology-precalciner", "kiln_dry-precalciner_efficiency-moderate", "an add-on to an existing kiln"),
    (B + r"kiln_oxyfuel-ccs@.*", "kiln_oxy-fuel", "an oxy-fuel kiln"),
    (E + r"kiln_oxyfuel@clinker-kiln", "kiln_oxy-fuel", "an oxy-fuel kiln"),
    (U + r"kiln_oxyfuel@cement-plant", "kiln_oxy-fuel", "an oxy-fuel kiln"),
    (I + r"capture-unit_oxyfuel-ccs@with-carbon-capture", "kiln_oxy-fuel", "IEA: oxy-fuelling of the cement kiln"),
    (I + r"capture-unit_ccs@with-carbon-capture", "capture-unit_calcium-looping", "IEA: calcium looping"),
    # capture
    (P + r"capture-unit@cross-cutting.*", "compressor_co2-dehydration", "IPCC: CCUS of concentrated CO2 needs only drying and compression"),
    (I + r"capture-unit@with-carbon-capture", BLANK, "IEA: capture in the Bayer process; no archetype describes it"),
    # iron and steel
    (B + r"blast-furnace_hisarna@.*", "smelting-vessel_bath-reduction", "HIsarna is bath smelting"),
    (B + r"blast-furnace_hisarna-ccs@.*", "smelting-vessel_bath-reduction_ccs-concentrated", "HIsarna with capture"),
    (P + r"smelting-vessel_hisarna-ccs@.*", "smelting-vessel_bath-reduction_ccs-concentrated", "HIsarna with capture"),
    (U + r"smelting-vessel_hisarna-ccs@.*", "smelting-vessel_bath-reduction_ccs-concentrated", "HIsarna with capture"),
    (I + r"smelting-vessel@with-carbon-capture-and-usage", "smelting-vessel_bath-reduction_ccs-concentrated", "IEA: smelting reduction with capture"),
    (E + r"smelting-vessel_coal_corex-ccs@smelting-reduction", "smelting-vessel_two-stage_ccs-concentrated", "COREX with capture"),
    (B + r"smelting-vessel_coal@iron-and-steel", "smelting-vessel_bath-reduction", "coal-based smelting reduction in iron and steel"),
    (E + r"smelting-vessel_coal_tecnored(-chp)?@smelting-reduction", BLANK, "Tecnored is a distinct low-shaft route: user decision"),
    (B + r"blast-furnace_coal@production-processes-blast-furnaces.*", "blast-furnace_efficiency-moderate", "UK TIMES improvement: pulverized coal injection"),
    (B + r"blast-furnace_coke_top-gas-recycling-ccs@.*", "blast-furnace_top-gas-recycling", "top-gas recycling"),
    (E + r"blast-furnace_oxyfuel@blast-furnace", "blast-furnace_top-gas-recycling", "oxygen blast furnace with top-gas recycling"),
    (B + r"blast-furnace_coke_ulcowin@.*", "electrolysis-cell_iron-electrowinning", "ULCOWIN is iron electrowinning"),
    (B + r"converter_coal@iron-and-steel", BLANK, "unclear which process it is"),
    (I + r"blast-furnace(_biomass)?@with-carbon-capture-and-usage", BLANK, "IEA: conversion of steel off-gases (CCU); no archetype describes it"),
    (B + r"electric-arc-furnace_(electricity|natural-gas)_midrex@.*", "shaft-furnace_direct-reduction", "UK TIMES: the MIDREX DRI route"),
    (B + r"electric-arc-furnace_natural-gas_ulcored-ccs@.*", "shaft-furnace_direct-reduction_ccs-concentrated", "ULCORED DRI with capture"),
    (B + r"shaft-furnace_ulcored-ccs@.*", "shaft-furnace_direct-reduction_ccs-concentrated", "ULCORED DRI with capture"),
    (U + r"shaft-furnace_natural-gas_ulcored-ccs@.*", "shaft-furnace_direct-reduction_ccs-concentrated", "ULCORED DRI with capture"),
    (U + r"(furnace|furnace_preheat|melting-furnace)@electric-arc-furnace", "electric-arc-furnace_high-efficiency", "UKERC IS-EAF9, 12, 13: DC, twin-shell shaft-preheat and Comelt EAFs"),
    (U + r"rolling-mill_efficiency-strong@hot-rolling", "furnace_reheating_efficiency-strong", "UKERC IS-HR5, 6: recuperative burners and oxygen control on the reheat furnace"),
    (U + r"rolling-mill_efficiency-strong@hot-rolling-not-including-heavy-section", "rolling-mill_hot-charging", "UKERC IS-HR8: hot charging"),
    (U + r"caster_efficiency-strong@continuous-casting", "preheater_ladle", "UKERC IS-CC1: ladle preheating and tundish heating"),
    (B + r"heat-recovery-unit@production-processes-casting-rolling.*", "furnace_reheating_efficiency-moderate", "UK TIMES improvement on casters and hot rolling mills"),
    (I + r"rolling-mill@manufacturing", BLANK, "IEA: ring rolling in non-ferrous metals; no archetype describes it"),
    (B + r"rolling-mill_electricity_efficiency-moderate@mining", BLANK, "a mill in mining, not a steel rolling mill"),
    (E + r"caster@casting", BLANK, "an aluminium cast house, not steel continuous casting"),
    # heat supply: the EPA catalogs are CHP catalogs
    (G + r"(combustion-turbine_(natural-gas|biogas|landfill-gas)|microturbine)@steam", "combustion-turbine_heat-recovery-steam-generator", "EPA CHP catalog: turbine CHP"),
    (G + r"reciprocating-engine@steam", "reciprocating-engine_chp", "EPA CHP catalog: engine CHP"),
    (G + r"steam-turbine(_biomass)?@steam", "steam-turbine_back-pressure", "EPA CHP catalog: back-pressure turbine"),
    (G + r"gasifier_biomass@steam", "gasifier_biomass-chp", "EPA biomass CHP catalog: gasifier"),
    (I + r"boiler@other-production-techniques", "boiler_ccs-diffuse", "IEA: boilers fitted with CO2 capture"),
    (B + r"direct-heater_solar@non-ferrous-metals", "solar-concentrator_thermal", "solar direct heat"),
    (I + r"direct-heater_solar@shift-in-energy.*", "solar-concentrator_high-temperature", "IEA: solar direct heat for cement"),
    (B + r"refining-furnace@(all-industry|petroleum-refining)", "direct-heater_furnace", "a fired furnace"),
    (B + r"calciner_coal@mining", "dryer_rotary-direct-fired", "a direct-fired calciner"),
    # food
    (U + r"oven@bakery-indirect-ovens", "oven_indirect-fired", "indirect-fired bakery ovens"),
    (U + r"oven_electricity_efficiency-moderate@bakery-ovens", "oven_efficiency-moderate", "bakery oven measures"),
    (U + r"management-system_efficiency-strong@undefined-sector", "(none)", "UKERC FD-1 energy management, priced per £k of output"),
    # machine drive
    (U + r"fan_electricity_efficiency-moderate@motors-fans", "fan_optimization", "fan system measures"),
    (U + r"compressor_electricity@motors-compressors", "motor_induction-standard", "UKERC baseline motor driving a compressor"),
    (U + r"management-system_electricity_efficiency-moderate@sector", "(none)", "sector-wide energy management, not a technology option"),
    # pulp and paper
    (U + r"dryer@dryer", "dryer_steam-heated", "UKERC paper-machine dryer section baseline"),
    (U + r"dryer@sector", "(none)", "UKERC pulp-and-paper sector aggregate (energy per t of paper), not a dryer"),
    (B + r"dryer_efficiency-base@production-processes-dryer.*", "dryer_steam-heated", "UK TIMES new standard paper dryer"),
    (B + r"dryer_steam@production-processes-dryer.*", "dryer_steam-heated_efficiency-moderate", "UK TIMES improvement: flash steam use"),
    (B + r"dryer@production-processes-alternative-drying-systems", "press_dewatering-advanced", "UK TIMES impulse dryer"),
    (B + r"press@production-processes-dryer.*", "press_dewatering-advanced", "UK TIMES improvement: hot press"),
    (I + r"press@other-production-techniques", "press_dewatering-advanced", "IEA: less water into the size press"),
    (I + r"dryer@other-production-techniques", BLANK, "IEA: supercritical CO2 drying; no archetype describes it"),
    (U + r"(press_(steam|electricity)_efficiency-moderate@press|rolling-mill_efficiency-moderate@(wire|vacuum-wire-press-dryer))",
        "paper-machine_fourdrinier-gap_efficiency-moderate", "UKERC paper machine wire- and press-section measures"),
    (B + r"press_efficiency-moderate@production-processes-press-section.*", "paper-machine_fourdrinier-gap_efficiency-moderate", "UK TIMES improvement: press aggregate"),
    (B + r"process-improvement_efficiency-moderate@production-processes-other.*", "paper-machine_fourdrinier-gap_efficiency-moderate", "UK TIMES improvement: online moisture management"),
    (I + r"refining-furnace@other-production-techniques", "pulper_refiner-low-energy", "IEA: compression refining"),
    (I + r"pulper@other-production-techniques", BLANK, "IEA: deep eutectic solvent pulping; no archetype describes it"),
    (I + r"paper-machine@other-production-techniques", BLANK, "IEA: paper making without water; no archetype describes it"),
    (B + r"paper-machine@finishing-process", BLANK, "converting basic paper to final products, not the paper machine"),
]


def bataille_heat(eid):
    """UK TIMES direct heaters and dryers go by process, not by fuel."""
    m = re.fullmatch(r"bataille_2017_001:(direct-heater|dryer)_([a-z-]+?)(_efficiency-(base|strong))?@(.+)", eid)
    if not m:
        return None
    kind, fuel, level, proc = m.group(1), m.group(2), m.group(4), m.group(5)
    elec = fuel == "electricity"
    if kind == "direct-heater":
        if level == "strong":
            return None
        if "low-temperature-heat" in proc and level == "base":
            return ("direct-heater_electric-process" if elec else "direct-heater_air-water",
                    "UK TIMES low-temperature direct heat")
        if "high-temperature-heat" in proc and not level:
            return ("direct-heater_electric-process" if elec else "direct-heater_furnace",
                    "UK TIMES high-temperature direct heat")
        if "other-services" in proc and not level:
            return ("direct-heater_electric-process" if elec else "direct-heater_fired-process",
                    "UK TIMES direct heat for other services")
        if proc == "chemicals" and fuel in ("electricity", "coke"):
            return ("direct-heater_electric-process" if elec else "direct-heater_fired-process",
                    "UK TIMES direct heat in chemicals")
        return None
    if "drying-separation" in proc and level == "base":
        return ("direct-heater_electric-process" if elec else "dryer_direct-fired",
                "UK TIMES drying outside pulp and paper")
    if "drying-separation" in proc and level == "strong":
        return ("dryer_direct-fired_efficiency-strong", "UK TIMES advanced drying outside pulp and paper")
    return None


LEAF = "<sector>.metal-smelting.product.{}.hydrometallurgy"
HYDRO = [LEAF.format(m) for m in ("copper", "nickel", "zinc")]
# archetype: (branches to keep or set, end-use, note); None branches means drop listed ones
SERVICE_SET = {
    "electrolysis-cell_chlor-alkali-membrane": (["<sector>.chemicals.product.chlor-alkali.chlorine-electrolysis"], "electrochemical-products", "membrane cells make chlorine and caustic soda"),
    "electrolysis-cell_sodium-chlorate": (["<sector>.chemicals.product.sodium-chlorate"], "electrochemical-products", "the sodium chlorate leaf"),
    "leaching-vessel_heap-atmospheric": (["<sector>.mining.service.leaching"] + HYDRO, None, "heap leaching with SX-EW: copper, nickel and zinc"),
    "leaching-vessel_bioleaching": (["<sector>.mining.service.leaching"] + HYDRO, None, "bioleaching: copper, nickel and zinc"),
    "leaching-vessel_high-pressure-acid": (["<sector>.mining.service.leaching"] + HYDRO, None, "pressure leaching: copper, nickel and zinc"),
    "electrolysis-cell_advanced-anodes": (HYDRO, "hydrometallurgy", "electrowinning of copper, nickel and zinc"),
    "adsorber_direct-lithium": (["<sector>.mining.service.separation", "<sector>.mining.service.crystallization"], "separation-and-processing", "lithium from brine: separation and crystallization"),
}
SERVICE_ADD = {
    "flotation-cell_froth": [("<sector>.mining.service.separation", "separation-and-processing", "froth flotation of metal ores")],
    "steam-reformer_efficiency-moderate": [("<sector>.chemicals.product.ammonia-methanol.ammonia", "ammonia-and-methanol", "its UKERC host is the ammonia reformer")],
    "autothermal-reformer": [("<sector>.chemicals.product.ammonia-methanol.ammonia", "ammonia-and-methanol", "its UKERC example is an ammonia-plant reformer")],
}
ARCH_EDIT = {
    "oven_indirect-fired": {"product-unit": "t", "note": "product-unit t: its UKERC source prices it per t of product."},
}


def rd(p):
    with p.open(encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames, list(r)


def wr(p, cols, rows):
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    dry = "--dry-run" in sys.argv
    acols, arch = rd(REC / "archetype.csv")
    by = {a["archetype"]: a for a in arch}
    if any(k in by for k in NEW):
        sys.exit("already applied")
    ecols, exs = rd(REC / "source-example.csv")
    ids = [e["example-id"] for e in exs]
    plan, hits = {}, {}
    for pat, target, why in REMAP:
        rx = re.compile(pat)
        m = [i for i in ids if rx.fullmatch(i)]
        hits[pat] = m
        for i in m:
            plan[i] = (target, why)
    for i in ids:
        r = bataille_heat(i)
        if r and i not in plan:
            plan[i] = r
    dead = [p for p, m in hits.items() if not m]
    if dead:
        sys.exit("patterns with no match:\n  " + "\n  ".join(dead))
    known = set(by) | set(NEW) | {"", "(none)"}
    bad = {t for t, _ in plan.values()} - known
    if bad:
        sys.exit(f"unknown targets: {bad}")
    changes = [(e, *plan[e["example-id"]]) for e in exs
               if e["example-id"] in plan and plan[e["example-id"]][0] != e["archetype"]]
    for e, t, why in changes:
        print(f"{e['archetype'] or '(blank)':42} -> {t or '(blank)':46} {e['example-id']}")
    print(f"{len(changes)} examples change")
    if dry:
        return
    for e, t, why in changes:
        e["note"] = ((e["note"] + "; ") if e["note"] else "") + \
            f"was {e['archetype'] or 'blank'}, remapped {DAY} (assignment review): {why}"
        e["archetype"], e["seeded-by"] = t, "corrected"
    wr(REC / "source-example.csv", ecols, exs)

    scols, svc = rd(REC / "archetype-service.csv")
    for key, (host, label, typ, desc, named, srcs, note) in NEW.items():
        h = by[host]
        row = dict(h, archetype=key, label=label, type=typ, description=desc,
                   **{"examples-named": named, "sources": srcs, "note": note})
        arch.insert(arch.index(h) + 1, row)
        by[key] = row
        svc += [dict(s, archetype=key, note=f"as its host {host}") for s in svc if s["archetype"] == host]
    for key, edit in ARCH_EDIT.items():
        by[key].update(edit)
    # a moved example's carrier joins its new archetype's carriers
    vocab = {r["carrier"] for r in rd(REC / "vocabulary" / "carrier.csv")[1]}
    for e, t, _ in changes:
        if t in by:
            have = [c.strip() for c in by[t]["carriers"].split(";") if c.strip()]
            for tok in e["source-technology"].split("_")[1:]:
                if tok in vocab and tok not in have:
                    have.append(tok)
            by[t]["carriers"] = "; ".join(have)
    wr(REC / "archetype.csv", acols, arch)
    for key, (branches, eu, why) in SERVICE_SET.items():
        old = [s for s in svc if s["archetype"] == key]
        tmpl = old[0]
        keep = {s["branch"]: s for s in old}
        new = []
        for b in branches:
            s = keep.get(b) or dict(tmpl, branch=b)
            if eu:
                s["end-use"] = eu
            elif b not in keep:
                s["end-use"] = "hydrometallurgy" if "metal-smelting" in b else "separation-and-processing"
            s["note"] = f"corrected {DAY}: {why}"
            new.append(s)
        i = svc.index(old[0])
        svc = [s for s in svc if s["archetype"] != key]
        svc[i:i] = new
    for key, adds in SERVICE_ADD.items():
        tmpl = next(s for s in svc if s["archetype"] == key)
        i = max(j for j, s in enumerate(svc) if s["archetype"] == key) + 1
        svc[i:i] = [dict(tmpl, branch=b, **{"end-use": eu, "note": f"added {DAY}: {why}"}) for b, eu, why in adds]
    wr(REC / "archetype-service.csv", scols, svc)
    print(f"{len(NEW)} archetypes added; service links corrected for "
          f"{len(SERVICE_SET) + len(SERVICE_ADD)} archetypes")


if __name__ == "__main__":
    main()
