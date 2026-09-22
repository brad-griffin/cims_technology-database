"""The record for design/end-use-technology-table.csv: one t(...) call per row.

Run it to rebuild the CSV:   python design/build/tech_rows.py

This file is the record and the CSV is the output, so an edit here is the way
to change a technology -- editing the CSV by hand puts the two out of step with
no way to tell which is right. Until 2026-09-15 nothing wrote the CSV at all:
the rows were built into R and then dropped on exit, so an edit here reached
nobody. build_md.py now calls write() before it reads the table, and
build-design-crosswalk.py and design_names.py read what that produced.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent      # design/build
OUT = HERE.parent / "end-use-technology-table.csv"

COLS = ["sector","end-use","technology","type","description","energy-inputs","specific-energy-use","trl","trl-basis","examples","roster-match","cims-match","sources","note"]
# specific-energy-use: left empty for now; efficient variants are to carry their own value once a source is found.
R=[]
def t(*a):
    a = a[:6] + ('',) + a[6:]   # specific-energy-use, empty for now
    assert len(a)==len(COLS), (len(a),a[:3]); R.append(dict(zip(COLS,a)))
X="cross-sector"

# ---------- cross-sector: heat, low temperature ----------
E=(X,"heat-low-temp")
t(*E,"Fuel-fired boiler","conventional","Fire-tube or water-tube boiler raising hot water or low-pressure steam.",
  "natural gas, oil, propane, biomethane, hydrogen","9","commercial; iea_2024_001 rows 389, 387 (hydrogen, biomethane)",
  "packaged fire-tube boilers","boiler_natural-gas; boiler_oil; boiler_hydrogen; boiler_biomethane","<sector>.Steam (NG, HFO, Hydrogen HR and reg burner)","etsap_2010_001; iea_2024_001; CIMS","")
t(*E,"Boiler with post-combustion capture","prospective","The boiler above with an amine or solid-sorbent plant on the flue gas; the regeneration steam is drawn from the boiler itself.",
  "natural gas, oil, biomass, by-product gases; steam and electricity for the capture plant","5","iea_2024_001 row 422; 8-9 at power-station scale (rows 201, 215)","","boiler_ccs; boiler_natural-gas_ccs; boiler_coal_ccs; boiler_biomass_ccs; boiler_by-product-gas_ccs","<sector>.Steam (NG CCS, Coal CCS, Biomass CCS)","iea_2024_001; CIMS","Flue gas is dilute, so the capture plant is the one on cross-sector co2-capture-diffuse and its cost and energy are not repeated here. The steam taken for regeneration is the host-side penalty and belongs on this row. Biomass firing makes it a removal.")
t(*E,"Condensing boiler","efficient variant","Recovers latent heat from the flue gas; needs a low return-water temperature.",
  "natural gas, biomethane, hydrogen","9","commercial","","boiler_efficiency-strong","Light Industrial.Water Heating (High Eff hot water NG)","CIMS","Hot-water duties only.")
t(*E,"Solid-fuel boiler","conventional","Grate or fluidized-bed boiler firing solid fuels.",
  "biomass (hog fuel, pellets), coal, municipal waste","9","iea_2024_001 row 388 (fluidized-bed biomass)","mill hog-fuel boilers","boiler_biomass; boiler_coal","<sector>.Steam (Solid Biomass, Thermal Coal)","iea_2024_001; CIMS","")
t(*E,"Electric boiler","alternative","Resistance or electrode boiler raising hot water or steam at about 99% efficiency.",
  "electricity","9","iea_2024_001 row 437","electrode boilers at MW scale","boiler_electricity","<sector>.Steam (Electric)","iea_2024_001; lbnl_2021_001","")
t(*E,"Industrial heat pump","alternative","Closed-cycle heat pump lifting waste or ambient heat to hot water or low-pressure steam.",
  "electricity; recovered heat","9","iea_2024_001 row 390","ammonia and CO2 heat pumps on washing and drying duties","heat-pump_electricity","","iea_2024_001; etsap_2013_002","Commercial ceiling about 150-165 degC.")
t(*E,"Mechanical vapour recompression","alternative","Compresses process vapour and returns it as usable heat, replacing live steam.",
  "electricity","9","commercial","MVR evaporators and dryers","vapour-recompressor_electricity","","harmonized","")
t(*E,"Solar thermal collectors","alternative","Flat-plate or evacuated-tube collectors for hot water and low-pressure steam.",
  "solar","9","iea_2024_001 row 536","","solar-collector_solar_low-temp","","iea_2024_001","")
t(*E,"Waste-heat recovery unit","conventional","Economizers and heat exchangers recovering heat from flue gas or process streams.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Geothermal direct use","prospective","Hot water drawn from a geothermal well.",
  "geothermal","8","design doc s4.1 (ETSAP E07)","","geothermal-well_geothermal","","design doc s4.1","Little Canadian industrial use.")
t(*E,"Direct-fired air or water heater","conventional","Burner heating air or water directly for washing, drying and space duties.",
  "natural gas, propane, biomethane, hydrogen","9","commercial","make-up air heaters, direct-contact water heaters","direct-heater_natural-gas_low-temp","Light Industrial.Heat.Direct","CIMS","")
t(*E,"Fired heater efficiency measures, moderate","efficient variant","Combustion and recovery measures on an existing fired heater or boiler plant.",
  "natural gas, refinery fuel gas, oil, by-product gases","9","commercial","combustion-air preheat; oxygen trim and burner control; economizer; insulation and steam-trap programs","direct-heater_efficiency-moderate","<sector>.Heat.Direct (Eff)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Fired heater efficiency measures, strong","efficient variant","Air preheat taken to recuperation or regeneration, with the heater train integrated.",
  "natural gas, refinery fuel gas, oil, by-product gases; recovered heat","9","commercial","recuperative or regenerative burners; condensing economizer; pinch-designed preheat train","direct-heater_efficiency-strong","<sector>.Heat.Direct (High Eff)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
# ---------- cross-sector: heat, medium temperature ----------

t(*E,"Back-pressure or extraction steam turbine","conventional","Boiler raises high-pressure steam; the turbine passes it to process at lower pressure.",
  "natural gas, oil, coal, biomass, black liquor, by-product gas","9","commercial","","steam-turbine_steam_back-pressure; steam-turbine_biomass_chp","<sector>.Steam (BPST NG 30 MW)","epa_2017_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Gas turbine with heat-recovery steam generator","conventional","Turbine exhaust raises process steam in an HRSG.",
  "natural gas, hydrogen (TRL 8 pure, 9 blended), biogas","9","commercial; iea_2024_001 rows 255, 252","","combustion-turbine_natural-gas_chp","<sector>.Steam (SCGT HRSG 10/40 MW)","epa_2017_001; iea_2024_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Combined-cycle CHP","conventional","Gas turbine plus steam turbine, with steam extracted for process.",
  "natural gas","9","commercial","","combined-cycle_natural-gas_chp","<sector>.Steam (CCGT 50/250 MW)","epa_2017_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"CHP with post-combustion capture","prospective","Capture plant on the turbine or engine exhaust, with the regeneration steam taken from the unit, which cuts the heat delivered to the site.",
  "natural gas, biogas, by-product gases; steam and electricity for the capture plant","8","iea_2024_001 row 215","","combined-cycle_ccs; combined-cycle_natural-gas_ccs; combined-cycle_by-product-gas_ccs; steam-turbine_natural-gas_ccs","<sector>.Steam (Cogen NG CCS)","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. The heat-to-power ratio after extraction is the host-side fact this row carries. CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Reciprocating engine CHP","conventional","Engine generator with jacket and exhaust heat recovery, at small scale.",
  "natural gas, biogas","9","commercial","","reciprocating-engine_natural-gas_chp","<sector>.Steam (Spark Ignition Reciprocating engine NG 6MW)","epa_2017_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Fuel-cell CHP","alternative","Solid-oxide or molten-carbonate cell producing power and usable heat.",
  "natural gas, hydrogen, biogas","8-9","iea_2024_001 rows 256, 254","","fuel-cell_natural-gas_chp","","iea_2024_001","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Biomass gasifier CHP","prospective","Gasifier feeding an engine or turbine, with heat recovery.",
  "biomass, waste","6","iea_2024_001 row 274","","gasifier_biomass_chp","","iea_2024_001; epa_2007_001","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Small modular reactor CHP","prospective","Reactor supplying process steam and electricity to an industrial site.",
  "nuclear","7-8","iea_2024_001 rows 451, 455","Dow Seadrift with X-energy Xe-100","reactor_nuclear_smr","","iea_2024_001; X-energy/Dow (web)","")

# ---------- cross-sector: on-site power -------- CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
E=(X,"heat-medium-temp")
t(*E,"Fuel-fired boiler","conventional","Water-tube boiler raising medium- or high-pressure steam.",
  "natural gas, oil, by-product gas, biomethane, hydrogen","9","commercial; iea_2024_001 row 379 (hydrogen)","","boiler_natural-gas; boiler_oil","<sector>.Steam","etsap_2010_001; CIMS","")
t(*E,"Boiler with post-combustion capture","prospective","The boiler above with an amine or solid-sorbent plant on the flue gas; the regeneration steam is drawn from the boiler itself.",
  "natural gas, oil, biomass, by-product gases; steam and electricity for the capture plant","5","iea_2024_001 row 422; 8-9 at power-station scale (rows 201, 215)","","boiler_ccs; boiler_natural-gas_ccs; boiler_coal_ccs; boiler_biomass_ccs; boiler_by-product-gas_ccs","<sector>.Steam (NG CCS, Coal CCS, Biomass CCS)","iea_2024_001; CIMS","Flue gas is dilute, so the capture plant is the one on cross-sector co2-capture-diffuse and its cost and energy are not repeated here. Regeneration steam at 120-150 degC competes with the medium-temperature duties this band serves.")
t(*E,"Solid-fuel boiler","conventional","Grate or fluidized-bed boiler firing solid fuels.",
  "biomass, coal, waste","9","iea_2024_001 row 388","","boiler_biomass; boiler_coal","<sector>.Steam","iea_2024_001","")
t(*E,"Electric boiler","alternative","Electrode boiler at MW scale raising saturated steam.",
  "electricity","9","iea_2024_001 row 437","","boiler_electricity","<sector>.Steam (Electric)","iea_2024_001; lbnl_2021_001","")
t(*E,"Steam-generating heat pump","prospective","High-temperature heat pump delivering steam to about 180-200 degC from waste heat.",
  "electricity; recovered heat","7","iea_2024_001 rows 57, 438","Heaten HeatBooster (180 degC steam, Suedzucker 2025)","heat-pump_electricity","","iea_2024_001; Heaten (web)","")
t(*E,"Mechanical vapour recompression","alternative","Steam compressor upgrading low-pressure waste steam to process pressure.",
  "electricity","9","commercial","","vapour-recompressor_electricity","","harmonized","")
t(*E,"Electric thermal energy storage","prospective","Electrically charged solid or salt store discharging steam, decoupling heat from power prices.",
  "electricity","8","iea_2024_001 row 174 (solids storage)","Rondo (100 MWh, >100 bar steam, California, October 2025); Kraftblock; Antora","boiler_electricity_tes","","iea_2024_001; Rondo 2025 (web)","")
t(*E,"Thermal-oil heater","conventional","Fired or electric heater circulating thermal fluid at 200-400 degC without pressure.",
  "natural gas, oil, electricity","9","commercial","","","","harmonized","")
t(*E,"Fired process heater","conventional","Direct-fired heater raising a process stream, as in refinery charge heaters and dryers.",
  "natural gas, refinery fuel gas, oil","9","commercial","","direct-heater_natural-gas_medium-temp","Petroleum Refining.Direct Heat; Light Industrial.Heat.Direct","CIMS","")
t(*E,"Fired heater efficiency measures, strong","efficient variant","Air preheat taken to recuperation or regeneration, with the heater train integrated.",
  "natural gas, refinery fuel gas, oil, by-product gases; recovered heat","9","commercial","recuperative or regenerative burners; condensing economizer; pinch-designed preheat train","direct-heater_efficiency-strong","<sector>.Heat.Direct (High Eff)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Fired heater efficiency measures, moderate","efficient variant","Combustion and recovery measures on an existing fired heater or boiler plant.",
  "natural gas, refinery fuel gas, oil, by-product gases","9","commercial","combustion-air preheat; oxygen trim and burner control; economizer; insulation and steam-trap programs","direct-heater_efficiency-moderate","<sector>.Heat.Direct (Eff)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Electric process heater","alternative","Resistance heater raising a gas or liquid stream in place of a fired heater.",
  "electricity","9","commercial","large circulation heaters","resistance-heater_electricity_medium-temp","Petroleum Refining.Direct Heat (electric heaters)","CIMS","")
t(*E,"Electromagnetic heating (microwave, radio-frequency, infrared)","alternative","Heats the product itself rather than the surrounding air; used in drying and curing.",
  "electricity","9","iea_2024_001 rows 382, 384, 385","","microwave-heater_electricity; radio-frequency-heater_electricity_low-temp","","iea_2024_001","")
t(*E,"Concentrating solar thermal","prospective","Parabolic trough or linear Fresnel field raising steam or thermal oil.",
  "solar","7-9","iea_2024_001 rows 535, 534","","solar-collector_solar_medium-temp","","iea_2024_001","")
# ---------- cross-sector: heat, high temperature ----------

t(*E,"Back-pressure or extraction steam turbine","conventional","Boiler raises high-pressure steam; the turbine passes it to process at lower pressure.",
  "natural gas, oil, coal, biomass, black liquor, by-product gas","9","commercial","","steam-turbine_steam_back-pressure; steam-turbine_biomass_chp","<sector>.Steam (BPST NG 30 MW)","epa_2017_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Gas turbine with heat-recovery steam generator","conventional","Turbine exhaust raises process steam in an HRSG.",
  "natural gas, hydrogen (TRL 8 pure, 9 blended), biogas","9","commercial; iea_2024_001 rows 255, 252","","combustion-turbine_natural-gas_chp","<sector>.Steam (SCGT HRSG 10/40 MW)","epa_2017_001; iea_2024_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Combined-cycle CHP","conventional","Gas turbine plus steam turbine, with steam extracted for process.",
  "natural gas","9","commercial","","combined-cycle_natural-gas_chp","<sector>.Steam (CCGT 50/250 MW)","epa_2017_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"CHP with post-combustion capture","prospective","Capture plant on the turbine or engine exhaust, with the regeneration steam taken from the unit, which cuts the heat delivered to the site.",
  "natural gas, biogas, by-product gases; steam and electricity for the capture plant","8","iea_2024_001 row 215","","combined-cycle_ccs; combined-cycle_natural-gas_ccs; combined-cycle_by-product-gas_ccs; steam-turbine_natural-gas_ccs","<sector>.Steam (Cogen NG CCS)","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. The heat-to-power ratio after extraction is the host-side fact this row carries. CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Reciprocating engine CHP","conventional","Engine generator with jacket and exhaust heat recovery, at small scale.",
  "natural gas, biogas","9","commercial","","reciprocating-engine_natural-gas_chp","<sector>.Steam (Spark Ignition Reciprocating engine NG 6MW)","epa_2017_001; CIMS","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Fuel-cell CHP","alternative","Solid-oxide or molten-carbonate cell producing power and usable heat.",
  "natural gas, hydrogen, biogas","8-9","iea_2024_001 rows 256, 254","","fuel-cell_natural-gas_chp","","iea_2024_001","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Biomass gasifier CHP","prospective","Gasifier feeding an engine or turbine, with heat recovery.",
  "biomass, waste","6","iea_2024_001 row 274","","gasifier_biomass_chp","","iea_2024_001; epa_2007_001","CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
t(*E,"Small modular reactor CHP","prospective","Reactor supplying process steam and electricity to an industrial site.",
  "nuclear","7-8","iea_2024_001 rows 451, 455","Dow Seadrift with X-energy Xe-100","reactor_nuclear_smr","","iea_2024_001; X-energy/Dow (web)","")

# ---------- cross-sector: on-site power -------- CHP: the heat is the service and the electricity a co-product (design doc D1). Moved off the retired chp end use, 2026-09-14.")
E=(X,"heat-high-temp")
t(*E,"Fired furnace or process heater","conventional","Burner-fired furnace or heater above 400 degC, separable from the process unit.",
  "natural gas, oil, refinery and by-product gas, biomethane (TRL 9), hydrogen (TRL 8), ammonia (TRL 5)","9","commercial; iea_2024_001 rows 378, 379, 377",
  "","furnace_natural-gas; furnace_hydrogen; furnace_ammonia","Petroleum Refining.Direct Heat; Light Industrial.Heat.Direct","iea_2024_001; CIMS","")
t(*E,"Fired heater or furnace with post-combustion capture","prospective","Capture plant on the flue gas of a fired heater or furnace; the delivered duty is unchanged and the regeneration steam is imported.",
  "natural gas, refinery fuel gas, by-product gases; steam and electricity for the capture plant","3-4","iea_2024_001 row 228","","direct-heater_ccs; furnace_ccs","<sector>.CCS","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. What holds this back is the number of small stacks, not the chemistry.")
t(*E,"Regenerative or oxy-fuel burner furnace","efficient variant","Preheats combustion air, or fires on oxygen, cutting flue-gas losses.",
  "natural gas, oil, hydrogen; oxygen","9","commercial","regenerative burners; oxy-fuel glass furnaces","furnace_preheat","Iron and Steel.Reheating (recuperated reheat furnace)","CIMS","")
t(*E,"Electric resistance furnace","alternative","Resistance elements heating the charge or chamber directly.",
  "electricity","9","commercial","heat-treatment furnaces","resistance-heater_electricity_high-temp","","harmonized","")
t(*E,"Induction heating","alternative","Induces eddy currents in the workpiece; for conductive materials.",
  "electricity","9","iea_2024_001 row 372","billet and slab induction heaters","induction-heater_electricity","Iron and Steel.Reheating (induction reheat furnace)","iea_2024_001; CIMS","")
t(*E,"Electric arc or plasma heating","prospective","Arc or plasma torch heating a gas or charge to very high temperature.",
  "electricity","6","iea_2024_001 row 371","","arc-heater_electricity; plasma-torch_electricity","","iea_2024_001","")
t(*E,"Rotodynamic heater","prospective","Rotating machine converting electricity to heat in a gas stream at furnace temperatures.",
  "electricity","6","iea_2024_001 row 375","Coolbrook RotoDynamic Heater (over 1,000 degC in pilot, Brightlands Chemelot)","rotary-compression-heater_electricity","","iea_2024_001; Coolbrook 2024 (web)","")
t(*E,"Electric thermal energy storage","prospective","Electrically charged refractory or carbon store discharging hot gas above 1,000 degC.",
  "electricity","8","iea_2024_001 row 174","Rondo; Antora; Kraftblock","","","iea_2024_001; Rondo 2025 (web)","")
t(*E,"Concentrating solar for high-temperature heat","prospective","Solar tower or dish concentrating to furnace temperatures.",
  "solar","6","iea_2024_001 row 381","","solar-concentrator_solar","","iea_2024_001","")
t(*E,"High-temperature gas-cooled reactor","prospective","Small modular reactor delivering high-temperature steam or process heat.",
  "nuclear","8","iea_2024_001 row 451","Dow Seadrift with X-energy Xe-100 (construction permit under review)","reactor_nuclear_htgr","","iea_2024_001; X-energy/Dow (web)","")

# ---------- cross-sector: CHP ----------
E=(X,"on-site-power-generation")
t(*E,"Diesel generator set","conventional","Reciprocating diesel generator, the standard off-grid supply.",
  "diesel, renewable diesel","9","commercial","off-grid mine power plants","","","Energies 2026 mining review (web)","")
t(*E,"Generating set efficiency measures, moderate","efficient variant","Raising the electrical efficiency of an existing on-site set.",
  "natural gas, diesel, by-product gases","9","commercial","combined-cycle conversion of a simple-cycle set; lean-burn engine upgrade; turbine inlet cooling","combined-cycle_efficiency-moderate","","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Gas engine or simple-cycle gas turbine","conventional","Gas-fired generator without heat recovery.",
  "natural gas, associated gas","9","iea_2024_001 row 214","upstream oil and gas sites","","","iea_2024_001","")
t(*E,"Condensing steam turbine","conventional","Boiler and condensing turbine producing power only.",
  "natural gas, coal, biomass, by-product gas","9","commercial","steelworks power plants firing coke-oven gas","steam-turbine_steam_condensing","","harmonized; nrcan_2025_001","")
t(*E,"Waste-heat power (ORC or steam Rankine)","alternative","Converts exhaust or process heat to electricity.",
  "recovered heat","9","iea_2024_001 row 516","ORC on kiln and compressor exhaust","","","iea_2024_001","")
t(*E,"Solar PV with battery storage","alternative","Site-scale PV and storage displacing genset fuel.",
  "solar; electricity storage","9","iea_2024_001 rows 527, 580","remote mine microgrids","","","iea_2024_001","")
t(*E,"Wind turbines at site","alternative","Site wind generation, usually with storage, at remote operations.",
  "wind","9","commercial","Raglan Mine (Nunavik) wind and storage","","","Energies 2026 mining review (web)","")
t(*E,"Microreactor","prospective","Factory-built heat-pipe reactor sized for a remote site.",
  "nuclear","5","iea_2024_001 row 450","Westinghouse eVinci","","","iea_2024_001","")

# ---------- cross-sector: hydrogen and fuel supply ----------
E=(X,"pumps")
t(*E,"Induction motor, standard efficiency","conventional","IE2-IE3 squirrel-cage motor driving a pump, fan or compressor.",
  "electricity","9","commercial","","motor","<sector>.Machine Drive; Natural Gas.Production.Supply.Direct Drive Large (Std AC motor 500 hp)","CIMS","")
t(*E,"Premium-efficiency motor","efficient variant","IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs.",
  "electricity","9","commercial","","motor_efficiency-moderate","<sector>.Direct Drive (Eff AC motor 500 hp); light-industrial.service.machine-drive (High efficiency)","CIMS","")
t(*E,"Variable-speed drive","efficient variant","Matches motor speed to load instead of throttling.",
  "electricity","9","commercial","","","<sector>.Direct Drive (Motor speed control variable speed); natural-gas.service.compressor-drive.engine (Reciprocating compressor Efficient)","CIMS","CIMS carries the drive as its own `Direct Drive` service in seven sectors; the hierarchy folds it in here as a variant of the motor.")
t(*E,"Gas engine or gas turbine drive","conventional","Engine or turbine driving a compressor or pump directly.",
  "natural gas","9","iea_2024_001 row 214","pipeline and field compressors","combustion-turbine_natural-gas","Natural Gas.Production.Supply.Direct Drive Large (Natural Gas turbine); Petroleum Crude.Industrial Engines","iea_2024_001; CIMS","")
t(*E,"Turbine or engine drive efficiency measures, moderate","efficient variant","Driver upgrades and staging on gas-driven compression and pumping.",
  "natural gas, field gas","9","commercial","high-efficiency gas-turbine drives; lean-burn engine retrofit; driver right-sizing and staging","combustion-turbine_efficiency-moderate; compressor_efficiency-moderate","Natural Gas.Production.Supply.Direct Drive {Large, Small} (Eff)","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Steam turbine drive","conventional","Back-pressure turbine driving a large compressor or pump.",
  "steam","9","commercial","refinery and chemical compressor drives","steam-turbine","","harmonized","")

# ---------- cross-sector: air separation ----------
t(*E,"Pump system optimization","efficient variant","Right-sizing, impeller trimming and control changes on the pump system rather than the pump.",
  "electricity","9","commercial","impeller trimming; parallel staging; control-valve removal","pump_efficiency-moderate","","harmonized","")
E=(X,"fans-and-blowers")
t(*E,"Induction motor, standard efficiency","conventional","IE2-IE3 squirrel-cage motor driving a pump, fan or compressor.",
  "electricity","9","commercial","","motor","<sector>.Machine Drive; Natural Gas.Production.Supply.Direct Drive Large (Std AC motor 500 hp)","CIMS","")
t(*E,"Premium-efficiency motor","efficient variant","IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs.",
  "electricity","9","commercial","","motor_efficiency-moderate","<sector>.Direct Drive (Eff AC motor 500 hp); light-industrial.service.machine-drive (High efficiency)","CIMS","")
t(*E,"Variable-speed drive","efficient variant","Matches motor speed to load instead of throttling.",
  "electricity","9","commercial","","","<sector>.Direct Drive (Motor speed control variable speed); natural-gas.service.compressor-drive.engine (Reciprocating compressor Efficient)","CIMS","CIMS carries the drive as its own `Direct Drive` service in seven sectors; the hierarchy folds it in here as a variant of the motor.")
t(*E,"Gas engine or gas turbine drive","conventional","Engine or turbine driving a compressor or pump directly.",
  "natural gas","9","iea_2024_001 row 214","pipeline and field compressors","combustion-turbine_natural-gas","Natural Gas.Production.Supply.Direct Drive Large (Natural Gas turbine); Petroleum Crude.Industrial Engines","iea_2024_001; CIMS","")
t(*E,"Turbine or engine drive efficiency measures, moderate","efficient variant","Driver upgrades and staging on gas-driven compression and pumping.",
  "natural gas, field gas","9","commercial","high-efficiency gas-turbine drives; lean-burn engine retrofit; driver right-sizing and staging","combustion-turbine_efficiency-moderate; compressor_efficiency-moderate","Natural Gas.Production.Supply.Direct Drive {Large, Small} (Eff)","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Steam turbine drive","conventional","Back-pressure turbine driving a large compressor or pump.",
  "steam","9","commercial","refinery and chemical compressor drives","steam-turbine","","harmonized","")

# ---------- cross-sector: air separation ----------
t(*E,"Fan system optimization","efficient variant","High-efficiency fan selection with duct and damper changes.",
  "electricity","9","commercial","airfoil fans; damper-to-VSD conversion; duct resizing","fan_efficiency-moderate","","harmonized","")
E=(X,"compressed-air")
t(*E,"Induction motor, standard efficiency","conventional","IE2-IE3 squirrel-cage motor driving a pump, fan or compressor.",
  "electricity","9","commercial","","motor","<sector>.Machine Drive; Natural Gas.Production.Supply.Direct Drive Large (Std AC motor 500 hp)","CIMS","")
t(*E,"Premium-efficiency motor","efficient variant","IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs.",
  "electricity","9","commercial","","motor_efficiency-moderate","<sector>.Direct Drive (Eff AC motor 500 hp); light-industrial.service.machine-drive (High efficiency)","CIMS","")
t(*E,"Variable-speed drive","efficient variant","Matches motor speed to load instead of throttling.",
  "electricity","9","commercial","","","<sector>.Direct Drive (Motor speed control variable speed); natural-gas.service.compressor-drive.engine (Reciprocating compressor Efficient)","CIMS","CIMS carries the drive as its own `Direct Drive` service in seven sectors; the hierarchy folds it in here as a variant of the motor.")
t(*E,"Gas engine or gas turbine drive","conventional","Engine or turbine driving a compressor or pump directly.",
  "natural gas","9","iea_2024_001 row 214","pipeline and field compressors","combustion-turbine_natural-gas","Natural Gas.Production.Supply.Direct Drive Large (Natural Gas turbine); Petroleum Crude.Industrial Engines","iea_2024_001; CIMS","")
t(*E,"Turbine or engine drive efficiency measures, moderate","efficient variant","Driver upgrades and staging on gas-driven compression and pumping.",
  "natural gas, field gas","9","commercial","high-efficiency gas-turbine drives; lean-burn engine retrofit; driver right-sizing and staging","combustion-turbine_efficiency-moderate; compressor_efficiency-moderate","Natural Gas.Production.Supply.Direct Drive {Large, Small} (Eff)","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Steam turbine drive","conventional","Back-pressure turbine driving a large compressor or pump.",
  "steam","9","commercial","refinery and chemical compressor drives","steam-turbine","","harmonized","")

# ---------- cross-sector: air separation ----------
t(*E,"Compressed-air system management","efficient variant","Leak management, pressure reduction and sequencing across the compressor house.",
  "electricity","9","commercial","leak surveys; pressure optimization; sequencing controls; heat recovery","compressor_efficiency-moderate","","harmonized","")
E=(X,"materials-handling")
t(*E,"Induction motor, standard efficiency","conventional","IE2-IE3 squirrel-cage motor driving a pump, fan or compressor.",
  "electricity","9","commercial","","motor","<sector>.Machine Drive; Natural Gas.Production.Supply.Direct Drive Large (Std AC motor 500 hp)","CIMS","")
t(*E,"Premium-efficiency motor","efficient variant","IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs.",
  "electricity","9","commercial","","motor_efficiency-moderate","<sector>.Direct Drive (Eff AC motor 500 hp); light-industrial.service.machine-drive (High efficiency)","CIMS","")
t(*E,"Variable-speed drive","efficient variant","Matches motor speed to load instead of throttling.",
  "electricity","9","commercial","","","<sector>.Direct Drive (Motor speed control variable speed); natural-gas.service.compressor-drive.engine (Reciprocating compressor Efficient)","CIMS","CIMS carries the drive as its own `Direct Drive` service in seven sectors; the hierarchy folds it in here as a variant of the motor.")
t(*E,"Conveying in place of truck haulage","efficient variant","Fixed conveying and hoisting replacing engine-driven movement of solids.",
  "electricity","9","commercial","in-pit crushing and conveying; overland conveyors","conveyor_efficiency-moderate","","harmonized","")
E=(X,"materials-processing")
t(*E,"Induction motor, standard efficiency","conventional","IE2-IE3 squirrel-cage motor driving a pump, fan or compressor.",
  "electricity","9","commercial","","motor","<sector>.Machine Drive; Natural Gas.Production.Supply.Direct Drive Large (Std AC motor 500 hp)","CIMS","")
t(*E,"Premium-efficiency motor","efficient variant","IE4-IE5 motor, including permanent-magnet and synchronous-reluctance designs.",
  "electricity","9","commercial","","motor_efficiency-moderate","<sector>.Direct Drive (Eff AC motor 500 hp); light-industrial.service.machine-drive (High efficiency)","CIMS","")
t(*E,"Variable-speed drive","efficient variant","Matches motor speed to load instead of throttling.",
  "electricity","9","commercial","","","<sector>.Direct Drive (Motor speed control variable speed); natural-gas.service.compressor-drive.engine (Reciprocating compressor Efficient)","CIMS","CIMS carries the drive as its own `Direct Drive` service in seven sectors; the hierarchy folds it in here as a variant of the motor.")
E=(X,"space-heating")
t(*E,"Fuel-fired space or make-up air heater","conventional","Unit heaters, radiant tubes and make-up air units firing gas.",
  "natural gas, propane, oil","9","commercial","","","<sector>.HVAC.Space Heating","CIMS","")
t(*E,"Space-heating heat pump","alternative","Air-source or ground-source heat pump for building heat and cooling.",
  "electricity","9","iea_2024_001 rows 53, 75","","heat-pump_electricity","","iea_2024_001","")
t(*E,"Electric resistance space heating","conventional","Unit heaters and baseboards.",
  "electricity","9","commercial","","","<sector>.HVAC.Space Heating (electric)","CIMS","")
t(*E,"Heat-recovery ventilation","efficient variant","Exhaust air preheats or precools the incoming supply air.","electricity; recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","Building ventilation.")
t(*E,"Demand-controlled ventilation","efficient variant","Air flow set by occupancy or contaminant sensing.","electricity","9","commercial","","","","harmonized","Building ventilation.")
E=(X,"lighting")
t(*E,"Fluorescent or high-intensity discharge lighting","conventional","The incumbent industrial lighting stock.",
  "electricity","9","commercial","","","<sector>.Lighting","CIMS","")
t(*E,"LED lighting with controls","efficient variant","Solid-state lighting with occupancy and daylight controls.",
  "electricity","9","commercial","","","<sector>.Lighting (efficient)","CIMS","")

# ---------- cross-sector: mobile equipment ----------
E=(X,"mobile-equipment")
t(*E,"Diesel non-road equipment","conventional","Loaders, forklifts, yard trucks and construction equipment on diesel engines.",
  "diesel, renewable diesel, biodiesel blends","9","commercial","","","Construction.Transport (Diesel)","CIMS","")
t(*E,"Propane or natural gas forklift","conventional","Spark-ignition industrial truck.",
  "propane, natural gas","9","commercial","","","","harmonized","")
t(*E,"Battery-electric equipment","alternative","Battery drive for forklifts, loaders and excavators.",
  "electricity","8-9","iea_2024_001 row 135; commercial for forklifts","","","Construction.Transport (Electric)","iea_2024_001; CIMS","")
t(*E,"Hydrogen fuel-cell equipment","prospective","Fuel-cell drive, commercial in forklifts and in demonstration for heavy equipment.",
  "hydrogen","6-9","commercial (forklifts); demonstration (heavy equipment)","","","","harmonized","TRL spans the two classes of equipment.")
t(*E,"Diesel-electric hybrid equipment","efficient variant","Series or parallel hybrid drive recovering braking and smoothing engine load.",
  "diesel, electricity","9","commercial","","","","harmonized","")

# ---------- cross-sector: capture ----------
E=(X,"co2-capture-concentrated")
t(*E,"Dehydration and compression","conventional","Dries and compresses an already pure CO2 stream for transport.",
  "electricity","9","ipcc_2022_001 Table 11.3 (CCUS of concentrated CO2)","Alberta Carbon Trunk Line: Nutrien Redwater fertilizer plant; ethanol plants","capture-unit","<sector>.CCS","ipcc_2022_001","")
t(*E,"Chemical solvent on process gas","conventional","Amine absorption on shifted syngas or acid gas, then regeneration.",
  "steam, electricity","9","iea_2024_001 row 285","Quest (Shell Scotford upgrader hydrogen units)","capture-unit_hydrogen","Petroleum Crude.CCS (SMR CCS)","iea_2024_001; CIMS","")
t(*E,"Physical solvent","conventional","Selexol or Rectisol absorption at pressure on gasifier syngas.",
  "electricity, steam","9","commercial","Sturgeon refinery","","","harmonized","")
t(*E,"Pressure or vacuum swing adsorption","conventional","Adsorbent beds separating CO2 from hydrogen-plant syngas.",
  "electricity","9","commercial","Air Products Port Arthur","","","harmonized","")
t(*E,"Cryogenic separation","prospective","Condenses CO2 from a pressurized stream at low temperature.",
  "electricity","6","iea_2024_001 row 334","Air Liquide Cryocap","","","iea_2024_001","")
E=(X,"co2-capture-diffuse")
t(*E,"Amine post-combustion capture","conventional","Absorbs CO2 from flue gas into an amine solvent; steam strips it back out.",
  "steam (reboiler), electricity","7-9","iea_2024_001 rows 332, 333; ipcc_2022_001 Table 11.3","Boundary Dam (Cansolv); Entropy Glacier; Brevik cement","capture-unit_ccs","<sector>.CCS","iea_2024_001; ipcc_2022_001","TRL 9 in power, 7-8 on cement kilns.")
t(*E,"Advanced low-energy solvent","efficient variant","Second-generation solvents cutting reboiler duty against first-generation MEA.",
  "steam, electricity","8","assessed (commercial licences)","KS-21; Cansolv DC-103","","","harmonized","")
t(*E,"Solid sorbent capture","prospective","Structured adsorbent beds cycling on temperature or pressure, with lower heat demand.",
  "low-temperature heat, electricity","6","iea_2024_001 row 337","Svante (Lafarge Richmond pilot)","","","iea_2024_001; Svante (web)","")
t(*E,"Calcium looping","prospective","Lime carries CO2 between a carbonator and a calciner, with high-grade heat recovery.",
  "fuel, electricity","7","iea_2024_001 row 331","","capture-unit_ccs","","iea_2024_001","")
t(*E,"Cryogenic post-combustion capture","prospective","Chills flue gas so CO2 desublimates or condenses out.",
  "electricity","6","iea_2024_001 row 334","","","","iea_2024_001","")
E=(X,"direct-air-capture")
t(*E,"Liquid-solvent DAC","prospective","Alkaline solution captures CO2; a high-temperature calciner regenerates it.",
  "natural gas or electricity (calciner), electricity","6","iea_2024_001 row 95","Carbon Engineering (Squamish); 1PointFive Stratos","capture-unit_direct","","iea_2024_001; Stratos (web)","")
t(*E,"Solid-sorbent DAC","prospective","Sorbent beds cycled at low temperature, suited to waste heat and modular build.",
  "low-temperature heat, electricity","7","iea_2024_001 row 96","Climeworks; Deep Sky Alpha (Innisfail, Alberta, operating since August 2025)","capture-unit_direct","","iea_2024_001; Deep Sky 2025 (web)","")

# ---------- iron and steel ----------
S="iron-and-steel"
E=(S,"cokemaking")
t(*E,"By-product coke oven battery","conventional","Slot ovens carbonizing coal, with the gas cleaned and recovered as coke-oven gas and chemicals.",
  "coking coal; coke-oven and blast-furnace gas (underfiring)","9","commercial","ArcelorMittal Dofasco coke plant (Hamilton); Algoma ovens decommissioned January 2026","coke-oven_coal","","etsap_2010_002; Algoma 2025 (web); GEM Dofasco (web)","")
t(*E,"Coke oven efficiency measures, strong","efficient variant","Recovering the heat now lost in quenching and in the raw gas, the measures the roster files as the strong bucket.",
  "coke-oven gas; recovered heat (raises steam)","9","commercial","coke dry quenching; coke-oven gas sensible-heat recovery","coke-oven_efficiency-moderate","Iron and Steel.Coke","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column. Dry quenching raises steam and cuts coke breeze, and is the measure this bucket is usually named for.")
t(*E,"Coke oven efficiency measures, moderate","efficient variant","Battery housekeeping and control, each worth a few per cent of heating fuel.",
  "coke-oven gas, blast-furnace gas, natural gas","9","commercial","reduced air leakage; battery insulation; heating control and pressure regulation","coke-oven_efficiency-moderate","Iron and Steel.Coke","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Heat-recovery coke oven","alternative","Non-recovery ovens burning the volatiles on site and raising steam for power.",
  "coking coal","9","commercial","","","","harmonized","No Canadian stock.")
E=(S,"agglomeration")
t(*E,"Sinter strand","conventional","Travelling-grate strand fusing ore fines, fluxes and coke breeze into sinter.",
  "coke breeze, natural gas, electricity","9","commercial","","sinter-plant","Iron and Steel.Agglomeration (Iron sinter agglomeration)","CIMS; etsap_2010_002","")
t(*E,"Sinter plant efficiency measures, strong","efficient variant","Recirculating part of the waste gas and recovering cooler heat.",
  "coke breeze, natural gas; recovered heat","9","commercial","waste-gas recirculation (EPOSINT, EOS); sinter-cooler exhaust gas heat recovery","sinter-plant_efficiency-strong","Iron and Steel.Sinter","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Sinter plant efficiency measures, moderate","efficient variant","Charging, bed and sealing measures on an existing sinter strand.",
  "coke breeze, natural gas","9","commercial","improved charging; increased bed depth; reduced air leakage; ignition-hood control","sinter-plant_efficiency-moderate","Iron and Steel.Sinter","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Pellet induration (straight-grate, grate-kiln)","conventional","Hardens green pellets on a travelling grate or grate-kiln.",
  "heavy oil, natural gas, coke/coal, electricity","9","commercial","","pellet-plant","","nrcan_2025_001","Most Canadian pelletizing is at the mines; see mining pelletizing.")
t(*E,"Plasma or electric induration","prospective","Replaces the burner with plasma torches or electric heating in the induration furnace.",
  "electricity","5","iea_2024_001 row 409","LKAB plasma trials","pellet-plant","","iea_2024_001","")
E=(S,"ironmaking")
t(*E,"Blast furnace","conventional","Coke-based counter-current shaft reducing iron ore to hot metal, with hot stoves.",
  "coke, pulverized coal, natural gas; hydrogen injection (TRL 7), biomass or charcoal injection (TRL 9)","9","commercial; iea_2024_001 rows 406, 410",
  "Stelco Lake Erie; ArcelorMittal Dofasco BF2 and BF4 (retirement scheduled 2030)","blast-furnace; blast-furnace_coal; blast-furnace_biomass","Iron and Steel.Molten Steel.Integrated (BF-BOF)","iea_2024_001; CIMS; GEM Dofasco (web)","")
t(*E,"Blast furnace efficiency measures, strong","efficient variant","Heat recovery off the stoves and the slag, the measures the roster separates as the strong bucket.",
  "coke, coal, natural gas, by-product gases; recovered heat","9","commercial","hot stove waste-heat recovery; slag heat recovery; top-gas heat recovery","","Iron and Steel.Molten Steel.Integrated (BF-BOF, efficiency options)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Blast furnace efficiency measures, moderate","efficient variant","Incremental measures on an existing blast furnace, each worth a few per cent of fuel.",
  "coke, coal, natural gas, by-product gases","9","commercial","top-pressure recovery turbine; improved burden distribution; higher pulverized coal injection; dry gas cleaning","blast-furnace_efficiency-moderate","Iron and Steel.Molten Steel.Integrated (BF-BOF, efficiency options)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Blast furnace with post-combustion capture","prospective","Capture on the blast-furnace gas, or on the stoves and power plant that burn it.",
  "coke, coal, natural gas; steam and electricity for the capture plant","5","iea_2024_001 row 412","","blast-furnace_ccs; blast-furnace_hydrogen_ccs; capture-unit_by-product-gas_ccs","Iron and Steel.CCS","iea_2024_001; CIMS","Blast-furnace gas is about a fifth CO2, so this is the dilute plant on cross-sector co2-capture-diffuse. Top-gas recycling concentrates the stream instead and is its own row.")
t(*E,"Top-gas recycling oxygen blast furnace","prospective","Oxygen blast with CO2 stripped from the recycled top gas, which also concentrates the CO2.",
  "coke, coal, oxygen; electricity","6","ukerc_2013_001 via harmonized; iea_2024_001 row 412","ULCOS experimental blast furnace; COURSE50","blast-furnace_top-gas-recycling; blast-furnace_top-gas-recycling-ccs","Iron and Steel.Molten Steel.Integrated (Top gas recycling CCS)","ukerc_2013_001; iea_2024_001; CIMS","Recycling concentrates the top gas, so capture sits on cross-sector co2-capture-concentrated rather than the dilute plant a conventional blast furnace needs.")
t(*E,"Shaft-furnace direct reduction","conventional","Reduces pellets in a shaft with reformed gas or hydrogen, giving solid DRI for an EAF.",
  "natural gas (TRL 9), hydrogen (TRL 6-7)","9","iea_2024_001 rows 394, 392, 395",
  "MIDREX; Energiron; ArcelorMittal Contrecoeur; Dofasco Energiron ZR project (2.5 Mt/yr, announced); HYBRIT; Stegra","shaft-furnace_midrex; shaft-furnace_hyl; shaft-furnace_hydrogen","Iron and Steel.Molten Steel.Integrated (DRI + EAF, HDRI + EAF)","iea_2024_001; CIMS; GEM Dofasco (web)","")
t(*E,"Gas-based direct reduction with capture on the CO2 removal unit","alternative","A gas-based DRI plant already strips CO2 from the recycled top gas, so capture is dehydration and compression on a nearly pure stream.",
  "natural gas; electricity for compression","9","iea_2024_001 row 394","Al Reyadah, Abu Dhabi","shaft-furnace_ccs; shaft-furnace_by-product-gas_ccs","Iron and Steel.CCS","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. The reformer and heater flue gas is a separate, dilute stream.")
t(*E,"Fluidized-bed direct reduction","prospective","Reduces ore fines directly, skipping pelletizing.",
  "hydrogen, natural gas","6","assessed (Primetals HYFOR pilot; Circored operated commercially)","HYFOR; Circored","shaft-furnace","","HYFOR (web)","")
t(*E,"Bath smelting reduction","prospective","Smelts coal and ore fines in one vessel, with no coke ovens or sinter plant; off-gas is CO2-rich.",
  "coal, oxygen","6","ukerc_2013_001 via harmonized; iea_2024_001 row 415","HIsarna pilot at Tata Steel IJmuiden (60 kt/yr)","smelting-vessel_hisarna; smelting-vessel_hisarna-ccs","Iron and Steel.Molten Steel.Integrated (HIsarna CCS)","ukerc_2013_001; iea_2024_001; GEM HIsarna (web)","Oxygen blowing concentrates the off-gas, so capture sits on cross-sector co2-capture-concentrated rather than the dilute plant a blast furnace needs.")
t(*E,"Two-stage smelting reduction","alternative","Pre-reduction shaft plus a melter-gasifier running on coal, avoiding coke ovens.",
  "coal, oxygen","9","commercial","Corex; Finex","smelting-vessel_coal_corex","Iron and Steel.Molten Steel.Integrated (Corex smelter)","etsap_2010_002; CIMS","No Canadian stock.")
t(*E,"Electric smelting furnace for DRI","prospective","Melts DRI made from lower-grade ore into hot metal for a BOF, removing gangue as slag.",
  "electricity, carbon","6-7","assessed (NeoSmelt pilot study 2025-26; the furnace type is commercial in ferroalloys)","NeoSmelt (Kwinana); Primetals Smelter","smelting-vessel_electricity","Iron and Steel.Molten Steel.Integrated (Smelter + EAF)","ARENA NeoSmelt (web); CIMS","")
t(*E,"Molten oxide electrolysis","prospective","Electrolyzes iron oxide above 1,500 degC, giving liquid iron and oxygen.",
  "electricity","5","iea_2024_001 row 402","Boston Metal (demonstration cell)","electrolysis-cell_electricity","","iea_2024_001; Boston Metal (web)","")
t(*E,"Low-temperature iron electrowinning","prospective","Dissolves ore in an aqueous electrolyte and plates out iron near ambient temperature.",
  "electricity","5","iea_2024_001 row 408","Electra (demonstration plant, about 500 t/yr, 2026); Siderwin","electrolysis-cell_electricity_ulcowin","","iea_2024_001; Electra (web)","")
E=(S,"steelmaking")
t(*E,"Basic oxygen furnace","conventional","Blows oxygen through hot metal to burn out carbon; scrap is the coolant.",
  "hot metal chemical energy, oxygen, scrap","9","commercial","","basic-oxygen-furnace","Iron and Steel.Molten Steel.Integrated (BF-BOF)","etsap_2010_002; CIMS","")
t(*E,"Basic oxygen furnace efficiency measures, strong","efficient variant","Recovering the converter gas and its sensible heat instead of flaring it.",
  "oxygen, electricity; by-product gases","9","commercial","converter gas collection and use; sensible heat recovery on the off-gas hood","basic-oxygen-furnace_efficiency-strong","Iron and Steel.Molten Steel.Integrated (BOF)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Basic oxygen furnace efficiency measures, moderate","efficient variant","Drive and control measures on the converter and its gas-cleaning plant.",
  "oxygen, electricity; by-product gases","9","commercial","variable-speed drives on fan motors; improved gas cleaning; lining and ladle management","basic-oxygen-furnace_efficiency-moderate","Iron and Steel.Molten Steel.Integrated (BOF)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Electric arc furnace","conventional","Melts scrap or DRI with graphite electrodes, with oxy-fuel burners and chemical energy.",
  "electricity, oxygen, natural gas, charge carbon","9","commercial","Algoma (first EAF July 2025, second in 2026); ArcelorMittal Dofasco; Gerdau Whitby","electric-arc-furnace","Iron and Steel.Molten Steel.Recycled (High power EAF)","ukerc_2013_001; Algoma 2025 (web); CIMS","")
t(*E,"High-efficiency EAF","efficient variant","Ultra-high power with scrap preheating or continuous charging, cutting electricity and tap-to-tap time.",
  "electricity, oxygen, natural gas","9","commercial","Consteel; Quantum; EcoArc","electric-arc-furnace_electricity_preheat; electric-arc-furnace_efficiency-moderate","Iron and Steel.Molten Steel.Recycled (Ultra power EAF + O2)","harmonized; CIMS","")
t(*E,"Ladle metallurgy furnace","conventional","Arc-heated ladle station for alloying, desulphurization and temperature control.",
  "electricity, argon","9","commercial","","","Iron and Steel.Molten Steel.Ladle Refining","CIMS","")
t(*E,"Ladle preheating","conventional","Gas burners drying and preheating ladle refractory; oxy-fuel and electric units are the alternatives.",
  "natural gas; oxygen; electricity","9","commercial","","furnace_natural-gas_preheat; furnace_electricity_preheat","Iron and Steel.Molten Steel.Ladle Preheat (NG, Electric)","CIMS","")
E=(S,"casting")
t(*E,"Continuous casting","conventional","Casts liquid steel into slabs, blooms or billets in a continuous strand.",
  "electricity, water","9","commercial","","caster; continuous-casting","Iron and Steel.Steel Product.Slabs.Casting (Continued casting)","CIMS","")
t(*E,"Ingot casting","conventional","Casts into ingots, reheated in soaking pits before rolling.",
  "natural gas, oil, electricity","9","commercial","","caster","Steel Product.Slabs.Casting (Ingot casting, soaking pit and slab mill)","CIMS","Legacy route; CIMS keeps it for the remaining stock.")
t(*E,"Thin-slab casting with direct rolling","efficient variant","Casts a thin slab and rolls it hot in line, cutting reheating and rolling passes.",
  "natural gas, electricity","9","commercial","CSP; Arvedi ESP","","Steel Product.Slabs.Casting (Thin slab casting)","CIMS","")
t(*E,"Strip casting","alternative","Casts near-net-shape strip directly from liquid steel.",
  "electricity","9","commercial","Castrip","","Steel Product.Slabs.Casting (Strip casting)","CIMS","No Canadian stock.")
E=(S,"reheating")
t(*E,"Reheating furnace, fuel-fired","conventional","Walking-beam or pusher furnace heating semis to about 1,200 degC before rolling.",
  "natural gas, coke-oven and blast-furnace gas, oil; hydrogen","9","commercial; iea_2024_001 row 379 (hydrogen)","","furnace_natural-gas; rolling-mill_natural-gas","Iron and Steel.Reheating.Reheators (NG unrecuperated reheat furnace)","CIMS; iea_2024_001","")
t(*E,"Reheating furnace efficiency measures, moderate","efficient variant","Control and insulation measures on an existing reheating furnace.",
  "natural gas, by-product gases","9","commercial","oxygen and air-flow control; increased insulation; scheduling and skid design","furnace_efficiency-moderate; refining-furnace_efficiency-moderate","","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Reheating furnace efficiency measures, strong","efficient variant","Combustion air preheated against the flue gas, taken to recuperation or regeneration.",
  "natural gas, by-product gases; recovered heat","9","commercial","recuperative burners; regenerative burners; furnace sealing and insulation package","furnace_efficiency-moderate","Iron and Steel.Hot Rolled (Eff)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column. Hot charging is the other measure the roster files as strong; it is its own row here because it depends on the caster and mill being coupled.")
t(*E,"Hot charging and direct rolling","efficient variant","Charges hot semis straight from casting, avoiding full reheating.",
  "natural gas, electricity","9","commercial","","","Iron and Steel.Reheating.Reheators (NG direct rolling reheat furnace)","CIMS","")
t(*E,"Induction reheating","alternative","Electric induction heaters in place of, or boosting, a fired reheating furnace.",
  "electricity","9","iea_2024_001 row 372","","induction-heater_electricity","Iron and Steel.Reheating.Reheators (NG induction reheat furnace)","iea_2024_001; CIMS","")
E=(S,"rolling")
t(*E,"Hot rolling mill","conventional","Roughing and finishing stands, plus section, bar, rod and tube mills.",
  "electricity","9","commercial","","rolling-mill; rolling-mill_efficiency-moderate","Steel Product.Slabs.Slab Roughing and Slab Finishing; Billets and Blooms mills","CIMS; ukerc_2013_001","")
t(*E,"Hot rolling mill efficiency measures, moderate","efficient variant","Mill-side measures cutting rolling power and reheat losses.",
  "electricity; natural gas (reheat)","9","commercial","coil box; endless rolling; automatic gauge and flatness control; mill lubrication systems","rolling-mill_efficiency-moderate","Iron and Steel.Hot Rolled (Eff)","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Acid pickling line","conventional","Removes scale in hydrochloric or sulphuric acid, with acid regeneration.",
  "steam, electricity, acid","9","commercial","","","Steel Product.Slabs.Pickled Slabs (Sulphuric acid treatment)","CIMS","")
t(*E,"Cold rolling mill","conventional","Tandem or reversing mill reducing strip thickness cold.",
  "electricity","9","commercial","","rolling-mill","Steel Product.Slabs.Cold Rolled.Cold Roll","CIMS","")
t(*E,"Coupled pickling and tandem cold mill","efficient variant","Pickling line and tandem mill joined in one continuous line, avoiding re-coiling and re-heating.",
  "electricity, steam, acid","9","commercial","","","","harmonized","")
E=(S,"annealing-and-coating")
t(*E,"Batch (bell) annealing","conventional","Coils annealed under a hood in a protective atmosphere over long cycles.",
  "natural gas, oil","9","commercial","","rolling-mill_natural-gas","Cold Rolled.ElectroClean.Anneal Temper (Batch annealing NG)","CIMS","")
t(*E,"Hydrogen bell annealing","efficient variant","100% hydrogen atmosphere improves heat transfer and shortens the cycle.",
  "natural gas or electricity (heating); hydrogen (atmosphere)","9","commercial","HICON/H2","","","harmonized","")
t(*E,"Continuous annealing line","alternative","Strip annealed in line at high speed rather than in batches.",
  "natural gas, electricity","9","commercial","","","Cold Rolled.ElectroClean.Anneal Temper (Continuous annealing NG)","CIMS","")
t(*E,"Hot-dip galvanizing line","conventional","Strip heated and passed through a molten zinc bath.",
  "natural gas, electricity; zinc","9","commercial","","","Cold Rolled.Galvanize (Hot dip galvanizing NG)","CIMS","")
t(*E,"Electrolytic coating line","conventional","Electro-galvanizing and tin plating from solution.",
  "electricity","9","commercial","","","Cold Rolled.Galvanize (Electro galvanizing); Tin Plate","CIMS","")
t(*E,"Induction strip heating","alternative","Induction heaters for annealing and galvanizing lines in place of fired furnaces.",
  "electricity","9","iea_2024_001 row 372","","induction-heater_electricity","","iea_2024_001","")

# ---------- cross-sector: space cooling / ventilation split ----------
E=(X,"space-cooling")
t(*E,"Packaged air conditioner or rooftop unit","conventional","Direct-expansion cooling with an air handler.","electricity","9","commercial","","","<sector>.HVAC.Space Cooling","CIMS","")
t(*E,"Chilled-water system","conventional","Central chiller serving air handlers through chilled water.","electricity","9","commercial","","chiller_electricity","","harmonized","")
t(*E,"Reversible heat pump","alternative","One machine providing both building heat and cooling.","electricity","9","iea_2024_001 rows 53, 75","","heat-pump_electricity","","iea_2024_001","")
t(*E,"Free or evaporative cooling","efficient variant","Uses ambient air or evaporation before running the refrigeration cycle.","electricity; water","9","commercial","","","","harmonized","")
t(*E,"Constant-volume fan system","conventional","Supply and exhaust fans running at fixed flow.","electricity","9","commercial","","","light-industrial.service.hvac.space-cooling","CIMS","Building ventilation.")
t(*E,"Variable-speed fans","efficient variant","Fan speed follows the load instead of throttling or running flat out.","electricity","9","commercial","","","","","Building ventilation.")
# ---------- cement ----------
E=(S,"steel-oxygen-supply")
t(*E,"Cryogenic air separation unit","conventional","Distils liquefied air into oxygen, nitrogen and argon at large scale.",
  "electricity","9","commercial","on-site ASUs at steelworks and smelters","","Iron and Steel.Oxygen.Cryogenics (Air compression and distillation)","CIMS","")
t(*E,"Pressure or vacuum swing adsorption","conventional","Adsorbent beds producing oxygen or nitrogen at smaller scale and lower purity.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Membrane separation","conventional","Polymer membranes producing nitrogen or oxygen-enriched air.",
  "electricity","9","commercial","","","","harmonized","")

# ---------- cross-sector: process cooling ----------
S="cement"
E=(S,"clinker-production")
t(*E,"Dry rotary kiln with preheater and precalciner","conventional","Multi-stage cyclone preheater and precalciner ahead of a short rotary kiln, with a grate cooler.",
  "coal, petroleum coke, natural gas, waste-derived and biomass fuels; hydrogen firing (TRL 6)","9","commercial; iea_2024_001 row 330 (hydrogen)","","kiln_dry; kiln","Industrial Minerals.Products.Cement.Portland cement.Clinker.Dry process rotary kiln","etsap_2010_003; iea_2024_001; CIMS","")
t(*E,"Cement kiln efficiency measures, moderate","efficient variant","Combustion and sealing measures on an existing kiln line.",
  "coal, petroleum coke, natural gas, waste fuels","9","commercial","burner and combustion control; reduced false air; kiln shell insulation","kiln_efficiency-moderate","","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Cement kiln with post-combustion capture","prospective","Amine or solid-sorbent capture on the kiln stack, taking the process and combustion CO2 together.",
  "coal, petroleum coke, natural gas, waste fuels; steam and electricity for the capture plant","7","iea_2024_001 row 332 (full capture); row 333 gives 8 for partial capture below 50%","Heidelberg Brevik","kiln_ccs; calciner_ccs","Industrial Minerals.CCS","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. The regeneration steam is large enough that the plant needs a heat source of its own, which is the host-side fact this row carries. Oxy-fuel and direct-separation kilns concentrate the stream instead and are their own rows.")
t(*E,"Cement kiln efficiency measures, strong","efficient variant","The preheater, cooler and gas-path upgrades that together take a kiln line well below its current fuel use.",
  "coal, petroleum coke, natural gas, alternative fuels","9","commercial","extra preheater stages; high-efficiency grate cooler; low-pressure-drop gas path","kiln_efficiency-strong","","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Fluidized-bed kiln","alternative","Sinters clinker in a fluidized bed rather than a rotating kiln, at lower temperature.",
  "coal, natural gas","6-7","assessed (demonstration scale; modelled in CIMS)","","kiln_fluidised-bed","Industrial Minerals.Products.Cement.Portland cement.Clinker.Fluidized bed","CIMS","")
t(*E,"Oxy-fuel kiln","prospective","Fires on oxygen and recycled flue gas, so the kiln gas is CO2-rich.",
  "coal, natural gas, oxygen","7","iea_2024_001 row 338","","kiln_oxyfuel","","iea_2024_001","Oxy-firing concentrates the kiln gas, so the capture plant is the one on cross-sector co2-capture-concentrated and is not repeated here; the air separation unit is the host-side cost.")
t(*E,"Electrified or indirectly heated calciner","prospective","Calcines the meal with electric heat or an indirectly heated vessel, separating process CO2 from flue gas.",
  "electricity; natural gas (kiln burner)","6","iea_2024_001 rows 328, 335","LEILAC","calciner_electricity","","iea_2024_001","")
E=(S,"cement-grinding-and-blending")
t(*E,"Ball mill","conventional","Tumbling mill grinding clinker and additions to cement fineness.","electricity","9","commercial","","grinding-mill","Portland cement.Finish Grinding","CIMS","")
t(*E,"Vertical roller mill or high-pressure grinding rolls","efficient variant","Bed comminution in place of impact grinding, at much lower specific power.",
  "electricity","9","commercial","","grinding-mill_efficiency-strong","","harmonized","")
t(*E,"Blended cement with supplementary cementitious materials","alternative","Replaces clinker with slag, fly ash or ground limestone.",
  "electricity","9","commercial","","alternative-binder","","harmonized","")
t(*E,"Calcined clay cement (LC3)","alternative","Clay calcined at about 800 degC replaces part of the clinker.",
  "natural gas or electricity (clay calciner), electricity","9","iea_2024_001 rows 318, 324","","alternative-binder","","iea_2024_001","")
t(*E,"Alkali-activated binder","alternative","Geopolymer binder from slag or ash with an alkali activator, without clinker.",
  "electricity; chemical activators","9","iea_2024_001 row 317","","alternative-binder","","iea_2024_001","")
t(*E,"Carbonated binder","prospective","Calcium silicate binder cured with CO2 rather than water.",
  "electricity; CO2","8","iea_2024_001 row 319","","alternative-binder","","iea_2024_001","")

# ---------- non-metallic minerals ----------
S="non-metallic-minerals"
E=(S,"lime-calcination")
t(*E,"Rotary lime kiln with preheater","conventional","Rotating kiln calcining limestone, with a preheater and product cooler.",
  "natural gas, coal, petroleum coke, alternative fuels","9","commercial","","kilns","Industrial Minerals.Products.Lime.Kilns (Rotary NG)","CIMS; nrcan_2025_001","")
t(*E,"Lime kiln with post-combustion capture","prospective","Capture on the lime kiln stack. Two thirds of the CO2 is process CO2 off the limestone, which no fuel switch can reach.",
  "natural gas, coal, petroleum coke, biomass; steam and electricity for the capture plant","7","iea_2024_001 row 332 (cement analogue)","","","Industrial Minerals.CCS","iea_2024_001","Dilute stream, held once on cross-sector co2-capture-diffuse. A lime kiln has no waste heat to spare for regeneration, so the capture plant needs its own heat source - that is the host-side fact this row carries.")
t(*E,"Parallel-flow regenerative shaft kiln","efficient variant","Two shafts alternate firing and preheating, cutting fuel use well below a rotary kiln.",
  "natural gas, coal","9","commercial","","kilns","","harmonized","")
t(*E,"Dolomitic lime kiln","conventional","Calcines dolomite to dolomitic lime.","natural gas, coal","9","commercial","","","Industrial Minerals.Products.Lime.Dolomitic","CIMS","")
t(*E,"Oxy-fuel lime kiln","prospective","Fires on oxygen and recycled gas so the kiln gas is CO2-rich.","natural gas, oxygen","7","iea_2024_001 row 338 (cement analogue)","","","","iea_2024_001","Oxy-firing concentrates the stream: capture sits on cross-sector co2-capture-concentrated.")
t(*E,"Electrified or indirectly heated calciner","prospective","Electric or indirect heating separates process CO2 from combustion gas.","electricity","6","iea_2024_001 rows 328, 335","LEILAC","","","iea_2024_001","")
E=(S,"glass-melting")
t(*E,"Air-fuel regenerative glass furnace","conventional","Cross- or end-fired furnace with regenerators preheating combustion air.",
  "natural gas, oil","9","commercial","","furnace_natural-gas","industrial-minerals.product.glass.furnaces","NREL97; CIMS","")
t(*E,"Oxy-fuel glass furnace","efficient variant","Fires on oxygen, cutting flue-gas volume and fuel use.","natural gas, oxygen","9","commercial","","furnace_oxyfuel","","harmonized","")
t(*E,"Electric melter","alternative","All-electric cold-top furnace melting the batch with immersed electrodes.",
  "electricity","9","commercial","","melting-furnace_electricity","","harmonized","")
t(*E,"Hybrid furnace with electric boosting","efficient variant","Fuel firing with electrode boosting, raising pull and cutting fuel per tonne.",
  "natural gas, electricity","9","commercial","","","","harmonized","")
t(*E,"Hydrogen-fired furnace","prospective","Burners fired on hydrogen for high-temperature melting or firing.","hydrogen","8","iea_2024_001 row 379","","furnace_hydrogen","","iea_2024_001","")
E=(S,"glass-forming-and-finishing")
t(*E,"Gas-fired annealing lehr","conventional","Conveyor oven that reheats formed glass and cools it slowly to relieve stress.","natural gas","9","commercial","","","industrial-minerals.product.glass.form-and-finish","CIMS; NREL97","")
t(*E,"Electric annealing lehr","alternative","Resistance-heated lehr doing the same duty on electricity.","electricity","9","commercial","","","","","")
t(*E,"Glass tempering furnace","conventional","Heats flat glass to about 620 degC and quenches it with air jets.","electricity, natural gas; compressed air","9","commercial","","","industrial-minerals.product.glass.form-and-finish","CIMS","")
E=(S,"ceramic-firing")
t(*E,"Tunnel or roller kiln","conventional","Continuous kiln firing brick, tile and refractories.","natural gas","9","commercial","","kiln_natural-gas","industrial-minerals.product.ceramics.kiln","CIMS","")
t(*E,"Electric kiln","alternative","Resistance-heated kiln for ceramics and technical products.","electricity","9","commercial","","kiln_electricity","","harmonized","")
t(*E,"Hydrogen-fired kiln","prospective","Kiln burners fired on hydrogen for high-temperature firing.","hydrogen","8","iea_2024_001 row 379","","","","iea_2024_001","")
E=(S,"drying-and-low-temp-calcining")
t(*E,"Direct-fired rotary dryer or calciner","conventional","Hot gas in direct contact with the mineral, for drying and gypsum calcining.",
  "natural gas","9","commercial","","dryer_natural-gas; calciner","industrial-minerals.product.ceramics.dryer; industrial-minerals.product.gypsum","NREL97","")
t(*E,"Flash or fluid-bed calciner","efficient variant","Short residence time in suspension or a fluidized bed, with better heat transfer.",
  "natural gas","9","commercial","","calciner","","harmonized","")
t(*E,"Kiln waste-heat drying","efficient variant","Uses kiln or cooler exhaust to dry raw materials and additions.","recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Electric or heat-pump dryer","alternative","Electric air heating, or a heat pump where the duty is below about 150 degC.",
  "electricity","7-9","iea_2024_001 rows 436, 438","","dryer_electricity; heat-pump_electricity","","iea_2024_001","")

# ---------- chemicals ----------
S="chemicals"
E=(S,"steam-cracking")
t(*E,"Fired tubular steam cracker","conventional","Hydrocarbon feed cracked in fired tubular coils, then quenched and separated.",
  "ethane, propane, naphtha, gas oil feed; fuel gas, natural gas","9","iea_2024_001 row 355","","steam-cracker","Chemical Products.Chemical Product.Other Petrochemicals.Pyrolysis","iea_2024_001; CIMS","")
t(*E,"Steam cracker with capture on the furnace flue gas","prospective","Capture on the cracking furnace stacks, which are numerous and dilute.",
  "natural gas, by-product gases; steam and electricity for the capture plant","3-4","iea_2024_001 row 227","","steam-cracker_ccs; steam-cracker_steam_ccs","Chemical Products.CCS","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. Oxy-fuel cracking (iea_2024_001 row 226, TRL 5) concentrates it instead.")
t(*E,"Electrified cracker furnace","prospective","Electric heating of the cracking coils in place of burners.",
  "electricity; hydrocarbon feed","5","iea_2024_001 row 357","BASF, SABIC and Linde demonstration at Ludwigshafen (4 t/h, 6 MW, 2024)","steam-cracker_electricity","","iea_2024_001; BASF e-cracker (web)","")
t(*E,"Rotodynamic cracking reactor","prospective","Rotating machine heating the process gas directly with electricity.",
  "electricity; hydrocarbon feed","6","iea_2024_001 row 375 (heater variant)","Coolbrook RotoDynamic Reactor","","","iea_2024_001; Coolbrook 2024 (web)","")
t(*E,"Catalytic cracking of naphtha","alternative","Catalysis lowers the cracking temperature against a thermal cracker.",
  "naphtha; fuel gas","9","iea_2024_001 row 355","","","","iea_2024_001","")
t(*E,"Bio-ethanol dehydration to ethylene","alternative","Dehydrates ethanol to ethylene, bypassing cracking.",
  "ethanol; steam","9","iea_2024_001 row 351","","fermenter_biomass","","iea_2024_001","")
t(*E,"Methanol to olefins","alternative","Converts methanol to ethylene and propylene over a zeolite catalyst.",
  "methanol","9","assessed (commercial plants in China)","","","","harmonized","")
E=(S,"ammonia-and-methanol")
t(*E,"Steam reforming with Haber-Bosch synthesis","conventional","Reformed natural gas feeds ammonia synthesis at pressure.",
  "natural gas (feedstock and fuel), electricity","9","iea_2024_001 row 347","","reactor_ammonia","Chemical Product.Ammonia Methanol.Ammonia Synthesis","iea_2024_001; CIMS","")
t(*E,"Ammonia plant with capture on the process CO2","alternative","The CO2 removal step ahead of synthesis already delivers a pure stream; capture is dehydration and compression, and part of it is already sold for urea.",
  "natural gas; electricity for compression","9","iea_2024_001 row 347 (partial capture); row 346 gives 6 for full capture","Enid, Oklahoma","steam-reformer_ammonia_ccs; capture-unit_hydrogen","Chemical Products.CCS","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. This is the cheapest capture in the sector and should not be averaged with flue-gas capture. Full capture needs a second, dilute plant on the reformer flue gas.")
t(*E,"Electrolytic-hydrogen Haber-Bosch","prospective","Electrolysis replaces the reformer; synthesis is unchanged.",
  "electricity, water, nitrogen","8","iea_2024_001 row 345","","reactor_hydrogen","","iea_2024_001","")
t(*E,"Autothermal reforming with full capture","prospective","Oxygen-blown reforming designed for high capture rates.",
  "natural gas, oxygen","6","iea_2024_001 row 346","","autothermal-reformer","","iea_2024_001","The oxygen-blown route gives one concentrated stream, held on cross-sector co2-capture-concentrated; there is no dilute flue gas to treat separately.")
t(*E,"Low-pressure Haber-Bosch","prospective","Synthesis loop at lower pressure, better matched to variable electrolytic hydrogen.",
  "electricity, hydrogen, nitrogen","5","iea_2024_001 row 348","","","","iea_2024_001","")
t(*E,"Syngas methanol synthesis","conventional","Reformed gas converted to methanol over a copper catalyst.",
  "natural gas, electricity","9","iea_2024_001 row 362","","reactor_methanol","Chemical Product.Ammonia Methanol.Methanol Synthesis","iea_2024_001; CIMS","")
t(*E,"CO2-to-methanol","prospective","Hydrogenates captured CO2 to methanol, directly or through reverse water-gas shift.",
  "hydrogen, CO2, electricity","6-7","iea_2024_001 rows 358, 359","","reactor_methanol","","iea_2024_001","")
t(*E,"Biomass or waste gasification to methanol","prospective","Gasifies biomass or waste to syngas, then synthesizes methanol.",
  "biomass, waste, oxygen","8","iea_2024_001 row 360","","gasifier_biomass","","iea_2024_001","")
E=(S,"electrochemical-products")
t(*E,"Membrane chlor-alkali cell","conventional","Ion-exchange membrane cell producing chlorine, caustic soda and hydrogen.",
  "electricity, salt","9","commercial","","electrolysis-cell_electricity","Chemical Product.Chlor Alkali.Chlorine Electrolysis","CIMS","")
t(*E,"Oxygen-depolarized cathode cell","efficient variant","Feeds oxygen to the cathode, cutting cell voltage and power use, with no hydrogen co-product.",
  "electricity, salt, oxygen","8","assessed (commercial references)","","","","harmonized","")
t(*E,"Sodium chlorate cell","conventional","Electrolytic cell making sodium chlorate for pulp bleaching.",
  "electricity, salt","9","commercial","","electrolysis-cell_electricity","Chemical Product.Sodium Chlorate.Process","CIMS","")
t(*E,"Caustic evaporation with mechanical vapour recompression","efficient variant","Recompresses vapour in place of multiple-effect steam evaporation.",
  "electricity, steam","9","commercial","","evaporator","Chlor Alkali.Caustic Sodium.Chlor Alkali Evaporation","CIMS","")
E=(S,"other-chemicals")
t(*E,"Fired heater and distillation train","conventional","Reboilers and fired heaters driving separation columns.",
  "natural gas, refinery fuel gas, steam","9","commercial","","distillation-column","Other Petrochemicals.Petrochemicals.Intermediate Production","CIMS","")
t(*E,"Heat-integrated or divided-wall column","efficient variant","Column internals and heat integration cutting reboiler duty against a conventional train.",
  "steam, natural gas","9","commercial","","distillation-column","","harmonized","")
t(*E,"Heat-pumped distillation","alternative","Vapour recompression or a closed-cycle heat pump replaces the reboiler steam.",
  "electricity","9","commercial","","vapour-recompressor_electricity","","harmonized","")
t(*E,"Polymerization reactor and extrusion","conventional","Reactor trains and extruders making polymers and compounds.",
  "electricity, steam, cooling","9","commercial","","reactor_natural-gas","Other Petrochemicals.Petrochemicals.All Polymerization","CIMS","")
t(*E,"Plastics pyrolysis recycling","alternative","Pyrolyzes mixed plastic waste to a cracker feedstock.",
  "natural gas, electricity; plastic waste","9","iea_2024_001 row 363","","","","iea_2024_001","")
t(*E,"Chemical depolymerization","prospective","Depolymerizes PET or polystyrene back to monomer.",
  "steam, electricity; solvents","8-9","iea_2024_001 rows 364, 365","","","","iea_2024_001","")

E=(S,"nitric-and-adipic-acid")
t(*E,"Ammonia oxidation nitric acid plant","conventional","Ostwald process: ammonia burned over platinum gauze and the gases absorbed in water; the reaction heat raises export steam.",
  "ammonia, electricity","9","commercial","","","chemicals.product.nitric-acid","CIMS","")
t(*E,"Nitric acid oxidation adipic acid plant","conventional","Cyclohexanol and cyclohexanone oxidized with nitric acid, releasing N2O in the off-gas.",
  "nitric acid, steam, electricity","9","commercial","","","chemicals.product.adipic-acid","CIMS","")
t(*E,"Catalytic N2O abatement","efficient variant","Secondary or tertiary catalyst destroying N2O in nitric and adipic acid plants.",
  "electricity","9","commercial","","","chemicals.product.adipic-acid","CIMS","Abates process emissions rather than energy.")
t(*E,"Thermal N2O destruction","alternative","Adipic acid off-gas burned or thermally decomposed, destroying N2O and raising steam from the heat.",
  "natural gas","9","commercial","","","","","Abates process emissions rather than energy.")

# ---------- biofuels ----------
S="biofuels"
E=(S,"ethanol-production")
t(*E,"Grain dry-mill fermentation and distillation","conventional","Mills, cooks and ferments starch, then distils and dehydrates the beer and dries the stillage.",
  "natural gas (steam and dryers), electricity; corn or wheat","9","iea_2024_001 row 499","","fermenter","Ethanol.Production.Corn","iea_2024_001; CIMS","")
t(*E,"Fermentation CO2 capture and compression","alternative","Fermentation off-gas is about 99% CO2, so capture is dehydration and compression.",
  "electricity for compression","9","iea_2024_001 row 498","ADM Decatur, Illinois","","Ethanol.CCS","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. Biogenic, so it is a removal. The distillation and drying heat is unchanged and still comes from the heat bands.")
t(*E,"Distillation with mechanical vapour recompression","efficient variant","Recompresses overhead vapour to drive the reboiler, cutting steam use.",
  "electricity","9","commercial","","vapour-recompressor_electricity","","harmonized","")
t(*E,"Molecular-sieve dehydration with heat integration","efficient variant","Pressure-swing sieves plus heat integration replace azeotropic distillation.",
  "steam, electricity","9","commercial","","","","harmonized","")
t(*E,"Lignocellulosic enzymatic fermentation","alternative","Pretreats and enzymatically hydrolyzes biomass before fermentation.",
  "biomass residues; steam, electricity","9","iea_2024_001 row 497","","fermenter_biomass","Ethanol.Production.Cellulosic","iea_2024_001; CIMS","")
t(*E,"Syngas fermentation","prospective","Microbes convert gasified biomass or waste gas to ethanol.",
  "biomass, waste or industrial off-gas","8","iea_2024_001 row 500","LanzaTech","fermenter_biomass","","iea_2024_001","")
t(*E,"Distillers-grain drying with heat recovery or heat pumps","efficient variant","Recovers dryer exhaust heat, or uses a heat pump, on the largest gas load in the plant.",
  "natural gas, electricity, recovered heat","7-9","iea_2024_001 rows 390, 436","","dryer_efficiency-moderate","","iea_2024_001","")
E=(S,"biodiesel-production")
t(*E,"Alkali-catalyzed transesterification","conventional","Reacts oils or fats with methanol over a homogeneous catalyst to fatty acid methyl esters.",
  "vegetable oil, tallow or used cooking oil; methanol; steam, electricity","9","iea_2024_001 row 495","","reactor_biomass","Biodiesel.Production","iea_2024_001; CIMS","")
t(*E,"Heterogeneous-catalyst transesterification","alternative","Solid catalyst avoids the washing and neutralization steps and gives cleaner glycerin.",
  "oils and fats; methanol; steam, electricity","8","assessed (commercial plants)","Axens Esterfip-H","","","harmonized","")
t(*E,"Methanol recovery with heat integration","efficient variant","Recovers and recycles methanol with column heat integration or vapour recompression.",
  "steam, electricity","9","commercial","","","","harmonized","")
E=(S,"renewable-diesel-and-saf")
t(*E,"Hydrotreating of oils and fats (HEFA/HVO)","conventional","Hydrodeoxygenates and isomerizes lipids to diesel and jet range fuels.",
  "hydrogen, natural gas, electricity; vegetable oil, tallow, used cooking oil","9","iea_2024_001 row 491","","","","iea_2024_001","")
t(*E,"Alcohol-to-jet","prospective","Dehydrates and oligomerizes ethanol or isobutanol to jet fuel.",
  "ethanol or isobutanol; hydrogen","7-8","iea_2024_001 row 483","","","","iea_2024_001","")
t(*E,"Gasification with Fischer-Tropsch synthesis","prospective","Gasifies biomass or waste and synthesizes liquid hydrocarbons.",
  "biomass, waste, oxygen; hydrogen","7","iea_2024_001 row 486","","gasifier_biomass","","iea_2024_001","")
t(*E,"Pyrolysis oil upgrading","prospective","Fast pyrolysis of biomass then hydroprocessing of the oil.",
  "biomass; hydrogen","7","iea_2024_001 row 492","","","","iea_2024_001","")
t(*E,"Hydrothermal liquefaction","prospective","Converts wet biomass to bio-crude in hot pressurized water, then upgrades it.",
  "wet biomass; hydrogen","5","iea_2024_001 row 487","","","","iea_2024_001","")
t(*E,"Methanol-to-jet","prospective","Converts methanol, including e-methanol, to jet fuel.",
  "methanol; hydrogen","5","iea_2024_001 row 298","","","","iea_2024_001","")

# ---------- petroleum refining ----------
E=(S,"renewable-natural-gas")
t(*E,"Anaerobic digestion with upgrading","alternative","Digests organic feed to biogas and upgrades it to pipeline-quality gas.",
  "organic waste, manure","9","iea_2024_001 row 477","RNG plants on landfills and digesters","anaerobic-digester_biomass","","iea_2024_001","")

# ---------- cross-sector: machine drive ----------
t(*E,"Landfill gas recovery and upgrading","conventional","Collects landfill gas and upgrades it to pipeline specification.",
  "landfill gas; electricity (compression)","9","iea_2024_001 row 477","","","","iea_2024_001","")
t(*E,"Biomass gasification with methanation","prospective","Gasifies solid biomass and methanates the syngas to pipeline-quality gas.",
  "biomass, waste; electricity","5","iea_2024_001 row 482","","gasifier_biomass","<sector>.Methane Fuel","iea_2024_001; CIMS","")
S="petroleum-refining"
E=(S,"crude-distillation")
t(*E,"Atmospheric and vacuum distillation with fired heaters","conventional","Crude heated in fired heaters and fractionated at atmospheric pressure, then under vacuum.",
  "refinery fuel gas, natural gas, steam, electricity","9","commercial","","distillation-column; direct-heater_natural-gas_medium-temp","Refined Petroleum Products.Petroleum Fractions.Distillation.{Atmospheric, Vacuum}","CIMS; rtc_2023_001 p.97","")
t(*E,"Advanced heat integration","efficient variant","Pinch-designed preheat train and better fouling control, cutting furnace duty.",
  "refinery fuel gas, natural gas","9","commercial","","","","harmonized","")
t(*E,"Progressive or divided-wall distillation","efficient variant","Splits the separation across columns or one shell to cut reboiler and furnace duty.",
  "refinery fuel gas, steam","8","assessed (commercial references)","","","","harmonized","")
t(*E,"Electrified crude heater","prospective","Electric resistance or rotodynamic heating replaces the fired crude heater.",
  "electricity","6","iea_2024_001 row 375","Coolbrook RotoDynamic Heater","resistance-heater_electricity_medium-temp","Petroleum Refining.Direct Heat (electric heaters)","iea_2024_001; CIMS","")
E=(S,"conversion-and-treating")
t(*E,"Fluid catalytic cracking","conventional","Cracks gas oil over a circulating catalyst; coke burnt off in the regenerator supplies the heat.",
  "coke on catalyst (captive), refinery fuel gas, steam, electricity","9","commercial","","","Cracked Gas Oil.Hydrocracking.Cracking; Coking","CIMS; nrcan_2025_001","")
t(*E,"FCC regenerator with post-combustion capture","prospective","Capture on the catalytic cracker regenerator flue gas, the largest single stack in a refinery.",
  "coke burnt off the catalyst; steam and electricity for the capture plant","3-4","iea_2024_001 row 227","","","Petroleum Refining.CCS","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. Oxy-fuel regeneration is its own row and gives a concentrated stream.")
t(*E,"Hydroprocessing (hydrocracking and hydrotreating)","conventional","Hydrogen-driven cracking and sulphur or nitrogen removal at pressure.",
  "hydrogen, refinery fuel gas, natural gas, electricity","9","commercial","","","Hydrocracking.{High, Medium, Low}; Hydrotreating.Desulphurization","CIMS","")
t(*E,"Delayed coking","conventional","Thermally cracks residue to lighter products and petroleum coke.",
  "refinery fuel gas, steam","9","commercial","","","Cracked Gas Oil.Coking","CIMS","")
t(*E,"Catalytic reforming","conventional","Upgrades naphtha to high-octane reformate, producing hydrogen.",
  "refinery fuel gas, electricity","9","commercial","","","Refined Petroleum Products.Reforming","CIMS","")
t(*E,"Alkylation and isomerization","conventional","Combines or rearranges light ends into high-octane blendstock.",
  "refinery fuel gas, steam, electricity; acid catalyst","9","commercial","","","Alkylates.Alkylation; Alkylates.Isoparaffins.Isomerization","CIMS","")
t(*E,"Sulphur recovery and acid gas removal","conventional","Amine treating plus a Claus unit and tail-gas treatment.",
  "steam, electricity","9","commercial","","","Hydrotreating.Sulphur Recovery","CIMS","")
t(*E,"Advanced acid gas removal","efficient variant","Selective solvents or membranes cutting regeneration energy.",
  "steam, electricity","9","iea_2024_001 row 225","","","","iea_2024_001","")
t(*E,"Oxy-fuel FCC regeneration","prospective","Burns catalyst coke in oxygen so the regenerator flue gas is CO2-rich.",
  "oxygen, refinery fuel gas","5","iea_2024_001 row 226","","","","iea_2024_001","Oxy-firing the regenerator concentrates the stream: capture sits on cross-sector co2-capture-concentrated.")

# ---------- pulp and paper ----------
E=(S,"refinery-hydrogen")
t(*E,"Steam methane reformer","conventional","Reforms natural gas with steam, then shifts to hydrogen and CO2.",
  "natural gas, refinery fuel gas","9","iea_2024_001 row 285","refinery and ammonia hydrogen plants","steam-reformer_natural-gas","Petroleum Refining.Hydrogen (NG steam reforming); Petroleum Crude.Hydrogen (SMR)","iea_2024_001; CIMS","")
t(*E,"Reformer efficiency measures, moderate","efficient variant","Heat integration and feed conditioning on an existing reformer.",
  "natural gas; recovered heat","9","commercial","pre-reforming; convection-section heat recovery; combustion-air preheat; hydrogen recovery from purge gas","steam-reformer_efficiency-moderate; reactor_efficiency-moderate","","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Steam methane reformer with capture on the shift gas","alternative","Capture on the shifted syngas, where the CO2 is already at high partial pressure. Taking the reformer flue gas as well needs a second, dilute-stream plant.",
  "natural gas; steam and electricity for the capture plant","9","iea_2024_001 row 285 (partial capture); row 284 gives 6 for high capture rates","Quest, Alberta","steam-reformer_ccs; steam-reformer_natural-gas_ccs; capture-unit_hydrogen","Petroleum Crude.Hydrogen (SMR CCS); Hydrogen.Production","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. Partial capture takes only the shift gas and reaches about 60% of the plant total; full capture adds a diffuse-stream plant on the reformer flue gas.")
t(*E,"Autothermal reformer","prospective","Partial oxidation with oxygen in one vessel; suits high capture rates.",
  "natural gas, oxygen","5","iea_2024_001 row 276","Air Products Alberta net-zero hydrogen complex (Edmonton)","autothermal-reformer","","iea_2024_001","Commercial for syngas; the IEA TRL is for the CCUS-enabled hydrogen configuration.")
t(*E,"Coal or petroleum-coke gasification","conventional","Partial oxidation of solid feed to syngas, then shift.",
  "coal, petroleum coke, oxygen","9","iea_2024_001 row 280","","gasifier_coal","Petroleum Refining.Hydrogen (petcoke gasification)","iea_2024_001; CIMS","")
t(*E,"Water electrolysis, low temperature","alternative","Alkaline or PEM stacks splitting water with electricity.",
  "electricity, water","9","iea_2024_001 rows 261, 263","","electrolyser_electricity","","iea_2024_001","")
S="pulp-and-paper"
E=(S,"wood-preparation")
t(*E,"Drum debarker and disc chipper","conventional","A rotating drum strips bark by tumbling the logs; disc chippers cut them to chips for screening.",
  "electricity","9","commercial","","","pulp-and-paper.product.pulp.wood-preparation","CIMS","")
t(*E,"Log and chip thawing with recovered heat","efficient variant","Warm water or low-grade waste heat thaws frozen wood in place of live steam.",
  "recovered heat, steam","9","commercial","","","","","")
E=(S,"chemical-pulping")
t(*E,"Continuous kraft digester","conventional","Continuous vessel cooking chips in white liquor, with heat recovery from the flash steam.",
  "steam, electricity; white liquor","9","commercial","","digester","Raw Pulp.Pulping Chemical","CIMS; NREL97","")
t(*E,"Batch kraft digester with displacement heating","efficient variant","Batch cooking with hot-liquor displacement recovering most of the cooking heat.",
  "steam, electricity","9","commercial","","digester","","harmonized","")
t(*E,"Semi-chemical and sulphite pulping","conventional","Milder chemical cooking for corrugating medium and specialty pulps.",
  "steam, electricity; chemicals","9","commercial","","","Raw Pulp.Pulping Semi Chemical","CIMS","")
t(*E,"Oxygen delignification with ECF bleaching","efficient variant","Removes lignin with oxygen before bleaching, cutting chemical and steam use.",
  "oxygen, steam, electricity; chlorine dioxide","9","commercial","","bleaching-tower","Bleached Pulp.Bleaching.{Bleaching Fully, Bleaching Semi}","CIMS","")
E=(S,"mechanical-pulping")
t(*E,"Thermomechanical pulping refiners","conventional","Steam-pressurized disc refiners fibrillating chips; refiner heat is recovered as steam.",
  "electricity; recovered steam","9","commercial","","refiner_electricity","Raw Pulp.Pulping Mechanical","CIMS","")
t(*E,"Low-energy refining","efficient variant","Advanced segments, RTS conditions or pre-treatment cutting refiner electricity.",
  "electricity","9","commercial","","refiner_efficiency-moderate","","harmonized","")
t(*E,"Chemi-thermomechanical pulping","alternative","Mild chemical pre-treatment before refining, at lower electricity per tonne.",
  "electricity, steam; chemicals","9","commercial","","","","harmonized","")
E=(S,"recycled-pulping")
t(*E,"Recycled-fibre repulping and deinking","conventional","Pulpers, screens and flotation cells recovering fibre from recovered paper.",
  "electricity, steam, chemicals","9","commercial","","flotation-cell_electricity","Raw Pulp.Pulping Recycled","CIMS","")
E=(S,"chemical-recovery")
t(*E,"Recovery boiler","conventional","Burns concentrated black liquor, recovering smelt and raising high-pressure steam.",
  "black liquor","9","commercial","","boiler_black-liquor_recovery; recovery-furnace","Black Liquor Service.Concentrated Black Liquor.Recovery Furnace","CIMS; etsap_2015_001","")
t(*E,"Recovery boiler with post-combustion capture","prospective","Capture on the recovery boiler stack. The CO2 is biogenic, so this is a removal rather than an avoided emission.",
  "black liquor; steam and electricity for the capture plant","5","iea_2024_001 row 422; row 501 gives 6 for post-combustion capture on biomass combustion","","","Pulp and Paper.CCS","iea_2024_001; CIMS","Dilute stream, held once on cross-sector co2-capture-diffuse. The mill steam balance is what binds, and that is the host-side fact this row carries.")
t(*E,"High-solids firing and high-pressure recovery boiler","efficient variant","Higher liquor dry solids and steam conditions, raising power and steam yield.",
  "black liquor","9","commercial","","recovery-furnace","","harmonized","")
t(*E,"Multiple-effect evaporators","conventional","Concentrates weak black liquor in a train of effects on live steam.",
  "steam, electricity","9","commercial","","evaporator","Black Liquor Service.Evaporator","CIMS; NREL97","")
t(*E,"Mechanical vapour recompression evaporation","efficient variant","Recompresses vapour to drive the evaporator, replacing most live steam with electricity.",
  "electricity","9","commercial","","vapour-recompressor_electricity","","harmonized","")
t(*E,"Black liquor gasification","alternative","Gasifies liquor to syngas for fuels, chemicals or a gas turbine, in place of a recovery boiler.",
  "black liquor, oxygen","9","iea_2024_001 row 432","","gasifier_black-liquor","","iea_2024_001","")
t(*E,"Lignin extraction","alternative","Precipitates lignin from the liquor as a fuel or chemical feedstock, debottlenecking the boiler.",
  "CO2, acid, electricity","9","iea_2024_001 row 434","LignoBoost","","","iea_2024_001","")
E=(S,"lime-kiln")
t(*E,"Rotary lime kiln","conventional","Calcines lime mud back to lime for causticizing.",
  "natural gas, oil; tall oil and pitch","9","commercial","","kiln_natural-gas; kiln_oil","Concentrated Black Liquor.Lime Kiln","CIMS; nrcan_2025_001","")
t(*E,"Lime kiln with post-combustion capture","prospective","Capture on the kraft mill lime kiln stack; the calcination CO2 comes back round the causticizing loop, so most of it is biogenic.",
  "natural gas, oil, biomass; steam and electricity for the capture plant","7","iea_2024_001 row 332 (cement analogue)","","","Pulp and Paper.CCS","iea_2024_001","Dilute stream, held once on cross-sector co2-capture-diffuse. Small beside the recovery boiler, but on the same steam balance.")
t(*E,"Lime kiln with product cooler and improved drying","efficient variant","Better cooler, chain section and mud drying, cutting fuel per tonne of lime.",
  "natural gas, oil","9","commercial","","kiln_efficiency-moderate","","harmonized","")
t(*E,"Biomass-gasifier-fired lime kiln","alternative","On-site gasifier supplies producer gas to the kiln burner in place of fossil fuel.",
  "biomass (bark, residues)","8","assessed (operating installations in Scandinavia)","","gasifier_biomass","","harmonized","")
t(*E,"Electrified lime kiln","prospective","Plasma or electric heating of the calcination zone.",
  "electricity","5-6","iea_2024_001 rows 328, 409 (analogues)","","","","iea_2024_001","")
E=(S,"paper-forming")
t(*E,"Fourdrinier or gap former with press section","conventional","Headbox, wire and press section dewatering the sheet mechanically.",
  "electricity (drives, vacuum), steam","9","commercial","","paper-machine","Paper.*.Forming Pressing Finishing","CIMS","")
t(*E,"Shoe (extended-nip) press","efficient variant","Longer nip raises sheet dryness into the dryer section, cutting drying steam.",
  "electricity","9","commercial","","paper-machine_efficiency-strong","","harmonized","")
t(*E,"Advanced mechanical dewatering","prospective","Impulse or pressurized dewatering removing more water before the dryers.",
  "electricity, steam","5","iea_2024_001 row 425","","","","iea_2024_001","")
E=(S,"paper-drying")
t(*E,"Steam-heated cylinder dryer section","conventional","Steam-filled cans drying the web, with condensate return.",
  "steam","9","commercial","","dryer_steam","Paper.*.Drying; Prepared Pulp.Pulp Drying","CIMS; NREL97","")
t(*E,"High-efficiency hood with heat recovery","efficient variant","Closed hood and air system recovering exhaust heat to the machine and mill.",
  "steam, electricity, recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Gas-fired hood, infrared or air dryer","conventional","Direct-fired Yankee hoods, infrared and air dryers on tissue and coating.",
  "natural gas","9","commercial","","dryer_natural-gas","","nrcan_2025_001","")
t(*E,"Electric air heating","alternative","Electric heaters replace the gas burner on hoods and air dryers.",
  "electricity","9","iea_2024_001 row 436","","dryer_electricity","","iea_2024_001","")
t(*E,"Heat-pump drying","prospective","Heat pump upgrades dryer exhaust heat back into the drying air.",
  "electricity, recovered heat","7","iea_2024_001 row 438","","heat-pump_electricity","","iea_2024_001","")

# ---------- mining ----------
E=(S,"effluent-treatment")
t(*E,"Activated sludge aeration","conventional","Surface aerators or coarse-bubble diffusers holding an aeration basin at the oxygen demand of the effluent.",
  "electricity","9","commercial","","","","","")
t(*E,"Fine-bubble diffused aeration","efficient variant","Fine-bubble diffusers with blower control on dissolved oxygen, at a fraction of the power of surface aeration.",
  "electricity","9","commercial","dissolved-oxygen trim; turbo blowers","fan_efficiency-moderate","","harmonized","")
t(*E,"Anaerobic treatment with biogas recovery","alternative","Anaerobic reactors on high-strength streams, cutting aeration load and recovering biogas as fuel.",
  "low-temperature heat (reactor); electricity; biogas recovered","9","commercial","UASB and IC reactors","anaerobic-digester_biomass","","harmonized","Turns part of the treatment load into a fuel, which is why it is a technology choice rather than generic pumping.")
t(*E,"Clarification and sludge dewatering","conventional","Primary clarifiers with belt or screw presses, and dryers where the sludge is burnt.",
  "electricity; low-temperature heat (sludge drying)","9","commercial","","press","","harmonized","")
S="mining"
E=(S,"extraction-and-haulage")
t(*E,"Diesel haul truck fleet","conventional","Diesel trucks, loaders and drills moving ore and waste.",
  "diesel, renewable diesel","9","commercial","","","Mining.Final Product.*.Raw Product.Transportation","CIMS; nrcan_2025_001","")
t(*E,"Battery-electric haulage","prospective","Battery trucks and loaders with fast charging or battery swap.",
  "electricity","8","iea_2024_001 row 135","","","","iea_2024_001","")
t(*E,"Trolley-assist haulage","alternative","Overhead catenary powers trucks on the ramp, cutting diesel on the loaded climb.",
  "electricity, diesel","9","assessed (operating mines)","","","","harmonized","")
t(*E,"In-pit crushing and conveying","efficient variant","Crushes at the face and conveys ore out, replacing truck haulage.",
  "electricity","9","commercial","","conveyor_electricity","Mining.Conveyance","CIMS","")
t(*E,"Hydrogen fuel-cell haulage","prospective","Fuel-cell trucks in demonstration at mine scale.",
  "hydrogen","6","assessed (demonstration fleets)","","","","harmonized","")
t(*E,"Underground battery-electric equipment","alternative","Battery LHDs, trucks and drills, which also cut ventilation demand.",
  "electricity","9","iea_2024_001 row 135","","","","iea_2024_001","")
t(*E,"Shaft hoisting","conventional","Hoists lifting ore from depth in place of ramp haulage.",
  "electricity","9","commercial","","","","harmonized","")
E=(S,"comminution")
t(*E,"SAG and ball mill circuit","conventional","Semi-autogenous grinding followed by ball milling, the standard hard-rock circuit.",
  "electricity","9","commercial","","grinding-mill_electricity","Mining.Final Product.*.Primary Milling","CIMS","")
t(*E,"High-pressure grinding rolls","efficient variant","Bed comminution in place of part of the milling duty, at lower specific energy.",
  "electricity","9","commercial","","grinding-mill_efficiency-strong","","harmonized","")
t(*E,"Stirred fine grinding mills","efficient variant","Vertical or horizontal stirred mills for fine and regrind duties.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Sensor-based ore sorting","alternative","Rejects waste rock before milling, cutting the tonnes ground.",
  "electricity","9","commercial","","","","harmonized","")
E=(S,"separation-and-processing")
t(*E,"Froth flotation","conventional","Reagents and air separate value minerals from gangue in flotation cells.",
  "electricity; reagents","9","commercial","","flotation-cell_electricity","Mining.Final Product.*.Mineral Separation","CIMS","")
t(*E,"Gravity and magnetic separation","conventional","Density and magnetic separation for iron ore and heavy minerals.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Thickening and filtration","conventional","Dewaters concentrate and tailings before drying or disposal.",
  "electricity; flocculants","9","commercial","","","Mining.Final Product.*.Tailing Disposal","CIMS","")
t(*E,"Heap and atmospheric leaching with SX-EW","conventional","Leaches metal into solution, then solvent extraction and electrowinning.",
  "electricity; acid","9","commercial","","leaching-vessel","","harmonized","")
t(*E,"Bioleaching","alternative","Bacteria oxidize sulphides at low temperature in heaps or tanks.",
  "electricity; air","9","iea_2024_001 row 126","","","","iea_2024_001","")
t(*E,"High-pressure acid leaching","alternative","Autoclave leaching of laterite and refractory ores.",
  "steam, electricity; acid","9","iea_2024_001 row 128","","","","iea_2024_001","")
t(*E,"In-situ leaching","alternative","Leaches the orebody in place, with no mining or milling.",
  "electricity; lixiviant","9","iea_2024_001 row 129","","","Potash.Separated Product.Raw Product.Solution Mining","iea_2024_001; CIMS","")
t(*E,"Potash crystallization and flotation","conventional","Separates potash by flotation, or crystallizes it from hot brine.",
  "steam, electricity","9","commercial","","crystalliser","Potash.Separated Product.{Flotation, Crystalization}","CIMS","")
t(*E,"Direct lithium extraction","prospective","Sorbents or membranes recover lithium from brine without evaporation ponds.",
  "electricity, heat","6","iea_2024_001 row 127","","","","iea_2024_001","")
E=(S,"product-drying")
t(*E,"Direct-fired rotary or fluid-bed dryer","conventional","Hot combustion gas drying concentrate, potash or coal.",
  "natural gas, oil","9","commercial","","dryer_natural-gas","mining.product.potash.drying; coal-mining.product.coal-preparation.drying","CIMS","")
t(*E,"Mechanical dewatering before drying","efficient variant","Filters and centrifuges removing water mechanically instead of thermally.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Dryer heat recovery","efficient variant","Recirculates exhaust or preheats feed air from the dryer stack.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Electric or heat-pump drying","alternative","Electric air heating, or a heat pump on low-temperature duties.",
  "electricity","7-9","iea_2024_001 rows 436, 438","","dryer_electricity","","iea_2024_001","")
E=(S,"pelletizing")
t(*E,"Straight-grate induration","conventional","Green pellets dried, fired and cooled on one travelling grate.",
  "heavy oil, natural gas, coke breeze, electricity","9","commercial","","pellet-plant","Mining.Final Product.Metal Open Pit.Size Reduced Iron Product.Agglomeration","CIMS; nrcan_2025_001","")
t(*E,"Grate-kiln induration","conventional","Travelling grate for drying and preheating, then a rotary kiln for firing.",
  "heavy oil, natural gas, coal, electricity","9","commercial","","pellet-plant","","nrcan_2025_001","")
t(*E,"Induration with cooler heat recovery","efficient variant","Returns cooling-zone heat to drying and preheating zones.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Plasma or electric induration","prospective","Plasma torches or electric heating replace the oil or gas burner.",
  "electricity","5","iea_2024_001 row 409","LKAB plasma trials","pellet-plant","","iea_2024_001","")
E=(S,"ventilation-and-air-heating")
t(*E,"Fixed-flow ventilation with direct-fired air heater","conventional","Main fans at constant flow, with a gas or propane mine air heater.",
  "electricity, natural gas, propane","9","commercial","","direct-heater_natural-gas_low-temp","Mining.Ventilation; Mining.HVAC.Space Heating","CIMS; nrcan_2025_001","")
t(*E,"Ventilation on demand","efficient variant","Fan and regulator control following where equipment and people are.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Electric or heat-pump mine air heating","alternative","Electric heaters, or heat pumps on mine water or exhaust air.",
  "electricity","8","assessed (operating installations)","","heat-pump_electricity","","harmonized","")
t(*E,"Exhaust-air heat recovery","efficient variant","Glycol loops or ice-stope storage recovering heat from exhaust air.",
  "recovered heat, electricity","7","assessed","","heat-recovery-unit_waste-heat","","harmonized","")

# ---------- oil and gas ----------
E=(S,"water-and-tailings-management")
t(*E,"Mine dewatering pumping","conventional","Pumping groundwater and surface water out of the pit or workings, and to treatment or discharge.",
  "electricity","9","commercial","","pump","","harmonized","Runs on the site water balance, not on ore throughput.")
t(*E,"Tailings thickening and water reclaim","conventional","Thickeners and reclaim barges returning process water to the mill.",
  "electricity","9","commercial","","separator_thickening-filtration","","harmonized","")
t(*E,"Paste and dry-stack tailings","alternative","Dewaters tailings mechanically before placement, cutting pond volume and reclaim pumping.",
  "electricity","9","commercial","filtered dry stack; paste thickeners","","","","")
t(*E,"Mine water treatment plant","conventional","Lime treatment, settling and polishing before discharge.",
  "electricity; reagents","9","commercial","","","","","")
t(*E,"Reverse osmosis and evaporative concentration","alternative","Membrane or thermal concentration where the discharge permit needs it, at much higher energy per cubic metre.",
  "electricity; low-temperature heat (evaporation)","9","commercial","","separator_membrane-separation","","harmonized","")
S="oil-and-gas"
E=(S,"drilling-and-well-services")
t(*E,"Diesel drilling rig","conventional","Diesel-electric rig powering the drawworks, mud pumps and camp.",
  "diesel","9","commercial","","","Petroleum Crude.Production.Exploration; Natural Gas.Production.Supply.Extraction.Drilling","CIMS","")
t(*E,"Grid-powered or electric rig","alternative","Rig drawing from the grid or a field electrical system.",
  "electricity","9","iea_2024_001 row 218","","","","iea_2024_001","")
t(*E,"Dual-fuel or natural-gas engines","efficient variant","Field or well gas displaces part of the diesel in rig and pump engines.",
  "natural gas, diesel","9","commercial","","","","harmonized","")
t(*E,"Electric fracturing fleet","alternative","Electric pumps on grid or turbine power replace diesel pump spreads.",
  "electricity, natural gas","9","assessed (commercial fleets)","","","","harmonized","")
t(*E,"Battery hybrid rig power","efficient variant","Battery smooths engine load, cutting fuel and run hours.",
  "diesel, electricity","8","assessed","","","","harmonized","")
E=(S,"oil-and-gas-production")
t(*E,"Electric artificial lift","conventional","Beam pumps, progressive-cavity and electric submersible pumps on motors.",
  "electricity","9","iea_2024_001 row 218","","motor","Natural Gas.Production.Supply.Pumping (Electric Motor)","iea_2024_001; CIMS","")
t(*E,"Fired line heater and treater","conventional","Burner heating produced fluids to break emulsions and prevent hydrates.",
  "natural gas","9","commercial","","direct-heater_natural-gas_low-temp","","harmonized","")
t(*E,"Electric or heat-pump treating","alternative","Electric heaters, or heat pumps, on low-temperature treating duties.",
  "electricity","8","assessed","","resistance-heater_electricity_medium-temp","","harmonized","")
E=(S,"venting")
t(*E,"Gas-driven pneumatic controllers and pumps","conventional","Well-site instruments and chemical-injection pumps driven by pipeline gas, which vent methane.",
  "natural gas","9","commercial","","","natural-gas.product.supply.venting.controls; natural-gas.service.pumping (Pneumatic)","CIMS","")
t(*E,"Instrument air or electric actuation","efficient variant","Compressed air or electric actuators and pumps replace gas-driven devices.",
  "electricity","9","iea_2024_001 row 219","","","natural-gas.product.supply.venting.controls (Electric)","iea_2024_001; CIMS","")
t(*E,"Vapour recovery unit","efficient variant","Compresses tank and process vapours back into the sales line.",
  "electricity","9","iea_2024_001 row 220","","","natural-gas.product.supply.venting.point-venting (VRU)","iea_2024_001; CIMS","")
t(*E,"Plunger lift and smart liquids unloading","efficient variant","Unloads liquids without blowing the well down to atmosphere.",
  "natural gas, electricity","9","commercial","","","natural-gas.product.supply.venting.liquid-unloading (Plunger Install)","CIMS","")
t(*E,"Blowdown gas recompression","alternative","Recompresses depressurization gas into the line instead of venting it before maintenance.",
  "electricity, natural gas (compressor drive)","9","commercial","portable recompression units; pressurized pipeline transfer","capture-unit","natural-gas.product.supply.venting.blowdowns (Capture)","CIMS","The harmonized `capture-unit` entry for this service is filed as CO2 capture; it is methane recovery.")
t(*E,"Enclosed combustor","alternative","Enclosed burner destroying tank and process vapours that would otherwise be vented.",
  "natural gas (pilot and purge)","9","commercial","enclosed vapour combustors","","","","Destroys vented gas, so release and destruction compete inside this end use.")
E=(S,"flaring")
t(*E,"Flare with continuous pilot","conventional","Elevated flare burning solution and process gas that is not captured; the incumbent disposal route.",
  "natural gas (the gas flared, plus pilot and purge gas)","9","commercial","","","natural-gas.product.supply.flaring","CIMS","")
t(*E,"Flare gas recovery","efficient variant","Compresses gas that would be flared back into the fuel or sales line.",
  "electricity","9","iea_2024_001 row 220","","","","iea_2024_001","")
t(*E,"High-efficiency flare","alternative","Air-assisted or improved flare tips raising destruction efficiency and cutting unburnt methane.",
  "natural gas (pilot and purge)","9","commercial","air-assisted flare tips","","natural-gas.product.supply.flaring (Efficient)","CIMS","Abates the methane slip from an ordinary flare, not the flaring itself.")
E=(S,"fugitive-emissions")
t(*E,"Leak detection and repair","conventional","Scheduled surveys finding and fixing leaking components.",
  "electricity (survey equipment)","9","commercial","optical gas imaging surveys; Method 21 screening","","Natural Gas.Production.Supply.Fugitive","CIMS","Frequency is what sets the abatement; an annual program and a quarterly one are different technologies in practice.")
t(*E,"Continuous methane monitoring","alternative","Fixed sensors, or aerial and satellite screening, finding leaks between surveys; it also catches vent events, but it substitutes for survey frequency, which is why it sits here.",
  "electricity","8","assessed; commercial deployments on production sites","site sensor networks; aerial and satellite screening","","","","")
t(*E,"Low-emission valves and connectors","alternative","Bellows-sealed and low-leak valve and connector designs cutting the leak rate of new and replaced components.",
  "—","9","commercial","bellows-sealed valves; low-e packing; welded connections","","","","")
t(*E,"Dry gas seals on centrifugal compressors","alternative","Replaces wet seals, whose degassing vents methane continuously, on centrifugal compressors.",
  "electricity (seal gas conditioning)","9","commercial","dry gas seal retrofits; seal gas recovery on wet seals","","","","Wet-seal degassing is one of the largest single fugitive sources at a compressor station.")
E=(S,"in-situ-bitumen")
t(*E,"Once-through field boiler","conventional","Field boiler raising 75-80% quality steam from treated produced water; known in the field as a once-through steam generator (OTSG).",
  "natural gas","9","commercial","","boiler_natural-gas","Petroleum Crude.Steam (Boiler NG)","CIMS","")
t(*E,"Cogeneration supplying steam and power","alternative","Gas turbine with a heat-recovery generator serving the steam demand and exporting power.",
  "natural gas","9","commercial","","combustion-turbine_natural-gas_chp","Petroleum Crude.Steam (Cogen NG)","CIMS","")
t(*E,"Solvent-assisted steam recovery","prospective","Co-injects a solvent with steam, cutting the steam-to-oil ratio.",
  "natural gas, solvent","7","assessed (commercial-scale trials)","","","Production.Bitumen.In-Situ (Hybrid Thermal-Solvent)","CIMS","")
t(*E,"Solvent-only extraction","prospective","Dissolves bitumen with solvent and little or no steam.",
  "solvent, electricity","6","assessed (field pilots)","","","Production.Bitumen.In-Situ (Solvent)","CIMS","")
t(*E,"Direct contact steam generation","prospective","Burns fuel in the water stream, producing steam and CO2 together for injection.",
  "natural gas, oxygen","6","assessed (pilots)","","","","harmonized","")
t(*E,"Electric steam generation","prospective","Electrode or resistance boilers raising injection steam.",
  "electricity","7","assessed; iea_2024_001 row 437","","boiler_electricity","Petroleum Crude.Steam (Electric)","iea_2024_001; CIMS","")
t(*E,"Nuclear steam supply","prospective","Small modular reactor raising steam for injection.",
  "nuclear","7","iea_2024_001 row 455","","reactor_nuclear_smr","Petroleum Crude.Steam (Nuclear)","iea_2024_001; CIMS","")
E=(S,"oil-sands-mining-and-extraction")
t(*E,"Truck-and-shovel mining","conventional","Electric shovels loading large diesel haul trucks.",
  "diesel, electricity","9","commercial","","","Production.Bitumen.Mining","CIMS","")
t(*E,"Hydrotransport and warm-water extraction","conventional","Slurries ore in warm water, separating bitumen froth in gravity vessels.",
  "natural gas (water heating), electricity","9","commercial","","","Production.Bitumen.Mining","CIMS; Alberta Energy Heritage (web)","")
t(*E,"Paraffinic froth treatment","alternative","Paraffinic solvent rejects asphaltenes, giving a cleaner bitumen product.",
  "solvent, natural gas, electricity","9","commercial","","","","harmonized","")
t(*E,"Non-aqueous extraction","prospective","Solvent-based extraction without hot water, cutting heat and tailings.",
  "solvent, electricity","5-6","assessed (pilot scale)","","","","harmonized","")
t(*E,"Electric or autonomous haul fleet","prospective","Battery or trolley trucks, often with autonomous haulage control.",
  "electricity, diesel","7-8","iea_2024_001 row 135","","","","iea_2024_001","")
t(*E,"Thickened or dry-stack tailings","efficient variant","Dewaters tailings mechanically, cutting pond volume and recycled-water heating.",
  "electricity; flocculants","8","assessed","","","","harmonized","")
E=(S,"bitumen-upgrading")
t(*E,"Delayed coking","conventional","Thermally cracks bitumen to lighter products and petroleum coke.",
  "refinery fuel gas, steam","9","commercial","","","Production.Bitumen.Upgrading","CIMS","")
t(*E,"Fluid or flexi-coking","conventional","Fluidized thermal cracking, with the coke partly gasified for fuel gas.",
  "petroleum coke (captive), steam","9","commercial","","","Production.Bitumen.Upgrading","CIMS","")
t(*E,"Ebullated-bed hydrocracking","conventional","Hydrogen addition in a moving catalyst bed for high conversion of residue.",
  "hydrogen, natural gas, electricity","9","commercial","","","Production.Bitumen.Upgrading","CIMS","")
t(*E,"Fixed-bed hydrotreating","conventional","Hydrogen treating to remove sulphur and stabilize synthetic crude.",
  "hydrogen, natural gas","9","commercial","","","","harmonized","")
t(*E,"Partial upgrading","prospective","Field-scale treatment that meets pipeline specification without full upgrading.",
  "natural gas, electricity","6-7","assessed (demonstration plants)","","","","harmonized","")
E=(S,"gas-processing")
t(*E,"Amine sweetening","conventional","Amine absorption removing H2S and CO2, with a steam-heated regenerator.",
  "steam or fired heat, electricity","9","commercial","","capture-unit","Natural Gas.Production.Supply.Processing","CIMS","")
t(*E,"Acid gas removal with CO2 compression and injection","alternative","The amine unit already separates CO2 along with the H2S, so capture is compression, dehydration and injection instead of venting.",
  "electricity for compression; the amine unit's own reboiler heat","9","commercial; Alberta acid gas injection schemes","acid gas injection, Alberta","capture-unit_natural-gas_ccs","Natural Gas.Production.Supply.CCS; Natural Gas.Production.Supply.Formation CO2","CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. Reservoir CO2 separated here is the cheapest capture in the database and should not be averaged with flue-gas capture.")
t(*E,"Advanced acid gas removal","efficient variant","Selective solvents or membranes cutting regeneration energy and losses.",
  "steam, electricity","9","iea_2024_001 row 225","","","","iea_2024_001","")
t(*E,"Glycol dehydration","conventional","TEG contactor with a fired reboiler regenerating the glycol.",
  "natural gas","9","commercial","","","","harmonized","")
t(*E,"Molecular-sieve dehydration","alternative","Adsorbent beds regenerated with hot gas, to cryogenic-plant dryness.",
  "natural gas, electricity","9","commercial","","","","harmonized","")
t(*E,"Turboexpander NGL recovery","conventional","Expansion refrigeration recovering ethane and heavier liquids.",
  "electricity, natural gas","9","commercial","","","Natural Gas.Production.Supply.Processing.Compression","CIMS","")
t(*E,"Claus sulphur recovery","conventional","Converts H2S to elemental sulphur, with tail-gas treating.",
  "natural gas, electricity","9","commercial","","","","harmonized","")
t(*E,"Electric-drive compression","alternative","Motor-driven compressors in place of gas turbines or engines.",
  "electricity","9","iea_2024_001 row 218","","motor","Natural Gas.Production.Supply.Processing.Compression","iea_2024_001; CIMS","")
E=(S,"lng-liquefaction")
t(*E,"Gas-turbine-driven refrigeration","conventional","Aero-derivative or heavy-duty turbines driving the refrigerant compressors.",
  "natural gas","9","commercial","","combustion-turbine_natural-gas","Natural Gas.Production.Supply.LNG Compression (Natural Gas)","CIMS","")
t(*E,"Electric-motor-driven refrigeration","alternative","Large motors drive the compressors, moving the emissions to the grid.",
  "electricity","9","iea_2024_001 row 218","Woodfibre LNG; Cedar LNG","motor","Natural Gas.Production.Supply.LNG Compression (Electric)","iea_2024_001; CIMS","")
t(*E,"Small-scale or modular liquefaction","alternative","Modular trains for peak shaving and remote supply.",
  "natural gas, electricity","9","iea_2024_001 row 213","","","","iea_2024_001","")
t(*E,"Boil-off gas recovery","efficient variant","Recompresses boil-off gas back into the process instead of flaring or fuelling.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Turbine waste-heat recovery","efficient variant","Recovers turbine exhaust heat for process and utility duties.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
E=(S,"gas-pipelines")
t(*E,"Gas-turbine compressor station","conventional","Turbine-driven compressors burning pipeline gas.",
  "natural gas","9","iea_2024_001 row 214","","combustion-turbine_natural-gas","Natural Gas.Production.Transmission.Compression","iea_2024_001; CIMS","")
t(*E,"Reciprocating gas-engine compressor","conventional","Engine-driven reciprocating compressors, common on gathering systems.",
  "natural gas","9","commercial","","reciprocating-engine_natural-gas","Natural Gas.Production.Supply.Direct Drive Small","CIMS","")
t(*E,"Electric-drive compressor","alternative","Motor-driven compressors on grid power.",
  "electricity","9","iea_2024_001 row 218","","motor","","iea_2024_001","")
t(*E,"Compressor-station waste-heat power","efficient variant","Organic Rankine cycle on turbine exhaust generating station power.",
  "recovered heat","9","iea_2024_001 row 516","","","","iea_2024_001","")
t(*E,"Turboexpander at pressure let-down","efficient variant","Recovers pressure energy as power instead of throttling, with line heating.",
  "natural gas (line heaters), electricity","8","assessed","","","Natural Gas.Production.Distribution","harmonized","")
E=(S,"oil-pipelines")
t(*E,"Electric pump station","conventional","Motor-driven mainline pumps moving crude and products.",
  "electricity","9","commercial","","motor","","CER 2022 pipeline market snapshot (web)","")
t(*E,"Variable-speed pump drives","efficient variant","Speed control replaces throttling and station cycling.",
  "electricity","9","commercial","","motor_efficiency-moderate","","harmonized","")
t(*E,"Drag-reducing agents","efficient variant","Polymer injection cuts friction, raising throughput per unit of pumping power.",
  "electricity; chemical","9","commercial","","","","harmonized","")
t(*E,"Gas-engine driven pumps","conventional","Engine-driven pumps on lines without grid supply.",
  "natural gas, diesel","9","commercial","","reciprocating-engine_natural-gas","","harmonized","")

# ---------- food and beverage ----------
E=(S,"upgrader-hydrogen")
t(*E,"Steam methane reformer","conventional","Reforms natural gas with steam, then shifts to hydrogen and CO2.",
  "natural gas, refinery fuel gas","9","iea_2024_001 row 285","refinery and ammonia hydrogen plants","steam-reformer_natural-gas","Petroleum Refining.Hydrogen (NG steam reforming); Petroleum Crude.Hydrogen (SMR)","iea_2024_001; CIMS","")
t(*E,"Steam methane reformer with capture on the shift gas","alternative","Capture on the shifted syngas, where the CO2 is already at high partial pressure. Taking the reformer flue gas as well needs a second, dilute-stream plant.",
  "natural gas; steam and electricity for the capture plant","9","iea_2024_001 row 285 (partial capture); row 284 gives 6 for high capture rates","Quest, Alberta","steam-reformer_ccs; steam-reformer_natural-gas_ccs; capture-unit_hydrogen","Petroleum Crude.Hydrogen (SMR CCS); Hydrogen.Production","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. Partial capture takes only the shift gas and reaches about 60% of the plant total; full capture adds a diffuse-stream plant on the reformer flue gas.")
t(*E,"Coal or petroleum-coke gasification","conventional","Partial oxidation of solid feed to syngas, then shift.",
  "coal, petroleum coke, oxygen","9","iea_2024_001 row 280","","gasifier_coal","Petroleum Refining.Hydrogen (petcoke gasification)","iea_2024_001; CIMS","")
t(*E,"Water electrolysis, low temperature","alternative","Alkaline or PEM stacks splitting water with electricity.",
  "electricity, water","9","iea_2024_001 rows 261, 263","","electrolyser_electricity","","iea_2024_001","")
E=(S,"produced-water-handling")
t(*E,"Disposal well injection","conventional","Pumps produced and flowback water to a disposal formation.",
  "electricity (injection pumps)","9","commercial","","pump","","harmonized","")
t(*E,"De-oiling and warm lime softening","conventional","Skim tanks, induced gas flotation and warm lime softening conditioning produced water for steam generation.",
  "electricity; low-temperature heat","9","commercial","SAGD water plants","","","","The water plant is part of what sets the steam-to-oil ratio.")
t(*E,"Evaporators and crystallizers","alternative","Mechanical vapour recompression evaporators producing distilled makeup and a small residual for disposal.",
  "electricity (vapour recompression); natural gas","9","commercial","","vapour-recompressor_mechanical","","harmonized","")
t(*E,"Produced water recycling for makeup","alternative","Treats and reuses produced and flowback water as fracturing or steam makeup instead of disposing of it.",
  "electricity","9","commercial","","","","","Cuts both disposal energy and freshwater draw.")
S="food-and-beverage"
E=(S,"thermal-processing")
t(*E,"Steam-heated kettles, retorts and plate heat exchangers","conventional","Jacketed vessels, retorts and plate pasteurizers on site steam and hot water.",
  "steam, hot water","9","commercial","","heat-exchanger; retort","Light Industrial.Manufacturing.Food Tobacco and Beverage","CIMS; NREL97","")
t(*E,"Regenerative heat recovery on pasteurizers","efficient variant","Product-to-product regeneration recovering most of the heating duty.",
  "steam, electricity","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Clean-in-place efficiency measures, moderate","efficient variant","Recovery and control on cleaning and clean-in-place systems, which carry much of a plant's hot-water load.",
  "steam, hot water, electricity","9","commercial","final-rinse reuse; heat recovery from CIP returns; cycle time and temperature optimization","cleaning-system_efficiency-moderate; cleaning-system_efficiency-strong","","ukerc_2013_001; harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column. The roster carries a moderate and a strong cleaning bucket; both sit here until a source separates them.")
t(*E,"Heat pump for hot water and clean-in-place","alternative","Heat pump supplies wash, CIP and low-temperature process water.",
  "electricity","9","iea_2024_001 row 390","","heat-pump_electricity","","iea_2024_001","")
t(*E,"Ohmic, microwave or infrared heating","alternative","Heats the product directly, without a steam loop.",
  "electricity","9","iea_2024_001 rows 382, 384","","microwave-heater_electricity","","iea_2024_001","")
t(*E,"Aseptic and UHT processing","alternative","Short high-temperature treatment with regeneration, in place of in-container sterilizing.",
  "steam, electricity","9","commercial","","","","harmonized","")
t(*E,"High-pressure processing","alternative","Non-thermal pasteurization by pressure rather than heat.",
  "electricity","9","commercial","","","","harmonized","")
E=(S,"baking-frying-and-roasting")
t(*E,"Direct-fired tunnel or deck oven","conventional","Burners firing into the baking chamber.",
  "natural gas, propane","9","commercial","","oven_natural-gas","Light Industrial.Manufacturing.Food Tobacco and Beverage","CIMS; NREL97","")
t(*E,"Indirect-fired oven","conventional","Radiant tubes or heat exchangers keep combustion products out of the chamber.",
  "natural gas","9","commercial","","oven_natural-gas_indirect","","harmonized","")
t(*E,"Electric oven, fryer or roaster","alternative","Resistance elements in place of burners.",
  "electricity","9","commercial","","oven_electricity","","harmonized","")
t(*E,"Microwave or radio-frequency assisted baking","alternative","Volumetric heating shortens the bake and cuts oven length.",
  "electricity","9","iea_2024_001 rows 382, 384","","radio-frequency-heater_electricity_low-temp","","iea_2024_001","")
t(*E,"Oven exhaust heat recovery","efficient variant","Recovers oven and fryer exhaust heat to make-up air or process water.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
E=(S,"drying")
t(*E,"Direct-fired spray, drum or belt dryer","conventional","Hot gas drying liquids, solids and grain.",
  "natural gas","9","commercial","","dryer_natural-gas","Light Industrial.Manufacturing.Food Tobacco and Beverage","CIMS; NREL97","")
t(*E,"Mechanical vapour recompression evaporation","alternative","Concentrates the product before drying, with electricity instead of steam.",
  "electricity","9","commercial","","vapour-recompressor_electricity","","harmonized","")
t(*E,"Dryer exhaust heat recovery and recirculation","efficient variant","Recovers exhaust heat and recycles part of the drying air.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
t(*E,"Heat-pump dryer","alternative","Closed-loop heat pump drying at low temperature with dehumidification.",
  "electricity","8","iea_2024_001 rows 390, 438","","heat-pump_electricity","","iea_2024_001","")
t(*E,"Electric air heating","alternative","Electric heaters replace the dryer burner.",
  "electricity","9","iea_2024_001 row 436","","dryer_electricity","","iea_2024_001","")
t(*E,"Microwave or radio-frequency drying","alternative","Volumetric drying for finishing and low-moisture duties.",
  "electricity","9","iea_2024_001 rows 382, 384","","microwave-heater_electricity","","iea_2024_001","")

# ---------- non-ferrous metals ----------
E=(S,"refrigeration")
t(*E,"Vapour-compression chiller or refrigeration plant","conventional","Electric compressor cycle delivering chilled water, brine or refrigeration.",
  "electricity; ammonia, CO2 or HFC refrigerant","9","commercial","","chiller_electricity","","harmonized","")
t(*E,"High-efficiency chiller","efficient variant","Variable-speed or magnetic-bearing centrifugal machine, often on natural refrigerants.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Absorption chiller","alternative","Heat-driven cycle using waste heat or steam instead of electricity.",
  "recovered heat, steam, natural gas","9","iea_2024_001 row 85","","","","iea_2024_001","")
t(*E,"Free or evaporative cooling","conventional","Cooling towers and ambient air, without a refrigeration cycle.",
  "electricity (fans, pumps); water","9","commercial","","","","harmonized","")

# ---------- cross-sector: facility services ----------
S="non-ferrous-metals"
E=(S,"alumina-refining")
t(*E,"Bayer digestion on fossil steam","conventional","Caustic digestion of bauxite under pressure, with steam from gas or oil boilers.",
  "natural gas, oil (steam), electricity","9","commercial","","digester_bayer","Metal Smelting.Primary Metals.Aluminum.Primary Aluminum.Alumina","CIMS; nrcan_2025_001","")
t(*E,"Gas-suspension calciner","efficient variant","Suspension calcination of hydrate, at lower fuel use than a rotary calciner.",
  "natural gas","9","commercial","","calciner_natural-gas","","harmonized","")
t(*E,"Electrified Bayer heat","prospective","Electric boilers or heaters supply digestion heat.",
  "electricity","7","iea_2024_001 row 307","","boiler_electricity","","iea_2024_001","")
t(*E,"Biomass-fired Bayer heat","prospective","Biomass replaces a high share of the fossil fuel raising digestion steam.",
  "biomass","7","iea_2024_001 row 309","","boiler_biomass","","iea_2024_001","")
t(*E,"Solar thermal in the Bayer process","prospective","Concentrating solar raises part of the digestion heat.",
  "solar","6","iea_2024_001 row 312","","solar-collector_solar_medium-temp","","iea_2024_001","")
t(*E,"Hydrogen in the Bayer process","prospective","Hydrogen firing for digestion and calcination heat.",
  "hydrogen","5","iea_2024_001 row 311","","","","iea_2024_001","")
E=(S,"aluminum-smelting")
t(*E,"Prebaked anode cell","conventional","Centre-worked prebake Hall-Heroult cells with point feeding.",
  "electricity; carbon anodes","9","commercial","","electrolysis-cell_electricity_prebake","Primary Aluminum.Electrolysis","etsap_2012_001; CIMS","")
t(*E,"Soderberg cell","conventional","Self-baking anode cells, the older Canadian stock.",
  "electricity; anode paste","9","commercial","","electrolysis-cell_electricity_soderberg","Metal Smelting.Soderberg Anode","CIMS","")
t(*E,"Inert anode cell","prospective","Non-consumable anodes give oxygen instead of CO2 at the anode.",
  "electricity","7","iea_2024_001 row 303","ELYSIS (Quebec)","electrolysis-cell_electricity_inert-anode","","iea_2024_001","")
t(*E,"Multipolar or chloride cell","prospective","Cell geometry or chloride chemistry cutting cell voltage and footprint.",
  "electricity","5","iea_2024_001 rows 302, 304","","","","iea_2024_001","")
t(*E,"Smelter power modulation","efficient variant","Controlled amperage swings let the potline follow the grid without losing production.",
  "electricity","9","iea_2024_001 rows 306, 301","","","","iea_2024_001","")
E=(S,"anode-production")
t(*E,"Prebake anode baking furnace","conventional","Open or closed ring furnace baking green anodes.",
  "natural gas, oil","9","commercial","","oven_anode-baking","Metal Smelting.Pre-bake Anode","CIMS; nrcan_2025_001","")
t(*E,"Soderberg paste plant","conventional","Mixes and pastes anode material for self-baking cells.",
  "natural gas, electricity; pitch, coke","9","commercial","","","Metal Smelting.Soderberg Anode","CIMS","")
t(*E,"Electrified or hydrogen-fired anode baking","prospective","Electric or hydrogen heat replaces the fossil burner on the baking furnace.",
  "electricity, hydrogen","6-8","iea_2024_001 rows 308, 310","","","","iea_2024_001","")
t(*E,"Bio-pitch and bio-coke anodes","prospective","Biogenic binder and filler replacing fossil pitch and petroleum coke.",
  "biomass-derived pitch and coke","6","assessed (pilot production)","","","","harmonized","")
E=(S,"pyrometallurgy")
t(*E,"Flash smelting furnace","conventional","Oxygen-enriched flash smelting of sulphide concentrate, with a waste-heat boiler.",
  "oxygen, natural gas, coal; sulphide oxidation heat","9","commercial","","smelting-vessel","Primary Metals.*.Metallurgy.Pyro Metallurgy.Smelting Process","CIMS; NREL97","")
t(*E,"Smelting efficiency measures, moderate","efficient variant","Incremental measures on an existing smelter off-gas and feed system.",
  "natural gas, oxygen, electricity","9","commercial","feed drying with off-gas heat; improved hooding; oxygen control","","Metal Smelting.Primary Metals (Eff)","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Top-submerged-lance bath smelting","conventional","Bath smelting with a submerged lance, for concentrates and secondary feed.",
  "natural gas, oxygen, coal","9","commercial","","smelting-vessel","","harmonized","")
t(*E,"Peirce-Smith converting","conventional","Batch converting of matte to blister metal.",
  "oxygen; matte oxidation heat","9","commercial","","converter","Pyro Metallurgy.Smelting Process.Conventional Smelting.Convert","CIMS","")
t(*E,"Continuous converting","efficient variant","Continuous flash or bath converting, cutting fugitive losses and fuel per tonne.",
  "oxygen, natural gas","9","commercial","","converter","Pyro Metallurgy.Smelting Process.Continuous Smelting","CIMS","")
t(*E,"Smelting efficiency measures, strong","efficient variant","Higher oxygen enrichment with a waste-heat boiler on the off-gas.",
  "natural gas, oxygen; recovered heat","9","commercial","higher oxygen enrichment; waste-heat boiler on the off-gas; off-gas heat to feed drying","","Metal Smelting.Primary Metals (Eff)","harmonized","Bucket, not a single device: it groups the incremental measures on this technology that the roster files under this variant (design doc s6.2, about 15% energy saving separating moderate from strong). The measures themselves are in the examples column.")
t(*E,"Hydrogen-fired ancillary heat","prospective","Hydrogen burners on holding, roasting and refining furnaces.",
  "hydrogen","6","iea_2024_001 row 310","","furnace_hydrogen","","iea_2024_001","")
E=(S,"electric-smelting")
t(*E,"Submerged-arc furnace","conventional","Electrodes buried in the charge, smelting silicon, ferroalloys or titanium slag.",
  "electricity; coal, coke, charcoal, wood chips","9","commercial","","smelting-vessel_electricity","Primary Metals.Titanium.Metallurgy.Pyro Metallurgy","NREL97; CIMS","")
t(*E,"Open-arc DC furnace","alternative","Direct-current open arc, taking finer feed and a wider reductant range.",
  "electricity; carbon reductant","9","commercial","","smelting-vessel_electricity","","harmonized","")
t(*E,"Pre-reduction of feed","efficient variant","Reduces the ore before smelting, cutting furnace electricity per tonne.",
  "natural gas or hydrogen; electricity","6-7","assessed (demonstration plant)","BlueSmelting (Rio Tinto Fer et Titane)","","","Rio Tinto (web)","")
t(*E,"Biocarbon reductant","alternative","Charcoal or biocoke replaces fossil carbon in the charge.",
  "biocarbon; electricity","8","assessed; iea_2024_001 row 400","","","","iea_2024_001","")
t(*E,"Off-gas energy recovery","efficient variant","Recovers CO-rich furnace gas as fuel or power.",
  "recovered gas","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
E=(S,"hydrometallurgy")
t(*E,"Atmospheric leaching with solvent extraction and electrowinning","conventional","Leach, solvent extraction and electrowinning producing cathode metal.",
  "electricity; acid, steam","9","commercial","","leaching-vessel; electrowinning-cell","Primary Metals.*.Metallurgy.Hydro Metallurgy","CIMS; NREL97","")
t(*E,"High-pressure acid leaching","alternative","Autoclave leaching of laterites and refractory concentrates.",
  "steam, electricity; acid","9","iea_2024_001 row 128","","","","iea_2024_001","")
t(*E,"Bioleaching","alternative","Bacterial oxidation of sulphides at low temperature.",
  "electricity; air","9","iea_2024_001 row 126","","","","iea_2024_001","")
t(*E,"Electrowinning with advanced anodes and energy control","efficient variant","Lower-overpotential anodes and current control cutting cell power.",
  "electricity","8","assessed","","electrowinning-cell","","harmonized","")
t(*E,"Direct lithium extraction","prospective","Sorbent or membrane recovery of lithium from brine.",
  "electricity, heat","6","iea_2024_001 row 127","","","","iea_2024_001","")
E=(S,"melting-casting-and-fabrication")
t(*E,"Reverberatory or rotary melting furnace","conventional","Gas-fired melting of ingot, scrap and returns before casting.",
  "natural gas, oil","9","commercial","","melting-furnace_secondary","Primary Metals.*.Melt Cast; Primary Aluminum.Recycle","CIMS; NREL97","")
t(*E,"Regenerative or oxy-fuel melting","efficient variant","Air preheat or oxygen firing cutting melting fuel per tonne.",
  "natural gas, oxygen","9","commercial","","furnace_preheat","","harmonized","")
t(*E,"Twin-chamber furnace with decoating","efficient variant","Burns off coatings and melts in separate chambers, raising recovery and cutting fuel.",
  "natural gas","9","iea_2024_001 row 305","","","","iea_2024_001","")
t(*E,"Induction melting and holding","alternative","Electric induction melting and holding in place of fired furnaces.",
  "electricity","9","iea_2024_001 row 372","","induction-heater_electricity","","iea_2024_001","")
t(*E,"Homogenizing and reheat furnaces","conventional","Heat treatment of billets and slabs before extrusion or rolling.",
  "natural gas, electricity","9","commercial","","furnace_natural-gas","","harmonized","")
t(*E,"Continuous casting and rolling","efficient variant","Casts and rolls in one line, avoiding a reheating step.",
  "electricity, natural gas","9","commercial","","caster","","harmonized","")

# ---------- other industry ----------
E=(S,"smelter-oxygen-supply")
t(*E,"Cryogenic air separation unit","conventional","Distils liquefied air into oxygen, nitrogen and argon at large scale.",
  "electricity","9","commercial","on-site ASUs at steelworks and smelters","","Iron and Steel.Oxygen.Cryogenics (Air compression and distillation)","CIMS","")
t(*E,"Pressure or vacuum swing adsorption","conventional","Adsorbent beds producing oxygen or nitrogen at smaller scale and lower purity.",
  "electricity","9","commercial","","","","harmonized","")
t(*E,"Membrane separation","conventional","Polymer membranes producing nitrogen or oxygen-enriched air.",
  "electricity","9","commercial","","","","harmonized","")

# ---------- cross-sector: process cooling ----------
S="other-industry"
E=(S,"metal-melting-and-heat-treatment")
t(*E,"Cupola or gas-fired melting furnace","conventional","Coke cupola or gas-fired furnace melting iron and non-ferrous metal in foundries.",
  "coke, natural gas","9","commercial","","melting-furnace","Light Industrial.Heat.Direct","CIMS; NREL97","")
t(*E,"Induction melting furnace","alternative","Coreless or channel induction melting, common in modern foundries.",
  "electricity","9","iea_2024_001 row 372","","induction-heater_electricity","","iea_2024_001","")
t(*E,"Electric arc melting furnace","alternative","Arc melting for steel and iron castings.",
  "electricity","9","commercial","","electric-arc-furnace","","harmonized","")
t(*E,"Fuel-fired heat-treatment furnace","conventional","Batch and continuous furnaces for annealing, normalizing and forging heat.",
  "natural gas, propane","9","commercial","","furnace_natural-gas","Light Industrial.Heat.Direct","CIMS; NREL97","")
t(*E,"Electric or induction heat treatment","alternative","Resistance or induction heating for hardening, forging and annealing.",
  "electricity","9","iea_2024_001 row 372","","induction-heater_electricity","","iea_2024_001","")
t(*E,"Regenerative or recuperative burners","efficient variant","Air preheat on melting and heat-treatment furnaces.",
  "natural gas","9","commercial","","furnace_preheat","","harmonized","")
E=(S,"drying-curing-and-forming")
t(*E,"Direct-fired dryer or curing oven","conventional","Gas-fired ovens for paint curing, textile finishing and product drying.",
  "natural gas","9","commercial","","dryer_natural-gas; oven_natural-gas","Light Industrial.Heat.Direct","CIMS; NREL97","")
t(*E,"Infrared or ultraviolet curing","alternative","Radiant or photochemical curing in place of hot-air ovens.",
  "electricity","9","iea_2024_001 rows 383, 385","","ultraviolet-curer_electricity","","iea_2024_001","")
t(*E,"Electric air heating","alternative","Electric heaters replace the oven or dryer burner.",
  "electricity","9","iea_2024_001 row 436","","dryer_electricity","Light Industrial.Heat.Direct (Eff electric)","iea_2024_001; CIMS","")
t(*E,"Heat-pump drying","prospective","Closed-loop heat pump drying and dehumidification below about 150 degC.",
  "electricity","7-8","iea_2024_001 rows 390, 438","","heat-pump_electricity","","iea_2024_001","")
t(*E,"All-electric injection moulding and extrusion","efficient variant","Servo-electric machines replacing hydraulic drives, with electric barrel heating.",
  "electricity","9","commercial","","","Manufacturing.Rubber and Plastics","CIMS","")
t(*E,"Oven and dryer heat recovery","efficient variant","Recovers exhaust heat to make-up air or process water.",
  "recovered heat","9","commercial","","heat-recovery-unit_waste-heat","","harmonized","")
E=(S,"wood-drying-and-pressing")
t(*E,"Steam or thermal-oil lumber kiln","conventional","Batch kilns heated by hog-fuel boilers through steam or thermal oil.",
  "biomass (hog fuel), natural gas; electricity (fans)","9","commercial","","dryer_steam","Light Industrial.Manufacturing.Wood Products","CIMS; NREL97","")
t(*E,"Continuous kiln with heat recovery","efficient variant","Continuous drying with zone heat recovery, at lower energy per cubic metre.",
  "biomass, natural gas, recovered heat","9","commercial","","dryer_efficiency-moderate","","harmonized","")
t(*E,"Direct-fired veneer and strand dryer","conventional","Hot gas from a burner or boiler drying veneer, strands and particles.",
  "biomass, natural gas","9","commercial","","dryer_natural-gas","","NREL97","")
t(*E,"Hot press with thermal-oil heater","conventional","Heated platens curing resin in plywood, OSB and MDF panels.",
  "biomass, natural gas (thermal oil)","9","commercial","","press_thermal-oil","","harmonized","")
t(*E,"Dehumidification or heat-pump kiln","alternative","Heat-pump kiln recovering latent heat from the drying air.",
  "electricity","8","iea_2024_001 rows 390, 438","","heat-pump_electricity","","iea_2024_001","")
t(*E,"Radio-frequency or vacuum drying","prospective","Volumetric drying for thick stock and specialty products.",
  "electricity","7","iea_2024_001 row 384","","radio-frequency-heater_electricity_low-temp","","iea_2024_001","")
S="hydrogen"
E=(S,"centralized-hydrogen-production")
t(*E,"Steam methane reformer","conventional","Reforms natural gas with steam, then shifts to hydrogen and CO2.",
  "natural gas, refinery fuel gas","9","iea_2024_001 row 285","refinery and ammonia hydrogen plants","steam-reformer_natural-gas","Petroleum Refining.Hydrogen (NG steam reforming); Petroleum Crude.Hydrogen (SMR)","iea_2024_001; CIMS","")
t(*E,"Steam methane reformer with capture on the shift gas","alternative","Capture on the shifted syngas, where the CO2 is already at high partial pressure. Taking the reformer flue gas as well needs a second, dilute-stream plant.",
  "natural gas; steam and electricity for the capture plant","9","iea_2024_001 row 285 (partial capture); row 284 gives 6 for high capture rates","Quest, Alberta","steam-reformer_ccs; steam-reformer_natural-gas_ccs; capture-unit_hydrogen","Petroleum Crude.Hydrogen (SMR CCS); Hydrogen.Production","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated. Partial capture takes only the shift gas and reaches about 60% of the plant total; full capture adds a diffuse-stream plant on the reformer flue gas.")
t(*E,"Autothermal reformer","prospective","Partial oxidation with oxygen in one vessel; suits high capture rates.",
  "natural gas, oxygen","5","iea_2024_001 row 276","Air Products Alberta net-zero hydrogen complex (Edmonton)","autothermal-reformer","","iea_2024_001","Commercial for syngas; the IEA TRL is for the CCUS-enabled hydrogen configuration.")
t(*E,"Water electrolysis, low temperature","alternative","Alkaline or PEM stacks splitting water with electricity.",
  "electricity, water","9","iea_2024_001 rows 261, 263","","electrolyser_electricity","","iea_2024_001","")
t(*E,"Solid-oxide electrolysis","prospective","High-temperature steam electrolysis with higher electrical efficiency.",
  "electricity, steam","8","iea_2024_001 row 264","","","","iea_2024_001","")
t(*E,"Methane pyrolysis","prospective","Splits methane into hydrogen and solid carbon, with no CO2 to capture.",
  "natural gas, electricity","7-8","iea_2024_001 rows 287, 290","Monolith; Hazer","","","iea_2024_001","")
t(*E,"Biomass or waste gasification","prospective","Gasifies biomass or waste to syngas for fuels or hydrogen.",
  "biomass, waste, oxygen","6","iea_2024_001 row 274","Enerkem (Varennes)","gasifier_biomass","","iea_2024_001","")
t(*E,"Gasification with capture on the shift gas","prospective","Gasifier with a shift reactor and physical-solvent capture, giving one concentrated stream; biomass or waste feed makes it a removal.",
  "biomass, waste, coal, petroleum coke; electricity and steam for the capture plant","5","iea_2024_001 row 277 (biomass-waste gasification with CCUS); row 280 gives 9 for coal gasification at partial capture rates","","gasifier_biomass_ccs; gasifier_coal_ccs","<sector>.CCS","iea_2024_001; CIMS","Concentrated stream, held once on cross-sector co2-capture-concentrated.")
E=(S,"hydrogen-distribution")
t(*E,"Pipeline compression and transmission","conventional","Compressors moving hydrogen through a dedicated pipeline to industrial users.",
  "electricity; natural gas (gas-driven compressors)","9","commercial","","","","","")
t(*E,"Hydrogen liquefaction and road transport","alternative","Liquefies hydrogen for trucking where there is no pipeline; liquefaction takes about a third of the hydrogen's energy.",
  "electricity","9","commercial","","","","","")
t(*E,"Blending into the natural gas network","prospective","Injects hydrogen into the existing gas system at a limited volume share, delivering it to users as a blended fuel.",
  "electricity (compression)","8","assessed; blending trials at 5-20% by volume","","","Natural Gas.OG Methane Blend","CIMS","")


def write(path: Path = OUT) -> int:
    """Write the rows above to `path` and return how many there were.

    newline="" with an explicit "\n" terminator keeps the file LF-ended on
    Windows as well, matching .gitattributes and keeping the diff to the rows
    that actually changed.
    """
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(R)
    return len(R)


if __name__ == "__main__":
    print(f"  end-use-technology-table.csv  {write()} rows")
