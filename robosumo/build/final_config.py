"""Exact operating points for the 3 kg magnetic MegaSumo finalists (verified, no variable bugs)."""

G = 9.81
MU = 1.0
KGCM_TO_NM = 0.0980665
R_TERM = 0.35          # ohm, 37D terminal resistance (approx)

# Pololu 37D 24 V 100:1 : 39 kg.cm stall, 100 rpm no-load @24 V, 3.0 A stall
STALL_KGCM, RPM0, I_STALL, V_NOM = 39.0, 100.0, 3.0, 24.0


def point(pack, volts, robot_kg, downforce_kgf, wheel_mm, n_motors=4):
    scale = volts / V_NOM
    stall_kgcm = STALL_KGCM * scale
    rpm_nl = RPM0 * scale
    radius = wheel_mm / 2000.0
    n_tot = robot_kg * G + downforce_kgf * G
    f_traction = MU * n_tot
    t_each = f_traction * radius / n_motors
    load = t_each / (stall_kgcm * KGCM_TO_NM)
    i_each = I_STALL * load
    rpm = rpm_nl * (1 - load)
    v = rpm * 3.14159265 * (wheel_mm / 1000.0) / 60.0
    heat = i_each ** 2 * R_TERM
    # time to cross the 154 cm dohyo diameter
    t_cross = 1.54 / v if v > 0 else float("inf")
    return dict(pack=pack, volts=volts, stall_kgcm=stall_kgcm, rpm_nl=rpm_nl,
                n_tot=n_tot, f_traction=f_traction, t_each_kgcm=t_each / KGCM_TO_NM,
                load=load, i_each=i_each, i_total=i_each * n_motors,
                rpm=rpm, v=v, heat_each=heat, t_cross=t_cross)


print("=" * 100)
print("FINALISTS - 4 x Pololu 37D 24V 100:1, 4WD, 3 kg robot")
print("=" * 100)
print(f"{'pack':<5}{'downf':>7}{'wheel':>6}{'T/whl':>8}{'load':>7}{'A/mot':>7}"
      f"{'A tot':>7}{'m/s':>7}{'W/mot':>7}{'cross154':>10}")
print("-" * 100)

finalists = [
    ("6S", 22.2, 15, 50),
    ("6S", 22.2, 20, 50),
    ("6S", 22.2, 25, 50),
    ("6S", 22.2, 20, 60),
    ("7S", 25.9, 20, 50),
    ("7S", 25.9, 15, 60),
    ("8S", 29.6, 20, 50),
    ("8S", 29.6, 25, 60),
]
rows = []
for pack, volts, df, wheel in finalists:
    p = point(pack, volts, 3.0, df, wheel)
    rows.append(p)
    print(f"{p['pack']:<5}{df:>7}{wheel:>6}{p['t_each_kgcm']:>8.1f}"
          f"{p['load']*100:>6.0f}%{p['i_each']:>7.2f}{p['i_total']:>7.1f}"
          f"{p['v']:>7.2f}{p['heat_each']:>7.1f}{p['t_cross']:>9.2f}s")

print("\n" + "=" * 100)
print("RECOMMENDED: 6S, 20 kgf downforce, 50 mm wheels")
print("=" * 100)
p = point("6S", 22.2, 3.0, 20, 50)
print(f"  Applied voltage        : {p['volts']} V  ({p['pack']}, 1.25x overvolt on a 24 V motor)")
print(f"  Stall torque per motor : {p['stall_kgcm']:.1f} kg.cm")
print(f"  No-load speed          : {p['rpm_nl']:.0f} rpm  ->  {p['rpm_nl']*3.14159*0.05/60:.2f} m/s")
print(f"  Total normal force     : {p['n_tot']:.0f} N  (3 kg + 20 kgf magnets)")
print(f"  Traction available     : {p['f_traction']:.0f} N  at mu = {MU}")
print(f"  Torque per wheel       : {p['t_each_kgcm']:.1f} kg.cm")
print(f"  Motor load             : {p['load']*100:.0f}% of stall")
print(f"  Current                : {p['i_each']:.2f} A/motor, {p['i_total']:.1f} A total")
print(f"  Speed under full load  : {p['v']:.2f} m/s")
print(f"  Copper loss per motor  : {p['heat_each']:.1f} W")
print(f"  Cross the dohyo (154 cm): {p['t_cross']:.2f} s")

print("\n  --- duty-cycle check for an 'until knockout' format ---")
heat = p['heat_each']
for duty in (1.0, 0.5, 0.25):
    avg = heat * duty
    print(f"    at {duty*100:>3.0f}% duty: {avg:>5.2f} W average per motor")
print("    a 37D in free air dissipates roughly 5-8 W before the case gets painful,")
print("    so 50% duty at this operating point is inside the survivable band.")

print("\n" + "=" * 100)
print("MAGNET BILL (k = 8-10 N per gram of N52 at 0.4-0.5 mm gap)")
print("=" * 100)
for df in (15, 20, 25):
    need = df * G
    print(f"  {df} kgf = {need:.0f} N  ->  {need/10:.1f}-{need/8:.1f} g of N52")
print("\n  Practical array for 20 kgf (target ~196 N):")
print("    2 x 20x20x5 mm N52 blocks = 36 g  -> 290-360 N at k=8-10 ... 1.5-1.8x margin")
print("    4 x 20x20x3 mm N52 blocks = 43 g  -> similar, thinner, fits under a low chassis")
print("    40 x 5x5x5 mm N52 cubes   = 38 g  -> best for a Halbach array")
