import sys,struct; sys.path.insert(0,'/root/work/tools'); sys.path.insert(0,'/home/claude/cod-boz-remastered/src/lib'); import dz,tlres
from propdump import comps
D,F,C,_,_=dz.parse('/root/work/s2/dz3d.dz')
def get(di,nm):
    i=[k for k,f in enumerate(F) if f[0]==nm and f[1]==di][0]; c=C[i]; return bytes(D[c[0]:c[0]+c[1]])
def name_of(x):
    for c in comps(x):
        if c[0]=='CIsNamed' and c[2]: p=c[2][0]; return x[p[4]:p[4]+p[3]].split(b'\0')[0].decode('latin1')
def show(x):
    print('==',name_of(x),len(x),'hdr',x[:12].hex())
    for c in comps(x):
        vals=[]
        for p in c[2]:
            raw=x[p[4]:p[4]+p[3]]
            if p[3]%4==0 and p[3]<=64 and p[1] not in ('assets',):
                f=struct.unpack('<%df'%(p[3]//4),raw); u=struct.unpack('<%dI'%(p[3]//4),raw)
                v=tuple(round(a,2) if 1e-6<abs(a)<1e7 or a==0 else hex(b) for a,b in zip(f,u))
            else: v=raw[:48]
            vals.append((p[1],p[3],v))
        print('  ',c[0],vals)
