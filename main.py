#!/usr/bin/env python3
"""news-image-20261124 v1 — draws Tuesday 24 November 2026's world news as one
newspaper front page. Stdlib only (zlib/struct/os/sys). Deterministic: the same
bytes on every run. No network, no Pillow, no files read besides this source.
Layout follows the v4/v6 formula: giant masthead, KPI strip, 3 heroes, 10 cards,
world map + 27 more stories, DATE CHECK footer. No v7 status package."""
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (247, 240, 220)
NAVY = (26, 47, 90)
INK = (30, 32, 38)
RED = (163, 30, 34)
DARKRED = (140, 40, 30)
GRAY = (112, 106, 94)
TAN = (217, 196, 154)
TAN_D = (150, 125, 85)
SLATE = (70, 90, 120)
TEAL = (40, 100, 80)
WHITE = (255, 255, 255)
CREAM2 = (238, 228, 200)

# 5x7 bitmap font: each glyph is 7 rows, 5 bits, bit 4 = leftmost column.
F = {
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x18),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '*': (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    '-': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '=': (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    '@': (0x0E, 0x11, 0x01, 0x0D, 0x15, 0x15, 0x0E),
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x01, 0x01, 0x01, 0x01, 0x01, 0x11, 0x0E),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    '\\': (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '^': (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
    '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    '`': (0x04, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00),
    'a': (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    'b': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    'c': (0x00, 0x00, 0x0E, 0x10, 0x10, 0x10, 0x0E),
    'd': (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    'e': (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    'f': (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x02, 0x0C),
    'k': (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm': (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    'n': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'o': (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    'p': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    'q': (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    'r': (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    's': (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    't': (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    'u': (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v': (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w': (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'x': (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    'y': (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'z': (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    '{': (0x02, 0x04, 0x04, 0x08, 0x04, 0x04, 0x02),
    '|': (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    '}': (0x08, 0x04, 0x04, 0x02, 0x04, 0x04, 0x08),
    '~': (0x00, 0x00, 0x00, 0x0E, 0x15, 0x00, 0x00),
    '·': (0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00, 0x00),
    '×': (0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x00),
    '—': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '–': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '’': (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '‘': (0x08, 0x08, 0x04, 0x00, 0x00, 0x00, 0x00),
    '“': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    '”': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
}
FALLBACK = F['?']


def glyph(ch):
    return F.get(ch, FALLBACK)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        row = bytes(bg) * w
        self.px = bytearray(row * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            i = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x0, x1, y, c):
        self.rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def ring(self, cx, cy, r, c):
        import math
        for a in range(0, 360, 2):
            t = math.radians(a)
            self.set(cx + int(r * math.cos(t)), cy + int(r * math.sin(t)), c)

    def poly(self, pts, c):
        # scanline even-odd fill
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    def char(self, x, y, ch, s, c, bold=False, shear=0):
        g = glyph(ch)
        off = max(1, s // 3) if bold else 0
        for r in range(7):
            bits = g[r]
            if not bits:
                continue
            sh = (r // 2) * shear
            for col in range(5):
                if bits >> (4 - col) & 1:
                    bx = x + col * s + sh
                    by = y + r * s
                    self.rect(bx, by, s, s, c)
                    if off:
                        self.rect(bx + off, by, s, s, c)

    def text(self, x, y, s, sc, c, bold=False, shear=0, spacing=0):
        cx = x
        for ch in s:
            self.char(cx, y, ch, sc, c, bold, shear)
            cx += (6 + spacing) * sc
        return cx

    def text_w(self, s, sc, spacing=0):
        return len(s) * (6 + spacing) * sc

    def text_c(self, cx, y, s, sc, c, bold=False, shear=0, spacing=0):
        self.text(cx - self.text_w(s, sc, spacing) // 2, y, s, sc, c, bold, shear, spacing)

    def wrap(self, text, max_chars):
        words, lines, cur = text.split(), [], ""
        for wd in words:
            add = wd if not cur else " " + wd
            if len(cur) + len(add) <= max_chars:
                cur += add
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, text, sc, c, max_chars, lh, max_lines=None, bold=False):
        lines = self.wrap(text, max_chars)
        if max_lines:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, sc, c, bold)
        return y + len(lines) * lh


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- content
KPIS = [
    ("+31%", ["Nvidia shares", "in a day"], "Reuters"),
    ("6.5%", ["Nasdaq jumps", "on the day"], "Reuters"),
    ("50", ["tankers hit", "in ship attacks"], "WSJ via Reuters"),
    ("450", ["German schools", "get bomb threats"], "Times of India"),
    ("50M", ["children in", "typhoid drive"], "Access24"),
    ("5,300", ["DRC Ebola", "deaths passed"], "C54"),
    ("~300", ["migrants cross", "into Mexico"], "Al Jazeera"),
    ("4.5%", ["Nikkei climbs", "in Asia rally"], "Reuters"),
]

HEROES = [
    dict(tag="GLOBAL", num="1", color=SLATE,
         title="Huang returns to Nvidia",
         body=("Nvidia brings back Jensen Huang as chief executive. Shares jump "
               "31% in a day; the Nasdaq climbs 6.5% and the S&P 500 4.7%. The "
               "board backs him unanimously."),
         quote="Trump says: \u201cI made the deal.\u201d",
         src="BBC \u00b7 Reuters", art="chart"),
    dict(tag="EUROPE", num="2", color=NAVY,
         title="Poland scrambles jets as drone crosses in",
         body=("Poland scrambles its air defence after a Russian drone enters "
               "its airspace near Dorohusk during an overnight Russian attack "
               "on Ukraine. NATO allies are informed at once."),
         quote="",
         src="en.h.ua", art="radar"),
    dict(tag="CLIMATE", num="3", color=TEAL,
         title="COP31 collapses; Pacific goes it alone",
         body=("Climate talks in Turkey fail and Pacific nations walk away to "
               "act on their own. Delegates call it the worst COP ever. The "
               "blame game points at Australia, holder of the COP31 presidency."),
         quote="",
         src="PINA", art="globe"),
]

CARDS = [
    ("US probes Iran link to ship attacks",
     "Washington investigates an Iranian link to dozens of cyberattacks on "
     "ships; up to 50 tankers are hit.",
     "WSJ via Reuters"),
    ("O'Hare halts flights in rush",
     "Chicago O'Hare orders a brief ground stop over a staffing shortage in "
     "the Thanksgiving rush.",
     "Times of India"),
    ("Russian cargo ship burns in Baltic",
     "A Russian cargo ship catches fire in the Gulf of Finland after a drone "
     "incident; a second vessel is towed.",
     "Careerindia"),
    ("Lagarde quits; ECB hunt begins",
     "The EU begins its search for a new ECB chief as Christine Lagarde "
     "resigns from the top job.",
     "C54"),
    ("Gaza strike kills three",
     "An Israeli airstrike kills at least three Palestinians near a police "
     "outpost in Khan Younis, southern Gaza.",
     "Reuters"),
    ("Sudan blackouts after drone raids",
     "RSF drone attacks strike power stations across Sudan and trigger mass "
     "blackouts.",
     "C54"),
    ("Asia stocks rally on Huang",
     "Kospi up 7.5%, Nikkei 4.5%, Taiwan 9.1% \u2014 the best day since "
     "31 July.",
     "Reuters"),
    ("Singapore lifts growth outlook",
     "Singapore lifts its 2026 growth forecast to about 6.0% after 6.1% "
     "expansion in the third quarter.",
     "Reuters"),
    ("Ebola toll passes 5,300",
     "Kenya discharges its last Ebola patient as the death toll in DR Congo "
     "passes 5,300.",
     "C54"),
    ("'El Chapo Isidro' to face trial",
     "The captured cartel figure known as 'El Chapo Isidro' will face trial "
     "in Mexico after his capture in Sinaloa.",
     "Al Jazeera"),
]

MORE = [
    "Canada-Qatar pact signed. \u2014 Reuters",
    "ICE arrests father and daughter. \u2014 Newsmriti",
    "Senate to vote on $9.4bn aid cuts. \u2014 Access24",
    "Trump hits Newsom over 548 commutations. \u2014 TOI",
    "Caravan of ~300 enters Mexico. \u2014 Al Jazeera",
    "Quake hits Peru cinemas. \u2014 Al Jazeera",
    "US trio convicted in Honduras. \u2014 Al Jazeera",
    "Milei's fall lifts borrowing costs. \u2014 FT",
    "Moscow tows drone-hit vessel in Baltic. \u2014 SYB.eu",
    "Norway court voids disputed oil licences. \u2014 C54",
    "450 German schools get bomb threats. \u2014 TOI",
    "Mossad saved Swift's Vienna shows. \u2014 TOI",
    "Israeli army storms West Bank camp. \u2014 SYB.eu",
    "Israeli fire kills Palestinian. \u2014 SYB.eu",
    "Iran warns EU sites with missiles. \u2014 SYB.eu",
    "Iran sentences singer to 74 lashes. \u2014 SYB.eu",
    "Libya condemns Benghazi strike. \u2014 Guardian",
    "UN mission demands Benghazi probe. \u2014 UN News",
    "South Africans vote amid service chaos. \u2014 C54",
    "Sahel states restart West Africa dialogue. \u2014 C54",
    "Typhoid jabs for 50m children. \u2014 Access24",
    "Flood missing hunted in Himalayas. \u2014 Access24",
    "Factory fire in Indonesia. \u2014 Careerindia",
    "India pledges $1.6bn Nepal relief. \u2014 Al Jazeera",
    "Fiji shuts schools as El Nino drought bites. \u2014 PINA",
    "Kiribati island Kanton evacuated. \u2014 PINA",
    "Six nations join coral-reef pact at COP31. \u2014 PINA",
]

THROWN_OUT = [
    "Trump warns Iran of \u201cvery traumatic\u201d outcome \u2014 23 Nov",
    "Lego opens EUR 1bn Portugal factory \u2014 23 Nov",
    "CrowdStrike buys Zscaler for $44bn \u2014 23 Nov",
    "Bolsonaro moved to ICU \u2014 23 Nov",
    "Boca Juniors win Copa Sudamericana \u2014 21 Nov",
    "EU 22nd sanctions package on Russia \u2014 23 Nov",
]

DATE_NOTE = [
    "Huang's return was first reported late on 23 Nov UTC, but the main BBC",
    "and Reuters coverage is dated 24 Nov \u2014 and no earlier edition could",
    "have carried it. Fiji's school closure, announced 24 Nov, takes effect",
    "from 30 Nov.",
]

DOTS = [
    (1, 70, 735), (2, 200, 712), (3, 228, 735), (4, 232, 752),
    (5, 88, 728), (6, 205, 700), (7, 192, 722), (8, 224, 748),
    (9, 205, 790), (10, 295, 725), (11, 272, 800), (12, 200, 815),
    (13, 55, 765),
]

CONTINENTS = [
    [(45, 712), (95, 705), (125, 720), (130, 745), (105, 760), (80, 782),
     (55, 775), (35, 745)],
    [(100, 800), (128, 795), (138, 820), (125, 855), (108, 840), (98, 815)],
    [(168, 705), (195, 700), (208, 712), (198, 732), (178, 730), (165, 718)],
    [(172, 745), (205, 740), (222, 762), (212, 800), (192, 812), (178, 785),
     (168, 762)],
    [(210, 702), (300, 700), (318, 725), (295, 752), (265, 745), (240, 728),
     (218, 715)],
    [(282, 805), (312, 800), (318, 820), (288, 828)],
]


# ---------------------------------------------------------------- drawing
def draw_art(cv, kind, x, y, w, h):
    """Small original illustration inside a hero panel."""
    if kind == "chart":
        base = y + h - 8
        cv.hline(x, x + w, base, NAVY)
        cv.vline(x, y + 4, base, NAVY)
        bars = [12, 20, 16, 30, 26, 44]
        bw = w // 7
        for i, bh in enumerate(bars):
            bx = x + 8 + i * bw
            cv.rect(bx, base - bh, bw - 4, bh, SLATE if i < 5 else RED)
        cv.line(x + 8, base - 14, x + w - 10, y + 6, RED)
        cv.line(x + w - 10, y + 6, x + w - 22, y + 8, RED)
        cv.line(x + w - 10, y + 6, x + w - 12, y + 18, RED)
    elif kind == "radar":
        cx, cy = x + w // 2 - 20, y + h // 2
        for r in (34, 26, 18, 10):
            cv.ring(cx, cy, r, SLATE)
        cv.line(cx, cy, cx + 30, cy - 26, RED)
        cv.circle(cx + 30, cy - 26, 3, RED)
        dx = x + w - 40
        cv.rect(dx, y + 14, 22, 6, INK)
        cv.rect(dx + 4, y + 10, 4, 4, INK)
        cv.rect(dx + 14, y + 10, 4, 4, INK)
        cv.hline(dx - 4, dx + 26, y + 8, INK)
        cv.hline(dx - 4, dx + 26, y + 24, INK)
        cv.circle(dx - 4, y + 8, 2, INK)
        cv.circle(dx + 26, y + 8, 2, INK)
        cv.circle(dx - 4, y + 24, 2, INK)
        cv.circle(dx + 26, y + 24, 2, INK)
    elif kind == "globe":
        cx, cy, r = x + 44, y + h // 2, 26
        cv.circle(cx, cy, r, (90, 140, 170))
        cv.ring(cx, cy, r, NAVY)
        cv.line(cx - r, cy, cx + r, cy, NAVY)
        cv.line(cx, cy - r, cx, cy + r, NAVY)
        cv.line(cx - 12, cy - r + 6, cx - 2, cy + 2, RED)
        cv.line(cx - 2, cy + 2, cx - 12, cy + r - 8, RED)
        cv.line(cx + 6, cy - r + 10, cx + 14, cy - 2, RED)
        cv.line(cx + 14, cy - 2, cx + 4, cy + r - 6, RED)
        cv.poly([(cx + 52, cy - 14), (cx + 66, cy - 14), (cx + 59, cy + 2)], TAN_D)
        cv.text(x + w - 78, y + h - 16, "COP31", 2, NAVY, bold=True)


def draw_hero(cv, x, y, w, h, hero):
    cv.rect(x, y, w, 16, hero["color"])
    cv.text(x + 6, y + 4, hero["tag"] + "  " + hero["num"], 1, WHITE, bold=True)
    ty = y + 22
    lines = cv.wrap(hero["title"], 24)
    for i, ln in enumerate(lines[:2]):
        cv.text(x + 6, ty + i * 15, ln, 2, NAVY, bold=True)
    ay = ty + 2 * 15 + 4
    draw_art(cv, hero["art"], x + 6, ay, w - 12, 52)
    by = ay + 56
    end = cv.para(x + 6, by, hero["body"], 1, INK, 48, 9, max_lines=4)
    if hero["quote"]:
        cv.text(x + 6, end + 2, hero["quote"], 1, DARKRED, bold=True)
        end += 11
    cv.text(x + 6, y + h - 12, hero["src"], 1, GRAY)
    cv.rect(x, y, w, 1, NAVY)
    cv.rect(x, y + h - 1, w, 1, NAVY)
    cv.rect(x, y, 1, h, NAVY)
    cv.rect(x + w - 1, y, 1, h, NAVY)


def draw_card(cv, x, y, w, h, num, title, body, src):
    cv.rect(x, y, w, 1, NAVY)
    cv.rect(x, y + h - 1, w, 1, NAVY)
    cv.rect(x, y, 1, h, NAVY)
    cv.rect(x + w - 1, y, 1, h, NAVY)
    cv.text(x + 6, y + 5, str(num), 1, RED, bold=True)
    ty = y + 16
    lines = cv.wrap(title, 28)
    for i, ln in enumerate(lines[:2]):
        cv.text(x + 6, ty + i * 9, ln, 1, NAVY, bold=True)
    cv.para(x + 6, ty + 2 * 9 + 3, body, 1, INK, 28, 9, max_lines=4)
    cv.text(x + 6, y + h - 12, str(num) + " \u00b7 " + src, 1, GRAY)


def build():
    cv = Canvas(W, H, PAPER)
    # outer double border
    cv.rect(8, 8, W - 16, 1, NAVY)
    cv.rect(8, H - 9, W - 16, 1, NAVY)
    cv.rect(8, 8, 1, H - 16, NAVY)
    cv.rect(W - 9, 8, 1, H - 16, NAVY)
    cv.rect(14, 14, W - 28, 1, NAVY)
    cv.rect(14, H - 15, W - 28, 1, NAVY)
    cv.rect(14, 14, 1, H - 28, NAVY)
    cv.rect(W - 15, 14, 1, H - 28, NAVY)

    # masthead
    cv.text_c(W // 2, 30, "Tuesday 24 November 2026", 6, NAVY, bold=True)
    cv.text_c(W // 2, 82, "THE WORLD IN ONE DAY", 2, NAVY, bold=True, spacing=2)
    cv.text_c(W // 2, 104, "40 STORIES \u00b7 7 REGIONS \u00b7 AS REPORTED ON "
             "TUESDAY 24 NOVEMBER 2026", 1, RED, bold=True)
    cv.text_c(W // 2, 120, "Huang back \u00b7 Poland scrambles \u00b7 COP31 fails "
             "\u00b7 Asia rallies", 2, DARKRED, shear=1)
    cv.hline(24, W - 24, 140, NAVY)

    # KPI strip
    kx, ky, kw = 24, 148, 122
    for i, (num, label, src) in enumerate(KPIS):
        cx = kx + i * kw
        if i:
            cv.vline(cx, ky, ky + 44, GRAY)
        cv.text_c(cx + kw // 2, ky, num, 2, NAVY, bold=True)
        for j, ln in enumerate(label):
            cv.text_c(cx + kw // 2, ky + 17 + j * 9, ln, 1, INK)
        cv.text_c(cx + kw // 2, ky + 36, src, 1, GRAY)
    cv.hline(24, W - 24, 198, NAVY)

    # heroes
    hx, hy, hw, hh, gap = 24, 206, 318, 186, 10
    for i, hero in enumerate(HEROES):
        draw_hero(cv, hx + i * (hw + gap), hy, hw, hh, hero)

    # cards, two rows of five
    cw, ch, cg = 188, 118, 9
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            title, body, src = CARDS[idx]
            draw_card(cv, 24 + col * (cw + cg), 402 + row * (ch + 8),
                      cw, ch, 4 + idx, title, body, src)

    # map + list
    cv.hline(24, W - 24, 652, NAVY)
    cv.text(24, 660, "WHERE IT HAPPENED", 1, NAVY, bold=True)
    cv.text(340, 660, "ALSO ON TUESDAY 24 NOVEMBER \u2014 27 MORE STORIES",
            1, NAVY, bold=True)
    for pts in CONTINENTS:
        cv.poly(pts, TAN)
    for n, dx, dy in DOTS:
        cv.circle(dx, dy, 7, NAVY)
        s = str(n)
        cv.text(dx - len(s) * 3, dy - 3, s, 1, WHITE, bold=True)
    cv.text(24, 862, "Dots mark the 13 featured stories.", 1, GRAY)
    lx, ly = 340, 676
    col_w = 330
    for i, item in enumerate(MORE):
        col = 0 if i < 14 else 1
        row = i if i < 14 else i - 14
        cv.text(lx + col * col_w, ly + row * 13,
                "%d. %s" % (14 + i, item), 1, INK)

    # DATE CHECK footer
    fy = 884
    cv.rect(24, fy, W - 48, 108, RED)
    cv.rect(26, fy + 2, W - 52, 104, PAPER)
    cv.text(34, fy + 8, "DATE CHECK \u2014 WHAT WE LEFT OUT, AND WHAT WAS "
            "STILL UNCONFIRMED", 1, RED, bold=True)
    cv.text(34, fy + 26, "THROWN OUT AS OLD NEWS", 1, NAVY, bold=True)
    for i, item in enumerate(THROWN_OUT):
        cv.text(34, fy + 38 + i * 10, "\u00d7  " + item, 1, INK)
    cv.text(560, fy + 26, "DATE NOTE \u2014 WHY ONE STORY COUNTS", 1, NAVY,
            bold=True)
    for i, ln in enumerate(DATE_NOTE):
        cv.text(560, fy + 38 + i * 10, ln, 1, INK)

    # bottom footer
    cv.text_c(W // 2, 997,
              "Every story here happened, or was first reported, on Tuesday "
              "24 November 2026 in at least one time zone.", 1, GRAY)
    return cv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out is None:
        out = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
                           if os.path.isdir(os.environ.get(
                               "MAKEFUN_OUTPUT_DIR", "/output")) else ".",
                           "entry.png")
    cv = build()
    data = png_bytes(cv)
    with open(out, "wb") as f:
        f.write(data)
    import hashlib
    print("wrote %s  %d bytes  sha256 %s" % (out, len(data),
          hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
