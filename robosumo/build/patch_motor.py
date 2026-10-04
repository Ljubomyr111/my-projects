"""Rewrite fig_motor for the CHOSEN motor: 37D 24 V 100:1 run at 6S (22.2 V)."""

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
src = open(PATH, encoding="utf-8").read()

start = src.index("def fig_motor():")
nxt = src.index("# ----------------------------------------------------------------------------", start)

NEW = '''def fig_motor():
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
        pts.append((tx(rpm), ty(pw / 9.0 * STALL)))
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
        (3, ACCENT2, "P_max ≈ 9 Вт", "пік потужності цього мотора"),
        (4, GREEN, "робоча точка: 11,1 кг·см", "56 % завантаження, швидкість 0,17 м/с"),
        (5, ACCENT, "зупинка: 36,1 кг·см, 2,8 А", "тримати довго = спалити обмотки"),
    ]
    for i, (n, col, t, s) in enumerate(rows):
        y = py + 62 + i * 66
        badge(px + 40, y + 8, n, col)
        text(dr, (px + 68, y - 4), t, 17, "semi", INK)
        text(dr, (px + 68, y + 18), s, 15, "reg", MUTED)
    text(dr, (px + 20, py + 414), "Ми працюємо ВИЩЕ безперервної межі.", 17, "bold", ACCENT)
    text(dr, (px + 20, py + 442), "Це свідомий вибір: формат «до вибиття»", 15, "reg", INK)
    text(dr, (px + 20, py + 462), "не дає часу на очікування. Тому потрібні", 15, "reg", INK)
    text(dr, (px + 20, py + 482), "радіатори й обмеження шпаруватості в коді.", 15, "reg", INK)

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


'''

src = src[:start] + NEW + src[nxt:]
open(PATH, "w", encoding="utf-8").write(src)
print("fig_motor replaced")
