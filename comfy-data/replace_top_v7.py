import json, os, time, urllib.request
from PIL import Image
import numpy as np
HOST="http://127.0.0.1:8188"; ws=r"C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
INP=os.path.join(ws,"comfy-data","input"); OUT=os.path.join(ws,"comfy-data","output")
def get(u,t=60):
    with urllib.request.urlopen(u,timeout=t) as r: return json.loads(r.read().decode())
def post(u,p,t=180):
    req=urllib.request.Request(u,data=json.dumps(p).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=t) as r: return json.loads(r.read().decode())
best=None
for cfg in (13.0,):
    wf={
     "1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":"v1-5-pruned-emaonly.safetensors"}},
     "2":{"class_type":"LoadImage","inputs":{"image":"c5_img.png"}},
     "3":{"class_type":"LoadImageMask","inputs":{"image":"c5_mask.png","channel":"red"}},
     "5":{"class_type":"VAEEncode","inputs":{"pixels":["2",0],"vae":["1",2]}},
     "6":{"class_type":"CLIPTextEncode","inputs":{"text":"dark navy blue blazer, blue jacket, blue clothing, woman","clip":["1",1]}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":"lowres, bad anatomy, deformed, worst quality, jpeg artifacts","clip":["1",1]}},
     "8":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["6",0],"negative":["7",0],
          "latent_image":["5",0],"seed":606,"steps":32,"cfg":cfg,
          "sampler_name":"dpmpp_2m","scheduler":"karras","denoise":1.0}},
     "10":{"class_type":"VAEDecode","inputs":{"samples":["8",0],"vae":["1",2]}},
     "11":{"class_type":"SaveImage","inputs":{"images":["10",0],"filename_prefix":"c7_cfg%d"%int(cfg)}}}
    t0=time.time(); pid=post(HOST+"/prompt",{"prompt":wf})["prompt_id"]
    while time.time()-t0<1200:
        time.sleep(2); h=get(HOST+"/history/%s"%pid)
        if pid in h:
            st=h[pid]["status"]; f=[i["filename"] for o in h[pid].get("outputs",{}).values() for i in o.get("images",[])]
            print("cfg",cfg,"status",st.get("status_str"),"%.1fs"%(time.time()-t0))
            if st.get("status_str")!="success":
                for m in st.get("messages",[]):
                    if m[0]=="execution_error": print("  ",m[1].get("exception_type"),m[1].get("exception_message"))
                break
            res=Image.open(os.path.join(OUT,f[0])).convert("RGB")
            m=np.array(Image.open(os.path.join(INP,"c5_mask.png")).resize(res.size,Image.NEAREST))>127
            a=np.array(res).astype(float)[m]
            blueness=(a[:,2]-a[:,0]).mean()
            print("  mean colour:",a.mean(axis=0).round(1)," blueness (B-R): %.1f"%blueness)
            roi=Image.open(os.path.join(INP,"c5_img.png")).convert("RGB")
            o=np.array(roi); n=np.array(res); o[m]=n[m]
            p=os.path.join(OUT,"photo_outfit_v7_roi.png"); Image.fromarray(o).save(p)
            print("  saved",p)
            break
