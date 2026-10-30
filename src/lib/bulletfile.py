import struct
def parse(blob):
    assert blob[:7]==b'BULLETf' or blob[:7]==b'BULLETd'
    ptr=4 if blob[7:8]==b'_' else 8
    p=12; chunks=[]
    while p<len(blob):
        code=blob[p:p+4]
        ln,=struct.unpack_from('<i',blob,p+4)
        old,=struct.unpack_from('<I' if ptr==4 else '<Q',blob,p+8)
        sdna,nr=struct.unpack_from('<ii',blob,p+8+ptr)
        hdr=8+ptr+8
        chunks.append(dict(code=code,len=ln,old=old,sdna=sdna,nr=nr,off=p,data=blob[p+hdr:p+hdr+ln]))
        p+=hdr+ln
        if code==b'ENDB': break
    return ptr,chunks,p
def parse_dna(data):
    p=0; assert data[:4]==b'SDNA'; p=4
    def take_names(tag):
        nonlocal p
        assert data[p:p+4]==tag,(data[p:p+4],tag); p+=4
        n,=struct.unpack_from('<i',data,p); p+=4; out=[]
        for _ in range(n):
            e=data.index(b'\0',p); out.append(data[p:e].decode()); p=e+1
        p=(p+3)&~3; return out
    names=take_names(b'NAME'); types=take_names(b'TYPE')
    assert data[p:p+4]==b'TLEN'; p+=4
    tlen=list(struct.unpack_from('<%dh'%len(types),data,p)); p+=2*len(types); p=(p+3)&~3
    assert data[p:p+4]==b'STRC'; p+=4
    n,=struct.unpack_from('<i',data,p); p+=4; structs=[]
    for _ in range(n):
        t,nf=struct.unpack_from('<hh',data,p); p+=4
        fields=[struct.unpack_from('<hh',data,p+4*k) for k in range(nf)]; p+=4*nf
        structs.append((t,fields))
    return names,types,tlen,structs
