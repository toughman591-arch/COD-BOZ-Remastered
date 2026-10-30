import sys,collections,numpy as np
sys.path.insert(0,'/root/tools')
import navgraph2,navgraph
T=navgraph2.load('/root/work/dz/levels/kino/kino_statics.group.bin')
flat,_=navgraph2.graph(T)
# rebuild graph but drop polys near closed doors/windows
doors={'Lobby_To_Atrium':(-1429,195,1568),'Lobby_To_Balcony':(1424,779,1568),'PowerOn_Door1':(-1,195,1259),
       'LobbyLeft_Barricade':(-976,210,3446),'LobbyTop_Barricade':(-1423,794,1563),'LobbyStart_Barricade':(400,220,3680),'LobbyRight_Barricade':(515,213,1727)}
def near(P,c,r=170):
    m=P.mean(0); return abs(m[0]-c[0])<r and abs(m[2]-c[2])<r and abs(m[1]-c[1])<200
blocked=set(i for i,P in enumerate(flat) for c in doors.values() if near(P,c))
# union-find on shared edges among non-blocked polys (geometric)
import math
key=lambda p:(round(p[0]),round(p[1]/5),round(p[2]))
par=list(range(len(flat)))
def f(x):
    while par[x]!=x: par[x]=par[par[x]];x=par[x]
    return x
# use original graph connectivity from navgraph2 internals: recompute with blocked removal
tiles=T;ids={};k=0
for ti,t in enumerate(tiles):
    for pi,P in enumerate(t['polys']): ids[(ti,pi)]=k;k+=1
bykey={(t['tx'],t['ty']):ti for ti,t in enumerate(tiles)}
ext=collections.defaultdict(list)
for ti,t in enumerate(tiles):
    for pi,P in enumerate(t['polys']):
        a=ids[(ti,pi)]
        if a in blocked: continue
        n=len(P['v'])
        for kk,nb in enumerate(P['ne']):
            if nb==0: continue
            if nb&0x8000: ext[(ti,nb&0xff)].append((pi,P['v'][kk],P['v'][(kk+1)%n]))
            else:
                b=ids[(ti,nb-1)]
                if b not in blocked: par[f(a)]=f(b)
opp={0:4,4:0,2:6,6:2};off={0:(1,0),4:(-1,0),2:(0,1),6:(0,-1)}
for (ti,side),lst in ext.items():
    t=tiles[ti];dx,dz=off.get(side,(0,0));tj=bykey.get((t['tx']+dx,t['ty']+dz))
    if tj is None: continue
    oax=2 if side in (0,4) else 0
    for pi,a,b2 in lst:
        lo,hi=sorted([a[oax],b2[oax]])
        for pj,c,e in ext.get((tj,opp[side]),[]):
            lo2,hi2=sorted([c[oax],e[oax]])
            if min(hi,hi2)-max(lo,lo2)>1 and abs((a[1]+b2[1])/2-(c[1]+e[1])/2)<120:
                x1,x2=ids[(ti,pi)],ids[(tj,pj)]
                if x1 not in blocked and x2 not in blocked: par[f(x1)]=f(x2)
comp=[f(i) for i in range(len(flat))]
sp=navgraph.locate(flat,-167,203.5,3133.3);C=comp[sp[0]]
region=[i for i in range(len(flat)) if comp[i]==C]
