import struct,numpy as np,sys
sys.path.insert(0,'/root/tools')
from hashes import djb2
VB=struct.pack('<I',djb2('ciwmodelblockverts'))*2
TB=struct.pack('<I',djb2('ciwmodelblockgltrilist'))*2
def positions(b):
    i=b.find(VB); sz,cnt,z0,n=struct.unpack_from('<HHHH',b,i+8)
    bias=struct.unpack_from('<h',b,i+16)[0]
    a=np.frombuffer(b,dtype='<i2',offset=i+18,count=3*n).reshape(3,n).T.astype(float)+bias
    extra=cnt-n
    if extra>0:
        m=np.frombuffer(b,dtype='<u2',offset=i+18+6*n,count=extra).astype(int)
        a=np.vstack([a,a[m]])
    return a,cnt
def trilists(b,cnt):
    out=[]; j=b.find(TB)
    while j>=0:
        sz,c,z,mat=struct.unpack_from('<HHHH',b,j+8)
        idx=np.frombuffer(b,dtype='<u2',offset=j+18,count=c)
        if c%3==0 and (c==0 or idx.max()<cnt): out.append((mat,idx.reshape(-1,3)))
        j=b.find(TB,j+8)
    return out
def decode(b):
    a,cnt=positions(b)
    tl=trilists(b,cnt)
    T=np.vstack([t for _,t in tl]) if tl else np.zeros((0,3),int)
    return a,T
