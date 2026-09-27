# Hierarchy change requests

The one standing list of what the database asks of the CIMS hierarchy
(`data/harmonized/records/cims_hierarchy.csv`) and of the CIMS model inputs. Add a
request here when a record needs a node the hierarchy does not have. Remove it once
the hierarchy snapshot has it and the build passes.

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
| A node for ferroalloys and silicon metal under `metal-smelting` | Electric smelting of them has no CIMS node; only titanium slag does. | 2026-09-16 |
| Food and beverage process steps under `light-industrial` | CIMS has the aggregate demand only. Heat, refrigeration and drive are carried by the light-industrial services. | 2026-09-16 |
| Mine air heating as its own service, or a documented home | No CIMS node. The mining ventilation end use carries it for now. | 2026-09-16 |
| A synthetic-fuels node (coal-to-SNG, coal-to-liquids, gas-to-liquids) | `gasifier_coal-methanation`, `gasifier_coal-to-liquids` and `reactor_gas-to-liquids` are linked provisionally to gas processing and crude distillation. | 2026-09-23 |
| A coal-mine methane node under `coal-mining` | `process-improvement_coal-mine-methane-drainage` is linked to coal extraction for now; seam methane is a distinct emission. | 2026-09-23 |
| A urea (or nitrogen fertilizer) node under `chemicals` | `reactor_urea-synthesis` is linked provisionally to petrochemical intermediate production; urea consumes ammonia-plant CO2. | 2026-09-25 |
| A CO2 capture node for metal smelting (`metal-smelting.service.ccs.concentrated`/`.diffuse`) | ADDED to records/cims_hierarchy.csv 2026-09-26 at the modeller's request, ahead of CIMS: the capture units now serve it through the `<sector>.*.service.ccs.*` links, and the alumina and smelter capture hosts (`digester_bayer_ccs-diffuse`, `electrolysis-cell_prebaked-anode_ccs-diffuse`) stay on their host nodes. CIMS needs the same node. | 2026-09-26 |
| On-site power nodes beyond mining (cement, iron and steel, glass, refining, chemicals, pulp and paper, metal smelting) | Waste-heat power (`steam-turbine_waste-heat`) should be available wherever it is feasible, but `mining.service.on-site-power` is the only on-site power node; the archetype cannot be offered elsewhere until the nodes exist. | 2026-09-26 |
| On-site power for offshore platforms (`petroleum-crude`) | The other candidate beside `mining.service.on-site-power`. Oil-sands cogeneration is CHP and stays on steam. | 2026-09-16 |
| Confirm `industrial-minerals.product.ceramics` warrants its own branch in every province | Check against NRCan's NAICS 3271 industrial energy series. | 2026-09-18 |

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
