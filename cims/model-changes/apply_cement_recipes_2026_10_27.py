"""Apply the cement recipe restructure (sanity-check S121, 2026-10-27) to the CIMS
model inputs.

The CIMS model inputs (data/model_inputs/model/industrial_minerals/*.csv in the cims
repo) are gitignored there, so this script and its revert are the record of the change.

What it adds to each province file:
  * four techs at Products.Cement that request a recipe rather than one Portland
    cement tonne: LC3 calcined clay cement, Slag blended cement, Alkali-activated
    cement and Electrochemical cement (Sublime);
  * two new nodes with their techs: Products.Cement.Calcined Clay (flash calciner,
    rotary kiln calciner) and Products.Cement.Ground Slag (slag drying and grinding).
The existing techs (Std process, Carbon curing, Increased clinker substitution) stay
for calibration. Values are the database's central values (2025 CAD), from
data/processed_data/technology_database after the S121 build. The clinker request is scaled by the
province's own clinker per t Portland cement over 0.95. The alkali activator is a
cost only (Brad 2026-10-28: the sectors are not linked): the database's opex-variable
of 75 CAD per t binder is a service request to CIMS.Generic Fuels.VOM, which costs $1
per unit, as the CCS nodes carry their variable cost.

STATUS (Brad 2026-10-28): NOT APPLIED. The design stays in the tech_data hierarchy
(records/cims_hierarchy.csv) and the change log (cims/hierarchy-change-requests.md)
until it is built into the CIMS data processing, calibration and model scripts.

Usage: python apply_cement_recipes_2026_10_27.py <cims>/data/model_inputs/model/industrial_minerals
Undo:  python revert_cement_recipes_2026_10_27.py <same folder>
"""
import csv
import glob
import io
import os
import sys

SRC = "EMRG technology database 2026-10-27 (2025 CAD)"


def line(vals):
    o = io.StringIO()
    csv.writer(o, lineterminator="").writerow(vals)
    return o.getvalue()


def main(folder):
    for f in sorted(glob.glob(os.path.join(folder, "industrial_minerals_*.csv"))):
        raw = open(f, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in raw else "\n"
        L = raw.split(nl)
        if any("Cement.Calcined Clay" in l for l in L):
            print("already applied:", f)
            continue
        R = os.path.basename(f).split("_")[-1][:2].upper()
        pre = f"CIMS.CAN.{R}.Industrial Minerals"
        cem = f"{pre}.Products.Cement"
        pc_clk = [l for l in L if l.startswith(cem + ".Portland cement,") and "service_request" in l
                  and l.split(",")[9].endswith("Portland cement.Clinker")]
        clk = float(next(csv.reader([pc_clk[0]]))[13])
        k = clk / 0.95
        fin = [l for l in L if l.startswith(cem + ".Portland cement,") and "service_request" in l
               and l.split(",")[9].endswith("Finish Grinding")]
        fg = float(next(csv.reader([fin[0]]))[13])

        def tech(branch, service, name, avail, life, ms, fcc, fom, reqs):
            base = [branch, "Service", R, "Industrial Minerals", service, name]
            rows = [base + ["technology", "", "", "", "", "", "", ""],
                    base + ["available", "", "", "", SRC, "Year", '""', f"{avail:.1f}"],
                    base + ["unavailable", "", "", "", SRC, "Year", '""', "2101.0"],
                    base + ["lifetime", "", "", "", SRC, "Years", '""', f"{life:.1f}"],
                    base + ["market_share_total", "", "", "", SRC, "%", "2000", f"{ms:.1f}"],
                    base + ["output", "", "", "", SRC, "node unit", '""', "1.0"],
                    base + ["fcc", "", "", "", SRC, "$", '""', f"{fcc:g}"],
                    base + ["fom", "", "", "", SRC, "$", '""', f"{fom:g}"]]
            for tgt, unit, v in reqs:
                rows.append(base + ["service_request", "", "", tgt, SRC, unit, '""', f"{v:g}"])
            return rows

        def node(branch, service, unit):
            base = [branch, "Service", R, "Industrial Minerals", service, ""]
            return [base + ["service_provide", "", "", "", "JCIMS", unit, "", unit],
                    base + ["competition", "", "", "", "", "", '""', "Tech Compete"],
                    base + ["discount_rate_financial", "", "", "", "JCIMS", "%", '""', "0.35"],
                    base + ["heterogeneity", "", "", "", "JCIMS", "", '""', "10.0"]]

        CL = f"{cem}.Portland cement.Clinker"
        FG = f"{cem}.Portland cement.Finish Grinding"
        CCn = f"{cem}.Calcined Clay"
        GSn = f"{cem}.Ground Slag"
        aux = [(f"{pre}.HVAC", "GJ", 0.005), (f"{pre}.Lighting", "GJ", 0.005)]
        new = []
        new += tech(cem, "Cement", "LC3 calcined clay cement", 2025, 25, 0, 8.0, 0.651,
                    [(CL, "tonne", round(0.50 * k, 4)), (FG, "tonne", fg), (CCn, "tonne", 0.30)] + aux)
        new += tech(cem, "Cement", "Slag blended cement", 2020, 25, 0, 8.0, 0.651,
                    [(CL, "tonne", round(0.55 * k, 4)), (FG, "tonne", fg), (GSn, "tonne", 0.40)] + aux)
        new += tech(cem, "Cement", "Alkali-activated cement", 2025, 25, 0, 15.0, 1.221,
                    [(GSn, "tonne", 0.85), (f"{pre}.Direct Drive", "GJ", 0.03),
                     ("CIMS.Generic Fuels.VOM", "$", 75.0)] + aux)
        new += tech(cem, "Cement", "Electrochemical cement", 2030, 25, 0, 1200.0, 97.68,
                    [(f"CIMS.CAN.{R}.Electricity", "GJ", 5.0)] + aux)
        new += node(CCn, "Calcined Clay", "tonne")
        new += tech(CCn, "Calcined Clay", "Flash calciner", 1950, 25, 1, 151.6, 12.34,
                    [(f"{pre}.Heat", "GJ", 3.03), (f"{pre}.Direct Drive", "GJ", 0.10)])
        new += tech(CCn, "Calcined Clay", "Rotary kiln calciner", 1950, 25, 0, 170.0, 9.52,
                    [(f"{pre}.Heat", "GJ", 3.59), (f"{pre}.Direct Drive", "GJ", 0.12)])
        new += node(GSn, "Ground Slag", "tonne")
        new += tech(GSn, "Ground Slag", "Slag drying and grinding mill", 1950, 25, 1, 90.0, 7.33,
                    [(f"{pre}.Heat", "GJ", 0.55), (f"{pre}.Direct Drive", "GJ", 0.16)])
        last = max(i for i, l in enumerate(L) if l.startswith(cem + ",Service"))
        L[last + 1:last + 1] = [line(r) for r in new]
        open(f, "w", encoding="utf-8", newline="").write(nl.join(L))
        print(f, R, "clinker per t PC", clk, "factor", round(k, 4), "finish", fg, "rows added", len(new))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
