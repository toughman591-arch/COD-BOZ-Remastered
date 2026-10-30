import struct,sys,os,collections
def parse(path):
    d=open(path,'rb').read()
    assert d[:4]==b'DTRZ'
    p=4;nf,nd=struct.unpack_from('<HH',d,p);p+=5
    def s():
        nonlocal p
        e=d.index(b'\0',p);r=d[p:e];p=e+1;return r.decode('latin1')
    names=[s() for _ in range(nf)];dirs=['']+[s() for _ in range(nd-1)]
    files=[]
    for i in range(nf):
        di,=struct.unpack_from('<H',d,p);p+=2;ch=[]
        while True:
            c,=struct.unpack_from('<H',d,p);p+=2
            if c==0xffff:break
            ch.append(c)
        files.append((names[i],dirs[di],ch))
    na,nc=struct.unpack_from('<HH',d,p);p+=4
    chunks=[struct.unpack_from('<IIIHH',d,p+16*i) for i in range(nc)];p+=16*nc
    return d,files,chunks,na,p
if __name__=='__main__':
    d,files,chunks,na,p=parse(sys.argv[1])
    print('files',len(files),'chunks',len(chunks),'archives',na,'hdr_end',p,'size',len(d))
    print(collections.Counter(c[3] for c in chunks))
    print('tail after chunks:',d[p:p+64])
    for f in files:
        n,di,ch=f
        tot=sum(chunks[c][2] for c in ch)
        print(f"{di}\\{n}  chunks={ch[:4]}{'...' if len(ch)>4 else ''} size={tot} flags={set(chunks[c][3] for c in ch)}")

def extract(path,out):
    d,files,chunks,na,p=parse(path)
    for n,di,ch in files:
        fp=os.path.join(out,di.replace('\\','/'),n)
        os.makedirs(os.path.dirname(fp),exist_ok=True)
        with open(fp,'wb') as f:
            for c in ch:
                o,z,s,fl,ai=chunks[c]; assert fl==256 and z==s
                f.write(d[o:o+z])

def rebuild(path,moddir,out):
    d,files,chunks,na,hdr_end=parse(path)
    # verify contiguous chunk layout
    o=hdr_end
    for c in chunks:
        assert c[0]==o,(c,o); o+=c[1]
    assert o==len(d)
    tbl_off=hdr_end-16*len(chunks)
    head=bytearray(d[:hdr_end])
    datas=[]
    for i,(n,di,ch) in enumerate(files):
        assert ch==[i]
        rel=os.path.join(di.replace('\\','/'),n)
        mp=os.path.join(moddir,rel)
        c=chunks[i]
        datas.append(open(mp,'rb').read() if os.path.exists(mp) else d[c[0]:c[0]+c[1]])
    off=hdr_end
    for i,b in enumerate(datas):
        o0,z,s,fl,ai=chunks[i]
        struct.pack_into('<IIIHH',head,tbl_off+16*i,off,len(b),len(b),fl,ai)
        off+=len(b)
    with open(out,'wb') as f:
        f.write(head)
        for b in datas: f.write(b)
    return off
