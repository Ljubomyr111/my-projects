# -*- coding: utf-8 -*-
"""
Export the clothing as a real LAYER:

  layer_outfit_new.png    transparent PNG - the clothing as it is in the edited
                          photo (full frame, everything else transparent)
  layer_outfit_original.png  same layer taken from the ORIGINAL photo, so it can
                          be re-edited from scratch
  layer_mask.png          the selection itself (white on black, full frame)
  layer_mask_preview.png  the selection shown in red over the photo

All four are full 722x1600 so they drop straight onto the photo in any editor.
"""
import json, os, urllib.request
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

WS  = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP = os.path.join(WS, "comfy-data", "input")
OUT = os.path.join(WS, "comfy-data", "output")
LAY = os.path.join(WS, "comfy-data", "layers")
os.makedirs(LAY, exist_ok=True)

SRC   = os.path.join(INP, "WhatsApp Image 2026-10-03 at 22.46.19.jpeg")
EDITED = os.path.join(OUT, "photo_full_outfit.png")

full = Image.open(SRC).convert("RGB")
new  = Image.open(EDITED).convert("RGB")
W, H = full.size
print("photo %dx%d" % (W, H))

# two regions were masked, with the same geometry the edit used
T = (60, 585, 680, 1045)      # top
B = (60, 1050, 680, 1305)     # legs (stops above the caption)

mask_full = Image.new("L", (W, H), 0)

# --- top region mask (identical maths to replace_outfit_full.py) ----------
tw, th = T[2]-T[0], T[3]-T[1]
work = full.crop(T).resize((576, int(th*576/tw)), Image.LANCZOS)
ww, wh = work.size
prot = Image.new("L", (ww, wh), 0); pd = ImageDraw.Draw(prot)
pd.ellipse([int(ww*0.26), -20, int(ww*0.76), int(wh*0.44)], fill=255)
pd.rectangle([int(ww*0.560), int(wh*0.55), ww, wh], fill=255)
pd.rectangle([0, int(wh*0.90), ww, wh], fill=255)
pd.rectangle([0, 0, int(ww*0.075), wh], fill=255)
pd.ellipse([int(ww*0.14), int(wh*0.62), int(ww*0.42), int(wh*0.94)], fill=255)
pm = np.array(prot) > 127
g = Image.new("L", (ww, wh), 0); gd = ImageDraw.Draw(g)
gd.ellipse([int(ww*0.20), int(wh*0.30), int(ww*0.60), int(wh*0.93)], fill=255)
gd.ellipse([int(ww*0.11), int(wh*0.26), int(ww*0.52), int(wh*0.64)], fill=255)
gd.rectangle([int(ww*0.09), int(wh*0.34), int(ww*0.27), int(wh*0.88)], fill=255)
gd.rectangle([int(ww*0.32), int(wh*0.26), int(ww*0.52), int(wh*0.42)], fill=255)
gm = np.array(g) > 127
gm &= ~pm
gm = np.array(Image.fromarray((gm*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) > 120
gm &= ~pm
top_mask = Image.fromarray((gm*255).astype(np.uint8)).resize((tw, th), Image.NEAREST)
mask_full.paste(top_mask, (T[0], T[1]))
print("top layer: %d px" % int(gm.sum()))

# --- legs region mask -----------------------------------------------------
bw, bh = B[2]-B[0], B[3]-B[1]
work2 = full.crop(B).resize((576, int(bh*576/bw)), Image.LANCZOS)
w2, h2 = work2.size
prot2 = Image.new("L", (w2, h2), 0); p2 = ImageDraw.Draw(prot2)
p2.rectangle([0, 0, int(w2*0.155), h2], fill=255)
p2.rectangle([int(w2*0.80), 0, w2, h2], fill=255)
p2.rectangle([0, int(h2*0.97), w2, h2], fill=255)
pm2 = np.array(prot2) > 127
g2 = Image.new("L", (w2, h2), 0); gd2 = ImageDraw.Draw(g2)
gd2.rectangle([int(w2*0.17), 0, int(w2*0.78), h2], fill=255)
g2m = np.array(g2) > 127
arr = np.array(work2).astype(np.int16)
lum = 0.299*arr[:, :, 0] + 0.587*arr[:, :, 1] + 0.114*arr[:, :, 2]
sat = arr.max(axis=2) - arr.min(axis=2)
trousers = (lum > 100) & (lum < 190) & (sat < 65)
g2m = g2m & (trousers | (lum > 90))
g2m &= ~pm2
g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 120
g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(7))) > 120
g2m &= ~pm2
bot_mask = Image.fromarray((g2m*255).astype(np.uint8)).resize((bw, bh), Image.NEAREST)
mask_full.paste(bot_mask, (B[0], B[1]))
print("legs layer: %d px" % int(g2m.sum()))

# Keep only the pixels that were genuinely re-drawn: this drops the tiny
# (mean diff < 5) noise the sampler left on the model panel, which the
# geometric mask happened to cover.
d_orig = np.array(full).astype(int)
d_new = np.array(new).astype(int)
delta = np.abs(d_orig - d_new).mean(axis=2)
geom = np.array(mask_full) > 120
real = geom & (delta > 6)
print("geometric selection %d px -> actually re-drawn %d px" % (geom.sum(), real.sum()))

mask_soft = Image.fromarray((real * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
alpha = np.array(mask_soft)

# --- build the layers -----------------------------------------------------
for tag, src in (("new", new), ("original", full)):
    a = np.dstack([np.array(src), alpha])
    out = os.path.join(LAY, "layer_outfit_%s.png" % tag)
    Image.fromarray(a, "RGBA").save(out)
    print("wrote", out)

mask_full.save(os.path.join(LAY, "layer_mask.png"))
print("wrote", os.path.join(LAY, "layer_mask.png"))

# red preview of the selection
ov = np.array(full).copy()
sel = alpha > 120
ov[sel] = (0.35*ov[sel] + 0.65*np.array([255, 30, 30])).astype(np.uint8)
Image.fromarray(ov).save(os.path.join(LAY, "layer_mask_preview.png"))

# a contact sheet so everything can be judged at once
th_w = 320
sc = th_w / W
sm = lambda im: im.resize((th_w, int(H*sc)), Image.LANCZOS)
tiles = [sm(full), sm(new),
         Image.fromarray(np.dstack([np.array(full), alpha]), "RGBA").resize((th_w, int(H*sc))),
         Image.fromarray(np.dstack([np.array(new),  alpha]), "RGBA").resize((th_w, int(H*sc)))]
sheet = Image.new("RGB", (th_w*4 + 30, int(H*sc)), (40, 40, 40))
for i, t in enumerate(tiles):
    sheet.paste(t, (i*(th_w+10), 0), t if t.mode == "RGBA" else None)
sheet.save(os.path.join(LAY, "layer_overview.png"))
print("wrote", os.path.join(LAY, "layer_overview.png"))
print("total selected px:", int(sel.sum()))

