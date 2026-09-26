# Path Groups — `riscv` (derived from the data flow)

Path groups partition all timing paths by the **functional data-flow role**
of their start/end points (the way a designer partitions for optimization).
They are derived directly from `dataflow.md`.

Endpoints: sequential = `pcreg` (32b), `SEPC` (32b flopenr),
`rf[1..31][31:0]` (1024 `edfxtp_1`); ports = `instr`, `readdata` (in),
`pc`, `aluout`, `writedata`, `memwrite`, `memread`, `suspend` (out).

## Group definitions

| ID | Path group | Start → End | Dominant logic (modules) |
|----|-----------|-------------|--------------------------|
| **PG1** | **PC / Fetch** | `pcreg` → `pcreg` | `adder` (pcadder +4, pcimm), `mux2` (pcsrcmux, pcextmux, pcmux, pcmux2, ISRmux), `flopr` |
| **PG2** | **Execute — ALU write-back** | `regfile` → `regfile` | `mux2` (rs1mux, memsrcmux), `alu`, `mux2` (srccmux), `mux2` (resmux, storepcmux) |
| **PG3** | **Execute — Shift write-back** | `regfile` → `regfile` | `shifter`, `mux2` (srccmux, resmux, storepcmux) |
| **PG4** | **Memory (LSU)** | `readdata` → `regfile` (load WB); `regfile` → `writedata` (store) | `mux3` (halfbytemux1 / halfbytemux2), `mux2` (resmux, storepcmux) |
| **PG5** | **Branch compare → PC** | `regfile` → `pcreg` | `magcompare32` (`magcompare2b`×16, `magcompare2c`×15) → `controller.pcsrc` → `datapath` pcmux |
| **PG6** | **Decode / Control** | `instr` → control bus, `regfile.we3/ra/wa` | `controller` (`maindec`, `aludec`), `mux2` (controller mx1/mx2) |
| **PG7** | **Immediate** | `instr` → `alu` (via `srcb`), `pcreg` (via adder pcimm) | `signext` (`mux5`), `mux2` (pcextmux), `adder` (pcimm) |
| **PG8** | **Outputs / Exception** | `regfile` → `aluout`, `pcreg` → `pc`; `pcreg` → `SEPC` | `mux2` (srccmux), `flopenr` (epc) |

### Notes per group

- **PG1** — the sequential next-PC loop; contains both the `+4` path and the
  branch/jump target (`+imm`) path that re-converges at `pcmux`. Bounds the
  instruction issue rate.
- **PG2** — the classic single-cycle loop
  `rf.rd1 → memsrcmux → alu → srccmux → resmux → storepcmux → rf.wd3`.
  This is the **dominant critical path** of the design.
- **PG3** — shift variant of PG2 (`shifter` instead of `alu`); normally faster
  than PG2.
- **PG4** — load data returns from the memory port (`readdata`) combinationally
  into the write-back mux; store data leaves via `halfbytemux2`.
- **PG5** — cross-module feedback: `datapath` → `magcompare32` → `controller`
  (branch/pcsrc logic) → back into `datapath` PC mux. A slow compare delays
  the redirect decision and the next-PC path (feeds PG1).
- **PG6** — pure input→combinational/control paths; usually not critical but
  the widest fan-out (`regwrite`, `alucontrol`, `shtype`, `imm`).
- **PG7** — `instr` through the 5-way `signext`/`mux5` into the PC adder and
  the ALU `srcb` mux.
- **PG8** — output/broadcast and the exception-PC capture (`suspend`) path.

## Mapping of the measured baseline critical path to a group

At the 6.0 ns constraint the two reported violations were:

| Reported path | Group |
|---------------|-------|
| `dp.rf.rf[1][0] → dp.rf.rf[27][0]` (regfile→ALU→regfile) | **PG2** |
| `dp.rf.rf[1][0] → aluout[0]` (regfile→ALU→output) | **PG7/PG8** (result-out) |

So the entire baseline setup pressure is concentrated in **PG2 (ALU
write-back)** and the **result-output** portion of PG8, both limited by the
register-file-read → ALU → endpoint delay.
