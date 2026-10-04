"""Validate the grid plate mesher against analytic volumes."""
import sys

import numpy as np

sys.path.insert(0, r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\robosumo\build")
import plate_mesh as p3


def check(name, outer, holes, height, pitch=0.25, tol=0.03):
    v, t = p3.extrude(outer, holes, height, pitch=pitch)
    vol = p3.mesh_volume(v, t)
    ne, lo, hi = p3.edge_stats(t)
    closed = (lo == 2 and hi == 2)
    mask, mx, my, mp = p3.rasterise(outer, holes, pitch)
    area = float(mask.sum()) * mp * mp
    exp = area * height
    err = abs(vol - exp) / exp if exp else 0
    ok = closed and vol > 0 and err < 1e-6
    print(f"{'OK ' if ok else 'BAD'} {name:<28} vol={vol:10.2f} exp={exp:10.2f} "
          f"err={err*100:6.3f}%  tris={len(t):6d} edges=[{lo},{hi}] "
          f"{'closed' if closed else 'OPEN'}{'' if vol > 0 else ' WINDING'}")
    return v, t, area


r = p3.rect(100, 60)
check("rect 100x60x5", r, [], 5.0)

h1 = p3.circle(5.0, 30, 0)
check("rect + 1 hole d10", r, [h1], 4.0)

holes4 = [p3.circle(1.6, x, y) for (x, y) in
          ((-40, -22), (-40, 22), (40, -22), (40, 22))]
check("rect + 4 holes d3.2", r, holes4, 4.0)

rr = p3.rounded_rect(80, 50, 6)
holes3 = [p3.circle(2.5, -25, 0), p3.circle(2.5, 25, 0), p3.circle(8, 0, 0)]
check("rounded rect + 3 holes", rr, holes3, 6.0)

hexp = [(15 * np.cos(np.radians(60 * i)), 15 * np.sin(np.radians(60 * i)))
        for i in range(6)]
check("hex plate + bore d8", hexp, [p3.circle(4.0)], 8.0)

print("\nresolution study on rect 100x60 with a d10 hole (vol should converge):")
for pitch in (0.8, 0.4, 0.25, 0.15):
    v, t = p3.extrude(r, [h1], 4.0, pitch=pitch)
    mask, mx, my, mp = p3.rasterise(r, [h1], pitch)
    vol = p3.mesh_volume(v, t)
    print(f"   pitch={pitch:4.2f}  tris={len(t):6d}  vol={vol:10.2f}")
print(f"   analytic area (rect - circle) = {100*60 - np.pi*25:.3f}")
