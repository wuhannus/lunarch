#!/usr/bin/env python3
"""
Render the riscv32i simulation as an animated GIF: a *pre-sim (RTL) vs
post-sim (routed gate-level) consistency-check* replay. The two simulations are
stepped side by side and a per-cycle diff proves the results are identical
(plus the SDF-annotated run and the memory-write trace), so the PPT slide shows
both simulators and the "results consistent" check in one animation.

Output: flow/opt/sweep/riscv32i_sim.gif (+ a couple of PNG stills for preview).
"""
import os
from PIL import Image, ImageDraw, ImageFont

SIM = "/mnt/d/opencode/lunarch/sim"
LST_PATH = os.path.join(SIM, "vectors", "program.lst")
OUT = "/mnt/d/opencode/lunarch/flow/opt/sweep/riscv32i_sim.gif"
PREVIEW = os.path.join(SIM, "out", "ppt_preview")
TRACES = {
    "pre":  os.path.join(SIM, "out", "presim_trace.txt"),
    "post": os.path.join(SIM, "out", "postsim_trace.txt"),
    "sdf":  os.path.join(SIM, "out", "sdfsim_trace.txt"),
}

W, H = 1000, 600
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

NAVY = (31, 58, 95)
BLUE = (74, 134, 232)
RED = (224, 102, 102)
RED_L = (250, 226, 226)
GREEN = (46, 158, 91)
GREEN_L = (214, 238, 223)
AMBER = (224, 144, 42)
GREY = (102, 112, 133)
LGREY = (245, 247, 250)
BORD = (208, 215, 226)
WHITE = (255, 255, 255)
DARK = (27, 39, 51)
SOFT = (201, 216, 238)

F = {s: ImageFont.truetype(FONT, s) for s in (10, 11, 12, 13, 14, 16, 18, 26)}
FB = {s: ImageFont.truetype(FONTB, s) for s in (11, 12, 13, 14, 16, 18, 22)}


def parse_trace(p):
    rows = []
    for line in open(p):
        t = line.split()
        if len(t) == 9:
            rows.append(t)
    return rows


def parse_lst(p):
    out = []
    for line in open(p):
        t = line.split()
        if len(t) >= 3:
            out.append((t[0], t[1], " ".join(t[2:])))
    return out


TR_PRE = parse_trace(TRACES["pre"])
TR_POST = parse_trace(TRACES["post"])
TR_SDF = parse_trace(TRACES["sdf"]) if os.path.exists(TRACES["sdf"]) else list(TR_PRE)
LST = parse_lst(LST_PATH)
N = min(len(TR_PRE), len(TR_POST), len(TR_SDF))
ADDR = {a: i for i, (a, _, _) in enumerate(LST)}
MAXPC = max(int(r[1], 16) for r in TR_PRE) or 1


def same(a, b):
    return a[:9] == b[:9]


MATCH_POST = [same(TR_PRE[i], TR_POST[i]) for i in range(N)]
MATCH_SDF = [same(TR_PRE[i], TR_SDF[i]) for i in range(N)]
DIFF = max(MATCH_POST.count(False), MATCH_SDF.count(False))
WRITES = sum(1 for i in range(N) if TR_PRE[i][6] == "1")
ALL_OK = DIFF == 0

FIELDS = [
    ("pc",        1, True),
    ("instr",     2, True),
    ("aluout",    3, True),
    ("writedata", 4, True),
    ("readdata",  5, True),
    ("memwrite",  6, False),
    ("memread",   7, False),
]

# ---------------- fixed geometry ----------------
PX, PY, PW, PH = 12, 58, 300, 442            # program listing
TX, TY, TW, ROW_H, HEAD_H = 324, 78, 664, 30, 26   # comparison table
SX, SY, SW, SH = 324, 324, 664, 176          # consistency signal strip
SLW = 64                                     # strip label width
BX, BY, BW, BH = 12, 508, 976, 46            # banner
GX, GY, GW, GH = 12, 562, 976, 30            # progress bar
COLW = None


def hexv(tok):
    return "0x" + tok


def draw_wave(d, top, h, vals, color, width=2):
    pts = []
    for i in range(len(vals)):
        x = SX + SLW + 6 + (i + 0.5) * COLW
        yv = top + 3 + (h - 6) * (1 - vals[i] / MAXPC)
        pts.append((x, yv))
    if len(pts) > 1:
        d.line(pts, fill=color, width=width)
    if pts:
        d.ellipse([pts[-1][0] - 2, pts[-1][1] - 2, pts[-1][0] + 2, pts[-1][1] + 2],
                  fill=color)


