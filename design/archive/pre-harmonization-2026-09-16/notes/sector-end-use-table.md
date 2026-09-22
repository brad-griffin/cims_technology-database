# Note: sector / end-use table

Record: `design/sector-end-use-table.csv` (86 end uses, 14 sector groups).
Readable build: `design/sector-end-use-table.md`.

## Purpose

The table sets out the **categories of information to look for**, not a mapping of
what the database already holds. Empty cells are the point: they are the gap list
that later source-hunting works through. The harmonized layer is not rewired to
match it — this is a design table only.

## Columns

`sector, end-use, end-use-label, covers, service-unit, heat-tier,
heat-demand-temp, heat-delivery, steam, energy-inputs, cims-services,
harmonized-now, sources, note`

## Decisions

- **Heat bands are heat-demand temperature, not steam conditions**: <150 / 150–400
  / >400 °C, matching the design doc §2 tiers. The user corrected an earlier
  reading that took them as steam-condition bands.
- **Integral vs supplied heat.** Heat released inside the unit that does the
  transformation belongs to the sector end use (integral). Heat delivered from a
  separable system belongs to a cross-sector heat band (supplied). This mirrors
  CIMS's own `<sector>.Steam` and `Petroleum Refining.Direct Heat` nodes. The
  `heat-delivery` cell names both where both apply, each with a `(...)` saying
  where it comes from.
- **End-use granularity rule** (widened 2026-09-15). Each end use is specific to
  a single end use, because each will likely become its own CIMS node. Keep it at
  the most general aggregation that still captures a real difference in energy use
  **or in emissions**. Two end uses may be generalised together when the
  generalisation is natural (different casting methods under casting); they may
  not be bundled when the energy service differs, when the emissions differ in
  kind or in how they are abated, or when a policy instrument treats them
  separately. Emissions were added because venting, flaring and fugitives are
  barely energy services at all, and splitting them turns on abatement and
  regulation rather than on fuel.
- **CO2 capture split into three** — concentrated / diffuse / DAC — because CIMS
  prices one CCS service per sector regardless of stream purity:
  Chemical Products.CCS 1.0 GJ NG/t and $153 per t-per-yr (concentrated-like)
  against Iron and Steel 4.29/$514, Industrial Minerals 4.84/$589,
  Petroleum Refining 3.38/$692.
- **Sectors.** Non-ferrous metals kept separate (electric smelting sits there).
  Biofuels split out as its own sector; renewable diesel moved into it.
  Oil and gas extraction added, with pipelines.
- **Splits made:** `space-cooling-and-ventilation` → `space-cooling` +
  `ventilation`; `wood-drying-and-pressing` split; papermaking →
  `paper-forming` + `paper-drying`; iron and steel finishing → `casting`,
  `reheating`, `rolling`, `annealing-and-coating` (four, down from six).
  `machine-drive` and mining `separation-and-processing` deliberately left whole.

## Cross-sector end uses (17)

heat-low-temp, heat-medium-temp, heat-high-temp, on-site-power-generation,
pumping, fans-and-blowers, compressed-air, materials-handling,
materials-processing, space-heating, space-cooling, ventilation, lighting,
mobile-equipment, co2-capture-concentrated, co2-capture-diffuse,
direct-air-capture.

## Venting, flaring and fugitives, 2026-09-15 (split the same day)

Two oil-and-gas end uses, `venting-and-flaring` (7 technologies) and
`fugitive-emissions` (4). The four abatement rows that were sitting on
`oil-and-gas-production` (pneumatic controllers, instrument air, vapour and
flare gas recovery, plunger lift) moved to venting and flaring, along with new
flare and blowdown-recompression rows; leak detection, continuous monitoring,
low-emission components and dry gas seals make up fugitives.

**Why they are separate.** The abatement options do not compete: venting and
flaring are cut by substituting equipment, fugitives by a programme - survey
frequency, monitoring, low-leak components. Vented and flared volumes scale with
throughput and discrete events and are largely metered; leak volumes scale with
component count and stock age and are inferred from emission factors or
top-down measurement. Canadian methane regulation sets venting limits and
flaring conservation separately from LDAR frequency, and CIMS carries the
branches separately. Flaring stays with venting because it competes with it as a
destruction route. Continuous monitoring sits with fugitives, where it
substitutes for survey frequency, though it also catches vent events.

The service is tonnes of methane rather than energy; the unit is the gas
disposed of on an energy basis, so it sits beside the other end uses. Most of
the CIMS venting and fugitive services are still unmapped in the harmonized
layer, and the one that is mapped sits on `capture-unit`, which conflates
methane blowdown capture with CO2 capture - the crosswalk now sends those CIMS
rows here instead.

