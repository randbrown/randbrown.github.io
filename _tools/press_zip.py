#!/usr/bin/env python3
"""Rebuild assets/press/randy-brown-press-photos.zip from _data/press_gallery.json.

Bundles every gallery item marked "zip": true plus a CREDITS.txt. Jekyll can't
build zips, so the zip is committed; re-run this after changing press photos:

    python3 _tools/press_zip.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/press/randy-brown-press-photos.zip"
STAMP = (2026, 1, 1, 0, 0, 0)  # fixed timestamp so unchanged inputs give an identical zip


def main():
    items = [it for it in json.loads((ROOT / "_data/press_gallery.json").read_text()) if it.get("zip")]
    credits = ["Randy Brown: press photos", "https://randbrown.com/press/", ""]
    for it in items:
        name = Path(it["full"]).name
        credits.append(f"{name}: {it['label']}" + (f" (photo: {it['credit']})" if it.get("credit") else ""))
    credits += ["", "Please credit photographers where listed.", ""]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_STORED) as z:
        z.writestr(zipfile.ZipInfo("CREDITS.txt", STAMP), "\n".join(credits))
        for it in items:
            src = ROOT / it["full"].lstrip("/")
            z.writestr(zipfile.ZipInfo(Path(src).name, STAMP), src.read_bytes())
    print(f"wrote {OUT.relative_to(ROOT)} ({len(items)} photos)")


if __name__ == "__main__":
    main()
