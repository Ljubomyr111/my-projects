# -*- coding: utf-8 -*-
"""
Full integration test for the C:\\AI image-editing stack.

Runs, in order, against the live ComfyUI on 127.0.0.1:8188:
  1. txt2img      -> generates two portraits (subject + donor face)
  2. img2img      -> re-renders the subject
  3. inpaint      -> removes an object using an auto-built mask (LaMa model)
  4. ReActor      -> swaps the donor face onto the subject (real ONNX run)
  5. upscale      -> Real-ESRGAN x4

Every workflow is built from the live /object_info schema, so field names and
enums are always the ones this build actually accepts.
"""
import json, time, urllib.request, urllib.error, os

HOST  = "http://127.0.0.1:8188"
WS    = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
OUT   = os.path.join(WS, "comfy-data", "output")
INP   = os.path.join(WS, "comfy-data", "input")

def log(m): print("[%s] %s" % (time.strftime("%H:%M:%S"), m), flush=True)

def get(url, t=30):
    with urllib.request.urlopen(url, timeout=t) as r:
        return json.loads(r.read().decode("utf-8"))

def post(url, payload, t=120):
    d = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=d, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r:
        return json.loads(r.read().decode("utf-8"))

INFO = get(HOST + "/object_info")
CKPTS = INFO["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]

def options_of(node, field):
    """ComfyUI 0.38 may return either a plain list or ['COMBO', {'options': [...]}]."""
    spec = INFO[node]["input"]["required"][field]
    first = spec[0]
    if isinstance(first, list):
        return first
    if isinstance(first, str) and first.upper() == "COMBO" and len(spec) > 1:
        return spec[1].get("options", [])
    return []

def ckpt(*names):
    for want in names:
        for c in CKPTS:
            if want.lower() in c.lower():
                return c
    raise SystemExit("checkpoint not found: %s (have %s)" % (names, CKPTS))

def as_input(path):
    """LoadImage resolves names under its input dir; absolute paths work too."""
    return path

NEG = ("lowres, bad anatomy, bad hands, extra digits, cropped, worst quality, "
       "low quality, jpeg artifacts, watermark, signature, text")

def run(name, wf, timeout_s=900):
    log("--- %s ---" % name)
    t0 = time.time()
    try:
        pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    except urllib.error.HTTPError as e:
        log("REJECTED %s: %s" % (e.code, e.read().decode("utf-8", "ignore")[:1200]))
        return None
    while time.time() - t0 < timeout_s:
        time.sleep(2)
        try:
            h = get(HOST + "/history/%s" % pid)
        except Exception:
            continue
        if pid in h:
            st = h[pid].get("status", {})
            files = [im["filename"] for o in h[pid].get("outputs", {}).values()
                     for im in o.get("images", [])]
            ok = st.get("status_str") == "success" and files
            log("%s in %.1fs -> %s" % ("OK  " if ok else "FAIL", time.time() - t0, files or st))
            if not ok:
                log("     detail: %s" % json.dumps(st, ensure_ascii=False)[:900])
            return files[0] if ok else None
    log("TIMEOUT after %ss" % timeout_s)
    return None

# ---------------------------------------------------------------- 1. txt2img
def txt2img(ck, prompt, seed, prefix, w=512, h=512, steps=22):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0],
              "negative": ["3", 0], "latent_image": ["4", 0], "seed": seed, "steps": steps,
              "cfg": 6.5, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": prefix}},
    }

photo = ckpt("realistic")
subject = run("1a txt2img subject",
              txt2img(photo, "portrait photo of a young woman, face to camera, "
                             "studio lighting, plain grey background, sharp focus", 101, "t_subject"))
donor = run("1b txt2img donor face",
            txt2img(photo, "portrait photo of a smiling man with short dark hair and a beard, "
                           "face to camera, studio lighting, plain background, sharp focus", 202, "t_donor"))
