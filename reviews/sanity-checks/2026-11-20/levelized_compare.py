"""Sourced levelized cost (wide-view column CB) against the calculated levelized cost
including energy (column CJ), sanity check 2026-11-20. Run from the repo root.
Writes levelized-compare.csv beside this script."""
from pathlib import Path
import re
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = Path("data/processed_data/technology_database")
a = pd.read_csv(OUT / "archetype-parameter.csv", low_memory=False)
e = pd.read_csv(OUT / "example-parameter.csv", low_memory=False)
lv = a[a.parameter == "cost-levelized"]
cb = lv[lv.target.isna()].set_index("archetype")
cf = lv[lv.target == "calculated"].set_index("archetype")["central"]
cj = lv[lv.target == "calculated-incl-energy"].set_index("archetype")["central"]
df = pd.DataFrame({"unit": cb.unit, "cb": cb.central, "cb_n": cb.n, "cb_low": cb.low, "cb_high": cb.high, "cf": cf, "cj": cj}).dropna(subset=["cb"])

ex = e[(e.parameter == "cost-levelized") & e.target.isna() & e.excluded.isna() & e["set-aside"].isna() & e["duplicate-of"].isna()]
PAT = {
    "incl-feedstock or selling price": r"feedstock|selling price|MFSP|MJSP|minimum .* price|production cost|incl(udes|uding)? (raw|material)",
    "incl-transport-storage or net removed": r"transport|storage|T&S|net removed",
    "market or price based": r"market price|price data|spot|plant-gate",
    "per unit of electricity": r"LCOE|per MWh|electricity",
    "abatement or incremental": r"abatement|avoided|incremental",
}
def tags(notes):
    t = set()
    for n in notes:
        for k, p in PAT.items():
            if re.search(p, str(n), re.I):
                t.add(k)
    return "; ".join(sorted(t))
info = ex.groupby("archetype").agg(sources=("source-id", lambda s: "; ".join(sorted(set(s)))),
                                   regions=("region", lambda s: "; ".join(sorted(set(map(str, s))))),
                                   rates=("discount-rate", lambda s: "; ".join(sorted(set(map(str, s.dropna()))))),
                                   basis_tags=("note", tags))
df = df.join(info)
both = df.dropna(subset=["cj"]).copy()
both["ratio_cb_cj"] = both.cb / both.cj
both["ratio_cb_cf"] = both.cb / both.cf
both.sort_values("ratio_cb_cj").to_csv(HERE / "levelized-compare.csv")

l = np.log(both[["cb", "cj", "cf"]].clip(lower=1e-9))
print("archetypes with a sourced levelized cost:", len(df), "; with both CB and CJ:", len(both))
print("correlation of log CB with log CJ: %.2f ; with log CF: %.2f" % (l.cb.corr(l.cj), l.cb.corr(l.cf)))
print("CB/CJ ratio quartiles:", both.ratio_cb_cj.quantile([.1, .25, .5, .75, .9]).round(2).to_dict())
print("within 0.67-1.5x:", ((both.ratio_cb_cj > 0.67) & (both.ratio_cb_cj < 1.5)).sum(), "; CB > 1.5 CJ:", (both.ratio_cb_cj >= 1.5).sum(), "; CB < 0.67 CJ:", (both.ratio_cb_cj <= 0.67).sum())
for t in PAT:
    s = both[both.basis_tags.str.contains(re.escape(t), na=False)]
    if len(s):
        print(f"  tag {t!r}: {len(s)} archetypes, median CB/CJ {s.ratio_cb_cj.median():.2f}")
s = both[both.basis_tags.eq("")]
print(f"  untagged: {len(s)} archetypes, median CB/CJ {s.ratio_cb_cj.median():.2f}, log corr {np.log(s.cb).corr(np.log(s.cj)):.2f}")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(both.sort_values("ratio_cb_cj")[["unit", "cb", "cj", "cf", "ratio_cb_cj", "cb_n", "basis_tags"]].round(2).to_string())
