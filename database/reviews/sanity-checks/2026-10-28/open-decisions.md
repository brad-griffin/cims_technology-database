> **Superseded 2026-10-28:** Brad ruled on every item below. What was applied is in [applied.md](applied.md); what is still open is S163-S170 in database/reviews/sanity-checks/sanity-check-list.csv.

# Open sanity-check decisions (2026-10-28)

I checked every open item in database/reviews/sanity-checks/sanity-check-list.csv against the 2026-10-28 build. I closed S10, S11, S12, S14, S16, S17, S19, and S150. Three rows stay open: S07, S158, and S162 (S151 was applied the same day). S162 is new: it tracks the 18 low-severity findings of the 2026-10-23 review. This file lists the decisions each one still needs. A recommendation follows each question.

## S151: pump station (done)

Applied on 2026-10-28 with the estimates: m3-km as the product unit, 5e-5 GJ/m3-km at 0.4 bar/km, and a 30-year lifetime. Rebuild on Windows to refresh the outputs.

## S07: heat-integrated distillation column

The variant's 4.47 GJ/t sits above its host's 3.90. Both come from DOE 2015 whole-product intensities for different products, not column energy use. The host also disagrees with its only carrier, the MIDDEN steam of 0.85. *Decision:* rule out the DOE rows on both archetypes (the MIDDEN cards and the UKERC saving then remain), or read each DOE state-of-the-art/current-typical pair as a saving of 12-41%.

## S158: medium findings

### Code rules to approve

| Item | Problem | Proposed rule |
| - | - | - |
| IS009, MCF011 | A sourced total sits below its own combustion and process CO2: the DR shaft has 0.453 against combustion of 0.53, and the regenerative glass furnace has 0.263 against parts of 0.41 | Where a pooled total is below combustion + process, the total from parts replaces it |
| MCF014 | The long rotary lime kiln's combustion CO2 is a midpoint, 0.71 t/t, which implies 0.115 t/GJ: above every fuel it lists | Where a midpoint implies a factor above every listed fuel's, use the fuel identity (about 0.48, total about 1.26) |
| HPCH012 | The capture variants are more efficient than their hosts: NGCC 50.5% against 49.1%, CHP electricity 46.9% against 37.3% | Rule out Weidmann's future-vintage efficiencies, and let the whole-plant "includes capture" rows pool |
| OG002 | The flare-gas recovery compressor's fixed O&M is 18% of capex; the norm is 4-8% | Exclude the methane devices from its cost-ratio pool, or raise the same-equipment minimum pool to 5 |
| RX013 | Four metal furnaces (heat treatment, crucible, isothermal, rotary oxy-fuel) all take the 901 kt/yr end-use median | Draft guesses: crucible 1-5 kt/yr, the others 5-50 kt/yr |
| RX017 | The delayed coker's steam band runs down to -0.16 | Floor energy-use bands at zero |
| RX019 | The cooling tower's energy use, 0.21 GJ/GJ, is a heat-pump guess; its lifetime band starts at 1 year | Redraft energy use at about 0.04; floor the class-lifetime band |
| PB014 | CO2-to-gasoline and pyrolysis oil are still per t | Apply the one-basis-per-family ruling: GJ, with an energy content |

### Rulings

