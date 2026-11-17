"""Write the Global Energy Monitor (GEM) tracker extractions (ETSAP-brief shape).

    python gem_extract.py                 # every tracker
    python gem_extract.py steel coal      # some of them (keys in TRACKERS)

Reads the GEM workbooks from the same folder under primary-sources/
(primary-sources/other-reports/gem/, unpacked from the modeller's gem-data.zip
download, 2026-11-11). Writes, beside this script, for each tracker loaded:
<stem>.csv, <stem>_nodes.csv, <stem>_other-values.csv, <stem>_meta.csv and
<stem>_canada-stock.csv; for the trackers held but not loaded (oil and gas
plants, coal plants, methane emitters) only _meta and the Canadian sidecar.

What is loaded: the size of the typical existing facility, as the median
(value-min, value-max = 25th and 75th percentiles) over operating facilities or
units, and, where GEM gives production, the capacity factor (production /
capacity, per facility). Brad 2026-10-21: archetype sizes are the median of
existing facilities; facility statistics are graded sourced. Brad 2026-11-11:
prioritise Canadian examples and use international ones where appropriate or
necessary. The scope rule, applied per example:

    Canada, if three or more Canadian facilities report the value;
    else North America (Canada, United States, Mexico), if three or more do;
    else global.

Each example names its scope in the process label and, when it falls back,
lists the Canadian facilities in its note. The Canadian rosters
(<stem>_canada-stock.csv: every Canadian facility or unit at any status, with
operating-capacity shares) are not loaded by the build: they are the stock data
for calibrating CIMS technology shares later (Brad 2026-11-11).

Costs GEM reports (pipelines, LNG terminals, blast-furnace relinings) go to
_other-values, not loaded: GEM converts them to USD without stating the cost
year, and a pipeline or terminal cost covers a whole project.
"""
import csv, math, re, sys, warnings
from pathlib import Path as _Path

import pandas as pd

warnings.filterwarnings("ignore")
_HERE = _Path(__file__).resolve().parent
_RAW = next(p for p in (_HERE, *_HERE.parents) if p.name == "technology_database" and p.parent.name == "raw_data")
REPO_ROOT = _RAW.parents[2]
DOCS = REPO_ROOT / "primary-sources" / _HERE.relative_to(_RAW)
HERE = _HERE
ACCESSED = "2026-11-11"

CANADA = {"Canada"}
NORTH_AMERICA = {"Canada", "United States", "United States of America", "USA", "Mexico"}
SCOPES = (("Canada", CANADA), ("North America (Canada, US, Mexico)", NORTH_AMERICA), ("global", None))
MIN_N = 3
BBL_M3 = 0.158987


def num(s):
    return pd.to_numeric(s, errors="coerce")


def q(v, p):
    v = sorted(v)
    k = (len(v) - 1) * p
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def g4(x):
    return float("%.4g" % x)


def fmt(x):
    x = g4(x)
    return str(int(x)) if x == int(x) and abs(x) < 1e15 else repr(x)


def is_op(s):
    return s.astype(str).str.lower().str.startswith("operating")


def in_scope(series, countries):
    """Rows whose country (or any country of a cross-border asset) is in the set."""
    if countries is None:
        return pd.Series(True, index=series.index)
    return series.astype(str).apply(lambda s: any(c.strip() in countries for c in re.split(r"[;,]", s)))


def pick(df, country_col, values):
    """Apply the scope rule. `values(df)` returns a list of (value, label) pairs.
    Returns (scope label, values, labels, Canadian pairs)."""
    ca = values(df[in_scope(df[country_col], CANADA)])
    for label, cs in SCOPES:
        pairs = values(df[in_scope(df[country_col], cs)])
        pairs = [(v, l) for v, l in pairs if v is not None and not math.isnan(v) and v > 0]
        if len(pairs) >= MIN_N or cs is None:
            return label, [v for v, _ in pairs], [l for _, l in pairs], ca
    raise AssertionError


def about_text(path, sheet):
    """The copyright, licence and recommended-citation lines of a GEM About sheet."""
    a = pd.read_excel(path, sheet_name=sheet, header=None)
    out = []
    for v in a.astype(str).values:
        t = " ".join(x for x in v if x != "nan").strip()
        if any(w in t for w in ("Copyright", "Recommended")):
            out.append(re.sub(r"\s+", " ", t))
    return " | ".join(out)


class Out:
    """One tracker's extraction files."""

    def __init__(self, stem, sid, title, sector):
        self.stem, self.sid, self.title, self.sector = stem, sid, title, sector
        self.rows, self.nodes, self.other, self.stock = [], [], [], []

    def example(self, process, tech, desc, end_use, step, unit):
        self.nodes.append([process, tech, self.sector, end_use, step, unit])
        self.rows.append([process, tech, "description", "", "", desc, "", "", "", "", ""])

    def stat(self, process, tech, param, unit, scope, vals, what, ref, note="", target=""):
        if not vals:
            return
        n = len(vals)
        self.rows.append([process, tech, param, target, unit, fmt(q(vals, .5)), fmt(q(vals, .25)),
                          fmt(q(vals, .75)), f"median (p25-p75) of {n} {what}, {scope}", ref, note])

    def ov(self, process, tech, item, vals, unit, ref, note):
        if not vals:
            return
        v = f"{fmt(q(vals, .5))} ({fmt(q(vals, .25))}-{fmt(q(vals, .75))}), n={len(vals)}"
        self.other.append([process, tech, item, v, unit, ref, note])

    def write(self, meta):
        def w(name, header, rows):
            with open(HERE / f"{self.stem}{name}.csv", "w", newline="", encoding="utf-8") as f:
                csv.writer(f, lineterminator="\n").writerows([header] + rows)
        if self.rows:
            w("", ["process", "technology", "parameter", "target", "unit", "value", "value-min",
                   "value-max", "formula", "reference", "note"], self.rows)
            w("_nodes", ["process", "technology", "sector", "end-use", "process-step", "service-unit"], self.nodes)
        if self.other:
            w("_other-values", ["process", "technology", "item", "value", "unit", "reference", "note"], self.other)
        if self.stock:
            for r in self.stock:
                r[5] = str(r[5])[:4] if str(r[5])[:4].isdigit() else ""
                r[9] = re.sub(r"\s+", " ", re.sub(r"\bnan\b", "", str(r[9]))).strip()
            w("_canada-stock", STOCK_HEADER, self.stock)
        w("_meta", ["parameter", "value"], [[k, v] for k, v in meta])
        print(self.stem, len(self.rows), "rows,", len(self.nodes), "examples,", len(self.other),
              "other values,", len(self.stock), "stock rows")


STOCK_HEADER = ["archetype", "item", "facility", "unit-name", "status", "start-year", "value", "unit",
                "year", "detail", "operating-share", "share-group", "gem-id"]


def shares(stock, group_of):
    """Fill operating-share: each operating capacity row's share of the Canadian
    operating capacity of its share group (the archetypes that compete for one
    product: ironmaking, steelmaking, clinker, ...)."""
    tot = {}
    for r in stock:
        g = group_of.get(r[0])
        if g and r[1] == "capacity" and str(r[4]).lower().startswith("operating") and r[6] != "":
            tot[g] = tot.get(g, 0) + float(r[6])
    for r in stock:
        g = group_of.get(r[0])
        r[11] = g or ""
        if g and r[1] == "capacity" and str(r[4]).lower().startswith("operating") and r[6] != "" and tot.get(g):
            r[10] = fmt(100 * float(r[6]) / tot[g])


def canada_note(ca, unit, scope):
    if scope == "Canada":
        return ""
    vs = [fmt(v) for v, _ in ca if v is not None and not math.isnan(v) and v > 0]
    return (f"Fewer than three Canadian facilities report it (Canada: {len(vs)}"
            + (f": {', '.join(vs)} {unit}" if vs else "") + f"), so the {scope} fleet. ")


def meta_rows(o, licence_text, citation, note):
    return [("licence", "CC BY 4.0 (Creative Commons Attribution 4.0 International); copyright Global "
             "Energy Monitor. As printed: " + licence_text),
            ("citation", citation), ("source-id", o.sid), ("extraction-note", note)]


