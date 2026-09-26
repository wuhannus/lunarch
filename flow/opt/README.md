# Optimization Runs — Timing vs Power

Two goal-directed re-runs of the `sky130hd/riscv32i` flow, compared against the
7.0 ns baseline. `6_finish.rpt` and the SDC for each run are in
`timing/` and `power/`.

| Metric | **Baseline** | **Run 1 — Timing** | **Run 2 — Power** |
|--------|-------------:|-------------------:|------------------:|
| Goal | reference | 200 MHz, power free | lowest power, freq free |
| Clock constraint | 7.0 ns (142.9 MHz) | **5.0 ns (200 MHz)** | **20.0 ns (50 MHz)** |
| Setup WNS | 0.00 ns | **−1.59 ns** ❌ | 0.00 ns ✅ |
| Setup TNS | 0.00 ns | **−610.13 ns** | 0.00 ns |
| Worst slack | +0.04 ns | −1.59 ns | +9.22 ns |
| Min reg→reg period | 6.76 ns | **6.51 ns** | 7.72 ns |
| **fmax (reg→reg)** | **147.9 MHz** | **153.6 MHz** | **129.6 MHz** |
| **Total power** | **19.7 mW** | **29.6 mW** | **6.67 mW** |
| — sequential | 7.91 mW | 11.0 mW | 2.74 mW |
| — combinational | 6.00 mW | 10.2 mW | 1.78 mW |
| — clock | 5.79 mW | 8.38 mW | 2.15 mW |

## Differences made

| Knob | Baseline | Run 1 (timing) | Run 2 (power) |
|------|----------|----------------|---------------|
| `clk_period` (SDC) | 7.0 ns | **5.0 ns** | **20.0 ns** |
| `ABC_AREA` (synthesis) | 0 (delay) | 0 (delay) | **1 (area)** |
| `CORE_UTILIZATION` | 45 | **35** | 40 |
| `PLACE_DENSITY_LB_ADDON` | 0.2 | **0.3** | 0.2 |
| `TNS_END_PERCENT` | default | **100** | default |
| `REMOVE_ABC_BUFFERS` | 1 | 1 | 1 |

**Run 1 (timing)** — lowered the period to 5.0 ns, reduced core utilization to
35% and raised the placement-density addon to 0.3 (more whitespace so the
resizer/CTS can size up the critical ALU loop), and forced full TNS cleanup. ABC
stayed delay-oriented.

**Run 2 (power)** — relaxed the clock to 20 ns (no timing pressure), switched
ABC to **area-oriented** (`ABC_AREA=1`) so the mapper picks smaller, lower-cap
gates, and left utilization near default.

## Conclusions

1. **200 MHz is not reachable for this RTL.** Even with the aggressive
   timing-oriented settings the best achievable reg→reg period is **6.51 ns
   (153.6 MHz)** — a mere **+3.9%** over baseline — while WNS is still **−1.59 ns**
   against 5.0 ns. The limiter is the **single-cycle register-file → ALU →
   register-file loop** (28 logic levels, cell-delay dominated). Reaching 200 MHz
   requires an **RTL/architecture change (pipelining)**, not P&R tuning.

2. **The timing run bought speed with power.** Upsizing to chase 5.0 ns pushed
   total power from 19.7 mW to **29.6 mW (+50%)** — sequential +39%, comb +70%,
   clock +45% — for only +6 MHz. Poor trade.

3. **The power run cut power by two-thirds.** `ABC_AREA=1` + a relaxed clock
   dropped total power to **6.67 mW (−66%)**: sequential −65%, comb −70%,
   clock −63%. The cost is fmax falling to **129.6 MHz (−12%)** and a ~10% larger
   die (413 µm vs 377 µm side, lower utilization).

4. **The two goals are strongly coupled** through gate sizing: the same loop that
   caps frequency also dominates dynamic power. There is no free lunch — the
   Pareto front between the two points below is steep:

   ```
   fmax  153.6 MHz  <---- Baseline 147.9 MHz ---->  129.6 MHz
   power  29.6 mW           19.7 mW                   6.67 mW
   ```

5. **Recommended settings** depend on the target: if 130 MHz is acceptable,
   `ABC_AREA=1` + relaxed clock gives a ~3× power saving; if maximum speed is
   required, the baseline (7.0 ns) is already near the achievable optimum, and
   further gains need a pipelined RTL rewrite.
