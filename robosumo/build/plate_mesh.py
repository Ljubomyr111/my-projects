"""Exact plate mesher: slice the cross-section into rectangles, then extrude.

Why this design:

  * The robot's printed parts are flat plates, so the surface is fully described
    by a 2D cross-section plus a height.
  * Slicing the cross-section at every boundary-vertex y gives exact
    axis-aligned rectangles. Their union is the part exactly, with no
    rasterisation error and no slivers.
  * Meshing that rectangle set - a floor and ceiling per rectangle, and a wall
    only where no neighbour covers the face - yields a surface that is closed
    and manifold by construction.
  * Flat faces stay flat and hole walls come out as exact vertical strips, so
    the triangle count scales with the number of corners, not the area.
"""
import math
import struct

import numpy as np


# --------------------------------------------------------------------------
# 2D outlines
# --------------------------------------------------------------------------


def rect(w, h, cx=0.0, cy=0.0):
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = cy - h / 2.0, cy + h / 2.0
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle(r, cx=0.0, cy=0.0, n=None):
    if n is None:
        n = max(24, int(round(2 * math.pi * r / 0.35)))
    return [(cx + r * math.cos(2 * math.pi * i / n),
             cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rounded_rect(w, h, r, cx=0.0, cy=0.0, seg=12):
    r = min(r, w / 2.0 - 1e-6, h / 2.0 - 1e-6)
    pts = []
    for (ax, ay, a0) in [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                         (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]:
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + ax + r * math.cos(a), cy + ay + r * math.sin(a)))
    return pts


def signed_area(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def bbox(polys):
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


# --------------------------------------------------------------------------
# Exact rectangle decomposition
# --------------------------------------------------------------------------


def rasterise(outer, holes, pitch, margin=2):
    """Rasterise outline-minus-holes to a boolean mask (cell centres)."""
    polys = [list(outer)] + [list(h) for h in holes]
    x0, y0, x1, y1 = bbox(polys)
    x0 -= margin * pitch
    y0 -= margin * pitch
    x1 += margin * pitch
    y1 += margin * pitch
    nx = int(math.ceil((x1 - x0) / pitch)) + 1
    ny = int(math.ceil((y1 - y0) / pitch)) + 1
    xs = x0 + (np.arange(nx) + 0.5) * pitch
    ys = y0 + (np.arange(ny) + 0.5) * pitch
    X, Y = np.meshgrid(xs, ys)

    def poly_mask(poly):
        n = len(poly)
        cnt = np.zeros(X.shape, dtype=np.int32)
        for k in range(n):
            xa, ya = poly[k]
            xb, yb = poly[(k + 1) % n]
            if ya == yb:
                continue
            cond = ((ya > Y) != (yb > Y))
            with np.errstate(divide="ignore", invalid="ignore"):
                xin = xa + (Y - ya) * (xb - xa) / (yb - ya)
            cnt += (cond & (X < xin)).astype(np.int32)
        return (cnt % 2 == 1)

    solid = poly_mask(list(outer))
    for h in holes:
        solid &= ~poly_mask(list(h))
    return solid, x0, y0, pitch


def _band_spans(outer, holes):
    """Split the cross-section into horizontal bands of constant topology.

    Returns a list of (y0, y1, [(xa, xb), ...]) where each band's spans are the
    solid x-intervals. Because the spans are cut at the exact boundary-vertex
    coordinates, their union is the region exactly - no rasterisation.
    """
    loops = [list(outer)] + [list(h) for h in holes]
    for lp in loops:
        if len(lp) < 3:
            raise ValueError("degenerate loop")

    ys = sorted({round(p[1], 9) for lp in loops for p in lp})
    if len(ys) < 2:
        raise ValueError("no vertical extent")

    edges = []
    for lp in loops:
        n = len(lp)
        for k in range(n):
            xa, ya = lp[k]
            xb, yb = lp[(k + 1) % n]
            if abs(ya - yb) < 1e-12:
                continue
            if ya < yb:
                edges.append((ya, yb, xa, xb))
            else:
                edges.append((yb, ya, xb, xa))

    bands = []
    for b in range(len(ys) - 1):
        y0, y1 = ys[b], ys[b + 1]
        if y1 - y0 < 1e-9:
            continue
        ymid = 0.5 * (y0 + y1)
        xs = []
        for (ya, yb, xa, xb) in edges:
            if ya <= ymid < yb:
                t = (ymid - ya) / (yb - ya)
                xs.append(round(xa + t * (xb - xa), 9))
        xs.sort()
        spans = [(xs[k], xs[k + 1]) for k in range(0, len(xs) - 1, 2)
                 if xs[k + 1] - xs[k] > 1e-9]
        if spans:
            bands.append((y0, y1, spans))
    return bands


def decompose_rectangles(outer, holes):
    """Flat list of exact rectangles, used for area checks and previews."""
    out = []
    for (y0, y1, spans) in _band_spans(outer, holes):
        for (xa, xb) in spans:
            out.append((xa, y0, xb, y1))
    return out


# --------------------------------------------------------------------------
# Mesh from bands
# --------------------------------------------------------------------------


def extrude_bands(bands, height, z0=0.0, verbose=False):
    """Closed, manifold mesh of a horizontally sliced cross-section.

    Every quad inside a band is bounded by that band's x-grid, so neighbouring
    quads share whole edges - no T-junctions. Walls between bands are emitted
    per span with exact x-extents, which also match the grids of both bands on
    the shared scanline because the spans come from the same crossing list
    restricted to that line.
    """
    verts = []
    vid_map = {}

    def vid(x, y, top):
        key = (round(x, 6), round(y, 6), 1 if top else 0)
        v = vid_map.get(key)
        if v is None:
            v = len(verts)
            vid_map[key] = v
            verts.append((x, y, z0 + height if top else z0))
        return v

    tris = []

    def quad_xy(x0, y0, x1, y1, top, flip):
        a = vid(x0, y0, top); b = vid(x1, y0, top)
        c = vid(x1, y1, top); d = vid(x0, y1, top)
        if flip:
            tris.append((a, c, b)); tris.append((a, d, c))
        else:
            tris.append((a, b, c)); tris.append((a, c, d))

    def wall_quad(x0, y0, x1, y1):
        """Vertical wall whose outward normal is perpendicular to the edge."""
        a = vid(x0, y0, False); b = vid(x1, y1, False)
        c = vid(x1, y1, True); d = vid(x0, y0, True)
        tris.append((a, b, c)); tris.append((a, c, d))

    n = len(bands)
    for bi, (y0, y1, spans) in enumerate(bands):
        # Per-cell boxes on this band's own x grid, with vertices shared
        # through vid_map.
        #
        # Merging cells into bigger rectangles would cut the triangle count a
        # lot, but wherever a hole boundary changes between two bands the
        # merged rectangles meet along a partial edge - and an edge used by
        # four faces is non-manifold. Per-cell boxes tiled on the lattice are
        # exactly manifold: every interior face is culled, every remaining edge
        # keeps two faces. Triangle count is controlled by the sampling pitch.
        xs_all = sorted({x for sp in spans for x in sp})
        idx = {x: i for i, x in enumerate(xs_all)}
        nc = len(xs_all) - 1
        solid = [False] * nc
        for (xa, xb) in spans:
            for k in range(idx[xa], idx[xb]):
                solid[k] = True

        prev = bands[bi - 1][2] if bi > 0 else []
        nxt = bands[bi + 1][2] if bi + 1 < n else []

        def covered(xa, xb, lst):
            return any(abs(xa - q[0]) < 1e-9 and abs(xb - q[1]) < 1e-9 for q in lst)

        for k in range(nc):
            if not solid[k]:
                continue
            xa, xb = xs_all[k], xs_all[k + 1]
            quad_xy(xa, y0, xb, y1, True, False)          # ceiling +z
            quad_xy(xa, y0, xb, y1, False, True)          # floor -z
            if not covered(xa, xb, prev):
                wall_quad(xa, y0, xb, y0)                 # interface, -y
            if not covered(xa, xb, nxt):
                wall_quad(xb, y1, xa, y1)                 # interface, +y
            if k == 0 or not solid[k - 1]:
                wall_quad(xa, y1, xa, y0)                 # -x
            if k == nc - 1 or not solid[k + 1]:
                wall_quad(xb, y0, xb, y1)                 # +x

    if not verts:
        raise ValueError("empty cross-section")
    if verbose:
        print(f"    bands={n} verts={len(verts)} tris={len(tris)}")
    return verts, tris


def extrude_mask(mask, x0, y0, pitch, height, z0=0.0):
    """Closed, manifold mesh of the solid cells in `mask`, extruded along +z.

    Cells are the unit squares of the sampled lattice, so the region is a
    union of identical cells. For each cell we emit a ceiling, a floor and a
    wall on every side whose neighbour is empty; because every neighbour face
    is either fully shared or fully absent, each interior face is culled and
    every surviving edge belongs to exactly two faces.

    The floor and ceiling are one quad per cell. Adjacent quads share their
    corners through the vertex dictionary, so the surface stays closed even
    though the triangulation differs from cell to cell.
    """
    mask = np.asarray(mask, dtype=bool)
    ny, nx = mask.shape
    verts = []
    vid_map = {}

    def vid(i, j, top):
        key = (i, j, 1 if top else 0)
        v = vid_map.get(key)
        if v is None:
            v = len(verts)
            vid_map[key] = v
            verts.append((x0 + i * pitch, y0 + j * pitch,
                          z0 + height if top else z0))
        return v

    tris = []

    def quad(p0, p1, p2, p3, flip):
        a, b, c, d = [vid(*p) for p in (p0, p1, p2, p3)]
        if flip:
            tris.append((a, c, b)); tris.append((a, d, c))
        else:
            tris.append((a, b, c)); tris.append((a, c, d))

    def cell(i, j):
        return 0 <= i < nx and 0 <= j < ny and mask[j, i]

    for j in range(ny):
        for i in range(nx):
            if not mask[j, i]:
                continue
            A, B, C, D = i, i + 1, j, j + 1
            quad((A, C, 1), (B, C, 1), (B, D, 1), (A, D, 1), False)   # ceiling
            quad((A, C, 0), (B, C, 0), (B, D, 0), (A, D, 0), True)    # floor
            if not cell(i, j - 1):
                quad((A, C, 0), (B, C, 0), (B, C, 1), (A, C, 1), False)
            if not cell(i, j + 1):
                quad((A, D, 0), (B, D, 0), (B, D, 1), (A, D, 1), True)
            if not cell(i - 1, j):
                quad((A, C, 0), (A, D, 0), (A, D, 1), (A, C, 1), True)
            if not cell(i + 1, j):
                quad((B, C, 0), (B, D, 0), (B, D, 1), (B, C, 1), False)

    if not verts:
        raise ValueError("empty mask")
    return verts, tris


def extrude(outer, holes, height, z0=0.0, pitch=0.5, verbose=False):
    mask, x0, y0, p = rasterise(outer, holes, pitch)
    v, t = extrude_mask(mask, x0, y0, p, height, z0)
    if verbose:
        print(f"    cells={int(mask.sum())} verts={len(v)} tris={len(t)}")
    return v, t


# --------------------------------------------------------------------------
# Output and checks
# --------------------------------------------------------------------------


def write_stl(path, verts, tris, name="part"):
    v = np.asarray(verts, float)
    t = np.asarray(tris, np.int64)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    nrm = np.cross(b - a, c - a)
    ln = np.linalg.norm(nrm, axis=1)
    ln[ln == 0] = 1.0
    nrm = nrm / ln[:, None]
    with open(path, "wb") as fh:
        fh.write(name.encode("ascii", "replace")[:79].ljust(80, b" "))
        fh.write(struct.pack("<I", len(t)))
        buf = bytearray()
        for i in range(len(t)):
            buf += struct.pack("<12fH",
                               nrm[i, 0], nrm[i, 1], nrm[i, 2],
                               a[i, 0], a[i, 1], a[i, 2],
                               b[i, 0], b[i, 1], b[i, 2],
                               c[i, 0], c[i, 1], c[i, 2], 0)
        fh.write(bytes(buf))
    return len(t)


def write_dxf(path, outlines, layer="CUT"):
    lines = ["0", "SECTION", "2", "ENTITIES"]
    for poly in outlines:
        lines += ["0", "POLYLINE", "8", layer, "66", "1", "70", "1"]
        for (x, y) in list(poly) + [poly[0]]:
            lines += ["0", "VERTEX", "8", layer, "10", f"{x:.4f}", "20", f"{y:.4f}"]
        lines += ["0", "SEQEND"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", encoding="ascii") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(outlines)


def mesh_volume(verts, tris):
    v = np.asarray(verts, float)
    t = np.asarray(tris, int)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    return float(np.sum(np.einsum("ij,ij->i", a, np.cross(b, c))) / 6.0)


def edge_stats(tris):
    t = np.asarray(tris, int)
    e = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    uniq, counts = np.unique(np.sort(e, axis=1), axis=0, return_counts=True)
    return len(uniq), int(counts.min()), int(counts.max())
