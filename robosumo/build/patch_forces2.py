"""Fix the on-diagram force arrow labels in fig_forces for a 3 kg robot."""

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
lines = open(PATH, encoding="utf-8").read().split("\n")
out, changed = [], []

for ln in lines:
    if '"m·g = 9,8 Н"' in ln:
        ln = '    text(dr, (bx0 + 50, by0 - 82), "m·g = 29,4 Н (3 кг)", 18, "bold", ACCENT2, anchor="rm")'
        changed.append("weight")
    elif '"F_магн = 10–15 Н"' in ln:
        ln = '    text(dr, (bx0 + 30, by0 + bh + 62), "F_магн = 147 Н (15 кгс)", 18, "bold", ACCENT)'
        changed.append("magnet")
    elif '"росте лінійно з притиском, без жодного грама ваги"' in ln:
        ln = ('    text(dr, (bx0 + 120, gy + 118), '
              '"але використати її можна лише на стільки, на скільки є момент", 16, "reg", MUTED)')
        changed.append("friction-note")
    # lengthen the arrows so the bigger forces read as bigger
    elif 'arrow(dr, (bx0 + 60, by0 - 70), (bx0 + 60, by0 + 90), ACCENT2, 4, 15)' in ln:
        ln = '    arrow(dr, (bx0 + 60, by0 - 110), (bx0 + 60, by0 + 90), ACCENT2, 5, 17)'
        changed.append("weight-arrow")
    elif 'arrow(dr, (bx0 + 120, by0 + bh + 26), (bx0 + 120, gy - 12), ACCENT, 4, 15)' in ln:
        ln = '    arrow(dr, (bx0 + 120, by0 + bh + 26), (bx0 + 120, gy - 12), ACCENT, 5, 17)'
        changed.append("magnet-arrow")
    elif 'arrow(dr, (bx0 + 120, gy + 70), (bx0 + 540, gy + 70), GREEN, 5, 17)' in ln:
        ln = '    arrow(dr, (bx0 + 120, gy + 70), (bx0 + 660, gy + 70), GREEN, 6, 19)'
        changed.append("friction-arrow")
    out.append(ln)

open(PATH, "w", encoding="utf-8").write("\n".join(out))
print("changed:", ", ".join(changed))
