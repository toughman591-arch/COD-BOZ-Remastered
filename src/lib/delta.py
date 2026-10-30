import numpy as np, struct, lzma
def common(a,b,i,j,limit=1<<22):
    n=min(len(a)-i,len(b)-j,limit); k=0; step=65536
    while k<n:
        m=min(step,n-k)
        x=np.frombuffer(a,np.uint8,m,i+k); y=np.frombuffer(b,np.uint8,m,j+k)
        ne=np.nonzero(x!=y)[0]
        if len(ne): return k+int(ne[0])
        k+=m
    return k
def make(old,new):
    ops=[];i=j=0;N=len(new)
    while j<N:
        k=common(old,new,i,j)
        while k==(1<<22): ops.append(('C',i,k)); i+=k;j+=k;k=common(old,new,i,j)
        if k>=24 or j+k==N:
            if k: ops.append(('C',i,k)); i+=k;j+=k
            continue
        # resync
        s=k+8 if k else 8; found=None
        while j+s+48<=N:
            key=new[j+s:j+s+48]
            pos=old.find(key,max(0,i-(1<<16)),min(len(old),i+(1<<23)))
            if pos>=0: found=(j+s,pos);break
            s=int(s*1.5)+8
        if not found:
            ops.append(('L',new[j:]));j=N;break
        p,pos=found
        # back-extend match
        b=0
        while p-b>j and pos-b>0 and new[p-b-1]==old[pos-b-1]: b+=1
        p-=b;pos-=b
        if p>j: ops.append(('L',new[j:p]))
        i=pos;j=p
    return ops
def encode(ops,old_md5,new_md5,new_len):
    out=bytearray(b'BOZDELTA1'+bytes.fromhex(old_md5)+bytes.fromhex(new_md5)+struct.pack('<QI',new_len,len(ops)))
    lit=bytearray()
    for op in ops:
        if op[0]=='C': out+=struct.pack('<BQQ',0,op[1],op[2])
        else: out+=struct.pack('<BQQ',1,len(lit),len(op[1])); lit+=op[1]
    return lzma.compress(bytes(out)+bytes(lit),preset=9|lzma.PRESET_EXTREME)
