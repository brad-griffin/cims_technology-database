# Deriving CAPEX and OPEX for CCS in Steelmaking

Working reference for backing out capital and operating cost parameters for carbon
capture applied to iron and steel production, starting from reported levelized cost
of capture ($/tCO2). Intended for use as CIMS technology parameters.

---

## 1. The core problem

A single reported $/tCO2 figure cannot uniquely identify CAPEX and OPEX — one
equation, multiple unknowns. The workable approach is to **compute variable costs
bottom-up and assign the residual to capital.**

Reported levelized cost of capture is almost always:

```
LCOC = (CRF x CAPEX + FOM) / M  +  VOM
```

where `M` = annual tonnes captured, `CRF = i(1+i)^n / ((1+i)^n - 1)`, and VOM covers
per-tonne energy, solvent, chemicals and waste disposal.

Parameterizing fixed O&M as a fraction of capital (`FOM = phi x CAPEX`) gives a
closed form:

```
CAPEX = (LCOC - VOM) x M / (CRF + phi)
```

Capital intensity is then `CAPEX / M`, in $ per tCO2-yr of capture capacity.
The whole exercise reduces to getting VOM, CRF and M right.

**Output should be a range, not a point estimate.** Solve across a grid — CRF from
0.065 to 0.12, VOM from a waste-heat case to a new-gas-boiler case — and report
implied capital intensity as a band.

---

## 2. Information required to invert

**Financial conventions.** Discount rate, lifetime, real vs nominal, and whether
the capital figure is overnight capital, total installed cost, or total capital
requirement including IDC and owner's costs. Largest single source of spread:
7%/25yr gives CRF ~0.086; 10%/20yr gives ~0.118.

**Boundary.** Check three things before anything else:

- Capture-only vs capture + compression vs full chain with T&S
- **Cost per tonne captured vs per tonne avoided** — these differ by 20–40% for
  post-combustion amine on steel because of the energy penalty. Conflating them
  corrupts everything downstream.
- Whether the figure is an incremental retrofit cost or includes reference-plant
  costs, and whether credits (45Q, CFR, OBPS/TIER) are already netted out.

**Energy and consumables** (to build VOM from below):

- Solvent regeneration heat: ~2.4–3.7 GJ/tCO2 for MEA; ~2.0–2.6 for advanced
  solvents (KS-21, CANSOLV)
- Compression: ~90–120 kWh/tCO2 to pipeline pressure, plus 20–40 kWh/tCO2
  auxiliaries
- Solvent makeup: ~1.5–3 kg MEA/tCO2, plus caustic, activated carbon, reclaimer
  waste
- Critically: whether regeneration heat comes from surplus BFG/waste heat
  (near-free) or a new dedicated boiler (a capital item that may or may not sit
  inside the reported number)

**Physical parameters** for `M`: crude steel output, CO2 intensity of the specific
stream, capture rate, capacity factor.

---

## 3. Discount rates — three distinct animals

Engineering-study annualization rates are normally a **weighted average cost of
capital**, not a borrowing rate:

```
WACC = (D/V) x r_d x (1-t) + (E/V) x r_e
```

Debt is the cheap, tax-shielded component; equity at 10–15% usually dominates the
blend. These are quoted **real**, not nominal — 8% real is roughly 10.5% nominal at
2.5% inflation.

Three rates land near 8% and are constantly conflated:

| Rate | What it is | Used for |
|---|---|---|
| Private WACC | A financing cost, partly borrowing | CRF in IEAGHG / NETL-style studies |
| Social discount rate | Return displaced elsewhere in the economy | TBS guidance: 8% with 3% and 10% sensitivities, via weighted social opportunity cost of capital. Federal policy requires the TBS opportunity cost of capital except where a social rate is more appropriate — impacts beyond 50 years, or proposals mainly affecting private consumption. The 50-year carve-out bites directly on CCS and CDR. |
| Behavioural hurdle rate | Reduced-form summary of payback requirements, perceived risk, option value, management attention — not a cost of capital in any sense | What CIMS estimates from revealed preference; typically 15–30% for industrial capital |

**Operating rule:** for the inversion, replicate the source study's CRF exactly,
whatever it is, even if you think it's wrong. You are undoing their arithmetic.
Apply the behavioural rate only afterwards, when the parameter enters the model.
Mixing the two steps double-counts a discount rate adjustment.

Consequence to state explicitly in any writeup: if a source used 8% and CIMS applies
15–25%, the in-model $/tCO2 will exceed the published figure. That is correct
behaviour, not an error.

---

## 4. Steel-specific complications

An aggregate "$/tCO2 for steel CCS" hides large dispersion. An integrated site has
many streams at very different CO2 partial pressures:

