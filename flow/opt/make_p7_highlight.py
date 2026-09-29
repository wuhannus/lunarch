#!/usr/bin/env python3
"""Build three highlighted views for the p7_area die:
  (1) loops diagram (write-back loop vs PC/branch loop)
  (2) extra nand2/nand3/inv cells highlighted on the die
  (3) cell-density heatmap of the die
"""
import re
from collections import defaultdict, deque

P = '/mnt/d/opencode/lunarch/flow/opt/paths/p7_area'
DEF = f'{P}/6_final.def'
V = f'{P}/6_final.v'
OUT = '/mnt/d/opencode/lunarch/flow/opt'

# ---------- classification: cell -> endpoint loop ----------
FF = ('df', 'edf', 'sdf')
def build(vfile):
    t = open(vfile, encoding='utf-8', errors='ignore').read()
    cells = {}
    for m in re.finditer(r'sky130_fd_sc_hd__([a-z0-9_]+)\s+(\\?\S+?)\s*\((.*?)\);', t, re.S):
        typ, inst = m.group(1), m.group(2).replace('\\', '')
        pins = {pm.group(1): pm.group(2).replace('\\', '')
                for pm in re.finditer(r'\.(\w+)\s*\(\s*([^)\s]+)\s*\)', m.group(3))}
        cells[inst] = (typ, pins)
    cons = defaultdict(list)
    for inst, (typ, pins) in cells.items():
        for p, n in pins.items():
            cons[n].append((inst, p))
    def loop_of(inst):
        seen = {inst}; q = deque(
            n for p, n in cells[inst][1].items() if p in ('X','Y','SUM','CO','Q','CON','S'))
        while q:
            n = q.popleft()
            for c, pin in cons.get(n, []):
                typ = cells[c][0]
                if any(typ.startswith(k) for k in FF) and pin == 'D':
                    return 'wb' if 'rf.rf' in c else 'pc' if 'pcreg' in c else None
                if c not in seen:
                    seen.add(c)
                    for p2, n2 in cells[c][1].items():
                        if p2 in ('X','Y','SUM','CO','CON','S'):
                            q.append(n2)
        return None
    return {i: (t_, loop_of(i)) for i, (t_, _) in cells.items()}

# ---------- placements ----------
die = None; place = {}
for line in open(DEF, encoding='utf-8', errors='ignore'):
    if die is None and line.startswith('DIEAREA'):
        mm = re.search(r'\(\s*\d+\s+\d+\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)', line)
        if mm: die = [int(mm.group(1))/1000, int(mm.group(2))/1000]
        continue
    mm = re.match(r'^\s*-\s+(\S+)\s+(\S+)\s+\+.*?PLACED\s+\(\s*(\d+)\s+(\d+)\s*\)', line)
    if mm and 'fill' not in mm.group(2) and 'decap' not in mm.group(2):
        place[mm.group(1).replace('\\','')] = (int(mm.group(3))/1000, int(mm.group(4))/1000)

cls = build(V)
W, H = die
S = 900; sc = S / W

# ============ (1) loops diagram ============
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="980" height="560" font-family="Helvetica,Arial" font-size="13">',
       '<rect width="980" height="560" fill="#fff"/>',
       '<text x="490" y="28" text-anchor="middle" font-size="17" font-weight="bold" fill="#1f3a5f">'
       'Two sequential loops (where the extra nand2/nand3/inv cells live)</text>']
