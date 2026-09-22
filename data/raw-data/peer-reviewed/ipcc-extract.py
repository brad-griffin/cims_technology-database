"""Turn the IPCC Table 11.3 dump into the structured raw-data extraction.

Run from the repo root:   python data/raw-data/peer-reviewed/ipcc-extract.py
Reads the output of ipcc-dump.py; writes the files the database build (data/harmonized/pipeline/extract.py) reads.

Table 11.3 is a mitigation-option table, not an engineering table, and it has to
be read as one:

  * Its costs are per tonne of CO2-eq AVOIDED, not per unit of capacity or
    output. They are not capex and cannot be converted into it -- an abatement
    cost already nets this technology's cost against the incumbent's and divides
    by the emissions avoided. Hence the parameter `abatement-cost`, which exists
    for this table.
  * Its potentials are ceilings, and the caption says they are MULTIPLICATIVE
    across options, not additive. Recorded as `emissions-reduction-potential`
    with that warning on every row, because summing them is the obvious mistake.
  * Many cells hold a condition rather than a number -- "Cost of H2", "Near
    zero", "Subject to logistical, transport, sorting and recycling equipment
    costs". Those carry no value; the text is kept in the note rather than being
    forced into a number.

The rows are NOT auto-classified. Running them through the naming rules engine
that serves CIMS and UKERC produced confident nonsense -- "More recycling" came
out a shaft furnace, "Clinker substitution" a calciner, "Material efficiency" a
bare efficiency variant with no device at all -- because those rules read
equipment nouns out of technology names and this table's rows are strategies
written as prose. Every row is therefore mapped by hand in OPTIONS below, where
the judgement is one line per row and can be argued with. Three outcomes:

  * a technology name, or a list of them where IPCC puts several devices in one
    row ("boilers, 90C-140C heat pumps"). The values are recorded against each,
    with a note saying they came from one shared row.
  * STRATEGY -- a demand- or material-side option with no device to name
    (material efficiency, recycling, clinker substitution, building design).
    Written to _strategies.csv with its numbers, because the roster has nowhere
    to put it and dropping it would hide a mitigation option the chapter rates.
  * INTENSITY -- a "current intensity" row, which states what a sector emits
    today rather than naming a technology, and often gives several numbers in
    one cell ("2.3/1.8 and 0.7"). Written to _sector-intensity.csv verbatim.

Every footnote names the primary literature behind a row (Axelson et al. 2018,
Leeson et al. 2017, Vogl et al. 2018 ...). Those are the real originals under
design doc D7: all 24 were resolved against the chapter's own reference list by
ipcc-references.py, registered in the manifest, and are attached here as
`source-original`, with the chapter itself as the via.

TWO FOOTNOTES ARE NOT ATTACHED, because the chapter's letters and its footnote
bodies disagree. Marker "e" labels four CCUS and hydrogen rows but its body is
about Molten Oxide Electrolysis; marker "f" labels the cement calcination CCUS
row but its body is about making hydrogen from SMR and ATR. Footnote f's text
does describe the CCUS rows that carry "e", so the two look transposed -- but
which way is a reading of the source, not a fact about it, and attaching the
wrong primary literature to a cost is worse than attaching none. Both rows keep
the footnote text in the note and are flagged.
"""
from __future__ import annotations

import collections
import csv
import importlib.util as _ilu
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
STEM = "ipcc_2022_ar6-wgiii-chapter11"
SOURCE_ID = "ipcc_2022_001"

_spec = _ilu.spec_from_file_location(
    "cims_map", ROOT / "compare" / "cims-model-inputs" / "build-cims-map.py")
cims_map = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(cims_map)

