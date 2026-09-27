"""Heating-value basis: every energy quantity in the database is on a HIGHER
heating value (HHV, gross calorific value) basis (design.md s5, 2026-09-26).

Most sources do not say which basis they use. A number whose basis the source
does not state is read as HHV and marked `not stated` in `heating-value`; one the
source states as HHV is used as it is. One the source states as LOWER heating
value (LHV) is converted, using the ratio of the two heating values of the fuel
going in and of the product coming out, as records/reference/
heating-value-stream.csv names them for the archetype (the ratios are factors in
conversion-factor.csv, class `property`). An LHV number on an archetype with no
row there is not pooled.

What changes, with r = HHV/LHV of a stream (1 for electricity, heat or a
stream the table leaves blank):

  efficiency, efficiency-chp        x r_out / r_in      (output over input energy)
  specific energy use (energy/pu)   x r_in, and / r_out when pu is GJ of product
  a cost or emission per GJ of pu   / r_out
  capacity or output in energy      x r_out (output basis), x r_in (input basis)

Anything else (a cost per tonne, a lifetime) does not depend on the basis, and
its `heating-value` cell stays blank.
"""
from __future__ import annotations

import re

from .common import REFERENCE, fnum, read

NOT_STATED = re.compile(r"\b(HHV|LHV)\b[^.]{0,25}not stated|not state (LHV|HHV)|"
                        r"basis NOT STATED|basis not stated", re.I)
ALL_CLAIM = re.compile(r"all energy quantities[^.]*?\b(HHV|LHV)\b", re.I)
LHV = re.compile(r"\bLHV\b|lower heating value|net calorific", re.I)
HHV = re.compile(r"\bHHV\b|higher heating value|gross calorific", re.I)
ENERGY = {"GJ", "MJ", "kJ", "TJ", "PJ", "kWh", "MWh", "GWh", "Btu", "kBtu", "MMBtu", "mmBtu"}
ENERGY_RATE = {"MW", "kW", "W", "GW", "MWth", "kWth", "GJ/h", "MJ/h", "MJ/s", "GJ/yr", "TJ/yr", "PJ/yr"}
EFFICIENCY = {"efficiency", "efficiency-chp"}
INPUT_BASES = {"thermal-input", "electric-input"}


def reported(text: str) -> str:
    """The basis a row's note says it is on: 'HHV', 'LHV' or '' (not stated).
    The first explicit mention wins ("HHV. The catalog also gives LHV")."""
    text = text or ""
    m = ALL_CLAIM.search(text)
    if m:
        return m.group(1).upper()
    if NOT_STATED.search(text):
        return ""
    lo, hi = LHV.search(text), HHV.search(text)
    if lo and hi:
        return "LHV" if lo.start() < hi.start() else "HHV"
    return "LHV" if lo else "HHV" if hi else ""


def kind(param: str, unit: str, pu: str, capacity_basis: str, per_pu: bool) -> str:
    """How a number depends on the heating value, or '' if it does not."""
    num = (unit or "").split("/", 1)[0]
    if param in EFFICIENCY:
        return "efficiency"
    if param == "specific-energy-consumption" and num in ENERGY:
        return "energy-use"
    if param in ("capacity", "annual-output") and (unit in ENERGY_RATE or num in ENERGY):
        return "capacity-in" if capacity_basis in INPUT_BASES else "capacity-out"
    if pu == "GJ" and per_pu:
        return "per-product"
    return ""


class Streams:
    def __init__(self, factors):
        self.rows = {r["archetype"]: r for r in read(REFERENCE / "heating-value-stream.csv")}
        self.factors = factors

    def _r(self, fid):
        if not fid:
            return 1.0
        f = self.factors.rows.get(fid)
        return fnum(f["factor"]) if f else None

    def to_hhv(self, archetype: str, how: str, pu: str):
        """(multiplier, [factor ids]) that puts an LHV number on HHV, or None when
        the archetype's streams are not recorded."""
        s = self.rows.get(archetype)
        if not s:
            return None
        fin, fout = s.get("fuel-in", "").strip(), s.get("product-out", "").strip()
        rin, rout = self._r(fin), self._r(fout)
        if rin is None or rout is None:
            return None
        m = {"efficiency": rout / rin,
             "energy-use": rin / (rout if pu == "GJ" else 1.0),
             "per-product": 1 / rout,
             "capacity-out": rout,
             "capacity-in": rin}[how]
        used = {"efficiency": [fout, fin], "energy-use": [fin] + ([fout] if pu == "GJ" else []),
                "per-product": [fout], "capacity-out": [fout], "capacity-in": [fin]}[how]
        return m, [u for u in used if u]
