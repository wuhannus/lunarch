#!/usr/bin/env python3
"""Generate the LUNARCH architecture / flow deck (title + body on one slide)."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

DARK = RGBColor(0x1F, 0x3A, 0x5F)
GREY = RGBColor(0x44, 0x54, 0x6A)
LGREY = RGBColor(0xEE, 0xF2, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xC9, 0xD8, 0xEE)
BLUE = RGBColor(0x9E, 0xC5, 0xFF)

IMG_BLOCK = '/mnt/d/opencode/lunarch/flow/analysis/design.png'
IMG_MODMAP = '/mnt/d/opencode/lunarch/flow/baseline/modules/6_final_modules.png'
IMG_LAYOUT = '/mnt/d/opencode/lunarch/flow/orfs_sky130hd_riscv32i/6_final_layout.png'
IMG_PARETO = '/mnt/d/opencode/lunarch/flow/opt/sweep/pareto_ppa.png'
IMG_GDS = '/mnt/d/opencode/lunarch/flow/orfs_sky130hd_riscv32i/6_final_gds.png'
IMG_GIF = '/mnt/d/opencode/lunarch/flow/opt/sweep/riscv32i_sim.gif'
IMG_ROUTING = '/mnt/d/opencode/lunarch/flow/timing/dashboard/routing_maps.gif'
IMG_LOOPS = '/mnt/d/opencode/lunarch/flow/opt/p7_area_loops.png'
ACC_BLUE = RGBColor(0x4A, 0x86, 0xE8)
ACC_RED = RGBColor(0xE0, 0x66, 0x66)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def newslide():
    return prs.slides.add_slide(BLANK)


def header(s, title, subtitle=None):
    b = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.18))
    b.fill.solid(); b.fill.fore_color.rgb = DARK; b.line.fill.background()
    tf = b.text_frame; tf.margin_left = Inches(0.5); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(32); p.font.bold = True; p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph(); p2.text = subtitle
        p2.font.size = Pt(16); p2.font.color.rgb = SOFT


def bullets(s, items, left=0.6, top=1.5, width=12.1, height=5.7, size=24):
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        lvl, txt = it if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.text = ('\u2022 ' if lvl == 0 else '\u2013 ') + txt
        p.level = lvl
        p.font.size = Pt(size if lvl == 0 else size - 4)
        p.font.color.rgb = GREY if lvl else DARK
        p.space_after = Pt(10)


def body_slide(title, items, subtitle=None, size=24):
    s = newslide(); header(s, title, subtitle); bullets(s, items, size=size); return s


def pic_slide(title, img, caption=None, subtitle=None):
    s = newslide(); header(s, title, subtitle)
    if os.path.exists(img):
        w, h = Image.open(img).size
        ratio = w / h
        max_w = 7.5 if caption else 12.2
        iw = max_w; ih = iw / ratio
        if ih > 5.5:
            ih = 5.5; iw = ih * ratio
        left = 0.4 if caption else (prs.slide_width.inches - iw) / 2
        s.shapes.add_picture(img, Inches(left), Inches(1.35), Inches(iw), Inches(ih))
    if caption:
        tb = s.shapes.add_textbox(Inches(8.35), Inches(1.5), Inches(4.55), Inches(5.3))
        tf = tb.text_frame; tf.word_wrap = True
        first = True
        for it in caption:
            lvl, txt = it if isinstance(it, tuple) else (0, it)
            p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
            p.text = ('\u2022 ' if lvl == 0 else '\u2013 ') + txt
            p.font.size = Pt(18 if lvl == 0 else 15)
            p.font.color.rgb = GREY if lvl else DARK
            p.space_after = Pt(8)
    return s


def add_table(s, headers, rows, left, top, width, col_w=None,
              header_size=15, body_size=14):
    nr, nc = len(rows) + 1, len(headers)
    gt = s.shapes.add_table(nr, nc, Inches(left), Inches(top),
                            Inches(width), Inches(0.34 * nr)).table
    if col_w:
        tot = sum(col_w)
        for i, w in enumerate(col_w):
            gt.columns[i].width = Emu(int(Inches(width) * w / tot))
    for j, h in enumerate(headers):
        c = gt.cell(0, j); c.text = h
        c.fill.solid(); c.fill.fore_color.rgb = DARK
        for p in c.text_frame.paragraphs:
            p.font.size = Pt(header_size); p.font.bold = True; p.font.color.rgb = WHITE
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            c = gt.cell(i, j); c.text = str(v)
            c.fill.solid(); c.fill.fore_color.rgb = WHITE if i % 2 else LGREY
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(body_size); p.font.color.rgb = GREY
    return gt


def table_slide(title, headers, rows, col_w=None, subtitle=None):
    s = newslide(); header(s, title, subtitle)
    add_table(s, headers, rows, 0.6, 1.35, 12.1, col_w)
    return s


def text_panel(s, left, top, width, height, items, size=16, sub=4):
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        lvl, txt = it if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.text = ('\u2022 ' if lvl == 0 else '\u2013 ') + txt
        p.level = lvl
        p.font.size = Pt(size if lvl == 0 else size - sub)
        p.font.color.rgb = GREY if lvl else DARK
        p.space_after = Pt(7)
    return tb


def pareto_page():
    """Full page: big (fair, 142.9 MHz-normalized) Pareto figure + ABC annotation."""
    s = newslide()
    header(s, "Timing vs Power \u2014 Pareto (same 376.6 \u00b5m die)",
           "power normalized to the 142.9 MHz baseline clock")
    img_h = Inches(5.45)
    img_w = Inches(5.45 * 1000.0 / 680.0)          # keep PNG aspect ratio
    left, top = Inches(0.5), Inches(1.45)
    if os.path.exists(IMG_PARETO):
        s.shapes.add_picture(IMG_PARETO, left, top, width=img_w, height=img_h)
    ann_left = left + img_w + Inches(0.3)
    ann_w = prs.slide_width - ann_left - Inches(0.4)
    tb = s.shapes.add_textbox(ann_left, top, ann_w, img_h)
    tf = tb.text_frame; tf.word_wrap = True
    specs = [
        ([("ABC mapper: \u201cdelay-oriented\u201d vs \u201carea-oriented\u201d", True, DARK, 17)], 10),
        ([("delay-oriented (ABC_AREA=0): ", True, ACC_BLUE, 13.5),
          ("the mapper optimises the critical path \u2014 larger, faster cells, area "
           "spent to shorten logic depth. Fastest, but more capacitance \u2192 more "
           "dynamic power.  (blue circles: p5/p7/p10_delay)", False, GREY, 13.5)], 10),
        ([("area-oriented (ABC_AREA=1): ", True, ACC_RED, 13.5),
          ("the mapper minimises gate area / transistor count \u2014 smaller cells, "
           "shared logic. Lower capacitance \u2192 less switching power, at some speed "
           "cost.  (red squares: p7/p10/p20_area)", False, GREY, 13.5)], 10),
        ([("Reading the plot: ", True, DARK, 13.5),
          ("X = achieved fmax; Y = total power @142.9 MHz (fair comparison). Dashed "
           "line = Pareto front.", False, GREY, 13.5)], 10),
        ([("Result: ", True, DARK, 13.5),
          ("p7_area is lower power AND faster than the delay baseline at equal "
           "frequency \u2192 area-oriented mapping dominates.", False, GREY, 13.5)], 0),
    ]
    for i, (runs, after) in enumerate(specs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(after)
        for text, bold, color, size in runs:
            r = p.add_run(); r.text = text
            r.font.bold = bold; r.font.size = Pt(size); r.font.color.rgb = color
    return s


# 1 title
s = newslide()
b = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
b.fill.solid(); b.fill.fore_color.rgb = DARK; b.line.fill.background()
tf = b.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.9); tf.margin_right = Inches(0.9)
p = tf.paragraphs[0]; p.text = "LUNARCH"
p.font.size = Pt(54); p.font.bold = True; p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER
p2 = tf.add_paragraph(); p2.text = "AI-Driven Chip Design Leveraging Open-Source Toolchains"
p2.font.size = Pt(24); p2.font.color.rgb = BLUE; p2.alignment = PP_ALIGN.CENTER
p4 = tf.add_paragraph(); p4.text = "Han Wu"
p4.font.size = Pt(22); p4.font.bold = True; p4.font.color.rgb = WHITE; p4.alignment = PP_ALIGN.CENTER
p3 = tf.add_paragraph()
p3.text = "RISC-V RV32I core  \u00b7  sky130HD  \u00b7  RTL-to-GDS  \u00b7  verification, timing & power studies"
p3.font.size = Pt(14); p3.font.color.rgb = SOFT; p3.alignment = PP_ALIGN.CENTER

db = s.shapes.add_textbox(Inches(0.9), Inches(6.55),
                          prs.slide_width - Inches(1.8), Inches(0.75))
dtf = db.text_frame; dtf.word_wrap = True
dp = dtf.paragraphs[0]; dp.alignment = PP_ALIGN.CENTER
dp.text = ("Disclaimer: this material reflects the author\u2019s personal research "
           "interest only. It is not related to, endorsed by, or affiliated with "
           "my current or former employers.")
dp.font.size = Pt(11); dp.font.color.rgb = SOFT

body_slide("Agenda", [
    "Introduction \u2014 RISC-V RV32I core and the open-source RTL\u2192GDS motivation",
    "Design under test and the AI-driven open-source flow",
    "Verification and sign-off \u2014 simulation, LEC, DRC, LVS",
    "Results \u2014 baseline timing / power and the Pareto study",
    "Conclusions and next steps",
], size=30)

body_slide("Design Under Test \u2014 RISC-V RV32I Core", [
    "Top module: riscv \u2014 a simple single-cycle RV32I core",
    "Origin: J. E. Stine, Oklahoma State University (Harris & Harris textbook processor); bundled with OpenROAD Flow Scripts (Apache-2.0)",
    "24 RTL modules; 18 elaborated under the riscv top",
    "Sequential state: PC register (32 b) + register file 32\u00d732 (1,024 FFs) + SEPC",
    "Instruction/data memories are external (instr / readdata in, memwrite / aluout / writedata out)",
    "Target platform: sky130HD (sky130_fd_sc_hd), high-density standard cells",
    "Baseline: 5,520 cells, 73,594 \u00b5m\u00b2 core area, 376.6 \u00b5m die",
])

s = newslide()
header(s, "Block Diagram & Microarchitecture", "controller + datapath, colour-coded by path group")
if os.path.exists(IMG_BLOCK):
    w, h = Image.open(IMG_BLOCK).size
    ratio = w / h
    iw = 6.5; ih = iw / ratio
    if ih > 5.4:
        ih = 5.4; iw = ih * ratio
    s.shapes.add_picture(IMG_BLOCK, Inches(0.45), Inches(1.45), Inches(iw), Inches(ih))
text_panel(s, 7.25, 1.5, 5.6, 5.4, [
    "Single cycle: fetch \u2192 decode \u2192 execute \u2192 write-back in one clock",
    "controller (maindec + aludec) drives the datapath control bus",
    "datapath: regfile 32\u00d732, ALU (add/sub/and/or/xor/slt), shifter (sll/srl/sra), magcompare32, adders, mux2/3/5, signext",
    "sequential: PC register + SEPC (saved exception PC on ecall/ebreak)",
    "Critical loop: regfile read \u2192 mux \u2192 ALU \u2192 mux \u2192 regfile write",
], size=17)

s = newslide()
header(s, "Data Flow & Path Groups", "critical path sits in PG2 (regfile \u2192 ALU \u2192 regfile)")
add_table(s, ["ID", "Group", "Start \u2192 End", "Dominant logic"], [
    ["PG1", "PC / Fetch", "pcreg \u2192 pcreg", "adder(+4/+imm), pcmux, flopr"],
    ["PG2", "ALU write-back", "regfile \u2192 regfile", "rs1mux, memsrcmux, alu, srccmux, resmux"],
    ["PG3", "Shift write-back", "regfile \u2192 regfile", "shifter, srccmux, resmux"],
    ["PG4", "Memory (LSU)", "readdata\u2192rf / rf\u2192writedata", "halfbytemux1/2, resmux"],
    ["PG5", "Branch compare", "regfile \u2192 pcreg", "magcompare32 \u2192 controller.pcsrc"],
    ["PG6", "Decode / Control", "instr \u2192 ctrl bus", "controller (maindec, aludec)"],
    ["PG7", "Immediate", "instr \u2192 alu/pcreg", "signext(mux5), pcextmux, adder"],
    ["PG8", "Output / Exception", "regfile \u2192 aluout; pcreg \u2192 SEPC", "srccmux, flopenr"],
], left=0.5, top=1.42, width=12.3, col_w=[0.9, 2.4, 3.0, 5.0],
   header_size=13, body_size=12)
text_panel(s, 0.6, 4.6, 12.1, 2.6, [
    "Fetch: pcreg \u2192 adder(+4) / adder(+imm) \u2192 pcmux(pcsrc) \u2192 pcreg",
    "Decode & read: instr \u2192 controller (maindec, aludec); regfile rd1\u2192srca2, rd2\u2192writedata",
    "Immediate: instr \u2192 signext(mux5) \u2192 pcextmux \u2192 adders / ALU B-operand",
    "Execute & compare: alu / shifter \u2192 srccmux \u2192 aluout; magcompare32 \u2192 gt/lt/eq \u2192 pcsrc",
    "Write-back: resmux(ALU/load) \u2192 storepcmux(link PC) \u2192 rf.wd3",
], size=15)

s = newslide()
header(s, "AI-Driven Open-Source Flow & Verification", "100% open-source RTL\u2192GDS, sign-off clean")
text_panel(s, 0.6, 1.45, 12.1, 2.8, [
    "Synthesis \u2014 Yosys (\u2265 0.69) \u2192 sky130_fd_sc_hd liberty",
    "Floorplan / place / CTS / route \u2014 OpenROAD + OpenROAD Flow Scripts (version-matched)",
    "GDS stream-out (OpenROAD / KLayout); DRC & LVS (KLayout); SPEF extraction for STA",
    "Logical equivalence \u2014 Kepler Formal (gate-level) + Yosys equiv_* (RTL vs synth)",
    "AI agents orchestrated: toolchain bring-up, version matching, debugging, report/dashboard generation, goal-directed optimization",
], size=16)
add_table(s, ["Check", "Tool / method", "Result"], [
    ["RTL \u2261 synthesised netlist", "Yosys equiv_make / equiv_induct / equiv_status", "Proven"],
    ["Synth \u2261 final routed netlist", "Kepler Formal (gate-level LEC, LEC_CHECK=1)", "Global output passed"],
    ["DRC", "KLayout sky130hd.lydrc", "0 violations"],
    ["LVS", "KLayout sky130hd.lylvs (+ Magic/netgen)", "Netlists match"],
    ["Timing sign-off", "OpenROAD STA (report_checks), SDC 7.0 ns", "WNS/TNS 0.00 ns, hold MET"],
    ["Simulation / equivalence", "Yosys formal + SAT (counter-example free)", "Pass"],
], left=0.6, top=4.5, width=12.1, col_w=[3.6, 5.6, 2.9], header_size=13, body_size=12)

# animated gate-level simulation replay (GIF)
s = newslide()
header(s, "Simulation Replay \u2014 gate-level", "pre-layout RTL trace \u2014 animates in slide-show mode (press F5)")
if os.path.exists(IMG_GIF):
    iw = 9.0
    ih = iw * 600.0 / 1000.0
    s.shapes.add_picture(IMG_GIF,
                         Inches((prs.slide_width.inches - iw) / 2),
                         Inches(1.4), Inches(iw), Inches(ih))
tb = s.shapes.add_textbox(Inches(0.6), Inches(6.9), Inches(12.1), Inches(0.5))
tf = tb.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
for text, bold, color in [
    ("Debugger-style replay of the 125-cycle directed test: ", False, GREY),
    ("program listing", True, DARK), (" (left, current PC highlighted), ", False, GREY),
    ("architectural state + memory-write log", True, DARK), (" (right), and a ", False, GREY),
    ("signal strip", True, DARK), (" (pc / instr / memwrite / memread).", False, GREY),
]:
    r = p.add_run(); r.text = text; r.font.bold = bold
    r.font.size = Pt(14); r.font.color.rgb = color

body_slide("Physical-Design Flow", [
    "1_synth \u2014 Yosys synthesis to sky130 std cells (1_synth.odb / 1_2_yosys.v)",
    "2_floorplan \u2014 die/core sizing, tapcells, PDN (power grid)",
    "3_place \u2014 global place \u2192 resizer \u2192 detailed place (sizing for timing/area)",
    "4_cts \u2014 clock-tree synthesis, clock buffers, skew balancing",
    "5_route \u2014 global route (FastRoute) \u2192 detailed route \u2192 fill cells",
    "6_finish \u2014 final GDSII, SPEF, netlist, reports (DRC/LVS run separately)",
    "Artifacts: 6_final.gds / .def / .v / .spef, 6_drc.lyrdb, 6_lvs.lvsdb",
])

table_slide("Baseline Results (7.0 ns, 142.9 MHz)", ["Metric", "Value"], [
    ["Setup WNS / TNS", "0.00 / 0.00 ns"],
    ["Min reg\u2192reg period", "6.76 ns (fmax 147.9 MHz)"],
    ["Hold", "MET (worst +0.58 ns)"],
    ["Core area", "73,594 \u00b5m\u00b2 (die 376.6 \u00b5m)"],
    ["Cells", "5,520 (1,024 edfxtp + 32 dfrtp)"],
    ["Power", "19.7 mW (seq 40% / comb 30% / clk 29%)"],
    ["Signal wirelength", "274.2 mm (met1/met2 dominated)"],
    ["DRC / LVS / LEC", "0 / match / proven"],
], col_w=[4, 4], subtitle="reference point for all optimization studies")

# final layout: GDS photo + animated critical-path routing map
s = newslide()
header(s, "Final Layout \u2014 GDS photo + critical-path routing",
       "timing-closed 7.0 ns, 376.6 \u00b5m die")
if os.path.exists(IMG_GDS):
    s.shapes.add_picture(IMG_GDS, Inches(1.28), Inches(1.5), Inches(5.4), Inches(5.4))
if os.path.exists(IMG_ROUTING):
    gh = 5.4; gw = gh * 814.0 / 900.0
    s.shapes.add_picture(IMG_ROUTING, Inches(7.18), Inches(1.5), Inches(gw), Inches(gh))
tb = s.shapes.add_textbox(Inches(0.5), Inches(7.0), Inches(12.3), Inches(0.45))
tf = tb.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
for text, bold, color in [
    ("GDS photo (left): ", True, DARK),
    ("final routed sky130 layout (poly / li / met1\u2013met5).    ", False, GREY),
    ("Routing map (right): ", True, DARK),
    ("critical-path route highlighted on the die \u2014 animates in slide-show mode.",
     False, GREY),
]:
    r = p.add_run(); r.text = text; r.font.bold = bold
    r.font.size = Pt(14); r.font.color.rgb = color

pareto_page()

# cell-type analysis: why p7_area beats p7_delay at the same clock
s = newslide()
header(s, "Why p7_area beats p7_delay (same 7 ns clock)",
       "cell-type analysis \u2014 area vs delay ABC mapping")
add_table(s, ["Cell class", "p7_delay", "p7_area", "\u0394"], [
    ["Multi-input combinational", "3,458", "6,404", "+2,946"],
    ["Inverter", "123", "843", "+720"],
    ["Clock inverter", "68", "63", "\u22125"],
    ["Clock buffer", "135", "148", "+13"],
    ["Timing-repair buffer", "680", "405", "\u2212275"],
    ["Sequential (FF)", "1,056", "1,056", "0"],
    ["Antenna", "2", "3", "+1"],
    ["Tap", "1,876", "1,876", "0"],
    ["Fill", "11,652", "12,904", "+1,252"],
    ["Total instances", "19,050", "23,702", "+4,652"],
], left=0.5, top=1.5, width=6.4, col_w=[2.5, 1.3, 1.3, 1.3],
   header_size=13, body_size=12)
text_panel(s, 7.2, 1.5, 5.65, 5.4, [
    "Only the combinational mapping changed (the ABC_AREA knob).",
    "~1.85\u00d7 more combinational gates (3,458\u21926,404), each smaller \u2014 +85% gates for only +3% comb area.",
    "~7\u00d7 more inverters (123\u2192843, +2.7k \u00b5m\u00b2): the area map leans on inversions / AOI-OAI structures.",
    "~40% fewer timing-repair buffers (680\u2192405, \u22122.3k \u00b5m\u00b2): smaller cells needed less resizer fixing.",
    "FFs (1,056), tap cells and clock buffers ~unchanged; fill grows (+1,252) as the extra small cells leave gaps.",
    "Net: a finer-grained, smaller-gate netlist the resizer + CTS could tune better \u2192 fmax 147.9\u2192155.4 MHz AND power 19.7\u219218.8 mW at the same 7 ns clock.",
], size=14)

# ---- Where the extra cells go: two critical loops + extra-cell table ----
s = newslide()
header(s, "Where the extra cells go \u2014 two critical loops",
       "p7_area vs p7_delay: extra nand2 / nand3 / inv by endpoint loop")
if os.path.exists(IMG_LOOPS):
    w, h = Image.open(IMG_LOOPS).size
    iw = 7.0; ih = iw * h / w
    s.shapes.add_picture(IMG_LOOPS, Inches(0.4), Inches(1.6), Inches(iw), Inches(ih))
add_table(s, ["Loop (endpoint FF)", "Run", "nand2", "nand3", "inv"], [
    ["write-back (rf/D)", "p7_delay", "151", "30", "40"],
    ["", "p7_area", "1,527", "566", "423"],
    ["PC / branch (pcreg/D)", "p7_delay", "175", "40", "33"],
    ["", "p7_area", "1,341", "538", "395"],
    ["\u0394 (area \u2212 delay)", "total", "+2,542", "+1,034", "+745"],
], left=7.75, top=2.1, width=5.2, col_w=[2.0, 1.0, 0.9, 0.9, 0.9],
   header_size=13, body_size=12)
text_panel(s, 7.75, 5.1, 5.2, 1.9, [
    "Extra cells split ~53% / ~47% between the register-file write-back loop and the PC/branch loop \u2014 both sequential loops were re-expressed.",
    "Avg logic levels/path: p7_delay 21.5 vs p7_area 24.7 \u2014 more levels.",
    "Avg logical effort/stage: p7_delay 1.96 vs p7_area 1.68 \u2014 each stage is cheaper (\u03a3g \u2248 42 both).",
], size=12)

# ---- Why the loops prefer nand2 / nand3 / inverter cells ----
body_slide("Why the critical loops prefer NAND2 / NAND3 / INVERTER cells", [
    "Logical effort: inverter = 1.0, nand2 = 4/3, nor2 = 5/3 \u2014 the LOWEST of any gate; compound AOI/OAI (2\u20133) and 4:1 muxes are much higher.",
    "A 32-bit ALU / comparator / mux network re-decomposes into shallower stages of low-effort gates, so the whole path has less stage delay.",
    "Shallow series stacks: nand/nor stack only 2\u20133 devices in series, vs deep AOI/OAI stacks \u2014 less intrinsic delay per logical level.",
    "Drive-strength granularity: nand2/nand3/inv ship in X1\u2026X8, so the resizer picks the exact drive to match each stage's fanout.",
    "The area map (map -B 0.9) emits this fine, uniform gate mix; resizer + CTS then tune it on the fixed 7 ns clock, whereas the delay map pre-sized with wide cells and left less room.",
    "Net effect at the same clock: fmax 147.9 \u2192 155.4 MHz and power 19.7 \u2192 18.8 mW \u2014 the extra nand/inv gates ARE the speedup, not a cost.",
], size=17)

body_slide("Hardware Requirements", [
    "Host: x86-64 machine running WSL2 (Ubuntu 24.04)",
    "CPU: multi-core (\u2265 4 cores; place/route are largely single-thread heavy)",
    "RAM: \u2265 16 GB (recommend 32 GB); peak route/STA ~ 1\u20132 GB for this design",
    "Disk: \u2265 50 GB free (PDK + tools + builds; ORFS submodules & sources are large)",
    "Optional: dedicated NVMe for the WSL VHD (this project used an external NVMe)",
    "No special accelerator required \u2014 a standard workstation/laptop suffices",
])

table_slide("Software Requirements (open-source)", ["Layer", "Tools / version"], [
    ["OS", "WSL2 Ubuntu 24.04 LTS"],
    ["Synthesis", "Yosys \u2265 0.69 (built from source)"],
    ["P&R + STA", "OpenROAD (built from source, matched to ORFS)"],
    ["Flow scripts", "OpenROAD Flow Scripts (ORFS, master)"],
    ["Layout / extract", "Magic 8.3 (build), netgen 1.5 (apt)"],
    ["DRC / LVS / view", "KLayout 0.28"],
    ["Formal LEC", "Kepler Formal (built from source)"],
    ["PDK", "sky130A (open_pdks, sky130_fd_sc_hd)"],
    ["AI / scripting", "opencode AI agent, Python 3 + openpyxl / python-pptx"],
], col_w=[3, 8], subtitle="100% open-source; no commercial EDA licenses")

body_slide("Conclusions", [
    "A complete open-source RTL\u2192GDS flow for an RV32I core was built and sign-off clean (DRC 0, LVS match, LEC proven)",
    "AI orchestration covered toolchain bring-up, version matching, debugging, dashboards and goal-directed studies",
    "Baseline closes timing at 7.0 ns (147.9 MHz, 19.7 mW)",
    "200 MHz is unreachable without RTL pipelining \u2014 best is 153.4 MHz",
    "Area-oriented synthesis cuts per-cycle energy ~5% (18.7 mW @142.9 MHz equiv.) and raises fmax to 155 MHz",
    "The design is cell-delay dominated; wire delay < 0.02 ns per path \u2014 not wire-limited",
    "Next steps: pipelined microarchitecture to reach 200 MHz+; SRAM macro for the memories",
], size=21)

# ---- backup: logical-effort distribution ----
table_slide("Backup \u2014 logical-effort distribution (stages)",
            ["g", "gate types", "p7_delay", "p7_area"], [
    ["1.00", "inv / buf", "1,623", "719"],
    ["1.33", "nand2", "181", "2,591"],
    ["1.60\u20131.80", "a21o/a22o/o21a/o22a \u00b7 nand3", "694", "885"],
    ["2.00", "aoi21 / oai21 / mux2 / ha", "1,516", "1,767"],
    ["2.30\u20132.33", "aoi22 / oai22 / nor3", "285", "4"],
    ["2.70", "aoi211/221/31 \u00b7 oai211", "381", "332"],
    ["3.00", "aoi311 / oai311 / mux4", "388", "1"],
    ["3.30", "aoi41", "295", "0"],
    ["4.00", "xor2 / xnor2", "305", "221"],
], col_w=[1.2, 5.2, 1.5, 1.5],
   subtitle="per-stage g over the worst 264 paths of each run")

# ---- acknowledgements ----
body_slide("Acknowledgements", [
    "OpenROAD + OpenROAD Flow Scripts \u2014 the open-source RTL\u2192GDS flow and STA.",
    "Yosys \u2014 open-source synthesis and formal equivalence (equiv_*).",
    "KLayout \u2014 GDS viewing, DRC and LVS.  Magic + netgen \u2014 extraction and LVS.",
    "Kepler Formal \u2014 gate-level logical equivalence checking.",
    "SkyWater Technology, Google and open_pdks \u2014 the open sky130 PDK and standard-cell library.",
    "The RISC-V community, and J. E. Stine (Harris & Harris textbook reference core) whose RV32I design is the DUT.",
    "With thanks to all these tool, PDK and research teams for making an open silicon flow possible.",
], subtitle="thanks to the open-source tool, PDK and research communities", size=19)

out = '/mnt/d/opencode/lunarch/flow/LUNARCH_AI_Driven_Chip_Design.pptx'
prs.save(out)
print('wrote', out, os.path.getsize(out), 'bytes;', len(prs.slides._sldIdLst), 'slides')
