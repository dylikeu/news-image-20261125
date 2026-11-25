#!/usr/bin/env python3
"""Render the news-image-20261125 front page: one day of world news,
Wednesday 25 November 2026, as a 1024x1024 PNG.

Every scene is drawn on its own layer exactly the size of its box and
then pasted, so no drawn pixel can spill outside its box. Every text
block is wrapped to a fixed font size and truncated with an ellipsis
as a safety net, so no text can overflow its box.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.png")

PAPER = (247, 243, 234, 255)
INK = (26, 26, 26, 255)
MUTED = (90, 86, 78, 255)
RULE = (180, 172, 158, 255)
RED = (176, 42, 32, 255)
NAVY = (31, 58, 95, 255)
GREEN = (46, 125, 50, 255)
AMBER = (176, 124, 0, 255)
CARD = (255, 255, 255, 255)
CARD_EDGE = (205, 198, 186, 255)
SKY = (210, 226, 238, 255)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)
F_REG = lambda s: font("DejaVuSans.ttf", s)
F_SERIF_REG = lambda s: font("DejaVuSerif.ttf", s)


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, f, max_w, max_lines):
    """Wrap to max_lines, truncating the last line with an ellipsis."""
    lines = wrap(d, text, f, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and d.textlength(last + " …", font=f) > max_w:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    out[-1] = (last + " …") if last else "…"
    return out


def trunc(d, text, f, max_w):
    """Single line truncated with an ellipsis to fit max_w."""
    if d.textlength(text, font=f) <= max_w:
        return text
    t = text
    while t and d.textlength(t + " …", font=f) > max_w:
        t = t.rsplit(" ", 1)[0] if " " in t else t[:-1]
    return (t + " …") if t else "…"


def tag_width(label):
    """Width of a proof-tag pill, without drawing it."""
    return int(F_BOLD(8).getlength(label)) + 12


def tag_pill(d, x, y, label, kind):
    """Proof tag pill; returns its width. kind: CONFIRMED / REPORTED."""
    f = F_BOLD(8)
    tw = d.textlength(label, font=f)
    w = int(tw) + 12
    h = 13
    col = GREEN if kind == "CONFIRMED" else AMBER
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=col)
    d.text((x + 6, y + 2), label, font=f, fill=(255, 255, 255, 255))
    return w


def make_layer(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

# ---------------------------------------------------------------- scenes
def scene_hormuz(w, h):
    """Hero 1: a tanker on a dark sea, fire bursting from its deck,
    a naval mine below the waterline."""
    img, d = make_layer(w, h)
    d.rectangle([0, 0, w, h], fill=(16, 34, 58, 255))
    # warm glow behind the fire, kept above the deck
    d.ellipse([w // 2 - 56, 0, w // 2 + 24, 48], fill=(120, 62, 28, 255))
    # sea
    d.rectangle([0, 62, w, h], fill=(24, 68, 104, 255))
    for wx in range(8, w - 8, 26):
        d.line([(wx, 74), (wx + 14, 74)], fill=(90, 150, 190, 255), width=2)
        d.line([(wx + 6, 88), (wx + 20, 88)], fill=(70, 130, 170, 255), width=2)
    # tanker hull
    hx0, hy0, hx1, hy1 = 30, 52, w - 30, 74
    d.polygon([(hx0, hy0), (hx1, hy0), (hx1 - 14, hy1), (hx0 + 10, hy1)],
              fill=(40, 40, 46, 255))
    d.rectangle([hx0, hy0, hx1, hy0 + 4], fill=(120, 30, 24, 255))
    # containers on deck
    for i, col in enumerate(((200, 90, 40), (40, 110, 160), (180, 170, 60))):
        cx0 = 52 + i * 62
        d.rectangle([cx0, hy0 - 16, cx0 + 54, hy0 - 2], fill=col + (255,))
    # bridge tower, right end
    d.rectangle([hx1 - 52, hy0 - 30, hx1 - 22, hy0 - 2], fill=(220, 225, 230, 255))
    d.rectangle([hx1 - 48, hy0 - 26, hx1 - 26, hy0 - 18], fill=(30, 60, 100, 255))
    # fire burst above the mid-deck, clear of the bridge:
    # overlapping flame circles, no spokes, so it reads as fire
    bx, by = w // 2 - 20, 28
    for (fx, fy, r, col) in ((0, 0, 20, (255, 140, 30, 255)),
                             (-7, 4, 14, (255, 190, 60, 255)),
                             (7, -3, 12, (255, 240, 150, 255))):
        d.ellipse([bx + fx - r, by + fy - r, bx + fx + r, by + fy + r], fill=col)
    # flame tongues rising from the burst, ending below the top edge
    d.polygon([(bx - 9, by - 12), (bx - 2, by - 28), (bx + 5, by - 12)],
              fill=(255, 170, 50, 255))
    d.polygon([(bx + 2, by - 14), (bx + 8, by - 26), (bx + 13, by - 14)],
              fill=(255, 220, 100, 255))
    # naval mine under the water, left foreground
    mx, my = 52, 88
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(20, 20, 24, 255))
    for ang in range(0, 360, 45):
        x2 = mx + int(11 * math.cos(math.radians(ang)))
        y2 = my + int(11 * math.sin(math.radians(ang)))
        d.line([(mx, my), (x2, y2)], fill=(20, 20, 24, 255), width=2)
    return img


def scene_tariffs(w, h):
    """Hero 2: a globe, a big red percent sign, and a falling arrow
    over a tariff document."""
    img, d = make_layer(w, h)
    d.rectangle([0, 0, w, h], fill=(24, 32, 64, 255))
    # document sheet, left
    dx0, dy0, dx1, dy1 = 24, 14, 150, h - 12
    d.rectangle([dx0, dy0, dx1, dy1], fill=(245, 242, 232, 255))
    d.rectangle([dx0, dy0, dx1, dy0 + 16], fill=(176, 42, 32, 255))
    d.text((dx0 + 8, dy0 + 3), "TARIFFS", font=F_BOLD(10),
           fill=(255, 255, 255, 255))
    d.text((dx0 + 10, 32), "16 partners", font=F_BOLD(9), fill=(26, 26, 26, 255))
    for i, ly in enumerate((46, 57, 68, 79)):
        d.line([(dx0 + 10, ly), (dx1 - 10 - (i % 2) * 22, ly)],
               fill=(120, 115, 105, 255), width=2)
    # globe, right of the sheet
    gx, gy, gr = 208, 48, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr],
              fill=(40, 90, 140, 255), outline=(150, 200, 240, 255), width=2)
    d.ellipse([gx - 12, gy - gr, gx + 12, gy + gr], outline=(150, 200, 240, 255), width=1)
    d.line([(gx - gr, gy), (gx + gr, gy)], fill=(150, 200, 240, 255), width=1)
    d.arc([gx - gr, gy - 18, gx + gr, gy + 18], start=200, end=340,
          fill=(150, 200, 240, 255), width=1)
    d.arc([gx - gr, gy - 18, gx + gr, gy + 18], start=20, end=160,
          fill=(150, 200, 240, 255), width=1)
    # big percent sign, right side, ending above the bottom edge
    d.text((252, 22), "%", font=F_BOLD(44), fill=(255, 90, 60, 255))
    # falling arrow under the globe
    d.line([(gx, gy + gr + 4), (gx, h - 16)], fill=(255, 90, 60, 255), width=4)
    d.polygon([(gx - 8, h - 24), (gx + 8, h - 24), (gx, h - 10)],
              fill=(255, 90, 60, 255))
    return img


def scene_russia(w, h):
    """Hero 3: rising bars of the death toll, with the total figure
    above them."""
    img, d = make_layer(w, h)
    d.rectangle([0, 0, w, h], fill=(32, 30, 36, 255))
    d.text((16, 8), "490,334", font=F_BOLD(30), fill=(255, 255, 255, 255))
    d.text((16, 42), "Russian soldiers dead, 2022–2026",
           font=F_REG(11), fill=(200, 200, 200, 255))
    d.text((w - 104, 12), "leaked figures", font=F_REG(9),
           fill=(160, 160, 160, 255))
    # bars, ascending left to right, tops below the subtitle line
    base = h - 10
    vals = [12, 18, 24, 30, 36]
    bw = 34
    for i, v in enumerate(vals):
        x0 = 30 + i * 54
        col = (120, 120, 130, 255) if i < 4 else (176, 42, 32, 255)
        d.rectangle([x0, base - v, x0 + bw, base], fill=col)
    d.line([(16, base), (w - 16, base)], fill=(200, 200, 200, 255), width=2)
    return img


def mini_scene(kind, w, h):
    """Small drawn scene for a medium card: coloured band + one icon."""
    img, d = make_layer(w, h)
    bands = {
        "refinery": (60, 40, 30), "gaza": (24, 28, 52), "drone": (30, 60, 90),
        "court": (70, 60, 50), "cpi": (120, 30, 30), "space": (16, 24, 54),
        "treaty": (30, 80, 50), "rescue": (30, 70, 110), "blast": (110, 50, 20),
        "sudan": (130, 90, 30), "plane": (40, 80, 130), "dell": (20, 50, 80),
    }
    d.rectangle([0, 0, w, h], fill=bands[kind] + (255,))
    cx, cy = w // 2, h // 2
    if kind == "refinery":
        d.rectangle([cx - 34, cy - 4, cx + 10, cy + 10], fill=(200, 200, 200, 255))
        d.rectangle([cx + 14, cy - 12, cx + 20, cy + 10], fill=(220, 220, 220, 255))
        d.polygon([(cx + 26, cy - 4), (cx + 30, cy - 12), (cx + 34, cy - 4)],
                  fill=(255, 170, 40, 255))
        d.ellipse([cx + 24, cy - 8, cx + 36, cy + 2], fill=(255, 200, 80, 255))
    elif kind == "gaza":
        for bx0, bw, bh in ((cx - 40, 22, 12), (cx - 16, 26, 16), (cx + 12, 24, 10)):
            d.rectangle([bx0, cy + 12 - bh, bx0 + bw, cy + 12], fill=(12, 14, 30, 255))
        d.ellipse([cx + 22, cy - 12, cx + 30, cy - 4], fill=(255, 190, 60, 255))
        d.ellipse([cx + 24, cy - 10, cx + 28, cy - 6], fill=(255, 240, 160, 255))
    elif kind == "drone":
        d.rectangle([cx - 10, cy - 4, cx + 10, cy + 4], fill=(220, 225, 235, 255))
        for sx in (-22, 22):
            d.ellipse([cx + sx - 4, cy - 8, cx + sx + 4, cy], fill=(180, 190, 205, 255))
            d.line([(cx + sx, cy - 4), (cx - 10 if sx < 0 else cx + 10, cy - 2)],
                   fill=(180, 190, 205, 255), width=2)
        d.ellipse([cx - 3, cy + 4, cx + 3, cy + 10], fill=(255, 80, 60, 255))
    elif kind == "court":
        d.rectangle([cx - 30, cy - 12, cx + 30, cy - 8], fill=(240, 235, 220, 255))
        d.rectangle([cx - 30, cy + 8, cx + 30, cy + 12], fill=(240, 235, 220, 255))
        for px in (-24, -3, 18):
            d.rectangle([cx + px, cy - 8, cx + px + 6, cy + 8],
                        fill=(240, 235, 220, 255))
    elif kind == "cpi":
        pts = [(cx - 34, cy + 8), (cx - 14, cy + 2), (cx + 4, cy + 6),
               (cx + 22, cy - 8), (cx + 34, cy - 12)]
        d.line(pts, fill=(255, 220, 90, 255), width=4)
        d.polygon([(cx + 34, cy - 12), (cx + 26, cy - 12), (cx + 34, cy - 4)],
                  fill=(255, 220, 90, 255))
        d.text((cx - 34, cy - 12), "%", font=F_BOLD(11), fill=(255, 255, 255, 255))
    elif kind == "space":
        for sx, sy in ((cx - 40, cy - 8), (cx - 24, cy + 6), (cx + 34, cy - 10),
                       (cx + 44, cy + 4), (cx + 8, cy - 12)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220, 255))
        d.polygon([(cx - 6, cy - 12), (cx + 6, cy - 12), (cx + 4, cy + 2),
                   (cx - 4, cy + 2)], fill=(240, 240, 240, 255))
        d.polygon([(cx - 6, cy - 12), (cx, cy - 18), (cx + 6, cy - 12)],
                  fill=(255, 80, 60, 255))
        d.polygon([(cx - 4, cy + 2), (cx, cy + 10), (cx + 4, cy + 2)],
                  fill=(255, 170, 40, 255))
    elif kind == "treaty":
        for fx, col in ((-26, (40, 90, 180)), (10, (250, 200, 40))):
            d.line([(cx + fx, cy - 12), (cx + fx, cy + 12)],
                   fill=(240, 240, 240, 255), width=2)
            d.rectangle([cx + fx, cy - 12, cx + fx + 16, cy - 2],
                        fill=col + (255,))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255, 255))
    elif kind == "rescue":
        d.rectangle([cx - 22, cy - 11, cx + 22, cy + 11], fill=(240, 235, 220, 255))
        d.rectangle([cx - 22, cy - 11, cx, cy + 11], fill=(200, 190, 170, 255))
        d.line([(cx, cy - 11), (cx, cy + 11)], fill=(120, 100, 80, 255), width=2)
        d.ellipse([cx - 4, cy - 2, cx, cy + 2], fill=(176, 42, 32, 255))
        d.polygon([(cx + 14, cy - 6), (cx + 18, cy - 2), (cx + 14, cy + 2),
                   (cx + 10, cy - 2)], fill=(176, 42, 32, 255))
    elif kind == "blast":
        for r, col in ((12, (255, 140, 30, 255)), (8, (255, 190, 60, 255)),
                       (4, (255, 240, 150, 255))):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        for ang in range(0, 360, 60):
            x2 = cx + int(18 * math.cos(math.radians(ang)))
            y2 = cy + int(18 * math.sin(math.radians(ang)))
            if y2 > cy + 12:
                y2 = cy + 12
            d.line([(cx, cy), (x2, y2)], fill=(255, 170, 50, 255), width=2)
    elif kind == "sudan":
        d.ellipse([cx + 28, cy - 12, cx + 38, cy - 2], fill=(255, 220, 120, 255))
        d.polygon([(0, cy + 6), (w, cy + 6), (w, h), (0, h)], fill=(180, 140, 80, 255))
        d.rectangle([cx - 34, cy - 6, cx - 14, cy], fill=(60, 60, 66, 255))
        d.line([(cx - 24, cy - 6), (cx - 24, cy - 12)], fill=(220, 220, 220, 255), width=2)
    elif kind == "plane":
        d.polygon([(cx - 34, cy), (cx + 30, cy - 4), (cx + 36, cy),
                   (cx + 30, cy + 4)], fill=(240, 240, 240, 255))
        d.polygon([(cx - 6, cy - 2), (cx + 6, cy - 12), (cx + 10, cy - 2)],
                  fill=(220, 220, 220, 255))
        d.polygon([(cx - 6, cy + 2), (cx + 4, cy + 10), (cx + 8, cy + 2)],
                  fill=(220, 220, 220, 255))
        d.rectangle([cx + 24, cy - 1, cx + 30, cy + 1], fill=(255, 80, 60, 255))
    elif kind == "dell":
        d.rectangle([cx - 30, cy - 11, cx + 30, cy + 11], fill=(40, 40, 46, 255))
        for ry in (-7, 0, 7):
            d.rectangle([cx - 24, cy + ry, cx + 20, cy + ry + 4],
                        fill=(90, 120, 160, 255))
            d.ellipse([cx + 24, cy + ry + 1, cx + 27, cy + ry + 4],
                      fill=(120, 220, 130, 255))
    return img

# ---------------------------------------------------------------- data
HEROES = [
    dict(kicker="MIDDLE EAST · HORMUZ", scene=scene_hormuz, tag="REPORTED",
         head="Two tankers hit mines and burn in Strait of Hormuz",
         deck="Iran's Guards say the tankers hit mines on an "
             "unauthorised route and caught fire.",
         src="Reuters"),
    dict(kicker="TRADE · TARIFFS", scene=scene_tariffs, tag="CONFIRMED",
         head="US unveils new tariffs on China, EU and others",
         deck="Washington's new tariff plan lands as world stocks slide "
             "and Asia's chip markets plunge.",
         src="BBC"),
    dict(kicker="WAR · UKRAINE", scene=scene_russia, tag="REPORTED",
         head="Russia's own figures show nearly 500,000 war dead",
         deck="Leaked Russian statistics analysed by the BBC put the "
             "death toll near half a million since 2022.",
         src="BBC"),
]

MEDIUMS = [
    dict(kicker="MIDDLE EAST · SAUDI", kind="refinery", tag="REPORTED",
         head="Houthis claim Ras Tanura refinery hit",
         deck="Houthis claim they hit the kingdom's biggest refinery; "
             "the coalition says it downed four drones.",
         src="Reuters"),
    dict(kicker="WAR · GAZA", kind="gaza", tag="REPORTED",
         head="Israeli strike kills Hamas security chief",
         deck="Colonel Mohammad Abuelouf, his wife and two children were "
             "killed in Gaza City, medics said.",
         src="Reuters"),
    dict(kicker="WAR · UKRAINE", kind="drone", tag="REPORTED",
         head="Ukraine drones hit two Russian refineries",
         deck="Strikes set two Rosneft plants ablaze; Kyiv says five "
             "jets were hit at the Savasleyka airfield.",
         src="BBC"),
    dict(kicker="TECH · LAW", kind="court", tag="REPORTED",
         head="Huawei convicted of stealing US trade secrets",
         deck="A New York jury found it guilty of trade-secret theft and "
             "bank fraud — but not racketeering.",
         src="BBC"),
    dict(kicker="ECONOMY · AUSTRALIA", kind="cpi", tag="CONFIRMED",
         head="Australia inflation jumps to 4.9%",
         deck="Fuel and clothing drove October prices up more than "
             "expected; the central bank is tipped to hold.",
         src="Reuters"),
    dict(kicker="SPACE · CHINA", kind="space", tag="CONFIRMED",
         head="Shenzhou-24 docks; first Pakistani in orbit",
         deck="Zeeshan Ali, the first Pakistani in orbit, boarded "
             "China's Tiangong station 3.5 hours after launch.",
         src="Reuters"),
    dict(kicker="DIPLOMACY · PACIFIC", kind="treaty", tag="CONFIRMED",
         head="Australia, Solomons sign security treaty",
         deck="The treaty, signed in Canberra, bars foreign military "
             "bases on the Solomon Islands.",
         src="BBC"),
    dict(kicker="LATIN AMERICA · COLOMBIA", kind="rescue", tag="CONFIRMED",
         head="Police free 20 hostages in Cartagena siege",
         deck="Police stormed a supermarket after 17 hours; all 20 "
             "hostages were freed, one captor killed.",
         src="BBC"),
    dict(kicker="US · IOWA", kind="blast", tag="CONFIRMED",
         head="Army detonates 5 tons of explosives in Iowa",
         deck="Five tons of unstable lead azide were blown up at 9 a.m.; "
             "nearby residents were told to stay indoors.",
         src="NPR"),
    dict(kicker="AFRICA · SUDAN", kind="sudan", tag="REPORTED",
         head="RSF drone strikes kill 19 civilians in Sudan",
         deck="A Sudanese rights group says paramilitary drones hit two "
             "cities, killing 19 and wounding 20.",
         src="Just Security"),
    dict(kicker="US · IMMIGRATION", kind="plane", tag="CONFIRMED",
         head="Ábrego García arrives in Spain",
         deck="The Salvadoran at the heart of Trump's deportation fight "
             "left the US after 20 months.",
         src="BBC"),
    dict(kicker="TECH · BUSINESS", kind="dell", tag="REPORTED",
         head="Dell posts record quarter on AI servers",
         deck="Revenue hit $54.9bn, up 103%; AI server sales of $22bn "
             "rose 291% on the year.",
         src="Reuters"),
]

ALSO_ON = [
    "US inflation rose 0.3% in Oct; Fed hike odds rise — Reuters",
    "Zelensky: Ukraine needs €115bn foreign aid for 2027 — Principia",
    "US defence chief pauses Patriot supplies to Ukraine — Principia",
    "Two Libyan officers die in Ukraine drone attack in Benghazi — Principia",
    "Eurozone inflation rises to 4.0% — Eurostat",
    "Pope Leo XIV laments COP31 failure — AP",
    "Senegal restored as AFCON champions by CAS — Principia",
    "Roche breast cancer drug wins 2nd FDA approval — Principia",
    "EasyJet profit falls 89% as fuel costs soar — Principia",
    "Amazon buys Decart to rival Nvidia chips — Principia",
    "Amazon: hackers' AI agents broke into university server — Principia",
    "Anthropic shares fall below IPO price — Principia",
    "Bogor mine flood: 6 dead, ~20 trapped — AP",
    "Plane crash off Mississippi coast kills 6, incl. 2 children — BBC",
    "Ramaphosa wins court battle over impeachment — BBC",
    "Pete Edochie dies aged 79 — BBC",
    "Zimbabwe warrant for Mugabe's son — BBC",
    "Sarkozy and Carla Bruni to face trial — BBC",
    "Raheem Sterling given suspended sentence — BBC",
    "Fury v Joshua fight to go ahead — BBC",
    "UK energy bills to rise 26% from January — BBC",
    "UK sent sex offender refugee to Eswatini — BBC",
    "UN warns funding cuts threaten HIV progress — Principia",
    "North Koreans 'spied on, beaten, jailed for being Christian' — BBC",
    "Spain election: clashing visions — BBC",
    "India food prices rising — BBC",
    "EA adds AI John Motson to FC 27 — BBC",
]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off from Jiuquan"),
    ("00:30", "Australia CPI 4.9% lands"),
    ("03:56", "Shenzhou-24 docks with Tiangong"),
    ("12:21", "BBC: Russia's own figures show 490,000 war dead"),
    ("15:00", "Army detonates 5 tons of explosives in Iowa"),
    ("21:19", "US unveils new tariff plan"),
]

# lon/lat polygons, drawn by hand (simplified world outline)
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 70), (-60, 60), (-55, 52), (-60, 46), (-68, 44),
     (-70, 40), (-75, 35), (-80, 26), (-81, 31), (-84, 30), (-90, 21),
     (-94, 17), (-97, 16), (-105, 20), (-110, 23), (-115, 29), (-120, 34),
     (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-152, 58), (-162, 55),
     (-168, 66)],
    # Greenland
    [(-58, 64), (-48, 60), (-40, 60), (-32, 68), (-40, 76), (-55, 76),
     (-60, 73), (-58, 64)],
    # South America
    [(-80, 9), (-77, 8), (-72, 11), (-64, 10), (-60, 8), (-52, 4),
     (-50, 0), (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -27),
     (-52, -33), (-58, -35), (-62, -39), (-65, -41), (-68, -47),
     (-69, -52), (-73, -53), (-73, -45), (-73, -37), (-71, -30),
     (-70, -20), (-75, -15), (-80, -6), (-81, 0), (-80, 9)],
    # Africa
    [(-17, 15), (-16, 20), (-10, 30), (-5, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (38, 22),
     (43, 12), (48, 11), (51, 11), (46, 5), (41, -2), (40, -10),
     (36, -18), (32, -26), (28, -33), (20, -35), (16, -28), (12, -18),
     (13, -12), (9, -1), (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 15)],
    # Eurasia — clockwise from Gibraltar, up the Atlantic coast,
    # round Scandinavia and the Arctic, down the Pacific coast,
    # round India and Arabia, back along the Mediterranean
    [(-9, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 47), (-4, 48),
     (0, 50), (2, 51), (4, 52), (7, 54), (8, 57), (10, 57), (10, 55),
     (12, 56), (14, 57), (18, 59), (21, 60), (24, 60), (22, 63),
     (21, 66), (25, 71), (30, 70), (33, 68), (35, 66), (40, 65),
     (44, 68), (50, 69), (55, 68), (60, 69), (68, 70), (75, 72),
     (80, 73), (85, 74), (90, 75), (95, 76), (100, 77), (105, 77),
     (110, 74), (115, 73), (120, 73), (125, 72), (130, 72), (135, 71),
     (140, 72), (145, 71), (150, 70), (155, 70), (160, 70), (165, 69),
     (170, 67), (178, 66), (178, 65), (170, 60), (162, 56), (156, 52),
     (150, 59), (142, 54), (141, 45), (135, 43),
     (130, 42), (127, 40), (126, 38), (122, 31), (120, 28), (115, 23),
     (110, 20), (108, 18), (105, 10), (103, 8), (100, 7), (98, 10),
     (95, 16), (92, 21), (89, 22), (86, 20), (83, 18), (80, 13),
     (77, 8), (74, 13), (72, 20), (68, 23), (66, 25), (61, 25),
     (57, 26), (56, 27), (54, 28), (52, 29), (50, 30), (48, 30),
     (47, 29), (49, 28), (50, 27), (51, 26), (51, 25), (52, 24),
     (54, 24), (56, 24), (58, 23), (59, 22), (58, 20), (56, 17),
     (54, 15), (51, 14), (48, 14), (45, 13), (43, 12),
     (40, 15), (38, 21), (36, 28), (34, 29), (32, 31),
     (27, 36), (23, 36), (20, 39), (15, 44), (8, 44), (3, 43),
     (0, 38), (-2, 37), (-6, 36), (-9, 36)],
    # Australia
    [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -30), (153, -27), (150, -23),
     (146, -19), (142, -11), (139, -15), (136, -12), (132, -11),
     (128, -14), (124, -15), (120, -20), (114, -22)],
    # United Kingdom (drawn slightly enlarged so the island reads)
    [(-8, 50), (-4, 49), (-1, 51), (0, 53), (-1, 56), (-2, 59),
     (-5, 59), (-7, 57), (-7, 53), (-8, 50)],
    # Japan (drawn enlarged so the island chain reads at this scale —
    # Tokyo must sit on land, not on sea)
    [(130, 28), (131, 31), (133, 33), (135, 34), (137, 35), (139, 36),
     (140, 38), (141, 40), (141, 46), (147, 46), (146, 42), (145, 38),
     (144, 34), (142, 30), (138, 28), (132, 28), (130, 28)],
    # Korea peninsula (drawn slightly enlarged so Seoul sits on land)
    [(125.5, 34.5), (126, 37), (126.5, 39.5), (128, 40), (129.5, 39),
     (129.5, 37), (129, 35), (127.5, 34.5), (125.5, 34.5)],
    # Caribbean islands (drawn slightly enlarged so they read at this
    # scale — so no dot floats on sea)
    [(-87, 24), (-82, 24), (-77, 21), (-73, 20), (-77, 19), (-82, 22),
     (-87, 24)],  # Cuba
    [(-75, 20), (-72, 20), (-69, 19), (-67, 18), (-71, 17), (-75, 19)],  # Hispaniola
    [(-79, 19), (-76, 18), (-77, 17), (-79, 18)],  # Jamaica
    [(-68, 19), (-65, 19), (-66, 17), (-68, 18)],  # Puerto Rico
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -20), (44, -16)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -8), (136, -6), (131, -3), (131, -1)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -3),
     (110, -2), (109, 1)],
    # Sumatra
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (103, -5),
     (100, -1), (97, 3), (95, 5)],
    # Java
    [(105, -6), (110, -7), (114, -8), (114, -9), (108, -8), (105, -7), (105, -6)],
]

# (number, label, lon, lat) — every dot sits on a drawn polygon.
MAP_DOTS = [
    (1, "Hormuz", 57.0, 27.0),
    (2, "Ras Tanura", 50.0, 26.6),
    (3, "Gaza", 34.5, 31.5),
    (4, "Moscow", 37.6, 55.8),
    (5, "Washington", -77.0, 38.9),
    (6, "Beijing", 116.4, 39.9),
    (7, "Canberra", 149.1, -35.3),
    (8, "Cartagena", -73.5, 9.0),
    (9, "Iowa", -91.3, 40.8),
    (10, "Sudan", 32.5, 15.6),
    (11, "Madrid", -3.7, 40.4),
    (12, "Bogor", 106.8, -6.6),
]

# ---------------------------------------------------------------- layout
def draw_masthead(img, d):
    d.rectangle([0, 0, W, 78], fill=(26, 26, 26, 255))
    d.text((14, 8), "THE WORLD IN ONE DAY", font=F_SERIF(34),
           fill=(247, 243, 234, 255))
    d.text((14, 50), "WEDNESDAY, 25 NOVEMBER 2026",
           font=F_BOLD(15), fill=(255, 210, 90, 255))
    right = "42 STORIES  ·  7 REGIONS  ·  13 FIELDS"
    rw = d.textlength(right, font=F_BOLD(13))
    d.text((W - 14 - rw, 52), right, font=F_BOLD(13),
           fill=(247, 243, 234, 255))
    d.text((W - 14 - rw, 14), "ONE DAY · ONE PAGE",
           font=F_BOLD(11), fill=(180, 175, 165, 255))


def draw_timeline(img, d):
    y0, y1 = 82, 120
    d.rectangle([12, y0, W - 12, y1], fill=(31, 58, 95, 255))
    d.text((22, y0 + 3), "THE DAY IN TIME — UTC", font=F_BOLD(10),
           fill=(255, 210, 90, 255))
    # two rows x three columns; time bold, text on the same line
    xs = [22, 352, 682]
    for i, (t, txt) in enumerate(TIMELINE):
        col = i % 3
        row = i // 3
        x = xs[col]
        yy = y0 + 15 + row * 12
        d.text((x, yy), t, font=F_BOLD(9), fill=(255, 210, 90, 255))
        tw = d.textlength(t, font=F_BOLD(9))
        d.text((x + tw + 6, yy),
               trunc(d, txt, F_REG(9), 322 - tw - 6),
               font=F_REG(9), fill=(235, 240, 245, 255))
    d.line([(12, y1), (W - 12, y1)], fill=RULE, width=1)


def hero_card(img, d, x, y, w, h, hero):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_EDGE, width=1)
    pad = 8
    # top row: kicker left, proof tag right
    d.text((x + pad, y + 5), hero["kicker"], font=F_BOLD(9), fill=RED)
    tag_pill(d, x + w - pad - tag_width(hero["tag"]), y + 4,
             hero["tag"], hero["tag"])
    # scene
    sy = y + 22
    sh = 100
    img.paste(hero["scene"](w - 2 * pad, sh), (x + pad, sy))
    # headline, 2 lines fixed size
    hy = sy + sh + 6
    for i, ln in enumerate(fit_lines(d, hero["head"], F_BOLD(15), w - 2 * pad, 2)):
        d.text((x + pad, hy + i * 18), ln, font=F_BOLD(15), fill=INK)
    # deck, 2 lines fixed size
    dy = hy + 38
    for i, ln in enumerate(fit_lines(d, hero["deck"], F_REG(12), w - 2 * pad, 2)):
        d.text((x + pad, dy + i * 15), ln, font=F_REG(12), fill=(50, 48, 44, 255))
    # source
    d.text((x + pad, y + h - 14), "Source: " + hero["src"],
           font=F_REG(9), fill=MUTED)


def medium_card(img, d, x, y, w, h, m):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_EDGE, width=1)
    pad = 6
    # top row: kicker left, proof tag right
    d.text((x + pad, y + 4), trunc(d, m["kicker"], F_BOLD(8), w - 2 * pad - 66),
           font=F_BOLD(8), fill=NAVY)
    tag_pill(d, x + w - pad - tag_width(m["tag"]), y + 3, m["tag"], m["tag"])
    # scene band
    sy = y + 17
    sh = 28
    img.paste(mini_scene(m["kind"], w - 2 * pad, sh), (x + pad, sy))
    # headline, 2 lines fixed size
    hy = sy + sh + 4
    for i, ln in enumerate(fit_lines(d, m["head"], F_BOLD(11), w - 2 * pad, 2)):
        d.text((x + pad, hy + i * 12), ln, font=F_BOLD(11), fill=INK)
    # deck, 2 lines fixed size
    dy = hy + 25
    for i, ln in enumerate(fit_lines(d, m["deck"], F_REG(9), w - 2 * pad, 2)):
        d.text((x + pad, dy + i * 10), ln, font=F_REG(9), fill=(50, 48, 44, 255))
    # source
    d.text((x + pad, y + h - 10), "Source: " + m["src"],
           font=F_REG(8), fill=MUTED)


def draw_map(img, d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 240, 246, 255),
                outline=CARD_EDGE, width=1)
    d.text((x + 8, y + 4), "WHERE IT HAPPENED — 12 STORIES ON THE MAP",
           font=F_BOLD(10), fill=NAVY)
    # map area stops short of the legend strip on the right
    mx0, my0, mx1, my1 = x + 8, y + 20, x + w - 198, y + h - 4

    def proj(lon, lat):
        px = mx0 + (lon + 170) / 360.0 * (mx1 - mx0)
        py = my0 + (78 - lat) / 156.0 * (my1 - my0)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(168, 196, 168, 255), outline=(110, 140, 110, 255))
    for num, label, lon, lat in MAP_DOTS:
        px, py = proj(lon, lat)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                  outline=(255, 255, 255, 255), width=2)
        tw = d.textlength(str(num), font=F_BOLD(7))
        d.text((px - tw / 2, py - 5), str(num), font=F_BOLD(7),
               fill=(255, 255, 255, 255))
    # legend, right side of the map box
    lx = x + w - 178
    d.text((lx, y + 20), "ON THE MAP", font=F_BOLD(9), fill=NAVY)
    for i, (num, label, lon, lat) in enumerate(MAP_DOTS):
        col = i % 2
        row = i // 2
        lx2 = lx + col * 88
        ly2 = y + 34 + row * 14
        d.ellipse([lx2, ly2, lx2 + 11, ly2 + 11], fill=RED)
        tw = d.textlength(str(num), font=F_BOLD(7))
        d.text((lx2 + 5.5 - tw / 2, ly2 + 1), str(num), font=F_BOLD(7),
               fill=(255, 255, 255, 255))
        d.text((lx2 + 14, ly2 + 1), trunc(d, label, F_REG(8), 72),
               font=F_REG(8), fill=INK)


def draw_also_on(img, d, x, y, w, h):
    d.text((x, y), "ALSO ON WEDNESDAY 25 NOVEMBER — 27 MORE STORIES",
           font=F_BOLD(11), fill=NAVY)
    col_w = (w - 14) // 2
    f = F_REG(9)
    lh = 8.0
    for i, item in enumerate(ALSO_ON):
        col = i // 14
        row = i % 14
        ix = x + col * (col_w + 14)
        iy = y + 14 + row * lh
        num = f"{i + 16}. "
        nw = d.textlength(num, font=F_BOLD(9))
        d.text((ix, iy), num, font=F_BOLD(9), fill=RED)
        d.text((ix + nw, iy), trunc(d, item, f, col_w - nw),
               font=f, fill=INK)


def draw_bottom(img, d, y, h):
    # DATE CHECK, left half
    x0, w0 = 12, 496
    d.rectangle([x0, y, x0 + w0, y + h], fill=(255, 250, 230, 255),
                outline=CARD_EDGE, width=1)
    d.text((x0 + 8, y + 4), "DATE CHECK — LEFT OUT ON PURPOSE",
           font=F_BOLD(10), fill=RED)
    left_out = [
        "Riyadh tower drone hit, 11 hurt — Tue 24 Nov",
        "COP31 talks end with no deal — Sun 23 Nov",
        "Nvidia +31.5% Monday surge — Mon 23 Nov",
        "Hamas chief Abu Nahel killed — Tue 24 Nov",
        "Zaporizhzhia flats hit, 2 killed — Tue 24 Nov",
        "Russian missiles hit Poland — 19 Nov",
    ]
    not_yet = [
        "Champions League results — kick off 17:45 GMT",
        "Wall Street close — after this edition",
        "US Thanksgiving — Thu 27 Nov",
    ]
    f = F_REG(9)
    ly = y + 17
    for t in left_out:
        d.text((x0 + 8, ly), "✕ " + trunc(d, t, f, 236), font=f, fill=INK)
        ly += 8.0
    d.text((x0 + 256, y + 17), "NOT YET:", font=F_BOLD(9), fill=NAVY)
    ny = y + 28
    for t in not_yet:
        d.text((x0 + 256, ny), "• " + trunc(d, t, f, 228), font=f, fill=INK)
        ny += 9
    # MARKETS, right half
    x1, w1 = 516, 496
    d.rectangle([x1, y, x1 + w1, y + h], fill=(235, 240, 245, 255),
                outline=CARD_EDGE, width=1)
    d.text((x1 + 8, y + 4), "MARKETS — WED 25 NOV SO FAR + TUE 24 NOV US CLOSES",
           font=F_BOLD(10), fill=NAVY)
    mlines = [
        "KOSPI −6.2% · Nikkei −2.8% · Taiex ~−5% · MSCI world −0.5%",
        "Tue US: Dow 50,019 +0.9%, first close above 50,000",
        "S&P −0.5% · Nasdaq −1.5% · Nvidia −5.9% · Brent ~$90",
        "US futures after PCE: S&P −2.1% · Nasdaq −3.1% · Bitcoin $59,324",
    ]
    my = y + 16
    for t in mlines:
        d.text((x1 + 8, my), t, font=F_REG(10), fill=INK)
        my += 10
    d.text((x1 + 8, y + h - 9), "Sources: Reuters — Wed 25 Nov 2026",
           font=F_REG(8), fill=MUTED)


def main():
    img = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(img, d)
    draw_timeline(img, d)
    # heroes: y 124–348
    hx = [12, 348, 684]
    for x, hero in zip(hx, HEROES):
        hero_card(img, d, x, 124, 328, 224, hero)
    # mediums: 4 cols x 3 rows, y 352–674
    mx = [12, 264, 516, 768]
    my = [352, 460, 568]
    for r in range(3):
        for c in range(4):
            medium_card(img, d, mx[c], my[r], 244, 106, MEDIUMS[r * 4 + c])
    # map: y 678–800
    draw_map(img, d, 12, 678, 1000, 122)
    # also on: y 804–937
    draw_also_on(img, d, 12, 804, 1000, 133)
    # bottom: y 942–1012
    draw_bottom(img, d, 942, 70)
    # footer
    foot = ("Sources: BBC · Reuters · AP · Xinhua · Eurostat · Principia — "
            "every event happened or was first reported Wed 25 Nov 2026.")
    fw = d.textlength(foot, font=F_REG(8))
    d.text(((W - fw) / 2, 1014), foot, font=F_REG(8), fill=MUTED)
    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