# --------------------------------------------------------------------------- steel
def steel():
    f_pl = DOCS / "gem_2026_global-iron-and-steel-tracker_plant-level.xlsx"
    f_ir = DOCS / "gem_2026_global-iron-and-steel-tracker_iron-units.xlsx"
    f_st = DOCS / "gem_2026_global-iron-and-steel-tracker_steel-units.xlsx"
    o = Out("gem_2026_global-iron-and-steel-tracker", "gem_2026_001",
            "Global Iron and Steel Tracker, September 2026 (V1)", "iron-and-steel")
    bf = pd.read_excel(f_ir, sheet_name="Blast furnaces")
    dri = pd.read_excel(f_ir, sheet_name="Direct reduced iron furnaces")
    rl = pd.read_excel(f_ir, sheet_name="Blast furnace relinings")
    eaf = pd.read_excel(f_st, sheet_name="Electric arc furnaces")
    bof = pd.read_excel(f_st, sheet_name="Basic oxygen furnaces")
    pdat = pd.read_excel(f_pl, sheet_name="Plant data")
    pcap = pd.read_excel(f_pl, sheet_name="Plant capacities and status")
    prod = pd.read_excel(f_pl, sheet_name="Plant production")
    for d in (bf, dri, eaf, bof):
        d["cap"] = num(d["Current capacity (ttpa)"])
    for k in ("% DRI", "% HBI", "% sponge iron (unknown if DRI or HBI)"):
        eaf[k] = num(eaf[k])
    eaf["ri"] = eaf[["% DRI", "% HBI", "% sponge iron (unknown if DRI or HBI)"]].sum(axis=1, min_count=1).fillna(0)
    names = dict(zip(pdat["GEM plant ID"], pdat["Plant name (English)"]))
    REF_U = "GEM Global Iron and Steel Tracker, September 2026 (V1), {f}, '{s}' tab: Current capacity (ttpa); units with status operating or operating pre-retirement"
    units = [
        ("blast-furnace", bf, "Blast furnaces", "iron unit data", lambda d: d,
         "Blast furnaces", "ironmaking", "iron", "operating blast furnaces"),
        ("shaft-furnace_direct-reduction", dri, "Direct reduced iron furnaces", "iron unit data",
         lambda d: d[(d["Furnace type"] == "shaft furnace") & (d["Current or initial Reductant"] == "gas")],
         "Gas-based shaft-furnace direct reduction", "ironmaking", "reduced iron",
         "operating gas-based shaft furnaces (furnace type shaft furnace, reductant gas)"),
        ("basic-oxygen-furnace", bof, "Basic oxygen furnaces", "steel unit data", lambda d: d,
         "Basic oxygen furnaces", "steelmaking", "liquid steel", "operating basic oxygen furnaces"),
        ("electric-arc-furnace", eaf, "Electric arc furnaces", "steel unit data", lambda d: d[d["ri"] < 0.5],
         "Electric arc furnaces, scrap charge (under 50% reduced iron)", "steelmaking", "liquid steel",
         "operating electric arc furnaces charging under 50% DRI, HBI or sponge iron"),
        ("electric-arc-furnace_reduced-iron-charge", eaf, "Electric arc furnaces", "steel unit data",
         lambda d: d[d["ri"] >= 0.5],
         "Electric arc furnaces, reduced-iron charge (50% or more DRI or HBI)", "steelmaking", "liquid steel",
         "operating electric arc furnaces charging 50% or more DRI, HBI or sponge iron"),
    ]
    procs = {}
    for tech, d, sheet, fname, sel, label, step, prodname, what in units:
        op = sel(d[is_op(d["Unit status"])])
        scope, vals, labs, ca = pick(op, "Country/area",
                                     lambda x: list(zip(x["cap"], x["GEM unit ID"])))
        proc = f"{label} (GEM GIST September 2026)"
        o.example(proc, tech, f"{label}: nameplate capacity per furnace of the operating fleet; "
                  f"Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula) (GEM Global Iron and Steel Tracker).", "material-conversion", step, "t")
        o.stat(proc, tech, "capacity", "kt/yr", scope, vals, f"{what} (per furnace)",
               REF_U.format(f=fname, s=sheet),
               canada_note([(v, None) for v, _ in ca], "kt/yr", scope)
               + f"Per furnace, nameplate {prodname} capacity. CAPACITY BASIS: product-output.")
        procs[tech] = proc

    # plant-level capacity factor: 2024 production / operating route capacity
    pcap_op = pcap[is_op(pcap["Status"])]
    capcols = {"blast-furnace": ("Nominal BF capacity (ttpa)", "BF production (ttpa)"),
               "basic-oxygen-furnace": ("Nominal BOF steel capacity (ttpa)", "BOF steel production (ttpa)"),
               "shaft-furnace_direct-reduction": ("Nominal DRI capacity (ttpa)", "DRI production (ttpa)"),
               "electric-arc-furnace": ("Nominal EAF steel capacity (ttpa)", "EAF steel production (ttpa)"),
               "electric-arc-furnace_reduced-iron-charge": ("Nominal EAF steel capacity (ttpa)", "EAF steel production (ttpa)")}
    eop = eaf[is_op(eaf["Unit status"])]
    ri_plant = (eop.assign(w=eop["cap"] * eop["ri"]).groupby("GEM plant ID")[["w", "cap"]].sum())
    ri_plant = (ri_plant["w"] / ri_plant["cap"]).to_dict()
    country = dict(zip(pcap["GEM plant ID"], pcap["Country/area"]))
    for tech, proc in procs.items():
        ccol, pcol = capcols[tech]
        cap = pcap_op.groupby("GEM plant ID")[ccol].apply(lambda s: num(s).sum(min_count=1))
        pr = prod[prod["Type of production"] == pcol].assign(v=lambda x: num(x[2024])).groupby("GEM plant ID")["v"].sum(min_count=1)
        rows = []
        for pid, c in cap.items():
            if not (c and c > 0) or pid not in pr.index or not (pr[pid] > 0):
                continue
            if tech.startswith("electric-arc-furnace"):
                r = ri_plant.get(pid)
                if r is None or (r >= 0.5) != tech.endswith("reduced-iron-charge"):
                    continue
            cf = 100 * float(pr[pid]) / c
            if cf <= 110:
                rows.append({"pid": pid, "Country/area": country.get(pid, ""), "cf": cf})
        df = pd.DataFrame(rows)
        if df.empty:
            continue
        scope, vals, labs, ca = pick(df, "Country/area", lambda x: list(zip(x["cf"], x["pid"])))
        o.stat(proc, tech, "capacity-factor", "%", scope, vals,
               "plants (2024 production / operating route capacity)",
               f"GEM GIST September 2026 (V1), plant-level data: 'Plant production' tab, {pcol} 2024, over "
               f"'Plant capacities and status' tab, {ccol} of the operating rows",
               canada_note(ca, "%", scope) + "Plant-level: the route's 2024 output over its operating "
               "capacity; plants whose ratio exceeds 110% are left out (capacity and output rows that do "
               "not match)." + (" EAF plants are split by the capacity-weighted reduced-iron share of "
                                "their operating furnaces." if tech.startswith("electric") else ""))

    # plant-level agglomeration and coke capacities
    live = set(pcap_op["GEM plant ID"])
    pl = pdat[pdat["GEM plant ID"].isin(live)]
    for tech, col, label, prodname in (
            ("coke-oven_by-product", "Coking plant capacity (ttpa)", "Coke plants at steel works", "coke"),
            ("sinter-plant", "Sinter plant capacity (ttpa)", "Sinter plants at steel works", "sinter"),
            ("pellet-plant_induration", "Pelletizing plant capacity (ttpa)", "Pellet plants at steel works", "pellets")):
        scope, vals, labs, ca = pick(pl, "Country/area",
                                     lambda x: list(zip(num(x[col]), x["GEM plant ID"])))
        proc = f"{label} (GEM GIST September 2026)"
        o.example(proc, tech, f"{label}: {prodname} capacity per plant at operating steel works; Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).",
                  "material-conversion", "coke-making" if tech.startswith("coke") else "agglomeration", "t")
        o.stat(proc, tech, "capacity", "kt/yr", scope, vals, f"steel works reporting a {prodname} capacity",
               f"GEM GIST September 2026 (V1), plant-level data, 'Plant data' tab: {col}; plants with an "
               "operating row in 'Plant capacities and status'",
               canada_note(ca, "kt/yr", scope) + f"Per plant (all batteries or strands together), "
               f"{prodname} capacity; only plants inside steel works (mine-site pellet plants are not in "
               "this tracker). CAPACITY BASIS: product-output.")

    # other values: retired blast-furnace and BOF lifetimes; relining costs
    for d, tech, label in ((bf, "blast-furnace", "Blast furnaces"), (bof, "basic-oxygen-furnace", "Basic oxygen furnaces")):
        r = d[d["Unit status"] == "retired"]
        life = (num(r["Retired date"].astype(str).str[:4]) - num(r["Start date"].astype(str).str[:4])).dropna()
        life = [v for v in life if v > 0]
        o.ov(f"{label}, retired units (GEM GIST September 2026)", tech,
             "service life of retired units (retired year - start year)", life, "years",
             "GEM GIST September 2026 (V1), unit data: Start date, Retired date",
             "Not loaded: few retired units carry both years, and blast furnaces are relined every "
             "15-20 years, so the start year is often the site's first campaign, not the furnace's.")
    rl = rl.merge(bf[["GEM unit ID", "cap", "Country/area"]], on="GEM unit ID", how="left")
    usd = rl[(rl["Relining cost unit"] == "USD") & (num(rl["Relining cost"]) > 0) & (rl["cap"] > 0)]
    o.ov("Blast furnace relinings with a USD cost (GEM GIST September 2026)", "blast-furnace",
         "relining cost per t of annual furnace capacity", list(num(usd["Relining cost"]) / (usd["cap"] * 1000)),
         "USD/t-per-yr", "GEM GIST September 2026 (V1), iron unit data, 'Blast furnace relinings' tab",
         "Not loaded: nominal costs, cost year not stated (relining start years range widely); a "
         "candidate for the rebuild allowance.")
    dur = num(rl["Furnace relining duration (Days)"]).dropna()
    o.ov("Blast furnace relinings (GEM GIST September 2026)", "blast-furnace", "relining duration",
         [v for v in dur if v > 0], "days", "GEM GIST September 2026 (V1), iron unit data, "
         "'Blast furnace relinings' tab: Furnace relining duration (Days)", "Not loaded.")

    # Canadian stock (every unit, any status) and plant production
    def add_units(d, tech_of, sheet):
        for _, r in d[d["Country/area"] == "Canada"].iterrows():
            t = tech_of(r)
            o.stock.append([t, "capacity", names.get(r["GEM plant ID"], ""), r["Unit name"], r["Unit status"],
                            str(r["Start date"])[:4], "" if pd.isna(r["cap"]) else fmt(r["cap"]), "kt/yr", "",
                            sheet + (f"; reduced-iron share {fmt(100 * r['ri'])}%" if "ri" in r else "")
                            + (f"; {r['Furnace type']}, {r['Current or initial Reductant']}" if "Furnace type" in r else ""),
                            "", "", r["GEM unit ID"]])
    add_units(bf, lambda r: "blast-furnace", "blast furnace")
    add_units(dri, lambda r: "shaft-furnace_direct-reduction" if r["Furnace type"] == "shaft furnace" else "", "DRI furnace")
    add_units(bof, lambda r: "basic-oxygen-furnace", "basic oxygen furnace")
    add_units(eaf, lambda r: "electric-arc-furnace_reduced-iron-charge" if r["ri"] >= 0.5 else "electric-arc-furnace",
              "electric arc furnace")
    for _, r in pdat[pdat["Country/area"] == "Canada"].iterrows():
        for tech, col in (("coke-oven_by-product", "Coking plant capacity (ttpa)"),
                          ("sinter-plant", "Sinter plant capacity (ttpa)"),
                          ("pellet-plant_induration", "Pelletizing plant capacity (ttpa)")):
            v = r[col]
            if pd.notna(v) and str(v) not in ("0", "unknown"):
                o.stock.append([tech, "capacity", r["Plant name (English)"], "", "operating" if r["GEM plant ID"] in live else "",
                                "", fmt(float(v)) if num(pd.Series([v]))[0] > 0 else "", "kt/yr", "",
                                f"plant-level; printed '{v}'", "", "", r["GEM plant ID"]])
    can = set(pdat.loc[pdat["Country/area"] == "Canada", "GEM plant ID"])
    for _, r in prod[prod["GEM plant ID"].isin(can)].iterrows():
        for y in (2019, 2020, 2021, 2022, 2023, 2024, 2025):
            v = num(pd.Series([r[y]]))[0]
            if v > 0:
                o.stock.append(["", "production", r["Plant name (English)"], "", "", "", fmt(v), "kt/yr", str(y),
                                r["Type of production"], "", "", r["GEM plant ID"]])
    shares(o.stock, {"blast-furnace": "ironmaking", "shaft-furnace_direct-reduction": "ironmaking",
                     "basic-oxygen-furnace": "steelmaking", "electric-arc-furnace": "steelmaking",
                     "electric-arc-furnace_reduced-iron-charge": "steelmaking"})
    lic = about_text(f_pl, "About")
    o.write(meta_rows(o, lic,
        "Global Energy Monitor (2026). Global Iron and Steel Tracker, September 2026 (V1) release: plant-level "
        "data, iron unit data and steel unit data workbooks. https://globalenergymonitor.org/projects/"
        f"global-iron-and-steel-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip, downloaded by the modeller). Three workbooks: plant-level "
        "data (plants, capacities by route, production 2019-2025), iron unit data (blast furnaces, DRI furnaces, "
        "relinings) and steel unit data (EAF, BOF, induction and open-hearth furnaces). Loaded by gem_extract.py: "
        "per-furnace nameplate capacity of the operating fleet for blast furnaces, gas-based shaft furnaces, BOFs and "
        "EAFs (scrap and reduced-iron charge split at 50% DRI+HBI+sponge iron), per-plant coke, sinter and pellet "
        "capacity, and plant-level 2024 capacity factors. Scope rule: Canada where three or more facilities report "
        "the value, else North America, else global (Brad 2026-11-11). Not loaded: induction and open-hearth "
        "furnaces (no archetype), coal-based and rotary-kiln DRI (no matching archetype), lifetimes and relining "
        "costs (_other-values). The Canadian roster with operating-capacity shares (_canada-stock.csv) is for "
        "calibrating CIMS technology shares later, not loaded. Traps: percentages of the EAF charge are printed as "
        "fractions (0-1); Cleveland-Cliffs Lake Erie's 2024 output is printed under 'EAF steel production' although "
        "the plant has no EAF (left out by the capacity match); Algoma's blast furnaces and BOFs are shown retired "
        "(EAF transition, 2025-2026); capacities printed 'unknown' or '>0' are not numbers and are skipped."))


