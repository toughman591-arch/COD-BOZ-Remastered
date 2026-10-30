import re,struct,os,glob,collections
PAT=re.compile(rb'(.{4})(.)\x43(.)(?:.)\x00\x22\x00(.)\x00(.)(.)\x00(.)(.{2})(.{2})(.{2})(.{4})\x22\x00\x02\x00(.{4})(.{4})',re.S)
def scan(d):
    out=[]
    for m in PAT.finditer(d):
        h=struct.unpack('<I',m.group(1))[0]
        w,hh,pitch=[struct.unpack('<H',m.group(i))[0] for i in (8,9,10)]
        size=struct.unpack('<I',m.group(11))[0]; size2=struct.unpack('<I',m.group(12))[0]
        glf=struct.unpack('<I',m.group(13))[0]
        if size!=size2: continue
        hdr=m.end()
        nm=struct.unpack_from('<I',d,hdr)[0]
        out.append(dict(off=m.start(),hash=h,flag=(m.group(2)[0],m.group(3)[0]),b=(m.group(4)[0],m.group(5)[0],m.group(6)[0],m.group(7)[0]),w=w,h=hh,pitch=pitch,size=size,glf=glf,datastart=m.end(),nm=nm))
    return out
if __name__=='__main__':
    root='/root/work/dz'
    tot=collections.Counter();n=0
    for f in sorted(glob.glob(root+'/**/*.group.bin',recursive=True)):
        d=open(f,'rb').read()
        cls=d.count(bytes.fromhex('39f52135'))
        t=scan(d);n+=len(t)
        for x in t: tot[(hex(x['glf']),x['b'])]+=1
        if 'kino' in f or 'ingame' in f or 'shared' in f or 'loading' in f: print(os.path.relpath(f,root),len(t))
    print(n,tot)
