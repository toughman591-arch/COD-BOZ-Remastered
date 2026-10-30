"""Entity spec (true payload) editing. payload = name(4) + ncomp(4) + components;
component = [CIsComponentSpec][0][cls][size] + LFER block (size bytes: 'LFER' cls size nprops + props)
prop = [cls][type][1][prop][1][vsize][value]"""
import struct,sys
sys.path.insert(0,'/root/tools')
from hashes import djb2
CS=djb2('ciscomponentspec')
H=lambda s:djb2(s.lower())
def comps(p):
    n=struct.unpack_from('<I',p,4)[0]; o=8; out=[]
    while o<len(p)-15 and struct.unpack_from('<I',p,o)[0]==CS:
        cls,sz=struct.unpack_from('<II',p,o+8); assert p[o+16:o+20]==b'LFER',(o,p[o+16:o+20])
        out.append(dict(cls=cls,hdr=o,lfer=o+16,size=sz,end=o+16+sz)); o+=16+sz
    return n,out,o
def props(p,c):
    o=c['lfer']+16; out=[]
    while o<c['end']-23:
        cls,typ,one,pr,one2,vs=struct.unpack_from('<6I',p,o)
        if one!=1 or one2!=1: break
        out.append(dict(type=typ,prop=pr,off=o,val=o+24,vsize=vs)); o+=24+vs
    return out
def find_prop(p,prop,comp_cls=None,nth=0):
    n,cs,_=comps(p); k=0
    for c in cs:
        if comp_cls is not None and c['cls']!=H(comp_cls): continue
        for q in props(p,c):
            if q['prop']==H(prop):
                if k==nth: return c,q
                k+=1
    return None,None
def set_value(p,prop,raw,comp_cls=None,nth=0):
    """replace a property's value bytes (any size); fixes component sizes"""
    p=bytearray(p); c,q=find_prop(p,prop,comp_cls,nth); assert q,prop
    d=len(raw)-q['vsize']
    p[q['val']:q['val']+q['vsize']]=raw; struct.pack_into('<I',p,q['off']+20,len(raw))
    if d:
        struct.pack_into('<I',p,c['hdr']+12,c['size']+d); struct.pack_into('<I',p,c['lfer']+8,c['size']+d)
    return bytes(p)
def add_prop(p,comp_cls,prop,type_name_hash,raw,nth=0):
    p=bytearray(p); n,cs,_=comps(p); c=[c for c in cs if c['cls']==H(comp_cls)][nth]
    rec=struct.pack('<6I',c['cls'],type_name_hash,1,H(prop),1,len(raw))+raw
    p[c['end']:c['end']]=rec
    struct.pack_into('<I',p,c['hdr']+12,c['size']+len(rec)); struct.pack_into('<I',p,c['lfer']+8,c['size']+len(rec))
    np_=struct.unpack_from('<I',p,c['lfer']+12)[0]; struct.pack_into('<I',p,c['lfer']+12,np_+1)
    return bytes(p)
def get(p,prop,fmt,comp_cls=None,nth=0):
    c,q=find_prop(p,prop,comp_cls,nth); return struct.unpack_from(fmt,p,q['val']) if q else None
def setf(p,prop,fmt,*vals,comp_cls=None,nth=0):
    return set_value(p,prop,struct.pack(fmt,*vals),comp_cls,nth)
def rename(p,newname):
    """new entity name: item hash + CIsNamed 'name' string (first CIsNamed)"""
    p=bytearray(p); struct.pack_into('<I',p,0,H(newname))
    c,q=find_prop(bytes(p),'name','CIsNamed',0)
    return set_value(bytes(p),'name',newname.encode()+b'\0','CIsNamed',0)
def name(p):
    c,q=find_prop(p,'name','CIsNamed',0)
    return p[q['val']:q['val']+q['vsize']].split(b'\0')[0].decode('latin1') if q else None
