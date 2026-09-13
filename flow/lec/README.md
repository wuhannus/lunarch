# Logical Equivalence Checking (LEC) — sky130hd/riscv32i

Both stages of the LEC chain were proven.

## 1. RTL ≡ Synthesized Netlist

| Field | Value |
|-------|-------|
| Engine | Yosys 0.69 `equiv_make` / `equiv_simple` / `equiv_induct` / `equiv_status` |
| Golden | `riscv32i` RTL (`adder.v`, `alu.v`, `aludec.v`, `controller.v`, `datapath.v`, `dmem.v`, `flopenr.v`, `flopens.v`, `flopr.v`, `magcompare2b.v`, `magcompare2c.v`, `magcompare32.v`, `maindec.v`, `mux2.v`–`mux8.v`, `regfile.v`, `riscv.v`, `rom.v`, `shifter.v`, `signext.v`) |
| Revised | `1_synth_lec.v` (ORFS synthesized netlist) |
| Result | ✅ **Equivalence successfully proven** (99 cells proven, 0 unproven) |
| Log | `rtl_equiv2.log` |
| Script | `rtl_equiv.ys` |

## 2. Synthesized Netlist ≡ Final Routed Netlist

| Field | Value |
|-------|-------|
| Engine | Kepler Formal (ORFS `LEC_CHECK=1`) |
| Golden | `1_synth_lec.v` |
| Revised | `6_final_lec.v` (final routed netlist) |
| Result | ✅ **Global output passed lec test** |
| Log | `6_final_lec_check.log` |

## Notes

- Kepler Formal (ORFS's LEC engine) is **gate-level only** — it cannot parse
  RTL, which is why ORFS uses the synthesized netlist as golden. The
  RTL-vs-synth stage therefore uses Yosys.
- `SEC_CHECK=1` (sequential equivalence, PDR engine) is optional and can be very
  slow on a full core; it is not required for sign-off.
