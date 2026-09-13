# Flow Resource Summary

Resource consumption for the open-source EDA toolchain flow, measured from the
opencode session database (`opencode.db`, session `GitHub lunarch connection`).

## Token Consumption

| Metric | Tokens |
|--------|-------:|
| Input | 2,993,693 |
| Output | 162,494 |
| Reasoning | 325,730 |
| **Total (input + output + reasoning)** | **3,598,282** |
| Cache reads | 232,025,216 |
| Cache writes | 0 |
| **Cost** | **$1.06** |

## Scope of Work (what the tokens bought)

- Set up WSL2 + Ubuntu 24.04 (diagnosed and fixed a Windows servicing deadlock)
- Built **Yosys 0.69** from source
- Built **OpenROAD** from source (matched to ORFS) with all dependencies
- Built **Magic 8.3.683** from source
- Installed **netgen**, **KLayout 0.28.16**, and the **sky130 PDK** (open_pdks)
- Built the full **ORFS `sky130hd/riscv32i`** RTL-to-GDS flow:
  - Synthesis -> Floorplan -> Place -> CTS -> Route -> Finish
  - **GDSII generated**
  - **DRC: 0 violations**
  - **LVS: Netlists match**

## Result

```
DRC : 0 violations
LVS : INFO : Congratulations! Netlists match.
```

Artifacts: `flow/orfs_sky130hd_riscv32i/` (`6_final.gds`, `6_final.def`,
`6_final.v`, `6_final.spef`, `6_drc.lyrdb`).
