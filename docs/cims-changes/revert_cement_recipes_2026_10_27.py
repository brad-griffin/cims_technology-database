"""Undo apply_cement_recipes_2026_10_27.py: remove the rows it added to the CIMS
industrial-minerals model inputs (the four recipe techs at Products.Cement and the
Calcined Clay and Ground Slag nodes).

Usage: python revert_cement_recipes_2026_10_27.py <cims>/data/model_inputs/model/industrial_minerals
"""
import glob
import os
import sys

SRC = "EMRG technology database 2026-10-27"
TECHS = {"LC3 calcined clay cement", "Slag blended cement", "Alkali-activated cement",
         "Electrochemical cement"}


def added(l):
    b = l.split(",")
    if len(b) < 6:
        return False
    if ".Products.Cement.Calcined Clay" in b[0] or ".Products.Cement.Ground Slag" in b[0]:
        return True
    return b[0].endswith(".Products.Cement") and b[5] in TECHS


def main(folder):
    for f in sorted(glob.glob(os.path.join(folder, "industrial_minerals_*.csv"))):
        raw = open(f, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in raw else "\n"
        L = raw.split(nl)
        keep = [l for l in L if not added(l)]
        left = sum(SRC in l for l in keep)
        open(f, "w", encoding="utf-8", newline="").write(nl.join(keep))
        print(f, "rows removed", len(L) - len(keep), "marker rows left", left)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
