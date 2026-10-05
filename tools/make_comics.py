"""Draws the comic strips (BD) that open each chapter, as SVG files.

Run from the repository root:

    python tools/make_comics.py

and it (re)writes images/comics/*.svg. To change what a character says, edit the
text in the SCENES section at the bottom and re-run. The drawings are deliberately
simple, so they are easy to tweak -- or to replace later by hand-drawn panels.
"""
import base64
import io
import os
import sys
import textwrap

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "notebooks"))
import painters as P  # noqa: E402
 
OUT = os.path.join(os.path.dirname(__file__), "..", "images", "comics")
INK = "#000"
PANEL_W, PANEL_H, GAP = 440, 300, 16
FONT = "'Comic Neue', 'Comic Sans MS', 'Chalkboard SE', cursive"

CREW = {  # name: (coat accent, hair colour, skin)
    "A":  ("#2E86DE", "#6B3E26", "#F1C9A5"),
    "B":  ("#C6379E", "#222222", "#8D5A3B"),
    "C":   ("#8E44AD", "#C0392B", "#A47554"),
    "D": ("#16A085", "#BDC3C7", "#E0AC84"),
    "E":  ("#F39C12", "#F7DC6F", "#E8B98F"),
    "Fourier": ("#922B21", "#ECF0F1", "#F3D2B8"),
}
QUARTET = ["#E74C3C", "#3498DB", "#2ECC71", "#F1C40F"]