# --------------------------------------------------------------------------- cement
def cement():
    f = DOCS / "gem_2026_global-cement-and-concrete-tracker.xlsx"
    o = Out("gem_2026_global-cement-and-concrete-tracker", "gem_2026_002",
            "Global Cement and Concrete Tracker, July 2026 (V1)", "cement")
    c = pd.read_excel(f, sheet_name="Final data")
    c["cl"] = num(c["Clinker capacity (million metric tonnes per annum)"]) * 1000
    c["ce"] = num(c["Cement capacity (million metric tonnes per annum)"]) * 1000
    c["pr"] = num(c["2024-2025 Cement production (million metric tonnes)"]) * 1000
    c["k"] = num(c["Number of existing kilns"])
    c["perkiln"] = c["cl"] / c["k"]
    op = c[c["Operating status"] == "operating"]
    REF = "GEM Global Cement and Concrete Tracker, July 2026 (V1), 'Final data' tab"
    for tech, sel, label, what in (
            ("kiln_dry-precalciner",
             lambda d: d[(d["Kiln technology - precalciner"] == "yes") & (d["Clinker production method"] == "dry")],
             "Dry preheater-precalciner kilns", "operating plants with a precalciner (clinker capacity / existing kilns)"),
            ("kiln_legacy", lambda d: d[d["Clinker production method"].isin(["wet", "semidry"])],
             "Wet and semi-dry kilns", "operating wet or semi-dry plants (clinker capacity / existing kilns)")):
        d = sel(op)
        scope, vals, labs, ca = pick(d, "Country/area", lambda x: list(zip(x["perkiln"], x["GEM plant ID"])))
        proc = f"{label} (GEM GCCT July 2026)"
        o.example(proc, tech, f"{label}: clinker capacity per kiln; Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).",
                  "process-heat-high-temp", "clinker-production", "t")
        o.stat(proc, tech, "capacity", "kt/yr", scope, vals, what,
               REF + ": Clinker capacity (million metric tonnes per annum) / Number of existing kilns",
               canada_note([(v, None) for v, _ in ca], "kt/yr", scope)
               + "Per kiln, clinker. Plants whose precalciner is printed 'unknown' are left out. CAPACITY BASIS: product-output.")
    for tech, ctype, label in (("binder_portland-cement", "opc", "Cement plants making mostly portland cement (OPC)"),
                               ("binder_blended-cement", "blended", "Cement plants making mostly blended cement")):
        d = op[(op["Majority cement type"] == ctype) & op["Plant type"].isin(["integrated", "grinding"])]
        scope, vals, labs, ca = pick(d, "Country/area", lambda x: list(zip(x["ce"], x["GEM plant ID"])))
        proc = f"{label} (GEM GCCT July 2026)"
        o.example(proc, tech, f"{label}: cement capacity per plant (integrated and grinding); Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).",
                  "material-conversion", "cement", "t")
        o.stat(proc, tech, "capacity", "kt/yr", scope, vals, "operating integrated and grinding plants",
               REF + ": Cement capacity (million metric tonnes per annum); Majority cement type " + ctype,
               canada_note([(v, None) for v, _ in ca], "kt/yr", scope) + "Per plant, cement. CAPACITY BASIS: product-output.")
        dd = op[(op["pr"] > 0) & (op["ce"] > 0)].assign(cf=lambda x: 100 * x["pr"] / x["ce"])
        dd = dd[dd["cf"] <= 110]
        s2, v2, l2, ca2 = pick(dd, "Country/area", lambda x: list(zip(x["cf"], x["GEM plant ID"])))
        o.stat(proc, tech, "capacity-factor", "%", s2, v2, "operating plants (2024-2025 cement production / cement capacity)",
               REF + ": 2024-2025 Cement production / Cement capacity",
               canada_note(ca2, "%", s2) + "All cement types together (GEM prints production for few plants). "
               "Ratios above 110% left out.")
    # other values: Canadian kiln technology and fuels
    ca = c[c["Country/area"] == "Canada"]
    o.other.append(["Canadian cement plants (GEM GCCT July 2026)", "kiln_dry-precalciner",
                    "Canadian operating integrated plants: precalciner yes / unknown",
                    f"{((ca['Operating status'] == 'operating') & (ca['Kiln technology - precalciner'] == 'yes')).sum()} / "
                    f"{((ca['Operating status'] == 'operating') & (ca['Kiln technology - precalciner'] == 'unknown')).sum()}",
                    "plants", REF, "Not loaded: kiln-technology mix for the CIMS share calibration (see _canada-stock.csv)."])
    for _, r in ca.iterrows():
        tech = ("kiln_dry-precalciner" if r["Kiln technology - precalciner"] == "yes" else
                "kiln_legacy" if r["Clinker production method"] in ("wet", "semidry") else
                "kiln (precalciner unknown)" if r["Plant type"] in ("integrated", "clinker only") else "")
        det = (f"{r['Plant type']}; {r['Clinker production method']}; preheater {r['Kiln technology - preheater']}; "
               f"precalciner {r['Kiln technology - precalciner']}; WHR {r['Kiln technology - waste heat recovery']}; "
               f"CCS {r['CCS/CCUS']}; alternative fuel {r['Alternative fuel type (for kiln)']}; "
               f"majority cement {r['Majority cement type']}; kilns {r['Number of existing kilns']}")
        o.stock.append([tech, "capacity", r["Plant name (English)"], "clinker", r["Operating status"],
                        str(r["Start date"])[:4], "" if pd.isna(r["cl"]) else fmt(r["cl"]), "kt/yr", "", det, "", "", r["GEM plant ID"]])
        o.stock.append(["binder_portland-cement" if r["Majority cement type"] == "opc" else
                        "binder_blended-cement" if r["Majority cement type"] == "blended" else "",
                        "capacity", r["Plant name (English)"], "cement", r["Operating status"], str(r["Start date"])[:4],
                        "" if pd.isna(r["ce"]) else fmt(r["ce"]), "kt/yr", "", det, "", "", r["GEM plant ID"]])
    shares(o.stock, {"kiln_dry-precalciner": "clinker", "kiln_legacy": "clinker", "kiln (precalciner unknown)": "clinker",
                     "binder_portland-cement": "cement", "binder_blended-cement": "cement"})
    o.write(meta_rows(o, about_text(f, "About"),
        "Global Energy Monitor (2026). Global Cement and Concrete Tracker, July 2026 (V1) release, plant-level data "
        f"(standard copy). https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). One row per cement plant: cement and clinker capacity, "
        "2024-2025 cement production (few plants), kiln count and kiln technology flags. Loaded by gem_extract.py: "
        "clinker capacity per kiln for precalciner and for wet or semi-dry kilns, cement capacity per plant by majority "
        "cement type, and the cement-plant capacity factor. Scope rule: Canada where three or more plants report the "
        "value, else North America, else global (Brad 2026-11-11). Traps: capacities are in million tonnes (x1000 to "
        "kt/yr); clinker capacity is per plant, so it is divided by the number of existing kilns (every Canadian "
        "plant has one); kiln technology is often 'unknown' (11 of 20 Canadian plants for the precalciner), and "
        "those plants are left out of the kiln sizes; GEM prints no production for any Canadian or US plant. The "
        "Canadian roster with shares is in _canada-stock.csv (for calibrating CIMS shares later, not loaded)."))


