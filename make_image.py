# make_image.py - builder only (NOT shipped as entrypoint).
# Draws the v2 front page for news-image-20261119: "Thursday 19 November 2026".
# All pictures are drawn with Pillow code. No outside images, no AI pictures.
# Run: python3 make_image.py  ->  writes entry.png (1024x1024, under 1 MiB).

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 8                      # page margin
CW = W - 2 * M             # content width = 1008
PAPER = (246, 241, 227)
INK = (28, 28, 28)
RED = (164, 35, 26)
NAVY = (32, 52, 79)
GOLD = (201, 162, 39)
GREY = (110, 104, 90)
LINE = (138, 127, 102)
SEA = (207, 224, 232)
LAND = (220, 196, 143)

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
SERIFB = os.path.join(F, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(F, "DejaVuSerif.ttf")
SANSB = os.path.join(F, "DejaVuSans-Bold.ttf")
MONTS = os.path.join(F, "Montserrat-Bold.ttf")
WS600 = os.path.join(F, "WorkSans-600.woff")
WS400 = os.path.join(F, "WorkSans-400.woff")

FONT_CACHE = {}


def font(path, size):
    key = (path, size)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = ImageFont.truetype(path, size)
    return FONT_CACHE[key]


def text_w(d, s, f):
    return d.textlength(s, font=f)


def fit_font(path, s, size, max_w, d):
    while size > 7 and text_w(d, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(d, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, f, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


# ---------------- small drawing helpers ----------------

def flag_us(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(32, 52, 79))
    for r in range(2):
        for c in range(3):
            d.ellipse([x + 4 + c * 7, y + 3 + r * 7, x + 8 + c * 7, y + 7 + r * 7],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.ellipse([x + 3, y + 3, x + 9, y + 9], fill=(255, 222, 0))
    for dx, dy in [(14, 2), (16, 6), (14, 10), (10, 8)]:
        d.ellipse([x + dx, y + dy, x + dx + 3, y + dy + 3], fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)


def flag_dk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(198, 12, 48))
    d.rectangle([x + w * 0.3, y, x + w * 0.42, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(255, 255, 255))


def person(d, cx, y, suit, tie, skin=(240, 200, 160)):
    d.ellipse([cx - 15, y, cx + 15, y + 30], fill=skin)
    d.pieslice([cx - 15, y - 2, cx + 15, y + 14], 180, 360, fill=(60, 50, 40))
    d.rectangle([cx - 22, y + 30, cx + 22, y + 66], fill=suit)
    d.polygon([(cx - 4, y + 32), (cx + 4, y + 32), (cx, y + 52)], fill=tie)
    d.rectangle([cx - 22, y + 30, cx - 14, y + 66], fill=(255, 255, 255))
    d.rectangle([cx + 14, y + 30, cx + 22, y + 66], fill=(255, 255, 255))


def scales(d, cx, y, s=1.0):
    d.line([cx, y, cx, y + 52 * s], fill=(90, 70, 40), width=3)
    d.line([cx - 30 * s, y + 8 * s, cx + 30 * s, y + 8 * s], fill=(90, 70, 40), width=3)
    for sx in (-30 * s, 30 * s):
        d.line([cx + sx, y + 8 * s, cx + sx, y + 26 * s], fill=(90, 70, 40), width=2)
        d.pieslice([cx + sx - 12 * s, y + 24 * s, cx + sx + 12 * s, y + 36 * s],
                   0, 180, fill=(201, 162, 39), outline=(90, 70, 40))


# ---------------- story data (39 stories, verified for 19 Nov 2026) ----------------

LEADS = [
    {"n": 1, "kick": "SHENZHEN \u00b7 SUMMIT",
     "head": "Trump, Xi and Putin hold first three-way summit",
     "body": "The three leaders met for 90 minutes beside the APEC summit and issued a joint declaration on nuclear risk and UN reform. \u2014 Reuters"},
    {"n": 2, "kick": "THE HAGUE \u00b7 JUSTICE",
     "head": "World Court: Myanmar committed genocide",
     "body": "By 9 votes to 6 the ICJ found Myanmar guilty of genocide against the Rohingya and ordered reparations. \u2014 Al Jazeera \u00b7 UN News"},
    {"n": 3, "kick": "WORLDWIDE \u00b7 GAMES",
     "head": "GTA VI arrives after a 13-year wait",
     "body": "Rockstar's sequel unlocks at midnight in each country, New Zealand first. 15.9m pre-orders, $79.99 on PS5 and Xbox, no PC yet. \u2014 ABC"},
]

MEDIUMS = [
    {"n": 4, "kick": "NASDAQ \u00b7 MARKETS", "art": "anthropic",
     "head": "Anthropic debuts after $81.3bn IPO",
     "body": "Priced at $83 on Wednesday, it raised $81.3bn. Shares opened at $111.50 as ANT. \u2014 AP"},
    {"n": 5, "kick": "ANTALYA \u00b7 CLIMATE", "art": "cop31",
     "head": "COP31 draft cuts $120bn aid goal",
     "body": "The slimmed text cuts the phase-out and the $120bn goal. Talks must end Friday. \u2014 Reuters"},
    {"n": 6, "kick": "SEOUL \u00b7 EDUCATION", "art": "suneung",
     "head": "Half a million sit Korea's big exam",
     "body": "551,864 take the Suneung at 1,312 sites. Flights pause; phone alerts catch 22. \u2014 Yonhap"},
    {"n": 7, "kick": "CANBERRA \u00b7 ECONOMY", "art": "jobs",
     "head": "Australia's jobless rate jumps to 4.9%",
     "body": "A five-year high, up from 4.7%. Jobs fell 43,500 in October, against a forecast rise of 25,000. \u2014 ABS"},
    {"n": 8, "kick": "ODISHA \u00b7 STORM", "art": "cyclone",
     "head": "Cyclone Akvan nears India's east coast",
     "body": "Red alerts in 11 districts; 200,000 in the evacuation zone. Landfall near Puri due Friday. \u2014 IMD"},
    {"n": 9, "kick": "CRIMEA \u00b7 WAR", "art": "bridge",
     "head": "Ukraine hits Crimea bridge for third time",
     "body": "Rail section hit overnight; traffic halted, the Russian-installed governor said. \u2014 AP"},
    {"n": 10, "kick": "RIYADH \u00b7 WAR", "art": "missile",
     "head": "Saudis down Houthi missiles over Riyadh",
     "body": "Sirens sounded at 04:42; debris fell on the capital, no casualties reported. \u2014 Reuters"},
    {"n": 11, "kick": "GAZA \u00b7 WAR", "art": "tank",
     "head": "Israeli tanks cross Gaza ceasefire line",
     "body": "The army says its raid past the Yellow Line is over; Hamas calls it a breach. \u2014 AFP"},
    {"n": 12, "kick": "GREENLAND \u00b7 SECURITY", "art": "denmark",
     "head": "Denmark backs Arctic pact, 109-0",
     "body": "Parliament approves the Greenland security deal. \u2014 AP"},
    {"n": 13, "kick": "BOGOT\u00c1 \u00b7 LABOUR", "art": "strike",
     "head": "Colombia's unions hold a national strike",
     "body": "Marches in five cities against the Economic Rescue bill. \u2014 US Embassy"},
]

BRIEFS = [
    "14 APEC \u2014 Shenzhen Outlook adopted.",
    "15 SEOUL \u2014 Top court clears ex-PM Han.",
    "16 MONGOLIA \u2014 Leader quits over graft.",
    "17 JAKARTA \u2014 Asset-seize law passes.",
    "18 DHAKA \u2014 Yunus family home torched.",
    "19 SIBERIA \u2014 Military plane crash kills 19.",
    "20 BELGRADE \u2014 New speaker elected.",
    "21 LONDON \u2014 Apple loses UK probe bid.",
    "22 LONDON \u2014 Royal Mail names new CEO.",
    "23 BERLIN \u2014 Allies back Ukraine plan.",
    "24 TURIN \u2014 Tiafoe reaches ATP semis.",
    "25 TURIN \u2014 Shelton into the last four.",
    "26 GAZA \u2014 Nasser hospital hit, 6 dead.",
    "27 JERUSALEM \u2014 Herzog meets Kahana.",
    "28 GAZA \u2014 Aid score 4 out of 26.",
    "29 MOGADISHU \u2014 Somalia expels UAE envoy.",
    "30 NAIROBI \u2014 Jepchirchir banned 3 years.",
    "31 FLORIDA \u2014 Schools shut after 15 in rain.",
    "32 WASHINGTON \u2014 Trump vs global AI rules.",
    "33 MANILA \u2014 $2bn loan to build rail.",
    "34 WASHINGTON \u2014 Trump: Iran eyes bio arms.",
    "35 NASSAU \u2014 Cyclone Xavier nears.",
    "36 SUVA \u2014 Fiji declares disaster.",
    "37 WELLINGTON \u2014 NZ 243 for 5 in Test.",
    "38 WORLD \u2014 589m children out of school.",
    "39 WORLD \u2014 NASA sets CRS-25 cover.",
]

REGIONS = [("ASIA", 10, (168, 90, 26)), ("MIDDLE EAST", 5, (142, 47, 47)),
           ("EUROPE", 8, (47, 93, 138)), ("AFRICA", 2, (61, 122, 61)),
           ("AMERICAS", 7, (106, 74, 138)), ("OCEANIA", 3, (47, 122, 122)),
           ("WORLD", 4, (51, 51, 51))]

NUMBERS = [("$81.3bn", "Anthropic's $81.3bn IPO"),
           ("15.9m", "GTA VI pre-orders banked"),
           ("551,864", "Suneung exam sitters"),
           ("$120bn", "Aid goal cut at COP31"),
           ("9-6", "World Court genocide vote"),
           ("4.9%", "Australian jobless rate")]

# ---------------- lead illustrations ----------------

def illo_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(143, 184, 216))
    for bx, bw, bh in [(0, 40, 46), (48, 26, 70), (82, 34, 52), (200, 30, 60),
                       (236, 44, 40), (288, 26, 66)]:
        d.rectangle([x + bx, y + h - 46 - bh, x + bx + bw, y + h - 46],
                    fill=(70, 90, 120))
    d.rectangle([x + 10, y + h - 46, x + w - 10, y + h - 20], fill=(122, 74, 44))
    d.rectangle([x + 10, y + h - 20, x + w - 10, y + h], fill=(240, 240, 235))
    for cx, flag, suit, tie, name in [
            (w * 0.22, flag_us, (32, 32, 48), (178, 34, 52), "TRUMP"),
            (w * 0.50, flag_cn, (24, 24, 24), (32, 93, 138), "XI"),
            (w * 0.78, flag_ru, (80, 80, 80), (32, 93, 138), "PUTIN")]:
        px = x + cx
        d.line([px - 26, y + 12, px - 26, y + 62], fill=(90, 70, 40), width=2)
        flag(d, px - 26, y + 12, 26, 17)
        person(d, px, y + 34, suit, tie)
        d.rectangle([px - 26, y + h - 34, px + 26, y + h - 20], fill=(255, 255, 255),
                    outline=(120, 110, 90))
        f = font(SANSB, 9)
        tw = text_w(d, name, f)
        d.text((px - tw / 2, y + h - 33), name, font=f, fill=INK)


def illo_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(207, 224, 232))
    d.rectangle([x + 30, y + 62, x + w - 30, y + h - 14], fill=(216, 192, 143))
    d.polygon([(x + 22, y + 64), (x + w / 2, y + 28), (x + w - 22, y + 64)],
              fill=(190, 160, 110))
    for cx in [70, 120, 170, 220, 270]:
        d.rectangle([x + cx - 7, y + 70, x + cx + 7, y + h - 30], fill=(245, 240, 225))
    d.rectangle([x + w / 2 - 14, y + h - 44, x + w / 2 + 14, y + h - 14],
                fill=(90, 70, 40))
    scales(d, x + w - 62, y + 66, s=0.9)
    d.ellipse([x + w - 78, y + 8, x + w - 18, y + 52], fill=RED)
    f = font(SANSB, 20)
    t = "9-6"
    d.text((x + w - 48 - text_w(d, t, f) / 2, y + 18), t, font=f, fill=(255, 255, 255))


def illo_gta(d, x, y, w, h):
    bands = [(123, 45, 139), (168, 60, 150), (232, 106, 168), (247, 200, 115)]
    for i, c in enumerate(bands):
        d.rectangle([x, y + i * h / 4, x + w, y + (i + 1) * h / 4], fill=c)
    d.ellipse([x + w - 110, y + 14, x + w - 40, y + 84], fill=(255, 215, 106))
    for bx, bw, bh in [(0, 46, 66), (52, 30, 96), (88, 40, 56), (134, 34, 110),
                       (174, 44, 70), (224, 30, 100), (260, 44, 60), (300, 28, 88)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(52, 24, 74))
        for wy in range(y + h - bh + 8, y + h - 6, 14):
            for wx in range(x + bx + 6, x + bx + bw - 6, 12):
                d.rectangle([wx, wy, wx + 4, wy + 6], fill=(255, 215, 106))
    for px in (30, 290):
        d.line([x + px, y + h - 52, x + px, y + h - 8], fill=(30, 90, 50), width=4)
        for a in (-50, -20, 10, 40):
            r = math.radians(a)
            d.line([x + px, y + h - 52, x + px + 26 * math.cos(r),
                    y + h - 52 + 20 * math.sin(r)], fill=(30, 90, 50), width=3)
    d.rectangle([x + 12, y + 10, x + 62, y + 40], fill=(255, 255, 255))
    f = font(SANSB, 18)
    d.text((x + 20, y + 14), "VI", font=f, fill=RED)
    f2 = font(SANSB, 9)
    d.text((x + 66, y + 20), "OUT NOW", font=f2, fill=(255, 255, 255))

LEAD_ILLOS = [illo_summit, illo_court, illo_gta]

# ---------------- medium illustrations (196 x 62) ----------------

def illo_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 59, 46))
    pts = [(x + 8, y + h - 12), (x + 40, y + h - 26), (x + 70, y + h - 20),
           (x + 100, y + h - 34), (x + 130, y + h - 28), (x + 160, y + h - 44),
           (x + 188, y + h - 52)]
    d.line(pts, fill=(255, 215, 106), width=3)
    for px, py in pts[1:]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
    f = font(SANSB, 16)
    d.text((x + 8, y + 4), "$83", font=f, fill=(255, 255, 255))
    f2 = font(SANSB, 9)
    d.text((x + 138, y + 4), "ANT", font=f2, fill=(255, 215, 106))


