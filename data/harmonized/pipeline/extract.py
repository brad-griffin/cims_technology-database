"""Layer 1 -> layer 2: read every extraction and return its facts, as reported.

Each source's own technology name is kept exactly as the extraction wrote it
(`source-technology`). Nothing is renamed, grouped or canonicalized here: which
archetype a source's technology is an example of is decided in one place,
records/source-example.csv, and applied by examples.py.

An EXAMPLE is one technology as one source presents it, in one of that source's
own contexts (its process or table band). Its id is

    <source-id>:<source-technology>[@<process>]

where source-id is the document the extraction was made from (UKERC for the
UKERC tables, even where a value is attributed to an original UKERC cites).

Returns facts, flows and constraints in the long schema, plus per-example
attributes (description, readiness, state of development) that sources report
as parameters but that describe the example rather than quantify it.
"""
from __future__ import annotations

import re
from collections import defaultdict

from .common import RAW, REFERENCE, currency_year, read

# UK TIMES (via Bataille) prices its "improvement technologies" and add-ons as
# the cost of adding them to an existing plant: cost-basis incremental.
UKTM_ADD_ON = re.compile(r"^(Improvement technology \d+ for existing|[^.]*\badd-on for existing)")

# --- the extractions, in load order (record ids are numbered in this order) --
TEMPLATE_FILES = [
    ("gov-usa/epa/epa_2007_biomass-chp-technologies-catalog.csv", "epa_2007_001"),
    ("gov-usa/epa/epa_2017_chp-technologies-catalog.csv", "epa_2017_001"),
    ("gov-usa/lbnl/lbnl_2021_electrification-of-boilers.csv", "lbnl_2021_001"),
    ("iea/etsap/etsap_2010_industrial-combustion-boilers.csv", "etsap_2010_001"),
]
UKERC = ("other-reports/ukerc_2013_usable-energy-database", "ukerc_2013_001")
BATAILLE = ("other-reports/bataille_2017_heavy-industry-database", "bataille_2017_001")
IPCC = ("peer-reviewed/ipcc_2022_ar6-wgiii-chapter11", "ipcc_2022_001")
IEA_GUIDE = ("iea/iea_2024_clean-tech-guide", "iea_2024_001")
ETSAP_BRIEFS = [
    ("iea/etsap/etsap_2010_iron-and-steel", "etsap_2010_002"),
    ("iea/etsap/etsap_2010_cement-production", "etsap_2010_003"),
    ("iea/etsap/etsap_2015_pulp-and-paper", "etsap_2015_001"),
    ("iea/etsap/etsap_2012_aluminium-production", "etsap_2012_001"),
    ("iea/etsap/etsap_2013_heat-pumps", "etsap_2013_002"),
]
# parameters that describe the example rather than quantify it
EXAMPLE_ATTRS = ("description", "trl", "state-of-development", "year-available")


def slug(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (x or "").lower()).strip("-")


def example_id(source_id: str, tech: str, process: str = "") -> str:
    return f"{source_id}:{tech}" + (f"@{slug(process)}" if process else "")


