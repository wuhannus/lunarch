# Module-coloured final layout — baseline

Top-down view of the placed `sky130hd/riscv32i` die (`377.8 × 377.8 µm`) with
cells coloured **by module**.

- Image: `6_final_modules.png` / `6_final_modules.svg`
- Interactive page: **`index.html`** (self-contained; open in a browser)
- Counts: `module_counts.txt`
- Generator: `make_module_layout.py`, `make_module_html.py`

## How module info was obtained

The baseline flow runs `synth -flatten`, which discards hierarchy and renames
most cells `_NNNN_`. To recover module membership the flow was re-run with

```bash
export SYNTH_HIER_SEPARATOR=__     # Yosys flatten separator
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk ...
```

so that **net names keep their instance path** (e.g. `dp__rf__rf[0][0]`,
`dp__alu__exor[2]`, `c__ad__aluop`). Each final cell is then assigned to the
module of the first module-prefixed net it touches.

> Note: `SYNTH_HIERARCHICAL=1` (keep full module boundaries) was tried first but
> OpenROAD's Verilog front-end cannot parse the resulting netlist (Yosys emits
> `$paramod\...` module names → syntax error). The separator approach keeps the
> flow flat/parseable and still labels the nets.

## Coverage

| Module | Colour | Cells |
|--------|--------|------:|
| regfile (32×32 RF) | `#e06666` red | 877 |
| alu | `#4a86e8` blue | 254 |
| datapath muxes (`memsrcmux`, `ISRmux`, `result2`, `pcext`) | `#8e7cc3` purple | 120 |
| adder (`pcimm`, `pcadder`) | `#f6b26b` orange | 38 |
| aludec (controller) | `#76a5af` teal | 10 |
| **other / unmapped** (opt-merged logic, buffers, clock, fill) | `#d9dee6` grey | 4,236 |
| **total placed** | | **5,535** |

**2,353 / 5,535 cells (43%)** get an explicit module label — the large,
name-preserving blocks (register file, ALU, address adders, datapath muxes,
decoder). The remainder are the datapath's fine combinational logic (shifter,
comparator, sign-extension, branch muxes) and the clock/resizer/fill cells whose
nets were renamed during `opt`, so no module path survives for them.

## Observations from the map

- The **register file** (red) occupies the **left third** of the die.
- The **ALU** (blue) is a dense cluster on the **right side**.
- Address adders (orange) and datapath muxes (purple) sit between them.
- Layout is consistent with the PG2 critical loop: the regfile read muxes,
  ALU and write-back all sit far apart, but the wire delay is still <0.02 ns
  (cell-delay dominated), so the split placement is not a timing problem.

Timing after this re-run is unchanged: **setup WNS 0.00 ns / TNS 0.00 ns** at
7.0 ns, DRC 0, LVS match.
