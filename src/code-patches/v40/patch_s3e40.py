"""v4.0 code: Nacht's spare level slot (old 'nachtb' debug card) becomes 'verruck' (Verrückt);
co-op map-name lookup cave now checks both slots ('nacht','verruck')."""
import struct,lzma,subprocess
raw=bytearray(open('/root/work/v38/boz.s3e.raw','rb').read()); B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
def blx_arm(src,dst):          # Thumb BLX to ARM code
    off=dst-((src+4)&~3); assert -(1<<24)<=off<(1<<24) and off%4==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    imm10=(off>>12)&0x3ff; imm10L=(off>>2)&0x3ff
    return hw(0xf000|(S<<10)|imm10, 0xc000|(J1<<13)|(J2<<11)|(imm10L<<1))
assert get(0x1c3fd0,16)==b'nacht\0\0\0nachtb\0\0'
put(0x1c3fd8,b'verruck\0')
CAVE=0x1c3fe0; HASH=0x284eac; S1=0x1c3fd0
assert get(CAVE,2)==hw(0xb93c)
def adrw_neg(at,target):       # ADR.W Rd,#-imm (SUB form): T3 encoding 0xf2af
    base=(at+4)&~3; imm=base-target; assert 0<imm<4096
    i=(imm>>11)&1; imm3=(imm>>8)&7; imm8=imm&0xff; rd=4
    return hw(0xf2af|(i<<10), (imm3<<12)|(rd<<8)|imm8)
code=b''
L=CAVE+8
code+=hw(0xb000)                                   # placeholder cbnz (fixed below)
code+=adrw_neg(CAVE+2,S1)                          # adr.w r4,"nacht"
code+=hw(0x2502)                                   # movs r5,#2
assert CAVE+len(code)==L
code+=hw(0x4620)                                   # L: mov r0,r4
code+=blx_arm(CAVE+len(code),HASH)                 # blx hash
code+=hw(0x42b0)                                   # cmp r0,r6
beq_at=CAVE+len(code); code+=hw(0xd000)            # beq D (fixed below)
code+=hw(0x3408)                                   # adds r4,#8
code+=hw(0x3d01)                                   # subs r5,#1
bne_at=CAVE+len(code); off=(L-(bne_at+4))>>1; code+=hw(0xd100|(off&0xff))   # bne L
code+=hw(0x2400)                                   # movs r4,#0
D=CAVE+len(code)
code+=hw(0x4620,0xb006,0xbd70)                     # D: mov r0,r4; add sp,#0x18; pop {r4,r5,r6,pc}
code=bytearray(code)
o=(D-(CAVE+4))>>1; assert 0<=o<64; struct.pack_into('<H',code,0,0xb900|((o>>5)&1)<<9|(o&0x1f)<<3|4)   # cbnz r4,D
o=(D-(beq_at+4))>>1; struct.pack_into('<H',code,beq_at-CAVE,0xd000|(o&0xff))
assert CAVE+len(code)<=0x1c4002,hex(CAVE+len(code))
put(CAVE,bytes(code))
open('/root/work/v40/boz.s3e.raw','wb').write(raw)
open('/root/work/v40/code40.bin','wb').write(raw[B:])
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
c=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',c,5,len(raw))
assert lzma.decompress(bytes(c),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v40/boz.s3e','wb').write(c); print('ok',len(c),'cave end',hex(CAVE+len(code)))
