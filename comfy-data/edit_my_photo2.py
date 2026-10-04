# -*- coding: utf-8 -*-
"""
Remove the caption text and the story bars from the user's photo, with a TIGHT
mask built automatically:

  * white caption pixels are found by brightness (they are near-white with a
    dark shadow on a darker floor, so a threshold isolates them well)
  * the thin white story bar at the very bottom is masked explicitly
  * the top status-bar strip is masked explicitly
  * everything is dilated so anti-aliased edges and shadows are covered too

Only the text itself is regenerated, so legs/floor stay untouched.
"""
import json, os, time, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np

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

SRC = os.path.join(INP, "WhatsApp Image 2026-10-03 at 22.46.19.jpeg")
img = Image.open(SRC).convert("RGB")
W, H = img.size
log("photo %dx%d" % (W, H))

def inpaint(pixels, mask, tag, model="big-lama.pt"):
    """Run LaMa on the given full-size image + mask, return the result image."""
    pf, mf = "tight_%s_img.png" % tag, "tight_%s_mask.png" % tag
    pixels.save(os.path.join(INP, pf))
    mask.convert("L").save(os.path.join(INP, mf))
    wf = {
        "1": {"class_type": "LoadImage", "inputs": {"image": pf}},
        "2": {"class_type": "LoadImageMask", "inputs": {"image": mf, "channel": "red"}},
        "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": model}},
        "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
              "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
        "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "tight_" + tag}},
    }
    t0 = time.time()
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    while time.time() - t0 < 900:
        time.sleep(2)
        h = get(HOST + "/history/%s" % pid)
        if pid in h:
            st = h[pid]["status"]
            files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
            log("%s: %s in %.1fs" % (tag, st.get("status_str"), time.time() - t0))
            if st.get("status_str") != "success":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        log("   %s: %s" % (m[1].get("exception_type"), m[1].get("exception_message")))
                raise SystemExit(1)
            return Image.open(os.path.join(OUT, files[0])).convert("RGB")
    raise SystemExit("timeout")

# ---------------- build masks on the FULL image, then work in one crop ----
TOP_BAR    = 130
TEXT_TOP   = int(H * 0.855)
TEXT_BOT   = int(H * 0.975)
FOOTER_BAR = int(H * 0.985)

region = np.array(img.crop((0, TEXT_TOP, W, TEXT_BOT)).convert("L"))
bright = (region > 195).astype(np.uint8) * 255          # the white letters
log("text pixels found: %d (%.2f%% of the caption strip)" % ((bright > 0).sum(), 100.0 * (bright > 0).mean()))

m = Image.new("L", (W, H), 0)
m.paste(Image.fromarray(bright), (0, TEXT_TOP))
d = ImageDraw.Draw(m)
d.rectangle([0, 0, W, TOP_BAR], fill=255)               # phone status bar
d.rectangle([0, FOOTER_BAR, W, H], fill=255)            # story footer bar
d.rectangle([0, TEXT_TOP - 6, W, TEXT_BOT + 6], fill=255)  # safety band over captions
m = m.filter(ImageFilter.MaxFilter(9))                  # grow ~4 px to cover edges/shadow

# keep the inpaint crop tight: top bar strip, and the caption strip only
crop_top = 0
crop_bot = TEXT_BOT + 40
crop = img.crop((0, crop_top, W, crop_bot))
cmask = m.crop((0, crop_top, W, crop_bot))
log("crop %dx%d, masked %.1f%%" % (crop.size[0], crop.size[1], 100.0 * (np.array(cmask) > 127).mean()))

clean = inpaint(crop, cmask, "clean")
final = img.copy()
final.paste(clean, (0, crop_top))
final = final.crop((0, 0, W, int(H * 0.983)))           # drop the story footer entirely
out_main = os.path.join(OUT, "photo_clean.png")
final.save(out_main)
log("FINAL: %s (%dx%d)" % (out_main, final.size[0], final.size[1]))

# diagnostics: what the mask covered and before/after preview
m.save(os.path.join(OUT, "photo_clean_mask.png"))
prev = Image.new("RGB", (W * 2 + 20, H), (25, 25, 25))
prev.paste(img, (0, 0)); prev.paste(final, (W + 20, 0))
prev.save(os.path.join(OUT, "photo_clean_before_after.png"))
log("BEFORE/AFTER: %s" % os.path.join(OUT, "photo_clean_before_after.png"))
