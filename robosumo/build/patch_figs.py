"""Update fig_forces and fig_wiring for the confirmed 3 kg / 4WD / 6S design."""

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
src = open(PATH, encoding="utf-8").read()


def sub(old, new, label):
    global src
    if old not in src:
        raise SystemExit("MISSING PATTERN: " + label)
    src = src.replace(old, new, 1)
    print("ok:", label)


# ------------------------------------------------------------------ fig_wiring
sub(
    'title_block(dr, W, "Рис. 5. Електрична схема — блок-діаграма",\n'
    '                "Nano + 2 × BTS7960 + 3S LiPo. Спільна земля обов'язкова.")',
    'title_block(dr, W, "Рис. 5. Електрична схема — 4WD, 6S",\n'
    '                "Nano + 4 × BTS7960 + 6S LiPo (22,2 В). Спільна земля обов'язкова, '
    'радіатори на драйверах.")',
    "wiring title")

sub(
    '    block(60, 300, 200, 130, "3S LiPo", "11,1 В · 1000 мА·год · 25C",\n'
    '          fill=(224, 232, 248), outline=ACCENT2)',
    '    block(60, 300, 200, 130, "6S LiPo", "22,2 В · 2200 мА·год · 30C",\n'
    '          fill=(224, 232, 248), outline=ACCENT2)',
    "wiring battery")

sub(
    '    block(560, 520, 260, 110, "BTS7960 #1", "43 А · 5,5–27 В", fill=(250, 232, 232), outline=ACCENT, tsize=19)\n'
    '    block(560, 700, 260, 110, "BTS7960 #2", "43 А · 5,5–27 В", fill=(250, 232, 232), outline=ACCENT, tsize=19)\n'
    '    block(960, 520, 190, 110, "Мотор M1", "37D 30:1", fill=(236, 236, 240), tsize=19)\n'
    '    block(960, 700, 190, 110, "Мотор M2", "37D 30:1", fill=(236, 236, 240), tsize=19)',
    '    block(560, 500, 210, 95, "BTS7960 × 2", "мотори 1 і 2", fill=(250, 232, 232), outline=ACCENT, tsize=16)\n'
    '    block(560, 630, 210, 95, "BTS7960 × 2", "мотори 3 і 4", fill=(250, 232, 232), outline=ACCENT, tsize=16)\n'
    '    block(880, 500, 200, 95, "Мотори 1–2", "37D 24 В 100:1", fill=(236, 236, 240), tsize=15)\n'
    '    block(880, 630, 200, 95, "Мотори 3–4", "37D 24 В 100:1", fill=(236, 236, 240), tsize=15)',
    "wiring drivers")

sub(
    '    block(560, 880, 260, 110, "QTR-8A", "8 × IR · аналог", fill=(250, 246, 224), outline=AMBER, tsize=19)',
    '    block(560, 800, 260, 95, "QTR-8A + INA226", "8 × IR + струм моторів", '
    'fill=(250, 246, 224), outline=AMBER, tsize=16)',
    "wiring sensors")

open(PATH, "w", encoding="utf-8").write(src)
print("\nwritten")
