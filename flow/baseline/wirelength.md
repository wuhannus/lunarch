# Routed Wire Length — baseline reference

Total routed metal length of the timing-closed **7.0 ns** `sky130hd/riscv32i`
layout, measured from `6_final.def` (Manhattan length of every routed segment,
summed per layer). Source of record: `wirelength.json`; regenerate with
`make_wirelength.py`.

## Totals

| Class | Total length | Vias | Notes |
|-------|-------------:|-----:|-------|
| **Signal** (`NETS`) | **274,231.4 µm (274.2 mm)** | 51,506 | 5,601 routed statements |
| **Power** (`SPECIALNETS`) | 77,520.1 µm (77.5 mm) | 5,954 | 2 nets (VPWR/VGND stripes) |
| **Combined** | **351,751.5 µm (351.8 mm)** | 57,460 | |

## Per-layer breakdown

| Layer | Signal (µm) | Power (µm) | Total (µm) |
|-------|------------:|-----------:|-----------:|
| li1 | 0.0 | — | 0.0 |
| met1 | 104,686.5 | 51,609.2 | 156,295.7 |
| met2 | 118,212.3 | 2,869.0 | 121,081.3 |
| met3 | 33,362.9 | 2,943.5 | 36,306.4 |
| met4 | 17,629.4 | 10,000.8 | 27,630.2 |
| met5 | 340.4 | 10,097.5 | 10,437.9 |
| **Total** | **274,231.4** | **77,520.1** | **351,751.5** |

Signal routing is almost entirely on **met1/met2** (81%); the upper layers
(met3–met5) are mostly the power grid and clock.

## Derived metrics

| Metric | Value |
|--------|------:|
| Die | 376.625 × 376.625 µm (141,846 µm²) |
| Signal wirelength density | **1.93 µm / µm²** |
| Signal wirelength per placed cell (5,520 cells) | **49.7 µm/cell** |
| Signal wirelength / std-cell area (73,594 µm²) | **3.73** |
| Signal vias per mm of wire | 188 /mm |

## Position vs timing

The timing paths are **cell-delay dominated** (< 0.02 ns wire per path, see
`../timing/riscv32i_worst10_path_details.xlsx`), consistent with this short
average interconnect — the design is not wire-limited.

> `li1` shows 0.0 µm because the router uses li1 only for pin/via landings here
> (single points), not for wire segments.
