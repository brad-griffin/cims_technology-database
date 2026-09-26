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

A source's generic `/unit` denominator means the service unit the source
reports for that step (UKERC: t of product, GJ, m3). It is read as that unit,
and as pu only when the source names none; a row per tonne on a GJ archetype is
therefore not pooled. A service unit that is not a physical product (UKERC's
"£k" of output) is never pooled. A row missing the basis parameter.csv requires for it (status review,
BASIS NOT RECORDED) is not pooled: an equipment cost and an installed cost
differ by up to a factor of two. It is converted where possible and marked
excluded until the basis is read back out of its source.
"""
from __future__ import annotations

import re
from collections import defaultdict

from .common import REFERENCE, fnum, read, split_list
from . import convert
from .currency import TARGET
from .wholeplant import NEEDS_HOST

PER_CAPACITY = {"capex", "opex-fixed", "decommissioning-cost"}
PER_OUTPUT = {"opex-variable", "opex-total", "cost-levelized"}
# parameters stated per unit of a product (or of product capacity): a basis factor
# (records/reference/example-conversion.csv) applies to these
PER_PRODUCT = {"specific-energy-consumption", "capacity", "annual-output"}
EXTENSIVE = {"capacity", "annual-output"}
PERCENT = {"efficiency", "efficiency-chp", "capacity-factor", "availability", "capture-rate",
           "emissions-reduction-potential", "load-range-min", "discount-rate",
           "cost-learning-rate", "capital-recovery", "degradation-rate"}
# A share of emissions avoided is one percentage whether the source counted CO2
# alone or CO2-equivalent, so the species is not a column of its own here.
SPECIES_POOLED = {"emissions-reduction-potential"}
GJ_PER_KW_YR = 8760 * 0.0036
OUTPUT_BASES = {"thermal-output", "electric-output", "product-output"}
# A derived cost written "<cost per t> / <GJ per t>" is per GJ of what the
# technology consumes, not of what it delivers (D13).
import re as _re
FUEL_INPUT_DIVISOR = _re.compile(r"^\s*[\d.eE+-]+\s*/\s*[\d.eE+-]+\s*$")
# An archetype carries absolute costs (design §2). A negative cost is a change
# against a baseline plant -- UKERC's measure costs are the cost of adding the
# measure, and a negative O&M is the saving it brings -- so it is not pooled.
NEGATIVE_COST = ("negative cost: a saving against the baseline plant, not the "
                 "archetype's own absolute cost")
SET_ASIDE = ("set aside: needs an efficiency factor. UKERC gives this cost per tonne of the "
             "host plant's product and only the fuel used per tonne; per GJ of output needs "
             "the efficiency (output = fuel x efficiency), which UKERC does not give")
FUEL_INPUT_NOTE = ("PER GJ OF FUEL INPUT: {parent} per tonne divided by the source's fuel use "
                   "per tonne")
UNIT_ALIAS = {"tonnes of mixed product": "t"}
# A cost with cost-basis `incremental` is the cost of adding something to an
# existing plant (a UK TIMES improvement or add-on, or an example listed in
# records/reference/incremental-cost.csv), so it is not a whole-plant cost.
INCREMENTAL_NOTE = ("set aside: needs a host-plant cost. The source prices this as the cost of "
                    "adding it to an existing plant, not as a whole plant")
PHYSICAL_SERVICE = {"t", "GJ", "m3", "m", "MWh"}


def service_unit(example: dict | None, pu: str) -> str:
    """What a source's generic `unit` denominator stands for in this example."""
    su = ((example or {}).get("service-unit-reported") or "").strip()
    su = UNIT_ALIAS.get(su, su)
    return su or pu


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
        self.factors = convert.Factors()

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
    """Adds value-norm, value-min-norm, value-max-norm, unit-norm, target-norm,
    duplicate-of and excluded to each fact row, in place."""
    # per example, what turns a rating or an absolute sum into a rate: the
    # SOURCE'S OWN factors only, and only on an output basis
    scale = defaultdict(dict)
    for r in facts:
        v = fnum(r.get("value"))
        if v is None:
            continue
        if r["parameter"] == "annual-output" and r.get("unit") == "GJ":
            scale[r["example-id"]].setdefault("annual-output", v)
        elif r["parameter"] == "capacity-factor":
            scale[r["example-id"]].setdefault("cf", v / 100 if v > 1.5 else v)
        elif (r["parameter"] == "capacity" and r.get("unit") in ("MW", "kW")
              and r.get("capacity-basis") in OUTPUT_BASES):
            mw = v / 1000 if r["unit"] == "kW" else v
            scale[r["example-id"]].setdefault("mw-out", (mw, r["record-id"]))
    by_id = {r["record-id"]: r for r in facts}
    incremental = {r["example-id"] for r in read(REFERENCE / "incremental-cost.csv")}
    if incremental - set(examples):
        raise SystemExit(f"incremental-cost.csv names unknown examples: {incremental - set(examples)}")
    for r in facts:
        if r["example-id"] in incremental and r["parameter"] in PER_CAPACITY | PER_OUTPUT:
            r["cost-basis"] = "incremental"

    for r in facts:
        r.update({"value-norm": "", "value-min-norm": "", "value-max-norm": "",
                  "unit-norm": "", "excluded": "", "conversion": "",
                  "target-norm": r.get("target", "")})
        if r["parameter"] in SPECIES_POOLED:
            r["target-norm"] = ""
        parent = by_id.get(r.get("derived-from", ""))
        r["duplicate-of"] = (parent["record-id"] if parent and r.get("value-type") == "derived"
                             and parent["parameter"] == r["parameter"]
                             and not r.get("derived-kind") else "")
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
        exrow, flist = units.factors.for_row(a["archetype"], r["example-id"])
        exf = [f for f in flist if exrow and f["factor-id"] in split_list(exrow.get("factor-id", ""))]
        alias = dict(x.split("=", 1) for x in split_list((exrow or {}).get("unit-alias", "")) if "=" in x)
        per_product = (p in PER_PRODUCT or p in PER_CAPACITY or p in PER_OUTPUT
                       or (p.startswith("emissions-") and p != "emissions-reduction-potential"))
        if exrow and exrow.get("factor-id") == "none" and per_product:
            r["excluded"] = ("reported per a product the archetype does not make, and no factor "
                             "links the two: " + (exrow.get("note") or ""))
            continue
        if (p == "cost-levelized" and a.get("family") == "heat-supply"
                and re.search(r"/(k|M)Wh\b", unit)
                and not re.search(r"per MWh of heat", r.get("note") or "", re.I)):
            r["excluded"] = ("a cost per unit of electricity (or of unstated output) on an archetype "
                             "whose product is heat: a CHP plant's cost per MWh of electricity is not "
                             "a cost per GJ of heat")
            continue
        bf = convert.basis_factor(exf) if per_product else None
        species_ok = a.get("product", "").lower().startswith("t co2") or "CO2" in tgt
        used = []
        if (p.startswith("emissions-") and pu == "GJ" and unit.endswith("/GJ")):
            # an emission factor per GJ of FUEL; the archetype's basis is per GJ
            # of OUTPUT, and the two differ by the efficiency (D13)
            r["excluded"] = "per GJ of fuel input, not per GJ of output"
            continue
        for k, s in UNIT_ALIAS.items():
            unit = unit.replace(k, s)
        if "/unit" in unit:
            su = service_unit(examples.get(r["example-id"]), pu)
            if su not in PHYSICAL_SERVICE:
                r["excluded"] = (f"per unit of the source's service ({su}), which is not a "
                                 "physical product")
                continue
            unit = unit.replace("/unit", f"/{su}")
        if not unit and tgt == "dimensionless":
            unit = tgt              # a ratio a source prints without a unit
        factor, offset, note = None, 0.0, ""
        m = convert.MONEY.match(unit)
        if m:
            cur = f"{m.group(1)}_{m.group(2)}"
            if cur not in units.cur:
                r["excluded"] = f"no currency factor for {cur}"
                continue
            f = units.cur[cur] * convert.MULT[m.group(3)]
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
            elif p in PER_CAPACITY and not d and pu == "GJ" and sc.get("mw-out"):
                mw, rid = sc["mw-out"]
                cf = sc.get("cf")
                factor = f / (mw * GJ_PER_KW_YR * 1000 * (cf or 1.0))
                note = (f"absolute sum over the source's own output capacity, {mw:.4g} MW "
                        f"({rid}), " + (f"at a {cf:.0%} capacity factor" if cf else "at nameplate"))
            else:
                ext = convert.intensive(unit, tgt, flist, species_ok, alias) if d else None
                if not ext:
                    r["excluded"] = (f"cost per {d or 'plant'} cannot be put per {td}: the source "
                                     "gives no output factor to convert it with")
                    continue
                factor, used = f * ext[0], ext[1]
                note = f"per {d} -> per {td}"
        else:
            route = units.physical(unit, tgt)
            if route is None:
                ext = (convert.extensive(unit, tgt, flist, alias) if p in EXTENSIVE
                       else convert.intensive(unit, tgt, flist, species_ok, alias))
                if not ext:
                    r["excluded"] = f"no conversion from {unit or '(none)'} to {tgt}"
                    continue
                route, used = (ext[0], 0.0), ext[1]
            factor, offset = route
        if bf:
            # the source reports per another product (per t aluminium on an alumina
            # archetype): per-product numbers divide by it, capacities multiply
            factor = factor * bf[0] if p in EXTENSIVE else factor / bf[0]
            used.append(bf[1])
        if used:
            note = (note + "; " if note else "") + "factor " + ", ".join(dict.fromkeys(used)) + \
                " (records/reference/conversion-factor.csv)"
        conv = lambda x: None if x is None else x * factor + offset
        r["value-norm"], r["value-min-norm"], r["value-max-norm"] = (
            "" if x is None else f"{x:.6g}" for x in (conv(v), conv(lo), conv(hi)))
        r["unit-norm"], r["conversion"] = tgt, note
        if (r.get("status") or "") == "review" and "BASIS NOT RECORDED" in (r.get("note") or ""):
            r["excluded"] = "a required basis (cost-basis or capacity-basis) is not recorded"
        elif p in PER_CAPACITY | PER_OUTPUT and any(x is not None and x < 0 for x in (v, lo, hi)):
            r["excluded"] = NEGATIVE_COST
        if r["duplicate-of"] and FUEL_INPUT_DIVISOR.search(r.get("formula") or "") and pu == "GJ":
            r["conversion"] = FUEL_INPUT_NOTE.format(parent=r["duplicate-of"])
            r["excluded"] = SET_ASIDE
    # A fixed O&M the source gives as a percentage of capital per year is put on the
    # example's own capital cost -- the same source's number, so it is only a
    # derivation -- where the example has one pooled capex (or one per case).
    capex = defaultdict(list)
    for r in facts:
        if r["parameter"] == "capex" and r.get("value-norm") and not r.get("excluded"):
            capex[r["example-id"]].append(r)
    for r in facts:
        u = (r.get("unit") or "").strip()
        if r["parameter"] != "opex-fixed" or not u.startswith("%") or r.get("value-norm"):
            continue
        cands = capex.get(r["example-id"], [])
        case = re.match(r"^\[([^\]]+)\]", r.get("note") or "")
        if case and len(cands) > 1:
            cands = [c for c in cands if (c.get("note") or "").startswith(f"[{case.group(1)}]")]
        if len({c["value-norm"] for c in cands}) != 1:
            r["excluded"] = ("percentage of capital cost: the example has "
                             + ("no pooled capital cost" if not cands else "several capital costs")
                             + " to put it on")
            continue
        c = cands[0]
        v, lo, hi = _num(r)
        cv = fnum(c["value-norm"])
        r["value-norm"], r["value-min-norm"], r["value-max-norm"] = (
            "" if x is None else f"{x / 100 * cv:.6g}" for x in (v, lo, hi))
        r["unit-norm"] = c["unit-norm"]
        r["excluded"] = ""
        r["conversion"] = f"percentage of the example's capital cost {c['record-id']} per year"
    # A derived row that restates its parent in another unit adds no information.
    # UKERC's per-GJ costs are the per-tonne cost divided by the fuel used per
    # tonne, i.e. per GJ of fuel INPUT. Where the parent could not be pooled either,
    # the reason stays the parent's.
    # The per-tonne rows those came from are set aside with them: on an
    # energy-service archetype both need the same missing efficiency.
    sec = {r["example-id"] for r in facts if r["parameter"] == "specific-energy-consumption"
           and (r.get("value") or "").strip()}
    for r in facts:
        a = records.by_key.get(r.get("archetype", ""))
        if (a and a["product-unit"] == "GJ" and r["parameter"] in PER_CAPACITY | PER_OUTPUT
                and "ukerc" in (r.get("via-source-id") or r.get("source-id") or "")
                and r["example-id"] in sec and r.get("value-type") != "derived"
                and (r.get("excluded") or "").startswith("cost per t")):
            r["excluded"] = SET_ASIDE
    for r in facts:
        if (r["parameter"] in PER_CAPACITY | PER_OUTPUT and r.get("cost-basis") == "incremental"
                and r.get("excluded") != "no number"):
            r["set-aside"], r["excluded"] = "needs-host-cost", INCREMENTAL_NOTE
            continue
        if r.get("set-aside") == "needs-host-cost" and r.get("excluded") != "no number":
            r["excluded"] = NEEDS_HOST
        elif r.get("whole-plant") and r.get("excluded") != "no number":
            r["excluded"] = (f"incremental: the whole-plant row {r['whole-plant']} adds the "
                             "host plant's baseline cost")
        elif r.get("excluded") == SET_ASIDE:
            r["set-aside"] = "needs-efficiency"
    for r in facts:
        if r.get("assembly-duplicate"):
            # an assembled sum the source also prints: a check, not a second value
            r["duplicate-of"] = r["assembly-duplicate"]
            r["excluded"] = ("assembly check: the sum of this source's component costs, "
                             "which it also prints as a total (duplicate-of); not pooled")
            continue
        if r.get("excluded") == SET_ASIDE:
            continue
        if r.get("duplicate-of") and r["excluded"] and r["excluded"] != "no number":
            par = by_id[r["duplicate-of"]]
            how = ("its per-tonne cost divided by fuel use per tonne"
                   if FUEL_INPUT_DIVISOR.search(r.get("formula") or "")
                   else "the same number in another unit")
            r["excluded"] = (f"duplicate of the row in duplicate-of: {how}"
                             + ("" if not par.get("excluded") else "; that row is not pooled either"))


FLOW_PER_UNIT = {"unit-baseline-output": None, "unit": None}   # None: the archetype's own unit


def normalise_flows(flows, records, units, examples=None) -> None:
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
        if per in FLOW_PER_UNIT:
            per = service_unit((examples or {}).get(r.get("example-id", "")), pu)
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
