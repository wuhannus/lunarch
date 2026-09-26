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

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def newslide():
    return prs.slides.add_slide(BLANK)


def header(s, title, subtitle=None):
    b = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.02))
    b.fill.solid(); b.fill.fore_color.rgb = DARK; b.line.fill.background()
    tf = b.text_frame; tf.margin_left = Inches(0.5); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(26); p.font.bold = True; p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph(); p2.text = subtitle
        p2.font.size = Pt(12); p2.font.color.rgb = SOFT


def bullets(s, items, left=0.6, top=1.25, width=12.1, height=5.9, size=17):
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        lvl, txt = it if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.text = ('\u2022 ' if lvl == 0 else '\u2013 ') + txt
        p.level = lvl
        p.font.size = Pt(size if lvl == 0 else size - 3)
        p.font.color.rgb = GREY if lvl else DARK
        p.space_after = Pt(7)


def body_slide(title, items, subtitle=None, size=17):
    s = newslide(); header(s, title, subtitle); bullets(s, items, size=size); return s


def pic_slide(title, img, caption=None, subtitle=None):
    s = newslide(); header(s, title, subtitle)
    if os.path.exists(img):
        w, h = Image.open(img).size
        ratio = w / h
        max_w = 8.3 if caption else 12.2
        iw = max_w; ih = iw / ratio
        if ih > 5.7:
            ih = 5.7; iw = ih * ratio
        left = 0.4 if caption else (prs.slide_width.inches - iw) / 2
        s.shapes.add_picture(img, Inches(left), Inches(1.2), Inches(iw), Inches(ih))
    if caption:
        tb = s.shapes.add_textbox(Inches(8.95), Inches(1.35), Inches(3.95), Inches(5.5))
        tf = tb.text_frame; tf.word_wrap = True
        first = True
        for it in caption:
            lvl, txt = it if isinstance(it, tuple) else (0, it)
            p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
            p.text = ('\u2022 ' if lvl == 0 else '\u2013 ') + txt
            p.font.size = Pt(13 if lvl == 0 else 11)
            p.font.color.rgb = GREY if lvl else DARK
            p.space_after = Pt(5)
    return s


def table_slide(title, headers, rows, col_w=None, subtitle=None):
    s = newslide(); header(s, title, subtitle)
    nr, nc = len(rows) + 1, len(headers)
    gt = s.shapes.add_table(nr, nc, Inches(0.6), Inches(1.35), Inches(12.1), Inches(0.42 * nr)).table
    if col_w:
        tot = sum(col_w)
        for i, w in enumerate(col_w):
            gt.columns[i].width = Emu(int(Inches(12.1) * w / tot))
    for j, h in enumerate(headers):
        c = gt.cell(0, j); c.text = h
        c.fill.solid(); c.fill.fore_color.rgb = DARK
        for p in c.text_frame.paragraphs:
            p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = WHITE
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            c = gt.cell(i, j); c.text = str(v)
            c.fill.solid(); c.fill.fore_color.rgb = WHITE if i % 2 else LGREY
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(11); p.font.color.rgb = GREY
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
p3 = tf.add_paragraph()
p3.text = "RISC-V RV32I core  \u00b7  sky130HD  \u00b7  RTL-to-GDS  \u00b7  verification, timing & power studies"
p3.font.size = Pt(14); p3.font.color.rgb = SOFT; p3.alignment = PP_ALIGN.CENTER

body_slide("Agenda", [
    "Design under test \u2014 the RISC-V RV32I core",
    "Block diagram and module hierarchy",
    "Microarchitecture \u2014 the single-cycle datapath",
    "Data flow and path groups",
    "AI-driven open-source design flow (RTL \u2192 GDS)",
    "Verification & simulation (LEC, DRC, LVS, timing dashboards)",
    "Physical-design flow (synthesis \u2192 place \u2192 CTS \u2192 route)",
    "Power-oriented and timing-oriented runs",
    "Baseline results and Pareto comparison",
    "Hardware and software requirements",
    "Conclusions",
], size=18)

body_slide("Design Under Test \u2014 RISC-V RV32I Core", [
    "Top module: riscv \u2014 a simple single-cycle RV32I core",
    "Origin: J. E. Stine, Oklahoma State University (Harris & Harris textbook processor); bundled with OpenROAD Flow Scripts (Apache-2.0)",
    "24 RTL modules; 18 elaborated under the riscv top",
    "Sequential state: PC register (32 b) + register file 32\u00d732 (1,024 FFs) + SEPC",
    "Instruction/data memories are external (instr / readdata in, memwrite / aluout / writedata out)",
    "Target platform: sky130HD (sky130_fd_sc_hd), high-density standard cells",
    "Baseline: 5,520 cells, 73,594 \u00b5m\u00b2 core area, 376.6 \u00b5m die",
])

