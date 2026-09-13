# AGENTS.md — Verilog-to-GDS Flow (lunarch)

This document describes the **complete open-source RTL-to-GDS flow** used in this
repository, written so that an autonomous agent can reproduce it end-to-end.

## Design Under Test

The flow was verified on the **`riscv32i`** design bundled with OpenROAD Flow
Scripts (`flow/designs/src/riscv32i/`): a simple **RV32I** core created for an
Oregon State University undergraduate course (July 2019), Apache-2.0 licensed
(the classic Harris & Harris *Digital Design and Computer Architecture* processor).
Top module: `riscv`.

> Note: the `lunahan_v1`/`lunahan_v2` cores are pyCircuit (Python) designs and
> require the pyCircuit→MLIR→Verilog toolchain; this flow targets the
> synthesizable Verilog `riscv32i` reference core.

## Toolchain

| Tool | Version | How installed |
|------|---------|---------------|
| WSL2 Ubuntu | 24.04.3 LTS | Windows feature + Store Ubuntu |
| Yosys | 0.69+post | built from source (Release tarball, CMake) |
| OpenROAD | built from source, matched to ORFS | `etc/DependencyInstaller.sh -all` then CMake |
| Magic | 8.3.683 | built from source |
| netgen | 1.5.133 | `apt install netgen-lvs` |
| KLayout | 0.28.16 | `apt install klayout` |
| Kepler Formal | built from source | cloned `keplertech/kepler-formal` + CMake |
| sky130 PDK | open_pdks | conda (`litex-hub/open_pdks.sky130a`) |
| ORFS | master | `OpenROAD-flow-scripts` |

Key lesson: **ORFS needs a version-matched OpenROAD and Yosys.**
- Ubuntu Yosys 0.33 fails on the ORFS sky130 liberty
  (`Missing function on output GCLK of cell sky130_fd_sc_hd__dlclkp_1`).
- A 2024 prebuilt OpenROAD lacks `global_connect`, `utl::set_metrics_stage`,
  `eliminate_dead_logic`, `report_units_metric`. Build OpenROAD from source.

## Flow (commands)

```bash
cd ~/orfs-clean/flow
export PATH=/usr/local/bin:/usr/bin:/bin

# 1. Synthesis -> Floorplan -> Place -> CTS -> Route -> Finish (GDS)
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
  OPENROAD_EXE=/usr/local/bin/openroad \
  YOSYS_EXE=/usr/local/bin/yosys \
  KLAYOUT_CMD=/usr/bin/klayout

# 2. GDS -> DRC -> LVS
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
  OPENROAD_EXE=/usr/local/bin/openroad \
  YOSYS_EXE=/usr/local/bin/yosys \
  KLAYOUT_CMD=/usr/bin/klayout \
  drc lvs
```

### LEC (logical equivalence)

Kepler Formal is a **gate-level** LEC engine (it cannot parse RTL). ORFS's
`LEC_CHECK=1` compares the *synthesized* netlist (`1_synth_lec.v`) against the
*final routed* netlist (`6_final_lec.v`):

```bash
export KEPLER_FORMAL_EXE=~/orfs-clean/tools/install/kepler-formal/bin/kepler-formal
export LD_LIBRARY_PATH=~/orfs-clean/tools/install/kepler-formal/lib
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
  OPENROAD_EXE=/usr/local/bin/openroad YOSYS_EXE=/usr/local/bin/yosys \
  KLAYOUT_CMD=/usr/bin/klayout LEC_CHECK=1
```

The **RTL ≡ synthesized netlist** check uses **Yosys** `equiv_*`
(see `flow/lec/rtl_equiv.ys`): synthesize the RTL with the sky130 liberty as
gold, read `1_synth_lec.v` as revised, then `equiv_make/equiv_simple/equiv_induct/equiv_status`.

## Verification Results

| Check | Tool | Result |
|-------|------|--------|
| **RTL ≡ synthesized netlist** | Yosys `equiv_status` | ✅ **Equivalence successfully proven!** |
| **Synthesized ≡ final routed netlist** | Kepler Formal (`LEC_CHECK=1`) | ✅ **Global output passed lec test** |
| **DRC** | KLayout (`sky130hd.lydrc`) | ✅ **0 violations** |
| **LVS** | KLayout (`sky130hd.lylvs`) | ✅ **Netlists match** |

## Artifacts

- `flow/orfs_sky130hd_riscv32i/` — `6_final.gds`, `6_final.def`, `6_final.v`,
  `6_final.spef`, `6_drc.lyrdb`, layout PNGs
- `flow/lec/` — `1_synth_lec.v`, `6_final_lec.v`, `6_final_lec_check.log`,
  `rtl_equiv.ys`, `rtl_equiv2.log`

## Reproducibility Notes for Agents

1. Install/build the matched toolchain (see above). Build Yosys ≥ 0.69 and
   OpenROAD from source; use `--recurse-submodules` (git works when GitHub is
   reachable; use a proxy/mirror otherwise).
2. Kepler Formal needs `libtbb-dev` and `capnproto`/`libcapnp-dev`, and its
   submodules (`naja`, `slang`, `cadical`, `glucose`, `kissat`, `yaml-cpp`).
   Set `LD_LIBRARY_PATH` to its `lib/` at runtime.
3. `SEC_CHECK=1` (sequential equivalence, PDR) can hang on a full core — it is
   optional; keep it off for routine sign-off.
4. Always run `drc` and `lvs` targets after the main flow (they are not part of
   the default `all` target).
```
