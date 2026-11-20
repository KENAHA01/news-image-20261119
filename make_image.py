# make_image.py -- v15 builder, derived from the v14 builder.
# Draws "Thursday 19 November 2026", 45 stories, for
# news-image-20261119.
# v15 is a DIFFERENT design, not another iteration of the same grid:
# only 7 ILLUSTRATED featured cards (3 leads + 4 mediums, all
# painterly, modelled on rank 10 aw-rama, which wins reads and craft
# against us with just 7 cards), each much bigger than v14's, with
# lead headlines 32/30pt and medium headlines 24/22pt. The other six
# v14 mediums become briefs, so the page still carries 45 stories
# (7 featured + 38 briefs). See SOURCES-v15.md; every story still on
# the page traces to sources.json (ids 1-39) or SOURCES-v12.md
# (ids 40-45). Nothing is invented. Assets are fixed files, so
# compositing is deterministic.
# Run: python3 make_image.py -> writes entry.png.

import hashlib
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

# ---------------- generated illustration assets ----------------
# Thirteen panels use painterly illustrations: 8 reused from v12
# (gta, summit, court, riyadh, ant, cop, bridge, tank) + 5 generated
# in this session (exam, storm, senate, dow, navy). The images carry
# no text at all; every word on the page is drawn by Pillow.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
_CTX = {"img": None}
_ASSET_CACHE = {}


def asset(name):
    if name not in _ASSET_CACHE:
        _ASSET_CACHE[name] = Image.open(
            os.path.join(ASSET_DIR, name)).convert("RGB")
    return _ASSET_CACHE[name]


def paste_asset(name, x0, y0, x1, y1, fy=0.5):
    """Paste a generated illustration into a panel: crop to the panel
    aspect (vertical focus fy = centre of the crop window as a
    fraction of the source height), resize with LANCZOS, paste.
    No stretching, no randomness: byte-identical every run."""
    src = asset(name)
    tw_, th_ = x1 - x0, y1 - y0
    target = tw_ / th_
    sw, sh = src.size
    if sw / sh > target:
        ch = sh
        cw = int(round(ch * target))
        cx0 = (sw - cw) // 2
        box = (cx0, 0, cx0 + cw, ch)
    else:
        cw = sw
        ch = int(round(cw / target))
        cy0 = int(round(fy * sh - ch / 2))
        cy0 = max(0, min(sh - ch, cy0))
        box = (0, cy0, cw, cy0 + ch)
    crop = src.crop(box).resize((tw_, th_), Image.LANCZOS)
    _CTX["img"].paste(crop, (x0, y0))


W, H = 1024, 1024
M = 8                      # page margin
CW = W - 2 * M             # content width: 1008

PAPER = (246, 241, 227)
CARD = (252, 250, 242)
INK = (28, 28, 28)
RED = (164, 35, 26)
NAVY = (32, 52, 79)
GOLD = (201, 162, 39)
GREY = (110, 104, 90)
RULE = (138, 127, 102)
SEA = (207, 224, 232)
LAND = (220, 196, 143)
GREEN = (34, 120, 62)
AMBER = (176, 124, 18)


def _pick(cands):
    for p in cands:
        p = os.path.expanduser(p)
        if os.path.exists(p):
            return p
    raise SystemExit("font missing: %s" % (cands,))


SERIF_B = _pick(["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"])
SERIF_R = _pick(["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"])
SERIF_I = _pick(["/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"])
SANS_B = _pick(["/usr/share/fonts/truetype/gfonts/montserrat/montserrat-v14-latin-700.ttf",
                "~/.fonts/Montserrat-Bold.ttf"])
SANS_R = _pick(["/usr/share/fonts/truetype/gfonts/montserrat/montserrat-v14-latin-regular.ttf",
                "~/.fonts/Montserrat-Regular.ttf"])
SANS_XB = _pick(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])

_F = {}


def F(path, size):
    k = (path, size)
    if k not in _F:
        _F[k] = ImageFont.truetype(path, size)
    return _F[k]


def tw(d, s, f):
    return d.textlength(s, font=f)


def wrap_lines(d, text, f, limit):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= limit:
            cur = t
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def draw_lines(d, ls, x, y, f, fill, step):
    for s in ls:
        d.text((x, y), s, font=f, fill=fill)
        y += step
    return y


def fit_font(d, text, path, size, limit):
    while size > 7 and tw(d, text, F(path, size)) > limit:
        size -= 1
    return F(path, size)


def head_font(d, text, path, big, small, limit):
    """Try the bigger size; fall back if the headline needs > 2 lines."""
    f = F(path, big)
    if len(wrap_lines(d, text, f, limit)) <= 2:
        return f
    return F(path, small)


def chip(d, x, y, label, bg, fg=(255, 255, 255), size=9):
    f = F(SANS_B, size)
    w = int(tw(d, label, f)) + 12
    h = size + 8
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    d.text((x + 6, y + 3), label, font=f, fill=fg)
    return w


def hline(d, x0, x1, y, fill=RULE, w=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(d, box, top, bot, steps=24):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        d.rectangle([x0, y0 + h * t0, x1, y0 + h * t1 + 1],
                    fill=mix(top, bot, (t0 + t1) / 2))


def rings(d, cx, cy, spec):
    for r, col in spec:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def drop_shadow(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0 + 2, y1 - 1, x1 + 2, y1 + 2], fill=(210, 204, 188))
    d.rectangle([x1 + 1, y0 + 2, x1 + 2, y1 + 1], fill=(210, 204, 188))


