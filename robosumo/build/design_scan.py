"""Design-space scan for the 3 kg magnetic MegaSumo robot.

Constraints (confirmed by the organisers):
  * class 3 kg, footprint 20 x 20 cm, height unlimited, dimensions MAY change after start
  * steel dohyo d = 154 cm, permanent magnets allowed
  * match runs UNTIL KNOCKOUT -> no time limit -> thermal duty matters
  * free construction, parts budget cap $500

Goal: pick a drivetrain + magnet budget that is traction-safe, thermally
survivable, and fast enough to actually win exchanges.
"""

MOTORS = {
    # name: (stall torque kg.cm, no-load rpm, stall current A, voltage, price USD)
    "37D 12V 100:1": (34, 100, 5.5, 12, 34),
    "37D 12V 70:1":  (27, 150, 5.5, 12, 34),
    "37D 12V 50:1":  (21, 200, 5.5, 12, 37),
    "37D 24V 100:1": (39, 100, 3.0, 24, 40),
    "37D 24V 50:1":  (21, 200, 3.0, 24, 40),
}

G = 9.81
MU = 1.0          # rubber/urethane on steel, optimistic-but-documented bound
KGCM_TO_NM = 0.0980665


def analyse(robot_kg, downforce_kgf, wheel_mm, motor, n_motors):
    """Return the key numbers for one design point."""
    stall_kgcm, rpm0, i_stall, volt, price = MOTORS[motor]
    r = wheel_mm / 2000.0                       # radius in metres
    n_total = robot_kg * G + downforce_kgf * G  # normal force on the arena
    f_traction = MU * n_total                   # max usable push force
    t_need_total = f_traction * r               # torque to use ALL of it
    t_need_each = t_need_total / n_motors
    t_stall_nm = stall_kgcm * KGCM_TO_NM
    load_frac = (t_need_each / t_stall_nm) if t_stall_nm else 99
    i_each = i_stall * load_frac
    rpm_at = rpm0 * (1 - load_frac)
    v = rpm_at * 3.14159265 * (wheel_mm / 1000.0) / 60.0
    p_heat_each = i_each ** 2 * 0.35            # ~0.35 ohm 37D terminal resistance
    return dict(
        n_total=n_total, f_traction=f_traction,
        t_each_kgcm=t_need_each / KGCM_TO_NM, t_each_nm=t_need_each,
        load_frac=load_frac, i_each=i_each, i_total=i_each * n_motors,
        rpm=rpm_at, v=v, heat_each=p_heat_each,
        motor_cost=price * n_motors,
    )


def verdict(d):
    """Thermal + traction verdict for the 'until knockout' format."""
    notes = []
    if d["load_frac"] <= 0.25:
        notes.append("THERMAL OK (<=25% stall, Pololu recommendation)")
    elif d["load_frac"] <= 0.50:
        notes.append("thermal WARN (25-50% stall) - needs heatsink + duty limit")
    else:
        notes.append("thermal FAIL (>50% stall)")
    if d["v"] < 0.25:
        notes.append("too slow")
    elif d["v"] > 1.2:
        notes.append("very fast")
    return notes


print("=" * 108)
print("DESIGN SCAN - 3 kg, 4WD, traction-limited torque requirement")
print("=" * 108)
print(f"{'motor':<16}{'wheel':>6}{'downf':>7}{'T/wheel':>10}{'load%':>7}"
      f"{'A/mot':>7}{'A tot':>7}{'m/s':>7}{'W/mot':>7}  verdict")
print("-" * 108)

best = []
for motor in MOTORS:
    for wheel in (30, 40, 50, 60):
        for df in (10, 15, 20, 25, 30):
            d = analyse(3.0, df, wheel, motor, 4)
            v = verdict(d)
            line = (f"{motor:<16}{wheel:>6}{df:>7}{d['t_each_kgcm']:>10.1f}"
                    f"{d['load_frac']*100:>6.0f}%{d['i_each']:>7.2f}"
                    f"{d['i_total']:>7.1f}{d['v']:>7.2f}{d['heat_each']:>7.1f}  "
                    + "; ".join(v))
            if "THERMAL OK" in " ".join(v) and "too slow" not in v:
                best.append((motor, wheel, df, d))
                print(line + "   <== VIABLE")
            elif "THERMAL OK" in " ".join(v):
                print(line + "   (slow)")
print("-" * 108)

print("\nVIABLE DESIGN POINTS (thermally safe at 25% stall AND >= 0.25 m/s):")
print(f"{'motor':<16}{'wheel':>6}{'downf':>7}{'speed':>8}{'T/wheel':>10}{'motors $':>10}")
for motor, wheel, df, d in best:
    print(f"{motor:<16}{wheel:>6}{df:>7}{d['v']:>8.2f}{d['t_each_kgcm']:>10.1f}"
          f"{d['motor_cost']:>10.0f}")
if not best:
    print("  (none - relaxing to <=50% stall)")

print("\n" + "=" * 108)
print("CHOSEN CONFIGURATION")
print("=" * 108)
chosen = analyse(3.0, 20, 50, "37D 24V 100:1", 4)
for k, val in chosen.items():
    print(f"  {k:<16} {val:,.2f}")
