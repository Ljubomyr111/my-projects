"""Refine fig_top_view geometry: visible corner magnets, sensor bar on the blade."""
import re

PATH = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build\diagrams.py"
src = open(PATH, encoding="utf-8").read()

# 1. more room on the left for the "ПЕРЕД" label
src = src.replace("    ox, oy = 180, 320\n", "    ox, oy = 300, 320\n")

# 2. corner magnets: move them outboard of the wheels so they are visible,
#    and draw them AFTER the wheels
old_mag = """    corners = [(40, 74), (160, 74), (40, 146), (160, 146)]
    for wx, wy in corners:
        rrect(dr, [ox + (wx - 10) * S, oy + (wy - 10) * S,
                   ox + (wx + 10) * S, oy + (wy + 10) * S], 5,
              fill=(238, 210, 210), outline=ACCENT, width=2)

"""
new_mag = """    corners = [(40, 74), (160, 74), (40, 146), (160, 146)]

"""
assert old_mag in src
src = src.replace(old_mag, new_mag)

# 3. draw the corner magnets just outboard of each wheel, after the wheels
old_wheels = """    text(dr, (ox + 40 * S, oy + 74 * S - wheel_d / 2 - 16), "37D 24 \u0412 100:1", 13, "semi", ACCENT2, anchor="mm")
"""
new_wheels = """    text(dr, (ox + 40 * S, oy + 74 * S - wheel_d / 2 - 16), "37D 24 \u0412 100:1", 13, "semi", ACCENT2, anchor="mm")
    # corner magnets sit just outboard of each wheel and are drawn on top
    for wx, wy in corners:
        for dx in (-26, 26):
            rrect(dr, [ox + (wx + dx - 7) * S, oy + (wy - 7) * S,
                       ox + (wx + dx + 7) * S, oy + (wy + 7) * S], 4,
                  fill=(238, 210, 210), outline=ACCENT, width=2)
    text(dr, (ox + 100 * S, oy + 172 * S),
         "4 \u00d7 10\u00d75\u00d75 \u043c\u043c N52 \u2014 \u0431\u0456\u043b\u044f \u043a\u043e\u0436\u043d\u043e\u0433\u043e \u043a\u043e\u043b\u0435\u0441\u0430",
         14, "semi", ACCENT, anchor="mm")
"""
assert old_wheels in src
src = src.replace(old_wheels, new_wheels)

# 4. sensor bar sits ON the blade: move it to the blade plane
old_bar = """    dr.rectangle([ox, oy - 74, ox + L, oy - 60], fill=(250, 246, 224), outline=AMBER, width=2)
    for i in range(8):
        sx = ox + (10 + i * 25.7) * S
        dr.ellipse([sx - 8, oy - 74, sx + 8, oy - 56], fill=(250, 226, 140), outline=INK, width=1)
"""
new_bar = """    dr.rectangle([ox, oy - 44, ox + L, oy - 34], fill=(250, 246, 224), outline=AMBER, width=2)
    for i in range(8):
        sx = ox + (12 + i * 25.2) * S
        dr.ellipse([sx - 8, oy - 45, sx + 8, oy - 33], fill=(250, 226, 140), outline=INK, width=1)
"""
assert old_bar in src
src = src.replace(old_bar, new_bar)

# 5. move the blade label up so it does not sit on the sensors
src = src.replace(
    'text(dr, (ox + L / 2, oy - 26), "\u043a\u043b\u0438\u043d: \u0456\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u0430 \u0441\u0442\u0430\u043b\u044c 3 \u043c\u043c, \u043a\u0443\u0442 12\u00b0",\n         16, "semi", INK, anchor="mm")',
    'text(dr, (ox + L / 2, oy - 26), "\u043a\u043b\u0438\u043d: \u0456\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u0430 \u0441\u0442\u0430\u043b\u044c 3 \u043c\u043c, \u043a\u0443\u0442 12\u00b0",\n         16, "semi", INK, anchor="mm")\n    text(dr, (ox + L + 26, oy - 40), "\u0441\u0435\u043d\u0441\u043e\u0440\u0438 \u043d\u0430 \u043f\u043b\u0430\u043d\u0446\u0438\u0440\u0456 \u043a\u043b\u0438\u043d\u0430", 14, "semi", AMBER, anchor="lm")')

open(PATH, "w", encoding="utf-8").write(src)
print("patched")
