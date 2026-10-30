import sys,struct,numpy as np
sys.path.insert(0,'/root/tools')
import resgrp,navmesh
def load(path):
    d=open(path,'rb').read();g=resgrp.walk(d)
    L=[l for l in g['lists'] if l['cls']=='CIsNavMesh'][0];q,fl,s=L['items'][0]
    T=navmesh.tiles(d[q+5:q+s])
    polys=[]
    for t in T:
        for vs,at in t['polys']:
            if len(vs)>=3: polys.append(np.array([t['verts'][v]*100 for v in vs]))
    return polys
def components(polys,tol=2.0):
    # connect polys sharing an edge (both endpoints within tol) or overlapping collinear edges (tile borders)
    import collections
    key=lambda p:(round(p[0]/tol),round(p[1]/tol),round(p[2]/tol))
    edges=collections.defaultdict(list)
    for i,P in enumerate(polys):
        n=len(P)
        for k in range(n):
            a,b=P[k],P[(k+1)%n]
            edges[frozenset([key(a),key(b)])].append(i)
    parent=list(range(len(polys)))
    def f(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for e,lst in edges.items():
        for j in lst[1:]: parent[f(j)]=f(lst[0])
    # tile-border edges: connect polys with collinear overlapping boundary edges
    bnd=[(i,P[k],P[(k+1)%len(P)]) for i,P in enumerate(polys) for k in range(len(P)) if len(edges[frozenset([key(P[k]),key(P[(k+1)%len(P)])])])==1]
    for ax in (0,2):
        groups=collections.defaultdict(list)
        for i,a,b in bnd:
            if abs(a[ax]-b[ax])<0.5: groups[round(a[ax])].append((i,a,b))
        for c,lst in groups.items():
            oax=2 if ax==0 else 0
            for m in range(len(lst)):
                i,a,b=lst[m];lo,hi=sorted([a[oax],b[oax]])
                for n2 in range(m+1,len(lst)):
                    j,c2,d2=lst[n2];lo2,hi2=sorted([c2[oax],d2[oax]])
                    if i!=j and min(hi,hi2)-max(lo,lo2)>5 and abs((a[1]+b[1])/2-(c2[1]+d2[1])/2)<60:
                        parent[f(j)]=f(i)
    return [f(i) for i in range(len(polys))]
def inside(P,x,z):
    n=len(P);c=False
    for k in range(n):
        x1,z1=P[k][0],P[k][2];x2,z2=P[(k+1)%n][0],P[(k+1)%n][2]
        if (z1>z)!=(z2>z) and x<(x2-x1)*(z-z1)/(z2-z1+1e-9)+x1: c=not c
    return c
def locate(polys,x,y,z,ytol=150):
    best=None
    for i,P in enumerate(polys):
        if inside(P,x,z):
            dy=abs(P[:,1].mean()-y)
            if dy<ytol and (best is None or dy<best[1]): best=(i,dy)
    return best
