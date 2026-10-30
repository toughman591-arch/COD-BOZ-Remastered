import sys,struct,math,numpy as np
sys.path.insert(0,'/root/tools')
import texlib,atc,resgrp
from PIL import Image
def full_nm(w,h): return int(math.log2(max(w,h)))+1
def build_mips(img_rgba,w,h,nm,alpha):
    """img_rgba: PIL RGBA at >= w,h. returns list of encoded bytes per mip"""
    out=[]
    for k in range(nm):
        mw,mh=max(1,w>>k),max(1,h>>k)
        m=np.asarray(img_rgba.resize((mw,mh),Image.LANCZOS if k==0 else Image.BOX),np.uint8) if (mw,mh)!=img_rgba.size else np.asarray(img_rgba,np.uint8)
        out.append(atc.encode(m,alpha))
    return out
def find_item(g,pos):
    for L in g['lists']:
        for (q,fl,s) in L['items']:
            if q<=pos<q+s: return q
    raise ValueError('no item for %d'%pos)
def apply(d,edits):
    """edits: list of (pos, old_len, new_bytes, extra_sizefields) applied to buffer d.
       Each edit replaces d[pos:pos+old_len]. Size fields of enclosing item + ResGroupResources are fixed automatically.
       extra_sizefields: list of absolute offsets of u32 size fields (in original coords) to bump by delta."""
    g=resgrp.walk(d)
    bumps={}  # offset -> delta
    for pos,ol,nb,extra in edits:
        delta=len(nb)-ol
        if delta==0 and not extra: continue
        it=find_item(g,pos)
        bumps[it+1]=bumps.get(it+1,0)+delta
        bumps[g['res_off']+4]=bumps.get(g['res_off']+4,0)+delta
        for e in extra: bumps[e]=bumps.get(e,0)+delta
    b=bytearray(d)
    for off,dl in bumps.items():
        v=struct.unpack_from('<I',b,off)[0]; struct.pack_into('<I',b,off,v+dl)
    # splice from end to start
    for pos,ol,nb,extra in sorted(edits,key=lambda e:-e[0]):
        b[pos:pos+ol]=nb
    return bytes(b)
def texture_edit(d,t,src_img,new_w,new_h,gain=None):
    """Return an edit tuple replacing texture record t with src image at new dims."""
    alpha=t['alpha']
    old_nm=t['nm']; old_full=full_nm(t['w'],t['h'])
    if old_nm==1: nm=1
    elif old_nm==old_full: nm=full_nm(new_w,new_h)
    else:
        if (new_w,new_h)!=(t['w'],t['h']): raise ValueError('odd mip count')
        nm=old_nm
    img=src_img.convert('RGBA')
    if gain is not None:
        a=np.asarray(img,np.float32); a[...,:3]=np.clip(a[...,:3]*np.array(gain,np.float32),0,255)
        img=Image.fromarray(a.astype(np.uint8),'RGBA')
    if not alpha:
        a=np.asarray(img).copy(); a[...,3]=255; img=Image.fromarray(a,'RGBA')
    mips=build_mips(img,new_w,new_h,nm,alpha)
    sizes=[len(m) for m in mips]
    data=b''.join(mips)
    s=t['s']  # glf pos
    # header pieces
    off=t['off']
    hdr=bytearray(d[off:s+64])   # hash .. glf + 64-byte header
    rel=lambda x:x-off
    # w,h,pitch,size,size2 positions: hash(4)+13 bytes -> w at off+17
    wpos=off+17
    old_pitch=struct.unpack_from('<H',d,wpos+4)[0]
    pitch=old_pitch*new_w//t['w']
    size=72+len(data)
    struct.pack_into('<HHHI',hdr,rel(wpos),new_w,new_h,pitch,size)
    assert d[wpos+10:wpos+14]==b'\x22\x00\x02\x00'
    struct.pack_into('<I',hdr,rel(wpos+14),size)
    assert struct.unpack_from('<I',d,wpos+18)[0]==t['glf'] and wpos+18==s
    struct.pack_into('<III',hdr,rel(s+4),nm,new_w,new_h)
    for i,sz in enumerate(sizes): struct.pack_into('<I',hdr,rel(s+16+4*i),sz)
    new=bytes(hdr)+data
    old_len=(s+t['size']-8)-off
    return (off,old_len,new,[])
