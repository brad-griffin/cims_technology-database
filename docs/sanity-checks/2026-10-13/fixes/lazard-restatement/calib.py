import itertools, statistics
from lazard_model import lazard_lcoh, ref_lcoh
from lazard_cases import cases
fin = dict(debt=.4, rd=.08, re=.12, tax=.21)
res = []
for dep, ee, es, sc in itertools.product([5, 7, 15, 20], [False, True], [False, True], [False, True]):
    errs = []
    for c in cases:
        m = lazard_lcoh(c, fin, dep, c['infl'], ee, es, sc)
        errs.append(m / c['printed'] - 1)
    res.append((statistics.mean(abs(e) for e in errs), max(abs(e) for e in errs), dep, ee, es, sc, statistics.mean(errs)))
res.sort()
for r in res[:6]: print(['%.3f' % r[0], '%.3f' % r[1]] + list(r[2:6]) + ['bias %.3f' % r[6]])
