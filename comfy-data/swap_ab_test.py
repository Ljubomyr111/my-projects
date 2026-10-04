# -*- coding: utf-8 -*-
"""A/B/C test: same subject, three very different donor faces -> three swaps."""
import json, time, urllib.request, os, shutil

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

info = get(HOST + "/object_info")
swappers = info["ReActorFaceSwap"]["input"]["required"]["swap_model"]
swappers = swappers[0] if isinstance(swappers[0], list) else swappers[1]["options"]

def txt2img(prompt, seed, prefix, ckpt="realistic"):
    ck = [c for c in info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0] if ckpt in c.lower()][0]
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "lowres, blurry, bad anatomy", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
              "latent_image": ["4", 0], "seed": seed, "steps": 24, "cfg": 6.5,
              "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": prefix}},
    }

def run(name, wf, timeout_s=1500):
    t0 = time.time()
    try:
        pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
    except urllib.error.HTTPError as e:
        log("%-28s REJECTED %s %s" % (name, e.code, e.read().decode("utf-8", "ignore")[:400])); return None
    while time.time() - t0 < timeout_s:
        time.sleep(3)
        h = get(HOST + "/history/%s" % pid)
        if pid in h:
            st = h[pid]["status"]
            files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
            log("%-28s %-8s %5.1fs %s" % (name, st.get("status_str"), time.time() - t0, files))
            if st.get("status_str") != "success":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        log("      %s: %s" % (m[1].get("exception_type"), m[1].get("exception_message")))
            return files[0] if files else None
    log("%-28s TIMEOUT" % name); return None

# one fixed subject
subj = run("A0 subject", txt2img("portrait photo of a young woman looking at camera, "
                                 "neutral expression, plain grey background, sharp focus", 555, "ab_subject"))
donors = [
    ("B1 old_man",   "portrait photo of an 80 year old man with white hair and deep wrinkles, face to camera", 556, "ab_d_old"),
    ("B2 bald_man",  "portrait photo of a bald black man with a full beard, face to camera", 557, "ab_d_bald"),
    ("B3 asian_woman","portrait photo of a young east asian woman with black hair, face to camera", 558, "ab_d_asian"),
]
made = []
for label, prompt, seed, prefix in donors:
    f = run("gen " + label, txt2img(prompt, seed, prefix))
    if f: made.append((label, f))
if not subj or not made:
    raise SystemExit("generation stage failed")

shutil.copy2(os.path.join(OUT, subj), os.path.join(INP, subj))
for label, f in made:
    shutil.copy2(os.path.join(OUT, f), os.path.join(INP, f))

for label, f in made:
    wf = {
        "1": {"class_type": "LoadImage", "inputs": {"image": subj}},
        "2": {"class_type": "LoadImage", "inputs": {"image": f}},
        "3": {"class_type": "ReActorFaceSwap", "inputs": {
              "enabled": True, "input_image": ["1", 0], "source_image": ["2", 0],
              "swap_model": swappers[0], "facedetection": "retinaface_resnet50",
              "face_restore_model": "GFPGANv1.4.pth", "face_restore_visibility": 1.0,
              "codeformer_weight": 0.5, "detect_gender_input": "no", "detect_gender_source": "no",
              "input_faces_index": "0", "source_faces_index": "0", "console_log_level": 1}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "ab_swap_" + label}},
    }
    run("swap " + label, wf)
log("DONE")
