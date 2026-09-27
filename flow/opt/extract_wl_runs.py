#!/usr/bin/env python3
"""Sum routed wire length (and show density) per run from ORFS route logs."""
import re, os, glob

LOGS = [
    ('baseline (7.0 ns, delay)', None),
    ('timing run (5.0 ns, delay)', '/home/lunarch/opt2_timing.log'),
    ('power run (20.0 ns, area)', '/home/lunarch/opt2_power.log'),
    ('sweep p7_delay (7.0 ns, delay)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p7_delay.log'),
    ('sweep p10_delay (10.0 ns, delay)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p10_delay.log'),
    ('sweep p7_area (7.0 ns, area)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p7_area.log'),
    ('sweep p10_area (10.0 ns, area)', '/mnt/d/opencode/lunarch/flow/opt/sweep/p10_area.log'),
    ('kogge-stone (5.0 ns, delay)', '/mnt/d/opencode/lunarch/flow/opt/ks/ks_5ns.log'),
]

def parse(path):
    if not path or not os.path.exists(path):
        return None
    t = open(path, encoding='utf-8', errors='ignore').read()
    by = {}
    for m in re.finditer(r'Total wire length on LAYER (\w+)\s*=\s*([\d.]+) um', t):
        by[m.group(1)] = float(m.group(2))      # keep last (final route)
    # last block wins (final route)
    tot = None
    ms = re.findall(r'Total wire length\s*=\s*([\d.]+) um', t)
    if ms:
        tot = float(ms[-1])
    return by, tot

print(f'{"run":36} {"signal wl (mm)":>14} {"met1":>8} {"met2":>8} {"met3":>8} {"met4":>8} {"met5":>8}')
for name, path in LOGS:
    r = parse(path)
    if not r:
        print(f'{name:36} {"(no log; baseline kept)":>14}')
        continue
    by, tot = r
    sig = sum(v for k, v in by.items() if k.startswith('met') or k == 'li1')
    print(f'{name:36} {sig/1000:14.1f} {by.get("met1",0)/1000:8.1f} {by.get("met2",0)/1000:8.1f} '
          f'{by.get("met3",0)/1000:8.1f} {by.get("met4",0)/1000:8.1f} {by.get("met5",0)/1000:8.1f}')
