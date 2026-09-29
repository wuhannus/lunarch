# PPA — p7_area vs low-logical-effort-restricted variants

Two extra p7_area runs where the mapper is **forbidden** (`DONT_USE_CELLS`)
from using cells above a logical-effort cap. Same 7 ns clock, same 376.6 µm die.

| Run | Cell g cap | Setup WNS | fmax | Power | Cell area | Density | Instances |
|-----|-----------:|----------:|-----:|------:|----------:|--------:|----------:|
| **p7_area** (reference) | none | 0.00 | **155.4 MHz** | **18.8 mW** | **74,874 µm²** | 52.8 % | ~7,831 |
| **p7_area_g2** | g ≤ 2.0 | 0.00 | **155.4 MHz** | 18.9 mW | 77,543 µm² | 54.7 % | ~8,623 |
| **p7_area_g15** | g ≤ 1.5 | 0.00 | **154.9 MHz** | 19.0 mW | 82,306 µm² | 58.0 % | ~10,850 |

(Cells capped: g>2 removes xor2/xnor2, aoi41, aoi311/oai311, mux4, aoi22/oai22,
nor3, … — 210 cells; g>1.5 additionally removes nand3/nor2/AOI/OAI/mux — 299 cells.)

## Result: capping logical effort does **not** help — it slightly hurts

| vs p7_area | fmax | Power | Area | Density |
|-----------|-----:|------:|-----:|--------:|
| **g ≤ 2.0** | same (0.0) | +0.1 mW (+0.5%) | **+2,669 µm² (+3.6%)** | +1.9 pt |
| **g ≤ 1.5** | −0.5 MHz (−0.3%) | +0.2 mW (+1.1%) | **+7,432 µm² (+9.9%)** | +5.2 pt |

- **No timing gain** (g≤2 identical, g≤1.5 marginally worse).
- **More area and more power** as the cap tightens — the design grows ~4–10 %.
- Cell count rises (+10 % at g≤2, +39 % at g≤1.5) as logic is rebuilt from more,
  smaller low-effort gates.

## Why

1. The **area-ABC map already does the right thing**: it already picks mostly
   low-effort nand2/nand3/inv on the critical loops (avg g = 1.68), but it *also*
   uses the occasional high-effort cell (AOI/OAI/xor/mux) where that is genuinely
   the cheapest realization.
2. **Hard-capping removes those useful cells** and forces the Boolean network to
   be re-expanded into more low-effort gates → **larger, not faster**. The effort
   model predicts this: what matters is **total path effort** (Σg ≈ 42), not per-
   stage effort — a slightly-fewer-higher-g chain often beats a longer-lower-g one.
3. So **logical effort is a guide, not an optimization target by itself**.
   Constraining it degrades the result; letting the mapper choose the best mix
   per cone (as p7_area does) is better.

**Takeaway:** the p7_area / area-ABC configuration is already near-optimal for
this design; imposing a hard logical-effort ceiling on the library only adds area
and power for no speed. Optimality comes from the *mapper's* effort-aware choice
of low-effort gates where beneficial, not from banning high-effort cells outright.
