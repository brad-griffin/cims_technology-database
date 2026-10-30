"""Worked example for cims/reporting-accounting/reporting-accounting.md: 100 GJ of coal through an
integrated BF-BOF steel plant, recorded as a flow ledger and then reported under
several accounting conventions, each defined by a config in cims/reporting-accounting/configs/.

Run from the repo root:  python cims/reporting-accounting/accounting_example.py [--ledger out.csv]

The ledger is what the note proposes CIMS should record after each year's
equilibrium: every flow in or out of a process (a node/tech), with its energy and
carbon, and every emission, tagged with the fuel the carbon came from and the
processes it passed through. The configs never change the ledger; they only decide
which rows and categories each flow lands in.

Quantities are illustrative. Emission factors are IPCC 2006 defaults (kg CO2/GJ)
except coal tar, which is an assumption. Exits 1 if any balance check fails.
"""
import argparse, csv, sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = Path(__file__).resolve().parent / "configs"

# ---------------------------------------------------------------- assumptions
EF = {  # kg CO2 per GJ (carbon content, expressed as CO2)
    "coal-metallurgical": 94.6, "coke": 107.0, "coke-oven-gas": 44.4,
    "blast-furnace-gas": 260.0, "bof-gas": 182.0, "natural-gas": 56.1,
    "coal-tar": 90.0,  # assumption
}
CO2_PER_C = 44 / 12
P = {
    "coal_to_ovens": 80.0,     # GJ coal charged to the coke ovens
    "coal_pci": 20.0,          # GJ coal injected in the blast furnace
    "coke": 57.6,              # GJ coke out of the ovens
    "cog_gross": 17.6,         # GJ coke oven gas produced
    "oven_underfiring": 6.4,   # GJ process gas burned to heat the ovens
    "tar": 3.2,                # GJ coal tar and light oil (non-energy product)
    "hot_metal_t": 5.76,       # t hot metal
    "hot_metal_c": 0.045,      # carbon mass fraction in hot metal
    "stoves": 10.0,            # GJ process gas burned in the hot-blast stoves
    "steel_t": 6.4,            # t liquid steel (hot metal + scrap)
    "steel_c": 0.001,          # carbon mass fraction in steel
    "bof_gas": 5.0,            # GJ BOF gas recovered
    "reheating": 25.0,         # GJ process gas burned in reheating furnaces
    "cogen_fuel": 15.0,        # GJ process gas burned in the cogeneration unit
    "cogen_heat": 8.25,        # GJ useful steam it delivers to the plant
    "cogen_power": 3.75,       # GJ electricity it generates (a by-product)
}


def co2(commodity, gj):
    return gj * EF[commodity] / 1000.0


# ---------------------------------------------------------------- the ledger
class Ledger:
    """flows: dicts with process, commodity, direction (in/out), role, qty, unit,
    co2, parcels, self_supplied.  role: purchase, fuel, feed, material (in);
    product, byproduct, stored (out).  parcels: {(primary fuel, path): t CO2}.
    emissions: dicts with process, kind and parcels. kind is 'combustion' (fuel burned
    for heat, including a process's own by-product gas) or 'process' (carbon lost any
    other way: reduction, leaks, quenching)."""

    def __init__(self):
        self.flows, self.emissions = [], []

    def add(self, **f):
        f.setdefault("unit", "GJ"); f.setdefault("self_supplied", False)
        f.setdefault("parcels", {}); f.setdefault("co2", sum(f["parcels"].values()))
        self.flows.append(f)
        return f


def _tag(parcels, process):
    out = defaultdict(float)
    for (primary, path), v in parcels.items():
        out[(primary, path if path[-1:] == (process,) else path + (process,))] += v
    return dict(out)


def _scale(parcels, k):
    return {key: v * k for key, v in parcels.items()}


