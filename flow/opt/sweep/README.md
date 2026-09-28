# AI-Driven PPA Sweep — RISC-V RV32I on sky130

Application #3 from the LUNARCH brief: use the automated open-source flow as a
**PPA research vehicle** to search the **timing ↔ power Pareto** of the core.

- Search space: `clk_period` × `ABC_AREA` (delay vs area mapping)
- **All points share the identical baseline die** (`376.625 µm`) so only the
  synthesis/clock knobs vary.
- Points: `ppa_points.csv` · Plots: `pareto_ppa.svg`/`.png` (fair, normalized)
  and `pareto_ppa_asrun.svg`/`.png` (raw) · Per-point logs & `6_finish.rpt` here.

## ⚠️ Power must be compared at the same frequency

OpenSTA reports power at the run's **constrained clock**, not at the achieved
fmax. Comparing those raw numbers across points with different clock targets is
**unfair**: a point run at 20 ns trivially shows ~1/3 the power of a 7 ns point.

All dynamic power (internal + switching) scales with frequency; leakage
(~0.00003 mW at TT/1.8 V) does not. So every point is normalized to the
baseline clock (7.0 ns = **142.857 MHz**):

```
P_ref = P_leakage + (P_internal + P_switching) · (clk_ns / 7.0)
```

`pareto_ppa.svg` uses `P_ref`; `pareto_ppa_asrun.svg` keeps the raw values.

## Measured points

| Point | clk (ns) | ABC | fmax (MHz) | Power as-run (mW) | **Power @142.9 MHz (mW)** | On Pareto |
|-------|---------:|-----|-----------:|------------------:|--------------------------:|:---------:|
| p5_delay  | 5  | delay | 153.37 | 29.30 | 20.94 | no |
| p7_delay  | 7  | delay | 147.93 | 19.70 | 19.74 | no |
| p10_delay | 10 | delay | 122.07 | 13.40 | 19.11 | no |
| **p7_area**  | 7  | **area** | **155.37** | 18.80 | **18.82** | **yes** |
| p10_area  | 10 | area  | 127.49 | 13.30 | 19.06 | no |
| **p20_area** | 20 | **area** | **132.50** | 6.54 | **18.69** | **yes** |

## The interesting result

At an **equal 142.9 MHz clock**, area-oriented synthesis (`ABC_AREA=1`) is both
faster and lower power than the delay-oriented baseline — and clearly better
than the 5 ns "timing" attempt:

| Point | fmax | Power as-run | Power @142.9 MHz |
|---|---:|---:|---:|
| p7_delay (baseline) | 147.93 MHz | 19.70 mW | 19.74 mW |
| p5_delay (timing run) | 153.37 MHz | 29.30 mW | 20.94 mW |
| **p7_area** | **155.37 MHz** | 18.80 mW | **18.82 mW** |

So the usual intuition "delay-oriented ABC for speed" was **wrong here**: the
area mapping produced a structure the resizer/CTS could optimize better,
giving **+5% fmax at −5% power** versus baseline. Because leakage is negligible,
power @142.9 MHz is essentially energy-per-cycle × 142.9 MHz, so the ~5%
difference is a genuine per-cycle energy reduction.

## Pareto front (normalized to 142.9 MHz)

Two non-dominated points:

```
fmax  155.37 MHz  <---------------------------->  132.50 MHz
power@142.9MHz  18.82 mW                           18.69 mW
              (p7_area: max speed)            (p20_area: min power)
```

- **p20_area** (clk 20 ns, area ABC): **18.69 mW @142.9 MHz**, 132.5 MHz — the
  low-power design point. At its *own* 50 MHz clock it draws 6.54 mW, but that
  is not comparable to the 7 ns baseline; at equal frequency the saving is
  **~5%**, not ~67%.
- **p7_area** (clk 7 ns, area ABC): **18.82 mW @142.9 MHz**, 155.4 MHz — best
  speed, better than baseline on both axes.

Dominant knob: **`ABC_AREA` (synthesis mapper)**, not the clock period — the
clock period mostly sets how hard the resizer pushes, and relaxing it too far
(p10_area) does not lower energy-per-cycle further.

## Takeaways

1. A small, automated sweep over 2 knobs × 6 points (~3 h of compute) found a
   configuration (`p7_area`) that **dominates the manual baseline** on both
   timing and power — **at the same frequency**.
2. **The mapper choice dominated** the clock constraint for this design.
3. `fmax` is **non-monotonic** in the clock constraint — the flow's
   resizer/CTS behaviour matters more than the target, so the target clock
   cannot be used as a proxy for fmax.
4. **Report power at a common frequency (or as energy/cycle).** As-run power
   across different clock targets is misleading; see `pareto_ppa.svg`.
5. This is exactly the kind of search loop an AI agent can run unattended:
   define the space → sweep → collect → normalize → plot Pareto → pick the knee.

## Reproduction

`run_sweep.sh` loops the points (die pinned via `DIE_AREA`/`CORE_AREA`);
`make_pareto.py` parses each `6_finish.rpt`, normalizes the dynamic power to
142.9 MHz and renders the dependency-free SVG, then `rsvg-convert` makes the PNG.
