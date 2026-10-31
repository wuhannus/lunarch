# Open-Source NPU Architecture & Applications

A survey of open-source neural-processing-unit (NPU) hardware, how the
architectures differ, where they are used, and a concrete **small INT8 design
that fits the lunarch sky130 RTL→GDS flow**.

## 1. What “open-source NPU” means

A usable open NPU has three layers — most projects ship only some of them:

| Layer | What it is | Examples |
|-------|------------|----------|
| **RTL** | Synthesizable accelerator hardware | NVDLA, Gemmini, VTA, PULP |
| **Compiler / runtime** | Graph → tiled ISA / DMA schedule | TVM/VTA, ONNX-Runtime-RISC-V (Gemmini), TFLite (Tensil) |
| **Models / simulators** | C-model, cycle-accurate sim, perf model | NVDLA C-model, SCALE-Sim, Timely |

An RTL-only project is a demo; the **compiler** is what makes an NPU
deployable.

## 2. Landscape

| Project | Origin | HDL / flow | Architecture | Dataflow | Precision | Coupling | Best for |
|---------|--------|------------|--------------|----------|-----------|----------|----------|
| **NVDLA** | NVIDIA | Verilog + `tmake` | convolution core + SDP/CDP + BDMA; `nvdlav1` fixed at 2048×INT8 (or 1024×16-bit) | pipelined engines | INT8 / INT16 / FP16 | AXI + CSB | full edge-inference datapath reference |
| **Gemmini** | UC Berkeley | Chisel → Verilog (Chipyard) | 2-level systolic array + scratchpad + accumulator + DMA | **output- or weight-stationary** (runtime-selectable) | INT8 (configurable to FP) | **RoCC** on Rocket/BOOM | architecture research, RISC-V SoC integration |
| **VTA** | Apache TVM | Verilog | GEMM core + SRAM + RISC-V control | blocked GEMM | INT8 | RISC-V + TVM | compiler/hardware co-design |
| **PULP / PULP-NN** | ETH Zürich / Uni Bologna | SystemVerilog (RI5CY/RISCY) | RISC-V + SIMD vector extensions | SIMD MAC | INT8 / INT16 | tightly coupled | ultra-low-power TinyML |
| **CFU Playground** | Google | Verilog + Amaranth | Custom Function Unit beside a RISC-V core | user-defined | any | CFU bus | teaching / rapid custom accelerators |
| **Tensil** | Tensil.ai | Verilog generator | tiled MAC array | configurable | INT8 | AXI | FPGA inference from TFLite |
| **SCALE-Sim** | Georgia Tech | Python | cycle-accurate systolic-array **simulator** | OS / WS / RS | any | — | early design-space exploration |
| **Timely / MAERI** | Georgia Tech | RTL | near-memory / flexible-interconnect DNN accelerators | — | — | — | memory-bounded and NoC research |

**Licenses:** NVDLA (NVIDIA Open NVDLA License), Gemmini (BSD-3, Chipyard),
VTA (Apache-2.0), PULP (Solderpad), CFU Playground (Apache-2.0).

## 3. Architecture anatomy

1. **Compute fabric** — 1-D MAC lanes (VTA, PULP SIMD) vs **2-D systolic
   arrays** (Gemmini, SCALE-Sim, Tensil) vs engine pipelines (NVDLA).
   Array size sets peak TOPS and area.
2. **Dataflow** — **weight-stationary** (reuse weights; good for small
   batches/edge), **output-stationary** (reuse partial sums; good for large
   GEMM), **row-stationary** (Eyeriss, not open). Dataflow dominates energy,
   not just speed.
3. **Memory** — explicit **scratchpad + accumulator SRAM**, banked, with a
   **DMA** and double buffering. Most open NPUs are decoupled access/execute
   (load/store/execute queues + reorder buffer, as in Gemmini).
4. **Precision / quantization** — INT8 is the baseline; INT4/binary and mixed
   INT8/FP16 are research directions.
5. **Control** — instruction-driven custom RISC-V ISA (Gemmini, VTA),
   microcode, or compiler-scheduled (TVM).
6. **Integration** — RoCC coprocessor (Gemmini), AXI peripheral (NVDLA,
   Tensil), CFU (CFU Playground), or memory-mapped accelerator.

## 4. Applications