# --------------------------------------------------------------------------- chemicals
def chemicals():
    f = DOCS / "gem_2026_global-chemicals-tracker.xlsx"
    o = Out("gem_2026_global-chemicals-tracker", "gem_2026_003", "Global Chemicals Tracker, November 2026 (V1)", "chemicals")
    p = pd.read_excel(f, sheet_name="Plant Data")
    c = pd.read_excel(f, sheet_name="Chemical Capacities")
    m = c.merge(p[["GEM Plant ID", "Plant Name (English)", "Country/Area", "Operating Status", "Main Production Equipment",
                   "Feedstock", "Start Date | Year"]], on="GEM Plant ID")
    m["cap"] = num(m["Capacity (ttpa)"])
    m["eqp"] = m["Main Production Equipment"].astype(str)
    m["fst"] = m["Feedstock"].astype(str)
    op = m[is_op(m["Capacity Status"]) & is_op(m["Operating Status"])]
    has = lambda s, k: s.str.contains(k, regex=False)
    REF = "GEM Global Chemicals Tracker, November 2026 (V1): 'Chemical Capacities' tab Capacity (ttpa), joined to 'Plant Data' (Main Production Equipment, Feedstock); capacity and plant status operating"
    cases = [
        ("steam-reformer_ammonia", "ammonia", lambda d: d[has(d.eqp, "steam methane reformer") & has(d.fst, "natural gas")],
         "Natural-gas steam-reforming ammonia plants", "ammonia", "plants (SMR + Haber-Bosch, natural-gas feed)"),
        ("autothermal-reformer_ammonia", "ammonia", lambda d: d[has(d.eqp, "autothermal reformer")],
         "Autothermal-reforming ammonia plants", "ammonia", "plants (ATR + Haber-Bosch)"),
        ("gasifier_coal-ammonia", "ammonia", lambda d: d[has(d.eqp, "gasifier (coal)")],
         "Coal-gasification ammonia plants", "ammonia", "plants (coal gasifier + Haber-Bosch)"),
        ("reactor_haber-bosch-electrolytic", "ammonia", lambda d: d[has(d.eqp, "electrolyzer")],
         "Electrolytic-hydrogen ammonia plants", "ammonia", "plants (electrolyzer + Haber-Bosch)"),
        ("steam-reformer_methanol", "methanol",
         lambda d: d[has(d.eqp, "methanol synthesis") & has(d.fst, "natural gas") & ~has(d.eqp, "gasifier") & ~has(d.eqp, "electrolyzer")],
         "Natural-gas methanol plants", "methanol", "plants (natural-gas feed, methanol synthesis)"),
        ("gasifier_coal-methanol", "methanol", lambda d: d[has(d.eqp, "gasifier (coal)")],
         "Coal-gasification methanol plants", "methanol", "plants (coal gasifier + methanol synthesis)"),
        ("reactor_propane-dehydrogenation", "propylene", lambda d: d[has(d.eqp, "propane dehydrogenation")],
         "Propane dehydrogenation plants", "propylene", "plants (propylene capacity)"),
    ]
    for tech, product, sel, label, pname, what in cases:
        d = sel(op[op["Product"] == product])
        scope, vals, labs, ca = pick(d, "Country/Area", lambda x: list(zip(x["cap"], x["GEM Plant ID"])))
        proc = f"{label} (GEM GCT November 2026)"
        o.example(proc, tech, f"{label}: {pname} capacity per plant; Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).", "material-conversion", pname, "t")
        o.stat(proc, tech, "capacity", "kt/yr", scope, vals, what, REF,
               canada_note([(v, None) for v, _ in ca], "kt/yr", scope)
               + f"Per plant (all trains together), {pname}. CAPACITY BASIS: product-output.")
    # steam crackers: ethylene x the ethane-cracker HVC ratio
    d = op[(op["Product"] == "ethylene") & has(op.eqp, "steam cracker")].copy()
    d["hvc"] = d["cap"] * 1.14
    scope, vals, labs, ca = pick(d, "Country/Area", lambda x: list(zip(x["hvc"], x["GEM Plant ID"])))
    proc = f"Steam crackers (GEM GCT November 2026)"
    o.example(proc, "steam-cracker_fired-tubular", f"Steam crackers: high-value chemicals capacity per plant "
              f"(ethylene capacity x 1.14); Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).", "material-conversion", "high-value chemicals", "t")
    o.stat(proc, "steam-cracker_fired-tubular", "capacity", "kt/yr", scope, vals,
           "plants (ethylene capacity x 1.14 t HVC per t ethylene)", REF + "; product ethylene, equipment steam cracker",
           canada_note([(v, None) for v, _ in ca], "kt/yr", scope)
           + "DERIVED: GEM prints ethylene capacity; times 1.14 t HVC per t ethylene, the ethane-cracker ratio "
           "(cf-hvc-per-ethylene-ethane, Boulamanti and Moya 2017 Table 34), the Canadian fleet's feed (ruling "
           "2026-10-14). Ethylene medians are in _other-values. CAPACITY BASIS: product-output.")
    o.ov("Steam crackers, ethylene as printed (GEM GCT November 2026)", "steam-cracker_fired-tubular",
         f"ethylene capacity per plant, {scope}", [v / 1.14 for v in vals], "kt/yr", REF, "The printed ethylene capacities behind the loaded HVC value.")
    # Canadian stock
    group = {"steam-reformer_ammonia": "ammonia", "autothermal-reformer_ammonia": "ammonia",
             "gasifier_coal-ammonia": "ammonia", "reactor_haber-bosch-electrolytic": "ammonia",
             "steam-reformer_methanol": "methanol", "gasifier_coal-methanol": "methanol",
             "steam-cracker_fired-tubular": "ethylene", "reactor_propane-dehydrogenation": "propylene"}
    for idx, r in m[m["Country/Area"] == "Canada"].iterrows():
        tech = ""
        for t, product, sel, *rest in cases:
            if r["Product"] == product and len(sel(m.loc[[idx]])):
                tech = t
                break
        if r["Product"] == "ethylene" and "steam cracker" in r["eqp"]:
            tech = "steam-cracker_fired-tubular"
        o.stock.append([tech, "capacity", r["Plant Name (English)"], r["Product"], r["Capacity Status"],
                        str(r["Start Date | Year"]), "" if pd.isna(r["cap"]) else fmt(r["cap"]), "kt/yr", "",
                        f"{r['eqp']}; feedstock {r['fst']}; plant status {r['Operating Status']}", "", "", r["GEM Plant ID"]])
    shares(o.stock, group)
    o.write(meta_rows(o, about_text(f, "About"),
        "Global Energy Monitor (2026). Global Chemicals Tracker, November 2026 (V1) release, plant-level data. "
        f"https://globalenergymonitor.org/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). Plants making ammonia, methanol, olefins and aromatics, with "
        "equipment, feedstock and capacity per product. Loaded by gem_extract.py: capacity per plant for the ammonia, "
        "methanol, propane-dehydrogenation and steam-cracker archetypes, classified by GEM's equipment and feedstock "
        "fields. Scope rule: Canada where three or more plants report the value, else North America, else global "
        "(Brad 2026-11-11). Traps: capacity is per plant, not per train (CF Medicine Hat's two trains are one row); "
        "steam crackers print ethylene only, so the HVC capacity is derived with the ethane ratio 1.14; Nutrien "
        "Joffre makes ammonia from by-product hydrogen and Sherritt's equipment is 'other', so neither counts as an "
        "SMR plant; aromatics capacities sit on refinery reformers (no archetype here). Not loaded: aromatics, "
        "butadiene, and refinery propylene. Canadian roster in _canada-stock.csv (for calibrating CIMS shares later)."))


