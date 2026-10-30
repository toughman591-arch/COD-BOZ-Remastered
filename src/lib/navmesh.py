import struct,numpy as np
def tiles(b):
    out=[];p=b.find(b'VAND')
    while p>=0:
        h=struct.unpack_from('<5iI9i3f3f3f f',b,p) if False else None
        magic,ver=struct.unpack_from('<ii',b,p)
        if ver>=7:
            f=struct.unpack_from('<5iI9i3f3f3ff',b,p)
            (magic,ver,x,y,layer,uid,polyCount,vertCount,maxLink,dmc,dvc,dtc,bvc,omc,omb,wh,wr,wc,b0,b1,b2,c0,c1,c2,q)=f
            hs=4*25
        else:
            raise ValueError('ver %d'%ver)
        vp=p+hs
        verts=np.frombuffer(b,np.float32,3*vertCount,vp).reshape(-1,3)
        pp=vp+12*vertCount
        polys=[]
        for i in range(polyCount):
            o=pp+40*i
            vs=struct.unpack_from('<6H',b,o+4)
            at,vc=struct.unpack_from('<II',b,o+32)
            polys.append((vs[:vc],at))
        out.append(dict(ver=ver,bmin=(b0,b1,b2),bmax=(c0,c1,c2),verts=verts,polys=polys,wr=wr))
        p=b.find(b'VAND',p+4)
    return out
