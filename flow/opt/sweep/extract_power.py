#!/usr/bin/env python3
"""Extract the report_power total (internal/switching/leakage) for the sweep points."""
import os
import re

POINTS = [
    ("p5_delay", 5.0, "timing_diematch/6_finish.rpt"),
    ("p7_delay", 7.0, "sweep/p7_delay.rpt"),
    ("p10_delay", 10.0, "sweep/p10_delay.rpt"),
    ("p7_area", 7.0, "sweep/p7_area.rpt"),
    ("p10_area", 10.0, "sweep/p10_area.rpt"),
    ("p20_area", 20.0, "power_diematch/6_finish.rpt"),
]
BASE = "/mnt/d/opencode/lunarch/flow/opt"


def parse(path):
    txt = open(path).read()
    # take the LAST "Total" line of a report_power table
    lines = txt.splitlines()
    tot = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("Total") and ("e-0" in ln or "e+0" in ln):
            tot = ln
    if tot is None:
        return None
    nums = re.findall(r"[-+0-9.]+e[-+][0-9]+", tot)
    if len(nums) < 4:
        return None
    return [float(x) for x in nums[:4]]   # internal, switching, leakage, total


print(f"{'point':10} {'clk':>4} {'int_mW':>8} {'sw_mW':>8} {'leak_mW':>9} "
      f"{'tot_mW':>8}")
for name, clk, rel in POINTS:
    p = os.path.join(BASE, rel)
    v = parse(p)
    if v:
        print(f"{name:10} {clk:4.0f} {v[0]*1e3:8.3f} {v[1]*1e3:8.3f} "
              f"{v[2]*1e3:9.5f} {v[3]*1e3:8.3f}")
    else:
        print(f"{name:10} MISSING/none in {p}")
