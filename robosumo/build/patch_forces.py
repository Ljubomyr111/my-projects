"""Line-oriented update of fig_forces to the confirmed 3 kg numbers."""

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
lines = open(PATH, encoding="utf-8").read().split("\n")
out, changed = [], []

for ln in lines:
    if 'title_block(dr, W, "Рис. 4.' in ln:
        ln = ('    title_block(dr, W, "Рис. 4. Сили на магнітній арені — вид збоку (3 кг)",')
        changed.append("title")
    elif 'Притискна сила магнітів множить силу тертя' in ln:
        ln = ('                "Магніти множать силу тертя. Але момент мотора вирішує, '
              'скільки з неї можна використати.")')
        changed.append("subtitle")
    elif '"Робот 1 кг, μ = 0,7 (гума / сталь):"' in ln:
        ln = '    text(dr, (px + 22, py + 108), "Робот 3 кг, μ = 0,7 (гума / сталь):", 18, "semi")'
        changed.append("header")
    elif '"без магнітів:    0,7 · 9,8  =  6,9 Н"' in ln:
        ln = '        ("без магнітів:      0,7 · 29,4 =  20,6 Н", INK),'
        changed.append("row1")
    elif '"з 13 Н магнітів:  0,7 · 22,8 = 16,0 Н"' in ln:
        ln = '        ("з 15 кгс (147 Н):  0,7 · 176,6 = 123,6 Н", GREEN),'
        changed.append("row2")
    elif '"приріст тяги ×2,3 — без грама ваги"' in ln:
        ln = '        ("приріст тяги ×6,0 — без грама ваги", GREEN),'
        changed.append("row3")
    elif '"Робот 3 кг з 30 Н магнітів:"' in ln:
        ln = '    text(dr, (px + 22, py + 258), "Те саме при μ = 1,0 (оптимістично):", 18, "semi")'
        changed.append("header2")
    elif '"без магнітів:    0,7 · 29,4 = 20,6 Н"' in ln:
        ln = '        ("без магнітів:      1,0 · 29,4 =  29,4 Н", INK),'
        changed.append("row4")
    elif '"з 30 Н магнітів:  0,7 · 59,4 = 41,6 Н"' in ln:
        ln = '        ("з 15 кгс (147 Н):  1,0 · 176,6 = 176,6 Н", GREEN),'
        changed.append("row5")
    elif '"Висновок: магніти — «безкоштовна» вага."' in ln:
        ln = '    text(dr, (px + 22, py + 376), "Висновок: магніти — майже безкоштовна вага.", 18, "bold", ACCENT2)'
        changed.append("concl")
    elif '"Але момент на валу росте так само:"' in ln:
        ln = '    text(dr, (px + 22, py + 410), "Але момент на валу росте так само, а 37D", 17, "reg")'
        changed.append("c2")
    elif '"M = F · r, тому колесо Ø50 вимагає"' in ln:
        ln = '    text(dr, (px + 22, py + 436), "тримає лише 10 кг·см безперервно. Тому", 17, "reg")'
        changed.append("c3")
    elif '"≈1,25 × більше моменту, ніж Ø40."' in ln:
        ln = '    text(dr, (px + 22, py + 462), "зайві магніти не додають сили штовхання.", 17, "semi", ACCENT)'
        changed.append("c4")
    elif '"Хитрість: магніти ставимо так, щоб"' in ln:
        ln = '    text(dr, (px + 22, py + 512), "Головне обмеження — не зчеплення,", 17, "semi", ACCENT2)'
        changed.append("c5")
    elif '"притиск припадав на колеса й клин,"' in ln:
        ln = '    text(dr, (px + 22, py + 538), "а момент мотора. Став магніти під колеса", 17, "reg")'
        changed.append("c6")
    elif '"а не на центр днища — центр не тягне."' in ln:
        ln = '    text(dr, (px + 22, py + 564), "й клин — тоді вся тяга йде в бій,", 17, "reg")'
        changed.append("c7")
    elif '"Кожен +1 Н притиску ≈ +0,7 Н тяги."' in ln:
        ln = '    text(dr, (px + 22, py + 590), "а не в марне притискання днища.", 17, "reg")'
        changed.append("c8")
    out.append(ln)

open(PATH, "w", encoding="utf-8").write("\n".join(out))
print("changed:", ", ".join(changed))
