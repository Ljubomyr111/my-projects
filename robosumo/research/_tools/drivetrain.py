#!/usr/bin/env python
"""Drivetrain sizing for a magnetic-dohyo sumo robot.

Formulas used
-------------
Traction limit          F_max = mu * N_total,  N_total = m_robot*g + F_magnets
Wheel torque needed     T_wheel = F_max * r
Speed                   v = RPM * pi * D / 60
Motor torque at wheel   T_wheel = T_motor * ratio * eta
Stopping/travel         d = v * t
"""
import math

G0 = 9.80665


def v_from_rpm(rpm, D_mm):
    return rpm * math.pi * (D_mm / 1000.0) / 60.0


def rpm_for_v(v, D_mm):
    return v * 60.0 / (math.pi * (D_mm / 1000.0))


print("#" * 78)
print("# A. SPEED vs WHEEL DIAMETER at fixed motor output RPM")
print("#" * 78)
Ds = [30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90]
rpms = [100, 150, 200, 250, 300, 400, 500, 600, 750, 1000, 1450, 2000]
print(f"{'RPM':>6} " + " ".join(f"{d:>6}mm" for d in Ds))
for rpm in rpms:
    row = " ".join(f"{v_from_rpm(rpm,d):6.2f}" for d in Ds)
    print(f"{rpm:6d} {row}   (m/s)")

print("\nRPM needed for a target speed:")
print(f"{'target m/s':>11} " + " ".join(f"{d:>6}mm" for d in [40, 50, 60, 75, 90]))
for v in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.5):
    row = " ".join(f"{rpm_for_v(v,d):6.0f}" for d in [40, 50, 60, 75, 90])
    print(f"{v:11.1f} {row}")

print("\n" + "#" * 78)
print("# B. WHEEL TORQUE REQUIRED TO BREAK TRACTION (drive limit)")
print("#" * 78)
print("T_wheel = mu * (m*g + F_mag) * r   [N.m]   ;  1 N.m = 10.197 kg.cm")
print(f"{'robot kg':>8} {'Fmag kgf':>9} {'mu':>5} {'N_tot N':>9} "
      f"{'F_max N':>9} " + " ".join(f"{d:>8}" for d in [30, 40, 50, 60, 75]))
print(" " * 44 + " ".join(f"{'D='+str(d):>8}" for d in [30, 40, 50, 60, 75]))
print(" " * 44 + " ".join(f"{'kg.cm':>8}" for _ in range(5)))
for m_r in (1.0, 3.0):
    for Fmag_kgf in (0, 10, 30, 50, 80):
        for mu in (0.7, 1.0):
            N = m_r * G0 + Fmag_kgf * G0
            F = mu * N
            row = " ".join(f"{F*(d/2000.0)*10.197:8.1f}" for d in [30, 40, 50, 60, 75])
            print(f"{m_r:8.1f} {Fmag_kgf:9.0f} {mu:5.1f} {N:9.1f} {F:9.1f} {row}")

print("\n" + "#" * 78)
print("# C. WHICH MOTOR/GEAR RATIO? ")
print("#   T_wheel = T_motor_stall * ratio * eta   (eta = 0.75 for spur gearbox)")
print("#" * 78)
KGCM = 0.0980665  # N.m per kg.cm
motors = [
    # name, stall torque at OUTPUT shaft [kg.cm], no-load output rpm
    ("Pololu 37D 12V 19:1",   8.5, 530),
    ("Pololu 37D 12V 30:1",   14.0, 330),
    ("Pololu 37D 12V 50:1",   21.0, 200),
    ("Pololu 37D 12V 70:1",   27.0, 150),
    ("Pololu 37D 12V 100:1",  34.0, 100),
    ("Pololu 37D 24V 50:1",   23.0, 200),
    ("Pololu 37D 24V 100:1",  39.0, 100),
    ("JSumo Titan 12V 1000rpm", 7.5, 1000),
    ("JSumo Symtec Q 9.28:1", 44.0, 1450),
    ("Maxon DCX35L 24V (no gb)", 20.7, 7720),
]
print("NOTE: T listed is the torque at the gearbox OUTPUT shaft, so the gear")
print("      ratio is already inside it. Wheels mount straight on the shaft.")
print(f"{'motor':>26} {'T_out N.m':>10} {'RPM_out':>8} "
      + " ".join(f"{d:>7}mm" for d in [40, 50, 60]))
for name, T_kgcm, rpm in motors:
    T = T_kgcm * KGCM
    row = " ".join(f"{v_from_rpm(rpm,d):7.2f}" for d in [40, 50, 60])
    print(f"{name:>26} {T:10.3f} {rpm:8.0f} {row}   (m/s)")
