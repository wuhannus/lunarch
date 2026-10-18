#!/usr/bin/env python3
"""
Animated GIF: the AI-driven RTL->GDS flow, one step at a time, including the
real interaction records (the user prompts that drove each step) and the AI
action / result.

Output: flow/analysis/flow_steps.gif
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 600
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONTM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

NAVY = (31, 58, 95)
BLUE = (74, 134, 232)
BLUE_L = (226, 236, 252)
GREEN = (46, 158, 91)
GREEN_L = (219, 240, 227)
AMBER = (206, 128, 26)
AMBER_L = (252, 240, 219)
RED = (200, 30, 40)
GREY = (100, 110, 128)
LGREY = (245, 247, 250)
BORD = (208, 215, 226)
WHITE = (255, 255, 255)
DARK = (27, 39, 51)

F = {s: ImageFont.truetype(FONT, s) for s in (11, 12, 13, 14, 15, 16, 17, 18, 20, 26, 30)}
FB = {s: ImageFont.truetype(FONTB, s) for s in (11, 12, 13, 14, 15, 16, 18, 20, 22, 30)}
FM = {s: ImageFont.truetype(FONTM, s) for s in (11, 12, 13, 14)}

OUT = "/mnt/d/opencode/lunarch/flow/analysis/flow_steps.gif"

STEPS = [
    dict(name="Toolchain", sub="WSL2 \u00b7 Yosys \u00b7 OpenROAD \u00b7 ORFS",
         tool="WSL2 Ubuntu 24.04 \u00b7 Yosys 0.69 \u00b7 OpenROAD \u00b7 ORFS \u00b7 sky130 PDK",
         cmd="./DependencyInstaller.sh -all   +   cmake --build .",
         you="install the open-source synthesis tool, OpenROAD for physical design, and the DRC/LVS tool",
         ai="Diagnosed the WSL2 servicing deadlock, built Yosys + OpenROAD from source, installed ORFS, sky130 PDK, Magic/netgen/KLayout.",
         result="version-matched toolchain ready"),
    dict(name="1_synth", sub="Yosys \u2192 sky130 cells",
         tool="Yosys 0.69 \u2192 sky130_fd_sc_hd liberty",
         cmd="make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk",
         you="try the definitive ORFS \u2014 what does it stand for?",
         ai="Mapped the RTL to sky130 standard cells; wrote 1_synth.odb / 1_2_yosys.v.",
         result="5,520 cells synthesized"),
    dict(name="2_floorplan", sub="OpenROAD",
         tool="OpenROAD floorplan \u00b7 tapcells \u00b7 PDN",
         cmd="openroad -exit 2_floorplan.tcl",
         you="use the same die area as the baseline",
         ai="Fixed the die at 376.6 \u00b5m, placed tapcells, built the power grid.",
         result="376.6 \u00b5m die \u00b7 PDN \u00b7 tapcells"),
    dict(name="3_place", sub="OpenROAD",
         tool="global place \u2192 resizer \u2192 detailed place",
         cmd="openroad -exit 3_place.tcl",
         you="optimize timing as fast as possible (200 MHz target)",
         ai="Global placement, timing/area resizing, detailed placement.",
         result="placed, sized, legalized"),
    dict(name="4_cts", sub="OpenROAD",
         tool="clock-tree synthesis",
         cmd="openroad -exit 4_cts.tcl",
         you="continue  (autonomous flow step)",
         ai="Inserted clock buffers, balanced skew, re-estimated parasitics.",
         result="clock tree \u00b7 skew balanced"),
    dict(name="5_route", sub="FastRoute + TritonRoute",
         tool="global + detailed routing",
         cmd="openroad -exit 5_route.tcl",
         you="help me resolve the D-drive mount issue, then resume",
         ai="Global route, detailed route, fill cells; fixed the WSL/Windows drive mount.",
         result="routed 6_final.def"),
    dict(name="6_finish", sub="OpenROAD",
         tool="GDSII \u00b7 SPEF \u00b7 netlist \u00b7 reports",
         cmd="openroad -exit 6_finish.tcl",
         you="use KLayout to open the final GDS for me",
         ai="Streamed 6_final.gds, extracted 6_final.spef, wrote netlist + reports.",
         result="6_final.gds / .def / .v / .spef"),
    dict(name="Sign-off", sub="DRC \u00b7 LVS \u00b7 LEC \u00b7 STA",
         tool="KLayout \u00b7 Kepler Formal \u00b7 OpenSTA",
         cmd="make drc lvs    \u00b7    make LEC_CHECK=1",
         you="do the formal check synthesized\u2194routed; RTL \u2261 synthesized LEC is needed",
         ai="Ran KLayout DRC/LVS, Yosys equiv + Kepler LEC, OpenSTA on the SPEF.",
         result="DRC 0 \u00b7 LVS match \u00b7 LEC proven \u00b7 WNS 0.00"),
    dict(name="Optimize", sub="ABC \u00d7 clock sweep",
         tool="clk_period \u00d7 ABC_AREA sweep",
         cmd="run_sweep.sh   \u2192   make_pareto.py",
         you="optimize timing as fast as possible and in the power direction",
         ai="Swept clock \u00d7 ABC_AREA; found p7_power dominating the baseline.",
         result="155.4 MHz \u00b7 18.8 mW  (was 147.9 / 19.7)"),
    dict(name="Simulate", sub="Icarus Verilog",
         tool="pre/post/SDF simulation vs golden ISS",
         cmd="iverilog  +  vvp   (pre \u2192 post \u2192 SDF)",
         you="what tool do you use for the simulation?",
         ai="Ran the 125-cycle directed test pre-sim, post-sim and SDF; diffed the traces.",
         result="126/126 identical \u00b7 36/36 writes \u00b7 PASS"),
]

N = len(STEPS)

# geometry
HDR = 60
PIPE_Y, PIPE_H = 74, 56
DET_Y, DET_H = 150, 336
RES_Y, RES_H = 500, 52


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw(d, step, phase, intro=False):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # header
    d.rectangle([0, 0, W, HDR], fill=NAVY)
    d.text((18, 13), "RTL \u2192 GDS  \u2014  AI-driven physical-design flow",
           font=FB[22], fill=WHITE)
    d.text((18, 40), "each step: the tool, the command, and the interaction record",
           font=F[12], fill=(201, 216, 238))
    d.text((W - 190, 20), ("OVERVIEW" if intro else f"step {step + 1} / {N}"),
           font=FB[15], fill=(201, 216, 238))

    # pipeline
    gap = 6
    bw = (W - 28 - gap * (N - 1)) / N
    for j, st in enumerate(STEPS):
        x = 14 + j * (bw + gap)
        if intro:
            fill, out, txtc = LGREY, BORD, GREY
        elif j < step:
            fill, out, txtc = GREEN_L, GREEN, GREEN
        elif j == step:
            fill, out, txtc = NAVY, NAVY, WHITE
        else:
            fill, out, txtc = LGREY, BORD, GREY
        d.rounded_rectangle([x, PIPE_Y, x + bw, PIPE_Y + PIPE_H], radius=8,
                            fill=fill, outline=out, width=2)
        label = st["name"]
        fs = 13
        while d.textlength(label, font=FB[fs]) > bw - 10 and fs > 8:
            fs -= 1
        tw = d.textlength(label, font=FB[fs])
        d.text((x + (bw - tw) / 2, PIPE_Y + PIPE_H / 2 - fs * 0.7), label,
               font=FB[fs], fill=txtc)

    # progress line
    d.line([14, PIPE_Y + PIPE_H + 12, W - 14, PIPE_Y + PIPE_H + 12], fill=BORD, width=4)
    frac = 0 if intro else (step + 1) / N
    d.line([14, PIPE_Y + PIPE_H + 12, 14 + (W - 28) * frac, PIPE_Y + PIPE_H + 12],
           fill=BLUE, width=4)

    # detail cards
    d.rounded_rectangle([14, DET_Y, 386, DET_Y + DET_H], radius=10, fill=LGREY, outline=BORD, width=2)
    d.rounded_rectangle([400, DET_Y, W - 14, DET_Y + DET_H], radius=10, fill=WHITE, outline=BORD, width=2)

    if intro:
        d.text((32, DET_Y + 16), "SCOPE", font=FB[12], fill=GREY)
        d.text((32, DET_Y + 36), f"{N} steps", font=FB[30], fill=NAVY)
        d.text((32, DET_Y + 84), "toolchain \u2192 synth \u2192 floorplan \u2192 place \u2192 CTS", font=F[14], fill=GREY)
        d.text((32, DET_Y + 106), "route \u2192 finish \u2192 sign-off \u2192 optimize \u2192 simulate", font=F[14], fill=GREY)
        d.line([32, DET_Y + 140, 368, DET_Y + 140], fill=BORD)
        d.text((32, DET_Y + 154), "RECORDED INTERACTIONS", font=FB[12], fill=BLUE)
        d.text((32, DET_Y + 176), "Every step below is paired with the real",
               font=F[14], fill=DARK)
        d.text((32, DET_Y + 196), "prompt sent to the AI agent and the action", font=F[14], fill=DARK)
        d.text((32, DET_Y + 216), "it took, so the flow is reproducible.", font=F[14], fill=DARK)

        d.text((418, DET_Y + 16), "INTERACTION RECORD", font=FB[13], fill=NAVY)
        tx = 418
        ty = DET_Y + 46
        for i, st in enumerate(STEPS):
            col = NAVY if i % 2 == 0 else DARK
            d.text((tx, ty), f"{i+1:2}.  {st['name']}", font=FB[14], fill=col)
            wtxt = d.textlength(f"{i+1:2}.  {st['name']}", font=FB[14])
            d.text((tx + wtxt + 10, ty + 2), st["sub"], font=F[12], fill=GREY)
            ty += 26
    else:
        st = STEPS[step]
        d.text((32, DET_Y + 14), f"STEP {step + 1} / {N}", font=FB[12], fill=GREY)
        d.text((32, DET_Y + 32), st["name"], font=FB[30], fill=NAVY)
        d.text((32, DET_Y + 74), st["sub"], font=F[16], fill=GREY)
        d.line([32, DET_Y + 100, 368, DET_Y + 100], fill=BORD)
        d.text((32, DET_Y + 110), "TOOL", font=FB[12], fill=BLUE)
        y = DET_Y + 128
        for ln in wrap(d, st["tool"], F[14], 340):
            d.text((32, y), ln, font=F[14], fill=DARK); y += 19
        y += 8
        d.text((32, y), "COMMAND", font=FB[12], fill=BLUE); y += 18
        for ln in wrap(d, st["cmd"], FM[13], 340):
            d.text((32, y), ln, font=FM[13], fill=DARK); y += 18

        # right card: interaction
        d.text((418, DET_Y + 14), "INTERACTION RECORD", font=FB[13], fill=NAVY)
        y = DET_Y + 40
        # YOU
        d.rounded_rectangle([418, y, 466, y + 22], radius=5, fill=BLUE)
        d.text((424, y + 3), "YOU", font=FB[12], fill=WHITE)
        ytxt = DET_Y + 38
        for ln in wrap(d, st["you"], F[15], W - 418 - 30):
            d.text((476, ytxt), ln, font=F[15], fill=DARK); ytxt += 21
        y = max(ytxt + 8, DET_Y + 96)
        # AI
        if phase == 0:
            d.rounded_rectangle([418, y, 450, y + 22], radius=5, fill=BORD)
            d.text((424, y + 3), "AI", font=FB[12], fill=GREY)
            d.text((462, y + 2), "\u2026 working \u2026", font=F[14], fill=GREY)
        else:
            d.rounded_rectangle([418, y, 450, y + 22], radius=5, fill=GREEN)
            d.text((424, y + 3), "AI", font=FB[12], fill=WHITE)
            ytxt = y - 2
            for ln in wrap(d, st["ai"], F[15], W - 418 - 30):
                d.text((462, ytxt), ln, font=F[15], fill=DARK); ytxt += 21
            y = ytxt + 6
            d.rounded_rectangle([418, y, 486, y + 22], radius=5, fill=AMBER)
            d.text((424, y + 3), "RESULT", font=FB[12], fill=WHITE)
            for ln in wrap(d, st["result"], FB[15], W - 418 - 30):
                d.text((496, y - 1), ln, font=FB[15], fill=AMBER); y += 20

    # result banner
    if intro:
        msg = "AI agent: goal in \u2192 toolchain + flow executed \u2192 sign-off clean"
        fill, col = NAVY, WHITE
    elif phase == 0:
        msg = "\u25b6  running:  " + STEPS[step]["cmd"]
        fill, col = AMBER_L, AMBER
    else:
        msg = "\u2713  " + STEPS[step]["result"]
        fill, col = GREEN, WHITE
    d.rounded_rectangle([14, RES_Y, W - 14, RES_Y + RES_H], radius=10, fill=fill,
                        outline=None if fill != AMBER_L else AMBER, width=2)
    fs = 18
    while d.textlength(msg, font=FB[fs]) > W - 60 and fs > 11:
        fs -= 1
    d.text((28, RES_Y + (RES_H - fs) / 2 - 2), msg, font=FB[fs], fill=col)

    # footer
    d.text((16, RES_Y + RES_H + 8), "recorded from the actual opencode session",
           font=F[11], fill=GREY)
    d.text((W - 210, RES_Y + RES_H + 8), "RV32I \u00b7 sky130HD \u00b7 open-source",
           font=F[11], fill=GREY)
    return img


frames, durations = [], []
frames.append(draw(None, 0, 0, intro=True)); durations.append(2600)
for i in range(N):
    frames.append(draw(None, i, 0)); durations.append(1500)
    frames.append(draw(None, i, 1)); durations.append(2200)
frames += [frames[-1]] * 3
durations += [2200] * 3

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations,
               loop=0, optimize=True, disposal=2)
import os
print("wrote", OUT, os.path.getsize(OUT), "bytes,", len(frames), "frames")
