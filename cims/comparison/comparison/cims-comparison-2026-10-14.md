# CIMS model inputs compared with the database archetypes (2026-10-14)

This compares the values in the CIMS model inputs (`data_processing_calibration`,
`cims/data/model_inputs/model/`, staging branch) with the archetype values in
`database/harmonized/output/` (build at commit f7775d3). It feeds nothing back into the
database: the CIMS values remain unused there (ruling 2026-10-04).

## Headline

- **Mapping.** Of 1,582 industrial CIMS technologies, 344 match an archetype exactly,
  612 closely (other fuel, efficiency tier or size), 197 partly (scope differs), 345
  have no archetype, and 84 are fuel choices or placeholders rather than devices. The
  matches cover 209 archetypes.
- **Capital cost.** CIMS capital is lower. Across 851 same-or-close pairs, the median
  CIMS annualised capital cost is 0.60 times the database's (interquartile 0.28 to 1.25).
  Only 41% of pairs fall within a factor of two. Mining and non-ferrous metals are lowest
  (about 0.17 times); space conditioning and food-and-beverage run far higher.
- **Fixed O&M** agrees at the median (1.01) but scatters widely (0.35 to 2.5).
- **Lifetimes.** CIMS lifetimes run about 20% longer (median 1.2; 68% of pairs within the
  database's low-high band). CIMS rarely uses less than 25 years.
- **Energy.** Specific energy consumption agrees at the median (1.03) with an
  interquartile range of 0.85 to 1.52. Heater, boiler and motor efficiencies agree
  closely (median 0.98; 78% within 20%).
- **Variable O&M.** CIMS carries it only on the CCS technologies (the VOM request).
- **CCS.** Every CIMS CCS node reproduces a NETL (Hughes and Zoelle 2023) case: compression
  only for ammonia, ethanol and gas processing (about 1 GJ/t, as gas for power), solvent
  capture for SMR, cement and steel (3.4-4.8 GJ/t). CIMS applies one node's capture rate
  to all CO2 of every host in the sector, including diffuse boilers. Revised 2026-10-21.
- **Defects found** on both sides are listed below. The clearest CIMS ones: Portland
  cement requests 1.15 t clinker per t cement (likely inverted), electric space cooling
  has a COP of 0.75, and Light Industrial water heaters show 300-500% efficiency. The
  clearest database ones: space-conditioning capacity factors filled from process
  equipment (60-86%), and an efficiency-bridge bug that divides about 55 emission rows
  already per GJ of output by efficiency again (this is why boilers with capture show
  0.21 t per GJ steam).

## Method

| Step | Rule |
| - | - |
| Regions | CIMS repeats each technology per province. Each value is the median across provinces; the min and max are kept (`cims-values.csv`). |
| Year | The 2025 value where CIMS gives a series, else the undated value. |
| Mapping | Each CIMS technology maps to one archetype by identity (device, fuel, scope), never by value closeness. Classes: same, close, partial, none, not-a-technology. Done in five groups (`mapping/*.csv`); every archetype and node checked against the records. |
| Currency | CIMS is in 2020 CAD (root `currency`). Deflated to 2025 CAD with the database's CAD GDP deflator (x1.244). |
| Per unit | CIMS `fcc` and `fom` are per plant, with `output` the plant's actual annual output; divided through. The database's `capex` and `opex-fixed` are per unit of nameplate capacity, so they are divided by the archetype's capacity factor to put both per unit of output. |
| Annualising | Capital x CRF(8%, own lifetime) on both sides (ruling 2026-10-14). The non-energy levelized cost uses the database formula with CIMS inputs. |
| Energy | CIMS energy in = direct fuels + electricity + steam + heat services + auxiliary motor services (machine drive, pumping, compression, conveyance, ventilation), all in GJ; auxiliary services count as electricity. Negative requests (CHP electricity) count as output. Natural Gas Feedstock is kept apart and compared with the database's SEC plus feedstock-consumption. |
| Carrier shares | Electricity, steam, heat and fuel shares of total energy in. The database side uses only its top-level split (rows written as a share of the total). |
| Efficiency | For GJ-output technologies that buy no steam or heat: 100 / energy in, against the database `efficiency` (HHV). CHP gives heat and electricity efficiencies separately. CIMS is assumed to be on HHV. |
| Units | Values are compared only where the CIMS node unit matches the archetype's product unit (t, GJ, m3, kt converted). 132 technologies differ (lighting GJ vs Mlm-h, unstated CIMS units, per-GJ vs per-t nodes) and show values without a ratio. |

## Files

| File | Contents |
| - | - |
| `../extract_cims_values.py` | Collapses the model inputs to `cims-values.csv` (one row per technology x quantity, median/min/max over provinces). |
| `../build_cims_summary.py` | `cims-technology-summary.csv`: one readable row per CIMS technology, used for mapping. |
| `mapping/*.csv` | CIMS technology -> archetype, new node, match class and note (cross-cutting, pulp-light-industrial, steel-metals, mining-minerals, oil-gas-chemicals). |
| `../compare_cims_archetypes.py` | Builds the two comparison files. |
| `comparison-long.csv` | One row per CIMS technology x quantity: both values, database low/high/n/grade, ratio, in-range flag, basis and note. |
| `comparison-archetype.csv` | One row per archetype x quantity over its same/close CIMS technologies: CIMS median/min/max, ratio median, number within the database band. |
| `fixed-ratio-comparison.csv` | CIMS fixed-ratio coefficients and material requests against the database's conversion factors and flows. |

## Results by quantity (same and close matches)

| Quantity | Pairs | Median CIMS/database | Interquartile | Within x2 | Within database band |
| - | -: | -: | - | -: | -: |
| Annualised capital (8%) | 852 | 0.60 | 0.28-1.25 | 41% | 37% |
| Fixed O&M per unit output | 852 | 1.01 | 0.35-2.39 | 41% | 45% |
| Non-energy levelized cost | 851 | 0.59 | 0.26-1.19 | 41% | 41% |
| Lifetime | 957 | 1.20 | 1.00-1.25 | 94% | 68% |
| Specific energy consumption | 852 | 1.03 | 0.84-1.47 | 69% | 24% (many archetypes have no band) |
| Efficiency | 290 | 0.98 | 0.93-1.01 | 92% | 69% |
| Process CO2 | 52 | 0.96 | 0.83-0.96 | 94% | 29% |

CCS variants (`_ccs-*`) are compared on the host-plant capex and O&M
(`output/ccs-variant.csv` host-value), since CIMS prices the host only and buys capture
from the CCS node. Their database levelized cost still includes the add-on.

By family (median of each archetype's median ratio; number of archetypes in brackets):

| Family | Annualised capital | Fixed O&M | Lifetime | SEC |
| - | -: | -: | -: | -: |
| cement | 0.65 (10) | 0.35 | 1.09 | 0.74 |
| chemicals | 0.52 (18) | 0.58 | 1.20 | 0.74 |
| heat-supply | 0.62 (16) | 1.65 | 1.20 | 1.06 |
| iron-and-steel | 0.78 (21) | 0.93 | 1.25 | 0.99 |
| machine-drive | 0.35 (3) | 0.66 | 1.00 | 0.99 |
| mining | 0.16 (9) | 0.21 | 1.20 | 0.84 |
| non-ferrous-metals | 0.17 (15) | 0.34 | 1.50 | 1.04 |
| non-metallic-minerals | 1.27 (6) | 1.08 | 1.20 | 1.21 |
| petroleum-refining | 0.58 (11) | 1.70 | 1.25 | 1.94 |
| pulp-and-paper | 0.52 (24) | 0.84 | 1.00 | 0.79 |
| space-conditioning | 17.50 (2) | 83.60 | 1.20 | 1.09 |

Some anchors (2025 CAD per unit of output):

| Archetype | Quantity | Database (grade) | CIMS median (range) | n |
| - | - | - | - | -: |
| boiler_fuel-fired | annualised capital, $/GJ | 1.19 (sourced) | 0.73 (0.52-9.8) | 28 |
| boiler_fuel-fired | efficiency | 81% | 80% | 27 |
| kiln_dry-precalciner | capex, $/t-yr | 550 | 502 | 9 |
| kiln_dry-precalciner | SEC, GJ/t | 3.75 | 4.85 | 9 |
| electric-arc-furnace | capex, $/t-yr | 323 | 152 | 4 |
| electric-arc-furnace | SEC, GJ/t | 3.05 | 2.00 | 4 |
| motor_induction-standard | capex, $/GJ-yr | 20.7 | 8.2 | 49 |
| motor_induction-standard | efficiency | 91% | 92% | 49 |
| paper-machine | capex, $/t-yr | 768 | 597 | 6 |
| steam-reformer_methane | capex, $/GJ-yr | 25 | 129 | 1 |

## CCS (revised 2026-10-21)

### Where the CIMS numbers come from

Every CIMS sector CCS node reproduces a case in NETL's *Cost of Capturing CO2 from
Industrial Sources* (Hughes and Zoelle 2023, in the database as `hughes_2023_001`). The
plant sizes match to within 0.1% (cement 925,650 vs 925,793 t/yr; steel 2,861,100 vs
2,860,681; ethanol 121,550 vs 121,588; gas processing 551,650 vs 551,815), and the costs
match after currency conversion.

| CIMS node | NETL case | Stream | Database archetype compared |
| - | - | - | - |
| Chemical Products | ammonia stripper vent, compression only | concentrated | `compressor_co2-dehydration` |
| Ethanol; Biodiesel (a copy) | fermentation CO2, compression only | concentrated | `compressor_co2-dehydration` |
| Natural Gas; Petroleum Crude (a copy) | gas-processing CO2, compression only | concentrated | `compressor_co2-dehydration` |
| Hydrogen; Petroleum Refining (same numbers) | refinery SMR, ADIP-Ultra on shifted syngas, 90% | concentrated | `capture-unit_chemical-solvent` |
| Industrial Minerals | cement kiln off-gas, CANSOLV, 90% | diffuse | `capture-unit_amine` |
| Iron and Steel | BF-BOF mill, CANSOLV, 90% | diffuse | `capture-unit_amine` |

The mapping in `mapping/` now follows this (before 2026-10-21 every node except Hydrogen
was compared with `capture-unit_amine`). Host technologies with CCS were already matched
to the database variant at the same end use; `ccs-addon-comparison.csv` lists each host
with its stream type.

**Capture energy.** CIMS has no electricity request on the CCS nodes. Its natural gas
request is NETL's boiler gas plus NETL's electricity divided by 0.38, as if the power came
from on-site gas generation: ammonia 105.6 kWh/t gives 1.00 GJ/t, ethanol 112.7 kWh/t
gives 1.07, gas processing 82.6 kWh/t gives 0.78, the SMR case 2.46 GJ gas + 97.2 kWh
gives 3.38, and cement 3.74 GJ + 116.5 kWh gives 4.84. So the 0.8-1.1 GJ/t values are not
typos: they are compression power for already-pure CO2. Iron and Steel (4.29) is the one
that does not reproduce; NETL's steel case gives the same 4.84 as cement.

**Capture rates.** NETL captures all of a high-purity stream: the ammonia case compresses
486,074 t/yr of a 486,227 t/yr stripper vent, and the ethanol and gas-processing streams
are taken as 100% CO2. So 100% is right *for the pure stream*. The problem is in CIMS:
`emissions_removal` is applied to all of a host's CO2, combustion and process, whatever
quantity the host sends to the node (`src/CIMS/emissions.py`, the child-level removal
block, which says so). Two consequences:

1. A host that sends only part of its CO2 to capture is credited with removing all of it.
   An ammonia plant with CCS loses its reformer flue-gas CO2 too, though NETL captures
   only the vent.
2. Each sector has one CCS node, so diffuse hosts buy from a node priced for pure CO2. In
   Chemical Products, Ethanol and Biodiesel, gas and coal boilers with CCS pay
   compression-only costs (28-50 $/t) and get 100% removal of their flue gas. In
   Petroleum Crude they pay gas-processing costs at 90%.

This is item 4 of `cims/to-fix.md`, with the stream-type point added: the fix needs
a concentrated and a diffuse CCS node per sector (as the hierarchy now has) and
emissions_removal scaled by the share each host sends.

### Node against archetype (per t CO2, 2025 CAD; `ccs-node-comparison.csv`)

| CIMS node | Database archetype | Capex $/t-yr CIMS / db | Fixed O&M CIMS / db | VOM CIMS / db | Energy GJ/t CIMS / db | Capture rate CIMS / db |
| - | - | - | - | - | - | - |
| Chemical Products | compressor_co2-dehydration | 190 / 89 | 6.6 / 5.8 | 4.6 / 2.8 | 1.00 / 0.49 elec | 100 / 100 |
| Ethanol, Biodiesel | compressor_co2-dehydration | 349 / 89 | 15.8 / 5.8 | 3.0 / 2.8 | 1.07 / 0.49 elec | 100 / 100 |
| Natural Gas, Petroleum Crude | compressor_co2-dehydration | 177 / 89 | 5.8 / 5.8 | 2.6 / 2.8 | 0.78 / 0.49 elec | 95 and 90 / 100 |
| Hydrogen, Petroleum Refining | capture-unit_chemical-solvent | 860 / 398 | 26.8 / 11.2 | 9.2 / 9.3 | 3.38 / 2.08 | 90 / 83 |
| Industrial Minerals | capture-unit_amine | 732 / 518 | 19.1 / 14.8 | 10.5 / 18.3 | 4.84 / 4.80 | 90 / 90 |
| Iron and Steel | capture-unit_amine | 639 / 518 | 16.3 / 14.8 | 19.7 / 18.3 | 4.29 / 4.80 | 90 / 90 |

CIMS capex runs 1.2-3.9 times the database. For the compression-only cases this is
scale: NETL's ethanol plant compresses 0.12 Mt/yr, while the database median for
`compressor_co2-dehydration` pools 41 examples, many of them large. CIMS's energy for the
compression cases is natural gas standing in for 0.30-0.41 GJ of electricity.

### The CCS portion only (`ccs-addon-comparison.csv`)

For each CIMS host with CCS: request (t CO2 per unit of product) x the node's annualised
capex, fixed O&M and VOM per t, plus the host's own cost increment over its sibling
without CCS. For the database: the add-on in `output/ccs-variant.csv`, annualised at 8%
and put per unit of output. Results per t CO2 captured (37 hosts):

- **CIMS puts nearly all of the capture cost on the node.** Only 5 of 37 hosts cost more
  than their sibling without CCS (Corex, the steam cracker, petcoke gasification, the gas
  direct-heat boiler and the still-gas boiler).
- **Concentrated hosts** (6): CIMS costs a median 1.9 times the database per t (1.1 for
  DRI, 1.3 for ammonia, 1.5 for refinery SMR, 2.3-2.4 for HIsarna and Corex, 3.0 for
  petcoke gasification). The database's concentrated add-ons for smelting reduction and
  gasification are cheap tier-1 figures from their own sources.
- **Diffuse hosts** (31): median 0.55 after the 2026-10-21 emission-basis fix (0.86
  before). The low end is the boilers in Chemical Products, Ethanol and Biodiesel, which
  CIMS prices as pure-stream compression (28-50 $/t against the database's 91 $/t for a
  boiler with capture).
- **Captured CO2 per unit of product** differs as well: cement 0.44 t/t clinker in CIMS
  against 0.76 in the database; lime 1.16-1.23 against 0.74; Corex 3.36 against 1.0.

### If the host's request is the stream sent to capture (question 2026-10-21)

The database keeps the two apart: the host carries `share-to-capture` (the share of its
CO2 that goes to the capture plant) and the capture archetype carries `capture-rate`
(the share of that stream it captures). Captured = gross CO2 x share-to-capture x
capture-rate. The capture archetypes are priced **per t captured** (their product, like
NETL's cost of capture). That leaves two consistent ways to set the CIMS request:

| | Request = t CO2 **sent** to capture | Request = t CO2 **captured** |
| - | - | - |
| Capture node priced per | t treated: the database cost per t captured x capture rate | t captured: the database value as is |
| Node energy, VOM, transport request | per t captured x capture rate | as is (transport 1 t per t, plus the node's own fuel CO2) |
| Removal CIMS should book | capture rate x request | request |

Either works. The problem comes only from mixing them: a request for the stream bought
at a price per t captured overstates cost, energy and transport by 1/capture rate (about
11% at 90%), and sends the uncaptured 10% to storage. I'd use **request = t captured**,
since every database and NETL figure is per t captured and the node needs no
restatement; the node's capture rate then documents, rather than drives, the removal.

Under both, CIMS needs the code change in item 4 of `cims/to-fix.md`: removal
driven by the request, not the node's rate times all host CO2. Three things to settle in
that change:

1. **Fuel switching.** A request is a fixed coefficient per unit of product. If the host's
   fuel arrives through a blend node (renewable natural gas or hydrogen in the methane
   blend) or its fuel mix changes, its CO2 falls but the request does not, so CIMS would
   pay to capture CO2 that is not there. Cap removal at the host's actual CO2 of the
   types sent to capture, and accept that cost stays at the coefficient (or re-derive the
   coefficient per fuel variant, as CIMS already has separate NG, oil and coal hosts).
2. **Emission types.** CIMS books removal by gas and type (Combustion, Process). A
   quantity needs a split: an ammonia vent is all process CO2, a boiler flue all
   combustion, a cement kiln both. Splitting pro rata to the host's own gross emissions by
   type is the simple rule; the database could carry the split where a source gives it.
3. **Biogenic CO2.** Removal of biogenic CO2 is booked as negative emissions. The fossil
   and biogenic shares of the captured quantity should follow the host's actual fuel mix
   in the year, which a fixed coefficient alone cannot give.

## Fixed ratios and material requests

See `fixed-ratio-comparison.csv`. Agreement on raw meal per clinker (1.6 vs 1.52-1.7),
casting yield (1.01-1.02 vs 1.02), anode per aluminium (0.43 vs 0.41) and black liquor
solids per kraft pulp (1.6 vs 1.5). Disagreement:

- **Clinker per Portland cement: CIMS 1.15** in all provinces, against 0.74-0.95 in nine
  database sources. 1.15 is close to the inverse ratio (cement per clinker, 1.11-1.14).
- **EAF oxygen: CIMS 0.005 t/t**, a tenth of the database's 0.055 (0.007-0.1).
- **Corex oxygen: CIMS 0.08 t/t** against 0.71 (0.56-1.35).
- **Agglomerate per t steel: CIMS 0.068** against the blast furnace's 1.46 t sinter and
  pellets; presumably the rest arrives as purchased pellets. Worth confirming.
- **Log preparation per t pulp:** 11.9 in one province (others 1.1-1.4).

## Likely CIMS defects

1. Portland cement requests 1.15 t clinker per t cement (above).
2. Electric space cooling requests 1.33 GJ electricity per GJ cooling (COP 0.75; 1.91 in
   Coal Mining) in every sector. The database chiller COP is 3.95.
3. Light Industrial water heaters request 0.19-0.32 GJ per GJ of hot water (implied
   efficiency 300-530%); the output unit is probably not GJ.
4. One CCS node per sector, priced for its NETL case, serves both concentrated and diffuse
   hosts; with emissions_removal applied to all host CO2, boilers in Chemical Products,
   Ethanol and Biodiesel get 100% removal at compression-only cost (see CCS). Iron and
   Steel capture energy (4.29 GJ/t) does not reproduce from NETL (4.84 expected).
5. Petroleum Refining "NG CCS" requests 66.5 from the CCS node with unit `$`, a cost in the
   quantity field. Petroleum Crude "Boiler NG CCS" ramps its CCS request from 0.063 t/GJ in
   2000 to 1.28 in 2005, the value of its natural gas request; "Boiler Petcoke CCS" (1.22)
   and "Cogen NG CCS" (1.4) look the same.
6. EAF and Corex oxygen, and the province with 11.9 t logs per t pulp (above).
7. Lifetimes of 50 years on pneumatic devices and the hydrogen pipeline, 30 on
   Soderberg cells, and 1 year on "Increased clinker substitution".

## Possible database issues (for the sanity-check list; traced 2026-10-21)

### 1. Space-conditioning capacity factors come from process equipment (fixed 2026-10-21)

None of the space-heating or space-cooling archetypes has a sourced capacity factor. The
fill rules give them the median of their equipment class or sibling, which is process
equipment running most of the year:

| Archetype | Capacity factor | Rule |
| - | -: | - |
| space-heater_fuel-fired, resistance-heater_space-heating | 85.6% | est-class-capacity-factor (heat-equipment class) |
| heat-pump_space | 75.4% | est-sibling-capacity-factor |
| chiller_vapour-compression, cooling-tower_free-evaporative, ventilation-unit_demand-controlled, ventilation-unit_heat-recovery | 60.0% | est-class-capacity-factor |

The capacity factor divides capex and fixed O&M in the levelized cost and sets annual
output, so these costs per GJ are understated about 3-4 times for heating and 5-6 times
for cooling.

How to correct it, following the OG013 precedent (drilling rigs, pump stations):

1. Add rows to `records/fill/fill-judgement.csv` for each archetype (basis
   `engineering-relation`): equivalent full-load hours = 24 x heating degree-days /
   (indoor minus design temperature), with a sizing margin. Canadian degree-days and
   design temperatures give roughly 2,000-3,000 full-load hours, or 20-30% before
   oversizing; a draft of about 22% (15-30%) for heating and 10% (5-15%) for cooling.
   Ventilation heat recovery runs in the heating season, so it takes the heating figure.
2. Add these archetypes to `exclude-archetype` on `est-class-capacity-factor`,
   `est-sibling-capacity-factor` and `est-end-use-capacity-factor`, since the rules run
   before the judgements.
3. Better than a judgement, if you want it sourced: register ECCC climate normals
   (degree-days) and design temperatures (National Building Code Appendix C) as conversion
   sources and compute the figure for a few industrial regions.

**Done 2026-10-21 as judgements** (steps 1 and 2): the ECCC and NRC sites are not
reachable from either the cloud workspace or the computer's shell, so step 3 waits. Space
heaters, the space heat pump and the ventilation units take 22% (15-30%); chillers and
cooling towers 10% (5-15%), all `draft` in `fill-judgement.csv`. `space-heater_fuel-fired`
levelized cost moved from 0.63 to 2.47 $/GJ.

### 2. Captured CO2 on boilers with capture: the efficiency bridge runs twice (fixed 2026-10-21)

`boiler_fuel-fired_ccs-diffuse` captures 0.21 t CO2 per GJ of steam (CIMS 0.06 for gas,
0.10 for coal). Two causes:

- **A pipeline bug.** `pipeline/normalise.py` treats every emissions value per GJ on a
  GJ-product archetype as per GJ of *fuel* and sends it through the efficiency bridge,
  which divides by efficiency. The two boiler examples are already per GJ of steam: IEAGHG
  2007 case 3 prints 6.043 kg/s CO2 per 50 MWth steam (0.121 t/GJ), divided by 56.9% to
  0.213; IEAGHG 2013's works-gas boiler is 869.5 kg per 3.75 GJ steam (0.232), divided by
  80.4% to 0.288. About 55 example rows are affected: all 34 bridged MIDDEN rows (whose
  notes say "per GJ of main output"), the 14 IEAGHG 2007 rows (per MWth of steam or heat),
  both IEAGHG 2013 rows, four Pembina rows (per GJ hydrogen) and one Johansson row (per GJ
  of LP steam). The DEA, ETSAP and Zuberi rows are per GJ of fuel and are bridged
  correctly. One visible result: `boiler_fuel-fired` emissions-total is 0.085 t/GJ steam,
  where 66 kg/GJ (0.066) is what MIDDEN prints.
- **Unrepresentative examples.** Even unbridged, both examples are coal or blast-furnace-gas
  boilers (0.12 and 0.23 t/GJ). A gas boiler at 85% emits about 0.06 t/GJ steam.

**Done 2026-10-21.** `records/reference/emission-basis.csv` lists the output-basis rows
(MIDDEN by source; IEAGHG 2007 and 2013, Pembina and Johansson by record, each with the
evidence), `pipeline/normalise.py` skips the bridge for them, and `pipeline/checks.py`
checks the file. After the rebuild: `boiler_fuel-fired` emissions-total 0.085 -> 0.066
t/GJ; `boiler_fuel-fired_ccs-diffuse` captured 0.213 -> 0.121 t/GJ; `combustion-turbine_chp`
emissions-total 0.251 -> 0.103; `combustion-turbine_chp_ccs-diffuse` captured 0.203 ->
0.084. The boiler-with-capture value is still a coal CFB boiler (top-ranked IEAGHG 2007);
a gas-fired example, or a judgement near 0.055 t/GJ, would make it representative of
`boiler_fuel-fired`.

`combustion-turbine_chp_ccs-diffuse` was partly this bug (0.20 -> 0.084 t/GJ heat); the
rest of the gap to CIMS (0.055) is allocation: the database puts all CO2 on the heat,
while CIMS credits the electricity.

### 3. Where the short lifetimes come from (fixed 2026-10-21 except where noted)

| Archetype | Lifetime | Where it comes from |
| - | -: | - |
| dryer_direct-fired_efficiency-moderate | 5 | Top-ranked MIDDEN zeolite spray-drying measure (a retrofit measure life); Martin 2000's dryer heat recovery gives 25. |
| dryer_direct-fired | 5 | No sourced value; est-sibling-lifetime copied it from the modifier above, so the base dryer inherits a retrofit measure's life. |
| electrolysis-cell_soderberg | 5 (4-6) | ETSAP 2012 range midpoint. The extraction note already says "CATHODE life, not plant life", yet the row loads as lifetime. Treat it like the glass furnace: a relining (rebuild) allowance on a 30-40 year potline. |
| electrolysis-cell_inert-anode | 10 | Martin 2000 emerging-technology data table (a measure life). |
| coating-line_hot-dip, coating-line_electrolytic | 15 | Daniels 2002, Eurofer depreciation periods: accounting lives, not physical ones. |
| pipeline_hydrogen | 15 (15-30) | Top-ranked of two HDSAM examples, one of which is the pipeline compressor (15); the pipeline itself is 30. The compressor example likely belongs on a compressor archetype. |
| pneumatic devices | 10 | Carbon Limits 2016 (11 sourced examples); plausible for controllers. CIMS's 50 years is the outlier. |
| flare, plunger lift, blowdown recovery | 10 | US EPA and Dunsky measure lives; plausible. |

**Now (rebuild 2026-10-21; rows set aside in `excluded-row.csv`, judgements `draft`):**
direct-fired dryer and its two modifiers 25 years (Martin 2000's heat-recovery life, then
siblings); Soderberg and inert-anode cells 20 by judgement (as the prebake cell; the
Soderberg relining every 4-6 years is not yet costed, and a rebuild allowance like the
glass furnace's would carry it); coating lines 25 (process-plant class median);
`pipeline_hydrogen` 30. Pneumatic devices, flares, plunger lifts and blowdown recovery
are left at 10. Daniels 2002 also supplies Eurofer depreciation lives for `rolling-mill_hot`
and `rolling-mill_cold` (20 years); I left those, as 20 is within the usual range, but the
same reasoning would set them aside.

### 4. Steam methane reformer

`steam-reformer_methane` capex 25 $/GJ-yr against CIMS's 129 (one CIMS technology); its
SEC (0.63 GJ/GJ, excluding feedstock) differs in basis from CIMS (1.34 including
feedstock).

## Basis differences to resolve before reading a ratio

Ratios beyond 10x (112 capital pairs, 144 fixed O&M pairs, 61 SEC pairs) are mostly
product-basis differences, not value differences. Examples:

- Pulp-mill lime kilns: CIMS per t pulp, database per t lime (ratio about 0.01).
- Dryers in mining and coal mining: CIMS per t concentrate or coal, database per t of
  product dried on a different basis (SEC ratios 13-18).
- Mine ventilation, potash solution mining, nickel-matte refining and Peirce-Smith
  converters: whole-mine or whole-refinery nodes against unit-process archetypes.
- Lighting: CIMS per GJ of lighting service, database per Mlm-h (not compared).
- Lines with an unstated CIMS output unit (natural gas, crude) are shown without a ratio.

## Gaps: CIMS technologies with no archetype

- Driven machines: compressors (88), conveyors (40), most fans (34) and base pumps (48).
  The database holds motors and system measures, not the machines.
- DC motors, V-belt drives and Light Industrial whole-building HVAC packages.
- Mining: crushers, coal grinding, electric shovels and drills, continuous miners,
  potash dissolution, brine pipelines and conventional tailings.
- Metals: roast plus reverberatory matte smelting, non-ferrous blast furnaces, retorts,
  slag fuming and titanium electrorefining.
- Oil and gas: whole-field production, gas wells, compressor stations and transmission;
  lube oil and asphalt units; capture variants for delayed coking and biomass
  gasification.
- Pulp and paper: stock-preparation refining and screening, pulp washers; agriculture
  soils and enteric practices.

## Caveats

- The mapping is judgement, made in five groups by delegated reviewers and checked for
  valid names and nodes. The `note` column records each call; read it before relying on a
  close or partial pair.
- CIMS heat and auxiliary-service requests are service GJ, not purchased energy, so CIMS
  SEC sits slightly below a purchased-energy total for motor-heavy techs.
- Database values graded `guess` (271 of 1,150 capital comparisons) are as uncertain as
  the CIMS ones.