def illo_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 214, 228))
    d.ellipse([x + 12, y + 6, x + 66, y + 60], fill=(47, 93, 138))
    d.ellipse([x + 24, y + 16, x + 38, y + 28], fill=(90, 160, 90))
    d.ellipse([x + 40, y + 34, x + 58, y + 48], fill=(90, 160, 90))
    d.rectangle([x + 150, y + 8, x + 162, y + 52], fill=(255, 255, 255),
                outline=(120, 110, 90))
    d.rectangle([x + 152, y + 30, x + 160, y + 50], fill=(213, 0, 50))
    d.ellipse([x + 144, y + 46, x + 168, y + 60], fill=(213, 0, 50))
    f = font(SANSB, 9)
    d.text((x + 76, y + 10), "FINAL 48", font=f, fill=RED)
    d.text((x + 76, y + 24), "HOURS", font=f, fill=RED)
    d.text((x + 76, y + 40), "$120bn", font=f, fill=INK)


def illo_suneung(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(242, 228, 180))
    d.rectangle([x + 10, y + 34, x + w - 10, y + 46], fill=(122, 74, 44))
    d.rectangle([x + 30, y + 12, x + 110, y + 36], fill=(255, 255, 255),
                outline=(120, 110, 90))
    for ly in (18, 25, 32):
        d.line([x + 36, y + ly, x + 104, y + ly], fill=(150, 150, 150), width=1)
    d.rectangle([x + 118, y + 14, x + 172, y + 32], fill=(255, 215, 106),
                outline=(180, 140, 40))
    f = font(SANSB, 8)
    d.text((x + 122, y + 19), "551,864", font=f, fill=INK)
    d.ellipse([x + 6, y + 8, x + 28, y + 30], fill=(255, 255, 255),
              outline=INK)
    d.line([x + 17, y + 19, x + 17, y + 11], fill=INK, width=2)
    d.line([x + 17, y + 19, x + 23, y + 23], fill=INK, width=2)