# --------------------------------------------------------------------- primitives
def png_uri(z, size=None):
    """Tiny PNG as a data URI (so the SVG stays a single file).

    z is either a 2D array (drawn in grayscale) or an RGB / RGBA array in [0, 1].
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    if z.ndim == 3:
        plt.imsave(buf, np.clip(z, 0, 1), format="png")
    else:
        plt.imsave(buf, z, cmap="gray", format="png")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# The flower is painted with the same paints as the canvases.
PAINT = {"red": "#E74C3C", "blue": "#3498DB", "yellow": "#F1C40F",
         "green": "#19AD57", "purple": "#9B59B6", "orange": "#E67E22"}
FLOWER_COLOURS = [
    (0.70, "red"),
    (0.71, "purple"),
    (1.00, "yellow"),  # heart
    (0.45, "green"),   # stem
    (0.50, "blue"),    # leaves
    (0.30, "orange"),  # pot
]


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def flower_rgb(transparent=False):
    """The flower in colour, background black (screen) or transparent (pedestal)."""
    img = P.flower()
    rgb = np.zeros(img.shape + (3,))
    for level, paint in FLOWER_COLOURS:
        rgb[np.isclose(img, level)] = hex_rgb(PAINT[paint])
    if transparent:
        alpha = (img > 0).astype(float)[..., None]
        return np.concatenate([rgb, alpha], -1)
    return rgb


def folded_rgb(R):
    """What the scanner shows when every R-th line is painted, colour by colour."""
    rgb = flower_rgb()
    out = np.stack([np.abs(P.ifft2c(P.undersample(P.fft2c(rgb[..., c]), R)[0]))
                    for c in range(3)], -1)
    return np.clip(min(R, 2) * out, 0, 1)   # bright, without burning the overlaps to white


def text_block(x, y, text, width_chars, size=15, anchor="start", weight="normal"):
    lines = []
    for para in text.split("\n"):
        lines += textwrap.wrap(para, width_chars) or [""]
    out = [f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
           f'font-weight="{weight}" text-anchor="{anchor}" fill="{INK}">']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else size * 1.2
        out.append(f'<tspan x="{x}" dy="{dy}">{ln}</tspan>')
    out.append("</text>")
    return "".join(out), len(lines) * size * 1.2


def bubble(x, y, w, text, tail_to, size=14, thought=False):
    """Speech bubble with its top-left at (x, y), tail pointing at tail_to."""
    chars = max(8, int(w / (size * 0.6)))
    body, h = text_block(x + w / 2, y + size + 8, text, chars, size, anchor="middle")
    h += 14
    tx, ty = tail_to
    bx = min(max(tx, x + 20), x + w - 20)
    s = []
    if thought:
        s.append(f'<ellipse cx="{x + w/2}" cy="{y + h/2}" rx="{w/2 + 6}" ry="{h/2 + 6}" '
                 f'fill="white" stroke="{INK}" stroke-width="2.5"/>')
        for i, r in enumerate((6, 4)):
            px = bx + (tx - bx) * (i + 1) / 3
            py = y + h + (ty - y - h) * (i + 1) / 3
            s.append(f'<circle cx="{px}" cy="{py}" r="{r}" fill="white" stroke="{INK}" stroke-width="2"/>')
    else:
        s.append(f'<path d="M{bx - 10},{y + h - 2} L{tx},{ty} L{bx + 10},{y + h - 2} Z" '
                 f'fill="white" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
                 f'fill="white" stroke="{INK}" stroke-width="2.5"/>')
        s.append(f'<rect x="{bx - 8}" y="{y + h - 6}" width="16" height="6" fill="white"/>')
    s.append(body)
    return "".join(s)


def caption(x, y, w, text, size=13):
    """The yellow narration box of franco-belgian comics (le récitatif)."""
    body, h = text_block(x + 8, y + size + 5, text, int(w / (size * 0.64)), size, weight="bold")
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h + 10}" fill="#FFE66D" '
            f'stroke="{INK}" stroke-width="2"/>' + body)


def scientist(x, y, name, pose="stand", mood="happy", s=1.0, goggles=None, flip=False):
    """A little scientist whose feet stand at (x, y)."""
    accent, hair, skin = CREW.get(name, ("#555", "#333", "#F1C9A5"))
    g = [f'<g transform="translate({x},{y}) scale({-s if flip else s},{s})">']
    # legs
    g.append(f'<rect x="-14" y="-38" width="10" height="38" rx="3" fill="#34495E" stroke="{INK}" stroke-width="2"/>')
    g.append(f'<rect x="4" y="-38" width="10" height="38" rx="3" fill="#34495E" stroke="{INK}" stroke-width="2"/>')
    # arms (behind coat for some poses)
    arms = {
        "stand": ["M-20,-80 L-32,-45", "M20,-80 L32,-45"],
        "paint": ["M-20,-80 L-32,-45", "M20,-80 L50,-110"],
        "point": ["M-20,-80 L-32,-45", "M20,-80 L58,-95"],
        "carry": ["M-20,-80 L-34,-120", "M20,-80 L34,-120"],
        "cheer": ["M-20,-80 L-40,-122", "M20,-80 L40,-122"],
        "walk":  ["M-20,-80 L-38,-55", "M20,-80 L36,-58"],
    }[pose]
    for a in arms:
        g.append(f'<path d="{a}" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>')
        g.append(f'<path d="{a}" stroke="white" stroke-width="5" stroke-linecap="round"/>')
    # lab coat
    g.append(f'<path d="M-24,-92 Q0,-100 24,-92 L28,-34 L-28,-34 Z" fill="white" stroke="{INK}" stroke-width="2.5"/>')
    g.append(f'<path d="M-10,-94 L0,-74 L10,-94" fill="none" stroke="{accent}" stroke-width="5"/>')
    g.append(f'<line x1="0" y1="-74" x2="0" y2="-36" stroke="{INK}" stroke-width="1.5"/>')
    g.append(f'<rect x="8" y="-66" width="11" height="9" fill="{accent}" stroke="{INK}" stroke-width="1.5"/>')
    # head
    g.append(f'<circle cx="0" cy="-122" r="26" fill="{skin}" stroke="{INK}" stroke-width="2.5"/>')
    if name == "E":
        g.append(f'<path d="M-26,-128 L-22,-160 L-10,-142 L-2,-166 L6,-144 L20,-162 L22,-138 L27,-128 '
                 f'Q0,-146 -26,-128 Z" fill="{hair}" stroke="{INK}" stroke-width="2"/>')
    elif name == "C":
        g.append(f'<path d="M-27,-128 Q0,-162 27,-128 Z" fill="{accent}" stroke="{INK}" stroke-width="2"/>')
        g.append(f'<path d="M20,-130 L44,-128 L22,-124 Z" fill="{accent}" stroke="{INK}" stroke-width="2"/>')
    elif name == "Fourier":
        for cx in (-24, 24):
            g.append(f'<circle cx="{cx}" cy="-118" r="11" fill="{hair}" stroke="{INK}" stroke-width="2"/>')
        g.append(f'<path d="M-24,-132 Q0,-158 24,-132 Q0,-142 -24,-132Z" fill="{hair}" stroke="{INK}" stroke-width="2"/>')
    elif name == "B":
        for cx in range(-22, 26, 9):
            g.append(f'<circle cx="{cx}" cy="{-142 + abs(cx) * 0.4}" r="8" fill="{hair}"/>')
    else:
        g.append(f'<path d="M-27,-122 Q-26,-152 0,-150 Q26,-152 27,-122 Q14,-138 -27,-122Z" '
                 f'fill="{hair}" stroke="{INK}" stroke-width="2"/>')
        if name == "A":
            g.append(f'<circle cx="0" cy="-154" r="9" fill="{hair}" stroke="{INK}" stroke-width="2"/>')
    # face
    lens = goggles or "white"
    for cx in (-10, 10):
        g.append(f'<circle cx="{cx}" cy="-122" r="8" fill="{lens}" fill-opacity="0.6" stroke="{INK}" stroke-width="2"/>')
        g.append(f'<circle cx="{cx}" cy="-121" r="2.2" fill="{INK}"/>')
    g.append(f'<line x1="-2" y1="-122" x2="2" y2="-122" stroke="{INK}" stroke-width="2"/>')
    mouth = {"happy": "M-8,-108 Q0,-100 8,-108", "worried": "M-7,-104 Q0,-110 7,-104",
             "tired": "M-7,-106 L7,-106", "wow": None}[mood]
    if mouth:
        g.append(f'<path d="{mouth}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    else:
        g.append(f'<ellipse cx="0" cy="-106" rx="4" ry="5" fill="{INK}"/>')
    if mood == "tired":
        g.append(f'<path d="M30,-140 q4,8 0,12 q-4,-4 0,-12Z" fill="#5DADE2" stroke="{INK}" stroke-width="1"/>')
    if pose == "paint":  # brush in the raised hand
        g.append(f'<line x1="50" y1="-110" x2="66" y2="-132" stroke="#8B5A2B" stroke-width="5" stroke-linecap="round"/>')
        g.append(f'<circle cx="68" cy="-135" r="5" fill="{accent}" stroke="{INK}" stroke-width="1.5"/>')
    g.append("</g>")
    return "".join(g)


def buckets(x, y, colors=("#E74C3C", "#3498DB", "#F1C40F"), label="Paint station"):
    s = []
    for i, c in enumerate(colors):
        bx = x + i * 30
        s.append(f'<path d="M{bx},{y - 30} L{bx + 24},{y - 30} L{bx + 21},{y} L{bx + 3},{y} Z" '
                 f'fill="#BDC3C7" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<ellipse cx="{bx + 12}" cy="{y - 30}" rx="12" ry="4" fill="{c}" stroke="{INK}" stroke-width="2"/>')
    if label:
        s.append(f'<text x="{x + 40}" y="{y + 18}" font-family="{FONT}" font-size="12" '
                 f'text-anchor="middle" fill="{INK}">{label}</text>')
    return "".join(s)


def canvas(x, y, w, h, rows, total=12, pattern="seq", colors=None, zigzag=False, easel=True,
           guessed=(), border=None):
    """An easel with a canvas whose lines are progressively painted.

    rows: which line indices are painted (list) -- each painted line is a stroke.
    guessed: lines filled in by guessing, drawn pale and dashed.
    border: colour of the canvas frame (the painter's goggles), default black.
    """
    colors = colors or ["#E74C3C", "#3498DB", "#F1C40F", "#2ECC71", "#9B59B6", "#E67E22"]
    s = []
    if easel:
        s.append(f'<path d="M{x + 10},{y + h + 50} L{x + w / 2},{y - 12} L{x + w - 10},{y + h + 50}" '
                 f'fill="none" stroke="#8B5A2B" stroke-width="6" stroke-linecap="round"/>')
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FDFEFE" '
             f'stroke="{border or INK}" stroke-width="{2 if border else 3}"/>')
    lh = h / total
    for r in guessed:
        c = colors[r % len(colors)]
        yy = y + (r + 0.5) * lh
        s.append(f'<path d="M{x + 6},{yy} q{w / 8},-{lh / 3} {w / 4},0 t{w / 4},0 t{w / 4},0 t{w / 4 - 12},0" '
                 f'fill="none" stroke="{c}" stroke-opacity="0.45" stroke-width="{lh * 0.55}" '
                 f'stroke-dasharray="{lh * 0.9} {lh * 0.6}"/>')
    for r in rows:
        c = colors[r % len(colors)]
        yy = y + (r + 0.5) * lh +2
        s.append(f'<path d="M{x + 6},{yy} q{w / 8},-{lh / 3} {w / 4},0 t{w / 4},0 t{w / 4},0 t{w / 4 - 12},0" '
                 f'fill="none" stroke="{c}" stroke-width="{lh * 0.6}" stroke-linecap="round"/>')
    if zigzag:
        pts = []
        for r in range(total):
            yy = y + (r + 0.5) * lh
            xs = (x + 6, x + w - 6) if r % 2 == 0 else (x + w - 6, x + 6)
            pts += [f"{xs[0]},{yy}", f"{xs[1]},{yy}"]
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="1.8" '
                 f'stroke-dasharray="5 3"/>')
    return "".join(s)


def path_dots(x1, y1, x2, y2, label=None):
    s = [f'<path d="M{x1},{y1} Q{(x1 + x2) / 2},{min(y1, y2) + 30} {x2},{y2}" fill="none" '
         f'stroke="{INK}" stroke-width="2.5" stroke-dasharray="3 7" stroke-linecap="round"/>']
    if label:
        s.append(f'<text x="{(x1 + x2) / 2}" y="{max(y1, y2) + 38}" font-family="{FONT}" font-size="13" '
                 f'text-anchor="middle" fill="{INK}">{label}</text>')
    return "".join(s)


def clock(x, y, r=20, label="TR"):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{INK}" stroke-width="2.5"/>'
            f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y - r * 0.7}" stroke="{INK}" stroke-width="2.5"/>'
            f'<line x1="{x}" y1="{y}" x2="{x + r * 0.5}" y2="{y + r * 0.2}" stroke="{INK}" stroke-width="2.5"/>'
            f'<text x="{x}" y="{y + r + 16}" font-family="{FONT}" font-size="13" font-weight="bold" '
            f'text-anchor="middle">{label}</text>')


def sparkles(x, y, n=5, color="#F4D03F"):
    rng = np.random.default_rng(3)
    s = []
    for _ in range(n):
        cx, cy, r = x + rng.uniform(-35, 35), y + rng.uniform(-60, 20), rng.uniform(6, 12)
        pts = " ".join(f"{cx + (r if i % 2 == 0 else r / 3) * np.cos(i * np.pi / 4):.1f},"
                       f"{cy + (r if i % 2 == 0 else r / 3) * np.sin(i * np.pi / 4):.1f}" for i in range(8))
        s.append(f'<polygon points="{pts}" fill="{color}" stroke="{INK}" stroke-width="1.2"/>')
    return "".join(s)


def screen(x, y, w, h, img_uri, label=None):
    s = [f'<rect x="{x - 8}" y="{y - 8}" width="{w + 16}" height="{h + 16}" rx="8" fill="#566573" stroke="{INK}" stroke-width="2.5"/>',
         f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{img_uri}" preserveAspectRatio="none"/>',
         f'<rect x="{x + w / 2 - 10}" y="{y + h + 8}" width="20" height="16" fill="#566573" stroke="{INK}" stroke-width="2"/>',
         f'<rect x="{x + w / 2 - 30}" y="{y + h + 24}" width="60" height="6" fill="#566573" stroke="{INK}" stroke-width="2"/>']
    if label:
        s.append(f'<text x="{x + w / 2}" y="{y + h + 48}" font-family="{FONT}" font-size="12" '
                 f'text-anchor="middle">{label}</text>')
    return "".join(s)


def panel(i, bg, content):
    x0 = i * (PANEL_W + GAP)
    return (f'<g transform="translate({x0},0)">'
            f'<clipPath id="c{i}"><rect width="{PANEL_W}" height="{PANEL_H}"/></clipPath>'
            f'<g clip-path="url(#c{i})"><rect width="{PANEL_W}" height="{PANEL_H}" fill="{bg}"/>'
            f'<rect y="{PANEL_H - 40}" width="{PANEL_W}" height="40" fill="#D5B895"/>{content}</g>'
            f'<rect width="{PANEL_W}" height="{PANEL_H}" fill="none" stroke="{INK}" stroke-width="4"/></g>')


def strip(name, panels, title):
    n = len(panels)
    W = n * PANEL_W + (n - 1) * GAP
    body = "".join(panel(i, bg, c) for i, (bg, c) in enumerate(panels))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -4 {W + 8} {PANEL_H + 8}" '
           f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>')
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(svg)
    print("wrote", name)


# ------------------------------------------------------------------------- scenes
def main():
    img = P.flower()
    k = P.fft2c(img)
    flower_png = png_uri(flower_rgb())
    pedestal_png = png_uri(flower_rgb(transparent=True))
    kspace_png = png_uri(np.log1p(np.abs(k)))
    alias_png = png_uri(folded_rgb(2))
    alias4_png = png_uri(folded_rgb(4))

    # # ---- Prologue: meet the crew
    # crew = "".join(scientist(60 + 62 * i, 262, n, s=0.62, mood="happy",
    #                          pose="cheer" if i == 2 else "stand")
    #                for i, n in enumerate(["A", "E", "B", "C", "D"]))
    # strip("00-prologue", [
    #     ("#AED6F1",
    #      caption(10, 12, 300, "The crew, I have a new mission for you. I want this flower on the computer but no camera allowed! You can only use a Fourier transform machine... Goog luck!") +
    #      f'<rect x="250" y="120" width="90" height="140" fill="#A04000" stroke="{INK}" stroke-width="2.5"/>'
    #      f'<image x="255" y="60" width="80" height="70" href="{pedestal_png}"/>' +
    #      scientist(120, 262, "Fourier", pose="point", s=0.9) +
    #      bubble(25, 60, 190, "I want the best quality, as quickly as possible!", (110, 140))),
    #     ("#FAD7A0", crew + bubble(60, 20, 300, "We'll paint it line by line and put the painting in the machine!", (190, 150))),
    # ], "Prologue: the crew receives its mission")

    # ---- Prologue: meet the crew
    crew = "".join(scientist(60 + 62 * i, 262, n, s=0.62, mood="happy", pose="cheer" if i == 2 else "stand")
                   for i, n in enumerate(["A", "E", "B", "C", "D"]))
    strip("00-prologue", [
        ("#AED6F1",
         caption(10, 10, 400, "Crew, I have a new mission for you. I want this flower on the computer, "
                              "but no camera allowed! You can only use a Fourier transform machine... Good luck!") +
         # a smaller pedestal, with the flower standing on it
         f'<rect x="295" y="200" width="70" height="60" fill="#A04000" stroke="{INK}" stroke-width="2.5"/>'
         f'<image x="285" y="122" width="90" height="80" href="{pedestal_png}"/>' +
         scientist(85, 262, "Fourier", pose="point", s=0.75) +
         bubble(15, 92, 240, "I want the best quality, as quickly as possible!", (85, 136))),
        ("#FAD7A0", crew + bubble(60, 20, 300, "We'll paint it line by line and put the painting in the machine!", (190, 150))),
    ], "Prologue: the crew receives its mission")

    # ---- Chapter 2: GRE, walking back every TR
    strip("01-gre", [
        ("#D6EAF8",
         caption(10, 10, 250, "ONE line per trip...") +
         buckets(20, 258) + canvas(270, 90, 130, 120, rows=[0, 1, 2]) +
         scientist(240, 262, "A", pose="paint", s=0.85) +
         bubble(20, 60, 190, "One line done! Now back to the paint station...", (215, 150))),
        ("#D6EAF8",
         buckets(20, 258) + canvas(300, 90, 110, 110, rows=[0, 1, 2, 3]) +
         path_dots(110, 250, 290, 250, "walking back") +
         scientist(170, 262, "A", pose="walk", mood="tired", s=0.85, flip=True) + clock(380, 40) +
         bubble(20, 20, 250, "96 lines... 96 trips... this will take forever!", (170, 120))),
    ], "Chapter 1: A paints one line per trip")

    # ---- Chapter 3: EPI, carry everything, zigzag
    strip("03-epi", [
        ("#D5F5E3",
         buckets(80, 142, label=None) +
         scientist(120, 262, "B", pose="carry", s=0.85) +
         bubble(200, 30, 220, "I'll carry ALL the paint with me !", (160, 130))),
        ("#D5F5E3",
         canvas(250, 70, 160, 160, rows=list(range(9)), zigzag=True) +
         scientist(150, 262, "B", pose="paint", s=0.8) +
         bubble(10, 60, 170, "Left, right, left, right... all in one go!", (135, 135)) +
         caption(10, 10, 420, "...but the paint slowly dries.")),
    ], "Chapter 3: B carries all the paint and zigzags")

    # ---- Chapter 4: undersampling, aliasing
    strip("04-undersampling", [
        ("#E8DAEF",
         canvas(250, 70, 140, 140, rows=[0, 2, 4, 6, 8, 10], total=12) +
         scientist(150, 262, "C", pose="paint", s=0.85) +
         bubble(20, 30, 200, "Shhh... I'll just skip every other line. Twice as fast!", (140, 130))),
        ("#E8DAEF",
         screen(230, 50, 150, 150, alias_png, "the scanner's result") +
         scientist(110, 262, "C", pose="stand", mood="wow", s=0.85) +
         bubble(20, 20, 170, "Uh-oh... why are there TWO flowers?!", (110, 130))),
    ], "Chapter 4: C skips lines and gets two flowers")


    # ---- Chapter 5: SENSE, four painters placed AROUND the flower, like the coils
    # Each painter sits at one corner, looks at the flower through coloured goggles,
    # and paints only 1 line in 4 on their own small canvas.
    corners = [  # (scientist x, feet y, flip, canvas x, canvas y, part of the flower they see best)
        (38, 160, False, 64, 98, (200, 110)),    # top-left     (coil 1)
        (402, 160, True, 330, 98, (245, 110)),   # top-right    (coil 2)
        (38, 262, False, 64, 196, (210, 175)),   # bottom-left  (coil 3)
        (402, 262, True, 330, 196, (235, 175)),  # bottom-right (coil 4)
    ]
    sparse = [0, 4, 8]
    around = (f'<rect x="185" y="190" width="70" height="70" fill="#A04000" stroke="{INK}" stroke-width="2.5"/>'
              f'<image x="165" y="85" width="110" height="110" href="{pedestal_png}"/>')
    for (sx, sy, flip, cx, cy, (gx, gy)), c in zip(corners, QUARTET):
        if sy < 200:  # a little shelf for the painters at the top
            around += f'<rect x="{sx - 32}" y="{sy}" width="64" height="7" fill="#8B5A2B" stroke="{INK}" stroke-width="1.5"/>'
        # dotted gaze line: each painter looks at the part of the flower closest to them
        around += (f'<line x1="{sx}" y1="{sy - 55}" x2="{gx}" y2="{gy}" stroke="{c}" stroke-width="2.5" '
                   f'stroke-dasharray="4 4"/>')
        around += canvas(cx, cy, 46, 46, rows=sparse, total=12, colors=[c], easel=False, border=INK)
        around += scientist(sx, sy, "Q", goggles=c, s=0.45, pose="paint", flip=flip)
    strip("05-sense", [
        ("#FADBD8",
         caption(10, 8, 420, "Four painters all around the flower, each painting only 1 line in 2. "
                             "Each one sees best the part of the flower closest to them.") + around),
        ("#FADBD8",
         screen(40, 50, 120, 120, alias4_png, "folded picture") +
         f'<path d="M185,115 L245,115" stroke="{INK}" stroke-width="5"/>'
         f'<polygon points="245,103 268,115 245,127" fill="{INK}"/>' +
         screen(290, 50, 120, 120, flower_png, "unfolded!") +
         caption(20, 232, 400, "Each painter knows which part of the canvas they see best. The computer uses that to unfold the picture.")),
    ], "Chapter 5: the four painters around the flower, then the unfolded picture")

    # ---- Chapter 6: GRAPPA
    # Panel 1: the four canvases, completed with guessed (pale) lines.
    # Panel 2: like SENSE, a complete canvas goes into the machine -> the flower.
    acquired, centre = [0, 4, 8, 12], [5, 6, 7]
    missing = [r for r in range(13) if r not in acquired + centre]

    def quartet(pose, guessed=()):
        return "".join(
            canvas(128 + 77 * i, 95, 64, 72, rows=acquired + centre, total=13, colors=[c],
                   easel=False, border=INK, guessed=guessed) +
            scientist(160 + 77 * i, 262, "Q", goggles=c, s=0.5, pose=pose)
            for i, c in enumerate(QUARTET))

    strip("06-grappa", [
        ("#D1F2EB",
         scientist(55, 262, "D", pose="point", s=0.75) + quartet("cheer", guessed=missing) +
         bubble(10, 12, 300, "From the common zone we learned the rule can guess every missing line!", (60, 128))),
        ("#D1F2EB",
         canvas(45, 55, 120, 130, rows=acquired + centre, total=13, colors=QUARTET,
                easel=False, border=INK, guessed=missing) +
         f'<text x="105" y="208" font-family="{FONT}" font-size="12" text-anchor="middle">complete canvas</text>'
         f'<path d="M185,120 L245,120" stroke="{INK}" stroke-width="5"/>'
         f'<polygon points="245,108 268,120 245,132" fill="{INK}"/>' +
         screen(290, 55, 120, 120, flower_png, "reconstructed!") +
         caption(20, 232, 400, "No line is missing any more: We get the flower without any copies !")),
    ], "Chapter 6: the guessed lines complete the canvases, and the machine gives back the flower")

if __name__ == "__main__":
    main()