def box(x, y, w, h, txt, fill, sub=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#1f3a5f"/>')
    svg.append(f'<text x="{x+w/2}" y="{y+h/2+4}" text-anchor="middle" fill="#1b2733" font-weight="bold">{txt}</text>')
    if sub:
        svg.append(f'<text x="{x+w/2}" y="{y+h+16}" text-anchor="middle" fill="#555" font-size="11">{sub}</text>')
# write-back loop (red)
box(60, 80, 150, 50, 'regfile read (RF)', '#f8d7da')
box(250, 80, 120, 50, 'ALU / shift', '#f8d7da')
box(410, 80, 120, 50, 'write-back mux', '#f8d7da')
box(570, 80, 150, 50, 'regfile write (RF)', '#f8d7da')
svg.append('<path d="M210 105 H250" stroke="#c0392b" stroke-width="2" marker-end="url(#a)"/>')
svg.append('<path d="M370 105 H410" stroke="#c0392b" stroke-width="2" marker-end="url(#a)"/>')
svg.append('<path d="M530 105 H570" stroke="#c0392b" stroke-width="2" marker-end="url(#a)"/>')
svg.append('<path d="M645 130 C645 200 135 200 135 130" fill="none" stroke="#c0392b" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a)"/>')
svg.append('<text x="390" y="215" text-anchor="middle" fill="#c0392b" font-weight="bold">WRITE-BACK LOOP (PG2/3/4) — ~53% of extra cells</text>')
# PC / branch loop (blue)
box(60, 300, 150, 50, 'pcreg (PC)', '#d9e6fb')
box(250, 300, 120, 50, 'PC +4 / +imm', '#d9e6fb')
box(410, 300, 120, 50, 'branch compare', '#d9e6fb')
box(570, 300, 150, 50, 'PC mux (pcsrc)', '#d9e6fb')
svg.append('<path d="M210 325 H250" stroke="#4a86e8" stroke-width="2" marker-end="url(#a)"/>')
svg.append('<path d="M370 325 H410" stroke="#4a86e8" stroke-width="2" marker-end="url(#a)"/>')
svg.append('<path d="M530 325 H570" stroke="#4a86e8" stroke-width="2" marker-end="url(#a)"/>')
svg.append('<path d="M645 350 C645 420 135 420 135 350" fill="none" stroke="#4a86e8" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a)"/>')
svg.append('<text x="390" y="435" text-anchor="middle" fill="#4a86e8" font-weight="bold">PC / BRANCH LOOP (PG1/5) — ~47% of extra cells</text>')
svg.append('<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">'
           '<path d="M0,0 L7,3 L0,6 z" fill="#1f3a5f"/></marker></defs>')
svg.append('<text x="490" y="510" text-anchor="middle" fill="#555" font-size="12">'
           'extra cells feed the flip-flops of BOTH loops: +1,376 nand2 / +536 nand3 / +383 inv (RF) and +1,166 / +498 / +362 (PC)</text>')
svg.append('</svg>')
open(f'{OUT}/p7_area_loops.svg', 'w').write('\n'.join(svg))

# ============ (2) extra cells highlighted on die ============
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{S}" height="{S}" font-family="Helvetica,Arial">',
       f'<rect x="0" y="0" width="{W}" height="{H}" fill="#f6f8fb" stroke="#c4cfdd"/>']
for name, (x, y) in place.items():
    typ = cls.get(name, ('', None))[0]
    extra = typ.startswith(('nand2', 'nand3', 'inv'))
    if extra:
        continue
    svg.append(f'<rect x="{x-0.5:.2f}" y="{y-0.5:.2f}" width="1" height="1" fill="#dbe3ee"/>')
nex = 0
for name, (x, y) in place.items():
    typ = cls.get(name, ('', None))[0]
    if typ.startswith(('nand2', 'nand3', 'inv')):
        loop = cls.get(name, ('', None))[1]
        col = '#c0392b' if typ.startswith('nand2') else '#e69138' if typ.startswith('nand3') else '#6aa84f'
        svg.append(f'<rect x="{x-0.65:.2f}" y="{y-0.65:.2f}" width="1.3" height="1.3" fill="{col}"/>')
        nex += 1
svg.append('</svg>')
open(f'{OUT}/p7_area_extra_cells.svg', 'w').write('\n'.join(svg))

# ============ (3) density heatmap ============
G = 40
grid = [[0]*G for _ in range(G)]
for x, y in place.values():
    grid[min(int(y/H*G), G-1)][min(int(x/W*G), G-1)] += 1
mx = max(max(r) for r in grid) or 1
cell = S / G
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{S+120}" height="{S+50}" font-family="Helvetica,Arial" font-size="12">',
       '<rect width="100%" height="100%" fill="#fff"/>',
       f'<text x="{(S+120)/2}" y="20" text-anchor="middle" font-size="15" font-weight="bold" fill="#1f3a5f">'
       'p7_area cell-density map ('+str(len(place))+' placed cells, 40x40 grid)</text>']
for r in range(G):
    for c in range(G):
        v = grid[r][c] / mx
        # blue -> red heat
        R = int(30 + 225*v); Gc = int(80 + 120*(1-v)); B = int(200 - 180*v)
        svg.append(f'<rect x="{c*cell:.1f}" y="{30+r*cell:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                   f'fill="rgb({R},{Gc},{B})" stroke="none"/>')
svg.append(f'<rect x="0" y="30" width="{S}" height="{S}" fill="none" stroke="#1f3a5f"/>')
svg.append(f'<text x="{S+12}" y="30" fill="#1b2733">dense</text>')
svg.append(f'<rect x="{S+12}" y="40" width="16" height="16" fill="rgb(255,80,20)"/>')
svg.append(f'<text x="{S+10}" y="{S+20}" fill="#1b2733">sparse</text>')
svg.append(f'<rect x="{S+12}" y="{S-6}" width="16" height="16" fill="rgb(30,200,200)"/>')
svg.append('</svg>')
open(f'{OUT}/p7_area_density.svg', 'w').write('\n'.join(svg))

print('die', die, 'placed', len(place), 'extra nand2/nand3/inv', nex)
