# Assignment review, 2026-09-23

Review of example -> archetype mappings and archetype -> end-use links. All of
it is applied: the `/unit` and add-on rules in `pipeline/normalise.py`, the rest by
`archive/scripts/review_2026-09-23_assignments.py` (201 examples re-homed, each
with the reason in its `note`). The "To flag" list is carried in `decisions.md`
under Open.

## Applied
- normalise: a source's generic `/unit` is now read as the example's reported
  service unit (UKERC: t, GJ, m3), not the archetype's product unit. ~90 UKERC rows
  per tonne of product were being pooled as per GJ on GJ archetypes; they are now
  excluded. Rows per UKERC "£k" of output are never pooled.

## Example remaps
- Biofuels/chemicals: iea fermenter@ethylene -> reactor_ethanol-to-ethylene; iea fermenter_biomass@high-value-chemicals -> fermenter_syngas; iea electrolysis-cell_hydrogen@ammonia -> reactor_haber-bosch-electrolytic; ipcc reactor_natural-gas (CH4 pyrolysis) -> reactor_methane-pyrolysis; ipcc reactor_electricity (electrocatalysis) -> blank.
- Electrolysis: iea "Alkaline electrolyser" -> electrolyzer_low-temperature; iea molten oxide (x2) -> electrolysis-cell_molten-oxide; iea low-temp iron electrolysis -> electrolysis-cell_iron-electrowinning; ipcc Al inert electrodes -> electrolysis-cell_inert-anode; etsap soderberg-modified, soderberg-vss -> electrolysis-cell_soderberg; iea chloride-electrolysis smelting -> electrolysis-cell_multipolar-chloride; iea firmed-renewables Al smelting -> electrolysis-cell_power-modulation.
- Cement: etsap high-pressure-roll and iea advanced grinding -> grinding-mill_vertical-roller; oxy-fuel kilns (etsap, ukerc, bataille x2, iea capture-unit_oxyfuel-ccs) -> kiln_oxy-fuel; iea calcium looping -> capture-unit_calcium-looping; ukerc kiln_dry@dry-kiln is C-DK4 fluidised bed -> kiln_fluidized-bed; ukerc kiln@cement-subsector-2030 (Novacem, E-crete, Celitement, Aether binders) -> blank; ipcc kiln_biomass@cement -> kiln_dry-precalciner; legacy etsap kilns (wet, semi-wet, lepol, wet-precalciner, long-dry) -> blank pending decision; iea electrolyser decarbonation kiln -> blank.
- Iron and steel: bataille hisarna -> smelting-vessel_bath-reduction; HIsarna-CCS (bataille, ipcc, ukerc) and iea smelting w/ capture -> NEW smelting-vessel_bath-reduction_ccs-concentrated; etsap corex-ccs -> NEW smelting-vessel_two-stage_ccs-concentrated; bataille top-gas-recycling-ccs -> blast-furnace_top-gas-recycling; etsap oxygen BF -> blast-furnace_top-gas-recycling; bataille ulcowin -> electrolysis-cell_iron-electrowinning; bataille EAF midrex (x2) -> shaft-furnace_direct-reduction; ULCORED-CCS (bataille EAF + shaft, ukerc) -> shaft-furnace_direct-reduction_ccs-concentrated; ukerc Comelt, DC furnace, twin-shell shaft preheat -> electric-arc-furnace_high-efficiency; ukerc hot-rolling strong (recuperative burners, O2 control) -> furnace_reheating_efficiency-strong; ukerc hot charging -> rolling-mill_hot-charging; ukerc IS-CC1 ladle/tundish preheating -> preheater_ladle; bataille casting/rolling aggregate improvement -> furnace_reheating_efficiency-moderate; tecnored (x2), iea BF off-gas CCU (x2), iea ring rolling, etsap Al cast house, bataille converter_coal, bataille rolling-mill@mining -> blank.
- Heat supply: EPA 2007 CHP catalog items are CHP, not power/drives: gas turbines + microturbine -> combustion-turbine_heat-recovery-steam-generator; spark-ignition engine -> reciprocating-engine_chp; back-pressure turbine (epa 2007 and 2017) -> steam-turbine_back-pressure; biomass gasifier -> gasifier_biomass-chp. iea boiler with CO2 capture -> boiler_ccs-diffuse.
- Bataille direct heaters, by process not fuel: high-temperature heat -> direct-heater_furnace; other services -> direct-heater_fired-process; low-temp base -> direct-heater_air-water; electricity -> direct-heater_electric-process (today split across air-water, fired-process, oven_indirect-fired, melting-furnace_cupola by fuel). Bataille dryers (food/chemicals/other): base -> dryer_direct-fired, strong -> NEW dryer_direct-fired_efficiency-strong (today on paper hood dryer and kiln waste-heat drying).
- Food: ukerc bakery indirect ovens -> oven_indirect-fired (set product-unit t); ukerc bakery oven efficiency -> oven_efficiency-moderate; ukerc FD-1 energy management -> (none).
- Pulp and paper: ukerc dryer@dryer -> dryer_steam-heated; ukerc dryer@sector (sector aggregate) -> (none); bataille "new dryers (standard)" -> dryer_steam-heated; bataille flash steam -> dryer_steam-heated_efficiency-moderate; hot press, impulse dryer, iea size-press -> press_dewatering-advanced; wire-section, vacuum/wire/press/dryer, press steam/electricity moderate, bataille press aggregate, bataille online moisture -> NEW paper-machine_fourdrinier-gap_efficiency-moderate; iea compression refining -> pulper_refiner-low-energy; bataille finishing paper-machine, iea waterless paper, iea supercritical CO2 drying, iea deep eutectic pulping -> blank.
- Other: ukerc fan efficiency -> fan_optimization; ukerc motors-compressors baseline -> motor_induction-standard; ukerc pulp management-system -> (none); ipcc concentrated-CO2 CCUS -> compressor_co2-dehydration; iea Bayer capture -> blank; iea coal gasification high capture -> gasifier_ccs-concentrated; iea biomass gasification -> gasifier_biomass-methanol / gasifier_biomass-waste; bataille solar direct heat -> solar-concentrator_thermal, iea (cement) -> solar-concentrator_high-temperature; bataille refining-furnace -> direct-heater_furnace; bataille calciner_coal@mining -> dryer_rotary-direct-fired.

