# Glossary — `riscv` (sky130hd/riscv32i)

Abbreviations used in `dataflow.md`, `path_groups.md` and the RTL.

## A. RISC-V / architecture terms

| Abbr. | Meaning | Where |
|-------|---------|-------|
| **PC** | **Program Counter** — address of the current instruction | `pcreg`, `pc` port |
| RV32I | RISC-V 32-bit Integer base ISA | design name |
| **ALU** | **Arithmetic Logic Unit** | `alu` module |
| RF / regfile | Register File (32×32) | `regfile` module |
| rs1 / rs2 | register **source** 1 / 2 (the two read operands) | `instr[19:15]` / `instr[24:20]` |
| rd | register **destination** (write operand) | `instr[11:7]` |
| imm | immediate value encoded in the instruction | `signext` |
| I / S / B / U / J | immediate **encodings**: I=ALU/imm, S=store, B=branch, U=upper (lui/auipc), J=jump | `imm[2:0]` |
| lui | load upper immediate | — |
| auipc | add upper immediate to PC | `auipc_cntrl` |
| jal / jalr | jump and link / jump and link register | `storepc`, `pcadd` |
| lw/lh/lb | load word / halfword / byte (`lhu`/`lbu` = unsigned) | `lh,lb,lhu,lbu` |
| sw/sh/sb | store word / halfword / byte | `lh,lb` (store side) |
| beq/bge/blt | branch if equal / greater-or-equal / less-than | `branch`, `funct3` |
| slt / sltu | set-less-than (signed / unsigned) | `sltunsigned` |
| **SEPC** | **Saved Exception Program Counter** (CSR) | `SEPC` reg |
| ISR | Interrupt Service Routine | `ISR`, `ISRsel` |
| WB | Write-Back (result written to regfile) | path group PG2–PG4 |
| EXE | Execute stage/unit | path groups |
| LSU | Load/Store Unit | path group PG4 |
| CSR | Control/Status Register | — |

## B. Naming conventions (from the RTL)

| Suffix/prefix | Meaning |
|---------------|---------|
| `mux2` / `mux3` / `mux4` / `mux5` / `mux8` | N-input **multiplexer** (N:1 select) |
| `flopr` | **fl**ip-**flop** with **r**eset |
| `flopenr` | flip-flop with **en**able + **r**eset |
| `flopens` | flip-flop with **en**able + **s**et |
| `adder` | adder |
| `signext` | sign extender |
| `shifter` | barrel shifter |
| `magcompare32` / `2b` / `2c` | magnitude **compar**ator (32-bit / 2-bit building blocks) |
| `#(N)` | Verilog parameter — bit width N |

## C. Control signals (`controller` output bus)

| Signal | Meaning |
|--------|---------|
| `memtoreg` | **mem**ory-**to-reg**ister (select load data for write-back) |
| `memread` / `memwrite` | memory read / write enable |
| `regwrite` | register-file write enable |
| `pcsrc` | **PC src** — next PC = PC+4 vs branch/jump target |
| `alusrc` | **ALU src** — B operand = rs2 vs immediate |
| `alu2src` | ALU-vs-shifter result **select** (drives `srccmux`) |
| `alucontrol[3:0]` | ALU operation code |
| `shtype[1:0]` | **sh**ift **type** (left / logical-right / arithmetic-right) |
| `shamt[4:0]` | **sh**ift **am**oun**t** (how many bits to shift) |
| `imm[2:0]` | immediate-type select |
| `branch` | branch instruction flag |
| `storepc` | store PC into rd (link value for jal/jalr) |
| `pcadd` | add PC (jalr uses PC as adder base) |
| `pcext` | **PC ext**end — branch offset ×2 |
| `unsign` / `sltunsigned` | unsigned-compare controls |
| `lh,lb,lhu,lbu` | load-size controls |
| `suspend` | suspend / halt |

## D. Datapath signals & instances

| Name | Meaning |
|------|---------|
| `srca2` | **src A** — ALU operand A (= `rf.rd1`, i.e. rs1) |
| `srcb` | **src B** — ALU operand B (rs2 or immediate) |
| **`srccmux`** | **src C mux** — selects the result **source** between ALU and shifter (`aluout2` vs `shoutput`) |
| `signimm` | **sign**-extended **imm**ediate |
| `pcext_imm` | PC immediate (branch offset, doubled) |
| `pcjalr` | adder base for PC+imm (rs1 when jalr, else PC) |
| `pcsum` | **PC sum** = PC + 4 |
| `pcimm_sum` | PC + immediate (branch/jump target) |
| `pctoreg` | **PC to reg**ister (link value to write) |
| `pcISRin` | PC/ISR input to the ISR mux |
| `pcnext` | next PC value |
| `aluout2` | internal raw ALU output |
| `aluout` | result after ALU/shift mux **and** an output port |
| `shoutput` | **sh**ifter **output** |
| `result`, `result2` | write-back value (ALU/shift vs load; then vs PC link) |
| `readdata`, `readdata4` | data from memory, and after byte/half extension |
| `writedata`, `writedata4` | rs2 value, and after byte/half masking (store data) |
| `ra1/ra2` | register-file **r**ead **a**ddress 1/2 |
| `rd1/rd2` | register-file **r**ead **d**ata 1/2 |
| `wa3` | register-file **w**rite **a**ddress |
| `wd3` | register-file **w**rite **d**ata |
| `we3` | register-file **w**rite **e**nable |
| `gt/lt/eq` | **g**reater-**t**han / **l**ess-**t**han / **eq**ual (comparator) |
| `compA/compB` | **comp**arator inputs A / B |
| `zero` | ALU zero flag |

## E. Multiplexer instance names (in `datapath`/`controller`)

| Instance | Selects |
|----------|---------|
| `pcmux` | next PC: PC+4 (`pcsum`) vs branch target (`pcimm_sum`) |
| `pcmux2` | PC link value: branch target vs PC+4 |
| `pcsrcmux` | adder base: rs1 (`srca2`) vs PC |
| `pcextmux` | branch offset: ×2 or not |
| `storepcmux` | write-back: `result` vs PC link (`pctoreg`) |
| `memsrcmux` | ALU B operand: rs2 (`writedata`) vs immediate |
| `srccmux` | result source: ALU (`aluout2`) vs shifter (`shoutput`) |
| `resmux` | write-back: ALU result vs load data (`readdata4`) |
| `ISRmux` | interrupt vector: `pcISRin` vs `ISR` |
| `rs1mux` | rs1 address: `instr[19:15]` vs 0 (for lui) |
| `halfbytemux1` / `halfbytemux2` | load byte/half extension / store byte/half masking |
| controller `mx1` / `mx2` | `alu2src` / `alucontrol` override muxes |
