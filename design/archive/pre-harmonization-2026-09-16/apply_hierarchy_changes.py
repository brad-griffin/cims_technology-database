"""One-off: apply the suggested-branch column and the proposed nodes of
design/cims-hierarchy-crosswalk.csv to data/service-technology-map/cims_hierarchy.csv
(2026-09-16). Kept for provenance; the pre-change hierarchy is beside this file.

Leaves in the 15 industrial sectors are renamed, merged, split or removed as the
crosswalk says; proposed nodes are added; parent rows are then rebuilt from the
leaves (a parent with no remaining leaf is dropped, a missing parent is added).
Rows outside those sectors are untouched.
"""
import csv, io, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HIER = ROOT / "design/cims_hierarchy.csv"          # moved out of data/ on 2026-09-17
XW = ROOT / "design/cims-hierarchy-crosswalk.csv"
FP = "data/service-technology-map/"
SECTORS = {"biodiesel", "chemicals", "coal-mining", "construction", "direct-air-capture",
           "ethanol", "hydrogen", "industrial-minerals", "iron-and-steel",
           "light-industrial", "metal-smelting", "mining", "natural-gas",
           "petroleum-crude", "petroleum-refining", "pulp-and-paper"}

# shared technology data (general-services), by the path after the sector
SHARED = [
    (r"^service$", None),
    (r"^service\.steam$", "general-services/steam"),
    (r"^service\.ccs$", "general-services/ccs"),
    (r"^service\.ccs\.(concentrated|diffuse)$", r"general-services/ccs/\1"),
    (r"^service\.fuel-blend$", "general-services/fuel-blend"),
    (r"^service\.fuel-blend\.(.+)$", r"general-services/fuel-blend/\1"),
    (r"^service\.machine-drive$", "general-services/machine-drive"),
    (r"^service\.machine-drive\.(.+)$", r"general-services/machine-drive/\1"),
]
# ... and the two the industrial sectors share but the buildings sectors do not:
# commercial and residential heating, cooling and lighting are their own equipment.
SHARED_INDUSTRIAL = [
    (r"^service\.hvac$", "general-services/industrial/hvac"),
    (r"^service\.hvac\.(.+)$", r"general-services/industrial/hvac/\1"),
    (r"^service\.lighting$", "general-services/industrial/lighting"),
]


def filepath(branch):
    """Derived data-filepath for a new or renamed node."""
    _, sector, *rest = branch.split(".")
    tail = ".".join(rest)
    for rx, rep in SHARED + (SHARED_INDUSTRIAL if sector in SECTORS else []):
        if rep and re.match(rx, tail):
            return FP + re.sub(rx, rep, tail)
    return FP + "/".join([sector] + rest)


