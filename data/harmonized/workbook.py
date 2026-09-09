"""Workbook-wide view settings, in one place so the three builders agree.

build-template.py creates technology-database-template.xlsx and build-wide.py
and build-source-list.py add sheets to it afterwards, so a setting applied in
only one of them survives until the next script runs and then quietly does not.
Each builder calls apply_view(wb) immediately before saving, which makes the
setting idempotent and independent of the order the builders run in.
"""
from __future__ import annotations

# The wide views are wide -- 104 columns on wide-technology -- so the default
# 100% shows about four columns of a sector band at a time. 75% is the point
# where a band reads as a band without the body text going grey.
ZOOM = 75


def apply_view(wb) -> None:
    """Set every sheet in `wb` to the house zoom."""
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = ZOOM
        # zoomScaleNormal is what Excel restores when leaving page-break or
        # page-layout view; without it a round trip through either resets to 100%.
        ws.sheet_view.zoomScaleNormal = ZOOM
