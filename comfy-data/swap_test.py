# -*- coding: utf-8 -*-
"""Face-swap only test: reuses the already staged subject/donor images."""
import json, time, urllib.request, urllib.error, os

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP  = os.path.join(WS, "comfy-data", "input")

def log(m): print("[%s] %s" % (time.strftime("%H:%M:%S"), m), flush=True)
def get(u, t=30):
    with urllib.request.urlopen(u, timeout=t) as r: return json.loads(r.read().decode())
def post(u, p, t=120):
    req = urllib.request.Request(u, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=t) as r: return json.loads(r.read().decode())

info = get(HOST + "/object_info")
if "ReActorFaceSwap" not in info:
    raise SystemExit("ReActor node not loaded")

swappers = info["ReActorFaceSwap"]["input"]["required"]["swap_model"]
swappers = swappers[0] if isinstance(swappers[0], list) else swappers[1]["options"]
log("swap models: %s" % swappers)

# newest staged pair
subs = sorted([f for f in os.listdir(INP) if f.startswith("t_subject")])
dons = sorted([f for f in os.listdir(INP) if f.startswith("t_donor")])
if not subs or not dons:
    raise SystemExit("no staged images in %s" % INP)
subject, donor = subs[-1], dons[-1]
log("subject=%s donor=%s" % (subject, donor))

wf = {
    "1": {"class_type": "LoadImage", "inputs": {"image": subject}},
    "2": {"class_type": "LoadImage", "inputs": {"image": donor}},
    "3": {"class_type": "ReActorFaceSwap", "inputs": {
          "enabled": True, "input_image": ["1", 0], "source_image": ["2", 0],
          "swap_model": swappers[0], "facedetection": "retinaface_resnet50",
          "face_restore_model": "GFPGANv1.4.pth", "face_restore_visibility": 1.0,
          "codeformer_weight": 0.5, "detect_gender_input": "no",
          "detect_gender_source": "no", "input_faces_index": "0",
          "source_faces_index": "0", "console_log_level": 2}},
    "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "swap_test"}},
}
t0 = time.time()
try:
    pid = post(HOST + "/prompt", {"prompt": wf})["prompt_id"]
except urllib.error.HTTPError as e:
    raise SystemExit("rejected: %s %s" % (e.code, e.read().decode("utf-8", "ignore")[:1500]))
log("queued %s" % pid)
while time.time() - t0 < 1800:
    time.sleep(3)
    h = get(HOST + "/history/%s" % pid)
    if pid in h:
        st = h[pid]["status"]
        files = [i["filename"] for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
        print("STATUS:", st.get("status_str"), "in %.1fs" % (time.time() - t0))
        if st.get("status_str") != "success":
            for m in st.get("messages", []):
                if m[0] == "execution_error":
                    print("  NODE:", m[1].get("node_type"))
                    print("  MSG :", m[1].get("exception_message"))
                    print("  TYPE:", m[1].get("exception_type"))
        print("FILES:", files)
        break
log("DONE")
