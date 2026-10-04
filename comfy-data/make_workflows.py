# -*- coding: utf-8 -*-
"""
make_workflows.py
Запускається вбудованим python з ComfyUI.
1. Чекає, поки ComfyUI підніме HTTP-сервер.
2. Забирає /object_info (живі схеми вузлів).
3. Перевіряє, що потрібні вузли існують.
4. Збирає робочі процеси в API-форматі та кладе у C:\\AI\\workflows.
5. Робить контрольний txt2img через /prompt і чекає результат.
"""
import json, os, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
OUT_DIR = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\comfy-data\workflows"
CKPT_DIR = r"C:\AI\models\checkpoints"

def log(m):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), m), flush=True)

def get_json(url, timeout=20):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def post_json(url, payload, timeout=180):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

# ---------- 1. чекаємо сервер ----------
log("waiting for ComfyUI on %s ..." % HOST)
info = None
for i in range(180):
    try:
        info = get_json(HOST + "/object_info", timeout=10)
        break
    except Exception:
        time.sleep(2)
if info is None:
    log("FATAL: ComfyUI did not respond in 6 minutes")
    sys.exit(1)
log("server is up. nodes available: %d" % len(info))

# ---------- 2. що реально є ----------
wanted = ["CheckpointLoaderSimple", "LoadImage", "LoadImageMask", "VAEEncodeForInpaint",
          "VAEEncode", "VAEDecode", "KSampler", "CLIPTextEncode", "EmptyLatentImage",
          "SaveImage", "ImageScale", "ControlNetLoader", "ControlNetApplyAdvanced",
          "UpscaleModelLoader", "ImageUpscaleWithModel", "LoraLoader"]
for w in wanted:
    log("  %-26s %s" % (w, "OK" if w in info else "MISSING"))

# список чекпойнтів, які бачить ComfyUI
try:
    ckpts = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    log("checkpoints visible to ComfyUI: %s" % ckpts)
except Exception as e:
    ckpts = []
    log("could not read checkpoint list: %s" % e)

def pick(name_part, fallback):
    for c in ckpts:
        if name_part.lower() in c.lower():
            return c
    return fallback

ck_inpaint = pick("inpaint", "sd-v1-5-inpainting.ckpt")
ck_photo   = pick("realistic", pick("dream", "v1-5-pruned-emaonly.safetensors"))
log("will use inpaint checkpoint: %s" % ck_inpaint)
log("will use photo checkpoint  : %s" % ck_photo)

# допоміжні конструктори
def node(class_type, inputs, title=None):
    n = {"class_type": class_type, "inputs": inputs}
    if title:
        n["_meta"] = {"title": title}
    return n

def base_txt2img(ckpt, prompt, negative, w, h, steps, cfg, sampler, sched, seed, prefix):
    return {
        "1": node("CheckpointLoaderSimple", {"ckpt_name": ckpt}, "Checkpoint"),
        "2": node("CLIPTextEncode", {"text": prompt, "clip": ["1", 1]}, "Prompt (+)"),
        "3": node("CLIPTextEncode", {"text": negative, "clip": ["1", 1]}, "Prompt (-)"),
        "4": node("EmptyLatentImage", {"width": w, "height": h, "batch_size": 1}, "Empty latent"),
        "5": node("KSampler", {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                               "latent_image": ["4", 0], "seed": seed, "steps": steps, "cfg": cfg,
                               "sampler_name": sampler, "scheduler": sched, "denoise": 1.0}, "KSampler"),
        "6": node("VAEDecode", {"samples": ["5", 0], "vae": ["1", 2]}, "VAE Decode"),
        "7": node("SaveImage", {"images": ["6", 0], "filename_prefix": prefix}, "Save"),
    }

DEFAULT_NEG = ("lowres, bad anatomy, bad hands, extra digits, fewer digits, cropped, "
               "worst quality, low quality, jpeg artifacts, watermark, signature, text")

workflows = {}

# ---------- A. txt2img (база) ----------
workflows["01_txt2img.json"] = base_txt2img(
    ck_photo,
    "photo of a woman standing in a park, natural light, detailed skin, sharp focus",
    DEFAULT_NEG, 512, 512, 24, 7.0, "dpmpp_2m", "karras", 12345, "txt2img")