## Pooling rule
Bataille/UKTM "Improvement technology" and "add-on" costs are incremental (precalciner 2.4, PCI 9.9, EAF scrap preheat 16.1, paper dryer 10.0 vs whole plants in the hundreds). Keep the examples, set their costs aside as needs-host-cost (precalciner -> kiln_dry-precalciner_efficiency-moderate, PCI -> blast-furnace_efficiency-moderate).

## End-use links
- electrolysis-cell_chlor-alkali-membrane -> chlor-alkali.chlorine-electrolysis (now sodium-chlorate); electrolysis-cell_sodium-chlorate -> sodium-chlorate only.
- leaching-vessel_heap-atmospheric, electrolysis-cell_advanced-anodes -> copper/nickel/zinc hydrometallurgy (now magnesium electrolysis); bioleaching and HPAL drop magnesium and titanium-slag; adsorber_direct-lithium drop coal washing, compaction and metal hydrometallurgy.
- flotation-cell_froth add mining.service.separation; steam-reformer_efficiency-moderate and autothermal-reformer add ammonia (their UKERC examples are ammonia reformers).

## To flag for the user
Legacy cement kilns; Tecnored; bataille kiln post-combustion 74 vs ~900-1200; three identical UKERC BAT-kiln rows counted as three examples; solid-fuel variants (coal, biomass) pooled with gas heaters; FCC has no hierarchy node (sits on coking/hydrocracking).
