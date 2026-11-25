#!/usr/bin/env python3
"""Render the Tuesday 24 November 2026 front page (news-image-20261124 v3).

Every story here was reported on Tuesday 24 November 2026 (UTC). Three
earlier events (the Benghazi sinking, the Hormuz tankers, Huang's
reinstatement) are named only in the DATE CHECK box: they are not counted
among today's stories. Each story carries a source tag: C = reported by two
or more outlets, O = an official announcement, R = one outlet, CL = one
party's claim. PIL-only, DejaVu fonts, deterministic output.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (252, 250, 244)
INK = (18, 18, 18)
MID = (82, 82, 82)
RULE = (196, 188, 172)
NAVY = (27, 55, 96)
GOLD = (184, 138, 20)
RED = (172, 32, 24)
PANEL = (240, 236, 224)
CHECK_BG = (245, 235, 203)
CHECK_EDGE = (196, 172, 110)


def font(sz, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, sz)


def centre(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rrect(d, box, fill, outline=None, width=1, radius=6):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


LEADS = [
    ("LEAKED DATA · ROSSTAT", "LEAKED DATA PUTS RUSSIAN DEAD AT 700,000",
     "Leaked data puts the Russian war dead at 700,000. · C", "leak"),
    ("GAZA · TODAY", "GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
     "Israeli strike kills Hamas security chief, six others. · C", "gaza"),
    ("TECH · NVIDIA", "NVIDIA SHARES JUMP 31% ON HUANG RETURN",
     "Shares jump 31% as Jensen Huang retakes the top job. · C", "chip"),
]

STATS = [
    ("96", "NIGHT RAID DRONES"),
    ("700,000", "RUSSIAN DEAD"),
    ("31%", "NVIDIA JUMP"),
    ("26", "FACTORY FIRE DEAD"),
    ("5.6", "NEPAL QUAKE"),
    ("432,000", "2026 LOSSES"),
]

REGIONS = [
    ("EUROPE", [
        "EU unveils new sanctions on banks and shadow fleet · O",
        "Russia's 2026 casualties hit a record 432,000 · R",
        "COP31 climate talks end without a deal · C",
        "Allies warn of Russian nuclear-armed satellite · C",
        "Britain warns firms aiding Ukraine of sabotage · R",
        "Hungary's PM meets Zelenskyy in western Ukraine · C",
    ]),
    ("MIDDLE EAST", [
        "Gaza: Oxfam calls the territory 'toxic land' · R",
        "Iran sets seven conditions before any US talks · O",
        "Netanyahu urges Trump to resume strikes on Iran · R",
        "Trump warns Iran of a 'very traumatic' outcome · R",
        "Eleven die in coach-truck crash in Ras el-Khaimah · R",
    ]),
    ("SOUTH ASIA", [
        "Quake of 5.6 strikes Nepal near the China border · R",
        "Pakistani astronaut to join China's space station · C",
        "Nepal starts death process for 213 missing Indians · R",
    ]),
    ("EAST ASIA & PACIFIC", [
        "Solomon Islands to end its security pact with China · R",
        "UK sanctions Myanmar generals after genocide ruling · O",
        "Malaysia to send 6,500 Rohingya back to Myanmar · O",
        "South Korea scrambles jets as Russian planes near · C",
        "Taiwan welcomes Huang's return to Nvidia · R",
    ]),
    ("AFRICA", [
        "Borno school enrolment nearly doubles after conflict · R",
        "Two Nigerians die while serving in Russian military · R",
        "Tripoli denies any deal with Kyiv over Benghazi · R",
        "Erdogan plans first Libya trip in over a decade · R",
        "Analysts: Libya strike takes the war to Africa · CL",
    ]),
    ("NORTH AMERICA", [
        "Pennsylvania measles outbreak claims ninth death · R",
        "Trump: China plans to buy more Boeing planes · R",
        "Watchdog: ICE cut new-officer training too far · R",
    ]),
    ("LATIN AMERICA", [
        "Car bomb wrecks buildings in Villavicencio, Colombia · C",
        "Drone attack on Colombia police base injures civilians · R",
        "Mexico to try 'El Chapo Isidro' despite US request · C",
        "WHO chief visits Cuba as health care falters · O",
        "Brazil asks WTO panel over US duties · O",
    ]),
    ("TECH & MARKETS", [
        "Singapore vows action in Nvidia chip-diversion case · R",
        "WSJ: no proof Alice Huang was tasked to spy · R",
        "Huang apologises to staff on first day back · R",
        "SpaceX outages shake confidence across Europe · R",
        "Asian markets rally after Huang's return · C",
    ]),
]

# (number, label, longitude, latitude, label side: left/right/above)
PINS = [
    (1, "KYIV", 30.5, 50.4, "left"),
    (2, "GAZA", 34.5, 31.5, "right"),
    (3, "KATHMANDU", 85.3, 27.7, "below"),
    (4, "TAIPEI", 121.5, 25.0, "right"),
    (5, "TRIPOLI", 13.2, 32.9, "left"),
    (6, "WASHINGTON", -77.0, 38.9, "left"),
    (7, "BOGOTA", -74.0, 4.7, "right"),
    (8, "BEIJING", 116.4, 39.9, "above"),
]

# Continent silhouettes, rescaled for the 528..616 map strip.
CONTINENTS = [
    [(40, 531), (300, 528), (290, 559), (120, 550), (50, 555)],          # N America
    [(240, 571), (350, 570), (330, 613), (270, 611), (245, 588)],        # S America
    [(460, 531), (740, 530), (730, 567), (520, 575), (465, 555)],        # Europe
    [(470, 580), (560, 578), (545, 614), (500, 614), (475, 596)],        # Africa
    [(570, 561), (660, 558), (655, 578), (575, 579)],                    # Middle East
    [(690, 545), (940, 538), (930, 579), (760, 580), (700, 568)],        # Asia
    [(870, 596), (940, 592), (930, 608), (880, 608)],                    # Oceania
]


def draw_leak(d, x, y, w, h):
    # leaked papers plus a rising bar chart of the war dead
    d.rectangle([x, y, x + w, y + h], fill=(231, 235, 240))
    for dx, dy in ((14, 14), (34, 26), (54, 38)):
        d.rectangle([x + dx, y + dy, x + dx + 92, y + dy + 62],
                    fill=(255, 255, 255), outline=(150, 156, 164))
        for k in range(3):
            d.line([x + dx + 10, y + dy + 12 + k * 12, x + dx + 82, y + dy + 12 + k * 12],
                   fill=(168, 174, 182), width=2)
    base = y + h - 26
    for bx, bh, col in ((150, 34, NAVY), (182, 52, NAVY), (214, 74, NAVY), (246, 96, RED)):
        d.rectangle([x + bx, base - bh, x + bx + 22, base], fill=col)
    d.line([x + 140, base, x + 280, base], fill=INK, width=2)


def draw_gaza(d, x, y, w, h):
    # dusk sky, dark skyline, one smoke column, lit windows
    d.rectangle([x, y, x + w, y + h], fill=(232, 178, 138))
    d.ellipse([x + 232, y + 16, x + 268, y + 52], fill=(250, 226, 190))
    for cx, cy, r in ((120, 92, 14), (128, 66, 18), (120, 40, 13), (130, 18, 10)):
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r], fill=(120, 116, 112))
    for bx, bw, bh in ((0, 44, 62), (48, 36, 84), (88, 52, 58),
                       (144, 40, 92), (188, 48, 70), (240, 72, 96)):
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(52, 50, 48))
    for wx, wy in ((12, 108), (56, 84), (96, 110), (152, 76),
                   (200, 96), (252, 68), (268, 92)):
        d.rectangle([x + wx, y + wy, x + wx + 6, y + wy + 8], fill=(250, 214, 120))


def draw_chip(d, x, y, w, h):
    # dark circuit board with a rising green chart
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 40))
    for gx in range(x + 28, x + w, 44):
        d.line([gx, y + 12, gx, y + h - 12], fill=(44, 58, 84), width=1)
    for gy in range(y + 24, y + h, 36):
        d.line([x + 12, gy, x + w - 12, gy], fill=(44, 58, 84), width=1)
    d.rectangle([x + 52, y + 48, x + 122, y + 118], fill=(30, 44, 66),
                outline=(96, 116, 148), width=2)
    d.rectangle([x + 72, y + 68, x + 102, y + 98], fill=(60, 88, 128))
    for px in (62, 82, 102):
        d.line([x + px, y + 48, x + px, y + 34], fill=(96, 116, 148), width=2)
        d.line([x + px, y + 118, x + px, y + 132], fill=(96, 116, 148), width=2)
    pts = [(x + 150, y + 128), (x + 190, y + 104), (x + 224, y + 112),
           (x + 258, y + 66), (x + 292, y + 28)]
    d.line(pts, fill=(74, 222, 128), width=4, joint="curve")
    d.ellipse([x + 286, y + 22, x + 298, y + 34], fill=(74, 222, 128))
    d.text((x + 190, y + 14), "+31%", font=font(28, True), fill=(74, 222, 128))


def draw_ill(d, kind, x, y, w, h):
    {"leak": draw_leak, "gaza": draw_gaza, "chip": draw_chip}[kind](d, x, y, w, h)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # masthead
    centre(d, 512, 10, "THE DAILY FRONT PAGE", font(12, True), GOLD)
    centre(d, 512, 24, "THE WORLD IN ONE DAY", font(46, True), INK)
    centre(d, 512, 76, "TUESDAY 24 NOVEMBER 2026 · 40 STORIES · 8 REGIONS",
           font(20, True), MID)
    d.line([16, 96, 1008, 96], fill=INK, width=2)

    # DATE CHECK strip
    rrect(d, [16, 100, 1008, 130], fill=CHECK_BG, outline=CHECK_EDGE, width=1)
    d.text((26, 103), "DATE CHECK — All 40 stories were reported on Tuesday 24 November 2026 (UTC).",
           font=font(11, True), fill=INK)
    d.text((26, 117), "Left out as stories: Benghazi sinking (22 Nov) · Hormuz tankers (23 Nov) · Huang's reinstatement (22–23 Nov).",
           font=font(11), fill=INK)

    # stats strip
    d.line([16, 190, 1008, 190], fill=RULE, width=1)
    for i, (num, lab) in enumerate(STATS):
        cx = 16 + i * 165 + 82
        centre(d, cx, 138, num, font(28, True), NAVY)
        centre(d, cx, 170, lab, font(11, True), MID)
        if i:
            d.line([16 + i * 165, 140, 16 + i * 165, 184], fill=RULE, width=1)

    # three illustrated leads
    for i, (tag, head, summ, kind) in enumerate(LEADS):
        x = 16 + i * 324
        draw_ill(d, kind, x, 198, 312, 150)
        d.rectangle([x, 326, x + 150, 348], fill=(0, 0, 0))
        centre(d, x + 75, 331, tag, font(11, True), (255, 255, 255))
        hl = wrap(d, head, font(24, True), 296)
        assert len(hl) <= 3, (head, hl)
        for j, ln in enumerate(hl):
            d.text((x, 356 + j * 29), ln, font=font(24, True), fill=INK)
        sl = wrap(d, summ, font(15), 296)
        assert len(sl) <= 2, (summ, sl)
        for j, ln in enumerate(sl):
            d.text((x, 449 + j * 20), ln, font=font(15), fill=MID)

    # map strip, pins numbered 1-8, one per region
    d.line([16, 502, 1008, 502], fill=RULE, width=1)
    d.text((24, 508), "WHERE THE DAY HAPPENED", font=font(13, True), fill=INK)
    rt = "8 REGIONS · 40 STORIES"
    d.text((1000 - d.textlength(rt, font=font(12, True)), 509), rt,
           font=font(12, True), fill=MID)
    for gx in (150, 350, 550, 750, 950):
        d.line([gx, 528, gx, 616], fill=(228, 224, 212), width=1)
    for gy in (560, 590):
        d.line([24, gy, 1000, gy], fill=(228, 224, 212), width=1)
    for poly in CONTINENTS:
        d.polygon(poly, fill=(226, 232, 222), outline=(160, 156, 148))

    def proj(lon, lat):
        return 24 + (lon + 170) / 360 * 976, 528 + (75 - lat) / 130 * 88

    for num, label, lon, lat, side in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(255, 255, 255))
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=NAVY)
        txt = f"{num} {label}"
        if side == "left":
            d.text((px - 10 - d.textlength(txt, font=font(11, True)), py - 8),
                   txt, font=font(11, True), fill=INK)
        elif side == "right":
            d.text((px + 10, py - 8), txt, font=font(11, True), fill=INK)
        elif side == "below":
            centre(d, px, py + 12, txt, font(11, True), INK)
        else:
            centre(d, px, py - 22, txt, font(11, True), INK)

    # region blocks, 2 columns x 4 rows
    rows = [102, 94, 90, 90]
    tops = [630, 732, 826, 916]
    pairs = [(0, 1), (2, 3), (4, 5), (6, 7)]
    for ri, (a, b) in enumerate(pairs):
        for ci, idx in enumerate((a, b)):
            name, items = REGIONS[idx]
            x = 16 + ci * 508
            by = tops[ri]
            assert 22 + len(items) * 13 <= rows[ri], (name, len(items), rows[ri])
            d.text((x, by + 2), name, font=font(14, True), fill=NAVY)
            d.line([x, by + 20, x + 484, by + 20], fill=RULE, width=1)
            for j, item in enumerate(items):
                assert d.textlength(item, font=font(11)) <= 464, item
                d.text((x, by + 24 + j * 13), item, font=font(11), fill=INK)

    # footer
    d.line([16, 1006, 1008, 1006], fill=RULE, width=1)
    centre(d, 512, 1010, "40 stories · 8 regions — every event above was reported on Tuesday 24 November 2026.",
           font(12), MID)
    return img


if __name__ == "__main__":
    im = build()
    im.save("entry.png")
    with open("entry.png", "rb") as f:
        raw = f.read()
    assert len(raw) <= 1024 * 1024, len(raw)
    assert im.size == (1024, 1024)
    print(len(raw), hashlib.sha256(raw).hexdigest())
