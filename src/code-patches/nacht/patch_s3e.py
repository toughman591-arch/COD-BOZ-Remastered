import struct,lzma,subprocess
raw=bytearray(open('/root/work/ow/boz.s3e.raw','rb').read())   # v1.7.5 code (One Window patches applied)
B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
def t32_branch(src,dst,link):
    off=dst-(src+4); assert -(1<<24)<=off<(1<<24) and off%2==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    imm10=(off>>12)&0x3ff; imm11=(off>>1)&0x7ff
    h1=0xf000|(S<<10)|imm10; h2=(0xd000 if link else 0x9000)|(J1<<13)|(J2<<11)|imm11
    return hw(h1,h2)
# 1) weapons/arms/projectile mapping: first letter >= 'n' -> kino set (nacht, proto, tutorial)
for site,k in [(0x1cbc3c,4),(0x1e1e46,6),(0x1e1ed6,6)]:
    a=site+k; assert get(a,2)==hw(0x2870),(hex(a),get(a,2).hex()); put(a,hw(0x286e))
# 2) START whitelist chain is dead code (nopped earlier) -> skip it, reuse the space as a code cave
assert get(0x1c3fb2,2)==hw(0x4845)
put(0x1c3fb2,hw(0xe000|((0x1c4034-(0x1c3fb2+4))>>1)))           # b 0x1c4034
CAVE=0x1c3fb4
S1,S2=0x1c3fd0,0x1c3fd8
def adr(at,target):
    base=(at+4)&~3; off=target-base; assert off>=0 and off%4==0 and off<1024; return hw(0xa100|(off>>2))
code=hw(0x4620)+adr(CAVE+2,S1)+t32_branch(CAVE+4,0x1c40f8,True)          # register "nacht"
code+=hw(0x4620)+adr(CAVE+10,S2)+t32_branch(CAVE+12,0x1c40f8,True)       # register "nachtb" (debug card)
code+=hw(0x69af)+bytes.fromhex('17f00107')                                # ldr r7,[r5,#0x18]; ands.w r7,r7,#1 (moved from 0x1c4240)
code+=t32_branch(CAVE+len(code),0x1c4246,False)+hw(0xbf00)
assert CAVE+len(code)==S1,hex(CAVE+len(code))
code+=b'nacht\0\0\0'+b'nachtb\0\0'
assert CAVE+len(code)<=0x1c4002
put(CAVE,code)
# 3) constructor: after registering cotdeadops, detour to the cave to also register "nacht"
assert get(0x1c4240,6)==hw(0x69af)+bytes.fromhex('17f00107')
put(0x1c4240,t32_branch(0x1c4240,CAVE,False)+hw(0xbf00))
open('/root/work/nacht/boz.s3e.raw','wb').write(raw)
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
c=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',c,5,len(raw))
assert lzma.decompress(bytes(c),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/nacht/boz.s3e','wb').write(c); print('ok',len(c))