def face(d, cx, cy, r, style):
    """Finished face: hair with highlight, brows, eyes, nose, mouth."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 190, 150))
    d.ellipse([cx - r - 2, cy - 2, cx - r + 2, cy + 4], fill=(232, 190, 150))
    d.ellipse([cx + r - 2, cy - 2, cx + r + 2, cy + 4], fill=(232, 190, 150))
    if style == "blond":
        d.pieslice([cx - r, cy - r - 3, cx + r, cy - 1], 180, 360,
                   fill=(238, 210, 120))
        d.arc([cx - r + 2, cy - r, cx + r - 2, cy + 2], 200, 340,
              fill=(250, 232, 160), width=2)
        d.rectangle([cx - r, cy - 4, cx - r + 4, cy + 3], fill=(238, 210, 120))
    elif style == "black":
        d.pieslice([cx - r, cy - r - 3, cx + r, cy - 2], 180, 360,
                   fill=(24, 24, 24))
        d.arc([cx - r + 3, cy - r + 1, cx + r - 3, cy + 2], 205, 335,
              fill=(90, 90, 90), width=2)
    else:
        d.pieslice([cx - r, cy - r - 3, cx + r, cy - 2], 180, 360,
                   fill=(198, 198, 198))
        d.arc([cx - r + 3, cy - r + 1, cx + r - 3, cy + 2], 205, 335,
              fill=(255, 255, 255), width=2)
    d.line([(cx - 7, cy - 5), (cx - 3, cy - 6)], fill=INK, width=1)
    d.line([(cx + 3, cy - 6), (cx + 7, cy - 5)], fill=INK, width=1)
    for ex in (-5, 5):
        d.ellipse([cx + ex - 2, cy - 3, cx + ex + 2, cy + 1], fill=(255, 255, 255))
        d.ellipse([cx + ex - 1, cy - 2, cx + ex + 1, cy], fill=INK)
    d.line([(cx, cy + 1), (cx - 1, cy + 4)], fill=(180, 140, 110), width=1)
    d.arc([cx - 4, cy + 3, cx + 4, cy + 9], 10, 170, fill=(140, 60, 50), width=1)
    d.ellipse([cx - r + 1, cy + 2, cx - r + 4, cy + 5], fill=(240, 170, 150))
    d.ellipse([cx + r - 4, cy + 2, cx + r - 1, cy + 5], fill=(240, 170, 150))


def leader(d, cx, hy, style, suit=(38, 38, 48), tie=(164, 35, 26)):
    face(d, cx, hy, 13, style)
    d.rectangle([cx - 22, hy + 15, cx + 22, hy + 44], fill=suit)
    d.rectangle([cx - 22, hy + 15, cx - 18, hy + 44], fill=(60, 60, 74))
    d.rectangle([cx + 18, hy + 15, cx + 22, hy + 44], fill=(24, 24, 32))
    d.polygon([(cx - 7, hy + 15), (cx + 7, hy + 15), (cx, hy + 31)],
              fill=(255, 255, 255))
    d.polygon([(cx - 3, hy + 18), (cx + 3, hy + 18), (cx + 2, hy + 42),
               (cx - 2, hy + 42)], fill=tie)
    d.line([(cx - 7, hy + 15), (cx, hy + 31)], fill=(220, 220, 220), width=1)
    d.line([(cx + 7, hy + 15), (cx, hy + 31)], fill=(200, 200, 200), width=1)


def flag(d, x, y, kind):
    d.line([(x + 8, y), (x + 8, y + 16)], fill=(90, 70, 40), width=1)
    if kind == "us":
        d.rectangle([x, y, x + 16, y + 11], fill=(178, 34, 52))
        for i in range(3):
            d.rectangle([x, y + i * 4, x + 16, y + i * 4 + 2],
                        fill=(255, 255, 255))
        d.rectangle([x, y, x + 7, y + 6], fill=(40, 60, 120))
    elif kind == "cn":
        d.rectangle([x, y, x + 16, y + 11], fill=(222, 41, 16))
        d.ellipse([x + 2, y + 2, x + 6, y + 6], fill=(255, 222, 0))
    else:
        d.rectangle([x, y, x + 16, y + 4], fill=(255, 255, 255))
        d.rectangle([x, y + 4, x + 16, y + 8], fill=(0, 60, 160))
        d.rectangle([x, y + 8, x + 16, y + 11], fill=(200, 30, 30))


def starburst(d, cx, cy, r, fill):
    pts = []
    for i in range(16):
        a = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)

# ---------------- verified story data: 45 stories, all 19 Nov 2026 ----------------
# Every entry traces to sources.json (ids 1-39) or SOURCES-v12.md
# (ids 40-45). v15 features only 7 cards (ids 1, 2, 3, 4, 5, 10, 11);
# the six v14 mediums demoted to briefs are ids 6, 8, 9, 40, 41, 42.
# Total: 3 leads + 4 mediums + 38 briefs = 45.

LEAD_ITEMS = [
    (1, "SHENZHEN \u00b7 SUMMIT", "REPORTED",
     "Trump, Xi, Putin hold first three-way summit",
     "Three leaders met 90 minutes beside APEC and declared nuclear "
     "war cannot be won. \u2014 Reuters"),
    (2, "THE HAGUE \u00b7 JUSTICE", "REPORTED",
     "World Court: Myanmar committed genocide",
     "By 9-6 the ICJ found Myanmar guilty of genocide against the "
     "Rohingya. \u2014 Al Jazeera"),
    (3, "WORLDWIDE \u00b7 GAMES", "REPORTED",
     "GTA VI arrives after a 13-year wait",
     "Unlocks at midnight in each country, New Zealand first, 13 years "
     "after GTA V. \u2014 ABC"),
]

# Row 1: three cards across (330px each). Row 2: three cards across
# (330px each, the war row). Row 3: four cards across (245px each).
MID_ITEMS = [
    # v15: ONE row of four BIG cards (245px each). Only the four most
    # consequential mediums stay featured; the other six are briefs.
    (4, "NASDAQ \u00b7 MARKETS", "ant", "REPORTED",
     "Anthropic debuts after $81.3bn IPO",
     "Priced at $83 on Wednesday, it raised $81.3bn. Shares opened at "
     "$111.50 as ANT. \u2014 AP"),
    (5, "ANTALYA \u00b7 CLIMATE", "cop", "REPORTED",
     "COP31 draft cuts $120bn aid goal",
     "The slimmed text cuts the phase-out and the $120bn goal. Talks "
     "must end Friday. \u2014 Reuters"),
    (10, "RIYADH \u00b7 WAR", "rocket", "CLAIM",
     "Saudis down Houthi missiles over Riyadh",
     "Sirens at 04:42; debris fell, no casualties. A Houthi hit claim "
     "is unverified. \u2014 Reuters"),
    (11, "GAZA \u00b7 WAR", "tank", "CLAIM",
     "Israeli tanks cross Gaza ceasefire line",
     "Israel says its raid past the Yellow Line is over; Hamas calls it "
     "a breach. \u2014 AFP"),
]

# 38 briefs, in numeric order. Total stories: 3 leads + 4 mediums
# + 38 = 45. The six demoted v14 mediums are briefs 6, 8, 9, 40, 41, 42.
BRIEF_ITEMS = [
    (6, "SEOUL", "551,864 sit Suneung exam."),
    (7, "CANBERRA", "Jobless 4.9%, 5-year high."),
    (8, "ODISHA", "Cyclone Akvan nears coast."),
    (9, "CRIMEA", "Bridge hit a third time."),
    (12, "GREENLAND", "Arctic pact passes 109-0."),
    (13, "BOGOT\u00c1", "Unions hold national strike."),
    (14, "APEC", "Shenzhen Outlook adopted."),
    (15, "SEOUL", "Top court clears ex-PM Han."),
    (16, "MONGOLIA", "Leader quits over graft."),
    (17, "JAKARTA", "Asset-seize law passes."),
    (18, "DHAKA", "Yunus family home torched."),
    (19, "SIBERIA", "Military plane crash kills 19."),
    (20, "BELGRADE", "New speaker elected."),
    (21, "LONDON", "Apple loses UK probe bid."),
    (22, "LONDON", "Royal Mail names CEO."),
    (23, "BERLIN", "Allies back Ukraine plan."),
    (24, "TURIN", "Tiafoe reaches ATP semis."),
    (25, "TURIN", "Shelton beats Jodar."),
    (26, "GAZA", "Nasser hospital hit, 6 dead."),
    (27, "JERUSALEM", "Herzog meets Kahana."),
    (28, "GAZA", "Aid score 4 out of 26."),
    (29, "MOGADISHU", "UAE envoy expelled."),
    (30, "NAIROBI", "Jepchirchir banned 3 yrs."),
    (31, "FLORIDA", "Schools shut, 15 in rain."),
    (32, "WASHINGTON", "Trump vs AI rules."),
    (33, "MANILA", "$2bn loan to build rail."),
    (34, "WASHINGTON", "Trump: Iran eyes bio arms."),
    (35, "NASSAU", "Cyclone Xavier nears."),
    (36, "FIJI", "Disaster over drought."),
    (37, "WELLINGTON", "NZ 243 for 5, day one."),
    (38, "WORLD", "589m children in conflict zones."),
    (39, "FLORIDA", "NASA sets CRS-25 cover."),
    (40, "WASHINGTON", "Senate rejects Iran bid 51-48."),
    (41, "NEW YORK", "Dow falls 1,101."),
    (42, "LONDON", "UK, Norway fund naval craft."),
    (43, "PARIS", "1,000 mayors seek primary vs Le Pen."),
    (44, "WASHINGTON", "Sanders rules out 2028 run at 85."),
    (45, "NEW YORK", "Walmart sales $188.8bn, +5.2%."),
]

REGION_BANDS = [
    ("ASIA 10", (168, 84, 32), 10),
    ("MIDDLE EAST 5", (140, 32, 32), 5),
    ("EUROPE 10", (38, 84, 138), 10),
    ("AFRICA 2", (46, 110, 62), 2),
    ("AMERICAS 12", (96, 58, 128), 12),
    ("OCEANIA 3", (22, 122, 118), 3),
    ("WORLD 3", (74, 74, 74), 3),
]

NUMBER_CELLS = [
    ("$81.3bn", "Anthropic's $81.3bn IPO"),
    ("15.9m", "GTA VI pre-orders banked"),
    ("551,864", "Suneung exam sitters"),
    ("$120bn", "Aid goal cut at COP31"),
    ("9-6", "World Court genocide vote"),
    ("-1,101", "Dow's 1,101-point fall"),
]

HOUR_CELLS = [
    ("00:00", "AUCKLAND", "GTA VI unlocks"),
    ("04:42", "RIYADH", "air-raid sirens"),
    ("08:40", "SEOUL", "exam begins"),
    ("09:30", "NEW YORK", "market opens"),
    ("10:00", "THE HAGUE", "genocide ruling"),
    ("13:05", "SEOUL", "flights pause"),
    ("16:30", "SHENZHEN", "three leaders meet"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Left out as other days' news: Anthropic's $83 pricing "
    "(Wed 18, first trades Thu 19) \u00b7 Iran fires on Kuwait and Bahrain "
    "(18 Nov) \u00b7 Tanker hit in Hormuz (18 Nov) \u00b7 Voyager 1 crosses "
    "one light-day (18 Nov) \u00b7 Kahana elected speaker (Tue 17) \u00b7 "
    "Pew: Muslims largest by 2035. "
    "Not yet Thursday's news: COP31's scheduled close (Fri 20) \u00b7 "
    "Cyclone Akvan's landfall (Fri 20)."
)

FOOT_LINE = (
    "Every story here happened, or was first reported, on Thursday 19 "
    "November 2026. Claims are attributed, not stated as fact. Sources: "
    "Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, ABS, IMD, UN News, "
    "Nasdaq, Sensor Tower, Investopedia, Morningstar, BusinessWire, "
    "Europa Express, Wash. Examiner."
)

PIN_SPOTS = [(0.84, 0.38), (0.48, 0.20), (0.93, 0.80), (0.24, 0.30),
             (0.55, 0.30), (0.88, 0.30), (0.88, 0.72)]

# ---------------- lead illustrations: shaded, finished, richer ----------------

def art_summit(d, x0, y0, x1, y1):
    """Grand summit hall: generated painterly scene (leaders left,
    centre, right at the oval table). Pillow name plates, flags and
    the APEC caption bar stay drawn on top, exactly as in v10."""
    w = x1 - x0
    paste_asset("summit.png", x0, y0, x1, y1, fy=0.56)
    spots = [(0.20, "TRUMP", "USA", "us"),
             (0.50, "XI", "CHINA", "cn"),
             (0.80, "PUTIN", "RUSSIA", "ru")]
    for frac, name, country, flg in spots:
        cx = x0 + w * frac
        flag(d, cx - 34, y0 + 62, flg)
        pf = F(SANS_B, 9)
        pw = int(tw(d, name, pf)) + 10
        d.rectangle([cx - pw // 2 + 1, y0 + 81, cx + pw // 2 + 1, y0 + 93],
                    fill=(200, 196, 182))
        d.rectangle([cx - pw // 2, y0 + 80, cx + pw // 2, y0 + 92],
                    fill=(255, 255, 255))
        d.text((cx - pw // 2 + 5, y0 + 82), name, font=pf, fill=INK)
        cf = F(SANS_B, 8)
        cw = tw(d, country, cf)
        # v11: the generated table is dark wood, so the red country
        # label needs the same white chip as the name plate, or it
        # vanishes against the wood and the red caption strip below.
        d.rectangle([cx - cw / 2 - 4, y0 + 93, cx + cw / 2 + 4, y0 + 102],
                    fill=(255, 255, 255))
        d.text((cx - cw / 2, y0 + 94), country, font=cf, fill=RED)
    d.rectangle([x0, y1 - 8, x1, y1], fill=RED)
    d.rectangle([x0, y1 - 8, x1, y1 - 6], fill=(200, 60, 44))
    sf = F(SANS_B, 7)
    label = "APEC 2026 \u00b7 SHENZHEN"
    lw = tw(d, label, sf)
    d.text((x0 + (w - lw) / 2, y1 - 7), label, font=sf, fill=GOLD)


def art_court(d, x0, y0, x1, y1):
    """The Hague courtroom: generated painterly scene (marble columns,
    pediment, golden scales on the right). The Pillow 9-6 verdict
    badge stays drawn on top; the decorative flag is dropped."""
    paste_asset("court.png", x0, y0, x1, y1, fy=0.55)
    d.ellipse([x1 - 53, y0 + 7, x1 - 9, y0 + 39], fill=(120, 20, 16))
    d.ellipse([x1 - 52, y0 + 8, x1 - 10, y0 + 38], fill=RED,
              outline=(255, 255, 255), width=1)
    d.text((x1 - 44, y0 + 14), "9-6", font=F(SANS_B, 15),
           fill=(255, 255, 255))


def art_gta(d, x0, y0, x1, y1):
    """Vice City at night: generated painterly scene (huge orange sun,
    lit skyline, pink sports car, palms, crowd). The Pillow VI badge
    and OUT NOW label stay drawn on top, exactly as in v10."""
    paste_asset("gta.png", x0, y0, x1, y1, fy=0.47)
    d.rectangle([x0 + 7, y0 + 7, x0 + 53, y0 + 35], fill=(220, 216, 200))
    d.rectangle([x0 + 8, y0 + 8, x0 + 52, y0 + 34], fill=(255, 255, 255))
    d.text((x0 + 14, y0 + 10), "VI", font=F(SANS_B, 18), fill=RED)
    d.text((x0 + 56, y0 + 12), "OUT NOW", font=F(SANS_B, 10),
           fill=(255, 255, 255))


def art_ant(d, x0, y0, x1, y1):
    """Dark market panel: generated painterly trading floor (green
    candles on dark screens). The Pillow $83 label and ANT +34% chip
    stay drawn on top, on dark chips so they read on any background."""
    paste_asset("ant.png", x0, y0, x1, y1, fy=0.5)
    d.rounded_rectangle([x0 + 6, y0 + 4, x0 + 52, y0 + 24], radius=4,
                        fill=(10, 22, 36))
    d.text((x0 + 10, y0 + 6), "$83", font=F(SANS_B, 15),
           fill=(255, 255, 255))
    d.rounded_rectangle([x0 + 56, y0 + 7, x0 + 118, y0 + 21], radius=7,
                        fill=(34, 120, 62))
    d.text((x0 + 60, y0 + 9), "ANT +34%", font=F(SANS_B, 10),
           fill=(255, 255, 255))


def art_cop(d, x0, y0, x1, y1):
    """Climate summit hall: generated painterly scene (globe, delegates,
    sunset). The Pillow CUT stamp and $120bn label stay drawn on top,
    the $120bn on a white chip so it reads on the bright sky."""
    paste_asset("cop.png", x0, y0, x1, y1, fy=0.5)
    sx = x1 - 42
    d.rectangle([sx, y0 + 7, sx + 42, y0 + 27], fill=(140, 20, 16))
    d.rectangle([sx + 1, y0 + 8, sx + 41, y0 + 26], fill=RED)
    d.text((sx + 7, y0 + 11), "CUT", font=F(SANS_B, 12),
           fill=(255, 255, 255))
    d.rectangle([sx - 18, y0 + 30, x1 - 1, y0 + 46], fill=(255, 255, 255))
    d.text((sx - 15, y0 + 32), "$120bn", font=F(SANS_B, 11), fill=RED)


def art_exam(d, x0, y0, x1, y1):
    """Exam hall: generated painterly scene (students at desks, wall
    clock, morning light). No text in the panel."""
    paste_asset("exam.png", x0, y0, x1, y1, fy=0.55)


def art_storm(d, x0, y0, x1, y1):
    """Cyclone spiral over the coast: generated painterly scene. The
    small RED ALERT strip stays drawn on top."""
    paste_asset("storm.png", x0, y0, x1, y1, fy=0.5)
    d.rectangle([x0, y1 - 10, x1, y1], fill=RED)
    d.rectangle([x0, y1 - 10, x1, y1 - 8], fill=(200, 60, 44))
    d.text((x0 + 6, y1 - 9), "RED ALERT", font=F(SANS_B, 8),
           fill=(255, 255, 255))


def art_bridge(d, x0, y0, x1, y1):
    """Kerch bridge at night: generated painterly scene (moon, fire
    burst on the deck, reflections on the water). No text in the panel."""
    paste_asset("bridge.png", x0, y0, x1, y1, fy=0.5)


def art_rocket(d, x0, y0, x1, y1):
    """Riyadh skyline at night: generated painterly scene, golden
    interceptor bursts over lit towers. No text in the panel."""
    paste_asset("riyadh.png", x0, y0, x1, y1, fy=0.42)


def art_tank(d, x0, y0, x1, y1):
    """Tank on sand: generated painterly desert scene (golden hour,
    second tank in the distance). The small TANK label stays drawn
    on top, on a pale chip."""
    paste_asset("tank.png", x0, y0, x1, y1, fy=0.5)
    d.rectangle([x0 + 6, y0 + 2, x0 + 46, y0 + 16], fill=(240, 232, 210))
    d.text((x0 + 8, y0 + 4), "TANK", font=F(SANS_B, 9), fill=(90, 80, 60))


def art_senate(d, x0, y0, x1, y1):
    """US Senate chamber: generated painterly scene (curved desks,
    flags, golden ceiling light). The 51-48 vote chip stays drawn
    on top, on a white chip."""
    paste_asset("senate.png", x0, y0, x1, y1, fy=0.5)
    d.rectangle([x0 + 6, y0 + 4, x0 + 58, y0 + 20], fill=(255, 255, 255))
    d.text((x0 + 10, y0 + 6), "51-48", font=F(SANS_B, 10), fill=RED)


def art_dow(d, x0, y0, x1, y1):
    """Trading floor in a sell-off: generated painterly scene (red
    falling candles on dark screens, traders below). The -1,101 chip
    stays drawn on top, white on red."""
    paste_asset("dow.png", x0, y0, x1, y1, fy=0.4)
    d.rectangle([x0 + 6, y0 + 4, x0 + 62, y0 + 20], fill=RED)
    d.text((x0 + 10, y0 + 6), "-1,101", font=F(SANS_B, 10),
           fill=(255, 255, 255))


def art_navy(d, x0, y0, x1, y1):
    """Two warships at dusk: generated painterly scene (grey sea,
    orange sunset). The £100m+ chip stays drawn on top, on a white
    chip."""
    paste_asset("navy.png", x0, y0, x1, y1, fy=0.5)
    d.rectangle([x0 + 6, y0 + 4, x0 + 66, y0 + 20], fill=(255, 255, 255))
    d.text((x0 + 10, y0 + 6), "\u00a3100m+", font=F(SANS_B, 10), fill=INK)


ART_FNS = {"ant": art_ant, "cop": art_cop, "exam": art_exam,
           "storm": art_storm, "bridge": art_bridge,
           "rocket": art_rocket, "tank": art_tank,
           "senate": art_senate, "dow": art_dow, "navy": art_navy}
LEAD_FNS = [art_summit, art_court, art_gta]

# ---------------- map ----------------

def draw_map(d, x0, y0, x1, y1):
    """Simplified world map: sea, rough continents, numbered pins."""
    w, h = x1 - x0, y1 - y0

    def px(fx):
        return x0 + w * fx

    def py(fy):
        return y0 + h * fy

    vgrad(d, (x0, y0, x1, y1), (200, 220, 230), (212, 226, 234))
    polys = [
        [(0.02, 0.30), (0.10, 0.10), (0.26, 0.12), (0.30, 0.28),
         (0.22, 0.44), (0.14, 0.52), (0.06, 0.44)],
        [(0.24, 0.54), (0.33, 0.54), (0.34, 0.72), (0.28, 0.94),
         (0.23, 0.72)],
        [(0.46, 0.12), (0.56, 0.10), (0.58, 0.26), (0.50, 0.34),
         (0.45, 0.26)],
        [(0.47, 0.38), (0.60, 0.36), (0.62, 0.56), (0.56, 0.72),
         (0.50, 0.58)],
        [(0.58, 0.10), (0.94, 0.08), (0.96, 0.34), (0.86, 0.52),
         (0.72, 0.48), (0.66, 0.30), (0.58, 0.26)],
    ]
    for p in polys:
        pts = [(px(a), py(b)) for a, b in p]
        d.polygon(pts, fill=LAND, outline=(196, 170, 116))
    d.ellipse([px(0.32), py(0.04), px(0.39), py(0.14)], fill=LAND,
              outline=(196, 170, 116))
    d.ellipse([px(0.80), py(0.64), px(0.93), py(0.78)], fill=LAND,
              outline=(196, 170, 116))
    for i, (fx, fy) in enumerate(PIN_SPOTS, start=1):
        cx, cy = px(fx), py(fy)
        d.ellipse([cx - 6, cy - 5, cx + 8, cy + 8], fill=(150, 150, 140))
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        nf = F(SANS_B, 8)
        label = str(i)
        lw = tw(d, label, nf)
        d.text((cx - lw / 2, cy - 5), label, font=nf, fill=(255, 255, 255))


# ---------------- page layout (v15: 7 featured cards, all painterly, 45 stories) ----------------

def lead_card(d, x, y, w, art_h, item):
    n, kick, tagname, head, body = item
    drop_shadow(d, (x, y, x + w, y + art_h))
    LEAD_FNS[n - 1](d, x, y, x + w, y + art_h)
    y += art_h + 6
    tag_bg = GREEN if tagname == "REPORTED" else (
        AMBER if tagname == "CLAIM" else (90, 110, 140))
    kf = F(SANS_B, 10)
    d.text((x, y), "%d \u00b7 %s" % (n, kick), font=kf, fill=RED)
    chip(d, x + w - 62, y - 1, tagname, tag_bg)
    y += 17
    hf = head_font(d, head, SERIF_B, 32, 30, w)
    ls = wrap_lines(d, head, hf, w)
    assert len(ls) <= 2, "lead headline too long: %s" % head
    y = draw_lines(d, ls, x, y, hf, INK, hf.size + 2)
    bf = F(SERIF_R, 11)
    blines = wrap_lines(d, body, bf, w)
    assert len(blines) <= 2, "lead body too long: %s" % body[:40]
    y = draw_lines(d, blines, x, y + 2, bf, INK, 12)
    return y


def medium_card(d, x, y, w, art_h, item, head_big, head_small):
    n, kick, art, tagname, head, body = item
    drop_shadow(d, (x, y, x + w, y + art_h))
    ART_FNS[art](d, x, y, x + w, y + art_h)
    d.line([(x, y + art_h), (x + w, y + art_h)], fill=(90, 80, 60), width=1)
    y += art_h + 3
    tag_bg = GREEN if tagname == "REPORTED" else (
        AMBER if tagname == "CLAIM" else (90, 110, 140))
    kf = F(SANS_B, 9)
    d.text((x, y), "%d \u00b7 %s" % (n, kick), font=kf, fill=RED)
    chip(d, x + w - 56, y - 1, tagname, tag_bg, size=8)
    y += 14
    hf = head_font(d, head, SERIF_B, head_big, head_small, w)
    ls = wrap_lines(d, head, hf, w)
    assert len(ls) <= 2, "medium headline too long: %s" % head
    y = draw_lines(d, ls, x, y, hf, INK, hf.size + 2)
    bf = F(SERIF_R, 10)
    blines = wrap_lines(d, body, bf, w)
    assert len(blines) <= 2, "medium body too long: %s" % body[:40]
    y = draw_lines(d, blines, x, y + 1, bf, INK, 11)
    return y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    _CTX["img"] = img
    d = ImageDraw.Draw(img)
    x0, x1 = M, M + CW
    y = 8
    d.text((x0, y), "THE WORLD IN ONE DAY", font=F(SANS_B, 12), fill=RED)
    rf = F(SANS_B, 11)
    right = "45 STORIES \u00b7 EVERY CONTINENT \u00b7 ALL FROM THIS ONE DAY"
    d.text((x1 - tw(d, right, rf), y + 1), right, font=rf, fill=INK)
    y = 22
    mast = "Thursday 19 November 2026"
    mf = fit_font(d, mast, SERIF_B, 50, 890)
    d.text((x0, y), mast, font=mf, fill=INK)
    bx0, bx1 = x1 - 104, x1
    d.rectangle([bx0 + 1, y + 1, bx1 + 1, y + 63], fill=(220, 214, 198))
    d.rectangle([bx0, y, bx1, y + 62], outline=NAVY, width=2, fill=(255, 255, 255))
    d.text((bx0 + 10, y + 3), "NOVEMBER 2026", font=F(SANS_B, 8), fill=RED)
    d.text((bx0 + 30, y + 14), "19", font=F(SERIF_B, 30), fill=INK)
    d.text((bx0 + 24, y + 46), "THURSDAY", font=F(SANS_B, 9), fill=INK)
    y = 80
    sub = ("Trump, Xi and Putin share one table \u00b7 World Court finds "
           "genocide in Myanmar \u00b7 GTA VI ends a 13-year wait")
    d.text((x0, y), sub, font=F(SERIF_I, 15), fill=RED)
    y = 98
    widths = [250, 130, 220, 70, 190, 64, 84]
    assert sum(widths) == CW
    cx = x0
    for (label, colour, _n), seg_w in zip(REGION_BANDS, widths):
        d.rectangle([cx, y, cx + seg_w, y + 16], fill=colour)
        lf = fit_font(d, label, SANS_B, 10, seg_w - 6)
        lw = tw(d, label, lf)
        d.text((cx + (seg_w - lw) / 2, y + 3), label, font=lf,
               fill=(255, 255, 255))
        cx += seg_w
    y = 116
    cell_w = CW // 6
    for i, (num, cap) in enumerate(NUMBER_CELLS):
        cxc = x0 + i * cell_w + cell_w // 2
        nf = F(SERIF_B, 22)
        nw = tw(d, num, nf)
        d.text((cxc - nw / 2, y), num, font=nf, fill=RED)
        cf = F(SERIF_R, 10)
        cw = tw(d, cap, cf)
        d.text((cxc - cw / 2, y + 22), cap, font=cf, fill=INK)
        if i:
            d.line([(x0 + i * cell_w, y + 4), (x0 + i * cell_w, y + 35)],
                   fill=RULE, width=1)
    hline(d, x0, x1, y + 33)
    y = 154
    d.text((x0, y), "THE DAY", font=F(SANS_B, 10), fill=RED)
    d.text((x0, y + 11), "BY HOURS", font=F(SANS_B, 10), fill=RED)
    d.text((x0, y + 22), "local time", font=F(SERIF_R, 8), fill=GREY)
    cell_w = (CW - 92) // 7
    for i, (t, place, ev) in enumerate(HOUR_CELLS):
        hx = x0 + 92 + i * cell_w
        d.text((hx, y), t, font=F(SANS_B, 10), fill=RED)
        d.text((hx + 36, y), place, font=F(SANS_B, 10), fill=INK)
        d.text((hx, y + 13), ev, font=F(SERIF_R, 9), fill=INK)
    hline(d, x0, x1, y + 23)
    y = 181
    lead_w = 332
    lead_art_h = 195
    bottoms = []
    for i, item in enumerate(LEAD_ITEMS):
        lx = x0 + i * (lead_w + 6)
        bottoms.append(lead_card(d, lx, y, lead_w, lead_art_h, item))
    y = max(bottoms)
    # v15: ONE row of four BIG mediums (245px each, art 135,
    # headlines 24pt falling back to 22pt). The other six v14
    # mediums are briefs now; nothing else changes above this row.
    mid_w = 245
    mid_y = y + 4
    for c in range(4):
        item = MID_ITEMS[c]
        mx = x0 + c * (mid_w + 9)
        end = medium_card(d, mx, mid_y, mid_w, 135, item, 24, 22)
        assert end <= mid_y + 232, "medium card overflow: %s" % (item[4],)
    y = mid_y + 232

    return img, d, y


def bottom_section(d, y0):
    x0, x1 = M, M + CW
    top = y0
    map_x1 = x0 + 288
    d.text((x0, top), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=RED)
    draw_map(d, x0, top + 16, map_x1, top + 136)
    d.text((x0, top + 142), "Red pins mark the 7 featured stories.",
           font=F(SERIF_R, 8), fill=GREY)
    d.text((x0, top + 152), "Positions are approximate.",
           font=F(SERIF_R, 8), fill=GREY)
    ax0, ax1 = x0 + 296, x0 + 756
    d.text((ax0, top), "ALSO ON THURSDAY 19 NOVEMBER \u2014 38 MORE STORIES",
           font=F(SANS_B, 11), fill=RED)
    col_w = (ax1 - ax0 - 8) // 2
    bf = F(SERIF_R, 10)
    bfb = F(SANS_B, 10)
    for ci in range(2):
        cx = ax0 + ci * (col_w + 8)
        for ri in range(19):
            idx = ci * 16 + ri
            if idx >= len(BRIEF_ITEMS):
                continue
            n, place, text = BRIEF_ITEMS[idx]
            by = top + 12 + ri * 11
            d.text((cx, by), str(n), font=F(SANS_B, 9), fill=RED)
            nw = tw(d, str(n), F(SANS_B, 9))
            d.text((cx + nw + 3, by), place, font=bfb, fill=INK)
            pw = tw(d, place, bfb)
            d.text((cx + nw + 6 + pw, by), " \u2014 " + text, font=bf,
                   fill=INK)
            full = "%d %s \u2014 %s" % (n, place, text)
            assert tw(d, full, bf) <= col_w + 8, "brief too wide: %s" % full
    rx0, rx1 = x0 + 764, x1
    bw = rx1 - rx0
    by = top
    d.rectangle([rx0, by, rx1, by + 40], fill=NAVY)
    d.rectangle([rx0, by + 38, rx1, by + 40], fill=GOLD)
    d.text((rx0 + 8, by + 4), "THE VERDICT", font=F(SANS_B, 10),
           fill=(255, 255, 255))
    d.text((rx1 - 92, by + 4), "THE HAGUE \u00b7 10:00",
           font=F(SANS_B, 8), fill=GOLD)
    vf = F(SERIF_R, 10)
    draw_lines(d, ["Myanmar committed genocide, 9 to 6.",
                   "The court found it responsible."],
               rx0 + 8, by + 17, vf, (255, 255, 255), 11)
    by += 43
    d.rectangle([rx0, by, rx1, by + 62], outline=RULE, width=1,
                fill=(250, 248, 240))
    d.text((rx0 + 8, by + 4), "HOW SURE ARE WE?", font=F(SANS_B, 10),
           fill=RED)
    rows = [("REPORTED", GREEN, "confirmed by named sources"),
            ("CLAIM", AMBER, "one side says so, unverified"),
            ("FORECAST", (90, 110, 140), "poll, draft or schedule")]
    ry = by + 16
    for label, colour, note in rows:
        w = chip(d, rx0 + 8, ry, label, colour, size=8)
        d.text((rx0 + 8 + w + 6, ry + 3), note, font=F(SERIF_R, 9),
               fill=INK)
        ry += 14
    by += 65
    d.rectangle([rx0, by, rx1, by + 62], outline=RULE, width=1,
                fill=(250, 248, 240))
    d.text((rx0 + 8, by + 4), "MARKETS & MONEY", font=F(SANS_B, 10),
           fill=RED)
    cells = [("$83", "IPO PRICE, WED"), ("$81.3bn", "LARGEST IPO EVER"),
             ("4.9%", "JOBLESS FROM 4.7%"), ("$97.17", "ANT CLOSE, +17%")]
    for i, (val, cap) in enumerate(cells):
        ccx = rx0 + 8 + (i % 2) * (bw // 2)
        ccy = by + 16 + (i // 2) * 22
        d.text((ccx, ccy), val, font=F(SANS_B, 12), fill=RED)
        d.text((ccx, ccy + 12), cap, font=F(SERIF_R, 8), fill=INK)
    return top + 221


def finish(img, d, y):
    x0, x1 = M, M + CW
    y += 6
    df = F(SERIF_R, 9)
    ls = wrap_lines(d, DATE_CHECK, df, CW - 16)
    box_h = len(ls) * 11 + 4
    d.rectangle([x0, y, x1, y + box_h], outline=RED, width=1)
    draw_lines(d, ls, x0 + 8, y + 2, df, INK, 11)
    y += box_h + 5
    sf = F(SERIF_R, 8)
    assert tw(d, FOOT_LINE, sf) <= CW
    d.text((x0, y), FOOT_LINE, font=sf, fill=GREY)
    y += 12
    assert y <= H - M, "page overflow: %d" % y
    img.save("entry.png", optimize=True)
    raw = open("entry.png", "rb").read()
    assert len(raw) <= 1048576, "over 1 MiB: %d" % len(raw)
    probe = Image.open("entry.png")
    assert probe.size == (1024, 1024)
    print("entry.png %d bytes sha256 %s" % (
        len(raw), hashlib.sha256(raw).hexdigest()))


def main():
    # v14: 45 stories, every id 1-45 exactly once (3 leads + 10
    # mediums + 32 briefs). Featured ids: 1,2,3,4,5,6,8,9,10,11,
    # 40,41,42. Brief ids: all the rest.
    expected = list(range(1, 46))
    ids = ([n for n, _, _, _, _ in LEAD_ITEMS]
           + [n for n, _, _, _, _, _ in MID_ITEMS]
           + [n for n, _, _ in BRIEF_ITEMS])
    assert sorted(ids) == expected, "story ids: %s" % (ids,)
    assert len(ids) == 45, "story count: %d" % len(ids)
    img, d, y = build()
    y = bottom_section(d, y + 2)
    finish(img, d, y)


if __name__ == "__main__":
    main()
