"""Clean-up passes on the facts as loaded, before they meet an archetype.

None of these changes what a source said. They evaluate arithmetic a source
wrote as a formula, spell each unit one way, write fractions as percent, link a
derived capex row to the row it came from, flag a quantified row missing the
basis parameter.csv requires, and number records within each source so that a
record id is citable: tp-ukerc_2013_001-0042 is the 42nd row taken from UKERC.
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict

from .common import VOCAB, currency_year, read

UNIT_SPELLING = {"C": "degC", "c": "degC", "degrees C": "degC",
                 "kgeCO2/unit": "kg/unit", "kgCO2/unit": "kg/unit",
                 "tCO2/unit": "t/unit", "yrs": "years", "yr": "years",
                 # added 2026-10-02: spellings only, no change of quantity
                 "tCO2/t": "t/t", "short-t/yr": "short-ton/yr", "g/GJ_i": "g/GJ"}
# trailing species spellings in a money unit (EUR/t-co2e is EUR/t-CO2-eq)
SPECIES_SPELLING = (("/t-co2e", "/t-CO2-eq"), ("/t-co2eq", "/t-CO2-eq"))
FRACTION = {"fraction": "%", "fraction/yr": "%/yr"}
BASIS_NOTE = ("  BASIS NOT RECORDED: parameter.csv requires a {col} for {param} "
              "and this extraction does not give one. Marked for review rather "
              "than guessed.")


def _arith(expr):
    """Value of a formula made only of numbers and + - * / **, else None.
    Formulas that name another parameter are the extraction template's job."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None
    ok = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub,
          ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd)
    if not all(isinstance(n, ok) for n in ast.walk(tree)):
        return None
    try:
        return eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, {})
    except Exception:
        return None


def clean(facts, flows, cons) -> dict:
    stats = defaultdict(int)
    # "REVIEW:" in an extraction note marks the row for review; it is still pooled
    for r in facts + flows + cons:
        if "REVIEW:" in (r.get("note") or "") and r.get("status") == "draft":
            r["status"] = "review"
            stats["rows marked REVIEW"] += 1
    for r in facts:
        if not r.get("value") and r.get("formula"):
            v = _arith(r["formula"])
            if v is not None:
                r["value"] = f"{v:.6g}"
                stats["formulas evaluated"] += 1
    for r in facts:
        if r.get("unit") in UNIT_SPELLING:
            r["unit"] = UNIT_SPELLING[r["unit"]]
        for a, b in SPECIES_SPELLING:
            if (r.get("unit") or "").endswith(a):
                r["unit"] = r["unit"][: -len(a)] + b
    for r in facts:
        if r.get("unit") in FRACTION:
            for k in ("value", "value-min", "value-max"):
                v = (r.get(k) or "").strip()
                if v:
                    try:
                        r[k] = f"{float(v) * 100:.6g}"
                    except ValueError:
                        pass
            if r.get("formula"):
                r["formula"] = f"({r['formula']}) * 100"
            r["unit"] = FRACTION[r["unit"]]
            stats["fractions written as %"] += 1

    # a derived capex points at the as-reported capex of the same example
    asrep = {}
    for r in facts:
        if r["parameter"] == "capex" and not r.get("formula"):
            asrep.setdefault((r["example-id"], r.get("region", "")), r["record-id"])
    for r in facts:
        if r["parameter"] == "capex" and r.get("formula") and not r.get("derived-from"):
            src = asrep.get((r["example-id"], r.get("region", "")))
            if src:
                r["derived-from"] = src
                stats["derived rows linked"] += 1

    # the basis each parameter requires, read from the dictionary
    basis_req = {r["parameter"]: (r.get("basis-required") or "").strip()
                 for r in read(VOCAB / "parameter.csv")
                 if (r.get("basis-required") or "").strip()}
    for r in facts:
        col = basis_req.get(r["parameter"], "")
        if not col or not (r.get("value") or r.get("value-min") or r.get("value-max")):
            continue
        if (r.get(col) or "").strip():
            continue
        stats["rows missing a required basis"] += 1
        if r.get("status") == "draft":
            r["status"] = "review"
        if "BASIS NOT RECORDED" not in (r.get("note") or ""):
            r["note"] = (r.get("note") or "") + BASIS_NOTE.format(col=col, param=r["parameter"])

    bad = [r["record-id"] for r in facts
           if (r.get("currency") or "") != currency_year(r.get("unit", ""))]
    if bad:
        sys.exit(f"currency is not the currency-year of unit on {len(bad)} rows: {bad[:5]}")

    remap = _renumber(facts, "tp")
    _renumber(flows, "tf")
    _renumber(cons, "tc")
    dangling = []
    for r in facts:
        refs = [x.strip() for x in (r.get("derived-from") or "").split(";") if x.strip()]
        if refs:
            out = []
            for ref in refs:
                (out if ref in remap else dangling).append(remap.get(ref, f"{r['record-id']}->{ref}"))
            r["derived-from"] = "; ".join(out)
    if dangling:
        sys.exit(f"derived-from does not resolve after renumbering: {dangling[:5]}")
    ids = [r["record-id"] for r in facts]
    assert len(ids) == len(set(ids)), "record-id is not unique"
    return dict(stats)


def _renumber(rows, prefix):
    seq, remap = defaultdict(int), {}
    for r in rows:
        sid = (r.get("source-id") or "").strip() or "unattributed"
        seq[sid] += 1
        new = f"{prefix}-{sid}-{seq[sid]:04d}"
        remap[r["record-id"]] = new
        r["record-id"] = new
    return remap
