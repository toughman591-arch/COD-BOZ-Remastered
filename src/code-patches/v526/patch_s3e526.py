"""v5.26 code: co-op map-name lookup also knows 'proto' (Shi No Numa).
F (0x249f84) now walks the 4-map table in place (no stack copy) and, when nothing matched, jumps to the
cave at 0x1c3fe6, which checks the inline names nacht / verruck / proto (stride 8: 0x1c3fd0, 0x1c3fd8, 0x1c3fe0)."""
import struct,lzma
raw=bytearray(open('/root/work/v55/code/boz.s3e.raw','rb').read()); B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
def blx_arm(src,dst):
    off=dst-((src+4)&~3); assert -(1<<24)<=off<(1<<24) and off%4==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    return hw(0xf000|(S<<10)|((off>>12)&0x3ff), 0xc000|(J1<<13)|(J2<<11)|(((off>>2)&0x3ff)<<1))
def bw(src,dst):
    off=dst-(src+4); assert -(1<<24)<=off<(1<<24) and off%2==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    return hw(0xf000|(S<<10)|((off>>12)&0x3ff),0x9000|(J1<<13)|(J2<<11)|((off>>1)&0x7ff))
def adrw_neg(at,target,rd=4):
    base=(at+4)&~3; imm=base-target; assert 0<imm<4096
    return hw(0xf2af|(((imm>>11)&1)<<10), (((imm>>8)&7)<<12)|(rd<<8)|(imm&0xff))
HASH=0x284eac; F=0x249f84; CAVE=0x1c3fe0; TBL=0x453cec
# --- expected current state (v5.25)
assert get(F,0x30)==bytes.fromhex('70b506460a4d86b001ac7d4408350fcd0fc42b686d46236055f8044f24b120463af082efb042f7d1')+bw(0x249fac,CAVE)+hw(0xbf00,0xbf00)
assert struct.unpack('<I',get(0x249fb4,4))[0]+0x249f92+8==TBL
assert get(0x1c3fd0,16)==b'nacht\0\0\0verruck\0'
assert get(CAVE,32)==bytes.fromhex('5cb9aff21404022520 46c0f060efb04203d00834013df7d10024204606b070bd'.replace(' ',''))
assert get(0x1c4000,2)==hw(0xbf00) and get(0x1c4002,2)==hw(0xe017)
# --- F
f=hw(0xb570,0x4606,0x4d0a,0x447d)            # push {r4-r6,lr}; mov r6,r0; ldr r5,=lit; add r5,pc (pc=0x249f8e)
f+=hw(0xf855,0x4b04)                          # 8c L: ldr r4,[r5],#4
f+=hw(0xb134)                                 # 90 cbz r4,NOTF(a0)
f+=hw(0x4620)+blx_arm(F+0x10,HASH)            # 92 mov r0,r4 ; 94 blx hash
f+=hw(0x42b0,0xd1f7)                          # 98 cmp r0,r6 ; 9a bne L
f+=hw(0x4620,0xbd70)                          # 9c mov r0,r4 ; 9e pop {r4-r6,pc}
f+=bw(F+0x1c,CAVE+6)                          # a0 NOTF: b.w cave
f+=hw(0xbf00)*8                               # a4..b3 nop
assert len(f)==0x30
put(F,f); put(0x249fb4,struct.pack('<I',TBL-0x249f8e))   # add r5,pc at 0x249f8a: pc=0x249f8e
# --- cave
c=b'proto\0'
c+=adrw_neg(CAVE+6,0x1c3fd0)                  # e6 adr.w r4,"nacht"
c+=hw(0x2503)                                 # ea movs r5,#3
c+=hw(0x4620)+blx_arm(CAVE+0xe,HASH)          # ec L: mov r0,r4 ; ee blx hash
c+=hw(0x42b0,0xd003,0x3408,0x3d01,0xd1f7,0x2400)  # f2 cmp ; f4 beq D ; adds r4,#8 ; subs r5,#1 ; bne L ; movs r4,#0
c+=hw(0x4620,0xbd70)                          # fe D: mov r0,r4 ; pop {r4-r6,pc}
assert CAVE+len(c)==0x1c4002
put(CAVE,c)
open('/root/work/v526/code/boz.s3e.raw','wb').write(raw); open('/root/work/v526/code/code526.bin','wb').write(raw[B:])
fl=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
cc=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=fl)); struct.pack_into('<Q',cc,5,len(raw))
assert lzma.decompress(bytes(cc),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v526/code/boz.s3e','wb').write(cc); print('ok',len(cc))
# ---- v5.29: bigger game heap (Mali textures with alpha are 4x their ATC size; Dead Ops has ~66 MB of them)
cfg_old=b'MemSize = [GAME] ExtraMemorySize + 176000000'; cfg_new=b'MemSize = [GAME] ExtraMemorySize + 256000000'
assert raw.count(cfg_old)==1; raw[:]=raw.replace(cfg_old,cfg_new)
open('/root/work/v526/code/boz.s3e.raw','wb').write(raw); open('/root/work/v526/code/code526.bin','wb').write(raw[B:])
cc=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=fl)); struct.pack_into('<Q',cc,5,len(raw))
assert lzma.decompress(bytes(cc),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v526/code/boz.s3e','wb').write(cc); print('heap 256 MB ok',len(cc))
