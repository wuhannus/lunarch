# Optimization Runs — Timing vs Power (die-matched)

Two goal-directed re-runs of the `sky130hd/riscv32i` flow, compared against the
7.0 ns baseline. **All three use the identical die/core** pinned via
`DIE_AREA=0 0 376.625 376.625` / `CORE_AREA=1.38 2.72 375.36 375.36`
(the baseline floorplan), so only the synthesis/clock knobs differ.

Reports in `timing_diematch/` and `power_diematch/`.

| Metric | **Baseline** | **Run 1d — Timing** | **Run 2d — Power** |
|--------|-------------:|--------------------:|-------------------:|
| Goal | reference | 200 MHz, power free | lowest power, freq free |
| Die | 376.6 µm | **376.6 µm** | **376.6 µm** |
| Clock constraint | 7.0 ns (142.9 MHz) | **5.0 ns (200 MHz)** | **20.0 ns (50 MHz)** |
| Setup WNS | 0.00 ns | **−1.60 ns** ❌ | 0.00 ns ✅ |
| Setup TNS | 0.00 ns | **−752.82 ns** | 0.00 ns |
| Worst slack | +0.04 ns | −1.60 ns | +9.09 ns |
| Min reg→reg period | 6.76 ns | **6.52 ns** | 7.55 ns |
| **fmax (reg→reg)** | **147.9 MHz** | **153.4 MHz** | **132.5 MHz** |
| **Total power** | **19.7 mW** | **29.3 mW** | **6.54 mW** |
| — sequential | 7.91 mW | 11.0 mW | 2.74 mW |
| — combinational | 6.00 mW | 10.2 mW | 1.74 mW |
| — clock | 5.79 mW | 8.16 mW | 2.05 mW |

## Differences made

| Knob | Baseline | Run 1d (timing) | Run 2d (power) |
|------|----------|-----------------|----------------|
| `clk_period` (SDC) | 7.0 ns | **5.0 ns** | **20.0 ns** |
| `ABC_AREA` | 0 (delay) | 0 (delay) | **1 (area)** |
| `TNS_END_PERCENT` | default | **100** | default |
| Die/core | 376.6 µm | **same (pinned)** | **same (pinned)** |

**Run 1d (timing)** — period 5.0 ns, delay-oriented ABC, full TNS cleanup.
Die pinned to baseline (no extra whitespace this time).

**Run 2d (power)** — clock relaxed to 20 ns, ABC switched to **area-oriented**.

## Conclusions

1. **200 MHz is not reachable for this RTL.** Best delay-oriented result is
   **6.52 ns (153.4 MHz)**, only **+3.7%** over baseline, with WNS still
   **−1.60 ns** against 5.0 ns. The limiter is the single-cycle
   **regfile → ALU → regfile** loop (cell-delay dominated). 200 MHz needs an
   **RTL pipelining** change, not P&R tuning.
2. **Timing run traded power for almost no speed:** 19.7 → **29.3 mW (+49%)**
   for +5.5 MHz.
3. **Power run cut power by ~two-thirds:** 19.7 → **6.54 mW (−67%)**
   (seq −65%, comb −71%, clock −65%), at the cost of fmax 147.9 → **132.5 MHz
   (−10%)**.
4. **Die-matched result:** with the die pinned, the power run actually lands a
   *little faster* (132.5 vs 129.6 MHz) than the earlier larger-die run — smaller
   die ⇒ shorter wires — while power is essentially unchanged (6.54 vs 6.67 mW).
   The timing run is likewise ~unchanged (153.4 vs 153.6 MHz, 29.3 vs 29.6 mW).
   So the earlier conclusions hold after removing the area difference.
5. **Pareto front** (all at 376.6 µm die):

   ```
   fmax  153.4 MHz  <---- Baseline 147.9 MHz ---->  132.5 MHz
   power  29.3 mW           19.7 mW                  6.54 mW
   ```

6. **Recommendation:** if ≥130 MHz is acceptable, `ABC_AREA=1` + relaxed clock
   gives a ~3× power saving; if maximum speed is needed, the 7.0 ns baseline is
   already near the achievable optimum and further gains require a pipelined RTL.
