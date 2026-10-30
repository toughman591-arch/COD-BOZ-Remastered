import sys,struct,os
sys.path.insert(0,'/root/tools')
import rewrite,resgrp
from hashes import djb2
SRC,OUT,FOV=sys.argv[1],sys.argv[2],float(sys.argv[3])
f='ingame/ingame.group.bin'
src=os.path.join(OUT,f) if os.path.exists(os.path.join(OUT,f)) else os.path.join(SRC,f)
d=open(src,'rb').read()
CAM=struct.pack('<I',djb2('ciscamera')); NAMEH=djb2('maincamera')
ES=struct.pack('<I',djb2('cisentityspec'))
PROP=lambda v: CAM+bytes.fromhex('9be1710f 01000000 bc47e90f 01000000 04000000'.replace(' ',''))+struct.pack('<f',v)
edits=[];p=d.find(CAM)
while p>=0:
    if d[p+8:p+12]==b'LFER':
        e=d.rfind(ES,0,p)
        if struct.unpack_from('<I',d,e+4)[0]==NAMEH:
            assert struct.unpack_from('<III',d,p+4)==(16,0x5245464c,struct.unpack('<I',CAM)[0]) or True
            assert struct.unpack_from('<I',d,p+4)[0]==16 and struct.unpack_from('<I',d,p+16)[0]==16 and struct.unpack_from('<I',d,p+20)[0]==0
            nb=bytearray(d[p+4:p+24]); struct.pack_into('<I',nb,0,16+28); struct.pack_into('<I',nb,12,16+28); struct.pack_into('<I',nb,16,1)
            edits.append((p+4,20,bytes(nb)+PROP(FOV),[]))
    p=d.find(CAM,p+1)
print('MainCamera components:',len(edits))
nd=rewrite.apply(d,edits)
assert resgrp.walk(nd)['ok']
os.makedirs(os.path.dirname(os.path.join(OUT,f)),exist_ok=True)
open(os.path.join(OUT,f),'wb').write(nd)
print('delta',len(nd)-len(d))
