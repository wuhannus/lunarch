#!/usr/bin/env python3
"""AI-driven PPA sweep: timing-vs-power Pareto (dependency-free SVG).

IMPORTANT: OpenSTA reports power at the run's *constrained* clock, not at the
achieved fmax.  Comparing those raw numbers across points with different clock
targets is unfair.  The canonical figure therefore normalizes every point's
power to the baseline clock (7.0 ns = 142.857 MHz):

    P_ref = P_leakage + (P_internal + P_switching) * (clk_ns / 7.0)

(leakage is frequency independent; all dynamic power scales with frequency).
The as-run figure is kept as pareto_ppa_asrun.svg for reference.
"""
import os
import re

BASE = "/mnt/d/opencode/lunarch/flow/opt"
OUTDIR = os.path.join(BASE, "sweep")
F_REF = 1000.0 / 7.0          # 142.857 MHz

# name, clk_ns, abc_area, fmax_mhz, cells, report (relative to BASE)
PTS = [
    ("p5_delay",   5.0, 0, 153.37, 5689, "timing_diematch/6_finish.rpt"),
    ("p7_delay",   7.0, 0, 147.93, 5520, "sweep/p7_delay.rpt"),
    ("p10_delay", 10.0, 0, 122.07, 5209, "sweep/p10_delay.rpt"),
    ("p7_area",    7.0, 1, 155.37, 8919, "sweep/p7_area.rpt"),
    ("p10_area",  10.0, 1, 127.49, 8859, "sweep/p10_area.rpt"),
    ("p20_area",  20.0, 1, 132.50, 8800, "power_diematch/6_finish.rpt"),
]


def parse_power(path):
    """Return (internal, switching, leakage, total) in Watts."""
    tot = None
    for ln in open(path).read().splitlines():
        if ln.strip().startswith("Total") and "e-0" in ln:
            tot = ln
    nums = re.findall(r"[-+0-9.]+e[-+][0-9]+", tot)
    return [float(x) for x in nums[:4]]


def load():
    rows = []
    for name, clk, area, fmax, cells, rel in PTS:
        p = os.path.join(BASE, rel)
        internal, switching, leakage, total = parse_power(p)
        dyn = internal + switching
        pref = leakage + dyn * (clk / 7.0)
        rows.append(dict(name=name, clk=clk, area=area, fmax=fmax, cells=cells,
                         internal=internal, switching=switching,
                         leakage=leakage, total=total, pref=pref))
    return rows


def pareto(rows, key):
    front = []
    for p in rows:
        if not any(q is not p and q["fmax"] >= p["fmax"] and q[key] <= p[key]
                   and (q["fmax"] > p["fmax"] or q[key] < p[key]) for q in rows):
            front.append(p)
    front.sort(key=lambda p: p["fmax"])
    return front