- **Edge vision** — classification/detection on camera SoCs (NVDLA class).
- **TinyML / always-on sensing** — keyword spotting, gesture, anomaly
  detection, predictive maintenance (PULP, CFU).
- **Robotics / drones / automotive prototypes** — low-latency perception
  without a cloud round-trip.
- **FPGA prototyping & education** — Tensil, CFU Playground, Gemmini on
  FireSim.
- **RISC-V + accelerator research SoCs** — Gemmini/VTA as the canonical
  CPU+NPU platform.
- **Compiler/hardware co-design** — VTA/TVM, ONNX→Gemmini.
- **Datacenter/LLM inference** — dominated by proprietary NPUs; open projects
  are mostly edge-class (a real gap).

## 5. Recommended design for lunarch on sky130

sky130 is a 130 nm process: large arrays are area- and power-prohibitive.
The practical DUT is a **small INT8 systolic accelerator** attached to the
existing `riscv` (RV32I) core.

### 5.1 Microarchitecture

```
         host RV32I                 NPU
  ┌───────────────┐        ┌──────────────────────────┐
  │  riscv core   │  RoCC/ │  ctrl  → 8×8 INT8         │
  │  (existing)   │◀─CFU──▶│          systolic array   │
  │               │  AXI   │  scratchpad (banked SRAM) │
  │  instr/data   │        │  accumulator + ReLU/scale │
  │  memory       │        │  DMA (double-buffered)    │
  └───────────────┘        └──────────────────────────┘
```

- **Array**: 8×8 INT8 MACs (64 PEs), 32-bit accumulate; optionally 4×4 for a
  smaller first cut.
- **Dataflow**: weight-stationary by default (edge-friendly); output-stationary
  optional.
- **Memory**: banked scratchpad (~8–16 KiB) + accumulator (~4 KiB);
  double-buffered DMA.
- **Control**: a tiny custom ISA (mvin / matmul / mvout / config) or a
  memory-mapped register file driven by the RV32I.
- **Integration**: RoCC-style coprocessor port, a CFU, or a simple AXI-Lite
  slave — all three can be driven by the existing testbench/golden model.

### 5.2 Flow reuse

The lunarch RTL→GDS flow is reused unchanged:

```
RTL → Yosys synthesis → floorplan → place → CTS → route → finish (GDS)
    → KLayout DRC/LVS → Yosys/Kepler LEC → OpenSTA (SPEF)
```

Add the NPU top to the design's `VERILOG_FILES`, keep the existing SDC, and
run the same `make` / `make drc lvs` targets (see `onekey/`).

### 5.3 Metrics to report

- **Area**: MACs/mm², array utilization.
- **Speed**: fmax at the sky130 TT/1.8 V corner.
- **Efficiency**: TOPS/W, energy per inference (pJ/inference).
- **Correctness**: LEC against the RTL; pre/post-sim trace match (as on the
  simulation slide).

### 5.4 Milestones

1. Generate/copy a small INT8 MAC or systolic-array RTL (Gemmini 4×4/8×8, or a
   hand-written 8×8 array).
2. Integrate with `riscv` (RoCC / CFU / AXI-Lite) and add a directed test.
3. Run the lunarch RTL→GDS flow + DRC/LVS/LEC.
4. Add a TinyML workload (keyword spotting / anomaly detection) and compare
   CPU-only vs CPU+NPU latency and energy per inference.

## 6. Starting points

- NVDLA — <https://github.com/nvdla/hw>
- Gemmini — <https://github.com/ucb-bar/gemmini>
- VTA (TVM) — <https://github.com/apache/tvm/tree/main/vta>
- PULP — <https://github.com/pulp-platform>
- CFU Playground — <https://github.com/google/CFU-Playground>
- Tensil — <https://github.com/tensil-ai/tensil>
- SCALE-Sim — <https://github.com/scalesim-project/SCALE-Sim>

## 7. Takeaway

The open-source NPU ecosystem is rich in **architecture** (NVDLA, Gemmini,
VTA, PULP) but thin in **silicon-proven, compiler-complete, edge-class**
implementations. For lunarch the highest-value next step is a **small INT8
systolic accelerator on sky130**, integrated with the RV32I and pushed through
the existing sign-off-clean flow — turning the methodology demo into a
reproducible CPU+NPU reference design.
