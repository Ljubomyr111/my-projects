"""Voxel mesher + implicit solids: guaranteed-watertight STL for printing.

Approach: sample the signed distance field on a lattice, mark filled voxels,
then emit a quad for every voxel face that borders an empty neighbour. Closed
by construction, no lookup tables, and every slicer accepts the result.

Trade-off: flat surfaces land on the lattice, so a curved wall shows facets at
the voxel pitch. For the flat plates, brackets and prisms in this robot that is
exactly what we want; the pitch is a parameter.
"""
import math
import struct

import numpy as np

_DEBUG = False


class Grid:
    def __init__(self, bounds, pitch=0.5):
        (x0, y0, z0), (x1, y1, z1) = bounds
        self.pitch = float(pitch)
        self.x0, self.y0, self.z0 = float(x0), float(y0), float(z0)
        self.shape = (int(math.ceil((x1 - x0) / pitch)) + 1,
                      int(math.ceil((y1 - y0) / pitch)) + 1,
                      int(math.ceil((z1 - z0) / pitch)) + 1)
        nx, ny, nz = self.shape
        self.xs = x0 + np.arange(nx) * pitch
        self.ys = y0 + np.arange(ny) * pitch
        self.zs = z0 + np.arange(nz) * pitch

    def coords(self):
        X, Y, Z = np.meshgrid(self.xs, self.ys, self.zs, indexing="ij")
        return X, Y, Z


# --------------------------------------------------------------------------
# Signed distance primitives (negative = inside)
# --------------------------------------------------------------------------


def box(P, c, size):
    d = np.abs(P - np.asarray(c, float)) - np.asarray(size, float) / 2.0
    return (np.linalg.norm(np.maximum(d, 0.0), axis=-1)
            + np.minimum(np.max(d, axis=-1), 0.0))


def cylinder(P, c, r, h, axis=2):
    cc = np.asarray(c, float)
    d = P - cc
    radial = np.sqrt(sum(d[..., i] ** 2 for i in range(3) if i != axis))
    dr = radial - r
    da = np.abs(d[..., axis]) - h / 2.0
    return (np.sqrt(np.maximum(dr, 0.0) ** 2 + np.maximum(da, 0.0) ** 2)
            + np.minimum(np.maximum(dr, da), 0.0))


def hexprism(P, c, across_flats, h, axis=2):
    d = P - np.asarray(c, float)
    ap = across_flats / 2.0
    if axis == 2:
        a1, a2 = d[..., 0], d[..., 1]
    elif axis == 0:
        a1, a2 = d[..., 1], d[..., 2]
    else:
        a1, a2 = d[..., 0], d[..., 2]
    k = math.sqrt(3.0) / 2.0
    dxy = np.maximum(np.maximum(np.abs(a1) - ap, np.abs(a1 * 0.5 + a2 * k) - ap),
                     np.abs(a1 * 0.5 - a2 * k) - ap)
    da = np.abs(d[..., axis]) - h / 2.0
    return (np.sqrt(np.maximum(dxy, 0.0) ** 2 + np.maximum(da, 0.0) ** 2)
            + np.minimum(np.maximum(dxy, da), 0.0))


def union(*fields):
    out = fields[0]
    for f in fields[1:]:
        out = np.minimum(out, f)
    return out


def subtract(solid, *cutters):
    out = solid
    for c in cutters:
        out = np.maximum(out, -c)
    return out


# --------------------------------------------------------------------------
# Voxel mesher
# --------------------------------------------------------------------------


