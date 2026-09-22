"""Populate the harmonized database from the CIMS roster and the extractions.

Run from the repo root:   python data/harmonized/populate.py

Reads:
  data/harmonized/cims-map.csv            CIMS roster, mapped (build-cims-map.py)
  data/raw-data/**/<source>.csv           extraction CSVs in the template format
  design/industrial heat technology database design.md   section 4 heat roster
Writes (overwriting the empty tables build-template.py laid down):
  process-step.csv  service-node.csv  technology.csv  tech-parameter.csv  changelog.csv

Two rules from the 2026-08-27 instructions govern the shape of technology.csv:

  * every technology is standalone. `baseline-technology` is left blank and each
    row carries absolute values - no innovation is stored as a delta against a
    baseline it points at.
  * incremental efficiency options are bucketed into the `efficiency-base` /
    `efficiency-moderate` / `efficiency-strong` variants of section 6.2, and the
    specific measures rolled into each bucket are named in that row's note.

Technologies a source names but does not quantify are written with
status=placeholder and no fact rows, so the gap is visible rather than absent.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import aggregate
from aggregate import canon_sector, canon_tech

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = ROOT / "data" / "raw-data"
DOC = ROOT / "design" / "industrial heat technology database design.md"
TODAY = "2026-08-27"
AGG_DAY = "2026-09-10"   # the aggregation pass
ADOPT_DAY = "2026-09-22" # the adoption of the design vocabulary

END_USE_UNIT = {"steam-and-hot-water": "GJ", "process-heat-low-temp": "GJ",
                "process-heat-medium-temp": "GJ", "process-heat-high-temp": "GJ",
                "drying-and-separation": "GJ", "machine-drive": "GJ",
                "refrigeration-and-cooling": "GJ", "facility-services": "GJ",
                "other-services": "GJ", "material-preparation": "t",
                "material-conversion": "t", "forming-and-finishing": "t",
                "electrochemical": "t"}

# --- extraction files, with the source they came from ----------------------
EXTRACTIONS = [
    ("gov-usa/epa/epa_2007_biomass-chp-technologies-catalog.csv", "epa_2007_001", "all-industry"),
    ("gov-usa/epa/epa_2017_chp-technologies-catalog.csv",         "epa_2017_001", "all-industry"),
    ("gov-usa/lbnl/lbnl_2021_electrification-of-boilers.csv",     "lbnl_2021_001", "all-industry"),
    ("iea/etsap/etsap_2010_industrial-combustion-boilers.csv",    "etsap_2010_001", "all-industry"),
]
# original sources a compilation cites, for the via-source-id column
VIA = {}

EFF_BUCKET_NOTE = {
 "efficiency-base": "Bucket: the incumbent unit, no efficiency measures applied. CIMS spells this "
    "Std / Low Eff / unqualified. UKERC equivalent: the baseline column of each technology table.",
 "efficiency-moderate": "Bucket: moderate efficiency improvement, up to about 15% energy saving "
    "against the incumbent. CIMS spells this Eff / Med Eff / More Eff. UKERC measures in this "
    "bucket include sinter plant improved charging, reducing air leakages and increased bed depth; "
    "hot rolling lubrication systems, increased insulation and oxygen/air-flow control; EAF "
    "advanced control systems, flue gas monitoring and eccentric bottom tapping; BOF variable "
    "speed drives on fan motors.",
 "efficiency-strong": "Bucket: strong efficiency improvement, more than about 15% energy saving "
    "against the incumbent. CIMS spells this High Eff / Most Eff. UKERC measures in this bucket "
    "include coke dry quenching; sinter cooler exhaust gas heat recovery; blast furnace hot stove "
    "heat recovery and slag heat recovery; EAF scrap preheat (Consteel and shaft furnace); hot "
    "charging; recuperative burners on hot rolling.",
}


def slug(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (x or "").lower()).strip("-")


MONEY = re.compile(r"^(\d{4}_[A-Z]{3})")


def currency_year(unit: str) -> str:
    """The currency-year a money unit is expressed in, or "" if it is not money.

    `currency` holds the currency-year and nothing else -- `2013_USD`, never
    `2013_USD/kW`. What the money is per is the denominator of `unit`, which
    already carries it; copying the whole unit into `currency` put the same
    fact in two columns and gave the deflator a value it could not read. Every
    block writes the column through here so there is one rule rather than five
    spellings of it, and check-data.py re-tests the invariant on the file.
    """
    m = MONEY.match((unit or "").strip())
    return m.group(1) if m else ""


def read_csv(p: Path) -> list[dict]:
    """Read an extraction or map file, applying the aggregation rules to the
    technology name and the sector as the row is read.

    This is deliberately the ONLY place a name is canonicalized. The names
    appear in a dozen places downstream -- roster rows, node-map keys, fact
    rows, flow rows, the `tech not in techs` guards -- and canonicalizing some
    of them would silently drop every fact whose key no longer matched its
    roster row."""
    with p.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        if r.get("technology"):
            r["technology"] = canon_tech(r["technology"])
        if r.get("sector"):
            r["sector"] = canon_sector(r["sector"])
    return rows


def write_csv(name: str, rows: list[dict]) -> None:
    """Write rows using the header build-template.py laid down, so the table
    keeps its full column set even where this script fills only some of it."""
    path = HERE / name
    with path.open(encoding="utf-8-sig", newline="") as fh:
        cols = next(csv.reader(fh))
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"  {name:22s} {len(rows):5d} rows")


# section 4 subsection heading -> the end use its roster belongs to
ROSTER_SECTION = [
    (".steam", "steam-and-hot-water"),
    ("low temperature", "process-heat-low-temp"),
    ("medium temperature", "process-heat-medium-temp"),
    ("high temperature", "process-heat-high-temp"),
]


def design_doc_roster() -> list[tuple[str, str]]:
    """(technology, end-use) from section 4, taking the end use from the
    SUBSECTION each name appears under. Section 4 is split 4.1 steam, 4.2 low,
    4.3 medium, 4.4 high; guessing the tier from the equipment instead files
    every low- and medium-temperature heater under high temperature."""
    text = DOC.read_text(encoding="utf-8")
    sec = text[text.index("## 4. Technology roster"):text.index("## 5. Naming conventions")]
    out, end_use = {}, "steam-and-hot-water"
    for line in sec.splitlines():
        if line.startswith("### "):
            low = line.lower()
            end_use = next((e for k, e in ROSTER_SECTION if k in low), end_use)
            continue
        for m in re.findall(r"`([a-z0-9-]+(?:_[a-z0-9-]+){0,2})`", line):
            if ("_" in m or m.count("-") >= 1) and m not in out:
                out[m] = end_use
    return sorted(out.items())


def trl_tables():
    """(scale, level) -> canonical 1-9, and source-id -> priority rank."""
    m = {}
    path = HERE / "trl-scale-map.csv"
    if path.exists():
        for r in read_csv(path):
            m[(r["scale"], r["level"].strip().upper())] = r["canonical-trl"]
    rank = {}
    path = HERE / "source-priority.csv"
    if path.exists():
        for r in read_csv(path):
            rank[r["source-id"]] = int(r["rank"] or 99)
    return m, rank


TRL_MAP, TRL_RANK = {}, {}


def trl_rank(sid: str) -> int:
    return TRL_RANK.get(sid, 99)


def trl_canonical(val: str, scale: str) -> tuple[str, str]:
    """Map a reported readiness level onto the common 1-9 ladder.

    Handles the three shapes sources actually print: a plain rung ("7"), a range
    ("6-7"), and a scale-specific rung ("9B"). A RANGE IS CARRIED AT ITS LOWER
    BOUND -- the conservative reading, and the one that does not overstate how
    far a technology has got. IPCC also prints "9, 3" for a row covering two
    routes; that is not a range and the lower value is taken with a note.
    """
    v = (val or "").strip().upper().replace("\u2013", "-")
    if not v:
        return "", ""
    parts = [p.strip() for p in re.split(r"[-,]", v) if p.strip()]
    hits = [TRL_MAP.get((scale, p)) for p in parts]
    hits = [h for h in hits if h]
    if not hits:
        return "", ""
    low = min(hits, key=int)
    if len(parts) > 1:
        sep = "range" if "-" in v else "two levels"
        return low, (f"Readiness reported as {val!r} ({sep}); the common ladder "
                     f"carries the lower bound, {low}.")
    return low, ("" if parts[0] == low else
                 f"Readiness {val!r} on the {scale} scale maps to {low} on the "
                 f"common ladder.")


def main() -> int:
    global TRL_MAP, TRL_RANK
    TRL_MAP, TRL_RANK = trl_tables()
    aggregate._VOCAB_PATH[0] = HERE / "vocabulary.csv"
    cims = read_csv(HERE / "cims-map.csv")
    steps, nodes, techs = {}, {}, {}

    def set_trl(t, val, scale, source, sid=""):
        """Put a readiness level on the common 1-9 ladder in `trl`.

        The common ladder is `trl-1-9`, the one defined in
        data/service-technology-map/technology-readiness-levels.md. Sources that
        name a different scale -- IPCC the NASA ladder, the IEA guide the ETP
        scale -- are mapped through trl-scale-map.csv rather than compared as
        printed. Only a source that actually names a scale is labelled with one:
        UKERC, Bataille and the brief extractions print a plain 1-9 and are
        recorded as trl-1-9, not as NASA's, which they never claim to be. The scale it came
        from and the string the source printed are kept beside it, so the
        mapping can be audited and a range is not silently turned into a point.

        Where two sources disagree the better-ranked one wins, using the same
        source-priority order the wide views use to pick a central estimate.
        Keeping whichever loaded first would make the answer depend on the order
        of the blocks in this file.
        """
        mapped, note = trl_canonical(val, scale)
        if not mapped:
            t["note"] = (t["note"] + " " if t["note"] else "") + (
                f"{source} reports readiness {val!r} on the {scale} scale, which "
                f"trl-scale-map.csv does not define; left unmapped.")
            return
        if t["trl"] and trl_rank(t.get("trl-source", "")) <= trl_rank(sid):
            if t["trl"] != mapped:
                t["note"] = (t["note"] + " " if t["note"] else "") + (
                    f"{source} rates this {val} ({scale}) = {mapped} on the common "
                    f"ladder; the higher-ranked source's {t['trl']} is kept.")
            return
        if t["trl"] and t["trl"] != mapped:
            t["note"] = (t["note"] + " " if t["note"] else "") + (
                f"Replaced readiness {t['trl']} (from {t.get('trl-scale', '')}) with "
                f"{source}'s {val}, which outranks it.")
        t["trl"], t["trl-as-reported"], t["trl-scale"] = mapped, val, scale
        # transient: which source won. Not a schema column, so it never reaches
        # technology.csv -- it exists only to let a later, better-ranked source
        # know whether it should replace this value.
        t["trl-source"] = sid
        if note:
            t["note"] = (t["note"] + " " if t["note"] else "") + note
    # (technology, service-node) -> the link row. A technology is one thing
    # wherever it is installed, so it stays single in the roster and this
    # records every node it serves. Before this existed the roster kept the
    # first node that claimed a technology and wrote the rest into a note,
    # which put Bataille's multi-sector CHP units on a mining node.
    apps = {}
    changelog = []

    def node_for(sector, end_use, step):
        if not sector:
            return ""
        sector = canon_sector(sector)
        key = "_".join(x for x in (sector, end_use, step) if x)
        if key not in nodes:
            nodes[key] = {"service-node": key, "sector": sector, "end-use": end_use,
                          "process-step": step, "branch": "",
                          "service-unit": END_USE_UNIT.get(end_use, "GJ"),
                          "service-description": "", "note": ""}
        return key

    def add_tech(name, node, **kw):
        if not name:
            return
        if node:
            nd = nodes.get(node, {})
            apps.setdefault((name, node), {
                "technology": name, "service-node": node,
                "sector": nd.get("sector", ""), "end-use": nd.get("end-use", ""),
                "process-step": nd.get("process-step", ""),
                "source-id": kw.get("source_id", ""), "note": ""})
        if name in techs:
            t = techs[name]
            KW = {"source_id": "source-id", "end_use": "end-use"}
            for k, v in kw.items():
                k = KW.get(k, k)
                if v and not t.get(k):
                    t[k] = v
            return
        equipment, carrier, variant = aggregate.split_name(name, HERE / "vocabulary.csv")
        techs[name] = {
            "technology": name,

            "equipment": equipment, "energy-carrier": carrier, "variant": variant,
            "description": "", "role": "", "relationship-to-baseline": "",
            "baseline-technology": "",      # deliberately blank: every row is standalone
            "competes-with": "", "requires": "", "state-of-development": "", "trl": "",
            "trl-as-reported": "", "trl-scale": "", "trl-source": "",
            "year-available": "", "capacity-basis": "", "capacity-unit": "",
            "heat-output-type": "", "temperature-tier": "", "retrofit-applicable": "",
            "source-id": "", "status": "draft", "note": "",
        }
        # Callers pass source_id=, but the column is source-id. Without this
        # translation every kw went nowhere and all 461 roster rows carried a
        # blank source-id -- so the roster never recorded which source first
        # introduced a technology. Fixed 2026-08-29.
        KW = {"source_id": "source-id", "end_use": "end-use"}
        techs[name].update({KW.get(k, k): v for k, v in kw.items() if v})

    # ---- 1. CIMS roster -------------------------------------------------
    KEEP = {"retain", "merge", "merge-review"}
    cims_named = 0
    for r in cims:
        if r["action"] not in KEEP or not r["sector"]:
            continue
        step = r["process-step"]
        # a process step is unique WITHIN a sector, so the registry is keyed by
        # both -- 'steam' in iron-and-steel is a different row from 'steam' in
        # chemicals, and each needs its own registration
        if step and (r["sector"], step) not in steps:
            steps[(r["sector"], step)] = {"process-step": step, "sector": r["sector"],
                           "process-step-label": r["cims-service"], "product": "",
                           "product-unit": END_USE_UNIT.get(r["end-use"], "GJ"),
                           "upstream-step": "", "description": "",
                           "note": f"from the CIMS service name {r['cims-service']!r}"}
        node = node_for(r["sector"], r["end-use"], step)
        note = f"CIMS: {r['cims-sector']} / {r['cims-service']} / {r['cims-technology']}."
        if r["variant"].startswith("efficiency-"):
            note += " " + EFF_BUCKET_NOTE[r["variant"]]
        if r["action"] == "merge-review":
            note += f" Collapsed here from the CIMS technology {r['cims-technology']!r}, " \
                    "which CIMS distinguishes as a sub-type - see cims-review.md."
        add_tech(r["technology"], node, source_id="", status="draft", note=note)
        techs[r["technology"]]["note"] = techs[r["technology"]]["note"] or note
        cims_named += 1

    # ---- 2. extractions -------------------------------------------------
    facts, n = [], 0
    for rel, source_id, sector in EXTRACTIONS:
        path = RAW / rel
        if not path.exists():
            print(f"  warning: {rel} not found, skipped")
            continue
        for row in read_csv(path):
            tech = (row.get("technology") or "").strip()
            if not tech:
                continue
            # these four are boiler and CHP catalogues: everything in them
            # raises steam or hot water, so an unlabelled row is steam, not a
            # residual service. Sending them to other-services is what filled
            # the bin these rules now retire.
            end_use = "steam-and-hot-water"
            node = node_for(sector, end_use, "")
            add_tech(tech, node, source_id=source_id, status="draft")
            t = techs[tech]
            param = (row.get("parameter") or "").strip()
            val = (row.get("value") or "").strip()
            # a few extraction parameters belong on the roster row, not the fact table
            if param == "description" and val:
                t["description"] = t["description"] or val
                continue
            if param == "trl" and val:
                set_trl(t, val, "trl-1-9", f"The {source_id} extraction", source_id)
                continue
            if param in ("state-of-development", "year-available") and val:
                t[param] = t[param] or val
                continue
            if not (val or row.get("formula")):
                continue
            n += 1
            note = (row.get("note") or "").strip()
            # a note that names a cost basis is read whatever the parameter:
            # which parameters REQUIRE one is parameter.csv's business, checked
            # in one pass below, and refusing to read a basis the extractor
            # wrote down would throw away the answer to that check
            m = re.search(r"COST BASIS:\s*([a-z-]+)", note)
            cb = m.group(1) if m else ""
            unit = (row.get("unit") or "").strip()
            cur = currency_year(unit)
            facts.append({
                "record-id": f"tp-{n:04d}", "technology": tech, "parameter": param,
                "target": (row.get("target") or "").strip(), "unit": unit,
                "value": val, "value-min": (row.get("value-min") or "").strip(),
                "value-max": (row.get("value-max") or "").strip(),
                "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                         row.get("value-max")) else "",
                "value-type": "derived" if row.get("formula") else "reported",
                "formula": (row.get("formula") or "").strip(),
                "cost-basis": cb, "currency": cur,
                "source-id": source_id, "source-file": path.name,
                "source-locator": (row.get("reference") or "").strip(),
                "extraction-file": rel,
                "via-source-id": VIA.get(source_id, ""), "confidence": "",
                # a missing required basis is marked for review by the
                # dictionary-driven pass below, not here: the rule is the same
                # for every source and belongs in one place
                "status": "draft", "note": note,
            })

    # ---- 2b. UKERC: parameters, flows and constraints --------------------
    # UKERC comes with a node map because its rows span five sectors, so the
    # sector and end use cannot be inferred from the extraction file alone.
    UK = RAW / "other-reports"
    UK_SRC = "ukerc_2013_001"
    nodemap = {}
    npath = UK / "ukerc_2013_usable-energy-database_nodes.csv"
    if npath.exists():
        for r in read_csv(npath):
            nodemap[(r["process"], r["technology"])] = r
    fl, ct = [], []
    if nodemap:
        for r in read_csv(npath):
            step = r["process-step"]
            if step and (r["sector"], step) not in steps:
                steps[(r["sector"], step)] = {
                    "process-step": step, "sector": r["sector"],
                    "process-step-label": r["process"], "product": "",
                    "product-unit": r["service-unit"], "upstream-step": "",
                    "description": "", "note": "from the UKERC 'Baseline applicable' column"}
            node = node_for(r["sector"], r["end-use"], step)
            add_tech(r["technology"], node, source_id=UK_SRC, status="draft")

        def uk_node(row):
            return nodemap.get((row.get("process", ""), row.get("technology", "")))

        for row in read_csv(UK / "ukerc_2013_usable-energy-database.csv"):
            tech, param = row["technology"], row["parameter"]
            if not uk_node(row) or tech not in techs:
                continue
            t = techs[tech]
            val = (row.get("value") or "").strip()
            if param == "trl" and val:
                # UKERC gives a maturity ladder, mapped to 1-9 in the extraction --
                # the plain ladder, not a named external scale.
                set_trl(t, val, "trl-1-9", "UKERC 2013", UK_SRC)
                continue
            if param in ("state-of-development", "year-available") and val:
                t[param] = t[param] or val
                continue
            if not (val or row.get("formula")):
                continue
            n += 1
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            derived = bool(row.get("formula"))
            orig = [x for x in (row.get("source-original") or "").split(";") if x]
            facts.append({
                "record-id": f"tp-{n:04d}", "technology": tech, "parameter": param,
                "target": (row.get("target") or "").strip(), "unit": unit, "value": val,
                "value-min": (row.get("value-min") or "").strip(),
                "value-max": (row.get("value-max") or "").strip(),
                "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                         row.get("value-max")) else "",
                "value-type": "derived" if derived else "reported",
                "formula": (row.get("formula") or "").strip(),
                "cost-basis": "installed" if param.startswith(("capex", "opex")) else "",
                "capacity-basis": "product-output" if param.startswith(("capex", "opex")) else "",
                "currency": currency_year(unit),
                "region": "UK",
                # UKERC is a compilation: the value belongs to whoever it cites
                # (design doc D7). The original is the source; UKERC is the via.
                "source-id": orig[0] if orig else UK_SRC,
                "via-source-id": UK_SRC if orig else "",
                "via-locator": (row.get("reference") or "").strip(),
                "source-file": "ukerc_2013_usable-energy-database.xlsx",
                "source-locator": (row.get("reference") or "").strip(),
                "extraction-file": "data/raw-data/other-reports/"
                                   "ukerc_2013_usable-energy-database.csv",
                "confidence": "", "status": "draft",
                "note": note + (f"  Cited by UKERC alongside: {', '.join(orig[1:])}."
                                if len(orig) > 1 else "")})

        for i, row in enumerate(read_csv(UK / "ukerc_2013_usable-energy-database_flows.csv"), 1):
            if row["technology"] not in techs:
                continue
            fl.append({"record-id": f"tf-{i:04d}", "technology": row["technology"],
                       "direction": row["direction"], "commodity": row["commodity"],
                       "value": row["value"], "unit": row["unit"], "per-unit": row["per-unit"],
                       "value-min": row["value-min"], "value-max": row["value-max"],
                       "co-product": row["co-product"], "value-type": "reported",
                       "formula": row["formula"], "region": "UK",
                       "source-id": (row.get("source-original") or "").split(";")[0] or UK_SRC,
                       "via-source-id": UK_SRC if row.get("source-original") else "",
                       "source-file": "ukerc_2013_usable-energy-database.xlsx",
                       "source-locator": row["reference"], "status": "draft",
                       "note": row["note"]})

        for i, row in enumerate(read_csv(UK / "ukerc_2013_usable-energy-database_constraints.csv"), 1):
            if row["technology"] not in techs:
                continue
            ct.append({"record-id": f"tc-{i:04d}", "technology": row["technology"],
                       "constraint": row["constraint"], "region": row["region"],
                       "year": row["year"], "value": row["value"], "unit": row["unit"],
                       "constraint-basis": row["constraint-basis"], "value-type": "reported",
                       "source-id": (row.get("source-original") or "").split(";")[0] or UK_SRC,
                       "via-source-id": UK_SRC if row.get("source-original") else "",
                       "source-file": "ukerc_2013_usable-energy-database.xlsx",
                       "source-locator": row["reference"], "status": "draft",
                       "note": row["note"]})

    # ---- 2c. Bataille 2017: the UKTM and Database sheets -----------------
    # Like UKERC this comes with a node map, because its rows span eight
    # sectors and the sector cannot be inferred from the file alone. Unlike
    # UKERC it cites nothing: the UKTM costs are UK TIMES model inputs that
    # Bataille transcribed, so Bataille is the source and there is no via.
    BAT = RAW / "other-reports"
    BAT_SRC = "bataille_2017_001"
    BAT_STEM = "bataille_2017_heavy-industry-database"
    bnodes = {}
    bpath = BAT / f"{BAT_STEM}_nodes.csv"
    if bpath.exists():
        for r in read_csv(bpath):
            bnodes[(r["process"], r["technology"])] = r
            step = r["process-step"]
            if step and (r["sector"], step) not in steps:
                steps[(r["sector"], step)] = {
                    "process-step": step, "sector": r["sector"],
                    "process-step-label": r["process"], "product": "",
                    "product-unit": r["service-unit"], "upstream-step": "",
                    "description": "",
                    "note": "from the Bataille 2017 sheet's process-step band"}
            node = node_for(r["sector"], r["end-use"], step)
            # Bataille's Database sheet gives prose where a number should be, so
            # those technologies enter the roster as placeholders (design doc D8)
            # and the UKTM ones, which carry a cost, enter as drafts.
            add_tech(r["technology"], node, source_id=BAT_SRC, status="draft")

        for row in read_csv(BAT / f"{BAT_STEM}.csv"):
            tech, param = row["technology"], row["parameter"]
            if (row.get("process", ""), tech) not in bnodes or tech not in techs:
                continue
            t = techs[tech]
            val = (row.get("value") or "").strip()
            if param == "trl" and val:
                # The UKTM sheet's "State of development" column is a plain 1-9
                # with no scale named.
                set_trl(t, val, "trl-1-9", "Bataille 2017", BAT_SRC)
                continue
            if param in ("state-of-development", "year-available") and val:
                t[param] = t[param] or val
                continue
            if not val:
                continue
            n += 1
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            cost = param.startswith(("capex", "opex"))
            if cost:
                # Per unit of annual capacity, in the capacity unit the sheet
                # names -- GJ/yr, t/yr or kW. Not an installed plant cost.
                t["capacity-basis"] = t["capacity-basis"] or (
                    "nameplate" if unit.endswith("/kW") else "annual-output")
                t["capacity-unit"] = t["capacity-unit"] or unit.split("/")[-1]
            facts.append({
                "record-id": f"tp-{n:04d}", "technology": tech, "parameter": param,
                "target": (row.get("target") or "").strip(), "unit": unit, "value": val,
                "value-min": (row.get("value-min") or "").strip(),
                "value-max": (row.get("value-max") or "").strip(),
                "uncertainty-type": "collapsed-rows" if row.get("value-min") else "",
                "value-type": "reported", "formula": "",
                "cost-basis": "installed" if cost else "",
                "capacity-basis": "product-output" if cost else "",
                "currency": currency_year(unit),
                "region": "UK",
                "source-id": BAT_SRC, "via-source-id": "", "via-locator": "",
                "source-file": f"{BAT_STEM}.xlsx",
                "source-locator": (row.get("reference") or "").strip(),
                "extraction-file": f"data/raw-data/other-reports/{BAT_STEM}.csv",
                "confidence": "", "status": "review" if "REVIEW:" in note else "draft",
                "note": note})

    # ---- 2d. IPCC AR6 WGIII Chapter 11, Table 11.3 -----------------------
    # A mitigation-option table, so what it contributes is different in kind:
    # abatement costs per tonne of CO2-eq avoided and reduction potentials, not
    # capex and efficiencies. The table's own footnotes name the primary
    # literature behind each row -- those are the originals under D7 and none is
    # held locally, so they are listed in _footnote-sources.csv for a later
    # registration pass and the chapter stands as the source until then.
    IP = RAW / "peer-reviewed"
    IP_SRC = "ipcc_2022_001"
    IP_STEM = "ipcc_2022_ar6-wgiii-chapter11"
    ipnodes = {}
    ippath = IP / f"{IP_STEM}_nodes.csv"
    if ippath.exists():
        for r in read_csv(ippath):
            ipnodes[(r["process"], r["technology"])] = r
            node = node_for(r["sector"], r["end-use"], r["process-step"])
            add_tech(r["technology"], node, source_id=IP_SRC, status="draft")

        for row in read_csv(IP / f"{IP_STEM}.csv"):
            tech, param = row["technology"], row["parameter"]
            if (row.get("process", ""), tech) not in ipnodes or tech not in techs:
                continue
            t = techs[tech]
            val = (row.get("value") or "").strip()
            if param == "trl" and val:
                set_trl(t, val, "nasa-1-9", "IPCC AR6 Chapter 11", IP_SRC)
                continue
            if param in ("state-of-development", "year-available") and val:
                t[param] = t[param] or val
                continue
            n += 1
            unit = (row.get("unit") or "").strip()
            orig = [x for x in (row.get("source-original") or "").split(";") if x]
            # A row with no number is kept, not dropped. IPCC rates plenty of
            # options whose cost cell holds a condition ("Cost of H2"); the
            # rating is the finding, and a silent drop would hide it.
            facts.append({
                "record-id": f"tp-{n:04d}", "technology": tech, "parameter": param,
                "target": (row.get("target") or "").strip(), "unit": unit, "value": val,
                "value-min": (row.get("value-min") or "").strip(),
                "value-max": (row.get("value-max") or "").strip(),
                "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                         row.get("value-max")) else "",
                "value-type": "reported", "formula": "", "cost-basis": "",
                "capacity-basis": "",
                "currency": currency_year(unit),
                "region": "global",
                # Two-level attribution (D7): where the chapter's footnote names
                # the work behind a number, that work is the source and the
                # chapter is the via.
                "source-id": orig[0] if orig else IP_SRC,
                "via-source-id": IP_SRC if orig else "",
                "via-locator": (row.get("reference") or "").strip() if orig else "",
                "source-file": f"{IP_STEM}.pdf",
                "source-locator": (row.get("reference") or "").strip(),
                "extraction-file": f"data/raw-data/peer-reviewed/{IP_STEM}.csv",
                # A ceiling ("<=USD120 t-1") has no central estimate but is
                # still a number, so quantified means any of the three, not just
                # the central value.
                "confidence": "medium",
                "status": "draft" if (val or row.get("value-min")
                                      or row.get("value-max")) else "unquantified",
                "note": (row.get("note") or "").strip()
                        + (f"  Cited by IPCC alongside: {', '.join(orig[1:])}."
                           if len(orig) > 1 else "")})

    # ---- 2e. IEA ETP Clean Energy Technology Guide, 2024 edition ---------
    # One parameter only: a readiness level, assessed annually 2020-2024. On the
    # IEA ETP scale, which runs to 11 -- not the 1-9 NASA scale IPCC uses, which
    # is why set_trl refuses to mix them.
    IG = RAW / "iea"
    IG_SRC = "iea_2024_001"
    IG_STEM = "iea_2024_clean-tech-guide"
    ignodes = {}
    igpath = IG / f"{IG_STEM}_nodes.csv"
    if igpath.exists():
        for r in read_csv(igpath):
            ignodes[(r["process"], r["technology"])] = r
            node = node_for(r["sector"], r["end-use"], r["process-step"])
            add_tech(r["technology"], node, source_id=IG_SRC, status="draft")
        for row in read_csv(IG / f"{IG_STEM}.csv"):
            tech, val = row["technology"], (row.get("value") or "").strip()
            if (row.get("process", ""), tech) not in ignodes or tech not in techs or not val:
                continue
            if row["parameter"] == "trl":
                set_trl(techs[tech], val, "iea-etp",
                        "The IEA ETP Clean Energy Technology Guide", IG_SRC)
                note = (row.get("note") or "").strip()
                t = techs[tech]
                if note and not t["description"]:
                    t["description"] = note.split(".")[0]

    # ---- 2f. ETSAP sector technology briefs ------------------------------
    # The industry briefs (I02, I03, I07, I10) are unlike I01: their rows span
    # several process steps within one sector and they carry per-tonne material
    # and energy flows as well as parameters, so each comes with a node map and
    # an optional flows file, the same three-file shape UKERC and Bataille use.
    # I01 stays in EXTRACTIONS above -- it is one process step and has no flows.
    ETSAP_BRIEFS = [
        ("iea/etsap/etsap_2010_iron-and-steel", "etsap_2010_002"),
        ("iea/etsap/etsap_2010_cement-production", "etsap_2010_003"),
        ("iea/etsap/etsap_2015_pulp-and-paper", "etsap_2015_001"),
        ("iea/etsap/etsap_2012_aluminium-production", "etsap_2012_001"),
        ("iea/etsap/etsap_2013_heat-pumps", "etsap_2013_002"),
    ]
    for stem, es_src in ETSAP_BRIEFS:
        base = RAW / stem
        npath = base.with_name(base.name + "_nodes.csv")
        if not npath.exists():
            print(f"  warning: {stem}_nodes.csv not found, skipped")
            continue
        esnodes = {}
        for r in read_csv(npath):
            esnodes[(r["process"], r["technology"])] = r
            step = r["process-step"]
            if step and (r["sector"], step) not in steps:
                steps[(r["sector"], step)] = {
                    "process-step": step, "sector": r["sector"],
                    "process-step-label": r["process"], "product": "",
                    "product-unit": r["service-unit"], "upstream-step": "",
                    "description": "", "note": f"from the {es_src} extraction"}
            add_tech(r["technology"], node_for(r["sector"], r["end-use"], step),
                     source_id=es_src, status="draft")

        for row in read_csv(base.with_suffix(".csv")):
            tech, param = row["technology"], (row.get("parameter") or "").strip()
            if (row.get("process", ""), tech) not in esnodes or tech not in techs:
                continue
            t = techs[tech]
            val = (row.get("value") or "").strip()
            if param == "description" and val:
                t["description"] = t["description"] or val
                continue
            if param == "trl" and val:
                set_trl(t, val, "trl-1-9", f"The {es_src} extraction", es_src)
                continue
            if param in ("state-of-development", "year-available") and val:
                t[param] = t[param] or val
                continue
            # A range with no central value is kept. ETSAP prints several of
            # these (EAF dust at 1-780 g/t); dropping them would lose the only
            # figure the brief gives for that pollutant.
            if not (val or row.get("value-min") or row.get("value-max")
                    or row.get("formula")):
                continue
            n += 1
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            m = re.search(r"COST BASIS:\s*([a-z-]+)", note)
            cb = m.group(1) if m else ""
            facts.append({
                "record-id": f"tp-{n:04d}", "technology": tech, "parameter": param,
                "target": (row.get("target") or "").strip(), "unit": unit, "value": val,
                "value-min": (row.get("value-min") or "").strip(),
                "value-max": (row.get("value-max") or "").strip(),
                "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                         row.get("value-max")) else "",
                "value-type": "derived" if row.get("formula") else "reported",
                "formula": (row.get("formula") or "").strip(),
                "cost-basis": cb,
                "capacity-basis": "product-output" if param.startswith(("capex", "opex")) else "",
                "currency": currency_year(unit),
                "region": "global",
                "source-id": es_src, "via-source-id": "",
                "source-file": base.name + ".pdf",
                "source-locator": (row.get("reference") or "").strip(),
                "extraction-file": f"data/raw-data/{stem}.csv",
                "confidence": "", "status": "draft", "note": note})

        fpath = base.with_name(base.name + "_flows.csv")
        if fpath.exists():
            for row in read_csv(fpath):
                if (row.get("process", ""), row["technology"]) not in esnodes \
                        or row["technology"] not in techs:
                    continue
                fl.append({"record-id": f"tf-{len(fl) + 1:04d}",
                           "technology": row["technology"], "direction": row["direction"],
                           "commodity": row["commodity"], "value": row["value"],
                           "unit": row["unit"], "per-unit": row["per-unit"],
                           "value-min": row["value-min"], "value-max": row["value-max"],
                           "co-product": row["co-product"],
                           "value-type": "derived" if row["formula"] else "reported",
                           "formula": row["formula"], "region": "global",
                           "source-id": es_src, "via-source-id": "",
                           "source-file": base.name + ".pdf",
                           "source-locator": row["reference"], "status": "draft",
                           "note": row["note"]})

    # ---- 3. placeholders from the design document heat roster -----------
    placeholders = 0
    for name, end_use in design_doc_roster():
        # the roster is parsed out of the design document, not read through
        # read_csv, so it is the one name source the canonicalizer has to be
        # applied to by hand. The tier is read off the ORIGINAL name below,
        # before the suffix is dropped.
        raw, name = name, canon_tech(name)
        # the variant carries the tier where the name has one, and it beats the
        # subsection: boiler_electricity_tes is listed under steam, while
        # direct-heater_hydrogen_low-temp names its own tier
        for tier, eu in (("low-temp", "process-heat-low-temp"),
                         ("medium-temp", "process-heat-medium-temp"),
                         ("high-temp", "process-heat-high-temp")):
            if raw.endswith("_" + tier):
                end_use = eu
                break
        node = node_for(aggregate.CROSS_SECTOR, end_use, "")
        if name in techs:
            # the tier suffix is gone from the name (R4) but the tier itself is
            # not: direct-heater_natural-gas_medium-temp aggregates into
            # direct-heater_natural-gas, and the medium-temperature service it
            # was listed for has to survive as an application or the roster
            # quietly stops offering a gas heater at that tier
            add_tech(name, node)
            continue
        add_tech(name, node, status="placeholder",
                 note="PLACEHOLDER. Named in section 4 of the design document as in scope, but no "
                      "local source has been extracted for it yet. Section 7 lists several of these "
                      "under 'Known parameter gaps (no local source)'. Do not fill with a proxy "
                      "without saying so in the source note.")
        placeholders += 1

    changelog.append({"date": TODAY, "who": "claude", "table": "technology", "record-id": "",
                      "change": f"populated {len(techs)} technologies: {cims_named} CIMS roster "
                                f"entries, {len(EXTRACTIONS)} extractions, {placeholders} placeholders",
                      "reason": "first population of the harmonized layer", "note": ""})
    # ---- evaluate arithmetic-only formulas -------------------------------
    # Some extractions record a derivation as a formula with no computed value
    # (ETSAP I01's boiler capacity is "4695 * 2740 / 3600 / 1000"). The wide
    # view needs the number to put costs on a per-capacity basis, so plain
    # arithmetic is evaluated here. Anything referring to another parameter is
    # left alone -- that is the marimo template's job, not this script's.
    import ast as _ast

    def arith(expr):
        try:
            tree = _ast.parse(expr, mode="eval")
        except SyntaxError:
            return None
        ok = (_ast.Expression, _ast.BinOp, _ast.UnaryOp, _ast.Constant, _ast.Add,
              _ast.Sub, _ast.Mult, _ast.Div, _ast.Pow, _ast.USub, _ast.UAdd)
        for n in _ast.walk(tree):
            if not isinstance(n, ok):
                return None
        try:
            return eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, {})
        except Exception:
            return None

    evaluated = 0
    for r in facts:
        if r.get("value") or not r.get("formula"):
            continue
        v = arith(r["formula"])
        if v is not None:
            r["value"] = f"{v:.6g}"
            evaluated += 1

    # ---- normalize 'fraction' to '%' across the whole layer ---------------
    # A repo-wide unit convention, not a change of value: 0.87 fraction and 87%
    # are the same number written two ways, and having both in one column is
    # how a reader mistakes one for the other.
    # one spelling per unit. The species already lives in `target`, so an
    # emissions unit only has to carry mass -- 'kgeCO2/unit' and 'kgCO2/unit'
    # are the same quantity spelled two ways by different UKERC tables.
    CANON = {"C": "degC", "c": "degC", "degrees C": "degC",
             "kgeCO2/unit": "kg/unit", "kgCO2/unit": "kg/unit",
             "tCO2/unit": "t/unit", "yrs": "years", "yr": "years"}
    for r in facts:
        if r.get("unit") in CANON:
            r["unit"] = CANON[r["unit"]]

    FRAC = {"fraction": "%", "fraction/yr": "%/yr"}
    scaled = 0
    for r in facts:
        if r.get("unit") in FRAC:
            for k in ("value", "value-min", "value-max"):
                v = (r.get(k) or "").strip()
                if not v:
                    continue
                try:
                    r[k] = f"{float(v) * 100:.6g}"
                except ValueError:
                    continue
            if r.get("formula"):
                r["formula"] = f"({r['formula']}) * 100"
            r["unit"] = FRAC[r["unit"]]
            scaled += 1

    # link each derived capex row to the as-reported row it was computed from;
    # value-type 'derived' is not meaningful without a walkable chain
    asrep = {}
    for r in facts:
        if r["parameter"] == "capex" and not r["formula"]:
            asrep.setdefault((r["technology"], r.get("region", "")), r["record-id"])
    linked = 0
    for r in facts:
        if r["parameter"] == "capex" and r["formula"] and not r.get("derived-from"):
            src = asrep.get((r["technology"], r.get("region", "")))
            if src:
                r["derived-from"] = src
                linked += 1

    changelog.append({"date": TODAY, "who": "claude", "table": "tech-parameter",
                      "record-id": "",
                      "change": f"evaluated {evaluated} arithmetic-only formulas into values; "
                                f"normalized {scaled} rows from fraction to %",
                      "reason": "the wide view needs a number to put costs on a per-capacity "
                                "basis, and one unit convention per quantity",
                      "note": "formulas referring to other parameters are left for the "
                              "marimo template to resolve"})
    changelog.append({"date": TODAY, "who": "claude", "table": "tech-flow", "record-id": "",
                      "change": f"{len(fl)} flow rows and {len(ct)} constraint rows from UKERC 2013",
                      "reason": "UKERC extraction completed 2026-08-27; 84 distinct technologies "
                                "plus 167 efficiency measures bucketed into 78 buckets",
                      "note": "per-measure figures kept in "
                              "ukerc_2013_usable-energy-database_rows.csv"})
    changelog.append({"date": TODAY, "who": "claude", "table": "tech-parameter", "record-id": "",
                      "change": f"{len(facts)} fact rows from ETSAP I01, EPA 2007, EPA 2017 and LBNL 2021",
                      "reason": "extractions completed 2026-08-27", "note": ""})

    # ---- aggregation post-pass -------------------------------------------
    # Rules R1-R3 need the whole database loaded: R3 resolves an unclassified
    # application against the end uses the same equipment has elsewhere.
    review, unresolved = aggregate.rewrite(steps, nodes, techs, apps, facts, fl, ct)
    for t in techs.values():
        t["aggregated-from"] = "; ".join(sorted(aggregate.AGGREGATED.get(t["technology"], ())))
    (HERE / "aggregation-review.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    agg = sum(1 for t in techs.values() if t["aggregated-from"])
    print(f"aggregation: {agg} technologies carry a name that aggregates others; "
          f"{len(unresolved)} applications left unresolved")
    changelog.append({"date": AGG_DAY, "who": "claude", "table": "technology", "record-id": "",
                      "change": f"aggregation rules R1-R4 applied: {len(techs)} technologies, "
                                f"{len(apps)} applications, {len(nodes)} service nodes",
                      "reason": "roster had reached 506 technologies and 1,365 applications; "
                                "user asked for a general roster of about 500 or fewer, generic "
                                "end uses held once cross-sector, and other-services retired",
                      "note": "rules documented at the top of aggregate.py; every reassignment "
                              "listed in aggregation-review.md"})

    # ---- adoption: the design vocabulary, down to the hierarchy leaf ------
    # Everything above builds the roster the sources grew. adopt.py writes that
    # to source-roster/, runs the design crosswalk on it, and replaces the
    # roster, the service nodes and the process steps with the design tables
    # and the CIMS hierarchy leaves; every fact moves onto its design
    # technology and keeps its source name in roster-technology.
    import adopt
    sids = {r["term"] for r in read_csv(HERE / "vocabulary.csv") if r["list-name"] == "source-id"}
    ad = adopt.adopt(steps, nodes, techs, apps, facts, fl, ct, sids)
    print(f"adoption: {ad['folded']} source roster names onto {ad['technologies']} design "
          f"technologies ({ad['with-facts']} with facts, {ad['placeholders']} placeholders); "
          f"{ad['nodes']} service nodes on hierarchy leaves; {ad['applications']} applications "
          f"({ad['design-only']} from design placements alone)")
    changelog.append({"date": ADOPT_DAY, "who": "claude", "table": "technology", "record-id": "",
                      "change": f"design vocabulary adopted: {ad['technologies']} design "
                                f"technologies, {ad['nodes']} service nodes, "
                                f"{ad['applications']} applications",
                      "reason": "the design tables are the vocabulary and the CIMS hierarchy sets "
                                "the level of detail (the user, 2026-09-14 and 2026-09-22)",
                      "note": "adopt.py; the pre-adoption roster is in source-roster/, the "
                              "crosswalk and its review beside this file"})

    # ---- basis requirement, read from the parameter dictionary -----------
    # parameter.csv names, per parameter, the basis a number is meaningless
    # without: a capex with no cost-basis could be an equipment cost or an
    # installed one, and those differ by about a factor of two. The requirement
    # is read from the dictionary rather than spelled out here, so adding a
    # parameter is a row in parameter.csv and not an edit to five blocks of
    # this file. A row missing its declared basis is marked for review -- not
    # dropped, and not guessed. This does NOT fail the run: the extractions
    # that predate the basis rules have a backfill pass of their own.
    # check-data.py applies the same rule as a commit gate.
    basis_req = {r["parameter"]: (r.get("basis-required") or "").strip()
                 for r in read_csv(HERE / "parameter.csv")
                 if (r.get("basis-required") or "").strip()}
    BASIS_NOTE = ("  BASIS NOT RECORDED: parameter.csv requires a {col} for {param} "
                  "and this extraction does not give one. Marked for review rather "
                  "than guessed.")
    no_basis = 0
    for r in facts:
        col = basis_req.get(r["parameter"], "")
        # a basis says what a number is per; with no number there is nothing
        # for it to qualify, so an unquantified row is not held against it
        if not col or not (r.get("value") or r.get("value-min") or r.get("value-max")):
            continue
        if (r.get(col) or "").strip():
            continue
        no_basis += 1
        if r.get("status") == "draft":
            r["status"] = "review"
        if "BASIS NOT RECORDED" not in (r.get("note") or ""):
            r["note"] = (r.get("note") or "") + BASIS_NOTE.format(col=col,
                                                                  param=r["parameter"])
    print(f"basis: {no_basis} quantified rows are missing the basis parameter.csv "
          f"requires, marked for review")
    changelog.append({"date": TODAY, "who": "claude", "table": "tech-parameter",
                      "record-id": "",
                      "change": f"{no_basis} rows marked for review for a missing required basis",
                      "reason": "parameter.csv declares which parameters need a cost-basis or a "
                               "capacity-basis; the check now reads that column instead of "
                               "hard-coding capex",
                      "note": "check-data.py exits non-zero on the same condition"})

    # ---- currency is a currency-year, and only that ----------------------
    # Every block writes it through currency_year(), so a mismatch here means
    # a later pass rewrote a unit without its currency. That is a bug in this
    # file rather than in the data, so it stops the run.
    bad_cur = [f"{r['record-id']}: unit {r.get('unit','')!r}, currency "
               f"{r.get('currency','')!r}" for r in facts
               if (r.get("currency") or "") != currency_year(r.get("unit", ""))]
    if bad_cur:
        print(f"  ERROR: {len(bad_cur)} rows where currency is not the currency-year "
              f"of unit:", file=sys.stderr)
        for x in bad_cur[:10]:
            print(f"      {x}", file=sys.stderr)
        return 1

    # ---- record ids, stable within a source ------------------------------
    def renumber(rows: list[dict], prefix: str) -> dict:
        """Number each source's rows within its own block and return old -> new.

        A single run-wide counter made tp-0421 mean "the 421st row this run
        happened to produce", so adding one line to an early extraction
        renumbered every row below it -- and every reference to them -- for a
        reason that had nothing to do with those rows. Numbering within the
        source keeps an edit's blast radius inside the source it edits:
        tp-ukerc_2013_001-0042 is the 42nd row taken from UKERC. The ids are
        still assigned by position within the block, so they are stable against
        unrelated edits, not against a reordering of the same source.
        """
        seq, remap = defaultdict(int), {}
        for r in rows:
            sid = (r.get("source-id") or "").strip() or "unattributed"
            seq[sid] += 1
            new = f"{prefix}-{sid}-{seq[sid]:04d}"
            remap[r["record-id"]] = new
            r["record-id"] = new
        return remap

    remap = renumber(facts, "tp")
    renumber(fl, "tf")
    renumber(ct, "tc")
    # derived-from is the only column that points at a record-id, and it points
    # within tech-parameter. Rewriting it through the same map in the same pass
    # is what keeps the derivation chain walkable across the renumbering. The
    # column is declared as a semicolon-separated LIST, so it is split even
    # though nothing writes more than one today.
    dangling, remapped = [], 0
    for r in facts:
        refs = [x.strip() for x in (r.get("derived-from") or "").split(";") if x.strip()]
        if not refs:
            continue
        out = []
        for ref in refs:
            if ref in remap:
                out.append(remap[ref])
                remapped += 1
            else:
                dangling.append(f"{r['record-id']} -> {ref}")
        r["derived-from"] = "; ".join(out)
    if dangling:
        print(f"  ERROR: {len(dangling)} derived-from references do not resolve "
              f"after renumbering:", file=sys.stderr)
        for x in dangling[:10]:
            print(f"      {x}", file=sys.stderr)
        return 1
    ids = [r["record-id"] for r in facts]
    assert len(ids) == len(set(ids)), "record-id is not unique after renumbering"
    print(f"record ids: {len(set(i.rsplit('-', 1)[0] for i in ids))} per-source blocks "
          f"across {len(ids)} parameter rows; {remapped} derived-from links remapped")
    changelog.append({"date": TODAY, "who": "claude", "table": "tech-parameter",
                      "record-id": "",
                      "change": "record-ids renumbered per source as "
                                "tp-<source-id>-NNNN (likewise tf- and tc-)",
                      "reason": "a run-wide counter renumbered unrelated rows whenever an "
                                "early extraction changed, so no id could be cited",
                      "note": f"{remapped} derived-from references rewritten through the "
                              "same map; the run fails if one does not resolve"})

    print(f"evaluated {evaluated} arithmetic-only formulas into values")
    print(f"normalized {scaled} rows from fraction to %")
    print("populated:")
    write_csv("process-step.csv", sorted(steps.values(), key=lambda r: (r["sector"], r["process-step"])))
    write_csv("service-node.csv", sorted(nodes.values(), key=lambda r: r["service-node"]))
    write_csv("technology.csv", sorted(techs.values(), key=lambda r: r["technology"]))
    write_csv("technology-application.csv",
              sorted(apps.values(), key=lambda r: (r["technology"], r["service-node"])))
    write_csv("tech-parameter.csv", facts)
    write_csv("tech-flow.csv", fl)
    write_csv("tech-constraint.csv", ct)
    write_csv("changelog.csv", changelog)
    ph = sum(1 for t in techs.values() if t["status"] == "placeholder")
    print(f"\n  {len(techs)} technologies ({ph} placeholders), {len(nodes)} service nodes, "
          f"{len(steps)} process steps, {len(facts)} facts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
