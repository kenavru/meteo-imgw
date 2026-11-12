#!/usr/bin/env python3
"""Print the current video links shown in the "Produkty specjalne" section of
https://meteo.imgw.pl/ (the <video> tags inside <meteo-special-products>).

IMGW is an Angular SPA, so the page HTML has no links in it. The videos come
from a JSON API instead:

    https://meteo.imgw.pl/api/v1/products/cmm-maps?token=...&products[0]=merge
        &products[1]=inca_t2m

That returns paths like "/cmm_img/INCA_T2M_<timestamp>.mp4"; the timestamp
changes whenever IMGW republishes, so always re-fetch rather than caching.

Usage:
    python3 imgw_video.py                 # both links, one per line
    python3 imgw_video.py inca            # only the INCA (temperature) video
    python3 imgw_video.py merge           # only the MERGE video
    python3 imgw_video.py --json          # raw-ish JSON with timestamps
    python3 imgw_video.py --download-dir /tmp/opencode   # also save the files

Only the Python standard library is used.
"""

import argparse
import json
import sys
import urllib.request

API = "https://meteo.imgw.pl/api/v1/products/cmm-maps"
# Token is baked into the public app bundle (main.*.js) as apiToken.
TOKEN = "p4DXKjsYadfBV21TYrDk"
BASE = "https://meteo.imgw.pl"
PRODUCTS = ("merge", "inca_t2m")


def fetch(lang="pl", timeout=20):
    query = "&".join(f"products[{i}]={p}" for i, p in enumerate(PRODUCTS))
    url = f"{API}?token={TOKEN}&{query}&lang={lang}"
    req = urllib.request.Request(url, headers={"User-Agent": "imgw-video/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)["data"]


def download(path, out_dir, timeout=120):
    name = path.rsplit("/", 1)[-1]
    dest = f"{out_dir.rstrip('/')}/{name}"
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "imgw-video/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as fh:
        while chunk := resp.read(1 << 16):
            fh.write(chunk)
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("which", nargs="?", choices=["merge", "inca", "both"], default="both",
                    help="which video to print (default: both)")
    ap.add_argument("--json", action="store_true", help="dump JSON instead of plain URLs")
    ap.add_argument("--lang", default="pl", choices=["pl", "en"])
    ap.add_argument("--download-dir", help="also download the mp4 files here")
    args = ap.parse_args()

    data = fetch(lang=args.lang)

    wanted = PRODUCTS if args.which == "both" else (
        ("merge",) if args.which == "merge" else ("inca_t2m",))

    if args.json:
        print(json.dumps({k: {"url": BASE + data[k]["image"],
                              "modifiedTime": data[k]["modifiedTime"]}
                          for k in wanted}, indent=2))
    else:
        for key in wanted:
            print(BASE + data[key]["image"])

    if args.download_dir:
        for key in wanted:
            print("saved: " + download(data[key]["image"], args.download_dir),
                  file=sys.stderr)


if __name__ == "__main__":
    main()
