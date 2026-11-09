# Follow-up to the 2026-11-07 consistency fixes (2026-11-09)

Brad's requests of 2026-11-09, what I found, and what I changed. Rebuilt and rechecked: all build checks pass, and the consistency check has no open findings (76 rows, each accepted by a ruling).

## 1. Cement kilns: coal and petroleum coke co-fired (Brad)

- kiln_dry-precalciner and kiln_legacy (and their variants) now co-fire coal and petroleum coke, in the Canadian ratio: coal 41% and petroleum coke 13% of clinker energy, 1996-1998 average (NRCan 2001, CIPEC cement clinker benchmark, Figure 2). That gives coal 76% and petroleum coke 24% of the fuel.
- `reference/fuel-choice.csv` has a new `shares` column for a mix with set shares.

| Archetype | Coal (GJ/t clinker) | Petroleum coke (GJ/t clinker) |
| - | - | - |
| Dry precalciner kiln | 2.43 (was 3.19) | 0.77 |
| Legacy kiln | 3.45 | 1.09 |

The precalciner's sourced combustion CO2 (0.293 t/t) is still within the factor range of this fuel mix.

## 2. Gas-turbine CHP energy use (source review)

- **The error:** the pooled energy row (3.10 GJ/GJ) rested mostly on LeMar 2001 Table 2 (13 of 16 rows). That table prints heat rates in Btu per kWh **of electricity**, and the build had read them as fuel per GJ **of heat**. I checked this against the PDF: 3,412 / heat rate = the printed electric efficiency.
- **The same error** affected the LeMar rows on the reciprocating-engine and fuel-cell CHP archetypes.
- **The fix:** all 21 LeMar rows are restated per GJ of useful heat with each row's own electric and overall efficiencies. These are same-source rebases, sc-196 onward in `source-correction.csv`, with their factors in `conversion-factor.csv`.
- **Energy use per GJ of heat:**
  - The archetype value stays 2.46. It comes from the pooled overall efficiency (74%, n57) and heat-to-power ratio (1.22, n39), which give heat efficiency 40.7% and electric 33.3%.
  - The corrected LeMar rows give 1.7-2.1, because LeMar's overall efficiencies (85-90%) are high.
  - IEAGHG 2007 gives 1.91, and Johansson 2012 gives 3.1 (a combined cycle supplying a reboiler).
  - 2.46 sits inside that spread and matches typical gas-turbine CHP (30-35% electric, 40-45% heat).

## 3. Absorption chiller

- **Is 62.5% more realistic?** Yes, for a single-effect chiller.
- **The sources:**
  - Kermeli 2011 and Stuckrath 2022 both give 1.6 GJ of heat per GJ of cooling (a COP of 0.63).
  - Norman 2013 gives 70% (single-effect) and 100% (double-effect).
  - JRC 2009 gives 70% and 120%.
- **The old value:** 100% was the double-effect case, which needs high-pressure steam or direct firing and does not match the archetype's 1.6 GJ/GJ heat row.
- **Single-effect against double-effect:** most industrial absorption chillers run on low-grade steam, hot water, or waste heat (single-effect, COP 0.6-0.75). A double-effect archetype would be a separate, more efficient option. Your call: I have not split the archetype.

## 4. Oxy-fuel kiln, catalytic N2O unit, combined-cycle lifetime

- **kiln_oxy-fuel (I replaced the Fable call):**
  - Captured CO2 = 90% share-to-capture x gross (combustion 0.332 + process 0.476 = 0.808) = 0.727.
  - Net total = 0.081, close to the sourced nets (0.075-0.10; median 0.094).
  - The pooled captured 0.766 implied 95% capture of this gross, against the 90% every source assumes. The earlier identity net of 0.042 inherited that.
