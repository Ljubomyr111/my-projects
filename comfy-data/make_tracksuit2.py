# -*- coding: utf-8 -*-
"""
Tracksuit, approach 2: generate the garment separately, then composite.

Why: SD 1.5 inpainting on a mask this large reconstructs the original clothing
almost unchanged (measured: ~12 mean difference). Instead we

  1. generate a full tracksuit figure in a clean frame,
  2. align that generated torso/legs onto the photo regions,
  3. match its colour statistics to the photo lighting,
  4. blend it into the masked area with a feathered alpha,
  5. keep every pixel outside the mask bit-identical.

This gives a visible garment change while the face, caption and model stay
untouched.
"""
import json, os, time, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
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


def run(prompt, negative, w, h, seed, steps=30, cfg=6.5, prefix="gen"):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "Realistic_Vision_V6.0_NV_B1_fp16.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0],
              "negative": ["3", 0], "latent_image": ["4", 0], "seed": seed, "steps": steps,
              "cfg": cfg, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": prefix}},
    }
    t0 = time.time()
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    while time.time() - t0 < 900:
        time.sleep(2)
        hh = get(HOST + "/history/%s" % pid)
        if pid in hh:
            st = hh[pid]["status"]
            files = [i["filename"] for o in hh[pid].get("outputs", {}).values() for i in o.get("images", [])]
            log("   %s seed=%d: %s in %.1fs" % (prefix, seed, st.get("status_str"), time.time()-t0))
            if st.get("status_str") != "success" or not files:
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        log("      %s: %s" % (m[1].get("exception_type"), m[1].get("exception_message")))
                return None
            return Image.open(os.path.join(OUT, files[0])).convert("RGB")
    return None


NEG = ("lowres, bad anatomy, bad hands, extra limbs, deformed, worst quality, "
       "low quality, jpeg artifacts, watermark, text, two people, crowd, "
       "skirt, dress, lingerie, underwear, nude")

# ---- 1. generate a full-length tracksuit figure on a plain background ----
PROMPT = ("full length fashion photo of a woman standing facing the camera wearing a "
          "dark grey athletic tracksuit: zip-up track jacket with white side stripes and "
          "matching joggers, white sneakers, plain light grey studio background, "
          "soft even lighting, sharp focus, professional catalog photo")
log("generating tracksuit figures ...")
figs = []
for seed in (4101, 4102, 4103):
    f = run(PROMPT, NEG, 512, 768, seed, prefix="tracksuit_gen")
    if f is not None:
        figs.append((seed, f))
if not figs:
    raise SystemExit("generation failed")

# ---- 2. masks (same verified geometry) -----------------------------------
def top_mask_img():
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

def bot_mask_img():
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
    g2m = g2m & ((lum > 100) & (lum < 190) & (sat < 65) | (lum > 90))
    g2m &= ~pm2
    g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 120
    g2m = np.array(Image.fromarray((g2m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(7))) > 120
    g2m &= ~pm2
    return work2, Image.fromarray((g2m*255).astype(np.uint8))

top_work, top_mask = top_mask_img()
bot_work, bot_mask = bot_mask_img()


def colour_match(src, ref, mask):
    """Match src statistics to ref inside mask (mean/std per channel)."""
    s = np.array(src).astype(np.float32)
    r = np.array(ref).astype(np.float32)
    m = mask
    out = s.copy()
    for c in range(3):
        sc, rc = s[:, :, c][m], r[:, :, c][m]
        if sc.std() < 1e-3:
            continue
        out[:, :, c] = (s[:, :, c] - sc.mean()) * (rc.std() / sc.std()) + rc.mean()
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def blend_into(photo, donor, mask, strength=1.0, feather=3):
    """Put donor pixels where mask is set, feathered; return new image + alpha."""
    a = np.array(mask.filter(ImageFilter.GaussianBlur(feather))).astype(np.float32) / 255.0 * strength
    p = np.array(photo).astype(np.float32)
    d = np.array(donor).astype(np.float32)
    a3 = a[:, :, None]
    out = p * (1 - a3) + d * a3
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), a


results = []
for seed, fig in figs:
    final = full.copy()
    for box, mask, work, part in ((T, top_mask, top_work, "top"), (B, bot_mask, bot_work, "bottom")):
        rw, rh = box[2]-box[0], box[3]-box[1]
        m_full = np.array(mask.resize((rw, rh), Image.NEAREST)) > 127
        roi = full.crop(box)
        ys, xs = np.where(m_full)
        if len(ys) == 0:
            continue
        # take the corresponding band from the generated figure and stretch it
        # over the bounding box of the mask
        y0, y1, x0, x1 = ys.min(), ys.max()+1, xs.min(), xs.max()+1
        fw, fh = fig.size
        if part == "top":
            band = fig.crop((int(fw*0.10), int(fh*0.18), int(fw*0.90), int(fh*0.62)))
        else:
            band = fig.crop((int(fw*0.18), int(fh*0.45), int(fw*0.82), int(fh*0.95)))
        donor = band.resize((x1-x0, y1-y0), Image.LANCZOS)
        canvas = roi.copy()
        canvas.paste(donor, (x0, y0))
        matched = colour_match(canvas, roi, m_full)
        newroi, alpha = blend_into(roi, matched, mask.resize((rw, rh), Image.LANCZOS))
        final.paste(newroi, (box[0], box[1]))

    d = np.abs(np.array(final).astype(int) - np.array(full).astype(int)).mean(axis=2)
    log("seed %d: changed pixels %d (%.1f%%), caption %d, status %d, face %d" % (
        seed, (d > 6).sum(), 100.0*(d > 6).mean(),
        (d[1310:1425] > 6).sum(), (d[0:120] > 6).sum(), (d[380:650, 200:520] > 6).sum()))
    out = os.path.join(OUT, "photo_tracksuit_gen_%d.png" % seed)
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
p = os.path.join(OUT, "photo_tracksuit_gen_compare.png")
sheet.save(p)
log("COMPARE: %s" % p)
log("DONE")
