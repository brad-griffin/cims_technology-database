"""Put every example's facts on its archetype's basis.

Each archetype declares one `product-unit` (t for a kiln, GJ for a boiler).
Every number is converted to a unit fixed by the parameter and that product
unit, or left out with the reason written on its row. Nothing is averaged here;
this only makes numbers comparable. The as-reported value stays beside the
converted one in the output, and in the extraction it came from.

Target units, where pu is the archetype's product-unit:

  capex, opex-fixed                 2025_CAD per (pu/yr of capacity)
  opex-variable, opex-total         2025_CAD per pu
  abatement-cost                    2025_CAD per t CO2-eq
  specific-energy-consumption       GJ per pu
  emissions-* (species in target)   t per pu
  capacity                          MW when pu is GJ, kt/yr when pu is t
  shares, efficiencies, rates       %   (a COP is written as a % efficiency)
  lifetime, construction-time       years
  temperature, pressure             degC, bar

A source's generic `/unit` denominator means its own product unit and is read
as pu. A row missing the basis parameter.csv requires for it (status review,
BASIS NOT RECORDED) is not pooled: an equipment cost and an installed cost
differ by up to a factor of two. It is converted where possible and marked
excluded until the basis is read back out of its source.
"""
from __future__ import annotations

from collections import defaultdict

from .common import REFERENCE, fnum, read
from .currency import MONEY, TARGET

PER_CAPACITY = {"capex", "opex-fixed", "decommissioning-cost"}
PER_OUTPUT = {"opex-variable", "opex-total"}
PERCENT = {"efficiency", "efficiency-chp", "capacity-factor", "availability", "capture-rate",
           "emissions-reduction-potential", "load-range-min", "discount-rate",
           "cost-learning-rate", "capital-recovery", "degradation-rate"}
GJ_PER_KW_YR = 8760 * 0.0036
UNIT_ALIAS = {"tonnes of mixed product": "t"}


def target_unit(param: str, pu: str, default: str) -> str:
    if param in PER_CAPACITY:
        return f"{TARGET}/{pu}-per-yr"
    if param in PER_OUTPUT:
        return f"{TARGET}/{pu}"
    if param == "abatement-cost":
        return f"{TARGET}/t-CO2-eq"
    if param == "specific-energy-consumption":
        return f"GJ/{pu}"
    if param.startswith("emissions-") and param != "emissions-reduction-potential":
        return f"t/{pu}"
    if param == "capacity":
        return "MW" if pu == "GJ" else f"k{pu}/yr" if pu == "t" else f"{pu}/yr"
    if param == "annual-output":
        return pu
    if param in PERCENT:
        return "%"
    if param in ("lifetime", "construction-time"):
        return "years"
    if param == "temperature-output":
        return "degC"
    if param == "pressure-output":
        return "bar"
    return default


class Units:
    def __init__(self, cur_factors):
        self.table = {}
        for r in read(REFERENCE / "unit-conversion.csv"):
            f = fnum(r["factor"])
            if f is not None:
                self.table[(r["from-unit"], r["to-unit"])] = (f, fnum(r["offset"]) or 0.0)
        self.cur = cur_factors

    def physical(self, unit, target):
        """(factor, offset) from unit to target, or None."""
        if unit == target:
            return (1.0, 0.0)
        if (unit, target) in self.table:
            return self.table[(unit, target)]
        if "/" in unit and "/" in target:
            (n, d), (tn, td) = unit.split("/", 1), target.split("/", 1)
            if d == td and (n, tn) in self.table:
                return self.table[(n, tn)]
        return None


def _num(r):
    return fnum(r.get("value")), fnum(r.get("value-min")), fnum(r.get("value-max"))


