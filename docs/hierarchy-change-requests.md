# Hierarchy change requests

The one standing list of what the database asks of the CIMS hierarchy
(`data/harmonized/records/cims_hierarchy.csv`) and of the CIMS model inputs. Add a
request here when a record needs a node the hierarchy does not have. Remove it once
the hierarchy snapshot has it and the build passes.

Defects in the CIMS model inputs themselves (wrong units, broken request chains) are listed in
[cims-to-fix.md](cims-to-fix.md).

The harmonization proposal of 2026-09-16 to 09-22 is applied to the snapshot
(`archive/decisions/2026-09-16_cims-hierarchy-harmonization.md`, revision 6). That
includes every node requested so far:

- `iron-and-steel.service.coke`, and `hot-metal` and `direct-reduced-iron`;
- `direct-air-capture.product.co2-removal`;
- `mining.service.on-site-power`;
- `petroleum-crude.product.transmission`;
- `petroleum-crude.service.produced-water`;
- `pulp-and-paper.service.effluent-treatment`;
- `industrial-minerals.product.ceramics.dryer` and `product.gypsum`;
- `chemicals.product.nitric-acid`;
- `biofuels.service.ccs.concentrated`, for fermentation CO2;
- the shared `general-services/industrial/` data folders for HVAC and lighting (G1).

## Open: hierarchy

| Request | Why | Raised |
| - | - | - |
| Lighting nodes (`<sector>.*.service.lighting`): service unit lumen-hours (Mlm-h) instead of GJ, and each split into general lighting and high-bay lighting | The lighting archetypes deliver Mlm-h (ruling 2026-10-14) so that a service request stays the same whichever lamp meets it; end uses request general or high-bay light (light industrial by end-use type). General: lighting_fluorescent-t12, -t8, lighting_led; high bay: lighting_hid, lighting_fluorescent-high-bay, lighting_led-high-bay; lighting_led-controls in both. Base-year requests: lighting electricity x stock efficacy / output. | 2026-10-14 |
| A node for ferroalloys and silicon metal under `metal-smelting` | Electric smelting of them has no CIMS node; only titanium slag does. | 2026-09-16 |
| Food and beverage process steps under `light-industrial` | CIMS has the aggregate demand only. Heat, refrigeration and drive are carried by the light-industrial services. | 2026-09-16 |
| Mine air heating as its own service, or a documented home | No CIMS node. The mining ventilation end use carries it for now. | 2026-09-16 |
| A synthetic-fuels node (coal-to-SNG, coal-to-liquids, gas-to-liquids): ADDED 2026-10-09 as `petroleum-refining.product.synthetic-fuels` at the modeller's request, ahead of CIMS | `gasifier_coal-to-liquids` and `reactor_gas-to-liquids` are linked provisionally to crude distillation. `gasifier_coal-methanation` was taken off the hierarchy 2026-09-30 (no connection). | 2026-09-23 |
| A coal-mine methane node under `coal-mining`: ADDED 2026-10-22 as `coal-mining.product.raw-product.mine-methane` (node split), ahead of CIMS | Drainage, the VAM oxidiser and no-abatement now sit there; coal extraction requests it. | 2026-09-23 |
| Urea and fertilizer nodes under `chemicals` (`chemicals.product.urea`, `chemicals.product.fertilizer`) | ADDED to records/cims_hierarchy.csv 2026-09-30 at the modeller's request, ahead of CIMS. `reactor_urea-synthesis` serves `urea` (it consumes ammonia-plant CO2); `fertilizer` holds the other fertilizers (ammonium nitrate, UAN, ammonium phosphates and sulphate) and no archetype serves it yet. CIMS needs the same nodes. | 2026-09-25 |
| A fluid catalytic cracking node under `petroleum-refining` | The three FCC archetypes sit on `cracked-gas-oil.hydrocracking`, the nearest catalytic gas-oil conversion (2026-09-30). | 2026-09-30 |
| A CO2 capture node for metal smelting (`metal-smelting.service.ccs.concentrated`/`.diffuse`) | ADDED to records/cims_hierarchy.csv 2026-09-26 at the modeller's request, ahead of CIMS: the capture units now serve it through the `<sector>.*.service.ccs.*` links, and the alumina and smelter capture hosts (`digester_bayer_ccs-diffuse`, `electrolysis-cell_prebaked-anode_ccs-diffuse`) stay on their host nodes. CIMS needs the same node. | 2026-09-26 |
| On-site power nodes beyond mining (cement, iron and steel, glass, refining, chemicals, pulp and paper, metal smelting) | Waste-heat power (`steam-turbine_waste-heat`) should be available wherever it is feasible, but `mining.service.on-site-power` is the only on-site power node; the archetype cannot be offered elsewhere until the nodes exist. | 2026-09-26 |
| On-site power for offshore platforms (`petroleum-crude`) | The other candidate beside `mining.service.on-site-power`. Oil-sands cogeneration is CHP and stays on steam. | 2026-09-16 |
| Oil sands tailings: ADDED 2026-10-09 as `petroleum-crude.service.tailings-disposal`, ahead of CIMS | `separator_dry-stack-tailings` serves it per t tailings (it also serves the mining tailings nodes). | 2026-10-09 |
| A mine-water treatment node (coal and metal mining) | `separator_mine-water-treatment` is per m3 of water and was taken off tailings disposal (2026-10-09); it has no node. | 2026-10-09 |
| A mine ventilation node under `mining` (metal mines) | `fan_mine-ventilation` was taken off the fans node (2026-10-09); only coal mining has a ventilation node. | 2026-10-09 |
| Check `chemicals.product.petrochemicals.intermediate-production` | A catch-all node: distillation, depolymerization, ethylene oxide and PDH make different products, so costs per t are not comparable across its technologies. | 2026-10-09 |
| A sulphur-recovery basis | `gas-treatment-unit_sulphur-recovery` is per t sulphur on nodes that provide m3 of gas or of RPP; converting needs the H2S content per m3, which no example gives. | 2026-10-09 |
| `natural-gas.product.supply.formation-co2` provides t CO2 | Its amine-sweetening archetypes are per m3 of gas processed; converting needs the CO2 content per m3. | 2026-10-09 |
| `natural-gas.product.transmission` and `.distribution` provide 1000 m3 | `turboexpander_pressure-let-down` produces electricity (its primary product); in CIMS it would be a negative electricity request on a let-down step rather than a provider of gas transport. | 2026-10-09 |
| Light industrial | Products are in M$ of GDP; the heat-node and food-node unit changes from the 2026-10-09 review are deferred (modeller). | 2026-10-09 |
| Confirm `industrial-minerals.product.ceramics` warrants its own branch in every province | Check against NRCan's NAICS 3271 industrial energy series. | 2026-09-18 |
| A calcination sub-node under the alumina node (`metal-smelting.product.aluminum.primary-aluminum.alumina.calcination`), with the digester narrowed to digestion and precipitation | `digester_bayer` holds the whole Bayer refinery per t alumina, calcination included (NM003, 2026-10-13), while `calciner_gas-suspension`, `calciner_gas-suspension_ccs-diffuse`, `calciner_electric` and `calciner_hydrogen-fired` sit on the same node; a calciner cannot make alumina from bauxite, so it needs its own service (user 2026-10-14) | 2026-10-14 |