# Renames outside the 15 industrial sectors, which the crosswalk does not cover.
# Commercial (2026-09-17): the two climate-zone heating services and the cooling
# service become one `hvac` parent with the three leaves under it, as the industrial
# sectors already have.
RENAMES = {
    "<sector>.commercial.service.cooling": "<sector>.commercial.service.hvac.space-cooling",
    "<sector>.commercial.service.hvac_cold": "<sector>.commercial.service.hvac.space-heating_cold",
    "<sector>.commercial.service.hvac_marine": "<sector>.commercial.service.hvac.space-heating_marine",
    # Brick, tile, sanitaryware and refractories fire in the same kilns, so the
    # branch is named for the product family rather than one of its products
    # (the user, 2026-09-18).
    "<sector>.industrial-minerals.product.bricks": "<sector>.industrial-minerals.product.ceramics",
    "<sector>.industrial-minerals.product.bricks.kiln": "<sector>.industrial-minerals.product.ceramics.kiln",
    "<sector>.industrial-minerals.product.bricks.dryer": "<sector>.industrial-minerals.product.ceramics.dryer",
    # Single-child levels flattened 2026-09-17: the child is the only thing under
    # its parent, so no competition happens at the parent and the level says
    # nothing. Zinc keeps `pyrometallurgy.roasting` (the user), and the lime kilns
    # keep their own fuel requests until that sector is reviewed.
    "<sector>.industrial-minerals.product.lime.kiln": "<sector>.industrial-minerals.product.lime",
    "<sector>.light-industrial.service.heat.direct": "<sector>.light-industrial.service.heat",
    "<sector>.petroleum-refining.product.alkylates.alkylation": "<sector>.petroleum-refining.product.alkylates",
    # Natural gas, 2026-09-18. `extraction` holds resource types only, so the
    # activities move up beside it; gas compression is not MECS compressed air, so
    # it is renamed rather than filed under machine drive; the pumps are the MECS
    # pump service, so they move under it. The two venting nodes are the residual
    # inventory categories, and say so.
    "<sector>.natural-gas.product.supply.extraction.compression": "<sector>.natural-gas.product.supply.gas-compression",
    "<sector>.natural-gas.product.supply.extraction.drilling": "<sector>.natural-gas.product.supply.drilling",
    "<sector>.natural-gas.product.supply.extraction.well-tests": "<sector>.natural-gas.product.supply.well-tests",
    "<sector>.natural-gas.product.supply.extraction.off-road-transport": "<sector>.natural-gas.product.supply.off-road-transport",
    "<sector>.natural-gas.service.pumping": "<sector>.natural-gas.service.machine-drive.pumps",
    # `Direct Drive` means the motor speed-control accessory everywhere else, so the
    # natural gas node is named for what it drives (2026-09-18).
    "<sector>.natural-gas.service.direct-drive": "<sector>.natural-gas.service.compressor-drive",
    "<sector>.natural-gas.product.supply.venting.point-venting": "<sector>.natural-gas.product.supply.venting.other-point-venting",
    "<sector>.natural-gas.product.supply.venting.diffuse-venting": "<sector>.natural-gas.product.supply.venting.other-diffuse-venting",
    # Petroleum crude's `Industrial Engines` are a site-wide stationary engine fleet
    # competing only on fuel (diesel, gasoline, propane), requested by drilling,
    # onshore and offshore light-medium, heavy, in-situ, mining and upgrading. They
    # are not the motor-accessory `Direct Drive` of the other sectors, so they are
    # named for what they are (the user, 2026-09-18).
    "<sector>.petroleum-crude.service.direct-drive": "<sector>.petroleum-crude.service.field-engines",
    # Magnesium, 2026-09-18 (the user). The branch carried zinc's technology list
    # verbatim, so it spent real magnesium demand on leach tanks and zinc roasters.
    # The two routes Canada actually ran are named for what they are - molten-salt
    # electrolysis (Magnola to 2003, Norsk Hydro Becancour to 2007) and the
    # silicothermic retort (Timminco Haley, to about 2008). `melt-cast` stays: it
    # carries the SF6 cover-gas factor, which is the magnesium emission the NIR keeps
    # reporting after primary production ended, and it is five times the cell factor.
    "<sector>.metal-smelting.product.magnesium.pyrometallurgy.refining": "<sector>.metal-smelting.product.magnesium.electrolysis",
    "<sector>.metal-smelting.product.magnesium.pyrometallurgy.smelting": "<sector>.metal-smelting.product.magnesium.thermal-reduction",
    # Titanium named for its product (the user, 2026-09-18), matching the other
    # product branches. Rio Tinto Fer et Titane smelts ilmenite to titanium slag and
    # upgrades it by roast and leach; no titanium metal has been made in Canada.
    "<sector>.metal-smelting.product.titanium": "<sector>.metal-smelting.product.titanium-slag",
    "<sector>.metal-smelting.product.titanium.hydrometallurgy": "<sector>.metal-smelting.product.titanium-slag.hydrometallurgy",
    "<sector>.metal-smelting.product.titanium.pyrometallurgy": "<sector>.metal-smelting.product.titanium-slag.pyrometallurgy",
    "<sector>.metal-smelting.product.titanium.pyrometallurgy.roasting": "<sector>.metal-smelting.product.titanium-slag.pyrometallurgy.roasting",
    "<sector>.metal-smelting.product.titanium.pyrometallurgy.smelting": "<sector>.metal-smelting.product.titanium-slag.pyrometallurgy.smelting",
}

