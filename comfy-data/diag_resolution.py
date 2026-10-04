# -*- coding: utf-8 -*-
"""
Diagnose the smearing: run LaMa on the SAME masked content at different input
resolutions and measure whether the masked area comes out sharp (real pixels
replaced) or blurred (low-frequency hallucination).

Also compares a mask made by brightness detection against a hand-drawn one.
"""
import json, os, time, urllib.request
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP  = os.path.join(WS, "comfy-data", "input")
OUT  = os.path.join(WS, "comfy-data", "output")

def get(u, t=30):
    with urllib.request.urlopen(u, timeout=t) as r: return json.loads(r.read().decode())
def post(u, p, t=120):
    req = urllib.request.Request(u, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r: return json.loads(r.read().decode())

def lama(img, mask, tag):
    img.save(os.path.join(INP, "r_%s.png" % tag))
    mask.convert("L").save(os.path.join(INP, "rm_%s.png" % tag))
    wf = {
        "1": {"class_type": "LoadImage", "inputs": {"image": "r_%s.png" % tag}},
        "2": {"class_type": "LoadImageMask", "inputs": {"image": "rm_%s.png" % tag, "channel": "red"}},
        "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": "big-lama.pt"}},
        "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
              "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
        "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "r_" + tag}},
    }
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 600:
        time.sleep(2)
        h = get(HOST + "/history/%s" % pid)
        if pid in h:
            st = h[pid]["status"]
            if st.get("status_str") != "success":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        print("   ERR", m[1].get("exception_type"), m[1].get("exception_message"))
                return None
            f = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])][0]
            return Image.open(os.path.join(OUT, f)).convert("RGB")
    return None

SRC = os.path.join(INP, "WhatsApp Image 2026-10-03 at 22.46.19.jpeg")
full = Image.open(SRC).convert("RGB")
W, H = full.size

# text mask (brightness based), full resolution
TEXT_TOP, TEXT_BOT = 1360, 1520
region = np.array(full.crop((0, TEXT_TOP, W, TEXT_BOT)).convert("L"))
bright = (region > 195).astype(np.uint8) * 255
m_full = Image.new("L", (W, H), 0)
m_full.paste(Image.fromarray(bright), (0, TEXT_TOP))
m_full = m_full.filter(ImageFilter.MaxFilter(11))
print("text-only mask: %.2f%% of image" % (100.0 * (np.array(m_full) > 127).mean()))

def sharpness(im, box):
    a = np.array(im.crop(box).convert("L")).astype(float)
    gy, gx = np.gradient(a)
    return float(np.sqrt(gx**2 + gy**2).mean())

box = (0, TEXT_TOP, W, TEXT_BOT)

# --- A: full resolution ---
a = lama(full, m_full, "full")
if a is not None:
    print("A full-res  : sharpness in text area = %.2f" % sharpness(a, box))

# --- B: downscale to 512 on the long side, inpaint, upscale back ---
for target in (512, 1024):
    sc = target / max(W, H)
    small = full.resize((int(W*sc), int(H*sc)), Image.LANCZOS)
    smask = m_full.resize(small.size, Image.NEAREST)
    b = lama(small, smask, "s%d" % target)
    if b is None:
        continue
    back = b.resize((W, H), Image.LANCZOS)
    print("B %4d-res  : sharpness in text area = %.2f  (input size %s)" % (
        target, sharpness(back, box), small.size))
    back.save(os.path.join(OUT, "res_%d_back.png" % target))
