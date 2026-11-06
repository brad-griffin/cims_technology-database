"""Extract Cameco's monthly uranium prices from the saved web page.

    python data/raw-data/other-reports/cameco_price_extract.py

Reads cameco_2026_uranium-price.mhtml (the page https://www.cameco.com/invest/
markets/uranium-price, saved by the modeller; the page offers no download) and
writes cameco_2026_uranium-price.csv: month, series, value (US$ per lb U3O8),
how.

The page draws a Highcharts chart. Its accessibility labels give the visible
window (spot and long-term price, 61 months each) as text: these rows are
`how` = labelled. The chart's navigator draws the whole spot series (January
1988 onward) as an SVG path; its point heights map to prices by a straight line
fitted on the labelled months (the fit is exact to 1e-11), so those rows are
`how` = navigator, rounded to the cent as the page labels are. The page draws
no long-term price before the visible window. One navigator point repeats
(July 2019, the same value twice) and is dropped.
"""
from __future__ import annotations

import csv
import datetime as dt
import email
import re
import statistics
from pathlib import Path

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # extraction/
from paths import RECORDS, ROOT as REPO_ROOT, source_dirs  # noqa: E402
# documents in primary-sources/, extractions in data/raw_data/technology_database/ (2026-11-06)
DOCS, HERE = source_dirs(__file__)
SRC = DOCS / "cameco_2026_uranium-price.mhtml"
OUT = HERE / "cameco_2026_uranium-price.csv"
NAMES = {"Uranium Spot Price": "spot", "Long-term Uranium Price": "long-term"}


def html():
    msg = email.message_from_bytes(SRC.read_bytes())
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_payload(decode=True).decode("utf-8", "replace")
    raise SystemExit("no html part")


def navigator(h):
    i = h.find("highcharts-navigator-series")
    j = h.find('d="', i)
    k = h.find('"', j + 3)
    pts = []
    for seg in re.split(r"(?=[MCLZ])", h[j + 3:k]):
        if not seg.strip():
            continue
        v = [float(x) for x in re.findall(r"-?[\d.]+(?:e-?\d+)?", seg)]
        if seg[0] == "M":
            pts.append(v[0:2])
        elif seg[0] == "C":
            pts.append(v[4:6])
        elif seg[0] == "L":         # the area closes along the baseline: stop
            break
    return pts


def fit(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def main():
    h = html()
    labs = re.findall(r'aria-label="\w+, (\d+ \w+ \d{4}), ([\d.]+)\. '
                      r'(Uranium Spot Price|Long-term Uranium Price)\."', h)
    labelled = {}
    for d, v, s in labs:
        m = dt.datetime.strptime(d, "%d %b %Y").strftime("%Y-%m")
        labelled[(m, NAMES[s])] = float(v)
    spot = sorted((m, v) for (m, s), v in labelled.items() if s == "spot")

    pts = navigator(h)
    dedup = [pts[0]] + [p for q, p in zip(pts, pts[1:]) if p != q]
    tail = dedup[-len(spot):]
    a, b = fit([v for _, v in spot], [p[1] for p in tail])
    resid = max(abs(v - (p[1] - a) / b) for (_, v), p in zip(spot, tail))
    last = dt.date(int(spot[-1][0][:4]), int(spot[-1][0][5:]), 1)
    months = []
    y, mo = last.year, last.month
    for _ in dedup:
        months.append(f"{y:04d}-{mo:02d}")
        y, mo = (y, mo - 1) if mo > 1 else (y - 1, 12)
    months.reverse()

    rows = []
    for m, p in zip(months, dedup):
        if (m, "spot") in labelled:
            rows.append([m, "spot", f"{labelled[(m, 'spot')]:.2f}", "labelled"])
        else:
            rows.append([m, "spot", f"{(p[1] - a) / b:.2f}", "navigator"])
    for (m, s), v in sorted(labelled.items()):
        if s == "long-term":
            rows.append([m, s, f"{v:.2f}", "labelled"])
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["month", "series", "value", "unit", "how"])
        for r in rows:
            w.writerow(r[:3] + ["USD per lb U3O8"] + r[3:])
    print(f"  {OUT.name}: {len(rows)} rows ({months[0]} to {months[-1]}); "
          f"navigator fit max residual {resid:.1e}")


if __name__ == "__main__":
    main()
