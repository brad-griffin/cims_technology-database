
## Sources

| Key | What it is | Where |
| - | - | - |
| NREL97 | NREL county-level industrial energy use: `Process_temperatures.csv`, one temperature per unit process by SIC code, split by heat type (fuel, steam, water, electric) | `data/raw-data/gov-usa/nrel/97_2018/`, **not yet registered** |
| NREL118 | NREL Manufacturing Thermal Energy Use in 2014: `mfg_eu_temps_*.csv`, 3.2 M rows. The shares above are energy-weighted by 4-digit NAICS and computed for this table | `data/raw-data/gov-usa/nrel/118_2019/`, **not yet registered** |
| nrcan_2025_001 | NRCan sub-process fossil fuel distribution for heavy industry (Canada), with its own bands < 200 / 200–700 / > 700 °C | `data/raw-data/gov-can/nrcan/nrcan_2025_energy-mapping-canada.xlsx` |
| rtc_2023_001 | RTC Industrial Thermal Decarbonization Package. Process temperatures by sector from DOE 2022 and BCG; page numbers are PDF pages; its bands are < 130 / 130–500 / > 500 °C | `data/raw-data/other-reports/`, registered, not extracted |
| caelp_2024_001 | CAELP/E3 *Measuring Economic Potential for Decarbonizing Industrial Heat* | `data/raw-data/other-reports/`, registered, not extracted |
| etsap_2010_002, etsap_2010_003, etsap_2012_001, etsap_2013_002, etsap_2015_001 | ETSAP I02, I03, I10, E19, I07, via their extractions | `data/raw-data/iea/etsap/` |
| iea_2024_001 | IEA ETP Clean Energy Technology Guide, 2024 edition; `row N` is its row number, and TRLs are as the guide reports them | `data/raw-data/iea/iea_2024_clean-tech-guide_rows.csv` |
| etsap_2010_001, lbnl_2021_001 | ETSAP I01 industrial boilers; LBNL electrification of boilers | `data/raw-data/` |
| epa_2017_001 | EPA CHP catalogue (steam-turbine process steam conditions) | harmonized `tech-parameter` |
| epa_2007_001 | EPA biomass CHP catalogue | harmonized `tech-parameter` |
| ipcc_2022_001 | IPCC AR6 WGIII Chapter 11, Table 11.3 (capture options; cites keith_2018_001, fasihi_2019_001) | `data/raw-data/peer-reviewed/` |
| ukerc_2013_001 / johansson_2012_001 | UKERC CH-SC28 reboiler duty | harmonized `tech-flow` |
| design doc | `design/industrial heat technology database design.md` | this repo |
| harmonized | the current harmonized layer | `data/harmonized/` |
| CIMS | CIMS model inputs, regions stripped | `C:\_dev\staging\cims\data\model_inputs\model\`, via `cims-roster.csv` |

Web sources checked 2026-09-11, not held in the repo:

| Source | Used for |
| - | - |
| [DOE 2015 chemicals bandwidth study](https://www.energy.gov/sites/prod/files/2015/08/f26/chemical_bandwidth_report.pdf) | ethanol 10% and industrial gases 3% of US chemicals energy |
| [DOE 2017 aluminium bandwidth study](https://www.energy.gov/sites/prod/files/2017/12/f46/Aluminum_bandwidth_study_2017.pdf) | semi-fabrication shares |
| [DOE 2015 iron and steel bandwidth study](https://www.energy.gov/sites/default/files/2015/08/f26/iron_and_steel_bandwidth_report_0.pdf) | coverage check only |
| [NRCan Trends 2017](https://oee.nrcan.gc.ca/publications/statistics/trends/2017/industrial.cfm) | subsector shares: wood products 2.9%, construction 3.1%, upstream 36.5% |
| [CER bioenergy overview](https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/renewable-energy-canada/an-overview-of-bioenergy.html) | ethanol, biodiesel and renewable diesel capacity |
| [Energies 2026 mining review](https://www.mdpi.com/1996-1073/19/8/1890) | mine energy breakdown; diesel over 80% at isolated mines |
| [Ferroglobe Bécancour](https://www.ferroglobe.com/about-ferroglobe/industrial-footprint/b%C3%A9cancour) | furnace sizes |
| [QIT-Fer et Titane](https://en.wikipedia.org/wiki/QIT-Fer_et_Titane) | slag capacity |
| [Oil Sands Magazine](https://www.oilsandsmagazine.com/news/2024/10/24/sagd-vs-css-thermal-in-situ-recovery-differences) | SAGD and CSS steam-to-oil ratios |
| [Alberta Energy Heritage](https://www.history.alberta.ca/energyheritage/sands/unlocking-the-potential/the-scientific-and-industrial-research-council-of-alberta/the-hot-water-separation-process.aspx) | Clark process water temperatures |
| [Shell 2025](https://www.shell.com/news-and-insights/newsroom/news-and-media-releases/2025/first-cargo-leaves-lng-canada.html) | LNG Canada capacity and first cargo |
| [CER 2022 pipeline market snapshot](https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/market-snapshots/2022/market-snapshot-greening-canadas-pipeline-infrastructure.html) | pipeline emissions; gas pipelines use gas-driven compressors, oil pipelines use electric pumps |
| [Algoma 2025 sustainability report summary](https://www.stocktitan.net/news/ASTL/algoma-steel-releases-2025-sustainability-f731fifk23lf.html) | first EAF July 2025; blast furnace and coke ovens decommissioned January 2026 |
| [GEM Dofasco](https://www.gem.wiki/ArcelorMittal_Dofasco_steel_plant) | Energiron ZR DRI project, blast furnace retirement dates |
| [GEM HIsarna](https://www.gem.wiki/HIsarna_process) | HIsarna pilot scale at IJmuiden |
| [ARENA NeoSmelt](https://arena.gov.au/projects/project-neosmelt/) | DRI-ESF pilot study, 2025-26 |
| [Canary Media: Electra](https://www.canarymedia.com/articles/green-steel/electra-clean-iron-investment-electrowinning) | low-temperature iron electrowinning demonstration |
| [Boston Metal](https://www.bostonmetal.com/moe-steel/) | molten oxide electrolysis demonstration |
| [Primetals HYFOR](https://www.primetals.com/en/portfolio/solutions/ironmaking/direct-reduction/hyfor/) | fluidised-bed hydrogen direct reduction pilot |
| [Rondo 2025](https://www.rondo.com/news-press/rondo-powers-up-worlds-largest-industrial-heat-battery) | 100 MWh heat battery, steam above 100 bar, October 2025 |
| [Heaten](https://heaten.com/) | steam-generating heat pump to 180 degC |
| [Coolbrook 2024](https://www.thechemicalengineer.com/news/coolbrook-primed-for-industry-use-after-rotodynamic-heater-pilot-tests-reach-over-1-000-c/) | RotoDynamic Heater pilot above 1,000 degC |
| [X-energy/Dow](https://x-energy.com/news/nrc-issues-environmental-assessment-with-finding-of-no-significant-impact-for-dow-and-x-energys-propsed-advanced-nuclear-project-in-texas/) | HTGR for industrial steam and power |
| [Deep Sky 2025](https://www.deepskyclimate.com/blog/history-made-deep-sky-alpha-begins-operations-with-north-americas-first-co2-storage-via-direct-air-capture-2) | Deep Sky Alpha, Innisfail, operating August 2025 |
| [Stratos](https://www.qcintel.com/carbon/article/stratos-dac-timeline-unclear-after-commissioning-issue-found-64333.html) | liquid-solvent DAC commissioning status |
| [BASF e-cracker](https://www.thechemicalengineer.com/news/world-first-electric-steam-cracker-demo-starts-operations-in-push-to-slash-emissions-by-90/) | electric steam-cracker demonstration at Ludwigshafen |
| [Rio Tinto](https://www.riotinto.com/en/can/canada-operations/rio-tinto-fer-et-titane) | BlueSmelting pre-reduction at Sorel-Tracy |
| [Svante / Lafarge Richmond](https://www.svanteinc.com/press-releases/lafarge-canada-collaborates-with-svante-and-dimensional-energy-to-begin-utilization-of-co2-captured-at-richmond-cement-plant/) | solid-sorbent capture pilot on a cement plant |

NREL, NRCan and RTC bands are not mapped onto ours; tiers are assigned from continuous
temperatures (NREL 97 and 118) or stated process temperatures.

In the technology tables, "commercial" means the level is taken from wide deployment
rather than a published TRL, and "assessed" means it is read from project or pilot
evidence. "harmonized" means the technology is already in the roster.

## How CIMS's capture requests split

CIMS has one `CCS` service per sector, costed from NETL/DOE 2022 *Cost of Capturing
CO2 from Industrial Sources*:

| CIMS node | Natural gas (GJ/t CO2) | Capex ($ per t-per-yr) |
| - | - | - |
| Chemical Products.CCS | 1.0 | 153 |
| Iron and Steel.CCS | 4.29 | 514 |
| Industrial Minerals.CCS | 4.84 | 589 |
| Petroleum Refining.CCS | 3.38 | 692 |

Technologies requesting CCS, by stream:

| Concentrated | Diffuse |
| - | - |
| Chemicals: `Adv reforming reactors CCS` (ammonia, methanol) | Chemicals: `NG CCS`, `Coal CCS`, `BPST NG 30 MW CCS` (Steam); `Product gas CCS` (Pyrolysis) |
| Refining: `NG steam reforming Eff CCS`, `petcoke gasification CCS` (Hydrogen) | Refining: Steam, Still Gas boiler / cogen / heater, `NG Eff CCS` (Direct Heat), `Fluidized catalytic cracking CCS`, `Coking soaker visbreaking CCS` |
| Iron and steel: `HIsarna CCS`, `DRI + EAF + CCS`, `Smelter + EAF + CCS`, `Corex smelter + CCS`, `Top gas recycling CCS` | Iron and steel: Steam `NG CCS`, `Coal CCS`, `BPST NG 30 MW CCS`; `Iron sinter agglomeration CCS`; `Ultra power EAF + O2 + CCS` |
| Natural gas: `Formation CCS` (acid gas at processing plants) | Industrial minerals: `New preheat Eff with CCS` (cement kiln), `Rotary Coal/NG with CCS` (lime), `NG Eff` / `Coal Std with CCS` (Heat) |
| Petroleum crude: `SMR CCS` (Hydrogen), `Upgrading ELDAR CCS` | Petroleum crude: Steam and Still Gas Steam boilers and cogen |
| | Natural gas: `Boiler Efficient CCS` (Direct Heat), `Flaring CCS` |
| | Ethanol and biodiesel: Steam boilers only (CIMS has no fermentation-CO2 capture) |

Smelting reduction, Corex and top-gas recycling are unsourced as concentrated (IPCC
names only HIsarna and syngas DRI). An SMR emits both kinds; CIMS books one rate.

## Technology table

`end-use-technology-table.csv` holds the technology rows in full: type, description,
energy inputs, TRL and its basis, examples, matching roster and CIMS names, sources
and notes. The .md shows a shortened view.

`specific-energy-use` is empty everywhere for now. Each technology, efficient variants
included, is to carry its own energy use once a source is found, rather than a saving
against a base technology.

Coverage: all thirteen sector groups, 393 technologies. Empty `roster-match` and
`cims-match` cells mark technologies the database and CIMS do not yet carry.

## Found along the way

- **CIMS defect:** in the NB and NL petroleum-refining files, the service
  `Distillation.Atmospheric` reads `Distillation.NBmospheric` and
  `Distillation.NLmospheric`. It looks like a find-and-replace of a region code. It
  lives in `staging/cims/.../petroleum_refining/petroleum_refining_{nb,nl}.csv` and
  splits those provinces' atmospheric distillation onto a separate service.
- **CIMS defect:** `Petroleum Refining.Steam` technology `NG CCS` requests 66.5 t CO2
  per unit from the CCS service. Every other boiler requests about 0.06 t, including
  `NG Eff CCS` on the same node. It looks like a factor-of-1000 unit slip.
- **Harmonized extraction error:** `tp-1509` stores the direct-air-capture abatement
  cost as 2.0 USD/t. The IPCC Table 11.3 cell reads "about USD94–232 t–1", so the
  number was probably taken from a stray "2" in the cell. The fix belongs in the IPCC
  extraction, not in the generated CSV.
- **Harmonized naming clash:** the roster entry `capture-unit` carries both the CIMS
  natural-gas blowdown capture (methane) and IPCC's "CCUS of concentrated CO2". They
  are different things under one name.
- **Temperatures missing for the new sector:** no held or checked source gives
  temperatures for SAGD steam, heater-treaters, amine and glycol regeneration, or
  modern warm-water oil-sands extraction. Those cells say so, and `in-situ-bitumen` is
  marked as an unconfirmed tier.
- **Food ovens are filed under `process-heat-high-temp`** in the harmonized layer. The
  sources put baking at 100–232 °C (NREL 97), which is medium tier.
- **No held source gives a temperature** for potash drying and crystallisation, mine
  air heating, capture solvent regeneration, or recovery-boiler steam conditions.
  `mining/product-drying` is marked as an unconfirmed tier.
- NREL 97 and NREL 118 now carry real weight: they are the only continuous-temperature
  sources. Registering them in the manifest is overdue.
