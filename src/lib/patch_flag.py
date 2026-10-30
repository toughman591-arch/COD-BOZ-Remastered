import sys,os,numpy as np
sys.path.insert(0,'/root/tools')
import tex16,texlib,rewrite,resgrp
from PIL import Image
SRC,OUT=sys.argv[1],sys.argv[2]
H=0x9de661b6
pc=Image.open('/root/work/ximg/ximages/~-gdecal_flag_nazi_theater_c.png').convert('RGBA')
B=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],np.float32)/16-0.5
def enc4444(img,w,h,mob):
    a=np.asarray(img.resize((w,h),Image.LANCZOS),np.float32)
    m=(mob[...,3]>128)&(a[...,3]>128)
    gain=np.clip(mob[m][:,:3].mean(0)/np.maximum(a[m][:,:3].mean(0),1),0.75,1.33)
    a[...,:3]*=gain
    th=np.tile(B,(h//4+1,w//4+1))[:h,:w,None]
    q=np.clip(np.floor(a/17+0.5+th*0.9),0,15).astype(np.uint16)
    q[...,3]=np.clip(np.floor(a[...,3]/17+0.5),0,15)
    v=(q[...,0]<<12)|(q[...,1]<<8)|(q[...,2]<<4)|q[...,3]
    return v.astype('<u2').tobytes(),gain
# Kino: 16-bit RGBA4444 in alley_shared
f='levels/kino/alley_shared.group.bin'
src=os.path.join(OUT,f) if os.path.exists(os.path.join(OUT,f)) else os.path.join(SRC,f)
d=bytearray(open(src,'rb').read())
t=[t for t in tex16.records16(bytes(d)) if t['hash']==H][0]
mob=tex16.decode16(bytes(d),t).astype(np.float32)
data,gain=enc4444(pc,t['w'],t['h'],mob)
d[t['pix']:t['pix']+len(data)]=data
assert resgrp.walk(bytes(d))['ok']
open(os.path.join(OUT,f),'wb').write(d)
Image.fromarray(tex16.decode16(bytes(d),t)).resize((512,256),Image.NEAREST).save('/root/work/flag_new.png')
print('kino flag replaced',t['w'],t['h'],'gain',gain.round(2))
# Tutorial (set in the theater): ATC alpha 256x128, same size re-encode
f='levels/tutorial/tutorial_statics.group.bin'
src=os.path.join(OUT,f) if os.path.exists(os.path.join(OUT,f)) else os.path.join(SRC,f)
d=open(src,'rb').read()
t=[t for t in texlib.records(d) if t['hash']==H][0]
e=rewrite.texture_edit(d,t,pc,t['w'],t['h'])
nd=rewrite.apply(d,[e]); assert len(nd)==len(d) and resgrp.walk(nd)['ok']
os.makedirs(os.path.dirname(os.path.join(OUT,f)),exist_ok=True)
open(os.path.join(OUT,f),'wb').write(nd)
print('tutorial flag replaced',t['w'],t['h'])
