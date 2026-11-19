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
