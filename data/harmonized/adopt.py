"""Adopt the design vocabulary: rewrite the source roster onto the design tables,
down to the leaves of the CIMS hierarchy.

Called by populate.py after the aggregation post-pass, on the rows it holds in
memory; it does not run on its own. What it does, in order:

  1. writes the roster as the sources grew it to source-roster/ -- the record of
     what was adopted, and what build-design-crosswalk.py reads standalone;
  2. runs the crosswalk (build-design-crosswalk.py) on those same rows;
  3. replaces the roster with the design technology table: one row per design
     technology, named equipment_discriminator (design doc section 5), with
     every source roster name it absorbs in aggregated-from;
  4. replaces the service nodes with one node per (design end use, hierarchy
     leaf), and the process steps with the leaves themselves;
  5. rewrites every application onto those nodes, and every fact onto the
     design technology, keeping the source's own name in roster-technology.

The decisions behind it are the user's (2026-09-14 and 2026-09-22): the design
tables are the vocabulary, the design row is the roster row, carriers collapse
into a list on the row, the CIMS hierarchy sets the level of detail below the
end use, and a roster name the design table does not cover folds onto the
nearest design technology rather than being dropped.
"""
from __future__ import annotations

import collections
import csv
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ROSTER = HERE / "source-roster"
SECTOR_PREFIX = "<sector>."

# the design table's `type` column, onto the roster's `role` vocabulary
ROLE = {"conventional": "incumbent", "alternative": "alternative-route",
        "efficient variant": "improvement", "prospective": "new"}
# roster fields taken from the folded source rows, first non-empty wins
FROM_ROSTER = ("state-of-development", "year-available", "capacity-basis",
               "capacity-unit", "heat-output-type", "temperature-tier",
               "retrofit-applicable", "relationship-to-baseline")


