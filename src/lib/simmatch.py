import sys,glob,os,pickle,numpy as np
sys.path.insert(0,'/root/tools')
import texlib
from PIL import Image
X='/root/work/ximg/ximages'
def feat(img):
    im=Image.fromarray(img) if isinstance(img,np.ndarray) else img
    im=im.convert('RGB')
    g=np.asarray(im.resize((24,24),Image.BILINEAR),np.float32)
    v=g.reshape(-1)-g.mean(); v/= (np.linalg.norm(v)+1e-6)
    return v
src={}
for fn in os.listdir(X):
    n=fn[:-4]
    if n.startswith('~$') or n.startswith('~~'): continue  # spec/gloss maps
    im=Image.open(os.path.join(X,fn)).convert('RGBA')
    if im.size[0]<16: continue
    src[fn]=feat(im)
names=list(src);M=np.stack([src[n] for n in names])
targets=[]
for f in sorted(glob.glob('/root/work/dz/levels/kino/*.group.bin')):
    d=open(f,'rb').read()
    for t in texlib.records(d):
        img=texlib.mip0(d,t)
        targets.append((os.path.basename(f),t['hash'],t['w'],t['h'],t['alpha'],feat(img)))
res=[]
for fb,h,w,hh,a,v in targets:
    s=M@v; i=int(s.argmax())
    res.append((fb,h,w,hh,a,names[i],float(s[i])))
pickle.dump(res,open('/root/work/simres.pkl','wb'))
uniq={}
for r in res: uniq.setdefault(r[1],r)
print('kino tex records',len(res),'unique',len(uniq))
for r in sorted(uniq.values(),key=lambda r:-r[6]): print('%.3f'%r[6],r[0],hex(r[1]),r[2],r[3],r[4],r[5])
