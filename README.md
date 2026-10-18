# lunarch — Lunahan Architecture

**AI-assisted design of AI chips.** Open-source RISC-V cores from Python to GDS, purpose-built for the agentic AI era.

> ⚠️ **Project Status:** This work is in progress under the guidance of **Dr. Han Wu**. All results are based on pre-layout and post-layout simulation only; silicon validation have not yet been completed. Please contact Dr. Han Wu for the latest progress before adopting or citing any results.

---

## Why lunarch?

**lunarch** = **Luna** (月/moon — constant renewal) + **Arch** (architecture).

| Letter | Meaning |
|--------|---------|
| **L** | Lunahan — creator's name |
| **U** | Unified — one methodology across generations |
| **N** | Next-gen — purpose-built for AI workloads |
| **A** | Agile — Python→GDS in days, not months |
| **R** | RISC-V — open ISA, no licensing fees |
| **C** | Chips — from architecture to physical layout |
| **H** | Hardware-software co-design |

---

## One-key installation — AI-driven RTL→GDS flow (slide 7)

Reproduce the 10-step flow illustrated on slide 7 with one command on
**WSL2 / Ubuntu 24.04**:

```bash
curl -fsSL https://raw.githubusercontent.com/wuhannus/lunarch/main/onekey/install.sh | bash
```

It installs the toolchain (OpenROAD + Yosys + KLayout), runs
**synthesis → floorplan → place → CTS → route → finish** on the
`sky130hd/riscv32i` core, runs **DRC + LVS**, and places the
GDS / DEF / netlist / SPEF + reports in `~/lunarch-flow/artifacts/`.

See [`onekey/README.md`](onekey/README.md) for options (`--flow-only`,
`--skip-signoff`, `--clean`, build threads).

