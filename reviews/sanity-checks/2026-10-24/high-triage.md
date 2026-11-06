# High-severity findings triage (review 2026-10-23, checked against output of 2026-10-24 07:36)

Source: database/reviews/sanity-checks/2026-10-23/review.csv, severity = high (63). Values read from database/harmonized/output/archetype-parameter.csv and example-parameter.csv.

Counts: RESOLVED 48, PARTLY 11, OPEN 4. [R] marks items that need a modeller ruling, not only a data fix.

| id | archetype | verdict | current value / evidence | what remains / suggested fix |
| - | - | - | - | - |
| CHEM001 | gasifier_coal-methanol; _ccs-concentrated; gasifier_coal-ammonia | RESOLVED | SEC methanol 25.26 GJ/t (21.16-25.26), ccs 28.84, ammonia 23.16 (15.4-29.4); IEA Table 5 rows no longer take the feedstock off | none |
| CHEM002 | gasifier_coal-ammonia | RESOLVED | electricity 3.70 (Boulamanti's own), coal/fuel 19.46 = total less electricity | none |
| CHEM003 | autothermal-reformer_ammonia (+ccs) | RESOLVED | SEC 9.19 GJ/t (natural gas 8.69, electricity 0.50); ccs 11.80; feed 22.48 separate | none (slightly above the 5-9 benchmark) |
| CHEM004 | gasifier_biomass-methanol | RESOLVED | SEC 13.48 biomass-solid + feed 22.66, consistent with efficiency 62.7% | none |
| CHEM007 | chlor-alkali and chlorate cells | RESOLVED | capacity factor 93% (85-98) judgement on all electrolysis cells; JRC 39.4% ruled out | none |
| CHEM010 | steam-cracker_fired-tubular_ccs-diffuse | RESOLVED | share-to-capture 83%; captured 0.534 = 0.9 x 0.83 x host 0.715; net total 0.181 t/t | none |
| HPCH001 | combined-cycle; steam-turbine_condensing; simple-cycle; boiler | RESOLVED | CC CO2 0.101 t/GJ (from fuel); ST condensing 0.224; simple-cycle 0.137 (low 0.0756 is Interlab's per-MWh projected advanced turbine, a real output basis) | none (low on simple-cycle is a projected-technology row, not the bridge bug) |
| HPCH002 | combined-cycle_ccs-diffuse | RESOLVED | net emissions-total 0.00506 t/GJ written; captured 0.0962 = 95% x host 0.101 | none |
| HPCH003 | boiler_fuel-fired_ccs-diffuse; ATR-H2 ccs; petcoke gasifier ccs | RESOLVED | net totals 0.0066, 0.0027, 0.0120 t/GJ (no zeros); captured = rate x share x host gross | none |
| HPCH004 | boiler_fuel-fired_ccs-diffuse | PARTLY | captured now 0.0594 t/GJ from the host; efficiency still 56.87% (IEAGHG 2007 coal CFB, central) with the works-gas boiler (IEAGHG 2013) still mapped here | Re-map ieaghg_2007_001 coal CFB and ieaghg_2013_003 works-gas boiler examples off this gas-boiler variant; also host boiler_fuel-fired SEC 1.429 (one DOE example) disagrees with its 81% efficiency |
| HPCH005 | geothermal-well_direct-use | RESOLVED | no efficiency row; SEC total marked not-applicable; carriers geothermal 1.05 and electricity 0.03 (guesses) | none |
| HPCH006 | direct-heater_solid-fuel_efficiency-strong | PARTLY | SEC 1.031 GJ/GJ and efficiency 97.0% now agree (capped) | Carrier judgements still sum to the old 0.789 (coal 0.355, biomass 0.276, coke 0.118, tars 0.039); rescale them to 1.031 or derive from host shares |
| HPCH007 | gasifier_biomass-chp | RESOLVED | SEC 1.88 GJ biomass/GJ heat (CHP identity); combustion CO2 0 (biomass); no negative rows | none |
| IS001 | coke-oven, BF, BOF, EAF, sinter efficiency variants | RESOLVED | coke-oven moderate 3.91 vs host 4.01; BF moderate 16.05 vs 16.69; BOF strong 0.444 vs 0.457; EAF scrap-preheat 1.72 vs 2.21; sinter 1.61/1.38 vs 1.64 | none |
| IS002 | blast-furnace | RESOLVED | SEC 16.69 GJ/t (10.43-19.41); Remus -0034 total no longer formed; low is the MIDDEN card 10.43 | none (Philibert per-t-crude-steel 18.9 still pooled; minor) |
| IS003 | rolling-mill_hot | RESOLVED | SEC 0.432 GJ/t (0.31-0.49), mill-only rows | central-from text on the fuel row still quotes "natural-gas 1.4957 (guess)" while the value is 0.212: stale text |
| IS004 | rolling-mill_cold | RESOLVED | SEC 0.353 GJ/t, all electricity; fuel 0; no combustion CO2 row | none |
| IS005 | shaft-furnace_hydrogen-direct-reduction | RESOLVED | total 7.74, hydrogen 6.82, electricity 0.91, no natural gas | [R] S150: Devlin's total vs Rechberger 8.09 for Brad |
| IS007 | coke-oven_by-product_efficiency-strong | PARTLY | capex now 692 CAD/t-yr (host 597 + CDQ increment) | opex-fixed 28.9 (cost-ratio) is below the host's sourced 44.7, so levelized 142.7 < host 148; carry host O&M plus increment instead of the ratio |
| IS008 | smelting-vessel_smelting-reduction (+ccs) | PARTLY [R] | total 1.20 t/t (Gielen; Material Economics ruled out) still below combustion 2.17 + process 0.14 | Ruling needed: Hu's 2.17 combustion is gross of export gas vs Gielen's net basis; ccs variant is all guesses (captured 1.0, net 0.2) |
| IS010 | EAF; shaft-furnace_electrolytic-hydrogen; iron electrowinning | PARTLY | EAF and electrowinning now carry only calculated costs (116, 319); Material Economics and Draxler ruled out | shaft-furnace_electrolytic-hydrogen sourced 847 CAD/t (Vogl whole H-DR route incl. electrolyser and EAF; Agora, Devlin too) vs calculated 296; set aside the route rows |
| MCF001 | cement and lime capture kilns; chiller_absorption | RESOLVED | no heat target priced: cement incl-energy 285.6 (energy 90.8 = carriers incl. steam 2.83 x 16.76); lime 262.7; chiller 27.6 (steam + gas split) | none |
| MCF002 | kiln_lime-rotary-preheater_ccs-diffuse | RESOLVED | captured 1.105 = 0.9 x host 1.228; net 0.123 t/t | none |
| MCF003 | calciner_indirect | RESOLVED | combustion CO2 0.066 t/t from natural gas 1.3; carriers electricity 3.04 + gas 1.3 | none |
| MCF004 | kiln_ceramic-electric | RESOLVED | SEC 2.5 GJ/t electricity (1.8-3.5, guess); levelized incl. energy 142.6 | none |
| MCF005 | furnace_hybrid-electric | OPEN [R] | SEC 6.61 GJ/t (Rehfeldt flat glass, 68% electricity) still above host furnace_regenerative 5.55; only the high end moved | S152/P-C9: put the furnace family on one product basis (container glass) and pick a hybrid example on it |
| MCF006 | cement and lime capture kilns | RESOLVED | MEA ruling applied: capture steam 2.83 (cement) and 4.13 (lime) GJ/t | none |
| NFM001 | haul-truck siblings | RESOLVED | rescaled to diesel 0.0226: BEV 0.0087, FC 0.0136, trolley 0.0155, dual-fuel 0.0234 | none |
| NFM002 | electrolysis-cell_prebaked-anode (+15) | RESOLVED | JRC 39.4% ruled out; 93% (85-98) on all 17 cells | none |
| NFM003 | SAG-ball; oxy-fuel melter; inert anode | PARTLY | SAG 0.0673 (electricity pool n=10, now above HPGR 0.0616); oxy-fuel 2.33 (2.0-3.6) | Inert anode still 65.6 GJ/t (MIDDEN card now also an electricity row and sets the pool), above prebaked 53.7 (NM021); rank or exclude the MIDDEN sum against Martin/Morrey/MPP 36-55 |
| NFM004 | process-improvement_pre-reduction | RESOLVED [R] | coke 17.51, electricity 10.26, total 27.77 GJ/t; combustion CO2 1.93 t/t | Ruling still open: may a ferro-chrome source stand for titanium slag pre-reduction? |
| NFM005 | prebaked, Soderberg, prebaked ccs | OPEN [R] | prebaked process CO2e 0.99 (0.38-3.71) still below process CO2 1.54; Soderberg 3.97; total CO2e 2.13; ccs total CO2e 0.708 vs CO2 0.158 | Re-target PFC-only rows to pfc/cf4/c2f6 and build CO2e from species (AR5); drop 1990-factor rows. Listed for Brad |
| NFM006 | digester_bayer | RESOLVED | capex 3,160 CAD/t-yr (2,167-4,153) with cf-alumina-per-aluminium | none |
| NFM007 | leaching-vessel_high-pressure-acid | RESOLVED | capex 21,673 (19,703-23,644); per-feed row ruled out | none |
| NFM008 | melting-furnace_regenerative-oxy-fuel | OPEN | lifetime 6 yr (4-8) still from tp-aries_2024_001-0055, refractory lining ("not the furnace"), not excluded | Exclude or re-target the Aries row to a component lifetime; class rule would give about 25 yr |
| NFM009 | furnace_anode-baking | RESOLVED | SEC 4.19 GJ/t (2.29-4.57); fuel 3.73, electricity 0.46 sum to total | none |
| NFM010 | refinery_nickel-matte | RESOLVED | Brad's net-heat ruling: total 24.12 = electricity 12.6 + heat 11.52 GJ/t Ni | none |
| OG001 | LNG trains, plastic liner, flares | RESOLVED | base-load opex-fixed 74.3 (3.5% of capex 2,138); floating 55; electric 49; methane devices pooled apart | none |
| OG003 | coal SNG, coal FT, GTL | RESOLVED | SEC 0.581, 1.041, 0.893 GJ/GJ (100/eff - product) beside feed 1 | none |
| OG004 | reactor_fluid-coking | PARTLY [R] | zero identity stopped; combustion CO2 0.17 t/m3 (0.12-0.24) drafted guess | Brad to confirm the coke-burn draft; DOE electricity 0.68 GJ/m3 (one row setting the split) not re-checked |
| OG005 | pump_electric-station (+moderate) | OPEN [R] | unchanged: SEC 6e-6 GJ/"m3", annual output 1.7e9 "m3" (really m3-km), capex 0.02 | S151: settle m3-km unit, then redraft SEC near 1e-4 GJ/m3-km with a cited gradient |
| OG006 | reactor_integrated-upgrader_ccs-concentrated | RESOLVED | capex 1,411 = host 1,388 + tier-2 add-on 23 (tier-1 1,800 set aside) | none |
| PB001 | debarker_drum | RESOLVED | capex 33.0 (IETD); log thawing 34.5 | paper-machine still carries Bataille UKTM row 53 at 691 (aggregate "new press section"); check separately |
| PB002 | dryer_steam-heated | RESOLVED | emerging-drying rows ruled out; no fuel carrier; total 4.18 (electricity 0.22, heat 3.96); capex 1,382 (Bataille "new dryers (standard)") | steam pooled apart 4.89 sits above the total; minor |
| PB003 | dryer_through-air | PARTLY | Suhr p.81 rows ruled out; total now 23.79 GJ/t (heat 16.3, electricity 7.49) | The replacement Table 7.18 rows (sc-013) are also "full-mill energy data ranges" (ETS 2008); still whole-mill scope; needs a dryer-only source |
| PB004 | paper-machine_efficiency-strong | RESOLVED | total 1.99 split by host shares: electricity 1.04, steam 0.95 | none |
| PB005 | reactor_hydrothermal-liquefaction | RESOLVED | SEC 0.216 (biomass-solid 0.159, electricity 0.058) + feed 1; matches efficiency 82% | none |
| PB006 | fermenter_grain-dry-mill | RESOLVED | SEC 0.344 GJ/GJ: natural gas 0.313, electricity 0.030; grain feed gone | none |
| PB007 | fermenter dry-mill moderate; dryer_steam-heated moderate | PARTLY [R] | fermenter moderate CO2 0.0146 t/GJ; dryer moderate 0.232 t/t (host-scaled) | dryer_steam-heated_efficiency-strong now shows 0 (zero identity) against host 0.239 and moderate 0.232; rule whether a steam-heated dryer carries scope-1 combustion CO2 (UKERC row) at all, then make the three agree |
| PB008 | anaerobic-digester_effluent | RESOLVED | host off; no MW capacity; annual output 3.0e6 m3 (judgement) | none |
| PB009 | gasifier_biomass-fischer-tropsch_ccs-concentrated | RESOLVED | efficiency 33.5% = host | no capture penalty applied (minor) |
| PB010 | reactor_alcohol-to-jet | RESOLVED | efficiency 90.3% (Tao, HHV); Geleynse mass yields ruled out | none |
| PB011 | boiler_recovery | RESOLVED | total 16.14 GJ/t BLS (16.14-17.45); Martin per-product rows ruled out; partial Suhr total gone | none |
| RX001 | recip drive; turbine drive; diesel field engine | PARTLY | ng/J factor fixed: recip CH4 0.000538, N2O 5.72e-6 t/GJ | Per-fuel-input bridge still not applied (conversion blank on every Clearstone row), so CH4/N2O are per GJ fuel beside CO2 per GJ shaft; multiply by SEC (about 2.65-3.4) |
| RX002 | reciprocating-engine_diesel-field | RESOLVED | SEC 2.65 GJ/GJ (guess), CO2 0.185, CO2e 0.188 t/GJ, levelized incl. energy 66 CAD/GJ | none |
| RX003 | hvac-heater_fuel-fired; recip engines | RESOLVED | CO2e above CO2 on all: hvac 0.0516 vs 0.0513; recip 0.161 vs 0.144 | none |
| RX004 | motor archetypes | RESOLVED | no CO2e totals from UKERC kg/unit; CO2 total 0 | none |
| RX005 | motor moderate; VSD; hvac-heater variants | PARTLY | no SEC below 1 or efficiency above 100: motor moderate SEC 1.031 / 97.0% (capped); hvac strong 97.0%, moderate 88.2% | Motor moderate is pinned at the 97% cap, above motor_premium-efficiency 93.9%: the UKERC system bucket still drives a component saving; VSD now equals the host (1.099, 91%) |
| RX006 | gas-treatment-unit_acid-gas-advanced | RESOLVED | restated per 1000-m3 raw gas: capex 12, SEC 0.35 GJ/1000-m3, annual output 511,105 thousand m3 | none |
| RX007 | refinery_hydroskimming; refinery_deep-conversion | RESOLVED | totals 2.20 and 2.90 GJ/m3 (electricity + fuel); combustion CO2 0.107 and 0.141 under totals 0.132 and 0.191 | none |
| RX008 | melting-furnace_induction | RESOLVED | SEC 1.74 GJ/t from the electricity pool (n=17) | none |
| RX009 | mobile-equipment family | RESOLVED | capacity factor 15% (10-25) judgement on all six | none |
| RX010 | steam-reformer_methane_ccs-diffuse | RESOLVED | plant-level 90%; captured 0.0510 = 0.9 x host 0.0567; net 0.00567 t/GJ | none |
