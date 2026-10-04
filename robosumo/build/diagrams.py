"""Generate technical diagrams for the robot-sumo playbook (v2, layout-corrected).

All drawings are produced programmatically with PIL so the playbook carries no
third-party imagery. Labels are Ukrainian.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\images"
os.makedirs(OUT, exist_ok=True)

REG = "C:/Windows/Fonts/segoeui.ttf"
BOLD = "C:/Windows/Fonts/segoeuib.ttf"
SEMI = "C:/Windows/Fonts/seguisb.ttf"

INK = (28, 32, 38)
MUTED = (110, 120, 132)
ACCENT = (198, 40, 40)
ACCENT2 = (21, 101, 192)
GREEN = (27, 122, 72)
AMBER = (190, 115, 0)
PURPLE = (112, 48, 160)
PAPER = (255, 255, 255)
PANEL = (244, 246, 249)
LINE = (196, 204, 214)


def font(size, weight="reg"):
    return ImageFont.truetype({"reg": REG, "bold": BOLD, "semi": SEMI}[weight], size)


def canvas(w, h, bg=PAPER):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)


def grid(dr, box, step, color=(232, 237, 243)):
    x0, y0, x1, y1 = box
    x = x0 + step
    while x < x1:
        dr.line([(x, y0), (x, y1)], fill=color, width=1)
        x += step
    y = y0 + step
    while y < y1:
        dr.line([(x0, y), (x1, y)], fill=color, width=1)
        y += step


def text(dr, xy, s, size=22, weight="reg", fill=INK, anchor="la"):
    dr.text(xy, s, font=font(size, weight), fill=fill, anchor=anchor)


def rrect(dr, box, r=10, fill=None, outline=INK, width=2):
    dr.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def arrow(dr, p0, p1, color=INK, width=3, head=13):
    dr.line([p0, p1], fill=color, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (+1, -1):
        a = ang + s * 2.6
        dr.line([p1, (p1[0] + head * math.cos(a), p1[1] + head * math.sin(a))],
                fill=color, width=width)


def elbow(dr, pts, color=INK, width=3, head=13):
    for a, b in zip(pts[:-2], pts[1:-1]):
        dr.line([a, b], fill=color, width=width)
    arrow(dr, pts[-2], pts[-1], color, width, head)


def dim_h(dr, x0, x1, y, label, size=19, color=MUTED, tick=8):
    dr.line([(x0, y), (x1, y)], fill=color, width=2)
    dr.line([(x0, y - tick), (x0, y + tick)], fill=color, width=2)
    dr.line([(x1, y - tick), (x1, y + tick)], fill=color, width=2)
    text(dr, ((x0 + x1) / 2, y - 10), label, size, "semi", color, anchor="ms")


def dim_v_label(dr, x, y, label, size=19, color=MUTED):
    """Vertical label drawn into a rotated transparent tile."""
    tile = Image.new("RGBA", (600, 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.text((300, 20), label, font=font(size, "semi"), fill=color, anchor="mm")
    tile = tile.rotate(90, expand=True)
    dr._image.paste(tile, (int(x - 20), int(y - 300)), tile)


def title_block(dr, w, heading, sub=None):
    dr.rectangle([0, 0, w, 78], fill=(28, 32, 38))
    text(dr, (28, 16), heading, 30, "bold", (255, 255, 255))
    if sub:
        text(dr, (28, 50), sub, 18, "reg", (176, 186, 198))


# ----------------------------------------------------------------------------
# 1. Arena
# ----------------------------------------------------------------------------
def fig_arena():
    W, H = 1620, 1080
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 1. Дві можливі арени — і чому це вирішує всю конструкцію",
                "Специфікація за All Japan Robot-Sumo / Baltic: клас 3 кг — сталь 154 см; "
                "клас 500 г — пластик 77 см.")

    # ---- left: 3 kg steel dohyo ----
    cx, cy, R = 430, 600, 300
    dr.ellipse([cx - R - 15, cy - R - 15, cx + R + 15, cy + R + 15], fill=(196, 199, 204))
    dr.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(58, 60, 66), outline=(30, 30, 34), width=3)
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(150, 120, 90))
    h = 20 * (2 * R / 154) / 2
    off = 10 * (2 * R / 154)
    for dx in (-off, off):
        dr.line([(cx + dx, cy - h), (cx + dx, cy + h)], fill=(150, 120, 90), width=5)
    dim_h(dr, cx - R, cx + R, cy + R + 52, "d = 154 см · сталь SPCC · h = 5 см")
    text(dr, (cx, cy - R - 52), "КЛАС 3 кг (Mega Sumo)", 23, "bold", ACCENT, anchor="mm")
    text(dr, (cx, cy - R - 26), "поверхня стальна → магніти працюють", 17, "semi", ACCENT, anchor="mm")
    for i, s in enumerate([
        "магніти ДОЗВОЛЕНІ (RoboGames 6.7, RobotChallenge 4.3.M)",
        "робот 20 × 20 см · 3 кг · матч 3 хв, до 3 раундів",
        "потрібен kill switch + окуляри й рукавички",
        "реальні роботи: >100 кгс притиску, до 130 А струму",
    ]):
        text(dr, (cx - R - 10, cy + R + 100 + i * 26), "• " + s, 16, "reg", INK)

    # ---- right: 500 g plastic dohyo ----
    cx2, cy2, R2 = 1080, 520, 168
    dr.ellipse([cx2 - R2 - 12, cy2 - R2 - 12, cx2 + R2 + 12, cy2 + R2 + 12], fill=(238, 236, 230))
    dr.ellipse([cx2 - R2, cy2 - R2, cx2 + R2, cy2 + R2], fill=(250, 248, 244), outline=(216, 210, 200), width=3)
    dr.ellipse([cx2 - 5, cy2 - 5, cx2 + 5, cy2 + 5], fill=ACCENT)
    h2 = 10 * (2 * R2 / 77) / 2
    off2 = 5 * (2 * R2 / 77)
    for dx in (-off2, off2):
        dr.line([(cx2 + dx, cy2 - h2), (cx2 + dx, cy2 + h2)], fill=ACCENT, width=4)
    dim_h(dr, cx2 - R2, cx2 + R2, cy2 + R2 + 46, "d = 77 см · пластик / дерево · h = 2,5 см")
    text(dr, (cx2, cy2 - R2 - 48), "КЛАС 500 г (Mini Sumo)", 21, "bold", ACCENT2, anchor="mm")
    text(dr, (cx2, cy2 - R2 - 22), "поверхня немагнітна → магніти марні й заборонені",
         16, "semi", ACCENT2, anchor="mm")
    for i, s in enumerate([
        "магніти ЗАБОРОНЕНІ (RoboGames, RobotChallenge)",
        "робот 10 × 10 см · 500 г",
        "$500 тут — повний бюджет із запасом",
        "перемагає алгоритм і зчеплення гуми",
    ]):
        text(dr, (cx2 - R2 - 40, cy2 + R2 + 90 + i * 26), "• " + s, 16, "reg", INK)

    # ---- bottom banner: the open question ----
    rrect(dr, [60, 60, 1560, 150], 12, fill=(252, 246, 236), outline=(226, 200, 150))
    text(dr, (84, 76), "ГОЛОВНЕ ПИТАННЯ: яка саме арена буде на турнірі?", 22, "bold", (150, 100, 0))
    text(dr, (84, 108),
         "Публічного технічного регламенту RoboSumo НаУКМА немає — ні вагового класу, ні матеріалу арени.",
         17, "reg", INK)
    text(dr, (84, 130),
         "Тому перший тиждень підготовки — це лист організаторам, а не закупівля деталей. Контакти — на останній сторінці.",
         17, "semi", ACCENT)

    p = os.path.join(OUT, "fig1_arena.png")
    im.save(p)
    return p


# ----------------------------------------------------------------------------
# 2. Robot top view
# ----------------------------------------------------------------------------
def fig_top_view():
    W, H = 2020, 1300
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 2. Компонування 3-кг робота — вид зверху",
                "Габарит 200 × 200 мм (ліміт класу), 4WD, висота без обмежень. "
                "Сітка 20 мм. Після старту габарит дозволено збільшувати.")

    S = 5.3
    ox, oy = 300, 320
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
    text(dr, (ox + 10, oy + 12), "↑ сенсорна планка на клині", 14, "semi", AMBER, anchor="lm")

    # magnets: bar row under the blade + blocks at the four wheels
    my0 = oy + 26 * S
    for i in range(2):
        mx = ox + (22 + i * 96) * S
        rrect(dr, [mx, my0 - 20, mx + 86 * S, my0 + 20], 6,
              fill=(238, 210, 210), outline=ACCENT, width=2)
    text(dr, (ox + L / 2, my0 + 54), "2 × 20×20×5 мм N52 — суцільний ряд під клином",
         15, "semi", ACCENT, anchor="mm")

    corners = [(40, 74), (160, 74), (40, 146), (160, 146)]

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
    # corner magnets sit just outboard of each wheel and are drawn on top
    for wx, wy in corners:
        for dx in (-26, 26):
            rrect(dr, [ox + (wx + dx - 7) * S, oy + (wy - 7) * S,
                       ox + (wx + dx + 7) * S, oy + (wy + 7) * S], 4,
                  fill=(238, 210, 210), outline=ACCENT, width=2)
    text(dr, (ox + 100 * S, oy + 172 * S),
         "4 × 10×5×5 мм N52 — біля кожного колеса",
         14, "semi", ACCENT, anchor="mm")

    # electronics bay
    rrect(dr, [ox + 52 * S, oy + 86 * S, ox + 148 * S, oy + 126 * S], 8,
          fill=(214, 236, 214), outline=GREEN, width=2)
    text(dr, (ox + 100 * S, oy + 99 * S), "4 × BTS7960 + Arduino Nano", 15, "semi", GREEN, anchor="mm")
    text(dr, (ox + 100 * S, oy + 116 * S), "радіатори + 40 мм вентилятор", 13, "reg", MUTED, anchor="mm")
    rrect(dr, [ox + 58 * S, oy + 130 * S, ox + 142 * S, oy + 152 * S], 8,
          fill=(214, 224, 244), outline=ACCENT2, width=2)
    text(dr, (ox + 100 * S, oy + 141 * S), "6S LiPo 2200 мА·год (22,2 В)", 14, "semi", ACCENT2, anchor="mm")

    # sensor bar
    dr.rectangle([ox, oy - 44, ox + L, oy - 34], fill=(250, 246, 224), outline=AMBER, width=2)
    for i in range(8):
        sx = ox + (12 + i * 25.2) * S
        dr.ellipse([sx - 8, oy - 45, sx + 8, oy - 33], fill=(250, 226, 140), outline=INK, width=1)

    # expanding side blades (deployed after the start signal)
    for sx in (ox - 34, ox + L - 8):
        dr.polygon([(sx + 8, oy + 40 * S), (sx + 38, oy + 60 * S),
                    (sx + 38, oy + 140 * S), (sx + 8, oy + 160 * S)],
                   fill=(236, 226, 246), outline=PURPLE, width=2)

    dim_h(dr, ox, ox + L, oy + Wd + 78, "200 мм — ліміт класу")
    arrow(dr, (ox - 130, oy + Wd / 2), (ox - 50, oy + Wd / 2), ACCENT2, 4, 15)
    text(dr, (ox - 140, oy + Wd / 2), "ПЕРЕД", 20, "bold", ACCENT2, anchor="rm")

    # legend
    lx, ly = 1420, 230
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
    px, py = 1420, 660
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


# ----------------------------------------------------------------------------
# 3. Front view
# ----------------------------------------------------------------------------
def fig_front_view():
    W, H = 1680, 900
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 3. Вид спереду — клин, сенсори, кліренс",
                "Висота корпусу 45–55 мм. Клин нижче клина суперника — це і є перемога в контакті.")

    S = 6.2
    ox, oy = 300, 250          # body top-left
    L = 100 * S
    bh = 52 * S

    dr.rectangle([ox, oy, ox + L, oy + bh], fill=(242, 245, 250), outline=INK, width=3)
    grid(dr, (ox, oy, ox + L, oy + bh), 20 * S)

    # wheels behind body (dashed)
    for wx in (ox + 8 * S, ox + 92 * S):
        dr.ellipse([wx - 25 * S, oy + bh - 25 * S, wx + 25 * S, oy + bh + 25 * S],
                   fill=(226, 229, 235), outline=(160, 166, 176), width=2)
    text(dr, (ox + L / 2, oy + bh - 30), "колеса Ø50 мм — виступають на 2–3 мм за корпус",
         16, "reg", MUTED, anchor="mm")

    # blade
    dr.polygon([(ox - 18, oy + bh + 12), (ox + L + 18, oy + bh + 12),
                (ox + L + 18, oy + bh), (ox - 18, oy + bh)],
               fill=(176, 182, 192), outline=INK)
    text(dr, (ox + L / 2, oy + bh + 30), "клин: 3 мм, загартована сталь / титан, кут 8–12°",
         17, "semi", INK, anchor="ma")

    # ground
    gy = oy + bh + 118
    dr.line([(ox - 200, gy), (ox + L + 200, gy)], fill=INK, width=5)
    for x in range(ox - 200, int(ox + L + 200), 55):
        dr.line([(x, gy), (x + 26, gy + 16)], fill=(212, 212, 216), width=3)
    text(dr, (ox + L + 205, gy + 30), "поверхня арени (сталь)", 17, "semi", MUTED, anchor="ra")

    # clearance dim
    dim_v_label(dr, ox + L + 70, (oy + bh + 12 + gy) / 2 + 300, "кліренс 1–1,5 мм", 17, ACCENT)
    dr.line([(ox + L + 40, oy + bh + 12), (ox + L + 100, oy + bh + 12)], fill=ACCENT, width=2)
    dr.line([(ox + L + 40, gy), (ox + L + 100, gy)], fill=ACCENT, width=2)

    # sensor bar
    dr.rectangle([ox - 14, oy + bh - 16, ox + L + 14, oy + bh - 4],
                 fill=(250, 246, 224), outline=AMBER, width=2)
    for i in range(8):
        sx = ox + (7 + i * 12) * S
        dr.ellipse([sx - 7, oy + bh - 15, sx + 7, oy + bh - 5], fill=(250, 226, 140), outline=INK, width=1)
    arrow(dr, (ox + L + 150, oy + bh - 60), (ox + L + 16, oy + bh - 12), AMBER, 3, 13)
    text(dr, (ox + L + 158, oy + bh - 68), "сенсорна планка —", 17, "semi", AMBER)
    text(dr, (ox + L + 158, oy + bh - 46), "1,5–2 мм над підлогою", 17, "semi", AMBER)

    # side panel note
    dr.polygon([(ox, oy), (ox + 30 * S, oy), (ox, oy + bh)], fill=(230, 234, 240), outline=INK)
    arrow(dr, (ox - 150, oy + 60), (ox + 12, oy + 22), PURPLE, 3, 13)
    text(dr, (ox - 158, oy + 54), "похилі бокові панелі", 17, "semi", PURPLE, anchor="ra")
    text(dr, (ox - 158, oy + 76), "30–45°, матові чорні", 17, "semi", PURPLE, anchor="ra")

    # right panels
    px = 1080
    rrect(dr, [px, 130, px + 560, 420], 12, fill=PANEL, outline=LINE)
    text(dr, (px + 20, 144), "Геометрія, що виграє контакт", 21, "bold")
    for i, s in enumerate([
        "• Клин має заходити ПІД клин суперника.",
        "• Чим тонший і нижчий клин — тим краще.",
        "• Загартована сталь тримає зазубрини, м'який",
        "  алюміній загинається після 3–4 ударів.",
        "• Бокові панелі під кутом змушують суперника",
        "  зісковзувати, а не штовхати.",
        "• Матове чорне покриття + похилі панелі =",
        "  робот гірше видно для IR-сенсорів суперника.",
        "• Центр мас трохи позаду осі коліс: робот не",
        "  задирається, коли суперник тисне зверху.",
    ]):
        text(dr, (px + 20, 182 + i * 25), s, 16, "reg", INK)

    rrect(dr, [px, 450, px + 560, 760], 12, fill=(250, 244, 244), outline=(232, 200, 200))
    text(dr, (px + 20, 464), "Три способи програти на контакті", 21, "bold", ACCENT)
    for i, s in enumerate([
        "1. Клин задерто вгору — суперник підіймає тебе.",
        "   Лік: кліренс 1–1,5 мм і жорстке кріплення.",
        "2. Колеса в межах корпусу — тебе перевертають",
        "   через борт. Лік: колеса назовні на 2–3 мм.",
        "3. Магніти лише в центрі — тяга є, а зчеплення",
        "   під колесами немає. Лік: магніти до коліс.",
        "",
        "Перевірка: постав робота на сталь і спробуй",
        "зсунути його пальцем. Має бути важко.",
    ]):
        text(dr, (px + 20, 502 + i * 25), s, 16, "reg", ACCENT if s.startswith(("1.", "2.", "3.")) else INK)

    p = os.path.join(OUT, "fig3_front_view.png")
    im.save(p)
    return p


# ----------------------------------------------------------------------------
# 4. Forces side view
# ----------------------------------------------------------------------------
def fig_forces():
    W, H = 1600, 1000
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 4. Сили на магнітній арені — вид збоку (3 кг)",
                "Магніти множать силу тертя. Але момент мотора вирішує, скільки з неї можна використати.")

    gy = 620
    dr.line([(150, gy), (980, gy)], fill=INK, width=6)
    for x in range(150, 980, 58):
        dr.line([(x, gy), (x + 28, gy + 17)], fill=(224, 224, 228), width=3)
    text(dr, (975, gy + 30), "магнітна поверхня арени", 17, "semi", MUTED, anchor="ra")

    bx0, by0 = 430, 420
    bw, bh = 400, 130
    dr.polygon([(bx0, by0), (bx0 + bw, by0), (bx0 + bw, by0 + bh), (bx0, by0 + bh)],
               fill=(242, 245, 250), outline=INK)
    dr.polygon([(bx0 - 80, gy), (bx0, gy), (bx0, by0 + bh), (bx0 - 26, by0 + bh)],
               fill=(198, 206, 216), outline=INK)
    # wheel (behind body)
    dr.ellipse([bx0 + 250, by0 + bh - 10, bx0 + 340, by0 + bh + 80], fill=(52, 54, 60), outline=INK, width=2)
    dr.ellipse([bx0 + 285, by0 + bh + 25, bx0 + 305, by0 + bh + 45], fill=(122, 126, 134))
    # magnets, sitting just above the arena under the chassis
    for i in range(3):
        mx = bx0 + 40 + i * 74
        dr.rectangle([mx, by0 + bh + 2, mx + 46, by0 + bh + 18],
                     fill=(238, 210, 210), outline=ACCENT, width=2)

    # weight arrow (left of body, clear of wheel)
    arrow(dr, (bx0 + 60, by0 - 110), (bx0 + 60, by0 + 90), ACCENT2, 5, 17)
    text(dr, (bx0 + 50, by0 - 82), "m·g = 29,4 Н (3 кг)", 18, "bold", ACCENT2, anchor="rm")

    # magnet force arrow (left third, clear of wheel and hatches)
    arrow(dr, (bx0 + 120, by0 + bh + 26), (bx0 + 120, gy - 12), ACCENT, 5, 17)
    text(dr, (bx0 + 30, by0 + bh + 62), "F_магн = 147 Н (15 кгс)", 18, "bold", ACCENT)

    # clearance dim, right of the wheel
    dr.line([(bx0 + 430, by0 + bh + 18), (bx0 + 430, gy)], fill=ACCENT2, width=2)
    dr.line([(bx0 + 422, by0 + bh + 18), (bx0 + 438, by0 + bh + 18)], fill=ACCENT2, width=2)
    dr.line([(bx0 + 422, gy), (bx0 + 438, gy)], fill=ACCENT2, width=2)
    text(dr, (bx0 + 446, by0 + bh + 44), "кліренс 1–1,5 мм", 16, "semi", ACCENT2)

    # friction arrow, below the hatched ground
    arrow(dr, (bx0 + 120, gy + 70), (bx0 + 660, gy + 70), GREEN, 6, 19)
    text(dr, (bx0 + 120, gy + 88), "F_тертя = μ · (m·g + F_магн)  — це і штовхає суперника",
         18, "bold", GREEN)
    text(dr, (bx0 + 120, gy + 118), "але використати її можна лише на стільки, на скільки є момент", 16, "reg", MUTED)

    # formula panel
    px, py = 1040, 130
    rrect(dr, [px, py, px + 510, py + 620], 12, fill=PANEL, outline=LINE)
    text(dr, (px + 22, py + 16), "Ключова формула", 23, "bold")
    text(dr, (px + 22, py + 58), "F_max = μ · (m·g + F_магн)", 25, "bold", ACCENT)
    text(dr, (px + 22, py + 108), "Робот 3 кг, μ = 0,7 (гума / сталь):", 18, "semi")
    for i, (s, col) in enumerate([
        ("без магнітів:      0,7 · 29,4 =  20,6 Н", INK),
        ("з 15 кгс (147 Н):  0,7 · 176,6 = 123,6 Н", GREEN),
        ("приріст тяги ×6,0 — без грама ваги", GREEN),
    ]):
        text(dr, (px + 22, py + 140 + i * 32), s, 18, "reg", col)
    text(dr, (px + 22, py + 258), "Те саме при μ = 1,0 (оптимістично):", 18, "semi")
    for i, (s, col) in enumerate([
        ("без магнітів:      1,0 · 29,4 =  29,4 Н", INK),
        ("з 15 кгс (147 Н):  1,0 · 176,6 = 176,6 Н", GREEN),
    ]):
        text(dr, (px + 22, py + 290 + i * 30), s, 18, "reg", col)
    dr.line([(px + 22, py + 358), (px + 488, py + 358)], fill=LINE, width=1)
    text(dr, (px + 22, py + 376), "Висновок: магніти — майже безкоштовна вага.", 18, "bold", ACCENT2)
    text(dr, (px + 22, py + 410), "Але момент на валу росте так само, а 37D", 17, "reg")
    text(dr, (px + 22, py + 436), "тримає лише 10 кг·см безперервно. Тому", 17, "reg")
    text(dr, (px + 22, py + 462), "зайві магніти не додають сили штовхання.", 17, "semi", ACCENT)
    dr.line([(px + 22, py + 494), (px + 488, py + 494)], fill=LINE, width=1)
    text(dr, (px + 22, py + 512), "Головне обмеження — не зчеплення,", 17, "semi", ACCENT2)
    text(dr, (px + 22, py + 538), "а момент мотора. Став магніти під колеса", 17, "reg")
    text(dr, (px + 22, py + 564), "й клин — тоді вся тяга йде в бій,", 17, "reg")
    text(dr, (px + 22, py + 590), "а не в марне притискання днища.", 17, "reg")

    p = os.path.join(OUT, "fig4_forces.png")
    im.save(p)
    return p


# ----------------------------------------------------------------------------
# 5. Wiring
# ----------------------------------------------------------------------------
def fig_wiring():
    W, H = 1620, 1020
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 5. Електрична схема — 4WD, 6S",
                "Nano + 4 × BTS7960 + 6S LiPo (22,2 В). Спільна земля обовʼязкова, радіатори на драйверах.")

    def block(x, y, w, h, t, sub=None, fill=PAPER, outline=INK, tsize=20):
        rrect(dr, [x, y, x + w, y + h], 10, fill=fill, outline=outline, width=2)
        if sub:
            text(dr, (x + w / 2, y + h / 2 - 12), t, tsize, "bold", INK, anchor="mm")
            text(dr, (x + w / 2, y + h / 2 + 15), sub, 15, "reg", MUTED, anchor="mm")
        else:
            text(dr, (x + w / 2, y + h / 2), t, tsize, "bold", INK, anchor="mm")

    block(60, 300, 200, 130, "6S LiPo", "22,2 В · 2200 мА·год · 30C",
          fill=(224, 232, 248), outline=ACCENT2)
    block(330, 640, 170, 110, "Вимикач", "+ запобіжник 20 А", fill=(240, 240, 244), tsize=18)
    block(560, 300, 190, 130, "DC-DC 5 В", "MP1584 / LM2596", fill=(228, 242, 228), outline=GREEN)
    block(560, 60, 260, 150, "Arduino Nano", "ATmega328P · 16 МГц", fill=(246, 240, 224), outline=AMBER)
    block(540, 500, 230, 95, "BTS7960 × 2", "мотори 1 і 2", fill=(250, 232, 232), outline=ACCENT, tsize=16)
    block(540, 630, 230, 95, "BTS7960 × 2", "мотори 3 і 4", fill=(250, 232, 232), outline=ACCENT, tsize=16)
    block(860, 500, 210, 95, "Мотори 1–2", "37D 24 В 100:1", fill=(236, 236, 240), tsize=15)
    block(860, 630, 210, 95, "Мотори 3–4", "37D 24 В 100:1", fill=(236, 236, 240), tsize=15)
    block(540, 790, 260, 95, "QTR-8A + INA226", "8 × IR + струм моторів", fill=(250, 246, 224), outline=AMBER, tsize=16)

    # power bus
    dr.line([(260, 365), (330, 365)], fill=ACCENT2, width=4)
    dr.line([(500, 365), (560, 365)], fill=ACCENT2, width=4)
    text(dr, (395, 345), "11,1 В", 17, "semi", ACCENT2, anchor="mm")
    dr.line([(430, 365), (430, 700)], fill=(200, 60, 60), width=4)
    arrow(dr, (430, 575), (560, 575), (200, 60, 60), 4, 14)
    arrow(dr, (430, 700), (560, 755), (200, 60, 60), 4, 14)
    text(dr, (452, 546), "силова шина 11,1 В", 16, "semi", (200, 60, 60))
    arrow(dr, (430, 700), (430, 940), (200, 60, 60), 4, 14)
    dr.line([(430, 940), (560, 940)], fill=(200, 60, 60), width=4)
    arrow(dr, (560, 940), (560, 990), (200, 60, 60), 3, 12)
    text(dr, (452, 962), "QTR — від 5 В, не від шини!", 15, "semi", ACCENT)
    elbow(dr, [(660, 640), (660, 620), (800, 620), (800, 520)], MUTED, 3, 12)

    # 5V rail
    arrow(dr, (655, 300), (655, 210), GREEN, 4, 14)
    text(dr, (668, 254), "5 В", 17, "semi", GREEN)
    dr.line([(655, 210), (1050, 210)], fill=GREEN, width=4)
    elbow(dr, [(1050, 210), (1050, 300), (900, 300), (900, 520)], GREEN, 3, 12)
    elbow(dr, [(1050, 210), (1050, 300), (900, 300), (900, 700)], GREEN, 3, 12)
    elbow(dr, [(1050, 210), (1050, 940), (820, 940)], GREEN, 3, 12)
    text(dr, (890, 194), "шина 5 В (логіка)", 16, "semi", GREEN, anchor="mm")

    # control signals
    arrow(dr, (740, 210), (740, 145), AMBER, 3, 12)
    text(dr, (752, 176), "логіка", 15, "reg", MUTED)
    for x0, y0, y1 in ((690, 210, 520), (700, 210, 700)):
        elbow(dr, [(x0, y0), (x0, (y0 + y1) / 2 - 20), (520, (y0 + y1) / 2 - 20), (520, y1 - 20), (560, y1 - 20)],
              AMBER, 3, 12)
    text(dr, (505, 430), "RPWM / LPWM", 15, "reg", MUTED, anchor="rm")
    arrow(dr, (770, 547), (860, 547), INK, 4, 14)
    arrow(dr, (770, 677), (860, 677), INK, 4, 14)

    # notes panel
    nx, ny = 1210, 320
    rrect(dr, [nx, ny, nx + 360, ny + 620], 12, fill=PANEL, outline=LINE)
    text(dr, (nx + 20, ny + 16), "Чек-ліст складання", 21, "bold")
    items = [
        ("Спільна GND", False), ("усі блоки: батарея,", True), ("DC-DC, Nano, драйвери", True),
        ("Конденсатор 1000 мкФ", False), ("на силовій шині моторів", True),
        ("Запобіжник 20 А", False), ("послідовно з батареєю", True),
        ("Дроти моторів AWG 18–20", False), ("тонші гріються й просідають", True),
        ("Мотори — окремо від 5 В", False),
        ("Перевір полярність", False), ("до першого вмикання", True),
        ("Кнопка старту", False), ("окремо від вимикача", True),
        ("Радіатор на BTS7960", False), ("при 15 А обов'язковий", True),
        ("Вага проводів", False), ("врахуй у ліміті ваги", True),
    ]
    y = ny + 56
    for s, is_sub in items:
        if not is_sub:
            y += 6
        text(dr, (nx + 20, y), ("• " if not is_sub else "   ") + s, 15,
             "semi" if not is_sub else "reg", INK if not is_sub else MUTED)
        y += 24

    p = os.path.join(OUT, "fig5_wiring.png")
    im.save(p)
    return p


# ----------------------------------------------------------------------------
# 6. Motor curve
# ----------------------------------------------------------------------------
def fig_motor():
    W, H = 1640, 1060
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 6. Робоча точка обраного мотора: 37D 24 В 100:1 при 6S",
                "Номінал 24 В, працюємо на 22,2 В. Без навантаження 92 об/хв, "
                "зупинний момент 36,1 кг·см, зупинний струм 2,8 А.")

    x0, y0, x1, y1 = 250, 660, 1060, 250
    TQ_MAX = 40.0        # kg.cm
    RPM_MAX = 100.0      # rpm at 22.2 V

    dr.line([(x0, y1), (x0, y0)], fill=INK, width=3)
    dr.line([(x0, y0), (x1, y0)], fill=INK, width=3)

    def tx(rpm):
        return x0 + (rpm / RPM_MAX) * (x1 - x0)

    def ty(kgcm):
        return y0 - (kgcm / TQ_MAX) * (y0 - y1)

    for i in range(6):
        rpm = i * 20.0
        x = tx(rpm)
        dr.line([(x, y0), (x, y0 + 8)], fill=INK, width=2)
        text(dr, (x, y0 + 16), f"{int(rpm)}", 16, "reg", MUTED, anchor="ma")
    for i in range(6):
        kgcm = i * 8.0
        y = ty(kgcm)
        dr.line([(x0 - 8, y), (x0, y)], fill=INK, width=2)
        text(dr, (x0 - 16, y), f"{int(kgcm)}", 16, "reg", MUTED, anchor="rm")

    STALL, RPM0 = 36.1, 92.0
    dr.line([(tx(0), ty(STALL)), (tx(RPM0), ty(0))], fill=ACCENT, width=4)

    pts = []
    for i in range(81):
        kgcm = i * 0.5
        rpm = RPM0 * (1 - kgcm / STALL)
        pw = rpm * 2 * math.pi / 60 * kgcm * 0.0981
        pts.append((tx(rpm), ty(pw / 8.5 * STALL)))
    dr.line(pts, fill=ACCENT2, width=4)

    dr.line([(tx(0), ty(10)), (tx(RPM0 * (1 - 10 / STALL)), ty(10))], fill=AMBER, width=3)

    # operating point: 11.1 kg.cm at mu = 1.0
    op_tq = 11.1
    op_rpm = RPM0 * (1 - op_tq / STALL)
    ox_, oy_ = tx(op_rpm), ty(op_tq)
    dr.ellipse([ox_ - 12, oy_ - 12, ox_ + 12, oy_ + 12], fill=GREEN, outline=PAPER, width=3)

    def badge(cx, cy, n, col):
        dr.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=col, outline=PAPER, width=2)
        text(dr, (cx, cy), str(n), 17, "bold", PAPER, anchor="mm")

    badge(tx(6), ty(34), 1, ACCENT)
    badge(tx(52), ty(10.4), 2, AMBER)
    badge(tx(30), ty(9.0), 3, ACCENT2)
    badge(ox_ + 44, oy_ - 40, 4, GREEN)
    badge(tx(94), ty(2.0), 5, ACCENT)

    text(dr, (x1, y0 + 50), "швидкість обертання, об/хв", 18, "semi", INK, anchor="ra")
    text(dr, (x0 - 14, y1 - 32), "крутний момент, кг·см", 18, "semi", INK, anchor="rm")

    px, py = 1150, 180
    rrect(dr, [px, py, px + 440, py + 500], 12, fill=PANEL, outline=LINE)
    text(dr, (px + 20, py + 14), "Що показує графік", 21, "bold")
    rows = [
        (1, ACCENT, "без навантаження: 92 об/хв", "момент нульовий — робот стоїть"),
        (2, AMBER, "межа безперервного моменту", "10 кг·см — вище лише короткочасно"),
        (3, ACCENT2, "P_max ≈ 8,5 Вт", "пік потужності цього мотора"),
        (4, GREEN, "робоча точка: 11,1 кг·см", "56 % завантаження, швидкість 0,17 м/с"),
        (5, ACCENT, "зупинка: 36,1 кг·см, 2,8 А", "тримати довго = спалити обмотки"),
    ]
    for i, (n, col, t, s) in enumerate(rows):
        y = py + 62 + i * 66
        badge(px + 40, y + 8, n, col)
        text(dr, (px + 68, y - 4), t, 17, "semi", INK)
        text(dr, (px + 68, y + 18), s, 15, "reg", MUTED)
    text(dr, (px + 20, py + 414), "Ми працюємо ВИЩЕ безперервної межі.", 17, "bold", ACCENT)
    text(dr, (px + 20, py + 444), "часу на очікування. Тому потрібні радіатори", 15, "reg", INK)
    text(dr, (px + 20, py + 466), "й обмеження шпаруватості в коді.", 15, "reg", INK)

    rx, ry = 250, 790
    rrect(dr, [rx, ry, rx + 1340, ry + 216], 12, fill=PANEL, outline=LINE)
    text(dr, (rx + 20, ry + 12), "Чому саме 100:1 при 6S, а не 50:1 чи 70:1", 19, "bold")
    heads = ["редуктор при 6S", "об/хв", "зупинний момент", "момент на колесо", "завантаження", "вердикт"]
    xs = [rx + 20, rx + 230, rx + 340, rx + 540, rx + 740, rx + 900]
    for hx, h in zip(xs, heads):
        text(dr, (hx, ry + 48), h, 15, "semi", MUTED)
    for i, (r, rpm, tq, tw, load, verdict, col) in enumerate([
        ("50:1", "417", "19,4", "6,0", "31 %", "швидко, але момент на межі", INK),
        ("70:1", "312", "28,0", "8,6", "31 %", "компроміс, 0,27 м/с", INK),
        ("100:1", "92", "36,1", "11,1", "56 %", "наш вибір: 0,17 м/с, запас моменту", GREEN),
    ]):
        y = ry + 80 + i * 30
        text(dr, (xs[0], y), r, 16, "semi", col)
        text(dr, (xs[1], y), rpm, 16, "reg", col)
        text(dr, (xs[2], y), tq, 16, "reg", col)
        text(dr, (xs[3], y), tw, 16, "reg", col)
        text(dr, (xs[4], y), load, 16, "reg", col)
        text(dr, (xs[5], y), verdict, 16, "reg", col)
    text(dr, (rx + 20, ry + 184),
         "Менший редуктор дає швидкість, але момент на колесі падає до межі зчеплення. "
         "100:1 дає запас, який і є наша перевага.", 16, "semi", ACCENT2)

    p = os.path.join(OUT, "fig6_motor.png")
    im.save(p)
    return p


# ----------------------------------------------------------------------------
# 7. Tactics state machine
# ----------------------------------------------------------------------------
def fig_tactics():
    W, H = 1620, 1020
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 7. Алгоритм бою — скінченний автомат",
                "Мета: виграти перші 300 мс, утримати контакт і жодного разу не впасти з арени.")

    def state(x, y, w, h, t, sub, fill):
        rrect(dr, [x, y, x + w, y + h], 14, fill=fill, outline=INK, width=3)
        text(dr, (x + w / 2, y + 28), t, 21, "bold", INK, anchor="mm")
        for i, s in enumerate(sub):
            text(dr, (x + w / 2, y + 56 + i * 21), s, 15, "reg", MUTED, anchor="mm")

    state(40, 120, 280, 120, "СТАРТ", ["пауза 300 мс", "двигуни стоп"], (244, 246, 249))
    state(400, 120, 300, 120, "ПОШУК", ["коло / зигзаг", "максимальна швидкість"], (232, 240, 252))
    state(780, 120, 300, 120, "АТАКА", ["прямо на ціль", "повний газ"], (250, 232, 232))
    state(1160, 120, 280, 120, "УТРИМАННЯ", ["дотискати", "не відпускати"], (250, 240, 224))
    state(780, 360, 300, 120, "ВІДХІД", ["назад + розворот", "пріоритет краю"], (232, 246, 236))
    state(400, 620, 300, 120, "ЗАХИСТ", ["тримати центр", "чекати помилку"], (244, 236, 250))
    state(1160, 360, 280, 120, "КІНЕЦЬ", ["час вийшов або", "суперник за лінією"], (238, 238, 242))
    state(780, 620, 300, 120, "АНТИ-ПАТ", ["реверс 150 мс", "зміна кута"], (250, 236, 236))

    def edge(p0, p1, label, color=MUTED):
        arrow(dr, p0, p1, color, 3, 14)
        if label:
            text(dr, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 12), label,
                 15, "semi", color, anchor="mm")

    edge((320, 180), (400, 180), "300 мс")
    edge((700, 180), (780, 180), "побачив суперника")
    edge((1080, 180), (1160, 180), "контакт")
    edge((1300, 240), (1300, 360), "час")
    edge((1160, 420), (1080, 420), "втратив")
    edge((780, 420), (700, 420), "край")
    edge((550, 620), (550, 240), "понад 2 с без цілі")
    elbow(dr, [(930, 480), (930, 620)], ACCENT, 3, 14)
    text(dr, (944, 546), "застряг >1 с", 15, "semi", ACCENT)
    elbow(dr, [(780, 680), (300, 680), (300, 740), (400, 740)], ACCENT, 3, 14)
    text(dr, (540, 664), "вихід із пата", 15, "semi", ACCENT, anchor="mm")
    elbow(dr, [(1080, 300), (1080, 330), (900, 330), (900, 360)], ACCENT2, 3, 14)
    text(dr, (1010, 314), "край", 15, "semi", ACCENT2, anchor="mm")

    # rules panel (kept clear of the arrows)
    px, py = 40, 780
    rrect(dr, [px, py, 1580, py + 210], 12, fill=PANEL, outline=LINE)
    text(dr, (px + 22, py + 14), "Шість правил, які виграють матчі", 22, "bold")
    left = [
        "1. Детекція краю має пріоритет над атакою. Завжди.",
        "2. Псевдо-код відходу:  while (край) { назад 10 мс; розворот; }",
        "3. Суперник у центрі? Не штовхай — обійди і бий у бік.",
    ]
    right = [
        "4. Втратив ціль — не крутись на місці, іди по спіралі.",
        "5. Перші 300 мс вирішують, хто володіє центром.",
        "6. Понад 2 с без контакту — повертайся до центру.",
    ]
    for i, s in enumerate(left):
        text(dr, (px + 22, py + 56 + i * 32), s, 17, "reg", INK)
    for i, s in enumerate(right):
        text(dr, (px + 800, py + 56 + i * 32), s, 17, "reg", INK)
    text(dr, (px + 22, py + 166), "Кожне правило тестуй окремим прогоном і міряй час реакції секундоміром.",
         17, "semi", ACCENT)

    p = os.path.join(OUT, "fig7_tactics.png")
    im.save(p)
    return p


# ----------------------------------------------------------------------------
# 8. Roadmap
# ----------------------------------------------------------------------------
def fig_roadmap():
    W, H = 1620, 900
    im, dr = canvas(W, H)
    title_block(dr, W, "Рис. 8. План підготовки на 6 місяців",
                "Кожен місяць закінчується роботом, який їде. Не «майже готовим».")

    x0, y0 = 470, 170
    colw = (1500 - x0) / 6
    for i, m in enumerate(["Місяць 1", "Місяць 2", "Місяць 3", "Місяць 4", "Місяць 5", "Місяць 6"]):
        text(dr, (x0 + i * colw + colw / 2, y0 - 20), m, 18, "bold", INK, anchor="mm")
        dr.line([(x0 + i * colw, y0), (x0 + i * colw, 790)], fill=LINE, width=2)
    dr.line([(1500, y0), (1500, 790)], fill=LINE, width=2)

    rows = [
        ("Правила й клас", 0, 1, ACCENT2, "дізнатись вагу, габарит, тип арени"),
        ("Закупівля", 0.3, 1.4, AMBER, "магніти, мотори, драйвери, сенсори"),
        ("Шасі v1 (фрезер / 3D)", 1, 2, GREEN, "перша рама, клин, колеса"),
        ("Електроніка й прошивка", 1.5, 3, ACCENT2, "Nano, BTS7960, QTR, старт"),
        ("Тренувальна арена", 1.2, 2.2, MUTED, "коло 77 см + сталь 1 мм"),
        ("Магнітна система", 2, 3, ACCENT, "підбір магнітів і кліренсу"),
        ("Алгоритми бою", 2.5, 5, GREEN, "пошук, атака, анти-край, анти-пат"),
        ("Спаринги", 3, 6, ACCENT2, "мінімум 3 матчі на тиждень"),
        ("V2: силова версія", 3.5, 4.5, AMBER, "70:1 або Maxon, колеса Ø60"),
        ("Надійність", 4.5, 6, ACCENT, "радіатори, кріплення, контроль ваги"),
        ("Передзмагальний тиждень", 5.6, 6, PURPLE, "повний прогін за регламентом"),
    ]
    for i, (name, a, b, col, note) in enumerate(rows):
        y = y0 + 34 + i * 56
        text(dr, (50, y + 4), name, 18, "bold", INK)
        text(dr, (50, y + 26), note, 14, "reg", MUTED)
        bx = x0 + a * colw
        bw = max((b - a) * colw, 26)
        dr.rounded_rectangle([bx, y, bx + bw, y + 26], radius=13, fill=col, outline=PAPER, width=2)

    rrect(dr, [50, 810, 1570, 878], 10, fill=PANEL, outline=LINE)
    text(dr, (70, 830),
         "Критичний шлях: правила → магніти й мотори → шасі → алгоритм краю.", 18, "semi", ACCENT)
    text(dr, (70, 856),
         "Якщо замовлення запізнюється — починай із 3D-друку, симуляції логіки та тренувальної арени.",
         18, "reg")

    p = os.path.join(OUT, "fig8_roadmap.png")
    im.save(p)
    return p


if __name__ == "__main__":
    for fn in (fig_arena, fig_top_view, fig_front_view, fig_forces,
               fig_wiring, fig_motor, fig_tactics, fig_roadmap):
        p = fn()
        print("OK", os.path.basename(p), os.path.getsize(p), "bytes")
