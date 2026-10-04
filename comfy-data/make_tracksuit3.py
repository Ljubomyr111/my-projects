# -*- coding: utf-8 -*-
"""
Tracksuit, final approach: init-image inpainting.

The earlier attempts failed for two different reasons:
  * plain inpainting  -> the model re-drew the original clothes (mask too large)
  * rectangle paste   -> correct garment, but hard rectangular edges

Here we combine them: the generated tracksuit is pasted INTO THE MASK ONLY
(so the silhouette follows the selection, not a rectangle), and then inpainting
runs on that image with a LOW denoise, so the model harmonises lighting and
edges without re-drawing the garment.
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
T = (60, 585, 680, 1045)
B = (60, 1050, 680, 1305)

# ---------------------------------------------------------------- masks ----
def top_parts():
    tw, th = T[2]-T[0], T[3]-T[1]
    work = full.crop(T).resize((576, int(th*576/tw)), Image.LANCZOS)
    ww, wh = work.size
    prot = Image.new("L", (ww, wh), 0); pd = ImageDraw.Draw(prot)
    pd.ellipse([int(ww*0.26), -20, int(ww*0.76), int(wh*0.44)], fill=255)
    pd.rectangle([int(ww*0.560), int(wh*0.55), ww, wh], fill=255)
    pd.rectangle([0, int(wh*0.90), ww, wh], fill=255)
    pd.rectangle([0, 0, int(ww*0.075), wh], fill=255)
    pd.ellipse([int(ww*0.14), int(wh*0.62), int(ww*0.42), int(wh*0.94)], fill=255)
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
    return work, Image.fromarray((gm*255).astype(np.uint8))

def bot_parts():
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
    g2m = g2m & (((lum > 100) & (lum < 190) & (sat < 65)) | (lum > 90))
    g2m &= ~pm2
    g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 120
    g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(7))) > 120
    g2m &= ~pm2
    return work2, Image.fromarray((g2m*255).astype(np.uint8))

top_work, top_mask = top_parts()
bot_work, bot_mask = bot_parts()
log("masks ready")

# ------------------------------------------------------- tracksuit donor ----
def make_figure(seed, prompt):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "Realistic_Vision_V6.0_NV_B1_fp16.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text":
              "lowres, bad anatomy, deformed, worst quality, jpeg artifacts, text, two people, skirt, dress, nude",
              "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 768, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0],
              "negative": ["3", 0], "latent_image": ["4", 0], "seed": seed, "steps": 30, "cfg": 6.5,
              "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "donor"}},
    }
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 900:
        time.sleep(2)
        h = get(HOST + "/history/%s" % pid)
        if pid in h:
            f = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
            if f:
                return Image.open(os.path.join(OUT, f[0])).convert("RGB")
            return None
    return None

PROMPT = ("full length fashion photo of a woman standing facing the camera wearing a "
          "matching dark grey tracksuit: a long hip-length zip-up track jacket with white "
          "side stripes, fully zipped, and matching joggers, plain light grey studio "
          "background, soft even lighting, catalog photo, high waisted")

# Gentle luminance match. A full per-channel mean/std match washed the grey
# tracksuit out to near-white (it was being fitted to a bright white t-shirt),
# so only overall brightness is adjusted and the garment keeps its own colour.
def match_colours(patch, ref, m):
    p = np.array(patch).astype(np.float32)
    r = np.array(ref).astype(np.float32)
    lum_p = 0.299*p[:, :, 0] + 0.587*p[:, :, 1] + 0.114*p[:, :, 2]
    lum_r = 0.299*r[:, :, 0] + 0.587*r[:, :, 1] + 0.114*r[:, :, 2]
    src = lum_p[m].mean() if m.any() else lum_p.mean()
    dst = lum_r[m].mean() if m.any() else lum_r.mean()
    gain = float(np.clip(dst / max(src, 1e-3), 0.7, 1.3))   # capped, no washout
    out = np.clip(p * gain, 0, 255)
    return Image.fromarray(out.astype(np.uint8))

def init_image(box, mask, work, fig, part):
    rw, rh = box[2]-box[0], box[3]-box[1]
    roi = full.crop(box)
    m = np.array(mask.resize((rw, rh), Image.LANCZOS)).astype(np.float32)/255.0
    mend = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
    ys, xs = np.where(mend)
    y0, y1, x0, x1 = ys.min(), ys.max()+1, xs.min(), xs.max()+1
    fw, fh = fig.size
    # tight boxes around the garment on the generated figure (512x768)
    band = (fig.crop((int(fw*0.17), int(fh*0.25), int(fw*0.84), int(fh*0.60))) if part == "top"
            else fig.crop((int(fw*0.20), int(fh*0.60), int(fw*0.82), int(fh*0.95))))
    # scale to cover the target box, then centre-crop: keeps the figure's own
    # proportions instead of squashing it
    tw_, th_ = x1-x0, y1-y0
    k = max(tw_/band.size[0], th_/band.size[1])
    band = band.resize((max(1,int(band.size[0]*k)), max(1,int(band.size[1]*k))), Image.LANCZOS)
    bx = (band.size[0]-tw_)//2; by = (band.size[1]-th_)//2
    donor = band.crop((bx, by, bx+tw_, by+th_))
    canvas = roi.copy()
    canvas.paste(donor, (x0, y0))
    canvas = match_colours(canvas, roi, mend)
    # blend donor in ONLY where the mask is set, with a feathered edge
    c = np.array(canvas).astype(np.float32); o = np.array(roi).astype(np.float32)
    soft = np.array(mask.resize((rw, rh), Image.LANCZOS).filter(ImageFilter.GaussianBlur(4))).astype(np.float32)/255.0
    a3 = soft[:, :, None]
    out = o*(1-a3) + c*a3
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), mask.resize((rw, rh), Image.LANCZOS)

def refine(init_roi, mask_roi, tag, seed, denoise=0.55):
    init_roi.save(os.path.join(INP, "%s_img.png" % tag))
    mask_roi.save(os.path.join(INP, "%s_mask.png" % tag))
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd-v1-5-inpainting.ckpt"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": "%s_img.png" % tag}},
        "3": {"class_type": "LoadImageMask", "inputs": {"image": "%s_mask.png" % tag, "channel": "red"}},
        "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
              "mask": ["3", 0], "grow_mask_by": 4}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text":
              "woman wearing a dark grey athletic tracksuit, sportswear, natural light, "
              "fabric folds, photorealistic", "clip": ["1", 1]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text":
              "lowres, deformed, worst quality, jpeg artifacts, text, nude, underwear",
              "clip": ["1", 1]}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
              "negative": ["6", 0], "latent_image": ["4", 0], "seed": seed, "steps": 28,
              "cfg": 7.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": denoise}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": tag}},
    }
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 1200:
        time.sleep(2)
        h = get(HOST + "/history/%s" % pid)
        if pid in h:
            st = h[pid]["status"]
            f = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
            log("   refine %s: %s in %.1fs" % (tag, st.get("status_str"), time.time()-t0))
            if st.get("status_str") != "success" or not f:
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        log("      %s: %s" % (m[1].get("exception_type"), m[1].get("exception_message")))
                return None
            return Image.open(os.path.join(OUT, f[0])).convert("RGB")
    return None

results = []
for seed in (7101, 7102):
    fig = make_figure(seed, PROMPT)
    if fig is None:
        continue
    final = full.copy()
    for box, mask, work, part, tag in ((T, top_mask, top_work, "top", "ts_top_%d" % seed),
                                        (B, bot_mask, bot_work, "bottom", "ts_bot_%d" % seed)):
        rw, rh = box[2]-box[0], box[3]-box[1]
        init_roi, mask_roi = init_image(box, mask, work, fig, part)
        res = refine(init_roi, mask_roi, tag, seed)
        if res is None:
            res = init_roi
        # final composite: model output inside the mask, original outside
        rr = np.array(res.resize((rw, rh), Image.LANCZOS))
        mm = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
        oo = np.array(full.crop(box))
        cc = oo.copy(); cc[mm] = rr[mm]
        final.paste(Image.fromarray(cc), (box[0], box[1]))

    d = np.abs(np.array(final).astype(int) - np.array(full).astype(int)).mean(axis=2)
    log("seed %d: changed %d px (%.1f%%), caption %d, status %d, face %d, model panel %d" % (
        seed, (d > 6).sum(), 100.0*(d > 6).mean(), (d[1310:1425] > 6).sum(),
        (d[0:120] > 6).sum(), (d[380:650, 200:520] > 6).sum(), (d[560:1040, 370:660] > 6).sum()))
    out = os.path.join(OUT, "photo_tracksuit_final_%d.png" % seed)
    final.save(out)
    log("   RESULT: %s" % out)
    results.append((seed, out, final))

sc = 0.42
tiles = [full.resize((int(W*sc), int(H*sc)), Image.LANCZOS)]
for _, _, f in results:
    tiles.append(f.resize((int(W*sc), int(H*sc)), Image.LANCZOS))
sheet = Image.new("RGB", (tiles[0].size[0]*len(tiles) + 10*(len(tiles)-1), tiles[0].size[1]), (30, 30, 30))
for i, t in enumerate(tiles):
    sheet.paste(t, (i*(tiles[0].size[0]+10), 0))
p = os.path.join(OUT, "photo_tracksuit_final_compare.png")
sheet.save(p)
log("COMPARE: %s" % p)

if results:
    first = results[0][2]
    d = np.abs(np.array(first).astype(int) - np.array(full).astype(int)).mean(axis=2)
    y0, y1 = T[1], B[3]
    alpha = np.zeros((H, W), np.uint8)
    for box, mask in ((T, top_mask), (B, bot_mask)):
        rw, rh = box[2]-box[0], box[3]-box[1]
        mr = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
        sub = alpha[box[1]:box[3], box[0]:box[2]]
        sub[mr] = 255
    alpha = np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.5)))
    Image.fromarray(np.dstack([np.array(first), alpha]), "RGBA").save(os.path.join(LAY, "layer_tracksuit.png"))
    log("LAYER: %s" % os.path.join(LAY, "layer_tracksuit.png"))
log("DONE")


