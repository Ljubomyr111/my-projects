import io, sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

path = r"C:\Users\Lenovo\Downloads\Лабораторна робота 4.docx"
d = Document(path)
out = io.StringIO()

body = d.element.body
ti = pi = 0
for child in body.iterchildren():
    if child.tag == qn('w:p'):
        p = Paragraph(child, d)
        out.write(f"[P{pi}][{p.style.name}] {p.text}\n")
        pi += 1
    elif child.tag == qn('w:tbl'):
        t = Table(child, d)
        out.write(f"[TABLE {ti}] rows={len(t.rows)} cols={len(t.columns)}\n")
        for r_i, row in enumerate(t.rows):
            cells = [c.text.replace("\n", " | ") for c in row.cells]
            out.write(f"   R{r_i}: {cells}\n")
        ti += 1

with open("lab4_text.txt", "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("ok")