# ---------- B. img2img (переробити наявне зображення) ----------
workflows["02_img2img.json"] = {
    "1": node("CheckpointLoaderSimple", {"ckpt_name": ck_photo}, "Checkpoint"),
    "2": node("LoadImage", {"image": "input.png", "upload": "image"}, "Load image"),
    "3": node("VAEEncode", {"pixels": ["2", 0], "vae": ["1", 2]}, "VAE Encode"),
    "4": node("CLIPTextEncode", {"text": "same scene, more detail, photorealistic, sharp focus", "clip": ["1", 1]}, "Prompt (+)"),
    "5": node("CLIPTextEncode", {"text": DEFAULT_NEG, "clip": ["1", 1]}, "Prompt (-)"),
    "6": node("KSampler", {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
                           "latent_image": ["3", 0], "seed": 12345, "steps": 24, "cfg": 6.5,
                           "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 0.45}, "KSampler"),
    "7": node("VAEDecode", {"samples": ["6", 0], "vae": ["1", 2]}, "VAE Decode"),
    "8": node("SaveImage", {"images": ["7", 0], "filename_prefix": "img2img"}, "Save"),
}

# ---------- C. Inpainting (прибрати/замінити об'єкт, обличчя, тіло) ----------
workflows["03_inpaint.json"] = {
    "1": node("CheckpointLoaderSimple", {"ckpt_name": ck_inpaint}, "Checkpoint (inpainting)"),
    "2": node("LoadImage", {"image": "input.png", "upload": "image"}, "Load image"),
    "3": node("LoadImageMask", {"image": "mask.png", "channel": "red", "upload": "image"}, "Load mask (біле = що міняємо)"),
    "4": node("VAEEncodeForInpaint", {"pixels": ["2", 0], "vae": ["1", 2], "mask": ["3", 0],
                                      "grow_mask_by": 8}, "VAE Encode for inpaint"),
    "5": node("CLIPTextEncode", {"text": "what should appear inside the mask, photorealistic, sharp", "clip": ["1", 1]}, "Prompt (+)"),
    "6": node("CLIPTextEncode", {"text": DEFAULT_NEG, "clip": ["1", 1]}, "Prompt (-)"),
    "7": node("KSampler", {"model": ["1", 0], "positive": ["5", 0], "negative": ["6", 0],
                           "latent_image": ["4", 0], "seed": 12345, "steps": 28, "cfg": 7.0,
                           "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}, "KSampler"),
    "8": node("VAEDecode", {"samples": ["7", 0], "vae": ["1", 2]}, "VAE Decode"),
    "9": node("SaveImage", {"images": ["8", 0], "filename_prefix": "inpaint"}, "Save"),
}

# ---------- D. Inpaint + ControlNet openpose (заміна тіла зі збереженням пози) ----------
if "ControlNetLoader" in info and "ControlNetApplyAdvanced" in info:
    workflows["04_inpaint_controlnet_openpose.json"] = {
        "1": node("CheckpointLoaderSimple", {"ckpt_name": ck_inpaint}, "Checkpoint (inpainting)"),
        "2": node("LoadImage", {"image": "input.png", "upload": "image"}, "Load image (поза береться звідси)"),
        "3": node("LoadImageMask", {"image": "mask.png", "channel": "red", "upload": "image"}, "Load mask"),
        "4": node("ControlNetLoader", {"control_net_name": "control_v11p_sd15_openpose.pth"}, "ControlNet openpose"),
        "5": node("VAEEncodeForInpaint", {"pixels": ["2", 0], "vae": ["1", 2], "mask": ["3", 0],
                                          "grow_mask_by": 8}, "VAE Encode for inpaint"),
        "6": node("CLIPTextEncode", {"text": "photorealistic body matching the pose, detailed skin", "clip": ["1", 1]}, "Prompt (+)"),
        "7": node("CLIPTextEncode", {"text": DEFAULT_NEG, "clip": ["1", 1]}, "Prompt (-)"),
        "8": node("ControlNetApplyAdvanced", {"positive": ["6", 0], "negative": ["7", 0],
                                              "control_net": ["4", 0], "image": ["2", 0],
                                              "strength": 0.85, "start_percent": 0.0, "end_percent": 0.8},
                  "ControlNet apply"),
        "9": node("KSampler", {"model": ["1", 0], "positive": ["8", 0], "negative": ["8", 1],
                               "latent_image": ["5", 0], "seed": 12345, "steps": 28, "cfg": 7.0,
                               "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}, "KSampler"),
        "10": node("VAEDecode", {"samples": ["9", 0], "vae": ["1", 2]}, "VAE Decode"),
        "11": node("SaveImage", {"images": ["10", 0], "filename_prefix": "inpaint_pose"}, "Save"),
    }
else:
    log("ControlNet nodes not found - skipping workflow 04")

# ---------- E. Апскейл ----------
if "UpscaleModelLoader" in info and "ImageUpscaleWithModel" in info:
    workflows["05_upscale.json"] = {
        "1": node("LoadImage", {"image": "input.png", "upload": "image"}, "Load image"),
        "2": node("UpscaleModelLoader", {"model_name": "RealESRGAN_x4plus.pth"}, "Upscale model"),
        "3": node("ImageUpscaleWithModel", {"upscale_model": ["2", 0], "image": ["1", 0]}, "Upscale x4"),
        "4": node("SaveImage", {"images": ["3", 0], "filename_prefix": "upscaled"}, "Save"),
    }
else:
    log("Upscale nodes not found - skipping workflow 05")

# ---------- збереження ----------
os.makedirs(OUT_DIR, exist_ok=True)
for name, wf in workflows.items():
    p = os.path.join(OUT_DIR, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    log("wrote %s (%d nodes)" % (p, len(wf)))

# ---------- 3. контрольний запуск txt2img ----------
log("running test generation ...")
test = base_txt2img(ck_photo, "a red apple on a wooden table, studio light",
                    DEFAULT_NEG, 512, 512, 12, 6.0, "dpmpp_2m", "karras", 777, "selftest")
try:
    res = post_json(HOST + "/prompt", {"prompt": test})
    pid = res.get("prompt_id")
    log("queued prompt_id=%s" % pid)
    ok = False
    for i in range(150):
        time.sleep(2)
        try:
            hist = get_json(HOST + "/history/%s" % pid)
        except Exception:
            continue
        if pid in hist:
            h = hist[pid]
            status = h.get("status", {})
            log("status: %s" % status.get("status_str"))
            outs = h.get("outputs", {})
            files = []
            for nid, o in outs.items():
                for im in o.get("images", []):
                    files.append(im.get("filename"))
            if files:
                log("SELFTEST OK - generated: %s" % files)
                ok = True
            else:
                log("no images produced; status=%s" % json.dumps(status, ensure_ascii=False)[:800])
            break
    if not ok:
        log("SELFTEST FAILED")
except urllib.error.HTTPError as e:
    log("SELFTEST HTTP ERROR %s: %s" % (e.code, e.read().decode("utf-8", "ignore")[:1500]))
except Exception as e:
    log("SELFTEST ERROR: %r" % e)

log("DONE")

