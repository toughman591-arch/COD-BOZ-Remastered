import sys,glob,os,struct,numpy as np
sys.path.insert(0,'/root/tools')
import resgrp,texlib
def records16(d):
    g=resgrp.walk(d); parsed={t['off'] for t in texlib.records(d)}; out=[]
    for l in g['lists']:
        if l['cls']!='CIwTexture': continue
        for q,fl,s in l['items']:
            off=q+5
            if off in parsed: continue
            fmt=d[off+13]; w,h,pitch=struct.unpack_from('<HHH',d,off+17)
            out.append(dict(off=off,item=q,isize=s,hash=struct.unpack_from('<I',d,off)[0],fmt=fmt,w=w,h=h,pitch=pitch,pix=off+27))
    return out
def decode16(d,t,order='RGBA4444'):
    n=t['w']*t['h']; a=np.frombuffer(d,np.uint16,n,t['pix']).reshape(t['h'],t['w']).astype(np.uint32)
    if order=='RGBA4444': r,g,b,al=(a>>12)&15,(a>>8)&15,(a>>4)&15,a&15; return (np.stack([r,g,b,al],2)*17).astype(np.uint8)
    if order=='ABGR4444': al,b,g,r=(a>>12)&15,(a>>8)&15,(a>>4)&15,a&15; return (np.stack([r,g,b,al],2)*17).astype(np.uint8)
    if order=='RGB565': r,g,b=(a>>11)&31,(a>>5)&63,a&31; return np.stack([r*255//31,g*255//63,b*255//31,np.full_like(r,255)],2).astype(np.uint8)