- **reactor_catalytic-n2o (the Fable reading was wrong):**
  - The 1.83 t CO2 per t N2O comes from EC 2007 LVIC-AAF BREF Section 3.4.8, 0.0155 t CO2 per t HNO3.
  - It is the natural gas burned as the reducing agent in non-selective catalytic reduction (NSCR). That is real CO2, but from a different, fuel-using technique than the archetype's secondary and tertiary catalysts.
  - The combustion CO2 stays 0, and the row is kept as as-sourced with the correct reason.
- **Combined cycle lifetime:**
  - The host's 22.5 years was the median of EIA 40, Lazard 2023 20, Lazard 2024 20, and Weidmann 25.
  - Lazard's 2024 edition reprints the 2023 assumption, so it is now pooled once.
  - Host and capture variant are now 25 years.
- **Bug found and fixed:** 16 emission rows written by the 2026-11-07 fixes carried a "%" unit instead of t per unit of product. They took it from emissions-reduction-potential. Affected archetypes: fuel-cell CHP, lime-mud kiln, reheating furnace strong, rotary hearth DR, top-gas-recycling BF, indirect calciner, catalytic N2O, electrolytic Haber-Bosch, and steam cracker moderate. The values were right; only the unit label was wrong. The consistency check now tests emission units.

## 5. Source re-reads

- **pipeline_hydrogen (S102): fixed.**
  - **The source check:** the capex (86.6 CAD per GJ/yr) came from ANL HDSAM 'Cost Data' C122. That cell is the pipeline-**compressor** cost equation, per kW of compressor power, not pipe cost per kW of hydrogen carried.
  - **Now:** both rows are ruled out. The capex is drafted from HDSAM's own transmission-pipe cost (1.246 million 2019 USD per mile) on the US DOE Liftoff 2024 reference line (600 t/d over 300 km; p.18, Fig. 13, checked against the page image): 12.95 CAD per GJ/yr, with annual output 24.9 million GJ/yr.
  - **Result:** calculated levelized cost 1.9 CAD/GJ (was 12.7), against Liftoff's 0.1 USD/kg (about 1.0 CAD/GJ). Both points on Liftoff's figure are 0.1 USD/kg.
- **reactor_biomass-flash-pyrolysis: confirmed, no change.**
  - Gielen 1996 p.77 gives 3,000-6,000 NLG per t **ethylene**, total cost. It includes biomass (about a third) and small-scale labour and capital, and the build restates it per t HVC (3,300 CAD).
  - Joosten 1998's capex gives a non-energy cost of 490 CAD/t, plus 131 for biomass energy.
  - The gap is source disagreement on capital and labour, between two speculative 1990s estimates. It is not a reading error.
- **reactor_co2-to-dme: confirmed, no change.**
  - Schemme 2020 gives 1.49 EUR/kg DME (p.15), with hydrogen at 4.6 EUR/kg from electrolysis. Hydrogen is about 1,240 EUR of the 1,490 EUR/t.
  - The calculated 838 CAD/t prices the same hydrogen feed (38.5 GJ/t) at the database's reference hydrogen price (from the steam methane reformer, about 2.4 CAD/kg).
  - The gap is the hydrogen price basis.
- **motor_variable-speed (S154): confirmed.**
  - The sources give drive (ASD) efficiency of 95-98% (DOE 2012 tip sheet; JRC 2009; LBNL 2022).
  - With a premium motor of about 94%, that makes 91% motor plus drive, so energy is 1.099 GJ per GJ shaft.
  - McKane 2010's whole-system figures stay ruled out. The 0.82 system saving belongs to the driven system (pump or fan). In CIMS it is a service-demand saving, not a motor efficiency.

## 6. The 248 added carriers: confirmed

| Kind of addition | Count |
| - | - |
| Capture energy on capture variants (steam and electricity from the capture add-on) | 63 |
| Carriers efficient and capture variants inherit from their host | 58 |
| Sourced extra lines (mostly fan, pump, and drive electricity beside a fuel) | 102 |
| Drafted carriers with a rationale | 25 |

