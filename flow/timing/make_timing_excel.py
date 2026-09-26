#!/usr/bin/env python3
"""Build the timing-summary Excel workbook for sky130hd/riscv32i.

Inputs (dumped from the post-route ODB):
  timing_full.rpt  -> report_checks -path_delay max/min -group_path_count 5
                      -format full_clock_expanded   (detailed, worst 5 per group)
  allpaths.rpt     -> report_checks -path_delay max/min -group_path_count 1e6
                      -endpoint_path_count 1 -format summary (worst path per endpoint)
"""
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SRC = '/mnt/d/opencode/timing_full.rpt'
SRC_ALL = '/mnt/d/opencode/allpaths.rpt'
OUT = '/mnt/d/opencode/lunarch/flow/timing/riscv32i_timing_summary_full.xlsx'
PERIOD = 7.0

HDR = Font(bold=True, color='FFFFFF')
HFILL = PatternFill('solid', fgColor='3B6FB0')
SUB = Font(bold=True)
thin = Side(style='thin', color='BBBBBB')
BORD = Border(left=thin, right=thin, top=thin, bottom=thin)
ALT = PatternFill('solid', fgColor='F2F6FC')


def style_header(ws, ncol, row=1):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HDR
        cell.fill = HFILL
        cell.alignment = Alignment(horizontal='center', vertical='center')


def ltime(line):
    m = re.match(r'\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s', line)
    return float(m.group(2)) if m else None


def func_group(start, end, body):
    if end.startswith('aluout'):
        return 'PG8 result-out'
    if end.startswith('writedata'):
        return 'PG4 store-out'
    if end.startswith('pc[') or end == 'pc':
        return 'PG1 pc-out'
    if 'shifter' in body:
        return 'PG3 shift/write-back'
    if 'magcompare' in body:
        return 'PG5 branch-compare'
    if 'pcreg' in start and 'pcreg' in end:
        return 'PG1 fetch/next-PC'
    if 'pcreg' in end:
        return 'PG1/PG5 PC-redirect'
    if 'rf.rf' in start and 'rf.rf' in end:
        return 'PG2 ALU/write-back'
    if start.startswith(('instr', 'readdata')):
        return 'input->reg'
    return 'other'


# ---------- detailed (top-5 per group) ----------
text = open(SRC, encoding='utf-8', errors='ignore').read()
rows = []
for b in re.split(r'\n(?=Startpoint:)', text):
    b = b.strip('\n')
    if not b.startswith('Startpoint:'):
        continue
    lines = b.splitlines()
    start = lines[0].split('Startpoint:', 1)[1].strip()
    _m = re.search(r'Endpoint:\s*(\S+)', b)
    end = _m.group(1) if _m else '?'
    group = re.search(r'Path Group:\s*(\S+)', b).group(1)
    ptype = re.search(r'Path Type:\s*(\S+)', b).group(1)
    arrival = float(re.search(r'^\s*(-?[\d.]+)\s+data arrival time', b, re.M).group(1))
    required = float(re.search(r'^\s*(-?[\d.]+)\s+data required time', b, re.M).group(1))
    slack = float(re.search(r'^\s*(-?[\d.]+)\s+slack', b, re.M).group(1))
    arr_i = next(i for i, l in enumerate(lines) if 'data arrival time' in l)
    launch_i = max(i for i in range(arr_i) if '/CLK (' in lines[i])
    launch = ltime(lines[launch_i])
    cap_i = None
    for i in range(arr_i + 1, len(lines)):
        if '/CLK (' in lines[i]:
            cap_i = i
    if cap_i is not None:
        edge_i = next((i for i in range(arr_i + 1, len(lines)) if 'rise edge' in lines[i]), None)
        edge = ltime(lines[edge_i]) if edge_i is not None else PERIOD
        capture = ltime(lines[cap_i]) - edge
    else:
        edge_i = next((i for i in range(arr_i + 1, len(lines)) if 'rise edge' in lines[i]), None)
        edge = ltime(lines[edge_i]) if edge_i is not None else 0.0
        cn = next((i for i in range(arr_i + 1, len(lines)) if 'clock network delay' in lines[i]), None)
        capture = None
        if cn is not None:
            mm = re.match(r'\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s', lines[cn])
            if mm:
                capture = float(mm.group(2)) - edge
    skew = (capture - launch) if (capture is not None and launch is not None) else None
    q_i = max((i for i in range(arr_i) if '/Q (' in lines[i]), default=None)
    levels = None
    if q_i is not None:
        e_i = max((i for i in range(q_i + 1, arr_i)
                   if '(sky130_fd_sc_hd__' in lines[i] or '(out)' in lines[i]), default=None)
        if e_i is not None:
            levels = sum(1 for i in range(q_i + 1, e_i) if '(sky130_fd_sc_hd__' in lines[i])
    rows.append(dict(start=start, end=end, group=group, type=ptype,
                     fgroup=func_group(start, end, b), launch=launch, data=arrival - launch,
                     levels=levels, arrival=arrival, capture=capture, skew=skew,
                     required=required, slack=slack))