# --------------------------------------------------------------------------- LNG
def trains(name):
    m = re.search(r"T\s*0?(\d+)\s*[-–]\s*T?\s*0?(\d+)", str(name))
    return int(m.group(2)) - int(m.group(1)) + 1 if m and int(m.group(2)) > int(m.group(1)) else 1


def lng():
    f = DOCS / "gem_2026_global-gas-infrastructure-tracker_lng-terminals.xlsx"
    o = Out("gem_2026_global-gas-infrastructure-tracker_lng-terminals", "gem_2026_004",
            "Global Gas Infrastructure Tracker: LNG Terminals, October 2026", "oil-and-gas")
    l = pd.read_excel(f, sheet_name="LNG Terminals")
    l["cap"] = num(l["CapacityinMtpa"])
    l["n"] = l["UnitName"].apply(trains)
    l["per"] = l["cap"] * 1000 / l["n"]
    l["float"] = num(l["Floating"]).fillna(0) == 1
    e = l[(l["FacilityType"] == "export") & (l["Status"] == "operating")
          & ~l["UnitName"].astype(str).str.contains("ebottleneck", na=False)]
    REF = "GEM Global Gas Infrastructure Tracker, LNG Terminals, October 2026, 'LNG Terminals' tab: CapacityinMtpa / trains named in UnitName; FacilityType export, Status operating"
    for tech, sel, label, what in (
            ("liquefaction-train_base-load", lambda d: d[~d["float"] & (d["per"] >= 500)], "Onshore LNG trains of 0.5 Mt/yr or more", "operating onshore export units (capacity per train)"),
            ("liquefaction-train_small-scale", lambda d: d[~d["float"] & (d["per"] < 500)], "Onshore LNG trains under 0.5 Mt/yr", "operating onshore export units (capacity per train)"),
            ("liquefaction-train_floating", lambda d: d[d["float"]], "Floating LNG units", "operating floating export units (capacity per unit)")):
        d = sel(e)
        scope, vals, labs, ca = pick(d, "Country/Area", lambda x: list(zip(x["per"], x["UnitID"])))
        proc = f"{label} (GEM GGIT LNG October 2026)"
        o.example(proc, tech, f"{label}: liquefaction capacity per train of operating export terminals; Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).",
                  "natural-gas liquefaction", "liquefaction", "t")
        o.stat(proc, tech, "capacity", "kt/yr", scope, vals, what, REF,
               canada_note([(v, None) for v, _ in ca], "kt/yr", scope)
               + "Per train: a unit printed as a range of trains (T1-T2, T1-T18) is divided by the number of trains; "
               "one median over units, so a modular terminal counts once per unit row. CAPACITY BASIS: product-output.")
    cost = l[(l["FacilityType"] == "export") & l["Status"].isin(["operating", "construction"]) & (num(l["CostUSD"]) > 0) & (l["cap"] > 0)]
    for scope, cs in SCOPES:
        d = cost[in_scope(cost["Country/Area"], cs)]
        o.ov(f"LNG export units with a cost, {scope} (GEM GGIT LNG October 2026)", "liquefaction-train_base-load",
             "unit cost per t of annual capacity (operating and construction)", list(num(d["CostUSD"]) / (d["cap"] * 1e6)),
             "USD/t-per-yr", "GEM GGIT LNG October 2026: CostUSD / CapacityinMtpa",
             "Not loaded: nominal USD, cost year not stated; terminal scope varies (storage, berths, trains).")
    for _, r in l[l["Country/Area"] == "Canada"].iterrows():
        tech = ("" if r["FacilityType"] != "export" else "liquefaction-train_floating" if r["float"] else
                "liquefaction-train_base-load" if r["per"] >= 500 else "liquefaction-train_small-scale")
        o.stock.append([tech, "capacity", r["TerminalName"], r["UnitName"] if pd.notna(r["UnitName"]) else "", r["Status"],
                        "" if pd.isna(r["ActualStartYear"]) else str(int(r["ActualStartYear"])),
                        "" if pd.isna(r["cap"]) else fmt(r["cap"] * 1000), "kt/yr", "",
                        f"{r['FacilityType']}; trains {r['n']}; cost USD {'' if pd.isna(num(pd.Series([r['CostUSD']]))[0]) else fmt(num(pd.Series([r['CostUSD']]))[0])}",
                        "", "", r["UnitID"]])
    shares(o.stock, {"liquefaction-train_base-load": "lng", "liquefaction-train_small-scale": "lng", "liquefaction-train_floating": "lng"})
    o.write(meta_rows(o, about_text(f, "About GGIT LNG"),
        "Global Energy Monitor (2026). Global Gas Infrastructure Tracker: LNG Terminals, October 2026 release. "
        f"https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). One row per terminal unit (phase or train), import and export. "
        "Loaded by gem_extract.py: liquefaction capacity per train of operating export units, split into base-load "
        "(0.5 Mt/yr or more per train), small-scale (under 0.5) and floating. Scope rule: Canada where three or more "
        "units, else North America, else global (Brad 2026-11-11). Traps: a unit is often a phase of several trains "
        "(LNG Canada 'Phase 1 (T1-T2)' 14 Mt/yr, Calcasieu Pass 'T1-T18'), divided by the trains in its name; "
        "debottlenecking rows are left out. Costs to _other-values (cost year not stated). Canadian roster in "
        "_canada-stock.csv."))


