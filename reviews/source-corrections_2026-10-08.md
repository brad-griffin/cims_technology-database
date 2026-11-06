# Source corrections: first pass (2026-10-08)

Brad asked for a review of every held source for values set aside because the
source prints them wrongly (a typo, a wrong unit or basis), and for those values to
be taken in on an assumed correction, with a note and a marker.

## How it works

`records/reference/source-correction.csv` lists each correction (sc-NNN) with the
figure as printed, what was changed, the evidence and who decided. Stage 5d
(`pipeline/correction.py`) applies it:

| kind | what it does | record id |
| - | - | - |
| add | a value the extraction set aside (`_other-values`) becomes a new row on its example | `tp-<source>-xNNN` |
| replace | a corrected copy of a loaded row; the original stays, excluded as superseded | `tp-<source>-xNNN` |
| mark | a row the extraction had already corrected is tagged the same way; value unchanged | unchanged |

The marker on every such row:
- `correction` column = sc-NNN (example-parameter.csv);
- note starts `ASSUMED CORRECTION (sc-NNN): ... As printed: ... Evidence: ...`;
- conversion factor `assume:source-correction-sc-NNN`, so the conversion-class is `assumption`;
- summaries: `n-corrected` (archetype-parameter.csv, archetype-flow.csv), also counted in `n-external`;
- wide view: `source-corrections` column (e.g. `opex-fixed 1/5`); the workbook shades the value purple.

Rule (design.md §7): a correction is made only where the source itself (its own totals,
other tables, sibling rows, physical bounds) shows what was meant. Where two readings
stay plausible, the figure stays out.

## Corrections made (37)

**Added (5): values that had been left out**