# Nodes dropped outright (2026-09-18). Glass batch preparation folds into the
# furnace. The machine-drive children are pruned to what each sector's model file
# actually has: light industrial carries one undifferentiated `Motive Power`, and
# refining has no conveyance service.
REMOVE = {
    "<sector>.chemicals.service.direct-drive",
    "<sector>.coal-mining.service.direct-drive",
    "<sector>.industrial-minerals.service.direct-drive",
    "<sector>.iron-and-steel.service.direct-drive",
    "<sector>.metal-smelting.service.direct-drive",
    "<sector>.mining.service.direct-drive",
    "<sector>.pulp-and-paper.service.direct-drive",
    "<sector>.industrial-minerals.product.glass.preparation",
    "<sector>.light-industrial.service.machine-drive.compressed-air",
    "<sector>.light-industrial.service.machine-drive.fans-and-blowers",
    "<sector>.light-industrial.service.machine-drive.materials-handling",
    "<sector>.light-industrial.service.machine-drive.materials-processing",
    "<sector>.light-industrial.service.machine-drive.pumps",
    "<sector>.petroleum-refining.service.machine-drive.materials-handling",
    # Magnesium is not leached and not roasted; those nodes were zinc's (2026-09-18).
    "<sector>.metal-smelting.product.magnesium.hydrometallurgy",
    "<sector>.metal-smelting.product.magnesium.pyrometallurgy",
    "<sector>.metal-smelting.product.magnesium.pyrometallurgy.roasting",
    # Slag is tapped, not cast.
    "<sector>.metal-smelting.product.titanium.melt-cast",
}


# CIMS carries a `Direct Drive` service (motor speed control, V-belt against variable
# speed) in seven sectors. It was added to the hierarchy on 2026-09-18 and taken out
# again the same day (the user): the drive is an efficiency variant of the motor
# technologies, not a service competing with them, and machine drive is being
# simplified to the nodes the hierarchy lists. Natural gas and petroleum crude keep
# their `service.direct-drive`: those are gas turbines and engines driving compressors
# and field equipment, a fuel choice rather than a motor accessory.
DIRECT_DRIVE = []

# Natural gas keeps its drive split, renamed for the prime mover rather than for size
# (the user, 2026-09-18). `Direct Drive Small` and `Direct Drive Large` were never a
# competition: every compression technology requests both at exogenous shares (94.8/5.2
# at extraction, 68.5/31.5 at processing, 26.1/73.9 at transmission), so the split is
# the reciprocating-engine fleet against the turbine fleet, each with its own
# electrification alternative. The compression nodes keep requesting shares of each.
ADD = [
    "<sector>.natural-gas.service.compressor-drive.engine",
    "<sector>.natural-gas.service.compressor-drive.turbine",
]

# Mining, restructured 2026-09-18: products are commodity x mine type, and the
# process steps become services the product nodes request. Adding a commodity is
# then one product node plus its service requests, not a new chain of steps.
MINING_PRODUCTS = [
    "metal.open-pit", "metal.underground",
    "potash.conventional", "potash.solution",
    "uranium.open-pit", "uranium.underground",
    "diamond.open-pit", "diamond.underground",
    "aggregate.open-pit",
]
# mine-haulage is already a service; these are the rest of the process steps.
MINING_SERVICES = [
    # dissolution folded into crystallization (both are the potash solution circuit)
    # and brine transport dropped (its one technology is a pipeline: the solution
    # product node requests the shared pump service), 2026-09-18
    "extraction", "crushing", "milling", "separation", "leaching",
    "crystallization", "compaction", "pelletizing", "drying", "tailings-disposal",
]
# mining service nodes that are NOT process steps and stay as they are
MINING_KEEP = ("machine-drive", "hvac", "lighting", "steam", "fuel-blend",
               "mine-haulage", "on-site-power")


