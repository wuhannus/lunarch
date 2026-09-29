#!/usr/bin/env python3
"""PPA comparison: p7_area vs p7_area_g2 (g<=2) vs p7_area_g15 (g<=1.5)."""
import re, os

P = '/mnt/d/opencode/lunarch/flow/opt/paths'
DIE = 376.625 * 376.625


def metrics(d):
    r = f'{P}/{d}/6_finish.rpt'
    if not os.path.exists(r):
        return None
    t = open(r, encoding='utf-8', errors='ignore').read()
    wns = float(re.search(r'^wns max\s+(-?[\d.]+)', t, re.M).group(1))
    tns = float(re.search(r'^tns max\s+(-?[\d.]+)', t, re.M).group(1))
    pmin = float(re.search(r'period_min = ([\d.]+)', t).group(1))
    fmax = float(re.search(r'fmax = ([\d.]+)', t).group(1))
    mp = re.search(r'^Total\s+[\d.eE+-]+\s+[\d.eE+-]+\s+[\d.eE+-]+\s+([\d.eE+-]+)', t, re.M)
    pw = float(mp.group(1)) * 1000 if mp else None
    v = f'{P}/{d}/6_final.v'
    cells = len(re.findall(r'sky130_fd_sc_hd__[a-z0-9_]+ \S+ \(', open(v, encoding='utf-8', errors='ignore').read())) if os.path.exists(v) else 0
    da = re.search(r'Design area\s+([\d.]+) um\^2\s+([\d.]+)%', t)
    area = float(da.group(1)) if da else None
    dens = (area / DIE * 100) if area else None
    return dict(wns=wns, tns=tns, pmin=pmin, fmax=fmax, power=pw, area=area, dens=dens, cells=cells)


print(f'{"run":14} {"WNS":>7} {"TNS":>9} {"fmax":>8} {"power":>8} {"area":>9} {"dens":>6} {"cells":>7}')
for d in ('p7_area', 'p7_area_g2', 'p7_area_g15'):
    m = metrics(d)
    if m:
        print(f'{d:14} {m["wns"]:7.2f} {m["tns"]:9.1f} {m["fmax"]:8.1f} '
              f'{(m["power"] or 0):7.2f}m {(m["area"] or 0):9.0f} {(m["dens"] or 0):5.1f}% {m["cells"]:7d}')
    else:
        print(f'{d:14}  (missing)')
