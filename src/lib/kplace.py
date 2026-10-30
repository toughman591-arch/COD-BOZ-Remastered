import sys,math,collections
sys.path.insert(0,'/root/tools')
import kinoregion as K,navgraph
mine=[K.flat[i] for i in K.region if K.flat[i][:,1].mean()<300]   # main floor level only
def inside_any(x,z): return any(navgraph.inside(P,x,z) for P in mine)
key=lambda p:(round(p[0]),round(p[2]))
cnt=collections.Counter()
for P in mine:
    for k in range(len(P)): cnt[frozenset([key(P[k]),key(P[(k+1)%len(P)])])]+=1
bnd=[]
for P in mine:
    for k in range(len(P)):
        a,b=P[k],P[(k+1)%len(P)]
        if cnt[frozenset([key(a),key(b)])]==1:
            mx,mz=(a[0]+b[0])/2,(a[2]+b[2])/2;ex,ez=b[0]-a[0],b[2]-a[2];L=math.hypot(ex,ez)
            if L<1: continue
            nx,nz=-ez/L,ex/L
            if inside_any(mx+nx*5,mz+nz*5) and inside_any(mx-nx*5,mz-nz*5): continue
            bnd.append((a[0],a[2],b[0],b[2]))
def dseg(px,pz,s):
    x1,z1,x2,z2=s;dx,dz=x2-x1,z2-z1;t=max(0,min(1,((px-x1)*dx+(pz-z1)*dz)/(dx*dx+dz*dz)));return math.hypot(px-(x1+t*dx),pz-(z1+t*dz))
def dc(x,z): return min(dseg(x,z,s) for s in bnd)
def facing(t): return (math.sin(math.radians(t)),-math.cos(math.radians(t)))
def place(x,z,t,target=13.9):
    fx,fz=facing(t);best=None
    for s in range(-250,251):
        cx,cz=x+fx*s,z+fz*s
        if inside_any(cx,cz): continue
        d=dc(cx,cz)
        if inside_any(cx+fx*(d+10),cz+fz*(d+10)):
            e=abs(d-target)
            if best is None or e<best[0]: best=(e,cx,cz,d)
    return best
def clear(x,z,t,halfw,depth=60):
    fx,fz=facing(t);rx,rz=-fz,fx
    return all(inside_any(x+fx*(depth+100)+rx*w,z+fz*(depth+100)+rz*w) for w in (-halfw,0,halfw)) and all(inside_any(x+fx*(depth-15)+rx*w*0.9,z+fz*(depth-15)+rz*w*0.9) for w in (-halfw,halfw))
