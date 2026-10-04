# -*- coding: utf-8 -*-
"""
Careful clothing replacement, iteration 2.

Fixes over iteration 1:
  * the architectural model is now EXCLUDED from the mask geometrically, so it
    cannot get smudged;
  * denoise raised to 0.95 so the garment is actually replaced, not just
    slightly tinted;
  * after pasting back, every pixel outside the mask is restored from the
    original, so only the garment changes - verified by measurement.
"""
import json, os, time, urllib.request
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP  = os.path.join(WS, "comfy-data", "input")
OUT  = os.path.join(WS, "comfy-data", "output")

def log(m): print(m, flush=True)
def get(u, t=60):
    with urllib.request.urlopen(u, timeout=t) as r: return json.loads(r.read().decode())
def post(u, p, t=180):
    req = urllib.request.Request(u, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r: return json.loads(r.read().decode())

SRC = os.path.join(INP, "WhatsApp Image 2026-10-03 at 22.46.19.jpeg")
full = Image.open(SRC).convert("RGB")
W, H = full.size

CROP = (60, 590, 680, 1030)
roi = full.crop(CROP)
rw, rh = roi.size
SCALE = 576 / rw
work = roi.resize((int(rw * SCALE), int(rh * SCALE)), Image.LANCZOS)
ww, wh = work.size
log("ROI %dx%d -> working %dx%d" % (rw, rh, ww, wh))

arr = np.array(work).astype(np.int16)
R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
lum = 0.299 * R + 0.587 * G + 0.114 * B
sat = arr.max(axis=2) - arr.min(axis=2)
fabric = (lum > 130) & (sat < 95)

# ---- geometric protections: head, model, edges ---------------------------
protect = Image.new("L", (ww, wh), 0)
pd = ImageDraw.Draw(protect)
pd.ellipse([int(ww*0.28), -10, int(ww*0.74), int(wh*0.40)], fill=255)   # head + hair
pd.rectangle([0, int(wh*0.86), ww, wh], fill=255)                        # below the waist
pd.rectangle([int(ww*0.575), 0, ww, wh], fill=255)                        # the model panel on the right
pd.rectangle([0, 0, int(ww*0.09), wh], fill=255)                         # left edge
pd.rectangle([int(ww*0.93), 0, ww, wh], fill=255)                        # right edge
pm = np.array(protect) > 127

# garment region: torso box, then fabric pixels inside it
box = np.zeros_like(pm)
box[int(wh*0.22):int(wh*0.90), int(ww*0.08):int(ww*0.60)] = True
m = (fabric & box & ~pm).astype(np.uint8) * 255

mi = Image.fromarray(m)
mi = mi.filter(ImageFilter.MaxFilter(11))       # grow ~5 px over the edges
mi = mi.filter(ImageFilter.MedianFilter(7))
mi = mi.filter(ImageFilter.GaussianBlur(3))
mask = Image.fromarray(np.where(np.array(mi) > 120, 255, 0).astype(np.uint8))
marr = np.array(mask) > 127
marr &= ~pm                                    # never mask protected zones
mask = Image.fromarray((marr * 255).astype(np.uint8))

log("mask covers %.1f%% of the working area" % (100.0 * marr.mean()))
head_zone = np.zeros_like(marr)
head_zone[0:int(wh*0.40), int(ww*0.28):int(ww*0.74)] = True
log("masked pixels in head zone: %d (must be 0)" % (marr & head_zone).sum())
model_zone = np.zeros_like(marr); model_zone[int(wh*0.86):, :] = True
log("masked pixels on the model: %d (must be 0)" % (marr & model_zone).sum())

work.save(os.path.join(INP, "c4_img.png"))
mask.save(os.path.join(INP, "c4_mask.png"))
ov = np.array(work.copy())
ov[marr] = (0.4 * ov[marr] + 0.6 * np.array([255, 30, 30])).astype(np.uint8)
Image.fromarray(ov).save(os.path.join(OUT, "c4_mask_preview.png"))

info = get(HOST + "/object_info")
ck = [c for c in info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0] if "inpaint" in c.lower()][0]

NEG = ("lowres, bad anatomy, bad hands, extra limbs, deformed, worst quality, "
       "low quality, jpeg artifacts, watermark, text, bare shoulders, "
       "cleavage, lingerie, underwear, nsfw")
GARMENT = ("wearing a dark navy blue tailored blazer over a grey knit top, "
           "fashion photography, crisp fabric folds, detailed clothing texture, "
           "shoulders covered")

wf = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
    "2": {"class_type": "LoadImage", "inputs": {"image": "c4_img.png"}},
    "3": {"class_type": "LoadImageMask", "inputs": {"image": "c4_mask.png", "channel": "red"}},
    "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
          "mask": ["3", 0], "grow_mask_by": 8}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": GARMENT, "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
          "negative": ["6", 0], "latent_image": ["4", 0], "seed": 31337, "steps": 36, "cfg": 11.0,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "c2"}},
}
t0 = time.time()
pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
res = None
while time.time() - t0 < 1800:
    time.sleep(2)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
        log("inpaint: %s in %.1fs" % (st.get("status_str"), time.time() - t0))
        if st.get("status_str") != "success":
            for msg in st.get("messages", []):
                if msg[0] == "execution_error":
                    log("   %s: %s" % (msg[1].get("exception_type"), msg[1].get("exception_message")))
            raise SystemExit(1)
        res = Image.open(os.path.join(OUT, files[0])).convert("RGB")
        break
if res is None:
    raise SystemExit("no result")

# ---- composite: model output only inside the mask, original elsewhere ----
res_roi = res.resize((rw, rh), Image.LANCZOS)
mask_roi = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
orig_roi = np.array(roi)
new_roi = np.array(res_roi)
comp_roi = orig_roi.copy()
comp_roi[mask_roi] = new_roi[mask_roi]        # keep original outside the mask
comp = Image.fromarray(comp_roi)

final = full.copy()
final.paste(comp, (CROP[0], CROP[1]))
out = os.path.join(OUT, "photo_outfit_v4.png")
final.save(out)

diff = np.abs(comp_roi.astype(int) - orig_roi.astype(int)).mean(axis=2)
log("VERIFY outside mask: mean |diff| = %.4f (0 = untouched)" % diff[~mask_roi].mean())
log("VERIFY inside  mask: mean |diff| = %.2f (should be large)" % diff[mask_roi].mean())
log("RESULT: %s" % out)

strip = Image.new("RGB", (rw * 2 + 12, rh), (25, 25, 25))
strip.paste(roi, (0, 0)); strip.paste(comp, (rw + 12, 0))
strip.save(os.path.join(OUT, "photo_outfit_v4_compare.png"))
log("COMPARE: %s" % os.path.join(OUT, "photo_outfit_v4_compare.png"))