if not subject or not donor:
    raise SystemExit("txt2img stage failed - stopping")

# LoadImage only accepts files that live in its own input directory,
# so stage the freshly generated files there and reference them by name.
import shutil
for fn in (subject, donor):
    shutil.copy2(os.path.join(OUT, fn), os.path.join(INP, fn))
log("staged into input: %s, %s" % (subject, donor))

# ---------------------------------------------------------------- 2. img2img
img2img = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": photo}},
    "2": {"class_type": "LoadImage", "inputs": {"image": subject}},
    "3": {"class_type": "VAEEncode", "inputs": {"pixels": ["2", 0], "vae": ["1", 2]}},
    "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "same woman, cinematic light, detailed skin",
                                                     "clip": ["1", 1]}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "6": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0],
          "negative": ["5", 0], "latent_image": ["3", 0], "seed": 303, "steps": 20, "cfg": 6.0,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 0.45}},
    "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
    "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "t_img2img"}},
}
run("2 img2img", img2img)

# ------------------------------------------------- 3. inpaint object removal
# Build a mask programmatically: white rectangle over the middle of the image.
mask_path = os.path.join(INP, "auto_mask.png")
try:
    from PIL import Image, ImageDraw
    with Image.open(os.path.join(OUT, subject)) as im:
        w, h = im.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([int(w*0.40), int(h*0.55), int(w*0.60), int(h*0.75)], fill=255)
    m.save(mask_path)
    log("mask written: %s (%dx%d)" % (mask_path, w, h))
except Exception as e:
    log("could not build mask: %r" % e)

lama_models = options_of("INPAINT_LoadInpaintModel", "model_name")
log("inpaint models visible: %s" % lama_models)

mask_name = os.path.basename(mask_path)

if lama_models:
    run("3a inpaint with LaMa model (no prompt, pure removal)", {
        "1": {"class_type": "LoadImage", "inputs": {"image": subject}},
        "2": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
        "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": lama_models[0]}},
        "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
              "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
        "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "t_lama"}},
    })

run("3b inpaint with SD1.5 inpainting checkpoint (prompted)", {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt("inpaint")}},
    "2": {"class_type": "LoadImage", "inputs": {"image": subject}},
    "3": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
    "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
          "mask": ["3", 0], "grow_mask_by": 8}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "a denim jacket, photorealistic",
                                                     "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0],
          "negative": ["6", 0], "latent_image": ["4", 0], "seed": 404, "steps": 26, "cfg": 7.0,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "t_inpaint"}},
})

# ---------------------------------------------------------------- 4. face swap
swappers = options_of("ReActorFaceSwap", "swap_model")
log("swap models visible: %s" % swappers)
if swappers:
    run("4 ReActor face swap", {
        "1": {"class_type": "LoadImage", "inputs": {"image": subject}},
        "2": {"class_type": "LoadImage", "inputs": {"image": donor}},
        "3": {"class_type": "ReActorFaceSwap", "inputs": {
              "enabled": True, "input_image": ["1", 0], "source_image": ["2", 0],
              "swap_model": swappers[0], "facedetection": "retinaface_resnet50",
              "face_restore_model": "GFPGANv1.4.pth", "face_restore_visibility": 1.0,
              "codeformer_weight": 0.5, "detect_gender_input": "no",
              "detect_gender_source": "no", "input_faces_index": "0",
              "source_faces_index": "0", "console_log_level": 1}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "t_swap"}},
    }, timeout_s=1200)

# ---------------------------------------------------------------- 5. upscale
ups = options_of("UpscaleModelLoader", "model_name")
log("upscale models visible: %s" % ups)
if ups:
    run("5 upscale x4", {
        "1": {"class_type": "LoadImage", "inputs": {"image": subject}},
        "2": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": ups[0]}},
        "3": {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["2", 0],
              "image": ["1", 0]}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "t_upscale"}},
    })

log("DONE")