def illo_jobs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(246, 241, 227))
    bars = [18, 24, 22, 30, 44]
    for i, bh in enumerate(bars):
        bx = x + 14 + i * 30
        d.rectangle([bx, y + h - 8 - bh, bx + 20, y + h - 8], fill=(178, 34, 52))
    d.line([x + 8, y + h - 8, x + w - 8, y + h - 8], fill=INK, width=2)
    f = font(SANSB, 16)
    d.text((x + 8, y + 4), "4.9%", font=f, fill=RED)


def illo_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 214, 228))
    cx, cy = x + 60, y + 34
    for r in (26, 19, 12):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(255, 255, 255), width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(47, 93, 138))
    for dx, dy in [(130, 10), (150, 26), (168, 8), (140, 44)]:
        d.ellipse([x + dx, y + dy, x + dx + 4, y + dy + 8], fill=(47, 93, 138))
    f = font(SANSB, 9)
    d.text((x + 108, y + 46), "RED ALERT", font=f, fill=RED)


def illo_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 205))
    d.rectangle([x, y + 44, x + w, y + h], fill=(120, 170, 205))
    d.arc([x + 20, y + 2, x + w - 20, y + 58], 180, 360, fill=(90, 90, 90), width=4)
    for px in (40, 90, 140, 170):
        d.line([x + px, y + 22, x + px, y + 44], fill=(90, 90, 90), width=3)
    d.line([x + 8, y + 22, x + w - 8, y + 22], fill=(90, 90, 90), width=3)
    cx, cy = x + 150, y + 16
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([cx, cy, cx + 16 * math.cos(r), cy + 16 * math.sin(r)],
               fill=(255, 140, 0), width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 140, 0))