def voxel_mesh(F, grid, iso=0.0, pitch=None):
    """Closed triangle mesh from a signed distance field by face culling.

    Formal convention (this is the only convention; nothing else is assumed):

      * Grid sample (i,j,k) is at world (x0 + i*p, y0 + j*p, z0 + k*p).
      * VOXEL (i,j,k) is the cube  [i-0.5, i+0.5] x [j-0.5, j+0.5] x [k-0.5, k+0.5]
        in cell units, i.e. centred on grid sample (i,j,k).
      * A voxel is FILLED when its centre value F[i,j,k] < iso.
      * Voxel corners live at half-integer cell coordinates; keys are stored
        as integers in half-units (2i +- 1) so they never collide.

    A quad is emitted on every face where a filled voxel meets an empty one, so
    the surface is closed by construction. Quads are wound CCW seen from
    outside, which makes the signed volume positive.
    """
    F = np.asarray(F, float)
    nx, ny, nz = grid.shape
    if F.shape != (nx, ny, nz):
        raise ValueError("field shape does not match grid")
    p = grid.pitch
    step = 1 if pitch is None else max(1, int(round(pitch / p)))
    cell = p * step

    filled = F < iso
    # voxels on the outer shell of the sampling box are forced empty, so the
    # surface always closes inside the sampled region
    filled[0, :, :] = filled[-1, :, :] = False
    filled[:, 0, :] = filled[:, -1, :] = False
    filled[:, :, 0] = filled[:, :, -1] = False

    ox, oy, oz = grid.x0, grid.y0, grid.z0
    if step > 1:
        mx, my, mz = nx // step, ny // step, nz // step
        red = filled[:mx * step, :my * step, :mz * step]
        # a coarse voxel is filled when its centre block is mostly filled;
        # "any" keeps thin features alive
        filled = red.reshape(mx, step, my, step, mz, step).any(axis=(1, 3, 5))
        # centre of a coarse voxel, in world units
        ox = grid.x0 + (step - 1) * p / 2.0
        oy = grid.y0 + (step - 1) * p / 2.0
        oz = grid.z0 + (step - 1) * p / 2.0
    else:
        # shift so that voxel index i is centred at x0 + i*p
        ox, oy, oz = grid.x0, grid.y0, grid.z0

    nxf, nyf, nzf = filled.shape

    verts = []
    vindex = {}

    def vid(key):
        v = vindex.get(key)
        if v is None:
            v = len(verts)
            vindex[key] = v
            # key is in half-units of the coarse cell
            verts.append((ox + key[0] * cell * 0.5,
                          oy + key[1] * cell * 0.5,
                          oz + key[2] * cell * 0.5))
        return v

    # (axis, sign, four corners in half-units, CCW seen from OUTSIDE).
    # u x v must equal the outward normal; derivation checked against the cube.
    H = 1
    dirs = [
        (0, +1, [(H, -H, -H), (H, H, -H), (H, H, H), (H, -H, H)]),        # n=+x
        (0, -1, [(-H, -H, -H), (-H, -H, H), (-H, H, H), (-H, H, -H)]),    # n=-x
        (1, +1, [(-H, H, -H), (-H, H, H), (H, H, H), (H, H, -H)]),        # n=+y
        (1, -1, [(-H, -H, -H), (H, -H, -H), (H, -H, H), (-H, -H, H)]),    # n=-y
        (2, +1, [(-H, -H, H), (H, -H, H), (H, H, H), (-H, H, H)]),        # n=+z
        (2, -1, [(-H, -H, -H), (H, -H, -H), (H, H, -H), (-H, H, -H)]),    # n=-z
    ]

    tris = []
    for ax, sgn, corners in dirs:
        nb = np.zeros_like(filled)
        src = [slice(None)] * 3
        dst = [slice(None)] * 3
        if sgn > 0:
            src[ax] = slice(0, nxf - 1) if ax == 0 else slice(None)
        # generic neighbour shift
        nb = np.zeros_like(filled)
        src = [slice(None)] * 3
        dst = [slice(None)] * 3
        if sgn > 0:
            src[ax] = slice(0, filled.shape[ax] - 1)
            dst[ax] = slice(1, filled.shape[ax])
        else:
            src[ax] = slice(1, filled.shape[ax])
            dst[ax] = slice(0, filled.shape[ax] - 1)
        nb[tuple(dst)] = filled[tuple(src)]

        exposed = filled & ~nb
        shell = [slice(None)] * 3
        shell[ax] = 0 if sgn < 0 else filled.shape[ax] - 1
        exposed[tuple(shell)] = False

        for (i, j, k) in np.argwhere(exposed):
            quad = [vid((2 * i + ca, 2 * j + cb, 2 * k + cc))
                    for (ca, cb, cc) in corners]
            tris.append((quad[0], quad[1], quad[2]))
            tris.append((quad[0], quad[2], quad[3]))

    if not verts:
        raise ValueError("no voxels filled - check bounds and iso")
    return np.array(verts, float), np.array(tris, np.int64)


def mesh_volume(verts, tris):
    v = np.asarray(verts, float)
    t = np.asarray(tris, int)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    return float(np.sum(np.einsum("ij,ij->i", a, np.cross(b, c))) / 6.0)


def edge_stats(verts, tris):
    t = np.asarray(tris, int)
    e = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    uniq, counts = np.unique(np.sort(e, axis=1), axis=0, return_counts=True)
    return len(uniq), int(counts.min()), int(counts.max())


def write_stl(path, verts, tris):
    v = np.asarray(verts, float)
    t = np.asarray(tris, np.int64)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = n / ln[:, None]
    with open(path, "wb") as fh:
        fh.write(b"\x00" * 80)
        fh.write(struct.pack("<I", len(t)))
        buf = bytearray()
        for i in range(len(t)):
            buf += struct.pack("<12fH", n[i, 0], n[i, 1], n[i, 2],
                               a[i, 0], a[i, 1], a[i, 2],
                               b[i, 0], b[i, 1], b[i, 2],
                               c[i, 0], c[i, 1], c[i, 2], 0)
        fh.write(bytes(buf))
    return len(t)


def render_isometric(verts, tris, path, size=(900, 700), bg=(255, 255, 255),
                     title=None, azim=-35.0, elev=26.0):
    from PIL import Image, ImageDraw, ImageFont

    v = np.asarray(verts, float)
    t = np.asarray(tris, int)
    a_ = math.radians(azim)
    e_ = math.radians(elev)
    fwd = np.array([math.cos(e_) * math.cos(a_), math.cos(e_) * math.sin(a_), math.sin(e_)])
    right = np.array([-math.sin(a_), math.cos(a_), 0.0])
    up = np.cross(fwd, right)
    up /= np.linalg.norm(up)

    ctr = (v.max(axis=0) + v.min(axis=0)) / 2.0
    rel = v - ctr
    px, py, pz = rel @ right, rel @ up, rel @ fwd
    W, H = size
    span = max(px.max() - px.min(), py.max() - py.min(), 1e-6)
    scale = (min(W, H) * 0.76) / span
    sx = (px * scale + W / 2).astype(int)
    sy = (H / 2 - py * scale).astype(int)

    n = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
    nl = np.linalg.norm(n, axis=1)
    nl[nl == 0] = 1.0
    n = n / nl[:, None]
    light = np.array([0.45, -0.62, 0.65])
    light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0.18, 1.0)
    order = np.argsort(pz[t].mean(axis=1))

    im = Image.new("RGB", size, bg)
    dr = ImageDraw.Draw(im)
    base = np.array([92, 138, 184], float)
    for fi in order:
        tri = t[fi]
        dr.polygon([(sx[tri[0]], sy[tri[0]]), (sx[tri[1]], sy[tri[1]]),
                    (sx[tri[2]], sy[tri[2]])],
                   fill=tuple(int(np.clip(ch * shade[fi], 0, 255)) for ch in base))
    if title:
        f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
        dr.text((18, 14), title, font=f, fill=(28, 32, 38))
    im.save(path)
    return path