def run_process(ledger, name, inputs, outputs, kind="process"):
    """inputs: flow dicts already carrying parcels (recorded here as 'in').
    Inputs with role 'fuel' are burned here: all their carbon is emitted as
    'combustion'. The other inputs (feed, material, blend components) are mixed, and
    outputs: (commodity, role, qty, unit, co2) draw their carbon pro rata from that
    mix; carbon left in the mix is emitted here as `kind` (reduction, leaks, quenching)."""
    mix, burned = defaultdict(float), defaultdict(float)
    for f in inputs:
        ledger.add(process=name, direction="in", **{k: v for k, v in f.items() if k != "process"})
        # A parcel's path lists the processes its carbon passed through; carbon burned
        # here did not pass through, so the burner is not added (it is `emitted_at`).
        if f["role"] == "fuel":
            for key, v in f["parcels"].items():
                burned[key] += v
        else:
            for key, v in _tag(f["parcels"], name).items():
                mix[key] += v
    total = sum(mix.values())
    out_c = sum(o[4] for o in outputs)
    if out_c > total + 1e-9:
        raise ValueError(f"{name}: outputs carry more carbon than the non-fuel inputs")
    outs = {}
    for commodity, role, qty, unit, c in outputs:
        outs[commodity] = ledger.add(process=name, commodity=commodity, direction="out", role=role,
                                     qty=qty, unit=unit, parcels=_scale(mix, c / total) if total else {})
    if burned:
        ledger.emissions.append({"process": name, "kind": "combustion", "parcels": dict(burned)})
    if total - out_c > 1e-12:
        ledger.emissions.append({"process": name, "kind": kind, "parcels": _scale(mix, (total - out_c) / total)})
    return outs


def purchase(commodity, gj, role="fuel"):
    return {"commodity": commodity, "role": role, "qty": gj, "purchased": True,
            "parcels": {(commodity, ()): co2(commodity, gj)}}


def take(flow, qty, role="fuel"):
    """Part of an upstream output flow, as an input to the next process."""
    k = qty / flow["qty"]
    return {"commodity": flow["commodity"], "role": role, "qty": qty, "unit": flow["unit"],
            "parcels": _scale(flow["parcels"], k)}


def build_ledger(p=P):
    """By-products go to their own carrier nodes (COG, BFG, BOF gas); every burner,
    including the ovens' underfiring and the blast furnace's stoves, draws fuel from
    the process-gas pool (option 1 in the design note, adopted 2026-09-21)."""
    L = Ledger()
    # Coke ovens: coal charged; coke, COG and tar out; the rest of the coal carbon is lost
    # (leaks, pushing, quenching). Underfiring fuel is added below, from the pool.
    ov = run_process(L, "coke-ovens",
                     [purchase("coal-metallurgical", p["coal_to_ovens"], role="feed")],
                     [("coke", "product", p["coke"], "GJ", co2("coke", p["coke"])),
                      ("coke-oven-gas", "byproduct", p["cog_gross"], "GJ", co2("coke-oven-gas", p["cog_gross"])),
                      ("coal-tar", "stored", p["tar"], "GJ", co2("coal-tar", p["tar"]))])
    # Blast furnace: coke and injected coal are the reductants; hot metal and BFG out.
    bf_in = co2("coke", p["coke"]) + co2("coal-metallurgical", p["coal_pci"])
    hm_c = p["hot_metal_t"] * p["hot_metal_c"] * CO2_PER_C
    bfg = (bf_in - hm_c) / EF["blast-furnace-gas"] * 1000
    bf = run_process(L, "blast-furnace",
                     [take(ov["coke"], p["coke"], role="feed"),
                      purchase("coal-metallurgical", p["coal_pci"], role="feed")],
                     [("hot-metal", "product", p["hot_metal_t"], "t", hm_c),
                      ("blast-furnace-gas", "byproduct", bfg, "GJ", bf_in - hm_c)])
    # BOF: hot metal in; steel and BOF gas out.
    st_c = p["steel_t"] * p["steel_c"] * CO2_PER_C
    bof = run_process(L, "bof", [take(bf["hot-metal"], p["hot_metal_t"], role="material")],
                      [("steel", "stored", p["steel_t"], "t", st_c),
                       ("bof-gas", "byproduct", p["bof_gas"], "GJ", co2("bof-gas", p["bof_gas"]))])
    # Process-gas pool: all the by-product gas, topped up with natural gas; no emissions.
    demand = p["oven_underfiring"] + p["stoves"] + p["reheating"] + p["cogen_fuel"]
    ng = demand - p["cog_gross"] - bfg - p["bof_gas"]
    pool_in = [take(ov["coke-oven-gas"], p["cog_gross"], role="blend"),
               take(bf["blast-furnace-gas"], bfg, role="blend"),
               take(bof["bof-gas"], p["bof_gas"], role="blend"),
               purchase("natural-gas", ng, role="blend")]
    pg = run_process(L, "process-gas", pool_in,
                     [("process-gas", "product", demand, "GJ", sum(sum(f["parcels"].values()) for f in pool_in))])
    gas = pg["process-gas"]
    # Burners.
    run_process(L, "coke-ovens", [take(gas, p["oven_underfiring"])], [])
    run_process(L, "blast-furnace", [take(gas, p["stoves"])], [])
    run_process(L, "reheating", [take(gas, p["reheating"])], [])
    # Cogeneration: steam for the plant is the main output, electricity a by-product
    # (a negative request to the electricity node in CIMS). No carbon leaves in them.
    run_process(L, "steam-cogen", [take(gas, p["cogen_fuel"])],
                [("steam", "product", p["cogen_heat"], "GJ", 0.0),
                 ("electricity", "byproduct", p["cogen_power"], "GJ", 0.0)])
    return L


