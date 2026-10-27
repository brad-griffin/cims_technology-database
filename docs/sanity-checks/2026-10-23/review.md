# Sanity-check review, 2026-10-23

Third full pass over every pooled value in `data/harmonized/output/archetype-parameter.csv`, sourced and filled. Build of 2026-10-23 on commit 108a81d (clean tree, rebuilt before the screens): 503 archetypes, 7,825 pooled rows, 437 quantified. Eight family reviews ran in parallel from the same brief and screens as the 2026-10-11 pass. Nothing in `records/`, `pipeline/` or `data/raw-data/` was changed.

- `sanity-checks/2026-10-23/review.csv`: 152 findings (63 high, 71 medium, 18 low), 141 traced to example rows or pipeline code.
- `sanity-checks/2026-10-23/screens/`: the eight screens. Scripts and the brief are in `C:\_dev\staging\sanity-2026-10-23\`.
- `sanity-check-list.csv`: S133 to S146 added for the systematic defects below.

## Screens against the earlier passes

| Screen | 2026-10-11 | 2026-10-13 | 2026-10-23 |
| - | - | - | - |
| Band high/low >= 10 | 1,855 | 1,235 | 1,192 |
| Sourced-only wide bands | 279 | 278 | 327 |
| Physical bounds | 196 | 127 | 152 |
| Family outliers (>= 5x or <= 0.2x) | 1,108 | 1,074 | 1,078 |
| Carriers not summing to the total | 129 | 114 | 115 |
| Variant ordering | 5 | 2 | 3 |
| Back-test misses | 120 | 113 | 116 |

The bounds screen rose by 25: 40 new flags, 15 cleared. Most new flags are the Clearstone CH4 and N2O factor (S133) and zero-valued carrier fills on alkylation, isomerization, debarking and digesters.

## Systematic defects, in order of reach

1. **S133 The ng/J factor is 1,000 times too large** (RX001, RX002). `unit-conversion.csv` line 34 gives 0.001 t/GJ per ng/J; it should be 1e-6. Every Clearstone 2004 and 2019 CH4 and N2O row is affected. On `reciprocating-engine_diesel-field` the error cascades: CO2-eq 2.83 t/GJ, then `id-sec-from-emissions` writes an SEC of 40.4 GJ/GJ and a levelized cost of 932 CAD/GJ. This is a regression from the S108 fix.
2. **S134 The feedstock take-off misfires both ways** (CHEM001, CHEM003-005, PB005, PB006, OG003). It subtracts the product's energy from IEA 2013 rows that already exclude feed (coal methanol 24 to 2.6 GJ/t, coal ammonia 27.9 to 6.9). It leaves the feed in rows tagged `fuel` or `biomass-solid`, then adds it again as feedstock-consumption (ATR ammonia about 54 GJ/t in all against 28-32). `fermenter_grain-dry-mill` is missing from `feedstock.csv`. Three coal and gas conversion archetypes have feedstock-consumption but no energy use at all.
3. **S135 Carrier-split mechanics** (NFM003, NFM004, CHEM002, CHEM014, PB004, IS002). Several mechanisms:
   - Below three examples, one top-ranked total overwrites a much larger carrier pool. The SAG-ball mill shows 0.047 GJ/t against ten electricity rows with a median of 0.072, which is why NM006 and NM021 still show.
   - A single-carrier example becomes a 100% share.
   - A range-only carrier sits outside the split and is counted twice (pre-reduction combustion CO2 2.96 t/t).
   - The 2026-10-21 derived totals sum partial tables, so Remus Table 6.1 stove fuels pool as a 2.6 GJ/t whole blast furnace.
4. **S136 UKERC savings run on stale host totals** (IS001). `build.py` calls `ukercsaving.derive` before `carriers.example_totals`, so the efficiency buckets miss the carrier-derived totals added on 2026-10-21. For example, the coke-oven moderate variant comes out at 6.62 GJ/t against its host's 4.01.
5. **S137 The aluminium smelter's 39.4% capacity factor spreads to 15 electrolysis cells** (NFM002, CHEM007). The figure is a curtailed 2023 EU year. Working potlines and chlor-alkali cells run at 90-98%, so their levelized capital roughly doubles. Mobile equipment has the opposite problem: it takes a 90% all-archetype median against about 10-20% (RX009).
6. **S138 Capture variants still break the net-emissions ruling** (HPCH002, HPCH003, MCF002, RX010, CHEM010).
   - `ccs-host-emissions` writes nothing when the host lacks an emissions-total (`combined-cycle_ccs-diffuse`).
   - It floors at zero, without a warning, when captured CO2 from a different plant exceeds the host's gross.
   - A single derived 100% share-to-capture overrides printed 90% rates.
   - The lime capture kiln records only 61% capture.
   - The cracker's captured pool includes boiler-capture rows.
7. **S139 Capture energy and cost bases** (MCF006, IS018, HPCH011, IS007, OG006). The add-on steam is the ccs.diffuse node median, about 1.9 GJ per t CO2, against 3-3.7 for the MEA plants the cement, lime and steel sources describe. Whole-plant or equipment-basis costs treated as the add-on give double counts: combustion-turbine CHP capture variable O&M 13x its host, and coke dry quenching capex 8x below its host.
8. **S140 Emission-factor and CO2-eq rules** (HPCH001, RX003, RX004, HPCH007-008).
   - Per-fuel-input factors in units other than per GJ skip the efficiency bridge, so combined-cycle CO2 is 0.050 t/GJ against about 0.10.
   - `id-co2e-from-species` ignores a CO2 row that a later fill writes, so CO2-eq comes out below CO2.
   - UKERC "specific emissions" in kg per measure unit pool as kg/GJ, and they are grid (scope 2) emissions.
   - UKERC changes against a baseline pool as absolute values (gasifier CHP at 0.29 GJ/GJ, negative CO2).
9. **S141 `id-zero-combustion-no-fossil` reads the carriers list, not the rows** (MCF003, MCF013, PB007, NFM012, OG004). The indirect calciner, three kilns, two efficiency variants, the silicothermic magnesium reactor and the fluid coker all show zero combustion CO2 while burning fuel.
10. **S142 Fill rules without physical floors or the right analogue** (HPCH005, HPCH006, RX005, RX014, PB009, NFM001, OG001, OG002).
    - Saving buckets push SEC below 1 GJ/GJ: heaters at 108-127% efficiency.
    - The sibling rule matches product unit, not product, so a direct-use geothermal well takes a power plant's 18.9%.
    - The haul-truck judgements still scale from the pre-S89 diesel value, so they are about 2x low.
    - The fixed-O&M ratio for LNG trains comes from methane-abatement devices (20% of capex a year), and its rule text still says "parked".
11. **S143 The levelized cost including energy prices `heat` as a fuel** (MCF001). It is priced on top of the fuels and steam that supply it, on 34 rows, and only on variants, so a host and its variant sit on different bases.
12. **S144 A per-fuel heating-value uplift is applied to mixed whole-plant totals** (NFM011). This adds 11% to totals that include electricity or coal (Cusano, Van Geene, ETSAP, IAI).
13. **S145 The nickel refinery's net-heat restatement contradicts the gross-input ruling** (NFM010, commit f62ea55). It also assumes more recovery than the source prints.
14. **S146 Whole-route levelized costs sit on unit archetypes** (IS010). EAF, electrolytic-hydrogen DRI and electrowinning carry Material Economics production costs that include rolling, raw materials and a return.

## Record defects worth doing first

- **Iron and steel:** rolling-mill scope (the hot mill includes reheat-furnace fuel and the cold mill annealing fuel, both separate CIMS nodes; IS003, IS004); hydrogen DRI at 4.6 GJ/t of hydrogen, from a Circored split (IS005); smelting-reduction emissions on a per-t-steel route basis (IS008).
- **Oil and gas:** pipeline pump station per m3-km labelled m3 (OG005); fluid coking with no burned coke (OG004).
- **Pulp, paper and biofuels:**
  - debarker capex from a UKTM "other production steps" aggregate (PB001);
  - emerging dryers pooled into the steam-cylinder dryer (PB002);
  - a whole TAD mill on the through-air dryer (PB003);
  - alcohol-to-jet mass yields read as efficiency (PB010);
  - the recovery boiler band of 0.82 to 20.7 GJ/t BLS (PB011).
- **Non-ferrous and mining:**
  - Bayer digester capex per t aluminium (NFM006);
  - HPAL capex mixing per-t-metal and per-t-feed rows (NFM007);
  - the oxy-fuel furnace's 6-year refractory life (NFM008);
  - aluminium PFC rows on SAR GWPs (NFM005).
- **Refining:** acid-gas treatment on two product bases (RX006); refinery totals still the electricity row alone (RX007, S98).

## Still open from 2026-10-11

OG011, oxy-combustion net emissions (now OG015); the potash crystallizer still in oil and gas (OG018); S100, upgrader capture capex (OG006); MC002, MC009, MC015 and S97 (MCF010-012, MCF021); OT016, induction melting (RX008); OT024 and S98, refinery totals (RX007); PB025, cellulosic ethanol co-product.

## Rulings needed

1. Capture energy basis: MEA (3-3.7 GJ/t CO2, as the sources describe) or an advanced solvent (about 2.2)? (MCF006, IS018)
2. Does the cement binder node include clinker emissions? (MCF017)
3. Scope of `steam-turbine_condensing`: turbine only or the whole plant? (HPCH)
4. Electric frac fleet: turbine-powered or grid-tied? (OG010)
5. Which node `gas-treatment-unit_acid-gas-advanced` serves. (RX006)
6. Should cellulosic ethanol's energy use count the lignin burnt on site? (PB)
7. Which plant type the pellet archetype represents, and whether hydrogen cost rows belong on the reheating furnace. (IS016, IS011)
8. The conventional chiller's 10% capacity factor: air conditioning or year-round refrigeration? (MCF016)

## Suggested order

1. S133 (one factor, wide cascade).
2. S136 (one line in `build.py`).
3. S134 and S135 (the two largest mechanical families).
4. S137 to S143.
5. The rulings.
6. Record defects family by family.