# --------------------------------------------------------------------------- pipelines
def pipelines(kind):
    if kind == "gas":
        f = DOCS / "gem_2025_global-gas-infrastructure-tracker_gas-pipelines.xlsx"
        o = Out("gem_2025_global-gas-infrastructure-tracker_gas-pipelines", "gem_2025_001",
                "Global Gas Infrastructure Tracker: Gas Pipelines, November 2025", "oil-and-gas")
        d = pd.read_excel(f, sheet_name="Pipelines")
        d["thr"] = num(d["CapacityBcm/y"]) * 1e6          # 1000-m3/yr
        tech, unit, label, cname, sheet = "pipeline_natural-gas", "1000-m3/yr", "Gas transmission pipelines", "CapacityBcm/y x 1e6", "Pipelines"
        about = " ".join(str(x) for x in pd.read_excel(f, sheet_name="Copyright", header=None).fillna("").values.ravel() if str(x).strip())
        url = "https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/"
        cite = "Global Energy Monitor (2025). Global Gas Infrastructure Tracker: Gas Pipelines, November 2025 release."
    else:
        f = DOCS / "gem_2026_global-oil-infrastructure-tracker_oil-ngl-pipelines.xlsx"
        o = Out("gem_2026_global-oil-infrastructure-tracker_oil-ngl-pipelines", "gem_2026_005",
                "Global Oil Infrastructure Tracker: Oil and NGL Pipelines, June 2026", "oil-and-gas")
        d = pd.read_excel(f, sheet_name="Data")
        d = d[d["Fuel"] == "Oil"].copy()
        d["thr"] = num(d["CapacityBOEd"]) * BBL_M3 * 365    # m3/yr
        tech, unit, label, cname, sheet = "pipeline_crude-oil", "m3/yr", "Crude oil pipelines", "CapacityBOEd x 0.158987 x 365", "Data"
        about = " ".join(str(x) for x in pd.read_excel(f, sheet_name="Copyright", header=None).fillna("").values.ravel() if str(x).strip())
        url = "https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/"
        cite = "Global Energy Monitor (2026). Global Oil Infrastructure Tracker: Oil and NGL Pipelines, June 2026 release."
    d["L"] = num(d["LengthMergedKm"])
    d["cost"] = num(d["CostUSD"])
    op = d[(d["Status"] == "operating") & (d["L"] >= 100)]
    scope, vals, labs, ca = pick(op, "CountriesOrAreas", lambda x: list(zip(x["thr"], x["ProjectID"])))
    proc = f"{label} of 100 km or more (GEM {'GGIT' if kind == 'gas' else 'GOIT'})"
    o.example(proc, tech, f"{label}: throughput capacity per pipeline or segment of 100 km or more; Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).",
              "transmission", "pipeline", unit.split("/")[0])
    o.stat(proc, tech, "capacity", unit, scope, vals, "operating pipelines or segments of 100 km or more",
           f"GEM, '{sheet}' tab: {cname}; Status operating, LengthMergedKm 100 or more; cross-border pipelines count for each country",
           canada_note([(v, None) for v, _ in ca], unit, scope)
           + "Throughput capacity of the line (the archetype's size per 1000 km of pipe; length in _other-values). "
           "Segments under 100 km (loops, laterals and expansions) are left out. CAPACITY BASIS: product-output.")
    lp = op[in_scope(op["CountriesOrAreas"], CANADA if scope == "Canada" else NORTH_AMERICA if scope.startswith("North") else None)]
    o.ov(proc, tech, "length per pipeline or segment (same set)", [v for v in lp["L"] if v > 0], "km",
         "GEM: LengthMergedKm", "Not loaded.")
    cst = d[d["Status"].isin(["operating", "construction"]) & (d["cost"] > 0) & (d["L"] > 0)]
    for s, cs in SCOPES:
        x = cst[in_scope(cst["CountriesOrAreas"], cs)]
        o.ov(f"{label} with a cost, {s}", tech, "project cost per km (operating and construction)",
             list(x["cost"] / x["L"]), "USD/km", "GEM: CostUSD / LengthMergedKm",
             "Not loaded: nominal USD, cost year not stated; project scope varies (compression, laterals).")
        x = x[x["thr"] > 0]
        o.ov(f"{label} with a cost, {s}", tech, f"project cost per unit of throughput capacity per 1000 km",
             list(x["cost"] / (x["thr"] * x["L"] / 1000)), f"USD/{unit.split('/')[0]}-per-yr per 1000 km",
             f"GEM: CostUSD / ({cname} x LengthMergedKm / 1000)", "Not loaded: nominal USD, cost year not stated.")
    for _, r in d[in_scope(d["CountriesOrAreas"], CANADA)].iterrows():
        o.stock.append([tech, "capacity", r["PipelineName"], r["SegmentName"] if pd.notna(r["SegmentName"]) else "",
                        r["Status"], str(r["StartYear1"]) if pd.notna(r["StartYear1"]) else "",
                        "" if pd.isna(r["thr"]) else fmt(r["thr"]), unit, "",
                        f"length {'' if pd.isna(r['L']) else fmt(r['L'])} km; countries {r['CountriesOrAreas']}; "
                        f"cost USD {'' if pd.isna(r['cost']) else fmt(r['cost'])}", "", "", r["ProjectID"]])
    o.write(meta_rows(o, about, f"{cite} {url} (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). One row per pipeline or segment. Loaded by gem_extract.py: the "
        "throughput capacity of operating lines of 100 km or more. Scope rule: Canada where three or more lines, else "
        "North America, else global (Brad 2026-11-11). The archetype is per unit of product moved 1000 km, so the "
        "capacity is the line's throughput; lengths and costs are in _other-values (costs not loaded: cost year not "
        "stated). Traps: rows mix whole systems (NGTL, 24,500 km) with short loops and expansions, hence the 100 km "
        "floor; cross-border lines list several countries; some rows print length 0." +
        (" Oil rows only (NGL pipelines left out); capacity converted from barrels of oil equivalent per day." if kind == "oil" else "")
        + " Canadian roster in _canada-stock.csv."))


