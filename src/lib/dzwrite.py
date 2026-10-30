import struct,sys
sys.path.insert(0,'/root/tools')
import dz
def build(base,out,replace,add_after):
    """replace: {(dir,name): bytes}; add_after: {(dir,name): [(newdir,newname,bytes),...]}"""
    d=open(base,'rb').read()
    p=9
    def s():
        nonlocal p
        e=d.index(b'\0',p);r=d[p:e];p=e+1;return r.decode('latin1')
    nf,nd=struct.unpack_from('<HH',d,4); flag=d[8]
    names=[s() for _ in range(nf)];dirs=[s() for _ in range(nd-1)]
    _,files,chunks,na,hdr_end=dz.parse(base)
    allds=['']+dirs
    entries=[]   # (dirindex, name, data, flags, arch)
    used=set()
    for i,(n,di,ch) in enumerate(files):
        assert ch==[i]
        o,z,sz,fl,ai=chunks[i]
        dis=struct.unpack_from('<H',d,0)  # placeholder
        data=replace.get((di,n),d[o:o+z])
        if (di,n) in replace: used.add((di,n))
        entries.append([di,n,data,fl,ai,i])
        for nd_,nn,nb in add_after.get((di,n),[]):
            entries.append([nd_,nn,nb,fl,ai,None]); used.add(('add',nd_,nn))
    assert len(used)==len(replace)+sum(len(v) for v in add_after.values()),(used,)
    # dir table: keep original list, append any new dirs
    dlist=list(dirs)
    def dindex(dn):
        if dn=='': return 0
        # reuse an existing entry with same name
        for k,x in enumerate(dlist):
            if x==dn: return k+1
        dlist.append(dn); return len(dlist)
    # original files keep their original dir indices
    # re-read original per-file dir indices
    q=9
    for _ in range(nf+nd-1): q=d.index(b'\0',q)+1
    origdi=[]
    for i in range(nf):
        di,=struct.unpack_from('<H',d,q);q+=2
        while struct.unpack_from('<H',d,q)[0]!=0xffff: q+=2
        q+=2; origdi.append(di)
    recs=[]
    for e in entries:
        di=origdi[e[5]] if e[5] is not None else dindex(e[0])
        recs.append((di,)+tuple(e[:5]))
    hdr=bytearray(b'DTRZ'+struct.pack('<HH',len(recs),len(dlist)+1)+bytes([flag]))
    for r in recs: hdr+=r[2].encode('latin1')+b'\0'
    for x in dlist: hdr+=x.encode('latin1')+b'\0'
    for i,r in enumerate(recs): hdr+=struct.pack('<HHH',r[0],i,0xffff)
    hdr+=struct.pack('<HH',na,len(recs))
    off=len(hdr)+16*len(recs)
    tbl=bytearray()
    for r in recs:
        tbl+=struct.pack('<IIIHH',off,len(r[3]),len(r[3]),r[4],r[5]); off+=len(r[3])
    with open(out,'wb') as f:
        f.write(hdr); f.write(tbl)
        for r in recs: f.write(r[3])
    return off
