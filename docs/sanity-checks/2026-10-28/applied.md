# Sanity-check rulings applied (2026-10-28)

Brad ruled on the open items on 2026-10-28. This file records what changed. I tested every change in a build on the Linux VM, and all checks pass. The outputs are left at the last commit, because a Linux build rewrites unrelated output fields (source-file names, the currency table). Run `python data/harmonized/build.py` on Windows, then commit.

## Code (pipeline)

| Item | Change | Effect |
| - | - | - |
| S151 | `m3-km` unit (convert.py, PHYSICAL_SERVICE) | Pump station per m3-km: 5e-5 GJ/m3-km (0.4 bar/km), 30-year life |
| IS009, MCF011 | `id-total-from-parts` replaces a sourced total more than 10% below combustion + process, where the parts are sourced, identities or estimates. Totals net of capture are left alone, and so is smelting reduction (net of export gas, batch C) | DR shaft 0.453 to 0.53; regenerative glass 0.263 to 0.41; direct heater 0.057 to 0.065; tunnel kiln 0.17 to 0.21; polymer extrusion 0.052 to 0.08 |
| MCF014 | The fuel identity replaces a combustion range midpoint that implies a factor above every listed fuel, where the identity sits inside the source's range | Long rotary lime kiln combustion 0.71 to 0.44 |
| OG002 | `pool-as-plant` scope on est-cost-ratio-opex-fixed | Flare-gas recovery fixed O&M 268 to 46 (3% of capex) |
| RX017 | Energy-use bands floored at zero (summarise.py) | Delayed coker steam low -0.16 to 0. Why it went negative: Abella's PRELIM assay range runs to -20 lb/bbl, where the coker exports steam |
| RX019 | Class-lifetime bands from the members' 10th-90th percentile | Cooling tower lifetime 20 (10-25), was (1-25) |
| S07 | `records/reference/pair-saving.csv`: a same-source base/improved pair read as a saving on the host | Heat-integrated column 4.47 to 2.46 GJ/t |

## Records

- **Precedent fixes:**
  - MCF021: Gielen brick VOM out.
  - NFM015: measure abatement costs out of the hosts.
  - OG018: crystallizer to mining.
  - RX020: system-measure lives out.
  - RX022: names.
  - CHEM018: electric-drive ammonia rows out.
- **HPCH012:** Weidmann's SMM-W1 efficiencies are out. The EIA and NREL whole-plant net efficiencies (host and capture) are retargeted to electricity (sc-135 to sc-175). NGCC goes 49.1 to 54.1, and its capture variant 50.5 to 49.2.
- **PB014:** CO2-to-gasoline and pyrolysis oil are per GJ:
  - new factors cf-gasoline-hhv-mass (47.3) and cf-gasoline-density;
  - pyrolysis oil on the paraffinic-diesel factors;
  - Jones 2013's scf/gal natural gas put in GJ/gal (sc-176).
- **RX013, RX012:** drafted sizes:
  - heat treatment 15 kt/yr;
  - crucible 2 kt/yr;
  - isothermal 10 kt/yr;
  - rotary oxy-fuel 20 kt/yr;
  - mine dewatering 18,900 GJ/yr;
  - diesel field engine 5,200 GJ/yr.