# ---------- all endpoints (one worst path per endpoint) ----------
def parse_all(path, ptype):
    out = []
    text = open(path, encoding='utf-8', errors='ignore').read()
    marker = '===== SETUP endpoint paths =====' if ptype == 'max' else '===== HOLD endpoint paths ====='
    start = text.find(marker)
    body = text[start:]
    nxt = body.find('=====', len(marker))
    if nxt != -1:
        body = body[:nxt]
    for line in body.splitlines():
        m = re.match(r'^(\S+)\s+\(([^)]*)\)\s+(\S+)\s+\(([^)]*)\)\s+(-?[\d.]+)\s*$', line)
        if not m:
            continue
        s_sig, s_type, e_sig, e_type, sl = m.groups()
        if s_sig in ('Startpoint',):
            continue
        grp = 'vclk_clk' if e_type == 'output' else 'clk'
        out.append(dict(type=ptype, start=s_sig, end=e_sig, e_type=e_type,
                        slack=float(sl), group=grp,
                        fgroup=func_group(s_sig, e_sig, '')))
    return out


all_setup = parse_all(SRC_ALL, 'max')
all_hold = parse_all(SRC_ALL, 'min')

# ---------------- workbook ----------------
wb = Workbook()

ws = wb.active
ws.title = 'Worst 20 (detailed)'
headers = ['#', 'Type', 'Report group', 'Functional path group',
           'Start point', 'End point',
           'Launch clk latency (ns)', 'Data-path delay (ns)', 'Data-path cells (logic levels)',
           'Data arrival (ns)', 'Capture clk latency (ns)', 'Clock skew (ns)',
           'Data required (ns)', 'Slack / WNS (ns)', 'Status']
ws.append(headers)
for i, r in enumerate(rows, 1):
    ws.append([i, 'Setup (max)' if r['type'] == 'max' else 'Hold (min)', r['group'], r['fgroup'],
               r['start'], r['end'], r['launch'], r['data'], r['levels'], r['arrival'],
               r['capture'], r['skew'], r['required'], r['slack'],
               'MET' if r['slack'] >= 0 else 'VIOLATED'])
