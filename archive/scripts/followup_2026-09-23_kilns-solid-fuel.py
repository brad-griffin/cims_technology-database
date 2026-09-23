"""One-time edit (2026-09-23), the user's rulings on the assignment review:

- Legacy cement kilns (wet, semi-wet, semi-dry Lepol, wet-precalciner, long dry)
  were still operating in Canada after 2000 (NRCan 2001 benchmark guide: two wet
  kilns in May 1999; the 2014 Multi-Sector Air Pollutants Regulations RIAS names
  wet, long dry, preheater and precalciner kilns as the kiln types in Canada), so
  they get one archetype together: kiln_legacy.
- Solid-fuel direct heaters and dryers (coal, coke, biomass, and coal tars, which
  UK TIMES costs the same as coal) are split from the gas- and liquid-fired ones:
  their capex is 5-10 times higher. Their strong-efficiency variants likewise.
- UKERC's BAT rotary kiln is listed under three baselines (C-DK3, C-SWK1, C-SDK1)
  with one cost; the semi-wet and semi-dry copies are marked (none).
- IEA high-temperature direct heaters sat on the low-temperature air or water
  heater; they move to the fired furnace.
The Bataille kiln post-combustion cost is marked incremental in
records/reference/incremental-cost.csv, not here.
"""
import csv
import re
import sys
from pathlib import Path

REC = Path.cwd() / "data" / "harmonized" / "records"
DAY = "2026-09-23"
SOLID = "coal|coke|biomass|benzole-and-tars"

# key: (service hosts, row template, label, type, heat-tier, carriers, description, named, sources, note)
NEW = {
    "kiln_legacy": (["kiln_dry-precalciner"], "kiln_dry-precalciner",
        "Legacy cement kiln (wet, semi-dry or long dry)", "conventional", "",
        "coal; petroleum-coke; natural-gas",
        "Wet, semi-wet, semi-dry (Lepol grate) and long dry rotary kilns: routes older than "
        "the preheater-precalciner kiln, using more than 15% more fuel per t clinker.",
        "wet, semi-wet, Lepol, wet-precalciner and long dry kilns (ETSAP I03)", "etsap_2010_003",
        "Still operating in Canada after 2000: two wet kilns in 1999 (NRCan cement benchmark "
        "guide, 2001); the 2014 MSAPR RIAS lists wet and long dry kilns among Canada's kiln types."),
    "direct-heater_solid-fuel": (["direct-heater_air-water", "direct-heater_fired-process",
                                  "direct-heater_furnace"], "direct-heater_fired-process",
        "Solid-fuel direct heater", "conventional", "", "coal; coke; biomass; benzole-and-tars",
        "A fired heater or furnace burning coal, coke, biomass or coal tars, with the fuel "
        "handling and firing equipment they need.",
        "UK TIMES solid-fuel direct heaters (Bataille 2017)", "bataille_2017_001",
        "Split from the gas- and liquid-fired heaters: UK TIMES costs solid-fuel units at 5-10 times "
        "the gas-fired unit. Coal tars are grouped here because UK TIMES costs them as coal."),
    "direct-heater_solid-fuel_efficiency-strong": (["direct-heater_efficiency-strong"],
        "direct-heater_efficiency-strong", "Solid-fuel direct heater efficiency measures, strong",
        "efficient variant", "", "coal; coke; biomass; benzole-and-tars",
        "The solid-fuel direct heater with incremental efficiency measures applied.",
        "UK TIMES advanced solid-fuel direct heaters (Bataille 2017)", "bataille_2017_001",
        f"Added {DAY}, split from direct-heater_efficiency-strong by fuel handling."),
    "dryer_solid-fuel": (["dryer_direct-fired"], "dryer_direct-fired", "Solid-fuel dryer",
        "conventional", "", "coal; coke; biomass; benzole-and-tars",
        "A direct-fired dryer burning coal, coke, biomass or coal tars.",
        "UK TIMES solid-fuel dryers (Bataille 2017)", "bataille_2017_001",
        "Split from the gas- and liquid-fired dryer: UK TIMES costs solid-fuel units at 5-10 times "
        "the gas-fired unit. Coal tars are grouped here because UK TIMES costs them as coal."),
    "dryer_solid-fuel_efficiency-strong": (["dryer_direct-fired_efficiency-strong"],
        "dryer_direct-fired_efficiency-strong", "Solid-fuel dryer efficiency measures, strong",
        "efficient variant", "", "coal; coke; biomass; benzole-and-tars",
        "The solid-fuel dryer with incremental efficiency measures applied.",
        "UK TIMES advanced solid-fuel dryers (Bataille 2017)", "bataille_2017_001",
        f"Added {DAY}, split from dryer_direct-fired_efficiency-strong by fuel handling."),
}
DISCRIMINATORS = {
    "legacy": "Wet, semi-wet, semi-dry or long dry cement kiln, without the dry preheater-precalciner layout",
}

