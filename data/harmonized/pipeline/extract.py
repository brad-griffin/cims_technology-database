"""Layer 1 -> layer 2: read every extraction and return its facts, as reported.

Each source's own technology name is kept exactly as the extraction wrote it
(`source-technology`). Nothing is renamed, grouped or canonicalized here: which
archetype a source's technology is an example of is decided in one place,
records/source-example.csv, and applied by examples.py.

An EXAMPLE is one technology as one source presents it, in one of that source's
own contexts (its process or table band). Its id is

    <source-id>:<source-technology>[@<process>]

where source-id is the document the extraction was made from (UKERC for the
UKERC tables, even where a value is attributed to an original UKERC cites).

Returns facts, flows and constraints in the long schema, plus per-example
attributes (description, readiness, state of development) that sources report
as parameters but that describe the example rather than quantify it.
"""
from __future__ import annotations

import re
from collections import defaultdict

from .common import RAW, REFERENCE, currency_year, read

# UK TIMES (via Bataille) prices its "improvement technologies" and add-ons as
# the cost of adding them to an existing plant: cost-basis incremental.
UKTM_ADD_ON = re.compile(r"^(Improvement technology \d+ for existing|[^.]*\badd-on for existing)")

# --- the extractions, in load order (record ids are numbered in this order) --
TEMPLATE_FILES = [
    ("gov-usa/epa/epa_2007_biomass-chp-technologies-catalog.csv", "epa_2007_001"),
    ("gov-usa/epa/epa_2017_chp-technologies-catalog.csv", "epa_2017_001"),
    ("gov-usa/lbnl/lbnl_2021_electrification-of-boilers.csv", "lbnl_2021_001"),
    ("iea/etsap/etsap_2010_industrial-combustion-boilers.csv", "etsap_2010_001"),
]
UKERC = ("other-reports/ukerc_2013_usable-energy-database", "ukerc_2013_001")
BATAILLE = ("other-reports/bataille_2017_heavy-industry-database", "bataille_2017_001")
IPCC = ("peer-reviewed/ipcc_2022_ar6-wgiii-chapter11", "ipcc_2022_001")
IEA_GUIDE = ("iea/iea_2024_clean-tech-guide", "iea_2024_001")
ETSAP_BRIEFS = [
    ("iea/etsap/etsap_2010_iron-and-steel", "etsap_2010_002"),
    ("iea/etsap/etsap_2010_cement-production", "etsap_2010_003"),
    ("iea/etsap/etsap_2015_pulp-and-paper", "etsap_2015_001"),
    ("iea/etsap/etsap_2012_aluminium-production", "etsap_2012_001"),
    ("iea/etsap/etsap_2013_heat-pumps", "etsap_2013_002"),
    # extracted 2026-09-23/24 from the ETSAP brief assessment
    ("iea/etsap/etsap_2010_combined-heat-and-power", "etsap_2010_004"),
    ("iea/etsap/etsap_2010_biomass-for-heat-and-power", "etsap_2010_005"),
    ("iea/etsap/etsap_2013_stationary-fuel-cells", "etsap_2013_004"),
    ("iea/etsap/etsap_2010_syngas-from-coal", "etsap_2010_011"),
    ("iea/etsap/etsap_2014_coal-mining-and-logistics", "etsap_2014_002"),
    ("iea/etsap/etsap_2013_biogas-and-bio-syngas", "etsap_2013_012"),
    # the remaining partial briefs, extracted 2026-09-24
    ("iea/etsap/etsap_2010_geothermal-heat-and-power", "etsap_2010_006"),
    ("iea/etsap/etsap_2010_gas-fired-power", "etsap_2010_008"),
    ("iea/etsap/etsap_2013_concentrating-solar-power", "etsap_2013_001"),
    ("iea/etsap/etsap_2013_thermal-energy-storage", "etsap_2013_005"),
    ("iea/etsap/etsap_2010_co2-capture-and-storage", "etsap_2010_007"),
    ("iea/etsap/etsap_2014_hydrogen-production-and-distribution", "etsap_2014_003"),
    ("iea/etsap/etsap_2013_bio-methanol", "etsap_2013_007"),
    ("iea/etsap/etsap_2010_liquid-fuels-from-coal-and-gas", "etsap_2010_012"),
    ("iea/etsap/etsap_2010_unconventional-oil-and-gas", "etsap_2010_010"),
    ("iea/etsap/etsap_2011_oil-and-gas-logistics", "etsap_2011_001"),
    ("iea/etsap/etsap_2014_oil-refineries", "etsap_2014_001"),
    ("iea/etsap/etsap_2013_renewable-desalination", "etsap_2013_008"),
    ("iea/etsap/etsap_2013_bio-ethylene", "etsap_2013_009"),
    ("iea/etsap/etsap_2013_biomass-production-and-logistics", "etsap_2013_010"),
    ("iea/etsap/etsap_2013_liquid-biofuels", "etsap_2013_011"),
]
# other extractions in the ETSAP-brief shape (process/technology rows, _nodes, _flows),
# loaded by the same reader: (stem, source id, region of the data)
BRIEF_SHAPE = [
    ("gov-usa/doe/bandwidth-studies/doe_2015_iron-and-steel-bandwidth-study", "doe_2015_001", "US"),
    ("gov-usa/doe/bandwidth-studies/doe_2015_petroleum-refining-bandwidth-study", "doe_2015_002", "US"),
    ("gov-usa/doe/bandwidth-studies/doe_2015_pulp-and-paper-bandwidth-study", "doe_2015_003", "US"),
    ("gov-usa/doe/bandwidth-studies/doe_2015_chemicals-bandwidth-study", "doe_2015_004", "US"),
    ("gov-usa/doe/bandwidth-studies/doe_2017_aluminum-bandwidth-study", "doe_2017_001", "US"),
    ("gov-usa/doe/bandwidth-studies/doe_2017_cement-bandwidth-study", "doe_2017_002", "US"),
    ("gov-usa/doe/bandwidth-studies/doe_2017_food-and-beverage-bandwidth-study", "doe_2017_003", "US"),
    ("gov-usa/doe/doe_2022_industrial-decarbonization-roadmap", "doe_2022_001", "US"),
    ("gov-usa/epa/epa_2022_waste-heat-to-power", "epa_2022_001", "US"),
    ("gov-usa/netl/netl_2022_industrial-co2-capture-retrofit-database", "netl_2022_001", "US"),
    ("iea/iea_2018_future-of-petrochemicals", "iea_2018_001", "global"),
    ("iea/iea_2019_future-of-hydrogen", "iea_2019_002", "global"),
    ("iea/iea_2021_ammonia-technology-roadmap", "iea_2021_001", "global"),
    ("iea/philibert_2017_renewable-energy-for-industry_iea", "philibert_2017_001", "global"),
    ("other-reports/lehne-preston_2018_making-concrete-change_chatham-house", "lehne-preston_2018_001", "global"),
    ("other-reports/caelp-e3_2024_decarbonizing-industrial-heat", "caelp_2024_001", "US"),
    ("other-reports/rtc_2023_renewable-thermal-vision", "rtc_2023_001", "US"),
    ("other-reports/van-der-meijden_2011_bio-methane-from-wood_ecn", "van-der-meijden_2011_001", "global"),
    ("peer-reviewed/amin_2011_methane-catalytic-cracking-review_ijhe", "amin_2011_001", "global"),
    ("peer-reviewed/armijo-philibert_2020_green-hydrogen-ammonia-chile-argentina_ijhe", "armijo-philibert_2020_001", "global"),
    ("peer-reviewed/fasihi_2019_direct-air-capture-techno-economics_jclepro", "fasihi_2019_001", "global"),
    ("peer-reviewed/habert_2020_cement-concrete-decarbonization_nat-rev-earth-environ", "habert_2020_001", "global"),
    ("peer-reviewed/leeson_2017_industrial-ccs-techno-economics_ijggc", "leeson_2017_001", "global"),
    ("peer-reviewed/moore_2017_thermal-hydrogen_ijhe", "moore_2017_001", "global"),
    ("peer-reviewed/roemer_2026_mining-energy-decarbonization-review_energies", "roemer_2026_001", "global"),
    ("peer-reviewed/vogl_2018_hydrogen-direct-reduction-steelmaking_jclepro", "vogl_2018_001", "global"),
    ("gov-dk/dea/dea_2026_technology-data-industrial-process-heat", "dea_2026_001", "Denmark"),
    ("peer-reviewed/humbert_2024_electrowinning-iron-economics_jsm", "humbert_2024_001", "global"),
    ("peer-reviewed/siyambalapitiya_2026_induction-hydrogen-billet-reheating_jsm", "siyambalapitiya_2026_001", "Australia"),
    ("peer-reviewed/svensson_2021_electric-plasma-lime-calcination_fclim", "svensson_2021_001", "Sweden"),
    ("peer-reviewed/kuparinen_2017_lime-kiln-renewable-fuels_bioresources", "kuparinen_2017_001", "South America"),
    ("peer-reviewed/kiss_2012_energy-efficient-distillation_energy", "kiss_2012_001", "global"),
    ("peer-reviewed/smith_2020_haber-bosch-carbon-free-ammonia_ees", "smith_2020_001", "global"),
    ("peer-reviewed/layritz_2021_steam-cracker-electrification-ocm_apenergy", "layritz_2021_001", "EU"),
    ("gov-eu/jrc/brinkmann_2014_chlor-alkali-bref_jrc", "brinkmann_2014_001", "EU"),
    ("gov-eu/jrc/jrc_2007_lvic-s-bref", "jrc_2007_001", "EU"),
    ("gov-usa/epa/epa_2010_nitric-acid-ghg-technologies", "epa_2010_001", "US"),
    ("other-reports/rissman_2022_low-temperature-industrial-heat_energy-innovation", "rissman_2022_001", "US"),
    ("gov-nl/pbl/van-geene_2024_midden-database-v0-4a_pbl", "van-geene_2024_001", "Netherlands"),
    ("peer-reviewed/uekert_2023_closed-loop-plastics-recycling_acs-sce", "uekert_2023_001", "US"),
    ("peer-reviewed/onarheim_2017_ccs-pulp-paper-part1-performance_ijggc", "onarheim_2017_001", "Finland"),
    ("peer-reviewed/onarheim_2017_ccs-pulp-paper-part2-economics_ijggc", "onarheim_2017_002", "Finland"),
    ("gov-dk/dea/dea_2024_technology-data-carbon-capture-transport-storage", "dea_2024_002", "Denmark"),
    ("gov-dk/dea/dea_2026_technology-data-renewable-fuels", "dea_2026_003", "Denmark"),
    ("gov-dk/dea/dea_2026_technology-data-energy-storage", "dea_2026_004", "Denmark"),
    ("other-reports/mpp_2022_steel-capex-opex-per-technology", "mpp_2022_001", "global"),
    ("other-reports/rissman_2023_industrial-thermal-batteries_energy-innovation", "rissman_2023_001", "US"),
    ("peer-reviewed/zuberi_2022_heat-pumps-us-food-manufacturing_ecm", "zuberi_2022_001", "US"),
    ("peer-reviewed/zuberi_2023_heat-pumps-us-textile-paper-automotive_energy-efficiency", "zuberi_2023_001", "US"),
    ("peer-reviewed/kong_2016_emerging-energy-efficiency-pulp-paper_jclepro", "kong_2016_001", "global"),
    ("peer-reviewed/fleiter_2012_german-pulp-paper-saving-potentials_energy", "fleiter_2012_001", "Germany"),
    ("peer-reviewed/lipiainen_2022_pulp-paper-energy-transition-finland-sweden_spc", "lipiainen_2022_001", "Finland and Sweden"),
    ("peer-reviewed/hasanbeigi_2014_alternative-emerging-ironmaking_rser", "hasanbeigi_2014_001", "global"),
    ("gov-usa/lbnl/hasanbeigi_2013_emerging-steel-technologies_lbnl", "hasanbeigi_2013_001", "global"),
    ("peer-reviewed/ren_2006_olefins-steam-cracking-alternatives_energy", "ren_2006_001", "global"),
    ("gov-usa/lbnl/neelis_2008_petrochemical-energy-guide_lbnl", "neelis_2008_001", "US"),
    ("other-reports/ieaghg_2018_co2-capture-cement-iron-steel_tr03", "ieaghg_2018_001", "global"),
    ("gov-usa/netl/hughes_2023_cost-co2-capture-industrial-sources_netl", "hughes_2023_001", "US"),
    ("gov-nl/pbl/van-geene_2025_nobian-salt-chlor-alkali-update_pbl", "van-geene_2025_001", "Netherlands"),
    ("gov-nl/pbl/negri_2021_polyolefins-decarbonisation_pbl", "negri_2021_001", "Netherlands"),
    ("gov-nl/pbl/haque_2023_energy-efficiency-options_pbl", "haque_2023_001", "Netherlands"),
    ("gov-usa/lbnl/worrell_2010_energy-efficiency-iron-steel_lbnl", "worrell_2010_001", "US"),
    ("gov-usa/epa/epa_2010_pulp-paper-ghg-technologies", "epa_2010_002", "US"),
    ("gov-usa/epa/epa_2012_iron-steel-ghg-technologies", "epa_2012_001", "US"),
    ("iea/iea_2020_iron-steel-technology-roadmap_iea", "iea_2020_002", "global"),
    ("other-reports/larson_2006_gasification-biorefining-kraft-pulp-paper_princeton", "larson_2006_001", "US"),
    ("gov-usa/lbnl/khrushch_1999_chp-carbon-reduction-chemicals-pulp-paper_lbnl", "khrushch_1999_001", "US"),
    ("other-reports/app_2010_soact-steelmaking-handbook_lbnl", "app_2010_001", "global"),
    ("gov-usa/doe/doe_2023_liftoff-industrial-decarbonization", "doe_2023_001", "US"),
    ("gov-usa/doe/doe_2025_liftoff-chemicals-refining", "doe_2025_001", "US"),
    ("gov-eu/jrc/boulamanti_2017_chemicals-prospective-scenarios_jrc", "boulamanti_2017_001", "EU"),
    ("gov-usa/lbnl/kramer_2009_energy-efficiency-pulp-paper_lbnl", "kramer_2009_001", "US"),
    ("gov-eu/jrc/falcke_2017_lvoc-bref_jrc", "falcke_2017_001", "EU"),
    ("gov-eu/jrc/jrc_2022_ferrous-metals-processing-bref", "jrc_2022_001", "EU"),
    ("gov-eu/jrc/remus_2013_iron-steel-bref_jrc", "remus_2013_001", "EU"),
    ("gov-eu/jrc/suhr_2015_pulp-paper-bref_jrc", "suhr_2015_001", "EU"),
    ("gov-eu/jrc/jrc_2007_lvic-aaf-bref", "jrc_2007_002", "EU"),
    ("gov-eu/jrc/jrc_2007_polymers-bref", "jrc_2007_003", "EU"),
    ("gov-usa/doe/doe_2023_liftoff-low-carbon-cement", "doe_2023_002", "US"),
    ("gov-eu/jrc/schorcht_2013_cement-lime-magnesia-bref_jrc", "schorcht_2013_001", "EU"),
    ("other-reports/csi-ecra_2017_cement-technology-papers", "csi-ecra_2017_001", "global"),
    ("iea/iea_2018_cement-technology-roadmap_iea", "iea_2018_002", "global"),
    ("peer-reviewed/voldsund_2019_cement-co2-capture-comparison_energies", "voldsund_2019_001", "EU"),
    ("gov-usa/epa/worrell_2013_energy-efficiency-cement_energystar", "worrell_2013_001", "US"),
    ("gov-usa/lbnl/kermeli_2011_energy-efficiency-concrete_lbnl", "kermeli_2011_001", "US"),
    ("gov-eu/jrc/scalet_2013_glass-bref_jrc", "scalet_2013_001", "EU"),
    ("gov-usa/lbnl/worrell_2008_energy-efficiency-glass_lbnl", "worrell_2008_001", "US"),
    ("gov-eu/jrc/jrc_2007_ceramics-bref", "jrc_2007_004", "EU"),
    ("gov-eu/jrc/barthe_2015_refining-bref_jrc", "barthe_2015_001", "EU"),
    ("gov-usa/epa/worrell_2015_energy-efficiency-petroleum-refineries_energystar", "worrell_2015_001", "US"),
    ("gov-usa/epa/kermeli_2016_energy-efficiency-metal-casting_energystar", "kermeli_2016_001", "US"),
    ("gov-eu/jrc/aries_2024_smitheries-foundries-bref_jrc", "aries_2024_001", "EU"),
    ("gov-eu/jrc/cusano_2017_non-ferrous-metals-bref_jrc", "cusano_2017_001", "EU"),
    ("gov-eu/jrc/lecomte_2017_large-combustion-plants-bref_jrc", "lecomte_2017_001", "EU"),
    ("gov-eu/jrc/giner-santonja_2019_food-drink-milk-bref_jrc", "giner-santonja_2019_001", "EU"),
    ("gov-usa/lbnl/masanet_2012_energy-efficiency-baking_lbnl", "masanet_2012_001", "US"),
    ("gov-usa/epa/stuckrath_2022_energy-efficiency-distilleries_energystar", "stuckrath_2022_001", "US"),
    ("gov-usa/lbnl/galitsky_2003_energy-efficiency-breweries_lbnl", "galitsky_2003_001", "US"),
    ("gov-usa/lbnl/galitsky_2003_energy-efficiency-corn-wet-milling_lbnl", "galitsky_2003_002", "US"),
    ("gov-usa/lbnl/galitsky_2008_energy-efficiency-pharmaceutical_lbnl", "galitsky_2008_001", "US"),
    ("gov-eu/jrc/brinkmann_2016_common-waste-water-gas-bref_jrc", "brinkmann_2016_001", "EU"),
    ("gov-eu/jrc/daginnus_2023_common-waste-gas-chemical-bref_jrc", "daginnus_2023_001", "EU"),
    ("gov-eu/jrc/stubdrup_2016_wood-based-panels-bref_jrc", "stubdrup_2016_001", "EU"),
    ("gov-eu/jrc/neuwahl_2019_waste-incineration-bref_jrc", "neuwahl_2019_001", "EU"),
    ("gov-eu/jrc/pinasseau_2018_waste-treatment-bref_jrc", "pinasseau_2018_001", "EU"),
    ("gov-dk/dea/dea_2026_technology-data-electricity-district-heat", "dea_2026_006", "Denmark"),
    ("gov-dk/dea/dea_2026_technology-data-heating-installations", "dea_2026_007", "Denmark"),
    ("gov-dk/dea/dea_2026_technology-review-non-road-machinery", "dea_2026_005", "Denmark"),
    ("gov-nl/pbl/joshi_2022_midden-onshore-gas-oil_pbl", "joshi_2022_001", "Netherlands"),
    ("other-reports/ager_2023_hthp-paper-drying_kth", "ager_2023_001", "Sweden"),
    ("other-reports/agora_2021_breakthrough-strategies-climate-neutral-industry", "agora_2021_001", "EU"),
    ("peer-reviewed/allanore_2015_molten-oxide-electrolytes_jes", "allanore_2015_001", "global"),
    ("peer-reviewed/arens_2017_low-carbon-iron-steel-germany_jclepro", "arens_2017_001", "Germany"),
    ("peer-reviewed/bhaskar_2020_hydrogen-direct-reduction_energies", "bhaskar_2020_001", "EU"),
    ("other-reports/bhp_2023_electric-smelting-furnace", "bhp_2023_001", "Australia"),
    ("peer-reviewed/cancio-diaz_2017_limestone-calcined-clay-cement_deveng", "cancio-diaz_2017_001", "Cuba"),
    ("peer-reviewed/ciambellotti_2024_hthp-tissue-paper_energies", "ciambellotti_2024_001", "EU"),
    ("peer-reviewed/devlin_2023_green-hydrogen-steel-opportunities_ncomms", "devlin_2023_001", "global"),
    ("other-reports/draxler_2021_green-steel-technology-assessment_gsfe", "draxler_2021_001", "EU"),
    ("gov-usa/epa/natural-gas-star/epa_2006_lessons-learned_natural-gas-star", "epa_2006_001", "US"),
    ("gov-usa/epa/natural-gas-star/epa_2011_pro-fact-sheets_natural-gas-star", "epa_2011_001", "US"),
    ("gov-usa/epa/epa_2013_chp-boiler-replacement-fact-sheet", "epa_2013_001", "US"),
    ("other-reports/fpinnovations_2026_kraft-pulp-decarbonization-canada", "fpinnovations_2026_001", "Canada"),
    ("gov-can/nrcan/francis_2002_energy-benchmarking-pulp-paper_nrcan", "francis_2002_001", "Canada"),
    ("other-reports/golder_2021_canadian-steel-energy-ghg-roadmap_cspa", "golder_2021_001", "Canada"),
    ("peer-reviewed/hamaguchi_2012_biofuels-kraft-pulp-mills_energies", "hamaguchi_2012_001", "global"),
    ("iea/iea_2013_chemical-catalytic-processes-roadmap_iea", "iea_2013_001", "global"),
    ("other-reports/ieaghg_2013_co2-capture-integrated-steel-mill", "ieaghg_2013_003", "EU"),
    ("other-reports/ieaghg_2016_ccs-retrofit-pulp-board-mills", "ieaghg_2016_001", "EU"),
    ("other-reports/kearns_2021_ccs-technology-readiness-costs_gccsi", "kearns_2021_001", "US"),
    ("peer-reviewed/kim_2022_iron-steel-decarbonization-review_erss", "kim_2022_001", "global"),
    ("other-reports/kiss_2017_heat-pumps-chemical-process-industry_crc", "kiss_2017_001", "EU"),
    ("peer-reviewed/kuparinen_2019_biomass-ccu-kraft-pulp_mitig", "kuparinen_2019_001", "global"),
    ("other-reports/material-economics_2019_industrial-transformation-2050", "material-economics_2019_001", "EU"),
    ("peer-reviewed/moya_2013_eu-iron-steel-efficiency-payback_jclepro", "moya_2013_001", "EU"),
    ("peer-reviewed/mynko_2023_steam-cracking-electrification_jclepro", "mynko_2023_001", "EU"),
    ("gov-can/nrcan/nrcan_2008_benchmarking-canadian-pulp-paper-mills", "nrcan_2008_001", "Canada"),
    ("peer-reviewed/otto_2017_power-to-steel_energies", "otto_2017_001", "Germany"),
    ("peer-reviewed/owttrim_2022_pulp-paper-energy-saving-bandwidths_ecm", "owttrim_2022_001", "Canada"),
    ("peer-reviewed/pardo_2013_eu-iron-steel-prospective-scenarios_energy", "pardo_2013_001", "EU"),
    ("peer-reviewed/perez-ramirez_2003_n2o-nitric-acid_apcatb", "perez-ramirez_2003_001", "global"),
    ("other-reports/provides_2018_deep-eutectic-solvents-paper", "provides_2018_001", "EU"),
    ("peer-reviewed/rechberger_2020_hydrogen-direct-reduction_steel-research", "rechberger_2020_001", "EU"),
    ("peer-reviewed/riedewald_2021_mixed-plastic-pyrolysis-molten-metal_wm", "riedewald_2021_001", "Belgium"),
    ("peer-reviewed/rouwenhorst_2019_islanded-ammonia-power_rser", "rouwenhorst_2019_001", "global"),
    ("peer-reviewed/sabah_2026_electric-smelting-furnace-modelling_jsm", "sabah_2026_001", "global"),
    ("peer-reviewed/sanchez-berriel_2016_limestone-calcined-clay-cement-cuba_jclepro", "sanchez-berriel_2016_001", "Cuba"),
    ("peer-reviewed/saygin_2011_chemical-best-practice-technology_energy", "saygin_2011_001", "global"),
    ("peer-reviewed/schneider_2015_cement-process-technology_ccr", "schneider_2015_001", "global"),
    ("peer-reviewed/singh_2021_enzymatic-pet-recycling_joule", "singh_2021_001", "US"),
    ("peer-reviewed/solis_2020_chemical-recycling-household-plastics_wm", "solis_2020_001", "global"),
    ("other-reports/spees_2023_thermal-batteries_brattle", "spees_2023_001", "US"),
    ("peer-reviewed/talaei_2018_chemical-sector-efficiency-ghg_energy", "talaei_2018_001", "Canada"),
    ("peer-reviewed/talaei_2020_canada-iron-steel-efficiency_energy-efficiency", "talaei_2020_001", "Canada"),
    ("peer-reviewed/toktarova_2020_swedish-steel-pathways_energies", "toktarova_2020_001", "Sweden"),
    ("other-reports/vakkilainen_2006_kraft-recovery-boilers-high-dry-solids", "vakkilainen_2006_001", "global"),
]
# parameters that describe the example rather than quantify it
EXAMPLE_ATTRS = ("description", "trl", "state-of-development", "year-available")


