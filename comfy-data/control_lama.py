# -*- coding: utf-8 -*-
"""
Controlled test: does INPAINT_InpaintWithModel actually replace masked pixels?

Builds a synthetic image (solid blue background, a big RED square in the
middle), masks exactly that red square, runs LaMa, and then measures whether
the masked area changed. Prints pixel values before/after at fixed points.
"""
import json, os, time, urllib.request
from PIL import Image, ImageDraw
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

W = H = 512
img = Image.new("RGB", (W, H), (30, 60, 200))          # blue background
d = ImageDraw.Draw(img)
BOX = (int(W*0.30), int(H*0.30), int(W*0.70), int(H*0.70))
d.rectangle(BOX, fill=(230, 20, 20))                    # red square
d.text((20, 20), "CONTEXT TEXT", fill=(255, 255, 255))

mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).rectangle(BOX, fill=255)

img.save(os.path.join(INP, "ctl_img.png"))
mask.save(os.path.join(INP, "ctl_mask.png"))
before = np.array(img)
print("BEFORE centre pixel:", before[H//2, W//2], " mask centre:",
      np.array(mask)[H//2, W//2])

wf = {
    "1": {"class_type": "LoadImage", "inputs": {"image": "ctl_img.png"}},
    "2": {"class_type": "LoadImageMask", "inputs": {"image": "ctl_mask.png", "channel": "red"}},
    "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": "big-lama.pt"}},
    "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
          "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
    "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "ctl_out"}},
}
pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
t0 = time.time()
while time.time() - t0 < 300:
    time.sleep(2)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
        print("status:", st.get("status_str"), files)
        if st.get("status_str") != "success":
            for m in st.get("messages", []):
                if m[0] == "execution_error":
                    print("  ", m[1].get("exception_type"), m[1].get("exception_message"))
            raise SystemExit(1)
        res = Image.open(os.path.join(OUT, files[0])).convert("RGB")
        after = np.array(res)
        print("AFTER  centre pixel:", after[H//2, W//2])
        inner = after[BOX[1]+20:BOX[3]-20, BOX[0]+20:BOX[2]-20]
        print("masked area: mean=%s  still-red pixels(%%)=%.1f" % (
            inner.reshape(-1, 3).mean(axis=0).round(1),
            100.0 * ((inner[:, :, 0] > 180) & (inner[:, :, 1] < 70)).mean()))
        # did anything change at all inside the mask?
        diff = np.abs(after.astype(int) - before.astype(int)).mean(axis=2)
        m = np.array(mask) > 127
        print("mean |change| inside mask: %.1f   outside mask: %.1f" % (
            diff[m].mean(), diff[~m].mean()))
        break