# --------------------------------------------------------------------------- coal mines
def coal():
    f = DOCS / "gem_2026_global-coal-mine-tracker.xlsx"
    o = Out("gem_2026_global-coal-mine-tracker", "gem_2026_006", "Global Coal Mine Tracker, August 2026", "mining")
    m = pd.read_excel(f, sheet_name="Non-closed mines")
    h = pd.read_excel(f, sheet_name="Historic Production (2018-2025)")
    out = {y: dict(zip(h["GEM Mine ID"], num(h[f"Coal Output (Annual, Mt) {y}"]))) for y in range(2018, 2026)}
    m["cap"] = num(m["Capacity (Mtpa)"]) * 1000                     # kt/yr
    m["o24"] = m["GEM Mine ID"].map(out[2024]) * 1e6                # t/yr
    m["cmm"] = num(m["Reported Coal Mine Methane Emissions (thousand tonnes CH4)"]) * 1000   # t CH4/yr
    m["cmmy"] = num(m["Year of Reported Coal Mine Methane Emissions"])
    m["ocmm"] = [out.get(int(y), {}).get(i) if pd.notna(y) and 2018 <= y <= 2025 else None for i, y in zip(m["GEM Mine ID"], m["cmmy"])]
    m["ocmm"] = num(m["ocmm"]) * 1e6
    op = m[m["Status"] == "Operating"]
    REF = "GEM Global Coal Mine Tracker, August 2026, 'Non-closed mines' tab (Status Operating, Mine Type {t})"
    for tech, mt, label in (("mine_open-pit-coal", "Surface", "Surface coal mines"),
                            ("mine_underground-coal", "Underground", "Underground coal mines")):
        d = op[op["Mine Type"] == mt].copy()
        ref = REF.format(t=mt)
        s0, v0, l0, c0 = pick(d, "Country / Area", lambda x: list(zip(x["o24"], x["GEM Mine ID"])))
        proc = f"{label} (GEM GCMT August 2026)"
        o.example(proc, tech, f"{label}: 2024 coal output and reported coal-mine methane per mine of operating mines; Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).",
                  "coal mining", "mine", "t")
        if tech == "mine_open-pit-coal":
            o.stat(proc, tech, "annual-output", "t/yr", s0, v0, "operating mines (2024 output)",
                   ref + "; 'Historic Production (2018-2025)' tab: Coal Output (Annual, Mt) 2024",
                   canada_note([(v / 1e6 if v else v, None) for v, _ in c0], "Mt/yr", s0) + "Run-of-mine or saleable output as GEM prints it. CAPACITY BASIS: product-output.")
        else:
            # Brad 2026-11-12: underground sizes from Canadian mines only. No Canadian underground
            # mine operates, so the size is the stated capacity of the Canadian mothballed and
            # proposed underground mines (Donkin, and the Alberta and BC projects).
            cu = m[(m["Country / Area"] == "Canada") & (m["Mine Type"] == "Underground")
                   & m["Status"].isin(["Operating", "Mothballed", "Proposed"]) & (m["cap"] > 0)]
            vals = list(cu["cap"])
            o.stat(proc, tech, "capacity", "kt/yr", "Canada (mothballed and proposed mines; none operates)", vals,
                   "Canadian underground mines with a stated capacity",
                   "GEM Global Coal Mine Tracker, August 2026, 'Non-closed mines' tab: Capacity (Mtpa); Country Canada, "
                   "Mine Type Underground, Status Operating, Mothballed or Proposed",
                   "Brad 2026-11-12: underground mine size from Canadian mines only. No Canadian underground mine "
                   "operates (Donkin, Nova Scotia, is mothballed; Quinsam closed in 2019), so the size is the stated "
                   "capacity of the mothballed and proposed mines: " + ", ".join(f"{r['Mine Name']} {fmt(r['cap'])}"
                   for _, r in cu.iterrows()) + " kt/yr. CAPACITY BASIS: product-output.")
            o.ov(proc, tech, f"2024 output per operating underground mine, {s0}", v0, "t/yr",
                 ref + "; 'Historic Production (2018-2025)' tab: Coal Output (Annual, Mt) 2024",
                 "Not loaded (Brad 2026-11-12): the North American median is pulled down by many small US mines; "
                 "the size comes from the Canadian mines' stated capacity instead.")
        # capacity and capacity factor are kept, not loaded: GEM often prints a capacity equal to the
        # latest output (surface mines: CF 100%), and outside Canada mostly the large mines report one
        s1, v1, l1, c1 = pick(d, "Country / Area", lambda x: list(zip(x["cap"], x["GEM Mine ID"])))
        nscope = in_scope(d["Country / Area"], dict(SCOPES)[s1]).sum()
        o.ov(proc, tech, f"capacity per mine, {s1} ({len(v1)} of {nscope} operating mines report one)", v1, "kt/yr",
             ref + ": Capacity (Mtpa)", "Not loaded: GEM often prints a capacity equal to the latest output, and "
             "where few mines report one they are the large ones; the build takes capacity from the output and "
             "the capacity factor.")
        # Chinese mines' output is GEM's imputed capacity x 72.8% (README), not a production figure
        d = d[d["Country / Area"] != "China"]
        dd = d[(d["cap"] > 0) & (d["o24"] > 0)].assign(cf=lambda x: 100 * x["o24"] / (x["cap"] * 1000))
        dd = dd[dd["cf"] <= 110]
        s2, v2, l2, c2 = pick(dd, "Country / Area", lambda x: list(zip(x["cf"], x["GEM Mine ID"])))
        o.ov(proc, tech, f"2024 output / capacity per mine, {s2} (Chinese mines left out)", v2, "%",
             ref + ": Coal Output 2024 / Capacity (Mtpa)", "Not loaded, for the same reason as the capacity.")
        dd = d[(d["cmm"] > 0) & (d["ocmm"] > 0)].assign(ef=lambda x: 1000 * x["cmm"] / x["ocmm"])
        s3, v3, l3, c3 = pick(dd, "Country / Area", lambda x: list(zip(x["ef"], x["GEM Mine ID"])))
        o.stat(proc, tech, "emissions-process", "kg/t", s3, v3,
               "operating mines (reported methane / coal output of the same year)",
               ref + ": Reported Coal Mine Methane Emissions (thousand tonnes CH4) / Coal Output of the reported year",
               canada_note(c3, "kg/t", s3) + "Reported by an official source or the company (GEM README), not GEM's "
               "model estimate (that is in _other-values).", target="ch4")
        est = [1000 * v * 1e6 / (o24) for v, o24 in zip(num(d["GEM Coal Mine Methane Emissions Estimate (M tonnes/yr)"]), d["o24"])
               if pd.notna(v) and v > 0 and o24 > 0]
        o.ov(proc, tech, "GEM model (MC2M) methane estimate per t of 2024 output, all operating mines of this type outside China", est, "kg/t",
             "GEM GCMT: GEM Coal Mine Methane Emissions Estimate (M tonnes/yr) / Coal Output 2024",
             "Not loaded: GEM's own model estimate (gas content x output), not a measurement or a report.")
        if tech == "mine_underground-coal":
            for t2, lab2 in (("process-improvement_coal-mine-methane-drainage", "Coal-mine methane drainage"),
                             ("gas-treatment-unit_vam-oxidiser", "Ventilation-air methane oxidation")):
                dd = d[d["cmm"] > 0]
                s4, v4, l4, c4 = pick(dd, "Country / Area", lambda x: list(zip(x["cmm"], x["GEM Mine ID"])))
                p2 = f"{lab2}: methane per underground mine (GEM GCMT August 2026)"
                o.example(p2, t2, f"{lab2}: the coal-mine methane an operating underground mine releases per year (the "
                          f"tonnes the methane control is asked to handle); Canadian facilities where three or more report a value, else North America or global (the scope is in each value's formula).", "coal-mine methane", "methane control", "t")
                o.stat(p2, t2, "annual-output", "t/yr", s4, v4, "operating underground mines reporting methane",
                       ref + ": Reported Coal Mine Methane Emissions (thousand tonnes CH4) x 1000",
                       canada_note(c4, "t/yr", s4) + "Whole-mine methane (ventilation air and drained gas together, as "
                       "reported); the size of the methane-control installation at a typical mine. CAPACITY BASIS: product-output.")
    for _, r in m[m["Country / Area"] == "Canada"].iterrows():
        tech = {"Surface": "mine_open-pit-coal", "Underground": "mine_underground-coal"}.get(r["Mine Type"], "")
        det = f"{r['Mine Type']}; {r['Coal Type']}; met {r['Percentage of Met Coal']}; {r['State, Province']}; reported CH4 {'' if pd.isna(r['cmm']) else fmt(r['cmm'])} t ({'' if pd.isna(r['cmmy']) else int(r['cmmy'])})"
        o.stock.append([tech, "capacity", r["Mine Name"], "", r["Status"], "" if pd.isna(num(pd.Series([r["Opening Year"]]))[0]) else str(r["Opening Year"])[:4],
                        "" if pd.isna(r["cap"]) else fmt(r["cap"]), "kt/yr", "", det, "", "", r["GEM Mine ID"]])
        for y in range(2018, 2026):
            v = out[y].get(r["GEM Mine ID"])
            if v is not None and pd.notna(v) and v > 0:
                o.stock.append([tech, "production", r["Mine Name"], "", r["Status"], "", fmt(v * 1000), "kt/yr", str(y), "", "", "", r["GEM Mine ID"]])
    shares(o.stock, {"mine_open-pit-coal": "coal", "mine_underground-coal": "coal"})
    o.write(meta_rows(o, about_text(f, "README"),
        "Global Energy Monitor (2026). Global Coal Mine Tracker, August 2026 release. "
        f"https://globalenergymonitor.org/projects/global-coal-mine-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). One row per mine: capacity, output 2017-2025, mine type, coal "
        "type, reported and modelled coal-mine methane. Loaded by gem_extract.py: for surface and underground mines, the "
        "2024 output, capacity, capacity factor and reported methane per t of coal; for the coal-mine methane controls "
        "(drainage, VAM oxidation), the reported methane per underground mine. Scope rule: Canada where three or more "
        "mines, else North America, else global (Brad 2026-11-11): every operating Canadian mine is a surface mine, so "
        "the underground values are North American (US mines; their reported methane is the US EPA GHGRP). Traps: the "
        "supplement workbooks of 2024 (in gem-data.zip) are superseded by this release; the Mine Type 'Underground & "
        "Surface' rows are left out; the reported methane year (mostly 2024) is matched to the output of that year; "
        "GEM's MC2M model estimates are kept in _other-values only. Canadian roster in _canada-stock.csv."))


