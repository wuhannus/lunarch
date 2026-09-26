# Data Flow — `riscv` (sky130hd/riscv32i baseline)

Single-cycle RV32I core. Top module `riscv` = `controller` + `datapath`.
All state lives in the **PC register** (`flopr`) and the **register file**
(`regfile`, 32×32, `rf[0]` hard-wired to 0). There is no pipeline register,
so every instruction completes combinationally in one cycle:
`PC/latch → regfile read → execute → write-back`.

## 1. Top-level module flow

```
                        instr[31:0]
                             |
             +---------------v-----------------+
             |             controller            |
             |      maindec            aludec    |
             +---------------+-------------------+
                             |  control bus
                             |  (memtoreg, memwrite, memread, pcsrc, branch,
                             |   alusrc, alu2src, alucontrol[3:0], imm[2:0],
                             |   shtype[1:0], regwrite, storepc, pcadd, pcext,
                             |   unsign, sltunsigned, suspend, lh/lb/lhu/lbu)
                             v
  instr[31:0]  ------------->+---------------------+-----------> pc[31:0]
  readdata[31:0] ----------->|      datapath       |-----------> aluout[31:0]
  clk, reset  -------------->|  (all sequential    |-----------> writedata[31:0]
                             |   logic + datapath  |-----------> memwrite
                             |   muxes/adders/ALU) |-----------> memread
                             +----------+----------+-----------> suspend
                                        |
                                  gt, lt, eq
                                        |
                       (branch decision feedback to controller.pcsrc)
```

## 2. Datapath internal data flow

```
 pcreg(flopr) ──q=pc──┬─> adder(pcadder) +4 ──────────> pcsum ────────────┐
   ^                  │                                                   │
   │ pcnext           └─> pcsrcmux(pcadd) ─> pcjalr ─> adder(pcimm) ──────┼─> pcimm_sum
   │                                     ^                ^              │
   │                            (srca2 when jalr)   pcextmux(pcext)<─signext<─ instr
   │                                                                (mux5)      │
   │                                                                            │
   └── ISRmux(ISRsel)<─ pcISRin <─ pcmux(pcsrc) <─────── pcsum / pcimm_sum      │
                                                                                │
 pcreg ──q=pc──> flopenr(epc, en=suspend) ──> SEPC                              │
                                                                                │
 regfile(rf)  ra1=rs1mux(instr[19:15])  ra2=instr[24:20]                        │
   │          wa3=instr[11:7]  wd3=result2  we3=regwrite                         │
   │                                                                            │
   ├─ rd1=srca2 ──────────────┬──────────────────────────────┐                  │
   │                          │                              │                  │
   │                          v                              v                  │
   │                    alu(a=srca2,b=srcb)              shifter(a=srca2,       │
   │                          │                          shamt=srcb[4:0])       │
   │                          v                              │                  │
   │                      aluout2 ──────────┬─────────────── shoutput            │
   │                                        v                                     │
   │                                 srccmux(alu2src) ────────────> aluout (OUT)  │
   │                                        │                                     │
   ├─ rd2=writedata ──┬─> memsrcmux(alusrc) ┴─> srcb ──> alu / shifter           │
   │                  │                                                          │
   │                  ├─> magcompare32(A,B) ──> gt, lt, eq ──> controller.pcsrc  │
   │                  │                                                          │
   │                  └─> halfbytemux2 ─────────────────────────> writedata(OUT) │
   │                                        │
   │                              resmux(memtoreg) <─ halfbytemux1 <─ readdata   │
   │                                        │                                   │
   │                               result ──┘                                   │
   │                                        │                                   │
   │                            storepcmux(storepc) <─ pctoreg <── pcsum/pcimm_sum
   │                                        │
   └──────────────── result2 = wd3 ─────────┘          (register write-back)
```

## 3. Instruction-cycle walk-through (one clock period)

1. **Fetch / next-PC** — `pcreg` drives `pc`; `pcadder` forms `pc+4`; for
   branches/jumps `pcimm` forms `pc+imm`; `pcmux`/`pcmux2` pick the target;
   `ISRmux` (ISRsel tied 0) feeds `pcnext` back into `pcreg`.
2. **Decode** — `instr` → `controller` (`maindec` = opcode decode,
   `aludec` = funct3/funct7 decode) produces the control bus.
3. **Register read** — `regfile` gives `rd1→srca2` (rs1) and `rd2→writedata` (rs2).
4. **Immediate** — `signext`/`mux5` builds I/S/B/U/J immediates from `instr`.
5. **Execute** — `srcb` (rs2 or immediate) and `srca2` go to `alu`; `srca2`
   and `shamt` go to `shifter`; `srccmux` picks ALU vs shift → `aluout`.
6. **Compare** — `magcompare32` compares rs1 vs rs2 → `gt/lt/eq` → controller
   → `pcsrc` (branch resolution).
7. **Write-back** — `resmux` picks ALU result or load data (`readdata4`);
   `storepcmux` injects the PC for jal/jalr; `result2` is written to `rf[rd]`.
8. **Store** — `writedata4` (byte/half masked) leaves the core to memory.

## 4. Endpoints (timing start/end points)

| Kind | Names |
|------|-------|
| Sequential | `pcreg` (32b flopr), `SEPC` (32b flopenr), `rf[1..31][31:0]` (1024 `edfxtp_1`) |
| Input ports | `instr[31:0]`, `readdata[31:0]`, `clk`, `reset` |
| Output ports | `pc[31:0]`, `aluout[31:0]`, `writedata[31:0]`, `memwrite`, `memread`, `suspend` |
