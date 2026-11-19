import struct, numpy as np
def tiles(nb):
    out=[]; p=nb.find(b'VAND')
    while p>=0:
        f=struct.unpack_from('<5iI9i3f3f3ff',nb,p)
        (magic,ver,x,y,layer,uid,pc,vc,mlc,dmc,dvc,dtc,bvc,omc,omb,wh,wr,wc,b0,b1,b2,c0,c1,c2,q)=f
        t=dict(p=p,x=x,y=y,pc=pc,vc=vc,mlc=mlc,dmc=dmc,dvc=dvc,dtc=dtc,bvc=bvc,omc=omc,omb=omb,bmin=(b0,b1,b2),bmax=(c0,c1,c2),q=q,wh=wh,wr=wr,wc=wc)
        o=p+100; t['vo']=o; o+=12*vc; t['po']=o; o+=40*pc; t['lo']=o; o+=12*mlc; t['dmo']=o; o+=12*dmc; t['dvo']=o; o+=12*dvc; t['dto']=o; o+=4*dtc; t['bvo']=o; o+=16*bvc; t['oo']=o; o+=36*omc; t['end']=o
        t['verts']=np.frombuffer(nb,np.float32,3*vc,t['vo']).reshape(-1,3)
        out.append(t); p=nb.find(b'VAND',p+4)
    return out
def poly(nb,t,i):
    o=t['po']+40*i; fl,=struct.unpack_from('<I',nb,o); vs=struct.unpack_from('<6H',nb,o+4); ne=struct.unpack_from('<6H',nb,o+16)
    rest=struct.unpack_from('<HII',nb,o+28) ; return dict(o=o,first=fl,vs=vs,ne=ne,raw=nb[o+28:o+40])
def offmesh(nb,t):
    out=[]
    for i in range(t['omc']):
        o=t['oo']+36*i; pos=struct.unpack_from('<6f',nb,o); rad,=struct.unpack_from('<f',nb,o+24); pl,fl,side,uid=struct.unpack_from('<HBBI',nb,o+28)
        out.append(dict(a=pos[:3],b=pos[3:],rad=rad,poly=pl,flags=fl,side=side,uid=uid))
    return out
