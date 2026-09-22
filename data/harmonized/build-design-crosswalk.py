"""Crosswalk the harmonized layer onto the design tables, and report it.

The design tables -- design/sector-end-use-table.csv (end uses) and
design/end-use-technology-table.csv (technologies) -- become the controlled
vocabulary of the harmonized layer, in place of the roster the sources grew,
and design/cims_hierarchy.csv sets the level of detail below them.  This
script works out where every existing application and roster technology lands
in that vocabulary and writes it out, down to the hierarchy leaf.

The hierarchy is the definitive mapping (the user, 2026-09-22).  The CIMS
model-input files predate it and will be brought into line with it, so
cims-map.csv is not rebuilt: its rows are read only as the record of which
roster technologies came from CIMS and on which legacy branch, and that
legacy branch is used as evidence when choosing among hierarchy leaves, never
as a target.

It writes design-crosswalk-review.md and three crosswalk CSVs; it does not
touch the harmonized tables itself. populate.py applies it on every run
(adopt.py), handing it the source roster in memory; run standalone, it reads
that roster from source-roster/.

Run from the repo root:  python data/harmonized/build-design-crosswalk.py
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import design_names as dn
import design_names_hand as hand
import design_crosswalk as cw
import aggregate

ROOT = HERE.parent.parent


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def wr(path: Path, cols: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"  {path.name:34s} {len(rows):5d} rows")


# --- end-use resolution --------------------------------------------------
def step_rule(sector: str, step: str) -> str | None:
    if (sector, step) in cw.STEP_END_USE:
        return cw.STEP_END_USE[(sector, step)]
    for (s, pat), eu in cw.STEP_END_USE.items():
        if s == sector and pat.startswith("*") and step.endswith(pat[1:]):
            return eu
    return None


def resolve(sector: str, end_use: str, step: str, tech: str,
            equipment: str, variant: str) -> tuple[str, list[str], str]:
    """-> (design sector, design end uses, the rule that decided it)."""
    if tech in cw.TECH_END_USE:
        s, eu = cw.TECH_END_USE[tech]
        return s, [eu], "technology rule"
    # a separable steam system is cross-sector heat whatever sector raises it
    if end_use == "steam-and-hot-water":
        if variant == "chp":
            # CHP is a technology supplying the heat bands now, not an end use
            return "cross-sector", list(cw.BOTH_HEAT_BANDS), "chp supplies the bands"
        if equipment in cw.POWER_ONLY_EQUIPMENT:
            return "cross-sector", ["on-site-power-generation"], \
                "prime mover, no heat recovery"
        return "cross-sector", list(cw.BOTH_HEAT_BANDS), "steam serves both bands"
    # the step has its say before the generic services, so that mine
    # ventilation and mine air heating stay a mining end use
    if step:
        eu = step_rule(sector, step)
        if eu:
            return sector, [eu], "process step"
    # facility services, machine drive and refrigeration are cross-sector end
    # uses in the design table whatever sector the source reported them for --
    # the CIMS rows still carry their own sector, R2 having not run on them
    if end_use == "facility-services":
        return "cross-sector", [cw.FACILITY_SPLIT.get(equipment, "space-heating")], \
            "facility split by equipment"
    if end_use == "machine-drive":
        # the six MECS categories; the device decides which
        return "cross-sector", cw.MACHINE_DRIVE.get(equipment,
                                                    cw.MACHINE_DRIVE_DEFAULT), \
            "machine drive, MECS category"
    if end_use == "refrigeration-and-cooling":
        s, eu = cw.REFRIGERATION_END_USE
        return s, [eu], "refrigeration is a food and beverage end use"
    if end_use == "material-conversion" and equipment in cw.RNG_EQUIPMENT:
        s, eu = cw.RNG_END_USE
        return s, [eu], "biogas is a biofuels product"
    if sector == "petroleum-refining" and step in cw.REFINING_HEAT_GRADE:
        return "cross-sector", [cw.REFINING_HEAT_GRADE[step]], "refinery heat grade"
    # CIMS models a fuel blend and a hydrogen supply as services of their own
    if step == "methane-blend":
        s, eu = cw.RNG_END_USE
        return s, [eu], "fuel blend is renewable natural gas"
    if step == "hydrogen":
        s, eu = cw.HYDROGEN_BY_SECTOR.get(sector, cw.HYDROGEN_DEFAULT)
        return s, [eu], "hydrogen production, by host sector"
    if step == "cryogenics" and sector in cw.OXYGEN_BY_SECTOR:
        s, eu = cw.OXYGEN_BY_SECTOR[sector]
        return s, [eu], "oxygen supply, by sector"
    if step in cw.STEP_TO_CROSS_SECTOR:
        return "cross-sector", [cw.STEP_TO_CROSS_SECTOR[step]], "step moves cross-sector"
    if sector == "cross-sector" and end_use == "material-conversion":
        if equipment == "fuel-cell":
            return sector, ["on-site-power-generation"], "a fuel cell consumes hydrogen"
        if equipment in cw.CROSS_SECTOR_HYDROGEN:
            s, eu = cw.HYDROGEN_DEFAULT
            return s, [eu], "hydrogen production, no host sector"
    if sector == "chemicals" and end_use == "material-conversion":
        eu = cw.CHEMICALS_CONVERSION.get(equipment, "other-chemicals")
        return sector, [eu], "chemicals conversion by equipment"
    # After the sector rules: a reformer, electrolyzer or gasifier the sector
    # does not claim is hydrogen production -- on site where the host sector has
    # an end use for it, and the merchant hydrogen sector otherwise.
    if end_use == "material-conversion" and equipment in cw.HYDROGEN_SUPPLY_EQUIPMENT:
        s, eu = cw.HYDROGEN_BY_SECTOR.get(sector, cw.HYDROGEN_DEFAULT)
        return s, [eu], "hydrogen production, by host sector"
    key = (sector, end_use)
    if key in cw.EQUIPMENT_SPLIT:
        members, hit, miss = cw.EQUIPMENT_SPLIT[key]
        return sector, [hit if equipment in members else miss], "split by equipment"
    if key in cw.EU_END_USE:
        return sector, [cw.EU_END_USE[key]], "end use"
    return sector, [], "unmapped"


# --- branch resolution ----------------------------------------------------
# An application is taken from its design end use down to the hierarchy leaves
# that end use is made of (design/cims-hierarchy-crosswalk.csv). Where there is
# more than one, the source's own context chooses: first the sector it came
# from, then the device, then the words of its name, process step and legacy CIMS branch against the
# words of each leaf. What is still ambiguous is expanded to every remaining
# leaf and flagged, rather than guessed.
DESIGN = ROOT / "design"

HARM_TO_HIER = {          # harmonized (source) sector -> hierarchy sectors
    "iron-and-steel": {"iron-and-steel"}, "cement": {"industrial-minerals"},
    "non-metallic-minerals": {"industrial-minerals"}, "chemicals": {"chemicals"},
    "petroleum-refining": {"petroleum-refining"}, "pulp-and-paper": {"pulp-and-paper"},
    "mining": {"mining", "coal-mining"}, "food-and-beverage": {"light-industrial"},
    "other-industry": {"light-industrial", "iron-and-steel"},
    "non-ferrous-metals": {"metal-smelting"}, "oil-and-gas": {"natural-gas", "petroleum-crude"},
    "biofuels": {"biofuels"}, "hydrogen": {"hydrogen"},
}
LEGACY_TO_HIER = {        # first segment of a CIMS model-input branch
    "Iron and Steel": "iron-and-steel", "Metal Smelting": "metal-smelting",
    "Industrial Minerals": "industrial-minerals", "Chemical Products": "chemicals",
    "Pulp and Paper": "pulp-and-paper", "Petroleum Refining": "petroleum-refining",
    "Petroleum Crude": "petroleum-crude", "Natural Gas": "natural-gas", "Mining": "mining",
    "Coal Mining": "coal-mining", "Light Industrial": "light-industrial",
    "Ethanol": "biofuels", "Biodiesel": "biofuels", "Hydrogen": "hydrogen",
    "Direct Air Capture": "direct-air-capture",
}
STOP = {"product", "products", "service", "services", "primary", "metals", "size",
        "process", "the", "and", "of", "with", "other", "production", "supply",
        # energy words say what a device burns or delivers, not where it sits:
        # `heat-pump` must not pick `natural-gas.product.supply.direct-heat` for
        # sharing the word heat. `steam` stays, since steam leaves are a real home.
        "heat", "direct", "fired", "fuel", "natural", "gas", "electric",
        "electricity", "power", "efficiency", "moderate", "strong", "base"}


def _stem(w: str) -> str:
    """Crude, but enough to meet `roasting` with `roaster`, `smelting` with
    `smelter` and `refining` with `refining-furnace`."""
    for suf in ("ation", "ing", "ers", "er", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4 and not w.endswith("ss"):
            return w[: -len(suf)]
    return w


def _tok(text: str) -> set[str]:
    """Words for matching a source context against a leaf: lower-cased, stop
    words and numbers dropped, stemmed, and adjacent pairs joined so
    'Pyro Metallurgy' meets `pyrometallurgy`."""
    words = [w for w in re.split(r"[^a-z0-9]+", text.lower())
             if w and not w.isdigit() and w not in STOP]
    out = {_stem(w) for w in words}
    out |= {_stem(a + b) for a, b in zip(words, words[1:])}
    return out


def load_hierarchy() -> dict:
    """(design sector, end use) -> the hierarchy leaves that feed it."""
    fp = {r["branch"]: r["data-filepath"] for r in rd(DESIGN / "cims_hierarchy.csv")}
    out = collections.defaultdict(list)
    for r in rd(DESIGN / "cims-hierarchy-crosswalk.csv"):
        for t in (x.strip() for x in r["end-use"].split(";")):
            if t:
                s, eu = t.split("/", 1)
                out[(s, eu)].append({"branch": r["branch"], "share": r["share"],
                                     "role": r["role"],
                                     "data-filepath": fp.get(r["branch"], "")})
    return out


def narrow(cands: list[dict], ctx: dict, tech: str = "", equipment: str = "",
           key: tuple = ()) -> tuple[list[dict], str]:
    """The leaves among `cands` this source context points at, and how.

    Evidence in order: the sector the source came from; the equipment, where
    design_crosswalk.LEAF_BY_EQUIPMENT names the leaf a device belongs on; then
    the words of the roster name, the process step and the legacy branch
    against the words of each leaf."""
    if len(cands) <= 1:
        return cands, "single node"
    how = []
    lb = ctx.get("legacy-branch", "")
    head = lb.split(".")[0] if lb else ""
    secs = ({LEGACY_TO_HIER[head]} if head in LEGACY_TO_HIER
            else HARM_TO_HIER.get(ctx.get("from-sector", ""), set()))
    pool = [c for c in cands if c["branch"].split(".")[1] in secs]
    if pool and len(pool) < len(cands):
        cands, how = pool, ["sector"]
    hint = cw.LEAF_BY_EQUIPMENT.get(key, {}).get(equipment)
    if len(cands) > 1 and hint:
        pool = [c for c in cands if c["branch"].endswith("." + hint)]
        if pool:
            cands, how = pool, how + ["equipment"]
    if len(cands) > 1:
        words = _tok((lb.split(".", 1)[1] if "." in lb else "") + " "
                     + ctx.get("from-process-step", "") + " " + tech)
        # only the segments that tell the leaves apart: `ammonia-methanol`, the
        # parent both ammonia and methanol sit under, must not score for either
        segs = [c["branch"].split(".")[2:] for c in cands]
        common = set(segs[0]).intersection(*segs[1:])
        scored = [(len(set().union(set(), *(_tok(x) for x in sg if x not in common)) & words), c)
                  for sg, c in zip(segs, cands)]
        top = max(k for k, _ in scored)
        if top:
            pool = [c for k, c in scored if k == top]
            if len(pool) < len(cands):
                cands, how = pool, how + ["step"]
    if len(cands) > 1:
        how.append("expanded")
    return cands, "; ".join(how)


def branch_rows(app_rows: list[dict], contexts: dict, leaves: dict,
                equip: dict) -> list[dict]:
    """One row per (roster technology, hierarchy leaf)."""
    out, seen = [], {}
    for a in app_rows:
        s, eu = a["design-sector"], a["design-end-use"]
        if not eu:
            continue
        for ctx in contexts[(a["technology"], s, eu)]:
            picked, how = narrow(leaves.get((s, eu), []), ctx, a["technology"],
                                 equip.get(a["technology"], ""), (s, eu))
            for c in picked:
                key = (a["technology"], c["branch"], s, eu)
                if key in seen:
                    # several source contexts reach the same leaf: keep each
                    # distinct piece of evidence once
                    row = seen[key]
                    for k, v in (("origin", ctx["origin"]), ("how", how),
                                 ("source-id", ctx["source-id"]),
                                 ("from-sector", ctx["from-sector"]),
                                 ("from-end-use", ctx["from-end-use"]),
                                 ("from-process-step", ctx["from-process-step"]),
                                 ("legacy-branch", ctx.get("legacy-branch", ""))):
                        parts = row[k].split("; ")
                        parts += [x for x in v.split("; ") if x and x not in parts]
                        row[k] = "; ".join(parts)
                    continue
                row = {"technology": a["technology"], "design-sector": s,
                       "design-end-use": eu, "branch": c["branch"],
                       "data-filepath": c["data-filepath"], "share": c["share"],
                       "role": c["role"], "how": how, "origin": ctx["origin"],
                       "from-sector": ctx["from-sector"], "from-end-use": ctx["from-end-use"],
                       "from-process-step": ctx["from-process-step"],
                       "legacy-branch": ctx.get("legacy-branch", ""),
                       "source-id": ctx["source-id"]}
                seen[key] = row
                out.append(row)
    return out


# The roster as the sources grew it, before adoption. populate.py writes it
# here, and hands the same rows to main() in memory when it runs the adoption.
ROSTER = HERE / "source-roster"


def main(tech: list[dict] | None = None, apps: list[dict] | None = None,
         facts: dict | None = None) -> dict:
    """Build the crosswalk and write it out. Returns what an adoption pass needs.

    Standalone, it reads the source roster from source-roster/ and counts facts
    from the adopted fact tables by their roster-technology column."""
    aggregate._VOCAB_PATH[0] = HERE / "vocabulary.csv"
    seu = rd(dn.SEU)
    tt = rd(dn.TECHTABLE)
    vocab = dn.vocabularies()
    names = dn.build_names(tt, vocab, hand.EQUIPMENT_BY_LABEL,
                           hand.MERGE_LABEL, hand.HAND_NAME)

    tech = tech if tech is not None else rd(ROSTER / "technology.csv")
    apps = apps if apps is not None else rd(ROSTER / "technology-application.csv")
    cims = rd(HERE / "cims-map.csv")
    if facts is None:
        facts = {n: rd(HERE / f"tech-{n}.csv") for n in ("parameter", "flow", "constraint")}

    equip = {r["technology"]: r.get("equipment", "") for r in tech}
    variant = {r["technology"]: r.get("variant", "") for r in tech}
    carrier = {r["technology"]: r.get("energy-carrier", "") for r in tech}
    status = {r["technology"]: r.get("status", "") for r in tech}
    factcount = collections.Counter()
    for rows in facts.values():
        for r in rows:
            factcount[r.get("roster-technology") or r.get("technology", "")] += 1


    # design tables, indexed
    design_eu = {(r["sector"], r["end-use"]): r for r in seu}
    label_rows = collections.defaultdict(list)
    for r in tt:
        label_rows[hand.MERGE_LABEL.get(r["technology"], r["technology"])].append(r)
    by_name = {d["name"]: lab for lab, d in names.items()}
    placements = collections.defaultdict(set)       # design name -> {(sector, end use)}
    for lab, d in names.items():
        for r in label_rows[lab]:
            placements[d["name"]].add((r["sector"], r["end-use"]))

    # ---- 1. applications onto design end uses --------------------------
    # Two inputs.  The application rows carry everything the extractions and
    # the design-doc roster placed.  The CIMS rows are read again from
    # cims-map.csv because R2 merged the generic end uses onto cross-sector
    # and dropped the process step, and the design table's oil-and-gas end
    # uses need that step back (LNG compression against pipeline compression).
    seen, app_rows, unmapped_apps = {}, [], []
    reach = collections.defaultdict(set)            # roster tech -> design (sector, eu)
    contexts = collections.defaultdict(list)        # (tech, sector, eu) -> source contexts

    def place(t, s, eus, rule, origin, frm, legacy=""):
        if not eus:
            unmapped_apps.append({**frm, "technology": t})
            return
        for eu in eus:
            if (s, eu) not in design_eu:
                unmapped_apps.append({**frm, "technology": t})
                continue
            reach[t].add((s, eu))
            key = (t, s, eu)
            ctx = {"origin": origin, "from-sector": frm["from-sector"],
                   "from-end-use": frm["from-end-use"],
                   "from-process-step": frm["from-process-step"], "legacy-branch": legacy,
                   "source-id": frm.get("source-id", "")}
            if ctx not in contexts[key]:
                contexts[key].append(ctx)
            if key in seen:
                row = seen[key]
                if origin not in row["origin"]:
                    row["origin"] += "; " + origin
                if rule not in row["rule"]:
                    row["rule"] += "; " + rule
                continue
            row = {"technology": t, "design-sector": s, "design-end-use": eu,
                   "rule": rule, "origin": origin,
                   **{k: v for k, v in frm.items() if k != "source-id"}}
            seen[key] = row
            app_rows.append(row)

    for a in apps:
        t = a["technology"]
        s, eus, rule = resolve(a["sector"], a["end-use"], a["process-step"], t,
                               equip.get(t, ""), variant.get(t, ""))
        place(t, s, eus, rule, "application",
              {"from-sector": a["sector"], "from-end-use": a["end-use"],
               "from-process-step": a["process-step"],
               "source-id": a.get("source-id", "")})

    for r in cims:
        if r["action"] not in {"retain", "merge", "merge-review"} or not r["sector"]:
            continue
        t = aggregate.canon_tech(r["technology"])
        step = r["process-step"]
        hit = cw.branch_rule(r["cims-branch"])
        if hit and step not in cw.CIMS_STEP_TO_HEAT_BANDS:
            s, eu = hit
            eus, rule = [eu], "CIMS branch"
        elif step in cw.CIMS_STEP_TO_HEAT_BANDS:
            s, eus, rule = resolve(r["sector"], "steam-and-hot-water", "", t,
                                   equip.get(t, ""), variant.get(t, ""))
            rule = "CIMS steam service; " + rule
        else:
            s, eus, rule = resolve(r["sector"], r["end-use"], step, t,
                                   equip.get(t, ""), variant.get(t, ""))
        place(t, s, eus, rule, "cims-map",
              {"from-sector": r["sector"], "from-end-use": r["end-use"],
               "from-process-step": step}, legacy=r["cims-branch"])

    # ---- 1b. applications down to hierarchy leaves ----------------------
    leaves = load_hierarchy()
    br_rows = branch_rows(app_rows, contexts, leaves, equip)

    # ---- 2. roster technologies onto design technologies ---------------
    # the design table's own roster-match column first
    claimed = collections.defaultdict(list)
    for lab, d in names.items():
        for r in label_rows[lab]:
            for m in r["roster-match"].replace(",", ";").split(";"):
                m = m.strip()
                if m:
                    claimed[m].append(d["name"])

    missing = [n for n, _ in cw.HAND_TECH.values() if n not in by_name]
    assert not missing, f"HAND_TECH names not in the design table: {missing}"
    tech_rows, orphans = [], []
    for r in tech:
        t = r["technology"]
        cands, how, note_hand = [], "", ""
        if t in claimed:
            cands, how = sorted(set(claimed[t])), "roster-match"
        if len(cands) > 1 and reach.get(t):
            narrowed = [c for c in cands
                        if placements[c] & reach[t]]
            if narrowed:
                cands, how = narrowed, "roster-match, narrowed by end use"
        # `ccs` is in BOTH the carrier and the variant vocabulary in section
        # 6.2, so split_name files it in whichever component it reads first:
        # 14 of the 36 `_ccs` names carry it as the carrier.  Read it back.
        v = variant.get(t, "") or (
            carrier.get(t, "") if carrier.get(t, "") in vocab.get("variant", ()) else "")

        def by_carrier(pool):
            """Sorted, the rows whose energy inputs name the roster's carrier
            first: a plain electric pump is the standard motor, not the
            gas-turbine drive that happens to sort first."""
            c = carrier.get(t, "").replace("-", " ")
            return sorted(pool, key=lambda n: (not (c and c in names[by_name[n]]["carriers"]), n))

        def prefer(pool):
            """Within a pool, the row that matches the roster variant, else the
            conventional row, else the pool."""
            pref = []
            if v.startswith("efficiency-") and v != "efficiency-base":
                pref = [n for n in pool
                        if any(x["type"] == "efficient variant"
                               for x in label_rows[by_name[n]])]
                # a bucket row belongs to one device, so another device's bucket
                # is never the answer here: a pump's moderate bucket is the
                # premium motor and the variable-speed drive, not the gas-turbine
                # drive bucket that happens to sort first
                own = equip.get(t, "")
                pref = [n for n in pref
                        if "_efficiency-" not in n or n.rsplit("_", 1)[0] == own]
                same = [n for n in pref if n.split("_", 1)[0] == own]
                pref = same or pref
            elif v:
                pref = [n for n in pool if v in n]
            if not pref:
                pref = [n for n in pool
                        if any(x["type"] == "conventional"
                               for x in label_rows[by_name[n]])]
            return by_carrier(pref or pool)

        def strict(pool):
            """Only a row that matches the roster variant or is the conventional
            one; otherwise nothing, so the end use gets its say."""
            if v.startswith("efficiency-") and v != "efficiency-base":
                hit = [n for n in pool if any(x["type"] == "efficient variant"
                                              for x in label_rows[by_name[n]])]
            elif v and not v.startswith("efficiency-"):
                hit = [n for n in pool if v in n]
            else:
                hit = []
            return by_carrier(hit or [n for n in pool
                                      if any(x["type"] == "conventional"
                                             for x in label_rows[by_name[n]])])

        if not cands and v.startswith("efficiency-") and v != "efficiency-base":
            # the design table now carries `<equipment>_efficiency-moderate` and
            # `_efficiency-strong` rows; a roster bucket belongs on its own
            # bucket, and on the one for its own device where there is one
            same = [n for n in by_name if n.endswith("_" + v)
                    and n.rsplit("_", 1)[0] == equip.get(t, "")
                    and placements[n] & reach.get(t, set())]
            if same:
                cands, how = sorted(same), "efficiency bucket"
        if not cands and t in cw.HAND_TECH:
            n, note_hand = cw.HAND_TECH[t]
            cands, how = [n], "hand map"
        if not cands:
            eq = equip.get(t, "")
            pool = [n for n, lab in by_name.items()
                    if names[lab]["equipment"] == eq] if eq else []
            here = [n for n in pool if placements[n] & reach.get(t, set())]
            # Staying in the right end use beats matching the device: a wet
            # cement kiln belongs on the conventional clinker row, not on the
            # one other design row that happens to be spelled `kiln`.
            eu_pool = [n for n in by_name if placements[n] & reach.get(t, set())]
            # ...but the device beats the end use where the end use's claim is
            # weak: when the device has exactly one plain row there (a heat pump
            # on the low-temperature band is the industrial heat pump, not the
            # fuel-fired boiler that is the band's conventional row); when the
            # roster only placed it on generic cross-sector bands (a steam
            # cracker the old roster filed under steam); or when its own sector
            # holds the device on another end use (a pulper bucket filed under
            # chemical recovery). The wet-kiln case still reaches the clinker
            # row, because no cement kiln row is conventional.
            bucket = v.startswith("efficiency-") and v != "efficiency-base"

            def plain(pl):
                """Rows of the device's own kind: no capture row for a device
                without capture, no efficient variant for one that is not a
                bucket."""
                own_c = carrier.get(t, "")

                def other_carrier(n):
                    disc = "-" + (n.split("_", 1)[1] if "_" in n else "") + "-"
                    return any(f"-{c}-" in disc and c != own_c for c in vocab.get("carrier", ()))
                return [n for n in pl
                        if ("ccs" not in n or v == "ccs") and not other_carrier(n)
                        and (bucket or ("_efficiency-" not in n and not all(
                            x["type"] == "efficient variant" for x in label_rows[by_name[n]])))]

            def one_home(pl):
                """The rows all sit on one design end use, so the device's home
                is not a guess."""
                homes = {frozenset(placements[n]) for n in pl}
                return pl if len(homes) == 1 else []
            sectors_t = {s_ for s_, _ in reach.get(t, set())}
            same_sector = [n for n in pool if {s_ for s_, _ in placements[n]} & sectors_t]
            only_cross = sectors_t == {"cross-sector"}
            if strict(here):
                cands, how = strict(here), "equipment, same end use"
            elif len(plain(here)) == 1:
                cands, how = plain(here), "equipment, same end use (its only row)"
            elif only_cross and (len(strict(pool)) == 1 if bucket
                                 else (strict(pool) or len(plain(pool)) == 1)):
                cands, how = (strict(pool) or plain(pool)), "equipment, over a generic band"
            elif not only_cross and one_home(strict(same_sector)):
                cands, how = strict(same_sector), "equipment, same sector"
            elif eu_pool:
                cands, how = prefer(eu_pool), "end use, conventional row"
            elif here:
                cands, how = sorted(here), "equipment, same end use"
            elif pool:
                cands, how = prefer(pool), "equipment, any end use"
        note = note_hand
        if not cands:
            orphans.append(r)
            continue
        chosen = cands[0]
        types = {x["type"] for x in label_rows[by_name[chosen]]}

        def add(base, extra):
            if not base:
                return extra
            return base + ("" if base.endswith((".", ";")) else ".") + " " + extra

        if v == "ccs" and not any(k in chosen for k in ("ccs", "oxy-fuel", "capture")):
            note = add(note,
                "carries ccs; the design table holds capture as its own end use "
                "(co2-capture-concentrated / -diffuse), so the fold keeps the "
                "device and the capture moves")
        # efficiency-base is the incumbent with no measures applied, so landing
        # it on the conventional row is right, not a loss
        if v.startswith("efficiency-") and v != "efficiency-base" \
                and "efficient variant" not in types:
            note = add(note,
                f"the {v} bucket folds onto a {'/'.join(sorted(types))} row; the "
                "design table has no efficient variant for this device")
        tech_rows.append({"roster-technology": t, "design-technology": chosen,
                          "note": note,
                          "design-label": by_name[chosen],
                          "equipment": equip.get(t, ""), "energy-carrier": carrier.get(t, ""),
                          "variant": variant.get(t, ""), "status": status.get(t, ""),
                          "fact-rows": factcount[t], "matched-by": how,
                          "other-candidates": "; ".join(cands[1:])})
    write_review(seu, tt, names, label_rows, placements, app_rows,
                        unmapped_apps, tech_rows, orphans, tech, factcount,
                        vocab, apps, design_eu, br_rows, leaves)
    return {"names": names, "label_rows": label_rows, "tech_rows": tech_rows,
            "app_rows": app_rows, "br_rows": br_rows, "leaves": leaves,
            "seu": seu, "vocab": vocab, "factcount": factcount}


def write_review(seu, tt, names, label_rows, placements, app_rows, unmapped_apps,
                 tech_rows, orphans, tech, factcount, vocab, apps, design_eu,
                 br_rows, leaves) -> int:
    ccs_named = sum(1 for r in tech if r["technology"].endswith("_ccs"))
    ccs_as_carrier = sum(1 for r in tech if r["technology"].endswith("_ccs")
                         and r.get("energy-carrier") == "ccs")
    mapped = {r["roster-technology"] for r in tech_rows}
    landed = collections.Counter((r["design-sector"], r["design-end-use"])
                                 for r in app_rows if r["design-end-use"])
    filled = {r["design-technology"] for r in tech_rows}
    new_equipment = sorted({names[l]["equipment"] for l in names
                            if names[l]["equipment"] not in vocab.get("equipment", ())})
    new_disc = sorted({names[l]["discriminator"] for l in names
                       if names[l]["discriminator"]
                       and names[l]["discriminator"] not in vocab.get("variant", ())
                       and names[l]["discriminator"] not in vocab.get("energy-carrier", ())})

    wr(HERE / "design-crosswalk-technology.csv",
       ["roster-technology", "design-technology", "design-label", "equipment",
        "energy-carrier", "variant", "status", "fact-rows", "matched-by",
        "other-candidates", "note"], tech_rows)
    wr(HERE / "design-crosswalk-application.csv",
       ["technology", "from-sector", "from-end-use", "from-process-step",
        "design-sector", "design-end-use", "rule", "origin"], app_rows)
    wr(HERE / "design-crosswalk-branch.csv",
       ["technology", "design-sector", "design-end-use", "branch", "data-filepath",
        "share", "role", "how", "origin", "source-id", "from-sector", "from-end-use",
        "from-process-step", "legacy-branch"],
       sorted(br_rows, key=lambda r: (r["branch"], r["technology"])))

    out = []
    A = out.append
    A("# Adopting the design tables as the harmonized vocabulary")
    A("")
    A("Generated by `build-design-crosswalk.py`. **Applied** by `populate.py` "
      "through `adopt.py` since 2026-09-22: the harmonized tables are the design "
      "vocabulary, and the roster the sources grew is kept in `source-roster/`. "
      "This file is the record of how each source name, application and fact "
      "got where it is.")
    A("")
    A("## What changed")
    A("")
    A(f"| | now | design |")
    A("|---|---:|---:|")
    A(f"| Sectors | 11 | {len({r['sector'] for r in seu})} |")
    A(f"| End uses | 12 global | {len(seu)} sector-scoped |")
    A(f"| Technologies | {len(tech)} | {len(names)} |")
    A(f"| Applications | {len(apps)} | {len(app_rows)} |")
    A(f"| Applications at hierarchy-leaf level | -- | {len(br_rows)} |")
    A("")
    A("The sectors gained are `biofuels` and `oil-and-gas`; the end uses become "
      "sector-scoped, so the cross-sector heat bands supply the sector end uses "
      "rather than standing beside them, and CO2 capture splits three ways.")
    A("")
    A("## Coverage")
    A("")
    A(f"- **{len(mapped)} of {len(tech)}** roster technologies land on a design "
      f"technology; {len(orphans)} do not.")
    A(f"- **{len(filled)} of {len(names)}** design technologies receive at least one "
      f"roster technology. The other {len(names) - len(filled)} are the gap list: "
      "named in the design table, no data held.")
    A(f"- **{len(landed)} of {len(seu)}** design end uses receive at least one "
      f"application.")
    A(f"- {sum(factcount[o['technology']] for o in orphans)} fact rows sit on the "
      f"orphans, out of {sum(factcount.values())}.")
    A("")
    if orphans:
        A("### Orphans -- no design technology")
        A("")
        A("| roster technology | equipment | variant | status | fact rows |")
        A("|---|---|---|---|---:|")
        for o in sorted(orphans, key=lambda r: -factcount[r["technology"]]):
            A(f"| `{o['technology']}` | {o.get('equipment','')} | "
              f"{o.get('variant','')} | {o.get('status','')} | "
              f"{factcount[o['technology']]} |")
        A("")
    A("## Design end uses with nothing in them")
    A("")
    A("The hierarchy leaves each one is made of, and where their technology data "
      "would live. No roster application reaches them, so they are filled by new "
      "extractions, or by the CIMS model inputs once those follow the hierarchy -- "
      "not by re-labelling what the harmonized layer already holds.")
    A("")
    A("| design end use | hierarchy leaves | data folder |")
    A("|---|---|---|")
    for r in seu:
        k = (r["sector"], r["end-use"])
        if k in landed:
            continue
        ls = leaves.get(k, [])
        A(f"| `{r['sector']}` / `{r['end-use']}` | "
          f"{'; '.join(sorted('`' + x['branch'].split('.', 1)[1] + '`' for x in ls)) or 'none'} | "
          f"{'; '.join(sorted({'`' + x['data-filepath'].replace('data/service-technology-map/', '') + '`' for x in ls})) or '--'} |")
    A("")
    # ---- the branch level ------------------------------------------------
    per_app = collections.defaultdict(set)
    how_of = collections.defaultdict(set)
    for r in br_rows:
        k = (r["technology"], r["design-sector"], r["design-end-use"])
        per_app[k].add(r["branch"])
        how_of[k].update(r["how"].split("; "))
    one = sum(1 for v in per_app.values() if len(v) == 1)
    single = sum(1 for k, v in per_app.items() if len(v) == 1 and how_of[k] == {"single node"})
    all_leaves = {x["branch"] for v in leaves.values() for x in v}
    reached = {r["branch"] for r in br_rows}
    A("## Down to the hierarchy leaf")
    A("")
    A("Every application is taken from its design end use to the leaves of "
      "`design/cims_hierarchy.csv` that end use is made of. Where there is more "
      "than one, the source's own sector chooses first, then the device (a short "
      "hint table in `design_crosswalk.py`), then the words of the roster name, "
      "its process step and legacy CIMS branch against the leaf's; what is still "
      "ambiguous is expanded to every remaining leaf, flagged, and not guessed. "
      "The legacy branch is evidence only -- the hierarchy is the target.")
    A("")
    A(f"- **{one} of {len(per_app)}** applications land on exactly one leaf: "
      f"{single} because their end use has only one, {one - single} after narrowing "
      "by sector or step.")
    A(f"- **{len(per_app) - one}** are expanded across several leaves, giving "
      f"{len(br_rows)} leaf-level rows in `design-crosswalk-branch.csv`.")
    A(f"- **{len(reached)} of {len(all_leaves)}** hierarchy leaves that feed an end "
      "use receive at least one application.")
    A("")
    exp = collections.Counter()
    for k, v in per_app.items():
        if len(v) > 1:
            exp[(k[1], k[2])] += 1
    if exp:
        A("Expanded applications by design end use -- mostly generic technologies "
          "with no source sector, which legitimately apply on every sector's leaf, "
          "and sector end uses whose leaves are product grades:")
        A("")
        A("| design end use | expanded applications | leaves |")
        A("|---|---:|---:|")
        for (s_, eu), n in exp.most_common():
            A(f"| `{s_}` / `{eu}` | {n} | {len(leaves.get((s_, eu), []))} |")
        A("")
    A("## Vocabulary the names need")
    A("")
    A(f"Naming follows section 5: `-` within a component, `_` between. With the "
      f"carrier now a list on the row rather than a name component, a design "
      f"technology is named `equipment_discriminator`.")
    A("")
    A(f"**{len(new_equipment)} equipment terms** are not in section 6.2 and would "
      "have to be added, or the labels renamed onto existing terms:")
    A("")
    A(", ".join(f"`{t}`" for t in new_equipment))
    A("")
    A(f"**{len(new_disc)} discriminators** are not existing variant or carrier "
      "terms. Section 6.2 treats a new term as a modelling decision, so the "
      "options are to add them, to widen the variant list into a free "
      "discriminator, or to shorten the names.")
    A("")
    A("## How the adoption applies it")
    A("")
    A("1. `build-template.py` seeds `sector` with the design table's sectors and "
      "`end-use` from the design table itself, with a `sector` column; section 6.2 "
      "gained the equipment terms the design names use.")
    A("2. `adopt.py`, inside `populate.py`, writes the source roster to "
      "`source-roster/`, runs this crosswalk on it, and replaces the roster with "
      "one row per design technology, the service nodes with one per (end use, "
      "hierarchy leaf), and the applications with `design-crosswalk-branch.csv` "
      "plus the design table's own placements.")
    A("3. Every fact moves onto its design technology and keeps the source name in "
      "`roster-technology`; the wide views show one row per source name.")
    A("4. `cims-map.csv` is not rebuilt: the hierarchy is the target, and the "
      "model inputs will follow it.")
    A("5. `check-data.py` holds the result to the design vocabulary and the hierarchy.")
    A("")
    A("## Folds that carry a note")
    A("")
    A("Where the fold costs something, or where the target is not the obvious one.")
    A("")
    A("| roster technology | design technology | what to know |")
    A("|---|---|---|")
    for r in sorted(tech_rows, key=lambda x: x["roster-technology"]):
        if r["note"]:
            A(f"| `{r['roster-technology']}` | `{r['design-technology']}` | "
              f"{r['note']} |")
    A("")
    A("## Every technology")
    A("")
    A("| design technology | label | type | sectors | roster technologies folded in | fact rows |")
    A("|---|---|---|---|---|---:|")
    folded = collections.defaultdict(list)
    for r in tech_rows:
        folded[r["design-technology"]].append(r["roster-technology"])
    for lab in sorted(names, key=lambda l: names[l]["name"]):
        d = names[lab]
        rows = label_rows[lab]
        types = "; ".join(sorted({r["type"] for r in rows}))
        secs = "; ".join(sorted({f"{r['sector']}/{r['end-use']}" for r in rows}))
        fold = folded.get(d["name"], [])
        n = sum(factcount[t] for t in fold)
        A(f"| `{d['name']}` | {lab} | {types} | {secs} | "
          f"{'; '.join(f'`{t}`' for t in sorted(fold)) or '--'} | {n} |")
    A("")
    A("## Every end use")
    A("")
    A("| design end use | applications | rules that placed them |")
    A("|---|---:|---|")
    rules = collections.defaultdict(collections.Counter)
    for r in app_rows:
        if r["design-end-use"]:
            rules[(r["design-sector"], r["design-end-use"])][r["rule"]] += 1
    for r in seu:
        k = (r["sector"], r["end-use"])
        A(f"| `{r['sector']}` / `{r['end-use']}` | {landed.get(k, 0)} | "
          f"{'; '.join(f'{a} ({b})' for a, b in rules[k].most_common()) or '--'} |")
    A("")
    if unmapped_apps:
        A("## Applications no rule placed")
        A("")
        A("| technology | sector | end use | process step |")
        A("|---|---|---|---|")
        for a in sorted({(x["technology"], x["from-sector"], x["from-end-use"],
                          x["from-process-step"]) for x in unmapped_apps}):
            A(f"| `{a[0]}` | {a[1]} | {a[2]} | {a[3]} |")
        A("")
    A("## Found while crosswalking")
    A("")
    A(f"- **`ccs` is in both the carrier and the variant vocabulary** in section "
      f"6.2, so `aggregate.split_name` files it in whichever component it reads "
      f"first: {ccs_as_carrier} of the {ccs_named} roster names ending `_ccs` "
      "carry it as the energy carrier and the rest as the variant. The design "
      "doc already notes this for `oxyfuel-ccs`; plain `ccs` has the same "
      "problem. Until it is fixed, anything keying on the variant column misses "
      "those rows -- this script reads the carrier back.")
    A("- **R2 has already merged away a distinction the new end uses need.** The "
      "generic end uses were collapsed onto `cross-sector` with no process step, "
      "so `Natural Gas.Production.Supply.Extraction.Compression`, "
      "`...Processing.Compression` and `...Transmission.Compression` are one "
      "application row with a joined `reported-steps` cell, while the design "
      "table puts them in three different end uses. CIMS placements here are "
      "therefore resolved from each `cims-map.csv` row's legacy branch, not from "
      "the merged application row, and that branch is kept on the leaf-level "
      "rows as evidence.")
    A("- **One efficiency bucket sits on a node it does not belong to.** "
      "`rolling-mill_efficiency-moderate` reaches `mining` / "
      "`separation-and-processing` through a mining forming-and-finishing node, "
      "which is why that end use is the only one taking a roster efficiency "
      "bucket with no efficient variant of its own. The design table is not "
      "missing an option here; the extraction filed a rolling mill in mining.")
    A("- **`Petroleum Crude.Steam` is claimed twice** -- by `oil-and-gas` / "
      "`in-situ-bitumen` in its `cims-services` cell, and by the cross-sector "
      "heat bands. The integral-vs-supplied rule and that row's own "
      "`heat-delivery` cell (\"draws heat-medium-temp\") both say the steam "
      "system is cross-sector, so that is where this crosswalk puts it, and "
      "`in-situ-bitumen` is left with only the CIMS In-Situ rows, which the "
      "mapper has not placed.")
    A("")
    A("## Naming flags")
    A("")
    A("| design technology | label | flag |")
    A("|---|---|---|")
    for lab in sorted(names, key=lambda l: names[l]["name"]):
        for f in names[lab]["flags"]:
            if f != "new discriminator":
                A(f"| `{names[lab]['name']}` | {lab} | {f} |")
    path = HERE / "design-crosswalk-review.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"  {path.name:34s} {len(out):5d} lines")
    return 0


if __name__ == "__main__":
    main()
