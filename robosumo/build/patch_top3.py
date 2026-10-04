"""Final layout pass on fig_top_view: wider canvas, legend clear of the drawing."""
import re

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
src = open(PATH, encoding="utf-8").read()
orig = src

reps = [
    # wider canvas, robot keeps its place
    ("    W, H = 1800, 1280\n    im, dr = canvas(W, H)\n    title_block(dr, W, "
     "\"\u0420\u0438\u0441. 2.",
     "    W, H = 2020, 1300\n    im, dr = canvas(W, H)\n    title_block(dr, W, "
     "\"\u0420\u0438\u0441. 2."),
    # legend and numbers panel move right, clear of the 200 mm body
    ("    lx, ly = 1330, 220", "    lx, ly = 1420, 230"),
    ("    px, py = 1330, 650", "    px, py = 1420, 660"),
    # sensor callout: place it just under the blade, left of centre
    ('    text(dr, (ox + L + 26, oy - 40), "\u0441\u0435\u043d\u0441\u043e\u0440\u0438 \u043d\u0430 \u043f\u043b\u0430\u043d\u0446\u0438\u0440\u0456 \u043a\u043b\u0438\u043d\u0430", 14, "semi", AMBER, anchor="lm")',
     '    text(dr, (ox + 6, oy - 30), "\u2191 \u0441\u0435\u043d\u0441\u043e\u0440\u0438 \u043d\u0430 \u043f\u043b\u0430\u043d\u0446\u0438\u0440\u0456 \u043a\u043b\u0438\u043d\u0430", 14, "semi", AMBER, anchor="lm")'),
    # shield the front-arrow label from clipping
    ("    arrow(dr, (ox - 120, oy + Wd / 2), (ox - 44, oy + Wd / 2), ACCENT2, 4, 15)\n"
     "    text(dr, (ox - 128, oy + Wd / 2), \"\u041f\u0415\u0420\u0415\u0414\", 20, \"bold\", ACCENT2, anchor=\"rm\")",
     "    arrow(dr, (ox - 130, oy + Wd / 2), (ox - 50, oy + Wd / 2), ACCENT2, 4, 15)\n"
     "    text(dr, (ox - 140, oy + Wd / 2), \"\u041f\u0415\u0420\u0415\u0414\", 20, \"bold\", ACCENT2, anchor=\"rm\")"),
]

for a, b in reps:
    if a not in src:
        raise SystemExit("PATTERN NOT FOUND:\n" + a[:110])
    src = src.replace(a, b)

open(PATH, "w", encoding="utf-8").write(src)
print("patched,", len(src) - len(orig), "chars delta")
