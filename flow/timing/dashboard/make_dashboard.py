#!/usr/bin/env python3
"""Build an interactive HTML timing dashboard for sky130hd/riscv32i.

Parses the detailed report_checks dump (all setup endpoints, full format with
net+input_pin fields) into JSON embedded in a single self-contained HTML file.
"""
import re, json, os
from collections import defaultdict

SRC = '/mnt/d/opencode/dashboard.rpt'
OUTDIR = '/mnt/d/opencode/lunarch/flow/timing/dashboard'
OUT = os.path.join(OUTDIR, 'index.html')


def func_group(start, end):
    if end.startswith('aluout'):
        return 'PG8', 'PG8 result-out', '#e06666'
    if end.startswith('writedata'):
        return 'PG4', 'PG4 store-out', '#93c47d'
    if end.startswith('pc[') or end == 'pc':
        return 'PG1o', 'PG1 pc-out', '#4a86e8'
    if 'pcreg' in end:
        return 'PG1', 'PG1 next-PC', '#4a86e8'
    if 'rf.rf' in start and 'rf.rf' in end:
        return 'PG2', 'PG2 ALU/write-back', '#f6b26b'
    return 'PGx', 'unclassified', '#999999'


text = open(SRC, encoding='utf-8', errors='ignore').read()
paths = []
for b in re.split(r'\n(?=Startpoint:)', text):
    b = b.strip('\n')
    if not b.startswith('Startpoint:'):
        continue
    lines = b.splitlines()
    start = lines[0].split('Startpoint:', 1)[1].strip().split(' (')[0]
    end = re.search(r'Endpoint:\s*(\S+)', b).group(1)
    sta = re.search(r'Path Group:\s*(\S+)', b).group(1)
    arr = float(re.search(r'^\s*(-?[\d.]+)\s+data arrival time', b, re.M).group(1))
    req = float(re.search(r'^\s*(-?[\d.]+)\s+data required time', b, re.M).group(1))
    sl = float(re.search(r'^\s*(-?[\d.]+)\s+slack', b, re.M).group(1))
    gid, gname, gcolor = func_group(start, end)
    start_i = next((i for i, l in enumerate(lines) if '/Q (' in l), None)
    end_i = next((i for i, l in enumerate(lines) if 'data arrival time' in l), len(lines))
    stages = []
    pending = 0.0
    if start_i is not None:
        for l in lines[start_i + 1:end_i]:
            mo = re.match(r'^\s*\d+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s+[\^v]\s+(\S+)\s+\((\S+)\)', l)
            if mo:
                cd, t, pin, ct = mo.groups()
                stages.append([pin, ct, round(float(cd), 4), round(pending, 4)])
                pending = 0.0
                continue
            mi = re.match(r'^\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+[\^v]\s+(\S+)\s+\((\S+)\)', l)
            if mi:
                pending = float(mi.group(2))
    paths.append(dict(gid=gid, gname=gname, gcolor=gcolor, sta=sta, start=start, end=end,
                      arr=round(arr, 4), req=round(req, 4), slack=round(sl, 4),
                      levels=len(stages), stages=stages))

for i, p in enumerate(paths):
    p['id'] = i

g = defaultdict(list)
for p in paths:
    g[p['gid']].append(p)
groups = []
for gid, ps in g.items():
    ps.sort(key=lambda p: p['slack'])
    groups.append(dict(id=gid, name=ps[0]['gname'], color=ps[0]['gcolor'], sta=ps[0]['sta'],
                       count=len(ps), worst=min(p['slack'] for p in ps)))
groups.sort(key=lambda x: x['worst'])

data = dict(meta=dict(design='riscv (sky130hd/riscv32i)', clock_ns=7.0, fmax_mhz=147.93,
                      setup_wns=0.0415, endpoints=len(paths)),
            groups=groups, paths=paths)

TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>riscv timing dashboard</title>
<style>
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:13px;color:#1b2733;background:#eef2f7}
  header{background:#1f3a5f;color:#fff;padding:9px 16px;display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}
  header h1{font-size:15px;margin:0;letter-spacing:.02em}
  header .kpi{font-size:12px;opacity:.92}
  header .kpi b{color:#ffd966}
  #app{display:flex;height:calc(100% - 40px)}
  #groups{width:240px;background:#fff;border-right:1px solid #d6dee8;overflow:auto;padding:8px;flex:0 0 auto}
  #list{width:44%;min-width:340px;background:#fff;border-right:1px solid #d6dee8;overflow:auto;flex:0 0 auto}
  #detail{flex:1;overflow:auto;padding:10px 14px}
  .gcard{border:1px solid #d6dee8;border-radius:8px;padding:8px 9px;margin-bottom:8px;cursor:pointer;border-left-width:5px}
  .gcard:hover{background:#f4f8ff}
  .gcard.active{background:#e3edff;border-color:#3b6fb0}
  .gcard .gname{font-weight:600}
  .gcard .gmeta{color:#5b6b7d;font-size:11px;margin-top:2px}
  .gcard .gworst{color:#b45309;font-weight:600}
  table{width:100%;border-collapse:collapse}
  th,td{text-align:left;padding:5px 8px;border-bottom:1px solid #eef2f7;white-space:nowrap}
  th{position:sticky;top:0;background:#f7f9fc;font-size:11px;text-transform:uppercase;letter-spacing:.03em;color:#5b6b7d;z-index:1}
  tbody tr{cursor:pointer}
  tbody tr:hover{background:#f4f8ff}
  tbody tr.active{background:#e3edff}
  td.slack{font-weight:600;font-variant-numeric:tabular-nums}
  .neg{color:#c0392b}.pos{color:#1e7a46}
  .route h3{margin:0 0 4px;font-size:14px}
  .route .pathmeta{color:#5b6b7d;font-size:12px;margin-bottom:10px}
  .node{border:1px solid #cdd8e6;border-radius:8px;padding:6px 10px;background:#f7f9fc;display:flex;justify-content:space-between;gap:12px;align-items:center}
  .node .inst{font-weight:600;font-family:ui-monospace,Menlo,Consolas,monospace}
  .node .type{color:#5b6b7d;font-size:11px}
  .node .d{font-variant-numeric:tabular-nums;text-align:right;font-size:12px}
  .startnode{background:#d9e6fb;border-color:#4a86e8}
  .endnode{background:#fff2cc;border-color:#ffb300}
  .conn{width:2px;height:13px;background:#b8c4d4;margin-left:22px}
  .stagerow{display:flex;align-items:center;gap:6px}
  .stagerow .node{flex:1}
  .idx{color:#8a97a6;font-size:11px;width:30px;text-align:right;flex:0 0 auto}
  .delbarwrap{width:110px;background:#eef2f7;border-radius:3px;flex:0 0 auto}
  .delbar{height:8px;border-radius:3px;background:linear-gradient(90deg,#f6b26b,#e06666)}
  .empty{color:#8a97a6;padding:24px}
  .hint{color:#8a97a6;font-size:11px;padding:6px 10px}
</style>
</head>
<body>
<header>
  <h1>riscv — timing dashboard</h1>
  <span class="kpi" id="kpi"></span>
</header>
<div id="app">
  <div id="groups"></div>
  <div id="list"></div>
  <div id="detail"><div class="empty">Select a path group, then a path.</div></div>
</div>
<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const fmt = (v,n=4) => Number(v).toFixed(n);
$('#kpi').innerHTML =
  `clock <b>${DATA.meta.clock_ns} ns</b> &middot; reg&rarr;reg fmax <b>${DATA.meta.fmax_mhz} MHz</b> &middot; setup WNS <b>${DATA.meta.setup_wns} ns</b> &middot; endpoints <b>${DATA.meta.endpoints}</b>`;
let curGroup=null, curPath=null;

function renderGroups(){
  const el=$('#groups'); el.innerHTML='<div class="hint">Path groups (worst first)</div>';
  DATA.groups.forEach(g=>{
    const d=document.createElement('div');
    d.className='gcard'+(g.id===curGroup?' active':'');
    d.style.borderLeftColor=g.color;
    d.innerHTML=`<div class="gname">${g.name}</div>
      <div class="gmeta">STA group: ${g.sta} &middot; ${g.count} paths</div>
      <div class="gmeta">worst slack: <span class="gworst">${fmt(g.worst)} ns</span></div>`;
    d.onclick=()=>{ curGroup=g.id; curPath=null; renderGroups(); renderList(); $('#detail').innerHTML='<div class="empty">Select a path.</div>'; };
    el.appendChild(d);
  });
}

function renderList(){
  const el=$('#list');
  const ps=DATA.paths.filter(p=>p.gid===curGroup).sort((a,b)=>a.slack-b.slack);
  let h='<div class="hint">'+ps.length+' paths &mdash; worst at top, best at bottom</div>';
  h+='<table><thead><tr><th>#</th><th>slack (ns)</th><th>lvl</th><th>start point</th><th>end point</th></tr></thead><tbody>';
  ps.forEach((p,i)=>{
    h+=`<tr class="row${curPath===p.id?' active':''}" data-id="${p.id}">
      <td>${i+1}</td>
      <td class="slack ${p.slack<0?'neg':'pos'}">${fmt(p.slack)}</td>
      <td>${p.levels}</td>
      <td>${p.start}</td><td>${p.end}</td></tr>`;
  });
  h+='</tbody></table>';
  el.innerHTML=h;
  el.querySelectorAll('tbody tr').forEach(tr=>tr.onclick=()=>{ curPath=+tr.dataset.id; renderList(); renderDetail(); });
}

function renderDetail(){
  const p=DATA.paths.find(x=>x.id===curPath);
  const el=$('#detail');
  if(!p){ el.innerHTML='<div class="empty">Select a path.</div>'; return; }
  const maxc=Math.max(...p.stages.map(s=>s[2]),0.0001);
  let h=`<div class="route"><h3>${p.gname}</h3>
    <div class="pathmeta">start <code>${p.start}</code> &rarr; end <code>${p.end}</code><br>
      group <b>${p.sta}</b> &middot; arrival <b>${fmt(p.arr)} ns</b> &middot; required <b>${fmt(p.req)} ns</b> &middot;
      slack <span class="${p.slack<0?'neg':'pos'}"><b>${fmt(p.slack)} ns</b></span> &middot; ${p.levels} logic levels</div>
    <div class="startnode node"><div><div class="inst">${p.start}</div><div class="type">launch register (start point)</div></div><div class="d">Q</div></div>
    <div class="conn"></div>`;
  p.stages.forEach((s,i)=>{
    const w=Math.max(2,Math.round(100*s[2]/maxc));
    h+=`<div class="stagerow"><span class="idx">${i+1}</span>
      <div class="node"><div><div class="inst">${s[0]}</div><div class="type">${s[1]}</div></div>
      <div style="display:flex;align-items:center;gap:10px">
        <div class="delbarwrap"><div class="delbar" style="width:${w}%"></div></div>
        <div class="d">cell ${fmt(s[2])} ns<br><span class="type">wire ${fmt(s[3])} ns</span></div>
      </div></div></div><div class="conn"></div>`;
  });
  h+=`<div class="endnode node"><div><div class="inst">${p.end}</div><div class="type">capture / endpoint (end point)</div></div><div class="d">D</div></div></div>`;
  el.innerHTML=h;
}

renderGroups();
if(DATA.groups.length){ curGroup=DATA.groups[0].id; curPath=DATA.paths.filter(p=>p.gid===curGroup).sort((a,b)=>a.slack-b.slack)[0].id; renderGroups(); renderList(); renderDetail(); }
</script>
</body>
</html>'''

os.makedirs(OUTDIR, exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(TEMPLATE.replace('__DATA__', json.dumps(data, separators=(',', ':'))))
print('wrote', OUT, os.path.getsize(OUT), 'bytes;', len(paths), 'paths', len(groups), 'groups')
for gg in groups:
    print('  ', gg['id'], gg['name'], gg['sta'], gg['count'], 'worst', round(gg['worst'], 4))
