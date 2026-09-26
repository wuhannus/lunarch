#!/usr/bin/env python3
"""Colour the final layout by module using the module-path net names produced
by the SYNTH_HIER_SEPARATOR run, then render an SVG/PNG map + a summary."""
import re, json, os

R = '/home/lunarch/orfs-clean/flow/results/sky130hd/riscv32i/base'
V = os.path.join(R, '6_final.v')
DEF = os.path.join(R, '6_final.def')
OUTDIR = '/mnt/d/opencode/lunarch/flow/baseline/modules'

# net-prefix -> (module key, friendly name, colour)
MODMAP = [
    ('dp__rf',        'regfile',   'regfile (32x32 RF)',  '#e06666'),
    ('dp__alu',       'alu',       'alu',                 '#4a86e8'),
    ('dp__pcimm',     'adder',     'adder (pcimm)',       '#f6b26b'),
    ('dp__pcadder',   'adder',     'adder (pcadder)',     '#f6b26b'),
    ('dp__pcreg',     'pc',        'pcreg (PC)',          '#93c47d'),
    ('dp__memsrcmux', 'dpmux',     'datapath muxes',      '#8e7cc3'),
    ('dp__ISRmux',    'dpmux',     'datapath muxes',      '#8e7cc3'),
    ('dp__result2',   'dpmux',     'datapath muxes',      '#8e7cc3'),
    ('dp__pcext',     'dpmux',     'datapath muxes',      '#8e7cc3'),
    ('c__ad',         'aludec',    'aludec (controller)', '#76a5af'),
    ('c__md',         'maindec',   'maindec (controller)', '#a64d79'),
    ('dp__compare',   'magcmp',    'magcompare32',        '#f1c232'),
    ('dp__shift',     'shifter',   'shifter',             '#c27ba0'),
    ('dp__se',        'signext',   'signext',             '#45818e'),
]
def classify(net):
    for pre, key, name, col in MODMAP:
        if net.startswith(pre + '__'):
            return key
    return None

text = open(V, encoding='utf-8', errors='ignore').read()

# cell -> connected nets
cell_nets = {}
for m in re.finditer(r'sky130_fd_sc_hd__[a-z0-9_]+[ \t]+([^ \t(]+)[ \t]*\((.*?)\);', text, re.S):
    inst, ports = m.group(1), m.group(2)
    nets = re.findall(r'\.\w+\s*\(\s*([^)\s]+)\s*\)', ports)
    cell_nets[inst] = [n.replace('\\', '') for n in nets]

# cell -> module
cell_mod = {}
for inst, nets in cell_nets.items():
    for n in nets:
        k = classify(n)
        if k:
            cell_mod[inst] = k
            break

# placements
die = None
place = {}
for line in open(DEF, encoding='utf-8', errors='ignore'):
    if die is None and line.startswith('DIEAREA'):
        mm = re.search(r'\(\s*\d+\s+\d+\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)', line)
        if mm:
            die = [int(mm.group(1)) / 1000.0, int(mm.group(2)) / 1000.0]
        continue
    mm = re.match(r'^\s*-\s+(\S+)\s+(\S+)\s+\+.*?PLACED\s+\(\s*(\d+)\s+(\d+)\s*\)', line)
    if mm:
        name = mm.group(1).replace('\\', '')
        if 'fill' in mm.group(2) or 'decap' in mm.group(2):
            continue
        place[name] = (int(mm.group(3)) / 1000.0, int(mm.group(4)) / 1000.0)

# colour key
key = {}
for pre, k, name, col in MODMAP:
    key.setdefault(k, (name, col))
total = len(place)
counts = {}
S = 1500
sc = S / max(die)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {die[0]} {die[1]}" width="{int(die[0]*sc)}" height="{int(die[1]*sc)}">',
       f'<rect x="0" y="0" width="{die[0]}" height="{die[1]}" fill="#f6f8fb" stroke="#c4cfdd" stroke-width="0.4"/>']
OTHER = '#d9dee6'
for name, (x, y) in place.items():
    k = cell_mod.get(name)
    col = key[k][1] if k else OTHER
    counts[k or 'other'] = counts.get(k or 'other', 0) + 1
    svg.append(f'<rect x="{x-0.6:.2f}" y="{y-0.6:.2f}" width="1.2" height="1.2" fill="{col}"/>')
svg.append('</svg>')
os.makedirs(OUTDIR, exist_ok=True)
open(os.path.join(OUTDIR, '6_final_modules.svg'), 'w').write('\n'.join(svg))

# legend text
lines = []
for k in sorted(counts, key=lambda k: -counts[k]):
    nm, col = key.get(k, ('other / unmapped (flattened opt logic)', OTHER))
    lines.append((nm, col, counts[k]))
with open(os.path.join(OUTDIR, 'module_counts.txt'), 'w') as f:
    for nm, col, c in lines:
        f.write(f'{nm}\t{col}\t{c}\n')

print('die', die, 'placed', total, 'cells with module names', sum(1 for n in cell_mod))
for nm, col, c in lines:
    print(f'  {c:6d}  {col}  {nm}')
