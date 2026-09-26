# Timing Dashboard — `riscv` (sky130hd/riscv32i)

Interactive HTML dashboard over all **1,152 setup timing endpoints** of the
timing-closed 7.0 ns baseline.

Open **`index.html`** in a browser (self-contained, no server needed).

## Features

- **Left — path groups** (worst first): `PG8 result-out`, `PG2 ALU/write-back`,
  `PG1 next-PC`, `PG4 store-out`, `PG1 pc-out`. Each card shows its STA clock
  group, path count and worst slack.
- **Middle — path list** for the selected group, sorted **worst slack at the
  top → best slack at the bottom**. Columns: rank, slack (ns), logic levels,
  start point, end point.
- **Right — path route**: click a path to see the **start point → chain of
  cells → end point**, with each cell's **cell delay** and the **wire (net)
  delay** into it (plus a delay bar relative to the path's slowest cell).

## Data source & regeneration

`6_finish_dashboard_all_paths.rpt` — `report_checks -path_delay max
-group_path_count 1000000 -endpoint_path_count 1 -unique_paths_to_endpoint
-fields {net input_pin} -format full -digits 4 -no_line_splits`
(post-route ODB + SPEF, from `6_final.odb`).

Regenerate:

```bash
python3 make_dashboard.py        # writes index.html with embedded JSON
```

## Baseline snapshot

| Group | STA group | Paths | Worst slack |
|-------|-----------|------:|------------:|
| PG8 result-out | `vclk_clk` | 32 | +0.0415 ns |
| PG2 ALU/write-back | `clk` | 1,024 | +0.2402 ns |
| PG1 next-PC | `clk` | 32 | +0.6792 ns |
| PG4 store-out | `vclk_clk` | 32 | +2.9384 ns |
| PG1 pc-out | `vclk_clk` | 32 | +4.2654 ns |

Clock 7.0 ns (142.86 MHz); reg→reg fmax 147.93 MHz; 0 setup violations.
