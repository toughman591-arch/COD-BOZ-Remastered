"""Correct ResGroup resource-list format:
   list = [cls u32][count u32][2 flag bytes] then items [u32 size incl. itself][payload]"""
import struct,sys
sys.path.insert(0,'/root/tools')
from hashes import djb2
RES=struct.pack('<I',djb2('resgroupresources'))
def parse(d):
    p=d.find(RES); sz=struct.unpack_from('<I',d,p+4)[0]; q=p+12; n=struct.unpack_from('<I',d,p+8)[0]; out=[]
    for i in range(n):
        ch,cnt=struct.unpack_from('<II',d,q); h=d[q+8:q+10]; q+=10; items=[]
        for j in range(cnt):
            s=struct.unpack_from('<I',d,q)[0]; items.append(d[q+4:q+s]); q+=s
        out.append([ch,h,items])
    assert q==p+4+sz
    return dict(pre=d[:p],post=d[p+4+sz:],lists=out)
def build(g):
    res=struct.pack('<I',len(g['lists']))
    for ch,h,items in g['lists']:
        res+=struct.pack('<II',ch,len(items))+h+b''.join(struct.pack('<I',len(x)+4)+x for x in items)
    return g['pre']+RES+struct.pack('<I',4+len(res))+res+g['post']
def find(g,cls):
    h=djb2(cls.lower()); return [L for L in g['lists'] if L[0]==h][0]
def name(item): return struct.unpack_from('<I',item,0)[0]
