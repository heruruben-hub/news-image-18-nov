#!/usr/bin/env python3
"""Sum up Wednesday 18 November 2026's world news in one image.

Deterministic infographic drawn from scratch with the Python standard
library only: no network, no clock, no randomness. Running this program
twice writes byte-identical bytes to <output dir>/entry.png, where the
output dir is $MAKEFUN_OUTPUT_DIR when set, else /output.

Layout: a newspaper-style front page, 1024x1024. A dark masthead names
the day in huge letters, then six panels (2 columns x 3 rows), each with
a simple drawn icon, a bold headline and one short factual sublabel.
All text is rendered with the embedded 5x7 bitmap font below, scaled up
in whole pixels so it stays crisp and legible at small sizes.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one tuple of 7 rows per glyph, '#' = ink.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "+": (".....", "..#..", "..#..", ".####", "..#..", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
}


def text_width(s, scale):
    """Pixel width of string s at the given integer scale."""
    return len(s) * 6 * scale - scale if s else 0


# ---------------------------------------------------------------- canvas
class Canvas:
    """A flat RGB pixel buffer with clipped rectangle drawing."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def png_bytes(self):
        """Encode the buffer as a complete, valid PNG file."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter type 0 (None) for every row
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            body = tag + data
            return (struct.pack(">I", len(data)) + body
                    + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


# ---------------------------------------------------------------- shapes
def disc(cv, cx, cy, r, color):
    """Filled circle by distance test (deterministic, no anti-alias)."""
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                cv.set_px(xx, yy, color)


def ring(cv, cx, cy, r, thick, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if (r - thick) * (r - thick) < d2 <= r * r:
                cv.set_px(xx, yy, color)


def line(cv, x0, y0, x1, y1, thick, color):
    """Thick straight line: stamp small discs along the segment."""
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i // steps
        y = y0 + (y1 - y0) * i // steps
        disc(cv, x, y, thick // 2, color)


def draw_text(cv, x, y, s, scale, color):
    """Draw string s with the 5x7 font at integer scale; returns width."""
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "#":
                    cv.rect(cx + gx * scale, y + gy * scale, scale, scale,
                            color)
        cx += 6 * scale
    return cx - scale - x if s else 0


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


# ---------------------------------------------------------------- icons
# Each icon draws inside a box with top-left (x, y) and size s (square).

def icon_flags(cv, x, y, s):
    """Three summit flags: China, Russia, United States (simplified)."""
    pole = (70, 70, 70)
    poles = (x + 7 * s // 100, x + 2 * s // 5, x + 11 * s // 15)
    for px in poles:
        cv.rect(px - 2, y + 4, 4, s - 8, pole)
        disc(cv, px, y + 4, 4, (200, 170, 60))
    fw, fh = 6 * s // 25, s // 5
    # China: red flag, one big yellow star
    fx, fy = poles[0] + 2, y + 6
    cv.rect(fx, fy, fw, fh, (222, 41, 16))
    disc(cv, fx + fw // 4, fy + fh // 3, 3, (255, 222, 0))
    # Russia: white / blue / red horizontal stripes
    fx = poles[1] + 2
    cv.rect(fx, fy, fw, fh // 3, (245, 245, 245))
    cv.rect(fx, fy + fh // 3, fw, fh // 3, (0, 57, 166))
    cv.rect(fx, fy + 2 * fh // 3, fw, fh - 2 * fh // 3, (213, 0, 50))
    # USA: red stripes with a blue canton
    fx = poles[2] + 2
    cv.rect(fx, fy, fw, fh, (178, 34, 52))
    for i in range(1, 6, 2):
        cv.rect(fx, fy + i * fh // 6, fw, fh // 6, (245, 245, 245))
    cv.rect(fx, fy, fw // 2, fh // 2, (60, 59, 110))
    # ground line
    cv.rect(x + 2, y + s - 6, s - 4, 4, pole)


def icon_drone(cv, x, y, s):
    """Quadcopter drone over a shield: attacks flown, defences up."""
    dark = (38, 44, 58)
    cx, cy = x + s // 2, y + s // 3
    cv.rect(cx - s // 10, cy - s // 16, s // 5, s // 8, dark)  # body
    disc(cv, cx, cy + s // 32, s // 20, (200, 40, 40))          # red eye
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ax, ay = cx + dx * s // 4, cy + dy * s // 6
        line(cv, cx, cy, ax, ay, 4, dark)
        ring(cv, ax, ay, s // 9, 3, dark)
    # shield below: flat top, sides tapering to a point, white check
    sx, sy = cx, y + 3 * s // 4
    green = (46, 125, 50)
    cv.rect(sx - s // 6, sy - s // 4, s // 3, s // 12, green)
    for i in range(s // 5):
        wdt = s // 6 - (i * i) // (s // 3)
        cv.rect(sx - wdt, sy - s // 6 + i, 2 * wdt, 1, green)
    line(cv, sx - s // 13, sy - s // 7, sx - s // 30, sy - s // 22, 5,
         (245, 248, 245))
    line(cv, sx - s // 30, sy - s // 22, sx + s // 11, sy + s // 30, 5,
         (245, 248, 245))


def icon_bridge(cv, x, y, s):
    """Suspension bridge deck with a starburst: a struck bridge."""
    steel = (55, 71, 99)
    base = y + 4 * s // 5
    cv.rect(x + 2, base, s - 4, 5, steel)                       # deck
    for tx in (x + s // 5, x + 4 * s // 5):
        cv.rect(tx - 3, y + s // 4, 6, base - y - s // 4, steel)  # towers
    for i in range(9):                                          # cables
        t = i / 8.0
        px = x + s // 5 + int((x + 4 * s // 5 - x - s // 5) * t)
        py = y + s // 4 + int((base - y - s // 4) * (2 * t - 1) ** 2)
        line(cv, px, y + s // 4 if i in (0, 8) else py, px, base, 2, steel)
    # water
    for wy in (base + 10, base + 18):
        for wx in range(x + 6, x + s - 10, 18):
            cv.rect(wx, y + wy - y, 10, 3, (90, 140, 190))
    # starburst at mid-span
    bx, by = x + s // 2, base - 6
    for ang in range(8):
        import math
        dx = int(16 * math.cos(ang * math.pi / 4))
        dy = int(16 * math.sin(ang * math.pi / 4))
        line(cv, bx, by, bx + dx, by + dy, 4, (232, 119, 34))
    disc(cv, bx, by, 7, (241, 196, 15))


def icon_capitol(cv, x, y, s):
    """Capitol dome over columns and steps, plus a big election check."""
    stone = (90, 100, 120)
    cx = x + s // 2
    u = s / 150.0  # layout below is drawn on a 150-unit grid

    def R(rx, ry, rw, rh, color=stone):
        cv.rect(x + int(rx * u), y + int(ry * u), max(1, int(rw * u)),
                max(1, int(rh * u)), color)

    R(14, 128, 122, 8)          # steps
    R(22, 121, 106, 7)
    R(28, 114, 94, 7)           # floor
    for i in range(5):          # columns
        R(34 + i * 22, 84, 8, 30)
    R(26, 76, 98, 8)            # entablature
    for dy in range(28):        # squat dome, one row at a time
        hw = int(46 * (1 - (dy / 28.0) ** 2) ** 0.5)
        R(75 - hw, 75 - dy, 2 * hw, 1)
    R(73, 38, 4, 10)            # spire
    disc(cv, cx, y + int(34 * u), 4, (200, 170, 60))
    # big green check, top right, clear of the dome
    gx, gy = x + int(114 * u), y + int(6 * u)
    line(cv, gx, gy + int(10 * u), gx + int(8 * u), gy + int(18 * u), 7,
         (39, 174, 96))
    line(cv, gx + int(8 * u), gy + int(18 * u), gx + int(26 * u), gy, 7,
         (39, 174, 96))


def icon_globe(cv, x, y, s):
    """Globe with a rising thermometer: climate talks."""
    cx, cy = x + s // 2 - s // 10, y + s // 2
    r = s // 3
    disc(cv, cx, cy, r, (52, 152, 219))
    green = (46, 160, 90)
    disc(cv, cx - r // 2, cy - r // 3, r // 3, green)   # continent blobs
    disc(cv, cx + r // 3, cy + r // 4, r // 4, green)
    disc(cv, cx - r // 4, cy + r // 2, r // 5, green)
    ring(cv, cx, cy, r, 3, (30, 90, 140))
    # thermometer on the right
    tx = x + 4 * s // 5
    cv.rect(tx - 4, y + s // 6, 8, s // 2, (192, 57, 43))
    disc(cv, tx, y + s // 6 + s // 2 + 6, s // 9, (192, 57, 43))
    cv.rect(tx - 4, y + s // 6, 8, 6, (120, 120, 120))


def icon_chip(cv, x, y, s):
    """AI chip with pins and a rising bar chart: tech earnings."""
    body = (44, 62, 80)
    bx, by = x + s // 4, y + s // 4
    bs = s // 2
    for i in range(4):  # pins
        px = bx + (i + 1) * bs // 5
        cv.rect(px - 2, by - 8, 4, 8, body)
        cv.rect(px - 2, by + bs, 4, 8, body)
        py = by + (i + 1) * bs // 5
        cv.rect(bx - 8, py - 2, 8, 4, body)
        cv.rect(bx + bs, py - 2, 8, 4, body)
    cv.rect(bx, by, bs, bs, body)
    cv.rect(bx + bs // 4, by + bs // 4, bs // 2, bs // 2, (241, 196, 15))
    # rising bars at bottom right
    for i, hh in enumerate((10, 18, 28)):
        cv.rect(x + s // 2 + i * 14, y + s - 8 - hh, 10, hh, (39, 174, 96))


# ---------------------------------------------------------------- page
CREAM = (247, 243, 232)
NAVY = (13, 27, 46)
GOLD = (241, 196, 15)
WHITE = (255, 255, 255)
INK = (30, 34, 44)
GREY = (96, 104, 116)
CARD_LINE = (205, 200, 188)

# tag, accent, icon, headline lines, sublabel lines
PANELS = [
    ("ASIA - DIPLOMACY", (192, 57, 43), icon_flags,
     ("XI + PUTIN MEET", "IN SHENZHEN"),
     ("APEC SUMMIT IN CHINA.", "TRUMP 3-WAY TALKS SET", "FOR THURSDAY.")),
    ("MIDDLE EAST - CONFLICT", (211, 84, 0), icon_drone,
     ("IRAN DRONES HIT", "KUWAIT US BASE"),
     ("BAHRAIN STOPS MISSILES.", "US HIT IRAN LAUNCH SITE", "ON QESHM ISLAND.")),
    ("EUROPE - WAR", (41, 128, 185), icon_bridge,
     ("UKRAINE HITS", "CRIMEA BRIDGE"),
     ("SECOND NIGHT STRIKE ON", "THE KERCH BRIDGE LINK", "TO OCCUPIED CRIMEA.")),
    ("AMERICAS - POLITICS", (17, 122, 101), icon_capitol,
     ("PELTOLA WINS", "ALASKA SENATE"),
     ("DEMOCRATS TAKE SENATE", "WITH A 56-44 MAJORITY.")),
    ("WORLD - CLIMATE", (30, 132, 73), icon_globe,
     ("COP31 TALKS:", "FOSSIL FUEL ROW"),
     ("IN ANTALYA, TURKIYE.", "PHASE-OUT OF FOSSIL", "FUELS DIVIDES TALKS.")),
    ("TECH - BUSINESS", (142, 68, 173), icon_chip,
     ("NVIDIA SALES", "DOUBLE TO $116BN"),
     ("REVENUE $115.8BN AS THE", "BOARD RULES OUT A", "HUANG COMEBACK.")),
]


def draw_panel(cv, x, y, w, h, panel):
    tag, accent, icon, headline, sub = panel
    cv.rect(x - 3, y - 3, w + 6, h + 6, CARD_LINE)      # border
    cv.rect(x, y, w, h, WHITE)                          # card
    cv.rect(x, y, w, 40, accent)                        # tag strip
    draw_text(cv, x + 14, y + 10, tag, 3, WHITE)
    cv.rect(x + 12, y + 58, 158, 158, (238, 240, 244))  # icon tile
    icon(cv, x + 16, y + 62, 150)
    tx = x + 186
    for i, ln in enumerate(headline):
        draw_text(cv, tx, y + 66 + i * 30, ln, 3, INK)
    cv.rect(tx, y + 130, 110, 5, accent)                # rule
    for i, ln in enumerate(sub):
        draw_text(cv, tx, y + 148 + i * 22, ln, 2, GREY)


def compose():
    cv = Canvas(W, H, CREAM)
    # masthead
    cv.rect(0, 0, W, 182, NAVY)
    draw_text_centered(cv, W // 2, 12, "WORLD NEWS", 3, GOLD)
    draw_text_centered(cv, W // 2, 40, "WEDNESDAY", 10, WHITE)
    draw_text_centered(cv, W // 2, 122, "18 NOVEMBER 2026", 7, GOLD)
    cv.rect(0, 182, W, 6, (192, 57, 43))
    # panels: 2 columns x 3 rows
    pw, ph, gap, mx, top = 484, 262, 14, 20, 200
    for i, panel in enumerate(PANELS):
        px = mx + (i % 2) * (pw + 16)
        py = top + (i // 2) * (ph + gap)
        draw_panel(cv, px, py, pw, ph, panel)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(compose().png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
