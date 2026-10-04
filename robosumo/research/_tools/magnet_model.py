#!/usr/bin/env python
"""Magnet downforce model for a magnetic robot-sumo dohyo.

Physics
-------
Magnetic circuit (NovaSolver closed form, K&J-style):
    B_gap = Br * (t/g) / ((t/g) + 1)              [t = magnet thickness along
                                                   the magnetising axis,
                                                   g = total air gap]
Maxwell stress (this IS the standard result, also quoted verbatim in
Lapinska et al. IJMERR 9(5) 2020 eq.1):
    F = B_gap^2 * A / (2 * mu0)                   [A = pole face area]

Reality corrections fitted to published measurements:
    1. Fringing/leakage: 20-50 % of flux escapes sideways (NovaSolver).
    2. The steel target saturates: B in steel caps at ~1.6 T (SS400) to
       ~2.1 T (pure iron), so B_gap can never exceed that in practice.
    3. Real arrays do not put all poles at the nominal gap.
We therefore report a *bracket*: ideal maxwell stress vs a leakage-derated
value, and compare both to measured literature values.
"""
import math

MU0 = 4.0 * math.pi * 1e-7          # H/m
G0 = 9.80665                        # m/s^2


def b_gap_ideal(Br, t_mm, g_mm):
    """Air-gap flux density from the simple magnetic-circuit ratio."""
    if g_mm <= 0:
        return Br
    r = t_mm / g_mm
    return Br * r / (r + 1.0)


def flux_density_saturated(Br, t_mm, g_mm, B_sat=1.6):
    """Same, but clamped by the saturation of the steel return path."""
    return min(b_gap_ideal(Br, t_mm, g_mm), B_sat)


def force_N(B, A_mm2):
    """Maxwell stress force, N. A in mm^2."""
    A = A_mm2 * 1e-6
    return B * B * A / (2.0 * MU0)


def report(name, Br, t_mm, A_mm2, mass_g, gaps, k_leak=1.0, B_sat=1.6):
    print(f"\n=== {name}  Br={Br} T, t={t_mm} mm, A={A_mm2} mm^2, m={mass_g} g "
          f"(k_leak={k_leak}, B_sat={B_sat} T) ===")
    print(f"{'gap mm':>7} {'B_ideal T':>10} {'B_sat T':>8} "
          f"{'F_ideal N':>10} {'F_ideal kgf':>12} {'F_derated N':>12} "
          f"{'F/mass N/g':>11}")
    for g in gaps:
        Bi = b_gap_ideal(Br, t_mm, g)
        Bs = flux_density_saturated(Br, t_mm, g, B_sat)
        Fi = force_N(Bi, A_mm2)
        Fd = force_N(Bs, A_mm2) * k_leak
        print(f"{g:7.2f} {Bi:10.3f} {Bs:8.3f} {Fi:10.2f} "
              f"{Fi/G0:12.3f} {Fd:12.2f} {Fd/mass_g:11.3f}")


print("#" * 78)
print("# PART 1 - SINGLE MAGNETS (commercially available sumo sizes)")
print("#" * 78)

gaps = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]

# JSumo N52 block 10 x 5 x 15 mm, 10 g, vendor claim 4 kgf @ zero gap / 3 mm steel
report("JSumo N52 block 10x5x15 mm", 1.43, 5.0, 10 * 15, 10.0, gaps)
# JSumo N52 block 20 x 20 x 5 mm, 18 g, vendor claim 8 kgf @ zero gap / 3 mm steel
report("JSumo N52 block 20x20x5 mm", 1.43, 5.0, 20 * 20, 18.0, gaps)
# The 5x5x5 N52 cubes used by the Polish MegaSumo team (IJMERR 2020/2021)
report("N52 cube 5x5x5 mm", 1.47, 5.0, 5 * 5, 0.94, gaps)
# 10x5 mm N52 disc, t = 5 mm
report("N52 disc D10x5 mm", 1.43, 5.0, math.pi * 25, 1.5, gaps)