def illo_missile(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(32, 52, 79))
    for bx, bw, bh in [(0, 30, 30), (36, 22, 44), (64, 34, 26), (140, 26, 38),
                       (172, 24, 30)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(16, 28, 48))
        for wy in range(y + h - bh + 6, y + h - 4, 10):
            d.rectangle([x + bx + 6, wy, x + bx + 10, wy + 4], fill=(255, 215, 106))
    d.line([x + 100, y + 8, x + 150, y + 34], fill=(255, 255, 255), width=2)
    cx, cy = x + 152, y + 36
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([cx, cy, cx + 14 * math.cos(r), cy + 14 * math.sin(r)],
               fill=(255, 140, 0), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 140, 0))


def illo_tank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 180))
    d.rectangle([x + 20, y + 34, x + 120, y + 52], fill=(90, 110, 70))
    d.rectangle([x + 55, y + 22, x + 95, y + 36], fill=(70, 90, 55))
    d.rectangle([x + 95, y + 26, x + 150, y + 30], fill=(70, 90, 55))
    for wx in range(28, 118, 18):
        d.ellipse([x + wx, y + 50, x + wx + 12, y + 58], fill=(40, 40, 40))
    f = font(SANSB, 9)
    d.text((x + 140, y + 8), "TANK", font=f, fill=INK)


