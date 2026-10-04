# -*- coding: utf-8 -*-
"""
Edit the user's real photo: remove the story UI (top status bar, bottom edge)
and the caption text, using LaMa (no prompt needed) via ComfyUI.

Approach that actually works on a tall 722x1600 phone screenshot:
  1. crop the caption band out of the photo,
  2. inpaint that band on its own (so the model works at a sane resolution),
  3. paste the cleaned band back into the untouched original.

This avoids feeding SD/LaMa a 722x1600 image, where they smear detail.
"""
import json, os, shutil, time, urllib.request, urllib.error
from PIL import Image, ImageDraw

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP  = os.path.join(WS, "comfy-data", "input")
OUT  = os.path.join(WS, "comfy-data", "output")

def log(m): print("[%s] %s" % (time.strftime("%H:%M:%S"), m), flush=True)
def get(u, t=30):
    with urllib.request.urlopen(u, timeout=t) as r: return json.loads(r.read().decode())
def post(u, p, t=120):
    req = urllib.request.Request(u, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r: return json.loads(r.read().decode())

PHOTO = os.path.join(INP, "WhatsApp Image 2026-10-03 at 22.46.19.jpeg")
work  = os.path.join(WS, "comfy-data", "edit")
os.makedirs(work, exist_ok=True)

img = Image.open(PHOTO).convert("RGB")
W, H = img.size
log("photo: %dx%d" % (W, H))

# --- where the junk is -------------------------------------------------
# bottom caption band (text + the small white bar under it)
BAND_TOP = int(H * 0.862)
band = img.crop((0, BAND_TOP, W, H))
band_h = H - BAND_TOP
log("caption band: y=%d..%d (%dx%d)" % (BAND_TOP, H, W, band_h))

# pad the band with real pixels above it so the model has context
PAD = 160
crop_top = max(0, BAND_TOP - PAD)
crop = img.crop((0, crop_top, W, H))
cw, ch = crop.size
crop_file = "edit_crop.png"
crop.save(os.path.join(INP, crop_file))
log("crop for inpainting: %dx%d (top y=%d)" % (cw, ch, crop_top))

# mask inside the crop: everything from the band start downwards
mask = Image.new("L", (cw, ch), 0)
d = ImageDraw.Draw(mask)
d.rectangle([0, BAND_TOP - crop_top, cw, ch], fill=255)
mask_file = "edit_mask.png"
mask.save(os.path.join(INP, mask_file))
log("mask: white over y>=%d of the crop" % (BAND_TOP - crop_top))

info = get(HOST + "/object_info")
lama_spec = info["INPAINT_LoadInpaintModel"]["input"]["required"]["model_name"]
lama = (lama_spec[0] if isinstance(lama_spec[0], list) else lama_spec[1]["options"])[0]
log("inpaint model: %s" % lama)

wf = {
    "1": {"class_type": "LoadImage", "inputs": {"image": crop_file}},
    "2": {"class_type": "LoadImageMask", "inputs": {"image": mask_file, "channel": "red"}},
    "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": lama}},
    "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
          "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
    "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "edit_band"}},
}
t0 = time.time()
pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
while time.time() - t0 < 600:
    time.sleep(2)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
        log("LaMa band inpaint: %s in %.1fs -> %s" % (st.get("status_str"), time.time() - t0, files))
        if st.get("status_str") != "success":
            for m in st.get("messages", []):
                if m[0] == "execution_error":
                    log("  %s: %s" % (m[1].get("exception_type"), m[1].get("exception_message")))
            raise SystemExit(1)
        result = files[0]
        break

# --- paste the cleaned band back ---------------------------------------
cleaned = Image.open(os.path.join(OUT, result)).convert("RGB")
log("cleaned crop: %s" % (cleaned.size,))
final = img.copy()
final.paste(cleaned, (0, crop_top))
final_file = os.path.join(OUT, "photo_caption_removed.png")
final.save(final_file)
log("FINAL: %s" % final_file)

# side-by-side preview for quick eyeballing
prev = Image.new("RGB", (W * 2 + 20, H), (30, 30, 30))
prev.paste(img, (0, 0))
prev.paste(final, (W + 20, 0))
prev_file = os.path.join(OUT, "photo_before_after.png")
prev.save(prev_file)
log("BEFORE/AFTER: %s" % prev_file)
