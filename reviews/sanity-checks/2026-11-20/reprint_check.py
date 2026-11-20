"""Pooled values that two different sources give identically (likely a reprint pooled twice).
Sanity check 2026-11-20. Run from the repo root; writes identical-values.csv beside this script."""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
e = pd.read_csv("data/processed_data/technology_database/example-parameter.csv", low_memory=False)
p = e[e.excluded.isna() & e["set-aside"].isna() & e["duplicate-of"].isna() & e["value-norm"].notna()].copy()
p = p[~p.parameter.isin(["lifetime", "capacity-factor", "trl", "construction-time", "discount-rate", "capital-recovery"])]
p["v"] = p["value-norm"].map(lambda x: float(f"{x:.5g}"))
g = p.groupby(["archetype", "parameter", p.target.fillna(""), "v"])
rows = []
for k, d in g:
    if d["source-id"].nunique() > 1:
        rows.append(dict(archetype=k[0], parameter=k[1], target=k[2], value=k[3], n=len(d),
                         sources="; ".join(sorted(d["source-id"].unique())),
                         via="; ".join(sorted(d["via-source-id"].dropna().unique()))))
r = pd.DataFrame(rows).sort_values(["parameter", "archetype"])
r.to_csv(HERE / "identical-values.csv", index=False)
print(len(r), "groups;", r.archetype.nunique(), "archetypes")
print(r.parameter.value_counts().head(8).to_string())
print(r.sources.value_counts().head(12).to_string())
