"""Spread of pooled values, scale effects in capex, and cost-basis mixing (sanity check 2026-11-20).

Run from the repo root: python reviews/sanity-checks/2026-11-20/spread_analysis.py
Writes spread-by-archetype.csv, capex-scale.csv and capex-basis-mix.csv beside this script.
"""
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = Path("data/processed_data/technology_database")
a = pd.read_csv(OUT / "archetype-parameter.csv", low_memory=False)
e = pd.read_csv(OUT / "example-parameter.csv", low_memory=False)
arch = pd.read_csv(OUT / "archetype.csv", low_memory=False)[["archetype", "family", "type"]]

pooled = e[e.excluded.isna() & e["set-aside"].isna() & e["duplicate-of"].isna() & e["value-norm"].notna()]

# 1. spread of pooled values per archetype and parameter
rows = []
for p in ["capex", "capacity", "opex-fixed", "cost-levelized", "specific-energy-consumption", "lifetime"]:
    s = pooled[(pooled.parameter == p) & pooled.target.isna()]
    s = s[s["value-norm"] > 0]
    for k, g in s.groupby("archetype"):
        v = g["value-norm"].to_numpy()
        if len(v) < 3:
            continue
        q1, q3 = np.percentile(v, [25, 75])
        iqr = q3 - q1
        keep = v[(v >= q1 - 1.5 * iqr) & (v <= q3 + 1.5 * iqr)]
        rows.append(dict(archetype=k, parameter=p, n=len(v), sources=g["source-id"].nunique(),
                         median=np.median(v), low=v.min(), high=v.max(), ratio=v.max() / v.min(),
                         p25=q1, p75=q3, iqr_ratio=q3 / q1 if q1 > 0 else np.nan,
                         n_outliers=len(v) - len(keep), median_trimmed=np.median(keep),
                         cost_bases="; ".join(sorted(g["cost-basis"].dropna().unique())) if p in ("capex", "opex-fixed") else ""))
sp = pd.DataFrame(rows).merge(arch, on="archetype", how="left")
sp.sort_values(["parameter", "ratio"], ascending=[True, False]).to_csv(HERE / "spread-by-archetype.csv", index=False)

# 2. scale effect: capex per unit capacity against the same example's capacity
cap = pooled[(pooled.parameter == "capacity") & pooled.target.isna()][["example-id", "archetype", "value-norm"]].rename(columns={"value-norm": "cap"})
cap = cap.groupby(["example-id", "archetype"], as_index=False)["cap"].median()
cx = pooled[(pooled.parameter == "capex") & pooled.target.isna()][["example-id", "archetype", "source-id", "value-norm", "cost-basis"]]
m = cx.merge(cap, on=["example-id", "archetype"])
m = m[(m.cap > 0) & (m["value-norm"] > 0)]
sc = []
for k, g in m.groupby("archetype"):
    if len(g) < 5 or g.cap.max() / g.cap.min() < 3:
        continue
    b, c0 = np.polyfit(np.log(g.cap), np.log(g["value-norm"]), 1)
    r = np.corrcoef(np.log(g.cap), np.log(g["value-norm"]))[0, 1]
    sc.append(dict(archetype=k, n=len(g), cap_ratio=g.cap.max() / g.cap.min(), capex_ratio=g["value-norm"].max() / g["value-norm"].min(),
                   slope=b, scale_exponent=1 + b, r=r, r2=r * r))
sc = pd.DataFrame(sc).sort_values("n", ascending=False)
sc.to_csv(HERE / "capex-scale.csv", index=False)

# 3. cost-basis mixing in pooled capex
cb = pooled[(pooled.parameter == "capex") & pooled.target.isna()].groupby("archetype")["cost-basis"].agg(lambda s: "; ".join(sorted(s.dropna().unique())))
cb = cb.to_frame("bases")
cb["n_bases"] = cb.bases.str.count(";") + 1
cb["has_equipment_and_plant"] = cb.bases.str.contains("equipment") & cb.bases.str.contains("total-plant|installed|overnight")
cb.to_csv(HERE / "capex-basis-mix.csv")

# summary
for p in ["capex", "capacity", "cost-levelized", "opex-fixed", "specific-energy-consumption"]:
    s = sp[sp.parameter == p]
    print(f"{p:28} archetypes n>=3: {len(s):4}  ratio>5: {(s.ratio>5).sum():4}  ratio>10: {(s.ratio>10).sum():4}  IQR ratio>5: {(s.iqr_ratio>5).sum():3}  median moves >25% if outliers trimmed: {((s.median_trimmed/s['median']-1).abs()>0.25).sum()}")
print("\nscale fits:", len(sc), "archetypes; median exponent", round(sc.scale_exponent.median(), 2),
      "; share with r2>0.3:", round((sc.r2 > 0.3).mean(), 2))
print(sc.head(15).round(2).to_string())
print("\ncapex pools mixing equipment with installed/plant bases:", int(cb.has_equipment_and_plant.sum()), "of", len(cb))
