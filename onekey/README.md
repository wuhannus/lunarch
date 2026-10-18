# One-key installation — the AI-driven RTL→GDS flow (slide 7)

This directory turns the **10-step flow illustrated on slide 7** into a single
command. It runs the same stages the AI agent executed:

```
toolchain → 1_synth → 2_floorplan → 3_place → 4_cts → 5_route
          → 6_finish → sign-off (DRC + LVS) → optimize → simulate
```

## Quick start

On **WSL2 / Ubuntu 24.04** (x86-64, ≥ 30 GB free, sudo access):

```bash
curl -fsSL https://raw.githubusercontent.com/wuhannus/lunarch/main/onekey/install.sh | bash
```

That single command:

1. installs the system dependencies (git, cmake, build tools, KLayout, …),
2. clones and builds **OpenROAD Flow Scripts → OpenROAD + Yosys** (`--local`),
3. runs **synthesis → floorplan → place → CTS → route → finish** on the
   `sky130hd/riscv32i` reference core,
4. runs **DRC + LVS** sign-off,
5. copies `6_final.gds/.def/.v/.spef`, `6_finish.rpt`, `6_drc.lyrdb`,
   `6_lvs.lvsdb` to `~/lunarch-flow/artifacts/`.

The first run builds OpenROAD + Yosys, which takes roughly **30–90 min**
depending on the machine. Later runs skip the build.

## Options

```bash
./onekey/install.sh                 # install (if needed) + run the flow
./onekey/install.sh --flow-only     # only run the flow
./onekey/install.sh --skip-signoff  # skip DRC/LVS
./onekey/install.sh --clean         # clean previous results first
./onekey/install.sh -t 16           # 16 build threads
./onekey/install.sh -h              # help
```

Environment variables: `LUNARCH_HOME` (install root, default `~/lunarch-flow`),
`ORFS_DIR`, `JOBS`.

## Notes

- **PDK**: ORFS ships the `sky130hd` platform files (LEF/Liberty/GDS/DRC/LVS
  decks), so no separate PDK download is required for this flow.
- **Versions matter**: the installer builds OpenROAD and Yosys together via
  ORFS's `build_openroad.sh --local`, which keeps them version-matched.
- **KLayout** is used for DRC/LVS; install it with
  `sudo apt-get install klayout` if your distro does not provide it.
- **LEC (optional)**: gate-level equivalence uses Kepler Formal
  (`make … LEC_CHECK=1`). It is not part of the default one-key run; see
  `AGENTS.md` for the Kepler Formal build.
- **Optimize / simulate**: the sweep and pre/post-sim scripts live under
  `flow/` and `sim/` in this repository (slide-7 steps 9–10).