print("\nPulling force available at the wheel (F = T/r), N  [both wheels]")
print(f"{'motor':>26} " + " ".join(f"{d:>7}mm" for d in [40, 50, 60]))
for name, T_kgcm, rpm in motors:
    T = T_kgcm * KGCM
    row = " ".join(f"{T/(d/2000.0):7.1f}" for d in [40, 50, 60])
    print(f"{name:>26} {row}")
print("\nPeak mechanical power at half stall (W) = T_stall*omega_noload/4:")
for name, T_kgcm, rpm in motors:
    T = T_kgcm * KGCM
    w = rpm * 2 * math.pi / 60.0
    print(f"  {name:>26}: {T*w/4.0:6.1f} W")

print("\n" + "#" * 78)
print("# D. THE KEY TRADEOFF: downforce vs speed")
print("#   Speed with all traction used for acceleration:")
print("#     a = mu*(g + Fmag/m),  t_to_v = v/a,  d = v^2/(2a)")
print("#" * 78)
print(f"{'Fmag kgf':>9} {'mu':>5} {'a m/s2':>8} {'t->1m/s ms':>11} "
      f"{'t->3m/s ms':>11} {'d@3m/s m':>9} {'d@1m/s mm':>10}")
for Fmag in (0, 5, 10, 20, 30, 50, 80):
    for mu in (0.7, 1.0):
        a = mu * G0 * (1 + Fmag / 3.0)   # 3 kg robot
        t1 = 1.0 / a
        t3 = 3.0 / a
        d3 = 9.0 / (2 * a)
        d1 = 1.0 / (2 * a)
        print(f"{Fmag:9.0f} {mu:5.1f} {a:8.1f} {t1*1000:11.1f} {t3*1000:11.1f} "
              f"{d3:9.3f} {d1*1000:10.1f}")

print("\n" + "#" * 78)
print("# E. SENSOR / LOOP LATENCY -> DISTANCE TRAVELLED")
print("#   d = v * t")
print("#" * 78)
vs = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.5]
ts = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
print(f"{'v m/s':>6} " + " ".join(f"{t*1000:>7.2f}ms" for t in ts))
for v in vs:
    print(f"{v:6.1f} " + " ".join(f"{v*t*1000:8.1f}" for t in ts) + "   (mm)")

print("\n" + "#" * 78)
print("# F. DOWNFORCE vs GROUND CLEARANCE COST (magnet drag on dohyo)")
print("#   magnet must clear the dohyo by g; gap change dg changes F by dF/F")
print("#" * 78)
MU0 = 4 * math.pi * 1e-7
def F_of_gap(Br, t, A_mm2, g):
    r = t / g
    B = min(Br * r / (r + 1), 1.6)
    return B * B * (A_mm2 * 1e-6) / (2 * MU0)
print("Using the 20x20x5 N52 block (A=400 mm^2), F in N:")
print(f"{'gap mm':>7} {'F N':>8} {'dF/F per +0.1mm':>18}")
prev = None
for g in [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0]:
    F = F_of_gap(1.43, 5.0, 400.0, g)
    F2 = F_of_gap(1.43, 5.0, 400.0, g + 0.1)
    print(f"{g:7.2f} {F:8.1f} {100*(F2-F)/F:17.1f}%")

print("\n" + "#" * 78)
print("# G. WORKED DESIGN POINTS")
print("#" * 78)
designs = [
    ("1 kg minisumo, 500 g magnets", 1.0, 0.5, 0.9, 40),
    ("3 kg megasumo, 1.5 kg magnets", 3.0, 1.5, 0.9, 50),
    ("3 kg megasumo, 0.5 kg magnets", 3.0, 0.5, 0.9, 50),
]
for name, m_r, m_mag, mu, D in designs:
    # N52 ~ 10 N/g at 0.5 mm gap in a good Halbach array
    Fmag = m_mag * 1000 * 10.0
    N = m_r * G0 + Fmag
    F = mu * N
    T = F * (D / 2000.0)
    a = F / m_r
    print(f"\n{name}")
    print(f"  magnet mass {m_mag*1000:.0f} g -> est. downforce {Fmag:.0f} N "
          f"= {Fmag/G0:.1f} kgf")
    print(f"  N_total = {N:.0f} N ({N/G0:.1f} kgf); traction @mu={mu}: {F:.0f} N")
    print(f"  wheel D={D} mm -> T_wheel = {T:.2f} N.m = {T*10.197:.0f} kg.cm "
          f"PER WHEEL if 2WD split is 50/50")
    print(f"  equiv. acceleration if traction fully used = {a:.1f} m/s^2 "
          f"({a/G0:.1f} g)")
    print(f"  time to 1 m/s = {1000/a:.0f} ms; travel in first 200 ms = "
          f"{0.5*a*0.2**2*1000:.0f} mm")
    print(f"  ring crossing time (154 cm dohyo, straight line) at 2 m/s = "
          f"{1.54/2.0*1000:.0f} ms")