print(f"\n  traction force available : {chosen['f_traction']:.0f} N")
print(f"  push at the blade        : {chosen['t_each_nm']*4/0.025:.0f} N "
      f"(motor-limited, must exceed traction)")
print(f"  verdict                  : {'; '.join(verdict(chosen))}")

print("\n" + "=" * 108)
print("MAGNET BUDGET  (design constant k = 8-10 N per gram of N52 at 0.4-0.5 mm)")
print("=" * 108)
for target_kgf in (10, 15, 20, 25, 30, 40):
    need_n = target_kgf * G
    print(f"  {target_kgf:>3} kgf = {need_n:>6.0f} N  ->  "
          f"{need_n/10:>5.1f} g N52 (k=10)  ...  {need_n/8:>5.1f} g (k=8)")
print("\n  20x20x5 mm N52 block = 18 g each -> "
      f"{20*G/10:.1f} g..{20*G/8:.1f} g of N52 for 20 kgf")
print(f"  = {(20*G/10)/18:.1f} to {(20*G/8)/18:.1f} blocks of 20x20x5")


# ---------------------------------------------------------------------------
# OVERVOLTING: the Japanese answer to "37D gearboxes are too slow".
# Speed and stall torque both scale linearly with applied voltage; heat goes
# with I^2, so the motor must stay well under stall.
# ---------------------------------------------------------------------------
print("\n" + "=" * 108)
print("OVERVOLTING - 37D 24V 100:1 run above nominal (Japanese practice)")
print("=" * 108)
STALL_KGCM, RPM0, I_STALL = 39, 100, 3.0
print(f"{'pack':<8}{'V':>6}{'downf':>7}{'wheel':>6}{'T/wheel':>9}{'load%':>7}"
      f"{'A/mot':>7}{'A tot':>7}{'m/s':>7}{'W/mot':>7}  verdict")
print("-" * 108)

candidates = []
for pack, volts in (("4S", 14.8), ("5S", 18.5), ("6S", 22.2), ("7S", 25.9)):
    scale = volts / 24.0
    stall = STALL_KGCM * scale
    rpm_nl = RPM0 * scale
    for wheel in (40, 50, 60):
        for df in (15, 20, 25, 30, 40):
            radius = wheel / 2000.0
            n_tot = 3.0 * G + df * G
            f_tr = MU * n_tot
            t_each = f_tr * radius / 4
            load = t_each / (stall * KGCM_TO_NM)
            i_e = I_STALL * load
            rpm = rpm_nl * (1 - load)
            v = rpm * 3.14159265 * (wheel / 1000.0) / 60.0
            heat = i_e ** 2 * 0.35
            tag = []
            tag.append("OK" if load <= 0.25 else ("WARN" if load <= 0.50 else "FAIL"))
            if v < 0.28:
                tag.append("slow")
            line = (f"{pack:<8}{volts:>6.1f}{df:>7}{wheel:>6}{t_each/KGCM_TO_NM:>9.1f}"
                    f"{load*100:>6.0f}%{i_e:>7.2f}{i_e*4:>7.1f}{v:>7.2f}{heat:>7.1f}  "
                    + " ".join(tag))
            if load <= 0.35 and v >= 0.28:
                candidates.append((pack, volts, df, wheel, v, t_each, i_e, load, heat))
                print(line + "   <== CANDIDATE")
            else:
                print(line)
print("-" * 108)

print("\nCANDIDATES (load <= 35% stall AND speed >= 0.28 m/s):")
print(f"{'pack':<6}{'downf':>7}{'wheel':>6}{'m/s':>7}{'T/wheel':>9}{'A/mot':>7}{'load%':>7}{'W/mot':>7}")
for c in sorted(candidates, key=lambda x: -x[4]):
    print(f"{c[0]:<6}{c[2]:>7}{c[3]:>6}{c[4]:>7.2f}{c[5]/KGCM_TO_NM:>9.1f}"
          f"{c[6]:>7.2f}{c[7]*100:>6.0f}%{c[8]:>7.1f}")

print("\n" + "=" * 108)
print("SHORTLIST")
print("=" * 108)
for label, pack, df, wheel in (
        ("A - safe, slow",      "4S", 20, 50),
        ("B - recommended",     "6S", 25, 50),
        ("C - fast, hot",       "6S", 25, 60),
):
    scale = {"4S": 14.8, "5S": 18.5, "6S": 22.2, "7S": 25.9}[pack] / 24.0
    stall = STALL_KGCM * scale
    rpm_nl = RPM0 * scale
    radius = wheel / 2000.0
    n_tot = 3.0 * G + df * G
    t_each = MU * n_tot * radius / 4
    load = t_each / (stall * KGCM_TO_NM)
    i_e = I_STALL * load
    v = rpm_nl * (1 - load) * 3.14159265 * (wheel / 1000.0) / 60.0
    print(f"{label:<18} {pack} {df:>2} kgf {wheel} mm -> "
          f"{v:.2f} m/s, {t_each/KGCM_TO_NM:.1f} kg.cm/wheel, "
          f"{load*100:.0f}% stall, {i_e:.2f} A/motor, {i_e*i_e*0.35:.1f} W heat/motor")