## Restructure, 2026-09-14

Four cross-sector end uses were retired and machine drive was split.

- **CHP is a technology, not an end use.** Cogeneration now sits on
  `heat-low-temp` and `heat-medium-temp` as a technology supplying the band,
  with electricity as a co-product (design doc D1). Most CHP-served heat goes to
  duties below 150 degC - food, pulp and paper, basic chemicals - but refining
  and iron and steel take 68% and 100% of their steam-served heat at 150-400
  degC, so both bands carry it.
- **On-site hydrogen moved to the host sector**: `refinery-hydrogen`
  (petroleum refining) and `upgrader-hydrogen` (oil and gas). Reformers integral
  to ammonia, methanol and DRI stay where they were. Biogas and RNG became a
  biofuels end use, `renewable-natural-gas`.
- **A hydrogen sector was added** for off-site supply:
  `centralised-hydrogen-production` and `hydrogen-distribution`. Production for
  sale is sized by the merchant market rather than by one host process, and the
  distribution energy is what distinguishes centralised supply from production
  at the point of use.
- **Air separation moved to the two sectors that size it**:
  `steel-oxygen-supply` and `smelter-oxygen-supply`. Glass oxy-fuel firing,
  oxy-fuel capture and merchant industrial gases are not carried as end uses.
- **Process cooling moved to food and beverage** as `refrigeration`. Chemical
  and gas-plant refrigeration stays inside the process end use it serves.
- **Machine drive split into the EIA MECS categories**: pumping, fans and
  blowers, compressed air, materials handling and materials processing. The
  MECS residual is not carried: motor-driven equipment none of the five covers
  is filed under materials processing. Pipeline pumping and compression stay
  with oil and gas, and
  process electricity already counted in a sector end use - EAF, electrolysis,
  refiners, comminution, cement grinding, rolling - stays there.

## The `draws-on` column (2026-09-15)

One validated list per end use replaced the CSV's `heat-delivery` column *and*
the hand-maintained `heat_source.HS` display dict, which stated the same fact
twice and had drifted on four end uses.

Format: `target (duty)` parts separated by `; `, where the target is another end
use's id or one of the reserved words `integral` / `none`. **Every part carries
its own parenthetical**, including single-part cells.

`draws_on.py` parses it - splitting at parenthesis depth zero, so a duty may
contain a semicolon - checks that every reference resolves to a real end use,
and generates the reverse index. `build_md.py` renders it three ways: heat
targets into the Heat source column, everything else into a Draws on column, and
"Drawn on by" appended to each target's note.

**The link records a demand, not a second place the energy is counted.** A
sector end use lists only its own equipment; anything a separable cross-sector
system supplies is a link. That is the integral-vs-supplied rule extended past
heat, and it is what lets the technologies stay centralised while the sector
keeps its own end-use detail. 114 links across 14 targets; the most drawn on are
`heat-low-temp` (29), `fans-and-blowers` (22), `pumping` (18) and
`compressed-air` (12).

## Water end uses, 2026-09-15

Three sector end uses, added rather than treated as generic pumping:
`pulp-and-paper/effluent-treatment` (aeration is one of the largest electricity
loads in a mill after the refiners and the paper machine, and anaerobic
treatment turns part of it into recovered biogas),
`mining/water-and-tailings-management` (driven by the site water balance and the
discharge permit, not by ore throughput - dewatering runs whether or not the
mill does) and `oil-and-gas/produced-water-handling` (the water plant is part of
what sets the SAGD steam-to-oil ratio; disposal injection carries its own energy
and its own regulatory constraint). 13 technologies between them. Food and
beverage effluent was left out for now.

## Presentation rules for the .md

- Source references live in their own column, not inline in prose cells.
- No justification-of-decision text in the tables; notes carry facts and scope only.
- No CIMS services column in the readable build.
- Blank line and horizontal rule between sector sections; extra space between tables.
- `<sector>` in override dicts renders as `[sector]` (a bare `[sector]` is eaten
  by the bracket-citation regex).

## CIMS coverage check

14 CIMS sectors, 426 distinct services, 407 mapped, 19 unmapped (14 fuel-blend
nodes, 2 agricultural inputs, 3 venting/fugitive services). Region prefix
`CIMS.CAN.<XX>.` is stripped; FIC/DIC/DCC/market_share_limits are parameter
overlays, not sectors.
