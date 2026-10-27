"""Lazard LCOH cash-flow model: calibrate to printed LCOH, restate at the database's 8% real, pre-tax basis."""
import itertools

MACRS = {
    5: [.20, .32, .192, .1152, .1152, .0576],
    7: [.1429, .2449, .1749, .1249, .0893, .0892, .0893, .0446],
    15: [.05, .095, .0855, .077, .0693, .0623, .059, .059, .0591, .059, .0591, .059, .0591, .059, .0591, .0295],
    20: [.0375, .07219, .06677, .06177, .05713, .05285, .04888, .04522, .04462, .04461, .04462, .04461, .04462, .04461, .04462, .04461, .04462, .04461, .04462, .04461, .02231],
}

def stack_years(stack_h, cf, life):
    step = stack_h / (8760 * cf)
    ys, t = [], step
    while t < life - 1e-9:
        ys.append(int(round(t)) if round(t) >= 1 else 1)
        t += step
    return ys

def cashflows(c, infl, esc_elec, esc_stack):
    """yearly nominal costs (excluding capex at t0), and output"""
    life = c['life']
    capex = c['capex'] * c['kw']
    stack = c['stack'] * c['kw']
    rows = []
    sy = stack_years(c['stack_h'], c['cf'], life)
    for y in range(1, life + 1):
        f = (1 + infl) ** (y - 1)
        om = 0.015 * capex * f
        wi = 0.01 * capex * (1.01) ** (y - 1)
        el = c['mwh'] * c['elec'] * (f if esc_elec else 1)
        wa = c['h2_kg'] * c['water'] * (f if esc_elec else 1)
        st = stack * sy.count(y) * ((1 + infl) ** y if esc_stack else 1)
        rows.append(dict(om=om, wi=wi, el=el, wa=wa, st=st))
    return capex, rows

def lazard_lcoh(c, fin, dep, infl, esc_elec, esc_stack, stack_cap):
    capex, rows = cashflows(c, infl, esc_elec, esc_stack)
    life = c['life']; H = c['h2_kg']
    debt = fin['debt'] * capex; eq = capex - debt
    rd, re, tax = fin['rd'], fin['re'], fin['tax']
    pmt = debt * rd / (1 - (1 + rd) ** -life)
    bal = debt
    sched = MACRS[dep] if dep else None
    # depreciation of capex (and capitalised stacks: 5-yr straight line from replacement)
    depn = [0.0] * (life + 1)
    for i, d in enumerate(sched):
        if i + 1 <= life: depn[i + 1] += d * capex
    if stack_cap:
        for y, r in enumerate(rows, 1):
            if r['st']:
                for k, d in enumerate(MACRS[7]):
                    if y + k <= life: depn[y + k] += d * r['st']
    def npv_eq(P):
        v = -eq; b = bal
        for y, r in enumerate(rows, 1):
            interest = b * rd; princ = pmt - interest; b -= princ
            opex = r['om'] + r['wi'] + r['el'] + r['wa'] + (0 if stack_cap else r['st'])
            rev = P * H
            taxable = rev - opex - interest - depn[y]
            cf = rev - opex - pmt - tax * taxable - (r['st'] if stack_cap else 0)
            v += cf / (1 + re) ** y
        return v
    lo, hi = 0.0, 100.0
    for _ in range(80):
        m = (lo + hi) / 2
        if npv_eq(m) > 0: hi = m
        else: lo = m
    return (lo + hi) / 2

def ref_lcoh(c, r=0.08):
    """constant-dollar, pre-tax, capital recovered at r real; no escalation beyond W&I real ~0"""
    life = c['life']; capex = c['capex'] * c['kw']; stack = c['stack'] * c['kw']; H = c['h2_kg']
    crf = r / (1 - (1 + r) ** -life)
    pv_stack = sum(stack / (1 + r) ** y for y in stack_years(c['stack_h'], c['cf'], life))
    annual = (capex + pv_stack) * crf + 0.025 * capex + c['mwh'] * c['elec'] + H * c['water']
    return annual / H, dict(capital=(capex + pv_stack) * crf / H, fixed=0.025 * capex / H,
                            elec=c['mwh'] * c['elec'] / H, water=c['water'])