## Applied ahead of CIMS, 2026-10-22 and 23 (node split and petrochemicals)

These are in `records/cims_hierarchy.csv` at the modeller's request (one competition per node: alternatives,
not steps). CIMS needs the same nodes, and the parent nodes need techs that request the new services. The full
log is `docs/reviews/node-split-review_2026-10-22.csv`; the summary is in the project note node-split-2026-10-22.

| Change | Nodes |
| - | - |
| CO2 transport split from storage | `<root>.transmission.co2-pipeline-and-storage.<route>.pipeline` and `.storage` (7 routes) |
| N2O abatement and distillation as chemical services | `chemicals.service.n2o-abatement`, `chemicals.service.distillation` |
| Petrochemicals regrouped for Canada (renamed) | `petrochemicals.olefins` (was steam-cracking; now with PDH), `.aromatics` (was btx-reforming), `.polymers` (was all-polymerization), `.derivatives` (was intermediate-production) |
| Cement binder split from grinding | `industrial-minerals.product.cement.binder` |
| Steel finishing steps | `continuous-cast.annealing-and-coating.annealing` and `.coating`; `continuous-cast.pickling` |
| Alumina steps | `alumina.digestion`, `alumina.calcination` |
| Converting split from smelting | `copper.pyrometallurgy.converting`, `nickel.pyrometallurgy.converting` |
| Gas processing steps (acid gas removal is `formation-co2`) | `processing.dehydration`, `.sulphur-recovery`, `.ngl-recovery` |
| Well completion (frac fleets, per GJ of hydraulic work) | `natural-gas.product.supply.completion`, `petroleum-crude.product.completion` |
| Production services requested by the extraction nodes | `natural-gas.service.artificial-lift` and `.treating`; `petroleum-crude.service.artificial-lift` and `.treating` |
| Oil sands mining steps | `bitumen.mining.extraction`, `.froth-treatment`; `bitumen.upgrading.primary`, `.secondary` |
| Pulp mill effluent steps | `effluent-treatment.primary`, `.secondary` |
| Light-industrial heat by operation (GJ of process heat) | `light-industrial.service.heat.drying`, `.process-heating`, `.cleaning`, `.baking-frying-roasting`, `.forming-pressing`, `.metal-melting`, `.heat-treatment` |
| Solid biofuels | `biofuels.product.solid-biofuel` |
| Coal-mine methane | `coal-mining.product.raw-product.mine-methane` |
| HVAC nodes renamed (2026-10-23), every sector including commercial | `service.hvac.space-heating` -> `service.hvac.heating`, `service.hvac.space-cooling` -> `service.hvac.cooling` (commercial `space-heating_cold` and `_marine` -> `heating_cold` and `heating_marine`) |
| Ammonia and methanol as separate products (2026-10-23) | `chemicals.product.ammonia-methanol` removed; `.ammonia` and `.methanol` -> `chemicals.product.ammonia` and `chemicals.product.methanol` |

## Open: CIMS model inputs (for the comparison stage)

| Item | Detail |
| - | - |
| `industrial-minerals.service.kiln-heat` | Most lime kilns request their fuel directly rather than this service. Revisit the service requests when the sector is reviewed. |
| CCS cost sets | `service.ccs.concentrated` and `.diffuse` need their own cost sets. CIMS priced one CCS service per sector. |
| Magnesium SF6 | The casting SF6 factors are in the Alberta and Ontario files only. Quebec, British Columbia and Manitoba carry demand with no factor. |
| Titanium slag | `metal-smelting.product.titanium-slag` has no demand series. |

## Nodes no archetype serves

The build lists these in `data/harmonized/output/mapping-review.md`, under
*Hierarchy nodes no archetype serves*. A node there needs either an archetype link
in `records/archetype-service.csv` or a request here to remove it.
