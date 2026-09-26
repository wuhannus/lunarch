# AI-Driven PPA Sweep — RISC-V RV32I on sky130

Application #3 from the LUNARCH brief: use the automated open-source flow as a
**PPA research vehicle** to search the **timing ↔ power Pareto** of the core.

- Search space: `clk_period` × `ABC_AREA` (delay vs area mapping)
- **All points share the identical baseline die** (`376.625 µm`) so only the
  synthesis/clock knobs vary.
- Points: `ppa_points.csv` · Plot: `pareto_ppa.svg` / `.png` · Per-point logs &
  `6_finish.rpt` in this folder.

## Measured points

| Point | clk (ns) | ABC | fmax (MHz) | Power (mW) | On Pareto |
|-------|---------:|-----|-----------:|-----------:|:---------:|
| p5_delay  | 5  | delay | 153.37 | 29.30 | no |
| p7_delay  | 7  | delay | 147.93 | 19.70 | no |
| p10_delay | 10 | delay | 122.07 | 13.40 | no |
| **p7_area**  | 7  | **area** | **155.37** | **18.80** | **yes** |
| p10_area  | 10 | area  | 127.49 | 13.30 | no |
| **p20_area** | 20 | **area** | **132.50** | **6.54** | **yes** |

## The interesting result

**The AI-driven search found that area-oriented synthesis (`ABC_AREA=1`) at the
same 7 ns clock strictly dominates the "obvious" delay-oriented baseline and the
5 ns timing-attempt** — higher fmax *and* lower power:

| | fmax | power |
|---|---:|---:|
| p7_delay (baseline) | 147.93 MHz | 19.70 mW |
| p5_delay (timing run) | 153.37 MHz | 29.30 mW |
| **p7_area** | **155.37 MHz** | **18.80 mW** |

So the usual intuition "delay-oriented ABC for speed" was **wrong here**: the
area mapping produced a structure that the resizer/CTS could optimize better,
giving **+5% fmax at −5% power** versus baseline.

## Pareto front

Two non-dominated points:

```
fmax  155.37 MHz  <---------------------------->  132.50 MHz
power  18.80 mW                                    6.54 mW
      (p7_area: max speed)              (p20_area: min power)
```

- **p20_area** (clk 20 ns, area ABC): **6.54 mW, 132.5 MHz** — the low-power
  design point (−67% power vs baseline, −10% fmax).
- **p7_area** (clk 7 ns, area ABC): **18.8 mW, 155.4 MHz** — best speed, and
  better than baseline on both axes.

Dominant knob: **`ABC_AREA` (synthesis mapper)**, not the clock period — the
clock period mostly sets how hard the resizer pushes, and relaxing it too far
(p10_area) actually *lowers* achieved fmax.

## Takeaways

1. A small, automated sweep over 2 knobs × 6 points (≈3 h of compute) found a
   configuration that **dominates the manual baseline** on both timing and power.
2. **The mapper choice dominated** the clock constraint for this design.
3. `fmax` is **non-monotonic** in the clock constraint — the flow's
   resizer/CTS behaviour matters more than the target, so the target clock
   cannot be used as a proxy for fmax.
4. This is exactly the kind of search loop an AI agent can run unattended:
   define the space → sweep → collect → plot Pareto → pick the knee.

## Reproduction

`run_sweep.sh` loops the points (die pinned via `DIE_AREA`/`CORE_AREA`),
`collect()` extracts WNS/TNS/period_min/fmax/power/cells per point;
`make_pareto.py` renders the dependency-free SVG.
