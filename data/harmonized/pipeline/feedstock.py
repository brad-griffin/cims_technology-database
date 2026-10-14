"""Feedstock is not energy use (ruling 2026-10-13, sanity-check 2026-10-11 section
4.4): only the feedstock CONSUMED as energy, not the part whose energy ends in the
product, is in specific-energy-consumption.

records/reference/feedstock.csv names the conversion archetypes (a material
feedstock whose energy ends in the product: gas into hydrogen, ammonia or
methanol; biomass into fuels; oil into biodiesel; naphtha into HVC), the feedstock
carrier, and the energy the product holds (GJ HHV per product unit: 1 on a GJ
product). For each example on such an archetype, a total or feedstock-carrier
energy use above `inclusive-above` (default 0.9 x that energy) counts the feed:
the product's energy is taken off it, and written instead as `feedstock-
consumption` (target = the carrier) on a derived row `tp-<source>-dNNN`, so the
feed stays recorded and priced. A value below the threshold already leaves the
feed out and is kept as it is. The fill writes feedstock-consumption = the
product's energy where no example gives one (id-feedstock-in-product).
"""
from __future__ import annotations

import fnmatch
import re
from collections import defaultdict

from .common import REFERENCE, fnum, read

SEC = "specific-energy-consumption"
FEED = "feedstock-consumption"


def table():
    return read(REFERENCE / "feedstock.csv")


def row_for(archetype: str, rows=None):
    for r in rows if rows is not None else table():
        if fnmatch.fnmatchcase(archetype, r["archetype"]):
            return r
    return None


def apply(facts, records) -> dict:
    T = table()
    stats = defaultdict(int)
    nxt = defaultdict(int)
    for r in facts:
        m = re.match(r"^(tp-.+)-d(\d{3})$", r.get("record-id", ""))
        if m:
            nxt[m.group(1)] = max(nxt[m.group(1)], int(m.group(2)))
    by_ex = defaultdict(list)
    for r in facts:
        if r["parameter"] == SEC and not r.get("excluded") and r.get("archetype") and any(
                fnum(r.get(c)) is not None for c in ("value-norm", "value-min-norm", "value-max-norm")):
            by_ex[r["example-id"]].append(r)
    new = []
    for eid, rs in by_ex.items():
        t = row_for(rs[0]["archetype"], T)
        if not t:
            continue
        e = fnum(t["energy-in-product"])
        thr = fnum(t.get("inclusive-above")) or 0.9 * e
        feeds = t["feedstock"].split("|")
        hit = []
        for r in rs:
            tg = (r.get("target-norm") if r.get("target-norm") is not None else r.get("target")) or ""
            tg = tg.strip().lower()
            if tg not in ("",) + tuple(feeds):
                continue
            v = fnum(r.get("value-norm"))
            if v is None:
                # a range-only row counts the feed when its range does (2026-10-13)
                v = fnum(r.get("value-min-norm"))
            if v is None or v < thr:
                continue
            for col in ("value-norm", "value-min-norm", "value-max-norm"):
                x = fnum(r.get(col))
                if x is not None:
                    r[col] = f"{max(x - e, 0.0):.6g}"
            r["note"] = (r.get("note") or "") + (
                f"  FEEDSTOCK TAKEN OFF: the figure counts the {feeds[0]} whose energy ends in the "
                f"product ({e:g} GJ per unit, records/reference/feedstock.csv); that part is "
                "feedstock-consumption, not energy use (ruling 2026-10-13).")
            hit.append((r, tg))
            stats["energy rows net of feedstock"] += 1
        if not hit:
            continue
        r0 = next((r for r, tg in hit if tg in feeds), hit[0][0])
        tg0 = next((tg for _, tg in hit if tg in feeds), feeds[0])
        src = r0.get("source-id", "")
        nxt[f"tp-{src}"] += 1
        row = {k: "" for k in r0}
        row.update({
            "record-id": f"tp-{src}-d{nxt[f'tp-{src}']:03d}", "example-id": eid,
            "archetype": r0["archetype"], "source-technology": r0.get("source-technology", ""),
            "parameter": FEED, "target": tg0, "target-norm": tg0, "value": f"{e:.6g}",
            "unit": r0.get("unit-norm", ""), "value-norm": f"{e:.6g}", "unit-norm": r0.get("unit-norm", ""),
            "conversion-class": r0.get("conversion-class", ""), "value-type": "derived",
            "derived-from": "; ".join(r["record-id"] for r, _ in hit),
            "source-id": src, "via-source-id": r0.get("via-source-id", ""),
            "source-file": r0.get("source-file", ""), "source-locator": r0.get("source-locator", ""),
            "region": r0.get("region", ""), "year": r0.get("year", ""), "status": r0.get("status", ""),
            "note": (f"The feedstock whose energy ends in the product, taken out of the energy use of "
                     f"{', '.join(r['record-id'] for r, _ in hit)} (ruling 2026-10-13).")})
        new.append(row)
        stats["feedstock rows written"] += 1
    facts.extend(new)
    return dict(stats)
