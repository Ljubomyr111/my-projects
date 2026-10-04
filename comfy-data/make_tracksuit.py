# -*- coding: utf-8 -*-
"""
Replace the clothing with a SPORTS TRACKSUIT.

Uses the same verified masking as the earlier outfit work:
  * top region  y 585..1045   (protected: head/hair, her hand, model panel)
  * legs region y 1050..1305  (stops above the caption text)
  * Real inpaint checkpoint + VAEEncodeForInpaint (the combination that actually
    respects the mask; a plain checkpoint + VAEEncode repaints the whole frame)
  * only masked pixels are taken from the model output, everything else is
    restored from the original, so the result is measured, not assumed.
"""
import json, os, time, urllib.request
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP  = os.path.join(WS, "comfy-data", "input")
OUT  = os.path.join(WS, "comfy-data", "output")
LAY  = os.path.join(WS, "comfy-data", "layers")
os.makedirs(LAY, exist_ok=True)

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
       "low quality, jpeg artifacts, watermark, text, skirt, dress, bare shoulders, "
       "cleavage, lingerie, underwear, nude, topless")

T = (60, 585, 680, 1045)      # top
B = (60, 1050, 680, 1305)     # legs, safely above the caption


def inpaint(img, mask, prompt, tag, seed, steps=38, cfg=8.5, denoise=1.0):
    img.save(os.path.join(INP, "%s_img.png" % tag))
    mask.save(os.path.join(INP, "%s_mask.png" % tag))
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd-v1-5-inpainting.ckpt"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": "%s_img.png" % tag}},
        "3": {"class_type": "LoadImageMask", "inputs": {"image": "%s_mask.png" % tag, "channel": "red"}},
        "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
              "mask": ["3", 0], "grow_mask_by": 6}},
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
            log("   %s seed=%d: %s in %.1fs" % (tag, seed, st.get("status_str"), time.time() - t0))
            if st.get("status_str") != "success":
                for msg in st.get("messages", []):
                    if msg[0] == "execution_error":
                        log("      %s: %s" % (msg[1].get("exception_type"), msg[1].get("exception_message")))
                return None
            return Image.open(os.path.join(OUT, files[0])).convert("RGB")
    log("   %s TIMEOUT" % tag)
    return None


def build_masks():
    """Return (top_work, top_mask, bot_work, bot_mask) with the verified geometry."""
    # ---- top ----
    tw, th = T[2]-T[0], T[3]-T[1]
    work = full.crop(T).resize((576, int(th*576/tw)), Image.LANCZOS)
    ww, wh = work.size
    prot = Image.new("L", (ww, wh), 0); pd = ImageDraw.Draw(prot)
    pd.ellipse([int(ww*0.26), -20, int(ww*0.76), int(wh*0.44)], fill=255)   # head + hair
    pd.rectangle([int(ww*0.560), int(wh*0.55), ww, wh], fill=255)           # model panel
    pd.rectangle([0, int(wh*0.90), ww, wh], fill=255)                       # bottom edge
    pd.rectangle([0, 0, int(ww*0.075), wh], fill=255)
    pd.ellipse([int(ww*0.14), int(wh*0.62), int(ww*0.42), int(wh*0.94)], fill=255)  # her hand
    pm = np.array(prot) > 127
    g = Image.new("L", (ww, wh), 0); gd = ImageDraw.Draw(g)
    gd.ellipse([int(ww*0.20), int(wh*0.30), int(ww*0.60), int(wh*0.93)], fill=255)
    gd.ellipse([int(ww*0.11), int(wh*0.26), int(ww*0.52), int(wh*0.64)], fill=255)
    gd.rectangle([int(ww*0.09), int(wh*0.34), int(ww*0.27), int(wh*0.88)], fill=255)
    gd.rectangle([int(ww*0.32), int(wh*0.26), int(ww*0.52), int(wh*0.42)], fill=255)
    gm = np.array(g) > 127
    gm &= ~pm
    gm = np.array(Image.fromarray((gm*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) > 120
    gm &= ~pm
    top_mask = Image.fromarray((gm*255).astype(np.uint8))
    log("top mask: %.1f%% of region, head hits=%d, model hits=%d" % (
        100*gm.mean(), int(gm[0:int(wh*0.44), int(ww*0.26):int(ww*0.76)].sum()),
        int(gm[int(wh*0.55):, int(ww*0.560):].sum())))

    # ---- legs ----
    bw, bh = B[2]-B[0], B[3]-B[1]
    work2 = full.crop(B).resize((576, int(bh*576/bw)), Image.LANCZOS)
    w2, h2 = work2.size
    prot2 = Image.new("L", (w2, h2), 0); p2 = ImageDraw.Draw(prot2)
    p2.rectangle([0, 0, int(w2*0.155), h2], fill=255)
    p2.rectangle([int(w2*0.80), 0, w2, h2], fill=255)
    p2.rectangle([0, int(h2*0.97), w2, h2], fill=255)
    pm2 = np.array(prot2) > 127
    g2 = Image.new("L", (w2, h2), 0); gd2 = ImageDraw.Draw(g2)
    gd2.rectangle([int(w2*0.17), 0, int(w2*0.78), h2], fill=255)
    g2m = np.array(g2) > 127
    arr = np.array(work2).astype(np.int16)
    lum = 0.299*arr[:, :, 0] + 0.587*arr[:, :, 1] + 0.114*arr[:, :, 2]
    sat = arr.max(axis=2) - arr.min(axis=2)
    trousers = (lum > 100) & (lum < 190) & (sat < 65)
    g2m = g2m & (trousers | (lum > 90))
    g2m &= ~pm2
    g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 120
    g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(7))) > 120
    g2m &= ~pm2
    bot_mask = Image.fromarray((g2m*255).astype(np.uint8))
    log("legs mask: %.1f%% of region" % (100*g2m.mean()))
    return work, top_mask, work2, bot_mask