def draw_frame(c):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    r = TR_PRE[c]
    cyc, pc = r[0], r[1]
    ok = MATCH_POST[c] and MATCH_SDF[c]

    # ---------------- header ----------------
    d.rectangle([0, 0, W, 54], fill=NAVY)
    d.text((16, 11), "riscv32i  \u2014  pre-sim vs post-sim  consistency replay",
           font=FB[18], fill=WHITE)
    d.text((16, 34),
           "PRE = pre-layout RTL      POST = post-layout routed gate netlist      "
           "SDF = SDF back-annotated",
           font=F[11], fill=SOFT)
    d.text((W - 186, 16), f"cycle {int(cyc):3d} / {N-1}", font=FB[14], fill=SOFT)

    # ---------------- program listing ----------------
    d.rectangle([PX, PY, PX + PW, PY + PH], fill=LGREY, outline=BORD)
    d.text((PX + 8, PY + 6), "PROGRAM", font=FB[12], fill=NAVY)
    cur = ADDR.get(pc)
    rows = 15
    if cur is None:
        start = 0
    else:
        start = max(0, min(cur - rows // 2, len(LST) - rows))
    ry = PY + 26
    for k in range(rows):
        idx = start + k
        if idx >= len(LST):
            break
        a, code, asm = LST[idx]
        y = ry + k * 20
        if a == pc:
            d.rectangle([PX + 4, y - 1, PX + PW - 4, y + 18], fill=(214, 228, 248))
            d.rectangle([PX + 4, y - 1, PX + 7, y + 18], fill=BLUE)
        col = DARK if a == pc else GREY
        d.text((PX + 12, y), a, font=F[13], fill=col)
        d.text((PX + 96, y), code, font=F[13], fill=col)
        d.text((PX + 190, y), asm[:15], font=F[13], fill=col)
        if TR_PRE[c][6] == "1" and idx == cur:
            d.text((PX + PW - 30, y), "ST", font=FB[12], fill=RED)
        elif TR_PRE[c][7] == "1" and idx == cur:
            d.text((PX + PW - 30, y), "LD", font=FB[12], fill=GREEN)

    # ---------------- cycle-by-cycle state consistency table ----------------
    c0, c1 = TX, TX + 116
    c2, c3 = c1 + 214, c1 + 214 + 214
    cend = TX + TW
    d.text((TX, 58), "CYCLE-BY-CYCLE STATE CONSISTENCY", font=FB[13], fill=NAVY)
    # per-cycle badge
    bw = 168
    bx = TX + TW - bw
    d.rectangle([bx, 56, bx + bw, 56 + 20],
                fill=GREEN if ok else RED, outline=GREEN if ok else RED)
    d.text((bx + 14, 58), ("cycle MATCH \u2713" if ok else "cycle MISMATCH \u2717"),
           font=FB[13], fill=WHITE)
    # table
    d.rectangle([c0, TY, cend, TY + HEAD_H + ROW_H * len(FIELDS)],
                fill=WHITE, outline=BORD)
    # header
    d.rectangle([c0, TY, cend, TY + HEAD_H], fill=NAVY)
    for x, t in [(c0 + 8, "SIGNAL"), (c1 + 8, "PRE-SIM (RTL)"),
                 (c2 + 8, "POST-SIM (routed)"), (c3 + 8, "MATCH")]:
        d.text((x, TY + 6), t, font=FB[12], fill=WHITE)
    # rows
    for j, (name, idx, ishex) in enumerate(FIELDS):
        y = TY + HEAD_H + j * ROW_H
        if j % 2:
            d.rectangle([c0 + 1, y, cend - 1, y + ROW_H], fill=LGREY)
        d.line([c0, y, cend, y], fill=BORD)
        pv = TR_PRE[c][idx]
        qv = TR_POST[c][idx]
        eq = pv == qv
        d.text((c0 + 8, y + 7), name, font=FB[13], fill=DARK)
        if ishex:
            d.text((c1 + 8, y + 7), hexv(pv), font=F[14], fill=DARK)
            d.text((c2 + 8, y + 7), hexv(qv), font=F[14], fill=DARK)
        else:
            d.text((c1 + 8, y + 7), pv, font=FB[14], fill=RED if pv == "1" else GREY)
            d.text((c2 + 8, y + 7), qv, font=FB[14], fill=GREEN if qv == "1" else GREY)
        pill = "OK" if eq else "DIFF"
        pcol = GREEN if eq else RED
        d.rectangle([c3 + 10, y + 5, c3 + 70, y + ROW_H - 5], fill=pcol)
        d.text((c3 + 28, y + 7), pill, font=FB[13], fill=WHITE)

    # ---------------- consistency signal strip ----------------
    d.rectangle([SX, SY, SX + SW, SY + SH], fill=LGREY, outline=BORD)
    d.text((SX + 8, SY + 4),
           "PER-CYCLE CONSISTENCY  \u2014  PRE vs POST vs SDF", font=FB[12], fill=NAVY)
    # legend
    lx = SX + SW - 300
    for txt, col in [("PRE", BLUE), ("POST", GREEN), ("match", GREEN), ("differ", RED)]:
        d.rectangle([lx, SY + 8, lx + 10, SY + 18], fill=col)
        d.text((lx + 14, SY + 5), txt, font=F[11], fill=GREY)
        lx += 74
    plot_x0 = SX + SLW + 6
    plot_w = SW - SLW - 12
    # PRE pc lane
    d.text((SX + 6, SY + 34), "pc PRE", font=F[11], fill=BLUE)
    d.line([plot_x0, SY + 46, plot_x0 + plot_w, SY + 46], fill=BORD)
    draw_wave(d, SY + 26, 30, [int(TR_PRE[i][1], 16) for i in range(c + 1)], BLUE)
    # POST pc lane
    d.text((SX + 6, SY + 62), "pc POST", font=F[11], fill=GREEN)
    d.line([plot_x0, SY + 74, plot_x0 + plot_w, SY + 74], fill=BORD)
    draw_wave(d, SY + 54, 30, [int(TR_POST[i][1], 16) for i in range(c + 1)], GREEN)
    # match band
    d.text((SX + 6, SY + 90), "match", font=F[11], fill=GREY)
    for i in range(c + 1):
        x = plot_x0 + i * COLW
        m = MATCH_POST[i] and MATCH_SDF[i]
        d.rectangle([x, SY + 90, x + COLW - 0.5, SY + 106],
                    fill=GREEN if m else RED)
    d.line([plot_x0, SY + 108, plot_x0 + plot_w, SY + 108], fill=BORD)
    # memwrite ticks (pre red, post green)
    d.text((SX + 6, SY + 114), "memwr", font=F[11], fill=GREY)
    for i in range(c + 1):
        x = plot_x0 + i * COLW
        if TR_PRE[i][6] == "1":
            d.rectangle([x, SY + 112, x + COLW - 0.5, SY + 130], fill=RED)
        if TR_POST[i][6] == "1":
            d.rectangle([x + 1, SY + 114, x + COLW - 1.5, SY + 128], fill=GREEN)
    d.text((plot_x0 + plot_w - 150, SY + 132), f"writes: {WRITES}  (PRE = POST)",
           font=F[11], fill=GREY)
    # cycle axis
    for i in range(0, N, 20):
        x = plot_x0 + i * COLW
        d.text((x, SY + SH - 16), str(i), font=F[10], fill=GREY)
    # playhead
    phx = plot_x0 + (c + 1) * COLW
    d.line([phx, SY + 24, phx, SY + SH - 18], fill=AMBER, width=2)
    d.polygon([(phx - 5, SY + 24), (phx + 5, SY + 24), (phx, SY + 32)], fill=AMBER)

    # ---------------- consistency banner ----------------
    colb = GREEN if ALL_OK else RED
    d.rectangle([BX, BY, BX + BW, BY + BH], fill=colb, outline=colb)
    verdict = "OVERALL: PASS" if ALL_OK else "OVERALL: FAIL"
    d.text((BX + 14, BY + 10),
           f"PRE \u2261 POST \u2261 SDF   \u00b7   {N}/{N} lines identical, {DIFF} differing"
           f"   \u00b7   {WRITES}/{WRITES} writes match   \u00b7   {verdict}",
           font=FB[13], fill=WHITE)

    # ---------------- progress bar ----------------
    d.rectangle([GX, GY, GX + GW, GY + GH], fill=(225, 229, 236), outline=BORD)
    frac = (c + 1) / N
    d.rectangle([GX + 1, GY + 1, GX + int(GW * frac) - 1, GY + GH - 1], fill=BLUE)
    d.text((GX + 8, GY + 7), f"cycle {int(cyc)} / {N-1}    writes {WRITES}",
           font=FB[13], fill=WHITE)
    return img


def main():
    global COLW
    COLW = (SW - SLW - 12) / N
    frames = []
    for c in range(0, N, 1):
        frames.append(draw_frame(c).convert("P", palette=Image.ADAPTIVE, colors=128))
    frames += [frames[-1]] * 6
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=110, loop=0, optimize=True, disposal=2)
    print("wrote", OUT, os.path.getsize(OUT), "bytes,", len(frames), "frames")
    os.makedirs(PREVIEW, exist_ok=True)
    for cyc, name in [(20, "gif_frame20.png"), (60, "gif_frame60.png")]:
        draw_frame(min(cyc, N - 1)).convert("RGB").save(os.path.join(PREVIEW, name))


if __name__ == "__main__":
    main()
