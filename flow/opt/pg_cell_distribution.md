# Cell Distribution by Path Group — p7_delay vs p7_area

How the **extra** area-run cells (`nand2`, `nand3`, `inv`) are distributed
across path groups.

Method: cells are flattened so their nets are `_NNNN_`; instead of net prefixes,
each cell is classified by the **flip-flop its forward logic cone reaches**
(the endpoint register), which maps to a path group:
- **write-back (PG2/3/4)** = cone reaches `dp.rf.rf[*][*]/D` (ALU/shift/load write into the register file)
- **PC / branch (PG1/5)** = cone reaches `dp.pcreg.q[*]/D` (next-PC / branch redirect)

Source: `flow/opt/paths/{p7_delay,p7_area}/6_final.v`, script `make_pg_distribution2.py`.

## Counts

| Path group (by endpoint FF) | Run | nand2 | nand3 | inv | subtotal |
|---|---|---:|---:|---:|---:|
| **write-back** (`rf/D`) | p7_delay | 151 | 30 | 40 | 221 |
| | p7_area | **1,527** | **566** | **423** | **2,516** |
| | **Δ** | **+1,376** | **+536** | **+383** | **+2,295** |
| **PC / branch** (`pcreg/D`) | p7_delay | 175 | 40 | 33 | 248 |
| | p7_area | **1,341** | **538** | **395** | **2,274** |
| | **Δ** | **+1,166** | **+498** | **+362** | **+2,026** |
| unmatched (no FF endpoint) | p7_delay | 5 | 12 | 51 | 68 |
| | p7_area | 34 | 10 | 16 | 60 |

## Findings

1. The area run adds **~4,300 extra `nand2/nand3/inv` cells** versus the delay
   run (nand2 +2,542, nand3 +1,034, inv +745 total).
2. They are split **almost evenly** between the two endpoint groups:
   - **write-back / register-file loop: ~53 %** (+1,376 nand2, +536 nand3, +383 inv)
   - **PC / next-PC & branch loop: ~47 %** (+1,166 nand2, +498 nand3, +362 inv)
3. So the area mapper didn't just slim the critical ALU loop — it **re-expressed
   both major sequential loops** (the regfile write-back loop *and* the
   next-PC/branch loop) in terms of many small NAND/inverter gates, versus the
   delay mapper's fewer, wider AOI/mux (`mux2i_1`, `mux4_2`, `a21oi_1`) cells.

This matches the master histogram: the delay netlist is **mux/AOI-heavy** while
the area netlist is **NAND/inverter-heavy**, and that structural rewrite is what
moved PPA (fmax 147.9→155.4 MHz, power 19.7→18.8 mW) at the same 7 ns clock.

> Caveat: output-port cones (`aluout`, `writedata`, `pc`) were not captured (the
> walk followed FF D-pins only), and PG3/PG4 (shift/LSU) share the regfile
> endpoint so they are grouped as "write-back". The split is therefore by
> *sequential endpoint*, not by every PG1–PG8 label.
