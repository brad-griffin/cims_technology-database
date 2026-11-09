"""Within-archetype internal consistency check on the built database (2026-11-07).

Run from the tech_data root:
    python reviews/sanity-checks/2026-11-07/internal_consistency.py . reviews/sanity-checks/2026-11-07/internal-consistency.csv
Reads only data/processed_data/technology_database and data/technology_database; writes one CSV.
"""
import csv, math, sys, re
from collections import defaultdict
import pandas as pd

ROOT = sys.argv[1]
OUT = sys.argv[2]
P = f"{ROOT}/data/processed_data/technology_database"
R = f"{ROOT}/data/technology_database"
par = pd.read_csv(f"{P}/archetype-parameter.csv", dtype={"target": str})
par["target"] = par["target"].fillna("")
arch = pd.read_csv(f"{P}/archetype.csv").fillna("")
hosts = pd.read_csv(f"{R}/fill/host-archetype.csv").fillna("")
hosts = {r.archetype: r.host for r in hosts.itertuples() if r.status == "active" and r.host}
cf = pd.read_csv(f"{R}/reference/conversion-factor.csv").fillna("")
EF = {r["factor-id"][len("cf-ef-co2-"):]: (float(r.factor), float(r["factor-low"] or r.factor), float(r["factor-high"] or r.factor))
      for _, r in cf.iterrows() if r["factor-id"].startswith("cf-ef-co2-") and r["from-unit"] == "GJ"}
price = pd.read_csv(f"{R}/reference/energy-price.csv").fillna("")
VOCAB = set(pd.read_csv(f"{R}/vocabulary/carrier.csv").carrier)
# findings a ruling accepts (consistency fixes 2026-11-07; rulings.md): reported as `ruled`
RULED = {}
for _f in ("emission-fix.csv", "efficiency-fix.csv"):
    pass
ACCEPT = {
    ("reactor_fluid-coking", "combustion-co2"): "R7: own coke burned, 0.17 draft pending Brad",
    ("electric-arc-furnace_scrap-preheating", "variant-efficient"): "E10: Brad 2026-11-06 own-carrier ruling",
}
for _a in ["autothermal-reformer_hydrogen", "autothermal-reformer_hydrogen_ccs-concentrated", "gasifier_biomass-waste",
           "gasifier_coal-ammonia", "gasifier_coal-fischer-tropsch", "gasifier_coal-methanation", "gasifier_coal-methanol",
           "gasifier_coal-methanol_ccs-concentrated", "gasifier_coal-petroleum-coke",
           "gasifier_coal-petroleum-coke_ccs-concentrated", "reactor_gas-to-liquids"]:
    ACCEPT[(_a, "combustion-co2")] = "R7: feed carbon oxidised in the process stream, carried in the total"
for _a in ["binder_blended-cement", "binder_calcined-clay", "binder_portland-cement", "no-abatement_coal-mine-methane",
           "no-abatement_methane", "no-abatement_n2o", "no-abatement_sf6", "pipeline_crude-oil", "pipeline_natural-gas",
           "process-improvement_magnesium-cover-gas"]:
    ACCEPT[(_a, "sign")] = "F4: zero energy use by ruling (energy on other nodes)"
    ACCEPT[(_a, "missing")] = "F3: not-applicable by ruling"
ACCEPT[("fermenter_lignocellulosic-enzymatic", "missing")] = "F3: lignin burn covers process energy; feed carries it"
ACCEPT[("pipeline_hydrogen", "levelized-vs-sourced")] = "F6: S102 length basis, pending Brad"
ACCEPT[("reactor_biomass-flash-pyrolysis", "levelized-vs-sourced")] = "F6: source re-read of the basis, for Brad"
ACCEPT[("reactor_co2-to-dme", "levelized-vs-sourced")] = "as F6: 3.4x, source basis to re-read, for Brad"
ACCEPT[("liquefaction-train_base-load", "levelized-vs-sourced")] = "F6: 2.6x, capex basis to check, for Brad"
PRICE = {r.carrier: (r.kind, float(r.price) if r.price != "" else None) for r in price.itertuples()}

FOSSIL = {"natural-gas", "coal", "oil", "diesel", "gasoline", "coke", "petroleum-coke", "lpg", "naphtha",
          "fuel-oil", "heavy-fuel-oil", "refinery-gas", "still-gas", "coke-oven-gas", "blast-furnace-gas"}