def illo_denmark(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 214, 228))
    for bx, bw, bh in [(0, 60, 40), (60, 70, 30), (130, 66, 46)]:
        d.polygon([(x + bx, y + h), (x + bx + bw / 2, y + h - bh),
                   (x + bx + bw, y + h)], fill=(245, 245, 240),
                  outline=(150, 150, 150))
    d.line([x + 20, y + 8, x + 20, y + 30], fill=(90, 70, 40), width=2)
    flag_dk(d, x + 20, y + 8, 24, 15)
    d.line([x + 60, y + 8, x + 60, y + 30], fill=(90, 70, 40), width=2)
    flag_us(d, x + 60, y + 8, 24, 15)
    d.rectangle([x + 118, y + 4, x + 188, y + 24], fill=RED)
    f = font(SANSB, 12)
    d.text((x + 128, y + 7), "109-0", font=f, fill=(255, 255, 255))


def illo_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(242, 228, 180))
    d.rectangle([x + 8, y + 6, x + 78, y + 22], fill=(255, 215, 106),
                outline=(180, 140, 40))
    f = font(SANSB, 10)
    d.text((x + 16, y + 8), "PARO", font=f, fill=INK)
    for i, cx in enumerate((30, 70, 110, 150, 180)):
        d.ellipse([x + cx - 8, y + 30, x + cx + 8, y + 46], fill=(240, 200, 160))
        d.rectangle([x + cx - 12, y + 46, x + cx + 12, y + h], fill=(32, 93, 138)
                    if i % 2 == 0 else (178, 34, 52))
        d.rectangle([x + cx - 14, y + 24, x + cx + 14, y + 34], fill=(255, 255, 255),
                    outline=(120, 110, 90))

