# -*- coding: utf-8 -*-
"""
Convert the API-format workflows into UI (graph) format so they can be opened
in the ComfyUI web UI with Workflow -> Open / drag-and-drop.

Widget order is taken from the LIVE /object_info schema (required inputs first,
then optional ones), which is exactly how the frontend lays them out, so the
widgets_values array lines up with the right fields.
"""
import json, os, urllib.request

HOST = "http://127.0.0.1:8188"
WS   = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
SRC  = os.path.join(WS, "comfy-data", "workflows-api")
DST  = os.path.join(WS, "comfy-data", "workflows")

info = json.loads(urllib.request.urlopen(HOST + "/object_info", timeout=30).read())

TYPE_COLOR = {
    "MODEL": "#B39DDB", "CLIP": "#FFD54F", "VAE": "#FF8A65", "CONDITIONING": "#FFA726",
    "LATENT": "#FF9CF9", "IMAGE": "#64B5F6", "MASK": "#81C784", "CONTROL_NET": "#6EE7B7",
    "UPSCALE_MODEL": "#7DD3FC", "INPAINT_MODEL": "#F9A8D4", "FACE_MODEL": "#FCA5A5",
}

def field_specs(cls):
    """Return [(name, is_link, type_or_enum, default)] in frontend widget order."""
    d = info.get(cls)
    if not d:
        return []
    out = []
    for kind in ("required", "optional"):
        for name, spec in d.get("input", {}).get(kind, {}).items():
            t = spec[0]
            extra = spec[1] if len(spec) > 1 else {}
            if isinstance(t, list):
                out.append((name, False, t, extra.get("default", t[0] if t else "")))
            elif isinstance(t, str) and t.upper() == "COMBO":
                o = extra.get("options", [])
                dflt = extra.get("default", o[0] if o else "")
                out.append((name, False, o, dflt))
            elif t in ("INT", "FLOAT", "STRING", "BOOLEAN"):
                dflt = extra.get("default", 0 if t == "INT" else (0.0 if t == "FLOAT" else ""))
                out.append((name, False, t, dflt))
            else:
                out.append((name, True, t, None))
    return out

def convert(api_graph, title):
    nodes, links = [], []
    order = sorted(api_graph.keys(), key=lambda k: int(k))
    info_by_id = {nid: api_graph[nid] for nid in order}

    for nid in order:
        node = info_by_id[nid]
        cls = node["class_type"]
        specs = field_specs(cls)
        if not specs:
            raise SystemExit("unknown node type in schema: %s" % cls)
        widgets, inputs = [], []
        for name, is_link, t, dflt in specs:
            val = node["inputs"].get(name)
            if is_link:
                inputs.append({"name": name, "type": t, "link": None})
            else:
                if val is None:
                    val = dflt
                widgets.append(val)
        nodes.append({
            "id": int(nid),
            "type": cls,
            "pos": [100 + (int(nid) % 5) * 340, 100 + (int(nid) // 5) * 260],
            "size": [300, 110 + 26 * max(0, len(widgets) - 1)],
            "flags": {},
            "order": int(nid),
            "mode": 0,
            "inputs": inputs,
            "outputs": [{"name": str(n), "type": t, "links": [], "slot_index": i}
                        for i, (n, t) in enumerate(zip(
                            info[cls].get("output_name") or [],
                            info[cls].get("output") or []))],
            "properties": {"Node name for S&R": cls},
            "widgets_values": widgets,
        })

    # links: (id, origin_id, origin_slot, target_id, target_slot, type)
    lid = 1
    for nid in order:
        node = info_by_id[nid]
        cls = node["class_type"]
        link_specs = [s for s in field_specs(cls) if s[1]]
        names = [s[0] for s in link_specs]
        for i, (name, _is, t, _d) in enumerate(link_specs):
            src = node["inputs"].get(name)
            if not src:
                continue
            src_id, src_slot = int(src[0]), int(src[1])
            # target input slot index among the UI-visible link inputs
            tgt = next(n for n in nodes if n["id"] == int(nid))
            tslot = next(j for j, inp in enumerate(tgt["inputs"]) if inp["name"] == name)
            links.append([lid, src_id, src_slot, int(nid), tslot, t])
            tgt["inputs"][tslot]["link"] = lid
            origin = next(n for n in nodes if n["id"] == src_id)
            if src_slot < len(origin["outputs"]):
                origin["outputs"][src_slot]["links"].append(lid)
            lid += 1

    return {
        "id": "wf-" + str(abs(hash(title)) % 10**10),
        "revision": 0,
        "last_node_id": max(int(n) for n in order),
        "last_link_id": lid - 1,
        "nodes": nodes,
        "links": links,
        "groups": [],
        "config": {},
        "extra": {"ds": {"scale": 0.75, "offset": [0, 0]}},
        "version": 0.4,
    }

os.makedirs(DST, exist_ok=True)
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".json"):
        continue
    api = json.load(open(os.path.join(SRC, f), encoding="utf-8"))
    ui = convert(api, f)
    out = os.path.join(DST, "ui_" + f)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(ui, fh, indent=2, ensure_ascii=False)
    print("UI  %-38s %2d nodes, %2d links" % (f, len(ui["nodes"]), len(ui["links"])))
print("written to", DST)

