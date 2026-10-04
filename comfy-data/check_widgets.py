import json, urllib.request
info = json.loads(urllib.request.urlopen("http://127.0.0.1:8188/object_info", timeout=30).read())
def widget_names(cls):
    out = []
    for kind in ("required", "optional"):
        for name, spec in info[cls]["input"].get(kind, {}).items():
            t = spec[0]
            is_link = not (isinstance(t, list) or (isinstance(t, str) and (t.upper() == "COMBO" or t in ("INT","FLOAT","STRING","BOOLEAN"))))
            if not is_link:
                out.append(name)
    return out
d = json.load(open(r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\comfy-data\workflows\ui_06_faceswap.json", encoding="utf-8"))
for n in d["nodes"]:
    names = widget_names(n["type"])
    vals = n.get("widgets_values", [])
    print("== %s (id %s)" % (n["type"], n["id"]))
    if len(names) != len(vals):
        print("   MISMATCH: %d widgets vs %d values" % (len(names), len(vals)))
    for nm, v in zip(names, vals):
        print("   %-26s = %r" % (nm, v))
    for inp in n.get("inputs", []):
        print("   [link] %-19s <- link %s" % (inp["name"], inp.get("link")))
