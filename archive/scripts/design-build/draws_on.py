"""The `draws-on` column: what an end use calls on, and how to read it.

One column replaces the old `heat-delivery` and the hand-maintained
`heat_source.HS` display dict, which stated the same fact twice and had drifted
on four end uses.  A cell is a list of parts separated by "; ":

    integral (kiln, precalciner and cooler); fans-and-blowers (cooler fans)

Each part is `target (duty)`.  The target is another end use's id, or one of
the two reserved words:

    integral   the end use's own equipment does it; no link
    none       it calls on nothing

**Every part carries its own parenthetical** (the user, 2026-09-15), including
single-part cells, so the duty is always named.  A semicolon can appear inside
a parenthetical, so split at depth zero -- `split_parts` does that.

The link records a DEMAND, not a second place the energy is counted: the energy
stays on the target end use.  This is the integral-vs-supplied rule extended
past heat, and it is what lets a sector end use keep its own detail while the
technologies stay centralized on the cross-sector one.
"""
from __future__ import annotations

import re

PART = re.compile(r'^([a-z0-9-]+)\s*\((.+)\)$')
RESERVED = ('integral', 'none')


def split_parts(cell: str) -> list[str]:
    """Split on '; ' at parenthesis depth zero."""
    out, cur, depth = [], '', 0
    for ch in cell or '':
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ';' and depth == 0:
            out.append(cur.strip()); cur = ''
            continue
        cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse(cell: str) -> list[tuple[str, str]]:
    """-> [(target, duty)], target being an end-use id, 'integral' or 'none'."""
    out = []
    for part in split_parts(cell):
        if part == 'none':
            out.append(('none', '')); continue
        m = PART.match(part)
        if not m:
            raise ValueError(f'draws-on part is not `target (duty)`: {part!r}')
        out.append((m.group(1), m.group(2)))
    return out


def check(rows: list[dict]) -> None:
    """Every reference resolves, and every part is parenthesized."""
    ids = {r['end-use'] for r in rows}
    for r in rows:
        for target, duty in parse(r['draws-on']):
            if target in RESERVED:
                continue
            if target not in ids:
                raise AssertionError(
                    f"{r['end-use']}: draws-on names {target!r}, which is not an end use")
            if not duty:
                raise AssertionError(f"{r['end-use']}: {target} has no duty in brackets")


def drawn_on_by(rows: list[dict]) -> dict[str, list[str]]:
    """The reverse index, generated: end use -> the end uses that call on it."""
    out: dict[str, list[str]] = {}
    for r in rows:
        for target, _ in parse(r['draws-on']):
            if target not in RESERVED:
                out.setdefault(target, []).append(r['end-use'])
    return out
