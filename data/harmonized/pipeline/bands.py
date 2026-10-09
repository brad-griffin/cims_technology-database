"""Workbook banding of the wide views: family, then end use (modeller 2026-10-09).

Each family band is split into end-use sub-bands: the family's own end uses
first, in process-chain order (ORDER), then end uses of other sectors that some
of its archetypes also serve, then "(no connection)".
An archetype that serves several end uses is repeated under each, in the
workbook only (the CSVs stay one row per archetype); repeats are marked.

  * heat supply: the sub-bands are the heat tiers in the archetype's `heat-tier`
    column (the shared steam node carries only the first tier on the service
    record), plus any other end use it serves;
  * machine drive: kept by equipment, as before, because most drives serve many
    end uses (pumps, fans, compressed air, ...); the family band says so;
  * sub-bands with the same label (oxygen supply for steel and for smelters,
    on-site hydrogen for refineries and upgraders) are one sub-band;
  * an archetype that serves no end use goes in a closing "(no connection)" sub-band.
"""
from __future__ import annotations

from collections import defaultdict

from .common import RECORDS, read

ORDER = [
    "heat-low-temp", "heat-medium-temp", "heat-high-temp", "on-site-power-generation", "gas-pipelines",
    "space-heating", "space-cooling", "refrigeration", "lighting", "mobile-equipment",
    "co2-capture-concentrated", "co2-capture-diffuse", "direct-air-capture", "co2-transport-and-storage",
    "extraction-and-haulage", "ventilation-and-air-heating", "comminution", "separation-and-processing",
    "product-drying", "pelletizing",
    "drilling-and-well-services", "oil-and-gas-production", "in-situ-bitumen", "oil-sands-mining-and-extraction",
    "bitumen-upgrading", "upgrader-hydrogen", "water-and-tailings-management", "oil-sands-tailings",
    "produced-water-handling", "gas-processing", "lng-liquefaction", "oil-pipelines", "venting", "flaring",
    "fugitive-emissions", "synthetic-fuels",
    "crude-distillation", "conversion-and-treating", "refinery-hydrogen",
    "centralized-hydrogen-production", "hydrogen-distribution",
    "cokemaking", "agglomeration", "ironmaking", "steel-oxygen-supply", "steelmaking", "casting", "reheating",
    "rolling", "annealing-and-coating", "metal-melting-and-heat-treatment",
    "clinker-production", "cement-grinding-and-blending", "lime-calcination",
    "glass-melting", "glass-forming-and-finishing", "drying-and-low-temp-calcining", "ceramic-firing",
    "petrochemical-feedstock", "steam-cracking", "ammonia-and-methanol", "nitric-and-adipic-acid",
    "electrochemical-products", "other-chemicals",
    "ethanol-production", "biodiesel-production", "renewable-diesel-and-saf", "renewable-natural-gas",
    "wood-preparation", "chemical-pulping", "mechanical-pulping", "recycled-pulping", "chemical-recovery",
    "lime-kiln", "paper-forming", "paper-drying", "effluent-treatment",
    "alumina-refining", "anode-production", "aluminum-smelting", "pyrometallurgy", "electric-smelting",
    "hydrometallurgy", "smelter-oxygen-supply", "melting-casting-and-fabrication",
    "thermal-processing", "baking-frying-and-roasting", "drying", "drying-curing-and-forming",
    "wood-drying-and-pressing",
]
TIER = {"low-temp": "heat-low-temp", "medium-temp": "heat-medium-temp", "high-temp": "heat-high-temp"}
BY_EQUIPMENT = {"machine-drive"}
FAMILY_NOTE = {"machine-drive": "Shown by equipment, not end use: most machine-drive archetypes "
                                "serve many end uses (pumps, fans, compressed air, materials "
                                "handling and processing, compressor drive)."}
NO_CONNECTION = "(no connection)"


def expand(rows: list[dict], records) -> list[dict]:
    """Rows for a banded sheet: one per (archetype, end-use sub-band), ordered
    by family (the rows' own order), sub-band, then equipment and archetype.
    Adds `_sub` (sub-band label) and `_repeat` (True after an archetype's first row)."""
    ann = read(RECORDS / "hierarchy-annotation.csv")
    label = {r["annotation"]: r.get("label") or r["annotation"] for r in ann}
    asector = {r["annotation"]: r.get("sector", "") for r in ann}
    service_fams = {f for f, r in records.families.items() if r.get("kind") == "service"}

    def own(f, e):
        a = asector.get(e, "")
        return a == f or (f in service_fams and a == "cross-sector")
    rank = {e: i for i, e in enumerate(ORDER)}
    eus = defaultdict(list)
    for s in records.service:
        if s.get("end-use") and s["end-use"] not in eus[s["archetype"]]:
            eus[s["archetype"]].append(s["end-use"])
    fam_pos = {}
    out = []
    for i, r in enumerate(rows):
        f = r.get("family", "")
        fam_pos.setdefault(f, len(fam_pos))
        k = r.get("archetype", "")
        if f in BY_EQUIPMENT:
            subs = [("", r.get("equipment", ""))]
        else:
            ids = list(eus.get(k, []))
            if f == "heat-supply":
                tiers = [TIER[t.strip()] for t in (r.get("heat-tier") or "").split(";") if t.strip() in TIER]
                ids = tiers + [e for e in ids if e not in TIER.values()] if tiers else ids
            seen, subs = set(), []
            for e in sorted(ids, key=lambda e: (not own(f, e), rank.get(e, 999))):
                lab = label.get(e, e)
                if lab not in seen:
                    seen.add(lab)
                    subs.append((e, lab))
            subs = subs or [("~", NO_CONNECTION)]
        for j, (e, lab) in enumerate(subs):
            out.append(dict(r, _sub=lab, _repeat=j > 0,
                            _key=(fam_pos[f], (0 if own(f, e) else 1000 if e != "~" else 5000)
                                  + rank.get(e, 998), lab,
                                  r.get("equipment", ""), k)))
    # within a family, a sub-band label sits at the rank of its first end use
    first = {}
    for o in out:
        kk = (o["_key"][0], o["_sub"])
        first[kk] = min(first.get(kk, o["_key"][1]), o["_key"][1])
    out.sort(key=lambda o: (o["_key"][0], first[(o["_key"][0], o["_sub"])], o["_sub"]) + o["_key"][3:])
    # the repeat mark goes on every row after an archetype's first in sheet order
    shown = set()
    for o in out:
        o["_repeat"] = o["archetype"] in shown
        shown.add(o["archetype"])
        o.pop("_key", None)
    return out