# CIMS costs one CCS service per sector whatever the stream purity, so a sector with
# both a process stream and a flue-gas stream gets one price for both. Each sector's
# CCS node is split (or named) by stream, 2026-09-18. Natural gas keeps
# `product.supply.formation-co2` as the stream-and-decision node: its `Formation CCS`
# technology requests the concentrated service.
CCS_STREAMS = {
    "chemicals": ["concentrated", "diffuse"],
    "iron-and-steel": ["concentrated", "diffuse"],
    "petroleum-refining": ["concentrated", "diffuse"],
    "petroleum-crude": ["concentrated", "diffuse"],
    "natural-gas": ["concentrated", "diffuse"],
    "hydrogen": ["concentrated"],
    "industrial-minerals": ["diffuse"],
    "ethanol": ["diffuse"],
    "biodiesel": ["diffuse"],
}


def nest_composites(rows):
    """`service.ccs_x` -> `service.ccs.x` and `service.fuel-blend_x` ->
    `service.fuel-blend.x` (the user, 2026-09-18), which sometimes leaves a parent
    with one child. Electricity's capture nodes are renamed by stream at the same
    time, keeping the fuel so the parasitic energy stays right."""
    ELEC = {"ccs_biomass": "diffuse_biomass", "ccs_coal": "diffuse_coal",
            "ccs_natural-gas": "diffuse_natural-gas"}
    for r in rows:
        b = r["branch"]
        for comp in ("service.ccs_", "service.fuel-blend_"):
            if comp in b:
                b = b.replace(comp, comp[:-1] + ".")
        if b.startswith("<sector>.electricity.service.ccs."):
            leaf = b.rsplit(".", 1)[1]
            if leaf in ELEC:
                b = b.rsplit(".", 1)[0] + "." + ELEC[leaf]
        if b != r["branch"]:
            r["branch"] = b
            r["data-filepath"] = filepath(b)
    return rows


def ccs_split(rows):
    """Replace each sector's single `service.ccs` with stream-named services."""
    rows[:] = [r for r in rows
               if not (r["branch"].endswith(".service.ccs")
                       and r["branch"].split(".")[1] in CCS_STREAMS
                       and not any(o["branch"].startswith(r["branch"] + ".") for o in rows))
               and not (r["branch"].startswith("<sector>.natural-gas.product.supply.ccs"))]
    have = {r["branch"] for r in rows}
    for sector, streams in CCS_STREAMS.items():
        for s in streams:
            b = f"<sector>.{sector}.service.ccs.{s}"
            if b not in have:
                rows.append({"branch": b, "data-filepath": filepath(b)})
    return rows


def mining_restructure(rows):
    """Replace the mining product chain with commodity x mine-type products and
    process services. Idempotent: the desired set is written, the old one dropped."""
    keep = []
    for r in rows:
        b = r["branch"]
        if b.startswith("<sector>.mining.product"):
            continue
        if b.startswith("<sector>.mining.service.") and not any(
                b.split("<sector>.mining.service.")[1].startswith(k) for k in MINING_KEEP):
            continue
        keep.append(r)
    for p in MINING_PRODUCTS:
        b = f"<sector>.mining.product.{p}"
        keep.append({"branch": b, "data-filepath": filepath(b)})
    for s in MINING_SERVICES:
        b = f"<sector>.mining.service.{s}"
        keep.append({"branch": b, "data-filepath": filepath(b)})
    rows[:] = keep
    return rows


def apply_renames(rows):
    """Rename rows, add any parent the new paths need, and re-sort. Idempotent."""
    have = {r["branch"] for r in rows}
    rows[:] = [r for r in rows if r["branch"] not in REMOVE]
    mining_restructure(rows)
    ccs_split(rows)
    nest_composites(rows)
    have = {r["branch"] for r in rows}
    for s in DIRECT_DRIVE:
        b = f"<sector>.{s}.service.direct-drive"
        if b not in have:
            rows.append({"branch": b, "data-filepath": filepath(b)})
    for b in ADD:
        if b not in have:
            rows.append({"branch": b, "data-filepath": filepath(b)})
    targets = set(RENAMES.values())
    for r in rows:
        if r["branch"] in RENAMES:
            r["branch"] = RENAMES[r["branch"]]
        if r["branch"] in targets:
            r["data-filepath"] = filepath(r["branch"])
    have = {r["branch"] for r in rows}
    for b in sorted(have):
        p = b.split(".")
        for i in range(2, len(p)):
            parent = ".".join(p[:i])
            if parent not in have:
                rows.append({"branch": parent, "data-filepath": filepath(parent)})
                have.add(parent)
    # a flatten renames a child onto its parent's path: keep one row, with the
    # path derived for the target
    seen, out = set(), []
    for r in rows:
        if r["branch"] in seen:
            continue
        seen.add(r["branch"]); out.append(r)
    out.sort(key=lambda r: r["branch"].split("."))
    rows[:] = out
    return rows


