import sys,struct,pickle,os,shutil
sys.path.insert(0,'/root/tools')
from hashes import djb2
D=pickle.load(open('/root/tools/hashdict.pkl','rb'))
SRC,OUT,CAP=sys.argv[1],sys.argv[2],int(sys.argv[3])
f='levels/kino/kino_statics.group.bin'
src=os.path.join(OUT,f) if os.path.exists(os.path.join(OUT,f)) else os.path.join(SRC,f)
d=bytearray(open(src,'rb').read())
HM=struct.pack('<I',djb2('m_maxactive'));HC=struct.pack('<I',djb2('m_zombiecount'))
ok={djb2('cwave'),djb2('cwaverepeatable')}
def ints(h):
    out=[];p=d.find(h)
    while p>=0:
        if d[p+4:p+12]==b'\x01\x00\x00\x00\x04\x00\x00\x00': out.append(p)
        p=d.find(h,p+1)
    return out
counts=ints(HC);changes=[]
for p in ints(HM):
    cls=struct.unpack_from('<I',d,p-12)[0]
    if cls not in ok: continue
    prev=[q for q in counts if q<p][-1]
    cnt=struct.unpack_from('<I',d,prev+12)[0]; old=struct.unpack_from('<I',d,p+12)[0]
    new=old if old>=cnt else min(cnt,CAP)
    if new!=old:
        struct.pack_into('<I',d,p+12,new); changes.append((p+12,cnt,old,new))
os.makedirs(os.path.dirname(os.path.join(OUT,f)),exist_ok=True)
open(os.path.join(OUT,f),'wb').write(d)
print(len(changes),'waves changed; e.g.',changes[:6])
