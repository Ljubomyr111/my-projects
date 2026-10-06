import os
from pypdf import PdfReader

pdfs = [
    r"C:\Users\Lenovo\Downloads\P4 - Reading exercises (Big-O).pdf",
    r"C:\Users\Lenovo\Downloads\P4 - Git tips.pdf",
    r"C:\Users\Lenovo\Downloads\L4 - Algorithmic complexity. Big-O notation.pdf",
    r"C:\Users\Lenovo\Downloads\Group Project - terms.pdf",
    r"C:\Users\Lenovo\Downloads\P5 - Static arrays and strings.pdf",
]

out_dir = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\_pdf_text"
os.makedirs(out_dir, exist_ok=True)

for p in pdfs:
    name = os.path.basename(p)
    try:
        r = PdfReader(p)
        text = "\n".join((page.extract_text() or "") for page in r.pages)
        out = os.path.join(out_dir, name + ".txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK {name}: {len(text)} chars, {len(r.pages)} pages")
    except Exception as e:
        print(f"FAIL {name}: {e!r}")