def renames_only():
    """Apply RENAMES to the hierarchy as it stands (the main pass has already run)."""
    rows = list(csv.DictReader(open(HIER, encoding="utf-8-sig", newline="")))
    cols = list(rows[0].keys())
    before = {r["branch"] for r in rows}
    rows = apply_renames(rows)
    after = {r["branch"] for r in rows}
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\r\n")
    w.writeheader(); w.writerows(rows)
    HIER.write_text("\ufeff" + buf.getvalue(), encoding="utf-8")
    for b in sorted(before - after): print("-", b)
    for b in sorted(after - before): print("+", b, "|", dict((r["branch"], r["data-filepath"]) for r in rows)[b])
    print(f"rows {len(before)} -> {len(after)}")
    return 0


def main():
    rows = list(csv.DictReader(open(HIER, encoding="utf-8-sig", newline="")))
    cols = list(rows[0].keys())
    fp = {r["branch"]: r["data-filepath"] for r in rows}
    branches = [r["branch"] for r in rows]
    leaves = [b for b in branches if not any(o.startswith(b + ".") for o in branches)]
    xw = {r["branch"]: r for r in csv.DictReader(open(XW, encoding="utf-8", newline=""))}

    def in_scope(b):
        p = b.split(".")
        return p[0] == "<sector>" and len(p) > 1 and p[1] in SECTORS

    keep_out = [r for r in rows if not in_scope(r["branch"])]
    new_leaves, carry = [], {}
    for b in leaves:
        if not in_scope(b):
            continue
        x = xw.get(b)
        sug = (x or {}).get("suggested-branch", "")
        if x and x["status"] == "proposed-new":
            sug = ""
        if sug.startswith("(remove"):
            continue
        if not sug:
            new_leaves.append(b); carry[b] = fp[b]
            continue
        for s in sug.split("; "):
            s = re.sub(r"\s*\(.*\)$", "", s)
            nb = "<sector>." + s
            new_leaves.append(nb)
            # a pure rename inside shared data keeps the shared pattern
            carry.setdefault(nb, filepath(nb))
    for b, x in xw.items():
        if x["status"] == "proposed-new":
            new_leaves.append(b); carry.setdefault(b, filepath(b))
    new_leaves = list(dict.fromkeys(new_leaves))

    # parents
    allb = set(new_leaves)
    for b in new_leaves:
        p = b.split(".")
        for i in range(2, len(p)):
            allb.add(".".join(p[:i]))
    # a leaf that is also someone's prefix is a parent now (e.g. light-industrial hvac)
    out = {}
    for b in allb:
        if b in fp and b not in carry:
            out[b] = fp[b]                      # existing parent keeps its path
        elif b in carry:
            is_parent = any(o.startswith(b + ".") for o in allb)
            out[b] = fp[b] if (is_parent and b in fp) else carry[b]
        else:
            out[b] = filepath(b)
    new = apply_renames([{"branch": b, "data-filepath": p} for b, p in out.items()] + keep_out)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\r\n" if b"\r\n" in HIER.read_bytes() else "\n")
    w.writeheader(); w.writerows(new)
    HIER.write_text("﻿" + buf.getvalue(), encoding="utf-8")
    old_in = sum(1 for r in rows if in_scope(r["branch"]))
    print(f"rows {len(rows)} -> {len(new)}; in-scope {old_in} -> {len(out)}; leaves in scope {len(new_leaves)}")


if __name__ == "__main__":
    import sys
    sys.exit(renames_only() if "--renames" in sys.argv else main())
