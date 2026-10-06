# CIMS to-fix list

Defects and open questions in the CIMS model inputs
(`data_processing_calibration/cims/data/model_inputs/model/`) found while building
this database. This list is about the model's numbers and links. What the database
needs the hierarchy to add is in [hierarchy-change-requests.md](hierarchy-change-requests.md).

Node names are those of `data/harmonized/records/cims_hierarchy.csv`, the definitive
end-use list. The model inputs still use the older branch names, given in brackets
where they differ.

## Open

| # | Node | Issue | Evidence | Suggested fix | Raised |
| - | - | - | - | - | - |
| 1 | `natural-gas.product.transmission` requesting `natural-gas.product.supply.fugitive` | The request is in tCO2 (0.00017 per 1000 m3), but the fugitive node provides tCH4. Either the unit label is wrong or the coefficient is a CO2 figure feeding a methane service. | `natural_gas_*.csv`, all 13 provinces and territories, technologies `Transmission` and `Transmission Efficient` (Natural Gas.Production.Transmission) | Confirm what 0.00017 measures and restate it in tCH4 per 1000 m3. | 2026-10-02 |
| 2 | Whole tree, starting with natural gas | Sanity-check the chain of requests and provides down the tree: every service_request's unit should match the service_provide unit of the node it targets, and each unit should be the quantity the technologies there actually act on. Example: flaring provides tCO2 (the gas after it is burned), and point-venting "Flare Install" requests 2.29 tCO2 per tCH4. Should flaring instead be in tCH4 sent to the flare, with the CO2 (and the methane slip) as the flare technologies' emissions? Also: blowdowns and liquid unloading provide a nominal "unit" (Testing and Maintenance.*), while venting.controls provides 1000 m3 of gas. | `natural_gas_ab.csv`: Supply.Flaring provides tCO2; Supply.Venting.Point Venting, Flare Install requests Supply.Flaring 2.289953462 tCO2; Testing and Maintenance.Blowdowns and .Liquid Unloading provide unit | Script the unit check across all sectors; settle each node's service quantity; re-derive the coefficients that change. | 2026-10-02 |
| 3 | `natural-gas.product.supply.well-tests` | The database's `separator_reduced-emission-completion` (green completions) is placed here with a product of t CH4 avoided, like the other methane-control archetypes. The other archetypes on this node and on `supply.drilling` use m drilled or wells. Which unit this node provides, and whether completion flowback methane belongs here or under `supply.venting.other-point-venting`, is not settled. | `records/archetype-service.csv`; Natural Gas STAR reduced emission completions (epa_2006_001) | Confirm the service unit of well-tests and where completion venting is modelled; move the archetype if needed. | 2026-10-03 |
| 4 | Every `ccs` service and the hosts that request it (e.g. `iron-and-steel...blast-furnace` with capture) | CIMS's emissions_removal applies the capture technology's rate to the host's emissions as if all of them were sent to capture. The database now separates the two: the capture archetype carries its capture-rate (about 90% of the CO2 in the gas it treats) and the host with capture carries `share-to-capture`, the share of its CO2 sent there (blast furnace with stove flue-gas capture 38%: 0.376 t captured / (90% x 1.10 t); cement and lime about 100%). | `output/archetype-parameter.csv` share-to-capture (`pipeline/captureshare.py`); docs/decisions.md 2026-10-05 | Change emissions_removal so the removal is the capture rate (at the ccs node) times the host's service_request to the ccs node, with the service_request set from share-to-capture, rather than the capture rate applied to all the host's emissions. | 2026-10-05 |
