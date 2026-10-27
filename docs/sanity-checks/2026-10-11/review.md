# Sanity-check pass (2026-10-11)

A second full review of every pooled value in `output/archetype-parameter.csv`, the
first since the fill was completed. Build of 2026-10-11 on commit 1f81c0a (clean tree
apart from an untracked `data/raw-data/gov-usa/eia/prices/` folder): 491 archetypes,
7,615 pooled rows, 423 quantified, checks and back-tests pass, `exit 0`.

Scope this time covers the filled values as well as the sourced ones, so a bad analogue
or a misfiring rule counts as a finding alongside a bad extraction.

Nothing in `records/`, `pipeline/` or `data/raw-data/` was changed by this pass. What it
wrote:

- `docs/sanity-checks/2026-10-11/review.csv` — 183 findings (94 high, 76 medium, 13 low);
  172 traced to the example rows or the pipeline code (`verified = yes`).
- `docs/sanity-checks/2026-10-11/screens/` — the eight screens the pass ran, so the next
  one can be run the same way: `screen-bounds.csv` (physical bounds), `screen-spread.csv`
  and `screen-spread-sourced.csv` (high/low >= 10), `screen-outlier.csv` and
  `screen-family-outlier.csv` (central far from the group median), `screen-carriers.csv`
  (carriers not summing to the total), `screen-variant.csv`, `screen-backtest.csv`.
  The scripts behind them are in `C:\_dev\staging\sanity-2026-10-11\`.
- `docs/sanity-check-list.csv` — S104 to S119 added for the systematic items; ten open
  items annotated where this pass found the mechanism.

## 1. One-line fixes, in order of what they buy

1. **One extraction cell poisons 157 rows (S104, finding PB002, and the same defect
   reported independently as IS006, NM001 and OT007).** `tp-mueller_2013_001-0007` holds
   Mueller and Kwik's "greater than 355 days per year" as `0.972603` in a field whose
   unit is `%`; the row's own `value-min` is 97.3. `est-class-capacity-factor` carries
   that low to 157 archetype rows in 17 families, `annual-output` lows follow it, and
   `lc-calculated` divides by it: a flash copper smelter reaches a levelized high of
   389,239 CAD/t, HPAL 1.6 million CAD/t, `paper-machine` 55,913 CAD/t. Fix the cell to
   97.26 and add a check that a capacity factor in per cent never pools below about 5.
2. **Unit aliases and missing conversions silently delete good rows (S108).** Verified
   counts of excluded rows: `y` 33 and `a` 20 (not read as years, which is why
   `management-system_leak-detection` has a 2-year life while eleven 20-25 year project
   lives sit excluded), `MWe` to `MW` 42, `mtpa` 25, `tpa` 38, `t/h` to `MW` 25,
   `short-ton/yr` to `m3/yr` 48, `bpd` to `m3/yr` 36, `ng/J` 20, `tCO2(eq)/GWh` 26, plus
   `MBtu/short-ton` on seven Martin 2000 rows, the product-qualified `GJ/t-glass`,
   `GJ/t-clinker` and `GJ/t-brick` (the whole Zier 2023 glass extraction), and
   `Btu/MMscf` on the two GPSA rows that would have replaced the bad amine-sweetening
   heat value. Each alias is a line in `unit-conversion.csv`.
3. **Six duplicate keys (S106, findings IS004, NM012, OT015).** `melting-furnace_induction`,
   `refinery_sugar-beet`, `preheater_ladle`, `fan_mine-ventilation`,
   `smelting-vessel_smelting-reduction` and `process-improvement_pre-reduction` each emit
   two rows for the same archetype, parameter and blank target: one range-only, one
   central-only. The wide view takes whichever it meets first, so
   `smelting-vessel_smelting-reduction` shows 1.3 GJ/t of hot metal. Merge the range-only
   group into the pooled row and add a uniqueness check to the gate.
4. **Exclusions keyed to one record id miss the source's twins (S113).** The MIDDEN coke
   card is in twice and only `-0099` carries the R246 ruling, so its identical twin
   `-0131` still pools 42.9 GJ/t; Gielen 1997's whole-product variable O&M was ruled out
   on the year-2000 records but not the year-2050 twins, so glass melting still carries
   699 CAD/t; Agora's 3.6 MWh/t per tonne of crude steel was set aside but Draxler's
   identical figure was not. Match exclusions on the source and the derivation, not the
   record id.
5. **53 sourced rows carry n >= 1 with a blank central (S114)**, mostly
   `temperature-output` and `emissions-reduction-potential`. Either pool them or report
   them as unpooled; a blank with a count reads as a bug to anyone downstream.

## 2. Rules that misfire

- **`id-efficiency-from-sec` inverts anything (S105).** Six rows above 100%:
  `transesterification-unit_acid-catalyzed` 496% and `_supercritical-methanol` 468%
  (utility-only SEC on a conversion archetype), `liquefaction-train_hydrogen` 371%
  (parasitic electricity), `incinerator_waste-to-energy` 322% (auxiliary demand per tonne
  of waste in, against a per-GJ-heat-out archetype), `cooling-tower_free-evaporative` 476%
  and `lighting_led-controls` 222% (an index, not an energy ratio). The guard tests that
  the carrier split agrees with the total, which a single-carrier archetype passes
  trivially. Add the condition that the split must include the product's own input
  carrier, and cap a non-heat-pump efficiency at 100%.
- **`ccs-host-plus-addon-energy` splits the add-on over the capture node's carrier mix,
  not the host's (S107).** It gives a naphtha cracker 0.214 GJ/t of coal, a kraft recovery
  boiler 0.116 GJ/t of coal, and writes 50 zero rows for blast-furnace gas, coke-oven gas,
  by-product gas and hydrogen across 13 archetypes. On the cement kiln it scales the named
  fuels by the capture duty but leaves the `fuel` aggregate at the host value, so the two
  levels no longer reconcile, and it leaves `emissions-combustion` at the host figure.
- **The variant carrier split replaces the host's fuel mix instead of scaling it.**
  `blast-furnace_efficiency-moderate` emits 1.304 t CO2/t against the host's 0.793, and
  `coke-oven_by-product_efficiency-moderate` 0.895 against 0.202, because
  `id-combustion-co2-from-fuel` reads a judgement mix that is richer in coke than the
  plant it improves.
- **The `fuel` aggregate is summed with its own named fuels, and `heat` with `steam`
  (S115).** In the capture family and on the fossil heat archetypes any sum over carriers
  double-counts: `capture-unit_amine` reaches 11.49 GJ/t against a real 4.88.
  `wide-archetype.csv` is safe; `wide-archetype-carriers-species.csv` is not.
- **`fuel-emission-factor` sums every fossil carrier present.** `capture-unit_amine`
  combustion CO2 of 0.7399 t/t is the coal SEC and the gas SEC both burned
  (5.82277 x 0.0889 + 4.38925 x 0.05064), where only one belongs. The right figure is
  0.22 or 0.52.
- **The carrier split takes its shares from one example while the total comes from the
  pool (S117).** Nineteen totals disagree with their carriers and 31 carrier sets are left
  unscaled. The bad cases: `air-separation-unit` takes a nitrogen total and overrides seven
  direct oxygen measurements; `autothermal-reformer_hydrogen` has no natural-gas row at all,
  so its carriers are 9% of its total; `reactor_hydrotreating-lipids` is 426x apart from
  its DEA split; `digester_bayer` carries the same refinery total under both `fuel` and
  `heat`; `dryer_direct-fired`, `distillation-column_heat-pumped` and
  `smelting-vessel_smelting-reduction` all take a share from a row that is not what the
  total measures.
- **The levelized band compounds worst-case corners (S119).**
  `steam-reformer_ammonia_efficiency-strong` has a central above its own high, and 30 rows
  in the heat and hydrogen families have a high at least eight times the central. Fix S104
  first, then carry the central's own capacity factor into the band.
- **`est-range-midpoint` on a sector bucket (S118).** One DOE 2023 Appendix B range
  (-110.454, -147.272 to -73.6361 CAD/t CO2-eq) sits identically on `motor_variable-speed`,
  `dryer_steam-heated_efficiency-moderate`, `press_shoe-extended`,
  `pulper_refiner-low-energy` and `vapour-recompressor_evaporation`. It is a post-IRA US
  MACC bucket, not a technology cost.
- **Fill analogues that do not hold:** gas-plant rotating equipment takes a four-member
  class median (dehydrators and pump stations at 60%, the NGL turboexpander at 38%, drilling
  rigs at 90% against a real 40-60%); `lighting_led-controls` inherits a 4-year lamp
  interval as its asset life; `est-end-use-annual-output` built from a group of one gives
  `paper-machine_waterless` a 243 t/yr low.

## 3. Record and extraction defects

Named in full in the CSV; the ones worth doing first:

- `gas-treatment-unit_amine-sweetening` heat 0.29 GJ/m3 is four Kidnay 2019 rows stated per
  litre of lean amine circulated (OG001, closes S92 with its mechanism).
- Saygin 2011's Steam column is a net export and the loader keeps the sign as consumption:
  the cracker reads -1.4 GJ/t and `steam-reformer_ammonia_efficiency-strong` -3.9 (CH002).
  The capture variant's -1.19 is that host value plus a correct 0.208 reboiler duty.
- `basic-oxygen-furnace` emissions-total 0.00804 t/t is a single top-ranked MIDDEN row, 30x
  below the archetype's own combustion and process rows (IS007, now S109).
- Biogenic CO2 in fossil parameters: `boiler_recovery` 1.112 t/t and `kiln_lime-rotary`
  0.582 t/t, where every example says biogenic (PB003, PB004, now S110).
- Wrong-product rows setting bands: an infrared paper dryer inside `dryer_electric`, a
  glass-wool plant card on `furnace_electric`, edible rendering on
  `heat-exchanger_steam-heated`, ETSAP's 445 kWh/t roller mill, copper electrowinning as
  the whole of `leaching-vessel_heap-atmospheric`, ETSAP seawater reverse osmosis as
  `separator_mine-water-treatment`, the RLE-plus-Waelz-kiln route as
  `electrolysis-cell_zinc-electrowinning`, DOE extrusion-press rows as
  `furnace_homogenizing` (R391, still unmoved).
- `cf-alumina-per-aluminium` was applied to the Gielen and DOE rows but missed on
  `tp-etsap_2012_001-0013`, which is the whole source of the `digester_bayer` high.
- Anode-carbon CO2 counted twice on `electrolysis-cell_prebaked-anode` and `_soderberg`
  (a cell burns no fuel, so it has no combustion CO2).
- `compressor_electric` carries a five-compressor station's annual electricity bill as
  fixed O&M; the motor archetypes still pool whole-system wire-to-work efficiencies as
  motor energy, and the central has moved the wrong way since S85 was written (2.5 to
  10-13.6 GJ/GJ).

## 4. Questions this pass cannot settle

These need a ruling, and several findings hang on each:

1. **Is specific energy consumption gross input or net of recovery (S111)?** Three of the
   four `basic-oxygen-furnace_efficiency-strong` examples are net of BOF gas and steam
   recovery, which is why the central is -0.325 GJ/t. `design.md` does not say. The same
   question governs the coke oven and the top-gas-recycling furnace.
2. **One product basis per family (S112).** Crackers pool per-tonne-of-ethylene figures on
   per-tonne-of-HVC archetypes with no yield applied, so capex, cost and emissions run
   1.3-1.8x high; cement kilns pool per-tonne-of-cement figures on per-tonne-of-clinker
   archetypes, which is why the kiln sits below the clinker literature at 0.82 t/t. Both
   want a stated factor, not a reviewer's guess.
3. **Is `emissions-total` gross or net on a capture variant (S116)?** The ccs variants copy
   the host's gross total while also reporting captured CO2, so they show no abatement,
   while `kiln_oxy-fuel` carries a sourced total already net of capture.
4. **Feedstock in or out of the energy total.** `steam-reformer_ammonia_efficiency-strong`
   reads 7.3 GJ/t against a 29.96 GJ/t gas carrier, and `gasifier_biomass-ethylene` 8.42
   against 55.26, because feedstock-free and feedstock-inclusive totals pool together.
5. **Unit-process or whole-plant scope** in the distillation family, on the ammonia
   reformers, on `paper-machine` against `dryer_steam-heated` (the dryer's capital is
   counted twice), and on `digester_bayer` against `calciner_gas-suspension`.
6. **Can a sourced `cost-levelized` be a supply cost?** The oil-sands well archetypes carry
   Toro 2021 dilbit supply costs including diluent, transport to Cushing and a 10-12%
   return, 3.8x the calculated levelized cost.

## 5. What verified clean

Worth recording, because it means the 2026-10-05 round held:

- The UKERC bucket fix: no negative or above-base bucket SEC remains from the saving path
  (the BOF negative is now literature, not the bucket), and 70 of 71 integrated-steelworks
  route examples stay excluded.
- The heat-pump species split: closed-cycle median 350% with vapour recompression separated
  at 445%. `heat-pump_heat-transformer` at 48% and `chiller_absorption` at 71.5% are right
  for those devices, so the screen needs the exception, not the data.
- The share-to-capture arithmetic: blast furnace 38.06%, direct reduction 58.3%, both
  reproducible from the stated inputs.
- The blast-furnace CO2 central of 1.10 t/t with NRCan 2007's net figure excluded.
- The MIDDEN scale re-read: no residual factor-of-1000 slips on the ammonia, methanol or
  cracker cards. What remains on MIDDEN is basis, not scale.
- The plunger-lift re-extraction (18.65 t CH4/yr, inside the R557 benchmark) and the
  ch4/co2e unit labelling.
- The hours-based lifetime species: lamps, haul trucks and `fuel-cell_chp` all carry stack
  or component correctly; only `mobile-equipment_hydrogen-fuel-cell` is missing its stack.
- The black-liquor solids ratios: IEAGHG's corrected 25.48 GJ/ADt and Ekbom's 21.02 both
  land on 13.70 GJ/t BLS. They are applied to energy but not to capacity or annual output,
  which is finding PB006.
- Negative values that are intended: capture units' `emissions-total`, and the blended-cement
  abatement cost. The calcined-clay one is not — that archetype has no calcination fuel.

## 6. Suggested order

1. Section 1, the five mechanical fixes, then rebuild and re-run the screens. Everything in
   the levelized-cost tail moves with S104 alone.
2. The rule fixes in section 2, hardest first: the capture add-on carrier split (S107), then
   the inverse identity (S105), then the variant split and the fuel double count.
3. Brad's six rulings in section 4, since the record work in section 3 depends on three of
   them.
4. The record and extraction defects family by family, as on 2026-10-05, iron and steel and
   chemicals first: they hold the most high-severity rows and feed the capture variants.
5. The 48 unnamed hosts (S20-S67) and the remaining medium findings last.