def slug(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (x or "").lower()).strip("-")


def example_id(source_id: str, tech: str, process: str = "") -> str:
    return f"{source_id}:{tech}" + (f"@{slug(process)}" if process else "")


class Loader:
    def __init__(self):
        self.facts, self.flows, self.cons = [], [], []
        self.examples: dict[str, dict] = {}
        self.missing: list[str] = []
        self.trl_map = {(r["scale"], r["level"].strip().upper()): r["canonical-trl"]
                        for r in read(REFERENCE / "trl-scale-map.csv")}

    # -- examples ---------------------------------------------------------
    def example(self, source_id, tech, process="", node=None, extraction=""):
        eid = example_id(source_id, tech, process)
        ex = self.examples.get(eid)
        if ex is None:
            node = node or {}
            ex = self.examples[eid] = {
                "example-id": eid, "source-id": source_id, "source-technology": tech,
                "process": process, "sector-reported": node.get("sector", ""),
                "end-use-reported": node.get("end-use", ""),
                "step-reported": node.get("process-step", ""),
                "service-unit-reported": node.get("service-unit", ""),
                "extraction-file": extraction, "description": "", "trl": "",
                "trl-as-reported": "", "trl-scale": "", "state-of-development": "",
                "year-available": "", "capacity-basis": "", "capacity-unit": "",
                "note": ""}
        return ex

    def attr(self, ex, param, val, scale="trl-1-9"):
        """Record a descriptive parameter on the example. First value wins; a
        readiness level is mapped onto the common 1-9 ladder, carrying a range
        at its lower bound."""
        if param == "trl":
            if ex["trl"]:
                return
            v = (val or "").strip().upper().replace("–", "-")
            parts = [p.strip() for p in re.split(r"[-,]", v) if p.strip()]
            hits = [h for h in (self.trl_map.get((scale, p)) for p in parts) if h]
            if not hits:
                ex["note"] = (ex["note"] + " " if ex["note"] else "") + (
                    f"Readiness {val!r} on the {scale} scale is not in trl-scale-map.csv.")
                return
            ex["trl"], ex["trl-as-reported"], ex["trl-scale"] = min(hits, key=int), val, scale
        elif not ex[param]:
            ex[param] = val

    # -- facts ------------------------------------------------------------
    def fact(self, ex, **kw):
        row = {"record-id": f"tp-{len(self.facts) + 1:04d}", "example-id": ex["example-id"],
               "source-technology": ex["source-technology"]}
        row.update(kw)
        self.facts.append(row)

    # -- the source shapes ----------------------------------------------------
    def template_file(self, rel, source_id):
        """A single-file extraction in the template format: one process step,
        no node map. These four are boiler and CHP catalogues."""
        path = RAW / rel
        if not path.exists():
            self.missing.append(rel)
            return
        node = {"sector": "all-industry", "end-use": "steam-and-hot-water"}
        for row in read(path):
            tech = (row.get("technology") or "").strip()
            if not tech:
                continue
            ex = self.example(source_id, tech, row.get("process", ""), node, rel)
            param = (row.get("parameter") or "").strip()
            val = (row.get("value") or "").strip()
            if param in EXAMPLE_ATTRS:
                if val:
                    self.attr(ex, param, val)
                continue
            if not (val or row.get("formula")):
                continue
            note = (row.get("note") or "").strip()
            m = re.search(r"COST BASIS:\s*([a-z-]+)", note)
            cap = re.search(r"CAPACITY BASIS:\s*([a-z-]+)", note)
            unit = (row.get("unit") or "").strip()
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, **{"capacity-basis": cap.group(1) if cap else ""},
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "derived" if row.get("formula") else "reported",
                         "formula": (row.get("formula") or "").strip(),
                         "cost-basis": m.group(1) if m else "", "currency": currency_year(unit),
                         "source-id": source_id, "source-file": path.name,
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": rel, "via-source-id": "", "confidence": "",
                         "status": "draft", "note": note})

    def nodes(self, stem, source_id):
        path = RAW / f"{stem}_nodes.csv"
        if not path.exists():
            self.missing.append(f"{stem}_nodes.csv")
            return {}
        out = {}
        for r in read(path):
            out[(r["process"], r["technology"])] = r
            self.example(source_id, r["technology"], r["process"], r, f"{stem}.csv")
        return out

    def ukerc(self):
        stem, sid = UKERC
        nm = self.nodes(stem, sid)
        if not nm:
            return
        for row in read(RAW / f"{stem}.csv"):
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = row["parameter"], (row.get("value") or "").strip()
            if param in ("trl", "state-of-development", "year-available"):
                if val:
                    self.attr(ex, param, val)
                continue
            if not (val or row.get("formula")):
                continue
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            orig = [x for x in (row.get("source-original") or "").split(";") if x]
            cost = param.startswith(("capex", "opex"))
            # UKERC is a compilation: the value belongs to whoever it cites
            # (design rule: two-level attribution). The original is the source,
            # UKERC the via.
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="UK",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "derived" if row.get("formula") else "reported",
                         "formula": (row.get("formula") or "").strip(),
                         "cost-basis": "installed" if cost else "",
                         "capacity-basis": "product-output" if cost else "",
                         "currency": currency_year(unit),
                         "source-id": orig[0] if orig else sid,
                         "via-source-id": sid if orig else "",
                         "via-locator": (row.get("reference") or "").strip(),
                         "source-file": "ukerc_2013_usable-energy-database.xlsx",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "", "status": "draft",
                         "note": note + (f"  Cited by UKERC alongside: {', '.join(orig[1:])}."
                                         if len(orig) > 1 else "")})
        techs = {t for (_, t) in nm}
        for i, row in enumerate(read(RAW / f"{stem}_flows.csv"), 1):
            if row["technology"] not in techs:
                continue
            ex = self.example_for(sid, row["technology"], nm)
            self.flows.append({
                "record-id": f"tf-{i:04d}", "example-id": ex["example-id"],
                "source-technology": row["technology"],
                "direction": row["direction"], "commodity": row["commodity"],
                "value": row["value"], "unit": row["unit"], "per-unit": row["per-unit"],
                "value-min": row["value-min"], "value-max": row["value-max"],
                "co-product": row["co-product"], "value-type": "reported",
                "formula": row["formula"], "region": "UK",
                "source-id": (row.get("source-original") or "").split(";")[0] or sid,
                "via-source-id": sid if row.get("source-original") else "",
                "source-file": "ukerc_2013_usable-energy-database.xlsx",
                "source-locator": row["reference"], "status": "draft", "note": row["note"]})
        for i, row in enumerate(read(RAW / f"{stem}_constraints.csv"), 1):
            if row["technology"] not in techs:
                continue
            ex = self.example_for(sid, row["technology"], nm)
            self.cons.append({
                "record-id": f"tc-{i:04d}", "example-id": ex["example-id"],
                "source-technology": row["technology"],
                "constraint": row["constraint"], "region": row["region"],
                "year": row["year"], "value": row["value"], "unit": row["unit"],
                "constraint-basis": row["constraint-basis"], "value-type": "reported",
                "source-id": (row.get("source-original") or "").split(";")[0] or sid,
                "via-source-id": sid if row.get("source-original") else "",
                "source-file": "ukerc_2013_usable-energy-database.xlsx",
                "source-locator": row["reference"], "status": "draft", "note": row["note"]})

    def example_for(self, sid, tech, nm, process=""):
        """The example a flow or constraint row belongs to. Those files carry
        no process column, so a technology listed under one process only is
        that example; one listed under several is keyed on its first."""
        if process:
            return self.example(sid, tech, process)
        procs = [p for (p, t) in nm if t == tech]
        return self.example(sid, tech, procs[0] if procs else "")

    def bataille(self):
        stem, sid = BATAILLE
        nm = self.nodes(stem, sid)
        for row in read(RAW / f"{stem}.csv") if nm else []:
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = row["parameter"], (row.get("value") or "").strip()
            if param in ("trl", "state-of-development", "year-available"):
                if val:
                    self.attr(ex, param, val)
                continue
            if not val:
                continue
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            cost = param.startswith(("capex", "opex"))
            if cost:
                ex["capacity-basis"] = ex["capacity-basis"] or (
                    "nameplate" if unit.endswith("/kW") else "annual-output")
                ex["capacity-unit"] = ex["capacity-unit"] or unit.split("/")[-1]
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="UK",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "collapsed-rows" if row.get("value-min") else "",
                         "value-type": "reported", "formula": "",
                         "cost-basis": ("" if not cost else "incremental"
                                        if UKTM_ADD_ON.search(note) else "installed"),
                         "capacity-basis": "product-output" if cost else "",
                         "currency": currency_year(unit),
                         "source-id": sid, "via-source-id": "", "via-locator": "",
                         "source-file": "bataille_2017_heavy-industry-database.xlsx",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "", "status": "review" if "REVIEW:" in note else "draft",
                         "note": note})

    def ipcc(self):
        stem, sid = IPCC
        nm = self.nodes(stem, sid)
        for row in read(RAW / f"{stem}.csv") if nm else []:
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = row["parameter"], (row.get("value") or "").strip()
            # an empty readiness or state cell is kept as an unquantified row,
            # like any other IPCC cell without a number
            if param == "trl" and val:
                self.attr(ex, param, val, scale="nasa-1-9")
                continue
            if param in ("state-of-development", "year-available") and val:
                self.attr(ex, param, val)
                continue
            unit = (row.get("unit") or "").strip()
            orig = [x for x in (row.get("source-original") or "").split(";") if x]
            # a row with no number is kept: IPCC rates options whose cost cell
            # holds a condition ("Cost of H2"), and the rating is the finding
            quantified = val or row.get("value-min") or row.get("value-max")
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region="global",
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "reported", "formula": "", "cost-basis": "",
                         "capacity-basis": "", "currency": currency_year(unit),
                         "source-id": orig[0] if orig else sid,
                         "via-source-id": sid if orig else "",
                         "via-locator": (row.get("reference") or "").strip() if orig else "",
                         "source-file": f"{stem.split('/')[-1]}.pdf",
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "medium",
                         "status": "draft" if quantified else "unquantified",
                         "note": (row.get("note") or "").strip()
                                 + (f"  Cited by IPCC alongside: {', '.join(orig[1:])}."
                                    if len(orig) > 1 else "")})

    def iea_guide(self):
        """Readiness levels only, on the IEA ETP scale (which runs to 11)."""
        stem, sid = IEA_GUIDE
        nm = self.nodes(stem, sid)
        for row in read(RAW / f"{stem}.csv") if nm else []:
            key = (row.get("process", ""), row["technology"])
            val = (row.get("value") or "").strip()
            if key not in nm or not val or row["parameter"] != "trl":
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            self.attr(ex, "trl", val, scale="iea-etp")
            note = (row.get("note") or "").strip()
            if note and not ex["description"]:
                ex["description"] = note.split(".")[0]

    def etsap_brief(self, stem, sid, region="global"):
        nm = self.nodes(stem, sid)
        if not nm:
            return
        base = stem.split("/")[-1]
        held = [p.name for p in (RAW / stem).parent.glob(base + ".*") if p.suffix != ".csv"]
        src_file = held[0] if held else base + ".pdf"
        for row in read(RAW / f"{stem}.csv"):
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            param, val = (row.get("parameter") or "").strip(), (row.get("value") or "").strip()
            if param in EXAMPLE_ATTRS:
                if val:
                    self.attr(ex, param, val)
                continue
            # a range with no central value is kept (EAF dust at 1-780 g/t)
            if not (val or row.get("value-min") or row.get("value-max") or row.get("formula")):
                continue
            unit = (row.get("unit") or "").strip()
            note = (row.get("note") or "").strip()
            m = re.search(r"COST BASIS:\s*([a-z-]+)", note)
            cap = re.search(r"CAPACITY BASIS:\s*([a-z-]+)", note)
            self.fact(ex, parameter=param, target=(row.get("target") or "").strip(),
                      unit=unit, value=val, region=region,
                      **{"value-min": (row.get("value-min") or "").strip(),
                         "value-max": (row.get("value-max") or "").strip(),
                         "uncertainty-type": "reported-range" if (row.get("value-min") or
                                                                  row.get("value-max")) else "",
                         "value-type": "derived" if row.get("formula") else "reported",
                         "formula": (row.get("formula") or "").strip(),
                         "cost-basis": m.group(1) if m else "",
                         "capacity-basis": cap.group(1) if cap else
                         "product-output" if param.startswith(("capex", "opex")) else "",
                         "currency": currency_year(unit),
                         "source-id": sid, "via-source-id": "",
                         "source-file": src_file,
                         "source-locator": (row.get("reference") or "").strip(),
                         "extraction-file": f"data/raw-data/{stem}.csv",
                         "confidence": "", "status": "draft", "note": note})
        fpath = RAW / f"{stem}_flows.csv"
        for row in read(fpath):
            key = (row.get("process", ""), row["technology"])
            if key not in nm:
                continue
            ex = self.example(sid, row["technology"], row.get("process", ""))
            self.flows.append({
                "record-id": f"tf-{len(self.flows) + 1:04d}", "example-id": ex["example-id"],
                "source-technology": row["technology"],
                "direction": row["direction"], "commodity": row["commodity"],
                "value": row["value"], "unit": row["unit"], "per-unit": row["per-unit"],
                "value-min": row["value-min"], "value-max": row["value-max"],
                "co-product": row["co-product"],
                "value-type": "derived" if row["formula"] else "reported",
                "formula": row["formula"], "region": region,
                "source-id": sid, "via-source-id": "", "source-file": src_file,
                "source-locator": row["reference"], "status": "draft", "note": row["note"]})


def load() -> Loader:
    L = Loader()
    for rel, sid in TEMPLATE_FILES:
        L.template_file(rel, sid)
    L.ukerc()
    L.bataille()
    L.ipcc()
    L.iea_guide()
    for stem, sid in ETSAP_BRIEFS:
        L.etsap_brief(stem, sid)
    for stem, sid, region in BRIEF_SHAPE:
        L.etsap_brief(stem, sid, region)
    return L