SECTOR = {
    "Iron and steel": "iron-and-steel",
    "Cement and concrete": "cement",
    "Aluminium and other non-ferrous metals": "non-ferrous-metals",
    # The trailing "i" is this row's footnote marker, printed at full size
    # rather than raised, so the dump cannot tell it from the band's own text.
    "Chemicals (see also cross-cutting feedstocks above)i": "chemicals",
    "Pulp and paper": "pulp-and-paper",
    "Other manufacturing": "other-industry",
    "Cross-cutting (CCUS, H2, net zero CoOxHy fuels/feedstocks)": "all-industry",
}
STRATEGY, INTENSITY = "STRATEGY", "INTENSITY"

# Footnote letter -> the short forms its body cites, as registered by
# ipcc-references.py. d and h cite nothing (a unit conversion and a corporate
# announcement), i is a sector-level note, and e and f are the crossed pair
# described above.
FOOTNOTE_CITES = {
    "a": ["Birat 2012", "Leeson et al 2017", "Axelson et al 2018"],
    "b": ["Axelson et al 2018"],
    "c": ["Fischedick et al 2014b", "Vogl et al 2018"],
    "g": ["Fechner and Kray 2012", "Lehne and Preston 2018", "Habert et al 2020"],
    "j": ["De Luna et al 2019"],
    "k": ["Bazzanella and Ausfelder 2017", "Philibert 2017a", "Philibert 2017b",
          "IEA 2019f", "Armijo and Philibert 2020"],
    "l": ["Abbas and Wan Daud 2010", "Amin et al 2011", "Ashik et al 2015"],
    "m": ["De Luna et al 2019"],
    "n": ["Li et al 2019", "van der Meijden et al 2011"],
    "o": ["Keith et al 2018", "Fasihi et al 2019"],
}
CROSSED = {
    "e": "IPCC marker 'e' labels this row but footnote e's body is about Molten "
         "Oxide Electrolysis; footnote f's body describes rows like this one. The "
         "two look transposed in the chapter, so no primary source is attached.",
    "f": "IPCC marker 'f' labels this row but footnote f's body is about making "
         "hydrogen from SMR and ATR, not cement calcination. The chapter's e and f "
         "look transposed, so no primary source is attached.",
}

