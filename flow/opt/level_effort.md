# Average Logic Levels & Logical Effort — p7_delay vs p7_area

Averaged over the **worst 264 timing paths** of each run (from
`paths/{p7_delay,p7_area}_allpaths.rpt`, `report_checks -group_path_count 200`).
Logical effort g per cell from the standard values (inv/buf = 1, nand_n=(n+2)/3,
nor_n=(2n+1)/3, AOI/OAI ≈ 2–3, xor/xnor ≈ 4, mux4 ≈ 3).

| Metric | **p7_delay** | **p7_area** |
|--------|-------------:|------------:|
| **Avg logic levels / path** | **21.47** | **24.70** |
| — min / max | 3 / 33 | 6 / 35 |
| **Avg logical effort / stage** | **1.96** | **1.68** |
| Avg logical effort / path (Σg) | 1.97 | 1.68 |
| Total path effort (levels × ḡ) | ≈ 42.3 | ≈ 41.5 |
| Cells sampled | 5,668 | 6,520 |

## Logical-effort distribution (share of stages)

| g | gate type | p7_delay | p7_area |
|---|-----------|---------:|--------:|
| 1.00 | inv / buf | 1,623 | 719 |
| 1.33 | **nand2** | 181 | **2,591** |
| 1.60–1.80 | a21o / a22o / o21a / o22a · **nand3** | 694 | 885 |
| 2.00 | aoi21 / oai21 / mux2 / ha | 1,516 | 1,767 |
| 2.30–2.33 | aoi22 / oai22 / nor3 | 285 | 4 |
| 2.70 | aoi211/221 / aoi31 / oai211 | 381 | 332 |
| 3.00 | aoi311 / oai311 / mux4 | 388 | 1 |
| 3.30 | aoi41 | 295 | 0 |
| 4.00 | xor2 / xnor2 | 305 | 221 |

(The area run is dominated by **g = 1.33 nand2 (2,591)** and **g = 1.67 nand3
(885)**; the delay run by high-effort **g = 2–4** AOI/OAI/xor/mux cells.)

## Interpretation

- **p7_area has MORE logic levels (24.7 vs 21.5) but LOWER effort per stage
  (1.68 vs 1.96).** The area map decomposes the same logic into a deeper chain
  of **low-effort nand2/nand3/inv** stages instead of fewer, high-effort
  AOI/OAI/mux/xor stages.
- The **total path effort is nearly equal (≈42 vs ≈41)**, but the area version
  spreads it over shallow, well-sizable stages — which the resizer can balance
  better → the faster netlist at the same clock.
- The delay map's stages are dominated by **g = 2–4** (AOI22, AOI311, AOI41, xor,
  mux4): fewer levels but each carries much more logical effort.
- So: **more levels, less effort each** (area) beats **fewer levels, more effort
  each** (delay) here — path delay tracks total effort, not level count alone.
