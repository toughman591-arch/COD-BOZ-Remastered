import sys,json,os,glob,shutil,numpy as np
sys.path.insert(0,'/root/tools')
import texlib,rewrite,resgrp
from PIL import Image
X='/root/work/ximg/ximages'
SRC='/root/work/dz'; OUT=sys.argv[1]
plan=json.load(open('/root/work/plan.json'))
SKIP={0x5f590500,0xd4685d9f}
byfile={}
for p in plan:
    if p['hash'] in SKIP: continue
    byfile.setdefault(p['file'],[]).append(p)
log=[];previews=[]
for f,ps in byfile.items():
    d=open(os.path.join(SRC,f),'rb').read()
    R={t['hash']:t for t in texlib.records(d)}
    edits=[]
    for p in ps:
        t=R[p['hash']]
        pc=Image.open(os.path.join(X,p['src'])).convert('RGBA')
        fct=2 if os.environ.get('SAFE')!='1' and (2*t['w']<=pc.size[0] and 2*t['h']<=pc.size[1] and 2*max(t['w'],t['h'])<=512) else 1
        nw,nh=t['w']*fct,t['h']*fct
        mob=texlib.mip0(d,t).astype(np.float32)
        pr=np.asarray(pc.resize((t['w'],t['h']),Image.LANCZOS),np.float32)
        if t['alpha']:
            m=(mob[...,3]>128)&(pr[...,3]>128)
            gain=np.clip(mob[m][:, :3].mean(0)/np.maximum(pr[m][:, :3].mean(0),1),0.6,1.6) if m.sum()>16 else np.ones(3)
        else:
            gain=np.clip(mob[...,:3].reshape(-1,3).mean(0)/np.maximum(pr[...,:3].reshape(-1,3).mean(0),1),0.6,1.6)
        edits.append(rewrite.texture_edit(d,t,pc,nw,nh,gain=gain))
        log.append(dict(group=f,hash=hex(p['hash']),src=p['src'],old=[t['w'],t['h']],new=[nw,nh],gain=[round(float(x),2) for x in gain],alpha=t['alpha'],match=p['how']))
        previews.append((f,p['hash']))
    nd=rewrite.apply(d,edits)
    assert resgrp.walk(nd)['ok'],f
    R2={t['hash']:t for t in texlib.records(nd)}
    assert len(R2)==len(R)
    for t in R2.values(): assert t['pix']+sum(t['sizes'])==t['s']+t['size']-8
    os.makedirs(os.path.dirname(os.path.join(OUT,f)),exist_ok=True)
    open(os.path.join(OUT,f),'wb').write(nd)
    print(f,len(ps),'delta',len(nd)-len(d))
json.dump(log,open('/root/work/tex_log.json','w'),indent=1)
