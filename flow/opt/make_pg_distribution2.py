#!/usr/bin/env python3
"""Classify cells by the FF/port their forward cone reaches, then map that
endpoint to a path group. Report nand2/nand3/inv distribution per PG."""
import re
from collections import defaultdict, deque

P = '/mnt/d/opencode/lunarch/flow/opt/paths'
V = {'p7_delay': f'{P}/p7_delay/6_final.v', 'p7_area': f'{P}/p7_area/6_final.v'}
INTEREST = ('nand2', 'nand3', 'inv')


def endpoint_pg(name):
    if 'rf.rf' in name:
        return 'PG2/3/4 write-back (regfile)'
    if 'pcreg' in name:
        return 'PG1/5 PC / branch'
    if name.startswith('aluout'):
        return 'PG8 result-out'
    if name.startswith('writedata'):
        return 'PG4 store-out'
    if name.startswith('pc'):
        return 'PG1 pc-out'
    if 'epc' in name or 'SEPC' in name:
        return 'PG8 exception (SEPC)'
    if name in ('memwrite', 'memread', 'suspend'):
        return 'PG6/PG4 control-out'
    return None


def scan(vfile):
    t = open(vfile, encoding='utf-8', errors='ignore').read()
    cells = {}          # inst -> (type, {pin:net})
    for m in re.finditer(r'sky130_fd_sc_hd__([a-z0-9_]+)\s+(\\?\S+?)\s*\((.*?)\);', t, re.S):
        typ, inst = m.group(1), m.group(2).replace('\\', '')
        pins = {pm.group(1): pm.group(2).replace('\\', '')
                for pm in re.finditer(r'\.(\w+)\s*\(\s*([^)\s]+)\s*\)', m.group(3))}
        cells[inst] = (typ, pins)
    # net -> list of (cell, pin) consumers
    cons = defaultdict(list)
    for inst, (typ, pins) in cells.items():
        for p, n in pins.items():
            cons[n].append((inst, p))
    FF = ('df', 'edf', 'sdf')

    def endpoint_of(inst):
        # forward BFS from inst outputs to first FF D-pin / output port
        seen = {inst}
        q = deque()
        for p, n in cells[inst][1].items():
            if p in ('X', 'Y', 'SUM', 'CO', 'Q', 'CON', 'S'):
                q.append(n)
        while q:
            n = q.popleft()
            for (c, pin) in cons.get(n, []):
                typ = cells[c][0]
                if any(typ.startswith(k) for k in FF) and pin == 'D':
                    return c
                if c not in seen:
                    seen.add(c)
                    for p2, n2 in cells[c][1].items():
                        if p2 in ('X', 'Y', 'SUM', 'CO', 'CON', 'S'):
                            q.append(n2)
        return None

    per = defaultdict(lambda: defaultdict(int)); unmatched = defaultdict(int)
    for inst, (typ, pins) in cells.items():
        if not any(typ.startswith(k) for k in INTEREST):
            continue
        key = 'nand2' if typ.startswith('nand2') else 'nand3' if typ.startswith('nand3') else 'inv'
        ep = endpoint_of(inst)
        pg = endpoint_pg(ep) if ep else None
        (per[pg] if pg else unmatched)[key] += 1
    return per, unmatched


for run in ('p7_delay', 'p7_area'):
    per, unmatched = scan(V[run])
    print(f'==== {run} ====')
    print(f'{"endpoint -> path group":36} {"nand2":>7} {"nand3":>7} {"inv":>7}')
    for pg in sorted(per, key=lambda k: -sum(per[k].values())):
        r = per[pg]
        print(f'{pg:36} {r.get("nand2",0):7} {r.get("nand3",0):7} {r.get("inv",0):7}')
    print(f'{"unmatched":36} {unmatched.get("nand2",0):7} {unmatched.get("nand3",0):7} {unmatched.get("inv",0):7}')
    print()
