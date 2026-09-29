#!/usr/bin/env python3
"""Average logic levels and average logical effort for p7_delay vs p7_area,
over the worst 200 timing paths of each."""
import re

P = '/mnt/d/opencode/lunarch/flow/opt/paths'
OUT = 'sky130_fd_sc_hd__'

AOI = {'a21oi': 2.0, 'a21o': 1.6, 'a22oi': 2.3, 'a22o': 1.8, 'a31oi': 2.7,
       'a31o': 2.0, 'a41oi': 3.3, 'a211oi': 2.7, 'a221oi': 2.7, 'a311oi': 3.0}
OAI = {'o21ai': 2.0, 'o21a': 1.6, 'o22ai': 2.3, 'o22a': 1.8, 'o211ai': 2.7,
       'o311ai': 3.0}
MISC = {'ha': 2.0, 'fa': 5.0, 'mux2': 2.0, 'mux2i': 2.0, 'mux4': 3.0,
        'xor2': 4.0, 'xnor2': 4.0, 'inv': 1.0, 'buf': 1.0,
        'and2': 1.33, 'and3': 1.67, 'and4': 2.0, 'or2': 1.33, 'or3': 1.67,
        'conb': 0.0, 'diode': 0.0, 'fill': 0.0, 'decap': 0.0, 'tap': 0.0}


def g_of(t):
    if t.startswith(('df', 'edf', 'sdf')):      # flip-flops: endpoints
        return None
    m = re.match(r'nand(\d)', t)
    if m: return (int(m.group(1)) + 2) / 3
    m = re.match(r'nor(\d)', t)
    if m: return (2 * int(m.group(1)) + 1) / 3
    for k, v in MISC.items():
        if t.startswith(k):
            return v
    for k in AOI:
        if t.startswith(k): return AOI[k]
    for k in OAI:
        if t.startswith(k): return OAI[k]
    return None


def analyze(rpt):
    t = open(rpt, encoding='utf-8', errors='ignore').read()
    paths = re.split(r'\n(?=Startpoint:)', t)[1:]
    lv, ge, per_g = [], [], []
    for p in paths:
        celltypes = []
        for l in p.splitlines():
            mo = re.match(r'^\s*([\d.]+)\s+([\d.]+)\s+[\^v]\s+\S+/(\S+)\s+\(sky130_fd_sc_hd__(\S+)\)', l)
            if mo and mo.group(3) in ('X', 'Y', 'SUM', 'CO', 'CON', 'S'):
                celltypes.append(mo.group(4))
        gs = [g for g in (g_of(c) for c in celltypes) if g is not None]
        if not gs:
            continue
        lv.append(len(gs))
        ge.extend(gs)
        per_g.append(sum(gs) / len(gs))
    return lv, ge, per_g


for run in ('p7_delay', 'p7_area'):
    lv, ge, per_g = analyze(f'{P}/{run}_allpaths.rpt')
    print(f'==== {run}  ({len(lv)} paths) ====')
    print(f'  avg logic levels/path      : {sum(lv)/len(lv):.2f}   (min {min(lv)}, max {max(lv)})')
    print(f'  avg logical effort / path  : {sum(per_g)/len(per_g):.2f}')
    print(f'  avg logical effort / stage : {sum(ge)/len(ge):.2f}  (over {len(ge)} cells)')
    from collections import Counter
    c = Counter()
    for g in ge:
        c[round(g, 2)] += 1
    print('  g distribution:', dict(sorted(c.items())))
    print()