def _crosswalk():
    spec = importlib.util.spec_from_file_location(
        "build_design_crosswalk", HERE / "build-design-crosswalk.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _header(name: str) -> list[str]:
    with (HERE / name).open(encoding="utf-8-sig", newline="") as fh:
        return next(csv.reader(fh))


def snapshot(steps: dict, nodes: dict, techs: dict, apps: dict) -> None:
    """The pre-adoption roster, in the harmonized schema, under source-roster/."""
    ROSTER.mkdir(exist_ok=True)
    for name, rows in (("process-step.csv", steps.values()),
                       ("service-node.csv", nodes.values()),
                       ("technology.csv", techs.values()),
                       ("technology-application.csv", apps.values())):
        cols = _header(name)
        rows = sorted(rows, key=lambda r: tuple(r.get(c, "") for c in cols[:3]))
        with (ROSTER / name).open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            for r in rows:
                w.writerow({c: r.get(c, "") for c in cols})


def _join(values) -> str:
    out = []
    for v in values:
        for x in (v or "").split(";"):
            x = x.strip()
            if x and x not in out:
                out.append(x)
    return "; ".join(out)


def _leaf(branch: str) -> str:
    return branch[len(SECTOR_PREFIX):] if branch.startswith(SECTOR_PREFIX) else branch


def _node_id(sector: str, end_use: str, branch: str) -> str:
    """sector_end-use_process-step (design doc section 5), where the process
    step is the hierarchy leaf, dotted as the hierarchy writes it."""
    return f"{sector}_{end_use}_{_leaf(branch)}"


def _step_label(branch: str) -> str:
    parts = _leaf(branch).split(".")
    rest = [p for p in parts[1:] if p not in ("product", "service")]
    return f"{parts[0]}: " + " / ".join(rest) if rest else parts[0]


def _trl_low(text: str) -> str:
    m = re.match(r"\s*(\d)", text or "")
    return m.group(1) if m else ""


def adopt(steps: dict, nodes: dict, techs: dict, apps: dict,
          facts: list, flows: list, constraints: list, source_ids: set) -> dict:
    """Rewrite the roster in place. Returns a summary for the changelog."""
    snapshot(steps, nodes, techs, apps)
    cw = _crosswalk().main(list(techs.values()), list(apps.values()),
                           {"parameter": facts, "flow": flows, "constraint": constraints})
    names, label_rows = cw["names"], cw["label_rows"]
    seu = {(r["sector"], r["end-use"]): r for r in cw["seu"]}
    leaves = cw["leaves"]
    carriers_vocab = set(cw["vocab"].get("energy-carrier", ())) | set(cw["vocab"].get("carrier", ()))

    to_design = {r["roster-technology"]: r["design-technology"] for r in cw["tech_rows"]}
    fold_note = {r["roster-technology"]: r["note"] for r in cw["tech_rows"] if r["note"]}
    missing = sorted(set(techs) - set(to_design))
    assert not missing, f"roster technologies the crosswalk did not map: {missing[:10]}"

    # ---- facts: onto the design technology, the source name kept -----------
    nfacts = collections.Counter()
    for rows in (facts, flows, constraints):
        for r in rows:
            src = r["technology"]
            assert src in to_design, f"fact on a technology not in the roster: {src}"
            r["roster-technology"] = src
            r["technology"] = to_design[src]
            nfacts[r["technology"]] += 1

    # ---- service nodes and process steps: one per (end use, leaf) ----------
    new_nodes, new_steps = {}, {}
    for (s, eu), ls in leaves.items():
        d = seu[(s, eu)]
        for lf in ls:
            nid = _node_id(s, eu, lf["branch"])
            step = _leaf(lf["branch"])
            new_nodes[nid] = {
                "service-node": nid, "sector": s, "end-use": eu, "process-step": step,
                "branch": lf["branch"], "service-unit": d["service-unit"],
                "service-description": f"{d['end-use-label']}, at {step}",
                "note": ("This leaf is shared with other end uses (part); "
                         if lf["share"] == "part" else "")
                        + f"hierarchy role {lf['role']}; data folder {lf['data-filepath']}"}
            new_steps.setdefault((s, step), {
                "process-step": step, "sector": s, "process-step-label": _step_label(lf["branch"]),
                "product": "", "product-unit": d["service-unit"], "upstream-step": "",
                "description": "", "note": f"CIMS hierarchy leaf {lf['branch']}"})

    # ---- the roster: one row per design technology -------------------------
    folded = collections.defaultdict(list)
    for src, dt in to_design.items():
        folded[dt].append(src)
    new_techs = {}
    for lab, d in names.items():
        dt = d["name"]
        rows = label_rows[lab]
        first = rows[0]
        srcs = sorted(folded.get(dt, []), key=lambda t: -cw["factcount"][t])
        src_rows = [techs[t] for t in srcs]
        carriers = _join([techs[t].get("energy-carrier", "") for t in srcs]
                         + [c.replace(" ", "-") for c in d["carriers"]
                            if c.replace(" ", "-") in carriers_vocab])
        design_srcs = [x for r in rows for x in re.split(r"[;,\s]+", r["sources"] + " " + r["trl-basis"])
                       if x in source_ids]
        notes = [first["note"]] if first["note"] else []
        trls = sorted({techs[t].get("trl", "") for t in srcs} - {""})
        if trls and trls != [_trl_low(first["trl"])]:
            notes.append(f"Sources report TRL {', '.join(trls)} for the roster names folded in; "
                         f"the design table's {first['trl']} is kept.")
        if first["trl-basis"]:
            notes.append(f"TRL basis: {first['trl-basis']}.")
        notes += [f"{t}: {fold_note[t]}" for t in srcs if t in fold_note]
        conflicts = [f for f in ("capacity-basis", "capacity-unit")
                     if len({r.get(f, "") for r in src_rows} - {""}) > 1]
        if conflicts:
            notes.append("The folded roster names disagree on " + " and ".join(conflicts)
                         + "; the first is shown, and each fact row keeps its own basis.")
        row = {
            "technology": dt, "technology-label": lab, "equipment": d["equipment"],
            "energy-carrier": carriers, "variant": d["discriminator"],
            "description": first["description"],
            "role": ROLE.get(first["type"].split(";")[0].strip(), ""),
            "baseline-technology": "", "competes-with": "", "requires": "",
            "trl": _trl_low(first["trl"]), "trl-as-reported": first["trl"],
            "trl-scale": "trl-1-9" if _trl_low(first["trl"]) else "",
            "source-id": _join([techs[t].get("source-id", "") for t in srcs] + design_srcs),
            "aggregated-from": _join(srcs + [techs[t].get("aggregated-from", "") for t in srcs]),
            "status": ("draft" if nfacts[dt] else
                       "unquantified" if srcs else "placeholder"),
            "note": " ".join(notes),
        }
        for f in FROM_ROSTER:
            row[f] = next((r.get(f, "") for r in src_rows if r.get(f, "")), "")
        new_techs[dt] = row

    # ---- applications: the leaf rows the data reached, then the design's ----
    new_apps = {}

    def add(dt, s, eu, branch, source, sectors, steps_, note):
        nid = _node_id(s, eu, branch)
        key = (dt, nid)
        if key in new_apps:
            a = new_apps[key]
            a["source-id"] = _join([a["source-id"], source])
            a["reported-sectors"] = _join([a["reported-sectors"], sectors])
            a["reported-steps"] = _join([a["reported-steps"], steps_])
            return
        n = new_nodes[nid]
        new_apps[key] = {"technology": dt, "service-node": nid, "sector": s, "end-use": eu,
                         "process-step": n["process-step"], "source-id": _join([source]),
                         "reported-sectors": _join([sectors]), "reported-steps": _join([steps_]),
                         "note": note}

    # the crosswalk also reads cims-map.csv, whose names predate the R4 merges in
    # aggregate.py, so a CIMS name can be one the roster has since folded into a
    # more general one: follow aggregated-from back to the roster row
    alias = {}
    for name, t in techs.items():
        for a in (x.strip() for x in (t.get("aggregated-from") or "").split(";")):
            if a:
                alias.setdefault(a, name)
    unplaced = collections.Counter()
    reached = set()
    for r in cw["br_rows"]:
        src = r["technology"] if r["technology"] in to_design else alias.get(r["technology"])
        if src is None:
            unplaced[r["technology"]] += 1
            continue
        dt = to_design[src]
        s, eu = r["design-sector"], r["design-end-use"]
        reached.add((dt, s, eu))
        add(dt, s, eu, r["branch"], r["source-id"], r["from-sector"], r["from-process-step"],
            f"leaf chosen by: {r['how']}")
    design_only = 0
    for lab, d in names.items():
        for row in label_rows[lab]:
            k = (row["sector"], row["end-use"])
            if (d["name"], *k) in reached:
                continue
            for lf in leaves.get(k, []):
                add(d["name"], *k, lf["branch"], "", "", "",
                    "design table placement; no source places it on a leaf, so it "
                    "applies on every leaf of the end use")
                design_only += 1

    # ---- swap the new tables in -------------------------------------------
    for old, new in ((steps, new_steps), (nodes, new_nodes), (techs, new_techs), (apps, new_apps)):
        old.clear()
        old.update(new)
    return {"technologies": len(new_techs), "with-facts": sum(1 for t in new_techs if nfacts[t]),
            "placeholders": sum(1 for t in new_techs.values() if t["status"] == "placeholder"),
            "folded": len(to_design), "nodes": len(new_nodes), "steps": len(new_steps),
            "applications": len(new_apps), "design-only": design_only,
            "unplaced": dict(unplaced),
            "facts": sum(nfacts.values())}
