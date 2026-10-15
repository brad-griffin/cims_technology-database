"""Lazard LCOE (gas peaking, combined cycle) restated at the database basis: same approach as lazard_model.py."""
import itertools, statistics, csv
from lazard_model import MACRS
MACRS[3] = [.3333, .4445, .1481, .0741]

def lazard(c, dep, esc_fuel, half=True, tax=.40, debt=.6, rd=.08, re=.12, esc=.0225):
    cap = c['capex']; gen = 8.76 * c['cf']  # MWh per kW-yr
    pmt = debt * cap * rd / (1 - (1 + rd) ** -c['life'])
    def npv(P):
        v = -(1 - debt) * cap; b = debt * cap
        for y in range(1, c['life'] + 1):
            f = (1 + esc) ** (y - 1)
            om = c['fom'] * f + c['vom'] * gen * f
            fuel = c['hr'] / 1000 * c['fuel'] * gen * (f if esc_fuel else 1)
            ebitda = P * gen - om - fuel
            i = b * rd; b -= pmt - i
            d = MACRS[dep][y - 1] * cap if y - 1 < len(MACRS[dep]) else 0
            cf = ebitda - pmt - tax * (ebitda - d - i)
            v += cf / (1 + re) ** (y - (0.5 if half else 0))
        return v
    lo, hi = 0, 2000
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if npv(m) > 0 else (m, hi)
    return (lo + hi) / 2

def ref(c, r=.08):
    gen = 8.76 * c['cf']; crf = r / (1 - (1 + r) ** -c['life'])
    return (c['capex'] * crf + c['fom']) / gen + c['vom'] + c['hr'] / 1000 * c['fuel']

C = [  # rid, bound, capex, fom, vom, hr, cf, printed
 ('tp-lazard_2024_001-0017','min',700,10,3.5,8000,.15,110), ('tp-lazard_2024_001-0017','max',1150,17,5.0,9800,.10,228),
 ('tp-lazard_2024_001-0035','min',850,10,2.75,6750,.90,45), ('tp-lazard_2024_001-0035','max',1300,25.5,5.0,7500,.30,108),
 ('tp-lazard_2023_001-0015','min',700,7,3.5,8000,.15,115), ('tp-lazard_2023_001-0015','max',1150,17,5.0,9800,.10,221),
 ('tp-lazard_2023_001-0033','min',650,10,2.75,6150,.90,39), ('tp-lazard_2023_001-0033','max',1300,17,5.0,6900,.30,101)]
cases = [dict(rid=a, bound=b, capex=k, fom=f, vom=v, hr=h, cf=cf, printed=p, life=20, fuel=3.45) for a, b, k, f, v, h, cf, p in C]
if __name__ == '__main__':
    res = []
    for dep, ef, half in itertools.product([3, 5, 7, 15, 20], [False, True], [False, True]):
        e = [lazard(c, dep, ef, half) / c['printed'] - 1 for c in cases]
        res.append((round(statistics.mean(map(abs, e)), 3), round(max(map(abs, e)), 3), dep, ef, half, [round(x, 2) for x in e]))
    res.sort()
    for r in res[:4]: print(r)
    dep, ef, half = res[0][2:5]
    out = []
    for c in cases:
        m = lazard(c, dep, ef, half); r = ref(c)
        out.append(dict(rid=c['rid'], bound=c['bound'], printed=c['printed'], model_lazard=round(m, 2), model_ref=round(r, 2), restated=round(c['printed'] - (m - r), 1), ratio=round((c['printed'] - (m - r)) / c['printed'], 3), fit_error=round(m / c['printed'] - 1, 3)))
    w = csv.DictWriter(open('lazard-lcoe-restated.csv', 'w', newline=''), fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    for o in out: print(o)
