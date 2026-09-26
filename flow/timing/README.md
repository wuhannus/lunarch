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

## Detailed Timing Reports & Excel Summaries

### 1. `riscv32i_timing_summary_full.xlsx` — full endpoint summary

| Sheet | Contents |
|-------|----------|
| **Worst 20 (detailed)** | start/end, report group, functional path group (PG1–PG8), launch-clock latency, data-path delay, logic levels, data arrival, capture-clock latency, clock skew, data required, slack/WNS |
| **All endpoints (setup)** | 1,152 rows — worst setup path per endpoint (start, end, group, functional group, slack) |
| **All endpoints (hold)** | 1,152 rows — worst hold path per endpoint |
| **Summary** | clock period/fmax, #endpoints, WNS/TNS, slack distribution, endpoint categories |
| **Clock Skew** | per-path launch vs capture clock latency and skew |
| **Notes** | field definitions |

Source: `6_finish_timing_full.rpt` (worst 5/group, `full_clock_expanded`) and
`6_finish_all_endpoints_summary.rpt` (worst path per endpoint). Regenerate
with `make_timing_excel.py`.

Baseline: setup endpoints = 1,152 (`dp.rf.rf` 1,024, `dp.pcreg.q` 32,
`aluout` 32, `writedata` 32, `pc` 32). Setup WNS **+0.0415 ns**
(`rf[11][2] → aluout[20]`), TNS 0, 0 violations; worst hold **+0.5849 ns**.

### 2. `riscv32i_worst10_path_details.xlsx` — per-cell / per-net delay baseline

One sheet per worst-5 SETUP path for **PG2 (ALU/write-back, group `clk`)** and
**PG8 (result-out, group `vclk_clk`)** — 10 sheets (`PG2-1..5`, `PG8-1..5`)
plus an `Index` and `Definitions` sheet. Each path sheet breaks the path into
its stages with **cell delay** and **wire (net) delay**:

| Column | Meaning |
|--------|---------|
| Stage (instance) | cell instance (output pin) on the path |
| Cell type | sky130 cell master |
| Cell delay (ns) | delay through that cell |
| Wire delay (ns) | interconnect (net RC) delay feeding that cell |
| Time (ns) | cumulative arrival time at that cell output |

Baseline totals (cell + wire):

| Path | Group | Levels | Cell delay | Wire delay | Slack |
|------|-------|-------:|-----------:|-----------:|------:|
| PG2-1..5 | clk | 28 | 6.0955 ns | 0.0191 ns | +0.2402…+0.2442 |
| PG8-1 | vclk_clk | 32 | 5.1832 ns | 0.0163 ns | +0.0415 |
| PG8-2 | vclk_clk | 27 | 5.1702 ns | 0.0183 ns | +0.0602 |
| PG8-3 | vclk_clk | 26 | 5.0645 ns | 0.0148 ns | +0.1694 |
| PG8-4 | vclk_clk | 24 | 5.0506 ns | 0.0091 ns | +0.1890 |
| PG8-5 | vclk_clk | 25 | 5.0364 ns | 0.0163 ns | +0.2008 |

**Cell delay dominates** (~99.7% of the path); wire delay is negligible
(<0.02 ns). Source: `6_finish_worst10_paths_detail.rpt`
(`report_checks -group_path_count 5 -fields {net input_pin capacitance slew fanout} -format full`).
Regenerate with `make_path_details.py`.
