# Baseline APR Results — sky130hd/riscv32i (`riscv`)

Reference point captured from the **timing-closed 7.0 ns run** (commit `dff10dd`).
All future changes (resizing, retiming, path-group optimization) are compared
against this baseline.

## Configuration

| | |
|---|---|
| Platform | `sky130hd` (`sky130_fd_sc_hd`) |
| Top module | `riscv` (single-cycle RV32I) |
| Clock | `clk`, period **7.0 ns → 142.86 MHz** |
| Flow | ORFS: synth → floorplan → place → CTS → route → finish; DRC/LVS via KLayout |

## Metrics

| Metric | Value |
|--------|-------|
| Setup **WNS** | **0.00 ns** |
| Setup **TNS** | **0.00 ns** |
| Worst slack | +0.04 ns |
| Min reg→reg period | 6.76 ns → **fmax 147.93 MHz** |
| Hold | MET |
| Design area | **73,594 µm²** (53% utilization) |
| Cells (final netlist) | **5,520** sky130 instances |
| — sequential | 1,024 `edfxtp_1` (regfile) + 32 `dfrtp_1` (PC + EPC) |
| Total power | **19.7 mW** (internal 13.2 + switching 6.54 + leakage ~0) |
| DRC | **0 violations** |
| LVS | **Netlists match** |
| LEC | proven (RTL≡synth, synth≡routed) |

## Power breakdown

| Group | Internal | Switching | Total | Share |
|-------|---------:|----------:|------:|------:|
| Sequential | 7.64 mW | 0.278 mW | 7.91 mW | 40.2% |
| Combinational | 2.34 mW | 3.66 mW | 6.00 mW | 30.5% |
| Clock | 3.18 mW | 2.61 mW | 5.79 mW | 29.4% |
| **Total** | 13.2 mW | 6.54 mW | **19.7 mW** | 100% |

## Critical path

| | |
|---|---|
| Path group | **PG2 — Execute (ALU write-back)** |
| Start | `dp.rf.rf[1][0]$_DFFE_PP_` |
| End | `dp.rf.rf[27][0]$_DFFE_PP_` |
| Delay | 6.3335 ns |
| Slack | +0.0415 ns |

At the tighter unrelaxed 6.0 ns constraint the same **PG2** path and a **PG8**
(`rf[1][0] → aluout[0]`) path violated — see `../analysis/path_groups.md`.

## Artifacts

- `6_finish.rpt` — post-route timing / power / area report.
- `../orfs_sky130hd_riscv32i/` — `6_final.gds/.def/.v/.spef`, `6_drc.lyrdb`, layout PNGs.
- `../timing/` — timing summary, `constraint_7ns.sdc`.
- `../analysis/` — `dataflow.md`, `path_groups.md`.
