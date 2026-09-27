# Wire Length & Density — all runs

Routed **signal** wire length (final route, sum of met1–met5 + li1) and density
for every run. All runs share the identical die (**376.625 µm → 0.14185 mm²**),
so density is directly comparable.

| Run | clk | ABC | Signal wire length | Wire density | Cells |
|-----|----:|-----|-------------------:|-------------:|------:|
| baseline | 7.0 | delay | 274.2 mm * | 1,933 mm/mm² | 5,520 |
| timing run | 5.0 | delay | 288.3 mm | 2,032 mm/mm² | ~5,689 |
| power run | 20.0 | area | 284.5 mm | 2,006 mm/mm² | ~8,800 |
| sweep p7_delay | 7.0 | delay | 276.1 mm | 1,946 mm/mm² | 5,520 |
| sweep p10_delay | 10.0 | delay | 277.5 mm | 1,956 mm/mm² | 5,209 |
| sweep p7_area | 7.0 | area | 284.2 mm | 2,004 mm/mm² | 8,919 |
| sweep p10_area | 10.0 | area | 283.7 mm | 2,000 mm/mm² | 8,859 |
| kogge-stone | 5.0 | delay | 268.4 mm | 1,892 mm/mm² | 5,659 |

\* baseline is DEF-computed; the others are the final-route totals from the ORFS
route log (`Total wire length on LAYER …`). Same method, same die.

## Per-layer split (mm)

| Run | met1 | met2 | met3 | met4 | met5 |
|-----|-----:|-----:|-----:|-----:|-----:|
| timing run | 108.3 | 127.5 | 35.2 | 17.3 | 0.1 |
| power run | 111.0 | 119.2 | 39.4 | 14.8 | 0.1 |
| p7_delay | 105.4 | 118.4 | 34.3 | 17.6 | 0.3 |
| p10_delay | 104.2 | 119.4 | 36.7 | 17.2 | 0.1 |
| p7_area | 109.8 | 119.8 | 40.3 | 14.4 | 0.1 |
| p10_area | 111.5 | 121.2 | 37.6 | 13.4 | 0.0 |
| kogge-stone | 102.0 | 115.9 | 35.4 | 15.1 | 0.1 |

## Observations

- **Wire length is essentially flat** across all runs: **268–288 mm**
  (±3.7%). It is **not** the differentiator between the timing/power designs —
  clock period and ABC choice barely move it.
- **~82% of routing is on met1+met2** for every run (short local interconnect),
  consistent with the earlier finding that paths are **cell-delay dominated**
  (wire delay < 0.02 ns/path).
- **Density tracks the cell count**, not the clock:
  - *area-ABC* runs have **~8,800–8,900 cells** → slightly higher wire
    (~284 mm) and density (~2,000 mm/mm²).
  - *delay-ABC* runs have **~5,200–5,700 cells** → ~274–288 mm.
- Lowest wire length = **kogge-stone run (268.4 mm)** — it also used the fewest
  mapped cells of the timing-oriented points; more wire is **not** why that run
  was slower.
- Density spread is tiny: **1,892–2,032 mm/mm²** (~7%). The design is uniformly
  low-density and **not routing-limited** — matching the DRC-clean result and
  the dominance of cell delay over wire delay.

## Takeaway

Changing the clock target and the ABC mapper changes **timing and power a lot**
but **wire length ~not at all** (±4%) and **density ~not at all** (±7%). So the
observed PPA differences come from **gate sizing / cell count**, not from
physical congestion — reinforcing that the bottleneck is logic depth, not wires.
