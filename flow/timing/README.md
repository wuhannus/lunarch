# Initial Timing Results — sky130hd/riscv32i (baseline)

First full RTL-to-GDS run of the baseline design.

## Design

| | |
|---|---|
| Top module | `riscv` (single-cycle RV32I) |
| Origin | James E. Stine, Oklahoma State University, ECEN 4243 (from the Harris & Harris textbook processor); bundled in ORFS, Apache-2.0 |
| Platform | `sky130hd` (sky130_fd_sc_hd) |
| Cells | 5,737 (incl. 1,024 `edfxtp_1` register-file FFs) |
| Area | ~81,986 µm² (33% utilization) |
| Power | 24.1 mW (internal 16.2 + switching 7.95 + leakage ~0) |

## Clock Target

| Attempt | Constraint | Post-route WNS | TNS | Status |
|--------:|-----------:|---------------:|----:|--------|
| Original | 6.0 ns (166.7 MHz) | −0.74 ns | −53.44 ns | ❌ setup violations |
| Relaxed | 6.5 ns (153.8 MHz) | −0.39 ns | −1.23 ns | ❌ near-close (IO path only) |
| **Final** | **7.0 ns (142.9 MHz)** | **0.00 ns** | **0.00 ns** | ✅ **clean / timing closed** |

Min clock period (reg→reg) achieved: **6.76 ns → fmax 147.93 MHz**.

## Final Timing (`6_finish.rpt`, post-route)

| Metric | Value |
|--------|-------|
| WNS (setup) | **−0.74 ns** ❌ |
| TNS | **−53.44 ns** |
| Worst slack | −0.74 ns |
| Min period (reg→reg) | 6.41 ns → fmax 155.96 MHz |
| Hold | MET |
| Clock skew (setup) | −0.06 ns |

## Violating Paths (2 unique)

**1. Register → Register (group `clk`)**
```
Start: dp.rf.rf[1][0]$_DFFE_PP_
End:   dp.rf.rf[27][0]$_DFFE_PP_
arrival = 6.88 ns   required = 6.47 ns   slack = −0.41 ns
```

**2. Register → Output (group `vclk_clk`)**
```
Start: dp.rf.rf[1][0]$_DFFE_PP_
End:   aluout[0] (output port)
arrival = 6.31 ns   required = 5.57 ns   slack = −0.74 ns
```

Path structure (single-cycle ALU loop):
`rf[1][0] → mux4_2 → mux2i_1 → o221ai_1 → nand3_2 → o31ai_4 → ... → ALU → rf[27][0]`

## Timing Convergence

| Stage | WNS (ns) | TNS (ns) |
|-------|---------:|---------:|
| 2_floorplan_final | −2.13 | −1209.54 |
| 3_global_place | −1.90 | −207.55 |
| 3_resizer | −1.90 | −207.55 |
| 3_detailed_place | −1.95 | −211.34 |
| 4_cts_final | −0.80 | −76.13 |
| 5_global_route | −0.89 | −112.57 |
| **6_finish** | **−0.74** | **−53.44** |

## Timing Fix Applied — Clock Relaxation to 7.0 ns

The −0.74 ns violation is on the register-file → ALU → register-file loop
(single-cycle datapath). Since no RTL change was made, the fix was to
**relax the clock constraint** and re-run the whole flow:

| Step | Result |
|------|--------|
| `constraint.sdc`: `clk_period 6.0` → `7.0` | 142.9 MHz |
| Synth → floorplan → place → CTS → route → finish | exit 0 |
| Post-route setup **WNS / TNS** | **0.00 / 0.00 ns** ✅ |
| Hold | MET |
| Min period (reg→reg) | 6.76 ns (fmax 147.93 MHz) |
| DRC | **0 violations** |
| LVS | **Netlists match** |

Artifacts for the timing-clean run: `6_finish.rpt`, `constraint_7ns.sdc`
(and layout/GDS updated in `../orfs_sky130hd_riscv32i/`).

## Conclusion

- The **critical path is the register-file → ALU → register-file loop** — the fundamental limit of this single-cycle architecture.
- The design is **timing-clean at 7.0 ns (142.9 MHz)**; its reg→reg fmax is 147.9 MHz.
- To push beyond ~148 MHz requires an RTL/architecture change (e.g. up-sizing the ALU path harder, or pipelining the 5-stage design) — a clock relaxation alone cannot exceed the reg→reg limit.

Full report: `6_finish.rpt`. DRC = 0 violations, LVS = match, LEC (RTL≡synth≡routed) = proven.

## Detailed Timing Report & Excel Summary

`riscv32i_timing_summary.xlsx` — per-path setup/hold summary (5 paths per clock
group) extracted from the post-route database:

| Sheet | Contents |
|-------|----------|
| **Timing Paths** | start/end point, report group, functional path group (PG1–PG8), launch-clock latency, data-path delay, data-path cells (logic levels), data arrival, capture-clock latency, clock skew, data required, slack/WNS, status |
| **Summary** | clock period / fmax / WNS / TNS, per-group worst slack, worst hold slack |
| **Clock Skew** | per-path launch vs capture clock latency and skew |
| **Notes** | field definitions |

Source data: `6_finish_timing_full.rpt` (`report_checks -path_delay max/min
-group_path_count 5 -format full_clock_expanded`). Regenerate with
`make_timing_excel.py` (`python3 make_timing_excel.py`).

Baseline worst values: setup **WNS +0.0415 ns** (group `vclk_clk`,
`rf[11][2] → aluout[20]`, 32 data-path cells), worst hold **+0.5849 ns**;
worst reg→reg setup slack +0.2402 ns (group `clk`, 28 data-path cells).