# --------------------------------------------------------------------------- held, not loaded
def stock_only():
    # oil and gas plants: Canadian captive industrial and CHP units
    f = DOCS / "gem_2026_global-oil-and-gas-plant-tracker.xlsx"
    o = Out("gem_2026_global-oil-and-gas-plant-tracker", "gem_2026_007", "Global Oil and Gas Plant Tracker, August 2026", "heat-supply")
    for sheet in ("Gas & Oil Units", "Sub-Threshold Units"):
        g = pd.read_excel(f, sheet_name=sheet)
        g = g[(g["Country/Area"] == "Canada") & (g["CHP"].astype(str).str.lower().eq("yes") | g["Captive industry use"].notna())]
        for _, r in g.iterrows():
            tech = "combustion-turbine_chp" if str(r["CHP"]).lower() == "yes" else ""
            o.stock.append([tech, "capacity", r["Plant name"], r["Unit name"] if pd.notna(r["Unit name"]) else "", r["Status"],
                            "" if pd.isna(r["Start year"]) else str(r["Start year"])[:4],
                            "" if pd.isna(num(pd.Series([r["Capacity (MW)"]]))[0]) else fmt(num(pd.Series([r["Capacity (MW)"]]))[0]), "MW", "",
                            f"{sheet}; {r['Fuel']}; {r['Turbine/Engine Technology']}; CHP {r['CHP']}; captive {r['Captive industry use']} "
                            f"{r['Captive industry type'] if pd.notna(r['Captive industry type']) else ''}; {r['State/Province']}",
                            "", "", r["GEM unit ID"]])
    o.write(meta_rows(o, about_text(f, "About"),
        "Global Energy Monitor (2026). Global Oil and Gas Plant Tracker (GOGPT), August 2026 release. "
        f"https://globalenergymonitor.org/projects/global-oil-and-gas-plant-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). Oil and gas power units worldwide, with CHP and captive-industry "
        "flags. NOT LOADED: the database's CHP archetypes are per GJ of heat and GEM gives electric MW only. Kept for "
        "calibrating CIMS shares later: _canada-stock.csv lists the Canadian CHP and captive-industry units."))
    # coal plants: Canadian captive and CHP units
    f = DOCS / "gem_2026_global-coal-plant-tracker.xlsx"
    o = Out("gem_2026_global-coal-plant-tracker", "gem_2026_008", "Global Coal Plant Tracker, July 2026", "heat-supply")
    g = pd.read_excel(f, sheet_name="Units")
    g = g[g["Country/Area"] == "Canada"]
    for _, r in g.iterrows():
        cap_ind = str(r.get("Captive", "")).lower() == "yes" or str(r.get("CHP", "")).lower() == "yes"
        o.stock.append(["steam-turbine_back-pressure" if str(r.get("CHP", "")).lower() == "yes" else
                        "steam-turbine_condensing" if cap_ind else "", "capacity", r["Plant name"],
                        r["Unit name"] if pd.notna(r["Unit name"]) else "", r["Status"],
                        "" if pd.isna(r["Start year"]) else str(r["Start year"])[:4], fmt(num(pd.Series([r["Capacity (MW)"]]))[0]),
                        "MW", "", f"{r['Combustion technology']}; {r['Coal type']}; captive {r['Captive']} {r['Captive industry use'] if pd.notna(r['Captive industry use']) else ''}; CHP {r['CHP']}; "
                        f"retired {r['Retired year'] if pd.notna(r['Retired year']) else ''}; {r['Subnational unit (province, state)']}",
                        "", "", r["GEM unit/phase ID"]])
    o.write(meta_rows(o, about_text(f, "About"),
        "Global Energy Monitor (2026). Global Coal Plant Tracker, July 2026 release. "
        f"https://globalenergymonitor.org/projects/global-coal-plant-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). Coal power units of 30 MW and more worldwide. NOT LOADED: utility "
        "power is outside the industrial database, and GEM's heat rate, emission factor and capacity factor are its own "
        "assignments by combustion technology, coal type and country (About sheet), not plant data. Kept for calibrating "
        "CIMS shares later: _canada-stock.csv lists every Canadian unit (all utility units; CHP and captive flags kept)."))
    # methane emitters: Canadian satellite plumes
    f = DOCS / "gem_2025_global-methane-emitters-tracker.xlsx"
    o = Out("gem_2025_global-methane-emitters-tracker", "gem_2025_002", "Global Methane Emitters Tracker, December 2025", "oil-and-gas")
    pl = pd.read_excel(f, sheet_name="Plumes")
    pl = pl[pl["Country/Area"] == "Canada"]
    for _, r in pl.iterrows():
        o.stock.append(["", "plume", r["GEM Infrastructure Name (Nearby)"] if pd.notna(r["GEM Infrastructure Name (Nearby)"]) else r["Name"],
                        "", "", "", "" if pd.isna(num(pd.Series([r["Emissions (kg/hr)"]]))[0]) else fmt(num(pd.Series([r["Emissions (kg/hr)"]]))[0]),
                        "kg/h", str(r["Observation Date"])[:10],
                        f"{r['Type of Infrastructure']}; {r['Instrument']}; {r['Subnational Unit']}; uncertainty {r['Emissions Uncertainty (kg/hr)']} kg/h",
                        "", "", r["GEM Methane Plume ID"]])
    o.write(meta_rows(o, about_text(f, "About"),
        "Global Energy Monitor (2025). Global Methane Emitters Tracker, December 2025 (V3) release. "
        f"https://globalenergymonitor.org/projects/global-methane-emitters-tracker/ (accessed {ACCESSED}).",
        "HELD LOCALLY since 2026-11-11 (gem-data.zip). Methane estimates for pipelines, LNG terminals, coal mines and oil "
        "and gas extraction areas, and satellite methane plumes. NOT LOADED: the asset estimates are emission factors "
        "times throughput (GEM, Climate TRACE and OCI+ models), not measurements of a technology, and the coal-mine "
        "methane comes in reported form from the Global Coal Mine Tracker (gem_2026_006); plumes are single "
        "detections in kg/h, not annual site emissions. Kept for calibrating CIMS methane later: _canada-stock.csv "
        "lists the Canadian plume detections with the infrastructure type."))


TRACKERS = {"steel": steel, "cement": cement, "chemicals": chemicals, "lng": lng,
            "gas-pipelines": lambda: pipelines("gas"), "oil-pipelines": lambda: pipelines("oil"),
            "coal": coal, "stock": stock_only}

if __name__ == "__main__":
    for k in (sys.argv[1:] or TRACKERS):
        TRACKERS[k]()