- **RX019:** cooling tower energy 0.21 to 0.04 GJ/GJ.
- **CHEM005, CHEM009, CHEM016:** sources re-read and confirmed; no change.
- **CHEM011:** Joosten's MTO fuel is mostly its own off-gas: process off-gas 5.12 and natural gas 1.51 GJ/t HVC.
- **CHEM012:** the Mantei feed is stripped out (sc-177 to sc-180). Variable O&M goes 3,655 to 295.
- **CHEM015:** IEA 2013 Table 9 gives 2 (Ren) and 1 (Benner), and Table 5 gives 0.75 and 0.57, so the median 0.875 stays. Natural gas is the carrier, and ethanol feed is 48.7 GJ/t (61% yield).
- **CHEM017:** the SMR strong variant takes its host's size (365 kt/yr).
- **CHEM019:** IEA's synthesis fuel takes the methane ratio (1.45 GJ/t).
- **CHEM020:** ATR ammonia capex judged at 830 CAD/t-yr on the SMR (IEA 2021: ATR with capture is about 10% above the SMR).
- **HPCH010:** condensing turbine is turbine only: carriers steam, the boiler emissions out, combustion 0.
- **HPCH014:** new cf-hhv-lhv-msw 1.151 (DEA). The waste boiler goes 100.3% to 91.7%.
- **MCF012** (recommendation applied): one 0% cullet basis. MIDDEN's high-cullet total and WSP's 100% reduction are out.
- **MCF018:** ETSAP and Worrell's 0.30 geopolymer totals are out (no breakdown to convert them). The hydrothermal binder takes Stemmermann's parts, 0.204 (recommendation applied: CSI-ECRA's lime-rich 0.483 is out).
- **MCF020:** cf-beer-wort-density 1.03, and cf-milk-density for the dairy rows. Galitsky's boiler fuel is rebased to steam at its own 85% (sc-181 to sc-189).
- **MCF022:**
  - plasma and calcium-looping kilns carry clinker process CO2 0.53;
  - plasma net total 0.016;
  - plasma temperature 1450 degC.
- **NFM012:** dolomite calcination 5.0 t CO2/t Mg.
- **NFM016:** rows put per t of tailings (gold 0.99, iron ore 0.65, mixed 0.8). NRCan's 28.6 kWhe/t is concentrate thickening, filtration and drying, so it is out.
- **OG010:** turbine-powered description.
- **OG013:** EPA Table 5-7 units confirmed: $/tCO2e, as printed (a 71 t CO2e/yr unit).
- **OG014:**
  - low-bleed CH4 4.4e-5 t/1000 m3;
  - plunger lift burns no gas.
- **OG015:** CERI's 0-10 kg/bbl is read as the net total (sc-190). Captured is 0.255 t/m3 and ASU electricity 0.34 GJ/m3.
- **OG016:** AER ST60/ST60B have no lift energy, so drafted at 0.17 GJ/m3.
- **OG017:** AER is the central (0.00146 t/1000 m3).
- **OG019:** product crude oil.
- **PB012:** Humbird's stover is biomass-solid (sc-191), and DEA's electricity is recorded as a co-product (0.138 GJ/GJ).
- **PB018:** TRL 6-7, and Larson's DME-a ratio is out.
- **RX011** (suggestion applied): SMR split as Collodi does. The feed-carbon process rows (Purvin, Abella) are out. Process 0.0345 + combustion 0.0294 = total 0.0635.
- **RX015** (suggestion applied): EIA's LED maintenance is the luminaire replaced over its life, a repeat of the capex, so it is out. LED fixed O&M goes 0.47 to 0.003.
- **RX018:** renamed reactor_fluid-catalytic-cracking_ccs-oxy-fuel (new modifier ccs-oxy-fuel, host FCC, share-to-capture 46%).

Side effect: removing Gielen's brick VOM and Mantei's feed-inclusive VOM from the cost-ratio pool lowered the pooled variable-O&M ratio. About 150 archetypes' variable O&M fell by 10-28%.

Open: S163-S170 in docs/sanity-check-list.csv.

## Second round (Brad 2026-10-28)

- **S163:** ammonia gasifier sizes judged: coal 500 kt/yr, biomass 100 kt/yr.
- **S164:** chiller split. The new chiller_hvac (space-conditioning) takes the hvac cooling node, EIA's commercial chillers and the 10% capacity factor. chiller_vapour-compression is now process refrigeration (product cooling, capacity factor 60%).
- **S165:** NRCan's zero steam is the groundwood central (Jacobs and Kramer steam ruled out).
- **S166:** Cusano confirmed: "Secondary aluminium melters, process equipment costs: rotary furnace EUR 15-60 per tonne produced per year" (abatement extra). MIDDEN TC0220 (primary casthouse) is unmapped, and Gielen's whole-plant capex is ruled out. Capex 74.8 CAD/t-yr, equipment only.
- **S169:** a new records/reference/ccs-addon-extra.csv adds the ASU to the oxy-fuel FCC: 0.65 GJ electricity and 260 CAD of capex per t CO2/yr.
- **S170:** ethanol price 28.99 CAD/GJ (Nebraska DWEE 2025 Omaha rack price, including the RIN).
- **Still open:** S167 (lighting vintages) and S168 (ETSAP CC-CHP examples), explained in the reply of 2026-10-28.

## Third round (Brad 2026-10-28)

- **S164 follow-up:** chiller_high-efficiency is now the efficient variant of chiller_vapour-compression (host link). EIA's commercial HVAC high-efficiency chiller example is unmapped. Capex is the 8.0 judgement, and the COP is 6.4 (Stuckrath).
- **S167, one lighting vintage:** capex and fixed O&M pool on EIA 2023's 2022 typical column only (47 rows ruled out).
  - T12 judged on the T8 2022 typical system x EIA 2013's T12/T8 ratio: capex 5.7, O&M 0.109.
  - LED and LED high-bay fixed O&M judged near 0, because EIA's maintenance is the replacement luminaire.
  - No efficient LED variant: the 2022 high system uses 12% less energy for 47% more capex.
- **S168:** left as is (option c).

The list has no open rows.