# ---------------------------------------------------------------- reports
def load(name):
    return yaml.safe_load((CONFIGS / f"{name}.yaml").read_text(encoding="utf-8"))


def _composition(ledger, commodity):
    """Energy shares of the inputs of the process that makes `commodity` (for expansion)."""
    maker = next(f["process"] for f in ledger.flows
                 if f["direction"] == "out" and f["commodity"] == commodity)
    ins = [f for f in ledger.flows if f["process"] == maker and f["direction"] == "in"]
    tot = sum(f["qty"] for f in ins)
    shares = defaultdict(float)
    for f in ins:
        shares[f["commodity"]] += f["qty"] / tot
    return shares


def cogeneration_processes(ledger, spec):
    """Processes that are cogeneration under `spec`: they deliver one of the heat outputs
    (e.g. steam) and produce electricity as a by-product (a negative request)."""
    if not spec:
        return set()
    heat = {p for p in (f["process"] for f in ledger.flows if f["direction"] == "out"
                        and f["role"] == "product" and f["commodity"] in spec["heat_outputs"])}
    power = {f["process"] for f in ledger.flows if f["direction"] == "out"
             and f["role"] == "byproduct" and f["commodity"] == spec["electricity_output"]}
    return heat & power


def cogeneration_share(ledger, process, spec):
    """Share of a cogeneration process's fuel (and emissions) allocated to electricity.

    incremental_fuel_to_electricity: the fuel for the heat is what a reference boiler
    would need for the same useful heat (heat / reference_boiler_efficiency); the
    rest of the fuel is the increment attributed to electricity."""
    if spec["method"] != "incremental_fuel_to_electricity":
        raise ValueError(f"unknown cogeneration method {spec['method']}")
    fuel = sum(f["qty"] for f in ledger.flows if f["process"] == process
               and f["direction"] == "in" and f["role"] in ("fuel", "feed") and f["unit"] == "GJ")
    heat = sum(f["qty"] for f in ledger.flows if f["process"] == process
               and f["direction"] == "out" and f["commodity"] in spec["heat_outputs"])
    return min(1.0, max(0.0, 1 - heat / spec["reference_boiler_efficiency"] / fuel))


def _resolve(ledger, cfg, commodity, qty):
    spec = cfg["commodities"].get(commodity, {})
    if spec.get("expand"):
        out = []
        for c, s in _composition(ledger, commodity).items():
            out += _resolve(ledger, cfg, c, qty * s)
        return out
    return [(spec["report_as"], qty)] if spec.get("report_as") else []


def energy_report(ledger, cfg):
    """Energy balance rows, RESD style: {(row, fuel): qty}."""
    rows = defaultdict(float)
    if cfg.get("method") == "purchases":      # CIMS today: quantities traced back to purchased fuels
        for f in ledger.flows:
            spec = cfg["commodities"].get(f["commodity"], {})
            if f.get("purchased") and spec.get("report_as"):
                rows[(cfg["account"], spec["report_as"])] += f["qty"]
        return rows
    procs = cfg["processes"]
    cogen = cogeneration_processes(ledger, cfg.get("cogeneration"))
    for f in ledger.flows:
        pc = procs.get(f["process"], {})
        if pc.get("report") is False:
            continue
        spec = cfg["commodities"].get(f["commodity"], {})
        tr = pc.get("transformation")
        cg = cfg["cogeneration"] if f["process"] in cogen else None
        if f["direction"] == "in" and f["role"] in ("fuel", "feed"):
            row = tr["row"] if tr and f["commodity"] in tr.get("feed", []) else pc["account"]
            parts = [(row, f["qty"])]
            if cg:                                   # split the fuel between electricity and heat
                e = cogeneration_share(ledger, f["process"], cg)
                parts = [(cg["electricity_row"], f["qty"] * e), (row, f["qty"] * (1 - e))]
            for r, qty in parts:
                for fuel, q in _resolve(ledger, cfg, f["commodity"], qty):
                    rows[(r, fuel)] += q
        elif (f["direction"] == "out" and f["role"] in ("product", "byproduct") and spec.get("report_as")
              and (tr or (cg and f["commodity"] == cg["electricity_output"]))):
            rows[(cfg["production_row"], spec["report_as"])] += f["qty"]
    return rows


