"""Extract a Danish Energy Agency technology-data workbook (the `alldata_flat` sheet)
into the ETSAP-brief shape: <stem>.csv, <stem>_nodes.csv and <stem>_projections.csv.

Usage (from data/raw-data):
    python gov-dk/dea/dea-extract.py <workbook stem> <config name>

Only the current year (the catalogue's first data year, 2025 in the 2026 editions)
is loaded: the central estimate ('ctrl') is the value and the 'lower'/'upper'
estimates for the same year are value-min/value-max (the catalogue's own
uncertainty range). Later years go to _projections.csv. Parameters with no home
in the parameter vocabulary go to _other-values.csv, as printed.

DEA units are converted only where the conversion is exact: M EUR/MW -> EUR/kW
(x 1000), EUR/MW/yr -> EUR/kW-yr (/ 1000), EUR/MWh kept, fractions -> %.
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))   # extraction/
from paths import RECORDS, ROOT as REPO_ROOT, source_dirs  # noqa: E402
# documents in primary-sources/, extractions in data/raw_data/technology_database/ (2026-11-06)
DOCS, HERE = source_dirs(__file__)

# per workbook: sheet prefix -> (technology, process, sector, end-use, service-unit)
CONFIGS = {
    "iph": {
        "currency-year": 2025,
        "sheets": {
            "1.1 ": ("heat-pump_electricity_60c", "1.1 Heat pump up to 60 degC, 40 K lift", "all-industry", "steam-and-hot-water"),
            "1.2 ": ("heat-pump_heating-cooling_80c", "1.2 Combined heating and cooling heat pump up to 80 degC, 75 K lift", "all-industry", "steam-and-hot-water"),
            "2.a ": ("heat-pump_high-temperature_125c", "2.a High-temperature heat pump up to 125 degC", "all-industry", "steam-and-hot-water"),
            "2.b ": ("heat-pump_high-temperature_150c", "2.b High-temperature heat pump up to 150 degC", "all-industry", "steam-and-hot-water"),
            "4 MVR": ("vapour-recompressor_mvr", "4 Mechanical vapour recompression, 5 K", "all-industry", "steam-and-hot-water"),
            "5.1a": ("boiler_electric-steam_low-voltage", "5.1a Electric boiler 0.4-0.69 kV, steam 1-12 bar", "all-industry", "steam-and-hot-water"),
            "5.1b": ("boiler_electric-steam_10kv", "5.1b Electric boiler 10 kV, steam 1-12 bar", "all-industry", "steam-and-hot-water"),
            "5.2a": ("boiler_electric-hot-water_low-voltage", "5.2a Electric boiler 0.4-0.69 kV, hot water", "all-industry", "steam-and-hot-water"),
            "5.2b": ("boiler_electric-hot-water_10kv", "5.2b Electric boiler 10 kV, hot water", "all-industry", "steam-and-hot-water"),
            "6.1 ": ("boiler_natural-gas-oil", "6.1 Boiler, gas and oil", "all-industry", "steam-and-hot-water"),
            "6.2 ": ("boiler_biomass", "6.2 Boiler, biomass", "all-industry", "steam-and-hot-water"),
            "6.3 ": ("boiler_coal", "6.3 Boiler, coal", "all-industry", "steam-and-hot-water"),
            "7.1 ": ("direct-heater_natural-gas", "7.1 Direct firing, natural gas", "all-industry", "process-heat-high-temp"),
            "7.2 ": ("direct-heater_solid-fuel", "7.2 Direct firing, solid fuels", "all-industry", "process-heat-high-temp"),
            "7.3 ": ("direct-heater_electric", "7.3 Direct electric firing (resistance heating of process air)", "all-industry", "process-heat-high-temp"),
        },
    },
}

CAP = "CAPACITY BASIS: thermal-output"
COMBUSTION = {"boiler_natural-gas-oil", "boiler_biomass", "boiler_coal",
              "direct-heater_natural-gas", "direct-heater_solid-fuel"}


def rules(cy):
    """(regex on the printed parameter, database parameter, unit, scale, note)"""
    return [
        (r"^Heat generation capacity for one unit \[MW\]", "capacity", "MW", 1, CAP),
        (r"^Total efficiency, net \[%\], annual average", "efficiency", "%", 100,
         "net annual-average efficiency (a COP for heat pumps), printed as a fraction"),
        (r"^Technical lifetime", "lifetime", "years", 1, "technical lifetime"),
        (r"^Construction time", "construction-time", "years", 1, ""),
        (r"^Nominal investment", "capex", f"{cy}_EUR/kW", 1000,
         f"COST BASIS: installed. Nominal investment (equipment plus installation) per MW of heat output, printed in M EUR/MW; x 1000 to EUR/kW. {CAP}"),
        (r"^Fixed O&M", "opex-fixed", f"{cy}_EUR/kW-yr", 0.001,
         f"printed per MW (or MJ/s) of heat output per year; / 1000 to EUR/kW-yr. {CAP}"),
        (r"^Variable O&M", "opex-variable", f"{cy}_EUR/MWh", 1, "per MWh of heat output"),
        (r"^Minimum load", "load-range-min", "%", 100, "printed as a fraction of full load"),
        (r"^Temperature heat\s+supply, maximum", "temperature-max", "degC", 1, ""),
    ]


def num(v):
    if v is None or isinstance(v, str):
        return None
    return float(v)


def fmt(x):
    return ("%.6g" % x) if x is not None else ""


def main(stem, cfg_name):
    cfg = CONFIGS[cfg_name]
    cy = cfg["currency-year"]
    R = rules(cy)
    wb = openpyxl.load_workbook(DOCS / f"{stem}.xlsx", data_only=True, read_only=True)
    rows = list(wb["alldata_flat"].iter_rows(min_row=2, values_only=True))
    first_year = min(r[9] for r in rows if isinstance(r[9], int))
    data = {}
    for r in rows:
        ws, tech, cat, par, unit, py, note, ref, est, year, val = r[:11]
        data.setdefault((ws, tech, par, unit), {})[(est, year)] = val

    def sheet_key(ws):
        for k, v in cfg["sheets"].items():
            if ws.startswith(k):
                return v
        return None

    main_rows, other, proj, nodes = [], [], [], {}
    for (ws, tech, par, unit), vals in data.items():
        info = sheet_key(ws)
        if not info:
            continue
        tname, process, sector, eu = info
        nodes[(process, tname)] = (sector, eu)
        par_s = (par or "").strip()
        ref = f"sheet '{ws}'"
        c, lo, hi = (num(vals.get((e, first_year))) for e in ("ctrl", "lower", "upper"))
        rule = next((x for x in R if re.search(x[0], par_s)), None)
        for (e, y), v in sorted(vals.items(), key=lambda kv: (str(kv[0][1]), kv[0][0])):
            if y != first_year and v not in (None, "-"):
                proj.append([process, tname, par_s, unit, e, y, v, ref])
        if rule is None:
            if any(v not in (None, "-") for (e, y), v in vals.items() if y == first_year):
                other.append([process, tname, par_s, unit,
                              vals.get(("ctrl", first_year)), vals.get(("lower", first_year)),
                              vals.get(("upper", first_year)), first_year, ref])
            continue
        _, p, u, s, note = rule
        if c is None and lo is None and hi is None:
            continue
        sc = lambda x: x * s if x is not None else None
        # keep min/max only when they differ from the central value
        vmin, vmax = sc(lo), sc(hi)
        if vmin is not None and vmax is not None and vmin == vmax == sc(c):
            vmin = vmax = None
        formula = ""
        if s not in (1,):
            formula = f"{fmt(c)}*{s:g}" if c is not None else ""
        n = note
        if "from last update in 2019" in par_s:
            n += " The row is labelled 'from last update in 2019' although the catalogue states all costs are in 2025 EUR."
        if p == "efficiency" and ("heat-pump" in tname or "vapour" in tname):
            n += " Printed as a COP."
        if p == "efficiency" and tname in COMBUSTION:
            n += (" On the LHV (lower heating value) of the fuel: the catalogue states efficiencies"
                  " of fuel-burning technologies at the lower calorific value (introduction, 'Energy efficiencies').")
        main_rows.append([process, tname, p, "", u, fmt(sc(c)), fmt(vmin), fmt(vmax), formula,
                          ref + f", {first_year} central (lower/upper as min/max)", n.strip()])
    for (process, tname), (sector, eu) in nodes.items():
        main_rows.insert(0, [process, tname, "description", "", "", process.split(" ", 1)[1], "", "", "", "sheet title", ""])

    hdr = ["process", "technology", "parameter", "target", "unit", "value", "value-min", "value-max", "formula", "reference", "note"]
    main_rows.sort(key=lambda r: (list(cfg["sheets"]).index(next(k for k, v in cfg["sheets"].items() if v[0] == r[1])), r[2] != "description"))
    with open(HERE / f"{stem}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(hdr); w.writerows(main_rows)
    with open(HERE / f"{stem}_nodes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["process", "technology", "sector", "end-use", "process-step", "service-unit"])
        for (process, tname), (sector, eu) in nodes.items():
            w.writerow([process, tname, sector, eu, "", "GJ"])
    with open(HERE / f"{stem}_projections.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["process", "technology", "parameter-as-printed", "unit", "estimate", "year", "value", "reference"])
        w.writerows(proj)
    with open(HERE / f"{stem}_other-values.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["process", "technology", "parameter-as-printed", "unit", "central", "lower", "upper", "year", "reference"])
        w.writerows(other)
    print(f"{len(main_rows)} main rows, {len(nodes)} technologies, {len(proj)} projection rows, {len(other)} other values")


if __name__ == "__main__":
    main(*sys.argv[1:3])
