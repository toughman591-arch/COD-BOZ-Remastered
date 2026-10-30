import sys,struct; sys.path.insert(0,'/root/work/v37')
from swfx import *; from actions import *
def patch_displayMapVote(b):
    O=ops(b)
    assert O[0][1]==0x88
    cp=O[0][2]; n=struct.unpack_from('<H',cp)[0]; pool=cp[2:].split(b'\0')[:n]
    assert b'nacht' not in pool and n==47
    idx_cotd=pool.index(b'callofthedead'); NI=n
    newcp=struct.pack('<H',n+1)+b''.join(p+b'\0' for p in pool)+b'nacht\0'
    grow_cp=len(newcp)-len(cp)
    # locate function
    fi=[i for i,(p,c,d) in enumerate(O) if c==0x8e and b'showVoteButtons' in d][0]
    fp,_,fd=O[fi]; csize=struct.unpack_from('<H',fd,len(fd)-2)[0]
    body_start=fp+3+len(fd); body_end=body_start+csize
    # block for callofthedead
    blk_i=[i for i,(p,c,d) in enumerate(O) if c==0x96 and d==bytes([8,idx_cotd]) and body_start<=p<body_end]
    assert len(blk_i)==1; k=blk_i[0]
    s=O[k-6][0]; e=O[k+6][0]+1   # Push r1,multi_lobby ... SetMember
    assert b[e-1]==0x4f and O[k-6][1]==0x96 and O[k+6][1]==0x4f
    blk=b[s:e].replace(bytes([0x96,2,0,8,idx_cotd]),bytes([0x96,2,0,8,NI]))
    assert len(blk)==e-s and blk!=b[s:e]
    ins=len(blk); nb=bytearray(b[:e]+blk+b[e:])
    # fix branches inside the function that cross position e
    for p,c,d in O:
        if c in (0x99,0x9d) and body_start<=p<body_end:
            off=struct.unpack_from('<h',d)[0]; src=p+5; tgt=src+off
            q=p+(ins if p>=e else 0)
            if src<=e<=tgt-1 or (src>e and tgt<=e):
                if off>0: off+=ins
                else: off-=ins
                struct.pack_into('<h',nb,q+3,off)
    struct.pack_into('<H',nb,fp+3+len(fd)-2,csize+ins)
    # replace constant pool (at start)
    nb=bytes(nb); assert nb[0]==0x88
    oldlen=struct.unpack_from('<H',nb,1)[0]
    nb=bytes([0x88])+struct.pack('<H',len(newcp))+newcp+nb[3+oldlen:]
    return nb
if __name__=='__main__':
    h,T=swf.parse(open('/root/work/nacht/fe_n.swf','rb').read()); b=body(T[2015])
    nb=patch_displayMapVote(b)
    print(len(b),len(nb))
