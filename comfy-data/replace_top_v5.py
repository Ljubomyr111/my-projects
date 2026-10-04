# -*- coding: utf-8 -*-
"""
Careful clothing replacement, final approach.

The earlier attempts masked only *bright fabric pixels*; the model then saw the
rest of the original garment in the latent and barely changed anything. Here the
mask is the FULLGARMENT SILHOUETTE, so the clothing must be synthesised anew,
while a strict protection map keeps the head, hair, hands and the architectural
model byte-identical.
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

# ---- protective zones (these must never change) ---------------------------
protect = Image.new("L", (ww, wh), 0)
pd = ImageDraw.Draw(protect)
pd.ellipse([int(ww*0.26), -20, int(ww*0.76), int(wh*0.42)], fill=255)   # head + hair
pd.rectangle([int(ww*0.585), 0, ww, wh], fill=255)                       # model panel (right)
pd.rectangle([0, int(wh*0.905), ww, wh], fill=255)                       # table / bottom
pd.rectangle([0, 0, int(ww*0.075), wh], fill=255)                        # left edge
pm = np.array(protect) > 127

# ---- garment silhouette: neck -> sleeves -> waist -------------------------
mask = Image.new("L", (ww, wh), 0)
md = ImageDraw.Draw(mask)
# main trunk, from just under the chin to the waist
md.ellipse([int(ww*0.20), int(wh*0.30), int(ww*0.60), int(wh*0.90)], fill=255)
# shoulders / upper chest across to the left sleeve
md.ellipse([int(ww*0.10), int(wh*0.26), int(ww*0.52), int(wh*0.62)], fill=255)
# left arm sleeve going down
md.rectangle([int(ww*0.08), int(wh*0.34), int(ww*0.26), int(wh*0.86)], fill=255)
# neckline area just below the chin (keeps the collar continuous)
md.rectangle([int(ww*0.32), int(wh*0.26), int(ww*0.52), int(wh*0.40)], fill=255)

marr = np.array(mask) > 127
marr &= ~pm
mm = Image.fromarray((marr * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
marr = np.array(mm) > 120
marr &= ~pm
mask = Image.fromarray((marr * 255).astype(np.uint8))

log("garment mask: %.1f%% of working area" % (100.0 * marr.mean()))
head = np.zeros_like(marr); head[0:int(wh*0.42), int(ww*0.26):int(ww*0.76)] = True
right = np.zeros_like(marr); right[:, int(ww*0.585):] = True
log("masked in head zone: %d (must be 0)" % (marr & head).sum())
log("masked on model panel: %d (must be 0)" % (marr & right).sum())

work.save(os.path.join(INP, "c5_img.png"))
mask.save(os.path.join(INP, "c5_mask.png"))
ov = np.array(work.copy())
ov[marr] = (0.35 * ov[marr] + 0.65 * np.array([255, 30, 30])).astype(np.uint8)
Image.fromarray(ov).save(os.path.join(OUT, "c5_mask_preview.png"))

info = get(HOST + "/object_info")
ck = [c for c in info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0] if "inpaint" in c.lower()][0]

NEG = ("lowres, bad anatomy, bad hands, extra limbs, deformed, worst quality, "
       "low quality, jpeg artifacts, watermark, text, bare shoulders, "
       "cleavage, lingerie, underwear, nsfw, nude, topless")
GARMENT = ("woman wearing a dark navy blue wool blazer with long sleeves, buttoned "
           "front, over a light grey shirt, fashion photography, detailed fabric "
           "folds and stitching, soft studio light")

wf = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
    "2": {"class_type": "LoadImage", "inputs": {"image": "c5_img.png"}},
    "3": {"class_type": "LoadImageMask", "inputs": {"image": "c5_mask.png", "channel": "red"}},
    "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
          "mask": ["3", 0], "grow_mask_by": 6}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": GARMENT, "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
          "negative": ["6", 0], "latent_image": ["4", 0], "seed": 5150, "steps": 40, "cfg": 9.0,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "c5"}},
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

res_roi = res.resize((rw, rh), Image.LANCZOS)
mask_roi = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
orig_roi = np.array(roi)
comp_roi = orig_roi.copy()
comp_roi[mask_roi] = np.array(res_roi)[mask_roi]
comp = Image.fromarray(comp_roi)

final = full.copy()
final.paste(comp, (CROP[0], CROP[1]))
out = os.path.join(OUT, "photo_outfit_v5.png")
final.save(out)

diff = np.abs(comp_roi.astype(int) - orig_roi.astype(int)).mean(axis=2)
log("VERIFY outside mask: mean |diff| = %.4f (0 = untouched)" % diff[~mask_roi].mean())
log("VERIFY inside mask: %.2f" % diff[mask_roi].mean())
log("RESULT: %s" % out)
strip = Image.new("RGB", (rw * 2 + 12, rh), (25, 25, 25))
strip.paste(roi, (0, 0)); strip.paste(comp, (rw + 12, 0))
strip.save(os.path.join(OUT, "photo_outfit_v5_compare.png"))
log("COMPARE: %s" % os.path.join(OUT, "photo_outfit_v5_compare.png"))