ART = {"anthropic": illo_anthropic, "cop31": illo_cop31, "suneung": illo_suneung,
       "jobs": illo_jobs, "cyclone": illo_cyclone, "bridge": illo_bridge,
       "missile": illo_missile, "tank": illo_tank, "denmark": illo_denmark,
       "strike": illo_strike}

# ---------------- page sections ----------------

def draw_top(d):
    f_small = font(WS600, 11)
    d.text((M, 8), "THE WORLD IN ONE DAY", font=f_small, fill=RED)
    right = "39 STORIES \u00b7 EVERY CONTINENT \u00b7 ALL FROM THIS ONE DAY"
    d.text((W - M - text_w(d, right, f_small), 8), right, font=f_small, fill=INK)
    f_head = fit_font(SERIFB, "Thursday 19 November 2026", 60, CW, d)
    d.text((M, 26), "Thursday 19 November 2026", font=f_head, fill=INK)
    kick = ("Trump, Xi and Putin share one table \u00b7 World Court finds genocide "
            "in Myanmar \u00b7 GTA VI ends a 13-year wait")
    f_kick = fit_font(SERIFB, kick, 15, CW, d)
    d.text((M, 94), kick, font=f_kick, fill=RED)
    d.line([M, 116, W - M, 116], fill=INK, width=2)


def draw_regions(d):
    y0, y1 = 120, 142
    total = sum(c for _, c, _ in REGIONS)
    x = M
    widths = []
    for name, count, color in REGIONS:
        widths.append(round(CW * count / total))
    widths[-1] += CW - sum(widths)
    f = font(WS600, 10)
    for (name, count, color), wd in zip(REGIONS, widths):
        d.rectangle([x, y0, x + wd, y1], fill=color)
        label = "%s %d" % (name, count)
        tw = text_w(d, label, f)
        d.text((x + (wd - tw) / 2, y0 + 5), label, font=f, fill=(255, 255, 255))
        x += wd


