import sys,math,numpy as np,pickle
sys.path.insert(0,'/root/tools')
import navgraph2,navgraph
T=navgraph2.load('/root/work/dz/levels/tutorial/tutorial_statics.group.bin')
flat,comp=navgraph2.graph(T)
sp=navgraph.locate(flat,196.9,235,3149.1);C=comp[sp[0]]
mine=[flat[i] for i in range(len(flat)) if comp[i]==C]
def inside_any(x,z): return any(navgraph.inside(P,x,z) for P in mine)
# boundary edges: edges of 'mine' polys not shared with another poly in mine (approx by coordinates)
import collections
key=lambda p:(round(p[0]),round(p[2]))
cnt=collections.Counter()
for P in mine:
    for k in range(len(P)):
        cnt[frozenset([key(P[k]),key(P[(k+1)%len(P)])])]+=1
bnd=[]
for P in mine:
    for k in range(len(P)):
        a,b=P[k],P[(k+1)%len(P)]
        if cnt[frozenset([key(a),key(b)])]==1:
            # check midpoint just outside isn't inside another poly (tile borders)
            mx,mz=(a[0]+b[0])/2,(a[2]+b[2])/2
            ex,ez=b[0]-a[0],b[2]-a[2];L=math.hypot(ex,ez)
            if L<1: continue
            nx,nz=-ez/L,ex/L
            if inside_any(mx+nx*5,mz+nz*5) and inside_any(mx-nx*5,mz-nz*5): continue
            bnd.append((a[0],a[2],b[0],b[2]))
def dist_seg(px,pz,s):
    x1,z1,x2,z2=s;dx,dz=x2-x1,z2-z1;t=max(0,min(1,((px-x1)*dx+(pz-z1)*dz)/(dx*dx+dz*dz)));return math.hypot(px-(x1+t*dx),pz-(z1+t*dz))
def facing(theta): return (math.sin(math.radians(theta)),-math.cos(math.radians(theta)))
def check(x,z,theta,halfw,depth=60):
    fx,fz=facing(theta); rx,rz=-fz,fx
    back=(x-fx*15,z-fz*15)
    db=min(dist_seg(back[0],back[1],s) for s in bnd)
    pts=[(x+fx*(depth+120)+rx*w, z+fz*(depth+120)+rz*w) for w in (-halfw,0,halfw)]
    front_ok=all(inside_any(px,pz) for px,pz in pts)
    corners_ok=all(inside_any(x+fx*(depth-15)+rx*w*0.9, z+fz*(depth-15)+rz*w*0.9) for w in (-halfw,halfw))
    return db,front_ok,corners_ok