- Blast furnace gas ~20–25% CO2 (BF is ~70% of site emissions, ~22 vol%)
- Hot stove flue gas ~25%
- BOF gas ~14 vol%
- Combined COG+BFG+BOFG routed to CHP ~30 vol%
- On-site power plant ~9–12%
- Sinter plant ~5–8% and contaminated

Capture cost scales strongly with partial pressure, so plant-level averages conceal
a $40–120/t range across streams. Economically attractive retrofits typically reach
only 50–65% site capture.

**DRI-EAF is a different technology, not a variant.** A gas-based MIDREX shaft
already has a CO2 removal unit for process reasons, so the top-gas stream is
high-purity — you are mostly paying for dehydration and compression. $15–35/tCO2,
with a compression-electricity-heavy rather than capital-heavy cost split. Emirates
Steel's Al Reyadah (~800 ktCO2/yr, operating since 2016, ~US$122M capital) is the
best real anchor.

Determine which streams and which route a figure covers before inverting anything.

---

## 5. Benchmark sources for CCS costs

### Primary — free and disaggregated

**IEAGHG 2018-TR03, *Cost of CO2 Capture in the Industrial Sector: Cement and Iron
and Steel Industries*** (Garcia, Berghout, Herraiz). Free PDF at ieaghg.org. The
single most useful document — it performs the decomposition across ~29 steel cases,
reporting capital and operating costs as increments over a reference case, split
into ΔCapital / ΔFixed O&M / ΔEnergy / ΔMaterials.

Capital aggregation ladder (lets you translate between costing conventions):

```
Process Equipment Cost
  + 208% (supporting facilities + labour)   -> Bare Erected Cost
  + 8% of BEC (engineering services)        -> EPC Cost
  + 7.5-40% project contingency (AACE class)-> Total Plant Cost
  + 7% of TPC (owner's cost)                -> Total Overnight Cost
  + 10.75% of TOC (IDC + escalation)        -> Total Capital Requirement
```

Other parameters: scaling exponent 0.67; location material factors USA 0.94,
Australia 1.00, China 0.77; fixed O&M anchored at 1.5% of TPC/yr for property taxes
and insurance plus separately computed labour and maintenance; process contingencies
excluded (NOAK basis throughout, no FOAK premium).

Standardized assumptions: **8% real, 25-year life, 80% capacity factor, 110 bar
compression outlet** — so CRF = 0.0937. Plant basis 4 Mt/yr steel, 3.9 Mt/yr iron,
3.4–9.4 Mt CO2/yr emitted without capture.

Raw capital costs from underlying studies (Table 1), useful for triangulation:

| Study | Case | Capture | Capital |
|---|---|---|---|
| IEAGHG 2013a | MEA greenfield, BFHS+SGP | 90% | EUR 5,036M (2013, TCR) |
| IEAGHG 2013a | MEA greenfield, COP/BFHS/LKP/SGP | 90% | EUR 5,296M (2013, TCR) |
| IEAGHG 2013a | Oxyfuel TGRBF | 90% | EUR 4,877M (2013, TCR) |
| Tsupari et al. 2015 | MEA retrofit, PP+BFHS | 9–89% | EUR 69.8–234.1M (2012, TCR) |
| Tsupari et al. 2015 | Oxyfuel + VPSA | 74% | EUR 370M (2013, additional) |
| Ho et al. 2013 | MEA retrofit, BF+PP | 90% | $412M (2010) |
| Ho et al. 2013 | VPSA retrofit, BF+PP | 90% | $227M (2010) |
| Ho et al. 2013 | HIsarna MEA / VPSA | 90% | $502M / $350M (2010) |
| Ho et al. 2013 | COREX MEA / VPSA | 90% | $475M / $352M (2010) |
| NETL 2014 | MDEA retrofit, COP/BFHS/PP | 95% | $699M (2011) |

The gap between a EUR 5bn greenfield figure and a EUR 70M partial-capture retrofit is
the boundary problem in one line.

Standardized headline results — capture cost: traditional chemical absorption 16–21
$2016/tCO2, advanced solvents 7–16, VPSA 11–14, hybrid 23–66. Avoidance cost: 56–82,
52–80, 34–52, 65–135 respectively.

### Complement

**NETL, *Cost of Capturing CO2 from Industrial Sources*** (2022, rev. 2023). Free at
netl.doe.gov. Reports capital, fixed O&M, variable O&M and purchased power/gas
separately; steel treated as retrofit. Capital broken out for the COG/blast furnace
section and COG power plant section at both 90% and 99% capture, with owners' costs
itemized. Uses CANSOLV post-combustion. Ships with the **Industrial Sources Carbon
Capture Retrofit Database (CCRD)** — a tool allowing estimation with study or
user-supplied inputs, i.e. a sensitivity engine rather than a fixed point.

