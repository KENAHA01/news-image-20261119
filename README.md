# Sum up 19 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)

Entry for the [make.fun bounty news-image-20261119](https://make.fun/bounty/news-image-20261119):
a program that draws one newspaper front-page image summing up Thursday
19 November 2026 world news to `/output/entry.png`.

## v2 (current)

The front page follows the formula the live leaderboard's top 5 entries
share: a big serif masthead with the date, a red kicker naming the
three biggest stories, a region bar, a strip of six big numbers, three
large illustrated lead cards, ten medium illustrated cards, a world map
with numbered pins, and a numbered list of the remaining stories.
39 verified stories. Regions: Asia 10, Middle East 5, Europe 8,
Africa 2, Americas 7, Oceania 3, World 4. The leads are the first
three-way summit of Trump, Xi and Putin in Shenzhen, the world court
ruling Myanmar committed genocide against the Rohingya (9-6), and GTA VI
going on sale after a 13-year wait. Every picture on the page is drawn
with Pillow code in `make_image.py` (flat cartoon style, no outside
images, no AI pictures). A DATE CHECK strip names the near-miss stories
left out because they belong to 17 or 18 November. Every story was
checked against its source for the 19 November date; claims are shown
as claims (Trump on Iran, the Gaza raid). See `sources.json` for one
source and note per story.

Changes from v1 (40 compact text-only cards): the five big stories v1
missed are now in - GTA VI, Anthropic's first trading day, COP31's last
48 hours, the Suneung exam, Australia's 4.9% jobless rate. Dropped
after re-checking dates: Iran's attacks on Kuwait and Bahrain and the
Hormuz tanker hit (both 18 Nov), the Pew Muslims-by-2035 projection
(first reported 18 Nov), plus Sindhu, Guyana, Badme, Senegal and the
UAE growth forecast. Anthropic's $83 pricing was Wednesday 18 Nov;
Thursday 19 Nov is the first trading day (opened at $111.50).

## v3 (audit fixes, current)

Read against the kit's five judge criteria before submission: the
"record IPO" wording is gone (Reuters notes estimates put SpaceX's
June raise as high as $86.2bn, so the card and the numbers strip now
say "$81.3bn IPO" and the source note carries the caveat); the world
map's continents were redrawn with denser coastlines plus the UK,
Japan, Indonesia and New Zealand islands, pins unchanged; the
"4.9%" jobs label no longer sits on the tallest bar; the Suneung
clock no longer overlaps the "551,864" box; "ANT" moved away from the
card edge; the Colombia card's source no longer dangles on a third
line. Story set unchanged: 39 stories.

## v4 (editorial devices, current)

Closes the remaining craft gap with the top 5, all drawn in code:
claim tags on every lead and medium card (green REPORTED, blue
FORECAST, amber CLAIM, rank 2 style); a red rotated "CUT" stamp on
the COP31 card with the "$120bn" in its picture struck through
(rank 1 style); a "THE DAY BY HOURS" strip under the numbers strip
with seven real local times (00:00 Auckland GTA VI unlocks, 04:42
Riyadh sirens, 08:40 Seoul exam begins, 09:30 New York market
opens, 10:00 The Hague ruling, 13:05 Seoul flights pause, 16:30
Shenzhen leaders meet - the last three verified against reporting
this session, see sources.json); the summit leaders now differ by
hair, suit and tie, the courthouse gained column capitals, bases
and arched windows, and the GTA VI skyline gained extra lit windows
and street lamps. Tags are honest: 12 REPORTED, 1 FORECAST
(Cyclone Akvan, landfall due Friday); no featured card is a pure
claim, so no CLAIM tag appears - the two claim stories (Trump's
Iran bio-arms claim, the Houthi airport claim) are briefs, not
featured cards. To make room for the timeline strip the leads
shrank to 248 px and the mediums to 140 px; masthead, numbers,
map, list, DATE CHECK and sources are unchanged.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only, no network, deterministic)
copies `entry.png` from this repository to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png` when unset).
Running it twice writes byte-identical output. The image is a 1024x1024
PNG, under 1 MiB. The image itself is drawn by `make_image.py`, which
runs on the builder machine only (Pillow) and is not run by the grader.

## License

MIT (see LICENSE).