All are real energy uses that the declared lists had missed. Two to keep an eye on:
- **reactor_haber-bosch-electrolytic:** natural gas 1.45 GJ/t (the earlier Fable flag).
- **digester_semi-chemical:** sourced fuel 1.40 GJ/t beside steam 5.82. This might be the boiler fuel counted twice, but it is sourced from three examples, so I left it.

## 7. Second round (Brad, 2026-11-09)

### Fermenter capture: in proportion to the whole mix (Brad)

- **Brad's rule:** a capture archetype captures CO2 in proportion to the complete fossil and biogenic mix in the stream sent to capture.
- **What changed:**
  - I removed the biogenic-only override.
  - The capture rule now reads the host's fossil CO2 as its total, or else its combustion plus process CO2. The host fermenter has no total row, so before this change the rule saw no fossil CO2 at all.
- **Result for fermenter_grain-dry-mill_ccs-concentrated:**
  - The host mix is 0.0054 fossil and 0.032 biogenic (14% fossil).
  - Of the 0.029 t/GJ captured, 0.0042 comes off the fossil total and 0.025 off the biogenic CO2.
  - Net fossil total: 0.0012 t/GJ (was 0.0054). Biogenic: 0.0072 t/GJ (was 0.003).

### Electrolytic Haber-Bosch natural gas: removed

- **What the source says:** IEA 2013's 1.35 GJ/t is the "SEC H2 to product" column of Annex 5, Table 8: the energy of the hydrogen-to-ammonia synthesis step in an all-electric route. The extraction had tagged it as fuel.
- **The fix:**
  - The row is re-targeted to electricity (sc-217).
  - The judgement that named the fuel natural gas is rejected.
  - Hydrogen and natural gas are removed from the declared carrier list. The hydrogen is made inside the archetype from electricity, and the list sync had added natural gas.
- **Result:**
  - The archetype is all electricity: 38.4 GJ/t, the pooled electricity median from 9 examples (the 40.2 total had been one MIDDEN card).
  - Combustion CO2 is 0.

### Semi-chemical pulping digester steam and fuel: scope problem, not changed yet

- **Where the values come from:** Jacobs 2006 (DOE bandwidth study, Table 4.5 and the area tables pp.94-95), repeated in Kramer 2009.
- **What they cover:** the **whole semi-chemical pulping line**, not the digester.
  - Steam 6.42 MMBtu per short ton is wood prep 0.25, cooking 2.24, evaporation 3.40, and lime kiln or chemical preparation 0.53.
  - The direct fuel (1.17) is all in the lime kiln or chemical-preparation area.
- **The conflict:**
  - The kraft digesters are on a cooking-only basis (steam 1.9-4.4 GJ/t).
  - Evaporation and the lime kiln are separate chemical-recovery nodes in the hierarchy.
  - So the semi-chemical digester counts recovery energy twice, if CIMS also sends it to chemical recovery.
- **Proposed fix:** restate the Jacobs and Kramer rows to the cooking area with the source's own area shares:
  - average: steam 2.60 and electricity 1.47 GJ/t;
  - BAT: steam 2.21 and electricity 1.40 GJ/t;
  - fuel moves to the chemical-recovery nodes.

  The archetype's total would fall from 9.30 to about 4 GJ/t. Waiting for Brad's go-ahead.

### Cement fuel mix: the 2001 mix no longer fits (not changed yet)

NRCan Comprehensive Energy Use Database, Table 46, Canadian cement industry, 2022:

| Fuel | PJ | Share of fuel |
| - | - | - |
| Natural gas | 21.0 | 39% |
| Petroleum coke and still gas | 20.0 | 37% |
| Coal | 8.3 | 16% |
| Other (waste fuels and steam) | 4.0 | 8% |
| Heavy fuel oil | 0.1 | |
| Electricity | 8.9 | not a fuel |

2021 is similar. In 1996-1998, coal was 41% of clinker energy and petroleum coke 13%. Petroleum coke and natural gas have since overtaken coal.
