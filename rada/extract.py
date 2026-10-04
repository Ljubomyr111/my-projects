import sys, os
from pypdf import PdfReader
d = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\rada"
for name in ["dstu4069","tuu","dstu2368","research13024","research_obmez"]:
    p = os.path.join(d, name + ".pdf")
    try:
        r = PdfReader(p)
        txt = "\n".join((pg.extract_text() or "") for pg in r.pages)
        open(os.path.join(d, name + ".txt"), "w", encoding="utf-8").write(txt)
        print(name, "pages=", len(r.pages), "chars=", len(txt))
    except Exception as e:
        print(name, "ERR", e)
