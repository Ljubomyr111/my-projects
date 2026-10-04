"""Direct, line-oriented update of fig_wiring for 4WD / 6S. No long string literals."""

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
lines = open(PATH, encoding="utf-8").read().split("\n")
out = []
changed = []

for ln in lines:
    s = ln.strip()

    # --- title -------------------------------------------------------------
    if 'title_block(dr, W, "Рис. 5.' in ln:
        ln = '    title_block(dr, W, "Рис. 5. Електрична схема — 4WD, 6S",'
        changed.append("title")
    elif 'Nano + 2 × BTS7960 + 3S LiPo' in ln:
        ln = ('                "Nano + 4 × BTS7960 + 6S LiPo (22,2 В). '
              'Спільна земля обовʼязкова, радіатори на драйверах.")')
        changed.append("subtitle")

    # --- battery -----------------------------------------------------------
    elif 'block(60, 300, 200, 130, "3S LiPo"' in ln:
        ln = '    block(60, 300, 200, 130, "6S LiPo", "22,2 В · 2200 мА·год · 30C",'
        changed.append("battery")

    # --- drivers + motors --------------------------------------------------
    elif 'block(560, 520, 260, 110, "BTS7960 #1"' in ln:
        ln = ('    block(540, 500, 230, 95, "BTS7960 × 2", "мотори 1 і 2", '
              'fill=(250, 232, 232), outline=ACCENT, tsize=16)')
        changed.append("drv1")
    elif 'block(560, 700, 260, 110, "BTS7960 #2"' in ln:
        ln = ('    block(540, 630, 230, 95, "BTS7960 × 2", "мотори 3 і 4", '
              'fill=(250, 232, 232), outline=ACCENT, tsize=16)')
        changed.append("drv2")
    elif 'block(960, 520, 190, 110, "Мотор M1"' in ln:
        ln = ('    block(860, 500, 210, 95, "Мотори 1–2", "37D 24 В 100:1", '
              'fill=(236, 236, 240), tsize=15)')
        changed.append("m1")
    elif 'block(960, 700, 190, 110, "Мотор M2"' in ln:
        ln = ('    block(860, 630, 210, 95, "Мотори 3–4", "37D 24 В 100:1", '
              'fill=(236, 236, 240), tsize=15)')
        changed.append("m2")

    # --- sensors -----------------------------------------------------------
    elif 'block(560, 880, 260, 110, "QTR-8A"' in ln:
        ln = ('    block(540, 790, 260, 95, "QTR-8A + INA226", '
              '"8 × IR + струм моторів", fill=(250, 246, 224), outline=AMBER, tsize=16)')
        changed.append("sensors")

    # --- arrows that pointed at the old block positions --------------------
    elif 'text(dr, (668, 254), "5 В", 17, "semi", GREEN)' in ln:
        ln = '    text(dr, (668, 254), "5 В", 17, "semi", GREEN)'
    elif 'arrow(dr, (820, 575), (960, 575), INK, 4, 14)' in ln:
        ln = '    arrow(dr, (770, 547), (860, 547), INK, 4, 14)'
        changed.append("arrow1")
    elif 'arrow(dr, (820, 755), (960, 755), INK, 4, 14)' in ln:
        ln = '    arrow(dr, (770, 677), (860, 677), INK, 4, 14)'
        changed.append("arrow2")

    # --- checklist line about the 5 V rail --------------------------------
    elif '("Мотори — окремо від 5 В", False)' in ln:
        ln = '        ("Мотори — окремо від 5 В", False),'

    out.append(ln)

open(PATH, "w", encoding="utf-8").write("\n".join(out))
print("changed:", ", ".join(changed))
