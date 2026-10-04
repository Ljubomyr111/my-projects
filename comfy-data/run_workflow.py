# -*- coding: utf-8 -*-
"""
Run one of the generated workflows (or any ComfyUI API-format JSON) and wait
for the result.

Examples:
  python run_workflow.py 04_object_removal_lama.json
  python run_workflow.py 01_txt2img.json --set-prompt "a red car" --seed 999
  python run_workflow.py 02_img2img.json --image C:\\pics\\photo.jpg

Options:
  --image PATH   use this file wherever the workflow loads "input.png"
                 (its basename is referenced; the file is copied into the input dir)
  --mask PATH    same for "mask.png"
  --target PATH  same for "target.png"   (face swap)
  --source PATH  same for "source_face.png" (face swap)
  --set-prompt S replace every positive prompt text with S
  --seed N       override all seeds
  --steps N      override all sampler step counts
  --timeout N    seconds to wait (default 1800)
"""
import argparse, json, os, shutil, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
WF   = os.path.join(WS, "comfy-data", "workflows")
INP  = os.path.join(WS, "comfy-data", "input")

ap = argparse.ArgumentParser(add_help=True)
ap.add_argument("workflow")
ap.add_argument("--image"); ap.add_argument("--mask")
ap.add_argument("--target"); ap.add_argument("--source")
ap.add_argument("--set-prompt"); ap.add_argument("--seed", type=int)
ap.add_argument("--steps", type=int); ap.add_argument("--timeout", type=int, default=1800)
a = ap.parse_args()

def log(m): print(m, flush=True)
def get(u, t=30):
    with urllib.request.urlopen(u, timeout=t) as r: return json.loads(r.read().decode())
def post(u, p, t=120):
    req = urllib.request.Request(u, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r: return json.loads(r.read().decode())

path = a.workflow if os.path.isabs(a.workflow) else os.path.join(WF, a.workflow)
if not os.path.exists(path):
    sys.exit("workflow not found: %s" % path)
graph = json.load(open(path, encoding="utf-8"))

# stage replacement images into the input dir and remember their names
staged = {}
for placeholder, real in (("input.png", a.image), ("mask.png", a.mask),
                          ("target.png", a.target), ("source_face.png", a.source)):
    if not real:
        continue
    if not os.path.exists(real):
        sys.exit("file not found: %s" % real)
    name = os.path.basename(real)
    dst = os.path.join(INP, name)
    if os.path.abspath(real) != os.path.abspath(dst):
        try:
            shutil.copy2(real, dst)
        except OSError as e:
            log("warning: could not copy %s (%s); using it in place" % (name, e))
    staged[placeholder] = name
    log("using image %s" % name)

seed = a.seed
for nid, node in graph.items():
    ins = node.get("inputs", {})
    for key, val in list(ins.items()):
        if key == "image" and isinstance(val, str) and val in staged:
            ins[key] = staged[val]
        if key == "seed" and seed is not None:
            ins[key] = seed; seed += 1
        if key == "noise_seed" and seed is not None:
            ins[key] = seed
        if key == "steps" and a.steps is not None:
            ins[key] = a.steps
    if a.set_prompt and node.get("class_type") == "CLIPTextEncode":
        txt = ins.get("text", "")
        if not any(w in txt.lower() for w in ("lowres", "worst quality", "jpeg artifacts")):
            ins["text"] = a.set_prompt

log("submitting %s (%d nodes)" % (os.path.basename(path), len(graph)))
t0 = time.time()
try:
    pid = post(HOST + "/prompt", {"prompt": graph})["prompt_id"]
except urllib.error.HTTPError as e:
    sys.exit("REJECTED %s: %s" % (e.code, e.read().decode("utf-8", "ignore")[:1500]))
log("queued %s" % pid)

while time.time() - t0 < a.timeout:
    time.sleep(2)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
        log("status=%s  %.1fs" % (st.get("status_str"), time.time() - t0))
        for f in files:
            log("  output: %s" % os.path.join(WS, "comfy-data", "output", f))
        if st.get("status_str") != "success":
            for m in st.get("messages", []):
                if m[0] == "execution_error":
                    log("  ERROR in %s: %s" % (m[1].get("node_type"), m[1].get("exception_message")))
            sys.exit(1)
        sys.exit(0)
sys.exit("timeout after %ss" % a.timeout)
