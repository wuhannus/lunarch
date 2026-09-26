#!/usr/bin/env python3
"""Summarize total routed wire length from the final DEF (per metal layer)."""
import re, json

DEF = '/home/lunarch/orfs-clean/flow/results/sky130hd/riscv32i/base/6_final.def'
OUT = '/mnt/d/opencode/wirelength.json'
UNITS = 1000.0  # DEF units per micron

text = open(DEF, encoding='utf-8', errors='ignore').read()


def section(name):
    m = re.search(r'\n' + name + r' \d+ ;(.*?)\nEND ' + name, text, re.S)
    return m.group(1) if m else ''


def scan(body):
    by, vias, stmts = {}, 0, 0
    for stmt in re.findall(r'\+[^;]*;', body, re.S):
        stmts += 1
        vias += len(re.findall(r'\)\s+(?!met[1-5]\b|li1\b|NEW\b)([A-Za-z_]\w*)', stmt))
        parts = re.split(r'\b(met[1-5]|li1)\b', stmt)
        for i in range(1, len(parts), 2):
            lay = parts[i]
            pts = []
            for a, b in re.findall(r'\(\s*(\d+|\*)\s+(\d+|\*)\s*\)', parts[i + 1]):
                x = pts[-1][0] if (a == '*' and pts) else (int(a) if a != '*' else 0)
                y = pts[-1][1] if (b == '*' and pts) else (int(b) if b != '*' else 0)
                pts.append((x, y))
            L = sum(abs(pts[j + 1][0] - pts[j][0]) + abs(pts[j + 1][1] - pts[j][1])
                    for j in range(len(pts) - 1))
            by[lay] = by.get(lay, 0) + L
    return by, vias, stmts


sig, sig_vias, sig_stmts = scan(section('NETS'))
pwr, pwr_vias, pwr_stmts = scan(section('SPECIALNETS'))

die = [376.625, 376.625]
li = [l for l in ['li1', 'met1', 'met2', 'met3', 'met4', 'met5'] if l in sig or l in pwr]

out = dict(die_um=die, units=UNITS,
           signal=dict(by_layer={k: round(v / UNITS, 1) for k, v in sig.items()},
                       total_um=round(sum(sig.values()) / UNITS, 1),
                       vias=sig_vias, routed_statements=sig_stmts),
           power=dict(by_layer={k: round(v / UNITS, 1) for k, v in pwr.items()},
                      total_um=round(sum(pwr.values()) / UNITS, 1),
                      vias=pwr_vias, routed_statements=pwr_stmts),
           combined_total_um=round(sum(sig.values()) / UNITS + sum(pwr.values()) / UNITS, 1))
json.dump(out, open(OUT, 'w'), indent=1)

print('die %.3f x %.3f um' % (die[0], die[1]))
print('SIGNAL routing:')
for l in li:
    if l in sig:
        print('   %-5s %10.1f um' % (l, sig[l] / UNITS))
print('   %-5s %10.1f um   (%d vias, %d statements)' % ('TOTAL', sum(sig.values()) / UNITS, sig_vias, sig_stmts))
print('POWER routing (specialnets):')
for l in li:
    if l in pwr:
        print('   %-5s %10.1f um' % (l, pwr[l] / UNITS))
print('   %-5s %10.1f um   (%d vias, %d statements)' % ('TOTAL', sum(pwr.values()) / UNITS, pwr_vias, pwr_stmts))
print('COMBINED %10.1f um' % (sum(sig.values()) / UNITS + sum(pwr.values()) / UNITS))
print('->', OUT)
