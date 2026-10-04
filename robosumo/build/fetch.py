"""Fetch a URL and dump cleaned readable text to stdout (works around PDF/doc content types)."""
import ssl, urllib.request, sys, re, io, os

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def raw(url, timeout=45):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read(), r.headers.get("Content-Type", "")

def strip_html(data):
    try:
        txt = data.decode("utf-8", "replace")
    except Exception:
        return ""
    txt = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", txt)
    txt = re.sub(r"(?is)<!--.*?-->", " ", txt)
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</tr>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    import html as _h
    txt = _h.unescape(txt)
    txt = re.sub(r"[ \t\xa0]+", " ", txt)
    txt = re.sub(r"\n\s*\n\s*\n+", "\n\n", txt)
    lines = [l.strip() for l in txt.split("\n")]
    return "\n".join(l for l in lines if l)

def pdf_text(data):
    try:
        from pypdf import PdfReader
    except Exception as e:
        return f"[pypdf missing: {e}]"
    try:
        r = PdfReader(io.BytesIO(data))
        out = []
        for i, p in enumerate(r.pages, 1):
            t = p.extract_text() or ""
            out.append(f"===== PAGE {i} ({len(p.images)} images) =====\n{t}")
        return "\n".join(out)
    except Exception as e:
        return f"[pdf parse failed: {e}]"

def grab(url):
    """Return cleaned text for a URL, never raising."""
    try:
        data, ct = raw(url)
    except Exception as e:
        return f"[FETCH FAIL {type(e).__name__}: {e}]"
    if "pdf" in ct.lower() or data[:5] == b"%PDF-":
        return f"[content-type {ct}, {len(data)} bytes -> pdf]\n" + pdf_text(data)
    return f"[content-type {ct}, {len(data)} bytes -> html]\n" + strip_html(data)


def main():
    # usage: fetch.py OUT.txt URL [URL ...]
    dest = sys.argv[1]
    urls = sys.argv[2:]
    chunks = []
    for url in urls:
        body = grab(url)
        chunks.append(f"\n########## {url} ##########\n{body}")
        # console echo, ascii-safe so a cp1251 console cannot kill the run
        print(f"OK {url} -> {len(body)} chars".encode("ascii", "replace").decode("ascii"))
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("".join(chunks))
    print(f"WROTE {dest} ({sum(len(c) for c in chunks)} chars)")

if __name__ == "__main__":
    main()