def draw_numbers(d):
    y0, y1 = 146, 206
    cw = CW // 6
    d.line([M, y0 - 2, W - M, y0 - 2], fill=LINE, width=1)
    d.line([M, y1 + 2, W - M, y1 + 2], fill=LINE, width=1)
    for i, (num, label) in enumerate(NUMBERS):
        x = M + i * cw
        if i:
            d.line([x, y0 + 4, x, y1 - 4], fill=LINE, width=1)
        f_num = fit_font(SERIFB, num, 30, cw - 8, d)
        tw = text_w(d, num, f_num)
        d.text((x + (cw - tw) / 2, y0 + 4), num, font=f_num, fill=RED)
        f_lab = fit_font(WS600, label, 10, cw - 8, d)
        tw = text_w(d, label, f_lab)
        d.text((x + (cw - tw) / 2, y0 + 40), label, font=f_lab, fill=INK)


def draw_leads(d):
    y0, h, w = 212, 258, 328
    xs = [M, M + 336, M + 672]
    for card, x, illo in zip(LEADS, xs, LEAD_ILLOS):
        d.rectangle([x, y0, x + w, y0 + h], fill=(255, 255, 255), outline=INK, width=2)
        illo(d, x + 2, y0 + 2, w - 4, 140)
        f_kick = font(SANSB, 10)
        d.text((x + 8, y0 + 146), "%d \u00b7 %s" % (card["n"], card["kick"]),
               font=f_kick, fill=RED)
        f_head = font(SERIFB, 22)
        lines = wrap(d, card["head"], f_head, w - 16)
        draw_lines(d, lines[:2], x + 8, y0 + 162, f_head, INK, 24)
        f_body = font(SERIF, 12)
        blines = wrap(d, card["body"], f_body, w - 16)
        draw_lines(d, blines[:3], x + 8, y0 + 162 + 24 * len(lines[:2]) + 2,
                   f_body, INK, 14)


def draw_mediums(d):
    rows = [476, 630]
    h, w = 148, 196
    xs = [M, M + 203, M + 406, M + 609, M + 812]
    for r, y0 in enumerate(rows):
        for c, x in enumerate(xs):
            card = MEDIUMS[r * 5 + c]
            d.rectangle([x, y0, x + w, y0 + h], fill=(255, 255, 255),
                        outline=INK, width=1)
            ART[card["art"]](d, x + 1, y0 + 1, w - 2, 56)
            f_kick = font(SANSB, 9)
            d.text((x + 6, y0 + 60), "%d \u00b7 %s" % (card["n"], card["kick"]),
                   font=f_kick, fill=RED)
            f_head = font(SERIFB, 15)
            lines = wrap(d, card["head"], f_head, w - 12)
            draw_lines(d, lines[:2], x + 6, y0 + 74, f_head, INK, 17)
            f_body = font(WS400, 10)
            blines = wrap(d, card["body"], f_body, w - 12)
            draw_lines(d, blines[:3], x + 6, y0 + 74 + 17 * len(lines[:2]) + 2,
                       f_body, INK, 12)


CONTINENTS = [
    [(26, 30), (44, 20), (72, 14), (104, 16), (126, 28), (120, 44), (112, 52),
     (104, 62), (96, 74), (88, 68), (76, 80), (58, 90), (40, 84), (28, 66), (22, 48)],
    [(88, 108), (128, 96), (146, 104), (154, 124), (146, 150), (130, 178),
     (116, 152), (98, 128)],
    [(166, 30), (184, 20), (202, 24), (210, 38), (202, 52), (188, 60),
     (172, 50), (162, 38)],
    [(172, 68), (196, 58), (216, 66), (230, 88), (232, 108), (222, 130),
     (206, 152), (190, 134), (180, 108), (170, 86)],
    [(212, 26), (244, 16), (282, 16), (312, 26), (330, 48), (324, 72),
     (306, 92), (292, 102), (268, 94), (250, 98), (234, 80), (220, 56), (208, 38)],
    [(286, 138), (306, 130), (326, 138), (330, 156), (312, 166), (292, 160), (282, 148)],
]
ISLANDS = [
    [(158, 26), (164, 24), (166, 34), (162, 42), (156, 36)],
    [(332, 56), (338, 54), (340, 68), (334, 70)],
    [(262, 104), (266, 102), (270, 106), (266, 108)],
    [(274, 108), (278, 106), (282, 110), (278, 112)],
    [(332, 148), (336, 146), (338, 158), (334, 160)],
]