def normalise(facts, examples, records, units) -> None:
    """Adds value-norm, value-min-norm, value-max-norm, unit-norm and excluded
    to each fact row, in place."""
    # per example, what turns a rating or an absolute sum into a rate
    scale = defaultdict(dict)
    for r in facts:
        v = fnum(r.get("value"))
        if v is None:
            continue
        if r["parameter"] == "annual-output" and r.get("unit") == "GJ":
            scale[r["example-id"]].setdefault("annual-output", v)
        elif r["parameter"] == "capacity-factor":
            scale[r["example-id"]].setdefault("cf", v / 100 if v > 1.5 else v)

    for r in facts:
        r.update({"value-norm": "", "value-min-norm": "", "value-max-norm": "",
                  "unit-norm": "", "excluded": "", "conversion": ""})
        v, lo, hi = _num(r)
        if v is None and lo is None and hi is None:
            r["excluded"] = "no number"
            continue
        a = records.by_key.get(r.get("archetype", ""))
        if not a:
            r["excluded"] = "example not mapped to an archetype"
            continue
        pu = a["product-unit"]
        p = r["parameter"]
        pdef = records.parameters.get(p, {})
        tgt = target_unit(p, pu, pdef.get("unit-default", "") or r.get("unit", ""))
        unit = (r.get("unit") or "").strip()
        if (p.startswith("emissions-") and pu == "GJ" and unit.endswith("/GJ")):
            # an emission factor per GJ of FUEL; the archetype's basis is per GJ
            # of OUTPUT, and the two differ by the efficiency (D13)
            r["excluded"] = "per GJ of fuel input, not per GJ of output"
            continue
        for k, s in UNIT_ALIAS.items():
            unit = unit.replace(k, s)
        unit = unit.replace("/unit", f"/{pu}")
        factor, offset, note = None, 0.0, ""
        m = MONEY.match(unit)
        if m:
            cur = m.group(0)
            if cur not in units.cur:
                r["excluded"] = f"no currency factor for {cur}"
                continue
            f = units.cur[cur]
            d = unit.split("/", 1)[1] if "/" in unit else ""
            td = tgt.split("/", 1)[1] if "/" in tgt else ""
            sc = scale.get(r["example-id"], {})
            if d == td:
                factor = f
            elif p in PER_CAPACITY and d == pu:
                factor, note = f, f"per {pu} read as per {pu} of annual capacity"
            elif p in PER_OUTPUT and d == f"{pu}-per-yr":
                factor, note = f, f"annual cost per {pu}/yr is a cost per {pu}"
            elif p in PER_CAPACITY and d == "kW" and pu == "GJ":
                cf = sc.get("cf")
                factor = f / (GJ_PER_KW_YR * (cf or 1.0))
                note = (f"per kW at a {cf:.0%} capacity factor" if cf
                        else "per kW at nameplate (no capacity factor)")
            elif p in PER_OUTPUT and d == "kWh" and pu == "GJ":
                factor, note = f / 0.0036, "per kWh -> per GJ"
            elif p in PER_CAPACITY and not d and pu == "GJ" and sc.get("annual-output"):
                factor = f / sc["annual-output"]
                note = "absolute sum over the annual output the same source states"
            else:
                r["excluded"] = f"cost per {d or 'plant'} cannot be put per {td}"
                continue
        else:
            route = units.physical(unit, tgt)
            if route is None:
                r["excluded"] = f"no conversion from {unit or '(none)'} to {tgt}"
                continue
            factor, offset = route
        conv = lambda x: None if x is None else x * factor + offset
        r["value-norm"], r["value-min-norm"], r["value-max-norm"] = (
            "" if x is None else f"{x:.6g}" for x in (conv(v), conv(lo), conv(hi)))
        r["unit-norm"], r["conversion"] = tgt, note
        if (r.get("status") or "") == "review" and "BASIS NOT RECORDED" in (r.get("note") or ""):
            r["excluded"] = "a required basis (cost-basis or capacity-basis) is not recorded"


FLOW_PER_UNIT = {"unit-baseline-output": None, "unit": None}   # None: the archetype's own unit


def normalise_flows(flows, records, units) -> None:
    """Flows per unit of the archetype's product: energy in GJ, mass in t,
    gas volumes in m3."""
    for r in flows:
        r.update({"value-norm": "", "value-min-norm": "", "value-max-norm": "",
                  "unit-norm": "", "excluded": "", "conversion": ""})
        a = records.by_key.get(r.get("archetype", ""))
        v, lo, hi = _num(r)
        if v is None and lo is None and hi is None:
            r["excluded"] = "no number"
            continue
        if not a:
            r["excluded"] = "example not mapped to an archetype"
            continue
        pu = a["product-unit"]
        per = (r.get("per-unit") or "").strip()
        per = UNIT_ALIAS.get(per, per)
        per = pu if per in FLOW_PER_UNIT else per
        if per != pu:
            r["excluded"] = f"per {per}, but the archetype's product is measured in {pu}"
            continue
        num = (r.get("unit") or "").split("/", 1)[0].replace("Nm3", "m3")
        cls = records.commodities.get(r["commodity"], {}).get("unit-default", "")
        tnum = "GJ" if num in ("GJ", "MJ", "kWh", "MWh") else "t" if num in ("kg", "t", "g") else num
        if cls and cls in ("GJ", "t") and tnum != cls and tnum in ("GJ", "t"):
            r["excluded"] = f"{r['commodity']} is measured in {cls}, the row in {num}"
            continue
        route = units.physical(num, tnum) if num != tnum else (1.0, 0.0)
        if route is None:
            r["excluded"] = f"no conversion from {num} to {tnum}"
            continue
        f, o = route
        conv = lambda x: None if x is None else x * f + o
        r["value-norm"], r["value-min-norm"], r["value-max-norm"] = (
            "" if x is None else f"{x:.6g}" for x in (conv(v), conv(lo), conv(hi)))
        r["unit-norm"] = f"{tnum}/{pu}"
