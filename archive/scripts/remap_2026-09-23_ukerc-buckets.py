"""One-time edit (2026-09-23): re-home the UKERC measure buckets that had been
folded onto boiler_condensing, heat-recovery-unit_oven-exhaust and
kiln_lumber-continuous (and the paper-dryer bucket on dryer_kiln-waste-heat).

The retired crosswalk folded them onto the nearest design technology; the user
approved moving each to the archetype it describes, adding the efficiency
bucket of the host where none existed, or marking it (none) where it is not a
technology option. New archetypes copy their host's family, product unit,
carriers, TRL and hierarchy links.
"""
import csv
import sys
from pathlib import Path

REC = Path.cwd() / "data" / "harmonized" / "records"
DAY = "2026-09-23"

# new key: (host, label, measures named)
NEW = {
    "boiler_fuel-fired_efficiency-moderate": ("boiler_fuel-fired",
        "Fuel-fired boiler efficiency measures, moderate",
        "boiler improvement to 80% and to 85% efficiency (UKERC ST-B1, ST-B2)"),
    "steam-cracker_fired-tubular_efficiency-moderate": ("steam-cracker_fired-tubular",
        "Steam cracker efficiency measures, moderate",
        "dividing-wall debutanizer/depropanizer; hybrid membrane-distillation for ethylene/ethane "
        "and butadiene separation (UKERC CH-SC1 to CH-SC3)"),
    "oven_efficiency-moderate": ("oven_tunnel-deck",
        "Bakery oven efficiency measures, moderate",
        "burner combustion control and firing-rate modulation, maintenance, heat-transfer "
        "optimisation, lighter baking tins (UKERC FD-B1, B2, B11, B12, B13, B25)"),
    "dryer_steam-heated_efficiency-moderate": ("dryer_steam-heated",
        "Paper dryer section efficiency measures, moderate",
        "reduced air infiltration, hood humidity, pressure and felt optimisation, condensate "
        "return, flash-steam use, low-pressure steam, heat recovery (UKERC PP-D1 to PP-D11)"),
    "dryer_steam-heated_efficiency-strong": ("dryer_steam-heated",
        "Paper dryer section efficiency measures, strong",
        "hot press ahead of the dryer section (UKERC PP-D12)"),
    "dryer_direct-fired_efficiency-moderate": ("dryer_direct-fired",
        "Direct-fired dryer efficiency measures, moderate",
        "UK TIMES dryer improvement option (Bataille 2017)"),
    "paper-machine_fourdrinier-gap_efficiency-strong": ("paper-machine_fourdrinier-gap",
        "Paper machine press section efficiency measures, strong",
        "steam boxes ahead of the press (UKERC PP-P2)"),
}
# example-id -> new archetype
REMAP = {
    "ukerc_2013_001:boiler_efficiency-moderate@boilers": "boiler_fuel-fired_efficiency-moderate",
    "ukerc_2013_001:boiler_steam_efficiency-moderate@steam-system": "(none)",
    "ukerc_2013_001:boiler_steam_efficiency-strong@undefined-sector-boilers": "heat-pump_industrial",
    "ukerc_2013_001:press_steam_efficiency-strong@press": "paper-machine_fourdrinier-gap_efficiency-strong",
    "ukerc_2013_001:steam-cracker_steam_efficiency-moderate@steam-cracker": "steam-cracker_fired-tubular_efficiency-moderate",
    "ukerc_2013_001:dryer_coke_efficiency-moderate@iron-manufacture": "coke-oven_efficiency-moderate",
    "ukerc_2013_001:dryer_efficiency-moderate@dryer": "dryer_steam-heated_efficiency-moderate",
    "ukerc_2013_001:dryer_steam_efficiency-moderate@dryer": "dryer_steam-heated_efficiency-moderate",
    "ukerc_2013_001:dryer_waste-heat_efficiency-moderate@dryer": "dryer_steam-heated_efficiency-moderate",
    "ukerc_2013_001:dryer_efficiency-strong@dryer": "dryer_steam-heated_efficiency-strong",
    "ukerc_2013_001:dryer_waste-heat_efficiency-strong@drying-systems": "heat-recovery-unit_dryer-exhaust",
    "bataille_2017_001:dryer_efficiency-moderate@production-processes-dryer-including-improvement-processes": "dryer_steam-heated_efficiency-moderate",
    "bataille_2017_001:dryer_natural-gas_efficiency-moderate@all-industry": "dryer_direct-fired_efficiency-moderate",
    "ukerc_2013_001:management-system_efficiency-moderate@bakery-non-ovens-including-cooler": "(none)",
    "ukerc_2013_001:management-system_efficiency-moderate@dairy": "(none)",
    "ukerc_2013_001:management-system_efficiency-moderate@subsector": "(none)",
    "ukerc_2013_001:management-system_electricity_efficiency-moderate@bakery": "(none)",
    "ukerc_2013_001:management-system_electricity_efficiency-moderate@sector": "pump_optimization",
    "ukerc_2013_001:oven_efficiency-moderate@bakery-direct-ovens": "oven_efficiency-moderate",
    "ukerc_2013_001:oven_efficiency-moderate@bakery-indirect-ovens": "oven_efficiency-moderate",
    "ukerc_2013_001:oven_efficiency-moderate@bakery-ovens": "oven_efficiency-moderate",
    "ukerc_2013_001:oven_efficiency-moderate@bakery-oven": "oven_efficiency-moderate",
    "ukerc_2013_001:oven_electricity_efficiency-moderate@bakery-ovens": "fan_optimization",
}
WHY_NONE = {
    "ukerc_2013_001:boiler_steam_efficiency-moderate@steam-system":
        "steam distribution efficiency, out of scope (design.md section 1)",
}
WHY_NONE_DEFAULT = "an organizational measure (good practice, maintenance, energy management), not a technology option"


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
    acols, arch = rd(REC / "archetype.csv")
    by = {a["archetype"]: a for a in arch}
    if any(k in by for k in NEW):
        sys.exit("already applied")
    scols, svc = rd(REC / "archetype-service.csv")
    for key, (host, label, measures) in NEW.items():
        h = by[host]
        row = dict(h, archetype=key, label=label, type="efficient variant",
                   description=f"The {h['label'].lower()} with incremental efficiency measures applied.",
                   **{"examples-named": measures, "sources": "ukerc_2013_001" if "UKERC" in measures
                      else "bataille_2017_001",
                      "note": f"Added {DAY} as the bucket for UKERC or UK TIMES measures on {host}."})
        arch.insert(arch.index(h) + 1, row)
        by[key] = row
        svc += [dict(s, archetype=key, note=f"as its host {host}") for s in svc if s["archetype"] == host]
    wr(REC / "archetype.csv", acols, arch)
    wr(REC / "archetype-service.csv", scols, svc)
    ecols, exs = rd(REC / "source-example.csv")
    done = set()
    for e in exs:
        new = REMAP.get(e["example-id"])
        if not new:
            continue
        why = (WHY_NONE.get(e["example-id"], WHY_NONE_DEFAULT) if new == "(none)"
               else "the retired crosswalk's fold did not describe it")
        e["note"] = ((e["note"] + "; ") if e["note"] else "") + f"was {e['archetype']}, remapped {DAY}: {why}"
        e["archetype"], e["seeded-by"] = new, "corrected"
        done.add(e["example-id"])
    missing = set(REMAP) - done
    if missing:
        sys.exit(f"examples not found: {missing}")
    wr(REC / "source-example.csv", ecols, exs)
    print(f"{len(NEW)} archetypes added, {len(done)} examples remapped")


if __name__ == "__main__":
    main()
