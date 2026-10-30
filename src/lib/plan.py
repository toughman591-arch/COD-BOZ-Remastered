import pickle,sys,os,glob,json,numpy as np;sys.path.insert(0,'/root/tools')
import texlib
from hashes import djb2
from PIL import Image
X='/root/work/ximg/ximages'
res=pickle.load(open('/root/work/simres.pkl','rb'))
# name-based candidates
import match
name_map={}
for fn in os.listdir(X):
    base,cs=match.cands(fn)
    for c in cs: name_map[djb2(c)]=fn
vis_ok={2,3,4,5,6,9,10,12,13,17,20,21}
uniq={}
for r in res: uniq.setdefault(r[1],r)
sel=sorted([r for r in uniq.values() if 0.75<=r[6]<0.97],key=lambda r:-r[6])
sim_map={}
for r in uniq.values():
    if r[6]>=0.97: sim_map[r[1]]=r[5]
for i,r in enumerate(sel):
    if i in vis_ok: sim_map[r[1]]=r[5]
plan=[]
for f in sorted(glob.glob('/root/work/dz/levels/kino/*.group.bin')):
    d=open(f,'rb').read()
    for t in texlib.records(d):
        src=name_map.get(t['hash']) or sim_map.get(t['hash'])
        if not src: continue
        how='name' if t['hash'] in name_map else 'sim'
        mob=texlib.mip0(d,t).astype(np.float32)
        pc=Image.open(os.path.join(X,src)).convert('RGBA')
        pr=np.asarray(pc.resize((t['w'],t['h']),Image.LANCZOS),np.float32)
        a=mob[...,:3].reshape(-1,3);b=pr[...,:3].reshape(-1,3)
        ga=a.mean(1)-a.mean();gb=b.mean(1)-b.mean()
        ncc=float((ga*gb).sum()/(np.linalg.norm(ga)*np.linalg.norm(gb)+1e-6))
        asp_m=t['w']/t['h'];asp_p=pc.size[0]/pc.size[1]
        plan.append(dict(file=os.path.relpath(f,'/root/work/dz'),hash=t['hash'],w=t['w'],h=t['h'],alpha=t['alpha'],src=src,how=how,
            pcw=pc.size[0],pch=pc.size[1],ncc=round(ncc,3),aspect_ok=abs(asp_m-asp_p)<1e-3,
            mean_m=[round(x) for x in a.mean(0)],mean_p=[round(x) for x in b.mean(0)]))
json.dump(plan,open('/root/work/plan.json','w'),indent=1)
for p in plan: print(p['file'].split('/')[-1][:22],hex(p['hash']),p['w'],p['h'],p['alpha'],p['how'],p['src'][:40],p['pcw'],p['pch'],p['ncc'],p['aspect_ok'],p['mean_m'],p['mean_p'])
print(len(plan))
