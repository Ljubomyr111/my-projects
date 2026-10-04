# -*- coding: utf-8 -*-
"""Estimate Word pagination for the coursework: TNR 14pt, 1.5 spacing,
A4 with 3/1/2/2 cm margins, justified body text with 1.25 cm first-line indent.
Uses the real Times New Roman font metrics through PIL."""
import os
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "text.txt")

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\times.ttf",
    r"C:\Windows\Fonts\Times New Roman.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)

PT = 14.0
TEXT_WIDTH = (21.0 - 3.0 - 1.0) * 28.3465      # cm -> pt  = 481.9
PAGE_HEIGHT = (29.7 - 2.0 - 2.0) * 28.3465     # = 728.5
LINE_H = 1.5 * (1825 + 443 + 87) / 2048 * PT   # TNR metrics @ 14pt, 1.5 spacing


def width(s, font):
    return font.getlength(s)


def break_lines(text, font, first_indent, width_limit):
    """Greedy line breaking like Word: fill each line with words up to the limit."""
    words = text.split()
    lines, cur, avail = [], "", width_limit - first_indent
    for w in words:
        cand = w if not cur else cur + " " + w
        if width(cand, font) <= avail or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
            avail = width_limit
    if cur:
        lines.append(cur)
    return lines


def main():
    font = ImageFont.truetype(FONT_PATH, int(PT))
    with open(SRC, encoding="utf-8") as f:
        raw = [l.rstrip("\n") for l in f]

    blocks = []   # (kind, lines, extra_before_pt, extra_after_pt)
    for line in raw:
        s = line.strip()
        if not s:
            continue
        if s.startswith("## "):
            blocks.append(("h2", break_lines(s[3:], font, 0, TEXT_WIDTH), 12, 12))
        elif s.startswith("# "):
            blocks.append(("h1", break_lines(s[2:], font, 0, TEXT_WIDTH), 0, 12))
        elif s.startswith("### "):
            blocks.append(("h3", break_lines(s[4:], font, 1.25 * 28.3465, TEXT_WIDTH), 0, 0))
        elif s.startswith("> "):
            blocks.append(("ref", break_lines(s[2:], font, 0, TEXT_WIDTH - 1.25 * 28.3465), 0, 0))
        else:
            blocks.append(("p", break_lines(s, font, 1.25 * 28.3465, TEXT_WIDTH), 0, 0))

    page, y, pages = 1, 0.0, []
    for kind, lines, before, after in blocks:
        y += before
        for ln in lines:
            if y + LINE_H > PAGE_HEIGHT + 0.01:
                pages.append((page, y))
                page += 1
                y = 0.0
            y += LINE_H
        y += after

    total_lines = sum(len(b[1]) for b in blocks)
    body_chars = sum(len(b[1]) for b in blocks)
    print("font:", FONT_PATH)
    print("line height pt: %.2f | lines per page: %.2f | width pt: %.1f"
          % (LINE_H, PAGE_HEIGHT / LINE_H, TEXT_WIDTH))
    print("total lines: %d" % total_lines)
    print("ESTIMATED PAGES: %d  (last page filled %.0f%%)"
          % (page, 100.0 * y / PAGE_HEIGHT))


if __name__ == "__main__":
    main()
