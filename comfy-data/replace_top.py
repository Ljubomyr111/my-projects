# -*- coding: utf-8 -*-
"""
Replace the clothing (t-shirt + cardigan) on the user's photo with a different
garment, using SD 1.5 inpainting with ControlNet (softedge) so the original
pose and silhouette are preserved.

Plan:
  1. crop the upper body (shoulders -> hips) so the model works at a
     reasonable resolution instead of the full 722x1600,
  2. mask only the garment: the torso region, with head/hair/arms/model
     excluded,
  3. inpaint at higher resolution with the SD1.5 inpainting checkpoint,
  4. paste the result back and produce a before/after strip.
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

# ---- region of interest: shoulders down to below the waist --------------
# photo layout found earlier: head ~y=380..640, torso ~640..960, model below
CROP = (40, 560, 690, 1060)
roi = full.crop(CROP).resize((512, int(512 * (CROP[3]-CROP[1]) / (CROP[2]-CROP[0]))), Image.LANCZOS)
rw, rh = roi.size
ROI_SIZE = (CROP[2]-CROP[0], CROP[3]-CROP[1])   # original ROI size for paste-back
log("ROI %dx%d from %s" % (rw, rh, CROP))

# ---- mask: the garment only --------------------------------------------
# torso oval, nudged to avoid the face and her hands/the model at the edges
mask = Image.new("L", (rw, rh), 0)
d = ImageDraw.Draw(mask)
d.ellipse([int(rw*0.16), int(rh*0.06), int(rw*0.86), rh], fill=255)   # trunk incl. arms
mask = mask.filter(ImageFilter.GaussianBlur(6))
mask = mask.point(lambda v: 255 if v > 110 else 0)
log("masked %.1f%% of the ROI" % (100.0 * (np.array(mask) > 127).mean()))

roi.save(os.path.join(INP, "cloth_img.png"))
mask.save(os.path.join(INP, "cloth_mask.png"))

info = get(HOST + "/object_info")
ck = [c for c in info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0] if "inpaint" in c.lower()][0]
cn_list = info["ControlNetLoader"]["input"]["required"]["control_net_name"][0]
cn = next((c for c in cn_list if "softedge" in c), None)
log("checkpoint=%s  controlnet=%s" % (ck, cn))

NEG = ("lowres, bad anatomy, bad hands, extra limbs, deformed, disfigured, "
       "worst quality, low quality, jpeg artifacts, watermark, text")

GARMENT = ("wearing a tailored beige linen blazer over a plain white top, "
           "fashion photo, natural fabric folds, detailed clothing texture")

nodes = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
    "2": {"class_type": "LoadImage", "inputs": {"image": "cloth_img.png"}},
    "3": {"class_type": "LoadImageMask", "inputs": {"image": "cloth_mask.png", "channel": "red"}},
    "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
          "mask": ["3", 0], "grow_mask_by": 6}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": GARMENT, "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "12": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
           "negative": ["6", 0], "latent_image": ["4", 0], "seed": 2024, "steps": 30, "cfg": 7.5,
           "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["1", 2]}},
    "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": "cloth"}},
}
if cn:
    nodes["7"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": cn}}
    nodes["8"] = {"class_type": "ControlNetApplyAdvanced", "inputs": {
        "positive": ["5", 0], "negative": ["6", 0], "control_net": ["7", 0],
        "image": ["2", 0], "strength": 0.6, "start_percent": 0.0, "end_percent": 0.7}}
    nodes["12"]["inputs"]["positive"] = ["8", 0]
    nodes["12"]["inputs"]["negative"] = ["8", 1]

t0 = time.time()
pid = post(HOST + "/prompt", {"prompt": nodes})["prompt_id"]
res = None
while time.time() - t0 < 1800:
    time.sleep(2)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
        log("inpaint: %s in %.1fs -> %s" % (st.get("status_str"), time.time() - t0, files))
        if st.get("status_str") != "success":
            for m in st.get("messages", []):
                if m[0] == "execution_error":
                    log("   %s: %s" % (m[1].get("exception_type"), m[1].get("exception_message")))
            raise SystemExit(1)
        res = Image.open(os.path.join(OUT, files[0])).convert("RGB")
        break
if res is None:
    raise SystemExit("no result")

final = full.copy()
final.paste(res.resize(ROI_SIZE, Image.LANCZOS), (CROP[0], CROP[1]))
out = os.path.join(OUT, "photo_new_outfit.png")
final.save(out)
log("RESULT: %s" % out)

a = full.crop(CROP); b = res.resize(ROI_SIZE, Image.LANCZOS)
strip = Image.new("RGB", (a.size[0]*2 + 12, a.size[1]), (25, 25, 25))
strip.paste(a, (0, 0)); strip.paste(b, (a.size[0] + 12, 0))
strip.save(os.path.join(OUT, "photo_new_outfit_compare.png"))
log("COMPARE: %s" % os.path.join(OUT, "photo_new_outfit_compare.png"))


