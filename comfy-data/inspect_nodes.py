# -*- coding: utf-8 -*-
"""Inspect the custom nodes' input schemas so the test workflows use real field names."""
import json, urllib.request

info = json.loads(urllib.request.urlopen("http://127.0.0.1:8188/object_info", timeout=30).read())

def show(cls):
    if cls not in info:
        print("MISSING:", cls)
        return
    d = info[cls]
    print("=== %s (category=%s) ===" % (cls, d.get("category")))
    for kind in ("required", "optional"):
        spec = d.get("input", {}).get(kind, {})
        for name, val in spec.items():
            t = val[0]
            if isinstance(t, list):
                t = "ENUM[%d]" % len(t)
            extra = val[1] if len(val) > 1 else {}
            dflt = extra.get("default", "")
            print("   %-8s %-22s %-16s default=%s" % (kind, name, t, dflt))
    print("   outputs:", d.get("output"), "return_names:", d.get("output_name"))

for cls in ["ReActorFaceSwap", "ReActorFaceSwapOpt", "ReActorOptions", "ReActorFaceBoost",
            "Load Inpaint Model", "Inpaint (using Model)", "INPAINT_InpaintWithModel",
            "LoadInpaintModel", "InpaintModelConditioning"]:
    show(cls)

print()
print("=== all ReActor/Inpaint node names available ===")
for k in sorted(info):
    if "reactor" in k.lower() or "inpaint" in k.lower() or "lama" in k.lower():
        print("  ", k)