class Loader:
    def __init__(self):
        self.facts, self.flows, self.cons = [], [], []
        self.examples: dict[str, dict] = {}
        self.missing: list[str] = []
        self.trl_map = {(r["scale"], r["level"].strip().upper()): r["canonical-trl"]
                        for r in read(REFERENCE / "trl-scale-map.csv")}

    # -- examples ---------------------------------------------------------
    def example(self, source_id, tech, process="", node=None, extraction=""):
        eid = example_id(source_id, tech, process)
        ex = self.examples.get(eid)
        if ex is None:
            node = node or {}
            ex = self.examples[eid] = {
                "example-id": eid, "source-id": source_id, "source-technology": tech,
                "process": process, "sector-reported": node.get("sector", ""),
                "end-use-reported": node.get("end-use", ""),
                "step-reported": node.get("process-step", ""),
                "service-unit-reported": node.get("service-unit", ""),
                "extraction-file": extraction, "description": "", "trl": "",
                "trl-as-reported": "", "trl-scale": "", "state-of-development": "",
                "year-available": "", "capacity-basis": "", "capacity-unit": "",
                "note": ""}
        return ex

    def attr(self, ex, param, val, scale="trl-1-9"):
        """Record a descriptive parameter on the example. First value wins; a
        readiness level is mapped onto the common 1-9 ladder, carrying a range
        at its lower bound."""
        if param == "trl":
            if ex["trl"]:
                return
            v = (val or "").strip().upper().replace("–", "-")
            parts = [p.strip() for p in re.split(r"[-,]", v) if p.strip()]
            hits = [h for h in (self.trl_map.get((scale, p)) for p in parts) if h]
            if not hits:
                ex["note"] = (ex["note"] + " " if ex["note"] else "") + (
                    f"Readiness {val!r} on the {scale} scale is not in trl-scale-map.csv.")
                return
            ex["trl"], ex["trl-as-reported"], ex["trl-scale"] = min(hits, key=int), val, scale
        elif not ex[param]:
            ex[param] = val

    # -- facts ------------------------------------------------------------
    def fact(self, ex, **kw):
        row = {"record-id": f"tp-{len(self.facts) + 1:04d}", "example-id": ex["example-id"],
               "source-technology": ex["source-technology"]}
        row.update(kw)
        self.facts.append(row)

    # -- the source shapes ----------------------------------------------------
    def template_file(self, rel, source_id):
        """A single-file extraction in the template format: one process step,
        no node map. These four are boiler and CHP catalogues."""
        path = RAW / rel
        if not path.exists():
            self.missing.append(rel)
            return
        node = {"sector": "all-industry", "end-use": "steam-and-hot-water"}
        for row in read(path):
            tech = (row.get("technology") or "").strip()
            if not tech:
                continue
            ex = self.example(source_id, tech, row.get("process", ""), node, rel)
            param = (row.get("parameter") or "").strip()
            val = (row.get("value") or "").strip()
            if param in EXAMPLE_ATTRS:
                if val:
                    self.attr(ex, param, val)
                continue
            if not (val or row.get("formula")):
                continue
            note = (row.get("note") or "").strip()
            m = re.search(r"COST BASIS:\s*([a-z-]+)", note)
            cap = re.search(r"CAPACITY BASIS:\s*([a-z-]+)", note)
            unit = (row.get("unit") or "").strip()
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, **{"capacity-basis": cap.group(1) if cap else ""},
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "derived" if row.get("formula") else "reported",
                         "formula": (row.get("formula") or "").strip(),
                         "cost-basis": m.group(1) if m else "", "currency": currency_year(unit),
                         "source-id": source_id, "source-file": path.name,
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": rel, "via-source-id": "", "confidence": "",
                         "status": "draft", "note": note})

    def nodes(self, stem, source_id):
        path = RAW / f"{stem}_nodes.csv"
        if not path.exists():
            self.missing.append(f"{stem}_nodes.csv")
            return {}
        out = {}
        for r in read(path):
            out[(r["process"], r["technology"])] = r
            self.example(source_id, r["technology"], r["process"], r, f"{stem}.csv")
        return out

    def ukerc(self):
        stem, sid = UKERC
        nm = self.nodes(stem, sid)
        if not nm:
            return
        for row in read(RAW / f"{stem}.csv"):
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = row["parameter"], (row.get("value") or "").strip()
            if param in ("trl", "state-of-development", "year-available"):
                if val:
                    self.attr(ex, param, val)
                continue
            if not (val or row.get("formula")):
                continue
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            orig = [x for x in (row.get("source-original") or "").split(";") if x]
            cost = param.startswith(("capex", "opex"))
            # UKERC is a compilation: the value belongs to whoever it cites
            # (design rule: two-level attribution). The original is the source,
            # UKERC the via.
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="UK",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "derived" if row.get("formula") else "reported",
                         "formula": (row.get("formula") or "").strip(),
                         "cost-basis": "installed" if cost else "",
                         "capacity-basis": "product-output" if cost else "",
                         "currency": currency_year(unit),
                         "source-id": orig[0] if orig else sid,
                         "via-source-id": sid if orig else "",
                         "via-locator": (row.get("reference") or "").strip(),
                         "source-file": "ukerc_2013_usable-energy-database.xlsx",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "", "status": "draft",
                         "note": note + (f"  Cited by UKERC alongside: {', '.join(orig[1:])}."
                                         if len(orig) > 1 else "")})
        techs = {t for (_, t) in nm}
        for i, row in enumerate(read(RAW / f"{stem}_flows.csv"), 1):
            if row["technology"] not in techs:
                continue
            ex = self.example_for(sid, row["technology"], nm)
            self.flows.append({
                "record-id": f"tf-{i:04d}", "example-id": ex["example-id"],
                "source-technology": row["technology"],
                "direction": row["direction"], "commodity": row["commodity"],
                "value": row["value"], "unit": row["unit"], "per-unit": row["per-unit"],
                "value-min": row["value-min"], "value-max": row["value-max"],
                "co-product": row["co-product"], "value-type": "reported",
                "formula": row["formula"], "region": "UK",
                "source-id": (row.get("source-original") or "").split(";")[0] or sid,
                "via-source-id": sid if row.get("source-original") else "",
                "source-file": "ukerc_2013_usable-energy-database.xlsx",
                "source-locator": row["reference"], "status": "draft", "note": row["note"]})
        for i, row in enumerate(read(RAW / f"{stem}_constraints.csv"), 1):
            if row["technology"] not in techs:
                continue
            ex = self.example_for(sid, row["technology"], nm)
            self.cons.append({
                "record-id": f"tc-{i:04d}", "example-id": ex["example-id"],
                "source-technology": row["technology"],
                "constraint": row["constraint"], "region": row["region"],
                "year": row["year"], "value": row["value"], "unit": row["unit"],
                "constraint-basis": row["constraint-basis"], "value-type": "reported",
                "source-id": (row.get("source-original") or "").split(";")[0] or sid,
                "via-source-id": sid if row.get("source-original") else "",
                "source-file": "ukerc_2013_usable-energy-database.xlsx",
                "source-locator": row["reference"], "status": "draft", "note": row["note"]})

    def example_for(self, sid, tech, nm, process=""):
        """The example a flow or constraint row belongs to. Those files carry
        no process column, so a technology listed under one process only is
        that example; one listed under several is keyed on its first."""
        if process:
            return self.example(sid, tech, process)
        procs = [p for (p, t) in nm if t == tech]
        return self.example(sid, tech, procs[0] if procs else "")

    def bataille(self):
        stem, sid = BATAILLE
        nm = self.nodes(stem, sid)
        for row in read(RAW / f"{stem}.csv") if nm else []:
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = row["parameter"], (row.get("value") or "").strip()
            if param in ("trl", "state-of-development", "year-available"):
                if val:
                    self.attr(ex, param, val)
                continue
            if not val:
                continue
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            cost = param.startswith(("capex", "opex"))
            if cost:
                ex["capacity-basis"] = ex["capacity-basis"] or (
                    "nameplate" if unit.endswith("/kW") else "annual-output")
                ex["capacity-unit"] = ex["capacity-unit"] or unit.split("/")[-1]
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="UK",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "collapsed-rows" if row.get("value-min") else "",
                         "value-type": "reported", "formula": "",
                         "cost-basis": ("" if not cost else "incremental"
                                        if UKTM_ADD_ON.search(note) else "installed"),
                         "capacity-basis": "product-output" if cost else "",
                         "currency": currency_year(unit),
                         "source-id": sid, "via-source-id": "", "via-locator": "",
                         "source-file": "bataille_2017_heavy-industry-database.xlsx",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "", "status": "review" if "REVIEW:" in note else "draft",
                         "note": note})

    def ipcc(self):
        stem, sid = IPCC
        nm = self.nodes(stem, sid)
        for row in read(RAW / f"{stem}.csv") if nm else []:
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = row["parameter"], (row.get("value") or "").strip()
            # an empty readiness or state cell is kept as an unquantified row,
            # like any other IPCC cell without a number
            if param == "trl" and val:
                self.attr(ex, param, val, scale="nasa-1-9")
                continue
            if param in ("state-of-development", "year-available") and val:
                self.attr(ex, param, val)
                continue
            unit = (row.get("unit") or "").strip()
            orig = [x for x in (row.get("source-original") or "").split(";") if x]
            # a row with no number is kept: IPCC rates options whose cost cell
            # holds a condition ("Cost of H2"), and the rating is the finding
            quantified = val or row.get("value-min") or row.get("value-max")
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="global",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "reported", "formula": "", "cost-basis": "",
                         "capacity-basis": "", "currency": currency_year(unit),
                         "source-id": orig[0] if orig else sid,
                         "via-source-id": sid if orig else "",
                         "via-locator": (row.get("reference") or "").strip() if orig else "",
                         "source-file": f"{stem.split('/')[-1]}.pdf",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "medium",
                         "status": "draft" if quantified else "unquantified",
                         "note": (row.get("note") or "").strip()
                                 + (f"  Cited by IPCC alongside: {', '.join(orig[1:])}."
                                    if len(orig) > 1 else "")})

    def iea_guide(self):
        """Readiness levels only, on the IEA ETP scale (which runs to 11)."""
        stem, sid = IEA_GUIDE
        nm = self.nodes(stem, sid)
        for row in read(RAW / f"{stem}.csv") if nm else []:
            key = (row.get("process", ""), row["technology"])
            val = (row.get("value") or "").strip()
            if key not in nm or not val or row["parameter"] != "trl":
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            self.attr(ex, "trl", val, scale="iea-etp")
            note = (row.get("note") or "").strip()
            if note and not ex["description"]:
                ex["description"] = note.split(".")[0]

    def etsap_brief(self, stem, sid):
        nm = self.nodes(stem, sid)
        if not nm:
            return
        base = stem.split("/")[-1]
        for row in read(RAW / f"{stem}.csv"):
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = (row.get("parameter") or "").strip(), (row.get("value") or "").strip()
            if param in EXAMPLE_ATTRS:
                if val:
                    self.attr(ex, param, val)
                continue
            # a range with no central value is kept (EAF dust at 1-780 g/t)
            if not (val or row.get("value-min") or row.get("value-max") or row.get("formula")):
                continue
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            m = re.search(r"COST BASIS:\s*([a-z-]+)", note)
            cap = re.search(r"CAPACITY BASIS:\s*([a-z-]+)", note)
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="global",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "derived" if row.get("formula") else "reported",
                         "formula": (row.get("formula") or "").strip(),
                         "cost-basis": m.group(1) if m else "",
                         "capacity-basis": cap.group(1) if cap else
                         "product-output" if param.startswith(("capex", "opex")) else "",
                         "currency": currency_year(unit),
                         "source-id": sid, "via-source-id": "",
                         "source-file": base + ".pdf",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "", "status": "draft", "note": note})
        fpath = RAW / f"{stem}_flows.csv"
        for row in read(fpath):
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            self.flows.append({
                "record-id": f"tf-{len(self.flows) + 1:04d}", "example-id": ex["example-id"],
                "source-technology": row["technology"],
                "direction": row["direction"], "commodity": row["commodity"],
                "value": row["value"], "unit": row["unit"], "per-unit": row["per-unit"],
                "value-min": row["value-min"], "value-max": row["value-max"],
                "co-product": row["co-product"],
                "value-type": "derived" if row["formula"] else "reported",
                "formula": row["formula"], "region": "global",
                "source-id": sid, "via-source-id": "", "source-file": base + ".pdf",
                "source-locator": row["reference"], "status": "draft", "note": row["note"]})


def load() -> Loader:
    L = Loader()
    for rel, sid in TEMPLATE_FILES:
        L.template_file(rel, sid)
    L.ukerc()
    L.bataille()
    L.ipcc()
    L.iea_guide()
    for stem, sid in ETSAP_BRIEFS:
        L.etsap_brief(stem, sid)
    return L
