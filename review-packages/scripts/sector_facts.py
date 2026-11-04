"""Facts for the sector notes: each package's archetypes and main sources, as JSON."""
import csv
import json

import openpyxl
from collections import Counter, OrderedDict

from package_map import HARM, ROOT

CROSS = {"heat-supply", "power-generation", "machine-drive", "space-conditioning", "lighting",
         "mobile-equipment", "co2-capture"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


wide = {r["archetype"]: r for r in rd(HARM / "output" / "wide-archetype.csv")}
arch = {r["archetype"]: r for r in rd(HARM / "records" / "archetype.csv")}
ex = rd(HARM / "output" / "example.csv")
src = {r["source-id"]: r for r in rd(HARM / "output" / "source-list.csv")}
out = {}
for pkg in ["breweries", "steel", "pulp-and-paper", "cement", "chemicals", "conventional-oil", "oil-sands", "natural-gas", "biofuels", "hydrogen", "mining", "aluminum", "petroleum-refining", "whole-database"]:
    rows = rd(ROOT / "review-packages" / "scripts" / f"rows_{pkg}.csv")
    bands = OrderedDict()
    # the database's own order, read from the package workbook: bands in process order, and within
    # each band conventional, efficient, capture, then alternative and prospective (Brad 2026-11-04)
    book = openpyxl.load_workbook(ROOT / "review-packages" / f"review-package_{pkg}" / f"wide-view_{pkg}.xlsx",
                                  read_only=True)
    band = None
    for (name,) in book["archetypes"].iter_rows(min_row=8, min_col=3, max_col=3, values_only=True):
        if name is None:
            continue
        if str(name).startswith("*"):
            band = str(name)[1:]
        elif name in wide and band is not None:
            bands.setdefault(band, [])
            if name not in bands[band]:
                bands[band].append(name)
    book.close()
    allarch = {r["archetype"] for r in rows}
    own = {a for a in allarch if arch[a]["family"] not in CROSS}
    table = []
    for b, al in bands.items():
        for a in al:
            if a in own:
                w = wide[a]
                g = Counter(x.strip().split(" ")[-1] for x in w["filled"].split(";") if x.strip())
                table.append(dict(band=b, archetype=a, label=w["label"], status=w["status"],
                                  n=w["n-examples"], trl=w["trl"], unit=w["product-unit"],
                                  guesses=g.get("guess", 0)))
    c = Counter(e["source-id"] for e in ex if e["archetype"] in own)
    top = [dict(short=src.get(s, {}).get("short-name", s), id=s, n=n,
                citation=src.get(s, {}).get("full-citation", "")) for s, n in c.most_common(10)]
    out[pkg] = dict(rows=len(rows), archetypes=len(allarch), own=len(own),
                    cross=len(allarch - own), table=table, top=top,
                    n_sources=len(c), n_examples=sum(c.values()),
                    cross_families=dict(Counter(arch[a]["family"] for a in allarch - own)))
tot = Counter(w["status"] for w in wide.values())
out["_totals"] = dict(archetypes=len(wide), status=dict(tot), examples=len(ex),
                      mapped=sum(1 for e in ex if e["archetype"] not in ("", "(none)")),
                      sources=len(src))
json.dump(out, open(ROOT / "review-packages" / "scripts" / "sector-facts.json", "w", encoding="utf-8"), indent=1)
print({k: (v["own"], v["cross"], v["n_sources"]) for k, v in out.items() if not k.startswith("_")}, out["_totals"])
