# Open-Source EDA Toolchain + ORFS Flow

This document captures the open-source RTL-to-GDS flow set up for the lunarch
project, verified end-to-end on the OpenROAD Flow Scripts (ORFS) `sky130hd/riscv32i`
reference design with **clean DRC and matching LVS**.

## Environment

| Component | Version | Location |
|-----------|---------|----------|
| WSL2 Ubuntu | 24.04.3 LTS | user `lunarch` |
| Yosys | 0.69+post (built from source) | `/usr/local/bin/yosys` |
| OpenROAD | built from source (matched to ORFS) | `/usr/local/bin/openroad` |
| Magic VLSI | 8.3.683 (built from source) | `/usr/local/bin/magic` |
| netgen | 1.5.133 | `/usr/local/bin/netgen` |
| KLayout | 0.28.16 | `/usr/bin/klayout` |
| sky130 PDK | open_pdks | `~/pdk-env/share/pdk/sky130A` |
| ORFS | master | `~/orfs-clean` |

## Tool Installation Notes

The critical lesson: **ORFS requires a version-matched OpenROAD and Yosys.**

- The Ubuntu-packaged Yosys 0.33 cannot parse the ORFS sky130 liberty
  (`Missing function on output GCLK of cell sky130_fd_sc_hd__dlclkp_1`).
  Build Yosys >= 0.69 from source.
- A 2024-era prebuilt OpenROAD lacks commands ORFS uses
  (`global_connect`, `utl::set_metrics_stage`, `eliminate_dead_logic`,
  `report_units_metric`). Build OpenROAD from source with its
  `etc/DependencyInstaller.sh -all`.

## Running the Flow

```bash
cd ~/orfs-clean/flow
export PATH=/usr/local/bin:/usr/bin:/bin
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
  OPENROAD_EXE=/usr/local/bin/openroad \
  YOSYS_EXE=/usr/local/bin/yosys \
  KLAYOUT_CMD=/usr/bin/klayout

# GDS -> DRC -> LVS
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
  OPENROAD_EXE=/usr/local/bin/openroad \
  YOSYS_EXE=/usr/local/bin/yosys \
  KLAYOUT_CMD=/usr/bin/klayout \
  drc lvs
```

## Verified Results

```
Synthesis (Yosys 0.69)      -> 1_synth.v
Floorplan / Place / CTS     -> 3_x / 4_x stages
Route                       -> 5_x stages
Finish                      -> 6_final.gds, 6_final.def, 6_final.spef, 6_final.v
DRC  (KLayout sky130hd.lydrc) -> 0 violations
LVS  (KLayout sky130hd.lylvs) -> INFO : Congratulations! Netlists match.
```

## Artifacts

Stored under `flow/orfs_sky130hd_riscv32i/`:

| File | Description |
|------|-------------|
| `6_final.gds` | Final GDSII layout |
| `6_final.def` | Routed DEF |
| `6_final.v` | Final gate-level netlist |
| `6_final.spef` | Parasitic extraction |
| `6_lvs.lvsdb` | LVS database (matched) |
| `6_drc.lyrdb` | DRC report (clean) |
