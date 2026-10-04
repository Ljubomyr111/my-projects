import json, os, time, urllib.request
from PIL import Image, ImageFilter
import numpy as np
HOST="http://127.0.0.1:8188"; ws=r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP=os.path.join(ws,"comfy-data","input"); OUT=os.path.join(ws,"comfy-data","output")
def get(u,t=60):
    import urllib.request as r
    with r.urlopen(u,timeout=t) as x: return json.loads(x.read().decode())
def post(u,p,t=120):
    import urllib.request as r
    q=r.Request(u,data=json.dumps(p).encode(),headers={"Content-Type":"application/json"})
    with r.urlopen(q,timeout=t) as x: return json.loads(x.read().decode())
full=Image.open(os.path.join(INP,"WhatsApp Image 2026-10-03 at 22.46.19.jpeg")).convert("RGB")
W,H=full.size; TEXT_TOP,TEXT_BOT=1360,1520
region=np.array(full.crop((0,TEXT_TOP,W,TEXT_BOT)).convert("L"))
bright=(region>195).astype(np.uint8)*255
m=Image.new("L",(W,H),0); m.paste(Image.fromarray(bright),(0,TEXT_TOP))
m=m.filter(ImageFilter.MaxFilter(13))
# paint the masked pixels MAGENTA
probe=np.array(full).copy()
sel=np.array(m)>127
probe[sel]=[255,0,255]
Image.fromarray(probe).save(os.path.join(INP,"probe_img.png"))
m.save(os.path.join(INP,"probe_mask.png"))
print("mask %.2f%%; magenta pixels painted: %d" % (100*sel.mean(), sel.sum()))
wf={"1":{"class_type":"LoadImage","inputs":{"image":"probe_img.png"}},
    "2":{"class_type":"LoadImageMask","inputs":{"image":"probe_mask.png","channel":"red"}},
    "3":{"class_type":"INPAINT_LoadInpaintModel","inputs":{"model_name":"big-lama.pt"}},
    "4":{"class_type":"INPAINT_InpaintWithModel","inputs":{"inpaint_model":["3",0],"image":["1",0],"mask":["2",0],"seed":1}},
    "5":{"class_type":"SaveImage","inputs":{"images":["4",0],"filename_prefix":"probe"}}}
pid=post(HOST+"/prompt",{"prompt":wf})["prompt_id"]; t0=time.time()
while time.time()-t0<600:
    time.sleep(2); h=get(HOST+"/history/%s"%pid)
    if pid in h:
        st=h[pid]["status"]; f=[i["filename"] for o in h[pid].get("outputs",{}).values() for i in o.get("images",[])][0]
        print("status",st.get("status_str"),f)
        res=np.array(Image.open(os.path.join(OUT,f)).convert("RGB")).astype(int)
        got=res[sel]
        magenta=((got[:,0]>200)&(got[:,1]<80)&(got[:,2]>200)).mean()
        print("after: magenta remaining in masked area = %.2f%%  (0% => model really replaces it)" % (100*magenta))
        print("mean colour after in masked area:", got.mean(axis=0).round(1))
        break
