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

## Cell-area density (cell area / die area)

Die area = **141,846 µm²** (376.625 µm) for every run, so density = Σ(std-cell
area) / 141,846 µm².

| Run | clk | ABC | Cell area (µm²) | **Cell area / die** |
|-----|----:|-----|----------------:|--------------------:|
| baseline (= p7_delay) | 7.0 | delay | 73,594 | **51.9 %** |
| timing run | 5.0 | delay | 78,144 | **55.1 %** |
| power run | 20.0 | area | 74,334 | **52.4 %** |
| sweep p10_delay | 10.0 | delay | 70,730 | **49.9 %** |
| sweep p7_area | 7.0 | area | 74,874 | **52.8 %** |
| sweep p10_area | 10.0 | area | 74,645 | **52.6 %** |
| kogge-stone | 5.0 | delay | 75,942 | **53.5 %** |

(ORFS reports utilization ~1% higher — 53% baseline — because its "Design area"
uses the padded/core area convention; the column above is the strict
cell-area/die-area ratio you asked for.)

### Density observations

- Cell-area density is remarkably **flat: 49.9 – 55.1 %** (a ~5-point spread).
- The **timing run is the densest (55.1 %)** — it up-sizes gates the hardest to
  chase 5 ns (largest cell area of all runs, 78,144 µm²), which is also why it
  burns the most power (29.3 mW).
- The **relaxed/faster-clocked delay runs are the least dense** (p10_delay
  49.9 %) — less resizing.
- Area-ABC runs sit in the middle (~52.6 %): the mapper picks smaller cells but
  the flow still sizes for the (loose) clock.
- With the die fixed, density is essentially **a proxy for how hard the resizer
  worked**, not for the mapper.

## Takeaway

Across every run the clock target and ABC objective change **timing and power a
lot** but leave the physical design nearly constant:

- **Signal wire length: 268–288 mm (±4 %)**
- **Cell-area density: 49.9–55.1 % (±2.6 points)**

So the PPA differences come from **gate sizing / logic depth**, not from wires
or congestion. The die is ~half-full in every case, DRC is clean, and
wire delay < 0.02 ns/path — reinforcing that the limiter is the single-cycle
logic depth, not physical density.
