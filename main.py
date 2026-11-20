"""Entrypoint for news-image-20261119 v15 (stdlib only).

Runs make_image.py in this folder, which rebuilds entry.png from
the generated illustration assets (assets/*.png) plus Pillow text,
deterministically, then copies entry.png to $MAKEFUN_OUTPUT_DIR.
"""

import hashlib
import os
import shutil
import subprocess
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, "make_image.py"], cwd=here, check=True)
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        sys.exit("MAKEFUN_OUTPUT_DIR is not set")
    dst = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    raw = open(dst, "rb").read()
    print("copied entry.png to %s" % dst)
    print("entry.png %d bytes sha256 %s" % (
        len(raw), hashlib.sha256(raw).hexdigest()))


if __name__ == "__main__":
    main()