### DRI route

- **SEWGS in DRI** (*Int. J. Greenhouse Gas Control*, 2023) — compares conventional
  Midrex DRI-EAF against MEA post-combustion, MDEA pre-combustion and SEWGS, with
  levelized cost of HRC and cost of CO2 avoided plus gas/electricity sensitivities.
- **Weng et al. / MIT EPPA** (*IJGGC*, 2023) — coarser cross-check: DRI-EAF with CCS
  raised costs ~7% vs conventional steel, blue-H2 DRI-EAF ~18%, green ~79%.

---

## 6. Baseline (reference plant) cost sources

**Note first:** IEAGHG figures are absolute increments in $2016/t steel (roughly
30–120/t depending on configuration), not percentages. For the capture increment you
can **add rather than scale**, which avoids compounding baseline error into the
delta. A baseline is only needed if CIMS represents BF-BOF-with-CCS as a whole
technology competing on full lifecycle cost.

**Most internally consistent:** IEAGHG 2013/04, which defines the reference Western
European integrated mill the 2018 increments are measured against (4 Mt/yr steel,
coke ovens, sinter, BF, BOF, casting, rolling). Behind registration.

**Capital benchmarks — three independent sources converge:**

- Steelonthenet (database of ~1,350 projects since 2010): ~EUR 1,500/t annual
  capacity for integrated BF-BOF incl. casting and hot rolling, end-2025; EAF
  mini-mill EUR 500–700/t; DRI-EAF EUR 800–1,200/t
- Global Energy Monitor: US$1–1.5bn per Mt crude steel capacity
- IIT Bombay (India): $1,000–1,200/t annual liquid steel capacity; EAF-scrap ~40–55%
  of BF-BOF capex

Central range **$1,000–1,500/t annual capacity**. Most include casting and hot
rolling — check whether the CIMS technology is defined at crude steel or HRC.

**Operating cost:**

- **Steelonthenet BOF cost model** — free structured breakdown (iron ore, coal,
  energy, conversion) for a notional 3 Mt/yr integrated Japanese coastal plant with
  own coke and sinter, PCI blast furnace. **Caution:** assumes straight-line
  depreciation over 20 years and treats 25% of labour as fixed, with depreciation
  *inside* the per-tonne cost. Adding annualized capex separately double-counts.
- **Weng et al. (2023)** for all routes on one basis: BF-BOF ~$350–475/t crude steel,
  NG DRI-EAF ~$400–590 (IEA figures); their own estimates ~$560/t DRI-EAF, ~$600
  DRI-EAF+CCS, ~$670 blue-H2, ~$1,000 green. The $560→$600 step cross-checks any
  derived CCS delta.
- **DIW Berlin DP 2082**, *Revisiting Investment Costs for Green Steel* — free,
  capital-focused, cross-route.
- **Zhang et al., Nature (2025)**, least-cost steel decarbonization pathways —
  integrates two global plant-level datasets with forecast technology costs;
  extensive supplementary material. Best public substitute for commercial data.

**Commercial cost curves** (authoritative for plant-level opex): CRU, MEPS, Wood
Mackenzie, S&P Global, World Steel Dynamics.

**Canadian anchors:**

- ArcelorMittal Dofasco Hamilton: CAD$1.8bn for a DRI facility plus 2.4 Mt/yr EAF,
  reusing existing casting/rolling/finishing; construction complete 2026, transition
  complete 2028. Real, dated, domestic — but a partial-scope brownfield conversion,
  not comparable to a greenfield $/t figure.
- Transition Accelerator, *Hydrogen and the Decarbonization of Steel Production in
  Canada* — works the Hamilton case with delivered-energy costs in CAD.

---

## 7. Standing cautions

- **Capacity factor consistency.** A baseline at 90% utilization paired with a delta
  standardized at 80% misallocates the fixed-cost share between them.
- **FOAK vs NOAK.** IEAGHG 2018-TR03 is NOAK throughout with process contingencies
  excluded. If CIMS represents near-term adoption decisions, add a FOAK uplift or
  early-period costs will be systematically understated.
- **Escalation.** Use CEPCI or IHS UCCI for dated capital figures, never CPI.
- **Scale.** Apply a 0.6–0.8 exponent when moving between plant sizes; some
  components step-change rather than scale smoothly.
- **Cross-validation target.** If the IEAGHG-derived and NETL/CCRD-derived capital
  intensities land within ~30% of each other on $/tCO2-yr, the parameter is
  probably defensible.