NO_HV = {"electricity", "heat", "steam", "cooling", "hot-water", "waste-heat", "solar", "geothermal", "nuclear", "hydrogen-as-feed"}
STEAMLIKE = {"steam", "heat", "hot-water", "district-heat", "waste-heat"}
NOT_CARRIER = {"", "component", "total", "not-stated"}
SEC = "specific-energy-consumption"

H = defaultdict(dict)   # archetype -> (parameter, target) -> row
for r in par.to_dict("records"):
    H[r["archetype"]][(r["parameter"], r["target"])] = r
A = {r["archetype"]: r for r in arch.to_dict("records")}

def v(r, k="central"):
    if r is None: return None
    x = r.get(k)
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)

def live(r):
    return r is not None and r.get("grade") != "not-applicable" and v(r) is not None

F = []
def flag(a, check, sev, param, detail, value=None, expected=None):
    acc = ACCEPT.get((a, check)) or (("R7: reductant, feed or exported-gas scope" ) if check == "combustion-co2-scope" else None) \
        or ("F2: source spread, accepted and reported" if check == "band-width" else None)
    if acc and sev != "high" or acc and check in ("combustion-co2",):
        detail = f"{detail} [accepted: {acc}]"
        sev = "ruled"
    ratio = (value / expected) if value not in (None, 0) and expected not in (None, 0) else None
    r = A.get(a, {})
    F.append({"archetype": a, "type": r.get("type", ""), "family": r.get("family", ""), "check": check,
              "severity": sev, "parameter": param, "value": value, "expected": expected,
              "ratio": round(ratio, 3) if ratio else None, "detail": detail})

def rel(x, y):
    return abs(x - y) / max(abs(y), 1e-12)

def sev_of(d, med=0.05, hi=0.25):
    return "high" if d > hi else "medium" if d > med else "low"

PCT = {"capacity-factor": (0, 100), "availability": (0, 100), "capture-rate": (0, 100),
       "share-to-capture": (0, 100), "emissions-reduction-potential": (0, 100), "discount-rate": (0, 30)}
NONNEG = {"capex", "opex-fixed", "lifetime", "construction-time", "capacity", "annual-output", "capacity-factor",
          "emissions-captured", "efficiency"}
SIZE = {"t": 1000, "GJ": 31536, "1000-m3": 1, "Mlm-h": 1, "m": 1, "m3": 1, "m3-km": 1}
HEATPUMPISH = re.compile(r"heat-pump|chiller|vapour-recompression|mvr|cooling")

def crf(r, n): return r / (1 - (1 + r) ** -n)