def _match(rule, process, kind, primary, path, use=None):
    m = rule.get("match", {})
    return (("emitted_at" not in m or m["emitted_at"] == process)
            and ("use" not in m or m["use"] == use)
            and ("kind" not in m or m["kind"] == kind)
            and ("path_includes" not in m or m["path_includes"] in path)
            and ("fuel" not in m or m["fuel"] == primary))


def emissions_report(ledger, cfg):
    """{category: t CO2}, or {(row, column): t CO2} for layout: matrix (rows from the
    process, columns from the rules). Carbon left in products is listed separately or
    counted as emitted if the config says so."""
    out = defaultdict(float)
    matrix = cfg.get("layout") == "matrix"
    cogen = cogeneration_processes(ledger, cfg.get("cogeneration"))
    for e in ledger.emissions:
        cg = cfg["cogeneration"] if e["process"] in cogen else None
        share = cogeneration_share(ledger, e["process"], cg) if cg else None
        for (primary, path), v in e["parcels"].items():
            if abs(v) < 1e-12:
                continue
            if cfg.get("group_by") == "fuel":
                out[cfg["fuels"].get(primary, primary)] += v
                continue
            parts = [(None, v)] if cg is None else [("electricity", v * share), ("heat", v * (1 - share))]
            for use, amount in parts:
                rule = next(r for r in cfg["rules"]
                            if _match(r, e["process"], e["kind"], primary, path, use))
                if matrix:
                    row = cfg["rows"].get(e["process"], cfg["rows"]["default"])
                    out[(row, rule["column"])] += amount
                else:
                    out[rule["category"]] += amount
    stored = sum(f["co2"] for f in ledger.flows if f["direction"] == "out" and f["role"] == "stored")
    if cfg.get("stored_carbon") == "emitted":       # reproduces CIMS's current totals
        for f in ledger.flows:
            if f["direction"] == "out" and f["role"] == "stored":
                for (primary, _), v in f["parcels"].items():
                    key = cfg["fuels"].get(primary, primary) if cfg.get("group_by") == "fuel" else cfg["stored_category"]
                    out[key] += v
    elif cfg.get("stored_carbon") == "separate":
        out[cfg["stored_category"]] += stored
    return out


def purchases(ledger):
    q = defaultdict(float)
    for f in ledger.flows:
        if f.get("purchased"):
            q[f["commodity"]] += f["qty"]
    return q


def current_code_view(ledger, supply=("coal-metallurgical", "natural-gas")):
    """What staging CIMS charges today: supply-node factor x positive requests, at the requester."""
    out = defaultdict(float)
    for f in ledger.flows:
        if f.get("purchased") and f["commodity"] in supply:
            out[f["process"]] += co2(f["commodity"], f["qty"])
    return out


# ---------------------------------------------------------------- output
def table(title, header, rows):
    print(f"\n### {title}\n")
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] + ["---:"] * (len(header) - 1)) + "|")
    for r in rows:
        print("| " + " | ".join(r) + " |")