print("\n" + "#" * 78)
print("# PART 2 - GAP RATIO: how force falls with distance (same magnet)")
print("#" * 78)
# JSumo 20x20x5 N52 block
base = None
print(f"{'gap mm':>7} {'F_ideal N':>10} {'ratio to 0.1mm':>16} "
      f"{'ratio to 0.5mm':>16} {'ratio to 1.0mm':>16}")
Q = 0.1
Fq = force_N(flux_density_saturated(1.43, 5.0, Q), 400)
F05 = force_N(flux_density_saturated(1.43, 5.0, 0.5), 400)
F10 = force_N(flux_density_saturated(1.43, 5.0, 1.0), 400)
for g in [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0]:
    F = force_N(flux_density_saturated(1.43, 5.0, g), 400)
    print(f"{g:7.2f} {F:10.2f} {F/Fq:16.3f} {F/F05:16.3f} {F/F10:16.3f}")

print("\n" + "#" * 78)
print("# PART 3 - RATIO-BASED ESTIMATE (no Br needed): F(g2)/F(g1)")
print("#   F ~ B^2 and B ~ (t/g)/((t/g)+1)  =>  ratio depends only on t,g")
print("#" * 78)
for t in (3.0, 5.0, 8.0, 10.0):
    b05 = b_gap_ideal(1.0, t, 0.5)
    b10 = b_gap_ideal(1.0, t, 1.0)
    b20 = b_gap_ideal(1.0, t, 2.0)
    print(f"t={t:4.1f} mm : F(0.5mm)/F(0.1mm)="
          f"{(b_gap_ideal(1.0,t,0.5)/b_gap_ideal(1.0,t,0.1))**2:5.3f}  "
          f"F(1mm)/F(0.5mm)={(b10/b05)**2:5.3f}  "
          f"F(2mm)/F(1mm)={(b20/b10)**2:5.3f}")

print("\n" + "#" * 78)
print("# PART 4 - CROSS-CHECK vs PUBLISHED MEASUREMENTS")
print("#" * 78)

print("\n[4a] Lapinska et al., IJMERR 9(5) 2020 Tables II & III")
print("     N52 5x5x5 mm cubes, COMSOL + MTS 858 pull-off, mean per magnet:")
hal200 = {0.1: 2624.658, 0.2: 2320.612, 0.3: 2072.31, 0.4: 1863.806,
          0.5: 1684.514, 0.6: 1527.466, 0.7: 1389.044, 0.8: 1266.126,
          0.9: 1156.353, 1.0: 1057.622}
alt200 = {0.1: 1588.905, 0.2: 1308.324, 0.3: 1093.866, 0.4: 924.885,
          0.5: 787.9425, 0.6: 674.2686, 0.7: 579.3249, 0.8: 499.4286,
          0.9: 431.6223, 1.0: 373.4322}
print(f"{'gap mm':>7} {'Halbach/mag N':>14} {'Alt.pol/mag N':>14} "
      f"{'Halbach/Alt':>12} {'F/mass N/g':>11}")
for g in sorted(hal200):
    h = hal200[g] / 200.0
    a = alt200[g] / 200.0
    print(f"{g:7.2f} {h:14.2f} {a:14.2f} {h/a:12.3f} {h/0.94:11.3f}")

print("\n     Same paper, 100-magnet Halbach set (Halbach/magnet identical):")
hal100 = {0.1: 1283.787, 0.2: 1133.0102, 0.3: 1010.226, 0.4: 907.3274,
          0.5: 819.075, 0.6: 741.9446, 0.7: 674.0602, 0.8: 613.9076,
          0.9: 560.0664, 1.0: 512.0408}
for g in sorted(hal100):
    print(f"       g={g:4.2f} mm -> {hal100[g]/100.0:6.2f} N/magnet "
          f"({hal100[g]/100.0/G0:5.3f} kgf/magnet)")

print("\n[4b] Dziubek et al., IJMERR 10(6) 2021 - MEASURED, 60 magnets Halbach")
F60 = 846.0
print(f"     846 N total / 60 magnets = {F60/60:.2f} N/magnet "
      f"= {F60/60/G0:.3f} kgf/magnet  (3 kg robot -> {F60/G0:.1f} kgf)")