for a, h in H.items():
    meta = A.get(a, {})
    is_ccs = "_ccs-" in a
    pu = meta.get("product-unit", "")
    # ---- 1. band order, signs, bounds ------------------------------------
    for (p, t), r in h.items():
        c, lo, hi = v(r), v(r, "low"), v(r, "high")
        if c is None: continue
        tol = 1e-3 * max(abs(c), 1e-12)
        if lo is not None and lo > c + tol:
            flag(a, "band-order", "high" if rel(lo, c) > 0.01 else "low", f"{p}|{t}", f"low {lo:.6g} above central {c:.6g}", lo, c)
        if hi is not None and hi < c - tol:
            flag(a, "band-order", "high" if rel(hi, c) > 0.01 else "low", f"{p}|{t}", f"high {hi:.6g} below central {c:.6g}", hi, c)
        if p in NONNEG and c < 0:
            flag(a, "sign", "high", f"{p}|{t}", f"negative central {c:.4g}", c)
        if p == SEC and t == "" and c <= 0 and r.get("grade") != "not-applicable":
            flag(a, "sign", "medium", f"{p}|total", f"total energy use {c:.4g}", c)
        if p in PCT:
            l0, h0 = PCT[p]
            if not (l0 <= c <= h0):
                flag(a, "bounds", "high", f"{p}|{t}", f"{c:.4g}% outside {l0}-{h0}", c)
        if p == "efficiency":
            cap = 700 if HEATPUMPISH.search(a) else 100.5
            if c > cap or c < 5:
                flag(a, "bounds", "high", f"{p}|{t}", f"efficiency {c:.4g}% implausible (cap {cap})", c)
        if p == "lifetime" and not (1 <= c <= 100):
            flag(a, "bounds", "medium", p, f"lifetime {c:g} years", c)
        if p in ("emissions-combustion", "emissions-process", "emissions-total", "emissions-captured") \
                and not str(r.get("unit") or "").startswith("t/"):
            flag(a, "unit", "high", f"{p}|{t}", f"emissions unit {r.get('unit')} is not a mass per unit of product")
        # unit vs product unit
        u = str(r.get("unit") or "")
        dens = None
        if "/" in u and p not in ("capacity",):
            dens = u.split("/", 1)[1].replace("-per-yr", "")
            if dens not in (pu,) and p not in PCT and u not in ("%",) and p not in ("temperature-output", "pressure-output", "lifetime", "construction-time"):
                if not (p == "abatement-cost" or p == "emissions-reduction-potential"):
                    flag(a, "unit", "medium", f"{p}|{t}", f"unit {u} not per product unit {pu}")
    # ---- 2. size identity -------------------------------------------------
    cap, cfac, ao = h.get(("capacity", "")), h.get(("capacity-factor", "")), h.get(("annual-output", ""))
    if live(cap) and live(cfac) and live(ao) and pu in SIZE:
        exp = v(cap) * v(cfac) / 100 * SIZE[pu]
        d = rel(v(ao), exp)
        if d > 0.02:
            flag(a, "size-identity", sev_of(d), "annual-output",
                 f"annual output {v(ao):.4g} {pu} vs capacity {v(cap):.4g} {cap['unit']} x CF {v(cfac):.3g}% = {exp:.4g}", v(ao), exp)
    # ---- 3. construction time vs lifetime -----------------------------------
    lt, ct = h.get(("lifetime", "")), h.get(("construction-time", ""))
    if live(lt) and live(ct) and v(ct) >= v(lt):
        flag(a, "time", "high", "construction-time", f"construction {v(ct):g} y >= lifetime {v(lt):g} y", v(ct), v(lt))
    # ---- 4. energy total vs carriers ----------------------------------------
    secs = {t: r for (p, t), r in h.items() if p == SEC and live(r) and "pooled apart" not in str(r.get("central-from") or "")}
    apart = sorted(t for (p, t), r in h.items() if p == SEC and live(r) and "pooled apart" in str(r.get("central-from") or ""))
    if apart:
        flag(a, "pooled-apart", "low", SEC, "carriers pooled apart (shown, but not part of the total or the fuel split): " + ", ".join(apart))
    tot = secs.get("")
    car = {t: r for t, r in secs.items() if t not in NOT_CARRIER}
    named = {t: v(r) for t, r in car.items() if t not in NO_HV and t != "fuel"}
    l1 = {t: v(r) for t, r in car.items() if t in NO_HV}
    if "fuel" in car: l1["fuel"] = v(car["fuel"])
    elif named: l1["fuel"] = sum(named.values())
    if "fuel" in car and named:
        s = sum(named.values()); d = rel(s, v(car["fuel"]))
        if d > 0.02:
            flag(a, "fuel-split", sev_of(d), SEC, f"named fuels sum {s:.4g} vs fuel {v(car['fuel']):.4g} ({', '.join(f'{k} {x:.3g}' for k, x in named.items())})", s, v(car["fuel"]))
    if tot is not None and l1:
        additive = not (("fuel" in l1 and set(l1) & STEAMLIKE) or len(set(l1) & STEAMLIKE) > 1)
        s = sum(x for x in l1.values() if x is not None)
        d = rel(s, v(tot))
        if d > 0.02:
            if additive:
                flag(a, "sec-carriers", sev_of(d), SEC, f"carriers sum {s:.4g} vs total {v(tot):.4g} ({', '.join(f'{k} {x:.3g}' for k, x in l1.items())})", s, v(tot))
            elif s < v(tot) * 0.98:
                flag(a, "sec-carriers", "low", SEC, f"non-additive mix (fuel beside steam/heat); carriers sum {s:.4g} below total {v(tot):.4g}", s, v(tot))
    if car and tot is None:
        flag(a, "sec-carriers", "medium", SEC, f"carriers given ({', '.join(car)}) but no total energy use")
    listed = {x.strip() for x in str(meta.get("carriers", "")).split(";") if x.strip()}
    have_c = {t for t, r in car.items() if (v(r) or 0) != 0 and t != "fuel"}
    extra = (have_c - listed - {"feedstock"}) & VOCAB
    if listed and extra:
        flag(a, "carrier-list", "low", SEC, f"energy rows for carriers not in the archetype's carrier list: {', '.join(sorted(extra))} (listed: {', '.join(sorted(listed))})")
    # ---- 5. efficiency vs energy use (energy-service archetypes) ------------
    eff = h.get(("efficiency", ""))
    if pu == "GJ" and live(eff) and tot is not None and v(eff) > 0 and not h.get(("heat-to-power-ratio", "")):
        exp = 100 / v(eff)
        feed = sum(v(r) for (p, t), r in h.items() if p == "feedstock-consumption" and live(r))
        if not feed and hosts.get(a) in H:
            feed = sum(v(r) for (p, t), r in H[hosts[a]].items() if p == "feedstock-consumption" and live(r))
        d = rel(v(tot) + feed, exp)
        if is_ccs:
            if d > 0.10:
                flag(a, "efficiency-vs-sec", "low", "efficiency", f"CCS variant keeps the host efficiency {v(eff):.4g}% while its energy use (with capture) is {v(tot):.4g} GJ/GJ (100/eff = {exp:.4g})", v(tot), exp)
            d = 0
        fs = h.get(("feedstock-consumption", ""))
        if d > 0.10:
            flag(a, "efficiency-vs-sec", sev_of(d, 0.10, 0.30), "efficiency",
                 f"energy use {v(tot):.4g}" + (f" + feedstock {feed:.4g}" if feed else " (no feedstock rows)") + f" GJ/GJ vs 100/efficiency {exp:.4g} (efficiency {v(eff):.4g}%)", v(tot) + feed, exp)
    eh, ee = h.get(("efficiency", "heat")), h.get(("efficiency", "electricity"))
    if live(eff) and live(eh) and not live(ee) and rel(v(eh), v(eff)) > 0.01:
        flag(a, "efficiency-streams", "medium", "efficiency", f"single-stream: efficiency {v(eff):.4g} vs efficiency_heat {v(eh):.4g}", v(eh), v(eff))
    if live(eh) and live(ee):
        hpr = h.get(("heat-to-power-ratio", ""))
        if live(hpr) and v(ee) > 0:
            d = rel(v(eh) / v(ee), v(hpr))
            if d > 0.05:
                flag(a, "chp-hpr", sev_of(d), "heat-to-power-ratio", f"eff_heat/eff_elec {v(eh)/v(ee):.3g} vs HPR {v(hpr):.3g}", v(eh) / v(ee), v(hpr))
        if live(eff) and v(eh) + v(ee) > 0 and rel(v(eff), v(eh) + v(ee)) > 0.05 and v(eff) < v(eh) + v(ee):
            flag(a, "chp-total", "medium", "efficiency", f"overall {v(eff):.4g}% vs heat {v(eh):.4g} + electricity {v(ee):.4g}", v(eff), v(eh) + v(ee))
        if v(eh) + v(ee) > 100.5 and not HEATPUMPISH.search(a):
            flag(a, "bounds", "high", "efficiency", f"heat {v(eh):.4g} + electricity {v(ee):.4g} > 100%")
    # ---- 6. combustion CO2 vs fuel burned ----------------------------------
    cco2 = h.get(("emissions-combustion", "co2"))
    fos = {k: x for k, x in named.items() if k in FOSSIL and x and x > 0}
    unnamed_fuel = "fuel" in car and not named
    if live(cco2) and v(cco2) > 0 and not fos and not unnamed_fuel and car:
        flag(a, "combustion-co2", "high", "emissions-combustion|co2",
             f"combustion CO2 {v(cco2):.4g} but no fossil fuel in the energy rows ({', '.join(f'{k} {x:.3g}' for k, x in l1.items() if x)})", v(cco2))
    if fos and live(cco2) and v(cco2) > 0 and not unnamed_fuel:
        efs = [EF[k] for k in fos if k in EF]
        if len(efs) == len(fos):
            exp = sum(x * EF[k][0] for k, x in fos.items())
            lo_ = sum(x * EF[k][1] for k, x in fos.items()); hi_ = sum(x * EF[k][2] for k, x in fos.items())
            if v(cco2) > hi_ * 1.10 or v(cco2) < lo_ * 0.80:
                d = rel(v(cco2), exp)
                scope = live(h.get(("emissions-process", "co2"))) or any(k[0] == "feedstock-consumption" for k in h) or \
                    re.match(r"(blast-furnace|coke-oven|smelting|steam-reformer|autothermal|steam-cracker|reactor_fluid|gasifier|electric-arc|shaft-furnace)", a)
                flag(a, "combustion-co2-scope" if scope else "combustion-co2", "medium" if scope else sev_of(d, 0.10, 0.30), "emissions-combustion|co2",
                     f"combustion CO2 {v(cco2):.4g} vs fossil fuel x factor {exp:.4g} ({', '.join(f'{k} {x:.3g}' for k, x in fos.items())}); grade {cco2['grade']}/{cco2['method']}", v(cco2), exp)
    if fos and sum(fos.values()) > 0.01 * (v(tot) or 1) and not (live(cco2) and v(cco2) > 0):
        flag(a, "combustion-co2", "medium", "emissions-combustion|co2",
             f"burns fossil fuel ({', '.join(f'{k} {x:.3g}' for k, x in fos.items())}) but combustion CO2 is {'missing' if cco2 is None else v(cco2)}")
    # ---- 7. emission totals vs parts ----------------------------------------
    for sp in ("co2", "co2e"):
        et = h.get(("emissions-total", sp))
        ec, ep = h.get(("emissions-combustion", sp)), h.get(("emissions-process", sp))
        cap_ = h.get(("emissions-captured", "co2"))
        if sp == "co2e":
            ec = ec if live(ec) else h.get(("emissions-combustion", "co2"))
            ep = ep if live(ep) else h.get(("emissions-process", "co2"))
        parts = (v(ec) if live(ec) else 0) + (v(ep) if live(ep) else 0)
        if not live(et) or parts <= 0 or meta.get("family") == "co2-capture": continue
        gross = parts
        if is_ccs or (live(cap_) and v(cap_) > 0):
            capt = v(cap_) if live(cap_) else 0
            bio = h.get(("emissions-biomass", "co2"))
            hb = H.get(hosts.get(a, ""), {}).get(("emissions-biomass", "co2"))
            if live(hb) and sp == "co2":
                # captured CO2 split between fossil and biogenic (Brad 2026-10-14):
                # the biogenic part comes off emissions-biomass, not the fossil total
                bio_cut = v(hb) - (v(bio) if live(bio) else v(hb))
                capt = max(capt - bio_cut, 0)
            exp = gross - capt
            d = abs(v(et) - exp) / max(gross, 1e-12)
            if d > 0.05:
                flag(a, "emissions-net", sev_of(d), f"emissions-total|{sp}",
                     f"net total {v(et):.4g} vs combustion+process {gross:.4g} - captured {capt:.4g} = {exp:.4g}", v(et), exp)
            if capt > gross * 1.02:
                flag(a, "emissions-net", "high", "emissions-captured|co2", f"captured {capt:.4g} above gross {gross:.4g}", capt, gross)
        else:
            if v(et) < parts * 0.95:
                flag(a, "emissions-total", sev_of(rel(v(et), parts)), f"emissions-total|{sp}",
                     f"total {v(et):.4g} below combustion {v(ec) if live(ec) else 0:.4g} + process {v(ep) if live(ep) else 0:.4g}", v(et), parts)
    for p in ("emissions-total", "emissions-combustion", "emissions-process"):
        c2, ce = h.get((p, "co2")), h.get((p, "co2e"))
        if live(c2) and live(ce) and v(ce) < v(c2) * 0.99:
            flag(a, "co2e-below-co2", "high", p, f"CO2-eq {v(ce):.4g} below CO2 {v(c2):.4g}", v(ce), v(c2))
    stc, cr, capt = h.get(("share-to-capture", "co2")), h.get(("capture-rate", "co2")), h.get(("emissions-captured", "co2"))
    if is_ccs and live(capt):
        g = sum(v(h[(p, "co2")]) for p in ("emissions-combustion", "emissions-process") if live(h.get((p, "co2"))))
        if g > 0:
            share = v(capt) / g * 100
            if live(stc) and share > v(stc) * 1.02:
                flag(a, "capture-share", "medium", "emissions-captured|co2", f"captured {share:.1f}% of gross CO2, above share-to-capture {v(stc):.3g}%", share, v(stc))
    # ---- 8. levelized cost recomputation ------------------------------------
    lc = h.get(("cost-levelized", "calculated"))
    cx, of, ov = h.get(("capex", "")), h.get(("opex-fixed", "")), h.get(("opex-variable", ""))
    if live(lc) and live(cx) and live(lt) and live(cfac) and v(cfac) > 0:
        o = v(of) if live(of) else 0; vv = v(ov) if live(ov) else 0
        exp = (v(cx) * crf(0.08, v(lt)) + o) / (min(v(cfac), 100) / 100) + vv
        d = rel(v(lc), exp)
        if d > 0.01:
            flag(a, "levelized-recalc", sev_of(d, 0.02, 0.10), "cost-levelized|calculated", f"stored {v(lc):.4g} vs recomputed {exp:.4g}", v(lc), exp)
    le = h.get(("cost-levelized", "calculated-incl-energy"))
    if live(lc) and live(le):
        en = 0; ok = True
        use = dict((k, x) for k, x in l1.items() if k != "fuel")
        if "fuel" in l1:
            if named: use.update(named)
            else: ok = False
        for k, x in use.items():
            kind, pr = PRICE.get(k, (None, None))
            if kind == "internal": continue
            if kind != "sourced" or pr is None: ok = False; break
            en += (x or 0) * pr
        if ok and use and not any(k[0] == "feedstock-consumption" for k in h):
            exp = v(lc) + en
            d = rel(v(le), exp)
            if d > 0.02:
                flag(a, "levelized-energy", sev_of(d, 0.05, 0.25), "cost-levelized|calculated-incl-energy",
                     f"stored {v(le):.4g} vs non-energy {v(lc):.4g} + energy {en:.4g} = {exp:.4g}", v(le), exp)
        if v(le) < v(lc) * 0.999:
            flag(a, "levelized-energy", "high", "cost-levelized", f"incl-energy {v(le):.4g} below non-energy {v(lc):.4g}", v(le), v(lc))
    ls = h.get(("cost-levelized", ""))
    if live(ls) and live(le) and v(le) > 0 and v(ls) > 0:
        # sourced levelized costs exclude the feed (a liquefaction fee excludes the gas):
        # compare against the calculated cost with energy but without feedstock
        feedc = 0.0
        for (pp, tt), rr_ in h.items():
            if pp == "feedstock-consumption" and tt and live(rr_):
                kind, pr = PRICE.get(tt, (None, None))
                if kind == "sourced" and pr:
                    feedc += v(rr_) * pr
        le_cmp = v(le) - feedc if v(le) - feedc > 0 else v(le)
        rr = v(ls) / le_cmp
        r_in = v(ls) / v(le)
        # a sourced cost may include the feed (biodiesel) or exclude it (a liquefaction
        # fee): flag only where it is far from both
        if abs(math.log(r_in)) < abs(math.log(rr)):
            rr, le_cmp = r_in, v(le)
        if rr > 3 or rr < 1 / 3:
            flag(a, "levelized-vs-sourced", "medium" if (rr > 5 or rr < 0.2) else "low", "cost-levelized",
                 f"sourced levelized {v(ls):.4g} vs calculated incl. energy (nearer of with and without feedstock) {le_cmp:.4g}", v(ls), le_cmp)
    # ---- 9. band width -------------------------------------------------------
    for (p, t), r in h.items():
        c, lo, hi = v(r), v(r, "low"), v(r, "high")
        if p in ("capex", "opex-fixed", "opex-variable") and t == "" and c and lo and hi and lo > 0 and hi / lo > 100:
            flag(a, "band-width", "low", p, f"band {lo:.3g}-{hi:.3g} spans {hi/lo:.0f}x (central {c:.3g}, n {r['n']})", hi / lo)
    # ---- 10. completeness ----------------------------------------------------
    miss = [p for p in ("capex", "opex-fixed", "lifetime", "capacity-factor", "capacity", "annual-output") if not live(h.get((p, "")))]
    if miss and meta.get("type") != "reference":
        flag(a, "missing", "low", "; ".join(miss), "core parameters missing or not applicable: " + ", ".join(miss))
    if tot is None and not any(k[0] == SEC for k in h) and meta.get("type") != "reference":
        flag(a, "missing", "low", SEC, "no energy use at all")
    # ---- 11. variant vs host -------------------------------------------------
    host = hosts.get(a)
    if host and host in H:
        hh = H[host]
        for p in ("capacity", "annual-output", "capacity-factor"):
            x, y = hh.get((p, "")), h.get((p, ""))
            if live(x) and live(y) and rel(v(y), v(x)) > 0.01:
                flag(a, "variant-size", "medium", p, f"variant {v(y):.4g} vs host {host} {v(x):.4g}", v(y), v(x))
        if is_ccs:
            for p in ("capex", "opex-fixed"):
                x, y = hh.get((p, "")), h.get((p, ""))
                if live(x) and live(y) and v(y) < v(x) * 0.999:
                    flag(a, "variant-ccs", "high", p, f"CCS variant {v(y):.4g} below host {host} {v(x):.4g}", v(y), v(x))
            x, y = hh.get((SEC, "")), h.get((SEC, ""))
            if live(x) and live(y) and v(y) < v(x) * 0.999:
                flag(a, "variant-ccs", "medium", SEC, f"CCS variant energy {v(y):.4g} below host {v(x):.4g}", v(y), v(x))
            for sp in ("co2", "co2e"):
                x, y = hh.get(("emissions-total", sp)), h.get(("emissions-total", sp))
                if live(x) and live(y) and v(y) > v(x) * 1.001:
                    flag(a, "variant-ccs", "high", f"emissions-total|{sp}", f"CCS variant {v(y):.4g} above host {v(x):.4g}", v(y), v(x))
            hx, hy = hh.get(("lifetime", "")), h.get(("lifetime", ""))
            if live(hx) and live(hy) and rel(v(hy), v(hx)) > 0.01:
                flag(a, "variant-ccs", "low", "lifetime", f"CCS variant lifetime {v(hy):g} vs host {v(hx):g}", v(hy), v(hx))
            # combustion/process should match host gross
            for p in ("emissions-combustion", "emissions-process"):
                x, y = hh.get((p, "co2")), h.get((p, "co2"))
                if live(x) and live(y) and rel(v(y), v(x)) > 0.02:
                    flag(a, "variant-ccs", "medium", f"{p}|co2", f"gross {v(y):.4g} vs host {v(x):.4g}", v(y), v(x))
            x = hh.get(("emissions-total", "co2"))
            if live(x) and live(capt) and v(capt) > v(x) * 1.02:
                flag(a, "variant-ccs", "high", "emissions-captured|co2", f"captured {v(capt):.4g} above host total {v(x):.4g}", v(capt), v(x))
        elif meta.get("type") == "efficient variant":
            x, y = hh.get((SEC, "")), h.get((SEC, ""))
            if live(x) and live(y) and v(y) > v(x) * 1.01:
                flag(a, "variant-efficient", "high", SEC, f"efficient variant {v(y):.4g} above host {host} {v(x):.4g}", v(y), v(x))
            for sp in ("co2",):
                x, y = hh.get(("emissions-combustion", sp)), h.get(("emissions-combustion", sp))
                if live(x) and live(y) and v(y) > v(x) * 1.01:
                    flag(a, "variant-efficient", "medium", "emissions-combustion|co2", f"efficient variant {v(y):.4g} above host {v(x):.4g}", v(y), v(x))

# archetypes with no rows
for a in A:
    if a not in H:
        flag(a, "missing", "medium", "", "archetype has no parameter rows")

df = pd.DataFrame(F)
order = {"high": 0, "medium": 1, "low": 2, "ruled": 3}
df["o"] = df.severity.map(order)
df = df.sort_values(["o", "check", "archetype"]).drop(columns="o")
df.insert(0, "id", [f"IC{i+1:03d}" for i in range(len(df))])
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(len(A), "archetypes;", len(df), "findings")
print(df.groupby(["check", "severity"]).size().unstack(fill_value=0).to_string())
