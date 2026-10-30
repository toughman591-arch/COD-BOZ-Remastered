import sys,struct,pickle
sys.path.insert(0,'/root/tools')
import resgrp,ents
D=pickle.load(open('/root/tools/hashdict.pkl','rb'))
TYPES={k for k,v in D.items() if v in ('unsigned int','float','bool','int','CIwFVec3','CIwFMat','CIwFQuat','std::string','CIwFVec2','unsigned char','unsigned short','char','short','CIwColour','CIwSVec3','CIwVec3','CIwFVec4')}
def dump(body,indent='  '):
    out=[];p=0;n=len(body)
    while p<n-4:
        if body[p:p+4]==b'LFER' and p+16<=n:
            c=struct.unpack_from('<I',body,p+4)[0];sz=struct.unpack_from('<I',body,p+8)[0];cnt=struct.unpack_from('<I',body,p+12)[0]
            out.append(f'{indent}[{D.get(c,hex(c))}] size={sz} nprops={cnt}');p+=16;continue
        if p+24<=n and body[p+8:p+12]==b'\x01\x00\x00\x00' and body[p+16:p+20]==b'\x01\x00\x00\x00':
            ty=struct.unpack_from('<I',body,p+4)[0];pr=struct.unpack_from('<I',body,p+12)[0];sz=struct.unpack_from('<I',body,p+20)[0]
            if pr in D and sz<4096 and p+24+sz<=n:
                raw=body[p+24:p+24+sz];tn=D.get(ty,hex(ty))
                if tn=='float' and sz==4: v='%.3f'%struct.unpack('<f',raw)[0]
                elif tn=='CIwFVec3' and sz==12: v=tuple(round(x,3) for x in struct.unpack('<3f',raw))
                elif sz==4: x=struct.unpack('<I',raw)[0]; v=f'{x} ({D[x]})' if x in D else (hex(x) if x>100000 else x)
                elif tn=='bool': v=raw[0]
                elif tn=='std::string': v=raw[4:].split(b'\0')[0].decode('latin1')
                else: v=raw.hex()[:64]
                out.append(f'{indent}  {D[pr]}:{tn} = {v}');p+=24+sz;continue
        p+=1
    return out
if __name__=='__main__':
    f,name=sys.argv[1],sys.argv[2]
    d=open(f,'rb').read()
    for e in ents.entity_items(d):
        if e['name']==name or (e['hname']==name):
            print('ENTITY',name,'item',e['q'],'size',e['size'],'hash',hex(e['hash']))
            print('\n'.join(dump(d[e['q']+5:e['q']+e['size']])))