style_header(ws, len(headers))
for i, w in enumerate([4, 12, 12, 24, 34, 34, 14, 14, 16, 12, 14, 12, 14, 14, 10], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.border = BORD
        if isinstance(cell.value, float):
            cell.number_format = '0.000'
    if row[0].row % 2 == 0:
        for cell in row:
            cell.fill = ALT
ws.freeze_panes = 'A2'


def add_all_sheet(title, data):
    sh = wb.create_sheet(title)
    hdr = ['#', 'Report group', 'Functional path group', 'Start point', 'End point',
           'Endpoint kind', 'Slack (ns)', 'Status']
    sh.append(hdr)
    for i, r in enumerate(data, 1):
        sh.append([i, r['group'], r['fgroup'], r['start'], r['end'],
                   'output port' if r['e_type'] == 'output' else 'register',
                   r['slack'], 'MET' if r['slack'] >= 0 else 'VIOLATED'])
    style_header(sh, len(hdr))
    for i, w in enumerate([5, 12, 24, 34, 24, 14, 12, 10], 1):
        sh.column_dimensions[get_column_letter(i)].width = w
    for row in sh.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORD
            if isinstance(cell.value, float):
                cell.number_format = '0.000'
        if row[0].row % 2 == 0:
            for cell in row:
                cell.fill = ALT
    sh.freeze_panes = 'A2'
    sh.auto_filter.ref = sh.dimensions


add_all_sheet('All endpoints (setup)', all_setup)
add_all_sheet('All endpoints (hold)', all_hold)


def slack_stats(data):
    vals = sorted(r['slack'] for r in data)
    return dict(n=len(vals), worst=vals[0], median=vals[len(vals) // 2], best=vals[-1],
                viol=sum(1 for v in vals if v < 0))


ss = slack_stats(all_setup)
hs = slack_stats(all_hold)

ws2 = wb.create_sheet('Summary')
lines = [
    ['Baseline APR timing summary — sky130hd/riscv32i (riscv)'],
    [],
    ['Clock period (ns)', PERIOD],
    ['Clock fmax (MHz)', round(1000.0 / PERIOD, 2)],
    ['Timing endpoints (setup)', ss['n']],
    ['Setup WNS (ns)', ss['worst']],
    ['Setup TNS (ns)', round(sum(v for v in (r['slack'] for r in all_setup) if v < 0), 4)],
    ['Setup violations', ss['viol']],
    ['Setup slack: worst / median / best', f"{ss['worst']} / {round(ss['median'],4)} / {round(ss['best'],4)}"],
    ['Hold WNS (ns)', hs['worst']],
    ['Hold violations', hs['viol']],
    ['Paths in "Worst 20 (detailed)" sheet', len(rows)],
    ['All-endpoint rows (setup / hold)', f"{ss['n']} / {hs['n']}"],
]
for l in lines:
    ws2.append(l)
ws2['A1'].font = Font(bold=True, size=13)
for r in range(3, ws2.max_row + 1):
    ws2.cell(row=r, column=1).font = SUB
ws2.column_dimensions['A'].width = 36
ws2.column_dimensions['B'].width = 24
ws2.append([])
ws2.append(['Endpoint category (setup)', 'Count', 'Worst slack (ns)'])
style_header(ws2, 3, ws2.max_row)
cats = {}
for r in all_setup:
    base = re.sub(r'\[.*', '', r['end']).replace('/D', '').rstrip('_')
    cats.setdefault(base, []).append(r['slack'])
for k in sorted(cats, key=lambda k: min(cats[k])):
    ws2.append([k, len(cats[k]), min(cats[k])])

ws3 = wb.create_sheet('Clock Skew')
ws3.append(['Per-path clock skew (capture clk latency − launch clk latency), worst 5 per group'])
ws3['A1'].font = Font(bold=True, size=12)
ws3.append([])
ws3.append(['Type', 'Report group', 'Functional path group', 'Start', 'End',
            'Launch clk lat (ns)', 'Capture clk lat (ns)', 'Clock skew (ns)'])
style_header(ws3, 8, 3)
for r in rows:
    ws3.append(['Setup' if r['type'] == 'max' else 'Hold', r['group'], r['fgroup'],
                r['start'], r['end'], r['launch'], r['capture'], r['skew']])
for i, w in enumerate([8, 12, 24, 34, 34, 16, 16, 14], 1):
    ws3.column_dimensions[get_column_letter(i)].width = w
for row in ws3.iter_rows(min_row=4):
    for cell in row:
        cell.border = BORD
        if isinstance(cell.value, float):
            cell.number_format = '0.0000'

ws4 = wb.create_sheet('Notes')
notes = [
    ['Field', 'Meaning'],
    ['Report group', 'STA clock group (clk = core, vclk_clk = output/virtual clock)'],
    ['Functional path group', 'Data-flow group PG1–PG8 (see flow/analysis/path_groups.md)'],
    ['Launch clk latency', 'Clock network delay to launch register CLK pin'],
    ['Data-path delay', 'data arrival time − launch clock latency'],
    ['Data-path cells (logic levels)', 'Cell instances in data path (launch Q → endpoint)'],
    ['Capture clk latency', 'Clock network delay to capture register CLK pin'],
    ['Clock skew', 'capture clk latency − launch clk latency'],
    ['Slack / WNS', 'report: data required − data arrival (setup); arrival − required (hold)'],
    ['Sheet "Worst 20 (detailed)"', 'report_checks -group_path_count 5 -format full_clock_expanded'],
    ['Sheets "All endpoints"', 'report_checks -endpoint_path_count 1 (worst path per endpoint)'],
    ['Clock period', f'{PERIOD} ns (142.86 MHz); source flow/timing/constraint_7ns.sdc'],
    ['Abbreviations', 'see flow/analysis/glossary.md'],
]
for row in notes:
    ws4.append(row)
for c in 'AB':
    ws4[f'{c}1'].font = HDR
    ws4[f'{c}1'].fill = HFILL
ws4.column_dimensions['A'].width = 32
ws4.column_dimensions['B'].width = 90

wb.save(OUT)
print('wrote', OUT)
print('detailed rows:', len(rows), '| all setup:', ss['n'], '| all hold:', hs['n'])
print('setup WNS/TNS:', ss['worst'], '/', round(sum(v for v in (r['slack'] for r in all_setup) if v < 0), 4), '| hold WNS:', hs['worst'])
