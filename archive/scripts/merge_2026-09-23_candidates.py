"""One-time edit (2026-09-23): fold the 14 candidate archetypes into their pairs.

The user reviewed the candidate merges listed in docs/decisions.md and asked for
all of them. For each (survivor, folded) pair: the folded archetype's examples
are repointed in source-example.csv, its hierarchy links join the survivor's,
its carriers, heat tiers, named examples and sources are added to the
survivor's, and its row is deleted. The survivor keeps its own family, type,
TRL, product unit and description; where the folded row differed, the note says
so. Discriminators no archetype uses any more leave the vocabulary.
Writes archive/scripts/archetype-merges-2026-09-23.csv.
"""
import csv
import sys
from pathlib import Path

ROOT = Path.cwd()
REC = ROOT / "data" / "harmonized" / "records"

# survivor, folded, new label for the survivor (blank keeps it), new product unit
MERGES = [
    ("boiler_electric", "boiler_electric-injection-steam", "", ""),
    ("combustion-turbine_heat-recovery-steam-generator", "combined-cycle_cogeneration", "", ""),
    ("heat-recovery-unit_dryer-exhaust", "heat-recovery-unit_dryer", "", ""),
    ("heat-recovery-unit_oven-exhaust", "heat-recovery-unit_oven-dryer",
     "Oven or dryer exhaust heat recovery", ""),
    ("ventilation-unit_demand-controlled", "ventilation-unit_mine-on-demand", "", ""),
    ("haul-truck_diesel-fleet", "haul-truck_truck-and-shovel", "", ""),
    ("separator_dry-stack-tailings", "separator_paste-tailings",
     "Thickened, paste or dry-stack tailings", "t"),
    ("distillation-column_heat-integrated", "distillation-column_progressive",
     "Heat-integrated, progressive or divided-wall distillation", ""),
    ("melting-furnace_induction", "induction-heater_melting-holding",
     "Induction melting and holding furnace", ""),
    ("dryer_rotary-direct-fired", "dryer_rotary-fluid-bed",
     "Direct-fired rotary or fluid-bed dryer or calciner", ""),
    ("pellet-plant_induration", "pellet-plant_straight-grate", "", ""),
    ("pellet-plant_induration", "pellet-plant_grate-kiln", "", ""),
    ("leaching-vessel_heap-atmospheric", "electrolysis-cell_sx-ew",
     "Heap or atmospheric leaching with SX-EW", ""),
    ("grinding-mill_vertical-roller", "grinding-mill_high-pressure-rolls", "", ""),
    ("radio-frequency-heater_drying", "radio-frequency-heater_vacuum-drying",
     "Microwave, radio-frequency or vacuum drying", ""),
]
LIST_COLS = ("carriers", "heat-tier", "examples-named", "sources")


def rd(p):
    with p.open(encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames, list(r)


def wr(p, cols, rows):
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def union(a, b):
    items = [x.strip() for x in (a + ";" + b).split(";") if x.strip()]
    return "; ".join(dict.fromkeys(items))


def main():
    acols, arch = rd(REC / "archetype.csv")
    by = {a["archetype"]: a for a in arch}
    if not all(f in by for _, f, _, _ in MERGES):
        sys.exit("a folded archetype is already gone: this edit ran once, on 2026-09-23")
    scols, svc = rd(REC / "archetype-service.csv")
    ecols, exs = rd(REC / "source-example.csv")
    log = []
    for keep, fold, label, pu in MERGES:
        k, f = by[keep], by[fold]
        diffs = [f"{c} {f[c]}" for c in ("family", "type", "trl", "product-unit")
                 if f[c] and f[c] != k[c]]
        for c in LIST_COLS:
            k[c] = union(k[c], f[c])
        note = f"Merged {fold} ({f['label']}) 2026-09-23" + (
            f"; it had {', '.join(diffs)}." if diffs else ".")
        k["note"] = (k["note"] + " " if k["note"] else "") + note
        if label:
            k["label"] = label
        if pu:
            k["product-unit"], k["product"] = pu, f"{pu} tailings"
        have = {s["branch"] for s in svc if s["archetype"] == keep}
        for s in svc:
            if s["archetype"] == fold:
                s["archetype"] = keep
                if s["branch"] in have:
                    s["_drop"] = True
                have.add(s["branch"])
        moved = 0
        for e in exs:
            if e["archetype"] == fold:
                e["archetype"] = keep
                e["note"] = (e["note"] + "; " if e["note"] else "") + f"was {fold}, merged 2026-09-23"
                moved += 1
        log.append({"folded": fold, "into": keep, "folded-label": f["label"],
                    "examples-moved": moved, "differences": "; ".join(diffs)})
        arch.remove(f)
        del by[fold]
    svc = [s for s in svc if not s.pop("_drop", False)]
    wr(REC / "archetype.csv", acols, arch)
    wr(REC / "archetype-service.csv", scols, svc)
    wr(REC / "source-example.csv", ecols, exs)
    # discriminators no archetype uses any more
    mods = {r["modifier"] for r in rd(REC / "vocabulary" / "modifier.csv")[1]}
    used = set()
    for a in arch:
        p = a["archetype"].split("_")
        while len(p) > 1 and p[-1] in mods:
            p.pop()
        used.add("_".join(p[1:]))
    dcols, disc = rd(REC / "vocabulary" / "discriminator.csv")
    wr(REC / "vocabulary" / "discriminator.csv", dcols, [d for d in disc if d["discriminator"] in used])
    wr(ROOT / "archive" / "scripts" / "archetype-merges-2026-09-23.csv",
       ["folded", "into", "folded-label", "examples-moved", "differences"], log)
    print(f"{len(log)} folded; {len(arch)} archetypes; "
          f"{len(disc) - sum(1 for d in disc if d['discriminator'] in used)} discriminators dropped")


if __name__ == "__main__":
    main()