pic_slide("Block Diagram \u2014 riscv", IMG_BLOCK, caption=[
    "controller (maindec + aludec) drives the datapath control bus",
    "datapath: regfile, ALU, shifter, magcompare32, adders, muxes",
    "gold = register file; blue = PC / fetch loop",
    "colour-coded by functional path group (PG1\u2013PG8)",
], subtitle="controller + datapath, colour-coded by path group")

body_slide("Microarchitecture \u2014 Single-Cycle Datapath", [
    "Single cycle: fetch \u2192 decode \u2192 execute \u2192 write-back in one clock",
    "controller \u2014 maindec (opcode decode) + aludec (funct decode) produce the control bus",
    "datapath blocks:",
    (1, "regfile 32\u00d732, 2 read + 1 write port, rf[0] hard-wired to 0"),
    (1, "alu \u2014 add/sub/and/or/xor/slt with zero flag"),
    (1, "shifter \u2014 left / logical-right / arithmetic-right (shtype, shamt)"),
    (1, "magcompare32 \u2014 32-bit magnitude comparator (2b\u00d716, 2c\u00d715) for branches"),
    (1, "adder \u00d72 (PC+4, PC+imm), signext/mux5, mux2 / mux3 / mux5"),
    "flopr / flopenr \u2014 PC and SEPC sequential elements",
    "Critical loop: regfile read \u2192 mux \u2192 ALU \u2192 mux \u2192 regfile write",
], size=16)

body_slide("Data Flow", [
    "Fetch: pcreg \u2192 adder(+4) / adder(+imm) \u2192 pcmux(pcsrc) \u2192 ISRmux \u2192 pcreg",
    "Decode: instr \u2192 controller (maindec, aludec) \u2192 control bus",
    "Register read: regfile.rd1 \u2192 srca2 (rs1), rd2 \u2192 writedata (rs2)",
    "Immediate: instr \u2192 signext(mux5) \u2192 pcextmux \u2192 adders / ALU B-operand",
    "Execute: alu(srca2, srcb) and shifter(srca2, shamt) \u2192 srccmux \u2192 aluout",
    "Compare: srca2/writedata \u2192 magcompare32 \u2192 gt/lt/eq \u2192 controller.pcsrc",
    "Write-back: resmux(ALU/load) \u2192 storepcmux(link PC) \u2192 rf.wd3",
    "Endpoints: pcreg, SEPC, rf[1..31]; ports instr/readdata \u2192 pc/aluout/writedata",
], size=15)

table_slide("Path Groups (timing partition)", ["ID", "Group", "Start \u2192 End", "Dominant logic"], [
    ["PG1", "PC / Fetch", "pcreg \u2192 pcreg", "adder(+4/+imm), pcmux, flopr"],
    ["PG2", "ALU write-back", "regfile \u2192 regfile", "rs1mux, memsrcmux, alu, srccmux, resmux"],
    ["PG3", "Shift write-back", "regfile \u2192 regfile", "shifter, srccmux, resmux"],
    ["PG4", "Memory (LSU)", "readdata\u2192rf / rf\u2192writedata", "halfbytemux1/2, resmux"],
    ["PG5", "Branch compare", "regfile \u2192 pcreg", "magcompare32 \u2192 controller.pcsrc"],
    ["PG6", "Decode / Control", "instr \u2192 ctrl bus", "controller (maindec, aludec)"],
    ["PG7", "Immediate", "instr \u2192 alu/pcreg", "signext(mux5), pcextmux, adder"],
    ["PG8", "Output / Exception", "regfile \u2192 aluout; pcreg \u2192 SEPC", "srccmux, flopenr"],
], col_w=[1, 2.6, 3.2, 5.2], subtitle="critical path sits in PG2 (regfile \u2192 ALU \u2192 regfile)")

body_slide("AI-Driven Open-Source Design Flow (RTL \u2192 GDS)", [
    "RTL synthesis \u2014 Yosys (\u2265 0.69), mapped to sky130_fd_sc_hd liberty",
    "Floorplan / place / CTS / route \u2014 OpenROAD Flow Scripts (ORFS) + version-matched OpenROAD",
    "GDS stream-out \u2014 OpenROAD / KLayout",
    "Physical verification \u2014 KLayout DRC (sky130hd.lydrc) and LVS (sky130hd.lylvs)",
    "Layout vs extracted \u2014 Magic + netgen (LVS); parasitic SPEF for STA",
    "Logical equivalence \u2014 Kepler Formal (gate-level) + Yosys equiv_* (RTL vs synth)",
    "AI agents orchestrated the flow: toolchain build & version matching, run debugging, artifact/report extraction, dashboard & Excel generation, goal-directed optimization",
], size=16)