F60e = 1333.86
print(f"     with 2 electromagnets ON: 1333.86 N = {F60e/G0:.1f} kgf; "
      f"delta {F60e-F60:.2f} N = {(F60e-F60)/G0:.1f} kgf "
      f"({(F60e-F60)/2/G0:.1f} kgf per electromagnet), +37 %")

print("\n[4c] Soares et al. ABCM CREEM 2014 / JMEA 5(2015) - N42 ring "
      "OD40 / ID6 / t10 mm")
# ring pole area
A_ring = math.pi / 4 * (40**2 - 6**2)
print(f"     ring pole area = {A_ring:.1f} mm^2 = {A_ring/100:.2f} cm^2")
print("     K&J pull force reported: 46.18 lb = 20.94 kgf = 205.4 N")
print(f"     implied mean B over the annulus = "
      f"{math.sqrt(2*MU0*205.4/(A_ring*1e-6)):.3f} T")
print("     6 magnets -> claimed 40x the robot's own weight")
for n in (6,):
    print(f"     {n} magnets x 20.94 kgf = {n*20.94:.1f} kgf "
          f"({n*205.4:.0f} N) = {n*20.94/3:.1f}x a 3 kg robot's weight")

print("\n[4d] Vendor claims vs model (maxwell stress upper bound)")
for nm, claim_kgf, Br, t, A, m in [
        ("JSumo N52 10x5x15 block", 4.0, 1.43, 5.0, 150.0, 10.0),
        ("JSumo N52 20x20x5 block", 8.0, 1.43, 5.0, 400.0, 18.0)]:
    Fc = claim_kgf * G0
    Bimpl = math.sqrt(2 * MU0 * Fc / (A * 1e-6))
    Fmax = force_N(min(Br, 2.1), A)
    print(f"  {nm}: claim {claim_kgf} kgf = {Fc:.1f} N -> implied B = "
          f"{Bimpl:.3f} T")
    print(f"      absolute Maxwell ceiling at B=Br={Br} T would be "
          f"{force_N(Br, A):.1f} N = {force_N(Br,A)/G0:.1f} kgf")
    print(f"      force per unit mass = {Fc/m:.1f} N/g")

print("\n" + "#" * 78)
print("# PART 5 - REQUIRED MAGNET MASS FOR A TARGET DOWNFORCE")
print("#" * 78)
print("Calibrated working numbers from measurement, N per gram of N52:")
for label, Ftot, n, mm in [
        ("IJMERR2020 Halbach 200 @1.0mm gap", hal200[1.0], 200, 0.94),
        ("IJMERR2020 Halbach 200 @0.5mm gap", hal200[0.5], 200, 0.94),
        ("IJMERR2020 AltPol 200 @1.0mm gap", alt200[1.0], 200, 0.94),
        ("IJMERR2021 measured 60 @~0 gap", 846.0, 60, 0.94)]:
    m_tot = n * mm
    print(f"  {label:38s}: {Ftot:8.1f} N / {m_tot:7.1f} g = "
          f"{Ftot/m_tot:6.2f} N/g")
print("\nEstimate: mass of N52 needed for a target downforce (use 10-15 N/g):")
for target_kgf in (10, 20, 30, 50, 80):
    target_N = target_kgf * G0
    print(f"  {target_kgf:3d} kgf = {target_N:6.1f} N -> "
          f"{target_N/10:6.1f} g @10 N/g   {target_N/15:6.1f} g @15 N/g")

print("\n" + "#" * 78)
print("# PART 6 - TRACTION: what downforce buys you")
print("#" * 78)
print("F_traction = mu * N_total, N_total = m_robot*g + F_magnets")
print(f"{'robot kg':>9} {'extra kgf':>10} {'mu':>5} {'N_total N':>10} "
      f"{'traction N':>11} {'equiv. mass kg':>15}")
for m_r in (1.0, 3.0):
    for extra in (0, 10, 30, 50, 80):
        for mu in (0.7, 1.0):
            Ntot = m_r * G0 + extra * G0
            print(f"{m_r:9.1f} {extra:10.0f} {mu:5.1f} {Ntot:10.1f} "
                  f"{mu*Ntot:11.1f} {mu*Ntot/G0:15.1f}")
