# Cases transcribed from the Key Assumptions pages (Lazard 2021 p.12; 2023 p.44)
cases = []
# 2021: alk then PEM; scales 1,20,100 MW; low/med/high efficiency
cap21 = {'alk': [[720,1460,2150],[430,860,1270],[310,630,920]], 'pem': [[970,1760,2490],[610,1110,1570],[460,840,1190]]}
stk21 = {'alk': [[240,480,710],[170,345,510],[145,295,435]], 'pem': [[320,580,820],[245,450,635],[215,395,555]]}
sh21 = {'alk': [60000,67500,75000], 'pem': [50000,60000,80000]}
h221 = {'alk': [[109,171,180],[2179,3426,3606],[10897,17128,18030]], 'pem': [[102,149,170],[2048,2988,3400],[10241,14939,17000]]}
lc21 = {'alk': [[5.85,4.40,4.75],[5.00,3.35,3.30],[4.90,3.25,3.20]], 'pem': [[6.70,5.45,5.30],[5.50,4.00,3.55],[5.40,3.90,3.45]]}
rec0 = {'alk': 13, 'pem': 130}
for t in ('alk','pem'):
    for si, kw in enumerate([1000, 20000, 100000]):
        for ei in range(3):
            n = rec0[t] + 13 * (si * 3 + ei)
            cases.append(dict(rid=f'tp-lazard_2021_001-{n:04d}', ed=2021, kw=kw, capex=cap21[t][si][ei], stack=stk21[t][si][ei],
                stack_h=sh21[t][ei], cf=0.98, life=20, mwh=kw/1000*8760*0.98, elec=40.0, water=0.021,
                h2_kg=h221[t][si][ei]*1000, printed=lc21[t][si][ei], infl=0.0225, bound=''))
# 2023 unsubsidised: low case = 100 MW, high case = 20 MW
c23 = [('tp-lazard_2023_001-0056', 'pem green', 943, 341, 2265, 1052, 60000, .55, 48, 7788, 1558, 4.77, 7.37),
       ('tp-lazard_2023_001-0071', 'alk green', 740, 203, 1984, 652, 67500, .55, 48, 8902, 1780, 3.79, 5.78),
       ('tp-lazard_2023_001-0086', 'pem pink', 1013, 341, 2335, 1052, 60000, .95, 35, 12744, 2549, 3.47, 5.29),
       ('tp-lazard_2023_001-0101', 'alk pink', 810, 203, 2054, 652, 67500, .95, 35, 14568, 2914, 2.75, 4.08)]
for rid, nm, capL, stL, capH, stH, sh, cf, el, h2L, h2H, lcL, lcH in c23:
    for bound, kw, cap, st, h2, lc in (('min', 100000, capL, stL, h2L, lcL), ('max', 20000, capH, stH, h2H, lcH)):
        cases.append(dict(rid=rid, ed=2023, kw=kw, capex=cap, stack=st, stack_h=sh, cf=cf, life=25, mwh=kw/1000*8760*cf,
            elec=el, water=0.005, h2_kg=h2*1000, printed=lc, infl=0.02, bound=bound))
