# -*- coding: utf-8 -*-
"""
Build the ready-to-use workflows for the C:\\AI ComfyUI install.

Writes API-format graphs (loadable via Workflow -> Load in the ComfyUI UI,
and runnable with scripts/run_workflow.py) into <workspace>\\comfy-data\\workflows.

Everything is derived from the live /object_info schema, so option lists and
the ComfyUI 0.38 COMBO format are always handled correctly.
"""
import json, os, urllib.request

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
OUT  = os.path.join(WS, "comfy-data", "workflows")

def log(m): print(m, flush=True)

info = json.loads(urllib.request.urlopen(HOST + "/object_info", timeout=30).read())

def opts(node, field):
    spec = info[node]["input"]["required"][field]
    first = spec[0]
    if isinstance(first, list):
        return first
    if isinstance(first, str) and first.upper() == "COMBO" and len(spec) > 1:
        return spec[1].get("options", [])
    return []

CKPTS = opts("CheckpointLoaderSimple", "ckpt_name")
def ckpt(*wants):
    for w in wants:
        for c in CKPTS:
            if w.lower() in c.lower():
                return c
    raise SystemExit("no checkpoint matching %s in %s" % (wants, CKPTS))

INPAINT_CKPT = ckpt("inpaint")
PHOTO_CKPT   = ckpt("realistic")
ALT_CKPT     = ckpt("dream")
LAMA         = (opts("INPAINT_LoadInpaintModel", "model_name") or [None])[0]
CN           = opts("ControlNetLoader", "control_net_name")
ESRGAN       = (opts("UpscaleModelLoader", "model_name") or [None])[0]
SWAP         = (opts("ReActorFaceSwap", "swap_model") or [None])[0]

log("photo checkpoint : %s" % PHOTO_CKPT)
log("inpaint ckpt     : %s" % INPAINT_CKPT)
log("LaMa model       : %s" % LAMA)
log("controlnets      : %s" % CN)
log("upscaler         : %s" % ESRGAN)
log("swap model       : %s" % SWAP)

NEG = ("lowres, bad anatomy, bad hands, extra digits, fewer digits, cropped, "
       "worst quality, low quality, jpeg artifacts, watermark, signature, text")

def wf(d): return d
W = {}

# ---------------------------------------------------------------- 01 txt2img
W["01_txt2img.json"] = wf({
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": PHOTO_CKPT}},
    "2": {"class_type": "CLIPTextEncode", "inputs": {"text":
          "photo of a woman standing in a park, natural light, detailed skin, sharp focus", "clip": ["1", 1]}},
    "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
    "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
          "latent_image": ["4", 0], "seed": 12345, "steps": 24, "cfg": 6.5,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
    "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "txt2img"}},
})

# ---------------------------------------------------------------- 02 img2img
W["02_img2img.json"] = wf({
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": PHOTO_CKPT}},
    "2": {"class_type": "LoadImage", "inputs": {"image": "input.png"}},
    "3": {"class_type": "VAEEncode", "inputs": {"pixels": ["2", 0], "vae": ["1", 2]}},
    "4": {"class_type": "CLIPTextEncode", "inputs": {"text":
          "same person, same pose, cinematic lighting, detailed skin", "clip": ["1", 1]}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "6": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
          "latent_image": ["3", 0], "seed": 12345, "steps": 24, "cfg": 6.0,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 0.45}},
    "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
    "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "img2img"}},
})

# ------------------------------------------------- 03 inpaint: SD1.5 inpainting
W["03_inpaint_sd15.json"] = wf({
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": INPAINT_CKPT}},
    "2": {"class_type": "LoadImage", "inputs": {"image": "input.png"}},
    "3": {"class_type": "LoadImageMask", "inputs": {"image": "mask.png", "channel": "red"}},
    "4": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
          "mask": ["3", 0], "grow_mask_by": 8}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text":
          "what should appear inside the masked area, photorealistic, sharp", "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0], "negative": ["6", 0],
          "latent_image": ["4", 0], "seed": 12345, "steps": 28, "cfg": 7.0,
          "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "inpaint_sd15"}},
})

# ------------------------------------------------- 04 inpaint: LaMa (no prompt)
if LAMA:
    W["04_object_removal_lama.json"] = wf({
        "1": {"class_type": "LoadImage", "inputs": {"image": "input.png"}},
        "2": {"class_type": "LoadImageMask", "inputs": {"image": "mask.png", "channel": "red"}},
        "3": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": LAMA}},
        "4": {"class_type": "INPAINT_InpaintWithModel", "inputs": {"inpaint_model": ["3", 0],
              "image": ["1", 0], "mask": ["2", 0], "seed": 1}},
        "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "lama_removed"}},
    })

# ------------------------------------------------- 05 ControlNet-guided inpaint
cn_openpose = next((c for c in CN if "openpose" in c), None)
cn_depth    = next((c for c in CN if "depth" in c), None)
if cn_openpose:
    W["05_inpaint_controlnet_openpose.json"] = wf({
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": INPAINT_CKPT}},
        "2": {"class_type": "LoadImage", "inputs": {"image": "input.png"}},
        "3": {"class_type": "LoadImageMask", "inputs": {"image": "mask.png", "channel": "red"}},
        "4": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": cn_openpose}},
        "5": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["2", 0], "vae": ["1", 2],
              "mask": ["3", 0], "grow_mask_by": 8}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text":
              "photorealistic body in the given pose, detailed skin", "clip": ["1", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "8": {"class_type": "ControlNetApplyAdvanced", "inputs": {"positive": ["6", 0], "negative": ["7", 0],
              "control_net": ["4", 0], "image": ["2", 0], "strength": 0.85,
              "start_percent": 0.0, "end_percent": 0.8}},
        "9": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["8", 0],
              "negative": ["8", 1], "latent_image": ["5", 0], "seed": 12345, "steps": 28, "cfg": 7.0,
              "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["1", 2]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "inpaint_pose"}},
    })

# ------------------------------------------------- 06 face swap
if SWAP:
    W["06_faceswap.json"] = wf({
        "1": {"class_type": "LoadImage", "inputs": {"image": "target.png"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": "source_face.png"}},
        "3": {"class_type": "ReActorFaceSwap", "inputs": {
              "enabled": True, "input_image": ["1", 0], "source_image": ["2", 0],
              "swap_model": SWAP, "facedetection": "retinaface_resnet50",
              "face_restore_model": "GFPGANv1.4.pth", "face_restore_visibility": 1.0,
              "codeformer_weight": 0.5, "detect_gender_input": "no", "detect_gender_source": "no",
              "input_faces_index": "0", "source_faces_index": "0", "console_log_level": 1}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "faceswap"}},
    })

# ------------------------------------------------- 07 upscale
if ESRGAN:
    W["07_upscale_x4.json"] = wf({
        "1": {"class_type": "LoadImage", "inputs": {"image": "input.png"}},
        "2": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": ESRGAN}},
        "3": {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["2", 0], "image": ["1", 0]}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "upscaled"}},
    })

os.makedirs(OUT, exist_ok=True)
# clear stale files from earlier runs
for f in os.listdir(OUT):
    if f.endswith(".json"):
        os.remove(os.path.join(OUT, f))
for name, graph in sorted(W.items()):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=2, ensure_ascii=False)
    log("wrote %-38s %2d nodes" % (name, len(graph)))
log("total: %d workflows in %s" % (len(W), OUT))