B, E, U, I = "bataille_2017_001:", "etsap_2010_003:", "ukerc_2013_001:", "iea_2024_001:"
REMAP = [
    (E + r"kiln_(wet|semi-wet|lepol|wet-precalciner|long-dry)@clinker-kiln", "kiln_legacy",
     "a legacy kiln type still used in Canada after 2000"),
    (B + rf"direct-heater_({SOLID})(_efficiency-base)?@.*", "direct-heater_solid-fuel", "a solid-fuel direct heater"),
    (B + rf"direct-heater_({SOLID})_efficiency-strong@.*", "direct-heater_solid-fuel_efficiency-strong", "a solid-fuel direct heater, strong efficiency"),
    (B + rf"dryer_({SOLID})_efficiency-base@.*", "dryer_solid-fuel", "a solid-fuel dryer"),
    (B + rf"dryer_({SOLID})_efficiency-strong@.*", "dryer_solid-fuel_efficiency-strong", "a solid-fuel dryer, strong efficiency"),
    (U + r"kiln_bat@semi-(wet|dry)-kiln", "(none)",
     "duplicate of ukerc_2013_001:kiln_bat@dry-kiln: UKERC lists the same BAT rotary kiln and cost "
     "under three baselines (C-DK3, C-SWK1, C-SDK1)"),
    (I + r"direct-heater(_hydrogen)?@high-temperature", "direct-heater_furnace", "IEA: high-temperature direct heat"),
]


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
    plan = {}
    for pat, t, why in REMAP:
        m = [i for i in ids if re.fullmatch(pat, i)]
        if not m:
            sys.exit(f"no match: {pat}")
        for i in m:
            plan[i] = (t, why)
    changes = [(e, *plan[e["example-id"]]) for e in exs
               if e["example-id"] in plan and plan[e["example-id"]][0] != e["archetype"]]
    for e, t, _ in changes:
        print(f"{e['archetype'] or '(blank)':36} -> {t:44} {e['example-id'][:100]}")
    print(f"{len(changes)} examples change")
    if dry:
        return
    for e, t, why in changes:
        e["note"] = ((e["note"] + "; ") if e["note"] else "") + f"was {e['archetype'] or 'blank'}, remapped {DAY}: {why}"
        e["archetype"], e["seeded-by"] = t, "corrected"
    wr(REC / "source-example.csv", ecols, exs)

    scols, svc = rd(REC / "archetype-service.csv")
    for key, (hosts, tmpl, label, typ, tier, carriers, desc, named, srcs, note) in NEW.items():
        h = by[tmpl]
        row = dict(h, archetype=key, label=label, type=typ, carriers=carriers, description=desc,
                   **{"heat-tier": tier, "examples-named": named, "sources": srcs, "note": note})
        arch.insert(arch.index(h) + 1, row)
        by[key] = row
        seen = set()
        for s in list(svc):
            if s["archetype"] in hosts and (s["branch"], s["end-use"]) not in seen:
                seen.add((s["branch"], s["end-use"]))
                svc.append(dict(s, archetype=key, note=f"as {s['archetype']}"))
    # the gas- and liquid-fired archetypes no longer carry the solid fuels
    for key in ("direct-heater_air-water", "direct-heater_fired-process", "direct-heater_furnace",
                "direct-heater_efficiency-strong", "dryer_direct-fired",
                "dryer_direct-fired_efficiency-strong"):
        by[key]["carriers"] = "; ".join(c.strip() for c in by[key]["carriers"].split(";")
                                        if c.strip() and not re.fullmatch(SOLID, c.strip()))
    wr(REC / "archetype.csv", acols, arch)
    wr(REC / "archetype-service.csv", scols, svc)
    dcols, disc = rd(REC / "vocabulary" / "discriminator.csv")
    have = {d["discriminator"] for d in disc}
    for k, v in DISCRIMINATORS.items():
        if k not in have:
            disc.append({"discriminator": k, "definition": v, "reviewed": "yes"})
    disc.sort(key=lambda d: d["discriminator"])
    wr(REC / "vocabulary" / "discriminator.csv", dcols, disc)
    print(f"{len(NEW)} archetypes added")


if __name__ == "__main__":
    main()
