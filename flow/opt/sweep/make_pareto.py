#!/usr/bin/env python3
"""AI-driven PPA sweep: build the timing-vs-power Pareto front (dependency-free SVG)."""
OUT = '/mnt/d/opencode/lunarch/flow/opt/sweep/pareto_ppa.svg'
# name, clk_ns, abc_area, fmax_mhz, power_mw, cells, note
pts = [
    ("p5_delay",   5.0,  0, 153.37, 29.30, 5689, "delay ABC, 5 ns rc"),
    ("p7_delay",   7.0,  0, 147.93, 19.70, 5520, "delay ABC, 7 ns (baseline)"),
    ("p10_delay", 10.0,  0, 122.07, 13.40, 5209, "delay ABC, 10 ns"),
    ("p7_area",    7.0,  1, 155.37, 18.80, 8919, "area ABC, 7 ns"),
    ("p10_area",  10.0,  1, 127.49, 13.30, 8859, "area ABC, 10 ns"),
    ("p20_area",  20.0,  1, 132.50,  6.54, 8800, "area ABC, 20 ns (min power)"),
]
front = [p for p in pts if not any(q[3] >= p[3] and q[4] <= p[4] and (q[3] > p[3] or q[4] < p[4]) for q in pts)]
front.sort(key=lambda p: p[3])

W, H = 1000, 660
ML, MR, MT, MB = 90, 40, 60, 70
pw, ph = W - ML - MR, H - MT - MB
xs = [p[3] for p in pts]; ys = [p[4] for p in pts]
x0, x1 = 115, 165
y0, y1 = 0, 32
def X(v): return ML + (v - x0) / (x1 - x0) * pw
def Y(v): return MT + (y1 - v) / (y1 - y0) * ph

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial" font-size="13">']
s.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
s.append(f'<text x="{W/2}" y="28" text-anchor="middle" font-size="17" font-weight="bold" fill="#1f3a5f">'
         'AI-driven PPA sweep \u2014 riscv32i on sky130 (same 376.6 \u00b5m die)</text>')
# axes
s.append(f'<line x1="{ML}" y1="{MT+ph}" x2="{ML+pw}" y2="{MT+ph}" stroke="#666"/>')
s.append(f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+ph}" stroke="#666"/>')
for v in range(120, 161, 5):
    s.append(f'<line x1="{X(v):.0f}" y1="{MT+ph}" x2="{X(v):.0f}" y2="{MT+ph+5}" stroke="#999"/>')
    s.append(f'<text x="{X(v):.0f}" y="{MT+ph+20}" text-anchor="middle" fill="#555">{v}</text>')
for v in range(0, 33, 4):
    s.append(f'<line x1="{ML-5}" y1="{Y(v):.0f}" x2="{ML}" y2="{Y(v):.0f}" stroke="#999"/>')
    s.append(f'<text x="{ML-10}" y="{Y(v)+4:.0f}" text-anchor="end" fill="#555">{v}</text>')
for v in range(120, 161, 5):
    s.append(f'<line x1="{X(v):.0f}" y1="{MT}" x2="{X(v):.0f}" y2="{MT+ph}" stroke="#eef2f7"/>')
for v in range(0, 33, 4):
    s.append(f'<line x1="{ML}" y1="{Y(v):.0f}" x2="{ML+pw}" y2="{Y(v):.0f}" stroke="#eef2f7"/>')
s.append(f'<text x="{ML+pw/2:.0f}" y="{H-20}" text-anchor="middle" fill="#1f3a5f">fmax (MHz) \u2192 faster</text>')
s.append(f'<text x="24" y="{MT+ph/2:.0f}" text-anchor="middle" fill="#1f3a5f" '
         f'transform="rotate(-90 24 {MT+ph/2:.0f})">total power (mW) \u2192 lower is better</text>')
# Pareto line
s.append('<polyline points="' + ' '.join(f'{X(p[3]):.0f},{Y(p[4]):.0f}' for p in front) +
         '" fill="none" stroke="#1E7A46" stroke-width="2" stroke-dasharray="6 4"/>')
# points
for p in pts:
    col = '#4A86E8' if p[2] == 0 else '#E06666'
    mk = ('circle', 6) if p[2] == 0 else ('rect', 6)
    if mk[0] == 'circle':
        s.append(f'<circle cx="{X(p[3]):.0f}" cy="{Y(p[4]):.0f}" r="{mk[1]}" fill="{col}" stroke="#1f3a5f" stroke-width="1"/>')
    else:
        s.append(f'<rect x="{X(p[3])-mk[1]:.0f}" y="{Y(p[4])-mk[1]:.0f}" width="{2*mk[1]}" height="{2*mk[1]}" fill="{col}" stroke="#1f3a5f" stroke-width="1"/>')
    s.append(f'<text x="{X(p[3])+9:.0f}" y="{Y(p[4])-8:.0f}" fill="#1b2733">{p[0]}</text>')
# legend (lower-left)
lx, ly = ML + 30, MT + ph - 82
s.append(f'<circle cx="{lx}" cy="{ly}" r="6" fill="#4A86E8" stroke="#1f3a5f"/>')
s.append(f'<text x="{lx+14}" y="{ly+4}" fill="#333">delay ABC (ABC_AREA=0)</text>')
s.append(f'<rect x="{lx-6}" y="{ly+18-6}" width="12" height="12" fill="#E06666" stroke="#1f3a5f"/>')
s.append(f'<text x="{lx+14}" y="{ly+22}" fill="#333">area ABC (ABC_AREA=1)</text>')
s.append(f'<line x1="{lx-6}" y1="{ly+38}" x2="{lx+8}" y2="{ly+38}" stroke="#1E7A46" stroke-width="2" stroke-dasharray="6 4"/>')
s.append(f'<text x="{lx+14}" y="{ly+42}" fill="#333">Pareto front</text>')
s.append('</svg>')
open(OUT, 'w').write('\n'.join(s))
print('Pareto front:', [(p[0], p[3], p[4]) for p in front])
print('dominated:  ', [p[0] for p in pts if p not in front])
print('wrote', OUT)
