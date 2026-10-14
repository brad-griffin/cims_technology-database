import csv
from lazard_model import lazard_lcoh, ref_lcoh
from lazard_cases import cases
fin = dict(debt=.4, rd=.08, re=.12, tax=.21)
cfg = {2021: (20, True, True, True), 2023: (5, False, False, False)}
out = []
for c in cases:
    m = lazard_lcoh(c, fin, *cfg[c['ed']][:1], c['infl'], *cfg[c['ed']][1:])
    r, parts = ref_lcoh(c)
    restated = c['printed'] - (m - r)
    out.append(dict(rid=c['rid'], bound=c['bound'], printed=c['printed'], model_lazard=round(m, 3), model_ref=round(r, 3),
                    delta=round(m - r, 3), restated=round(restated, 2), ratio=round(restated / c['printed'], 3), fit_error=round(m / c['printed'] - 1, 3)))
w = csv.DictWriter(open('lazard-restated.csv', 'w', newline=''), fieldnames=list(out[0]))
w.writeheader(); w.writerows(out)
for o in out: print(o)
