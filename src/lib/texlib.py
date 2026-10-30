import sys,struct;sys.path.insert(0,'/root/tools')
import tex,atc
def records(d):
    out=[]
    for t in tex.scan(d):
        s=t['datastart']-4
        nm,w,h=struct.unpack_from('<III',d,s+4)
        sizes=list(struct.unpack_from('<%dI'%nm,d,s+16))
        t.update(s=s,nm=nm,w=w,h=h,sizes=sizes,alpha=(t['glf']==0x8c93),pix=s+64)
        out.append(t)
    return out
def mip0(d,t):
    return atc.decode(d[t['pix']:t['pix']+t['sizes'][0]],t['w'],t['h'],t['alpha'])
