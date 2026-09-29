#!/usr/bin/env python3
"""Build DONT_USE_CELLS lists that cap logical effort, and print them."""
import re, sys

LIB = '/home/lunarch/orfs-clean/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
cells = re.findall(r'^\s*cell\s*\(\s*"?\s*([A-Za-z0-9_]+)\s*"?\s*\)', open(LIB, encoding='utf-8', errors='ignore').read(), re.M)
cells = sorted(set(cells))
print('total cells', len(cells))


def g_of(t):
    t = t.replace('sky130_fd_sc_hd__', '')
    if t.startswith(('dfxtp', 'dfrtp', 'dfstp', 'dfbbn', 'edfxtp', 'sdfxtp',
                     'sdfrtp', 'conb', 'fill', 'decap', 'tap', 'diode', 'antenna')):
        return 0.0                     # sequential / physical: always allowed
    if t.startswith(('inv', 'buf', 'clkbuf', 'clkinv', 'clkdlybuf', 'probe')):
        return 1.0
    m = re.match(r'nand(\d)', t)
    if m: return (int(m.group(1)) + 2) / 3
    m = re.match(r'nor(\d)', t)
    if m: return (2 * int(m.group(1)) + 1) / 3
    m = re.match(r'and(\d)', t)
    if m: return (int(m.group(1)) + 2) / 3
    m = re.match(r'or(\d)', t)
    if m: return (int(m.group(1)) + 4) / 3
    for pref, g in [('a21oi', 2.0), ('a21o', 1.6), ('a22oi', 2.3), ('a22o', 1.8),
                    ('a31oi', 2.7), ('a31o', 2.0), ('a41oi', 3.3), ('a211oi', 2.7),
                    ('a221oi', 2.7), ('a311oi', 3.0), ('a2bb2oi', 2.3), ('a2bb2o', 1.8),
                    ('o21ai', 2.0), ('o21a', 1.6), ('o22ai', 2.3), ('o22a', 1.8),
                    ('o211ai', 2.7), ('o311ai', 3.0), ('o2bb2ai', 2.3), ('o2bb2a', 1.8),
                    ('mux2i', 2.0), ('mux2', 2.0), ('mux4', 3.0),
                    ('xor2', 4.0), ('xnor2', 4.0), ('ha', 2.0), ('fa', 5.0),
                    ('maj3', 3.0), ('aa2', 2.3), ('oa2', 2.3), ('dlxtp', 2.0),
                    ('dlx', 2.0), ('lpflow', 0.0), ('sd', 0.0)]:
        if t.startswith(pref):
            return g
    return None


rows = [(t, g_of(t)) for t in cells]
unknown = [t for t, g in rows if g is None]
print('unknown-classified cells:', unknown[:20], '...', len(unknown))

for cap, tag in [(2.0, 'g2'), (1.5, 'g15')]:
    dont = [t for t, g in rows if g is None or g > cap]
    open(f'/mnt/d/opencode/dontuse_{tag}.txt', 'w').write(' '.join(dont))
    print(f'cap g<={cap}: {len(dont)} cells disallowed')
