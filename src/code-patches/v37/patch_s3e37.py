import struct,lzma
raw=bytearray(open('/root/work/nacht/boz.s3e.raw','rb').read())   # v2.1 code
B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
def t32_branch(src,dst,link):
    off=dst-(src+4); assert -(1<<24)<=off<(1<<24) and off%2==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    imm10=(off>>12)&0x3ff; imm11=(off>>1)&0x7ff
    return hw(0xf000|(S<<10)|imm10,(0xd000 if link else 0x9000)|(J1<<13)|(J2<<11)|imm11)
def t32_blx(src,dst):
    off=dst-((src+4)&~3); assert off%4==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    imm10=(off>>12)&0x3ff; imm11=(off>>1)&0x7fe
    return hw(0xf000|(S<<10)|imm10,0xc000|(J1<<13)|(J2<<11)|imm11)
HASH=0x284eac; S1=0x1c3fd0
assert get(S1,6)==b'nacht\0'
# the existing blx at 0x1c3fea encodes the same target; sanity-check our encoder against it
assert t32_blx(0x1c3fea,HASH)==get(0x1c3fea,4)
# MP map-name lookup (0x249f84): only knew kino/ascension/deadops/callofthedead -> returned NULL for nacht
# (MP single-map select strcpy'd NULL, vote tally ignored it). Add a fallback for "nacht".
F=0x249f84
_e=bytes.fromhex('70b506460a4d86b001ac7d4408350fcd0fc42b686d46236055f8044f24b120463af082efb042f7d1204606b070bd'); assert get(F,len(_e))==_e
CAVE=0x1c3fe0
code =hw(0xb93c)                       # cbnz r4, done
code+=hw(0xf2af,0x0414)                # adr.w r4, "nacht"
code+=hw(0x4620)                       # mov r0, r4
code+=t32_blx(CAVE+8,HASH)             # blx hash
code+=hw(0x42b0,0xbf18,0x2400)         # cmp r0,r6 ; it ne ; movne r4,#0
assert CAVE+len(code)==0x1c3ff2
code+=hw(0x4620,0xb006,0xbd70)         # done: mov r0,r4 ; add sp,#0x18 ; pop {r4,r5,r6,pc}
assert CAVE+len(code)<=0x1c4002
put(CAVE,code)
put(0x249fac,t32_branch(0x249fac,CAVE,False)+hw(0xbf00))
open('/root/work/v37/boz.s3e.raw','wb').write(raw)
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
c=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',c,5,len(raw))
assert lzma.decompress(bytes(c),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v37/boz.s3e','wb').write(c); print('ok',len(c))