work, top_mask, work2, bot_mask = build_masks()

TOP_PROMPT = ("woman wearing a dark grey athletic zip-up track jacket with white side "
              "stripes, sportswear, long sleeves, standing, fashion photo, fabric folds")
BOT_PROMPT = ("woman wearing dark grey tracksuit joggers with white side stripes, "
              "sportswear trousers, full length, fashion photo, fabric folds")

VARIANTS = [
    ("a", TOP_PROMPT, BOT_PROMPT, 1201, 1301),
    ("b", TOP_PROMPT, BOT_PROMPT, 1202, 1302),
]

def composited(top_res, bot_res):
    final = full.copy()
    for (box, res, mask) in ((T, top_res, top_mask), (B, bot_res, bot_mask)):
        rw, rh = box[2]-box[0], box[3]-box[1]
        res_roi = np.array(res.resize((rw, rh), Image.LANCZOS))
        mask_roi = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
        orig_roi = np.array(full.crop(box))
        comp = orig_roi.copy()
        comp[mask_roi] = res_roi[mask_roi]
        final.paste(Image.fromarray(comp), (box[0], box[1]))
    return final

results = []
for name, tp, bp, ts, bs in VARIANTS:
    log("variant %s" % name)
    top_res = inpaint(work, top_mask, tp, "sport_top_%s" % name, ts, cfg=8.0, denoise=0.98)
    bot_res = inpaint(work2, bot_mask, bp, "sport_bot_%s" % name, bs, cfg=8.0, denoise=0.98)
    if top_res is None or bot_res is None:
        continue
    final = composited(top_res, bot_res)

    # measurements: only the masked areas may differ
    d = np.abs(np.array(final).astype(int) - np.array(full).astype(int)).mean(axis=2)
    changed = (d > 6).sum()
    log("   changed pixels overall: %d (%.2f%% of frame)" % (changed, 100.0*changed/d.size))
    log("   caption rows changed: %d | status bar: %d | face zone: %d" % (
        (d[1310:1425] > 6).sum(), (d[0:120] > 6).sum(), (d[380:650, 200:520] > 6).sum()))

    out = os.path.join(OUT, "photo_tracksuit_%s.png" % name)
    final.save(out)
    log("   RESULT: %s" % out)
    results.append((name, out, final))

# comparison sheet
if results:
    sc = 0.42
    tiles = [full.resize((int(W*sc), int(H*sc)), Image.LANCZOS)]
    for _, _, f in results:
        tiles.append(f.resize((int(W*sc), int(H*sc)), Image.LANCZOS))
    sheet = Image.new("RGB", (tiles[0].size[0]*len(tiles) + 10*(len(tiles)-1), tiles[0].size[1]), (30, 30, 30))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i*(tiles[0].size[0]+10), 0))
    p = os.path.join(OUT, "photo_tracksuit_compare.png")
    sheet.save(p)
    log("COMPARE: %s" % p)

    # layer of the clothing from the first variant
    first = results[0][2]
    d = np.abs(np.array(first).astype(int) - np.array(full).astype(int)).mean(axis=2)
    geom = np.zeros((H, W), bool)
    for (box, mask) in ((T, top_mask), (B, bot_mask)):
        rw, rh = box[2]-box[0], box[3]-box[1]
        mr = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
        geom[box[1]:box[3], box[0]:box[2]] |= mr
    real = geom & (d > 6)
    alpha = np.array(Image.fromarray((real*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)))
    Image.fromarray(np.dstack([np.array(first), alpha]), "RGBA").save(
        os.path.join(LAY, "layer_tracksuit.png"))
    Image.fromarray(alpha, "L").save(os.path.join(LAY, "layer_tracksuit_mask.png"))
    log("LAYER: %s" % os.path.join(LAY, "layer_tracksuit.png"))
log("DONE")
