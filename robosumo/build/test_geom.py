"""Validate the voxel mesher against analytic volumes."""
import sys

import numpy as np

sys.path.insert(0, r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build")
import geom3d as g


def check(name, F, grid, expected, tol=0.06, pitch=None):
    v, t = g.voxel_mesh(F, grid, pitch=pitch)
    vol = g.mesh_volume(v, t)
    ne, lo, hi = g.edge_stats(v, t)
    closed = (lo == 2 and hi == 2)
    err = abs(abs(vol) - expected) / expected if expected else 0.0
    ok = (err <= tol) and closed and vol > 0
    print(f"{'OK ' if ok else 'BAD'} {name:<26} vol={vol:9.2f} exp={expected:9.2f} "
          f"err={err*100:5.1f}% tris={len(t):6d} edges=[{lo},{hi}] "
          f"{'closed' if closed else 'OPEN'}{'' if vol > 0 else ' WINDING'}")
    return v, t


P = 0.4


def mk(bounds, pitch=P):
    gr = g.Grid(bounds, pitch)
    X, Y, Z = gr.coords()
    return gr, np.stack([X, Y, Z], axis=-1)


gr, Q = mk(((-2, -2, -2), (22, 12, 7)))
b = g.box(Q, (10, 5, 2.5), (20, 10, 5))

check("box 20x10x5", b, gr, 20 * 10 * 5, tol=0.02)
check("box - hole d6 (z)", g.subtract(b, g.cylinder(Q, (10, 5, 2.5), 3.0, 30)), gr,
      20 * 10 * 5 - np.pi * 9 * 5, tol=0.06)
check("box - side hole d4 (x)", g.subtract(b, g.cylinder(Q, (10, 5, 2.5), 2.0, 40, axis=0)), gr,
      20 * 10 * 5 - np.pi * 4 * 10, tol=0.06)
check("4 holes d3", g.subtract(b, g.union(
    g.cylinder(Q, (4, 4, 2.5), 1.5, 30), g.cylinder(Q, (4, 6, 2.5), 1.5, 30),
    g.cylinder(Q, (16, 4, 2.5), 1.5, 30), g.cylinder(Q, (16, 6, 2.5), 1.5, 30))), gr,
      20 * 10 * 5 - 4 * np.pi * 2.25 * 5, tol=0.08)

gr2, Q2 = mk(((-2, -2, -2), (22, 22, 12)))
check("cylinder d20 h10", g.cylinder(Q2, (10, 10, 5), 10, 10), gr2,
      np.pi * 100 * 10, tol=0.04)
check("hex across-flats 15.5", g.hexprism(Q2, (10, 10, 5), 15.5, 10), gr2,
      2 * (15.5 ** 2) / (2 * np.sqrt(3)) * 10, tol=0.06)

check("L bracket", g.union(g.box(Q, (10, 5, 5), (20, 3, 10)),
                           g.box(Q, (1.5, 5, 5), (3, 10, 10))), gr,
      20 * 3 * 10 + 3 * 10 * 10 - 3 * 3 * 10, tol=0.03)

print("\ncoarse pitch decimation (0.8 mm):")
check("box 20x10x5 @0.8", b, gr, 20 * 10 * 5, tol=0.10, pitch=0.8)
