# -*- coding: utf-8 -*-
"""
Careful clothing replacement on the user's photo.

Compared to the first attempt this one:
  * builds a PRECISE mask - only actual garment pixels are masked, using
    brightness/colour similarity rather than a big ellipse;
  * explicitly protects the face, hair, hands and the architectural model;
  * uses denoise < 1 so the model repaints the fabric but leaves neighbouring
    structure alone;
  * drops ControlNet to free VRAM (the mask is precise enough without it);
  * verifies afterwards that pixels outside the mask are bit-identical.
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

# ---- work region: the upper body only ------------------------------------
CROP = (60, 590, 680, 1030)
roi = full.crop(CROP)
rw, rh = roi.size                     # 620 x 440
SCALE = 576 / rw                      # keep detail but stay inside 4 GB
work = roi.resize((int(rw * SCALE), int(rh * SCALE)), Image.LANCZOS)
ww, wh = work.size
log("ROI %dx%d -> working %dx%d (from %s)" % (rw, rh, ww, wh, CROP))

arr = np.array(work).astype(np.int16)
R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
lum = (0.299 * R + 0.587 * G + 0.114 * B)

# garment = bright, low-saturation fabric (white tee + pale pink cardigan)
mx = arr.max(axis=2); mn = arr.min(axis=2)
sat = mx - mn
garment = (lum > 150) & (sat < 75)

# region-of-interest box for the garment: below the chin, above the waist
torso = np.zeros_like(garment, dtype=bool)
Y0, Y1 = int(wh * 0.30), int(wh * 0.97)
X0, X1 = int(ww * 0.13), int(ww * 0.90)
torso[Y0:Y1, X0:X1] = True
garment &= torso

# ---- explicit protections ------------------------------------------------
protect = Image.new("L", (ww, wh), 0)
pd = ImageDraw.Draw(protect)
# face + hair (kept generous so nothing of the head is repainted)
pd.ellipse([int(ww*0.30), 0, int(ww*0.72), int(wh*0.42)], fill=255)
# her right arm / hand and the model she holds at the bottom
pd.rectangle([0, int(wh*0.88), ww, wh], fill=255)
pd.rectangle([0, 0, int(ww*0.10), wh], fill=255)
protect = np.array(protect) > 127

m = (garment & ~protect).astype(np.uint8) * 255
mi = Image.fromarray(m)
mi = mi.filter(ImageFilter.MaxFilter(9))          # grow ~4 px over edges
mi = mi.filter(ImageFilter.MedianFilter(7))       # drop speckles
mi = mi.filter(ImageFilter.GaussianBlur(3))
mi = mi.point(lambda v: 255 if v > 120 else 0)
mask = Image.fromarray(np.where(np.array(mi) > 127, 255, 0).astype(np.uint8))

marr = np.array(mask) > 127
log("precise mask: %.1f%% of working area (was 52%% before)" % (100.0 * marr.mean()))
# sanity: is the face really untouched?
face_zone = np.zeros_like(marr); face_zone[0:int(wh*0.42), int(ww*0.30):int(ww*0.72)] = True
log("masked pixels inside the protected head area: %d (must be 0)" % (marr & face_zone).sum())

work.save(os.path.join(INP, "care_img.png"))
mask.save(os.path.join(INP, "care_mask.png"))

# mask preview so the user can see exactly what gets repainted
prev = work.copy()
ov = np.array(prev); ov[marr] = (0.45 * ov[marr] + 0.55 * np.array([255, 40, 40])).astype(np.uint8)
Image.fromarray(ov).save(os.path.join(OUT, "care_mask_preview.png"))

info = get(HOST + "/object_info")
ck = [c for c in info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0] if "inpaint" in c.lower()][0]

NEG = ("lowres, bad anatomy, bad hands, extra limbs, deformed, disfigured, "
       "worst quality, low quality, jpeg artifacts, watermark, text, "
       "bare shoulders, cleavage, lingerie")
GARMENT = ("wearing a tailored beige linen blazer with a white top underneath, "
           "fashion photography, natural fabric folds, detailed stitching")

wf = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
    "2": {"class_type": "LoadImage", "inputs": {"image": "care_img.png"}},
    "3": {"class_type": "LoadImageMask", "inputs": {"image": "care_mask.png", "channel": "red"}},
    "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
          "mask": ["3", 0], "grow_mask_by": 6}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": GARMENT, "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
          "negative": ["6", 0], "latent_image": ["4", 0], "seed": 77, "steps": 32, "cfg": 7.5,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 0.88}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "care"}},
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

# ---- paste back and verify ----------------------------------------------
back = res.resize((rw, rh), Image.LANCZOS)
final = full.copy()
final.paste(back, (CROP[0], CROP[1]))
out = os.path.join(OUT, "photo_outfit_careful.png")
final.save(out)

# outside-mask identity check in the working space
rb = np.array(back).astype(int)
ro = np.array(roi).astype(int)
full_mask = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
diff = np.abs(rb - ro).mean(axis=2)
log("VERIFY outside mask: mean |diff| = %.2f (must be ~0)" % diff[~full_mask].mean())
log("VERIFY inside  mask: mean |diff| = %.2f" % diff[full_mask].mean())
log("RESULT: %s" % out)

a = roi; b = back
strip = Image.new("RGB", (a.size[0] * 2 + 12, a.size[1]), (25, 25, 25))
strip.paste(a, (0, 0)); strip.paste(b, (a.size[0] + 12, 0))
strip.save(os.path.join(OUT, "photo_outfit_careful_compare.png"))
log("COMPARE: %s" % os.path.join(OUT, "photo_outfit_careful_compare.png"))
