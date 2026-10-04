"""Replace the fig_top_view function in diagrams.py with the 3 kg / 4WD version."""
import io
import re

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"

NEW = '''def fig_top_view():
    W, H = 1800, 1280
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 2. Компонування 3-кг робота — вид зверху",
                "Габарит 200 × 200 мм (ліміт класу), 4WD, висота без обмежень. "
                "Сітка 20 мм. Після старту габарит дозволено збільшувати.")

    S = 5.3
    ox, oy = 180, 320
    L = Wd = 200 * S
    wheel_d = 50 * S
    wheel_w = 30 * S

    dr.rectangle([ox, oy, ox + L, oy + Wd], fill=(247, 249, 252), outline=INK, width=3)
    grid(dr, (ox, oy, ox + L, oy + Wd), 20 * S)

    # front plough
    dr.polygon([(ox - 10, oy - 52), (ox + L + 10, oy - 52), (ox + L + 10, oy), (ox - 10, oy)],
               fill=(176, 182, 192), outline=INK, width=2)
    text(dr, (ox + L / 2, oy - 26), "клин: інструментальна сталь 3 мм, кут 12°",
         16, "semi", INK, anchor="mm")

    # magnets: bar row under the blade + blocks at the four wheels
    my0 = oy + 26 * S
    for i in range(2):
        mx = ox + (22 + i * 96) * S
        rrect(dr, [mx, my0 - 20, mx + 86 * S, my0 + 20], 6,
              fill=(238, 210, 210), outline=ACCENT, width=2)
    text(dr, (ox + L / 2, my0 + 54), "2 × 20×20×5 мм N52 — суцільний ряд під клином",
         15, "semi", ACCENT, anchor="mm")

    corners = [(40, 74), (160, 74), (40, 146), (160, 146)]
    for wx, wy in corners:
        rrect(dr, [ox + (wx - 10) * S, oy + (wy - 10) * S,
                   ox + (wx + 10) * S, oy + (wy + 10) * S], 5,
              fill=(238, 210, 210), outline=ACCENT, width=2)

    # 4WD motors + wheels
    for wx, wy in corners:
        cx, cy = ox + wx * S, oy + wy * S
        rrect(dr, [cx - 15 * S, cy - 11 * S, cx + 15 * S, cy + 11 * S], 6,
              fill=(222, 228, 238), outline=ACCENT2, width=2)
        dr.rounded_rectangle([cx - wheel_w / 2, cy - wheel_d / 2,
                              cx + wheel_w / 2, cy + wheel_d / 2],
                             radius=int(wheel_w / 2), fill=(40, 42, 48), outline=INK, width=2)
        dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(122, 126, 134))
    text(dr, (ox + 40 * S, oy + 74 * S - wheel_d / 2 - 16), "37D 24 В 100:1", 13, "semi", ACCENT2, anchor="mm")

    # electronics bay
    rrect(dr, [ox + 52 * S, oy + 86 * S, ox + 148 * S, oy + 126 * S], 8,
          fill=(214, 236, 214), outline=GREEN, width=2)
    text(dr, (ox + 100 * S, oy + 99 * S), "4 × BTS7960 + Arduino Nano", 15, "semi", GREEN, anchor="mm")
    text(dr, (ox + 100 * S, oy + 116 * S), "радіатори + 40 мм вентилятор", 13, "reg", MUTED, anchor="mm")
    rrect(dr, [ox + 58 * S, oy + 130 * S, ox + 142 * S, oy + 152 * S], 8,
          fill=(214, 224, 244), outline=ACCENT2, width=2)
    text(dr, (ox + 100 * S, oy + 141 * S), "6S LiPo 2200 мА·год (22,2 В)", 14, "semi", ACCENT2, anchor="mm")

    # sensor bar
    dr.rectangle([ox, oy - 74, ox + L, oy - 60], fill=(250, 246, 224), outline=AMBER, width=2)
    for i in range(8):
        sx = ox + (10 + i * 25.7) * S
        dr.ellipse([sx - 8, oy - 74, sx + 8, oy - 56], fill=(250, 226, 140), outline=INK, width=1)

    # expanding side blades (deployed after the start signal)
    for sx in (ox - 34, ox + L - 8):
        dr.polygon([(sx + 8, oy + 40 * S), (sx + 38, oy + 60 * S),
                    (sx + 38, oy + 140 * S), (sx + 8, oy + 160 * S)],
                   fill=(236, 226, 246), outline=PURPLE, width=2)

    dim_h(dr, ox, ox + L, oy + Wd + 78, "200 мм — ліміт класу")
    arrow(dr, (ox - 120, oy + Wd / 2), (ox - 44, oy + Wd / 2), ACCENT2, 4, 15)
    text(dr, (ox - 128, oy + Wd / 2), "ПЕРЕД", 20, "bold", ACCENT2, anchor="rm")

    # legend
    lx, ly = 1330, 220
    legend = [
        (ACCENT, "магніти N52, ~76 г", "2 × 20×20×5 під клином + 4 × 10×5×5 біля коліс"),
        (ACCENT2, "4 × Pololu 37D 24 В 100:1", "0,19 м/с, 4,8 А сумарно, 4WD"),
        ((40, 42, 48), "колеса Ø50 × 15 мм", "Shore A 70 uretan, виступають за корпус"),
        (GREEN, "4 × BTS7960 + Nano", "з радіаторами й обдувом — матч без ліміту часу"),
        (AMBER, "сенсорна планка 8 × IR", "4 канали край + 4 суперник"),
        (PURPLE, "бокові клини, що розкриваються", "серво після старту (габарит можна міняти)"),
    ]
    for i, (col, t, s) in enumerate(legend):
        y = ly + i * 64
        dr.rounded_rectangle([lx, y, lx + 30, y + 20], radius=4, fill=col)
        text(dr, (lx + 44, y), t, 17, "semi", INK)
        text(dr, (lx + 44, y + 25), s, 14, "reg", MUTED)

    # key numbers
    px, py = 1330, 650
    rrect(dr, [px, py, px + 440, py + 320], 12, fill=PANEL, outline=LINE)
    text(dr, (px + 20, py + 14), "Числа цієї конструкції", 20, "bold")
    for i, (a, b) in enumerate([
        ("Нормальна сила", "3 кг + 15 кгс = 177 Н"),
        ("Тяга при μ = 1,0", "177 Н"),
        ("Тяга при μ = 0,7", "124 Н — консервативно"),
        ("Момент на колесо", "11,1 кг·см (μ = 1,0)"),
        ("Завантаження мотора", "31–44 % зупинного"),
        ("Швидкість під тягою", "0,17–0,19 м/с"),
        ("Перетин арени 154 см", "≈9 с"),
        ("Тепло на мотор", "0,3–1,3 Вт"),
    ]):
        text(dr, (px + 20, py + 54 + i * 32), a, 15, "semi", ACCENT2)
        text(dr, (px + 236, py + 54 + i * 32), b, 15, "reg", INK)
    text(dr, (px + 20, py + 292), "μ — головна невідома. Виміряй його першим.", 14, "semi", ACCENT)

    p = os.path.join(OUT, "fig2_top_view.png")
    im.save(p)
    return p
'''

src = open(PATH, encoding="utf-8").read()
start = src.index("def fig_top_view():")
# find the start of the NEXT top-level section comment after this function
nxt = src.index("# ----------------------------------------------------------------------------", start)
out = src[:start] + NEW + "\n\n" + src[nxt:]
open(PATH, "w", encoding="utf-8").write(out)
print("replaced fig_top_view; file now", len(out), "chars")
