# -*- coding: utf-8 -*-
"""
Mask and replace the ENTIRE outfit (top + trousers) on the user's photo.

Two regions are inpainted separately (top, then legs) and composited back with
an overlap band, so nothing outside the clothing mask changes. Protected:
head/hair, the architectural model on the right, the phone status bar, the
story caption, the floor and the edges.
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
log("photo %dx%d" % (W, H))

NEG = ("lowres, bad anatomy, bad hands, extra limbs, deformed, worst quality, "
       "low quality, jpeg artifacts, watermark, text, bare shoulders, "
       "cleavage, lingerie, underwear, nude, topless, skirt")

def inpaint(img, mask, prompt, tag, seed, steps=38, cfg=8.5, denoise=0.96):
    img.save(os.path.join(INP, "%s_img.png" % tag))
    mask.save(os.path.join(INP, "%s_mask.png" % tag))
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "sd-v1-5-inpainting.ckpt"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": "%s_img.png" % tag}},
        "3": {"class_type": "LoadImageMask", "inputs": {"image": "%s_mask.png" % tag, "channel": "red"}},
        "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2], "mask": ["3", 0], "grow_mask_by": 6}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
              "negative": ["6", 0], "latent_image": ["4", 0], "seed": seed, "steps": steps,
              "cfg": cfg, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": denoise}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": tag}},
    }
    t0 = time.time()
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    while time.time() - t0 < 1800:
        time.sleep(2)
        h = get(HOST + "/history/%s" % pid)
        if pid in h:
            st = h[pid]["status"]
            files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
            log("  %s: %s in %.1fs" % (tag, st.get("status_str"), time.time() - t0))
            if st.get("status_str") != "success":
                for msg in st.get("messages", []):
                    if msg[0] == "execution_error":
                        log("     %s: %s" % (msg[1].get("exception_type"), msg[1].get("exception_message")))
                raise SystemExit(1)
            return Image.open(os.path.join(OUT, files[0])).convert("RGB")
    raise SystemExit("timeout on " + tag)

# =========================================================================
# REGION 1 - the top (t-shirt + cardigan),  y 585..1045
# =========================================================================
T = (60, 585, 680, 1045)
top_roi = full.crop(T)
tw, th = top_roi.size
work = top_roi.resize((576, int(th * 576 / tw)), Image.LANCZOS)
ww, wh = work.size
log("top region %dx%d -> %dx%d" % (tw, th, ww, wh))

prot = Image.new("L", (ww, wh), 0)
pd = ImageDraw.Draw(prot)
pd.ellipse([int(ww*0.26), -20, int(ww*0.76), int(wh*0.44)], fill=255)   # head + hair
pd.rectangle([int(ww*0.560), int(wh*0.55), ww, wh], fill=255)                   # model panel (lower right)
pd.rectangle([0, int(wh*0.90), ww, wh], fill=255)                       # bottom edge
pd.ellipse([int(ww*0.14), int(wh*0.62), int(ww*0.42), int(wh*0.94)], fill=255)   # her hand
pd.rectangle([0, 0, int(ww*0.075), wh], fill=255)
pm = np.array(prot) > 127

g = Image.new("L", (ww, wh), 0)
gd = ImageDraw.Draw(g)
gd.ellipse([int(ww*0.20), int(wh*0.30), int(ww*0.60), int(wh*0.93)], fill=255)   # trunk
gd.ellipse([int(ww*0.11), int(wh*0.26), int(ww*0.52), int(wh*0.64)], fill=255)   # shoulders / chest
gd.rectangle([int(ww*0.09), int(wh*0.34), int(ww*0.27), int(wh*0.88)], fill=255) # left sleeve
gd.rectangle([int(ww*0.32), int(wh*0.26), int(ww*0.52), int(wh*0.42)], fill=255) # collar
gm = np.array(g) > 127
gm &= ~pm
gm = np.array(Image.fromarray((gm*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) > 120
gm &= ~pm
top_mask = Image.fromarray((gm*255).astype(np.uint8))
log("top mask %.1f%% of region; protected-zone hits: head=%d model=%d" % (
    100*gm.mean(),
    int((gm & np.pad(np.ones((int(wh*0.44), int(ww*0.50)), bool), ((0, wh-int(wh*0.44)), (int(ww*0.26), ww-int(ww*0.76))))).sum()),
    int(gm[:, int(ww*0.575):].sum())))

TOPPROMPT = ("woman wearing a dark navy blue overshirt jacket over a charcoal black "
             "t-shirt, long sleeves, fashion photography, detailed fabric folds")

top_res = inpaint(work, top_mask, TOPPROMPT, "fit_top", seed=811)

# =========================================================================
# REGION 2 - the trousers, y 1040..1596
# =========================================================================
B = (60, 1050, 680, 1305)
bot_roi = full.crop(B)
bw, bh = bot_roi.size
work2 = bot_roi.resize((576, int(bh * 576 / bw)), Image.LANCZOS)
w2, h2 = work2.size
log("legs region %dx%d -> %dx%d" % (bw, bh, w2, h2))

prot2 = Image.new("L", (w2, h2), 0)
p2 = ImageDraw.Draw(prot2)
p2.rectangle([0, 0, int(w2*0.155), h2], fill=255)      # far left: floor
p2.rectangle([int(w2*0.80), 0, w2, h2], fill=255)      # right: model panel + floor
p2.rectangle([0, int(h2*0.97), w2, h2], fill=255)      # bottom edge only
pm2 = np.array(prot2) > 127

g2 = Image.new("L", (w2, h2), 0)
gd2 = ImageDraw.Draw(g2)
gd2.rectangle([int(w2*0.17), 0, int(w2*0.78), h2], fill=255)   # both legs column (full height)
g2m = np.array(g2) > 127
# refine with the trouser colour signature inside that column
arr = np.array(work2).astype(np.int16)
lum = 0.299*arr[:, :, 0] + 0.587*arr[:, :, 1] + 0.114*arr[:, :, 2]
sat = arr.max(axis=2) - arr.min(axis=2)
trousers = (lum > 100) & (lum < 190) & (sat < 65)
g2m = g2m & (trousers | (lum > 90))   # beige trousers incl. shadowed folds
g2m[int(h2*0.97):, :] = False   # keep the very bottom edge
g2m &= ~pm2
g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 120
g2m[int(h2*0.97):, :] = False   # re-apply after dilation
g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(7))) > 120
g2m &= ~pm2
bot_mask = Image.fromarray((g2m*255).astype(np.uint8))
log("legs mask %.1f%% of region; right-side hits (model) = %d" % (
    100*g2m.mean(), int(g2m[:, int(w2*0.80):].sum())))

BOTPROMPT = ("woman wearing dark navy blue slim trousers, full length, denim texture, "
             "fashion photography, detailed fabric folds")
bot_res = inpaint(work2, bot_mask, BOTPROMPT, "fit_bottom", seed=812)

# =========================================================================
# composite: only masked pixels come from the model output
# =========================================================================
final = full.copy()

for (box, res, mask, work_img) in ((T, top_res, top_mask, work), (B, bot_res, bot_mask, work2)):
    rw, rh = box[2]-box[0], box[3]-box[1]
    res_roi = np.array(res.resize((rw, rh), Image.LANCZOS))
    mask_roi = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
    orig_roi = np.array(full.crop(box))
    comp = orig_roi.copy()
    comp[mask_roi] = res_roi[mask_roi]
    final.paste(Image.fromarray(comp), (box[0], box[1]))
    d = np.abs(comp.astype(int) - orig_roi.astype(int)).mean(axis=2)
    log("region %s: outside-mask diff %.4f (0 = untouched), inside %.2f" % (
        box, d[~mask_roi].mean(), d[mask_roi].mean()))

out = os.path.join(OUT, "photo_full_outfit.png")
final.save(out)
log("RESULT: %s" % out)

# before/after of the whole frame, scaled to a viewable strip
sc = 0.42
a = full.resize((int(W*sc), int(H*sc)), Image.LANCZOS)
b = final.resize((int(W*sc), int(H*sc)), Image.LANCZOS)
strip = Image.new("RGB", (a.size[0]*2+10, a.size[1]), (25, 25, 25))
strip.paste(a, (0, 0)); strip.paste(b, (a.size[0]+10, 0))
strip.save(os.path.join(OUT, "photo_full_outfit_compare.png"))
log("COMPARE: %s" % os.path.join(OUT, "photo_full_outfit_compare.png"))





