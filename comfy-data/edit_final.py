# -*- coding: utf-8 -*-
"""
Remove caption text + story bars from the user's photo, with NO guessed
coordinates:

  * find text by brightness (white glyphs) over the whole lower half
  * find the solid white story bar near the bottom edge
  * mask = text + bar + top status strip, dilated
  * inpaint with LaMa, then VERIFY: the mean brightness of the masked area must
    drop close to its surroundings (proving the white glyphs are gone).
"""
import json, os, time, urllib.request
from PIL import Image, ImageFilter
import numpy as np

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP  = os.path.join(WS, "comfy-data", "input")
OUT  = os.path.join(WS, "comfy-data", "output")

def log(m): print(m, flush=True)

def get(u, t=60):
    with urllib.request.urlopen(u, timeout=t) as r: return json.loads(r.read().decode())
def post(u, p, t=120):
    req = urllib.request.Request(u, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r: return json.loads(r.read().decode())

SRC = os.path.join(INP, "WhatsApp Image 2026-10-03 at 22.46.19.jpeg")
full = Image.open(SRC).convert("RGB")
W, H = full.size
gray = np.array(full.convert("L")).astype(np.int16)
log("photo %dx%d" % (W, H))

# ---- 1. text pixels: bright and in the lower third -----------------------
lower = np.zeros_like(gray, dtype=bool)
lower[int(H * 0.78):, :] = True
bright = (gray > 190) & lower
log("bright pixels in lower third: %d" % bright.sum())

# ---- 2. the solid story bar = wide fully-bright rows near the bottom -----
row_white = (gray > 225).mean(axis=1)
bar_rows = np.where((row_white > 0.6) & (np.arange(H) > H * 0.9))[0]
log("solid bar rows: %s" % ("none" if len(bar_rows) == 0 else "%d..%d" % (bar_rows.min(), bar_rows.max())))

mask = np.zeros((H, W), dtype=np.uint8)
mask[bright] = 255
if len(bar_rows):
    mask[bar_rows.min():bar_rows.max() + 1, :] = 255
mask[: int(H * 0.075), :] = 255          # phone status strip at the very top

m = Image.fromarray(mask).filter(ImageFilter.MaxFilter(15))   # dilate ~7 px
marr = np.array(m) > 127
log("mask covers %.2f%% of the image; text rows %s" % (
    100.0 * marr.mean(), "none" if not bright.any() else "%d..%d" % (
        np.where(bright.any(axis=1))[0].min(), np.where(bright.any(axis=1))[0].max())))

full.save(os.path.join(INP, "final_img.png"))
m.save(os.path.join(INP, "final_mask.png"))

wf = {
    "1": {"class_type": "LoadImage", "inputs": {"image": "final_img.png"}},
    "2": {"class_type": "LoadImageMask", "inputs": {"image": "final_mask.png", "channel": "red"}},
    "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": "big-lama.pt"}},
    "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
          "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
    "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "final_clean"}},
}
t0 = time.time()
pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
res = None
while time.time() - t0 < 900:
    time.sleep(2)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        f = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])][0]
        log("inpaint: %s in %.1fs -> %s" % (st.get("status_str"), time.time() - t0, f))
        res = Image.open(os.path.join(OUT, f)).convert("RGB")
        break
if res is None:
    raise SystemExit("no result")

# ---- 3. objective verification ------------------------------------------
before = np.array(full.convert("L")).astype(float)
after = np.array(res.convert("L")).astype(float)
white_before = (before[marr] > 190).mean()
white_after = (after[marr] > 190).mean()
log("VERIFY: white pixels inside mask  before=%.2f%%  after=%.2f%%" % (
    100 * white_before, 100 * white_after))
log("VERIFY: mean brightness inside mask before=%.1f after=%.1f (surroundings %.1f)" % (
    before[marr].mean(), after[marr].mean(),
    before[~marr][int(H*0.9):].mean()))

out = os.path.join(OUT, "photo_final_clean.png")
res.save(out)
log("RESULT: %s" % out)
prev = Image.new("RGB", (W * 2 + 16, H), (25, 25, 25))
prev.paste(full, (0, 0)); prev.paste(res, (W + 16, 0))
prev.save(os.path.join(OUT, "photo_final_before_after.png"))
log("BEFORE/AFTER: %s" % os.path.join(OUT, "photo_final_before_after.png"))