PINS = {1: (286, 44), 2: (188, 40), 3: (120, 130), 4: (70, 60), 5: (252, 56),
        6: (286, 74), 7: (310, 118), 8: (264, 78), 9: (186, 34), 10: (232, 66),
        11: (228, 58), 12: (66, 22), 13: (96, 122)}


def draw_map(d):
    f_title = font(SANSB, 11)
    d.text((M, 786), "WHERE IT HAPPENED", font=f_title, fill=RED)
    x0, y0, w, h = M, 802, 344, 182
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=INK, width=1)
    for poly in CONTINENTS:
        pts = [(x0 + px, y0 + py) for px, py in poly]
        d.polygon(pts, fill=LAND, outline=(150, 130, 90))
    for poly in ISLANDS:
        pts = [(x0 + px, y0 + py) for px, py in poly]
        d.polygon(pts, fill=LAND, outline=(150, 130, 90))
    f_pin = font(SANSB, 9)
    for n, (px, py) in PINS.items():
        cx, cy = x0 + px, y0 + py
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(n)
        d.text((cx - text_w(d, t, f_pin) / 2, cy - 6), t, font=f_pin,
               fill=(255, 255, 255))
    f_note = font(WS400, 8)
    d.text((x0 + 4, y0 + h - 12), "Red numbers mark stories 1-13. Positions are approximate.",
           font=f_note, fill=(60, 60, 60))


def draw_list(d):
    f_title = font(SANSB, 11)
    d.text((360, 786), "ALSO ON THURSDAY 19 NOVEMBER \u2014 26 MORE STORIES",
           font=f_title, fill=RED)
    f_item = font(WS600, 9)
    cols = [360, 578, 796]
    for i, item in enumerate(BRIEFS):
        col = i // 9
        row = i % 9
        x = cols[col]
        y = 804 + row * 20
        d.text((x, y), item, font=f_item, fill=INK)


def draw_footer(d):
    d.rectangle([M, 988, W - M, 1010], outline=RED, width=1)
    f_dc = font(WS600, 9)
    dc = ("DATE CHECK \u2014 Left out as other days' news: Anthropic's $83 pricing "
          "(Wed 18; first trades Thu 19) \u00b7 Iran fires on Kuwait and Bahrain (18 Nov) "
          "\u00b7 Tanker hit in Hormuz (18 Nov) \u00b7 Voyager 1 crosses one light-day (18 Nov) "
          "\u00b7 Kahana elected speaker (Tue 17) \u00b7 Peltola wins Alaska (18 Nov) "
          "\u00b7 Pew: Muslims largest by 2035 (first reported 18 Nov).")
    lines = wrap(d, dc, f_dc, CW - 12)
    draw_lines(d, lines, M + 6, 990, f_dc, RED, 11)
    f_src = font(WS400, 8)
    src = ("Every story here happened, or was first reported, on Thursday 19 November 2026. "
           "Claims are attributed, not stated as fact. Sources: Reuters, AP, AFP, BBC, "
           "Al Jazeera, Yonhap, ABS, IMD, UN News, Nasdaq, Sensor Tower.")
    d.text((M, 1012), src, font=f_src, fill=GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top(d)
    draw_regions(d)
    draw_numbers(d)
    draw_leads(d)
    draw_mediums(d)
    draw_map(d)
    draw_list(d)
    draw_footer(d)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    print(build())
