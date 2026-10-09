"""Workbook banding of the wide views: family, then end use (modeller 2026-10-09).

Each family band is split into end-use sub-bands in process-chain order (ORDER).
An archetype that serves several end uses is repeated under each, in the
workbook only (the CSVs stay one row per archetype), and each repeat sits in the
family whose sector owns that end use (haul trucks under mining and under oil and
gas: oil sands mining), so a sub-band gathers every archetype competing for it.
Cross-sector end uses (heat tiers, CO2 capture) stay in the archetype's own
family. Repeats are not styled differently (modeller 2026-10-09). `families()`
gives the derived families column.

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


def _context(records):
    ann = read(RECORDS / "hierarchy-annotation.csv")
    label = {r["annotation"]: r.get("label") or r["annotation"] for r in ann}
    asector = {r["annotation"]: r.get("sector", "") for r in ann}
    eus = defaultdict(list)
    for s in records.service:
        if s.get("end-use") and s["end-use"] not in eus[s["archetype"]]:
            eus[s["archetype"]].append(s["end-use"])
    return label, asector, eus


def _home_of(e, f, asector, records):
    """The family an end use's sub-band sits in: the family named by the end use's
    sector, else (cross-sector end uses, or a sector with no family) the archetype's own."""
    s = asector.get(e, "")
    return s if s in records.families and s != "cross-sector" else f


def families(records) -> dict[str, str]:
    """archetype -> its families, home family first, then the families of the sectors
    that own the other end uses it serves (modeller 2026-10-09). Derived from
    records/archetype-service.csv, so it never needs tagging by hand; `family` stays
    the single home family that the pipeline's rules use."""
    label, asector, eus = _context(records)
    out = {}
    for a in records.archetypes:
        f = a["family"]
        fs = [f] + [_home_of(e, f, asector, records) for e in eus.get(a["archetype"], [])]
        out[a["archetype"]] = "; ".join(dict.fromkeys(fs))
    return out


def expand(rows: list[dict], records) -> list[dict]:
    """One workbook row per (archetype, end-use sub-band), placed in the family whose
    sector owns the end use (modeller 2026-10-09), sorted by family (the rows' own
    order, then any family reached only through another family's archetypes),
    sub-band, then equipment and archetype. Adds `_family` (the band the row sits in)
    and `_sub` (sub-band label). All rows are shown alike (no repeat styling)."""
    label, asector, eus = _context(records)
    service_fams = {f for f, r in records.families.items() if r.get("kind") == "service"}

    def own(f, e):
        a = asector.get(e, "")
        return a == f or (f in service_fams and a == "cross-sector")
    rank = {e: i for i, e in enumerate(ORDER)}
    fam_pos = {}
    for r in rows:
        fam_pos.setdefault(r.get("family", ""), len(fam_pos))
    out = []
    for r in rows:
        f = r.get("family", "")
        k = r.get("archetype", "")
        if f in BY_EQUIPMENT:
            placed = [(f, "", r.get("equipment", ""))]
        else:
            ids = list(eus.get(k, []))
            if f == "heat-supply":
                tiers = [TIER[t.strip()] for t in (r.get("heat-tier") or "").split(";") if t.strip() in TIER]
                ids = tiers + [e for e in ids if e not in TIER.values()] if tiers else ids
            seen, placed = set(), []
            for e in ids:
                h = _home_of(e, f, asector, records)
                lab = label.get(e, e)
                if (h, lab) not in seen:
                    seen.add((h, lab))
                    placed.append((h, e, lab))
            placed = placed or [(f, "~", NO_CONNECTION)]
        for h, e, lab in placed:
            fam_pos.setdefault(h, len(fam_pos))
            out.append(dict(r, _family=h, _sub=lab,
                            _key=(fam_pos[h], (0 if (e == "" or own(h, e)) else 1000 if e != "~" else 5000)
                                  + rank.get(e, 998), lab,
                                  r.get("equipment", ""), k)))
    # within a family, a sub-band label sits at the rank of its first end use
    first = {}
    for o in out:
        kk = (o["_key"][0], o["_sub"])
        first[kk] = min(first.get(kk, o["_key"][1]), o["_key"][1])
    out.sort(key=lambda o: (o["_key"][0], first[(o["_key"][0], o["_sub"])], o["_sub"]) + o["_key"][3:])
    for o in out:
        o.pop("_key", None)
    return out