def fmt(x, d=2):
    return f"{x:,.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", help="write the flow ledger to this CSV")
    a = ap.parse_args()
    L = build_ledger()
    ok = True

    # Physical flows by process
    rows = []
    for proc in dict.fromkeys(f["process"] for f in L.flows):
        fin = [f for f in L.flows if f["process"] == proc and f["direction"] == "in"]
        fout = [f for f in L.flows if f["process"] == proc and f["direction"] == "out"]
        em = sum(sum(e["parcels"].values()) for e in L.emissions if e["process"] == proc)
        d = lambda fs: "; ".join(f"{f['commodity']} {fmt(f['qty'], 1)}{' t' if f['unit'] == 't' else ''}"
                                 f"{' (own)' if f['self_supplied'] else ''}" for f in fs) or "-"
        rows.append([proc, d(fin), d(fout), fmt(sum(f["co2"] for f in fin)),
                     fmt(sum(f["co2"] for f in fout)), fmt(em)])
    table("Ledger by process (energy GJ unless t; carbon t CO2)",
          ["process", "in", "out", "C in", "C out", "emitted"], rows)

    c_in = sum(f["co2"] for f in L.flows if f.get("purchased"))
    emitted = sum(sum(e["parcels"].values()) for e in L.emissions)
    stored = sum(f["co2"] for f in L.flows if f["direction"] == "out" and f["role"] == "stored")
    print(f"\nCarbon in {fmt(c_in, 3)} = emitted {fmt(emitted, 3)} + stored {fmt(stored, 3)}")
    ok &= abs(c_in - emitted - stored) < 1e-9

    cur = current_code_view(L)
    table("Current staging code: direct emissions charged (t CO2)", ["process", "charged"],
          [[k, fmt(v)] for k, v in cur.items()] + [["total", fmt(sum(cur.values()))]])

    buys = purchases(L)
    for name in ("resd", "nir-economic"):
        cfg = load(name)
        for section in ("energy", "emissions"):
            spec = cfg.get(section, {}).get("cogeneration")
            for proc in sorted(cogeneration_processes(L, spec)):
                print(f"\n{name}: {proc} is cogeneration; {fmt(100 * cogeneration_share(L, proc, spec), 2)}% "
                      f"of its fuel and emissions go to electricity ({spec['method']}, "
                      f"reference boiler {spec['reference_boiler_efficiency']:.0%})")
    for name in ("resd", "nir-economic", "ipcc-2006", "cims-origin"):
        cfg = load(name)
        if cfg.get("energy"):
            rep = energy_report(L, cfg["energy"])
            fuels = list(dict.fromkeys(f for _, f in rep))
            rws = list(dict.fromkeys(r for r, _ in rep))
            table(f"{cfg['name']}: energy (GJ)", ["row"] + fuels,
                  [[r] + [fmt(rep.get((r, f), 0), 1) if (r, f) in rep else "" for f in fuels] for r in rws])
            for c, spec in cfg["energy"]["commodities"].items():
                chk = spec.get("check_disposition")
                if chk and c in buys:
                    got = sum(v for (r, f), v in rep.items() if f == spec["report_as"] and r in chk)
                    print(f"\nCheck: {spec['report_as']} purchased {fmt(buys[c], 1)} = "
                          f"{' + '.join(chk)} {fmt(got, 1)}")
                    ok &= abs(got - buys[c]) < 1e-9
        if cfg.get("emissions") and cfg["emissions"].get("layout") == "matrix":
            rep = emissions_report(L, cfg["emissions"])
            cols = [c for c in cfg["emissions"]["columns"] if any(k[1] == c for k in rep)]
            rws = list(dict.fromkeys(r for r, _ in rep))
            table(f"{cfg['name']}: emissions (t CO2)", ["economic category"] + cols + ["Total"],
                  [[r] + [fmt(rep[(r, c)]) if (r, c) in rep else "" for c in cols]
                   + [fmt(sum(v for (rr, _), v in rep.items() if rr == r))] for r in rws])
        elif cfg.get("emissions"):
            rep = emissions_report(L, cfg["emissions"])
            table(f"{cfg['name']}: emissions (t CO2)", ["category", "t CO2"],
                  [[k, fmt(v)] for k, v in rep.items()] + [["total", fmt(sum(rep.values()))]])
        if cfg.get("emissions"):
            expect = cfg["emissions"].get("total_equals")
            if expect:
                target = {"carbon_in": c_in, "emitted": emitted}[expect]
                print(f"\nCheck: total {fmt(sum(rep.values()), 3)} = {expect} {fmt(target, 3)}")
                ok &= abs(sum(rep.values()) - target) < 1e-9

    if a.ledger:
        with open(a.ledger, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["process", "direction", "role", "commodity", "qty", "unit", "self_supplied",
                        "primary_fuel", "path", "t_co2"])
            for f in L.flows:
                for (primary, path), v in f["parcels"].items():
                    w.writerow([f["process"], f["direction"], f["role"], f["commodity"], f["qty"],
                                f["unit"], f["self_supplied"], primary, ">".join(path), v])
            for e in L.emissions:
                for (primary, path), v in e["parcels"].items():
                    w.writerow([e["process"], "emitted", e["kind"], "", "", "", "", primary, ">".join(path), v])
        print(f"\nLedger written to {a.ledger}")

    print("\nAll checks passed." if ok else "\nA CHECK FAILED.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
