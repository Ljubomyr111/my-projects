import json, urllib.request
info = json.loads(urllib.request.urlopen("http://127.0.0.1:8188/object_info", timeout=30).read())
for cls in ["ReActorFaceSwap", "ReActorRestoreFace", "INPAINT_LoadInpaintModel", "INPAINT_InpaintWithModel", "UpscaleModelLoader", "ControlNetLoader"]:
    d = info.get(cls)
    if not d: print("MISSING", cls); continue
    print("===", cls)
    for kind in ("required","optional"):
        for n,v in d.get("input",{}).get(kind,{}).items():
            t = v[0]
            if isinstance(t, list):
                print("   %-24s ENUM %s" % (n, t[:6]))
            else:
                print("   %-24s %s" % (n, t))