def render(rows, key, y0, y1, ystep, title, ycaption, out):
    front = pareto(rows, key)
    W, H = 1000, 680
    ML, MR, MT, MB = 96, 40, 64, 74
    pw, ph = W - ML - MR, H - MT - MB
    x0, x1 = 115, 165
    def X(v): return ML + (v - x0) / (x1 - x0) * pw
    def Y(v): return MT + (y1 - v) / (y1 - y0) * ph

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         'font-family="Helvetica,Arial" font-size="13">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{W/2}" y="30" text-anchor="middle" font-size="17" '
         'font-weight="bold" fill="#1f3a5f">' + title + '</text>',
         f'<line x1="{ML}" y1="{MT+ph}" x2="{ML+pw}" y2="{MT+ph}" stroke="#666"/>',
         f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+ph}" stroke="#666"/>']

    v = 120
    while v <= 165:
        s.append(f'<line x1="{X(v):.0f}" y1="{MT}" x2="{X(v):.0f}" y2="{MT+ph}" stroke="#eef2f7"/>')
        s.append(f'<line x1="{X(v):.0f}" y1="{MT+ph}" x2="{X(v):.0f}" y2="{MT+ph+5}" stroke="#999"/>')
        s.append(f'<text x="{X(v):.0f}" y="{MT+ph+20}" text-anchor="middle" fill="#555">{v}</text>')
        v += 5
    yv = y0
    while yv <= y1 + 1e-9:
        s.append(f'<line x1="{ML}" y1="{Y(yv):.0f}" x2="{ML+pw}" y2="{Y(yv):.0f}" stroke="#eef2f7"/>')
        s.append(f'<line x1="{ML-5}" y1="{Y(yv):.0f}" x2="{ML}" y2="{Y(yv):.0f}" stroke="#999"/>')
        lab = f'{yv:.1f}' if ystep < 1 else f'{yv:.0f}'
        s.append(f'<text x="{ML-10}" y="{Y(yv)+4:.0f}" text-anchor="end" fill="#555">{lab}</text>')
        yv += ystep

    s.append(f'<text x="{ML+pw/2:.0f}" y="{H-22}" text-anchor="middle" fill="#1f3a5f">'
             'fmax (MHz) \u2192 faster &amp; better</text>')
    s.append(f'<text x="26" y="{MT+ph/2:.0f}" text-anchor="middle" fill="#1f3a5f" '
             f'transform="rotate(-90 26 {MT+ph/2:.0f})">' + ycaption + '</text>')

    s.append('<polyline points="' +
             ' '.join(f'{X(p["fmax"]):.0f},{Y(p[key]*1e3):.0f}' for p in front) +
             '" fill="none" stroke="#1E7A46" stroke-width="2" stroke-dasharray="6 4"/>')

    for p in rows:
        col = '#4A86E8' if p["area"] == 0 else '#E06666'
        cx, cy = X(p["fmax"]), Y(p[key]*1e3)
        if p["area"] == 0:
            s.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="6" fill="{col}" stroke="#1f3a5f" stroke-width="1"/>')
        else:
            s.append(f'<rect x="{cx-6:.0f}" y="{cy-6:.0f}" width="12" height="12" fill="{col}" stroke="#1f3a5f" stroke-width="1"/>')
        s.append(f'<text x="{cx+9:.0f}" y="{cy-8:.0f}" fill="#1b2733">{p["name"]}</text>')

    lx, ly = ML + 26, MT + 18
    s.append(f'<circle cx="{lx}" cy="{ly}" r="6" fill="#4A86E8" stroke="#1f3a5f"/>')
    s.append(f'<text x="{lx+14}" y="{ly+4}" fill="#333">delay ABC (ABC_AREA=0)</text>')
    s.append(f'<rect x="{lx-6}" y="{ly+24-6}" width="12" height="12" fill="#E06666" stroke="#1f3a5f"/>')
    s.append(f'<text x="{lx+14}" y="{ly+28}" fill="#333">area ABC (ABC_AREA=1)</text>')
    s.append(f'<line x1="{lx-6}" y1="{ly+48}" x2="{lx+8}" y2="{ly+48}" stroke="#1E7A46" stroke-width="2" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{lx+14}" y="{ly+52}" fill="#333">Pareto front</text>')
    s.append('</svg>')
    open(out, 'w').write('\n'.join(s))

    print(f'--- {os.path.basename(out)} ---')
    for p in rows:
        print(f'  {p["name"]:10} clk={p["clk"]:4.0f}ns fmax={p["fmax"]:7.2f} '
              f'as-run={p["total"]*1e3:6.2f}mW  ref(142.9MHz)={p["pref"]*1e3:6.2f}mW')
    print('  Pareto:', [(p["name"], round(p["fmax"], 2), round(p[key]*1e3, 2))
                        for p in front])


rows = load()
render(rows, "pref", 18.0, 21.5, 0.5,
       'AI-driven PPA sweep \u2014 riscv32i on sky130 (power normalized to 142.9 MHz baseline)',
       'total power @ 142.9 MHz (mW) \u2192 lower is better',
       os.path.join(OUTDIR, "pareto_ppa.svg"))
render(rows, "total", 0.0, 32.0, 4.0,
       'AI-driven PPA sweep \u2014 riscv32i on sky130 (AS-RUN power, unfair across clocks)',
       'total power at each run\u2019s own clock (mW)',
       os.path.join(OUTDIR, "pareto_ppa_asrun.svg"))
print('wrote pareto_ppa.svg and pareto_ppa_asrun.svg')
