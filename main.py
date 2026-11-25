#!/usr/bin/env python3
"""Entry point for the news-image-20261125 bounty.

The front page is drawn ahead of time by render.py and ships in this
repository as news.png. This program only copies that file to
/output/entry.png, so it needs no network and both runs write the
same bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "news.png")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(src, os.path.join("/output", "entry.png"))


if __name__ == "__main__":
    main()
