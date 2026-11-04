"""Which wide-view rows go in each review package (Brad 2026-11-03).

A row of the banded wide view is one archetype under one end-use sub-band. It
goes in a sector package when the archetype serves a CIMS node of that sector
through that end use (output/archetype-application.csv). Cross-cutting
archetypes (boilers, motors, lighting, capture) stay in their own families.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARM = ROOT / "database" / "harmonized"

BREWERY_EXCLUDE = ("light-industrial.service.heat.drying", "light-industrial.service.heat.metal-melting",
                   "light-industrial.service.heat.heat-treatment", "light-industrial.service.heat.forming-pressing")

# petroleum-crude holds both conventional oil and oil sands; services both use go in both
_CRUDE_SHARED = ("petroleum-crude.service.produced-water", "petroleum-crude.service.steam",
                 "petroleum-crude.service.ccs")
CONVENTIONAL_OIL = ("petroleum-crude.product.exploration", "petroleum-crude.product.completion",
                    "petroleum-crude.product.heavy", "petroleum-crude.product.light-medium",
                    "petroleum-crude.product.transmission", "petroleum-crude.service.field-engines",
                    "petroleum-crude.service.artificial-lift", "petroleum-crude.service.pumping",
                    "petroleum-crude.service.treating") + _CRUDE_SHARED
OIL_SANDS = ("petroleum-crude.product.bitumen", "petroleum-crude.service.hydrogen",
             "petroleum-crude.service.mine-haulage", "petroleum-crude.service.tailings-disposal") + _CRUDE_SHARED
# aluminum: its own product nodes, anode production, and the smelting services it uses
# (not the oxygen or acid plants, which serve copper, nickel, lead, and zinc)
ALUMINUM = ("metal-smelting.product.aluminum", "metal-smelting.service.anode-production",
            "metal-smelting.service.ccs", "metal-smelting.service.hvac", "metal-smelting.service.lighting",
            "metal-smelting.service.machine-drive", "metal-smelting.service.steam")

PACKAGES = {
    "breweries": ("Breweries", lambda n: n.startswith("light-industrial.service.")
                  and not n.startswith(BREWERY_EXCLUDE)),
    "steel": ("Iron and steel", lambda n: n.startswith("iron-and-steel.")),
    "pulp-and-paper": ("Pulp and paper", lambda n: n.startswith("pulp-and-paper.")),
    # lime added 2026-11-04 (Brad), following the cement-and-lime family
    "cement-and-lime": ("Cement and lime", lambda n: n.startswith(("industrial-minerals.product.cement",
                                                                    "industrial-minerals.product.lime"))
                        or n.startswith("industrial-minerals.service.")),
    "chemicals": ("Chemicals", lambda n: n.startswith("chemicals.")),
    # added 2026-11-04
    "conventional-oil": ("Conventional oil production", lambda n: n.startswith(CONVENTIONAL_OIL)),
    "oil-sands": ("Oil sands", lambda n: n.startswith(OIL_SANDS)),
    "natural-gas": ("Natural gas production", lambda n: n.startswith("natural-gas.")
                    and not n.startswith(("natural-gas.product.transmission", "natural-gas.product.distribution"))),
    "biofuels": ("Biofuels", lambda n: n.startswith("biofuels.")),
    "hydrogen": ("Hydrogen", lambda n: n.startswith("hydrogen.")),
    "mining": ("Mining", lambda n: n.startswith(("mining.", "coal-mining."))),
    "aluminum": ("Aluminum", lambda n: n.startswith(ALUMINUM)),
    "petroleum-refining": ("Petroleum refining", lambda n: n.startswith("petroleum-refining.")),
    "whole-database": ("Whole database", None),
}
# sub-bands left out of a package even where a shared node matches: the lime band
# reaches the cement package only through the shared kiln-heat service node
# (cement nodes only, Brad 2026-11-03; lime is an add-on noted in the package)
EXCLUDE_BANDS = {}   # lime was left out of the cement package until 2026-11-04


def _read(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def load():
    ann = defaultdict(set)
    branches = {}
    asector = {}
    for r in _read(HARM / "records" / "hierarchy-annotation.csv"):
        ann[r["label"] or r["annotation"]].add(r["annotation"])
        asector[r["annotation"]] = r["sector"]
        branches[r["annotation"]] = [b.strip() for b in r["branches"].split(";") if b.strip()]
    app = defaultdict(set)
    allnodes = defaultdict(set)
    for r in _read(HARM / "output" / "archetype-application.csv"):
        n = ".".join(r["node"].split(".")[1:])
        app[(r["archetype"], r["annotation"])].add(n)
        allnodes[r["archetype"]].add(n)
    famlabel = {r["label"]: r["family"] for r in _read(HARM / "records" / "family.csv")}
    return ann, branches, app, allnodes, asector, famlabel


def _band_annotations(label, ann):
    if label in ann:
        return ann[label]
    m = re.match(r"^(.*): [^:]+$", label or "")
    return ann.get(m.group(1), set()) if m else set()


def _matches(node, branch):
    pat = ".".join(branch.split(".")[1:])
    rx = "^" + re.escape(pat).replace(r"\*", "[^.]+") + r"(\..*)?$"
    return re.match(rx, node) is not None


def row_nodes(archetype, band_label, ctx, family_label=None):
    """The CIMS nodes this archetype serves through this sub-band."""
    ann, branches, app, allnodes, asector, famlabel = ctx
    if band_label == "(no connection)":
        return set()
    anns = _band_annotations(band_label, ann)
    if len(anns) > 1:  # one label used by two families (oxygen supply, on-site hydrogen)
        own = {a for a in anns if asector.get(a) == famlabel.get(family_label)}
        anns = own or anns
    hit = set().union(*[app[(archetype, a)] for a in anns if (archetype, a) in app]) if anns else set()
    if hit:
        return hit
    if anns:  # an end use the archetype serves on nodes recorded under another annotation
        bs = [b for a in anns for b in branches.get(a, [])]
        hit = {n for n in allnodes[archetype] if any(_matches(n, b) for b in bs)}
        if hit:
            return hit
    return set(allnodes[archetype])  # equipment bands with no end use