# One line per row of Table 11.3, keyed on the option text as the dump writes it.
# Names use only terms already in design doc section 6.2 -- this table needed no
# new vocabulary. Where two rows would otherwise collide the source's own words
# separate them: the steel electrolysis row names SIDERWIN, so it takes the
# ulcowin variant, leaving the bare electrolysis cell to aluminium; and the
# reversible solid oxide unit is a fuel cell run backwards, which is what
# distinguishes it from the alkaline and PEM electrolysers.
OPTIONS = {
    "Current intensity – all steel (worldsteel)": INTENSITY,
    "Current intensity – ~BF-BOF/Best BF-BOF and NG-DRI (with near-zero GHG electricity)": INTENSITY,
    "Current intensity – EAF (depends on electricity intensity & pre-heating fuel)": INTENSITY,
    "Material efficiency (IEA 2019 ‘Material Efficiency…’)": STRATEGY,
    "More recycling; depends on available stock, recycling network, quality of scrap, "
    "availability of DRI for dilution": STRATEGY,
    "BF-BOF with top gas recirculation and CCU/S":
        [("blast-furnace_top-gas-recycling-ccs", "material-conversion")],
    "Syngas (H2 & CO) DRI EAF with concentrated flow CCU/S":
        [("shaft-furnace_syngas_ccs", "material-conversion")],
    "Hisarna with concentrated CO2 capture":
        [("smelting-vessel_hisarna-ccs", "material-conversion")],
    "Hydrogen DRI EAF – fossil hydrogen with CCS is in operation, electrolysis-based "
    "hydrogen scheduled for 2026": [("shaft-furnace_hydrogen", "material-conversion")],
    "Aqueous (e.g., SIDERWIN) or Molten Oxide (e.g., Boston Metals) Electrolysis (MOE)":
        [("electrolysis-cell_electricity_ulcowin", "material-conversion")],
    "Current intensity, about 60% is limestone calcination": INTENSITY,
    "Building design to minimise concrete (IEA 2019b, 2020a)": STRATEGY,
    "Alternative lower-GHG fuels, e.g., waste (biofuels and hydrogen, see above)":
        [("kiln_municipal-waste", "material-conversion"),
         ("kiln_biomass", "material-conversion"),
         ("kiln_hydrogen", "material-conversion")],
    "CCUS for process heating & CaCO3 calcination CO2 (e.g., LEILAC, possible retrofit)":
        [("calciner_ccs", "material-conversion")],
    "Clinker substitution (e.g., limestone + calcined clays)": STRATEGY,
    "Use of multi-sized and well-dispersed aggregates": STRATEGY,
    "Magnesium or ultramafic cements": STRATEGY,
    "Current Al intensity, from hydro- to coal-based electricity production. 1.5 tCO2 are "
    "produced by graphite electrode decay": INTENSITY,
    "Inert electrodes and green electricity":
        [("electrolysis-cell_electricity", "material-conversion")],
    "Hydro/electrolytic smelting (with CO2 CCUS if necessary)":
        [("smelting-vessel_electricity", "material-conversion")],
    "Catalysis of ammonia from low-/zero-GHG hydrogen H2":
        [("reactor_hydrogen", "material-conversion")],
    "Electrocatalysis: CH4, CH3OH, C2H5OH, CO, olefins":
        [("reactor_electricity", "material-conversion")],
    "Catalysis of olefins from: (m)ethanol, H2 and COx directly":
        [("reactor_methanol", "material-conversion")],
    "End-use plastics, mainly CCUS and recycling": STRATEGY,
    "Full biomass firing, including lime kilns": [("kiln_biomass", "material-conversion")],
    "Electrification using current tech (boilers, 90°C–140°C heat pumps":
        [("boiler_electricity", "steam-and-hot-water"),
         ("heat-pump_electricity", "process-heat-low-temp")],
    "Using new tech (induction, plasma heating)":
        [("induction-heater_electricity", "process-heat-high-temp"),
         ("plasma-torch_electricity", "process-heat-high-temp")],
    "CCUS of post-combustion CO2 diluted in nitrogen":
        [("capture-unit_post-combustion", "other-services")],
    "CCUS of concentrated CO2": [("capture-unit", "other-services")],
    "H2 production: steam or auto-thermal CH4 reforming with CCS":
        [("steam-reformer_natural-gas_ccs", "material-conversion")],
    "H2 production: coal with CCUS": [("gasifier_coal_ccs", "material-conversion")],
    "H2 production: alkaline or PEM electrolysis":
        [("electrolyser_electricity", "material-conversion")],
    "H2 production: reversible solid oxide fuel electrolysis":
        [("fuel-cell_electricity", "material-conversion")],
    "H2 production: CH4 pyrolysis or catalytic cracking":
        [("reactor_natural-gas", "material-conversion")],
    "Hydrogen as CH4 replacement": STRATEGY,
    "Biogas or liquid replacement hydrocarbons": STRATEGY,
    "Anaerobic digestion/fermentation: CH4, CH3OH and C2H5OH":
        [("anaerobic-digester_biomass", "material-conversion"),
         ("fermenter_biomass", "material-conversion")],
    "Methane or methanol from H2 and COx (CCUS for excess). Maximum –50% reduction if "
    "C source is FF": [("reactor_hydrogen_ccs", "material-conversion")],
    "850°C woody biomass gasification with CCS for excess carbon: CO, CO2, H2, H2O, CH4, "
    "C2H4 and C6H6": [("gasifier_biomass_ccs", "material-conversion")],
    "Direct air capture for short- and long-chain CoOxHy":
        [("capture-unit_direct", "other-services")],
}
NUM = r"[0-9]+(?:\.[0-9]+)?"