| Item | Question |
| - | - |
| CHEM005 | Ammonia SMR fuel is 13-19 GJ/t against a 7-12 benchmark. Is any feed left in the pool? |
| CHEM009 | Chlor-alkali fixed O&M: revert sc-006 (does Gielen print 10 or 100)? Does Gielen's 90 ECU/t variable O&M include salt or energy? |
| CHEM011 | Methanol-to-olefins: should the natural-gas guess be process off-gas? |
| CHEM012 | OME3-5 variable O&M (3,655) includes the H2 and CO2 feed. Strip the feed or set the rows aside? |
| CHEM015 | Ethanol-to-ethylene: take IEA's 2 GJ/t as the central, list natural gas, and draft about 1.7 t/t of ethanol feedstock? |
| CHEM016 | Biomass ammonia gasifier capex 10,815: re-read the scope on IEA 2018 p.112 |
| HPCH010 | Condensing steam turbine: turbine only, or the whole plant? |
| HPCH014 (residual) | DEA's waste-to-energy boiler is 100.3% HHV (high 103.6). Add a waste HHV/LHV factor, or cap at 100%? |
| MCF012 | Electric glass melter: which cullet basis for process CO2 and the total? Does the 100% reduction stand? |
| MCF016 | Chillers: one capacity factor (10% against 60%), or split by use? |
| MCF018 | Alkali-activated binder: rule out ETSAP's 0.30 total, which falls outside the recipe scope (S121)? Hydrothermal silicate: which scope, 0.483 or 0.204 from the parts? |
| NFM012 | Silicothermic magnesium: draft dolomite calcination process CO2 at about 5 t/t? |
| OG010 | Electric frac fleet: turbine-powered or grid-tied? A second source? |
| OG013 | Non-emitting pneumatics: re-read the units in EPA 2019 Table 5-7 |
| OG014 | Draft a CH4 row for the low-bleed pneumatic; keep or drop the plunger lift's gas guess? |
| OG015 | In-situ oxy-combustion: re-extract CERI's net and captured CO2; draft ASU electricity at 0.3-0.4 GJ/m3? |
| OG016 | Artificial lift has no energy use: draft one, or source it from AER ST60? |
| PB012 | Lignocellulosic fermenter: does the lignin burned on site count, or do DEA's co-products become output flows? |
| PB015 | Groundwood pulper: re-read the Kramer and Jacobs steam scope; use NRCan's 0 steam as the Canadian central? |
| RX011 | SMR process CO2 is 7.3 t/t H2, above the 5.5 stoichiometric value, and the parts exceed the total. Which rows stay? |
| RX012 | The mine-dewatering pump and the diesel field engine sit at 293 GJ/yr. Draft capacity guesses? |
| RX014 | The MIDDEN reverberatory base capex of 1,467 looks high for secondary aluminium |
| RX015 | Lighting: pool one vintage (2022 typical)? What does EIA's LED maintenance cover? |
| RX018 | Rename the oxy-fuel FCC to _ccs-oxy-fuel so the capture rules run? |

## S162: low findings (review 2026-10-23)

Resolved: IS017, IS018, and PB017.

**Data fixes with a precedent:** I can apply these on a yes.
- MCF021: rule out Gielen 1997's bricks variable O&M (41.97) on the tunnel kilns, as MC001 did for glass.
- NFM015: move the MVR and PFC abatement costs off the Bayer digester and the prebaked cell, onto their measures.
- OG018: move the potash crystallizer to the mining family.
- RX020: set aside the system-measure lives on the moderate motor variant (10 years against the host's 25).
- RX022: replace the old archetype names in 7 records rows.
- CHEM018: tag or exclude the electric-drive ammonia rows (Rehfeldt 7.5 and Material Economics 7.56 GJ/t).

**Rulings or sources:**

| Item | Question |
| - | - |
| CHEM017 | Three ammonia plants sit at 41.7 kt/yr, the median of a single archetype. Enforce the 3-archetype minimum, and give the efficiency variant its host's size? |
| CHEM019 | The electrolytic Haber-Bosch archetype carries a 2.02 GJ/t natural-gas guess. Convert IEA's synthesis fuel with the methane factor, or drop it? |
| CHEM020 | ATR ammonia has no capex. Source a greenfield figure, or judge it from the SMR? |
| MCF020 | Register wort, beer, and dairy-liquid densities so the brewing and dairy rows pool? |
| MCF022 | The plasma and calcium-looping kilns carry no process CO2. Copy the clinker process CO2? Report 1450 degC on the plasma kiln instead of the torch's 4000? |
| NFM016 | The thickening rows are per t of ore: treat a t of ore as a t of tailings? Is NRCan's 28.6 kWh/t wider than thickening? |
| OG017 | Gas-driven pneumatics: make AER's 1.46e-6 t/m3 the central, with Clearstone's 4.09e-6 as the high? |
| OG019 | Line heater, oil-treating heat pump, and artificial lift: relabel the product as oil (m3)? |
| PB018 | Black-liquor gasifier: TRL 6-7? Bound Larson's 357.5 heat-to-power ratio? |
