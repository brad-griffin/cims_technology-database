"""Option 1 boiler sizing: GHGRP facility CO2 divided by MSAPR Part 1 unit counts.

Mean rated input per unit = sector fossil CO2 / CO2 factor (natural gas, HHV) /
units / full-load hours. Upper bound: facility CO2 includes engines, turbines,
flares, kilns, dryers, and process CO2 that MSAPR units do not burn.

Unit counts: 2016 MSAPR RIAS Table 5 (2015 inventory, 819 units) and 2025
amendments RIAS (about 1,300 units, sector shares). Hours: 2016 RIAS assumption
of 90% load for 340 days a year.
"""
import sys
import pandas as pd

GHGRP = sys.argv[1] if len(sys.argv) > 1 else "../../../primary-sources/gov-can/eccc/eccc_2026_ghgrp-facility-ghg-emissions-2004-2024.csv"
EF = 0.05064            # t CO2/GJ natural gas, HHV (cf-ef-co2-natural-gas)
HOURS = 0.9 * 340 * 24  # full-load hours a year (2016 RIAS)
MIN_MW = 10.5 / 3.6     # MSAPR coverage threshold, MW input

SECTORS = {  # MSAPR sector: (NAICS prefixes, 2015 units, 2025 share, note)
    "pulp-paper": (["322"], 67, 0.066, "fossil CO2 only; includes lime kilns"),
    "base-metal-smelting": (["331410"], 50, None, "includes smelter process CO2"),
    "potash": (["212396"], 39, 0.021, "includes product dryers"),
    "chemicals": (["3251", "3252", "3254", "3259"], 60, 0.07,
                  "excludes fertilizer and industrial gas; crackers stay in the CO2 but MSAPR excludes them"),
    "oil-sands-and-upstream-oil-gas": (["211"], 387 + 179, 0.77,
                  "includes engines, turbines, cogeneration, flares, and upgrader SMRs"),
}
EXCLUDE = {"325313", "325120"}

d = pd.read_csv(GHGRP, encoding="utf-8-sig", low_memory=False, encoding_errors="replace")
d.columns = [c.split(" / ")[0] for c in d.columns]
d["naics"] = d["Facility NAICS Code"].astype(str)

rows = []
for sector, (pre, u2015, share, note) in SECTORS.items():
    m = d.naics.str.startswith(tuple(pre)) & ~d.naics.isin(EXCLUDE)
    for label, years, units in [("2015", (2015, 2015), u2015),
                                ("2022-2024", (2022, 2024), round(1300 * share) if share else None)]:
        if not units:
            continue
        x = d[m & d["Reference Year"].between(*years)]
        co2 = x["CO2 (tonnes)"].sum() / (years[1] - years[0] + 1)
        mw = co2 / EF / units / HOURS / 3.6
        rows.append(dict(sector=sector, years=label, facilities=x["GHGRP ID No."].nunique(),
                         fossil_co2_mt=round(co2 / 1e6, 2), units=units,
                         mean_input_mw_upper=round(mw, 1), note=note))
out = pd.DataFrame(rows)
out.to_csv("boiler-size-ghgrp.csv", index=False)
print(out.to_string(index=False))
print(f"MSAPR threshold {MIN_MW:.1f} MW input; full-load hours {HOURS:.0f}")


# ---- by emission source (2022-2023): stationary fuel combustion only ----------
# Removes process, flaring, venting, leakage, transport, and waste CO2. Still
# includes kilns, dryers, turbines, and engines.
BYSRC = "../../../primary-sources/gov-can/eccc/eccc_2026_ghgrp-facility-ghg-emissions-by-source-2022-2023.xlsx"
s = pd.read_excel(BYSRC, sheet_name=2)
s.columns = [c.split(" / ")[0] for c in s.columns]
s["naics"] = s["Facility NAICS Code"].astype(str)
s["Emission Source"] = s["Emission Source"].fillna("")
rows2 = []
for sector, (pre, u2015, share, note) in SECTORS.items():
    m = s.naics.str.startswith(tuple(pre)) & ~s.naics.isin(EXCLUDE)
    stat = s.loc[m & s["Emission Source"].str.startswith("Stationary"), "CO2 (tonnes)"].sum() / 2
    allsrc = s.loc[m, "CO2 (tonnes)"].sum() / 2
    units = round(1300 * share) if share else u2015
    rows2.append(dict(sector=sector, years="2022-2023", units=units,
                      units_basis="2025 RIAS share" if share else "2016 RIAS 2015 count",
                      stationary_co2_mt=round(stat / 1e6, 2), share_of_facility_co2=round(stat / allsrc, 2),
                      mean_input_mw_upper=round(stat / EF / units / HOURS / 3.6, 1)))
out2 = pd.DataFrame(rows2)
out2.to_csv("boiler-size-ghgrp-by-source.csv", index=False)
print(out2.to_string(index=False))
