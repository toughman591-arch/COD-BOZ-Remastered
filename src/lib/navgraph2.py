import sys,struct,numpy as np,collections
sys.path.insert(0,'/root/tools')
import resgrp
def load(path):
    d=open(path,'rb').read();g=resgrp.walk(d)
    L=[l for l in g['lists'] if l['cls']=='CIsNavMesh'][0];q,fl,s=L['items'][0]
    b=d[q+5:q+s];p=b.find(b'VAND');tiles=[]
    while p>=0:
        f=struct.unpack_from('<15i10f',b,p);tx,ty=f[2],f[3];pc,vc=f[6],f[7]
        verts=np.frombuffer(b,np.float32,3*vc,p+100).reshape(-1,3)*100
        pp=p+100+12*vc;polys=[]
        for i in range(pc):
            o=pp+40*i
            vs=struct.unpack_from('<6H',b,o+4);ne=struct.unpack_from('<6H',b,o+16);at,n=struct.unpack_from('<II',b,o+32)
            polys.append(dict(v=[verts[k] for k in vs[:n]],ne=ne[:n]))
        tiles.append(dict(tx=tx,ty=ty,polys=polys,bmin=f[18:21],bmax=f[21:24]))
        p=b.find(b'VAND',p+4)
    return tiles
def graph(tiles):
    ids={};flat=[]
    for ti,t in enumerate(tiles):
        for pi,P in enumerate(t['polys']): ids[(ti,pi)]=len(flat);flat.append(np.array(P['v']))
    par=list(range(len(flat)))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]];x=par[x]
        return x
    def u(a,b): par[f(a)]=f(b)
    bykey={(t['tx'],t['ty']):ti for ti,t in enumerate(tiles)}
    ext=collections.defaultdict(list)
    for ti,t in enumerate(tiles):
        for pi,P in enumerate(t['polys']):
            n=len(P['v'])
            for k,nb in enumerate(P['ne']):
                if nb==0: continue
                if nb&0x8000:
                    side=nb&0xff; a=P['v'][k];b2=P['v'][(k+1)%n]
                    ext[(ti,side)].append((pi,a,b2))
                else: u(ids[(ti,pi)],ids[(ti,nb-1)])
    opp={0:4,4:0,2:6,6:2};off={0:(1,0),4:(-1,0),2:(0,1),6:(0,-1)}
    for (ti,side),lst in ext.items():
        t=tiles[ti];dx,dz=off.get(side,(0,0))
        tj=bykey.get((t['tx']+dx,t['ty']+dz))
        if tj is None: continue
        other=ext.get((tj,opp[side]),[])
        oax=2 if side in (0,4) else 0
        for pi,a,b2 in lst:
            lo,hi=sorted([a[oax],b2[oax]])
            for pj,c,e in other:
                lo2,hi2=sorted([c[oax],e[oax]])
                if min(hi,hi2)-max(lo,lo2)>1 and abs((a[1]+b2[1])/2-(c[1]+e[1])/2)<120:
                    u(ids[(ti,pi)],ids[(tj,pj)])
    return flat,[f(i) for i in range(len(flat))]
