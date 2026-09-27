# Kogge-Stone Adder Experiment — does it make 5 ns reachable?

**Question:** replace the current adder structure on the critical paths with a
Kogge-Stone (parallel-prefix) adder and re-check the 5.0 ns (200 MHz) target.

**Answer: No.** The Kogge-Stone adder does **not** help — it makes timing
slightly *worse*, because the critical path is **not** the adder carry chain.

## What was changed

- Added `ks_adder.v` — a parameterised log-depth Kogge-Stone prefix adder.
- Rewrote the ALU add (`sum = a2 + b2 + alucont[2]`, 33-bit) to instantiate
  `ks_adder #(33)`.
- Rewrote `adder.v` (the two PC adders) to instantiate `ks_adder #(32)`.
- Re-ran the flow at **5.0 ns** with the baseline die (376.625 µm), delay ABC.

## Result vs the previous 5 ns run (no KS)

| | no-KS (`p5_delay`) | **KS adder** |
|---|---:|---:|
| clk constraint | 5.0 ns | 5.0 ns |
| Setup WNS | −1.60 ns | **−1.75 ns** (worse) |
| Setup TNS | −752.8 ns | **−1078.3 ns** (worse) |
| Min reg→reg period | 6.52 ns | **6.74 ns** |
| **fmax** | **153.4 MHz** | **148.4 MHz** (worse) |
| Power | 29.3 mW | 28.2 mW |
| Cells | ~5,689 | 5,659 |

Critical path (KS run): `dp.rf.rf[25][2]` → `dp.rf.rf[10][20]` — again a
**regfile → … → regfile** path (PG2), not an adder.

## Why it doesn't help

The PG2 critical path is dominated by the **register-file read multiplexer and
the ALU result-select logic**, not a ripple carry. Inspecting the path cells:

```
mux2_2 → a221o_1 → a22oi_1 → a31oi_1 → a22o_1 → a311oi_2 → buf×2 →
o21ai_0 → ha_1 → a21o_1 → a21oi_1 → o21bai_1 → … → a41oi_1 → a211oi_1 →
xnor2_1 → a22oi_1 → nand2_1 → buf_4
```

Only **one or two `ha_1` half-adders** appear — a single bit of the adder — so
even a perfect carry chain removes almost nothing. The depth is in the **4:1
read mux (`mux4_2`) + 1-of-N select AOI/OAI trees**, which a Kogge-Stone adder
cannot touch.

(Also note: the default ORFS flow already supplies a Kogge-Stone carry unit via
`-extra-map platforms/common/lcu_kogge_stone.v`, and ABC had already flattened
it away — so the adders were never the bottleneck.)

## Conclusion

- **5.0 ns / 200 MHz remains unreachable** with adder restructuring alone.
- The limiter is the **single-cycle regfile-read → mux/ALU-select → regfile-write
  loop** (28 logic levels), i.e. the architecture, not the adder topology.
- To push toward 200 MHz you must reduce that logic depth: **pipeline the core**,
  register the regfile read / ALU result, or reduce the ALU select tree — not
  change the carry-propagation scheme.

## Files

- `ks_5ns.rpt` / `ks_5ns.log` — the run's report and log.
- `run_ks.sh` — swap-in + run + restore script (RTL restored afterwards).
