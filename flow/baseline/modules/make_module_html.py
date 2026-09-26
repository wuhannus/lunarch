#!/usr/bin/env python3
"""Wrap the module-coloured layout into a self-contained HTML page."""
import os, html

D = '/mnt/d/opencode/lunarch/flow/baseline/modules'
svg = open(os.path.join(D, '6_final_modules.svg'), encoding='utf-8').read()
svg = svg.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()

rows = []
for line in open(os.path.join(D, 'module_counts.txt'), encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if len(parts) == 3:
        rows.append((parts[0], parts[1], int(parts[2])))
total = sum(c for _, _, c in rows)

def row(name, col, c):
    pct = 100.0 * c / total
    return (f'<tr><td><span class="sw" style="background:{col}"></span></td>'
            f'<td>{html.escape(name)}</td><td class="num">{c}</td><td class="num">{pct:.1f}%</td></tr>')

legend = '\n'.join(row(n, c, v) for n, c, v in rows)

HTML = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>riscv — module-coloured final layout</title>
<style>
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#eef2f7;color:#1b2733}}
  header{{background:#1f3a5f;color:#fff;padding:10px 18px}}
  header h1{{margin:0;font-size:16px}}
  header .sub{{font-size:12px;opacity:.9;margin-top:3px}}
  #app{{display:flex;gap:14px;padding:14px;align-items:flex-start}}
  .fig{{background:#fff;border:1px solid #d6dee8;border-radius:10px;padding:8px;flex:0 0 auto}}
  .fig svg{{display:block;width:820px;height:auto}}
  .side{{flex:1;min-width:300px}}
  .card{{background:#fff;border:1px solid #d6dee8;border-radius:10px;padding:12px 14px;margin-bottom:12px}}
  .card h2{{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:#5b6b7d}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th,td{{text-align:left;padding:4px 6px;border-bottom:1px solid #eef2f7}}
  th{{font-size:11px;color:#5b6b7d;text-transform:uppercase}}
  td.num{{text-align:right;font-variant-numeric:tabular-nums}}
  .sw{{display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid #c4cfdd;vertical-align:-2px}}
  .note{{font-size:12px;color:#44546a;line-height:1.5}}
  code{{background:#f2f6fc;padding:1px 4px;border-radius:3px}}
</style></head>
<body>
<header>
  <h1>riscv (sky130hd/riscv32i) — module-coloured final layout</h1>
  <div class="sub">die 377.8 × 377.8 µm · 5,535 placed cells · clock 7.0&nbsp;ns · setup WNS 0.00&nbsp;ns · DRC 0 · LVS match</div>
</header>
<div id="app">
  <div class="fig">{svg}</div>
  <div class="side">
    <div class="card">
      <h2>Module legend (cells)</h2>
      <table><thead><tr><th></th><th>Module</th><th class="num">Cells</th><th class="num">Share</th></tr></thead>
      <tbody>{legend}</tbody></table>
    </div>
    <div class="card">
      <h2>Observations</h2>
      <div class="note">
        <ul>
          <li><b>Register file</b> (red) occupies the <b>left third</b> of the die.</li>
          <li><b>ALU</b> (blue) is a dense cluster on the <b>right side</b>.</li>
          <li>Address adders (orange) and datapath muxes (purple) sit between them.</li>
          <li>Layout is consistent with the PG2 critical loop (regfile → ALU → regfile):
              cell-delay dominated, so the split placement is not a timing problem
              (wire delay &lt; 0.02 ns per path).</li>
        </ul>
      </div>
    </div>
    <div class="card">
      <h2>How the colours were derived</h2>
      <div class="note">
        The flow is flat-synthesised (<code>synth -flatten</code>), so most cells are
        renamed <code>_NNNN_</code>. The flow was re-run with
        <code>SYNTH_HIER_SEPARATOR=__</code> so net names keep their instance path
        (<code>dp__rf__…</code>, <code>dp__alu__…</code>, <code>c__ad__…</code>);
        each cell is assigned to the module of the first module-prefixed net it touches.
        <br><br>
        <b>Coverage: 2,353 / 5,535 cells (43%)</b> carry an explicit module label —
        the large name-preserving blocks. The grey remainder is the fine datapath
        logic (shifter, comparator, sign-ext, branch muxes) plus clock/resizer/fill,
        whose nets were renamed during <code>opt</code>.
      </div>
    </div>
  </div>
</div>
</body></html>'''

out = os.path.join(D, 'index.html')
open(out, 'w', encoding='utf-8').write(HTML)
print('wrote', out, len(HTML), 'bytes;', total, 'cells')
