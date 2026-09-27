# Cell-Type Comparison — p7_delay vs p7_area (same 7 ns clock, same die)

From the OpenROAD `Cell type report` (post-finish) of each run's log.

| Cell class | **p7_delay** (`ABC_AREA=0`) | **p7_area** (`ABC_AREA=1`) | Δ count |
|------------|----------------------------:|---------------------------:|--------:|
| Multi-Input combinational cell | 3,458 | **6,404** | **+2,946** |
| Inverter | 123 | **843** | **+720** |
| Clock inverter | 68 | 63 | −5 |
| Clock buffer | 135 | 148 | +13 |
| Timing Repair Buffer | 680 | 405 | −275 |
| Sequential cell (FF) | 1,056 | 1,056 | 0 |
| Antenna cell | 2 | 3 | +1 |
| Tap cell | 1,876 | 1,876 | 0 |
| Fill cell | 11,652 | 12,904 | +1,252 |
| **Total instances** | **19,050** | **23,702** | **+4,652** |

## Area (µm²)

| Cell class | p7_delay | p7_area | Δ |
|------------|---------:|--------:|--:|
| Multi-Input combinational | 29,971.24 | 30,835.82 | +864.6 |
| Inverter | 461.69 | 3,166.79 | +2,705.1 |
| Clock inverter | 634.36 | 549.28 | −85.1 |
| Clock buffer | 2,867.75 | 2,980.36 | +112.6 |
| Timing Repair Buffer | 5,756.77 | 3,437.05 | −2,319.7 |
| Sequential (FF) | 31,550.26 | 31,550.26 | 0 |
| Antenna | 5.00 | 7.51 | +2.5 |
| Tap | 2,347.25 | 2,347.25 | 0 |
| Fill | 65,765.57 | 64,485.60 | −1,279.97 |
| **Total** | **139,359.91** | **139,359.91** | 0 |
| **Design area / util** | **73,594 µm² / 53 %** | **74,874 µm² / 54 %** | +1,280 / +1 pt |

> *Design area* counts the real (non-physical) cells only; the *Total* row includes
> fill/tap/decap whose area just pads the die to the same 139,359.91 µm².

## What the ABC_AREA knob actually changed

Only the **combinational mapping**:

- **~1.85× more combinational gates** (3,458 → 6,404) that are **smaller each**
  (29,971 → 30,836 µm² total, i.e. +3 % area for +85 % gates).
- **~7× more inverters** (123 → 843, +2.7 k µm²) — the area map leans on
  inversions/buffering for area-efficient AOI/OAI structures.
- **~40 % fewer timing-repair buffers** (680 → 405, −2.3 k µm²) — the
  physically smaller area-mapped cells needed less resizer fixing.
- Sequential (1,056 FFs), tap cells and clock-buffer count are essentially
  unchanged; only the fill count grows (+1,252) because the extra, smaller cells
  leave more gaps.

## Why this *improved* both speed and power

The area script (`strash; dch; map -B 0.9`) produced a **finer-granularity,
smaller-gate netlist** that the OpenROAD resizer + CTS could tune better than the
speed script's (`&syn2`/`&if -g -K 6`) coarse, pre-upsized mapping:

| | p7_delay | p7_area |
|---|---:|---:|
| fmax | 147.9 MHz | **155.4 MHz** |
| Power | 19.7 mW | **18.8 mW** |
| Repair buffers | 680 | 405 |

Net: at the **same 7 ns clock**, the "area" map won on **both** speed and power —
more, smaller cells that the P&R tools could shape, rather than a pre-sized
netlist that left less room to optimize.
