#!/usr/bin/env python
"""Download a PDF (or HTML) URL and dump extracted text.

Usage:
    python pdffetch.py <url> [--out FILE] [--maxpages N] [--start N]
"""
import sys
import os
import argparse
import urllib.request
import io

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/pdf,text/html,*/*",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def pdf_text(data: bytes, start: int, maxpages: int) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    n = len(reader.pages)
    out = [f"### TOTAL PAGES: {n}"]
    end = n if maxpages <= 0 else min(n, start + maxpages)
    for i in range(start, end):
        try:
            t = reader.pages[i].extract_text() or ""
        except Exception as e:  # noqa: BLE001
            t = f"[extract error: {e}]"
        out.append(f"\n===== PAGE {i+1} =====\n{t}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="")
    ap.add_argument("--maxpages", type=int, default=0)
    ap.add_argument("--start", type=int, default=0)
    a = ap.parse_args()

    data = fetch(a.url)
    head = data[:8]
    print(f"[downloaded {len(data)} bytes, magic={head!r}]")
    if head.startswith(b"%PDF"):
        text = pdf_text(data, a.start, a.maxpages)
    else:
        text = data.decode("utf-8", errors="replace")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[wrote {len(text)} chars to {a.out}]")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
