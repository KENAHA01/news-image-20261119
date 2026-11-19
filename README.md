# Sum up 19 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)

Entry for the [make.fun bounty news-image-20261119](https://make.fun/bounty/news-image-20261119):
a program that draws one newspaper front-page image summing up Thursday
19 November 2026 world news to `/output/entry.png`.

The front page carries 40 verified stories in a 4-by-10 grid of compact
cards, no illustrations: each card has a colour bar for its region, a
Bebas headline on one line and a Work Sans summary on one line. Regions:
Europe 8, Middle East 8, Asia 10, Africa 4, Americas 5, Oceania 2,
World 3. The day's biggest stories are the first three-way summit of
Trump, Xi and Putin in Shenzhen, Iran widening its attacks on Kuwait
and Bahrain, and the world court ruling Myanmar committed genocide
against the Rohingya. A DATE CHECK strip names the near-miss stories
left out because they belong to 17 or 18 November. Every story was
checked against its source page for the 19 November date; claims are
shown as claims (Trump on Iran, the Badme clash reports). See
`sources.json` for one source and note per story.

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
