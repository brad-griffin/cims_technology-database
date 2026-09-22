# Note: end-use technology table

Record: `design/build/tech_rows.py` (493 rows, 434 distinct technologies, all 86
end uses covered), which generates `design/end-use-technology-table.csv`. Edit the
record, not the CSV: `python design/build/build_md.py` rebuilds the CSV and then
renders it into `design/sector-end-use-table.md` as a Technologies table under each
sector's end-use table. `tech_rows.py` can also be run on its own to rebuild just
the CSV.

## Purpose

Same as the sector/end-use table: these are the **classes of technology to find
data for**, not a mapping of data already held. 147 rows have no `roster-match`
and 238 have no `cims-match` — those blanks mark what the database and CIMS do
not yet carry, and are the gap list.

## Columns

`sector, end-use, technology, type, description, energy-inputs,
specific-energy-use, trl, trl-basis, examples, roster-match, cims-match,
sources, note`

`specific-energy-use` is **empty throughout**, by decision — efficient variants
should eventually carry their own absolute energy use rather than a percentage
against the base technology, so the column waits for sources.

## Scope rules

- Both existing conventional and prospective technologies; generally TRL ≥ 5–6.
- Generic names, with detail added only where needed to tell two technologies
  apart. Naming convention `equipment_carrier_variant`, `-` within a component
  and `_` between components.
- One technology per row with a **carrier list**, rather than a row per carrier.
- **Canadian stock only** for the conventional rows.
- Efficient variants are separate rows when the literature treats them as a major
  improvement, not a tweak.
- Ceiling about **10 technologies per end use** (max reached: heat-medium-temp 11,
  heat-low-temp 10). Mean 5.4.
- Examples go in their own column, not in parentheses in the technology name.
- Research was not restricted to sources already on disk; web sources were added
  to the Sources tables as used.

## CCS rows (2026-09-14)

A host technology that could reasonably carry capture gets its own row, named
`<host>_ccs-concentrated` or `<host>_ccs-diffuse`. **The suffix is the pointer:**
it names the cross-sector capture end use that holds the capture plant, so the
host row repeats none of the capture cost or energy and carries only the
host-side facts - the steam drawn for regeneration, the heat source the plant
needs, the capture rate reachable on that stream.

- Concentrated: the stream is already nitrogen-free - ammonia and hydrogen
  shift gas, gas-processing acid gas, gas-based DRI top gas, gasifier shift gas,
  fermentation off-gas, and the oxygen-blown and indirectly heated routes.
- Diffuse: flue gas - boilers, CHP, fired heaters, blast furnace, cement and
  lime kilns, cracker furnaces, FCC regenerators, recovery boilers.
- Integrated routes that concentrate the stream as part of the process
  (oxy-fuel kiln, oxy-fuel lime kiln, oxy-fuel FCC, ATR with full capture,
  top-gas recycling, bath smelting reduction) keep their existing row; their
  note says which capture end use they draw on.
- 16 rows added. No CCS row where capture is not a serious option for the host:
  EAF off-gas, sinter strands, aluminium pot lines, the Bayer process.

## Efficiency buckets (2026-09-14)

Incremental measures are not listed one per row. Where several measures sit on
the same device, the table carries a bucket row named for the roster variant it
corresponds to - `<equipment>_efficiency-moderate` or `_efficiency-strong`, the
two the roster uses (design doc s6.2, about 15% energy saving separating them) -
and **the individual measures go in the examples column**. So the blast furnace
carries a moderate row whose examples are the top-pressure recovery turbine,
improved burden distribution and higher pulverised coal injection, and a strong
row for hot stove and slag heat recovery.

23 bucket rows, covering blast furnace, basic oxygen furnace, coke oven, sinter
plant, reheating furnace, hot rolling mill, cement kiln, fired heater, reformer,
generating set, turbine and engine drive, smelting vessel and clean-in-place.
Six of them replace rows that used to name a single measure (coke dry quenching,
sinter waste-gas recirculation, recuperative burners on reheating, the efficient
hot rolling mill, the upgraded preheater and cooler, smelter oxygen enrichment);
those measures are now the examples on their bucket.

A named technology that a model would choose in its own right is NOT bucketed -
the condensing boiler, the shoe press, thin-slab casting, the heat-pump dryer,
premium-efficiency motors and variable-speed drives all stay as themselves. The
`efficiency-base` bucket is the incumbent with no measures applied, so it maps
to the conventional row and is not a loss.

## Type vocabulary (four labels)

| type | count |
|---|---|
| conventional | 145 |
| efficient variant | 85 |
| alternative | 84 |
| prospective | 79 |

## Counts by sector

cross-sector 94, oil-and-gas 51, iron-and-steel 40, non-ferrous-metals 37,
mining 32, pulp-and-paper 26, chemicals 24, other-industry 18,
food-and-beverage 17, non-metallic-minerals 16, biofuels 15,
petroleum-refining 12, cement 11.

## TRL sourcing order

1. IEA ETP Clean Energy Technology Guide 2024 rows file
   (`iea_2024_clean-tech-guide_rows.csv`, 891 rows with `trl-latest`), cited as
   `iea_2024_001 row N` — the workhorse.
2. IPCC AR6 Table 11.3.
3. UKERC, via the roster.
4. "commercial" where a technology is in ordinary commercial use.
5. "assessed" where only project or pilot evidence was found.

`trl-basis` records which of these applied.

## Build scripts

Now copied into `design/build/` (they were only in the session VM's scratch
before, where a VM reset would have lost them): `tech_rows.py` (all 393 rows), `md_notes.py` (NOTE / FIELD / SRC
overrides), `heat_source.py` (HS / HD / NOTE_ADD), `md_head.md`, `md_tail.md`,
`build_md.py` (renderer: `strip()`, `norm()` merging citation keys, `heat()`,
`hsrc()`, `c()` for `<sector>` → `[sector]`, `degC` → `°C`, `|` → `/`).
`build_md.py` reads the two CSVs, applies the overrides and writes
`design/sector-end-use-table.md`; it expects the other files beside it.

## Defects found along the way (also recorded in the .md)

- CIMS NB and NL refining files spell `Distillation.Atmospheric` as
  `NBmospheric` / `NLmospheric` — a region-prefix strip that ate the word.
- CIMS `Petroleum Refining.Steam` `NG CCS` requests 66.5 t CO2 per unit — a
  ×1000 slip.
- Harmonized `tp-1509` stores a DAC abatement cost of 2.0 USD/t instead of the
  ~94–232 the source gives.
- Harmonized `capture-unit` conflates CIMS methane blowdown capture with IPCC
  concentrated-CO2 capture.
- Food ovens filed as high-temp though the sources say 100–232 °C.
- Post-aggregation roster `description` fields are unreliable.

## Open items

- Fill `specific-energy-use` from sources.
- Sourced energy-saving figures for the efficient variants.
- Register NREL 97 / NREL 118 and the ~16 web sources in the source manifest.