def clean(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()


def span(text: str, pattern: str):
    """(value, min, max, qualifier) from a cell like 'USD70-130 t-1' or 'Up to 40%'.

    Returns None where the cell holds a condition rather than a quantity, which
    is most of the cost column. A range becomes min and max with the midpoint as
    the value; 'Up to' and '=<' become a maximum with no central estimate, and
    'at least' a minimum, because the source has not given one.
    """
    t = text.replace("–", "-").replace("−", "-").replace("≤", "<=").replace("≥", ">=")
    m = re.search(pattern.replace("NUM", NUM), t, re.I)
    if not m:
        return None
    lo, hi = m.group("lo"), m.groupdict().get("hi")
    lo, hi = float(lo), (float(hi) if hi else None)
    if re.search(r"(up to|<=|less than|below)", t, re.I) and hi is None:
        return "", "", lo, "ceiling"
    if re.search(r"(>=|at least|more than|about|around)", t, re.I) and hi is None:
        q = "floor" if ">=" in t or re.search(r"at least|more than", t, re.I) else "approximate"
        return ("" if q == "floor" else lo), (lo if q == "floor" else ""), "", q
    if hi is not None:
        return round((lo + hi) / 2, 4), lo, hi, "range"
    return lo, "", "", "point"


def main() -> int:
    src = HERE / f"{STEM}_table-11-3.csv"
    if not src.exists():
        print(f"missing {src.name}; run ipcc-dump.py first", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
    notes = {r["footnote"]: r["text"] for r in
             csv.DictReader((HERE / f"{STEM}_table-11-3-footnotes.csv")
                            .open(encoding="utf-8-sig"))}
    cited = {r["short-form"]: r["source-id"] for r in
             csv.DictReader((HERE / f"{STEM}_cited-references.csv")
                            .open(encoding="utf-8-sig")) if r.get("source-id")}
    missing = sorted({c for v in FOOTNOTE_CITES.values() for c in v} - set(cited))
    if missing:
        print("  short forms with no registered source-id: " + ", ".join(missing),
              file=sys.stderr)

    PCOLS = ["process", "technology", "parameter", "target", "unit", "value",
             "value-min", "value-max", "formula", "reference", "source-original", "note"]
    NCOLS = ["process", "technology", "sector", "end-use", "process-step", "service-unit"]
    params, nodes, intens, unnamed, refs, strat = [], {}, [], [], [], []
    seen = set()
    CAP = ("Percentages of maximum reduction are multiplicative, not additive "
           "(Table 11.3 caption): they must never be summed across options.")

    for r in rows:
        sector = SECTOR.get(r["sector"].strip())
        if not sector:
            unnamed.append((r["option"][:60], f"sector {r['sector']!r}"))
            continue
        opt = clean(r["option"])
        ref = f"IPCC AR6 WGIII Chapter 11, Table 11.3, p.{r['page']}"
        fn = notes.get(r["footnote"], "")
        base = opt + "."
        if fn:
            base += f" IPCC footnote {r['footnote']}: {fn}"
        # Two-level attribution (D7): the value belongs to the work IPCC cites,
        # and IPCC is the compilation it came through.
        originals = [cited[c] for c in FOOTNOTE_CITES.get(r["footnote"], [])
                     if c in cited]
        if r["footnote"] in CROSSED:
            base += " " + CROSSED[r["footnote"]]

        mapped = OPTIONS.get(opt)
        seen.add(opt)
        if mapped is None:
            unnamed.append((opt[:70], "not in the OPTIONS map"))
            continue
        if mapped is INTENSITY:
            intens.append({"sector": sector, "statement": opt,
                           "current-intensity": r["current-intensity"],
                           "unit": "tCO2-eq/t", "reference": ref, "note": base})
            continue
        if mapped is STRATEGY:
            strat.append({"sector": sector, "strategy": opt,
                          "potential-ghg-reduction": r["potential-ghg-reduction"],
                          "nasa-trl": r["nasa-trl"],
                          "abatement-cost": r["abatement-cost"],
                          "year-available": r["year-available"],
                          "reference": ref, "note": base})
            continue

        proc = r["sector"].strip()
        shared = (f" IPCC gives one row for {len(mapped)} devices "
                  f"({', '.join(n for n, _ in mapped)}); the same values are "
                  f"recorded against each." if len(mapped) > 1 else "")
        for name, eu in mapped:
            nodes.setdefault((proc, name), {
                "process": proc, "technology": name, "sector": sector,
                "end-use": eu, "process-step": "", "service-unit": "t"})

        def emit(param, cell, unit, extra="", name=None, base=base, shared=shared,
                 proc=proc, ref=ref):
            got = span(cell, r"(?P<lo>NUM)\s*(?:-\s*(?P<hi>NUM))?")
            note = base + (" " + extra if extra else "") + shared
            if got is None:
                params.append({"process": proc, "technology": name, "parameter": param,
                               "target": "", "unit": "", "value": "", "value-min": "",
                               "value-max": "", "formula": "", "reference": ref,
                               "source-original": ";".join(originals),
                               "note": note + f" NOT QUANTIFIED: the {param} cell reads "
                                              f"{cell!r}, a condition rather than a number."})
                return
            v, lo, hi, q = got
            params.append({"process": proc, "technology": name, "parameter": param,
                           "target": "co2e" if param != "abatement-cost" else "",
                           "unit": unit, "value": v, "value-min": lo, "value-max": hi,
                           "formula": "", "reference": ref,
                           "source-original": ";".join(originals),
                           "note": note + f" Cell reads {cell!r}, read as a {q}."})

        for name, _ in mapped:
            if r["potential-ghg-reduction"]:
                emit("emissions-reduction-potential", r["potential-ghg-reduction"],
                     "%", CAP, name=name)
            if r["abatement-cost"]:
                emit("abatement-cost", r["abatement-cost"], "2019_USD/t-CO2-eq",
                     "Cost per tonne of CO2-eq AVOIDED against the incumbent, not a "
                     "capital or operating cost.", name=name)
            for col, param in (("nasa-trl", "trl"), ("year-available", "year-available")):
                if r[col]:
                    params.append({"process": proc, "technology": name,
                                   "parameter": param, "target": "", "unit": "",
                                   "value": r[col].replace("–", "-"), "value-min": "",
                                   "value-max": "", "formula": "", "reference": ref,
                                   "source-original": ";".join(originals),
                                   "note": base + shared + (
                                       " NASA TRL scale, as the column heading states."
                                       if col == "nasa-trl" else "")})
            if fn:
                refs.append({"footnote": r["footnote"], "technology": name,
                             "option": opt, "cited-sources": fn})

    for path, cols, out in (
            (HERE / f"{STEM}.csv", PCOLS, params),
            (HERE / f"{STEM}_nodes.csv", NCOLS, list(nodes.values())),
            (HERE / f"{STEM}_sector-intensity.csv",
             ["sector", "statement", "current-intensity", "unit", "reference", "note"],
             intens),
            (HERE / f"{STEM}_strategies.csv",
             ["sector", "strategy", "potential-ghg-reduction", "nasa-trl",
              "abatement-cost", "year-available", "reference", "note"], strat),
            (HERE / f"{STEM}_footnote-sources.csv",
             ["footnote", "technology", "option", "cited-sources"], refs)):
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader(); w.writerows(out)
        print(f"  {path.name:52} {len(out):>4} rows")

    quant = sum(1 for p in params if p["value"] != "" or p["value-max"] != "")
    print(f"\n  {len(nodes)} technologies, {len(params)} parameter rows "
          f"({quant} carrying a number, {len(params) - quant} recording an "
          f"unquantified condition)")
    print("  " + ", ".join(f"{n} {k}" for k, n in collections.Counter(
        p["parameter"] for p in params).most_common()))
    missing = [k for k in OPTIONS if k not in seen]
    if missing:
        print(f"  {len(missing)} OPTIONS entr(ies) matched no row -- the dump text "
              "has changed:")
        for k in missing:
            print(f"      {k[:78]}")
    if unnamed:
        print(f"  {len(unnamed)} row(s) not carried:")
        for o, why in unnamed:
            print(f"      {o} -- {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
