#!/usr/bin/env python3
"""Density = standard-cell area / total die area, per run."""
import re, os

DIE_UM2 = 376.625 * 376.625   # 141,846 um^2 (all runs share the baseline die)
LOGS = [
    ('baseline & p7_delay (7.0 ns, delay)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p7_delay.log'),
    ('timing run (5.0 ns, delay)', '/home/lunarch/opt2_timing.log'),
    ('power run (20.0 ns, area)', '/home/lunarch/opt2_power.log'),
    ('sweep p10_delay (10.0 ns, delay)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p10_delay.log'),
    ('sweep p7_area (7.0 ns, area)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p7_area.log'),
    ('sweep p10_area (10.0 ns, area)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p10_area.log'),
    ('kogge-stone (5.0 ns, delay)', '/mnt/d/opencode/lunarch/flow/opt/ks/ks_5ns.log'),
]

def area_util(path):
    if not path or not os.path.exists(path):
        return None
    t = open(path, encoding='utf-8', errors='ignore').read()
    m = re.findall(r'Design area\s+([\d.]+) um\^2\s+([\d.]+)% utilization', t)
    if m:
        return float(m[-1][0]), float(m[-1][1])
    # fallback: ORFS "Design area" table
    m = re.findall(r'Design area\s+([\d.]+)', t)
    return (float(m[-1]), None) if m else None

print(f'{"run":38} {"cell area (um^2)":>16} {"die (um^2)":>11} {"cell area/die":>14}')
for name, path in LOGS:
    r = area_util(path)
    if not r:
        print(f'{name:38} {"(no log)":>16}')
        continue
    a, u = r
    print(f'{name:38} {a:16.0f} {DIE_UM2:11.0f} {100*a/DIE_UM2:13.1f}%' + (f'   (ORFS util {u}%)' if u else ''))
