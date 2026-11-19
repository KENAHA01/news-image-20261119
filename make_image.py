"""Draw the 19 November 2026 world-news front page (builder only).

Runs on the builder machine with Pillow. The graded entrypoint is
main.py, which only copies the entry.png this script draws, because
the grading sandbox has no Pillow and no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (242, 236, 220)
NAVY = (22, 38, 76)
INK = (18, 18, 18)
GREY = (74, 74, 74)
WHITE = (255, 255, 255)
CARD = (255, 253, 247)

# Region colours, one per region, reused in the strip and card bars.
REGION_COLOR = {
    "Europe": (36, 86, 166),
    "Middle East": (179, 39, 30),
    "Asia": (201, 106, 18),
    "Africa": (14, 122, 107),
    "Americas": (46, 125, 50),
    "Oceania": (15, 127, 140),
    "World": (90, 90, 90),
}

# (title, one-line body, region) in page order. 40 stories.
STORIES = [
    ("THREE LEADERS MEET", "First US-China-Russia talks.", "Asia"),
    ("IRAN HITS GULF AGAIN", "Kuwait, Bahrain attacked.", "Middle East"),
    ("MYANMAR GUILTY", "World court rules 9-6.", "Asia"),
    ("PLANE CRASH KILLS 19", "All aboard dead in Siberia.", "Asia"),
    ("KERCH RAIL HALTED", "Third strike in four days.", "Europe"),
    ("HOUTHI HITS RIYADH TOWER", "Saudi fund tower damaged.", "Middle East"),
    ("ISRAEL PUSHES INTO GAZA", "Tanks cross ceasefire line.", "Middle East"),
    ("NASSER HOSPITAL HIT", "Six dead, surgeon among them.", "Middle East"),
    ("TANKER STRUCK IN STRAIT", "Mine blast reported.", "Middle East"),
    ("HERZOG MEETS KAHANA", "New speaker's first day.", "Middle East"),
    ("GAZA AID SCORE 4 OF 26", "Peace plan falls short.", "Middle East"),
    ("UAE GROWTH 7.3%", "IMF sees strong 2027.", "Middle East"),
    ("APEC ADOPTS OUTLOOK", "Trade, data and AI pact set.", "Asia"),
    ("CYCLONE AKVAN WEAKENS", "Landfall Friday, winds 100.", "Asia"),
    ("HAN FREED BY TOP COURT", "15-year term overturned.", "Asia"),
    ("MONGOLIA LEADER QUITS", "Resigns over rail claims.", "Asia"),
    ("INDONESIA PASSES BILL", "Asset seizures now law.", "Asia"),
    ("BANGLADESH HOME TORCHED", "Yunus house set ablaze.", "Asia"),
    ("SINDHU BACK IN TOP 5", "Lakshya Sen joins top 10.", "Asia"),
    ("SERBIA PICKS NEW SPEAKER", "Student list wins 140-97.", "Europe"),
    ("GREENLAND DEAL PASSES", "Denmark votes 109-0.", "Europe"),
    ("UK CONFIRMS APPLE DEMAND", "Tribunal backs data order.", "Europe"),
    ("ROYAL MAIL NAMES NEW CHIEF", "Ablin takes over in January.", "Europe"),
    ("BERLIN HOSTS UKRAINE ALLIES", "Coalition of willing meets.", "Europe"),
    ("TIAFOE KEEPS HOPE ALIVE", "Beats Cobolli 7-6, 6-0.", "Europe"),
    ("SHELTON WINS IN TURIN", "Beats Jodar 2-0.", "Europe"),
    ("SOMALIA EXPELS UAE ENVOY", "Envoy out in 72 hours.", "Africa"),
    ("SENEGAL PASSES BUDGET", "President rules by decree.", "Africa"),
    ("JEPCHIRCHIR BANNED", "Marathon star out 3 years.", "Africa"),
    ("BADME CLASHES REPORTED", "Eritrea denies fighting.", "Africa"),
    ("TRUMP OPPOSES AI RULES", "US rejects global AI curbs.", "Americas"),
    ("US OFFERS MANILA $2BN+", "Loan package pursued.", "Americas"),
    ("GUYANA ROW DENIED", "US: policy unchanged.", "Americas"),
    ("XAVIER THREATENS NASSAU", "Storm alert for Bahamas.", "Americas"),
    ("TRUMP: IRAN EYES BIO ARMS", "Claims chemical, bio work.", "Americas"),
    ("FIJI DECLARES DISASTER", "El Nino drought bites.", "Oceania"),
    ("NZ 243 FOR 5", "Nicholls hits a century.", "Oceania"),
    ("PEW: MUSLIMS TOP BY 2035", "Largest faith group soon.", "World"),
    ("589M KIDS IN WAR ZONES", "Nearly one in four.", "World"),
    ("NASA SETS LAUNCH COVER", "Northrop cargo flight set.", "World"),
]

NUMBERS = [
    ("90 MIN", "Trilateral talks last"),
    ("9-6", "Court votes genocide"),
    ("19 DEAD", "Plane crash toll"),
    ("589M", "Kids in war zones"),
    ("$2BN+", "Manila loan sought"),
    ("109-0", "Greenland deal votes"),
]

DATE_CHECK = ("DATE CHECK - Not from 19 Nov: ICE contempt ruling + TPS filing "
              "(18 Nov); Voyager 1 light-day + Anthropic debut (18 Nov); "
              "Kahana elected speaker (17 Nov).")
SOURCES = ("Sources: Reuters, AP, USA Today, The Times, DPA, BBC, IAEA, IMF, "
           "Pew, Save the Children, ATP.")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def fit(name, text, max_w, start, minimum):
    """Largest size from start down to minimum that fits max_w in one line."""
    size = start
    while size > minimum:
        f = font(name, size)
        if f.getbbox(text)[2] <= max_w:
            return f, size
        size -= 1
    return font(name, minimum), minimum


def text_w(f, text):
    box = f.getbbox(text)
    return box[2] - box[0]


def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead: navy band, big day number, title, subtitle.
    d.rectangle([6, 6, 1018, 110], fill=NAVY)
    d.text((22, 12), "19", font=font("BebasNeue-Regular.ttf", 96),
           fill=WHITE, anchor="lt")
    title_f = font("BebasNeue-Regular.ttf", 62)
    d.text((584, 16), "THE WORLD IN ONE PAGE", font=title_f,
           fill=WHITE, anchor="mt")
    sub_f = font("WorkSans-600.woff", 15)
    d.text((584, 84), "THURSDAY 19 NOVEMBER 2026  -  40 STORIES  -  7 REGIONS",
           font=sub_f, fill=WHITE, anchor="mt")

    # Region strip, each region in its own colour.
    counts = {}
    for _, _, region in STORIES:
        counts[region] = counts.get(region, 0) + 1
    order = ["Europe", "Middle East", "Asia", "Africa",
             "Americas", "Oceania", "World"]
    parts = []
    strip_f = font("WorkSans-600.woff", 15)
    for region in order:
        parts.append((region.upper() + " " + str(counts[region]),
                      REGION_COLOR[region]))
    sep_w = text_w(strip_f, "  -  ")
    total = sum(text_w(strip_f, t) for t, _ in parts) + sep_w * (len(parts) - 1)
    x = (W - total) // 2
    for i, (t, color) in enumerate(parts):
        d.text((x, 116), t, font=strip_f, fill=color, anchor="lt")
        x += text_w(strip_f, t)
        if i < len(parts) - 1:
            d.text((x, 116), "  -  ", font=strip_f, fill=GREY, anchor="lt")
            x += sep_w

    # By-the-numbers strip: six cells, big figure over a small label.
    d.rectangle([6, 140, 1018, 196], fill=WHITE, outline=INK, width=2)
    cell_w = 1012 / 6
    num_f = font("Montserrat-Bold.ttf", 30)
    lab_f = font("WorkSans-600.woff", 12)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 6 + cell_w * i + cell_w / 2
        d.text((cx, 146), num, font=num_f, fill=NAVY, anchor="mt")
        d.text((cx, 180), lab, font=lab_f, fill=GREY, anchor="mt")
        if i:
            sx = 6 + cell_w * i
            d.line([(sx, 146), (sx, 192)], fill=(200, 200, 200), width=1)

    # Story grid: 4 columns by 10 rows, no pictures, title + one body line.
    x0, y0 = 7, 202
    cw, chh, gx, gy = 248, 72, 6, 4
    report = []
    for idx, (title, body, region) in enumerate(STORIES):
        col, row = idx % 4, idx // 4
        cx = x0 + col * (cw + gx)
        cy = y0 + row * (chh + gy)
        d.rectangle([cx, cy, cx + cw, cy + chh], fill=CARD, outline=INK, width=2)
        d.rectangle([cx + 2, cy + 2, cx + cw - 2, cy + 8],
                    fill=REGION_COLOR[region])
        tf, ts = fit("BebasNeue-Regular.ttf", title, cw - 16, 26, 18)
        d.text((cx + 8, cy + 12), title, font=tf, fill=INK, anchor="lt")
        bf, bs = fit("WorkSans-600.woff", body, cw - 16, 16, 11)
        d.text((cx + 8, cy + 43), body, font=bf, fill=INK, anchor="lt")
        if ts < 26 or bs < 16:
            report.append((idx + 1, title, ts, bs))

    # Footer: date-check bar, then the source line.
    d.rectangle([6, 962, 1018, 986], fill=WHITE, outline=INK, width=1)
    d.rectangle([6, 962, 10, 986], fill=(179, 39, 30))
    dc_f, _ = fit("WorkSans-600.woff", DATE_CHECK, 990, 12, 10)
    d.text((16, 966), DATE_CHECK, font=dc_f, fill=INK, anchor="lt")
    src_f = font("WorkSans-400.woff", 11)
    d.text((W // 2, 994), SOURCES, font=src_f, fill=GREY, anchor="mt")

    img.save(OUT, format="PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    print("stories:", len(STORIES))
    for r in report:
        print("shrunk card", r)


if __name__ == "__main__":
    draw()
