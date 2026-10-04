import json, sys
sys.path.insert(0, r"C:\AI\ComfyUI_windows_portable\ComfyUI")
from comfy_execution.graph_utils import GraphBuilder  # noqa
try:
    from app.frontend_management import FrontendManager
except Exception:
    pass
p = r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\comfy-data\workflows\ui_06_faceswap.json"
d = json.load(open(p, encoding="utf-8"))
print("keys:", sorted(d.keys()))
print("nodes:", [(n["id"], n["type"], len(n.get("widgets_values", []))) for n in d["nodes"]])
print("links:", d["links"])
sys.path.insert(0, r"C:\AI\ComfyUI_windows_portable\ComfyUI")
import execution, nodes as comfy_nodes
ok = True
for n in d["nodes"]:
    if n["type"] not in comfy_nodes.NODE_CLASS_MAPPINGS:
        print("UNKNOWN node type:", n["type"]); ok = False
print("all node types registered:", ok)
