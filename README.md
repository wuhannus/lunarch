# lunarch — Lunahan Architecture

**AI-assisted design of AI chips.** Open-source RISC-V cores from Python to GDS, purpose-built for the agentic AI era.

> ⚠️ **Project Status:** Under development by **Dr. Han Wu** + **DeepSeek V4 Pro**. Flow demonstration stage. Not silicon-proven.

> 🙏🙏🙏 ☕☕☕ 🌹🌹🌹 **Acknowledgments:** This work is conducted under the supervision of **Chief Scientist Dr. Liao Heng** (HUAWEI). The integration of the **pyCircuit** and **XiangShan** RISC-V open-source projects was proposed by **Huawei Fellow Du Wenhua**, whose vision of combining Python-native agile design with silicon-proven RISC-V microarchitecture inspired the lunarch methodology.

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

## Three Cores, One Methodology

| | **v1.0** Baseline | **v1.1** SRAM | **v2.0 "Orion"** Agentic |
|---|:---:|:---:|:---:|
| **Repo** | [lunahan_v1](https://github.com/wuhannus/lunahan_v1) | [lunahan_v1_sram](https://github.com/wuhannus/lunahan_v1_sram) | [lunahan_v2](https://github.com/wuhannus/lunahan_v2) |
| **Area** | 0.056 mm² | 0.020 mm² (−64%) | 0.176 mm² |
| **Power** | 0.95 mW | 0.94 mW | 3.50 mW |
| **Frequency** | 100 MHz (max 438) | 100 MHz (max 234) | 100 MHz (max 234) |
| **Cells** | 2,706 (1,224 DFFs) | 1,785 + 3 SRAM macros | 4,500 + SRAM |
| **ISA** | RV32IMC | RV32IMC | RV32IMC + 11 custom |
| **HW contexts** | 1 (single-thread) | 1 (single-thread) | **4 (banked register files, 1-cycle agent.switch)** |
| **Key Feature** | Full Python→GDS flow | SRAM proven equivalent | STU + KV-cache + agent SDK |
| **GDS** | ✓ | ✓ | ✓ |

---

## Architecture Comparison

```
v1.0 ─ Baseline                    v1.1 ─ SRAM                    v2.0 ─ Agentic AI
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────────┐
│ RV32IMC 5-stage│          │ RV32IMC + SRAM  │          │ RV32IMC + 11 ext    │
│ DFF caches     │          │ sky130 PDK SRAM │          │ 4 agent contexts    │
│ 4KB I$ + D$    │          │ ICache  SRAM    │          │ STU (256 MAC)       │
│ 32x32 RegFile  │          │ DCache  SRAM    │          │ KV-cache 128KB      │
│ BTB 64 entries │          │ RegFile SRAM    │          │ Trace 4×8KB         │
│                │          │                 │          │ Security PMP ×16    │
│ 0.056 mm²      │          │ 0.020 mm²       │          │ 0.176 mm²           │
└─────────────────┘          └─────────────────┘          └─────────────────────┘
```

---

## Unified Design Flow

All three cores share the same methodology:

| Phase | Tool | Output |
|-------|------|--------|
| 1. RTL Design | pyCircuit V5 Python DSL | Hardware described in Python |
| 2. MLIR Emission | pycircuit.emit | `.pyc` MLIR dialect IR |
| 3. Compilation | pycc (LLVM 19 + MLIR) | Verilog + C++ simulation |
| 4. Verification | Golden model + 10 checkers | ISA, pipeline, timing, protocol |
| 5. Physical Design | OpenROAD + sky130 PDK | GDSII, SPEF, STA, DRC, power |
| 6. Performance | Cycle-accurate profiler | IPC, CPI, cache, PPA correlation |

---

## Roadmap

| Phase | Timeline | Goal |
|-------|----------|------|
| **v1.x** ✓ | Done | Foundation validated: Python→GDS, DFF + SRAM |
| **v2.x** | Q3–Q4 2026 | Agentic ISA, hardware context switching, STU |
| **v3.x** | 2027 | NPU co-design: open-source NPU + RISC-V interface |
| **v4.x** | 2028 | Silicon: TinyTapeout/Efabless shuttle, open-source agentic AI SoC |

---

## Quick Start

```bash
git clone https://github.com/wuhannus/lunarch.git

# Explore v1 baseline
cd ../lunahan_v1 && python3 phys/scripts/physical_design.py

# Try the agentic v2 core
cd ../lunahan_v2 && python3 perf/profile_agent.py

# Run the Agent SDK
cd lunahan_v2/sw && python3 agent_sdk.py
```

---

## Links

- [Architecture Vision (v2 Orion)](https://github.com/wuhannus/lunahan_v2/blob/main/agentic_ai_vision.html)
- [v1 vs v1_sram Formal Equivalence](https://github.com/wuhannus/lunahan_v1_sram/blob/main/phys/results/sram_comparison.md)
- [v1 Verification Summary](https://github.com/wuhannus/lunahan_v1/blob/main/docs/verification_summary.md)
- [STCO Bottleneck Analysis](https://github.com/wuhannus/lunahan_v1/blob/main/STCO/bottleneck_analysis.md)

---

## Project Resources

> 📊 *Accumulated across all sessions. Last updated: 2026-06-14*

| Resource | Consumed | Detail |
|----------|----------|--------|
| 🤖 **LLM Tokens** | **~820K** | DeepSeek V4 Pro. 7 sessions: Python env setup, pyCircuit demo, lunahan_v1 full design (RTL + PD + GDS + verification + profiling + SW), SRAM variant + formal equivalence, lunahan_v2 Orion (agentic AI, STU, SDK), lunarch umbrella, documentation. |
| 💰 **API Cost** | **~¥1.2 / $0.16** | DeepSeek V4 Pro pricing (≈¥1.5/M blended tokens, output≈2× input). 820K tokens ≈ ¥1.2 RMB / $0.16 USD. |
| 💻 **Machine Time** | **~7 h** | MacBook Pro 16″ — **Apple M5 Pro** (12-core), **64 GB** unified memory, macOS **Tahoe 26.5.1**. LLM inference + Python execution (PD flow, GDS, STA, gate-sim, profiling, multi-agent demo). |
| 👨‍🔬 **Dr. Han Wu** | **~3 h** | Direction, review, corrections, strategic decisions. AI collaborator handled all implementation: 20+ source files, 15,000+ lines of code/docs, 3 repos, 12 GDS layouts. |

---

*June 2026 · Dr. Han Wu + DeepSeek V4 Pro · MIT License · Stats auto-updated per session*