| id | source | archetype | value |
| - | - | - | - |
| sc-001, sc-002 | DEA 2026 sheets 45.1.a and 45.2.a (geothermal DH with heat pump, 1200 m) | geothermal-well_direct-use | fixed O&M printed 500,000 EUR/MW/yr, read as 50,000 (the other 45.x sheets print 55,000-60,000; 500,000 would be 20% of capex a year). The two sheets are one figure, pooled once. Central 3.57 -> 3.00 CAD/GJ-yr. |
| sc-003 | Johansson 2012 Table 7, NGCC at 4,700 kJ/kg | capture-unit_amine | OPEX printed 66,068 kEUR/y, read as 6,068 (the row's own 17 EUR/t avoided x 356 kt = 6,050) -> 8.74 EUR/t captured |
| sc-004 | Kermeli 2016 p.79 | melting-furnace_regenerative-oxy-fuel (stack melter) | "electricity 600 kWh/ton" taken as natural gas (stack melters are gas-fired; 600 kWh/st = 1,024 Btu/lb beside the 955 Btu/lb gas on the same page) |
| sc-005 | Otto 2017 Sect. 5.4 | shaft-furnace_direct-reduction | Circored Trinidad capacity printed "65 t/a", read as 65 t/h (about 0.5 Mt/yr, the plant's published nameplate - outside knowledge) |

**Replaced (2): loaded values that were wrong as printed**

| id | row | change |
| - | - | - |
| sc-006 | tp-gielen_1997_001-0230, chlor-alkali membrane cell fixed O&M 2020 | 10 -> 100 ECU/t-yr (the series prints 100 / 10 / 100 with capex and variable O&M constant). Removes the low outlier: the archetype's fixed O&M is now one figure, 280 CAD/t-yr. |
| sc-007 | tp-ietd_2013_001-0118, grate cooler conversion | low end US$.044 -> 0.44 per annual t (IETD itself flags it; Martin 1999 gives 0.4-0.5). Still set aside as an incremental cost. |

**Marked (30): rows the extraction had already corrected**, so they now carry the same
marker: ETSAP I03 semi-wet kiln SEC (Table 7 cell copied from the wrong row), ETSAP
biogas CHP output (MWh/hr -> MWh/yr) and the capacity factor derived from it, Suhr
tissue heat (MJ/t -> GJ/t, 3 rows), EPA 2006 plunger-lift capex (per-year label), IEAGHG
2013 reboiler steam (MJ/t -> GJ/t, 4 rows; the two capture-energy rows derived from them
inherit the marker), Rehfeldt blast-furnace electricity ("060" -> 0.60), de Beer thin-slab
capex ("/thm" -> per t strip capacity, 2 rows), ESMAP coke oven (Mtce -> tce, 2 rows),
ICF LDC LDAR (7 -> 68.4 Mcf/yr), Wallace fuel cell (kWh -> kW), DOE 2023 clay calcination
(TJ -> GJ), Kermeli stainless foundry gas (267.2 -> 26.7), Galitsky MVR (MWh -> MW), NCCP
2000 co-generation capex (US$/kWh -> US$/kW, 9 rows). Eighteen of the 30 are on examples
not mapped to an archetype or excluded for another reason, so they carry the marker but
do not change a pooled value.

## Considered and not corrected

| source | figure | why it stays out |
| - | - | - |
| DEA 2026 storage 140 (PTES) | fixed O&M 2.5 M EUR/GWh/yr vs note G's ~28,000 EUR/storage/yr | the archetype's storage costs are per kWh of storage and cannot be put on its per GJ-yr basis, so a corrected figure would be excluded too |
| DEA 2026 storage 150, 151b, 151c | O&M printed 1e-5 (really M EUR), cavern size 1,100 MWh vs 1.1 TWh | examples mapped to (none) |
| DEA 2026 renewable fuels, SOEC 100 MW | rows shifted one line (lifetime 25,000 years, etc.) | the shift cannot be undone row by row from the extraction alone; needs a re-read of the workbook. The 10 MW SOEC sheet already supplies those parameters |
| DEA 2026 oil boiler | construction time 25 years (the lifetime) | the sheet's lifetime row already carries 25; nothing to recover for construction time |
| DEA 2026 solar O&M, MIDDEN lifetimes of 1 year and tc0360 O&M | (excluded-row.csv) | re-read 2026-10-05: no single slip gives a plausible figure |
| Barthe 2015 refining BREF | progressive distillation and visbreaker capex "per t/yr" | per t/h, per t/d and per bpd all give plausible plants; the evidence does not choose |
| Cusano 2017 NFM BREF | QSL electricity 9,000,000 MWh/yr; roaster heat 3.5 MJ/t | right magnitude not determinable; no parameter for the second |
| Galitsky 2003 corn wet milling | steepwater thermal energy in "TBtu" | unit not determinable |
| Daniels 2002 | CCF limestone 4.44 t/t | looks copied from another table; the true figure is not printed |
| Fleiter 2012 | measure 16 fuel saving 6.67 MJ/t | 667 or 770 both possible |
| ENS 2015 | pasteuriser investment 10.5 | misprint or merged columns; unresolved |
| IEAGHG 2018 TR03 | Ozcan hybrid electricity "0..79"; Anantharaman steam 6-9E-5 | Ozcan example mapped to (none); no single slip for the second |
| DOE 2025 liftoff | TES energy capex "$/kW capacity" (per kWh) | per-kWh storage costs cannot be put on thermal-storage_electric's basis (as for Spees 2023) |
| Concawe 2019 Table A.1.1-1 | refinery unit energy in "MMBtu/bbl" (thousand Btu) | a reprint of DOE 2015 refining bandwidth, which is held and extracted directly |
| EPA 2011 PRO 104 | CO2 and CO reductions apparently swapped | no matching parameter on reciprocating-engine_drive |
| EPA 2012 coke (3.4 MMBtu/ton printed 2.9 GJ/t), DOE 2024 coal gasification 230 Nm3/h, EPA 1999 service line $250,000, Ricardo-AEA MgO £220,000, RTC 2022 heat pump $/MMBtu, Brandt OPGEE kWh/Btu, Cusano Waelz CO2, ETSAP refinery capex per bpd, ETSAP fuel-cell per-system price | flagged in the extractions | examples not mapped to an archetype (or not loaded); correct them if those examples are ever mapped |
| Denis-Ryan 2016, Devlin 2023, Kim 2022, Toktarova 2020, Otto 2017 ASU factors, Schorcht cement CO2 and MgO enthalpy, Gielen dolomite, Vakkilainen, Neuwahl | unit slips in context figures | not technology parameters, or no technology/carrier |

## Non-typo fixes applied (Brad, 2026-10-08)

- **ETSAP I03 per t cement on per-t-clinker kilns.** New kind `rebase` in
  `source-correction.csv` (sc-038 to sc-042): the rows stated per t of cement
  (tp-etsap_2010_003-0006, -0008, -0011, -0014, -0015: O&M and CO2 of the reference,
  post-combustion and oxy-fuel plants) are restated per t clinker with the brief's own
  0.91 t clinker per t cement (factor `cf-clinker-per-cement-etsap-i03`, class
  same-source) as rows -x001 to -x005; the originals are excluded as superseded. A
  rebase is not a correction of the source, so it carries no `correction` marker; its
  note starts SAME-SOURCE REBASE and its conversion factors name the ratio. Capex
  (Table 7, per t clinker) is unchanged. Effect: O&M +9.9% (36 -> 39.6 EUR/t clinker,
  45 -> 49.5 oxy-fuel); CO2 770 -> 846 kg/t clinker.
- **DEA renewable fuels uncertainty multipliers.** Where a multiplier row matches
  exactly one main-file row of the same sheet (29 rows), the extraction now carries
  central x multiplier as value-min/value-max, with a RANGE note; 12 of them sit on
  mapped archetypes and are pooled. The other 21 (flow quantities, per-input shares,
  1/1 ranges) stay in `_other-values` only.
- **Plant costs with the capacity in the note.** Capacity rows added to the
  extractions where the source prints the plant's own capacity and the archetype's
  product matches it: Barthe 2015 Table 4.11 hydrotreaters (1.5 Mt/yr feed; capex
  80-100 and 200-300 M EUR now pooled per t-yr) and Vattenfall 2018 plasma kiln (1 Mt
  clinker/yr; 276.2 and 303.8 M EUR pooled, the 47.5 M EUR plasma-system-only row
  excluded as partial scope in excluded-row.csv). Not done: CSI/ECRA 2017 and
  Almeida-Benalcazar 2022 already carry derived per-t-yr rows, so nothing was lost;
  Element Energy 2018 mixes an equipment cost and a whole-system cost on one example;
  Vattenfall's and Gardarsdottir's capture costs are per clinker plant while the
  capture archetype is per t CO2; NCCP 1999 pairs a cost range with a size band
  without saying which end matches which. Barthe's annual opex (M EUR/yr) still does
  not pool: opex-total is per t of output and the build divides annual sums only for
  per-capacity parameters.