table_slide("Verification & Simulation", ["Check", "Tool / method", "Result"], [
    ["RTL \u2261 synthesised netlist", "Yosys equiv_make / equiv_induct / equiv_status", "Proven"],
    ["Synth \u2261 final routed netlist", "Kepler Formal (gate-level LEC, LEC_CHECK=1)", "Global output passed"],
    ["DRC", "KLayout sky130hd.lydrc", "0 violations"],
    ["LVS", "KLayout sky130hd.lylvs (+ Magic/netgen)", "Netlists match"],
    ["Timing sign-off", "OpenROAD STA (report_checks), SDC 7.0 ns", "WNS/TNS 0.00 ns, hold MET"],
    ["Simulation / equivalence", "Yosys formal + SAT (counter-example free)", "Pass"],
], col_w=[3.6, 5.6, 2.8], subtitle="functional + physical + logical equivalence all green")

body_slide("Physical-Design Flow", [
    "1_synth \u2014 Yosys synthesis to sky130 std cells (1_synth.odb / 1_2_yosys.v)",
    "2_floorplan \u2014 die/core sizing, tapcells, PDN (power grid)",
    "3_place \u2014 global place \u2192 resizer \u2192 detailed place (sizing for timing/area)",
    "4_cts \u2014 clock-tree synthesis, clock buffers, skew balancing",
    "5_route \u2014 global route (FastRoute) \u2192 detailed route \u2192 fill cells",
    "6_finish \u2014 final GDSII, SPEF, netlist, reports (DRC/LVS run separately)",
    "Artifacts: 6_final.gds / .def / .v / .spef, 6_drc.lyrdb, 6_lvs.lvsdb",
])

body_slide("Timing-Oriented Run (\u2192 200 MHz target)", [
    "Goal: fastest possible; power unconstrained; clock target 5.0 ns (200 MHz)",
    "Knobs: clk_period 5.0 ns, ABC_AREA=0 (delay), TNS_END_PERCENT=100, die pinned to baseline",
    "Result: NOT met \u2014 setup WNS \u22121.60 ns, TNS \u2212752.8 ns at 5.0 ns",
    "Best achievable: min period 6.52 ns \u2192 fmax 153.4 MHz (+3.7% vs baseline)",
    "Power: 29.3 mW (+49%) for only +5.5 MHz",
    "Why: single-cycle regfile\u2192ALU\u2192regfile loop, 28 logic levels, cell-delay dominated",
    "Conclusion: 200 MHz requires RTL pipelining, not P&R tuning",
], size=16)

body_slide("Power-Oriented Run (\u2192 minimum power)", [
    "Goal: lowest power; frequency unconstrained; clock relaxed to 20.0 ns",
    "Knobs: clk_period 20.0 ns, ABC_AREA=1 (area-oriented mapping), die pinned to baseline",
    "Result: timing clean (WNS/TNS 0.00 ns, worst slack +9.09 ns)",
    "Power: 6.54 mW vs 19.7 mW baseline \u2192 \u221267%",
    (1, "sequential \u221265%, combinational \u221271%, clock \u221265%"),
    "Cost: fmax 132.5 MHz (\u221210% vs baseline)",
    "Mechanism: smaller / lower-capacitance gates + relaxed clock \u2192 far less dynamic power",
], size=16)

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

table_slide("Timing vs Power \u2014 Pareto (same 376.6 \u00b5m die)", ["Metric", "Baseline", "Timing run", "Power run"], [
    ["Clock", "7.0 ns", "5.0 ns", "20.0 ns"],
    ["Setup WNS", "0.00 ns", "\u22121.60 ns \u2717", "0.00 ns \u2713"],
    ["fmax", "147.9 MHz", "153.4 MHz", "132.5 MHz"],
    ["Total power", "19.7 mW", "29.3 mW", "6.54 mW"],
    ["ABC mode", "delay", "delay", "area"],
], col_w=[3, 3, 3, 3], subtitle="trading speed for power and vice-versa")

pic_slide("Final Layout (GDS) + Module Map", IMG_MODMAP, caption=[
    "physical layout: regfile (red) left third, ALU (blue) right cluster",
    "adders / muxes between; grey = opt-merged logic + clock/fill",
    "376.6 \u00b5m die, 5,535 placed cells",
    "consistent with PG2 loop: split placement, yet wire delay < 0.02 ns/path",
], subtitle="timing-closed 7.0 ns layout")

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
    "Area-oriented synthesis + relaxed clock cuts power 67% (6.54 mW) at 132.5 MHz",
    "The design is cell-delay dominated; wire delay < 0.02 ns per path \u2014 not wire-limited",
    "Next steps: pipelined microarchitecture to reach 200 MHz+; SRAM macro for the memories",
], size=16)

out = '/mnt/d/opencode/lunarch/flow/LUNARCH_AI_Driven_Chip_Design.pptx'
prs.save(out)
print('wrote', out, os.path.getsize(out), 'bytes;', len(prs.slides._sldIdLst), 'slides')
